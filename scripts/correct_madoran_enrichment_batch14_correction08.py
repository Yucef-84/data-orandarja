"""Apply the eighth HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "5194b30"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-08"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-8"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch14_correction08_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction08_qa.json"
PROVENANCE_BEFORE = 12212

CORRECTIONS = {
    873: {
        "english": "The speaker addresses Aunt Zoulikha and asks her to make one special item. She replies in a colloquial, partly unclear way, explicitly saying that there is none, my child, and that the kofta is finished or has run out. The row does not establish the requesting speaker as a customer.",
        "korean": "화자는 줄리카 이모를 부르며 특별한 것을 하나 만들어 달라고 해요. 이모는 구어적이고 일부 불확실한 방식으로 ‘없어, 얘야’라고 하며 코프타가 다 떨어졌거나 끝났다고 말해요. 이 행은 요청한 화자를 손님으로 확정하지 않아요.",
    },
    874: {
        "english": "One speaker complains or asks whether the kofta has run out only for them. Another speaker explains that these items belong to a singular male owner and were ordered; he will come to take them. They add that, when he comes, the speaker will sort out the matter with him, and tell the addressee to give him one. The roles and genders of the speakers are not fixed by the row.",
        "korean": "한 화자가 코프타가 자기한테만 다 떨어진 것이냐고 불평하듯 물어요. 다른 화자는 이 음식들이 단수 남성 소유자의 것이며 주문된 것이라서 그가 와서 가져갈 거라고 설명해요. 이어 그가 오면 화자가 그와 일을 처리하겠다고 하며 상대에게 그에게 하나 주라고 해요. 이 행은 화자들의 역할과 성별을 확정하지 않아요.",
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
