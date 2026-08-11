"""Apply the fifth HeadGPT-directed semantic corrections for MADOran Batch 16."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "26774c8"
BATCH_ID = "MADORAN-ENRICH-016"
CORRECTION_ID = "MADORAN-ENRICH-016-CORRECTION-05"
PROMPT_VERSION = "madoran-source-enrichment-v16-correction-5"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch16_sentno_0961_1024.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_correction05_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch16_correction05_qa.json"
PROVENANCE_BEFORE = 13934

CORRECTIONS = {
    988: {
        "english": "The speaker mentions a Mercedes and an unclear phrase about an almond or a closed item, then asks for everything to be brought so there will be a large hall for the whole family. The closing surface saii bwia is spoken by the same speaker as a vocative or address to Dad, roughly ‘that is it/okay, Dad’; it does not create a separate Dad-agrees turn.",
        "korean": "화자는 메르세데스와 아몬드나 닫힌 물건을 가리키는 불분명한 말을 한 뒤, 가족 모두를 맞이할 큰 홀이 되도록 그것들을 가져오라고 해요. 마지막 표면형 ‘saii bwia’는 같은 화자가 아빠를 호격해 ‘됐어, 아빠’ 또는 ‘좋아, 아빠’라고 말하는 구조로 보존하고, 아빠가 별도로 동의하는 turn을 만들지 않아요.",
    },
    1012: {
        "english": "The long abusive exchange includes the explicit opening surface jabk hw ia w7d khain and the following dwr dwr w ti7 fi mwla alfwl; their exact actor and target remain uncertain. The later clause ghir alli ma bansh fi altri9 ma tl9tw b9ri ma tl9tw djaj ma tl9nw khrfan explicitly mentions what was or was not visible on the road and acts involving cows, chickens, and sheep; its polarity and roles are uncertain, so the surface and clause are retained rather than omitted. The speaker reproaches them with mt7shmwsh, roughly aren't you ashamed or you have no shame, then mentions straw, donkeys, and dogs and asks where everyone is going.",
        "korean": "긴 모욕적 대화에는 ‘jabk hw ia w7d khain’이라는 시작 표면형과 이어지는 ‘dwr dwr w ti7 fi mwla alfwl’이 명시적으로 나오며, 정확한 행위자와 대상은 불확실해요. 뒤의 ‘ghir alli ma bansh fi altri9 ma tl9tw b9ri ma tl9tw djaj ma tl9nw khrfan’ 절은 길에서 보이거나 보이지 않은 것과 소·닭·양을 풀어 놓거나 다루는 행위를 명시적으로 언급하지만 극성과 역할은 불확실하므로 표면형과 절 자체를 누락하지 않아요. 화자는 ‘mt7shmwsh’로 ‘부끄럽지도 않냐’ 또는 ‘부끄러움을 모른다’고 질책하고, 짚·당나귀·개를 언급하며 모두 어디로 가는지 물어요.",
    },
    1019: {
        "topic": "opaque_two_day_comparison_involving_weapon",
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
