"""Apply the sixth HeadGPT-directed semantic corrections for MADOran Batch 16."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "a842555"
BATCH_ID = "MADORAN-ENRICH-016"
CORRECTION_ID = "MADORAN-ENRICH-016-CORRECTION-06"
PROMPT_VERSION = "madoran-source-enrichment-v16-correction-6"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch16_sentno_0961_1024.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_correction06_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch16_correction06_qa.json"
PROVENANCE_BEFORE = 13939

CORRECTIONS = {
    966: {
        "english": "The other speaker rejects the ogre idea and lists several household or food-preparation tasks. The explicit shwtti bwzlalif refers to singeing or scorching bouzelouf, the head of a sheep or other sacrificed animal, rather than generic cutting meat; the exchange also mentions making عصبان, washing tripe or skins, and cleaning something. The French-derived form au moins (at least) appears in the remaining opaque description, which says another woman is at least working; the rest contains unclear grooming wording.",
        "korean": "상대는 괴물 이야기를 받아들이지 않고 여러 집안일이나 음식 준비를 나열해요. 명시적인 ‘shwtti bwzlalif’는 일반적인 고기 손질이 아니라 양머리나 다른 희생동물 머리인 bouzelouf를 불에 그슬리거나 태우는 조리 작업을 가리켜요. 이어 عصبان을 만들고 내장이나 가죽을 씻고 무언가를 닦았다는 말이 나와요. 남은 불투명한 표현에는 프랑스어계 ‘au moins’(‘적어도’)가 나타나며, 다른 여성이 적어도 일하고 있다는 말로 이어져요. 나머지 몸단장 관련 표현은 불분명해요.",
    },
    992: {
        "english": "The speaker blesses the listener and jokes that they are full of feathers and look like a dandou or dindon, a turkey. The feather comparison and the turkey meaning are preserved rather than treating dandwa as an opaque personal name.",
        "korean": "화자는 상대를 축복하며 상대가 깃털로 가득하고 ‘dandwa’처럼 보인다고 농담해요. 여기서 dandwa는 불투명한 고유명사가 아니라 프랑스어계 dindon에 해당하는 칠면조를 가리키는 표현으로, 깃털 비교와 칠면조 의미를 보존해요.",
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
    return engine.apply()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
