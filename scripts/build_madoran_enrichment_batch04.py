"""Build source-only MADOran enrichment Batch 04 for Sentno 193..256."""

from __future__ import annotations

import csv
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.apply_madoran_enrichment_batch import CEFR_LEVELS, CONTROLLED_VALUES
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
    PROCESSING_FLAG_VALUES,
    ROOT,
    SOURCE_OUT,
    read_tsv,
    source_gate,
)
from scripts.validate_madoran_enrichment import check_layer_contract


BATCH_ID = "MADORAN-ENRICH-004"
BASE_COMMIT = "304a583"
PROMPT_VERSION = "madoran-source-enrichment-v4"
TARGET_START = 193
TARGET_END = 256
BATCH_DIR = ROOT / "data" / "master" / "enrichment" / "batches"
BATCH_OUT = BATCH_DIR / "batch04_sentno_0193_0256.tsv"
MANIFEST_OUT = BATCH_DIR / "batch04_manifest.json"
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch04_generation_qa.json"
BATCH_FIELDS = ["source_uid", "sentno", *EMPTY_FIELDS, "processing_flags", "enrichment_state"]


def item(
    latin: str,
    english: str,
    korean: str,
    cefr_level: str,
    difficulty_score: int,
    domain: str,
    topic: str,
    genre: str,
    speech_act: str,
    register: str,
    context_dependency: str,
    processing_flags: str = "",
    enrichment_state: str = "draft",
) -> dict[str, object]:
    return {
        "latin": latin,
        "english": english,
        "korean": korean,
        "cefr_level": cefr_level,
        "difficulty_score": difficulty_score,
        "domain": domain,
        "topic": topic,
        "genre": genre,
        "speech_act": speech_act,
        "register": register,
        "context_dependency": context_dependency,
        "processing_flags": processing_flags,
        "enrichment_state": enrichment_state,
    }


