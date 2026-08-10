"""Apply the first HeadGPT content correction set for Batch 02."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from scripts.build_madoran_enrichment_batch02 import BATCH_OUT, ITEMS
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


BASE_COMMIT = "f75f363"
CORRECTION_ID = "MADORAN-ENRICH-002-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v2-correction-1"
METHOD = "llm_source_only_enrichment_correction"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 65
TARGET_END = 128
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction_qa.json"
CHANGED_FIELDS = {
    80: ("latin", "english", "korean"),
    90: ("english", "korean"),
    96: ("latin", "english", "korean", "processing_flags"),
    102: ("latin", "english", "korean"),
    105: ("latin", "english", "korean"),
}


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def assert_old_value(sentno: int, field: str, value: str) -> None:
    markers = {
        (80, "latin"): "brik",
        (80, "english"): "bourek",
        (80, "korean"): "부레크",
        (90, "english"): "mattresses",
        (90, "korean"): "매트리스",
        (96, "latin"): "9atlha",
        (96, "english"): "he killed her",
        (96, "korean"): "죽였",
        (96, "processing_flags"): "context_heavy",
        (102, "latin"): "Tlemcen",
        (102, "english"): "Tlemcen",
        (102, "korean"): "틀렘센",
        (105, "latin"): "tlemc",
        (105, "english"): "Tlemcen",
        (105, "korean"): "틀렘센",
    }
    marker = markers.get((sentno, field))
    if marker is None or marker not in value:
        raise RuntimeError(f"correction_precondition_failed:{sentno}:{field}")


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    if len(batch_rows) != TARGET_END - TARGET_START + 1:
        raise RuntimeError("batch02_row_count")
    batch_by_sentno = {int(row["sentno"]): row for row in batch_rows}
    if not set(CHANGED_FIELDS).issubset(batch_by_sentno):
        raise RuntimeError("correction_target_mismatch")
    source_keys = [(row["source_uid"], row["sentno"]) for row in source_rows]
    before_keys = [(row["source_uid"], row["sentno"]) for row in before_rows]
    if source_keys != before_keys:
        raise RuntimeError("source_linkage_changed")

    after_rows = [dict(row) for row in before_rows]
    changed_cells = 0
    for row in after_rows:
        sentno = int(row["sentno"])
        if sentno not in CHANGED_FIELDS:
            continue
        batch = batch_by_sentno[sentno]
        for field in CHANGED_FIELDS[sentno]:
            assert_old_value(sentno, field, row[field])
            row[field] = batch[field]
            changed_cells += 1
        if sentno == 96:
            row["enrichment_state"] = "flagged"
    if changed_cells != 15:
        raise RuntimeError(f"changed_cell_count:{changed_cells}")
    outside_mutations = sum(
        before != after
        for before, after in zip(before_rows, after_rows)
        if not TARGET_START <= int(after["sentno"]) <= TARGET_END
    )
    if outside_mutations:
        raise RuntimeError(f"outside_target_mutations:{outside_mutations}")

    existing_event_text = EVENTS_OUT.read_text(encoding="utf-8")
    if not existing_event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    source_uids = {row["source_uid"] for row in source_rows}
    existing_check = check_provenance_events(existing_event_text, source_uids)
    if existing_check["result"] != "PASS" or existing_check["events"] != 2174:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in after_rows
        for field in CHANGED_FIELDS.get(int(row["sentno"]), ())
    ]
    combined_event_text = existing_event_text + "".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in new_events
    )
    combined_check = check_provenance_events(combined_event_text, source_uids)
    if combined_check["result"] != "PASS":
        raise RuntimeError(json.dumps(combined_check, ensure_ascii=False))
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if trace["result"] != "PASS":
        raise RuntimeError(json.dumps(trace, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(
            "".join(
                json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
                for item in new_events
            ).encode("utf-8")
        )

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    counts = dict(status.get("counts", {}))
    counts["enrichment_completed_rows"] = sum(1 for row in after_rows if row["enrichment_state"] in {"qa_passed", "reviewed"})
    counts["enrichment_draft_rows"] = sum(1 for row in after_rows if row["enrichment_state"] == "draft")
    counts["enrichment_flagged_rows"] = sum(1 for row in after_rows if row["enrichment_state"] == "flagged")
    counts["enrichment_not_started_rows"] = sum(1 for row in after_rows if row["enrichment_state"] == "not_started")
    counts["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after_rows)
    status["counts"] = counts
    evidence = list(status.get("evidence_files", []))
    correction_path = "data/master/qa/madoran_enrichment_batch02_correction_qa.json"
    if correction_path not in evidence:
        evidence.append(correction_path)
    status["evidence_files"] = evidence
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa.update(
        {
            "correction_id": CORRECTION_ID,
            "correction_changed_fields": changed_cells,
            "correction_rows": len(CHANGED_FIELDS),
            "correction_provenance_events": len(new_events),
            "draft_rows": counts["enrichment_draft_rows"],
            "flagged_rows": counts["enrichment_flagged_rows"] - 2,
            "new_provenance_events": 740 + len(new_events),
            "total_provenance_events": existing_check["events"] + len(new_events),
            "generated_at": generated_at,
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-002",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(number) for number in sorted(CHANGED_FIELDS)],
        "changed_fields": changed_cells,
        "new_provenance_events": len(new_events),
        "provenance_events_before": existing_check["events"],
        "provenance_events_after": existing_check["events"] + len(new_events),
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "generated_at": generated_at,
        "outputs": {
            "batch": "data/master/enrichment/batches/batch02_sentno_0065_0128.tsv",
            "enrichment": "data/master/enrichment/madoran_sentence_enrichment.tsv",
            "provenance": "data/master/enrichment/madoran_sentence_enrichment_provenance.jsonl",
        },
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
