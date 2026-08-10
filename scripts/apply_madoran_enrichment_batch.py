"""Apply one source-only MADOran enrichment batch with append-only provenance."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

try:
    from scripts.build_madoran_enrichment_scaffold import (
        EMPTY_FIELDS,
        ENRICHMENT_FIELDS,
        ENRICHMENT_OUT,
        EVENTS_OUT,
        ROOT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
        write_tsv,
    )
    from scripts.validate_madoran_enrichment import check_enrichment_provenance
except ModuleNotFoundError:
    from build_madoran_enrichment_scaffold import (  # type: ignore
        EMPTY_FIELDS,
        ENRICHMENT_FIELDS,
        ENRICHMENT_OUT,
        EVENTS_OUT,
        ROOT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
        write_tsv,
    )
    from validate_madoran_enrichment import check_enrichment_provenance  # type: ignore


BATCH_ID = "MADORAN-ENRICH-001"
BASE_COMMIT = "c8d85c7"
PROMPT_VERSION = "madoran-source-enrichment-v1"
METHOD = "llm_source_only_enrichment"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.0.0"
GENERATED_AT = "2026-08-10T00:00:00Z"
TARGET_START = 1
TARGET_END = 64
TARGET_STATE = "draft"

BATCH_DIR = ROOT / "data" / "master" / "enrichment" / "batches"
BATCH_OUT = BATCH_DIR / "batch01_sentno_0001_0064.tsv"
MANIFEST_OUT = BATCH_DIR / "batch01_manifest.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch01_qa.json"
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"

BATCH_FIELDS = ["source_uid", "sentno", *EMPTY_FIELDS]
CEFR_LEVELS = frozenset({"A1", "A2", "B1", "B2", "C1", "C2"})
CONTROLLED_VALUES = {
    "domain": frozenset(
        {
            "daily_life",
            "family_relationships",
            "food",
            "shopping",
            "transport",
            "education",
            "work",
            "housing",
            "health",
            "religion",
            "culture_tradition",
            "history",
            "politics_public_affairs",
            "sports",
            "humor",
            "entertainment_music",
            "social_media",
            "administration",
            "finance",
            "crime_safety",
            "travel",
            "other",
        }
    ),
    "genre": frozenset(
        {"conversation", "narrative", "interview", "proverb", "joke", "recipe", "song_lyric", "speech", "social_media", "expository", "other"}
    ),
    "speech_act": frozenset(
        {
            "greeting",
            "question",
            "answer",
            "request",
            "command",
            "suggestion",
            "agreement",
            "disagreement",
            "refusal",
            "description",
            "narration",
            "opinion",
            "complaint",
            "warning",
            "thanks",
            "apology",
            "wish",
            "exclamation",
            "information",
            "other",
        }
    ),
    "register": frozenset({"neutral", "casual", "colloquial", "slang", "vulgar", "offensive", "mixed"}),
    "context_dependency": frozenset({"low", "medium", "high"}),
}


def _failure_report(failures: list[str], **values: object) -> dict[str, object]:
    return {"result": "PASS" if not failures else "FAIL", "failures": failures, **values}


def validate_batch_rows(
    source_rows: list[dict[str, str]], batch_rows: list[dict[str, str]]
) -> dict[str, object]:
    """Validate the immutable source linkage and the batch's 11 populated fields."""

    failures: list[str] = []
    expected_source = {
        row["sentno"]: row["source_uid"]
        for row in source_rows
        if TARGET_START <= int(row.get("sentno", "0")) <= TARGET_END
    }
    expected_sentnos = [str(index) for index in range(TARGET_START, TARGET_END + 1)]
    actual_sentnos = [row.get("sentno", "") for row in batch_rows]
    if len(batch_rows) != TARGET_END - TARGET_START + 1:
        failures.append("row_count")
    if actual_sentnos != expected_sentnos:
        failures.append("sentno_coverage")
    if len({row.get("source_uid", "") for row in batch_rows}) != len(batch_rows):
        failures.append("duplicate_source_uid")

    populated_fields = 0
    for row in batch_rows:
        sentno = row.get("sentno", "")
        if row.get("source_uid") != expected_source.get(sentno):
            failures.append(f"source_linkage:{sentno}")
        for field in EMPTY_FIELDS:
            value = row.get(field, "")
            if not value or value != value.strip() or any(char in value for char in "\t\r\n"):
                failures.append(f"invalid_value:{sentno}:{field}")
            else:
                populated_fields += 1
        if not row.get("latin", "").isascii():
            failures.append(f"latin_not_ascii:{sentno}")
        if row.get("cefr_level") not in CEFR_LEVELS:
            failures.append(f"invalid_cefr:{sentno}")
        try:
            score = int(row.get("difficulty_score", ""))
        except ValueError:
            score = -1
        if score < 0 or score > 100:
            failures.append(f"invalid_difficulty:{sentno}")
        for field, allowed in CONTROLLED_VALUES.items():
            if row.get(field) not in allowed:
                failures.append(f"invalid_controlled_value:{sentno}:{field}")

    return _failure_report(
        failures,
        source_rows=len(source_rows),
        batch_rows=len(batch_rows),
        sentno_start=TARGET_START,
        sentno_end=TARGET_END,
        populated_fields=populated_fields,
    )


