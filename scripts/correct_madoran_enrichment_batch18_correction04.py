"""Apply the remaining source-close clause corrections for MADOran Batch 18."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch18 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "e625f20"
BATCH_ID = "MADORAN-ENRICH-018"
CORRECTION_ID = "MADORAN-ENRICH-018-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v18-correction-4"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch18_correction04_qa.json"
PROVENANCE_BEFORE = 15940

CORRECTIONS = {
    1143: {
        "english": "The speaker begins, ‘I am telling you all, forgive me. Hazim, I want to ask you something: I want to become Indian like you.’ They preserve the explicit opaque turn, ‘I do not hear, Ania,’ then ask whether the listener was alone or with a group, say there were some with the speaker and some with the listener, and tell the other person to speak. They repeat, ‘I want to become Indian like you, forgive me,’ followed by the explicit turn ‘Do not become Indian; we are like you.’ They call Akasha: ‘Akasha, come, take him,’ preserving dwh as a take-away direction. The speaker says ‘God brought him,’ asks the listener to remember the day the listener took them, and asks where that happened. They say the listener and a friend tied and brought the speaker to Madam, then say ‘Fine, I remembered’ before threatening to make a tagine and roast the listener over fire. Every explicit turn, actor, and threat remains.",
        "korean": "화자는 ‘너희에게 말하니 용서해 줘. Hazim, 너에게 물어볼 게 있어. 너처럼 인도인이 되고 싶어’라고 시작해요. 불투명하지만 명시적인 ‘나는 듣지 못해, Ania’라는 turn을 보존한 뒤 상대가 혼자였는지 집단과 함께였는지 묻고, 자신과 함께 몇몇이 있었고 상대와 함께 몇몇이 있었다고 하며 상대에게 말하라고 해요. ‘너처럼 인도인이 되고 싶어, 용서해 줘’라고 반복하고 ‘인도인이 되지 마. 우리는 너희와 같아’라는 명시 turn도 보존해요. Akasha를 부르며 ‘Akasha, 어서 와서 그를 데려가’라고 하여 dwh를 데려가는 방향으로 유지해요. 화자는 ‘하느님이 그를 데려왔어’라고 하고 상대에게 자신을 데려간 날을 기억하느냐고 물으며 어디로 데려갔는지 묻어요. 상대와 친구가 자신을 묶어 Madam에게 데려왔다고 한 뒤 ‘그래, 기억났어’라고 말하고 타진을 만들고 불 위에서 상대를 굽겠다고 위협해요. 모든 명시 turn·행위자·위협을 보존해요.",
    },
    1146: {
        "english": "Mr Hazim is addressed: ‘Mr Hazim, I want to ask you: did you know the spy who was making trouble?’ The answer is, ‘Yes, I knew him, but I will leave it as a surprise—une surprise.’ The speaker then uses father/donkey/brother vocatives and says, ‘If you remain still and do not budge, by God I will give you every day a bidon of water and a kilo of grain.’ The final ‘Oh donkey, my brother, do not budge’ is a separate repeated command.",
        "korean": "화자는 Hazim 씨에게 ‘Hazim 씨, 물어보고 싶어. 문제를 일으키던 스파이를 알고 있었어?’라고 해요. 대답은 ‘응, 알고 있었어. 하지만 그건 놀라운 일, une surprise로 남겨 둘 거야’예요. 이어 아버지·당나귀·형제 호칭으로 상대를 부르며 ‘네가 움직이지 않고 꼼짝하지 않으면, 하느님께 맹세코 매일 물 한 통과 곡식 1킬로를 줄게’라고 해요. 마지막의 ‘오, 당나귀 같은 형제야, 꼼짝하지 마’는 별도의 반복 명령으로 보존해요.",
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
