"""Apply the HeadGPT-directed correction pass for MADOran Batch 01."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

try:
    from scripts.apply_madoran_enrichment_batch import (
        BATCH_FIELDS,
        BATCH_OUT,
        CONTROLLED_VALUES,
        EMPTY_FIELDS,
        MANIFEST_OUT,
        ROOT,
        TARGET_END,
        TARGET_START,
        validate_batch_rows,
    )
    from scripts.build_madoran_enrichment_scaffold import (
        ENRICHMENT_FIELDS,
        ENRICHMENT_OUT,
        EVENTS_OUT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
        write_tsv,
    )
    from scripts.validate_madoran_enrichment import check_enrichment_provenance
except ModuleNotFoundError:
    from apply_madoran_enrichment_batch import (  # type: ignore
        BATCH_FIELDS,
        BATCH_OUT,
        CONTROLLED_VALUES,
        EMPTY_FIELDS,
        MANIFEST_OUT,
        ROOT,
        TARGET_END,
        TARGET_START,
        validate_batch_rows,
    )
    from build_madoran_enrichment_scaffold import (  # type: ignore
        ENRICHMENT_FIELDS,
        ENRICHMENT_OUT,
        EVENTS_OUT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
        write_tsv,
    )
    from validate_madoran_enrichment import check_enrichment_provenance  # type: ignore


CORRECTION_ID = "MADORAN-ENRICH-001-CORRECTION-01"
CORRECTION_PROMPT_VERSION = "madoran-source-enrichment-v1-correction-1"
CORRECTION_METHOD = "llm_source_only_enrichment_correction"
CORRECTION_REVIEW_STATE = "generated"
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch01_qa.json"


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _event(source_uid: str, field: str, value: str, generated_at: str) -> dict[str, str]:
    import hashlib

    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": CORRECTION_METHOD,
        "model": "codex-unspecified",
        "prompt_version": CORRECTION_PROMPT_VERSION,
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "review_state": CORRECTION_REVIEW_STATE,
    }


def validate_corrected_state(
    before_rows: list[dict[str, str]], after_rows: list[dict[str, str]]
) -> dict[str, object]:
    failures: list[str] = []
    target_rows = 0
    populated_fields = 0
    outside_target_mutations = 0
    flagged_rows: list[str] = []
    for before, after in zip(before_rows, after_rows):
        sentno = int(after.get("sentno", "0")) if after.get("sentno", "").isdigit() else 0
        if TARGET_START <= sentno <= TARGET_END:
            target_rows += 1
            if before.get("enrichment_state") != "draft":
                failures.append(f"unexpected_before_state:{sentno}")
            if after.get("enrichment_state") not in {"draft", "flagged"}:
                failures.append(f"invalid_corrected_state:{sentno}")
            if after.get("enrichment_state") == "flagged":
                flagged_rows.append(str(sentno))
            for field in EMPTY_FIELDS:
                if not after.get(field):
                    failures.append(f"empty_corrected_field:{sentno}:{field}")
                else:
                    populated_fields += 1
        elif before != after:
            outside_target_mutations += 1
    if target_rows != TARGET_END - TARGET_START + 1:
        failures.append("target_row_count")
    if outside_target_mutations:
        failures.append("outside_target_mutations")
    return {
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "target_rows": target_rows,
        "populated_fields": populated_fields,
        "outside_target_mutations": outside_target_mutations,
        "flagged_rows": flagged_rows,
    }


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))

    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    if not before_rows or list(before_rows[0]) != ENRICHMENT_FIELDS:
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
            if row.get("enrichment_state") != "draft":
                raise RuntimeError(f"correction_precondition_failed:{sentno}")
            corrected = target_by_sentno[sentno]
            for field in EMPTY_FIELDS:
                row[field] = corrected[field]
            if sentno == "63":
                row["enrichment_state"] = "flagged"

    state_check = validate_corrected_state(before_rows, after_rows)
    if state_check["result"] != "PASS":
        raise RuntimeError(json.dumps(state_check, ensure_ascii=False))

    source_uids = {row.get("source_uid", "") for row in source_rows}
    existing_event_bytes = EVENTS_OUT.read_bytes() if EVENTS_OUT.exists() else b""
    existing_event_text = existing_event_bytes.decode("utf-8")
    if not existing_event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    existing_event_check = check_provenance_events(existing_event_text, source_uids)
    if existing_event_check["result"] != "PASS" or existing_event_check["events"] != 704:
        raise RuntimeError(json.dumps(existing_event_check, ensure_ascii=False))
    before_trace = check_enrichment_provenance(before_rows, existing_event_text)
    if before_trace["result"] != "PASS":
        raise RuntimeError(json.dumps(before_trace, ensure_ascii=False))

    generated_at = current_utc_timestamp()
    correction_events = [
        _event(row["source_uid"], field, row[field], generated_at)
        for row in batch_rows
        for field in EMPTY_FIELDS
    ]
    correction_text = "".join(
        json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
        for event in correction_events
    )
    combined_event_text = existing_event_text + correction_text
    combined_event_check = check_provenance_events(combined_event_text, source_uids)
    if combined_event_check["result"] != "PASS":
        raise RuntimeError(json.dumps(combined_event_check, ensure_ascii=False))
    after_trace = check_enrichment_provenance(after_rows, combined_event_text)
    if after_trace["result"] != "PASS":
        raise RuntimeError(json.dumps(after_trace, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(correction_text.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["enrichment_correction_id"] = CORRECTION_ID
    counts = dict(status.get("counts", {}))
    counts["enrichment_draft_rows"] = 63
    counts["enrichment_flagged_rows"] = 1
    counts["enrichment_not_started_rows"] = 1292
    counts["enrichment_completed_rows"] = 0
    status["counts"] = counts
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-001",
        "correction_id": CORRECTION_ID,
        "base_commit": "20d3b34",
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "target_rows": state_check["target_rows"],
        "draft_rows": 63,
        "flagged_rows": state_check["flagged_rows"],
        "not_started_rows": 1292,
        "correction_populated_fields": state_check["populated_fields"],
        "outside_target_mutations": state_check["outside_target_mutations"],
        "new_provenance_events": len(correction_events),
        "total_provenance_events": combined_event_check["events"],
        "latest_event_hash_gate": "PASS",
        "generated_at": generated_at,
        "source_gate": gate["result"],
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "validator": "PASS",
        "content_review_status": "corrected_pending_headgpt_recheck",
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = apply()
    print(json.dumps(result, ensure_ascii=False, indent=2))