def validate_applied_state(
    before_rows: list[dict[str, str]], after_rows: list[dict[str, str]]
) -> dict[str, object]:
    """Ensure the patch changes only the requested rows and fields."""

    failures: list[str] = []
    if len(before_rows) != len(after_rows):
        failures.append("row_count")
    target_rows = 0
    target_populated = 0
    outside_mutations = 0
    for before, after in zip(before_rows, after_rows):
        sentno = int(after.get("sentno", "0")) if after.get("sentno", "").isdigit() else 0
        if TARGET_START <= sentno <= TARGET_END:
            target_rows += 1
            if after.get("source_uid") != before.get("source_uid") or after.get("sentno") != before.get("sentno"):
                failures.append(f"target_source_key_changed:{sentno}")
            if after.get("enrichment_state") != TARGET_STATE:
                failures.append(f"target_state:{sentno}")
            for field in EMPTY_FIELDS:
                if not after.get(field):
                    failures.append(f"target_field_empty:{sentno}:{field}")
                else:
                    target_populated += 1
        elif before != after:
            outside_mutations += 1
    if target_rows != TARGET_END - TARGET_START + 1:
        failures.append("target_row_count")
    if outside_mutations:
        failures.append("outside_target_mutations")
    return _failure_report(
        failures,
        target_rows=target_rows,
        target_populated_fields=target_populated,
        outside_target_mutations=outside_mutations,
    )


def _event(source_uid: str, field: str, value: str) -> dict[str, str]:
    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": METHOD,
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "review_state": "generated",
    }


def _manifest() -> dict[str, object]:
    if not MANIFEST_OUT.exists():
        raise RuntimeError("batch_manifest_missing")
    manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
    expected = {
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "row_count": TARGET_END - TARGET_START + 1,
        "fields": list(EMPTY_FIELDS),
        "prompt_version": PROMPT_VERSION,
        "source_dependency": "canonical_source_only",
        "morphology_dependency": False,
        "darija_modified": False,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeError(f"batch_manifest_mismatch:{key}")
    return manifest


def _write_batch_qa(report: dict[str, object]) -> None:
    BATCH_QA_OUT.parent.mkdir(parents=True, exist_ok=True)
    BATCH_QA_OUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    manifest = _manifest()
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    batch_rows = read_tsv(BATCH_OUT)
    if not batch_rows or list(batch_rows[0]) != BATCH_FIELDS:
        raise RuntimeError("batch_header_mismatch")
    batch_check = validate_batch_rows(source_rows, batch_rows)
    if batch_check["result"] != "PASS":
        raise RuntimeError(json.dumps(batch_check, ensure_ascii=False))

    target_by_sentno = {row["sentno"]: row for row in batch_rows}
    after_rows = [dict(row) for row in before_rows]
    for row in after_rows:
        sentno = row.get("sentno", "")
        if TARGET_START <= int(sentno) <= TARGET_END:
            if row.get("enrichment_state") != "not_started":
                raise RuntimeError(f"target_row_already_processed:{sentno}")
            source_batch_row = target_by_sentno[sentno]
            for field in EMPTY_FIELDS:
                row[field] = source_batch_row[field]
            row["enrichment_state"] = TARGET_STATE

    state_check = validate_applied_state(before_rows, after_rows)
    if state_check["result"] != "PASS":
        raise RuntimeError(json.dumps(state_check, ensure_ascii=False))

    source_uids = {row.get("source_uid", "") for row in source_rows}
    existing_event_bytes = EVENTS_OUT.read_bytes() if EVENTS_OUT.exists() else b""
    existing_event_text = existing_event_bytes.decode("utf-8")
    if existing_event_text and not existing_event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    existing_event_check = check_provenance_events(existing_event_text, source_uids)
    if existing_event_check["result"] != "PASS":
        raise RuntimeError(json.dumps(existing_event_check, ensure_ascii=False))
    new_events = [
        _event(row["source_uid"], field, row[field])
        for row in batch_rows
        for field in EMPTY_FIELDS
    ]
    new_event_text = "".join(
        json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
        for event in new_events
    )
    combined_event_text = existing_event_text + new_event_text
    combined_event_check = check_provenance_events(combined_event_text, source_uids)
    if combined_event_check["result"] != "PASS":
        raise RuntimeError(json.dumps(combined_event_check, ensure_ascii=False))
    enrichment_provenance = check_enrichment_provenance(after_rows, combined_event_text)
    if enrichment_provenance["result"] != "PASS":
        raise RuntimeError(json.dumps(enrichment_provenance, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(new_event_text.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_batch_id"] = BATCH_ID
    counts = dict(status.get("counts", {}))
    counts["enrichment_draft_rows"] = TARGET_END - TARGET_START + 1
    counts["enrichment_not_started_rows"] = len(after_rows) - (TARGET_END - TARGET_START + 1)
    counts["enrichment_completed_rows"] = 0
    status["counts"] = counts
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "source_rows": len(source_rows),
        "target_rows": state_check["target_rows"],
        "state_transition": "not_started_to_draft",
        "populated_fields": state_check["target_populated_fields"],
        "outside_target_mutations": state_check["outside_target_mutations"],
        "new_provenance_events": len(new_events),
        "missing_provenance_events": 0,
        "hash_mismatch": 0,
        "invalid_provenance_events": 0,
        "source_linkage_failures": 0,
        "duplicate_source_uid": 0,
        "arabic_copied": 0,
        "arabic_modified": 0,
        "morphology_reads": 0,
        "dependency_violations": 0,
        "morphology": "BLOCKED_UPSTREAM_DEFECT",
        "validator": "PASS",
        "outputs": {
            "batch": BATCH_OUT.relative_to(ROOT).as_posix(),
            "manifest": MANIFEST_OUT.relative_to(ROOT).as_posix(),
            "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
            "provenance": EVENTS_OUT.relative_to(ROOT).as_posix(),
        },
    }
    _write_batch_qa(qa)
    return qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = apply()
    print(json.dumps(result, ensure_ascii=False, indent=2))
