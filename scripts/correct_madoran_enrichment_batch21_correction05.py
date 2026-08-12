"""Apply direct-utterance repairs from the latest HeadGPT P1_DETAILS for Batch 21."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch21 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "6d68727"
BATCH_ID = "MADORAN-ENRICH-021"
CORRECTION_ID = "MADORAN-ENRICH-021-CORRECTION-05"
PROMPT_VERSION = "madoran-source-enrichment-v21-correction-5"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction05_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch21_correction05_qa.json"
PROVENANCE_BEFORE = 18852

SEMANTIC = {
    1281: ("‘hwdwli barswl’ is kept source-close, but the utterance directly says: people eat restaurant food before they go to the sea; I clean potatoes and a little pepper; I found a watermelon; this is a life for which I seek God’s help and entrustment. The surface ‘7sbi allh w n3m alwkil fikm’ remains in the utterance.", "‘hwdwli barswl’은 원문에 가깝게 두되 발화는 직접 번역해요. 사람들은 바다에 가기 전에 식당 음식을 먹고, 나는 감자와 약간의 피망을 손질하고, 수박을 찾았으며, 이런 삶에 대해 신의 도움과 맡김을 구한다고 해요. ‘7sbi allh w n3m alwkil fikm’ 표면도 발화 안에 보존해요."),
    1282: ("The speaker says ‘rak 3a9d 3lia’—you are holding me back or tying me down—then says ‘I am going, going’; ‘ktlni 7man’ is kept as ‘the heat is killing me’ before ‘hit your head against the wall’.", "화자는 ‘rak 3a9d 3lia’(네가 나를 막고 있거나 옭아매고 있어)라고 하고 ‘나는 가, 가’라고 해요. ‘ktlni 7man’은 ‘더위가 나를 죽이겠어’로 보존한 뒤 ‘머리를 벽에 부딪혀’라고 해요."),
    1286: ("The speaker says directly, ‘Do not eat me, brother,’ and says that this husband is shouting at the speaker. The husband’s shouting direction is kept without inventing jealousy.", "화자는 직접 ‘나를 먹지 마, 형제야’라고 하고 이 남편이 화자에게 소리친다고 해요. 남편이 고함치는 방향을 보존하며 질투를 창작하지 않아요."),
    1291: ("The speaker says ‘I cannot hear your voices’, says they are hungry and asks for the opaque food surface ‘mbss’ in a bag, then says ‘you have been no good since the day I knew you’ and keeps the final sequence in which the speaker called and the addressee came running. The complaint and its cause are direct utterance content.", "화자는 ‘너희 목소리가 안 들려’라고 하고 배가 고프다며 봉지에 든 불투명한 음식 표면 ‘mbss’를 달라고 해요. 이어 ‘너를 안 날부터 너는 좋은 일을 한 적이 없어’라고 하고, 화자가 불러서 상대가 달려온 마지막 sequence도 직접 발화로 보존해요."),
    1292: ("The speaker directly insults the addressee in ‘nti brw7k 7rkia’, says ‘you killed him’, then ‘I went in a mess’, and ‘I was not the one who killed him’. The opaque surfaces ‘jra’ and ‘m9ndl’ remain unresolved, but the actor contrast is translated.", "화자는 ‘nti brw7k 7rkia’로 상대를 직접 모욕하고 ‘네가 그를 죽였어’, ‘나는 엉켜서 갔어’, ‘그를 죽인 건 내가 아니야’라고 해요. ‘jra’와 ‘m9ndl’은 불투명하게 두되 행위자 대비는 직접 번역해요."),
    1293: ("The speaker wants to enter alone but asks for company and a little entertainment. ‘awmwan’ is ‘at least’, and ‘7asbtni mtlw9a kifk wa9il’ keeps the direction ‘did you think I was a released/free woman like you?’ without forcing a single legal status.", "화자는 혼자 들어가고 싶지만 함께 있어 주고 조금 즐겁게 해 달라고 해요. ‘awmwan’은 ‘적어도’로, ‘7asbtni mtlw9a kifk wa9il’은 ‘나도 너처럼 풀려난/자유로운 여자라고 생각했어?’라는 방향으로 보존하되 법적 상태를 하나로 고정하지 않아요."),
    1295: ("The speaker asks, ‘Do you know where you are now?’; keeps the opaque name-like ‘mwjilali/mwljilali’; says whoever wants blood should come; says ‘I came well/right’ in ‘mzia jit’; and keeps the praise-like ‘awmbiws shaba rahi hna mn alsh3r’ source-close.", "화자는 ‘네가 지금 어디 있는지 알아?’라고 묻고 불투명한 이름 같은 ‘mwjilali/mwljilali’를 보존해요. 피를 원하는 사람은 오라고 하고 ‘mzia jit’은 ‘내가 오길 잘했어/잘 왔어’ 방향으로 번역하며 ‘awmbiws shaba rahi hna mn alsh3r’는 원문에 가깝게 둬요."),
    1298: ("The speaker says ‘I don’t know’; tells the listener to check with the service chief; says ‘I am drinking coffee’; then keeps the separate question ‘with whom?’ and answer ‘with your father’.", "화자는 ‘모르겠어’라고 하고 상대에게 서비스 책임자에게 확인하라고 해요. ‘나는 커피를 마시는 중이야’라고 한 뒤 별도의 ‘누구와?’와 ‘네 아버지와’라는 Q/A를 보존해요."),
    1299: ("The speaker says the listener has been sulky all year; says ‘Aymen’s mother is right’; and reports ‘your mother told me that you have not laughed ...’. The explicit ‘mk’/your-mother surface is retained and the reported relation is not merged with Aymen’s mother.", "화자는 상대가 1년 내내 시무룩하다고 하고 ‘아이만의 어머니가 맞아’라고 해요. 이어 ‘네 어머니가 네가 ... 웃지 않았다고 내게 말했어’라는 전언을 보존해요. 명시적인 ‘mk’/네 어머니 표면을 살리고 아이만의 어머니와 합치지 않아요."),
    1301: ("The speaker says ‘feel sorry for me’, ‘do not talk any more’, and ‘I will show her’. The object of ‘show her’ is left open; no event is invented.", "화자는 ‘나를 불쌍히 여겨’, ‘더 말하지 마’, ‘내가 그녀에게 보여 줄게’라고 해요. ‘보여 주다’의 내용은 열어 두고 어떤 사건도 발명하지 않아요."),
    1302: ("The speaker asks or tells the female addressee about dinner, keeps the greeting ‘good morning, my neighbour; how did you wake up?’, and says ‘make yourself dinner; come back tomorrow’. ‘wli ghdwa’ is not changed into ‘leave dinner for tomorrow’.", "화자는 여성 청자에게 저녁을 묻거나 요구하고 ‘좋은 아침, 이웃아. 잘 잤어?’라는 인사를 보존해요. ‘저녁을 만들어 먹고 내일 다시 와’라고 하며 ‘wli ghdwa’를 ‘내일 먹도록 남겨 둬’로 바꾸지 않아요."),
    1306: ("Keeping only the opaque title-like ‘almkrasha’, the speaker directly proposes: ‘Let us go this evening to Mustafa’s place and eat/break the fast’; the meal/iftar surface ‘nftrwa’ is not normalized as breakfast.", "불투명한 제목 같은 ‘almkrasha’만 원문에 가깝게 두고, 화자는 직접 ‘오늘 저녁 무스타파에게 가서 먹자/금식을 깨자’고 제안해요. 식사·이프타르 표면 ‘nftrwa’를 아침 식사로 특정하지 않아요."),
    1307: ("The speaker directly invokes protection—‘may God protect and shelter/keep us’—and asks ‘what is there to eat/swallow?’ in ‘sha tbl3’.", "화자는 ‘신이 보호하고 지켜 주시길’이라고 직접 축원하고 ‘뭘 먹어/삼켜?’라고 ‘sha tbl3’로 물어요."),
    1308: ("The speaker keeps the vocative ‘ia m3ad’, the repeated ‘tl9ni 7mbwk’, the line about what the speaker has to do, and the closing ‘ki dair ghiar’ as ‘how jealous he/she is’ or ‘the jealousy is something else’. The jealousy direction is not reduced to fear of being hit.", "화자는 호칭 ‘ia m3ad’, 반복되는 ‘tl9ni 7mbwk’, 화자가 무슨 상관이냐고 하는 절, 마지막 ‘ki dair ghiar’를 ‘질투가 참 심하네/얼마나 질투하는지’ 방향으로 보존해요. 이를 맞을까 두렵다는 말로 줄이지 않아요."),
    1309: ("The line keeps the direct insult ‘fm klb’, the warning not to twist or harm oneself in ‘hdri brki ma t3wji fi rw7k’, and the direct question ‘can I go to the restroom/sanitary place?’ in ‘lisanitr’.", "이 행은 직접 모욕 ‘fm klb’, ‘hdri brki ma t3wji fi rw7k’의 경고, ‘lisanitr’에 가도 되느냐는 화장실·위생 시설 질문을 직접 번역해요."),
    1312: ("The speaker directly calls it ‘that whore/bitch’ in the offensive surface ‘had shrmita’, says ‘we will not buy it, wear it, or deserve it’, says ‘we are not human’, and then wants to make a friend through a good-wish phrase. The abusive speech is not meta-described or softened.", "화자는 공격적인 ‘had shrmita’를 직접 욕설로 말하고 ‘우리는 사지도 입지도 그럴 자격도 없어’, ‘우리는 인간도 아니야’라고 해요. 이어 좋은 말로 친구를 만들고 싶다고 하며 욕설을 메타 설명으로 순화하지 않아요."),
    1313: ("‘tinisa’ is kept as a tennis/sneakers-like surface rather than a created woman. ‘saii si fini’ is ‘enough, it’s finished’; the final Ibiza surface and the other job phrase remain source-close where needed.", "‘tinisa’는 창작된 여성이 아니라 테니스화·운동화 같은 표면으로 보존해요. ‘saii si fini’는 ‘됐어, 끝났어’로 번역하고 마지막 이비자 표면과 다른 직업 표현은 필요한 만큼 원문에 가깝게 둬요."),
    1316: ("The speaker says ‘make/arrange a separate home for me’ in ‘diri dari w7di’, not ‘make your own home’, and says ‘I am telling you in front of her’ in ‘n9wlha lk 9damha’.", "화자는 ‘diri dari w7di’로 ‘내가 따로 살 집을 마련해 줘/내 집을 따로 해 줘’라고 하지 ‘네 집을 만들어’라고 하지 않아요. ‘n9wlha lk 9damha’는 ‘그녀 앞에서 너에게 말하는 거야’로 보존해요."),
    1317: ("The speaker teases with ‘fkrwna’ as a turtle, ‘kmartk’ as the face, ‘haila mraia’ as ‘what a mirror/that mirror’, says they will leave everyone and come photograph the listener, and asks ‘what shall I do with you?’ in ‘sha ndir bik’.", "화자는 ‘fkrwna’를 거북이라고 놀리고 ‘kmartk’를 얼굴·낯으로 말해요. ‘haila mraia’를 거울에 관한 놀림으로 두고, 모두를 두고 와서 상대를 찍겠다고 하며 ‘sha ndir bik’으로 ‘너를 어떻게 해야 하지?’라고 반문해요."),
    1318: ("The utterance directly asks why the sister is afraid, says ‘my brother’s wife’, and says ‘they put her in the group’ with plural ‘darwha’. The initial ‘3nddha’ relation is not omitted and the sole actor is not invented.", "발화는 누이가 왜 무서워하는지 직접 묻고 ‘내 형제의 아내’를 말하며 복수형 ‘darwha’로 ‘그들이 그녀를 그룹에 넣었다’고 해요. 초두 ‘3nddha’ 관계를 빠뜨리지 않고 유일한 행위자를 창작하지 않아요."),
    1320: ("The speaker says the other hammam scrubber gets five thousand from the speaker in ‘kiasa lkhra tkhls 3lia ghir khmslaf’, and keeps ‘ntrt9 fwta w ntir 3liha’ as the direct comic threat/action rather than a meta-summary.", "화자는 ‘kiasa lkhra tkhls 3lia ghir khmslaf’로 다른 목욕탕 때밀이가 자신에게 5천만 받는다고 직접 말해요. ‘ntrt9 fwta w ntir 3liha’도 메타 설명이 아니라 직접적인 코믹 위협·행동으로 보존해요."),
    1321: ("The speaker asks for five thousand, says ‘I will feed you the worms I pulled out’, and keeps ‘3r3wr’ unresolved if needed while translating ‘shlaghmh’ toward moustache. The known worm and moustache surfaces are not both hidden as generic body imagery.", "화자는 5천을 요구하고 ‘내가 꺼낸 벌레들을 너에게 먹일 거야’라고 해요. ‘3r3wr’는 필요하면 불확실하게 두되 ‘shlaghmh’는 콧수염 방향으로 번역해요. 아는 벌레·콧수염 표면을 모두 일반 신체 이미지로 숨기지 않아요."),
    1322: ("The speaker says ‘bring him inside’ with the masculine object, and says he will make all the women at the hammam run away in ‘ihrbli 9a3 nsa t3 al7mam’. The direction is a direct sentence, not a gender-switched summary.", "화자는 남성 목적어로 ‘그를 들여보내’라고 하고 ‘그가 목욕탕 여자들을 전부 도망가게 할 거야’라는 ‘ihrbli 9a3 nsa t3 al7mam’ 방향을 직접 번역해요. 성별을 바꾼 요약으로 만들지 않아요."),
    1323: ("The code-switch is kept as an air-hostess/‘bonjour’ greeting; ‘inwdwni drwk’ and ‘ki rak baghini nsb7’ are directly translated, and the closing says that if France will not feed them, they should stay in their own country. These are direct turns, not merely preserved surfaces.", "code-switch는 항공 승무원·‘bonjour’ 인사로 보존하고 ‘inwdwni drwk’와 ‘ki rak baghini nsb7’를 직접 번역해요. 마지막은 프랑스가 그들을 먹여 살리지 않으면 자기 나라에 남으라는 뜻으로 직접 보존해요. 단순히 표면을 보존한다는 메타 설명으로 대체하지 않아요."),
    1324: ("‘lakwb kari’ is an angular or square haircut, a la coupe carrée surface; ‘swnzari’ is ‘continuously/without stopping’ toward sans arrêt. Neither known direction is left wholly opaque.", "‘lakwb kari’는 la coupe carrée 계열의 각진·사각 헤어컷이고 ‘swnzari’는 sans arrêt, 즉 계속·쉼 없이의 방향이에요. 알려진 방향을 모두 불투명하게 두지 않아요."),
    1325: ("‘3lmi 3lmk’ is ‘I know as much as you/I don’t know either’; ‘7ta bilwt w rah mtlms’ says even the pilot is lost/confused; ‘bl3wa biban’ directly says close the doors. Only ‘twswst’ and ‘win t7si’ remain source-close if uncertain.", "‘3lmi 3lmk’는 ‘나도 너만큼 알아/나도 몰라’이고, ‘7ta bilwt w rah mtlms’는 조종사조차 헤매고 있다는 뜻이에요. ‘bl3wa biban’은 문을 닫으라고 직접 번역해요. 불확실한 ‘twswst’와 ‘win t7si’만 원문에 가깝게 남겨요."),
    1328: ("The speaker addresses ‘ia 3mri’, asks rhetorically whether they cannot bring Ziani to play even one match, and ends ‘tw7shth’—‘I miss him/he is missed’. The address and missing statement are direct content.", "화자는 ‘ia 3mri’라고 부르고 지아니를 한 경기라도 뛰게 데려올 수 없느냐고 수사적으로 물은 뒤 ‘tw7shth’—‘그가 그리워’—로 끝내요. 호칭과 그리움을 직접 번역해요."),
    1330: ("The speaker says the woman is coming to apply kohl, exclaims ‘wow, how handsome he became—I won’t say more’ in ‘ki shab wa7d kifah w mnzidsh’, keeps the tattoo, and says ‘tb3h’—follow him.", "화자는 아이라인을 하러 오는 여성을 말하고 ‘와, 얼마나 멋져졌는지—더 말 안 할게’라는 ‘ki shab wa7d kifah w mnzidsh’ 감탄을 해요. 문신을 말하고 ‘tb3h’로 그를 따라가라고 해요."),
    1331: ("The speaker keeps the direct insult: ‘if only your words had some use, you donkey’ in ‘kwn ghir hdrtk fiha faida 7mara’, together with the opening and named/opaque ‘iwnja7’. ‘7mara’ is translated as the insult, not as metadata.", "화자는 ‘네 말에 쓸모라도 있었으면 좋겠네, 이 당나귀야’라는 ‘kwn ghir hdrtk fiha faida 7mara’ 직접 욕설을 보존해요. ‘iwnja7’ 표면과 초두도 유지하고 ‘7mara’를 메타데이터로 처리하지 않아요."),
    1332: ("The speaker says the others make money while the listeners argue about them, tells the woman to get up and clean potatoes, and says she is gathered with the guys/men in ‘9a3dtli mjm3a li m3 traris’. ‘traris’ is translated toward guys, not erased as an opaque group.", "화자는 다른 사람들이 돈을 버는데 일행은 그들 때문에 다툰다고 말하고, 여성에게 일어나 감자를 손질하라고 해요. ‘9a3dtli mjm3a li m3 traris’는 그녀가 남자들·녀석들과 모여 있다는 직접적인 비난으로, ‘traris’를 막연한 그룹으로 지우지 않아요."),
    1333: ("‘ma n9ar3sh’ is ‘I do not wait’, not ‘I do not argue’. The late-night clause asks whether the speaker is meant to hear people say where the mother and daughter had been wandering in the middle of the night; that accusation is translated directly.", "‘ma n9ar3sh’는 ‘나는 기다리지 않아’이지 ‘다투지 않아’가 아니에요. 밤중 절은 엄마와 딸이 한밤중에 어디를 돌아다녔는지 사람들이 말하는 것을 자신이 듣게 하려는 것이냐는 비난으로 직접 번역해요."),
    1335: ("The addressee is the woman who wants to go and expose herself at the university in ‘baghi trw7i t3ri li fi aljam3a’; no speaker or third woman is invented as the exposed object.", "‘baghi trw7i t3ri li fi aljam3a’의 방향은 여성 청자가 대학에서 자기 자신을 드러내려 한다는 것이에요. 화자나 제3의 여성을 노출 대상이라고 창작하지 않아요."),
    1336: ("The amounts are distinct: fifty thousand for the item, two hundred thousand without exchange at the neighbour’s, and fifty thousand in the later plea. The final ‘la mama 3ndi bl3i fmk’ is the speaker saying ‘No, mother, I have money; shut your mouth’, not the mother answering.", "금액은 서로 달라요. 물건은 5만, 이웃의 것은 교환 없이 20만, 뒤의 부탁에는 5만이 나와요. 마지막 ‘la mama 3ndi bl3i fmk’는 화자가 ‘아니 엄마, 나 돈 있어. 입 다물어’라고 하는 turn이지 엄마의 대답이 아니에요."),
    1339: ("‘aia khfwa’ directly means hurry/come quickly; ‘sha rakm dirwa mn sba7’ is a reproach about what they have done since morning; the final ‘lbsi khmar stri rw7k ... 9dam rjal’ directly tells the woman to wear a khimar and cover herself before men. Only ‘shashra rahm i9ar3wa’ remains opaque.", "‘aia khfwa’는 어서·빨리 오라는 말이고, ‘sha rakm dirwa mn sba7’은 아침부터 무엇을 했느냐는 질책이에요. 마지막 ‘lbsi khmar stri rw7k ... 9dam rjal’은 남자들 앞에서 키마르를 쓰고 몸을 가리라는 직접 지시예요. ‘shashra rahm i9ar3wa’만 불투명하게 남겨요."),
    1340: ("‘rahi iz9i 3lia’ says she is shouting at me; ‘takl fi rw7k’ directly tells the addressee not to eat himself; ‘dkhl 7rira a bl3’ says bring in the harira and eat. Only ‘shir amn’ remains source-close.", "‘rahi iz9i 3lia’는 그녀가 나에게 소리치거나 고함친다는 뜻이고, ‘takl fi rw7k’는 자신을 먹지 말라는 직접 말이에요. ‘dkhl 7rira a bl3’는 하리라를 들여와 먹으라는 말이에요. ‘shir amn’만 원문에 가깝게 둬요."),
    1341: ("‘bit alma’ is the bathroom/toilet; ‘bash nstja’ is for post-toilet cleansing/istinja. The reply directly says only a little came out—‘here, water…’—before ‘s7a wldi’.", "‘bit alma’는 화장실이고 ‘bash nstja’는 용변 후 세정·이스틴자를 위한 말이에요. 응답은 ‘조금밖에 안 나왔어, 여기 물…’이라고 직접 말한 뒤 ‘s7a wldi’로 끝나요."),
    1344: ("The father is the singular pickup actor in ‘baba ja idik’; ‘hwd 9lh iwli mnb3d’ keeps ‘go down and tell him to come back later’; ‘had win 7lat aljma3a’ says the gathering has just become lively; and ‘raki tm3nili bash nrw7 z3ma’ asks, ‘are you hinting that I should go?’.", "‘baba ja idik’에서는 아버지가 단수로 데리러 오는 행위자예요. ‘hwd 9lh iwli mnb3d’는 내려가서 나중에 다시 오라고 하라는 방향이고, ‘had win 7lat aljma3a’는 이제 막 모임이 재미있어졌다는 말이에요. ‘raki tm3nili bash nrw7 z3ma’는 ‘내가 가라고 눈치 주는 거야?’라는 질문이에요."),
}

_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
CORRECTIONS = {}
for sentno, (english, korean) in SEMANTIC.items():
    surface = _batch_rows[sentno]["latin"]
    CORRECTIONS[sentno] = {
        "english": f"{english} Canonical surface: `{surface}`.",
        "korean": f"{korean} canonical 표면: `{surface}`.",
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
    rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    counts = {"draft": sum(r["enrichment_state"] == "draft" for r in rows), "flagged": sum(r["enrichment_state"] == "flagged" for r in rows), "not_started": sum(r["enrichment_state"] == "not_started" for r in rows)}
    batch_counts = {"draft": sum(r["enrichment_state"] == "draft" for r in batch_rows), "flagged": sum(r["enrichment_state"] == "flagged" for r in batch_rows)}
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    if qa.get("correction_history"):
        qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 0
    correction["correction_state_updates"] = 0
    correction["batch_artifact_sync_state_updates"] = 0
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 0, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
