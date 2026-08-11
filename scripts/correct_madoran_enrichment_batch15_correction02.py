"""Apply the second HeadGPT-directed semantic corrections for MADOran Batch 15."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "03ba2cc"
BATCH_ID = "MADORAN-ENRICH-015"
CORRECTION_ID = "MADORAN-ENRICH-015-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v15-correction-2"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch15_sentno_0897_0960.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch15_correction02_qa.json"
PROVENANCE_BEFORE = 13036

CORRECTIONS = {
    905: {
        "english": "One speaker asks Aunt Halima how she is. Aunt Halima asks the other person in return, ‘How are you, my child? Are you well? Is your health okay?’ The other person replies, ‘Fine, praise be to God,’ then warmly addresses Halima as ‘my mother’ and says, ‘May God protect you.’",
        "korean": "한 화자가 할리마 이모에게 잘 지내느냐고 물어요. 할리마 이모는 상대에게 다시 ‘너는 잘 지내니, 얘야? 괜찮니? 건강은 괜찮니?’라고 물어요. 상대는 ‘괜찮아요, 하나님께 감사해요’라고 답하고 이모를 ‘엄마’처럼 다정하게 부르며 ‘하나님이 지켜 주시길’이라고 말해요.",
    },
    909: {
        "english": "The speaker says Ali is no good for coffee or anything else and knows only what is in the opaque expression ‘filmaba’. They then use the opaque or uncertain expressions ‘fri samt’ and ‘yqllb mkh’, retaining their surface forms, before saying, ‘Yes, let’s leave him alone.’ The row does not force these expressions into ‘free/foolish’ or a definite personality change.",
        "korean": "화자는 알리가 커피도 다른 것도 제대로 못하고 불투명한 표현 ‘filmaba’ 안에 무엇이 있는지만 안다고 해요. 이어 ‘fri samt’와 ‘yqllb mkh’라는 불투명하거나 불확실한 표현을 표면형 그대로 사용한 뒤 ‘그래, 그 사람은 내버려 두자’고 말해요. 이를 ‘공짜·어리석다’나 확정적인 성격 변화로 해석하지 않아요.",
    },
    932: {
        "english": "The speakers agreed on a price with him, but say they cannot change their minds a minute later. They made two items called ‘tartat’, a property certificate, and another item whose name they do not know how to state (‘w mn3rt ki smwha’). They say that giving him all this money—no, it is too much for him.",
        "korean": "화자들은 그와 가격을 합의했지만 1분 뒤에 마음을 바꿀 수는 없다고 해요. 그들은 ‘tartat’이라고 불리는 항목 두 개와 소유권 증서, 그리고 이름을 어떻게 부르는지 모르는 또 다른 항목(‘w mn3rt ki smwha’)을 만들었다고 해요. 이 돈을 그에게 전부 주는 것은, 아니, 그에게 너무 많다고 말해요.",
    },
    933: {
        "english": "The speaker taunts Khairika, asking why he is eating himself. The row preserves the opaque token ‘madama’, says ‘you act like a penis’ (‘daayer ki zebi’), calls his mother a whore (‘mok qahba’), tells him to stay with men, challenges him to talk more and says ‘I will show you who I am’, then says ‘fuck your mother’ (‘nik mok’). The final ‘ya naqsh’ is retained as a source vocative or opaque token.",
        "korean": "화자는 카이리카에게 왜 자기 자신을 먹고 있느냐고 조롱해요. 불투명한 ‘madama’를 그대로 두고, ‘너는 성기처럼 굴어’(‘daayer ki zebi’), ‘네 엄마는 창녀야’(‘mok qahba’)라고 욕하며 남자들과 함께 있으라고 해요. 더 말해 보라며 자신이 누군지 보여 주겠다고 도발한 뒤 ‘네 엄마를 엿먹여’(‘nik mok’)라고 직접 욕해요. 마지막 ‘ya naqsh’도 원문의 호격 또는 불투명 표현으로 보존해요.",
    },
    934: {
        "english": "The speaker tells the addressee to get up in the morning, not leave anyone at peace, leave the speaker alone, and not circle around them. The row then ends with the direct sexual mother insult ‘fuck the [swa] of your mother’ (‘nik swa taʿ mok’); the uncertain surface token ‘swa’ is retained rather than replacing the source content with a generic label.",
        "korean": "화자는 상대에게 아침에 일어나 아무도 편히 두지 말고, 자신을 내버려 두며 주변을 맴돌지 말라고 해요. 이어 ‘네 엄마의 [swa]를 엿먹여’(‘nik swa taʿ mok’)라는 직접적인 모친 대상 성적 욕설로 끝나요. 불확실한 표면 토큰 ‘swa’는 그대로 두고 원문 내용을 일반적인 욕설 표지로 바꾸지 않아요.",
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
