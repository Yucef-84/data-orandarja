"""Apply the third HeadGPT-directed semantic corrections for MADOran Batch 15."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "41849b1"
BATCH_ID = "MADORAN-ENRICH-015"
CORRECTION_ID = "MADORAN-ENRICH-015-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v15-correction-3"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch15_sentno_0897_0960.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch15_correction03_qa.json"
PROVENANCE_BEFORE = 13046

CORRECTIONS = {
    903: {
        "english": "The speaker says the people have lived there for more than a year, paid their rent, eaten and drunk there, and have a car, and asks how the matter can be ignored. Tomorrow they will send Hussein after them to bring back the hidden or concealed things concerning them, using the opaque surface expression ‘dasa wa madsusa’; it is not normalized as a dossier.",
        "korean": "화자는 그 사람들이 1년 넘게 그곳에 살면서 임대료를 내고 먹고 마셨으며 차도 있다고 말하며, 이 일을 어떻게 무시할 수 있느냐고 물어요. 내일 후세인을 그들 뒤에 보내 그들에 관한 숨겨지거나 감춰진 것을 가져오게 하겠다고 하며, 불투명한 표면 표현 ‘dasa wa madsusa’를 서류(dossier)로 확정하지 않아요.",
    },
    910: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    918: {
        "english": "The speaker says the press has turned the whole world against the addressee. They mention the uncertain source form ‘7darat’ (حضارات), then say they will bring French code-switched ‘des machines’, machines that work by themselves, so they will not need workers. They sarcastically ask what the workers they have at the factory will do—polish the speaker’s shoes.",
        "korean": "화자는 언론이 상대에게 등을 돌리게 만들었다고 해요. 정확한 해석이 불확실한 원문 표면형 ‘7darat’(حضارات)을 언급한 뒤, 프랑스어가 섞인 ‘des machines’, 즉 혼자 작동하는 기계를 가져와 노동자가 필요 없게 하겠다고 해요. 지금 공장에 있는 노동자들은 무슨 일을 하겠느냐, 자신의 구두를 닦겠느냐고 비꼬아요.",
    },
    925: {
        "english": "The speaker says, in the first person, ‘I asked Dalila to bring us sandwiches.’ They say that despite having all their money, they are still eating Dalila’s sandwiches and ask why they do not store the money there.",
        "korean": "화자는 1인칭으로 ‘내가 달릴라에게 우리에게 샌드위치를 가져오라고 부탁했어’라고 말해요. 가진 돈이 모두 있는데도 계속 달릴라의 샌드위치를 먹고 있다며, 왜 돈을 이곳에 보관하지 않는지 물어요.",
    },
    928: {
        "english": "The speaker tells Hosni that it is a serious matter and invokes a generous Lord, but the threat-like wording remains unclear. One voice says they will not bring the sandwiches up to them, another voice tells someone to take them upstairs quickly and not forget the money, and a voice says, ‘I do not work for free, my daughter.’ The speaker then addresses their mother: ‘Okay, Mom, do not worry.’ Hot garantika is served. No seller role is assigned to any voice.",
        "korean": "화자는 호스니에게 큰일이라며 자비로운 신을 언급하지만 위협처럼 들리는 표현은 불분명해요. 한 목소리는 샌드위치를 그들에게 올려 주지 않겠다고 하고, 다른 목소리는 빨리 위로 가져가고 돈을 잊지 말라고 해요. 또 한 목소리는 ‘나는 공짜로 일하지 않아, 얘야’라고 말해요. 이어 화자가 어머니에게 ‘알겠어, 엄마, 걱정하지 마’라고 말해요. 어떤 목소리도 판매자라고 확정하지 않아요. 뜨거운 가란티카를 내요.",
    },
    932: {
        "english": "The speakers agreed on a price with him, but say they cannot change their minds a minute later. The man referred to by ‘with him’ made two items called ‘tartat’ for them, a property certificate, and another item whose name they do not know how to state (‘w mn3rt ki smwha’). They say that giving him all this money—no, it is too much for him.",
        "korean": "화자들은 그와 가격을 합의했지만 1분 뒤에 마음을 바꿀 수는 없다고 해요. ‘그와 함께’라는 앞의 지칭으로 연결되는 남성이 화자들을 위해 ‘tartat’이라고 불리는 항목 두 개와 소유권 증서, 그리고 이름을 어떻게 부르는지 모르는 또 다른 항목(‘w mn3rt ki smwha’)을 만들었다고 해요. 이 돈을 그에게 전부 주는 것은, 아니, 그에게 너무 많다고 말해요.",
    },
    934: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    946: {
        "english": "The Frenchman reacts, ‘Oh, this is ziqo,’ or ‘Oh, this one is ziqo.’ The utterance is a reaction or confirmation, not a question asking whether it is ziqo.",
        "korean": "프랑스인이 ‘아, 이건 지코네’ 또는 ‘아, 이게 지코야’라고 반응해요. 이 발화는 반응이나 확인이지, 지코인지 묻는 질문으로 확정하지 않아요.",
    },
    957: {
        "english": "A speaker says, ‘Please, welcome,’ welcomes the group, tells them not to worry, and says they are going to inform the tribal sheikh and return. The row does not identify the speaker as a host or householder.",
        "korean": "한 화자가 ‘어서 오세요, 환영해요’라고 일행을 맞이하고 걱정하지 말라고 해요. 부족 셰이크에게 알리고 돌아오겠다고 말하며, 이 행만으로 화자를 주인이나 호스트라고 확정하지 않아요.",
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
