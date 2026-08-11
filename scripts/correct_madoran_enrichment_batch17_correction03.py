"""Apply the remaining HeadGPT-directed corrections for MADOran Batch 17."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch17 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "8148f0e"
BATCH_ID = "MADORAN-ENRICH-017"
CORRECTION_ID = "MADORAN-ENRICH-017-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v17-correction-3"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch17_correction03_qa.json"
PROVENANCE_BEFORE = 14923

CORRECTIONS = {
    1026: {"topic": "repeated_opaque_command_to_go_down"},
    1028: {
        "english": "The speaker says someone wanted to ride her once, then says, ‘Bring Moulkheir; I will go down.’ The speaker then says they will see or find an unclear person or thing for the listener. The sexual and opaque surfaces are preserved, and the actors are not merged.",
        "korean": "화자는 누군가가 한 번 그녀를 타고 싶어 했다고 말한 뒤 ‘물카이르를 데려와. 나는 내려갈게’라고 해요. 이어 상대를 위해 불분명한 사람이나 물건을 찾아보겠다고 해요. 성적인 표면형과 불확실성을 보존하고 두 행위자를 합치지 않아요.",
    },
    1034: {
        "english": "The speaker asks about the daughter of the listener's shaf or chief. They say Bofu has one daughter and offer four cows as a reward for the listener's coffee or service; several terms remain opaque.",
        "korean": "화자는 상대의 shaf 또는 우두머리의 딸에 대해 묻고, 부푸에게 딸이 한 명 있다고 해요. 상대의 커피나 서비스에 대한 보상으로 소 네 마리를 주겠다고 하며 여러 표현은 불투명하게 남겨요.",
    },
    1051: {
        "english": "The speaker tells the worker to go and look for the daughter, or says it would be better for the speaker to go. They threaten the female listener with blinding and command her to go to the river, preserving the explicit opaque surface ntia ghaia; the remaining wording is uncertain.",
        "korean": "화자는 일하는 사람에게 가서 딸을 찾아보라고 하거나 자신이 가는 편이 낫다고 해요. 여성 청자에게 눈을 멀게 하겠다고 위협하며 강으로 가라고 명령하고, 명시적인 불투명 표면형 ‘ntia ghaia’를 보존해요. 나머지 표현은 불확실해요.",
    },
    1053: {
        "english": "The speaker says they do not know what happened and asks where the listener was. They address a sheikh and report that the girl has been at the lac or lake since morning and has not appeared. They say she is at the lake and tell the listener to hurry and go look at her; the French-derived lac surface is retained.",
        "korean": "화자는 무슨 일이 생겼는지 모르겠다며 상대가 어디 있었는지 물어요. 셰이크를 부르고 소녀가 아침부터 lac 또는 호수에 있었지만 나타나지 않았다고 말해요. 소녀가 호수에 있다고 분명히 말한 뒤 서둘러 가서 보라고 하며, 프랑스어계 lac 표면형을 보존해요.",
    },
    1055: {
        "english": "The speaker says there is something else: the girl is being taught crochet or embroidery. They say she went to wash, add the explicit opaque clauses rani flmjbwd and tdhmha, complain that Hazim is troubling them, and ask for a mirror.",
        "korean": "화자는 다른 일이 있다며 소녀가 코바늘뜨기나 자수를 배우고 있다고 해요. 소녀가 빨래하러 갔다고 말하고 명시적인 불투명 절 ‘rani flmjbwd’와 ‘tdhmha’를 덧붙여요. 하짐이 자신을 괴롭힌다고 불평하며 거울을 가져오라고 해요.",
    },
    1062: {
        "english": "The speaker says the woman or item is good and says ‘I love you,’ addressing the listener, then asks for 400 doro or other units. Another voice says it is not worth even a kiasa in the bathroom and offers 100; the haggling continues with the uncertain surface rana khawninha w la ml9ta, which may involve deceiving or betraying and something picked up or found, without fixing either meaning.",
        "korean": "화자는 그 여성이나 물건이 좋다고 하며 청자에게 ‘사랑해’라고 말한 뒤 400 도로나 다른 단위의 금액을 요구해요. 다른 목소리는 욕실의 ‘kiasa’만큼의 가치도 없다며 100을 제시하고, 속이거나 배신한다는 뜻과 무언가를 주워 오거나 찾았다는 뜻이 있을 수 있는 불확실한 ‘rana khawninha w la ml9ta’ 표면 속에서 흥정이 이어져요.",
    },
    1063: {
        "english": "The speakers bargain between 105 and 130 doro. The higher offer is said to include les impôts, taxes, and TVA, VAT, as well as wages for a worker, future work, food, and everything. One speaker says they will enter as a worker in an opaque khdam-khdakhwr role; later turns accept or reject the offer, say the other person has made things difficult, and promise to take care of them next time. Another voice says the item is dry in its fat and meat; the object remains unfixed.",
        "korean": "화자들은 105도로나 130도라 사이에서 흥정해요. 높은 가격에는 ‘les impôts’인 세금과 ‘TVA’인 부가가치세, 일꾼의 임금, 앞으로 들어올 일, 먹을 것 등이 모두 포함된다고 해요. 한 화자는 불투명한 khdam-khdakhwr 역할로 일하러 들어가겠다고 하고, 뒤의 turn에서는 제안을 받아들이거나 거절하고 상대가 일을 어렵게 만들었다고 하며 다음번에는 잘 돌보겠다고 해요. 다른 목소리는 그 물건이 지방과 살이 말랐다고 하며 대상을 확정하지 않아요.",
    },
    1066: {
        "english": "The speaker says they knew the Sons of the Day would do it and that it must be him who took her, him and his father. They order someone to bring her back, tell others to be quiet, ask for a turban, and say that staying safe is better than going themselves; they also tell someone to hurry. The speaker's epistemic uncertainty is retained.",
        "korean": "화자는 ‘울라드 나하르’가 그 일을 할 줄 알았으며 그녀를 데려간 사람은 그와 그의 아버지일 것이라고 강하게 추정해요. 누군가에게 그녀를 데려오라고 명령하고 조용히 하라고 하며 터번을 달라고 해요. 자신이 직접 가는 것보다 안전한 편이 낫다고 말하고 서두르라고도 해요. 추정의 말투를 사실 확정으로 바꾸지 않아요.",
    },
    1067: {
        "english": "The speaker tells someone to walk in front and says their daughter has been taken, using an opaque smell or recognition expression. They tell a woman to stay at home; she replies that she is staying or sitting there. The speaker invokes an unclear religious or legal phrase, threatens divorce if she follows, and says their heart is burning while asking where the daughter is.",
        "korean": "화자는 누군가에게 앞장서라고 하며 딸을 데려갔다고 말하고 냄새를 맡아 안다는 식의 불투명한 표현을 써요. 여성에게 집에 있으라고 하자 여성은 자신이 거기 있겠다고 답해요. 화자는 불분명한 종교·법률 표현을 언급하며 따라오면 이혼이라고 위협하고, 딸이 어디 있는지 묻고 마음이 타들어 간다고 해요.",
    },
    1068: {
        "english": "The speaker tells Mr Hazim not to be stingy or withhold the daughter and says, ‘I came so you would return the daughter to me.’ They call his heart white, curse the devil, and demand that the daughter be returned. Another voice asks, ‘Who will return the daughter to you?’ The speaker accuses them of kidnapping her and reports that her mother told her in the morning to wash clothes in the river before she disappeared.",
        "korean": "화자는 하짐 씨에게 딸을 두고 인색하게 굴거나 버티지 말라며 ‘내가 왔으니 딸을 내게 돌려줘’라고 해요. 하짐의 마음이 하얗다고 말하고 악마를 저주하며 딸을 돌려달라고 요구해요. 다른 목소리는 ‘누가 너에게 딸을 돌려주겠어?’라고 되묻고, 화자는 상대가 딸을 납치했다고 비난해요. 딸의 어머니가 아침에 강에서 빨래하라고 했고 그 뒤 딸이 사라졌다고 말해요.",
    },
    1069: {
        "english": "The speaker tells Hazim that he is falsely accusing them. A reply says, ‘Not you—your son,’ before Hazim's follow-up that his son was with him hunting and could not have kidnapped her. The exchange denies wrongdoing, repeats the demand to return the daughter, asks from whom she should be returned, suggests another man may have taken her, and then directly accuses the listener: ‘You took her; I know it was you.’ The refused marriage proposal remains part of the dispute.",
        "korean": "화자는 하짐에게 자신들을 억울하게 비난하고 있다고 직접 말해요. 이어 ‘네가 아니라 네 아들’이라는 반박이 나오고, 하짐은 자신의 아들이 자신과 사냥하고 있었다며 그녀를 납치했을 수 없다고 말해요. 잘못한 일이 없다고 부인하면서 딸을 돌려달라는 요구와 누구에게 딸을 돌려줘야 하느냐는 질문이 반복되고, 다른 남자가 데려갔을 가능성이 나온 뒤 ‘네가 데려갔어. 네가 한 줄 알아’라는 직접 비난이 이어져요. 거절된 청혼도 이 분쟁의 일부로 남겨요.",
    },
    1070: {
        "english": "The speaker says they are exposed or known in every market, tells Bqous to make his moustache, and says that he wants to be known or recognized. The remaining expressions about joy and beauty are opaque; the second-person direction is retained.",
        "korean": "화자는 자신들이 모든 시장에서 드러나거나 알려져 있다고 하고, 비쿠스에게 콧수염을 만들라고 하며 그가 알려지고 싶어 한다고 말해요. 기쁨과 아름다움에 관한 나머지 표현은 불투명하며 2인칭 방향을 보존해요.",
    },
    1080: {
        "english": "The speaker addresses Madam Sawsan and says this is not the Sawsan they are following, then uses an affectionate flower-like address. They also preserve the opaque bwia miki surface, ask who the person is, and identify the person as the shaf or chief of the Sons of the Day tribe; no daughter relationship is added.",
        "korean": "화자는 수산 부인에게 말을 걸며 자신들이 따르는 수산은 이런 사람이 아니라고 해요. 꽃처럼 다정한 호칭과 불투명한 ‘b wia miki’ 표면형을 보존하고, 상대가 누구냐고 물은 뒤 ‘울라드 나하르’ 부족의 shaf 또는 부족장이라고 설명해요. 딸이라는 관계는 추가하지 않아요.",
    },
    1086: {
        "english": "The speaker says the others have done it and relied on them, while another voice denies relying on anyone. They ask how the attack will happen and say there are dogs, only talk. The opaque 3idan surface is retained: the 3idan did not stop, then another voice says the 3idan have slept. The exchange preserves the later corrections raki 9albtha, 9lbwa khir, and the address ya stwta rather than compressing them into generic military terminology.",
        "korean": "화자는 상대가 일을 저질렀고 자신들을 믿었다고 말하지만, 다른 목소리는 아무도 믿지 않았다고 부인해요. 어떻게 공격할지 묻자 개들이 있지만 말뿐이라는 표현이 나와요. 불투명한 ‘3idan’ 표면을 보존하며 3idan이 멈추지 않았다고 했다가 다른 목소리가 3idan이 잠들었다고 말해요. 뒤의 ‘raki 9albtha’, ‘9lbwa khir’, ‘ya stwta’ 교정과 호칭도 일반적인 군사 용어로 압축하지 않고 보존해요.",
    },
    1087: {
        "english": "The speaker tells the listener to follow and prepare themselves. They ask the listener to help them, tell the listener to look after themselves so they become bright, and say the listener is extinguished or dim on their own. They then threaten to bring dogs from outside that will eat the listener without chewing.",
        "korean": "화자는 상대에게 따라오며 준비하라고 해요. 상대에게 자신을 도와 달라고 하고, 스스로를 잘 살펴 밝아지라고 말하며 상대가 혼자서는 꺼져 있거나 어둡다고 해요. 이어 밖에서 개들을 데려와 씹지도 않고 상대를 먹게 하겠다고 위협해요.",
    },
    1088: {
        "english": "The speaker asks who is there and welcomes the guests of God. They invite everyone to come, call the hunt good for the day, and repeat the surface command arfd arfd, asking someone to lift or carry without fixing an object; ya 3n9i and the repeated command are preserved.",
        "korean": "화자는 누가 왔는지 묻고 신의 손님들을 환영해요. 모두 오라고 부르고 오늘의 사냥이 좋다고 하며 ‘arfd arfd’라는 표면 명령을 반복해요. 특정 물건을 정하지 않고 누군가에게 들어 올리거나 나르라고 하며 ‘ya 3n9i’와 반복 명령을 보존해요.",
    },
    1045: {"processing_flags": "source_ambiguity"},
    1065: {"processing_flags": "code_switching"},
    1077: {"processing_flags": "code_switching"},
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
