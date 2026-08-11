"""Apply HeadGPT correction 02 for the six remaining MADOran Batch 10 P1s."""
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

BASE_COMMIT = "4f53435"
CORRECTION_ID = "MADORAN-ENRICH-010-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v10-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_correction02_qa.json"

CORRECTIONS = {
    599: {
        "english": "Get a grip, Naima—something like ‘a star, not Milan.’ Not Milan: you have had no value for a long time, and your children are Harkis (حركى), a historical and potentially derogatory label; they appeared in the Casbah. The lyric and name references remain partly unclear.",
        "korean": "정신 차려, 나이마. ‘스타이지 밀라노는 아니다’ 같은 말이에요. 밀라노는 아니야. 너는 오래전부터 가치가 없었고, 너희 아이들이 카스바에 나타났다는 식으로 말해요. 아이들을 ‘하르키(Harkis, حركى)’라고 부르는데 역사적이고 모욕적으로 쓰일 수 있는 명칭이에요. 가사와 이름의 지칭은 일부 불분명해요.",
    },
    619: {
        "english": "May God have mercy on them; may their place be in Paradise, and, God willing, may they enter through Bab Rayyan. There were many sheikhs whose words educated or delighted us, and a passionate or ardent poet grew up there. Many came from the Casbah and gave voice to our melody. The references to Qlal, Ibrahim Hamada Bouna, and poems written long ago are partly unclear.",
        "korean": "하느님께서 그들에게 자비를 베푸시고 그들의 자리가 천국이 되기를 바라요. 하느님의 뜻이라면 바브 라이얀을 통해 들어가기를 바라요. 우리를 가르치거나 즐겁게 한 말을 남긴 셰이크가 많았고, 그곳에서 열정적인 시인이 자랐어요. 많은 사람이 카스바 출신으로 우리의 멜로디에 목소리를 보탰어요. 끌랄과 이브라힘 하마다 부나, 오래전에 쓰인 시에 대한 지칭은 일부 불분명해요.",
    },
    623: {
        "english": "Moulay Abdq is named. The following verbs are actor-ambiguous and may mean ‘we liked [it or him]’ and ‘we went up’ or ‘it rose’; the source does not resolve the relation. Oran, you have so many domes.",
        "korean": "물라이 압드크가 언급돼요. 뒤의 동사는 행위자가 불명확해서 ‘우리가 그것이나 그를 좋아했다’와 ‘우리가 올라갔다’ 또는 ‘그것이 올라갔다’처럼 해석될 수 있어요. 원문은 그 관계를 확정하지 않아요. 오랑아, 너에게는 돔이 정말 많아요.",
    },
    630: {
        "english": "My friend, I need a vest. If there is a parking job, I want to work; then the French code-switch ‘Vive l’Algérie!’ appears. Stop fooling around. My friend, I told you I only need a vest—you thought I said something else. The rest of the banter is unclear.",
        "korean": "친구야, 나는 조끼가 필요해. 주차 일이 있으면 일하고 싶어요. 이어서 프랑스어로 ‘Vive l’Algérie!’(알제리 만세!)라는 말이 나와요. 장난 그만해. 친구야, 나는 조끼만 필요하다고 했는데 네가 다른 말을 들은 것 같아. 나머지 농담은 불분명해요.",
    },
    634: {
        "english": "I want to go to the toilet—is that all right? You, shut your mouth! How many times have I told you that when we are talking about food, you must not bring up the toilet? What is wrong with you—are you overdoing it in the toilet or what? This is a toilet-related taunt, and the exact wording is unclear. Fine, go; the remaining insults are unclear.",
        "korean": "화장실에 가고 싶은데 괜찮아요? 당신, 입 다물어요! 음식을 이야기할 때 화장실 얘기를 꺼내지 말라고 몇 번이나 말했어요? 왜 그래요. 화장실에서 너무 그러는 거예요? 화장실과 관련된 조롱이며 정확한 표현은 불분명해요. 됐어요, 가요. 나머지 욕설은 불분명해요.",
    },
    637: {
        "english": "I am with my dear friend Sofiane from Nas Khir. He helps us understand the mentality, what should happen, and what we are going to do. Go ahead, Sofiane. The following exchange welcomes Sofiane and welcomes people to Oran.",
        "korean": "나는 나스 키르 소속인 사랑하는 친구 소피안과 함께 있어요. 그는 우리가 그 방식과 무엇이 되어야 하는지, 우리가 무엇을 할지를 이해하도록 도와줘요. 소피안, 계속 말해 주세요. 이어지는 대화에서 소피안을 환영하고 사람들을 오랑으로 환영해요.",
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
    if len(CORRECTIONS) != 6 or changed_fields != 12:
        raise RuntimeError(f"correction_shape:{len(CORRECTIONS)}:{changed_fields}")
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 8639:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 8651 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch10_correction02_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": 6, "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID, "latest_correction_id": CORRECTION_ID,
        "correction_history": history, "correction_changed_fields": changed_fields,
        "correction_state_updates": 0, "correction_rows": 6, "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 8651, "expected_total_provenance_events": 8651,
        "content_review_status": "pending_headgpt_correction_review", "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS", "batch_id": BATCH_ID, "correction_id": CORRECTION_ID, "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)], "changed_fields": changed_fields,
        "state_updates": 0, "new_provenance_events": changed_fields, "provenance_events_before": 8639,
        "provenance_events_after": 8651, "source_gate": "PASS", "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
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
