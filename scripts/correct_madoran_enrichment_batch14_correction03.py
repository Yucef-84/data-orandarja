"""Apply the third HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "ffed34b"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-3"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch14_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction03_qa.json"
PROVENANCE_BEFORE = 12127

CORRECTIONS = {
    836: {
        "english": "The speaker asks why the addressee is carrying this item to Nariman in the morning and says Nariman could have combed the addressee's hair; the place will open first. The speaker's gender is not established.",
        "korean": "화자는 상대가 왜 아침에 이 물건을 나리만에게 들고 가느냐고 묻고, 나리만이 상대의 머리를 빗어 줄 수도 있었다고 말해요. 그곳이 먼저 문을 열 것이라고 덧붙여요. 화자의 성별은 확정하지 않아요.",
    },
    838: {
        "english": "The speaker says goodbye to a female addressee and wishes her a good morning. The addressee returns the greeting and asks how the speaker is; the speaker answers that they are fine. The speaker's gender is not established.",
        "korean": "화자는 여성 상대에게 작별 인사를 하고 좋은 아침이 되라고 해요. 상대가 인사를 돌려주며 화자는 어떠냐고 묻고, 화자는 괜찮다고 답해요. 화자의 성별은 확정하지 않아요.",
    },
    845: {
        "english": "He sold them and told me to wait a little because an older woman needed them; the he-to-me direction is preserved.",
        "korean": "그가 그것들을 팔았고, 한 노년 여성이 필요로 했으니 나에게 조금 기다리라고 말했다고 해요. 그가 말하고 내가 기다리는 방향을 보존해요.",
    },
    852: {
        "english": "The speaker asks whether the addressee wants her only temporarily or casually. She says that if she were a queen and had no family, perhaps she would accept, but she has a mother and a sister and wonders what she would do with them. Her heart is burning and she asks for a solution. She tells the addressee to ask his wife whether she agrees, then come to propose to her so they can see what happens.",
        "korean": "화자는 상대가 자신을 그저 임시적이거나 가벼운 상대로 원하는지 물어요. 자신이 여왕이고 가족이 없다면 받아들였을지도 모르지만, 자신에게는 어머니와 자매가 있어 그들과 어떻게 해야 할지 모르겠다고 해요. 마음이 타들어 간다며 해결책을 묻고, 상대의 아내가 받아들일지 물어본 뒤 자신에게 정식으로 청혼하러 오라고 해요.",
    },
    853: {
        "english": "The speaker asks whether the addressee wants her to demean herself like that. She says she is still young while the addressee is older, wants to preserve herself, and will make the addressee's wife comfortable. She says she wants to live and asks what would happen if she brought the addressee a girl or daughter; the turn is not assigned to a man as speaker.",
        "korean": "화자는 상대가 자신을 그렇게까지 낮추기를 원하는지 물어요. 자신은 아직 젊고 상대는 나이가 더 많다며, 자신을 지키고 상대의 아내도 편하게 해 주고 싶다고 해요. 살아가고 싶다며 자신이 상대에게 여자아이 또는 딸을 데려오면 어떻게 되겠느냐고 물어요. 화자를 남성으로 확정하지 않아요.",
    },
    854: {
        "english": "The speaker says the addressee is reproaching her for not having children. The speaker then strongly denies thinking that way, invoking God to cut off her tongue, and asks the male addressee to have some empathy; this is not an apology by the other person.",
        "korean": "화자는 상대가 자신에게 아이가 없다고 비난한다고 말해요. 이어 그런 식으로 생각하지 않는다며 신에게 자신의 혀를 끊어 달라고 할 정도로 강하게 부인하고, 남성 상대에게 자신을 조금 이해해 달라고 해요. 상대방의 사과로 바꾸지 않아요.",
    },
    861: {
        "english": "The listener says, ‘Forgive me, I did not understand you,’ and says the man never approached or hit them. When he came to check on them occasionally, he brought food, loosened their restraints, and let them go to the bathroom.",
        "korean": "상대는 ‘미안해, 내가 너를 이해하지 못했어’라고 말하고, 그 남자가 자신에게 다가오거나 때린 적은 없다고 해요. 가끔 확인하러 올 때 음식을 가져오고 묶인 것을 풀어 주며 화장실에 가게 했다고 말해요.",
    },
    868: {
        "english": "The speaker addresses Toufik as a brother and says they are not the one who will lose out or be ruined in dealing with him; the exact sense of this expression is uncertain. The speaker insults him, says the money will reach him, tells him to shut up, and threatens to plant something in his head; the exact turn boundaries remain somewhat uncertain.",
        "korean": "화자는 투피크를 형제라고 직접 부르며 자신이 그와 엮여 손해를 보거나 망할 사람은 아니라고 말해요. 이 표현의 정확한 의미는 불확실해요. 투피크를 모욕하고 돈이 그에게 도착할 것이라고 하며 입을 다물라고 하고, 그의 머리에 무엇인가를 박겠다고 위협해요. 정확한 turn 경계는 일부 불확실해요.",
    },
    872: {
        "topic": "telling_someone_to_work",
    },
    876: {
        "english": "The speaker says they would normally receive a percentage, then tells the addressee to work for themself like a man rather than come there to act tough with women. A command tells one addressee to shut up, and a later familiar address tells someone to leave; the exact speaker/addressee boundaries are uncertain. The familiar form ‘wldi Tito’ does not establish a boy's age.",
        "korean": "화자는 원래 수수료나 비율을 받아야 하지만, 상대에게 여자들 앞에서 허세를 부리러 오지 말고 남자답게 스스로 일하라고 해요. 한 상대에게 입을 다물라고 하고 뒤의 친근한 호칭으로 누군가에게 가라고 하지만, 정확한 화자·수신자 경계는 불확실해요. ‘wldi Tito’라는 친근한 표현만으로 소년의 나이를 확정하지 않아요.",
    },
    880: {
        "english": "The speaker asks the female addressee why she came and says it is none of her business. After seeing how a man spoke to them, the speaker tells the addressee to return to work. The speaker's gender is not established.",
        "korean": "화자는 여성 상대에게 왜 왔고 무슨 상관이냐고 물어요. 한 남자가 자신들에게 어떻게 말했는지 봤으니 상대에게 일하러 돌아가라고 해요. 화자의 성별은 확정하지 않아요.",
    },
    883: {
        "english": "The speaker addresses someone as ‘my son’ and refers to money and property. The speaker hopes that the son will graduate from university tomorrow, find work, and compensate the speaker for everything. A later statement about a man who never made the speaker feel that he was the speaker's father has an uncertain or shifted referent and is not merged with the son.",
    },
    892: {
        "english": "The speaker asks why they should contribute from their savings. The speaker says that the speaker and the addressee are not the same: the addressee saves for marriage, while the speaker saves for rent. The speaker wants to open a cosmetics shop, improve their situation a little, and escape the misery they are in. The entire contrast is kept as one speaker's continuous turn; French/code-switched forms in the source remain flagged.",
        "korean": "화자는 왜 자신이 모은 돈에서 내야 하느냐고 물어요. 자신과 상대는 같지 않다며, 상대는 결혼을 위해 모으고 자신은 집세를 위해 모은다고 말해요. 화장품 가게를 열어 형편을 조금 나아지게 하고 지금의 가난에서 벗어나고 싶다고 해요. 이 대비 전체를 한 화자의 연속 발화로 보존하고, 원문의 프랑스어·코드 스위칭 형태는 flag로 남겨요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    893: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    894: {
        "english": "The speaker asks the female addressee whether she is not one of us and says that helping is her duty. In a later turn, a speaker threatens to pull out the addressee's tongue, asks whether they understand, and orders them to fetch a slip. The exchange then shifts to a greeting and a question about Ziguomar; the speaker/addressee turns and speaker gender are not fully certain.",
        "korean": "화자는 여성 상대에게 상대도 우리 중 하나가 아니냐고 물으며 돕는 것이 상대의 의무라고 말해요. 뒤의 발화에서는 화자가 상대의 혀를 뽑겠다고 위협하고, 알아들었느냐고 물으며 종이쪽지를 가져오라고 명령해요. 이어 지구마르의 안부를 묻는 인사로 전환되며, 화자·수신자 turn과 화자의 성별은 완전히 확정하지 않아요.",
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
