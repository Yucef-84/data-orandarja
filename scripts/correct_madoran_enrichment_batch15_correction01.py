"""Apply the first HeadGPT-directed semantic corrections for MADOran Batch 15."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "874aace"
BATCH_ID = "MADORAN-ENRICH-015"
CORRECTION_ID = "MADORAN-ENRICH-015-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v15-correction-1"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch15_sentno_0897_0960.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch15_correction01_qa.json"
PROVENANCE_BEFORE = 12981

CORRECTIONS = {
    897: {
        "english": "The speaker tells the listener not to concern themselves about Zino, saying the listener knows what he is like. The speaker says they are not upset with their younger brother Zino, invites the listener to have coffee, and says they are tired. They ask the listener to come while they go upstairs to shower and return to talk with their brother.",
        "korean": "화자는 상대에게 지노는 신경 쓰지 말라고 하며, 지노가 어떤 사람인지 상대도 안다고 해요. 지노는 어린 남동생이고 그에게 화난 것이 아니라며 커피를 마시라고 해요. 자신은 피곤하다고 하면서 상대에게 오라고 하고, 위층에 올라가 샤워한 뒤 동생과 이야기하고 돌아오겠다고 해요.",
    },
    898: {
        "english": "The speaker tells the other person to rest and let them go, saying they are tired and will go upstairs to rest. They offer to pay for the coffee later, ask what the other person is carrying, and identify it as a printer, the French code-switched ‘imprimante’. They ask what the other person wants to do with it.",
        "korean": "화자는 상대에게 쉬라고 하며 자신을 보내 달라고 해요. 피곤해서 위층에 올라가 쉬겠다고 하고 나중에 커피값을 내겠다고 해요. 상대가 무엇을 들고 있는지 묻고, 그것이 프랑스어가 섞인 ‘imprimante’, 즉 프린터라고 하며 그것으로 무엇을 하려는지 물어요.",
    },
    899: {
        "english": "The speaker says the printer is faulty. They found it as a used or bargain item at an ‘occasion’ sale, a French code-switched expression, and Zino understands the relevant matters and will redo it so they can sell it again. The other person tells them to put it there and offers to buy it from them.",
        "korean": "화자는 프린터가 고장 났다고 해요. 그것을 프랑스어가 섞인 ‘occasion’, 즉 중고·할인 물건으로 찾았고, 지노가 관련된 일을 이해하니 다시 손봐서 재판매하겠다고 해요. 상대는 그것을 여기에 놓으라며 자신이 사겠다고 해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    908: {
        "english": "The speaker asks whether they should make sandwiches. The other person asks for something to eat. The speaker then asks, ‘What shall I put in it for you?’ and the other answers, ‘You know what I like.’ The exchange ends with the speaker calling Zino.",
        "korean": "화자는 샌드위치를 만들어 줄지 묻고, 상대는 먹을 것을 아무거나 만들어 달라고 해요. 이어 화자가 ‘그 안에 무엇을 넣어 줄까?’라고 묻고 상대가 ‘내가 무엇을 좋아하는지 알잖아’라고 답해요. 대화는 화자가 지노를 부르는 말로 끝나요.",
    },
    912: {
        "english": "The speaker says they have brought it and will store it in the refrigerator. They invite the other person to smell how good the money is and imagine a poor man inside his villa. They then address ‘Lila’—a possible name or vocative rather than a time expression—and ask whether she will accept marrying them.",
        "korean": "화자는 그것을 가져왔으니 냉장고에 보관하겠다고 해요. 상대에게 돈 냄새가 얼마나 좋은지 맡아 보라고 하고, 가엾은 남자가 자기 별장 안에 있는 모습을 상상해요. 이어 ‘릴라’라는 이름이나 호격일 수 있는 말을 부르며, 시간 표현으로 확정하지 않고 자신과 결혼해 줄지 물어요.",
    },
    914: {
        "english": "The speaker welcomes Mr. Jamal, tells him to sit and calm himself, and asks where the notary is; ‘muwaththiq’ is the legal term, not merely a document. They say the loss they will suffer if they do not travel today is serious, ask why the matter has taken so long, and say that the case has lasted so long that even the French code-switched ‘l’avocat’, the lawyer, can do nothing.",
        "korean": "화자는 جمال 씨를 맞이해 앉아서 진정하라고 해요. 문서가 아니라 법률상의 공증인인 ‘muwaththiq’가 어디 있는지 묻고, 오늘 떠나지 않으면 입을 손실이 크다고 해요. 왜 이렇게 오래 걸리느냐고 하며 사건이 너무 오래 끌어 프랑스어가 섞인 ‘l’avocat’, 즉 변호사조차 아무것도 할 수 없다고 말해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    915: {
        "english": "They return to the factory case. The speaker says the factory matter has a final decision that they have accepted, while the others are bringing a case against them. They will let the court rule and see what happens, preserving a wait-for-the-court-decision meaning rather than a definite claim that they will contest it in court.",
        "korean": "화자들은 공장 사건으로 돌아가요. 화자는 공장 문제에 최종 결정이 내려져 자신이 받아들였지만, 상대방이 자신을 상대로 소송을 제기했다고 해요. 법원이 판결할 때까지 지켜보고 어떻게 되는지 보겠다고 하며, 법정에서 반드시 다투겠다고 확정하지 않아요.",
    },
    916: {
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    917: {
        "english": "The speaker says they have nothing to give the workers. They say, in the first person, ‘I shut the factory down,’ and that restarting it from scratch will take at least a year. The adviser says that, if they take the advice, they should restore all the workers’ rights and negotiate so they can return to work.",
        "korean": "화자는 노동자들에게 줄 것이 아무것도 없다고 해요. 이어 1인칭으로 ‘내가 공장을 닫았다’고 말하고, 처음부터 다시 시작하려면 적어도 1년이 걸린다고 해요. 조언자는 자신의 말을 따른다면 노동자들의 권리를 모두 회복하고 협상해서 다시 일하게 해야 한다고 말해요.",
    },
    918: {
        "english": "The speaker says the press has turned the whole world against the addressee. They will bring French code-switched ‘des machines’, machines that work by themselves, so they will not need workers. They sarcastically ask what the workers they have at the factory will do—polish the speaker’s shoes.",
        "korean": "화자는 언론이 상대에게 등을 돌리게 만들었다고 해요. 프랑스어가 섞인 ‘des machines’, 즉 혼자 작동하는 기계를 가져와 노동자가 필요 없게 하겠다고 해요. 지금 공장에 있는 노동자들은 무슨 일을 하겠느냐, 자신의 구두를 닦겠느냐고 비꼬아요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    920: {
        "english": "The speaker says, ‘Sorry, I will give them nothing; I am leaving.’ The row does not name the speaker as Mr. Jamal or otherwise fix the speaker’s identity.",
        "korean": "화자는 ‘미안하지만 그들에게 아무것도 주지 않겠어. 나는 갈 거야’라고 해요. 이 행은 화자를 جمال 씨나 다른 특정 인물로 확정하지 않아요.",
    },
    921: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    923: {
        "english": "The speaker asks why the cards or items should be burned and says that they might need them for another French code-switched ‘affaire’, meaning a case or matter, with the exact proposal partly unclear. They then say that each punched card is used for one affair and burned, adding that they still have learned nothing.",
        "korean": "화자는 왜 카드나 물건을 태우느냐고 하며, 프랑스어가 섞인 ‘affaire’, 즉 다른 사건이나 일에 필요할 수도 있다고 말해요. 정확한 제안은 일부 불분명해요. 이어 구멍 난 카드는 각각 한 사건에 쓰고 태운다고 하면서도 아직 아무것도 배우지 못했다고 해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    926: {
        "english": "The speaker says Malik knows this place very well. They suggest that perhaps he has a camera set up everywhere, or that the other person may be ill; the final reference remains uncertain. ‘Ghay’ is not treated as a separate person.",
        "korean": "화자는 말리크가 이 장소를 아주 잘 안다고 해요. 아마 그가 곳곳에 카메라를 설치했거나 상대가 아픈 사람일 수도 있다고 말하지만, 마지막 지칭은 불확실해요. ‘Ghay’를 별도의 인물로 분리하지 않아요.",
    },
    928: {
        "english": "The speaker tells Hosni that it is a serious matter and invokes a generous Lord, but the threat-like wording remains unclear. They say they will not bring up the sandwiches, another voice tells them to take them upstairs quickly and not forget the money, and the seller says they do not work for free. The speaker then addresses their mother: ‘Okay, Mom, do not worry.’ Hot garantika is served.",
        "korean": "화자는 호스니에게 큰일이라며 자비로운 신을 언급하지만 위협처럼 들리는 표현은 불분명해요. 샌드위치를 올리지 않겠다고 하자 다른 목소리가 빨리 가져가고 돈을 잊지 말라고 하며, 판매자는 자신이 공짜로 일하지 않는다고 해요. 이어 화자가 어머니에게 ‘알겠어, 엄마, 걱정하지 마’라고 말해요. 뜨거운 가란티카를 내요.",
    },
    929: {
        "english": "One speaker addresses a woman familiarly as ‘khti’—a friendly feminine address, not proof of a sister relationship—and asks how much a bottle of perfume costs. The amount is explicitly two hundred thousand. The other person apologizes and says it is forbidden to try or smell it.",
        "korean": "한 화자가 여성 상대를 친근하게 ‘khti’라고 부르며 향수 한 병이 얼마인지 물어요. 이는 자매 관계의 증거로 확정하지 않는 여성 호격이고, 금액은 명시적으로 20만이에요. 상대는 미안하지만 그것을 시험해 보거나 맡아 보는 것은 금지되어 있다고 해요.",
    },
    932: {
        "english": "They agreed with him on a price, but the speaker says they cannot change their mind a minute later. He made two items called ‘tartat’ and a property certificate; the token ‘tartat’ is kept opaque rather than normalized as tarts or cakes. The speaker says giving him all this money is too much.",
        "korean": "화자들은 그와 가격을 합의했지만 1분 뒤에 마음을 바꿀 수는 없다고 해요. 그가 ‘tartat’이라고 불리는 불투명한 항목 두 개와 소유권 증서를 만들었다고 하며, ‘tartat’을 타르트나 케이크로 확정하지 않아요. 이 돈을 전부 주는 것은 너무 많다고 말해요.",
    },
    933: {
        "english": "The speaker launches into direct obscene insults at Khairika. The row includes source clauses such as ‘daayer ki zebi’ (acting like a penis), ‘mok qahba’ (a mother-directed whore insult), and the later ‘nik mok’ sexual mother insult, alongside commands and challenges. These explicit abusive meanings are preserved rather than compressed into a generic statement about masculinity or family.",
        "korean": "화자는 카이리카에게 직접적인 성적·모친 욕설을 쏟아내요. 원문에는 ‘daayer ki zebi’(성기를 닮게 행동한다는 욕설), ‘mok qahba’(어머니를 겨냥한 창녀 욕설), 뒤의 ‘nik mok’(모친 대상 성적 욕설) 같은 절과 명령·도발이 나와요. 이를 남성성이나 가족을 공격한다는 일반 설명으로 줄이지 않고 노골적인 모욕 의미를 보존해요.",
    },
    934: {
        "english": "The speaker uses a highly abusive and partly opaque command: they tell the addressee to get up in the morning, not leave anyone in peace, leave the speaker alone, and not circle around them. The final direct mother-directed sexual insult is retained as source content rather than replaced by a generic label.",
        "korean": "화자는 매우 모욕적이고 일부 불투명한 명령을 하며 상대에게 아침에 일어나 아무도 편히 두지 말고 자신을 내버려 두며 주변을 맴돌지 말라고 해요. 마지막의 직접적인 모친 대상 성적 욕설도 일반적인 ‘모친 욕설’이라는 표지로 대체하지 않고 원문 내용으로 보존해요.",
    },
    935: {
        "english": "The speaker says Zaki knows nothing, tells him to put the machine down and go away, and directly calls him ‘ya khra’, a shit-related insult. They then order him to take the opaque expression ‘msasistko’ away with him; that token is not normalized as ‘foolish things’.",
        "korean": "화자는 자키가 아무것도 모른다고 하며 기계를 내려놓고 가라고 해요. 그를 직접 ‘ya khra’, 즉 똥 계열의 욕설로 부르고, 불투명한 표현 ‘msasistko’를 가지고 가라고 해요. ‘msasistko’를 어리석은 물건으로 확정하지 않아요.",
    },
    936: {
        "english": "The speaker tells Bisha not to make them do ‘tba3’, a term about behavior, habits, or manner, rather than tricks. They ask what kind of behavior is meant, say they are coming to ask for a marriage proposal, and another voice calls it a strange proposal and asks how it is supposed to be.",
        "korean": "화자는 비샤에게 행동·태도·버릇을 뜻할 수 있는 ‘tba3’을 자신에게 하게 하지 말라고 해요. 무슨 태도냐고 묻고, 청혼하러 가는 중이라고 말해요. 다른 목소리는 이런 청혼이 대체 어떻게 된 것이냐고 해요.",
    },
    937: {
        "english": "The speaker says that people who eat with a fork and the group or people named by the opaque ‘lkhadmi’ act like ‘zebi’ (a penis), that nobody wants them, that they arrive like ‘khra’ (shit), and that nothing pleases them. The speaker adds the direct mother-directed sexual insult ‘nik mok’, then says they want to live normally as they choose, not like Khairika. The separate abusive clauses and register are preserved.",
        "korean": "화자는 포크로 먹는 사람들과 불투명한 ‘lkhadmi’ 관련 사람들이 ‘zebi’(성기)처럼 행동하고 아무도 그들을 원하지 않으며 ‘khra’(똥)처럼 온다고 욕해요. 아무것도 마음에 들어 하지 않는다고 하고 직접적인 모친 대상 성적 욕설 ‘nik mok’을 덧붙여요. 이어 카이리카처럼이 아니라 자신이 원하는 대로 평범하게 살고 싶다고 말해요. 각 모욕 절과 거친 말투를 보존해요.",
    },
    939: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    951: {
        "english": "The Frenchman responds to the repeated bottle number and says, in effect, ‘But that one is for the opaque item ziqo.’ This is the Frenchman’s turn in the joke.",
        "korean": "프랑스인이 반복해서 나온 병 번호에 반응하며 ‘하지만 저것은 불투명한 물질인 지코용이잖아’라는 뜻으로 말해요. 이 발화의 turn은 프랑스인에게 있어요.",
    },
    952: {
        "english": "The doctor delivers the punchline, saying, in effect, ‘Okay, good, your memory has returned.’ The speaker direction is doctor to Frenchman.",
        "korean": "의사가 ‘좋아, 잘됐네, 네 기억이 돌아왔어’라는 뜻으로 punchline을 말해요. 화자 방향은 의사에서 프랑스인으로 향해요.",
    },
    958: {
        "english": "The speaker addresses their father: ‘Dad, what is wrong with that person? Why is he eating himself?’ The vocative ‘boya’ is kept as Dad, while ‘this one’ refers to a third person and the eating expression remains idiomatic or figurative.",
        "korean": "화자는 아버지를 부르며 ‘아빠, 저 사람 왜 저래? 왜 저렇게 자신을 먹는 것처럼 괴로워해?’라고 물어요. ‘boya’는 아빠라는 호격으로 보존하고, ‘저 사람’은 제3자를 가리키며 자신을 먹는다는 표현은 관용적·비유적으로 남겨요.",
    },
    960: {
        "english": "The speakers say they have come as the proposing party or suitors, preserving ‘rana khattaba’ without fixing them as professional matchmakers. The speaker then asks who will take the daughter if the speaker does not take her, showing that the speaker’s side is a prospective marriage party.",
        "korean": "화자들은 ‘rana khattaba’를 전문 중매인이라고 확정하지 않고 청혼하러 온 쪽이나 구혼자들이라고 말해요. 이어 자신이 그 딸을 데려가지 않으면 누가 데려가겠느냐고 물어, 화자 쪽이 혼인을 제안하는 당사자임을 드러내요.",
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
