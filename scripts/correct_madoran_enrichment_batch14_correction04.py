"""Apply the fourth HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "d99069f"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-4"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch14_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction04_qa.json"
PROVENANCE_BEFORE = 12155

CORRECTIONS = {
    852: {
        "english": "The speaker asks whether the addressee wants the speaker only temporarily or casually. The speaker says that, under the opaque condition involving ‘mlkta’ and having no family or origin, perhaps the speaker would accept; the expression is not fixed as ‘queen’. The speaker has a mother and a sister and wonders what to do with them. The speaker's heart is burning and asks for a solution, then tells the addressee to ask his wife whether she agrees and come to propose to the speaker so they can see what happens.",
        "korean": "화자는 상대가 자신을 그저 임시적이거나 가벼운 상대로 원하는지 물어요. ‘mlkta’와 가족이나 출신이 없다는 조건이 함께 나오는 부분은 불투명하므로 ‘여왕’으로 확정하지 않고, 그런 경우라면 받아들였을지도 모른다고 해요. 자신에게는 어머니와 자매가 있어 그들과 어떻게 해야 할지 모르겠다고 하며, 마음이 타들어 간다면서 해결책을 물어요. 상대의 아내가 받아들일지 물어본 뒤 자신에게 정식으로 청혼하러 오라고 해요.",
    },
    853: {
        "english": "The speaker asks whether the addressee wants the speaker to demean herself like that. She says she is still young while the addressee is older, wants to preserve herself, and wants to make the addressee's wife comfortable. She says she wants to live. The later clause refers to a separate female third-person subject: if she brought the addressee a girl, would that girl accept sharing herself with the first wife? The referent and turn remain uncertain and are not merged with the speaker.",
        "korean": "화자는 상대가 자신을 그렇게까지 낮추기를 원하는지 물어요. 자신은 아직 젊고 상대는 나이가 더 많다며, 자신을 지키고 상대의 아내도 편하게 해 주고 싶다고 해요. 살아가고 싶다고 말한 뒤, 뒤의 절에서는 별도의 여성 제3자가 상대에게 여자아이를 데려오는 경우를 말해요. 그 여자아이가 첫 아내와 자신을 나누는 일을 받아들이겠느냐는 뜻으로 보이지만, 지시대상과 turn은 불확실하며 화자와 합치지 않아요.",
    },
    854: {
        "english": "The first speaker says the addressee is reproaching her for not having children. After an interjected ‘Me?’, another speaker strongly denies thinking that way, invoking God to cut her tongue, and asks the male addressee to have some empathy. The response turn and speaker gender are kept distinct and uncertain; it is not rendered as an apology.",
        "korean": "첫 화자는 상대가 자신에게 아이가 없다고 비난한다고 말해요. ‘나?’라는 끼어드는 말 뒤에 다른 화자가 그런 식으로 생각하지 않는다며 신에게 자신의 혀를 끊어 달라고 할 정도로 강하게 부인하고, 남성 상대에게 자신을 조금 이해해 달라고 해요. 응답 turn과 화자의 성별은 분리하고 불확실하게 두며, 사과로 번역하지 않아요.",
    },
    855: {
        "english": "The speaker addresses a female listener, saying she understands nothing and may say that her brother has a long reach. The speaker then turns to a male listener, saying that he too is not simple, and asks about his work and dealings with that man. The speaker says that if his wife accepts, nothing will change, and that the person standing before him deserves happiness. The female-to-male addressee shift and the identity of the standing person are preserved without merging them.",
        "korean": "화자는 여성 상대에게 상대가 아무것도 모른다며, 상대가 자신의 남자 형제가 영향력이 크다고 말할지도 모른다고 해요. 이어 남성 상대에게 당신도 만만하지 않다며 그 남자와의 일이나 거래가 무엇인지 물어요. 남성 상대의 아내가 받아들여도 달라질 것은 없고, 그 앞에 서 있는 사람도 행복할 자격이 있다고 해요. 여성에서 남성으로 바뀌는 수신자와 그 앞에 선 사람의 지시대상을 합치지 않아요.",
    },
    858: {
        "english": "The villa originally had almost nothing in it, only belongings. Si Toufik and his wife regularly travel to America to see their children, while the speaker says the speaker's employer never left money at the villa.",
    },
    870: {
        "english": "A person greets Aunt Zoulikha; she asks how the person is, and the person says they are fine. The person reminds her that, as they said, when her bread runs out they will bring bread to her from the bakery. The refusal includes the direct address ‘Rda’; Aunt Zoulikha says the bread from the last time smelled of chicken. ‘My son’ is treated as a familiar address, not an age claim.",
        "korean": "한 사람이 줄리카 이모에게 인사하고, 이모가 잘 지내느냐고 묻자 그 사람은 괜찮다고 답해요. 그 사람은 전에 말했듯 이모의 빵이 떨어지면 빵집에서 빵을 가져다주겠다고 상기시켜요. 거절하는 말에는 ‘Rda’라는 직접 호명이 나오고, 줄리카 이모는 지난번 빵에서 닭 냄새가 났다고 말해요. ‘내 아들’은 친근한 호칭으로 처리하고 나이를 확정하지 않아요.",
    },
    873: {
        "english": "A speaker asks Aunt Zoulikha to make a special item. She says there is no special one and that she has finished the kofta. The row does not establish the requesting speaker as a customer.",
        "korean": "한 화자가 줄리카 이모에게 특별한 것을 하나 만들어 달라고 해요. 이모는 특별한 것은 없고 코프타를 다 만들었다고 해요. 이 행은 요청한 화자를 손님으로 확정하지 않아요.",
    },
    874: {
        "english": "One speaker asks whether all the finished kofta was only for them. Another says the items belong to their owners and were ordered; the owners will come to take them. One item will be handled by the speaker when the person comes, and the addressee is told to give him one. The roles and genders of the speakers, seller, and customer are not fixed by the row.",
        "korean": "한 화자가 완성한 코프타가 전부 자기 것뿐인지 물어요. 다른 화자는 물건들이 주인들의 것이고 주문받은 것이라며 주인들이 와서 가져갈 것이라고 해요. 한 사람이나 물건 하나는 그 사람이 오면 화자가 처리하겠다고 하고, 상대에게 그에게 하나 주라고 해요. 화자들의 역할과 성별을 판매자나 손님으로 확정하지 않아요.",
    },
    875: {
        "english": "The speaker says they would not ask the others if it were not for them; without the opaque expression ‘lizabaj’, the others would have been ‘eaten’ by it. The expression is retained as opaque, and the line is treated as exaggerated social banter rather than a confirmed reference to wasps.",
        "korean": "화자는 자신 때문이 아니라면 상대들에게 부탁하지 않았을 것이라고 해요. 불투명한 표현 ‘lizabaj’가 없었다면 상대들이 그것에게 ‘먹혔을’ 것이라고 과장해 말해요. 그 표현은 그대로 불투명하게 보존하고, 말벌을 가리킨다고 확정하지 않아요.",
    },
    882: {
        "english": "The speaker says they are angry with the female addressee and with themself because, through the speaker's fault, the addressee was deprived of everything. The row does not identify the addressee as Elias; ‘t7rmti’ is preserved as addressing a female addressee.",
        "korean": "화자는 여성 상대에게도 자신에게도 화가 났다고 해요. 자신의 잘못으로 상대가 모든 것을 빼앗겼기 때문이라고 말해요. 이 행에는 엘리아스가 나오지 않으며, ‘t7rmti’는 여성 상대를 가리키는 표현으로 보존해요.",
    },
    894: {
        "english": "The speaker asks the female addressee whether she is not one of us and says that helping is her duty. In a later turn, a speaker threatens to pull out the addressee's tongue, asks whether they understand, and orders them to fetch a slipper (‘bligha’), not a slip of paper. The exchange then shifts to a greeting and a question about Ziguomar; the speaker/addressee turns and speaker gender are not fully certain.",
        "korean": "화자는 여성 상대에게 상대도 우리 중 하나가 아니냐고 물으며 돕는 것이 상대의 의무라고 말해요. 뒤의 발화에서는 화자가 상대의 혀를 뽑겠다고 위협하고, 알아들었느냐고 물으며 종이쪽지가 아니라 슬리퍼(‘bligha’)를 가져오라고 명령해요. 이어 지구마르의 안부를 묻는 인사로 전환되며, 화자·수신자 turn과 화자의 성별은 완전히 확정하지 않아요.",
    },
    896: {
        "english": "The listener asks why they should be quiet and what the other person wants, asking whether they should come every morning with the opaque expression ‘nbwantw’ or something similar; it is not translated as a gift. The speaker apologizes for being wrong and confused about the others, then adds the blessing ‘May God increase your goodness’ (‘Allah ykattar khirk’). The final instruction preserves the opaque/name-like form ‘zino’: the other person is told to go to the house and ‘zine’ or arrange it, and the speaker says they will come shortly; the exact roles remain uncertain.",
        "korean": "상대는 왜 조용히 해야 하고 무엇을 원하는지 묻고, 매일 아침 ‘nbwantw’ 같은 불투명한 것을 가지고 와야 하느냐고 물어요. 이를 선물로 번역하지 않아요. 화자는 자신이 잘못하고 상대를 혼동했다며 사과한 뒤, ‘알라께서 당신의 복을 늘려 주시길’(‘Allah ykattar khirk’)이라고 축복해요. 마지막 지시는 불투명하거나 이름처럼 보이는 ‘zino’ 표현을 보존해, 상대에게 집에 가서 ‘zine’하거나 정리하라고 하고 자신은 곧 오겠다고 해요. 정확한 역할은 불확실해요.",
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
