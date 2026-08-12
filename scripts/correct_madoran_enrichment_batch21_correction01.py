"""Apply the first HeadGPT-directed source-close correction for MADOran Batch 21."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch21 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "72430f7"
BATCH_ID = "MADORAN-ENRICH-021"
CORRECTION_ID = "MADORAN-ENRICH-021-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v21-correction-1"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch21_correction01_qa.json"
PROVENANCE_BEFORE = 18580


# These summaries deliberately keep uncertain names, slang, and turn boundaries
# unresolved.  The full canonical transliteration is appended below to every
# corrected bilingual field so that no source surface is lost in the gloss.
SEMANTIC = {
    1281: (
        "The speaker keeps the opening address, says people are eating at a restaurant before going to the sea, says ‘I am cleaning potatoes and a little pepper’, then ‘I found a watermelon’, and closes by condemning this life. The opaque opening and religious closing are not normalized away.",
        "화자는 초두 호칭을 보존한 채 사람들이 식당에서 바다에 가기 전에 먹는다고 말하고, ‘나는 감자와 조금의 피망을 손질한다’, ‘수박을 찾았다’고 한 뒤 이런 삶을 한탄해요. 불투명한 초두와 종교적 마무리를 임의로 정규화하지 않아요.",
    ),
    1282: (
        "The speaker keeps the full sequence: asking how they could not go to the sea, saying ‘I am going, going’, retaining the opaque ‘ktlni 7man’, and telling the addressee to hit their head against the wall. The direction of ‘rak 3a9d 3lia’ is not invented.",
        "화자는 바다에 어떻게 가지 않을 수 있느냐고 묻고 ‘나는 가, 가’라고 한 뒤 불투명한 ‘ktlni 7man’을 보존하며 상대에게 머리를 벽에 부딪히라고 해요. ‘rak 3a9d 3lia’의 방향은 임의로 확정하지 않아요.",
    ),
    1286: (
        "The speaker says ‘do not eat me, brother’ and says ‘my husband’ is acting against the speaker in the opaque phrase ‘iz9i 3lia’. It is kept as comic or adversarial source content without choosing between anger, pressure, and jealousy.",
        "화자는 ‘나를 먹지 마, 형제야’라고 하고 ‘내 남편’이 불투명한 ‘iz9i 3lia’의 행동을 한다고 말해요. 화남·압박·질투 중 하나로 고정하지 않고 코믹하거나 대립적인 원문 내용으로 보존해요.",
    ),
    1291: (
        "The speaker tells the others to be quiet, says they are hungry, asks for the opaque food surface ‘mbss’ in a bag, complains with ‘tfwa mrhwja 3la jalk’, and recalls calling D7s, bringing Bousbaa, and asking that it be measured with the speaker in the river. The sequence ‘nti brw7k ... jiti tjri’ is retained rather than compressed.",
        "화자는 일행에게 조용히 하라고 하고 배가 고프다며 봉지에 담긴 불투명한 음식 표면 ‘mbss’를 달라고 해요. ‘tfwa mrhwja 3la jalk’라는 불평을 하고, D7s를 부르고 Bousbaa를 데려와 강에서 자신과 함께 재 달라고 했던 일, ‘nti brw7k ... jiti tjri’의 순서를 줄이지 않고 보존해요.",
    ),
    1292: (
        "The speaker repeats ‘shut your mouth’, says that without being sent to Jijel they would not be here, then separates ‘you killed him’, ‘I went in a mess’, and ‘I was not the one who killed him’ from the help of measuring him in the river. The opaque surfaces ‘7rkia’, ‘jra’, and ‘m9ndl’ remain marked as such.",
        "화자는 ‘입을 다물어’라고 반복하고 지젤로 보내지지 않았다면 여기 없었을 거라고 해요. 이어 ‘네가 그를 죽였다’, ‘나는 엉켜서 갔다’, ‘그를 죽인 것은 내가 아니다’를 강에서 그를 재도록 도운 일과 구분해요. ‘7rkia’, ‘jra’, ‘m9ndl’은 불투명한 표면으로 남겨요.",
    ),
    1293: (
        "The speaker wants to enter alone, asks for accompaniment and a little entertainment, then says the addressee has treated the speaker as released or unrestrained in the opaque phrase ‘7asbtni mtlw9a’. The speaker fears prison and the brother’s reaction when he gets out; the names and slang are not resolved.",
        "화자는 혼자 들어가고 싶지만 동행해 잠시 즐겁게 해 달라고 해요. 상대가 불투명한 ‘7asbtni mtlw9a’처럼 자신을 풀려난 사람으로 여긴다고 말하고, 감옥에서 죽거나 형제가 출소할 때 자신을 해칠까 두려워해요. 이름과 속어는 확정하지 않아요.",
    ),
    1295: (
        "The speaker asks whether the listener knows where she is, repeats the commands involving the opaque name-like surface ‘mwjilali’, says that whoever wants blood should come, and then praises the woman and the hair in ‘awmbiws shaba rahi hna mn alsh3r’. The named and slang surfaces remain visible.",
        "화자는 상대가 자신이 어디 있는지 아느냐고 묻고 불투명한 이름 같은 ‘mwjilali’를 포함한 명령을 반복해요. 피를 원하는 사람은 오라고 한 뒤 ‘awmbiws shaba rahi hna mn alsh3r’에서 여성과 머리카락을 칭찬해요. 이름과 속어 표면을 그대로 드러내요.",
    ),
    1298: (
        "The speaker addresses mother, asks about going with Aymen to the stadium, says ‘m3lblish’ and that they are drinking coffee with ‘shaf srfis’, then answers the separate question ‘with whom?’ with ‘with your father’. The turn sequence is preserved.",
        "화자는 엄마를 부르며 아이만과 경기장에 가는 일을 묻고, ‘m3lblish’라고 한 뒤 ‘shaf srfis’와 커피를 마신다고 해요. 별도의 ‘누구와?’라는 질문에는 ‘네 아버지와’라고 답해 turn 순서를 보존해요.",
    ),
    1299: (
        "The speaker says the listener has been ‘mshnfa’ all year, says Aymen’s mother had the right to say something, and retains the opaque time expression ‘mk mn 3am da9iws’ rather than replacing it with a fixed duration.",
        "화자는 상대가 1년 내내 ‘mshnfa’하다고 하고 아이만의 어머니가 어떤 말을 한 것이 맞았다고 해요. 불투명한 시간 표현 ‘mk mn 3am da9iws’를 특정 기간으로 바꾸지 않고 보존해요.",
    ),
    1301: (
        "The line keeps the plea or reproach ‘t7zn 3lia’, the prohibition ‘ma tzid thdr’, and the final promise or threat ‘nwrilha’. It does not add an object or claim that the speaker will show a particular event to a particular woman.",
        "이 행은 ‘t7zn 3lia’라는 호소나 책망, ‘ma tzid thdr’라는 금지, ‘nwrilha’라는 약속 또는 위협을 그대로 보존해요. 누구에게 무엇을 보여 주는지 원문에 없는 대상을 추가하지 않아요.",
    ),
    1302: (
        "The speaker keeps the whole dinner exchange: no dinner, the pressure cooker ‘kikwta’ not working, ‘khwia’ and ‘ma ndirsh’, being on leave, the address to neighbor Sabah, the question about how she woke up, and the instruction to make dinner and leave it for tomorrow. The final imperative is not collapsed.",
        "화자는 저녁을 하지 않았다는 말, 작동하지 않는 압력솥 ‘kikwta’, ‘khwia’와 ‘ma ndirsh’, 휴가라는 말, 이웃 사바를 부르는 부분, 아침에 어떻게 일어났는지 묻는 부분, 저녁을 만들어 내일로 남기라는 지시를 모두 보존해요. 마지막 명령을 줄이지 않아요.",
    ),
    1306: (
        "The utterance preserves the title-like or opaque opening ‘almkrasha’, the proposal to go in the evening to Mustafa’s place and ‘nftrwa’, and the correction that it is only eight. The source does not force a single interpretation of the meal timing.",
        "이 발화는 제목처럼 보이는 불투명한 초두 ‘almkrasha’, 저녁에 무스타파에게 가서 ‘nftrwa’하자는 제안, 아직 8시라는 정정을 보존해요. 식사 시간의 의미를 하나로 강제하지 않아요.",
    ),
    1307: (
        "The speaker says they are hungry, cannot concentrate, and have an empty stomach, keeps the blessing ‘allh i7fz w istr’, and asks what there is to swallow in ‘sha tbl3’. The blessing is not translated as an ordinary food instruction.",
        "화자는 배가 고프고 집중할 수 없으며 배가 비었다고 해요. ‘allh i7fz w istr’라는 축원을 보존하고 ‘sha tbl3’에서 무엇을 삼킬 것이 있는지 물어요. 축원을 평범한 음식 지시로 바꾸지 않아요.",
    ),
    1308: (
        "The line retains the woman’s year-long dispute with her partner, the repeated ‘tl9ni 7mbwk’, the statement that he spoke to the speaker, ‘sha dkhlni’, ‘3ndk ghadi tzr9ni’, and the closing ‘ki dair ghiar’. It does not decide whether the final harm is a hit, threat, or another action.",
        "이 행은 여성이 연인과 1년 동안 다투었다는 부분, 반복되는 ‘tl9ni 7mbwk’, 그가 화자에게 말했다는 부분, ‘sha dkhlni’, ‘3ndk ghadi tzr9ni’, 마지막 ‘ki dair ghiar’를 보존해요. 마지막 해악을 구타·위협·다른 행동 중 하나로 확정하지 않아요.",
    ),
    1309: (
        "The speaker keeps the first-course fragment, the separate ‘astad’, the insult or opaque phrase ‘fm klb’, the warning ‘brki ma t3wji fi rw7k’, and the question about going to ‘lisanitr’. The source does not turn the phrase into a definite anatomical insult.",
        "화자는 첫 과정만 공부하고 나가는 부분, 별도의 ‘astad’, 모욕 또는 불투명한 표현 ‘fm klb’, ‘brki ma t3wji fi rw7k’라는 경고, ‘lisanitr’에 가도 되는지 묻는 부분을 보존해요. 이를 특정 신체 모욕으로 확정하지 않아요.",
    ),
    1312: (
        "The speaker asks the price, retains ‘mliwn’, ‘ma 9ash7thash’, and the insult surface ‘shrmita’, then lists ‘ma nshrwsh, ma nlbswsh, ma nstahlwsh, ma shi bniadm 7na’ before saying ‘baghi ndir sa7b ghir bd3wa alkhir’. The abusive register is marked as offensive, while the comic exaggeration is not mistaken for a literal claim that anyone is non-human.",
        "화자는 가격을 묻고 ‘mliwn’, ‘ma 9ash7thash’, 모욕 표면 ‘shrmita’를 보존해요. 이어 ‘ma nshrwsh, ma nlbswsh, ma nstahlwsh, ma shi bniadm 7na’를 나열하고 ‘baghi ndir sa7b ghir bd3wa alkhir’라고 해요. 공격적 register는 offensive로 표시하되, 인간이 아니라는 말을 문자 그대로의 사실로 처리하지 않아요.",
    ),
    1313: (
        "The speaker addresses ‘baba’, keeps the comparison with ‘tinisa’ and the former companion, the question ‘shwala?’, the idiom ‘takl fi rw7k’, the repeated-calling sequence, ‘si fini ma nkhdmsh 9lit’, and the final ‘aibiza w tl3’. Opaque job and place surfaces are not replaced by fixed occupations or destinations.",
        "화자는 ‘baba’를 부르고 ‘tinisa’와 예전에 함께 다니던 사람의 비교, ‘shwala?’, ‘takl fi rw7k’라는 관용 표현, 반복해서 부른 장면, ‘si fini ma nkhdmsh 9lit’, 마지막 ‘aibiza w tl3’를 보존해요. 불투명한 직업·장소 표면을 확정된 직업이나 목적지로 바꾸지 않아요.",
    ),
    1316: (
        "The speaker keeps ‘dija hadi hi’, the appearance word ‘msfara’, the refusal ‘ma nsknsh m3aha hadi’, the decision to make a home alone, and ‘n9wlha lk 9damha’. The color or appearance term remains source-close rather than being treated as a medical fact.",
        "화자는 ‘dija hadi hi’, 외모 표현 ‘msfara’, ‘ma nsknsh m3aha hadi’라는 거절, 혼자 집을 만들겠다는 결정, ‘n9wlha lk 9damha’를 보존해요. 색이나 외모 표현을 의학적 사실로 바꾸지 않아요.",
    ),
    1317: (
        "The speaker keeps the comparison ‘kiasa t3 al7mam’, asks why the sister is photographing them, retains ‘fkrwna’, points to ‘kmartk’ and the mirror, says they will photograph the listener, and closes with ‘sha ndir bik 7mbwk’. The teasing targets and action directions remain open where the source is open.",
        "화자는 ‘kiasa t3 al7mam’이라는 비교, 누이가 왜 자신을 찍는지 묻는 부분, ‘fkrwna’, ‘kmartk’와 거울을 가리키는 부분, 상대를 찍겠다는 말, ‘sha ndir bik 7mbwk’라는 마무리를 보존해요. 원문이 열어 둔 놀림의 대상과 행위 방향을 닫지 않아요.",
    ),
    1318: (
        "The speaker asks why the sister is afraid and says the brother’s wife put her in a group of divorced female teachers connected with the bath. The social-media surface ‘group’ and the bath context are retained without adding a real-world platform or relationship not stated in the line.",
        "화자는 누이가 왜 무서워하는지 묻고 형제의 아내가 그녀를 목욕탕과 관련된 이혼한 여성 교사들의 그룹에 넣었다고 해요. 소셜미디어 표면 ‘group’과 목욕탕 맥락은 보존하되, 원문에 없는 플랫폼이나 관계를 추가하지 않아요.",
    ),
    1320: (
        "The speaker keeps the one-hour, scratching, and square-metre sequence, the second kiosk’s ‘khmslaf’, and the final threat or comic movement ‘ntir 3liha’. The source does not require the back, the amount, or the object of the movement to be normalized beyond its surface.",
        "화자는 한 시간, 긁어 주기, 제곱미터 단위로 이어지는 순서, 두 번째 시설의 ‘khmslaf’, 마지막 위협 또는 코믹한 움직임 ‘ntir 3liha’를 보존해요. 등·금액·움직임의 대상을 원문 이상으로 확정하지 않아요.",
    ),
    1321: (
        "The speaker asks for ‘khmslaf’, keeps the opaque ‘aldwd’ and ‘3r3wr shlaghmh’, and preserves the image that the small boy’s teeth could satisfy a camel. The body imagery is comic source content; the unknown nouns are not translated as definite worms or a fixed animal part.",
        "화자는 ‘khmslaf’를 요구하고 불투명한 ‘aldwd’와 ‘3r3wr shlaghmh’를 보존하며 작은 소년의 이빨이 낙타도 만족시킬 수 있다는 이미지를 유지해요. 신체 이미지는 코믹한 원문 내용으로 두고, 불명확한 명사를 확정된 벌레나 동물 신체 부위로 번역하지 않아요.",
    ),
    1322: (
        "The line keeps the conditional ‘ghir i9r3lk hna’, the instruction involving ‘ghtdi dkhlih’, and the opaque escape surface ‘ihrbli’ before the reference to the women of the bath. The speaker direction and object are not silently reversed.",
        "이 행은 ‘ghir i9r3lk hna’라는 조건, ‘ghtdi dkhlih’가 들어간 지시, 목욕탕 여성들을 언급하기 전 불투명한 탈출 표면 ‘ihrbli’를 보존해요. 화자의 지시 방향과 대상을 조용히 뒤집지 않아요.",
    ),
    1323: (
        "The speaker keeps the opaque greeting, ‘awtas dw lagh’, ‘bwnjwgh’, the five-o’clock departure for France, the question about Zahra, the barking dog, the date bunches, the palm trees by the road, and the final France/home contrast. The long sequence is not reduced to a generic travel joke.",
        "화자는 불투명한 인사, ‘awtas dw lagh’, ‘bwnjwgh’, 오전 5시 프랑스 출발, 자흐라의 안부, 짖는 개, 대추야자 송이, 도로의 야자나무, 마지막 프랑스와 고향의 대비를 모두 보존해요. 긴 순서를 일반적인 여행 농담으로 줄이지 않아요.",
    ),
    1324: (
        "The speaker keeps the gold and crooked-back comparison, calls Karim, says it is six in the morning, asks to take Karim, retains the window action ‘ndlih lk mn alta9a’, and preserves ‘alzin lakwb kari w nkhmm fik swnzari’. The named and opaque surfaces remain unresolved.",
        "화자는 금과 굽은 등에 관한 비교, 카림을 부르는 말, 오전 6시라는 시간, 카림을 데려오라는 말, 창문 행동 ‘ndlih lk mn alta9a’, ‘alzin lakwb kari w nkhmm fik swnzari’를 보존해요. 이름과 불투명한 표면은 확정하지 않아요.",
    ),
    1325: (
        "The speaker keeps the sky opening, the blessing, the request to ask a question, the plane, the National Geographic report, the opaque ‘twswst’ and ‘win t7si’, the confused pilot, the doors, leaving, and the certificate. It does not turn the comic sequence into a literal aviation report.",
        "화자는 하늘에서 시작하는 부분, 축원, 질문하겠다는 말, 비행기, 내셔널 지오그래픽 리포트, 불투명한 ‘twswst’와 ‘win t7si’, 혼란스러운 조종사, 문, 나가라는 말, 증명서를 모두 보존해요. 코믹한 순서를 실제 항공 보고서로 바꾸지 않아요.",
    ),
    1328: (
        "The speaker says the listener thinks they are in 2010, says Ziani is no longer there, says they cannot bring him to play even one match, and ends ‘tw7shth’. The temporal and football reference is preserved without adding a biography.",
        "화자는 상대가 2010년에 있다고 생각한다고 하고 지아니는 더 이상 없으며 한 경기라도 뛰게 데려올 수 없다고 말한 뒤 ‘tw7shth’로 끝내요. 시간과 축구 참조는 전기를 추가하지 않고 보존해요.",
    ),
    1330: (
        "The speaker keeps the woman coming to apply kohl, the opaque appearance exclamation ‘ki shab wa7d kifah w mnzidsh’, the tattoo surface ‘tatwwaj’, and the closing ‘tb3h’. It is not reduced to a generic beauty description.",
        "화자는 아이라인을 하러 오는 여성, 불투명한 외모 감탄 ‘ki shab wa7d kifah w mnzidsh’, 문신 표면 ‘tatwwaj’, 마지막 ‘tb3h’를 보존해요. 일반적인 미모 묘사로 줄이지 않아요.",
    ),
    1331: (
        "The speaker keeps the viewer or watcher opening, the named surface ‘iwnja7’, the question about being treated that way, the Africa World Cup comparison, the repeated command to shut the mouth, the blessing, and the insult ‘7mara’. The insult is marked as speech content, not as a factual label.",
        "화자는 시청하거나 지켜보는 사람으로 시작하는 부분, 이름처럼 보이는 ‘iwnja7’, 왜 그렇게 대하느냐는 질문, 아프리카 월드컵 비교, 입을 다물라는 반복 명령, 축원, ‘7mara’라는 모욕을 보존해요. 모욕은 사실적 분류가 아니라 발화 내용으로 표시해요.",
    ),
    1332: (
        "The speaker contrasts others making money with the listeners arguing, tells the woman to get up and clean potatoes, and keeps ‘mjm3a li m3 traris’ as an opaque group description. The final noun is not forced into ‘brats’ or another fixed social label.",
        "화자는 다른 사람들이 돈을 버는 것과 일행이 다투는 것을 대비하고, 여성에게 일어나 감자를 손질하라고 해요. 마지막의 ‘mjm3a li m3 traris’는 불투명한 집단 묘사로 보존하며 ‘장난꾸러기’ 같은 고정된 사회적 꼬리표로 바꾸지 않아요.",
    ),
    1333: (
        "The long exchange keeps ‘nb3 al7nan’, the daughter-shopping scene, the one-year bride phrase, putting on shoes and leaving, not arguing, watching until dinner, the late-night wandering remark, and the final choice between two items. The kinship and agency of each turn are not merged.",
        "긴 대화에서 ‘nb3 al7nan’, 딸과 쇼핑하는 장면, 1년이 걸린다는 신부 표현, 신발을 신고 나가겠다는 말, 다투지 않겠다는 말, 저녁까지 지켜보는 부분, 밤늦게 헤매는 말, 마지막 두 물건 중 선택을 모두 보존해요. 각 turn의 친족 관계와 행위자를 합치지 않아요.",
    ),
    1335: (
        "The speaker says ‘if I tell you to take this one, take it’, calls the listener hard-headed, says ‘I like this one’, asks why the other covered or modest one is not chosen, and keeps the university undressing accusation and the upbringing question. The clothing choice and accusation remain distinct turns.",
        "화자는 ‘내가 이것을 가지라고 하면 가져’라고 하고 상대를 고집 세다고 부르며 ‘나는 이것이 마음에 든다’고 해요. 다른 단정하거나 가려진 것을 왜 고르지 않느냐고 묻고 대학에서 벗기려 한다는 비난과 양육에 관한 질문을 보존해요. 옷 선택과 비난을 서로 다른 turn으로 유지해요.",
    ),
    1336: (
        "The speaker keeps the blessing, the thought that the listener was angry, the mother taking the item, the price question, fifty thousand, the neighbour’s two hundred thousand without exchange, the appeal to treat the woman kindly, the fifty-thousand amount, ‘ftzdam’, and the mother’s final ‘shut your mouth’. The price relations are not rearranged.",
        "화자는 축원, 상대가 화났다고 생각한 부분, 엄마가 물건을 가져가는 부분, 가격 질문, 5만, 교환 없는 이웃의 20만, 여성에게 잘해 달라는 부탁, 5만이라는 금액, ‘ftzdam’, 엄마의 마지막 ‘입을 다물어’를 보존해요. 가격 관계를 재배열하지 않아요.",
    ),
    1339: (
        "The speaker keeps the family-house and invitation phrase, the request for two plates of harira, the complaint about what the others have done since morning, ‘shashra’, the accusation that they are arguing, and the instruction to wear a khimar and cover oneself before men. The clothing instruction is not expanded beyond the source.",
        "화자는 집과 초대 모임에 관한 말, 하리라 두 접시를 가져오라는 요청, 아침부터 일행이 한 일을 묻는 불평, ‘shashra’, 그들이 다툰다는 말, 남자들 앞에서 키마르를 쓰고 몸을 가리라는 지시를 보존해요. 의복 지시는 원문 이상으로 확대하지 않아요.",
    ),
    1340: (
        "The speaker addresses a sister, keeps the opaque ‘shir amn’, says a woman is acting against the speaker, calls the listener the neighbour’s son, keeps ‘takl fi rw7k’, and tells him to bring in harira and eat. ‘iz9i 3lia’ is not forced into a single physical action.",
        "화자는 자매를 부르고 불투명한 ‘shir amn’을 보존하며 한 여성이 자신에게 어떤 행동을 한다고 말해요. 상대를 이웃의 아들이라고 부르고 ‘takl fi rw7k’를 유지한 뒤 하리라를 들여와 먹으라고 해요. ‘iz9i 3lia’를 특정 신체 행동 하나로 확정하지 않아요.",
    ),
    1341: (
        "The speaker addresses ‘wldi’, asks about ‘bit alma’, keeps the blessing, says there is something there and that water is available for ‘nstja’, receives the reply that only a little water came, and closes with ‘s7a wldi’. The room and washing reference are not over-specified.",
        "화자는 ‘wldi’를 부르고 ‘bit alma’에 대해 묻고 축원을 보존해요. 그곳에 무엇인가 있고 ‘nstja’를 위한 물이 있다고 말한 뒤 물이 조금만 나왔다는 답을 듣고 ‘s7a wldi’로 끝내요. 방과 씻는 행위를 원문 이상으로 특정하지 않아요.",
    ),
    1344: (
        "The family pickup exchange keeps mother and father, the offer to take the listener before the stadium, the opaque ‘hwd 9lh iwli mnb3d’, the call to come now because the group has opened, the husband reference, the question about being dragged along, and the final request for a bed and overnight stay. The speaker turns are not merged.",
        "가족이 데리러 오는 대화에서 엄마와 아빠, 경기장에 가기 전에 데려다주겠다는 제안, 불투명한 ‘hwd 9lh iwli mnb3d’, 일행이 열렸으니 지금 오라는 말, 남편에 관한 말, 끌고 가는 이유를 묻는 부분, 잠자리와 하룻밤 묵겠다는 마지막 요청을 보존해요. 화자 turn을 합치지 않아요.",
    ),
}


BOUNDARY_ROWS = {
    1282, 1286, 1287, 1288, 1291, 1292, 1293, 1294, 1298, 1299, 1300,
    1303, 1305, 1310, 1311, 1312, 1313, 1315, 1316, 1317, 1318, 1320,
    1323, 1325, 1327, 1328, 1329, 1332, 1333, 1336, 1337, 1338, 1339,
    1340, 1342, 1344,
}

# Remove the mechanical blanket ambiguity flag only where the final content is
# a short, directly reusable utterance. Keep unresolved/long/source-corrupt
# rows flagged, and explicitly record soft CEFR boundaries requested by review.
FLAG_OVERRIDES = {
    1283: "",
    1306: "source_ambiguity",
    1307: "idiom_culture",
    1314: "idiom_culture|long_source",
    1318: "code_switching|idiom_culture",
    1326: "idiom_culture",
    1327: "",
    1330: "idiom_culture",
}
STATE_OVERRIDES = {1283: "draft", 1327: "draft"}


def canonical_flags(value: str) -> str:
    return "|".join(sorted(set(filter(None, value.split("|")))))


_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
CORRECTIONS = {}
for sentno, (english, korean) in SEMANTIC.items():
    surface = _batch_rows[sentno]["latin"]
    CORRECTIONS[sentno] = {
        "english": f"{english} Full canonical source surface retained in transliteration: `{surface}`.",
        "korean": f"{korean} canonical 원문 표면 전체를 로마자 표기로 그대로 보존해요: `{surface}`.",
    }

for sentno, row in _batch_rows.items():
    flags = FLAG_OVERRIDES.get(sentno, row["processing_flags"])
    if sentno in BOUNDARY_ROWS:
        flags = canonical_flags(f"{flags}|cefr_boundary")
    else:
        flags = canonical_flags(flags)
    if flags != row["processing_flags"]:
        CORRECTIONS.setdefault(sentno, {})["processing_flags"] = flags
    if sentno in STATE_OVERRIDES and STATE_OVERRIDES[sentno] != row["enrichment_state"]:
        CORRECTIONS.setdefault(sentno, {})["enrichment_state"] = STATE_OVERRIDES[sentno]

CORRECTIONS[1312]["register"] = "offensive"


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
    if qa.get("correction_history"):
        qa["correction_history"][-1]["state_updates"] = state_updates
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = state_updates
    correction["correction_state_updates"] = state_updates
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
