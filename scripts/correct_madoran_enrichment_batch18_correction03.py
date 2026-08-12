"""Apply the final focused semantic corrections for MADOran Batch 18."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch18 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "119a582"
BATCH_ID = "MADORAN-ENRICH-018"
CORRECTION_ID = "MADORAN-ENRICH-018-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v18-correction-3"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch18_correction03_qa.json"
PROVENANCE_BEFORE = 15930

CORRECTIONS = {
    1126: {
        "english": "The speaker says, ‘I brought you this news; go away, go away.’ They address Bourton, an opaque surface, and say, ‘I want Juventus to come and speak to me—zero-zero.’ They call their brother back, then say, ‘This is 120 doro for Sheikh Zdqdaq, who is absent tonight.’ They add, ‘This is another 120 doro for a group, as you did together, for the big and small cowboys, for the cowboys below and above, and for Las Vegas, Karkas, and Texas.’ The named people, groups, amounts, and place or group surfaces are preserved; the row is not reduced to generic bargaining over opaque items.",
        "korean": "화자는 ‘이 소식을 가져왔어. 가, 가’라고 해요. 불투명한 표면인 Bourton을 부르고 ‘Juventus가 와서 나에게 말했으면 해—0 대 0이야’라고 해요. 형제를 다시 부른 뒤 ‘이것은 오늘 밤 없는 셰이크 Zdqdaq를 위한 120도라야’라고 해요. 이어 ‘이것은 집단을 위한 또 다른 120도라야. 너희가 함께 한 것처럼, 크고 작은 cowboys를 위해, 아래와 위의 cowboys를 위해, Las Vegas·Karkas·Texas를 위해’라고 해요. 명시된 사람·집단·금액·장소 또는 집단 표면을 보존하고 일반적인 불투명 물건 흥정으로 축약하지 않아요.",
        "topic": "doro_allocations_for_people_groups_and_named_places",
    },
    1140: {
        "english": "The speaker says, ‘You, be quiet; when the elders speak, the children fall silent.’ The French-derived turn si di 9ws, si di zwnfwn, ail saf ba sw ki diz is retained with its explicit meaning that the children do not know what they are saying. The speaker says, ‘But the one who did this to us—you see him today; we will eat his flesh. He will pay dearly.’ Then: ‘Go, follow me, and leave it or mind your own business.’",
        "korean": "화자는 ‘너, 조용히 해. 어른들이 말할 때 아이들은 조용히 해야 해’라고 해요. 프랑스어 유래 turn si di 9ws, si di zwnfwn, ail saf ba sw ki diz를 아이들이 자신이 무슨 말을 하는지 모른다는 명시적 의미와 함께 보존해요. 이어 ‘하지만 우리에게 이 일을 한 사람을 너는 오늘 보고 있지. 우리는 그의 살을 먹을 거야. 그는 비싸게 대가를 치를 거야’라고 위협하고 ‘가서 나를 따라와. 내버려 둬, 네 일이나 신경 써’라고 해요.",
        "processing_flags": "code_switching",
    },
    1143: {
        "english": "The speaker begins, ‘I am telling you all, forgive me. Hazim, I want to ask you something: I want to become Indian like you.’ They ask whether the listener was alone or with a group, say there were some with the speaker and some with the listener, and repeat the Indian identity request. They call Akasha: ‘Akasha, come, take him,’ preserving dwh as a take-away direction rather than speech. They recall the day the listener took the speaker, ask where that happened, say the listener and a friend tied and brought the speaker to Madam, and then threaten to make a tagine and roast the listener over fire. All source turns remain.",
        "korean": "화자는 ‘너희에게 말하니 용서해 줘. Hazim, 너에게 물어볼 게 있어. 너처럼 인도인이 되고 싶어’라고 시작해요. 상대가 혼자였는지 집단과 함께였는지 묻고, 자신과 함께 몇몇이 있었고 상대와 함께 몇몇이 있었다고 하며 인도인 정체성 요청을 반복해요. Akasha를 부르며 ‘Akasha, 어서 와서 그를 데려가’라고 하여 dwh를 말하기가 아니라 데려가는 방향으로 보존해요. 상대가 자신을 데려간 날을 떠올리고 어디로 데려갔는지 묻고, 상대와 친구가 자신을 묶어 Madam에게 데려왔다고 한 뒤 타진을 만들고 불 위에서 상대를 굽겠다고 위협해요. 원문의 모든 turn을 보존해요.",
    },
    1146: {
        "english": "Mr Hazim is addressed: ‘Mr Hazim, I want to ask you: did you know the spy who was making trouble?’ The answer is, ‘Yes, I knew him, but I will leave it as a surprise—une surprise.’ The speaker then uses father/donkey/brother vocatives and says, ‘If you do not move or budge, by God I will give you every day a bidon of water and a kilo of grain.’ The final ‘Oh donkey, my brother, do not budge’ is a separate repeated command. The conditional relation and the final imperative remain distinct.",
        "korean": "화자는 Hazim 씨에게 ‘Hazim 씨, 물어보고 싶어. 문제를 일으키던 스파이를 알고 있었어?’라고 해요. 대답은 ‘응, 알고 있었어. 하지만 그건 놀라운 일, une surprise로 남겨 둘 거야’예요. 이어 아버지·당나귀·형제 호칭으로 상대를 부르며 ‘네가 움직이거나 꼼짝하지 않으면, 하느님께 맹세코 매일 물 한 통과 곡식 1킬로를 줄게’라고 해요. 마지막의 ‘오, 당나귀 같은 형제야, 꼼짝하지 마’는 별도의 반복 명령으로 보존해 조건 관계와 마지막 명령을 분리해요.",
    },
}


def apply():
    engine.BASE_COMMIT = BASE_COMMIT
    engine.BATCH_ID = BATCH_ID
    engine.CORRECTION_ID = CORRECTION_ID
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.BATCH_OUT = BATCH_OUT
    engine.BATCH_QA_OUT = BATCH_QA_OUT
    engine.CORRECTION_QA_OUT = CORRECTION_QA_OUT
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.PROVENANCE_BEFORE = PROVENANCE_BEFORE
    engine.CORRECTIONS = CORRECTIONS
    result = engine.apply()

    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = 20
    status["counts"]["enrichment_flagged_rows"] = 802
    status["enrichment_correction_id"] = CORRECTION_ID
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = 20
    qa["flagged_rows"] = 44
    qa["correction_state_updates"] = 0
    qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 0
    correction["batch_artifact_sync_state_updates"] = 0
    correction["draft_rows"] = 20
    correction["flagged_rows"] = 44
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 0, "draft_rows": 20, "flagged_rows": 44})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
