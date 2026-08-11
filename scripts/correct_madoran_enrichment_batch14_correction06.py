"""Apply the sixth HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "f4c4db2"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-06"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-6"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch14_correction06_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction06_qa.json"
PROVENANCE_BEFORE = 12195

CORRECTIONS = {
    847: {
        "english": "Asked where they were, the speaker says they were working on a purchase. Another voice tells them to get up, come to their senses, and do something with their life instead of sitting inactive; the wording is not normalized as ‘stop making excuses’.",
        "korean": "어디 있었느냐는 질문에 화자는 구매 일을 처리하고 있었다고 해요. 다른 목소리는 일어나서 정신을 차리고 인생에서 무언가를 하라고 해요. 가만히 앉아 아무것도 하지 말라는 뜻으로 보존하며 ‘변명하지 말라’고 확정하지 않아요.",
    },
    863: {
        "english": "The listener says this was stated in the first report: they could not shout because the man was carrying a weapon beneath an unspecified referent, but in fairness he never used it. They called the villa owners, who said they would enter with the opaque expression ‘fbrwmi fwl’; its exact wording and procedure are uncertain, so the surface form is retained. No coat or other garment is added.",
        "korean": "상대는 첫 번째 조서에 그렇게 말했다며, 그 남자가 불특정한 대상 아래 무기를 들고 있어 소리칠 수 없었지만 공정하게 말하면 그것을 사용한 적은 없다고 해요. 별장 주인에게 전화하자 불투명한 표현 ‘fbrwmi fwl’을 가지고 들어가겠다고 했다고 말해요. 정확한 표현과 절차는 불확실해 표면형을 보존하며, 코트나 다른 의복을 추가하지 않아요.",
    },
    866: {
        "english": "The speaker says Ali will not give up his rights and says they are afraid of the opaque expression ‘li9ar3 twfi9’, which may involve waiting around Toufik; the exact subject and structure are uncertain. They ask what the matter is and tell their friend to look.",
        "korean": "화자는 알리가 자신의 권리를 포기하지 않을 것이라며, 투피크 주변에서 기다리는 것과 관련될 수 있는 불투명한 표현 ‘li9ar3 twfi9’을 두려워한다고 말해요. 정확한 주체와 구조는 불확실해요. 무슨 일인지 묻고 친구에게 보라고 해요.",
    },
    879: {
        "english": "The speaker tells the other person to go to the café because the speaker is coming. They swear the matter is not finished, then tell the addressee, in effect, ‘If you do not like my situation, go and complain or report it,’ before telling them to go. An apology and a payment-related exchange follows.",
        "korean": "화자는 자신이 가고 있으니 상대에게 카페로 가라고 해요. 일이 끝나지 않았다고 맹세한 뒤, 상대에게 ‘내 상황이 마음에 들지 않으면 가서 항의하거나 신고해’라는 뜻으로 말하고 가라고 해요. 이어 사과와 계산에 관한 말이 오가요.",
    },
    887: {
        "english": "The speaker addresses Dalila and tells her to call her sister because the speaker needs her. After a brief clarification of the sister's name and an instruction to speak to mother, the speaker asks each woman to contribute three hundred thousand to buy a refrigerator, recalling that they had said repairing one would be better.",
        "korean": "화자는 달릴라를 직접 부르며 자신에게 필요한 달릴라의 자매에게 전화하라고 해요. 자매의 이름을 잠깐 확인하고 엄마에게 말하라고 한 뒤, 냉장고를 사려고 각자 30만씩 내 달라고 하며 전에 냉장고를 수리하는 것이 더 낫다고 했던 일을 떠올려요.",
    },
    888: {
        "english": "The speaker says a man has declared that the item cannot be repaired and says, ‘I need a new one today.’ The speaker asks why they should get involved with unsold goods, then tells the listener to buy a refrigerator or whatever they want.",
        "korean": "화자는 한 남자가 그것은 수리할 수 없다고 말했다며, ‘나는 오늘 새것 하나가 필요해’라고 해요. 팔리지 않는 물건에 자신이 왜 관여해야 하느냐고 묻고, 상대에게 냉장고나 원하는 것을 사라고 해요.",
    },
    891: {
        "english": "The speaker tells the female addressee to be ashamed or keep some dignity, then says the only thing the other person puts in is money. The other woman refuses to give even a coin and says she does not touch the money she saves.",
        "korean": "화자는 여성 상대에게 부끄러운 줄 알거나 체면을 차리라고 말한 뒤, 상대가 넣는 것은 돈뿐이라고 해요. 상대 여성은 한 푼도 주지 않겠다며 자신이 모은 돈에는 손대지 않는다고 말해요.",
    },
}


def apply():
    engine.BASE_COMMIT = BASE_COMMIT
    engine.CORRECTION_ID = CORRECTION_ID
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.CORRECTION_QA_OUT = CORRECTION_QA_OUT
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.PROVENANCE_BEFORE = PROVENANCE_BEFORE
    engine.CORRECTIONS = CORRECTIONS
    return engine.apply()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
