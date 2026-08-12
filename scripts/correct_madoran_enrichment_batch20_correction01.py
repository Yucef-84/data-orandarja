"""Apply HeadGPT-directed source-close corrections for MADOran Batch 20."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch20 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "c33ec29"
BATCH_ID = "MADORAN-ENRICH-020"
CORRECTION_ID = "MADORAN-ENRICH-020-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v20-correction-1"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch20_correction01_qa.json"
PROVENANCE_BEFORE = 17618


CORRECTIONS = {
    1217: {
        "english": "The source presents Oran as a premier city with Ottoman architecture and mentions the known surface ‘Bastos’ without deciding whether it names a person, building, or other thing. It then says that when you want to talk about Oran, speak freely.",
        "korean": "원문은 오랑을 오스만 건축이 있는 뛰어난 도시로 제시하고, 인물·건물·다른 대상을 가리킬 수 있는 ‘Bastos’라는 알려진 표면을 한 가지로 확정하지 않고 언급해요. 이어 오랑에 대해 말하고 싶으면 자유롭게 말하라고 해요.",
    },
    1218: {
        "english": "The speaker says that when they hear the story or history called ‘krantika’, it is nonsense upon nonsense, and that the story did not happen at all as it is being told.",
        "korean": "화자는 ‘krantika’라고 불리는 이야기나 역사에 대해 들으면 허튼소리의 연속이라고 하며, 그 이야기가 전해지는 방식대로는 전혀 일어나지 않았다고 말해요.",
        "topic": "rejecting_a_krantika_history_claim",
    },
    1220: {
        "english": "The speaker argues that the Spanish were not besieged in Oran: they entered and colonized it, and asks why they could not go on to colonize other cities if that was a siege. They stayed for three centuries; if they were supposedly besieged while the Ottoman fleet was among the world's strongest, why was Oran not liberated?",
        "korean": "화자는 스페인인들이 오랑에서 포위된 것이 아니라 들어와 식민화했다고 주장하며, 그것이 포위였다면 왜 다른 도시까지 계속 식민화하지 못했겠느냐고 물어요. 스페인인들은 3세기 동안 머물렀고, 오스만 함대가 세계 최강급이었다는데도 포위된 상태였다면 왜 오랑을 해방하지 못했는지 반문해요.",
    },
    1222: {
        "english": "The speaker says Oran contains a great deal of beautiful talk and makes one feel that one is discussing a civilization and a large city, not a village and the source-close surface ‘si malogua’. They welcome everyone who lives in Oran and everyone who arrived, including the surfaces ‘ma 3ndnash brani’, ‘mr7ba b Tlemond’, ‘iaba d w problam’, and ‘fif awrwn’. They say they will not speak about something that is absent, but will tell what happened without forcing a good-or-bad judgment.",
        "korean": "화자는 오랑에는 크고 아름다운 이야기가 많아 작은 마을이나 원문의 ‘si malogua’가 아니라 문명과 큰 도시를 말하는 느낌이 든다고 해요. 오랑에 사는 사람과 찾아온 사람을 모두 환영하며 ‘ma 3ndnash brani’, ‘mr7ba b Tlemond’, ‘iaba d w problam’, ‘fif awrwn’ 같은 표면도 보존해요. 없는 말을 하지 않고 좋다·나쁘다를 억지로 판단하지 않으면서 일어난 일을 말하겠다고 해요.",
    },
    1227: {
        "english": "The speaker jokes that this is their bad luck: the mafia betrays people, while the speaker has ended up with this person. They call the person frightening and ask what this is, brother.",
        "korean": "화자는 이것이 자신의 운이 나쁜 일이라고 농담해요. 마피아가 사람들을 배신하는데 자신은 이 사람에게 걸렸다고 말하고, 상대가 무섭다며 ‘이게 뭐야, 형제야’라는 식으로 말해요.",
    },
    1228: {
        "english": "The speaker asks for ‘khdmi Abdine’ to be brought, keeping the servant, helper, or person's name-like surface rather than converting it to work. They ask what the listener wants to do with him or it, then say, ‘You will see what I want to do with him or it.’",
        "korean": "화자는 일이라는 뜻으로 바꾸지 않고 하인·도우미·사람 이름처럼 보이는 ‘khdmi Abdine’ 표면을 가져오라고 해요. 그것 또는 그 사람에게 무엇을 하려는지 묻고, 자신이 무엇을 하려는지 곧 보게 될 것이라고 말해요.",
        "topic": "opaque_request_about_abdine",
    },
    1231: {
        "english": "The speaker says that their sister Chahinaz thinks the speaker is good at nothing—not cooking and not cleaning. The speaker recalls being mocked after cleaning the house with a face tissue, says they eat a lot, and retains the source-close ‘ndr b ghir mima’ rather than weakening it to merely bother their mother; the final joke remains partly opaque.",
        "korean": "화자는 여동생 샤히나즈가 자신을 요리도 청소도 못하고 아무것도 잘하지 못하는 사람으로 생각한다고 말해요. 얼굴 닦는 티슈로 집을 청소하다가 놀림받은 일을 떠올리고, 자신은 많이 먹는다고 하며 ‘ndr b ghir mima’라는 원문 표면을 어머니를 단순히 괴롭힌다는 뜻으로 약화하지 않고 보존해요. 마지막 농담은 일부 불투명하게 남겨요.",
    },
    1232: {
        "english": "The speaker states that the others are having breakfast, says that the addressee thinks she is in a restaurant, and accuses them of betraying or tricking God’s people at breakfast time. It is a complaint or exclamation, not primarily a question.",
        "korean": "화자는 일행이 아침을 먹고 있다고 말하고, 상대가 자신을 식당에 있는 줄 아느냐고 하며, 아침 식사 시간에 하느님의 사람들을 배신하거나 속인다고 비난해요. 주된 기능은 질문이 아니라 불평이나 감탄이에요.",
        "speech_act": "complaint",
    },
    1233: {
        "english": "The speaker asks for some bread with tomatoes and says they would die there without it. They say their series starts at two, that they will watch it and nap, and ask, ‘Don’t you have dimo here?’ The other turn answers, ‘No, there is not.’ The source-close dimo surface and both turns are retained before the request for a phone to connect for a while.",
        "korean": "화자는 토마토를 곁들인 빵을 조금 달라고 하며 그것이 없으면 여기서 죽겠다고 해요. 두 시에 시작하는 드라마를 보며 낮잠을 자겠다고 하고 ‘여기 dimo는 없어?’라고 물어요. 상대는 ‘아니, 없어’라고 답해요. 잠깐 연결하게 휴대전화를 달라는 요청에 앞서 dimo 표면과 두 turn을 모두 보존해요.",
    },
    1234: {
        "english": "The speaker asks, in a source-close first-person direction, whether they are the one who betrayed or tricked the listener, then says they will give the listener a phone so they can connect. The actor direction is not reversed into the listener tricking the speaker.",
        "korean": "화자는 자신이 상대를 배신하거나 속인 사람인지 원문에 가까운 1인칭 방향으로 묻고, 상대가 연결할 수 있도록 휴대전화를 주겠다고 해요. 상대가 화자를 속였다고 행위자를 뒤집지 않아요.",
    },
    1235: {
        "english": "The speaker asks what they have the right to do, says the others brought them to kill them with the opaque source surface ‘l9nta’, asks whether this is their house or the others’ house, and says ‘okay, brother, later, I swear.’ They then ask what else the listener wants and whether the listener wants to drive them crazy; the missing turn is restored without translating l9nta as humiliation.",
        "korean": "화자는 자신이 무엇을 할 권리가 있는지 묻고, 일행이 원문의 불투명한 ‘l9nta’와 함께 자신을 죽이려고 데려왔다고 해요. 여기가 자기 집인지 상대 집인지 묻고 ‘알겠어, 형제야, 나중에, 맹세해’라는 식으로 말해요. 이어 상대가 또 무엇을 원하며 자신을 미치게 하려는지 묻고, l9nta를 굴욕으로 확정하지 않아요.",
    },
    1237: {
        "english": "The speaker asks where the woman goes every day when she goes out ‘msh3ta’, retaining the source surface instead of reversing it to dressed up. They tell her to come look at the speaker, say the speaker is not a mirror, and continue with the opaque ‘awmwan … 7mir’ clause rather than inventing that she should install a mirror at home.",
        "korean": "화자는 여성이 매일 ‘msh3ta’인 채로 나갈 때 어디로 가는지 묻고, 이를 멋지게 차려입었다는 뜻으로 뒤집지 않아요. 자신에게 와서 보라고 하고 자신은 거울이 아니라고 말하며, 집에 거울을 설치하라는 뜻으로 창작하지 않고 ‘awmwan … 7mir’라는 불투명한 절을 보존해요.",
    },
    1238: {
        "english": "The speaker says Aicha has arrived and is teasing them, says a brother has gone to the army and that the clothes are tight, asks whether these are Nesrine’s trousers and why they are not being worn, and continues with the source-close cheek, Pikachu, groom, sister, and ‘men of the last age’ turns.",
        "korean": "화자는 아이샤가 와서 자신을 놀린다고 하고, 형제가 군대에 갔으며 옷이 꽉 끼었다고 말해요. 이것이 네스린의 바지인지 왜 입지 않았는지 묻고, 볼·피카츄·신랑·누이가 먼저 준비했다는 말·‘요즘 시대의 남자들’이라는 turn을 원문에 가깝게 이어 가요.",
    },
    1240: {
        "english": "The speaker greets the woman, asks how she is, and says they are coming and will not stay long. They say she looked like a respectable girl who had suffered a curse, say they do not know what she liked about the listener, complain that the mixed colors hurt their eyes like a rainbow, and end with the source-close face-and-man joke.",
        "korean": "화자는 여성에게 인사하고 잘 지내는지 물으며 곧 가고 오래 머물지 않겠다고 해요. 여성이 점잖은 사람처럼 보이지만 불운한 일을 당한 듯하다고 말하고, 그 여성이 상대의 무엇을 좋아했는지 모르겠다고 해요. 섞어 놓은 색이 무지개 같아 눈이 아프다고 불평한 뒤 얼굴과 남자에 관한 원문의 농담으로 끝내요.",
    },
    1241: {
        "english": "The speaker says the full religious expression ‘A3udhu billah min al-shaytan al-rajim’, says the listener made them explode, asks what the listener has put on their face, and jokes that all the household coffee and turmeric have been used up.",
        "korean": "화자는 ‘A3udhu billah min al-shaytan al-rajim’이라는 종교 표현 전체를 말하고 상대가 자신을 폭발하게 했다고 해요. 상대가 얼굴에 무엇을 발랐는지 묻고 집의 커피와 강황을 전부 쓴 것 같다고 농담해요.",
    },
    1243: {
        "english": "The speaker asks whether the listener has no shame, says they have merely kept quiet since morning, and complains that the listener makes noise while eating. ‘What is this—don’t you know how to eat in silence?’ is a rebuke, not an instruction not to be ashamed.",
        "korean": "화자는 상대에게 부끄러운 줄 모르느냐고 하며 아침부터 참고 있었다고 말해요. 상대가 먹을 때 소리를 낸다고 불평하고 ‘이게 뭐야, 조용히 먹을 줄 몰라?’라고 꾸짖어요.",
    },
    1244: {
        "english": "The speaker complains that the soup is salty and has no chickpeas. An older woman then asks her son to bring a woman who will fill the refrigerator and cook what he wants; she scolds or attacks without caring. The speaker says to eat the soup, then asks the listener to get ‘nakos’ from Qadri so they can share it; the source-close food surface is retained.",
        "korean": "화자는 국물이 짜고 병아리콩이 없다고 불평해요. 이어 나이 든 여성이 아들에게 냉장고를 채우고 원하는 음식을 해 줄 여자를 데려오라고 하며, 신경 쓰지 않고 꾸짖거나 공격하는 말이 나와요. 화자는 국물을 먹으라고 한 뒤 카드리에게서 ‘nakos’를 사 와 함께 먹자고 하고 음식 표면은 원문에 가깝게 보존해요.",
    },
    1245: {
        "english": "The speaker asks why the others are not eating the creamless savory pastries that the speaker made in the Oum Walid style or recipe line.",
        "korean": "화자는 자신이 움 왈리드식 또는 그 레시피 계열로 만든 크림 없는 짭짤한 페이스트리를 왜 먹지 않느냐고 물어요.",
    },
    1246: {
        "english": "A woman says, ‘No, my daughter, thank God we are full.’ She asks them to bring the pastries so she can eat them alone, says the others are not worthy of pastries, and tells them to take the ones referred to by the source surface ‘t7t’ downstairs or below and sell them; the direction remains source-close.",
        "korean": "한 여성이 ‘아니, 얘야, 하느님께 감사하게도 우리는 배불러’라고 말해요. 페이스트리를 가져오면 자신이 혼자 먹겠다고 하고, 일행은 페이스트리를 받을 자격이 없다고 농담해요. 이어 원문의 ‘t7t’가 가리키는 것들을 아래층이나 아래로 가져가 팔라고 하며 방향을 한 가지로 과도하게 확정하지 않아요.",
    },
    1247: {
        "english": "The speaker says that if they were not dieting, they would be hungry enough to dip bread with the others. They retain the opaque phrase ‘almut raha ghir arfd arfd’, the source surface ‘bz’, and the code-switched ‘les jeux’. They say it is good they were gathered at this table, that they do not want to gather with bz at a small table, and that the others drive them crazy by talking only about games.",
        "korean": "화자는 다이어트 중이 아니라면 일행과 빵을 찍어 먹을 만큼 배고프다고 해요. 불투명한 ‘almut raha ghir arfd arfd’, 원문의 ‘bz’, 코드스위칭 표현 ‘les jeux’를 보존해요. 이 식탁에 함께 모인 것은 다행이지만 작은 식탁에서 bz와 모이고 싶지는 않다고 하며, 일행이 게임 이야기만 해서 자신을 미치게 한다고 말해요.",
    },
    1252: {
        "english": "A woman says she had not intended to marry until finishing her studies, but marriage is written for her and she does not want to let it go. An older woman says that when she heard they were coming, he had dealt with everything, with the source-close surfaces ‘rdd yb9s’ and ‘7itan 7km’. The tables were taken to the speaker’s sister and treated with the source surface ‘rghwahum’; only ‘jhaz’, the equipment or household setup, had not been prepared.",
        "korean": "한 여성은 공부를 마칠 때까지 결혼할 생각이 없었지만 자신에게 정해진 결혼을 놓치고 싶지 않다고 해요. 나이 든 여성은 그들이 온다는 말을 듣고 그가 모든 일을 처리했으며 ‘rdd yb9s’, ‘7itan 7km’ 같은 원문 표면이 나온다고 말해요. 식탁은 화자의 누이에게 가져가 ‘rghwahum’이라는 표면의 처리를 했고, ‘jhaz’, 즉 살림살이나 준비물만 아직 마련되지 않았다고 해요.",
    },
    1253: {
        "english": "A woman says her daughter told her that the prospective groom is ‘saji’, keeping the source surface, and blesses him. She asks where their ‘tawws’ is and says to bring him so they can see him; the exchange then teases the aunt about talk and spinning.",
        "korean": "한 여성은 딸에게서 예비 신랑이 ‘saji’라는 말을 들었다며 원문 표면을 보존하고 그를 축복해요. 자신들의 ‘tawws’가 어디 있는지 묻고 그를 데려와 우리가 보자고 하며, 이어 이모의 말과 실 잣기에 관한 농담이 나와요.",
    },
    1255: {
        "english": "The speaker says there is only a little, says they have been seen and tells the woman to go to her room. They say she has made a pleasant sitting or gathering for herself, tell the listener to leave him alone and not bother him, and say that the poor man is gathered with them.",
        "korean": "화자는 얼마 남지 않았다고 말하고 사람들이 보았으니 여성에게 방으로 가라고 해요. 여성이 자기 자리를 즐겁게 만들어 놓았다고 하며, 상대에게 그 남자를 내버려 두고 방해하지 말라고 해요. 그 불쌍한 사람이 자신들과 함께 모여 있다고 말해요.",
    },
    1257: {
        "english": "The speaker says they came as if merely to put a hand on him, without inventing a shoulder greeting, and hopes that God will write a future for them and that they will begin working tomorrow. They will bring him a ring as a token, ask whether he is happy, and say that this is the speaker’s only one and that the listener will take him away, so they should care for him.",
        "korean": "화자는 그에게 손을 얹는 듯한 인사를 하러 왔다고 하며 어깨 인사를 덧붙이지 않아요. 하나님이 두 사람의 앞날을 정해 주고 내일부터 일을 시작하게 해 주기를 바란다고 해요. 약속의 표시로 반지를 가져오겠다고 하고 그가 기쁜지 묻으며, 자신에게는 이 아이 하나뿐이고 상대가 데려갈 것이니 잘 돌봐 달라고 해요.",
    },
    1259: {
        "english": "The speaker says the opposing player will pass to everyone, not only to his wife. They tell the others to follow because there are five in their team. They must score in this goal, but the speaker then says this is their own goal and they will score against themselves. The final exchange asks whether the listener is the speaker’s father or the speaker is the listener’s father.",
        "korean": "화자는 상대 선수가 아내에게만 패스하지 않고 모두에게 패스할 것이라고 해요. 자기 팀은 다섯 명이니 따라오라고 하고, 이 골에 넣어야 한다고 말한 뒤 자기 골대라서 자책골을 넣게 될 것이라고 농담해요. 마지막에는 상대가 자신의 아버지인지 자신이 상대의 아버지인지 묻는 장난이 이어져요.",
    },
    1260: {
        "english": "The speaker tells someone to come and teach them, says they know what they are saying, and predicts that when the others see the team score into its own goal—‘mrkina l l9wl ta3na’—they will say the players do not know how to play.",
        "korean": "화자는 누군가에게 와서 자신을 가르쳐 달라고 하며 자신이 무슨 말을 하는지 안다고 해요. 사람들이 자기 팀이 ‘mrkina l l9wl ta3na’, 즉 자기 골대에 넣는 것을 보면 경기할 줄 모른다고 말할 것이라고 해요.",
    },
    1262: {
        "english": "The speaker accuses the listener of wanting their team to lose and the listener’s sisters to win. They recall that the listener first and later told the speaker, ‘Come play a match with me.’",
        "korean": "화자는 상대가 자신들의 팀을 지게 하고 상대의 자매들이 이기게 하려 한다고 비난해요. 상대가 처음에도 나중에도 자신에게 ‘나와 경기하러 와’라고 말했다는 일을 떠올려요.",
    },
    1266: {
        "english": "One speaker asks whether the other will play goalkeeper in a djellaba. The answer says, ‘No, I will play in shorts; I want my husband to divorce me.’ Their father is then addressed about dividing socks among the players; the speaker says they will do it and become angry or make a mess. Another turn mentions a fruit-mixed yogurt, followed by ‘Run, you’ll see.’ Each turn and the deliberately provocative shorts condition are retained.",
        "korean": "한 화자는 상대가 젤라바를 입고 골키퍼를 할 것이냐고 물어요. 상대는 ‘아니, 반바지를 입고 경기할 거야. 남편이 나와 이혼하기를 바라’라고 답해요. 이어 아버지에게 경기 참가자들에게 양말을 나누라고 말하고, 자신은 그렇게 하며 화를 내거나 엉망으로 만들겠다고 해요. 과일이 섞인 요거트에 관한 turn과 ‘뛰어, 보면 알아’라는 말도 각각 보존해요.",
    },
    1269: {
        "english": "The speaker says the woman is at the psychiatric hospital, addresses the addressee as ‘Madam’, tells her to compose or gather herself, and asks her to explain why she is there. ‘Madam’ is not invented as the proper name Djemaa.",
        "korean": "화자는 여성이 정신병원에 있다고 말하고 상대를 ‘마담’이라고 부르며 진정하거나 정신을 가다듬고 왜 여기 있는지 설명하라고 해요. ‘마담’을 고유명사 즈므아로 창작하지 않아요.",
    },
    1270: {
        "english": "The speaker says they were walking peacefully when a female beggar approached and asked for money without greeting. They gave her ten thousand as charity, then saw her spit and turn on them, saying that she was asking them for ten thousand. The speaker says they flew at her by the hair, then jokes to the doctor that if she is ill, the speaker is even more ill.",
        "korean": "화자는 평화롭게 걷다가 한 여성 구걸꾼이 인사도 없이 돈을 요구해 만을 자선으로 주었다고 해요. 이어 그 여성이 침을 뱉고 자신에게 달려들 듯 돌아서서 만을 달라고 했다고 하며, 자신은 그 여성의 머리카락을 잡고 달려들었다고 말해요. 마지막에는 의사에게 여성이 아프다면 자신은 더 아프다고 농담해요.",
    },
    1271: {
        "english": "The speaker addresses the doctor and says that this is a face people would spit on, preserving the insult rather than reversing it into people paying to look. Two people who had gone ahead came back, took both of them upstairs, and the speaker went with the woman. The speaker insists they are not crazy, only lightly affected, and not a resident of the madhouse.",
        "korean": "화자는 의사에게 이 얼굴은 사람들이 침을 뱉을 얼굴이라고 말하며 모욕의 방향을 보존해요. 먼저 지나간 두 사람이 돌아와 자신과 그 여성을 함께 위로 데려갔고, 자신은 그 여성과 함께 갔다고 해요. 자신은 미친 것이 아니라 조금 영향을 받은 것뿐이며 정신병원 사람은 아니라고 주장해요.",
    },
    1272: {
        "english": "The speaker says that the woman the speaker spoke with is in full possession of her mental faculties. They then say they have reached the facility, reject the claim that she is crazy by calling someone a liar, ask the brother what he sees in the speaker, and threaten to do the same to him.",
        "korean": "화자는 자신이 이야기해 본 그 여성이 정신이 온전하다고 말해요. 이어 시설에 도착했다고 하고 여성이 미쳤다는 말을 거짓말이라고 반박해요. 형제에게 자신을 어떻게 보느냐고 묻고 그에게도 똑같이 하겠다고 위협해요.",
    },
    1274: {
        "english": "The speaker says ‘Astaghfirullah’ and jokes that people eat very well there. If they eat well, the speaker will stay there alone; they have not left home or gone to the sea that year. They ask why, during the break, they should be placed with a tribal madman who might slap them. The eating joke, beach remark, and slap threat are kept separate.",
        "korean": "화자는 ‘아스타그피룰라’라고 말하며 그곳에서는 사람들이 아주 잘 먹는다고 농담해요. 잘 먹여 준다면 그곳에 혼자 있겠다고 하며 올해 집 밖이나 바다에 나가지 못했다고 해요. 휴식 시간에 자신을 때릴 수 있는 부족 출신의 미친 사람과 함께 두는 이유가 무엇인지 묻고, 먹는 농담·해변 이야기·때릴 수 있다는 위협을 분리해 보존해요.",
    },
    1277: {
        "english": "The speaker comments on how the woman is talking with them and refers to her eyes being open. The line ends with the source surface ‘khatrsh’ (‘because’) and is incomplete; the speaker and gaze direction are not completed by invention.",
        "korean": "화자는 그 여성이 자신과 어떻게 이야기하는지에 대해 말하고 그녀의 눈이 떠 있는 것을 언급해요. 줄은 ‘khatrsh’(‘왜냐하면’)라는 표면에서 불완전하게 끝나므로 화자와 시선 방향을 임의로 완성하지 않아요.",
    },
    1279: {
        "english": "The speaker tells the others to look and listen, says they will remove their veil and gather a judge from Fez who cannot get them up, and tells the others to go to their own beach. They say not to ask them for the source-close ‘dra w msasik’ when they want to nap. They request the 2021 rai recording by Mamidou for the road and keep the named music surface.",
        "korean": "화자는 일행에게 보라고 하고 들으라고 하며, 머리 스카프를 벗고 자신을 일으킬 수 없는 페스의 판사를 모아 오겠다고 농담해요. 일행에게 자기들 해변으로 가라고 하고, 자신이 낮잠을 자려 할 때 원문의 불투명한 ‘dra w msasik’를 요구하지 말라고 해요. 길에서 즐기려고 마미두의 2021년 라이 음악을 틀어 달라고 하며 음악 표면을 보존해요.",
    },
    1280: {
        "english": "The speaker says they have reached the destination and asks for Mamidou to be played in the car. The speaker then addresses the listener as ‘baba’ or Dad and asks, ‘Where do you know Mamidou from?’ The vocative is not turned into a claim that Mamidou is the listener’s father.",
        "korean": "화자는 목적지에 도착했다고 하며 차에서 마미두의 음악을 틀어 달라고 해요. 이어 상대를 ‘baba’, 즉 아빠라고 부르며 ‘마미두를 어디서 알아?’라고 묻고, 마미두가 상대의 아버지라는 주장으로 바꾸지 않아요.",
    },
}


CODE_SWITCHING_ADD = {1217, 1218, 1221, 1222, 1230, 1231, 1232, 1234, 1237, 1240, 1243, 1244, 1245, 1247, 1255, 1258, 1259, 1260, 1262, 1265, 1266, 1273, 1276}
CEFR_BOUNDARY_ADD = {1217, 1219, 1220, 1222, 1224, 1226, 1227, 1229, 1231, 1237, 1238, 1239, 1241, 1242, 1246, 1247, 1252, 1253, 1254, 1257, 1259, 1260, 1262, 1263, 1265, 1266, 1267, 1269, 1272, 1276, 1279, 1280}
REMOVE_AMBIGUITY = {1223, 1224, 1225, 1232, 1239, 1241, 1243, 1245, 1246, 1251, 1256, 1260, 1261, 1262, 1263, 1265, 1267, 1268, 1269, 1273, 1275, 1276, 1280}
DRAFT_AFTER_REVIEW = {1225, 1245, 1256, 1260, 1262, 1269, 1273, 1275, 1280}


def add_metadata_corrections():
    current = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
    for sentno in sorted(CODE_SWITCHING_ADD | CEFR_BOUNDARY_ADD | REMOVE_AMBIGUITY):
        flags = set(filter(None, current[sentno]["processing_flags"].split("|")))
        if sentno in CODE_SWITCHING_ADD:
            flags.add("code_switching")
        if sentno in CEFR_BOUNDARY_ADD:
            flags.add("cefr_boundary")
        if sentno in REMOVE_AMBIGUITY:
            flags.discard("source_ambiguity")
        CORRECTIONS.setdefault(sentno, {})["processing_flags"] = "|".join(sorted(flags))
        if sentno in DRAFT_AFTER_REVIEW:
            CORRECTIONS[sentno]["enrichment_state"] = "draft"
    CORRECTIONS.setdefault(1277, {})["processing_flags"] = "code_switching|idiom_culture|source_corruption"


def apply():
    add_metadata_corrections()
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

    rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    counts = {
        "draft": sum(row["enrichment_state"] == "draft" for row in rows),
        "flagged": sum(row["enrichment_state"] == "flagged" for row in rows),
        "not_started": sum(row["enrichment_state"] == "not_started" for row in rows),
    }
    batch_counts = {
        "draft": sum(row["enrichment_state"] == "draft" for row in batch_rows),
        "flagged": sum(row["enrichment_state"] == "flagged" for row in batch_rows),
    }
    state_updates = sum("enrichment_state" in fields for fields in CORRECTIONS.values())
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    qa["correction_state_updates"] = state_updates
    qa["correction_history"][-1]["state_updates"] = state_updates
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = state_updates
    correction["batch_artifact_sync_state_updates"] = state_updates
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": state_updates, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
