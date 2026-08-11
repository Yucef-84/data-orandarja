"""Apply the fourth HeadGPT-directed semantic corrections for MADOran Batch 16."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "ffc23cb"
BATCH_ID = "MADORAN-ENRICH-016"
CORRECTION_ID = "MADORAN-ENRICH-016-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v16-correction-4"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch16_sentno_0961_1024.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch16_correction04_qa.json"
PROVENANCE_BEFORE = 13928

CORRECTIONS = {
    968: {
        "english": "Guests arrive and the speaker asks what is happening. A long multi-turn comic exchange includes the explicit surfaces je suis robot and w allah tkhlswha mam nta; their exact wording and force remain partly uncertain, but the clauses and the possible threat or warning turn are not reduced to a generic payment statement. The exchange also mentions not working on Friday, being driven crazy, looking for a jellaba or traditional robe in the explicit jlabti surface, moving back, following the speaker, and someone wanting to eat the earth.",
        "korean": "손님들이 오자 화자가 무슨 일이냐고 물어요. 긴 여러 turn의 희극적 대화에는 ‘je suis robot’과 ‘w allah tkhlswha mam nta’라는 명시적 표면형이 나오며 정확한 표현과 힘은 일부 불확실하지만, 각 절과 가능한 위협·경고 화행을 단순한 결제 이야기로 축약하지 않아요. 금요일에는 일하지 않는다는 말, 미치겠다는 말, 명시적 표면형 ‘jlabti’로 젤라바나 전통 로브를 찾는 말, 물러서기, 따라오라는 말, 땅을 먹고 싶다는 말도 이어져요.",
    },
    983: {
        "english": "The exchange contains a question and answer: khbrni ... sha 9ltlhm? asks, ‘Tell me, what did you tell them?’ and ma 9ltlhmsh answers, ‘I did not tell them because I wanted to consult you,’ with the feminine second-person addressee in ntia preserved. The speaker firmly refuses to give the daughter away. The exchange also says, ‘Your mother is nagging,’ before revealing that a group from the Sons of the Day tribe came for their son Bisha, who studied with the speaker; one voice says to give her to him. The question-to-answer direction is preserved.",
        "korean": "이 대화에는 질문과 응답이 나와요. ‘khbrni ... sha 9ltlhm?’은 ‘말해 봐, 그들에게 뭐라고 했어?’라고 묻고, ‘ma 9ltlhmsh’는 ‘아무 말도 안 했어. 너와 상의하려고 했어’라고 답해요. 여기서 ‘ntia’가 표시하는 여성 2인칭 청자에게 직접 상의한다는 방향을 보존하고 제3의 여성 청자를 추가하지 않아요. 화자는 자신의 딸을 절대 주지 않겠다고 단호하게 거절해요. 이어 ‘네 엄마가 잔소리하고 있다’는 절이 나오고, ‘울라드 나하르’ 부족 사람들이 아들 비샤를 위해 왔으며 그가 화자와 함께 공부했다는 사실이 드러나요. 한 목소리는 딸을 그에게 주라고 해요. 질문에서 응답으로 이어지는 방향을 보존해요.",
    },
    998: {
        "english": "The speaker asks what this talk is and includes the opaque surface bwiaz before saying désolé. The exact meaning of bwiaz is not fixed, but the surface is retained alongside the French apology as code-switching.",
        "korean": "화자가 이런 말이 무슨 말이냐고 묻고 ‘bwiaz’라는 불투명한 표면형을 말한 뒤 ‘désolé’라고 해요. bwiaz의 정확한 뜻은 확정하지 않고 프랑스어 사과 표현과 함께 코드 스위칭 표면형으로 보존해요.",
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
