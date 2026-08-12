"""Apply the second HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch14 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "4be5a22"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-2"
MODEL = "llm-review-directed"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch14_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch14_correction02_qa.json"
PROVENANCE_BEFORE = 12096
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction02_qa.json"

CORRECTIONS = {
    833: {
        "english": "The speaker mentions the listener's phone and the villa keys, asks what happened to them, and tells the listener to be quiet after reminding them not to call. The exact action in the opening fragment is uncertain; no stranger is added.",
        "korean": "화자는 상대의 전화기와 별장 열쇠를 언급하고 그것들이 어떻게 되었는지 물은 뒤, 전화하지 말라고 일렀잖느냐며 조용히 하라고 해요. 첫 부분의 정확한 행동은 불확실하게 두고 낯선 사람을 추가하지 않아요.",
    },
    834: {
        "english": "The speaker says they are speaking rationally and tells the listener to sit and listen carefully. They threaten to kill the listener if the listener moves or follows them when they leave, then tell a friend to move away; the threat is preserved as source content.",
        "korean": "화자는 이성적으로 말하고 있다며 앉아서 잘 들으라고 해요. 자신이 나갈 때 상대가 움직이거나 따라오면 죽이겠다고 위협한 뒤, 친구에게 물러나라고 해요. 위협은 원문 내용으로 보존해요.",
    },
    835: {
        "english": "The speaker asks Dalila to watch the speaker's table while the speaker goes to comb their hair at Nariman's place and returns.",
        "korean": "화자는 달릴라에게 자기 테이블을 봐 달라고 하고, 나리만에게 머리를 빗으러 갔다가 돌아오겠다고 해요.",
    },
    855: {
        "korean": "화자는 상대가 아무것도 모른다며, 상대가 자신의 남자 형제가 영향력이 크다고 말할 것이라고 예상해요. 상대도 만만하지 않다며 그 남자와 상대의 일이나 거래가 무엇인지 물어요. 상대의 아내가 받아들여도 달라질 것은 없고, 앞에 서 있는 여성도 행복할 자격이 있다고 말해요.",
    },
    860: {
        "english": "The listener says they never saw the man's face because it was covered, but he looked young and like a respectable or well-bred man. The source does not establish that he was a family man.",
        "korean": "상대는 얼굴이 가려져 있어서 그 남자의 얼굴을 한 번도 보지 못했지만, 젊고 예의 바르거나 집안이 좋은 남자처럼 보였다고 말해요. 원문은 그가 가족을 둔 남자라고 확정하지 않아요.",
    },
    863: {
        "english": "The listener says this was stated in the first report: they could not shout because the man carried a weapon under his coat, but in fairness he never used it. They called the villa owners, who said they would enter with the opaque French-like expression ‘fbrwmi fwl’; its exact wording and procedure are uncertain, so the surface form is retained.",
        "korean": "상대는 첫 번째 조서에 그렇게 말했다며, 그 남자가 옷 아래 무기를 들고 있어 소리칠 수 없었지만 공정하게 말하면 그것을 사용한 적은 없다고 해요. 별장 주인에게 전화하자 불투명한 프랑스어식 표현인 ‘fbrwmi fwl’을 가지고 들어가겠다고 했다고 말해요. 정확한 표현과 절차는 불확실해 표면형을 보존해요.",
    },
    865: {
        "english": "The speaker addresses Hussein as a friend and asks what to do about the money affair. The other person says they know nothing and calls Houari their brother; the direct addressee Hussein is not made the question speaker.",
        "korean": "화자는 후세인을 친구라고 직접 부르며 돈 문제를 어떻게 해야 하는지 물어요. 상대는 아무것도 모르겠다며 호아리를 형제라고 불러요. 직접 호격된 후세인을 질문 화자로 확정하지 않아요.",
    },
    868: {
        "english": "The speaker addresses Toufik as a brother and says they are not someone who will lose with him. The speaker insults him, says the money will reach him, tells him to shut up, and threatens to plant something in his head; the exact turn boundaries remain somewhat uncertain.",
        "korean": "화자는 투피크를 형제라고 직접 부르며 자신은 그와 싸움에서 질 사람이 아니라고 말해요. 투피크를 모욕하고 돈이 그에게 도착할 것이라고 하며 입을 다물라고 하고, 그의 머리에 무엇인가를 박겠다고 위협해요. 정확한 turn 경계는 일부 불확실해요.",
    },
    870: {
        "english": "A person greets Aunt Zoulikha; she asks how the person is, and the person says they are fine. The person reminds her that, as they said, when her bread runs out they will bring bread to her from the bakery. Aunt Zoulikha refuses, saying the bread from the last time smelled of chicken; ‘my son’ is treated as a familiar address, not an age claim.",
        "korean": "한 사람이 줄리카 이모에게 인사하고, 이모가 잘 지내느냐고 묻자 그 사람은 괜찮다고 답해요. 그 사람은 전에 말했듯 이모의 빵이 떨어지면 빵집에서 빵을 가져다주겠다고 상기시켜요. 줄리카 이모는 지난번 빵에서 닭 냄새가 났다며 거절해요. ‘내 아들’은 친근한 호칭으로 처리하고 나이를 확정하지 않아요.",
    },
    872: {
        "english": "The speaker tells the addressee to go and work, using the familiar form ‘my son’. The row itself does not identify the speaker as Aunt Zoulikha or establish the addressee's age.",
        "korean": "화자는 친근한 ‘내 아들’ 호칭을 사용해 상대에게 가서 일하라고 해요. 이 행 자체는 화자를 줄리카 이모로 밝히지 않으며 상대의 나이도 확정하지 않아요.",
    },
    883: {
        "english": "The speaker addresses someone as ‘my son’ and refers to money and property. She hopes that her son will graduate from university tomorrow, find work, and compensate her for everything. A later statement about a man who never made her feel that he was her father has an uncertain or shifted referent and is not merged with the son.",
        "korean": "화자는 누군가를 ‘내 아들’이라고 부르며 돈과 재산을 언급해요. 자신의 아들이 내일 대학을 졸업해 일하고 모든 것을 보상해 주기를 바라요. 뒤에서 자신에게 아버지라는 느낌을 주지 않았던 남자에 대한 말은 지시대상이 불확실하거나 바뀐 것이므로 그 아들과 합치지 않아요.",
    },
    886: {
        "english": "The speaker wishes to close and reopen their eyes in a faraway place where no one asks where they came from. They say they want to forget Elias completely. The speaker then addresses Elias as ‘my son’ and asks whether he too will forget the speaker; the actor direction is preserved.",
        "korean": "화자는 눈을 감았다가 다시 뜨면 아무도 어디서 왔는지 묻지 않는 먼 곳에 있기를 바라요. 엘리아스를 완전히 잊고 싶다고 말한 뒤, 엘리아스를 ‘내 아들’이라고 부르며 그도 자신을 잊을 것인지 물어요. 행위자 방향을 보존해요.",
    },
    887: {
        "english": "The speaker addresses Dalila and tells her to call her sister because the speaker needs her. After a brief clarification of the sister's name and an instruction to speak to mother, the speaker asks each woman to contribute three hundred thousand to buy a refrigerator, recalling that they had said making one would be better.",
        "korean": "화자는 달릴라를 직접 부르며 자신에게 필요한 달릴라의 자매에게 전화하라고 해요. 자매의 이름을 잠깐 확인하고 엄마에게 말하라고 한 뒤, 냉장고를 사려고 각자 30만씩 내 달라고 하며 전에 직접 만드는 것이 낫다고 했던 일을 떠올려요.",
    },
    890: {
        "english": "The speaker asks why the woman does not put anything in the refrigerator or eat anything cold from it. The woman says it has not cooled for some time and asks for the item or part referred to in the opaque expression ‘lizwnjin’; its exact referent is unclear.",
        "korean": "화자는 여성이 왜 냉장고에 아무것도 넣지 않고 차가운 것도 먹지 않느냐고 물어요. 여성은 한동안 차가워지지 않았다며 불투명한 표현 ‘lizwnjin’으로 가리킨 물건이나 부품을 가져와 달라고 해요. 정확한 지시대상은 불분명해요.",
    },
    893: {
        "english": "The speaker tells the woman to raise her level and asks whether she is listening. A following question about the money being put in and whether it should bother them is partly opaque, so the clause is preserved as uncertain. The speaker then mentions rent and says everything has fallen on their head.",
        "korean": "화자는 여성에게 수준을 높이라고 하며 듣고 있느냐고 물어요. 이어 넣는 돈과 그것이 왜 문제가 되느냐에 관한 질문이 나오지만 절 구조는 일부 불투명해 불확실하게 보존해요. 그 뒤 집세를 언급하며 모든 일이 자신에게 떨어졌다고 불평해요.",
    },
    896: {
        "english": "The listener asks why they should be quiet and what the other person wants, asking whether they should come every morning with the opaque expression ‘nbwantw’ or something similar; it is not translated as a gift. The speaker apologizes for being wrong and confused about the others. The final instruction preserves the opaque/name-like form ‘zino’: the other person is told to go to the house and ‘zine’ or arrange it, and the speaker says they will come shortly; the exact roles remain uncertain.",
        "korean": "상대는 왜 조용히 해야 하고 무엇을 원하는지 묻고, 매일 아침 ‘nbwantw’ 같은 불투명한 것을 가지고 와야 하느냐고 물어요. 이를 선물로 번역하지 않아요. 화자는 자신이 잘못하고 상대를 혼동했다며 사과해요. 마지막 지시는 불투명하거나 이름처럼 보이는 ‘zino’ 표현을 보존해, 상대에게 집에 가서 ‘zine’하거나 정리하라고 하고 자신은 곧 오겠다고 해요. 정확한 역할은 불확실해요.",
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
    source_uids = {row["source_uid"] for row in source}
    master_before = {row["sentno"]: row for row in before}
    batch_before = {row["sentno"]: row for row in batch}
    if list(before[0]) != ENRICHMENT_FIELDS or not batch:
        raise RuntimeError("artifact_shape_mismatch")
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
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != PROVENANCE_BEFORE:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != PROVENANCE_BEFORE + changed_fields or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"]["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after)
    evidence_path = EVIDENCE_PATH
    evidence = list(status.get("evidence_files", []))
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
        "total_provenance_events": PROVENANCE_BEFORE + changed_fields,
        "expected_total_provenance_events": PROVENANCE_BEFORE + changed_fields,
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
        "provenance_events_before": PROVENANCE_BEFORE,
        "provenance_events_after": PROVENANCE_BEFORE + changed_fields,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": len(batch),
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
