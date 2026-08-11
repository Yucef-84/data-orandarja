"""Apply the second HeadGPT-directed semantic corrections for MADOran Batch 16."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "0fd10d0"
BATCH_ID = "MADORAN-ENRICH-016"
CORRECTION_ID = "MADORAN-ENRICH-016-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v16-correction-2"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch16_sentno_0961_1024.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch16_correction02_qa.json"
PROVENANCE_BEFORE = 13873

CORRECTIONS = {
    962: {
        "english": "A long, partly unclear exchange explicitly preserves the French-derived surface l'âge in the phrase fi l'âge ta3k (exact phrasing and role remain uncertain), then lists food or household work such as cutting or preparing food, cleaning, washing, and gathering firewood. The exchange asks what the other person was doing; the source surface and uncertainty are retained.",
        "korean": "길고 일부 불분명한 대화에서 ‘fi l'âge ta3k’라는 프랑스어계 표면형이 명시적으로 나오지만 정확한 구문과 역할은 불확실해요. 이어 음식 준비·손질, 청소·세척, 장작 마련 같은 음식이나 집안일이 나열되고 상대가 무엇을 하고 있었는지 물어요. 원문의 표면형과 불확실성을 보존해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    968: {
        "english": "Guests arrive and the speaker asks what is happening. A long multi-turn comic exchange includes the explicit surfaces je suis robot and w allah tkhlswha mam nta; their exact wording and force remain partly uncertain, but the clauses and the possible threat or warning turn are not reduced to a generic payment statement. The exchange also mentions not working on Friday, being driven crazy, looking for a jacket, moving back, following the speaker, and someone wanting to eat the earth.",
        "korean": "손님들이 오자 화자가 무슨 일이냐고 물어요. 긴 여러 turn의 희극적 대화에는 ‘je suis robot’과 ‘w allah tkhlswha mam nta’라는 명시적 표면형이 나오며 정확한 표현과 힘은 일부 불확실하지만, 각 절과 가능한 위협·경고 화행을 단순한 결제 이야기로 축약하지 않아요. 금요일에는 일하지 않는다는 말, 미치겠다는 말, 재킷을 찾는 말, 물러서기, 따라오라는 말, 땅을 먹고 싶다는 말도 이어져요.",
    },
    977: {
        "english": "A speaker tells a woman to listen and complains that she has spent all morning on food, threatening to hit her with a shoe if she does not finish. They order her to fetch brika from Akasha's wife; here brika is a French-derived briquet-like lighter surface, not food. The final instruction is to light it, while the exact remaining household wording stays uncertain.",
        "korean": "화자가 한 여성에게 들으라고 하며 여성이 아침 내내 음식에 매달려 있다고 불평하고, 끝내지 않으면 신발로 때리겠다고 위협해요. 이어 아카샤의 아내에게서 ‘brika’를 가져오라고 하는데, 여기서 brika는 음식이 아니라 프랑스어계 briquet 계열의 라이터를 가리키는 표면형으로 보존해요. 마지막에는 그것에 불을 붙이라는 지시가 나오고 나머지 집안 표현은 불확실해요.",
        "domain": "daily_life",
        "topic": "household_command_and_lighter_request",
    },
    978: {
        "english": "The speaker repeats the instruction to fetch brika from Akasha's wife and clarifies that it is not from Akasha himself. In this smoking context brika is a French-derived briquet-like lighter surface, not food; the wife is smoking, followed by an agreement.",
        "korean": "화자는 아카샤의 아내에게서 brika를 가져오라는 지시를 반복하고 아카샤 본인에게서 가져오는 것은 아니라고 확인해요. 흡연 문맥에서 brika는 음식이 아니라 프랑스어계 briquet 계열의 라이터를 가리키는 표면형이고, 아내가 담배를 피우고 있다는 말 뒤에 동의가 나와요.",
        "domain": "daily_life",
        "topic": "clarifying_lighter_source_and_smoking",
        "processing_flags": "code_switching|source_ambiguity",
    },
    981: {
        "english": "They answer that it is for Bisha, their son. After asking who Bisha is, someone identifies him as that one and uses an opaque phrase about a bathhouse. Greetings follow, along with a question about where the father was; he says he was hunting and caught a fox. The final opaque surface tshak ya 7ai is retained rather than silently omitted.",
        "korean": "비샤라는 그들의 아들을 위한 것이라고 답해요. 비샤가 누구냐고 묻자 ‘저 사람’이라고 가리키고 목욕탕과 관련된 불투명한 표현을 써요. 이어 인사를 나누고 아빠가 어디 있었는지 묻자 사냥을 했고 여우를 잡았다고 답해요. 마지막의 불투명한 표면형 ‘tshak ya 7ai’도 누락하지 않고 보존해요.",
    },
    982: {
        "english": "The other speaker mocks the claim of catching a fox and says that the person should be hunting lions, tigers, and l'ours (the bear) instead. The opening t3lb t3 mk hadi is a separate mother-related insult. They then refer to having lost or released a lion in the valley that time, and the final tfwa 3lik and w 3la 7altk separately insult the addressee and the addressee's condition; these are not an either-or replacement.",
        "korean": "상대는 여우를 잡았다는 말을 비웃으며 사자와 호랑이, l'ours(곰)를 잡아야 한다고 해요. 처음의 ‘t3lb t3 mk hadi’는 상대의 어머니와 관련된 별도의 모욕이고, 이어 그때 계곡에서 사자를 놓쳤거나 잃었다는 방향의 이야기가 나와요. 마지막 ‘tfwa 3lik’과 ‘w 3la 7altk’는 각각 상대와 상대의 처지를 모욕하는 절이므로 ‘어머니 또는 처지’처럼 하나로 대체하지 않아요.",
    },
    984: {
        "english": "The speaker describes the proposed marriage with exaggerated or opaque comparisons, tells the listener to say they will not give the daughter, and hears that Bisha deserves her because his people are good. The exchange also explicitly contains mdha lbridatwr w saii, an opaque command-like clause that may mean to give her to the predator or simply finish; its surface and uncertainty are preserved. Then, addressing Dad, the speaker says, I myself am tired of her, while likidiha remains code-switched and opaque.",
        "korean": "화자는 과장되고 불투명한 비교를 이어가며 딸을 주지 않겠다고 말하라고 하고, 비샤와 그 집안이 좋은 사람들이라 딸을 받을 만하다는 말을 들어요. 이어 ‘mdha lbridatwr w saii’라는 명시적이고 명령처럼 보이는 불투명한 절이 나오는데, 포식자에게 그녀를 주라는 뜻인지 단순히 끝내라는 뜻인지 확정하지 않고 표면형과 불확실성을 보존해요. 그 뒤 화자가 아빠에게 ‘나 자신이 그녀에게 질렸어’라고 말하며 likidiha도 코드 스위칭된 불투명한 표현으로 남겨요.",
    },
    985: {
        "english": "The speaker tells someone to leave and explicitly uses the direct threat nlikidk, a code-switched or French-derived liquider-like form that may mean I will deal with or liquidate you. The exact threat remains partly opaque, but the direct address and threat structure are preserved; the person is also told to tell the suitor no.",
        "korean": "화자는 누군가에게 나가라고 하며 ‘nlikidk’라는 직접적인 위협을 명시해요. 이는 ‘너를 처리하거나 없애 버리겠다’는 뜻일 수 있는 코드 스위칭 또는 프랑스어계 liquider 계열 표현으로, 정확한 의미는 일부 불투명하지만 직접적인 위협 구조와 표면형을 보존해요. 이어 청혼자에게 안 된다고 말하라고 해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    986: {
        "english": "The speaker says they do not have the face to tell him no, but another voice tells them to say no. The plural form isalwni bnti means they ask for my daughter; it is kept separate from the later singular male referent in hw and the following opaque description. The speaker remains unwilling to give the daughter to him.",
        "korean": "화자는 그에게 안 된다고 말할 면목이 없다고 하지만 다른 목소리는 안 된다고 말하라고 해요. 복수형 표현 ‘isalwni bnti’는 ‘그들이 내 딸을 요구한다’는 뜻으로 보존하고, 뒤의 ‘hw’에 해당하는 단수 남성 지시대상과 이어지는 불투명한 설명을 합치지 않아요. 화자는 여전히 그에게 딸을 주지 않으려 해요.",
    },
    991: {
        "english": "Addressing Mr. Hazim, the speaker asks what they should tell the group and says drt m3aha hak mra, meaning they did that with her once or at that time; the exact temporal expression remains uncertain and is not treated as a separate generic woman. Reassurance follows that everything is fine.",
        "korean": "화자는 하짐 씨에게 무엇이라고 말해야 할지 묻고 ‘drt m3aha hak mra’라고 말해요. 여기서 mra는 별도의 여성을 뜻한다고 단정하지 않고 ‘그녀와 그때 또는 한 번 그렇게 했다’는 시간·횟수 표현의 가능성을 보존해요. 이어 모두 괜찮다는 안심의 말이 나와요.",
    },
    996: {
        "english": "The speaker says the girl is still studying, has a licence in law, wants to become a lawyer, and hopes to finish her studies, go to France, and marry there because there is no future here. A later separate response says it is all right and that the speaker or another marriage-side voice can wait for her; the turn boundary and speaker attribution are not collapsed into the preceding educational description.",
        "korean": "화자는 그 여성이 아직 공부 중이고 법학 학위가 있으며 변호사가 되고 싶어 한다고 해요. 공부를 마치면 프랑스에 가서 그곳에서 결혼하고 싶어 한다며 여기에는 더 이상 미래가 없다고 말해요. 뒤의 ‘괜찮아, 그녀를 기다릴 수 있어’라는 응답은 별도의 turn으로 보존하고, 앞의 학업 설명과 같은 화자라고 합치지 않아요.",
    },
    1004: {
        "topic": "expulsion_command_or_threat_to_visitors",
    },
    1012: {
        "english": "A long abusive exchange calls someone a traitor and tells them to turn around and fall on an opaque bean-related target. The speaker reproaches them with mt7shmwsh, meaning roughly aren't you ashamed or you have no shame, not an encouragement not to feel shame. It lists cows, chickens, sheep, straw, donkeys, and dogs, and asks where everyone is going; turns and several expressions remain uncertain.",
        "korean": "긴 모욕적 대화에서 누군가를 배신자라고 부르고 불투명한 콩 관련 대상을 향해 돌아가 쓰러지라고 해요. 화자는 ‘mt7shmwsh’로 ‘부끄럽지도 않냐’ 또는 ‘부끄러움을 모른다’는 식으로 질책하며, ‘부끄러워하지 마’라고 권유하는 뜻으로 뒤집지 않아요. 소·닭·양·짚·당나귀·개를 나열하고 모두 어디로 가는지 물으며, turn과 여러 표현은 불확실해요.",
    },
    1013: {
        "english": "The speaker uses the same mt7shmwsh reproach, roughly aren't you ashamed or you have no shame, and then accuses the others of even kidnapping women in villages and reselling them. It is a condemnation in the kidnapping context, not advice not to feel ashamed.",
        "korean": "화자는 같은 ‘mt7shmwsh’ 표현으로 ‘부끄럽지도 않냐’ 또는 ‘부끄러움을 모른다’고 질책한 뒤, 상대가 마을에서 여성들까지 납치해 다시 판다고 비난해요. 납치 비난 문맥의 질책이지 ‘부끄러워하지 마’라는 권유가 아니에요.",
    },
    1015: {
        "english": "The speaker says they are thinking of using it for a ferme (farm) associated with Khaïlia, then asks why they do not make a wzin ta3 l7lib, a milk factory or dairy plant. The later comparison with the listener's mother remains unclear; the milk-factory meaning is kept distinct from the yogurt factory in Sentno 1016.",
        "korean": "화자는 그것을 카할리아와 관련된 ferme(농장)에 쓰려고 생각한다고 한 뒤, 왜 ‘wzin ta3 l7lib’, 즉 우유 공장이나 유제품 공장을 만들지 않느냐고 물어요. 뒤의 상대 어머니와 비교하는 말은 불분명하게 두고, 1016번의 요구르트 공장과 구별되는 우유 공장 의미를 보존해요.",
    },
    1017: {
        "english": "The speaker addresses a friend, says they will take the other one, and asks what to do with dimil dwrw, an explicit French-derived deux mille, meaning 2,000. The quantity is preserved; only the exact currency or unit remains uncertain.",
        "korean": "화자는 친구를 부르며 다른 것을 잡겠다고 하고 ‘dimil dwrw’라고 말해요. 이는 프랑스어계 deux mille, 즉 2,000이라는 명시적 수량으로 보존하며, 정확한 통화나 단위만 불확실하게 둬요.",
    },
    1019: {
        "english": "The exchange opens with the explicit question mal 7ia kifah? (what is it, Hayia? or an uncertain name/address form). The speaker then says they were away for a minute and jokes that one day the other person was given a donkey and today something else, perhaps a kabous; the comparison remains opaque.",
        "korean": "대화는 ‘mal 7ia kifah?’라는 명시적 질문으로 시작해요. 이는 ‘무슨 일이야, 하이아?’ 또는 불확실한 이름·호격일 수 있어 표면형을 보존해요. 이어 잠깐 자리를 비웠다며 어느 날에는 상대에게 당나귀를 주더니 오늘은 ‘카부스’처럼 들리는 다른 것을 줬다고 농담하고, 비교의 의미는 불투명하게 둬요.",
    },
    1022: {
        "english": "The source may be saying that Bisha wants to throw himself or jump from a height; this is a hypothesis from the opaque form i9is rw7h and trwazim, which may connect with French troisième and a third floor. From the first clause onward, the possible jump or self-harm reading is marked as source ambiguity rather than stated as fact. The speaker says they knew he wanted to do it because of her and tells the others to follow; it is not reduced to competition or rank.",
        "korean": "원문은 비샤가 몸을 던지거나 높은 곳에서 뛰어내리려 한다고 말할 가능성이 있지만, 이는 ‘i9is rw7h’와 ‘trwazim’이라는 불투명한 표현에서 나온 가설이에요. ‘trwazim’은 프랑스어 troisième 및 3층과 연결될 가능성이 있어요. 첫 절부터 투신이나 자해 가능성을 사실로 확정하지 않고 source ambiguity로 표시해요. 화자는 그녀 때문에 그렇게 하려 한다는 것을 알고 있었다며 따라오라고 하고, 이를 경쟁이나 지위 비유로 축소하지 않아요.",
    },
    1023: {
        "english": "The speaker asks the others not to mention the person they love and not to keep nagging. The form trw7 in dwk trw7 is not silently changed into first-person I will leave; it may address another person or have an uncertain role, while the following ana m9ditsh separately expresses I cannot take it anymore. The speaker then says they love her very much.",
        "korean": "화자는 자신이 사랑하는 사람에 대해 말하지 말고 계속 괴롭히지도 말라고 해요. ‘dwk trw7’의 trw7은 1인칭 ‘내가 떠날 거야’로 조용히 바꾸지 않고, 다른 사람에게 하는 말이거나 역할이 불확실한 표현으로 보존해요. 뒤의 ‘ana m9ditsh’는 ‘나는 더는 견딜 수 없어’라는 별도 절로 두고, 이어 그녀를 매우 사랑한다고 말해요.",
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
