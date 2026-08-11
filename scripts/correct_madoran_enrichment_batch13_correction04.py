"""Apply the remaining HeadGPT turn and speaker corrections for MADOran Batch 13."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch13 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "10c2542"
CORRECTION_ID = "MADORAN-ENRICH-013-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v13-correction-4"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_correction04_qa.json"

CORRECTIONS = {
    777: {
        "english": "The speaker accepts that selling may be a solution but questions a price of two billion. They ask why, after another buyer was found, someone said no; the exact speaker of the refusal remains unclear. They then say the beautiful house in a good location could be listed on Ouedkniss and bring ten; the source leaves the unit unstated.",
        "korean": "화자는 매도가 해결책일 수는 있지만 20억 가격을 묻고, 다른 구매자를 찾았는데 왜 누군가 거절했느냐고 물어요. 거절한 화자는 불분명하게 남겨요. 이어 좋은 곳의 아름다운 집을 우드키니스에 올리면 10을 받을 수 있다고 말하며, 원문은 10의 단위를 밝히지 않아요.",
    },
    781: {
        "english": "After agreeing to enter through the door, the speaker addresses Si Jamal directly and says or asks, ‘Si Jamal, this villa is three billion, right?’ The speaker then suggests inspecting it before discussing the price; the direct addressee and price-confirmation turn are preserved.",
        "korean": "문으로 들어가 보기로 한 뒤, 화자가 시 자말 씨를 직접 호격해 ‘시 자말 씨, 이 별장은 30억이죠?’라고 가격을 확인해요. 이어 먼저 살펴본 뒤 가격을 이야기하자고 해요. 직접 호격과 가격 확인 turn을 보존해요.",
    },
    797: {
        "english": "The first speaker says they have no time because of a plane, but has the other person’s phone number and will contact them when needed. The other person replies, ‘Whenever you want, even at night, call me and I will come.’ The two contact turns and their speakers are kept separate.",
        "korean": "첫 화자는 비행기 때문에 시간이 없지만 상대의 전화번호를 가지고 있어 필요할 때 연락하겠다고 말해요. 상대방은 ‘원할 때, 밤이라도 전화하면 내가 갈게’라고 답해요. 연락 주체와 두 turn을 분리해요.",
    },
    799: {
        "english": "Salima is offered more coffee and replies, ‘No, thank you.’ The person who decorated the house then asks Salima what she thinks of the decor and villa and whether she likes the decorator’s goût, taste or sense. The question is not attributed to Salima asking about her own goût.",
        "korean": "살리마에게 커피를 더 마실지 묻자 살리마가 ‘아니요, 고마워요’라고 답해요. 이어 집을 꾸민 사람이 살리마에게 장식과 별장이 어떤지, 자신의 goût, 즉 취향이나 감각이 마음에 드는지 물어요. 살리마가 자신의 goût에 대해 묻는 것으로 돌리지 않아요.",
    },
    802: {
        "english": "The exchange first includes a greeting or check-in and a remark that seeing her again now may make them miss her more; the exact referents remain somewhat ambiguous. A woman then asks, ‘Who told you that I am leaving today?’ She says perhaps she is weighing on the other person’s heart or becoming a burden, while the surrounding lines say that she is loved and missed.",
        "korean": "대화 앞부분에는 안부를 묻고 지금 다시 그녀를 보면 더 그리워질 수 있다는 말이 나와요. 정확한 지시대상은 일부 모호하게 남겨요. 이어 한 여성이 ‘내가 오늘 간다고 누가 말했어?’라고 묻고, 자신이 상대의 마음에 짐이 되거나 부담이 된 모양인지도 모른다고 말해요. 주변 발화에서는 사람들이 그녀를 사랑하고 그리워한다고 해요.",
    },
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
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 11302:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 11312 or trace["result"] != "PASS":
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
    evidence_path = "data/master/qa/madoran_enrichment_batch13_correction04_qa.json"
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
        "total_provenance_events": 11312,
        "expected_total_provenance_events": 11312,
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
        "provenance_events_before": 11302,
        "provenance_events_after": 11312,
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
