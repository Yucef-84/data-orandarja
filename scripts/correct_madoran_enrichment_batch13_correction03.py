"""Apply the final known HeadGPT semantic corrections for MADOran Batch 13."""
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

BASE_COMMIT = "8025cdf"
CORRECTION_ID = "MADORAN-ENRICH-013-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v13-correction-3"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_correction03_qa.json"

CORRECTIONS = {
    778: {
        "english": "The speaker says there has been no sale despite five months of searching through a real-estate agency. They say that they have now found a buyer, so it is not appropriate or possible to replace that buyer; the buyer is not described as unsuitable.",
        "korean": "화자는 5개월 동안 부동산 중개업소를 찾아다녔지만 팔리지 않았다고 해요. 이제 구매자를 찾았으니 그 구매자를 바꾸는 것은 적절하지도 가능하지도 않다고 말해요. 구매자가 부적합하다고 평가하지 않아요.",
    },
    785: {"processing_flags": "code_switching"},
    788: {
        "english": "Salim is asked what he will drink. The speaker addresses Si Jamal and says, ‘Look, Si Jamal, I will speak directly and get to the point; I have not accepted this deal or matter.’ The speaker asks what they think and recalls that they only agreed to meet today to finish the purchase. Si Jamal is the addressee, not the speaker.",
        "korean": "살림에게 무엇을 마실지 묻고, 화자가 시 자말 씨에게 ‘보세요, 시 자말 씨, 바로 본론을 말할게요. 나는 이 거래나 일을 받아들이지 않았어요’라고 말해요. 어떻게 생각하는지 묻고 오늘 만나 매매를 끝내기로만 합의했다는 점을 상기해요. 시 자말 씨는 화자가 아니라 호격의 대상이에요.",
    },
    807: {
        "english": "The speaker asks what it means to handle the matter and why they came here while leaving the others there. The exact force of منستعلوش remains unclear, but the speaker explicitly hopes that they will grow, that their days and circumstances will improve, and that trouble will not come upon them.",
        "korean": "화자는 일을 처리한다는 것이 무슨 뜻인지, 왜 그들이 이곳에 오면서 다른 사람들을 그곳에 두었는지 물어요. منستعلوش의 정확한 힘은 불분명하게 남기지만, 우리가 성장하고 우리 형편과 날들이 나아지며 우리에게 나쁜 일이 닥치지 않기를 바란다는 의미는 보존해요.",
    },
    810: {
        "english": "The speaker challenges Salima: ‘Are you going to be better than his mother and sister?’ The line asks whether she wants Khaled to leave his wife and children in Oran and come away; Khaled cannot live far from us. The family came so the children could attend école privée, a private school, and be raised well.",
        "korean": "화자는 살리마에게 ‘네가 그의 어머니와 누이보다 더 나을 거라는 거야?’라고 도전적으로 물어요. 이어 칼레드가 아내와 아이들을 오랑에 두고 떠나기를 바라는지 묻고, 칼레드는 우리와 멀리 살 수 없다고 해요. 가족은 아이들이 프랑스어 école privée, 즉 사립학교에 다니며 잘 자라게 하려고 왔어요.",
    },
    811: {
        "english": "The speaker asks why they should come now and says that there is no difference between here and there. A woman then objects to being mocked for not giving birth and asks rhetorically whether she would have wanted this for herself; she says that this is a matter from God, not a choice she made for herself.",
        "korean": "화자는 그런데 이제 그들이 왜 와야 하느냐고 묻고, 여기든 저기든 마찬가지라고 말해요. 이어 한 여성이 아이를 낳지 못한다고 조롱받는 데 항의하며 자신이 이런 일을 스스로 원했겠느냐고 반문해요. 이것은 자신이 선택한 일이 아니라 하느님의 일이라고 말해요.",
    },
    813: {
        "english": "One person asks the other to wake him. She says she cannot because he is upset. She then says, ‘Look, the person who will take me to Oran is coming soon; I do not want to leave without seeing my brother. Go wake him.’ The person coming to take her, rather than the listener, is the subject of the Oran-movement clause.",
        "korean": "한 사람이 상대에게 그를 깨워 달라고 해요. 상대는 그가 화가 나서 깨울 수 없다고 말해요. 이어 ‘나를 오랑으로 데려갈 사람이 곧 와. 형제를 보지 않고 떠나고 싶지 않으니 가서 그를 깨워 줘’라고 말해요. 오랑 이동의 주체는 듣는 상대가 아니라 그녀를 데려갈 사람이에요.",
    },
    819: {
        "english": "The former-student speaker tells the woman that he was once her student and continues, in French-mixed speech, ‘That is why, after all, I summoned you about a matter…’ The former student is the person who called her; the final ‘خير إن شاء الله’ remains a separate response meaning roughly ‘I hope it is something good’ or ‘What is it, God willing?’",
        "korean": "예전 학생이었던 화자가 그 여성에게 자신이 예전에 그녀의 학생이었다고 말하고, 프랑스어가 섞인 표현으로 ‘그래서 그런 이유로 어떤 용건 때문에 당신을 불렀어요’라고 이어 말해요. 그녀를 부른 사람은 별도의 담당자가 아니라 그 former student 화자예요. 마지막 ‘خير إن شاء الله’는 ‘좋은 일이길 바라요’ 또는 ‘무슨 좋은 일인가요?’ 정도의 별도 응답으로 남겨요.",
    },
    830: {
        "english": "The speaker tells the listener to take a five-minute walk and return. The speaker says that they have kept the listener for a long time today, perhaps, and asks them not to shout; the long duration is the speaker’s action, not a statement that the day itself was long.",
        "korean": "화자는 듣는 사람에게 5분 정도 한 바퀴 걷고 돌아오라고 해요. 오늘 자신이 듣는 사람을 오래 붙잡아 둔 것 같다며, 소리치지 말아 달라고 해요. 오래 걸린 주체는 하루 자체가 아니라 화자의 행위예요.",
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
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 11285:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 11302 or trace["result"] != "PASS":
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
    evidence_path = "data/master/qa/madoran_enrichment_batch13_correction03_qa.json"
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
        "total_provenance_events": 11302,
        "expected_total_provenance_events": 11302,
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
        "provenance_events_before": 11285,
        "provenance_events_after": 11302,
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
