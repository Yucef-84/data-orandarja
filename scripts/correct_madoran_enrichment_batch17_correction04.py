"""Apply the remaining HeadGPT-directed corrections for MADOran Batch 17."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch17 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "9f777f8"
BATCH_ID = "MADORAN-ENRICH-017"
CORRECTION_ID = "MADORAN-ENRICH-017-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v17-correction-4"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch17_correction04_qa.json"
PROVENANCE_BEFORE = 14959

CORRECTIONS = {
    1053: {
        "english": "The speaker says they do not know what happened and asks where the listener was, then addresses a sheikh. They report that the girl went to the river and has not appeared since morning; this is distinct from the later statement that she is at the lac or lake. The speaker then says to hurry and go look at her, while retaining the French-derived surface lac.",
        "korean": "화자는 무슨 일이 생겼는지 모르겠다며 상대가 어디 있었는지 묻고 셰이크를 불러요. 소녀가 강으로 갔고 아침부터 나타나지 않았다고 말하며, 이는 뒤에서 소녀가 lac 또는 호수에 있다고 말하는 것과 별개의 사건이에요. 이어 서둘러 가서 보라고 하며 프랑스어계 표면형 lac을 보존해요.",
    },
    1063: {
        "english": "The speakers bargain between 105 and 130 doro. The higher offer is said to include les impôts, taxes, and TVA, VAT, as well as wages for a worker, future work, food, and everything. One speaker says they will bring in a worker and another worker, preserving the opaque khdam-khdakhwr surface without assigning the role to the speaker. Later turns accept or reject the offer, say the other person has made things difficult, and promise to take care of them next time. Another voice says the item is dry in its fat and meat; the object remains unfixed.",
        "korean": "화자들은 105도로나 130도라 사이에서 흥정해요. 높은 가격에는 ‘les impôts’인 세금과 ‘TVA’인 부가가치세, 일꾼의 임금, 앞으로 들어올 일, 먹을 것 등이 포함된다고 해요. 한 화자는 일꾼 한 명과 또 다른 일꾼을 들이겠다고 하며, 불투명한 khdam-khdakhwr 표면을 보존하고 그 역할을 화자 자신에게 배정하지 않아요. 뒤의 turn에서는 제안을 받아들이거나 거절하고 상대가 일을 어렵게 만들었다고 하며 다음번에는 잘 돌보겠다고 해요. 다른 목소리는 그 물건이 지방과 살이 말랐다고 하며 대상을 확정하지 않아요.",
    },
    1066: {
        "english": "The speaker says they knew the Sons of the Day would do it and that it must be him who took her, him and his father. They order someone to bring her back, tell others to be quiet, ask for a turban, and then say, ‘Hurry; it is better than me going myself.’ The epistemic uncertainty and the hurry direction are retained.",
        "korean": "화자는 ‘울라드 나하르’가 그 일을 할 줄 알았으며 그녀를 데려간 사람은 그와 그의 아버지일 것이라고 추정해요. 누군가에게 그녀를 데려오라고 명령하고 조용히 하라고 하며 터번을 달라고 한 뒤, ‘서둘러. 내가 직접 가는 것보다 낫다’고 말해요. 추정의 말투와 서두르라는 방향을 보존해요.",
    },
    1068: {
        "english": "The speaker tells Mr Hazim not to be stingy or withhold the daughter and says, ‘I came so you would give me the daughter.’ They call his heart white, curse the devil, and demand that the daughter be returned to them. Another voice asks, ‘Who will return the daughter to you?’ The speaker accuses them of kidnapping her and reports that her mother told her in the morning to wash clothes in the river before she disappeared.",
        "korean": "화자는 하짐 씨에게 딸을 두고 인색하게 굴거나 버티지 말라며 ‘내가 왔으니 네가 나에게 딸을 줘’라고 해요. 하짐의 마음이 하얗다고 말하고 악마를 저주하며 딸을 자신에게 돌려달라고 요구해요. 다른 목소리는 ‘누가 너에게 딸을 돌려주겠어?’라고 되묻고, 화자는 상대가 딸을 납치했다고 비난해요. 딸의 어머니가 아침에 강에서 빨래하라고 했고 그 뒤 딸이 사라졌다고 말해요.",
    },
    1086: {
        "english": "One speaker says, ‘I told you, they did it; rely on us,’ while another voice denies relying on anyone. They ask how they will attack us and answer that there are dogs, only talk, repeating the question about how they will attack. Another speaker says they want to hit you with a flitshat, ground-to-ground, repeating ard ard, and asks whether the 3idan are present. A reply says no, the 3idan have slept. The exchange then preserves the explicit hidden-ember clauses: they will hit them with a hidden ember, followed by the correction that they should hit them with a hidden ember in the other order. The later opaque surfaces raki 9albtha, 9lbwa khir, and the address ya stwta are also retained without compression.",
        "korean": "한 화자는 ‘내가 말했잖아, 그들이 그 일을 했어. 우리에게 의지해’라고 하지만 다른 목소리는 아무에게도 의지하지 않았다고 부인해요. 어떻게 우리를 공격할지 묻고 개들이 있지만 말뿐이라고 답하며 공격 방법을 다시 물어요. 다른 화자는 flitshat으로 너희를 치고, 지대지 방식으로, ard ard라고 반복하며 3idan이 있는지 물어요. 대답은 아니라고 하며 3idan이 잠들었다고 해요. 이어 숨겨진 불씨로 그들을 치겠다는 절과, 숨겨진 불씨로 쳐야 한다는 어순 교정 turn을 그대로 보존해요. 뒤의 불투명한 raki 9albtha, 9lbwa khir와 ya stwta 호칭도 압축하지 않아요.",
    },
    1065: {
        "enrichment_state": "draft",
    },
    1077: {
        "enrichment_state": "draft",
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
    status["counts"]["enrichment_draft_rows"] = 7
    status["counts"]["enrichment_flagged_rows"] = 758
    status["enrichment_correction_id"] = CORRECTION_ID
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = 7
    qa["flagged_rows"] = 57
    qa["correction_state_updates"] = 2
    qa["correction_history"][-1]["state_updates"] = 2
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 2
    correction["batch_artifact_sync_state_updates"] = 2
    correction["draft_rows"] = 7
    correction["flagged_rows"] = 57
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 2, "draft_rows": 7, "flagged_rows": 57})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
