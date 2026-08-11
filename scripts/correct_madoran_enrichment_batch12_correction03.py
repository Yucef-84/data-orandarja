"""Apply the third HeadGPT correction set for MADOran Batch 12."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch12 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "c7e9890"
CORRECTION_ID = "MADORAN-ENRICH-012-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v12-correction-3"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch12_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch12_correction03_qa.json"

CORRECTIONS = {
    709: {"processing_flags": "code_switching|source_ambiguity"},
    714: {"processing_flags": "code_switching|long_source|source_ambiguity"},
    715: {"processing_flags": "code_switching|idiom_culture|source_ambiguity"},
    721: {
        "english": "Do not drink while standing. Clean your face; you do not know what you may meet with it. The proverb then uses a comparative structure: if beauty has the advantage over you, answer or surpass it with a smile; if صيغة, a manner or form of conduct, has the advantage, answer or surpass it with tact or diplomacy; and if money has the advantage, answer or surpass it with contentment.",
        "korean": "서서 마시지 말아요. 얼굴을 깨끗이 하세요. 그 얼굴로 무엇을 만나게 될지는 알 수 없어요. 이어 속담은 비교 구조를 사용해요. 아름다움이 당신보다 앞서면 미소로 응수하거나 넘어설 수 있고, 처신이나 방식인 ‘صيغة’가 앞서면 처신·외교적 수완으로 응수하거나 넘어설 수 있으며, 돈이 앞서면 만족으로 응수하거나 넘어설 수 있다고 해요.",
    },
    731: {"processing_flags": "idiom_culture"},
    734: {"processing_flags": "code_switching|source_ambiguity"},
    736: {"processing_flags": "code_switching|context_heavy"},
    739: {"processing_flags": "code_switching|idiom_culture|source_ambiguity"},
    745: {"processing_flags": "code_switching|source_ambiguity"},
    749: {
        "english": "When they get married, she asks him: ‘Do we have a home and are we مستورين/مستروين?’ The term is a state expression meaning that they are settled, provided for, or living respectably, not a separate object or piece of furniture. He answers, ‘Thank God; do what you want in it.’",
        "korean": "그들이 결혼하면 그녀가 그에게 ‘우리에게 집이 있고 형편도 갖춰져 있지 않나요?’라고 물어요. ‘مستورين/مستروين’은 별도의 물건이나 가구가 아니라 형편이 갖춰지고 안정되며 남부럽지 않게 지낸다는 상태 표현이에요. 그는 하느님께 감사하다고 하며 그 안에서 원하는 일을 하라고 답해요.",
        "topic": "home_and_settled_marriage_state",
    },
    752: {"processing_flags": "code_switching|source_ambiguity"},
    753: {"processing_flags": "code_switching|source_ambiguity"},
    756: {
        "english": "Then he says, ‘I want you to arrange a proposal for my friend, a certain woman.’ She is a woman he usually brings to the house. His mother responds: ‘How can you want to marry a woman who usually comes with you to the house?’ She is questioning his intention to marry that familiar woman; the source does not say that she comes with him to search for a spouse.",
        "korean": "그러자 그는 ‘내 친구인 어떤 여자에게 청혼을 주선해 주세요’라고 말해요. 그 여자는 그가 평소 집에 데려오던 여자예요. 어머니는 ‘늘 너와 함께 집에 오던 그 여자와 네가 결혼하려는 게 어떻게 가능하니?’라는 취지로 반응해요. 어머니는 익숙한 그 여자와 결혼하려는 아들의 의도를 묻는 것이며, 그 여자가 그와 함께 배우자를 찾으러 온다는 뜻은 원문에 없어요.",
    },
    759: {"processing_flags": "code_switching|idiom_culture|source_ambiguity"},
    746: {"processing_flags": "idiom_culture"},
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid, field, value, generated_at):
    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": "llm_source_only_enrichment_correction",
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_state": "generated",
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
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 10373:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 10392 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"]["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after)
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch12_correction03_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": len(CORRECTIONS), "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID,
        "latest_correction_id": CORRECTION_ID,
        "correction_history": history,
        "correction_changed_fields": changed_fields,
        "correction_state_updates": 0,
        "correction_rows": len(CORRECTIONS),
        "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 10392,
        "expected_total_provenance_events": 10392,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "content_review_status": "pending_headgpt_correction_review",
        "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": changed_fields,
        "state_updates": 0,
        "new_provenance_events": changed_fields,
        "provenance_events_before": 10373,
        "provenance_events_after": 10392,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 3,
        "flagged_rows": 61,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "batch_artifact_sync": "PASS",
        "batch_artifact_sync_changed_fields": changed_fields,
        "batch_artifact_sync_state_updates": 0,
        "generated_at": generated_at,
        "outputs": {
            "batch": BATCH_OUT.relative_to(ROOT).as_posix(),
            "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
            "provenance": EVENTS_OUT.relative_to(ROOT).as_posix(),
        },
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