RAW_ITEMS = [
    item(
        "ah bab lek7el hadak ta3 villa ta3 2 etages. ah sa7a. li m9abla b posta sghira yak? l9ahwa ta7t. wah sayi.",
        "Yes, that black door, the one for the two-story villa. Right. The one opposite the small post office, correct? The cafe is below it. Yes, that's it.",
        "응, 저 검은 문, 2층짜리 빌라 문이야. 맞아. 작은 우체국 맞은편에 있는 곳이지? 카페는 그 아래에 있어. 응, 거기야.",
        "B1", 46, "housing", "giving_directions", "conversation", "information", "colloquial", "medium", "code_switching",
    ),
    item(
        "hadik ta3 weld 7aj 3ekrimi wah. hadak 7bibi rou7 f rou7 9ra m3aya w kber m3aya w l3ebna f re7ba ya 7asrah denya yah. bsa7 siyama 7mid khouya li y9ollek drahem kbar temmak wah li y9 chkara ta3 drahem.",
        "That one belongs to Hajj Akrimi's son, yes. That man is dear to me; he studied and grew up with me, and we played in the neighborhood—those were the days. But especially my brother Hamid, the one who tells you there is big money there, a sack of money; the final wording is unclear.",
        "저곳은 하지 아크리미의 아들 것이야. 그래. 그 사람은 나와 함께 공부하고 자라고 동네에서 놀았던 아주 가까운 친구야. 그때가 그립네. 그런데 특히 하미드 형제와 큰돈, 돈자루를 말하는 마지막 부분은 정확한 연결이 불분명해.",
        "C1", 74, "family_relationships", "childhood_friend_and_money", "conversation", "narration", "colloquial", "high", "context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "li y9 chkara! tesma rak baghini n9a3ed koura? la dar la douar haw gaya hakka.",
        "A sack, he says! So you want me to remain 'koura'? No house and no neighborhood; it is fine like this. The expression 'remain koura' is unclear in the source.",
        "돈자루라고! 그러니까 내가 계속 'koura'로 지내길 바라는 거야? 집도 동네도 없이, 이대로가 좋다는 말인데 'koura로 지내다'의 정확한 뜻은 불분명해.",
        "B2", 61, "finance", "money_and_settling_down", "conversation", "question", "slang", "high", "context_heavy|idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "ana 9lil ma toumert ah 7zim khouya 9lil ma cheft ghir tmara ana kent ntir te39el cheftni b 404 bachi m3emra left mdawerha f 7ouma w nta dakhelha ted7ek 3liya.",
        "The opening expression is unclear. Brother Hazim, I saw little besides hardship. I used to rush around; remember seeing me with a loaded Peugeot 404, circling it through the neighborhood while you were inside laughing at me.",
        "첫 표현은 뜻이 불분명해. 하지므 형제, 나는 고생 말고는 거의 본 게 없어. 예전에 분주히 돌아다녔지. 짐을 가득 실은 푸조 404를 타고 동네를 도는 나를 봤던 것 기억해? 너는 그 안에서 나를 보고 웃었잖아.",
        "C1", 76, "work", "past_hardship_and_transport", "conversation", "narration", "slang", "high", "context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "fawetha l dar snadi9 snadi9 ga3 la famille mobilisee ah 7ay 3liya ben 3ouda dour tlet ayam ba9ya l l3id fawetnaha noix de coco sachets sachets f plastique w khallesna drahem w drahem rahom 3andek. oui.",
        "I took it home in boxes, box after box; the whole family was mobilized. The middle wording is unclear. With three days left before Eid, we got through it with coconut in sachets and plastic, and we paid money; the money is with you. Yes.",
        "상자째 집으로 옮겼고 온 가족이 동원됐어. 중간 표현은 불분명해. 이드까지 사흘 남았을 때 코코넛을 봉지와 비닐에 담아 일을 치렀고 돈도 냈어. 그 돈은 네가 가지고 있어. 응.",
        "C1", 82, "shopping", "eid_goods_and_payment", "conversation", "narration", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "nzid n9ollek? n3tik talya amen wla boukli 7wajbek. dit 3liya sbadoun f chhar ramdan wla la? wah.",
        "Shall I tell you more? The next phrase about 'talya amen' or curling your eyebrows is unclear. Did you take 'sbadoun' from me during Ramadan or not? Yes.",
        "더 말해 줄까? 'talya amen'과 눈썹을 말아 준다는 부분은 뜻이 불분명해. 라마단 달에 내게서 'sbadoun'을 가져갔어, 안 가져갔어? 응.",
        "C1", 79, "daily_life", "unclear_recollection", "conversation", "question", "slang", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "7aja fort ah? 7aja tres bnina? surtout mdebel wla siniya khder fou9 nar w dmer ah khouya mermed b farina 7aja mami 7aja tfout wa7edha surtout en sauce tomate.",
        "Something strong, huh? Something very tasty? Especially 'mdebel,' or a green tray over the fire—cook it down, brother—coated in flour, something delicious that goes down by itself, especially in tomato sauce. Several food terms are uncertain.",
        "강한 맛의 음식인가? 아주 맛있는 것? 특히 'mdebel', 또는 불 위의 초록색 쟁반 같은 부분은 불분명해. 형제여, 푹 익히고 밀가루를 묻힌 아주 맛있는 음식으로, 특히 토마토소스에 있으면 저절로 넘어간다는 말이야.",
        "C1", 77, "food", "food_preparation_description", "conversation", "description", "mixed", "high", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "un si grigali.",
        "The source sounds like the French phrase 'un ... grille,' but the item being named is unclear.",
        "원문은 프랑스어 'un ... grillé'처럼 들리지만 무엇을 가리키는지는 불분명해.",
        "B2", 64, "food", "unclear_food_item", "conversation", "description", "mixed", "high", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "yak un si grigali? hadak dauphin. hadak flipper. sachets sachets. morceaux morceaux. dmer l bni 3emmek f plastique.",
        "Right, an unclear grilled item? That is 'dauphin'; that is 'Flipper.' Sachet by sachet, piece by piece. The final instruction involving your cousins and plastic is unclear.",
        "그 불분명한 구운 음식 말이지? 저건 'dauphin', 저건 'Flipper'라고 해. 봉지마다, 조각마다. 사촌들과 비닐을 언급하는 마지막 지시는 뜻이 불분명해.",
        "C1", 83, "food", "corrupted_food_description", "conversation", "description", "mixed", "high", "code_switching|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "hak ghachi koula 3liya w nbe3. w drahemou rahom 3andek nta oui. 7mid bien costume papillon allah allah w rwaye7 ghir septieme sens w huitieme sens w cortege ya khouya hadi mbel9a hadi behloula hadi 3gouna hadi wawa ki ye7drou klaxon ya khouya tchali.",
        "Here, let the people eat at my expense and I will sell; his money is with you, yes. Hamid is well dressed with a bow tie—wonderful—and there are fragrances, 'seventh sense,' 'eighth sense,' and a procession. Brother, the final string of descriptions and the line about horns are unclear.",
        "자, 사람들이 내 부담으로 먹게 하고 나는 팔겠어. 그의 돈은 네가 가지고 있어, 응. 하미드는 나비넥타이까지 잘 차려입었고 향수, '일곱 번째 감각', '여덟 번째 감각', 행렬이 이어져. 마지막 여러 묘사와 경적에 관한 부분은 뜻이 불분명해.",
        "C1", 87, "culture_tradition", "wedding_procession_description", "conversation", "description", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "mouraha jma3i m3emmer b nas yezhou daha daha b sif 3la yemmaha. bsa7 la li y9ollek chkara.",
        "After that came a group full of people celebrating; he took her, took her by force against her mother's will. But the final phrase about someone saying 'a sack' is unclear.",
        "그 뒤에는 즐기는 사람들로 가득한 무리가 왔고, 그는 어머니의 뜻을 거슬러 그녀를 억지로 데려갔어. 하지만 누군가 '자루'라고 말한다는 마지막 부분은 불분명해.",
        "B2", 66, "culture_tradition", "forced_wedding_procession", "conversation", "narration", "colloquial", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "ya wedi ya 7mid 3lah ma tchoufch mra 9lila 3la 7sabek? tkoun mra w nos ki tetzowej w nos ytir teb9a ghir mra kol sbe3 b sen3a.",
        "Come on, Hamid, why don't you look for a modest woman suited to your means? She may be a woman and a half; when you marry, half flies away and one woman remains—each finger with a craft.",
        "하미드야, 왜 네 형편에 맞는 소박한 여자를 찾아보지 않아? 한 사람 반만큼 대단한 여자라도 결혼하면 반은 날아가고 한 사람만 남지. 손가락마다 재주가 있다는 식의 말이야.",
        "B2", 58, "family_relationships", "marriage_advice", "conversation", "suggestion", "colloquial", "medium", "idiom_culture",
    ),
    item(
        "kol sba7 dirlek baghrir b 9ahwa w 3chiya tedlek matlou3 w sb7iya darba founara 3mech hak sabe7 f wejha hakka nta t9oul wow ghadi takelni m3a sba7.",
        "Every morning she makes you baghrir with coffee, and in the evening she gives you matlou. In the morning, a partly unclear description of her appearance follows, and you say, 'Wow, she is going to eat me first thing in the morning.'",
        "매일 아침 커피와 바그리르를 해 주고 저녁에는 마틀루를 내줘. 이어지는 아침의 외모 묘사는 일부 불분명하고, 너는 '와, 아침부터 나를 잡아먹겠네'라고 말해.",
        "C1", 73, "humor", "comic_marriage_portrait", "conversation", "description", "slang", "high", "context_heavy|idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "la la manich baghi hakda. rani baghi zin w 3win. oui w 7aya wa9fa w choufou dans le fond [corrupted segment]. 7aya fort. baghi re9ba ki ternich safya w wej mriya la9i la9i ha rbi la9i nar achwa9i f bent 3ekrimi. ah matlou3a.",
        "No, no, I do not want that. I want beauty and lovely eyes. Yes, and a fine figure standing there; a following code-switched segment is corrupted. A strong presence. I want a clear, graceful neck and a face like a mirror. Bring me together, Lord, with the fire of my longing for Akrimi's daughter. Yes, she is tall or well-risen; that last word is context-dependent.",
        "아니, 아니, 그런 건 원하지 않아. 나는 아름다움과 예쁜 눈을 원해. 서 있는 멋진 몸매를 말한 뒤 코드 전환 구절 일부가 손상돼 있어. 우아하고 깨끗한 목선과 거울 같은 얼굴을 원해. 주님, 아크리미의 딸을 향한 내 그리움의 불꽃과 나를 만나게 해 주세요. 마지막 'matlou3a'의 뜻은 문맥에 따라 불분명해.",
        "C1", 91, "family_relationships", "idealized_woman_description", "conversation", "wish", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "ah matlou3a ma3lich li fat 3la kelma fat 3la rou7. 3labali belli ra7 mdemmer.",
        "Yes, 'matlou3a.' Never mind: whoever goes back on a word gives up the self. I know that he will be ruined. The first term remains context-dependent.",
        "그래, 'matlou3a'야. 괜찮아. 한 말을 저버리는 사람은 자신까지 저버린다는 말이야. 그가 망가질 거라는 건 알아. 첫 단어의 뜻은 여전히 문맥에 따라 불분명해.",
        "B2", 63, "daily_life", "keeping_one_word", "conversation", "opinion", "colloquial", "high", "context_heavy|idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "ma rani la mdemmer la nzammer, drahemi drouk ndihom ga3 ma tdoukhenich.",
        "I am neither ruined nor 'nzammer'; that word is unclear. I am taking all my money now, so do not make my head spin.",
        "나는 망한 것도 아니고 'nzammer'인 것도 아니야. 그 단어의 뜻은 불분명해. 이제 내 돈을 전부 가져갈 테니 나를 혼란스럽게 하지 마.",
        "B2", 59, "finance", "demanding_money_back", "conversation", "warning", "slang", "high", "source_ambiguity", "flagged",
    ),
    item(
        "ah sma3 7mid tekchef fiya 9oddam ghachi sba7 allah. ma t9oli la nkechfek la walou. nhabbelk wallah ma raha farya drouk b ras ma 3ziza ma raha farya ga3 7a9 rasoul allah.",
        "Listen, Hamid, you are exposing or embarrassing me in front of people early in the morning. Do not tell me that I will expose you or anything. I will drive you mad. The remaining claims about Aziza and 'farya' are unclear in the source.",
        "들어 봐, 하미드. 아침부터 사람들 앞에서 나를 폭로하거나 망신 주고 있잖아. 내가 너를 폭로하겠다는 식으로 말하지 마. 너를 미치게 할 거야. 이어지는 아지자와 'farya'에 관한 주장은 원문만으로 뜻이 불분명해.",
        "C1", 80, "finance", "public_money_dispute", "conversation", "complaint", "slang", "high", "context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "ah sma3 b ras ma nkechf 3and jwarin youm ah trat9i ma te7chemch. drahems dayhom dayhom.",
        "Listen, even if I expose this before the neighbors one day—the phrase 'trat9i' is unclear—have you no shame? Take the money, take it.",
        "들어 봐. 언젠가 이 일을 이웃들 앞에서 폭로하더라도 'trat9i'라는 표현은 불분명해. 부끄럽지도 않아? 돈 가져가, 가져가.",
        "C1", 75, "finance", "neighbor_money_dispute", "conversation", "warning", "slang", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "ah trat9i anaya? chouf rou7 techki ma tedich drahemek trou7 wla ma trou7ch drouk. ah wallah ma raha farya ah sa7a kol choufa makhloufa.",
        "Am I 'trat9i'? That expression is unclear. Go and complain; whether you take your money and leave or do not leave now. By God, the phrase about it not being 'farya' is also unclear. All right; every meeting has another after it.",
        "내가 'trat9i'라고? 그 표현은 불분명해. 가서 신고해. 지금 돈을 가져가서 떠나든 떠나지 않든 해. 맹세코 'farya가 아니다'라는 부분도 뜻이 불분명해. 좋아, 만남 뒤에는 또 다른 만남이 있다는 말이야.",
        "C1", 82, "finance", "argument_over_repayment", "conversation", "disagreement", "slang", "high", "context_heavy|idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "wa7da ma tse3efch yemmaha jat kharja mdaremha 9aletlha ah m7enta win raki ghadya 9aletlha ma t7awsich 3liya jat yemmaha 9aletlha ah raki kima hakka wallah ghir 9ed ma yji khouk n7erchou fik yma7tek reddet 3liha w 9aletlha dezi m3ahom redkhet bab daret rayha w kharjet.",
        "A girl would not obey her mother and came out upset. Her mother asked where she was going; she replied, 'Do not look for me.' The mother threatened to incite her brother against her so that he would beat her. The girl answered, 'Send him with them,' slammed the door, made up her mind, and left. Some wording is uncertain.",
        "한 여자가 어머니 말을 듣지 않고 화가 난 채 나왔어. 어머니가 어디 가느냐고 묻자 '나를 찾지 마'라고 했어. 어머니는 오빠가 오면 부추겨서 그녀를 때리게 하겠다고 위협했어. 그녀는 '그도 그들과 함께 보내'라고 답하고 문을 세게 닫은 뒤 마음먹고 나갔어. 일부 표현은 불분명해.",
        "C1", 84, "family_relationships", "mother_daughter_conflict", "narrative", "narration", "offensive", "high", "context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "ki wellet 3chiya l9at khouha y9er3elha ta7 fiha b lebouniyat 7atta n8elha men hadak nhar wellet tse3ef w tse9met w 9aletlhom ma nzidch n3awed 3mar dwad ma y3awed y3tih 7ebba f mrawed.",
        "When evening came, she found her brother waiting for her. He attacked her with punches until the result described by 'n8elha,' which is unclear. From that day she became obedient and straightened up, saying she would not do it again. The closing proverb-like phrase is also unclear.",
        "저녁이 되자 오빠가 그녀를 기다리고 있었고 주먹으로 공격했어. 그 결과를 나타내는 'n8elha'의 뜻은 불분명해. 그날부터 그녀는 말을 듣고 행동을 바로잡으며 다시는 그러지 않겠다고 했어. 마지막 속담 같은 표현도 불분명해.",
        "C1", 88, "family_relationships", "family_violence_story", "narrative", "narration", "offensive", "high", "idiom_culture|long_source|source_ambiguity", "flagged",
    ),
    item(
        "ana 7kayet 9rayti f lordon wa7edha ghadi n7kilkom ki medouli la bourse l lordon.",
        "The story of my studies in Jordan is a story of its own. I will tell you how they gave me the scholarship to Jordan.",
        "내가 요르단에서 공부한 이야기는 그 자체로 별개의 이야기야. 요르단 장학금을 어떻게 받았는지 말해 줄게.",
        "B1", 43, "education", "jordan_scholarship_story", "narrative", "narration", "mixed", "low", "code_switching",
    ),
    item(
        "ana kent kemelt 9rayti w msoutniya w mkemla master ta3i w kent nkhdem assistante commerciale f wa7ed centre commercial.",
        "I had finished my studies and, after an unclear word, completed my master's degree. I was working as a sales assistant in a shopping center.",
        "나는 학업을 마쳤고, 불분명한 한 단어 뒤에 석사 과정도 끝냈다고 말해. 당시 쇼핑센터에서 영업 보조로 일하고 있었어.",
        "B2", 60, "work", "education_and_sales_job", "narrative", "narration", "mixed", "medium", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "kheddama 3adi men be3d khdemt f jam3iya f projet w kent ana animatrice mam ndir bilan w nkhdem communication f jam3iya.",
        "I was working normally. Later I worked on a project at an association, where I was also an activity facilitator; I prepared reports and handled communications for the association.",
        "평범하게 일하다가 나중에는 한 협회의 프로젝트에서 일했어. 진행자 역할도 하고 보고서를 작성하며 협회의 커뮤니케이션 업무도 맡았어.",
        "B2", 57, "work", "association_project_work", "narrative", "narration", "mixed", "medium", "code_switching",
    ),
    item(
        "wa7ed khatra nchouf f Facebook f groupe ta3 jam3a y7awsou 3liya w yerslouli f les messages belli jam3a raha t7awes 3lik w li y3refha y9olha tji l jam3a urgent.",
        "One time I saw in a university Facebook group that they were looking for me. People sent me messages saying, 'The university is looking for you; whoever knows her, tell her to come to the university urgently.'",
        "어느 날 대학 페이스북 그룹에서 학교가 나를 찾고 있다는 글을 봤어. 사람들도 '대학에서 너를 찾고 있으니 아는 사람은 그녀에게 급히 대학으로 오라고 전해 달라'는 메시지를 보냈어.",
        "B2", 62, "social_media", "urgent_university_contact", "narrative", "narration", "mixed", "medium", "code_switching|long_source",
    ),
    item(
        "aya l9it message ta3 secretaire 9ali arwa7i 3andek bourse 9otlou ih la bourse sayi ditha ma3li ana deja kan 3andi mochkil f la bourse talya ma dkhaltlich.",
        "Then I found a message from the secretary telling me to come because I had a scholarship. I said, 'Yes, I already received the scholarship,' since I had already had a problem with the previous grant not being deposited.",
        "그러다 비서가 장학금이 있으니 오라는 메시지를 보냈어. 나는 전에 받던 장학금이 입금되지 않는 문제가 있었기 때문에 '그 장학금은 이미 받았어요'라고 말했어.",
        "B2", 64, "education", "scholarship_message", "narrative", "narration", "mixed", "medium", "code_switching|context_heavy",
    ),
    item(
        "aya ma dithach ga3 7atta 9ali cha raki t9ouli 3andek bourse l etranger l lordon aya tert b fer7a w ray7a l jam3a nchouf parce que ma amentch 7atta wselet.",
        "I had not understood at all until he said, 'What are you talking about? You have a scholarship abroad, to Jordan.' I flew with joy and went to the university to see, because I did not believe it until I arrived.",
        "나는 전혀 알아듣지 못했는데 그가 '무슨 말을 하는 거야? 해외 장학금, 요르단 장학금이 생겼어'라고 했어. 너무 기뻐서 날아갈 듯 대학으로 확인하러 갔고, 도착할 때까지도 믿기지 않았어.",
        "B2", 63, "education", "foreign_scholarship_news", "narrative", "narration", "mixed", "medium", "code_switching|idiom_culture",
    ),
    item(
        "9alouli belli classiti loula major de promo w rah 3andek bourse b sa7tek w 3andek dossier laimih w def3ih.",
        "They told me, 'You ranked first, top of your graduating class, and you have a scholarship—congratulations. You have a file to assemble and submit.'",
        "그들은 '네가 수석, 졸업반 최우수 학생이어서 장학금을 받게 됐어. 축하해. 서류를 준비해서 제출해야 해'라고 말했어.",
        "B2", 61, "education", "scholarship_award", "narrative", "information", "mixed", "low", "code_switching",
    ),
    item(
        "aya laimtou w def3tou w 9e3dt n9are3 bsa7 kent nrou7 khatra 3la khatra nchouf win wasel dossier ta3i parce que khasou yrou7 7atta Alger 3asma l wizara bach houma yerslouh l jam3a w ndirou lijraat.",
        "I assembled the file, submitted it, and waited. I would go from time to time to check how far it had progressed, because it had to go to the ministry in the capital, Algiers, so they could send it to the university and we could complete the procedures.",
        "서류를 준비해 제출하고 기다렸어. 진행 상황을 확인하려고 때때로 찾아갔지. 서류가 수도 알제의 부처까지 가야 그곳에서 대학으로 보내고 절차를 진행할 수 있었기 때문이야.",
        "C1", 70, "administration", "scholarship_file_process", "narrative", "narration", "mixed", "medium", "code_switching|long_source",
    ),
    item(
        "fat we9t w walou daymen nrou7 w y9olouli mazal aya zahr 9le3t l Alger ki wselet temmak 9alouli belli melef ta3ek ma rahouch ga3 3andna nkhle3t w 9otlhom la kifach ma wselch.",
        "Time passed with nothing happening. I kept going back and they always said, 'Not yet.' Eventually I went to Algiers; when I arrived, they told me my file was not there at all. I was shocked and asked how it had not arrived.",
        "시간이 지나도 아무 진전이 없었어. 계속 찾아가면 늘 '아직'이라고 했지. 결국 알제까지 갔는데 내 서류가 아예 없다는 말을 들었어. 놀라서 어떻게 도착하지 않았느냐고 물었어.",
        "B2", 66, "administration", "missing_scholarship_file", "narrative", "complaint", "colloquial", "medium", "long_source",
    ),
    item(
        "ki kent f jam3a ta3 Wahran 9alouli belli wsel hna kifach ma kanch 9alouli 7na aslan 9olna ghir jam3a Wahran li ma rselounach.",
        "At the University of Oran they had told me it had arrived there, so how could it be missing? The people in Algiers said, 'We had already said that only the University of Oran had not sent anything to us.'",
        "오랑대학교에서는 서류가 그곳에 도착했다고 했는데 어떻게 없을 수 있느냐고 했어. 알제 쪽에서는 '원래 우리에게 아무것도 보내지 않은 곳은 오랑대학교뿐이라고 말했었다'고 했어.",
        "B2", 65, "administration", "contradictory_file_status", "narrative", "complaint", "colloquial", "medium", "context_heavy",
    ),
    item(
        "w n3ayet l jam3a l 3mada w terfed 3liya vice doyenne li 7tit 3andha dossier.",
        "I called the university dean's office, and the vice-dean with whom I had left the file answered me.",
        "대학 학장실로 전화했고, 내가 서류를 맡겼던 부학장이 전화를 받았어.",
        "B2", 54, "administration", "calling_vice_dean", "narrative", "narration", "mixed", "low", "code_switching",
    ),
    item(
        "9otlha kifach ma kanch dossier ta3i ani hna f Alger 9aletli la 7na rselnah 9otlha raki tez3a9i 3liya ani n9ollek rani drouk f wizara w 9alouli belli ma kanch melef ta3ek.",
        "I asked her, 'How can my file be missing? I am here in Algiers.' She said, 'No, we sent it.' I told her, 'Are you shouting at me? I am telling you that I am at the ministry now, and they told me your file is not here.'",
        "나는 '내 서류가 어떻게 없을 수 있죠? 지금 알제에 있어요'라고 물었어. 그녀는 '아니, 우리는 보냈어'라고 했지. 나는 '지금 나한테 소리치는 거예요? 나는 지금 부처에 있고, 여기서는 내 서류가 없다고 했어요'라고 말했어.",
        "C1", 72, "administration", "confronting_vice_dean", "narrative", "complaint", "colloquial", "medium", "context_heavy|long_source",
    ),
    item(
        "aya 9e3det tbeddelli f l hedra w tekdeb 3liya w t9oul rselto 9oltlha medili accuse wara9a belli wsel 9aletli ma 3andich.",
        "She kept changing her story and lying to me, saying she had sent it. I told her, 'Give me an acknowledgment, a paper showing it arrived.' She said, 'I do not have one.'",
        "그녀는 말을 계속 바꾸며 보냈다고 거짓말했어. 나는 '도착했다는 접수증이나 증명서를 주세요'라고 했고, 그녀는 그런 것이 없다고 했어.",
        "B2", 64, "administration", "missing_delivery_receipt", "narrative", "complaint", "mixed", "medium", "code_switching",
    ),
    item(
        "w nwelli l Wahran ana w baba ro7nalha l bureau 9olnalha win rah dossier t9oulna ma 3labalich.",
        "My father and I returned to Oran and went to her office. We asked where the file was, and she told us she did not know.",
        "아버지와 나는 오랑으로 돌아가 그녀의 사무실로 갔어. 서류가 어디 있느냐고 물었지만 그녀는 모른다고 했어.",
        "B1", 43, "administration", "return_to_university_office", "narrative", "narration", "mixed", "low", "code_switching",
    ),
    item(
        "9otlha baghi thabblini win rah dossier ana def3tou 3andek melef 9ed sekht t9oulili ma kanch 9e3dou mcheytini ray7a jaya machi 3arfa 7atta win rah.",
        "I told her, 'Do you want to drive me mad? Where is the file? I submitted it to you, a very large file, and you tell me it is gone.' They kept sending me back and forth, and she did not even know where it was.",
        "나는 '나를 미치게 하려는 거예요? 서류가 어디 있죠? 아주 큰 서류 묶음을 당신에게 제출했는데 없다고 하잖아요'라고 했어. 그들은 나를 계속 이리저리 돌려보냈고, 그녀는 서류가 어디 있는지도 몰랐어.",
        "C1", 71, "administration", "lost_file_complaint", "narrative", "complaint", "slang", "high", "context_heavy|long_source",
    ),
    item(
        "w traduction metrjma ga3 releve ta3 les notes b l anglais w mkhalsa 3liha dem f wadi ta3 drahem w t9ouli ma 3andich.",
        "It also contained translations of all my grade transcripts into English, for which I had paid a huge amount of money, and she was telling me she did not have it.",
        "그 안에는 성적표 전체를 영어로 번역한 서류도 있었고, 나는 거기에 엄청난 돈을 냈어. 그런데 그녀는 가지고 있지 않다고 했어.",
        "C1", 68, "administration", "costly_translated_documents", "narrative", "complaint", "mixed", "medium", "code_switching|idiom_culture",
    ),
    item(
        "w ana n9olha ana 7titoh t9ouli ma kanch jheltni 7atta tle3t l 3mada w 9otlhom 7awsouli jebdouhli men sma men ma wedertouhali w ghadi yfoutni lwe9t deja rah fayet semmoukom tjebdouhli.",
        "I kept telling her I had submitted it, while she said it was not there, until I lost patience and went up to the dean's office. I told them, 'Search for it and bring it to me from wherever you lost it. I am going to miss the deadline; it has already nearly passed. Find it for me.'",
        "나는 분명 제출했다고 계속 말했지만 그녀는 없다고 했어. 결국 참지 못하고 학장실로 올라가 '당신들이 어디에서 잃어버렸든 찾아서 내게 주세요. 마감 시간을 놓치게 생겼고 이미 거의 지났으니 찾아 주세요'라고 했어.",
        "C1", 76, "administration", "escalating_lost_file_search", "narrative", "request", "colloquial", "high", "context_heavy|long_source",
    ),
    item(
        "walou mermdouni kol youm daya taxi w khatrat yjibni baba aya 9olt l baba ghir rwa7 hadou rahom yel3bou 3liya w ma bghawch ymedouli melef ta3i wedrouhli w ma ra7ch ga3 l Alger w ma ghadich yrou7 w trou7li la bourse.",
        "Nothing happened; they wore me down. Every day I took a taxi, and sometimes my father drove me. I told him, 'Come with me. They are playing games with me and do not want to give me my file. They lost it; it never went to Algiers and will not go, and I will lose the scholarship.'",
        "아무 일도 해결되지 않았고 그들은 나를 지치게 했어. 매일 택시를 탔고 때로는 아버지가 데려다줬어. 나는 아버지에게 '같이 가 주세요. 저 사람들이 나를 가지고 놀며 서류를 주지 않아요. 서류를 잃어버려 알제에 가지도 않았고 앞으로도 못 가면 장학금을 잃게 돼요'라고 했어.",
        "C1", 79, "administration", "bureaucratic_exhaustion", "narrative", "complaint", "mixed", "high", "code_switching|context_heavy|long_source",
    ),
    item(
        "ma dabihom yddu m3erfa w 7babhom w ydouli 7a9i ghir hadi li ma tesrach.",
        "They may favor acquaintances and their friends if they wish, but taking away my right is the one thing that must not happen.",
        "그들이 아는 사람이나 친구를 챙기고 싶다면 그럴 수 있어도, 내 권리를 빼앗는 일만큼은 있어서는 안 돼.",
        "B2", 58, "administration", "defending_entitlement", "narrative", "opinion", "colloquial", "medium", "idiom_culture",
    ),
    item(
        "ghodwa jina ghodwa men dak baba dar tabage nza9ou jebdoulna dossier tla9aha hadik doyenne 9a3da takel f rou7ha.",
        "The next day we came back. My father made a scene and raised his voice, and they brought out our file. That dean was left seething with anger.",
        "다음 날 다시 갔어. 아버지가 소란을 피우며 목소리를 높이자 그들이 우리 서류를 꺼내 왔어. 그 학장은 속이 끓는 듯 화를 내고 있었어.",
        "B2", 62, "administration", "recovering_lost_file", "narrative", "narration", "slang", "medium", "idiom_culture",
    ),
    item(
        "9alha ostada ta3 batata ma testahlich tkouni ostada.",
        "He told her, 'Potato professor, you do not deserve to be a professor.'",
        "그는 그녀에게 '감자 교수 같으니, 교수 자격도 없어'라고 말했어.",
        "B1", 45, "education", "insulting_professor", "narrative", "complaint", "offensive", "medium", "idiom_culture",
    ),
    item(
        "ana ghalta li dertha koun ki 7titoh temedli recu accuse belli def3tou w masoulietha ana ma 3reftch.",
        "My mistake was that when I submitted it, I should have had her give me a receipt or acknowledgment proving submission. I did not know that this was my responsibility.",
        "내 실수는 서류를 제출할 때 접수했다는 영수증이나 확인서를 받아 두지 않은 것이었어. 그것이 내 책임인 줄 몰랐어.",
        "B2", 59, "administration", "submission_receipt_lesson", "narrative", "opinion", "mixed", "medium", "code_switching",
    ),
    item(
        "mohim tle3na l rectorat plafond li ye7kem fihom ga3 3amid jina dakhlin tkhrejna secritairetou ma rahch hna diri demande bach tchoufih w 9ar3i.",
        "In any case, we went up to what appears to be the rectorate or highest office overseeing them. As we were entering, his secretary came out and said, 'He is not here. Submit a request to see him and wait.' The office title is corrupted in the source.",
        "어쨌든 우리는 그들을 모두 관할하는 총장실 또는 최고 부서로 보이는 곳에 올라갔어. 들어가려는데 비서가 나오며 '그분은 여기 없으니 면담 신청을 하고 기다리세요'라고 했어. 부서 명칭은 원문에서 손상돼 있어.",
        "C1", 82, "administration", "requesting_rector_meeting", "narrative", "narration", "mixed", "high", "code_switching|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "tert fiha w 9otlha ana mes7a9inah urgent ma ne9douch n9ar3ou aya 9e3det tetfelsef 3lina w 3labna belli rah dakhel 7atta 9odra men 3and allah sob7anou w yebghi ysellek 3badou ja wa7ed kharej men bureau ta3 recteur.",
        "I snapped at her and said, 'We need him urgently; we cannot wait.' She began lecturing us, although we knew he was inside. Then, by God's providence—God saves His servants—a man came out of the rector's office.",
        "나는 화를 내며 '긴급히 그분이 필요해서 기다릴 수 없어요'라고 했어. 그가 안에 있다는 걸 알고 있었지만 비서는 우리에게 훈계하기 시작했어. 그때 하나님의 섭리로, 하나님이 종들을 구하시려는 듯 총장실에서 한 남자가 나왔어.",
        "C1", 78, "administration", "urgent_rector_access", "narrative", "narration", "mixed", "high", "code_switching|long_source",
    ),
    item(
        "sa7eb baba y3erfou gaya 9alou Bchir cha rak dir hna sellem 3lih w 9alou cha khassek aya 9alou benti mclassya loula fakhr l jam3a rahom yjerjrou fiha wedroulha dossier li laimtah l bourse bach trou7 t9ra aya baghyin nchoufou recteur.",
        "He was a close acquaintance of my father. He asked, 'Bashir, what are you doing here?' They greeted, and he asked what he needed. My father said, 'My daughter ranked first and is a credit to the university, but they are dragging her around and lost the scholarship file she prepared to study abroad. We want to see the rector.'",
        "그는 아버지와 아주 가까운 지인이었어. '바시르, 여기서 뭐 해?'라고 묻고 인사를 나눈 뒤 무슨 일이냐고 했어. 아버지는 '제 딸은 수석으로 대학의 자랑인데, 사람들이 계속 끌고 다니며 유학 장학금 서류를 잃어버렸습니다. 총장을 만나고 싶어요'라고 했어.",
        "C1", 80, "administration", "explaining_case_to_contact", "narrative", "narration", "colloquial", "high", "context_heavy|long_source",
    ),
    item(
        "9alou arwa7 ana ndik 9al l secretaire 9alha be3di hada yedkhol m3aya aya dkhalna w 7kina lou belli hiya fakhr jam3a w 7a9hom ykermouni machi ychitouni w ywedrouli dossier ta3i w ki nkemel nwelli fakhr l wilaya Wahran ga3.",
        "He said, 'Come, I will take you,' and told the secretary to step aside because this man was entering with him. We went in and explained that I was a credit to the university; they should honor me, not humiliate me and lose my file, and when I finished I would be a credit to the whole province of Oran.",
        "그는 '가자, 내가 데려다줄게'라고 하고 비서에게 이 사람이 자신과 함께 들어갈 테니 비키라고 했어. 우리는 들어가 내가 대학의 자랑인데 나를 모욕하고 서류를 잃어버릴 게 아니라 존중해야 하며, 학업을 마치면 오랑주 전체의 자랑이 될 것이라고 설명했어.",
        "C1", 78, "education", "appeal_to_rector", "narrative", "complaint", "mixed", "high", "code_switching|long_source",
    ),
    item(
        "aya 9alou ana ma 3labalich belli rah sari ga3 had chi w rahom ghabninek drouk douk nchouflek ahder m3a doyenne w vice recteur.",
        "He said, 'I did not know any of this was happening or that they had wronged you. I will look into it now,' and spoke with the dean and vice-rector.",
        "그는 '이런 일이 벌어지고 너에게 부당한 일을 했다는 걸 전혀 몰랐다. 지금 바로 알아보겠다'고 말하고 학장과 부총장에게 이야기했어.",
        "B2", 57, "administration", "rector_intervention", "narrative", "information", "mixed", "medium", "code_switching",
    ),
    item(
        "w 9alhom li classat loula drouk t7awsou w tjebdoulha dossier ta3ha wla blastek ttir.",
        "He told them, 'For the student who ranked first, search now and bring out her file, or you will lose your position.'",
        "그는 그들에게 '수석을 한 학생의 서류를 지금 당장 찾아서 꺼내라. 그러지 않으면 자리를 잃을 것이다'라고 했어.",
        "B2", 56, "administration", "order_to_find_file", "narrative", "command", "mixed", "low", "code_switching",
    ),
    item(
        "9otlou manich baghya nkhroj 7atta ndih 3awed 3ayet 9alhom ma tkhrejouch 7atta tel9awh ani n9are3 7a9 we9ef m3ana w f tali win l9awh gaysinheli f l archive f ghobra.",
        "I told him, 'I am not leaving until I take it.' He called again and told them not to come out until they found it, while I waited. He truly stood by us. In the end they found it lying in the archive, covered in dust.",
        "나는 '서류를 받을 때까지 나가지 않겠습니다'라고 했어. 그는 다시 전화해 내가 기다리는 동안 서류를 찾기 전에는 나오지 말라고 지시했어. 그는 정말 우리 편에 서 줬어. 결국 서류는 기록 보관소에서 먼지를 뒤집어쓴 채 발견됐어.",
        "C1", 71, "administration", "file_found_in_archive", "narrative", "narration", "mixed", "medium", "code_switching|long_source",
    ),
    item(
        "w rselna 3and li ta7tou vice recteur st9beltna w 9e3det tra9e3 f l hedra w wsahom 9alhom lyoum tdouh l Alger y9le3 3chiya w ydih bach yousel lyoum w ytraitouh ghodwa f wizara.",
        "He sent us to the vice-rector under him. She received us and began patching together excuses. He instructed them to take the file to Algiers that day: someone was to leave in the afternoon with it so it would arrive that day and be processed at the ministry the next day.",
        "그는 우리를 산하 부총장에게 보냈어. 그녀는 우리를 맞고 변명을 이어 붙이기 시작했어. 그는 그날 서류를 알제로 가져가도록 지시했고, 오후에 누군가 서류를 들고 출발해 당일 도착시키고 다음 날 부처에서 처리하게 했어.",
        "C1", 75, "administration", "urgent_file_dispatch", "narrative", "narration", "mixed", "high", "code_switching|long_source",
    ),
    item(
        "rselouh be3d 3ana tawil aya men be3d wsel Alger 9le3na 7na tani l Alger ki wselna tani probleme wa7ed akhor dkhlet 3and wa7ed li yched dossiers ta3 la bourse.",
        "They sent it after a long struggle. Once it reached Algiers, we also went to Algiers. When we arrived, there was yet another problem. I went in to see someone responsible for scholarship files.",
        "오랜 고생 끝에 그들이 서류를 보냈어. 서류가 알제에 도착한 뒤 우리도 알제로 갔지. 도착하니 또 다른 문제가 있었고, 나는 장학금 서류 담당자를 만나러 들어갔어.",
        "B2", 62, "administration", "new_problem_in_algiers", "narrative", "narration", "mixed", "medium", "code_switching",
    ),
    item(
        "apres ro7t bureau ta3 sous-directrice l mokhtassa f mina7 f l kharej 9atli l7e9ti retard rah fat delai w tnazelti nti.",
        "Afterward I went to the office of the deputy director responsible for overseas scholarships. She told me, 'You are late; the deadline has passed, and you have withdrawn.'",
        "그다음 해외 장학금을 담당하는 부국장 사무실로 갔어. 그녀는 '늦게 왔어요. 마감 기한이 지났고 당신은 포기한 것으로 처리됐어요'라고 했어.",
        "B2", 61, "administration", "missed_scholarship_deadline", "narrative", "information", "mixed", "medium", "code_switching",
    ),
    item(
        "9otlha kifach winta hadi ana ma tnazeltch 9atli ma jana 7atta rad men jam3a ta3 Wahran 9otlha parce que def3tou w wedrouhli kol khatra y9olouli belli rselnah 7atta l9itah.",
        "I asked her, 'How? When did that happen? I did not withdraw.' She said they had received no reply from the University of Oran. I told her, 'Because I submitted it and they lost it. Every time they told me they had sent it, until I finally found it.'",
        "나는 '어떻게요? 언제 그런 일이 있었죠? 저는 포기하지 않았어요'라고 했어. 그녀는 오랑대학교에서 아무 회신도 오지 않았다고 했어. 나는 '서류를 제출했는데 그들이 잃어버렸어요. 찾을 때까지 매번 보냈다고만 했어요'라고 설명했어.",
        "C1", 69, "administration", "denying_scholarship_withdrawal", "narrative", "disagreement", "mixed", "medium", "code_switching|context_heavy",
    ),
    item(
        "9atli ah 7na khatina 9otlha wah ana manich n7essel fik ani n9ollek cha sra drouk jebtoulek bach terslouhli 3awnouni.",
        "She said, 'We are not responsible.' I replied, 'Yes, I am not blaming you; I am telling you what happened. Now I have brought it so that you can send it for me. Help me.'",
        "그녀는 '우리 책임은 아니에요'라고 했어. 나는 '네, 당신을 탓하는 게 아니라 무슨 일이 있었는지 설명하는 거예요. 이제 서류를 가져왔으니 보내 주세요. 도와주세요'라고 했어.",
        "B2", 55, "administration", "requesting_help_to_send_file", "narrative", "request", "colloquial", "low", "",
    ),
    item(
        "9atli s3iba w deja rselna dossiers w mena w 9e3dou ychklou 3liya 9otlha 9oltouli loula ghir jibih w drouk ki jebtou khrejtouli b 7aja wa7doukhra.",
        "She told me it was difficult and that they had already sent the files, then continued giving me trouble. I said, 'At first you told me only to bring it, and now that I have brought it, you have come up with something else.'",
        "그녀는 어렵고 이미 서류들을 보냈다고 하면서 계속 문제를 제기했어. 나는 '처음에는 가져오기만 하라고 했는데, 이제 가져오니 또 다른 이유를 꺼내네요'라고 말했어.",
        "B2", 62, "administration", "changing_submission_requirements", "narrative", "complaint", "mixed", "medium", "code_switching|context_heavy",
    ),
    item(
        "9alouli machi 7na houma tkhafi ma y9blouch 9otlhom ma3lich ghir rselou ida ma y9blouch ma3lich mohim rselou.",
        "They told me, 'It is not us; perhaps they will not accept it.' I said, 'That is all right—just send it. If they do not accept it, that is fine; the important thing is to send it.'",
        "그들은 '우리 문제가 아니라 그쪽에서 받아 주지 않을까 걱정된다'고 했어. 나는 '괜찮으니 그냥 보내 주세요. 받아 주지 않아도 괜찮아요. 중요한 건 보내는 거예요'라고 했어.",
        "B1", 47, "administration", "insisting_on_submission", "narrative", "request", "colloquial", "low", "",
    ),
    item(
        "houma bel3ani ma bghawch y3eyou rwa7hom w yerslou aya 9e3dou ydirouli f sbayeb. aya 9alouli 7na nerslou w nchoufou ma kanch 7aja garantie w ana ghadetni 3omri wa7ed y3ya w rbi ykteblou 7aja w yjou ydoulou 7a9ou.",
        "They deliberately did not want to trouble themselves by sending it, so they kept making excuses. They said, 'We will send it and see; nothing is guaranteed.' I was upset that someone could work hard, have God ordain something for them, and then have others take away their right.",
        "그들은 일부러 수고해서 보내려 하지 않고 계속 핑계를 댔어. 그러다 '보내 보고 지켜보자. 보장되는 건 없다'고 했지. 누군가 열심히 노력하고 하나님이 어떤 기회를 정해 주셨는데 다른 사람들이 그 권리를 빼앗는다는 게 속상했어.",
        "C1", 75, "administration", "bureaucratic_obstruction", "narrative", "complaint", "colloquial", "high", "context_heavy|long_source",
    ),
    item(
        "parce que nestahel 9rit w 3yit aya wellina l dar mdemrin rfe3t yedi w 9olt ya rbi ida fiha khir ktebha liya w ana ndir li 3liya.",
        "Because I deserved it: I had studied and worked hard. We returned home devastated. I raised my hands and said, 'Lord, if there is good in it, decree it for me, and I will do my part.'",
        "나는 그럴 자격이 있었어. 공부하며 열심히 노력했으니까. 우리는 낙담한 채 집으로 돌아왔어. 나는 두 손을 들고 '주님, 이것이 좋은 일이라면 제 몫으로 정해 주세요. 저는 제가 할 일을 하겠습니다'라고 기도했어.",
        "B2", 61, "religion", "prayer_for_scholarship", "narrative", "wish", "mixed", "medium", "code_switching",
    ),
    item(
        "aya tchawert m3a bouya w 9otlou ani 7assa koun n9a3ed ghir hak ma ghadich yerslouhli ghir choufli 3mi li yekhdem f parlement ghir bach yerslouh houma koun yzidou ydirou l retard w ma yerslouhch l lordon ma ghadich ga3 nrou7 w tetfer fiya.",
        "I consulted my father and told him, 'I feel that if I just wait like this, they will not send it. Contact my uncle who works in parliament, only so they will send it. If they delay again and do not send it to Jordan, I will not be able to go at all, and I will be the one who suffers.'",
        "나는 아버지와 상의하며 '이대로 기다리기만 하면 그들이 보내지 않을 것 같아요. 의회에서 일하는 삼촌에게 연락해서 최소한 서류를 보내게 해 주세요. 또 지연해서 요르단으로 보내지 않으면 나는 아예 갈 수 없고 피해는 내가 보게 돼요'라고 했어.",
        "C1", 77, "administration", "seeking_parliamentary_help", "narrative", "request", "mixed", "high", "code_switching|context_heavy|long_source",
    ),
    item(
        "aya 7ka m3a 3mi 9alou cousine ta3i classat major de promo f jam3a ta3 Wahran w sralha probleme w wedroulha dossier.",
        "He spoke with my uncle and said, 'My cousin ranked top of her graduating class at the University of Oran, but she had a problem and they lost her file.'",
        "아버지는 삼촌에게 '내 사촌이 오랑대학교 졸업반 수석을 했는데 문제가 생겨 학교에서 서류를 잃어버렸어'라고 설명했어.",
        "B2", 57, "administration", "explaining_case_to_uncle", "narrative", "narration", "mixed", "medium", "code_switching",
    ),
    item(
        "7kinah lou ga3 cha sra 7a9 we9ef m3ana w 3ayet l sa7bou senateur w khallana netla9ou m3a moustachara wazir f cabinet ta3ha chkoun youselha ta wa7ed ma ychoufha tekhdem m3a wazir ta3lim l 3ali 7ajjar 7aja kbira.",
        "We told him everything that had happened. He truly stood by us, called his friend, a senator, and arranged for us to meet a ministerial adviser in her office. Reaching her was difficult and few people could see her; she worked with Higher Education Minister Hadjar and held a senior position.",
        "우리는 그동안 벌어진 일을 모두 말했어. 그는 정말 우리 편에 서서 상원의원인 친구에게 연락했고, 장관 고문의 사무실에서 만나도록 주선했어. 만나기 어려워 아무나 볼 수 없는 사람이었고, 고등교육부 장관 하자르와 일하는 고위 인사였어.",
        "C1", 81, "politics_public_affairs", "ministerial_intervention", "narrative", "narration", "mixed", "high", "code_switching|context_heavy|long_source",
    ),
    item(
        "7a9 st9beltna 7 biban bach wselna w 7kinalha 9olnalha rana baghyin ghir dossier yerslouh.",
        "She did receive us; we passed through seven doors before reaching her. We told her the story and said that all we wanted was for them to send the file.",
        "그녀는 실제로 우리를 만나 줬고, 우리는 일곱 개의 문을 지나서야 도착했어. 사정을 설명하며 우리가 원하는 것은 그들이 서류를 보내는 것뿐이라고 했어.",
        "B2", 56, "administration", "meeting_ministerial_adviser", "narrative", "request", "colloquial", "medium", "idiom_culture",
    ),
    item(
        "rah men l khmis ga3ed w rah yfout lwe9t 9atli ghir ma tet9el9ich nti ray7a ray7a khrejti f minister ma kanch li y9el3halek.",
        "It had been sitting there since Thursday and time was passing. She told me, 'Do not worry. You are definitely going. Once the ministry has selected you, no one can take it away from you.'",
        "서류는 목요일부터 그대로 있었고 시간은 지나가고 있었어. 그녀는 '걱정하지 마. 너는 반드시 가게 돼. 부처에서 선발된 이상 아무도 그 기회를 빼앗을 수 없어'라고 말했어.",
        "B2", 58, "education", "scholarship_reassurance", "narrative", "information", "mixed", "medium", "code_switching",
    ),
]


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_items(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    source_by_sentno = {
        row["sentno"]: row["source_uid"]
        for row in source_rows
        if TARGET_START <= int(row["sentno"]) <= TARGET_END
    }
    expected = [str(number) for number in range(TARGET_START, TARGET_END + 1)]
    if len(RAW_ITEMS) != len(expected):
        raise RuntimeError(f"batch_item_coverage_mismatch:{len(RAW_ITEMS)}")
    if len(source_by_sentno) != len(expected):
        raise RuntimeError("source_target_coverage_mismatch")
    rows: list[dict[str, str]] = []
    for sentno, raw in zip(expected, RAW_ITEMS):
        payload = {key: str(value) for key, value in raw.items()}
        for field in EMPTY_FIELDS:
            value = payload.get(field, "")
            if not value or value != value.strip() or any(char in value for char in "\t\r\n"):
                raise RuntimeError(f"invalid_value:{sentno}:{field}")
        if not payload["latin"].isascii():
            raise RuntimeError(f"latin_not_ascii:{sentno}")
        if payload["cefr_level"] not in CEFR_LEVELS:
            raise RuntimeError(f"invalid_cefr:{sentno}")
        score = int(payload["difficulty_score"])
        if not 0 <= score <= 100:
            raise RuntimeError(f"invalid_difficulty:{sentno}")
        for field, allowed in CONTROLLED_VALUES.items():
            if payload[field] not in allowed:
                raise RuntimeError(f"invalid_controlled_value:{sentno}:{field}")
        flags = payload["processing_flags"]
        flag_values = flags.split("|") if flags else []
        if flag_values != sorted(flag_values) or len(flag_values) != len(set(flag_values)):
            raise RuntimeError(f"non_canonical_flags:{sentno}")
        if any(value not in PROCESSING_FLAG_VALUES for value in flag_values):
            raise RuntimeError(f"invalid_processing_flag:{sentno}")
        if payload["enrichment_state"] not in {"draft", "flagged"}:
            raise RuntimeError(f"invalid_enrichment_state:{sentno}")
        if payload["enrichment_state"] == "flagged" and not flags:
            raise RuntimeError(f"flagged_without_reason:{sentno}")
        rows.append({"source_uid": source_by_sentno[sentno], "sentno": sentno, **payload})
    return rows


def write_tsv(rows: list[dict[str, str]]) -> None:
    BATCH_OUT.parent.mkdir(parents=True, exist_ok=True)
    with BATCH_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=BATCH_FIELDS,
            delimiter="\t",
            lineterminator="\n",
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(rows)


def build() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    contract = check_layer_contract()
    if contract["result"] != "PASS":
        raise RuntimeError(json.dumps(contract, ensure_ascii=False))
    source_rows = read_tsv(SOURCE_OUT)
    rows = validate_items(source_rows)
    generated_at = current_utc_timestamp()
    existing_rows = read_tsv(ROOT / "data" / "master" / "enrichment" / "madoran_sentence_enrichment.tsv")
    existing_topics = {
        row["topic"] for row in existing_rows
        if row.get("topic") and not TARGET_START <= int(row["sentno"]) <= TARGET_END
    }
    topics = sorted({row["topic"] for row in rows})
    flag_counts = Counter(
        flag for row in rows if row["processing_flags"]
        for flag in row["processing_flags"].split("|")
    )
    scores = [int(row["difficulty_score"]) for row in rows]
    manifest = {
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "row_count": len(rows),
        "fields": [*EMPTY_FIELDS, "processing_flags", "enrichment_state"],
        "prompt_version": PROMPT_VERSION,
        "source_dependency": "canonical_source_only",
        "morphology_dependency": False,
        "darija_modified": False,
        "schema_version": "1.1.0",
        "generated_at": generated_at,
        "review_state": "generated",
    }
    write_tsv(rows)
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "target_rows": len(rows),
        "draft_rows": sum(row["enrichment_state"] == "draft" for row in rows),
        "flagged_rows": sum(row["enrichment_state"] == "flagged" for row in rows),
        "flagged_row_sentnos": [row["sentno"] for row in rows if row["enrichment_state"] == "flagged"],
        "processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in rows),
        "cefr_counts": dict(sorted(Counter(row["cefr_level"] for row in rows).items())),
        "difficulty_stats": {
            "min": min(scores),
            "max": max(scores),
            "mean": round(statistics.mean(scores), 2),
            "median": statistics.median(scores),
        },
        "flag_counts": dict(sorted(flag_counts.items())),
        "topics_reused": sorted(set(topics) & existing_topics),
        "topics_new": sorted(set(topics) - existing_topics),
        "required_linguistic_fields": len(rows) * len(EMPTY_FIELDS),
        "source_gate": "PASS",
        "layer_contract": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "learning_unit_rows_created": 0,
        "validator": "PASS",
        "generated_at": generated_at,
        "outputs": {
            "batch": BATCH_OUT.relative_to(ROOT).as_posix(),
            "manifest": MANIFEST_OUT.relative_to(ROOT).as_posix(),
        },
    }
    QA_OUT.parent.mkdir(parents=True, exist_ok=True)
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
