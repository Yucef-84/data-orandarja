"""Apply HeadGPT-directed semantic and structural corrections for MADOran Batch 17."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch17 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "5c40544"
BATCH_ID = "MADORAN-ENRICH-017"
CORRECTION_ID = "MADORAN-ENRICH-017-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v17-correction-1"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch17_correction01_qa.json"
PROVENANCE_BEFORE = 14711

CORRECTIONS = {
    1025: {
        "english": "Bisha is told to go down or leave, with the surface hwd preserved. The speaker says they have come with an opaque factor-like expression, says the listener is here, and asks Dad where he is; the actor directions remain uncertain.",
        "korean": "비샤에게 ‘hwd’라고 내려가거나 가라고 하는 말이 나와요. 화자는 불투명한 factor 같은 표현과 함께 왔다고 하며 상대가 여기 있다고 하고, 아빠에게 어디 있느냐고 물어요. 행위자 방향은 불확실하게 보존해요.",
        "cefr_level": "A2",
        "difficulty_score": "28",
    },
    1026: {
        "english": "The speaker repeats the opaque surface hwd and says they will not go down. They address someone as their son, curse the devil, and urge or command him to go down; the exact sense of the surrounding surface remains uncertain.",
        "korean": "화자는 불투명한 표면형 ‘hwd’를 반복하며 자신은 내려가지 않겠다고 해요. 누군가를 아들이라고 부르고 악마를 저주하며 내려가라고 재촉하거나 명령해요. 주변 표면형의 정확한 뜻은 불확실해요.",
        "cefr_level": "A2",
        "difficulty_score": "36",
    },
    1027: {
        "english": "The speaker says they will not go down or do anything, then makes a crude sexual statement about the listener's beautiful mother and riding her. The vulgar actor direction is retained without softening it.",
        "korean": "화자는 내려가지도 아무것도 하지도 않겠다고 한 뒤, 상대의 아름다운 어머니를 타겠다는 식의 노골적이고 성적인 말을 해요. 저속한 행위자 방향을 순화하지 않고 보존해요.",
        "cefr_level": "B1",
        "difficulty_score": "48",
    },
    1028: {
        "english": "The speaker says someone wanted to ride her once, asks Moulkheir to go down, and says they will see or find an unclear person or thing for the listener. The sexual and opaque surfaces are preserved.",
        "korean": "화자는 누군가가 한 번 그녀를 타고 싶어 했다고 말하고, 물카이르에게 내려가거나 오라고 해요. 이어 상대를 위해 불분명한 사람이나 물건을 찾아보겠다고 하며 성적인 표면형과 불확실성을 보존해요.",
        "cefr_level": "B2",
        "difficulty_score": "56",
    },
    1029: {
        "english": "The speaker wants Moulkheir now and identifies Moulkheir as the person whose father is Hazim, a tribal chief. They say the group needs nothing from the listener, compare him to someone fleeing a washer or bathhouse, and propose sending a person from their side to go to her; they hope God brings good.",
        "korean": "화자는 지금 물카이르를 원하며 물카이르의 아버지가 부족장 하짐이라고 말해요. 상대에게서 필요한 것은 없다고 하고, 세탁장이나 목욕탕에서 도망친 사람처럼 행동한다고 비유해요. 자기들 쪽 사람을 보내 그녀에게 가게 하자고 하며 신이 좋은 일을 가져오기를 바라요.",
        "topic": "arranging_marriage_with_tribal_chiefs_daughter",
        "cefr_level": "B2",
        "difficulty_score": "58",
    },
    1030: {
        "english": "The speaker proposes sending someone and tells Dad to go while the speaker stays. They mention an opaque phrase about something reaching the head, say people want to go up and go down, curse the devil, reject the idea of going down, and ask to be released.",
        "korean": "화자는 누군가를 보내자고 하며 아빠에게 가라고 하고 자신은 여기 있겠다고 해요. 머리에 닿는 것과 관련된 불투명한 표현을 쓰고, 사람들이 올라가고 내려가려 한다고 하며 악마를 저주해요. 내려가고 싶지 않다고 거부한 뒤 자신을 놓아 달라고 해요.",
        "cefr_level": "B1",
        "difficulty_score": "48",
    },
    1038: {
        "english": "The speaker addresses Dad and says, ‘I want to ask you whether hunting a lion and hunting a tiger are the same.’ Dad asks whether the speaker has seen a lion and a hyena as the same, and the answer says they are not the same.",
        "korean": "화자가 아빠에게 ‘사자 사냥과 호랑이 사냥이 같은지 물어보고 싶어요’라고 말해요. 아빠는 사자와 하이에나를 같은 것으로 보았느냐고 되묻고, 둘은 같지 않다고 답해요.",
        "cefr_level": "A2",
        "difficulty_score": "24",
    },
    1043: {
        "english": "The speaker tells Lella to go down and wash these clothes because her brother needs them for sport tomorrow. They tell her not to be late; the source's lspor surface is retained.",
        "korean": "화자는 렐라에게 내려가서 이 옷들을 빨라고 해요. 동생이 내일 lspor에 필요하다고 하며 늦지 말라고 해요. 원문의 lspor 표면형을 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
        "cefr_level": "A2",
        "difficulty_score": "20",
    },
    1045: {
        "english": "The speaker asks where they were in the conversation, welcomes a man and tells him to raise his hands, then says he has finally appeared. They say they brought the amanah or entrusted item from the morning and had been looking for him; their legs are worn out from searching since morning, while the remaining surface is opaque.",
        "korean": "화자는 대화가 어디까지였는지 묻고 한 남자를 환영하며 손을 들라고 해요. 이제야 나타났다고 하며 아침부터 맡겨 둔 물건이나 ‘amanah’를 가져왔고 그를 찾고 있었다고 해요. 아침부터 찾아다녀 다리가 다 지쳤다고 하며, 나머지 표면형은 불투명하게 남겨요.",
        "cefr_level": "B1",
        "difficulty_score": "42",
    },
    1049: {
        "english": "The speaker addresses Hazim with an unclear insulting term and says their daughter has not appeared since morning. They say they are in maquillage or makeup and use an opaque expression containing déjà; their heart has been bleeding since morning, and the remaining surface is uncertain.",
        "korean": "화자는 하짐을 불분명한 모욕적 호칭으로 부르며 딸이 아침부터 나타나지 않았다고 해요. 화장이나 maquillage 중이라고 하며 ‘déjà’가 들어간 불투명한 표현을 써요. 아침부터 마음이 피를 흘리는 것 같다고 하며 나머지 표면형은 불확실해요.",
        "processing_flags": "code_switching|source_ambiguity",
        "cefr_level": "B1",
        "difficulty_score": "46",
    },
    1051: {
        "english": "The speaker tells the worker to go and look for the daughter, or says it would be better for the speaker to go. They threaten the female listener with blinding and command her to go to the river; the remaining surface is opaque.",
        "korean": "화자는 일하는 사람에게 가서 딸을 찾아보라고 하거나 자신이 가는 편이 낫다고 해요. 여성 청자에게 눈을 멀게 하겠다고 위협하며 강으로 가라고 명령해요. 나머지 표면형은 불투명하게 보존해요.",
        "cefr_level": "B1",
        "difficulty_score": "40",
    },
    1052: {
        "english": "The speaker says their heart is not at ease and tells someone to look for the daughter. They call the listener to come here.",
        "korean": "화자는 마음이 편하지 않다며 누군가에게 딸을 찾아보라고 해요. 상대에게 이리 오라고 불러요.",
        "processing_flags": "",
        "cefr_level": "A2",
        "difficulty_score": "22",
    },
    1055: {
        "english": "The speaker says there is something else: the girl is being taught crochet or embroidery. They say she went to wash, add the explicit opaque clause ‘rani flmjbwd’ describing the speaker's own state or activity, complain that Hazim is troubling them, and ask for a mirror.",
        "korean": "화자는 다른 일이 있다며 소녀가 코바늘뜨기나 자수를 배우고 있다고 해요. 소녀가 빨래하러 갔다고 말하고, 화자 자신의 상태나 활동을 나타내는 불투명한 ‘rani flmjbwd’ 절을 덧붙여요. 하짐이 자신을 괴롭힌다고 불평하며 거울을 가져오라고 해요.",
        "cefr_level": "B1",
        "difficulty_score": "46",
    },
    1058: {
        "english": "The speaker says the listener knows them as bad or dangerous but that they will bring only good. They use opaque commands about lowering a hand and going down, then present merchandise described as high quality or unlike what is usually kept.",
        "korean": "화자는 상대가 자신을 나쁘거나 위험한 사람으로 알지만 자신은 좋은 것만 가져오겠다고 해요. 손을 내리고 내려가라는 것과 관련된 불투명한 명령을 한 뒤, 고급품이거나 평소의 것과 다른 상품을 가져왔다고 소개해요.",
        "cefr_level": "B2",
        "difficulty_score": "56",
    },
    1059: {
        "english": "The speaker says the merchandise is not Taiwan or Taiwanese merchandise, then describes it as an item or vehicle with its papers, carte grise, insurance, and everything working. The Taiwan, registration, and insurance surfaces are retained without adding a generic fake or toy meaning.",
        "korean": "화자는 그 상품이 타이완이나 타이완산 상품이 아니라고 한 뒤, 서류와 ‘carte grise’, 보험 서류가 있고 모든 것이 작동하는 물건이나 차량이라고 해요. 타이완·등록·보험 표면형을 보존하고 일반적인 가짜나 장난감이라는 의미를 덧붙이지 않아요.",
        "cefr_level": "B2",
        "difficulty_score": "58",
    },
    1060: {
        "english": "The buyer asks to see what the merchandise looks like. Another voice tells someone to look because the merchandise sells itself and says it is not Taiwan or Taiwanese merchandise; the exact object remains uncertain.",
        "korean": "구매자가 상품이 어떻게 생겼는지 보여 달라고 해요. 다른 목소리는 상품이 스스로 팔릴 만큼 좋다며 보라고 하고 타이완이나 타이완산 상품이 아니라고 해요. 정확한 대상은 불확실해요.",
        "cefr_level": "B1",
        "difficulty_score": "36",
    },
    1062: {
        "english": "The speaker says the woman or item is good and says ‘I love you,’ addressing the listener, then asks for 400 doro or other units. Another voice says it is not worth even a kiasa in the bathroom and offers 100; the haggling continues with an opaque accusation that they ruined or muddled it.",
        "korean": "화자는 그 여성이나 물건이 좋다고 하며 청자에게 ‘사랑해’라고 말한 뒤 400 도로나 다른 단위의 금액을 요구해요. 다른 목소리는 욕실의 ‘kiasa’만큼의 가치도 없다며 100을 제시하고, 그것을 망쳤거나 뒤섞었다는 불투명한 비난 속에서 흥정이 이어져요.",
        "cefr_level": "B1",
        "difficulty_score": "44",
    },
    1063: {
        "english": "The speakers bargain between 105 and 130 doro. The higher offer is said to include les impôts, taxes, and TVA, VAT, as well as wages for a worker, future work, food, and everything; another voice says the item is dry in its fat and meat. The exchange remains a comic or metaphorical sale without fixing the object.",
        "korean": "화자들은 105도로나 130도라 사이에서 흥정해요. 높은 가격에는 ‘les impôts’인 세금과 ‘TVA’인 부가가치세, 일꾼의 임금, 앞으로 들어올 일, 먹을 것 등이 모두 포함된다고 해요. 다른 목소리는 그 물건이 지방과 살이 말랐다고 하며, 대상을 확정하지 않는 희극적·비유적 거래로 보존해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
        "cefr_level": "C1",
        "difficulty_score": "72",
    },
    1064: {
        "english": "The speaker tells a mangy or scabby goat to walk, then says the woman is good-hearted and should be cared for. The listener is accused of wanting to eat the speaker or the earth, and an opaque Indian-related command threatens to remove the listener's father if they stay. The French-derived or Indian-related surface is retained.",
        "korean": "화자는 옴이나 피부병이 있는 염소에게 걸으라고 하는 식으로 말한 뒤, 그 여성이 좋은 사람이고 마음이 착하니 잘 돌보라고 해요. 상대가 자신이나 땅을 먹으려 한다고 비난하고, 프랑스어계 또는 인디언 관련 불투명한 표현과 아버지를 없애 버리겠다는 위협이 이어져요.",
        "processing_flags": "code_switching|source_ambiguity",
        "cefr_level": "B2",
        "difficulty_score": "60",
    },
    1065: {
        "english": "The speaker addresses Moulkheir and says, ‘They took her. I told you.’ The speaker then asks who took her, answers that God knows and probably the Sons of the Day did it, and presents or points to a fletche or arrow with ‘Here is a fletche.’ The turn direction is preserved.",
        "korean": "화자가 물카이르에게 ‘그들이 그녀를 데려갔어. 내가 말했잖아’라고 말해요. 이어 누가 데려갔느냐고 묻고 신만이 알고 아마 ‘울라드 나하르’가 그랬을 것이라고 답한 뒤, ‘여기 fletche가 있어’라는 식으로 화살을 내보이거나 가리켜요. 화행 방향을 보존해요.",
        "cefr_level": "B1",
        "difficulty_score": "48",
    },
    1066: {
        "english": "The speaker says they knew the Sons of the Day would do it and that it must be him who took her, him and his father. They order someone to bring her back, tell others to be quiet, ask for a turban, and tell someone to hurry; the speaker's epistemic uncertainty is retained.",
        "korean": "화자는 ‘울라드 나하르’가 그 일을 할 줄 알았으며 그녀를 데려간 사람은 그와 그의 아버지일 것이라고 강하게 추정해요. 누군가에게 그녀를 데려오라고 명령하고 조용히 하라고 하며 터번을 달라고 하고 서두르라고 해요. 추정의 말투를 사실 확정으로 바꾸지 않아요.",
        "cefr_level": "B2",
        "difficulty_score": "58",
    },
    1068: {
        "english": "The speaker tells Mr Hazim not to deceive them and says, ‘I came so you would give me the daughter.’ They call his heart white, curse the devil, and demand that the daughter be returned. Another voice asks, ‘Who will give you the daughter?’ The speaker accuses them of kidnapping her and reports that her mother told her in the morning to wash clothes in the river before she disappeared.",
        "korean": "화자는 하짐 씨에게 자신을 속이지 말라며 ‘내가 왔으니 딸을 내게 줘’라고 해요. 하짐의 마음이 하얗다고 말하고 악마를 저주하며 딸을 돌려달라고 요구해요. 다른 목소리는 ‘누가 너에게 딸을 주겠어?’라고 되묻고, 화자는 상대가 딸을 납치했다고 비난해요. 딸의 어머니가 아침에 강에서 빨래하라고 했고 그 뒤 딸이 사라졌다고 말해요.",
        "cefr_level": "B2",
        "difficulty_score": "64",
    },
    1069: {
        "english": "The speaker tells Hazim that he is falsely accusing them. Hazim replies that his son was with him hunting and asks how he could have kidnapped her. The exchange denies wrongdoing, repeats the demand to give the daughter, asks from whom she should be given, suggests another man may have taken her, and then directly accuses the listener: ‘You took her; I know it was you.’ The refused marriage proposal remains part of the dispute.",
        "korean": "화자는 하짐에게 자신들을 억울하게 비난하고 있다고 직접 말해요. 하짐은 자신의 아들이 자신과 사냥하고 있었다며 어떻게 그가 그녀를 납치했겠느냐고 답해요. 잘못한 일이 없다고 부인하면서 딸을 달라는 요구와 누구에게 딸을 줘야 하느냐는 질문이 반복되고, 다른 남자가 데려갔을 가능성이 나온 뒤 ‘네가 데려갔어. 네가 한 줄 알아’라는 직접 비난이 이어져요. 거절된 청혼도 이 분쟁의 일부로 남겨요.",
        "cefr_level": "B2",
        "difficulty_score": "66",
    },
    1071: {
        "english": "The speaker says they have never been asleep on their ears and warns the listener not to miss a third occurrence after two times. An opaque name or phrase asks who killed someone. The speaker says they do not know, asks what the listener is doing there, and explains that they went to see bread and found an opaque daʿwa or situation; the French-derived and surface forms are retained without naming a person Omer.",
        "korean": "화자는 자신이 귀를 닫고 자고 있는 적이 한 번도 없었다는 식으로 말하며 두 번에 이어 세 번째 일을 놓치지 말라고 해요. 누가 누군가를 죽였는지 묻는 불투명한 표현이 나오고, 자신은 모른다고 해요. 상대가 여기서 무엇을 하는지 묻고 빵을 보러 갔다가 불투명한 ‘daʿwa’나 상황을 발견했다고 설명해요. ‘عمر ما’를 사람 이름 오메르로 확정하지 않고 표면형과 프랑스어계 표현을 보존해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
        "cefr_level": "B2",
        "difficulty_score": "64",
    },
    1073: {
        "english": "The speaker says the listener must take responsibility and that no one among them should move until a forensic doctor is brought. The French-derived surface disambisil is retained as the insult des imbéciles or an opaque related insult, not as a technical term; the speaker complains that the listener and doctor are both getting them into trouble.",
        "korean": "화자는 상대가 책임을 져야 한다고 하며 법의학 의사를 데려올 때까지 그들 중 누구도 움직이면 안 된다고 해요. 프랑스어계 표면형 ‘disambisil’을 ‘des imbéciles’ 같은 모욕 또는 그와 관련된 불투명한 모욕으로 보존하고 기술 용어로 꾸미지 않아요. 상대와 의사가 모두 자신을 곤란하게 만든다고 불평해요.",
        "cefr_level": "B2",
        "difficulty_score": "62",
    },
    1074: {
        "english": "The speaker complains that the others would not give the item to them, saying it is a matter of hearts rather than arms or force. An opaque clause involving the mother's wad or valley/river surface follows, and the speaker curses the devil; no movement or taking event is added.",
        "korean": "화자는 상대가 그 물건을 자신에게 주지 않았다며 이것은 팔이나 힘의 문제가 아니라 마음의 문제라고 말해요. 어머니의 ‘wad’나 계곡·강을 가리킬 수 있는 불투명한 절이 이어지고 악마를 저주해요. 이동이나 물건을 가져간 사건을 임의로 추가하지 않아요.",
        "cefr_level": "B1",
        "difficulty_score": "38",
    },
    1078: {
        "english": "The speaker rejects violence and then says that after the war the others want to eat them. They curse the others, say the war began because of the listener's condition or because of the listener, and warn that the others will pay dearly.",
        "korean": "화자는 폭력에 반대한다고 말한 뒤 전쟁이 끝나면 상대가 자신들을 먹으려 한다고 해요. 상대를 저주하고 상대의 상태나 상대 때문에 전쟁이 시작됐다고 하며 큰 대가를 치르게 될 것이라고 경고해요.",
        "cefr_level": "B1",
        "difficulty_score": "44",
    },
    1079: {
        "english": "The speaker orders the team to be called and asks why a war has been brought to them, saying they are waiting for or expecting the others. They address a daughter or sister, ask where she is from, call her a free Indian woman, note that she looks pale or yellow, and urge her to eat while using an opaque curse about what eats her.",
        "korean": "화자는 팀을 부르라고 하며 왜 전쟁을 자신들에게 가져왔느냐고 묻고 상대를 기다리고 있거나 맞이할 준비를 하고 있다고 해요. 딸이나 여동생을 부르고 어디 출신인지 묻고 자유로운 인디언 여성이라고 하며 창백하거나 누렇게 보인다고 말해요. 먹으라고 재촉하고 무엇이 그녀를 먹는다는 불투명한 저주를 해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
        "cefr_level": "B2",
        "difficulty_score": "68",
    },
    1080: {
        "english": "The speaker addresses Madam Sawsan and says this is not the Sawsan they are following, then uses an affectionate flower-like address. They ask who the person is and identify the person as the shaf or chief of the Sons of the Day tribe; no daughter relationship is added.",
        "korean": "화자는 수산 부인에게 말을 걸며 자신들이 따르는 수산은 이런 사람이 아니라고 해요. 꽃처럼 다정한 호칭을 쓰고, 상대가 누구냐고 물은 뒤 ‘울라드 나하르’ 부족의 shaf 또는 부족장이라고 설명해요. 딸이라는 관계는 추가하지 않아요.",
        "topic": "identifying_tribal_chief_of_sons_of_day",
        "processing_flags": "code_switching|source_ambiguity",
        "cefr_level": "B1",
        "difficulty_score": "38",
    },
    1081: {
        "english": "The speaker welcomes the visitors and asks why they have come now, saying they use an opaque expression that may be the French-derived répéter rather than explicitly saying they were getting ready. They ask how many people there are, and the answer is two and a half or one and a half; the exchange ends with a welcoming formula.",
        "korean": "화자는 방문객을 환영하며 왜 지금 왔느냐고 묻고, 준비 중이었다고 확정하지 않은 채 프랑스어계 ‘répéter’처럼 들릴 수 있는 불투명한 표현을 써요. 몇 명이 왔는지 묻자 둘 반이나 한 명 반이라는 답이 나오고 환영 인사로 이어져요.",
        "processing_flags": "code_switching|source_ambiguity",
        "cefr_level": "B1",
        "difficulty_score": "42",
    },
    1082: {
        "english": "The speaker jokes about increasing the number of opaque items and welcomes the visitors. They say they brought a danda or similarly opaque item, while the other person brought a dog that will eat him and his children; the comic exchange ends by joining the two speakers.",
        "korean": "화자는 불투명한 대상의 수가 늘었다고 농담하며 방문객을 환영해요. 자신은 ‘danda’처럼 들리는 불투명한 것을 가져왔고, 상대는 그 사람과 그의 아이들을 먹을 개를 가져왔다고 해요. 두 사람이 함께한다는 식으로 희극적 대화를 마무리해요.",
        "cefr_level": "B1",
        "difficulty_score": "46",
    },
    1083: {
        "english": "The speaker asks whether the listener wants to see it and asks for sticks. They first request large ones, then small ones, and criticize the sticks as soft or merely finger-like. They say the listener should have brought something for themselves instead of bringing it for others, perhaps adding that they should speak a little; the final dwi surface is not translated as providing light.",
        "korean": "화자는 상대가 그것을 보고 싶은지 묻고 막대기를 달라고 해요. 처음에는 큰 것을, 다음에는 작은 것을 요구하며 막대기가 물렁하거나 손가락 같다고 비판해요. 다른 사람을 위해 가져오기보다 자신을 위해 가져왔어야 했다며 조금 말하라는 듯한 말을 하고, 마지막의 ‘dwi’를 빛을 제공한다는 뜻으로 확정하지 않아요.",
        "cefr_level": "B2",
        "difficulty_score": "58",
    },
}

STRUCTURAL_FLAGS = {
    1034: "code_switching|source_ambiguity",
    1035: "code_switching|long_source|source_ambiguity",
    1043: "code_switching|source_ambiguity",
    1049: "code_switching|source_ambiguity",
    1053: "code_switching|long_source|source_ambiguity",
    1056: "code_switching|source_ambiguity",
    1057: "code_switching|source_ambiguity",
    1063: "code_switching|long_source|source_ambiguity",
    1064: "code_switching|source_ambiguity",
    1070: "code_switching|source_ambiguity",
    1071: "code_switching|long_source|source_ambiguity",
    1072: "code_switching|source_ambiguity",
    1076: "code_switching|source_ambiguity",
    1077: "code_switching|source_ambiguity",
    1079: "code_switching|long_source|source_ambiguity",
    1080: "code_switching|source_ambiguity",
    1081: "code_switching|source_ambiguity",
    1086: "code_switching|long_source|source_ambiguity",
}
for _sentno, _flags in STRUCTURAL_FLAGS.items():
    CORRECTIONS.setdefault(_sentno, {})["processing_flags"] = _flags

for _sentno, _flags in {1040: "", 1052: ""}.items():
    CORRECTIONS.setdefault(_sentno, {})["processing_flags"] = _flags

SCORE_CORRECTIONS = {
    1031: ("B1", "42"),
    1032: ("B1", "50"),
    1033: ("B1", "36"),
    1034: ("B1", "38"),
    1035: ("B1", "44"),
    1036: ("B1", "40"),
    1037: ("A2", "24"),
    1040: ("A1", "12"),
    1041: ("B2", "58"),
    1042: ("A2", "24"),
    1044: ("B1", "48"),
    1046: ("B1", "34"),
    1047: ("A2", "34"),
    1048: ("A2", "28"),
    1050: ("A2", "24"),
    1053: ("B1", "42"),
    1054: ("B1", "38"),
    1056: ("B1", "44"),
    1057: ("B1", "48"),
    1061: ("B2", "58"),
    1067: ("B2", "62"),
    1070: ("B1", "42"),
    1075: ("B2", "58"),
    1076: ("B1", "46"),
    1077: ("B1", "44"),
    1084: ("A2", "30"),
    1085: ("B1", "40"),
    1086: ("B2", "64"),
    1087: ("B1", "50"),
    1088: ("A2", "22"),
}
for _sentno, (_cefr, _score) in SCORE_CORRECTIONS.items():
    CORRECTIONS.setdefault(_sentno, {}).update({"cefr_level": _cefr, "difficulty_score": _score})


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
