"""Apply HeadGPT correction 03 for the final two MADOran Batch 10 P1s."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch10 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "14ad545"
CORRECTION_ID = "MADORAN-ENRICH-010-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v10-correction-3"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_correction03_qa.json"

CORRECTIONS = {
    634: {
        "english": "I want to go to the toilet—is that all right? You, shut your mouth! How many times have I told you that when we are talking about food, you must not bring up the toilet? What is wrong with you? The phrase ‘مالك زايد في كابيني’ is retained as an unclear toilet-related taunt involving زايد في; the source does not resolve whether it is an ‘overdoing it’ or birth/origin insult. Fine, go; the remaining insults are unclear.",
        "korean": "화장실에 가고 싶은데 괜찮아요? 당신, 입 다물어요! 음식을 이야기할 때 화장실 얘기를 꺼내지 말라고 몇 번이나 말했어요? 왜 그래요? ‘مالك زايد في كابيني’는 ‘زايد في’ 관계를 포함한 불분명한 화장실 관련 조롱으로 보존해요. 원문만으로 그것이 ‘너무 그러는 것’인지 출생·태생을 겨냥한 욕설인지 확정하지 않아요. 됐어요, 가요. 나머지 욕설은 불분명해요.",
    },
    637: {
        "english": "I am with my dear friend Sofiane from Nas Khir. He helps us understand the mentality, what should happen, and what we are going to do. Go ahead, Sofiane. The following exchange appears to be Sofiane welcoming the other participants or visitors to Oran, followed by the other speaker’s reply; the exact speaker assignment remains uncertain.",
        "korean": "나는 나스 키르 소속인 사랑하는 친구 소피안과 함께 있어요. 그는 우리가 그 방식과 무엇이 되어야 하는지, 우리가 무엇을 할지를 이해하도록 도와줘요. 소피안, 계속 말해 주세요. 이어지는 대화는 소피안이 다른 참가자나 방문객을 오랑으로 환영하고 다른 화자가 응답하는 흐름으로 보이지만, 정확한 화자 배정은 확정하지 않아요.",
    },
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid, field, value, generated_at):
    return {
        "source_uid": source_uid, "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": "llm_source_only_enrichment_correction", "model": MODEL,
        "prompt_version": PROMPT_VERSION, "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at, "review_state": "generated",
    }


def apply():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if not head.startswith(BASE_COMMIT) or source_gate()["result"] != "PASS":
        raise RuntimeError(f"gate_failed:{head}")
    source = read_tsv(SOURCE_OUT)
    before = read_tsv(ENRICHMENT_OUT)
    batch = read_tsv(BATCH_OUT)
    if list(before[0]) != ENRICHMENT_FIELDS or len(batch) != 64:
        raise RuntimeError("artifact_shape_mismatch")
    source_uids = {row["source_uid"] for row in source}
    master_before = {row["sentno"]: row for row in before}
    batch_before = {row["sentno"]: row for row in batch}
    for sentno in batch_before:
        if any(master_before[sentno].get(field) != batch_before[sentno].get(field) for field in ENRICHMENT_FIELDS):
            raise RuntimeError(f"batch_master_mismatch_before:{sentno}")
    after = [dict(row) for row in before]
    corrected_batch = [dict(row) for row in batch]
    for row in after:
        row.update(CORRECTIONS.get(int(row["sentno"]), {}))
    for row in corrected_batch:
        row.update(CORRECTIONS.get(int(row["sentno"]), {}))
    changed_fields = sum(len(fields) for fields in CORRECTIONS.values())
    if len(CORRECTIONS) != 2 or changed_fields != 4:
        raise RuntimeError(f"correction_shape:{len(CORRECTIONS)}:{changed_fields}")
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 8651:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 8655 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch10_correction03_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": 2, "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID, "latest_correction_id": CORRECTION_ID,
        "correction_history": history, "correction_changed_fields": changed_fields,
        "correction_state_updates": 0, "correction_rows": 2, "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 8655, "expected_total_provenance_events": 8655,
        "content_review_status": "pending_headgpt_correction_review", "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS", "batch_id": BATCH_ID, "correction_id": CORRECTION_ID, "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)], "changed_fields": changed_fields,
        "state_updates": 0, "new_provenance_events": changed_fields, "provenance_events_before": 8651,
        "provenance_events_after": 8655, "source_gate": "PASS", "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0, "arabic_modified": 0, "outside_target_mutations": 0, "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS", "validator": "PASS", "target_rows": 64, "draft_rows": 3, "flagged_rows": 61,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "batch_artifact_sync": "PASS", "batch_artifact_sync_changed_fields": changed_fields,
        "batch_artifact_sync_state_updates": 0, "generated_at": generated_at,
        "outputs": {"batch": BATCH_OUT.relative_to(ROOT).as_posix(), "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(), "provenance": EVENTS_OUT.relative_to(ROOT).as_posix()},
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
