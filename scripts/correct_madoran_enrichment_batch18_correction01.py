"""Apply HeadGPT-directed source-close corrections for MADOran Batch 18."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch18 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "93418c3"
BATCH_ID = "MADORAN-ENRICH-018"
CORRECTION_ID = "MADORAN-ENRICH-018-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v18-correction-1"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch18_correction01_qa.json"
PROVENANCE_BEFORE = 15725

CORRECTIONS = {
    1089: {
        "english": "The speaker says, ‘Be quiet or do not be quiet; you want to drive me out of my mind.’ They then say, ‘You want my head to rise with hair in it,’ preserving the direct second-person direction and the hair surface.",
        "korean": "화자는 ‘조용히 해, 아니면 조용히 하지 마. 너 때문에 내가 미치겠다’라고 해요. 이어 ‘네가 내 머리에 머리카락이 곤두서게 하려 한다’는 식으로 말하며 2인칭 방향과 머리카락 표면을 보존해요.",
        "domain": "daily_life",
        "topic": "reproach_about_driving_someone_mad",
    },
    1090: {
        "english": "In a long exchange, the speaker says they will tell and explain something, then says they are stuck or present with ghwla and a charm or talisman. They say someone will talk and that they will sell the listener, then mention selling or betraying people, selling them outside at Buya, the Sons of the Day finishing them at a high price, continuing to betray and sell, and living with or near Ghoula in blessing. The speaker says the Sons of the Day brought them here and ends by telling the listener to be quiet; actors and clauses remain separate.",
        "korean": "긴 대화에서 화자는 말하고 설명하겠다고 한 뒤 ghwla와 부적이나 주문 곁에 있다고 해요. 누군가가 말할 것이며 상대를 팔겠다고 하고, 사람들을 팔거나 배신하는 일, Buya 밖에서 그들을 파는 일, 울라드 나하르가 비싸게 마무리할 것, 계속 배신하고 파는 일을 차례로 말해요. 축복 속에서 Ghoula와 함께 살겠다고 하고 울라드 나하르가 자신을 여기로 데려왔다고 한 뒤 상대에게 조용히 하라고 해 행위자와 절을 분리해요.",
    },
    1091: {
        "english": "The speaker says, ‘I am bringing you a sal3a; what is yours, you?’ and addresses the listener with an opaque sh7ma or ground-related surface. They say they brought a commodity of their life and that one item speaks by itself and another speaks in its own voice; the source does not require the items to move.",
        "korean": "화자는 ‘내가 너에게 sal3a를 가져왔어. 네 것은 무엇이냐?’라고 하며 상대에게 불투명한 sh7ma와 땅 관련 표면형으로 말을 걸어요. 자신의 삶의 상품을 가져왔다고 하고 한 물건은 혼자 말하고 다른 물건은 자기 목소리로 말한다고 하며 물건이 움직인다고 추가하지 않아요.",
    },
    1092: {
        "english": "The speaker tells the listener to look at the sal3a and show it to someone, then says it is a piece or bead called 7ba krawswn. They ask where it was brought from and insult the person who despises it; the croissant-like surface and the question direction are retained.",
        "korean": "화자는 상대에게 sal3a를 보고 누군가에게 보여 주라고 한 뒤 그것이 7ba krawswn이라는 조각이나 알갱이라고 해요. 어디서 가져왔는지 묻고 그것을 업신여기는 사람을 모욕하며 croissant처럼 들리는 표면과 질문 방향을 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1093: {
        "english": "The speaker exclaims and asks whether the listeners know how to hunt, listing lizandian and other named or foreign-derived hunting surfaces. They say there is no barbar, tarzo, or fundamat, then ask what they should do with what was brought; the list is retained without normalizing the terms.",
        "korean": "화자는 감탄하며 상대가 사냥할 줄 아는지 묻고 lizandian과 다른 명명되거나 외래어처럼 들리는 사냥 표면형을 나열해요. barbar·tarzo·fundamat은 없다고 한 뒤 가져온 것으로 무엇을 해야 하느냐고 묻고 목록을 정규화하지 않아요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    1094: {
        "english": "The speaker says, ‘This, I will poke with it; it is on me,’ bargains over ten doro, refuses to give it, and then asks the friend to give eight doro. The repeated dih 3lia direction is preserved.",
        "korean": "화자는 ‘이것을 그것으로 찌를 거야. 이것은 내게 있어’라고 하며 10도라를 흥정하고 주지 않겠다고 한 뒤 친구에게 8도라를 달라고 해요. 반복되는 dih 3lia 방향을 보존해요.",
    },
    1095: {
        "english": "The speaker refuses to give it for nothing, says there are six doro or four doro, and distinguishes the money from the money for bran and feed. They say the feed is used for al3wad; that animal surface is retained without changing it to cows.",
        "korean": "화자는 이것을 공짜로 주지 않겠다고 하며 6도라 또는 4도라가 있다고 해요. 그 돈은 겨와 사료를 위한 돈과 다르며 al3wad에게 먹인다고 말해 al3wad 동물 표면을 소로 확정하지 않아요.",
    },
    1096: {
        "english": "The speaker says they will sleep with it unless it is sold, tells the listener to go, and says, ‘It bit me, look,’ preserving the explicit 3dni shwfi bitten-me-and-look clause before the remaining opaque wording.",
        "korean": "화자는 이것이 팔리지 않으면 함께 자겠다고 하며 상대에게 가라고 해요. 이어 ‘이것이 나를 물었어, 봐’라고 말해 명시적인 3dni shwfi 절을 보존하고 나머지 불투명한 표현은 확정하지 않아요.",
    },
    1097: {
        "speech_act": "wish",
    },
    1101: {
        "english": "The speaker says they will add an opaque kind of money and complains, ‘You did not give them to me, my friend. Listen—you did not give me my due.’ The direction is that the listener withheld them from the speaker.",
        "korean": "화자는 불투명한 종류의 돈을 더 주겠다고 하며 ‘친구야, 네가 그것들을 내게 주지 않았어. 들어 봐, 네가 내 몫을 주지 않았어’라고 불평해요. 상대가 화자에게 주지 않았다는 방향을 보존해요.",
    },
    1102: {
        "english": "The speaker tells the listener not to repeat this talk and says, ‘They gave me fiza next time,’ preserving the source's actor and time direction rather than turning it into a request for a visa. The speaker then says they will not meet the listener, will meet ghoula and lizandian, tells them to follow, and curses the service.",
        "korean": "화자는 이런 말을 다시 하지 말라고 하며 ‘다음에는 그들이 내게 fiza를 줬어’라는 식으로 원문의 행위자와 시간 방향을 보존해요. 이를 visa를 달라는 요청으로 바꾸지 않아요. 이어 상대를 만나지 않고 ghoula와 lizandian을 만나겠다고 하며 따라오라고 하고 그 일을 저주해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1103: {
        "english": "In the long exchange, the speaker preserves the explicit turns: they say the others brought you, the speaker did not bring you, tell someone dwni or let me down, mention a rendez-vous, distinguish a7na dinak from a7na ma dinaksh, say they took a risk and came yesterday, and describe the cold, hunger, and thirst after being housed in kadous. The actors and the repeated turns are not compressed.",
        "korean": "긴 대화에서 화자는 ‘그들이 너를 데려왔고 나는 데려오지 않았다’는 turn을 보존하고, dwni 또는 자신을 내려 달라고 하며 rendez-vous를 언급해요. a7na dinak과 a7na ma dinaksh를 구분하고 위험을 감수해 어제 왔다고 한 뒤 kadous에 머물며 추위·배고픔·갈증을 겪었다고 말해 행위자와 반복 turn을 압축하지 않아요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    1105: {
        "english": "The speaker says, ‘I grew a moustache, my brother, so that I would not understand—yes?’ and then addresses a son: ‘My child, do it with Boujadia as you did not do it with us.’ The rbit mwstash surface and the separate Boujadia turn are preserved.",
        "korean": "화자는 ‘형제야, 내가 콧수염을 길러서 이해하지 못하게 되었어, 그렇지?’라는 식으로 말한 뒤 아들에게 ‘얘야, Boujadia와 해. 너희가 우리와는 그렇게 하지 않았잖아’라고 해요. rbit mwstash 표면과 별도의 Boujadia turn을 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1106: {
        "english": "The speaker tells someone to raise their hands and look, calls them za3bata, asks where their friend is, and says the friend is in the forest hunting. They say they do not know what the friend is doing, then say, ‘I am rani rwbw liwm,’ preserving the repos or day-off-like surface without fixing it as robot. They came to stroll for a short while and continue with the remaining opaque commands.",
        "korean": "화자는 상대에게 손을 들고 보라고 하며 za3bata라고 부르고 친구가 어디 있는지 물어요. 친구가 숲에서 사냥한다고 하며 무엇을 하는지 모른다고 한 뒤 ‘나는 rani rwbw liwm’이라고 해 repos나 휴무처럼 들리는 표면을 로봇으로 확정하지 않고 보존해요. 잠시 산책하러 왔다고 하고 나머지 불투명한 명령을 이어 가요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    1107: {
        "english": "The speaker addresses a friend, says ‘come back 24 times,’ and says, ‘I kill you and do not die,’ preserving the repeated kill/threat surface ana nktl fik w ma mtsh. They tell the listener not to worry and to understand one another, then continue with the opaque danger and name surfaces.",
        "korean": "화자는 친구를 부르며 ‘24번 돌아와’라고 하고 ‘내가 너를 죽여도 나는 죽지 않아’라는 식의 반복적인 살해·위협 표면 ana nktl fik w ma mtsh를 보존해요. 걱정하지 말고 서로 이해하자고 한 뒤 불투명한 위험과 이름 표면을 이어 가요.",
    },
    1108: {
        "english": "The speaker says that after five minutes they were absent or distracted, then says they killed one person and that bullets are not allowed. The warning and threat structure are preserved without inventing a new scene.",
        "korean": "화자는 5분 뒤 자신이 없었거나 정신이 팔려 있었다고 하고, 한 사람을 죽였으며 총알은 허용되지 않는다고 해요. 새로운 장면을 만들어내지 않고 경고와 위협 구조를 보존해요.",
        "processing_flags": "",
        "enrichment_state": "draft",
    },
    1109: {
        "english": "The speaker says that the weddings or l3ras are not ready during Ramadan and that everyone is unaware. The l3ras wedding surface is retained rather than being changed to heads or people.",
        "korean": "화자는 라마단 동안 결혼식 또는 l3ras가 준비되지 않았고 모두가 알지 못한다고 해요. l3ras의 결혼식 표면을 머리나 사람으로 바꾸지 않고 보존해요.",
    },
    1110: {
        "english": "The speaker says they stayed or waited for three days, preserving kl 3 jwgh as a three-day French-derived code-switched surface, and continues with the remaining opaque wording.",
        "korean": "화자는 3일 동안 머물렀거나 기다렸다고 하며 kl 3 jwgh의 3일이라는 프랑스어 유래 코드스위칭 표면을 보존하고 나머지 불투명한 표현을 이어 가요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1111: {
        "english": "The speaker mentions rwjistr dw kwmars, preserving the registre du commerce surface and its uncertain preceding context. No invented two-hour register is added.",
        "korean": "화자는 rwjistr dw kwmars를 언급하며 registre du commerce 표면과 앞부분의 불확실한 맥락을 보존해요. 존재하지 않는 ‘두 시간 등록’을 추가하지 않아요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1112: {
        "english": "The speaker preserves lizambwa as the les impôts or taxes surface, without turning it into an opaque task.",
        "korean": "화자는 lizambwa를 les impôts 또는 세금이라는 표면으로 보존하고 불투명한 과업으로 바꾸지 않아요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1113: {
        "english": "The exchange preserves the ask-direction surfaces slkti, slkini, and nslkk: the speaker asks to be freed, saved, or released and keeps the actors and direction separate.",
        "korean": "대화는 slkti·slkini·nslkk의 요청 방향을 보존해요. 화자가 자유롭게 해 달라거나 구해 달라거나 풀어 달라고 요청하며 행위자와 방향을 분리해요.",
    },
    1114: {
        "english": "The speaker says they are clever or alert, preserving 9afz in that direction, and retains kwbwiz as a cowboys-like code-switched surface rather than changing it to coupons.",
        "korean": "화자는 영리하거나 눈치가 빠르다고 하며 9afz를 그 방향으로 보존하고, kwbwiz는 쿠폰으로 바꾸지 않고 cowboys처럼 들리는 코드스위칭 표면으로 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1115: {
        "english": "The speaker says, ‘I will not free or save you; free yourself,’ preserving the direction of mnslkaksh rather than changing it to ‘I will not ask.’",
        "korean": "화자는 ‘내가 너를 풀어 주거나 구해 주지 않을 테니 네가 스스로 풀려나라’고 하며 mnslkaksh의 방향을 보존하고 ‘내가 묻지 않겠다’로 바꾸지 않아요.",
    },
    1117: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    1119: {
        "english": "The speaker says they did not play with dogs, preserving ma la3it klab, then retorts by asking how or when the listener knew that the speaker was their son. The question remains a retort, not a statement.",
        "korean": "화자는 ma la3it klab, 즉 개들과 놀지 않았다고 보존해요. 이어 상대가 자신이 상대의 아들이라는 것을 어떻게 또는 언제 알았느냐고 되묻고, 이를 진술문으로 바꾸지 않아요.",
        "processing_flags": "cefr_boundary|long_source|source_ambiguity",
    },
    1121: {
        "english": "The speaker says that some people do not understand and preserves n9st as a first-person state or condition rather than adding a quantified group of two people.",
        "korean": "화자는 어떤 사람들은 이해하지 못한다고 하며 w7din을 두 사람으로 수량화하지 않고 ‘어떤 사람들’로 보존해요. n9st는 1인칭의 상태나 조건으로 보존해요.",
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
    1122: {
        "english": "The speaker says, ‘You are not my father; clearly, you are not my father.’ A friend tells them not to cry and to understand with them. The parentage denial is preserved without treating bwia as a named person.",
        "korean": "화자는 ‘너는 내 아버지가 아니야. 분명히 너는 내 아버지가 아니야’라고 해요. 친구는 울지 말고 그들과 함께 이해하라고 해요. bwia를 이름으로 처리하지 않고 친자관계 부인을 보존해요.",
        "topic": "denial_of_parentage",
        "processing_flags": "",
        "enrichment_state": "draft",
    },
    1123: {
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
    1125: {
        "english": "The exchange is about Juventus: the speaker asks about the previous day's score and the response is zero-zero. Juventus, the score question, and the zero-zero answer are preserved.",
        "korean": "대화는 Juventus에 관한 것으로, 화자는 전날 경기 점수를 묻고 대답은 0 대 0이에요. Juventus, 점수 질문, 0 대 0 답변을 보존해요.",
        "domain": "sports",
        "topic": "football_score_question_and_response",
        "processing_flags": "long_source",
        "enrichment_state": "draft",
    },
    1126: {
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
    1127: {
        "english": "The speaker explicitly says dra3i laimn, ‘my right arm,’ preserving the body-part direction rather than introducing a Yemeni interpretation.",
        "korean": "화자는 dra3i laimn, 즉 ‘내 오른팔’이라고 명시해요. 예멘인이라는 해석을 추가하지 않고 신체 부위 방향을 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1128: {
        "english": "The speaker preserves the kill-negation direction of ma iktlwhsh: they say that he or they did not kill him or them. It is not an instruction not to eat.",
        "korean": "화자는 ma iktlwhsh의 살해 부정 방향을 보존해요. 누군가가 그를 또는 그들을 죽이지 않았다고 하며 ‘먹지 마’라는 지시로 바꾸지 않아요.",
    },
    1129: {
        "english": "The speaker tells the listener to come directly or come in front, preserving ijwh 9bala without adding tomorrow. The zghratat surface is retained as ululations rather than a generic sound.",
        "korean": "화자는 ijwh 9bala를 직접 오거나 앞으로 오라는 뜻으로 보존하고 ‘내일’을 추가하지 않아요. zghratat는 일반적인 소리가 아니라 축하의 울음소리나 ululation 표면으로 보존해요.",
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
    1131: {
        "english": "The speaker refers to flkwzina as the kitchen, preserving the kitchen surface rather than treating it as an opaque place name.",
        "korean": "화자는 flkwzina를 부엌이나 주방으로 말하며 불투명한 장소 이름으로 처리하지 않고 주방 표면을 보존해요.",
    },
    1132: {
        "english": "The speaker says it is under 10,000 doro, preserving t7t 10 mil dwrwa as the amount and its code-switched money surface rather than interpreting it as ten miles or doro as an alternative.",
        "korean": "화자는 10,000도라 아래라고 하며 t7t 10 mil dwrwa의 금액과 코드스위칭 화폐 표면을 보존해요. 이를 10마일 또는 ‘doro’ 중 하나로 바꾸지 않아요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1134: {
        "english": "The speaker refers to the man with a black chapeau or hat, preserving mwl shabw lk7l as that hat surface. The meaning of ma alghalia remains uncertain and is not arbitrarily fixed as expensive.",
        "korean": "화자는 검은 샤포 또는 모자를 쓴 남자를 말하며 mwl shabw lk7l의 모자 표면을 보존해요. ma alghalia의 의미는 불확실한 채로 두고 임의로 ‘비싸다’로 확정하지 않아요.",
        "processing_flags": "cefr_boundary|code_switching|source_ambiguity",
    },
    1135: {
        "english": "The speaker says, ‘You are one of us,’ preserving ntia mna without inserting a negation. They then tell the listener to shut their mouth, preserving bl3i fmk rather than translating it as swallow it.",
        "korean": "화자는 ‘너는 우리 중 하나야’라고 하며 ntia mna에 존재하지 않는 부정을 넣지 않아요. 이어 bl3i fmk를 ‘삼켜’가 아니라 ‘입 다물어’로 보존해요.",
    },
    1137: {
        "english": "The long exchange preserves the opening w9ila krat lkm alskna mdam as a possibly housing or rent-related turn with madam, and preserves the final turn kirakm dairin ia sidi as ‘how are you, sir?’ rather than a reproach.",
        "korean": "긴 대화의 시작 w9ila krat lkm alskna mdam은 주거 또는 임대와 관련된 말일 가능성과 madam 호칭을 보존해요. 마지막 kirakm dairin ia sidi는 비난이 아니라 ‘어떻게 지내세요, 선생님?’이라는 turn으로 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|long_source|source_ambiguity",
    },
    1138: {
        "english": "The speaker says lafwt ta3i, ‘it is my fault,’ and says that flitsha deceived them. The actor direction is preserved rather than making the speaker fail to pass someone else's matter.",
        "korean": "화자는 lafwt ta3i, 즉 ‘내 잘못이야’라고 하고 flitsha가 자신을 속였다고 해요. 화자가 다른 사람의 일을 처리하지 못했다는 방향으로 뒤집지 않고 행위자 방향을 보존해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    1139: {
        "english": "The speaker preserves 3mwmia and nswbia as kinship or relative surfaces and aligns them with wlad 3m, the children or relatives of an uncle, without reducing the turn to generic speaking in general.",
        "korean": "화자는 3mwmia와 nswbia를 친족 또는 친척 관련 표면으로 보존하고 wlad 3m, 즉 삼촌의 자녀나 친척이라는 표면과 맞춰요. 이를 단순히 ‘일반적으로 말하기’로 축소하지 않아요.",
    },
    1140: {
        "english": "The French-derived turn si di 9ws, si di zwnfwn, ail saf ba sw ki diz is retained as a children-or-kids-do-not-know-what-they-say surface. The speaker threatens, ‘we eat his flesh,’ and khatik means leave it or mind your own business, not leave your brother.",
        "korean": "프랑스어 유래 turn si di 9ws, si di zwnfwn, ail saf ba sw ki diz는 아이들이 무슨 말을 하는지 모른다는 표면으로 보존해요. 화자는 ‘우리가 그의 살을 먹겠다’고 위협하고, khatik은 ‘내버려 둬’ 또는 ‘네 일이나 신경 써’라는 뜻으로 보존하며 ‘네 형제를 떠나라’로 바꾸지 않아요.",
        "processing_flags": "cefr_boundary|code_switching",
        "enrichment_state": "draft",
    },
    1141: {
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
    1142: {
        "english": "The speaker gives an imperative: ‘Come kidnap me, or kidnap this person.’ The command structure of arwa7 khtfni w la khtf hada is preserved rather than being reported as a past kidnapping.",
        "korean": "화자는 ‘와서 나를 납치해, 아니면 이 사람을 납치해’라고 명령해요. arwa7 khtfni w la khtf hada의 명령 구조를 과거의 납치 사건으로 바꾸지 않고 보존해요.",
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
    1143: {
        "english": "The speaker says they want to become Indian like the listener and repeats the Indian identity turn. The surfaces w7din m3aia and w7din m3ak remain ‘some with me’ and ‘some with you,’ not two each. The speaker says that the listener and their friend tied them, preserving ktftwni.",
        "korean": "화자는 상대처럼 인도인이 되고 싶다고 하며 인도인 정체성 turn을 반복해요. w7din m3aia와 w7din m3ak은 각각 두 명이 아니라 ‘나와 함께 있는 몇몇’과 ‘너와 함께 있는 몇몇’으로 보존해요. 상대와 그 친구가 자신을 묶었다고 하며 ktftwni를 보존해요.",
        "processing_flags": "cefr_boundary|long_source|source_ambiguity",
    },
    1145: {
        "english": "The speaker addresses the listener with bwia as a dad or father vocative, preserving the father surface rather than treating it as the name Boiya.",
        "korean": "화자는 bwia로 상대를 아버지라고 부르며 Boiya라는 이름으로 처리하지 않고 아버지 호격 표면을 보존해요.",
        "processing_flags": "cefr_boundary",
    },
    1146: {
        "english": "Mr Hazim is the addressee of the question ‘I want to ask you,’ not the speaker being named as Hazim. The speaker preserves jasws as a spy or informer surface, says it is a surprise or une surprise, tells the listener not to move or budge, and mentions the water and grain clause. The roles and French-derived surface are retained.",
        "korean": "‘당신에게 묻고 싶습니다’라고 말하는 화자는 Hazim 씨에게 말하는 것이며 화자 자신을 Hazim으로 부르는 것이 아니에요. jasws는 스파이나 밀고자 표면으로 보존하고, 놀라움 또는 une surprise를 말하며, 상대에게 움직이거나 꼼짝하지 말라고 해요. 물과 곡식 절도 보존하고 역할과 프랑스어 유래 표면을 유지해요.",
        "processing_flags": "cefr_boundary|code_switching|source_ambiguity",
    },
    1147: {
        "english": "The speaker gives the imperative go, donkey, preserving mshi 7mar as a command and retaining 9wfrit as an uncertain surface. It is not the statement that someone is not a donkey.",
        "korean": "화자는 ‘가, 당나귀야’라고 명령하며 mshi 7mar를 명령형으로 보존하고 9wfrit는 불확실한 표면으로 남겨요. 누군가가 당나귀가 아니라는 진술로 바꾸지 않아요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1149: {
        "english": "Abdelkader says, ‘How are you?’ The row does not add a Hawari recipient.",
        "korean": "압델카데르는 ‘어떻게 지내?’라고 말해요. 이 행에는 Hawari 수신자를 추가하지 않아요.",
    },
    1150: {
        "english": "Hawari says, ‘Fine, praise be to God, and you?’ The row does not add Abdelkader as the recipient.",
        "korean": "Hawari는 ‘괜찮아, 신께 찬미를, 너는?’이라고 말해요. 이 행에는 압델카데르 수신자를 추가하지 않아요.",
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
    result = engine.apply()

    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = 20
    status["counts"]["enrichment_flagged_rows"] = 802
    status["enrichment_correction_id"] = CORRECTION_ID
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = 20
    qa["flagged_rows"] = 44
    qa["correction_state_updates"] = 4
    qa["correction_history"][-1]["state_updates"] = 4
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 4
    correction["batch_artifact_sync_state_updates"] = 4
    correction["draft_rows"] = 20
    correction["flagged_rows"] = 44
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 4, "draft_rows": 20, "flagged_rows": 44})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
