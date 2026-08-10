"""Apply the final Sentno 97 speaker-direction correction for Batch 02."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from scripts.build_madoran_enrichment_batch02 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
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


BASE_COMMIT = "d8d6e4d"
CORRECTION_ID = "MADORAN-ENRICH-002-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v2-correction-4"
METHOD = "llm_source_only_enrichment_correction"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 65
TARGET_END = 128
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction04_qa.json"
CHANGED_FIELDS = {97: ("latin", "english", "korean")}
OLD_MARKERS = {
    (97, "latin"): "9atlha",
    (97, "english"): "told her, 'Go buy snails.'",
    (97, "korean"): "남자가 아내에게 '달팽이를 사 와'라고",
}
ABSENT_MARKERS = {(97, "latin"): "9atletlou"}


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
    marker = OLD_MARKERS[(sentno, field)]
    if marker not in value:
        raise RuntimeError(f"correction_precondition_failed:{sentno}:{field}")
    absent = ABSENT_MARKERS.get((sentno, field))
    if absent and absent in value:
        raise RuntimeError(f"correction_already_applied:{sentno}:{field}")


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS or len(batch_rows) != 64:
        raise RuntimeError("input_shape_mismatch")
    batch_by_sentno = {int(row["sentno"]): row for row in batch_rows}
    source_keys = [(row["source_uid"], row["sentno"]) for row in source_rows]
    before_keys = [(row["source_uid"], row["sentno"]) for row in before_rows]
    if source_keys != before_keys or 97 not in batch_by_sentno:
        raise RuntimeError("source_linkage_or_target_mismatch")

    after_rows = [dict(row) for row in before_rows]
    changed_cells = 0
    for row in after_rows:
        if int(row["sentno"]) != 97:
            continue
        for field in CHANGED_FIELDS[97]:
            assert_old_value(97, field, row[field])
            row[field] = batch_by_sentno[97][field]
            changed_cells += 1
    if changed_cells != 3:
        raise RuntimeError(f"changed_cell_count:{changed_cells}")
    outside_mutations = sum(
        before != after
        for before, after in zip(before_rows, after_rows)
        if not TARGET_START <= int(after["sentno"]) <= TARGET_END
    )
    if outside_mutations:
        raise RuntimeError(f"outside_target_mutations:{outside_mutations}")

    existing_event_text = EVENTS_OUT.read_text(encoding="utf-8")
    source_uids = {row["source_uid"] for row in source_rows}
    existing_check = check_provenance_events(existing_event_text, source_uids)
    if not existing_event_text.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 2271:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in after_rows
        for field in CHANGED_FIELDS.get(int(row["sentno"]), ())
    ]
    new_event_text = "".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in new_events
    )
    combined_event_text = existing_event_text + new_event_text
    combined_check = check_provenance_events(combined_event_text, source_uids)
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if combined_check["result"] != "PASS" or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(new_event_text.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    correction_path = "data/master/qa/madoran_enrichment_batch02_correction04_qa.json"
    if correction_path not in evidence:
        evidence.append(correction_path)
    status["evidence_files"] = evidence
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": 3, "rows": 1, "provenance_events": 3})
    qa.update(
        {
            "correction_id": CORRECTION_ID,
            "latest_correction_id": CORRECTION_ID,
            "correction_history": history,
            "correction_changed_fields": 3,
            "correction_rows": 1,
            "correction_provenance_events": 3,
            "new_provenance_events": qa.get("new_provenance_events", 837) + 3,
            "total_provenance_events": 2274,
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
        "corrected_rows": ["97"],
        "changed_fields": 3,
        "new_provenance_events": 3,
        "provenance_events_before": 2271,
        "provenance_events_after": 2274,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": outside_mutations,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 46,
        "flagged_rows": 18,
        "processing_flags_populated_rows": 39,
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
