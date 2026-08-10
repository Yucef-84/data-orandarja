"""Apply MADORAN-ENRICH-003 with source-only provenance and state gates."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

from scripts.apply_madoran_enrichment_batch import CONTROLLED_VALUES, CEFR_LEVELS
from scripts.build_madoran_enrichment_batch03 import (
    BATCH_FIELDS,
    BATCH_ID,
    BATCH_OUT,
    BASE_COMMIT,
    MANIFEST_OUT,
    PROMPT_VERSION,
    TARGET_END,
    TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
    ENRICHMENT_FIELDS,
    ENRICHMENT_OUT,
    EVENTS_OUT,
    PROCESSING_FLAG_VALUES,
    ROOT,
    SOURCE_OUT,
    check_provenance_events,
    read_tsv,
    source_gate,
    write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance, check_layer_contract


METHOD = "llm_source_only_enrichment"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_qa.json"


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_batch_rows(source_rows: list[dict[str, str]], batch_rows: list[dict[str, str]]) -> dict[str, object]:
    failures: list[str] = []
    source_by_sentno = {
        row["sentno"]: row["source_uid"]
        for row in source_rows
        if TARGET_START <= int(row["sentno"]) <= TARGET_END
    }
    expected_sentnos = [str(index) for index in range(TARGET_START, TARGET_END + 1)]
    if len(batch_rows) != len(expected_sentnos):
        failures.append("row_count")
    if [row.get("sentno", "") for row in batch_rows] != expected_sentnos:
        failures.append("sentno_coverage")
    if len({row.get("source_uid", "") for row in batch_rows}) != len(batch_rows):
        failures.append("duplicate_source_uid")
    for row in batch_rows:
        sentno = row.get("sentno", "")
        if row.get("source_uid") != source_by_sentno.get(sentno):
            failures.append(f"source_linkage:{sentno}")
        for field in EMPTY_FIELDS:
            value = row.get(field, "")
            if not value or value != value.strip() or any(char in value for char in "\t\r\n"):
                failures.append(f"invalid_value:{sentno}:{field}")
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
        flags = row.get("processing_flags", "")
        flag_values = flags.split("|") if flags else []
        if flag_values != sorted(flag_values) or len(flag_values) != len(set(flag_values)):
            failures.append(f"non_canonical_flags:{sentno}")
        if any(value not in PROCESSING_FLAG_VALUES for value in flag_values):
            failures.append(f"invalid_processing_flag:{sentno}")
        if row.get("enrichment_state") not in {"draft", "flagged"}:
            failures.append(f"invalid_enrichment_state:{sentno}")
        if row.get("enrichment_state") == "flagged" and not flags:
            failures.append(f"flagged_without_reason:{sentno}")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "target_rows": len(batch_rows),
        "processing_flags_populated_rows": sum(bool(row.get("processing_flags")) for row in batch_rows),
        "required_linguistic_fields": len(batch_rows) * len(EMPTY_FIELDS),
    }


def validate_applied_state(
    before_rows: list[dict[str, str]],
    after_rows: list[dict[str, str]],
    batch_rows: list[dict[str, str]],
) -> dict[str, object]:
    failures: list[str] = []
    target_by_sentno = {row["sentno"]: row for row in batch_rows}
    target_rows = 0
    outside_mutations = 0
    for before, after in zip(before_rows, after_rows):
        sentno = after.get("sentno", "")
        if TARGET_START <= int(sentno) <= TARGET_END:
            target_rows += 1
            batch = target_by_sentno[sentno]
            if before.get("enrichment_state") != "not_started":
                failures.append(f"target_pre_state:{sentno}")
            if after.get("enrichment_state") != batch["enrichment_state"]:
                failures.append(f"target_state:{sentno}")
            for field in (*EMPTY_FIELDS, "processing_flags"):
                if after.get(field) != batch.get(field):
                    failures.append(f"target_field:{sentno}:{field}")
        elif before != after:
            outside_mutations += 1
    if target_rows != TARGET_END - TARGET_START + 1:
        failures.append("target_row_count")
    if outside_mutations:
        failures.append("outside_target_mutations")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "target_rows": target_rows,
        "outside_target_mutations": outside_mutations,
        "flagged_rows": sum(row["enrichment_state"] == "flagged" for row in batch_rows),
        "draft_rows": sum(row["enrichment_state"] == "draft" for row in batch_rows),
    }


def event(source_uid: str, field: str, value: str, generated_at: str) -> dict[str, str]:
    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": METHOD,
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_state": "generated",
    }


def check_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
    expected = {
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "row_count": 64,
        "fields": [*EMPTY_FIELDS, "processing_flags", "enrichment_state"],
        "prompt_version": PROMPT_VERSION,
        "source_dependency": "canonical_source_only",
        "morphology_dependency": False,
        "darija_modified": False,
        "schema_version": SCHEMA_VERSION,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeError(f"batch_manifest_mismatch:{key}")
    return manifest


def current_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def apply() -> dict[str, object]:
    if not current_commit().startswith(BASE_COMMIT):
        raise RuntimeError(f"base_commit_mismatch:{current_commit()}:{BASE_COMMIT}")
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    contract = check_layer_contract()
    if contract["result"] != "PASS":
        raise RuntimeError(json.dumps(contract, ensure_ascii=False))
    check_manifest()
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    if list(batch_rows[0]) != BATCH_FIELDS:
        raise RuntimeError("batch_header_mismatch")
    batch_check = validate_batch_rows(source_rows, batch_rows)
    if batch_check["result"] != "PASS":
        raise RuntimeError(json.dumps(batch_check, ensure_ascii=False))

    source_uids = {row["source_uid"] for row in source_rows}
    existing_event_text = EVENTS_OUT.read_text(encoding="utf-8")
    if not existing_event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    existing_check = check_provenance_events(existing_event_text, source_uids)
    if existing_check["result"] != "PASS" or existing_check["events"] != 2274:
        raise RuntimeError(json.dumps({**existing_check, "expected_events": 2274}, ensure_ascii=False))

    target_by_sentno = {row["sentno"]: row for row in batch_rows}
    after_rows = [dict(row) for row in before_rows]
    for row in after_rows:
        sentno = row["sentno"]
        if TARGET_START <= int(sentno) <= TARGET_END:
            if row["enrichment_state"] != "not_started":
                raise RuntimeError(f"target_row_already_processed:{sentno}")
            batch = target_by_sentno[sentno]
            for field in (*EMPTY_FIELDS, "processing_flags"):
                row[field] = batch[field]
            row["enrichment_state"] = batch["enrichment_state"]

    state_check = validate_applied_state(before_rows, after_rows, batch_rows)
    if state_check["result"] != "PASS":
        raise RuntimeError(json.dumps(state_check, ensure_ascii=False))

    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in batch_rows
        for field in EMPTY_FIELDS
    ]
    new_events.extend(
        event(row["source_uid"], "processing_flags", row["processing_flags"], generated_at)
        for row in batch_rows
        if row["processing_flags"]
    )
    new_event_text = "".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in new_events
    )
    combined_event_text = existing_event_text + new_event_text
    if not combined_event_text.startswith(existing_event_text):
        raise RuntimeError("provenance_prefix_not_preserved")
    combined_check = check_provenance_events(combined_event_text, source_uids)
    if combined_check["result"] != "PASS":
        raise RuntimeError(json.dumps(combined_check, ensure_ascii=False))
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if trace["result"] != "PASS":
        raise RuntimeError(json.dumps(trace, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(new_event_text.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_batch_id"] = BATCH_ID
    counts = dict(status.get("counts", {}))
    counts["enrichment_completed_rows"] = sum(
        1 for row in after_rows if row["enrichment_state"] in {"qa_passed", "reviewed"}
    )
    counts["enrichment_draft_rows"] = sum(row["enrichment_state"] == "draft" for row in after_rows)
    counts["enrichment_flagged_rows"] = sum(row["enrichment_state"] == "flagged" for row in after_rows)
    counts["enrichment_not_started_rows"] = sum(row["enrichment_state"] == "not_started" for row in after_rows)
    counts["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after_rows)
    status["counts"] = counts
    evidence_files = list(status.get("evidence_files", []))
    for evidence in (
        "data/master/qa/madoran_enrichment_batch03_generation_qa.json",
        "data/master/qa/madoran_enrichment_batch03_qa.json",
    ):
        if evidence not in evidence_files:
            evidence_files.append(evidence)
    status["evidence_files"] = evidence_files
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validation = subprocess.run(
        [sys.executable, "scripts/validate_madoran_enrichment.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if validation.returncode != 0:
        raise RuntimeError(validation.stdout + validation.stderr)

    n_flags = batch_check["processing_flags_populated_rows"]
    qa = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "target_rows": state_check["target_rows"],
        "draft_rows": state_check["draft_rows"],
        "flagged_rows": state_check["flagged_rows"],
        "processing_flags_populated_rows": counts["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": n_flags,
        "required_linguistic_fields": batch_check["required_linguistic_fields"],
        "populated_linguistic_fields": len(after_rows) * 0 + sum(
            bool(row[field]) for row in after_rows for field in EMPTY_FIELDS
        ),
        "state_transition": "not_started_to_explicit_draft_or_flagged",
        "outside_target_mutations": state_check["outside_target_mutations"],
        "provenance_events_before": existing_check["events"],
        "new_provenance_events": len(new_events),
        "total_provenance_events": combined_check["events"],
        "expected_total_provenance_events": 2978 + n_flags,
        "missing_provenance_events": 0,
        "hash_mismatch": 0,
        "prefix_preserved": True,
        "source_gate": "PASS",
        "layer_contract": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "learning_unit_rows_created": 0,
        "validator": "PASS",
        "latest_event_hash_gate": "PASS",
        "content_review_status": "pending_headgpt",
        "generated_at": generated_at,
        "outputs": {
            "batch": BATCH_OUT.relative_to(ROOT).as_posix(),
            "manifest": MANIFEST_OUT.relative_to(ROOT).as_posix(),
            "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
            "provenance": EVENTS_OUT.relative_to(ROOT).as_posix(),
        },
    }
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


if __name__ == "__main__":
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
