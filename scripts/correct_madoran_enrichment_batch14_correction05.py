"""Apply the fifth HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "6118f97"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-05"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-5"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch14_correction05_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction05_qa.json"
PROVENANCE_BEFORE = 12178

CORRECTIONS = {
    852: {
        "latin": "mnitk ? lwkan jit mlqta w la ma 3ndish asl blak n9bl bs7 ana 3ndi ma w khti ki ghadi ndir m3ahm . 9lbi rah in7r9 w al7l ? 9wl lmrtk ada 9blt arwa7 tkhtbni tma nshwfw .",
        "english": "The row opens with the direct question ‘mnitk?’, whose exact force is uncertain and is not normalized as a temporary or casual arrangement. It continues with the opaque form ‘mlqta’ and a condition involving having no family or origin; the speaker says perhaps they would accept, without fixing the opaque expression. The speaker has a mother and a sister and wonders what to do with them. The speaker's heart is burning and asks for a solution, then tells the addressee to ask his wife whether she agrees and come to propose to the speaker so they can see what happens.",
        "korean": "이 행은 정확한 의미를 확정할 수 없는 직접 질문 ‘mnitk?’로 시작하며, 이를 임시적이거나 가벼운 관계를 묻는 말로 정규화하지 않아요. 이어 가족이나 출신이 없는 조건과 불투명한 표현 ‘mlqta’가 나오고, 화자는 그런 경우라면 받아들였을지도 모른다고 하지만 그 표현 자체는 확정하지 않아요. 자신에게는 어머니와 자매가 있어 그들과 어떻게 해야 할지 모르겠다고 하며, 마음이 타들어 간다면서 해결책을 물어요. 상대의 아내가 받아들일지 물어본 뒤 자신에게 정식으로 청혼하러 오라고 해요.",
    },
    854: {
        "english": "The first speaker says the addressee is reproaching the speaker for not having children. After an interjected ‘Me?’, another speaker strongly denies thinking that way, invoking God to cut the speaker's tongue, and asks the male addressee to have some empathy. The response turn and speaker gender are kept distinct and uncertain; it is not rendered as an apology.",
    },
    855: {
        "english": "The speaker addresses a female listener, saying she understands nothing and may say that another woman's brother has a long reach. The speaker then turns to a male listener, saying that he too is not simple, and asks about his work and dealings with that man. The speaker says that if his wife accepts, nothing will change, and that the person standing before him is also worth something. The speaker adds, ‘I ask only for peace or happiness.’ The female-to-male addressee shift and the separate third-person brother are preserved.",
        "korean": "화자는 여성 상대에게 상대가 아무것도 모른다며, 다른 여성의 남자 형제가 영향력이 크다고 말할지도 모른다고 해요. 이어 남성 상대에게 당신도 만만하지 않다며 그 남자와의 일이나 거래가 무엇인지 물어요. 남성 상대의 아내가 받아들여도 달라질 것은 없고, 그 앞에 서 있는 사람도 가치가 있다고 말해요. 화자는 이어 ‘나는 평온이나 행복만을 바란다’고 해요. 여성에서 남성으로 바뀌는 수신자와 별도의 제3자 남자 형제를 보존해요.",
    },
    874: {
        "english": "One speaker asks whether all the finished kofta was only for them. Another says the items belong to their single owner and were ordered; the owner will come to take them. One item will be handled by the speaker with him when he comes, and the addressee is told to give him one. The roles and genders of the speakers are not fixed by the row.",
        "korean": "한 화자가 완성한 코프타가 전부 자기 것뿐인지 물어요. 다른 화자는 물건들이 한 주인의 것이고 주문받은 것이라며 그 주인이 와서 가져갈 것이라고 해요. 그가 오면 물건 하나는 화자가 그와 처리하겠다고 하고, 상대에게 그에게 하나 주라고 해요. 이 행은 화자들의 역할과 성별을 확정하지 않아요.",
    },
    875: {
        "english": "The speaker says they would not ask the others if it were not for the speaker; if the speaker had not been there, the others would have been ‘eaten’ by the opaque expression ‘lizabaj’. The expression is retained as opaque, and its role as the eater is not replaced with wasps.",
        "korean": "화자는 자신이 아니었다면 상대들에게 부탁하지 않았을 것이라고 해요. 자신이 없었다면 상대들이 불투명한 표현 ‘lizabaj’에게 ‘먹혔을’ 것이라고 과장해 말해요. 그 표현은 그대로 불투명하게 보존하고, 말벌로 바꾸지 않아요.",
    },
    884: {
        "english": "The first speaker addresses mother and says she did not need to force the man to support or take responsibility for the speaker. Another speaker says, ‘I never forced you on him; your father was happy with you, [opaque expression], and the proof is that he gave you his name. But his family—may God forgive him.’ The direct second-person forms ‘your father’, ‘you’, and ‘gave you’ are preserved, and ‘mwa9f amni’ remains opaque rather than being rendered as definite support.",
        "korean": "첫 화자는 어머니를 부르며 그 남자에게 자신을 부양하거나 책임지라고 강요할 필요가 없었다고 말해요. 다른 화자는 ‘내가 너를 그에게 강요한 적은 없어. 네 아버지는 너를 기뻐했고, [불투명한 표현], 네게 이름을 준 것이 그 증거야. 하지만 그의 가족은—신이 그를 용서하시길’이라고 말해요. ‘네 아버지’, ‘너’, ‘너에게 주었다’라는 2인칭 방향을 보존하고, ‘mwa9f amni’는 확정적인 지지로 번역하지 않고 불투명하게 둬요.",
    },
    886: {
        "english": "The speaker wishes to close and reopen their eyes in a faraway place where no one asks where they came from. They mention the opaque or name-like form ‘3bdla’ while saying they want to forget Elias or that person completely; the exact relation of the form is uncertain. The speaker then addresses Elias as ‘my son’ and asks whether he too will forget the speaker.",
        "korean": "화자는 눈을 감았다가 다시 뜨면 아무도 어디서 왔는지 묻지 않는 먼 곳에 있기를 바라요. 엘리아스 또는 그 사람을 완전히 잊고 싶다고 말하면서 불투명하거나 이름처럼 보이는 ‘3bdla’를 언급하지만, 그 표현의 정확한 관계는 불확실해요. 이어 엘리아스를 ‘내 아들’이라고 부르며 그도 자신을 잊을 것인지 물어요.",
    },
    888: {
        "english": "The speaker says a man has declared that the item cannot be made and says, ‘I need a new one today.’ The speaker asks why they should get involved with unsold goods, then tells the listener to buy a refrigerator or whatever they want.",
        "korean": "화자는 한 남자가 그것은 만들 수 없다고 말했다며, ‘나는 오늘 새것 하나가 필요해’라고 해요. 팔리지 않는 물건에 자신이 왜 관여해야 하느냐고 묻고, 상대에게 냉장고나 원하는 것을 사라고 해요.",
    },
    889: {
        "english": "Someone says they forgot that the woman is a guest at the speaker's home and that she lives with them. The speaker says the speaker's belongings must not be wasted, and tells everyone to manage their own affairs.",
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
