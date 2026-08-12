"""Complete all canonical segments in the Batch 21 P1 rows."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch21 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "3e9ffc7"
BATCH_ID = "MADORAN-ENRICH-021"
CORRECTION_ID = "MADORAN-ENRICH-021-CORRECTION-06"
PROMPT_VERSION = "madoran-source-enrichment-v21-correction-6"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction06_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch21_correction06_qa.json"
PROVENANCE_BEFORE = 18926

DIRECT = {
1281: ("The speaker keeps the opaque address ‘hwdwli barswl’; says people eat at a restaurant before going to the sea; says ‘I clean potatoes’ and ‘a little pepper’; says ‘I found a watermelon’; and concludes ‘this is a life—God is sufficient for me and the best disposer of affairs for you’.", "화자는 불투명한 호칭 ‘hwdwli barswl’을 보존하고, 사람들이 바다에 가기 전에 식당에서 먹는다고 해요. 이어 ‘나는 감자를 손질해’, ‘약간의 피망’, ‘수박을 찾았어’라고 하고 ‘이런 삶이라니, 신은 나에게 충분하고 당신들을 맡길 가장 좋은 분이야’라고 마무리해요."),
1282: ("The speaker asks how they could not go to the sea, says ‘you are holding me back’, says ‘I am going, going’, says ‘the heat is killing me’, and tells the addressee to hit their head against the wall.", "화자는 바다에 어떻게 안 가느냐고 묻고 ‘네가 나를 막고 있어’라고 해요. ‘나는 가, 가’, ‘더위가 나를 죽이겠어’라고 한 뒤 상대에게 머리를 벽에 부딪히라고 해요."),
1286: ("The speaker says ‘do not eat me, brother’, then says ‘this husband of mine is shouting at me’. The shouting direction is retained without adding jealousy.", "화자는 ‘나를 먹지 마, 형제야’라고 한 뒤 ‘내 남편이 나에게 소리치고 있어’라고 해요. 질투를 추가하지 않고 고함치는 방향을 보존해요."),
1291: ("The speaker says ‘I cannot hear your voices’; says ‘I am hungry’; asks for the opaque food ‘mbss’ in a bag; says ‘what a disgrace because of you’; says ‘since the day I knew you I have seen no good’; addresses the opaque name-like ‘D7s’; says ‘I pulled Bousbaa for you and told you to measure it with me in the river’; says the addressee was alone and had only come for a reason kept opaque; and says ‘I called you and you came running’.", "화자는 ‘너희 목소리가 안 들려’, ‘배고파’라고 하고 봉지에 든 불투명한 음식 ‘mbss’를 달라고 해요. ‘너 때문에 정말 엉망이야’, ‘너를 안 날부터 좋은 일을 본 적이 없어’라고 하고 불투명한 이름 같은 ‘D7s’를 부른 뒤 ‘Bousbaa를 데려와 강에서 나와 함께 재라고 했어’라고 해요. 상대가 혼자 어떤 이유로 있었던 부분은 열어 두고 ‘내가 불렀더니 네가 달려왔어’라고 마무리해요."),
1292: ("The speaker repeats ‘shut your mouth’; directly insults the addressee as ‘you, by yourself, moving/acting’; says ‘if you had not sent me to the opaque place “jij”, I would not be here’; says ‘you killed him’; ‘I went in a mess’; ‘I was not the one who killed him’; and ‘I only helped you measure him in the river’, leaving ‘jra’ and ‘m9ndl’ source-close.", "화자는 ‘입을 다물어’라고 반복하고 상대를 ‘너 혼자서 움직이는 사람’이라고 직접 모욕해요. ‘네가 나를 불투명한 장소 “jij”로 보내지 않았다면 나는 여기 없었어’, ‘네가 그를 죽였어’, ‘나는 엉켜서 갔어’, ‘그를 죽인 건 내가 아니야’, ‘나는 네가 강에서 그를 재는 것만 도왔어’라고 하며 ‘jra’와 ‘m9ndl’은 원문에 가깝게 둬요."),
1293: ("The speaker wants to enter alone, asks the addressee to accompany and entertain them a little, says ‘at least’, asks whether the addressee thought the speaker was a released/free woman like them, and says that prison or the brother may kill the speaker when he gets out.", "화자는 혼자 들어가고 싶지만 상대에게 동행해 조금 즐겁게 해 달라고 해요. ‘적어도’라고 하고 상대가 자신을 상대처럼 풀려난·자유로운 여자로 생각했느냐고 묻고, 감옥이나 형제가 출소할 때 자신을 죽일 수 있다고 말해요."),
1295: ("The speaker asks ‘do you know where you are now?’; tells the opaque name-like person to fly away; calls the person again; says whoever wants blood should come; says ‘I came well/right’; and keeps the final praise-like expression about beauty and hair source-close.", "화자는 ‘네가 지금 어디 있는지 알아?’라고 묻고 불투명한 이름 같은 상대에게 날아가라고 해요. 다시 부르고 ‘피를 원하는 사람은 오라’고 하며 ‘내가 잘 왔어/오길 잘했어’라고 하고 마지막 아름다움과 머리카락을 칭찬하는 듯한 표현은 원문에 가깝게 둬요."),
1298: ("The speaker asks mother about going with Aymen to the stadium; says ‘I don’t know’; says ‘check with the service chief—I am drinking coffee’; asks ‘with whom?’; and answers ‘with your father’.", "화자는 엄마에게 아이만과 경기장에 가도 되는지 묻고 ‘모르겠어’라고 해요. ‘서비스 책임자에게 확인해, 나는 커피를 마시는 중이야’라고 하고 ‘누구와?’라고 묻자 ‘네 아버지와’라고 답해요."),
1299: ("The speaker says the listener has been sulky all year; says Aymen’s mother is right; and reports that the listener’s mother told the speaker that the listener had not laughed for the opaque time expression. The two mothers and the report are kept distinct.", "화자는 상대가 1년 내내 시무룩하다고 하고 아이만의 어머니가 맞다고 해요. 이어 상대의 어머니가 불투명한 기간 동안 상대가 웃지 않았다고 자신에게 말했다고 전해요. 두 어머니와 전언을 구분해요."),
1301: ("The speaker asks for sympathy, says ‘do not talk any more’, and says ‘I will show her’, leaving what will be shown unresolved.", "화자는 자신을 불쌍히 여겨 달라고 하고 ‘더 말하지 마’라고 한 뒤 ‘내가 그녀에게 보여 줄게’라고 해요. 무엇을 보여 주는지는 미확정으로 둬요."),
1302: ("The speaker asks or tells the female addressee about dinner; says the pressure cooker is not working; says ‘I will not do it’ and ‘I am on leave’; tells the listener to go to the neighbour with the greeting ‘good morning, neighbour, how did you wake up?’; says ‘make yourself dinner’; and says ‘come back tomorrow’.", "화자는 여성 청자에게 저녁을 묻거나 요구하고 압력솥이 작동하지 않는다고 해요. ‘나는 안 할 거야’, ‘휴가 중이야’라고 하고 이웃에게 가서 ‘좋은 아침, 이웃아. 잘 잤어?’라고 인사하라고 해요. ‘저녁을 만들어 먹고 내일 다시 와’라고 해요."),
1306: ("Keeping only the opaque title-like opening, the speaker proposes ‘let us go this evening to Mustafa’s place and eat/break the fast’; the meal surface is not narrowed to breakfast.", "불투명한 제목 같은 초두만 원문에 가깝게 두고 화자는 ‘오늘 저녁 무스타파에게 가서 먹자/금식을 깨자’고 제안해요. 식사 표면을 아침 식사로 좁히지 않아요."),
1307: ("The speaker says they are hungry, cannot concentrate, and have an empty stomach; invokes ‘may God protect and shelter us’; and asks ‘what is there to eat or swallow?’", "화자는 배가 고프고 집중할 수 없으며 배가 비었다고 해요. ‘신이 보호하고 지켜 주시길’이라고 축원하고 ‘뭘 먹어/삼켜?’라고 물어요."),
1308: ("The speaker says a woman has been arguing with her partner for a year; calls out ‘hey, release me, please’; says the partner spoke to the speaker and asks what that has to do with the speaker; says ‘you are going to hit/shout at me’ in the source-close threat; repeats ‘release me’; and ends by commenting on how intense the jealousy is.", "화자는 한 여성이 1년 동안 연인과 다투고 있다고 해요. ‘이봐, 제발 나를 놓아 줘’라고 부르고, 그 연인이 자신에게 말했다며 ‘그게 나와 무슨 상관이야?’라고 해요. 원문의 때리거나 소리치는 위협을 보존하고 ‘제발 나를 놓아 줘’를 반복한 뒤 질투가 얼마나 심한지 말하며 끝내요."),
1309: ("The speaker says someone studies only the first course and leaves; says ‘teacher’; directly insults them with ‘dog mouth’; warns ‘speak, perhaps do not twist yourself’; and asks ‘can I go to the restroom/sanitary place?’", "화자는 누군가가 첫 과정만 공부하고 나간다고 하고 ‘선생님’이라고 해요. ‘개 같은 입’이라는 직접 모욕을 하고 ‘말해, 네 몸을 꼬지 않도록 해’라고 경고한 뒤 ‘화장실에 가도 돼?’라고 물어요."),
1312: ("The speaker asks the price; says the item cost a million; says ‘I did not like it’; directly calls it ‘that whore/bitch’; says ‘we will not buy it, wear it, or deserve it’; says ‘we are not human’; and says they want to make a friend through a good-wish phrase.", "화자는 가격을 묻고 백만에 샀다고 하며 ‘마음에 들지 않았어’라고 해요. 물건을 직접 욕하고 ‘우리는 사지도 입지도 그럴 자격도 없어’, ‘우리는 인간도 아니야’라고 한 뒤 좋은 말로 친구를 만들고 싶다고 해요."),
1313: ("The speaker addresses father; keeps ‘tinisa’ as a tennis/sneakers-like surface; compares it with someone they used to go out with; asks ‘what?’; says ‘why are you eating yourself?’; says someone kept calling to return; says ‘enough, it’s finished, I do not work as the opaque job surface’; and ends with the Ibiza surface and ‘go up/leave’.", "화자는 아버지를 부르고 ‘tinisa’를 테니스화·운동화 같은 표면으로 두며 예전에 함께 다니던 사람과 비교해요. ‘뭐라고?’라고 묻고 ‘왜 너 자신을 갉아먹어?’라고 해요. 돌아오라고 계속 불렀던 일을 말하고 ‘됐어, 끝났어. 나는 그 불투명한 일은 안 해’라고 한 뒤 이비자 표면과 ‘올라가/나가’로 끝내요."),
1316: ("The speaker says the woman looks yellow/pale; says ‘I will not live with her’; says ‘make/arrange a separate home for me’; and says ‘I will tell you in front of her’. The addressee and the woman remain distinct.", "화자는 그 여성이 누렇거나 창백해 보인다고 하고 ‘나는 그녀와 살지 않을 거야’라고 해요. ‘내가 따로 살 집을 마련해 줘’라고 하고 ‘그녀 앞에서 너에게 말할 거야’라고 해 상대와 여성을 구분해요."),
1317: ("The speaker compares the friend with a hammam scrubber/attendant; asks why the sister is photographing the speaker; calls the addressee a turtle; says ‘look at your face’; says ‘what a mirror’; says they will leave everyone and come photograph the listener; and asks ‘what shall I do with you?’", "화자는 친구를 목욕탕 때밀이·관리인에 비유하고 누이가 왜 자신을 찍는지 물어요. 상대를 거북이라고 부르고 ‘네 얼굴을 봐’, ‘거울이네’라고 놀려요. 모두를 두고 와서 상대를 찍겠다고 한 뒤 ‘너를 어떻게 해야 하지?’라고 반문해요."),
1318: ("The speaker asks why the sister is afraid; says ‘my brother’s wife’; says ‘they put her in the group of divorced female teachers at the hammam’; and keeps the plural actor in ‘they put her’.", "화자는 누이가 왜 무서워하는지 묻고 ‘내 형제의 아내’를 말해요. ‘그들이 그녀를 목욕탕의 이혼한 여성 교사들 그룹에 넣었어’라고 하며 복수 행위자를 보존해요."),
1320: ("The speaker says the other hammam scrubber charges the speaker five thousand; says ‘they are going to make me burst and I will fly at her’ in the comic threat surface; and keeps the one-hour scratching and square-metre payment turns.", "화자는 다른 목욕탕 때밀이가 자신에게 5천을 받는다고 해요. ‘나를 터뜨리려 하니 내가 그녀에게 달려들 거야’라는 코믹한 위협 표면을 보존하고 한 시간 동안 긁어 주기와 제곱미터 금액 turn도 유지해요."),
1321: ("The speaker asks for five thousand; says ‘I will feed you the worms I pulled out’; repeats the address; says the addressee has brought in a small boy; and says the boy’s moustache/body surface is enough for a camel, keeping only the remaining ‘3r3wr’ opaque if needed.", "화자는 5천을 요구하고 ‘내가 꺼낸 벌레들을 너에게 먹일 거야’라고 해요. 상대를 다시 부르고 작은 소년을 데려왔다고 하며 그 소년의 콧수염·신체 표면이 낙대에게 충분하다고 코믹하게 말해요. 남은 ‘3r3wr’만 필요하면 불투명하게 둬요."),
1322: ("The speaker says ‘if he only knocks here, bring him inside’; says he will make all the women of the hammam run away; and keeps the masculine object and direct comic threat.", "화자는 ‘그가 여기서 노크만 하면 그를 안으로 들여보내’라고 하고 ‘그가 목욕탕 여자들을 전부 도망가게 할 거야’라고 해요. 남성 목적어와 직접적인 코믹 위협을 보존해요."),
1323: ("The speaker keeps the air-hostess/bonjour greeting; says ‘they will wake me now’; says people are going to France at five in the morning and someone will run away; asks how Zahra woke; says ‘how do you want me to greet you?’; recalls the barking dog; mentions date bunches; jokes about uprooting palms for the road; and says if France will not feed them they should stay in their own country.", "화자는 항공 승무원·bonjour 인사를 보존하고 ‘그들이 이제 나를 깨울 거야’라고 해요. 사람들이 새벽 5시에 프랑스로 가고 누군가는 도망갈 거라고 하며 자흐라가 어떻게 일어났는지 묻고 ‘내가 너에게 어떻게 인사하길 바라?’라고 해요. 짖는 개를 떠올리고 대추야자 송이와 도로의 야자나무를 말한 뒤 프랑스가 먹여 살리지 않으면 자기 나라에 남으라고 해요."),
1324: ("The speaker compares the woman’s appearance with gold and a crooked back; calls Karim; says it is six in the morning; tells Karim to come; keeps the square haircut surface; says the cup/beauty phrase; and says they think of the addressee continuously, with ‘swnzari’ translated toward without stopping.", "화자는 여성의 외모를 금과 굽은 등에 비유하고 카림을 부르며 오전 6시라고 해요. 카림에게 오라고 하고 사각 헤어컷 표면과 컵·미모 표현을 보존하며 ‘swnzari’를 쉼 없이·계속 상대를 생각한다는 방향으로 번역해요."),
1325: ("The speaker says they are in the sky; says they did not manage with the others; invokes protection; asks a question; says ‘what is it?’; says the plane will not fall; recalls a National Geographic report; says ‘I know as much as you/I do not know either’; says even the pilot is lost/confused; tells them to close the doors and leave; and says not to forget the shahada/profession of faith.", "화자는 하늘에 있다고 하고 일행과 잘 맞지 않았다고 해요. 보호를 축원하고 질문하며 ‘그게 뭐야?’라고 하고 비행기는 떨어지지 않는다고 해요. 내셔널 지오그래픽 리포트를 떠올리고 ‘나도 너만큼 알아/나도 몰라’라고 하며 조종사조차 헤맨다고 해요. 문을 닫고 나가라고 한 뒤 샤하다·신앙고백을 잊지 말라고 해요."),
1328: ("The speaker says the listener thinks they are in 2010; says Ziani is no longer there; asks rhetorically whether they cannot bring him to play even one match; addresses ‘my dear’; and ends ‘I miss him’.", "화자는 상대가 2010년에 있다고 생각한다고 하고 지아니는 더 이상 없다고 해요. 한 경기라도 뛰게 데려올 수 없느냐고 수사적으로 묻고 ‘내 사랑아’라고 부른 뒤 ‘그가 그리워’라고 끝내요."),
1330: ("The speaker describes the woman coming to apply kohl; exclaims ‘wow, how handsome he became—I will say no more’; says he has a tattoo; and says ‘follow him’.", "화자는 아이라인을 하러 오는 여성을 말하고 ‘와, 얼마나 멋져졌는지—더 말하지 않을게’라고 감탄해요. 그가 문신을 했다고 하고 ‘그를 따라가’라고 해요."),
1331: ("The speaker addresses the watcher; tells the named/opaque person to go; asks why they are treating the speaker that way; compares it with playing the Africa World Cup; says ‘shut your mouth, may God protect you’; and says ‘if only your words had some use, you donkey’.", "화자는 지켜보는 사람을 부르고 이름·불투명 표면의 상대에게 가라고 해요. 왜 자신에게 그렇게 하느냐고 묻고 아프리카 월드컵을 하는 것 같다고 비교해요. ‘입을 다물어, 신이 너를 보호하시길’이라고 한 뒤 ‘네 말에 쓸모라도 있었으면 좋겠네, 이 당나귀야’라고 직접 욕해요."),
1332: ("The speaker says the others make money while the listeners argue about them; tells the woman to get up and clean potatoes; and says she is sitting gathered with the guys/men. The accusation and the guys direction are direct.", "화자는 다른 사람들은 돈을 버는데 일행은 그들 때문에 다툰다고 해요. 여성에게 일어나 감자를 손질하라고 하고 그녀가 남자들·녀석들과 모여 앉아 있다고 말해요. 비난과 남자들 방향을 직접 번역해요."),
1333: ("The speaker says ‘the source of tenderness’ goes shopping with her daughter; says ‘a year for you to make her a bride’; says ‘I put on my shoes and leave—I do not wait’; says they will keep watch until dinner and return home; asks whether the speaker is meant to hear where the mother and daughter wandered at midnight; and asks mother which item to take.", "화자는 ‘다정함의 샘’이 딸과 쇼핑하러 간다고 해요. ‘네가 그녀를 신부로 만드는 데 1년이 걸려’라고 하고 ‘나는 신발을 신고 나가, 기다리지 않아’라고 해요. 저녁까지 지켜보다 집에 들어간다고 하며 엄마와 딸이 한밤중에 어디를 돌아다녔는지 듣게 하려는 거냐고 묻고 엄마에게 어느 물건을 가져갈지 물어요."),
1335: ("The speaker says ‘if I tell you to take this one, take it’; calls the listener hard-headed; says ‘look after yourself’; says ‘I like this one’; asks why the other modest one is not chosen; and says the female addressee wants to go to the university and expose herself. No third woman is added.", "화자는 ‘내가 이것을 가지라고 하면 가져’라고 하고 상대를 고집 세다고 부르며 ‘네 앞가림이나 해’라고 해요. ‘나는 이것이 마음에 들어’라고 하고 다른 단정한 것을 왜 고르지 않느냐고 묻고 여성 청자가 대학에서 자기 자신을 드러내러 간다고 말해요. 제3의 여성을 추가하지 않아요."),
1336: ("The speaker says praise be to God and thought the listener was angry; mother will take the item; asks its price; says fifty thousand; compares the neighbour’s two hundred thousand without exchange; asks the son to be kind because the woman has fifty thousand; and ends ‘No, mother, I have money—shut your mouth’ as the speaker’s turn.", "화자는 신을 찬양하며 상대가 화난 줄 알았다고 해요. 엄마가 물건을 가져갈 거라고 하고 가격을 묻고 5만이라고 해요. 이웃의 교환 없는 20만과 비교하고 여성에게 5만밖에 없으니 아들에게 잘해 달라고 한 뒤 화자가 ‘아니 엄마, 나 돈 있어. 입 다물어’라고 마무리해요."),
1339: ("The speaker says ‘come quickly’; asks what the others have done since morning, keeping ‘shashra rahm i9ar3wa’ opaque; asks for two plates of harira; and tells the woman to wear a khimar and cover herself before men.", "화자는 ‘어서 와’라고 하고 ‘shashra rahm i9ar3wa’는 불투명하게 둔 채 아침부터 무엇을 했는지 물어요. 하리라 두 접시를 가져오라고 하고 여성에게 키마르를 쓰고 남자들 앞에서 몸을 가리라고 해요."),
1340: ("The speaker keeps the opaque ‘shir amn’; says the woman is shouting at the speaker; calls the listener only the neighbour’s son; says ‘do not eat yourself’; and says ‘bring in the harira and eat’.", "화자는 불투명한 ‘shir amn’을 보존하고 여성이 자신에게 소리친다고 해요. 상대를 그저 이웃의 아들이라고 부르고 ‘자신을 먹지 마’라고 한 뒤 ‘하리라를 들여와 먹어’라고 해요."),
1341: ("The speaker asks where the bathroom/toilet is; says it is for istinja/post-toilet cleansing; the reply says only a little came out—‘here, water’; and the speaker ends ‘thanks, my son’.", "화자는 화장실이 어디인지 묻고 용변 후 세정·이스틴자를 위한 곳이라고 해요. 응답은 ‘조금밖에 안 나왔어, 여기 물’이라고 하고 화자는 ‘고마워, 아들아’라고 끝내요."),
1344: ("The father comes to pick the listener up; the source keeps the opaque instruction to go down and tell him to come back later; says the gathering has just become lively; says the husband will not object; asks ‘are you hinting that I should go?’; and asks for a bed because the speaker will stay overnight.", "아버지가 상대를 데리러 오고, 불투명한 ‘내려가서 나중에 다시 오라고 해’라는 지시를 보존해요. 모임이 이제 막 재미있어졌다고 하고 남편은 반대하지 않을 거라고 해요. ‘내가 가라고 눈치 주는 거야?’라고 묻고 하룻밤 묵을 테니 잠자리를 펴 달라고 해요."),
}

_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
CORRECTIONS = {}
for sentno, (english, korean) in DIRECT.items():
    surface = _batch_rows[sentno]["latin"]
    CORRECTIONS[sentno] = {"english": f"{english} Canonical surface sequence: `{surface}`.", "korean": f"{korean} canonical 표면 순서: `{surface}`."}
CORRECTIONS[1295]["topic"] = "source_close_blood_and_where_are_you_exchange"
CORRECTIONS[1301]["topic"] = "source_close_sympathy_and_showing_something"
CORRECTIONS[1326] = {
    "processing_flags": "context_heavy|idiom_culture|source_ambiguity",
    "enrichment_state": "flagged",
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
    rows = read_tsv(ENRICHMENT_OUT); batch_rows = read_tsv(BATCH_OUT)
    counts = {"draft": sum(r["enrichment_state"] == "draft" for r in rows), "flagged": sum(r["enrichment_state"] == "flagged" for r in rows), "not_started": sum(r["enrichment_state"] == "not_started" for r in rows)}
    batch_counts = {"draft": sum(r["enrichment_state"] == "draft" for r in batch_rows), "flagged": sum(r["enrichment_state"] == "flagged" for r in batch_rows)}
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8")); status["counts"]["enrichment_draft_rows"] = counts["draft"]; status["counts"]["enrichment_flagged_rows"] = counts["flagged"]; status["counts"]["enrichment_not_started_rows"] = counts["not_started"]; engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8")); qa["draft_rows"] = batch_counts["draft"]; qa["flagged_rows"] = batch_counts["flagged"]; BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8")); correction["state_updates"] = 1; correction["correction_state_updates"] = 1; correction["batch_artifact_sync_state_updates"] = 1; correction["draft_rows"] = batch_counts["draft"]; correction["flagged_rows"] = batch_counts["flagged"]; CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if qa.get("correction_history"):
        qa["correction_history"][-1]["state_updates"] = 1
    qa["correction_state_updates"] = 1
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 1, "batch_artifact_sync_state_updates": 1, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]}); return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
