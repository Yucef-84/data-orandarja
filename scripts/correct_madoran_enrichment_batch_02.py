"""Apply the second HeadGPT-directed correction pass for MADOran Batch 01."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone

try:
    from scripts.apply_madoran_enrichment_batch import (
        BATCH_FIELDS,
        BATCH_OUT,
        EMPTY_FIELDS,
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
        EMPTY_FIELDS,
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


CORRECTION_ID = "MADORAN-ENRICH-001-CORRECTION-02"
CORRECTION_PROMPT_VERSION = "madoran-source-enrichment-v1-correction-2"
CORRECTION_METHOD = "llm_source_only_enrichment_correction"
CORRECTION_REVIEW_STATE = "generated"
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch01_qa.json"


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _event(source_uid: str, field: str, value: str, generated_at: str) -> dict[str, str]:
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


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))

    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if not before_rows or list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    if not batch_rows or list(batch_rows[0]) != BATCH_FIELDS:
        raise RuntimeError("batch_header_mismatch")
    batch_check = validate_batch_rows(source_rows, batch_rows)
    if batch_check["result"] != "PASS":
        raise RuntimeError(json.dumps(batch_check, ensure_ascii=False))

    source_uids = {row["source_uid"] for row in source_rows}
    existing_event_bytes = EVENTS_OUT.read_bytes() if EVENTS_OUT.exists() else b""
    existing_event_text = existing_event_bytes.decode("utf-8")
    if not existing_event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    existing_event_check = check_provenance_events(existing_event_text, source_uids)
    if existing_event_check["result"] != "PASS" or existing_event_check["events"] != 1408:
        raise RuntimeError(json.dumps(existing_event_check, ensure_ascii=False))
    latest_events: dict[tuple[str, str], dict[str, str]] = {}
    for line in existing_event_text.splitlines():
        event = json.loads(line)
        latest_events[(event["source_uid"], event["field"])] = event

    target_by_sentno = {row["sentno"]: row for row in batch_rows}
    after_rows = [dict(row) for row in before_rows]
    changed_fields: list[tuple[str, str, str, str]] = []
    for before, after in zip(before_rows, after_rows):
        sentno = after.get("sentno", "")
        if TARGET_START <= int(sentno) <= TARGET_END:
            if before.get("enrichment_state") != ("flagged" if sentno == "63" else "draft"):
                raise RuntimeError(f"correction_precondition_failed:{sentno}")
            corrected = target_by_sentno[sentno]
            for field in EMPTY_FIELDS:
                if before[field] != corrected[field]:
                    raise RuntimeError(f"batch_master_mismatch:{sentno}:{field}")
                current_hash = "sha256:" + hashlib.sha256(before[field].encode("utf-8")).hexdigest()
                latest = latest_events.get((after["source_uid"], field))
                if latest is None:
                    raise RuntimeError(f"missing_latest_event:{sentno}:{field}")
                if latest["value_hash"] != current_hash:
                    changed_fields.append((after["source_uid"], field, latest["value_hash"], corrected[field]))
                after[field] = corrected[field]
            if after["enrichment_state"] != before["enrichment_state"]:
                raise RuntimeError(f"unexpected_state_mutation:{sentno}")
        elif before != after:
            raise RuntimeError(f"outside_target_mutation:{sentno}")

    if len(changed_fields) != 21:
        raise RuntimeError(f"unexpected_changed_field_count:{len(changed_fields)}")

    generated_at = current_utc_timestamp()
    correction_events = [_event(uid, field, new, generated_at) for uid, field, _old, new in changed_fields]
    correction_text = "".join(
        json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n" for event in correction_events
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
    status["counts"].update(
        {
            "enrichment_completed_rows": 0,
            "enrichment_draft_rows": 63,
            "enrichment_flagged_rows": 1,
            "enrichment_not_started_rows": 1292,
        }
    )
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-001",
        "correction_id": CORRECTION_ID,
        "base_commit": "cf209fe",
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "target_rows": 64,
        "draft_rows": 63,
        "flagged_rows": ["63"],
        "not_started_rows": 1292,
        "correction_populated_fields": 704,
        "changed_fields": len(changed_fields),
        "outside_target_mutations": 0,
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
            "batch": "data/master/enrichment/batches/batch01_sentno_0001_0064.tsv",
            "manifest": "data/master/enrichment/batches/batch01_manifest.json",
            "enrichment": "data/master/enrichment/madoran_sentence_enrichment.tsv",
            "provenance": "data/master/enrichment/madoran_sentence_enrichment_provenance.jsonl",
        },
    }
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
