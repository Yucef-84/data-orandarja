"""Build source-only MADOran enrichment Batch 05 for Sentno 257..320."""

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


BATCH_ID = "MADORAN-ENRICH-005"
BASE_COMMIT = "496ff56"
PROMPT_VERSION = "madoran-source-enrichment-v5"
TARGET_START = 257
TARGET_END = 320
BATCH_DIR = ROOT / "data" / "master" / "enrichment" / "batches"
BATCH_OUT = BATCH_DIR / "batch05_sentno_0257_0320.tsv"
MANIFEST_OUT = BATCH_DIR / "batch05_manifest.json"
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_generation_qa.json"
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
    # Keep the derived Latin layer ASCII even if a copied transliteration token
    # accidentally contains a source-script character.
    latin = latin.replace("मे", "me")
    latin = latin.translate(
        str.maketrans(
            {
                "ا": "a",
                "ب": "b",
                "ت": "t",
                "ث": "th",
                "ج": "j",
                "ح": "7",
                "د": "d",
                "ر": "r",
                "س": "s",
                "ش": "sh",
                "ص": "s",
                "ض": "d",
                "ط": "t",
                "ظ": "z",
                "ع": "3",
                "غ": "gh",
                "ف": "f",
                "ق": "9",
                "ك": "k",
                "ل": "l",
                "م": "m",
                "ن": "n",
                "ه": "h",
                "و": "w",
                "ي": "i",
                "ى": "a",
                "ة": "a",
                "ء": "'",
            }
        )
    )
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
        "ana tani kent kifek w medouli la bourse l France 3echt f Masr mi mohim re7t tesma nchallah b rabi trou7i.",
        "I was also like you, and they gave me a scholarship to France. I lived in Egypt, but anyway I went. God willing, you will go too.",
        "나도 너와 같았고 프랑스 장학금을 받았어. 이집트에서 살았지만 어쨌든 갔지. 하나님의 뜻이라면 너도 가게 될 거야.",
        "B2", 56, "education", "foreign_scholarship_encouragement", "conversation", "suggestion", "mixed", "medium", "code_switching",
    ),
    item(
        "3aytet l secretaire general S G y9oulou w houwa 3ayet l sous directrice li ma mdethach fiya w 9atli fat delai 9atlha drouk terslou dossier ta3ha aya 9atli welli 3andha aya lakhra ma 3ejbhash 7al.",
        "I called the secretary-general, S.G. He called the deputy director who had not helped me; she said the deadline had passed. He told her to send her file now. Then she told me that she had another matter that she did not like; the final wording is unclear.",
        "사무총장 S.G.에게 전화했어. 그는 나를 도와주지 않았던 부국장에게 전화했고, 그녀는 마감 기한이 지났다고 했어. 그는 지금 서류를 보내라고 했어. 이어 그녀가 마음에 들지 않는 다른 일이 있다고 했는데 마지막 표현은 불분명해.",
        "C1", 81, "administration", "scholarship_deadline_intervention", "narrative", "narration", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "mi cheft li fou9ha z3ma fawetha men che9ha parce que hiya 9e3det tetla3eb 3liya.",
        "But I saw the person above her and, supposedly, got past her through her side because she kept playing games with me. Some of the expression is unclear.",
        "그런데 그녀의 상급자를 만났고, 그녀가 계속 나를 가지고 놀았기 때문에 어떻게든 그녀를 거쳐 넘어갔다는 말이야. 일부 표현은 불분명해.",
        "B2", 62, "administration", "escalating_complaint", "narrative", "complaint", "slang", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "mohim 7amdillah l9it f groupe ta3 Facebook belli hadouk dossiers li rselouhom machi kamlin w lordon 3awed rje3thom l dzayer 9atlhom ma y9blouch 7atta ykemlou watha2e9.",
        "Anyway, thank God, I found in a Facebook group that the files they had sent were incomplete. Jordan had sent them back to Algeria and told them they would not be accepted until the documents were completed.",
        "어쨌든 다행히 페이스북 그룹에서 그들이 보낸 서류가 완전하지 않았다는 걸 알게 됐어. 요르단이 서류를 알제리로 돌려보내며 서류가 완비될 때까지 접수하지 않겠다고 했대.",
        "B2", 62, "education", "returned_incomplete_documents", "narrative", "information", "mixed", "medium", "code_switching",
    ),
    item(
        "ki cheftha fer7t 9olt sob7anallah haka ki y3awdou yerslou l jam3a l ordoniya yerslou dossier ta3i m3ahom parce que ta3i kamel fih kolchi ma ghadich yrefdouh 7amdillah.",
        "When I saw that, I was happy and said, 'Glory be to God. When they resend the files to the Jordanian university, they will send mine with them, because mine is complete and contains everything; they will not reject it, thank God.'",
        "그걸 보고 기뻐서 '하나님을 찬양해. 요르단 대학에 다시 보낼 때 내 서류도 함께 보내겠네. 내 서류는 모든 것이 갖춰져 있어서 거절하지 않을 거야. 다행이야'라고 했어.",
        "B2", 61, "education", "complete_file_hope", "narrative", "wish", "mixed", "medium", "code_switching|idiom_culture",
    ),
    item(
        "fer7t w tersel w 9are3t chwiya aya abri 3ayetouli 9alouli 7amdillah bsa7tek sniyt contrat ta3 4 snin w jبت visa hadak nhar w mيتة b fer7a 7amdillah rabi ktebhali w re7t w 7amdillah.",
        "I was happy; it was sent, and I waited a little. Then they called and told me, 'Thank God, congratulations.' I signed a four-year contract and got my visa that day. I was overwhelmed with joy. Thank God, God had written it for me, and I went.",
        "기뻤고 서류가 보내진 뒤 조금 기다렸어. 그러자 전화가 와서 '다행이야, 축하해'라고 했지. 4년 계약에 서명하고 그날 비자도 받았어. 기쁨으로 벅찼지. 하나님이 내게 정해 주신 일이어서 갔어. 감사해.",
        "B2", 67, "education", "scholarship_success", "narrative", "narration", "mixed", "medium", "code_switching|idiom_culture|long_source",
    ),
    item(
        "ki yektebhalek rabi 7atta 3abd ma y9olhalek ida 3tak 3ati jbal liki tati w hadi hiya wa7ed yes3a w rabi ykemlou inchallah.",
        "When God writes something for you, no person can take it away. If He gives, He gives mountains for you to climb. That is how it is: a person strives, and God completes the matter, God willing.",
        "하나님이 네게 정해 주신 일은 아무도 빼앗을 수 없어. 하나님이 주시면 네가 오를 산도 주셔. 사람이 노력하면 하나님이 일을 완성해 주신다는 말이야.",
        "B2", 65, "religion", "faith_and_perseverance", "proverb", "wish", "colloquial", "medium", "idiom_culture",
    ),
    item(
        "salam 3likom sa7a ramdankom wselouni bezaf men les messages men 3and mettab3in ta3 mosalsal Wlad Hlal w tkelmou 3la hadak li 9alou bayan belli madmoun mosalsal ma yli9ch ybث f les chaines ta3 television.",
        "Peace be upon you, Ramadan greetings. I received many messages from followers of the series Oulad El Halal. They discussed the statement saying that the series' content was not suitable for broadcast on television channels.",
        "안녕하세요. 라마단 잘 보내세요. 드라마 '울라드 할랄'의 시청자들에게서 많은 메시지를 받았어. 드라마의 내용이 텔레비전 채널에서 방송되기에 적절하지 않다는 성명에 대해 이야기했어.",
        "B2", 63, "entertainment_music", "television_series_controversy", "speech", "information", "mixed", "medium", "code_switching",
    ),
    item(
        "w rselouli ناس bezaf men mdina Wahran y9ollek belli 7na metberriyin men hada chi.",
        "Many people from the city of Oran sent me messages saying, 'We dissociate ourselves from this matter.'",
        "오랑시의 많은 사람들이 '우리는 이 일과 아무 관련이 없다'고 말하는 메시지를 보내 왔어.",
        "B1", 43, "politics_public_affairs", "public_disavowal", "speech", "disagreement", "colloquial", "low", "",
    ),
    item(
        "w 3labali parce que hadik 9anat Ben 3ami 7lebtouha w allah ma 3andich kifach nwessefkom rak fahem kont 9ayelkom kont emjinekkom belli ntouma 9anat kima y9olou zi9ou bsa7 had l 9anat kayen rkhess lel 7echti jib wa7ed 3000 metr ta7tha tji 9anat nhar.",
        "And I know why: you milked that Benami channel. By God, I do not know how to describe you; you understand. I had told you that you were a channel people call 'zi9ou,' but this channel has a cheapness that is hard to describe. Bring someone 3,000 meters below it and Nahar TV would still come out on top. Several expressions are unclear.",
        "왜 그런지 알아. 너희가 그 벤아미 채널을 완전히 이용해 먹었기 때문이야. 정말 어떻게 표현해야 할지 모르겠어. 너희는 사람들이 'zi9ou'라고 부르는 채널이라고 했지만, 이 채널의 저급함은 말로 다 못 해. 그보다 3,000미터 아래에 누군가를 데려와도 나하르 채널이 더 나을 거야. 일부 표현은 불분명해.",
        "C1", 88, "politics_public_affairs", "media_criticism", "speech", "complaint", "offensive", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "tesma فوتو rkhess z3ma manich mamen dertou wa7ed z3ma dar ورقة hadouk tajamou3at f blas d arm.",
        "So you made it pass as something cheap? I do not believe it. You had someone make a paper about those gatherings in Place d'Armes; the wording is unclear.",
        "그러니까 너희는 그 일을 저급한 것으로 넘겼다는 거야? 믿기지 않아. 너희가 누군가에게 아르메 광장의 집회에 관한 문서를 만들게 했다는 말인데, 표현이 불분명해.",
        "B2", 70, "politics_public_affairs", "protest_document_claim", "speech", "complaint", "slang", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "hadouk rahom yetjमे3ou l 7irak ntouma rakom did 7irak rahom kol youm yetjमे3ou w 3ardouni temmak bach nchouf spectacle de theatre rahom yjou kol youm yetjमे3ou l 7irak khati ga3 mosalsal.",
        "Those people gather for the Hirak movement, while you are against the Hirak. They gather every day. They invited me there to see a theater show; they come together for the Hirak every day, which has nothing to do with the series.",
        "그 사람들은 히라크 운동을 위해 모이고 너희는 히라크에 반대하잖아. 그들은 매일 모여. 나를 그곳의 연극 공연에 초대했는데, 그들이 매일 히라크를 위해 모이는 일은 드라마와 전혀 관계가 없어.",
        "C1", 79, "politics_public_affairs", "hirak_protest_and_series", "speech", "disagreement", "mixed", "high", "code_switching|context_heavy|long_source|source_corruption", "flagged",
    ),
    item(
        "hadouk ناس rahom ykhrjou kol lil hadouk monاضلين ta3 sa7 w ja wa7ed kteb ورقة w 7atha haka w z3ma dar tswira w khla cha3b morah w 9al hadouk سكان mdina Wahran.",
        "Those people go out every night; they are genuine activists. Then someone wrote a paper, placed it there, supposedly took a picture with people behind him, and said, 'These are residents of the city of Oran.'",
        "그 사람들은 매일 밤 나오는 진짜 활동가들이야. 그런데 누군가 문서를 써서 그곳에 놓고, 뒤에 사람들이 있는 사진을 찍은 듯 꾸민 다음 '이들은 오랑시 주민들이다'라고 했어.",
        "C1", 76, "politics_public_affairs", "staged_public_statement", "speech", "complaint", "mixed", "high", "context_heavy|long_source",
    ),
    item(
        "dak bayan ma rah mمضي ma fihch 9ayma ismiya ma walou z3ma fou9 rkhess ma kayench rak fahemni ntouma 9anat 7طيتو ma3loumat machi nicha 3la cha3b w arozmon cha3b y3refkom kidaيرين.",
        "That statement was not signed and had no list of names, nothing. It was worthless. You understand me: you are a channel that put inaccurate information about the people, and 'arozmon' is unclear; the people know what you are like.",
        "그 성명에는 서명도 명단도 아무것도 없었어. 사실상 아무 가치가 없었지. 너희는 사람들에 대한 정확하지 않은 정보를 내보낸 채널이고, 'arozmon'이라는 표현은 불분명해. 사람들은 너희가 어떤지 알고 있어.",
        "C1", 84, "politics_public_affairs", "unsigned_statement_critique", "speech", "complaint", "offensive", "high", "context_heavy|long_source|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "kima 9تلkom rkhess men be3d wa7ed 3000 wla 10000 km tji 9anat nhar w b nesba kayen li haka.",
        "As I told you, it is cheap. After that, someone 3,000 or 10,000 kilometers below would make Nahar TV appear, and there are people like that. The comparison is unclear.",
        "말했듯이 그건 저급해. 그보다 3,000킬로미터나 10,000킬로미터 아래에 누군가가 있어도 나하르 채널이 나타날 정도라는 식의 비교인데, 정확한 뜻은 불분명해.",
        "B2", 69, "politics_public_affairs", "media_comparison", "speech", "opinion", "slang", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "ana wallah menz3ef parce que kayen ممثلين ma rahomch yekhdmou w ممثلين fachlin 7na se7abna n3arfouhom ma rahomch yekhdmou ga3 w allah menz3ef 3lihom.",
        "By God, I am upset because there are actors who are not working and actors who have failed. We know some of them personally; they are not working at all, and I am upset for them.",
        "맹세코 속상해. 일하지 못하는 배우들도 있고 실패한 배우들도 있기 때문이야. 우리는 그들 중 일부를 개인적으로 아는데 전혀 활동하지 못하고 있어. 그들이 안타까워.",
        "B2", 60, "entertainment_music", "actors_and_work", "speech", "opinion", "colloquial", "medium", "code_switching",
    ),
    item(
        "ma3lich ghera w ch7al men 7aja bsa7 kayen wa7din yel3bouha ne9ad kima wa7ed mathalan ysemouh Slim Agha hder ana w allah ma nchoufouch houwa li kteb l sa7afa electronique hadi basco houwa li yekteb f dok maw9e3 ta3 nhar donc Slim Agha cha3b dzayri ma ya3rfouch.",
        "Never mind—there is jealousy and a great deal of something unclear. But some people play the role of critics, such as someone called Slim Agha. I swear I do not think he wrote this electronic-press material, because he writes on those Nahar websites. So Slim Agha is an Algerian person whom he does not know; several links are unclear.",
        "괜찮아. 질투와 관련된 불분명한 말이 있어. 하지만 어떤 사람들은 비평가인 척하는데, 예를 들면 살림 아가라는 사람이 그래. 맹세코 나는 그가 이 전자 언론 자료를 썼다고는 생각하지 않아. 그는 나하르의 그런 웹사이트에 글을 쓰기 때문이야. 그래서 살림 아가는 그가 모르는 알제리 사람이라는 말인데, 연결 관계가 불분명해.",
        "C1", 86, "politics_public_affairs", "electronic_press_critique", "speech", "opinion", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "houwa kan baghi y3arfouh bsa7 ma y3arfouch karton w ma y3arfouch chouf kayen fchel men ba3d kayen wa7ed 6000 w 10000 klm ta7t men ba3d yji houwa donc hadou nas nechfe9 3lihom.",
        "He wanted them to know him, but no one knows him—the middle wording is unclear. Look, there is failure; then there is someone 6,000 or 10,000 km below, and afterward he comes. So these are people I feel sorry for; the comparison is unclear.",
        "그는 사람들이 자신을 알아주길 바랐지만 아무도 그를 모른다는 말인데, 중간 표현은 불분명해. 봐, 실패가 있고 그보다 6,000킬로미터나 10,000킬로미터 아래에 누군가가 있다가 그가 온다는 식이야. 그래서 이런 사람들이 안쓰럽다는 뜻인데 비교가 불분명해.",
        "C1", 83, "entertainment_music", "unknown_person_and_failure", "speech", "opinion", "slang", "high", "context_heavy|long_source|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "donc had l mosalsal Wlad Hlal mosalsal 7amdillah te3bna 3lih bezaf safi 6 chhor rana nekhdmou fih.",
        "So this series, Oulad El Halal—thank God, we worked very hard on it. That is all; we have been working on it for six months.",
        "그러니까 이 드라마 '울라드 할랄'은 다행히 우리가 정말 많이 애쓴 작품이야. 그게 전부고, 6개월 동안 이 작품을 작업하고 있어.",
        "B2", 57, "entertainment_music", "series_production_effort", "speech", "information", "mixed", "medium", "code_switching",
    ),
    item(
        "7na ma jatsh ghir haka mezya wla 6 chhor w 7na nekhdmou 9rib 16 sa3a f nhar si ba ghayan f scenario.",
        "It did not happen just like that; fortunately, we worked for six months and nearly 16 hours a day. The phrase 'si ba ghayan in the script' is unclear.",
        "그 일이 그냥 이루어진 건 아니야. 다행히 6개월 동안 하루에 거의 16시간씩 작업했어. '대본의 si ba ghayan'이라는 표현은 불분명해.",
        "C1", 79, "entertainment_music", "long_working_hours_and_script", "speech", "information", "mixed", "high", "code_switching|context_heavy|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "khedmna bezaf w 3yina w f tournage tani 3yina w te3bna rana nsawrou f nhar w lil 7tta youm kملنا 7tta 7 ta3 sbah khedmna ga3 l noui blonch.",
        "We worked a lot and became tired. We were also tired during filming, and we kept filming day and night until we finished at 7 in the morning. We worked all night without stopping.",
        "많이 일해서 지쳤고 촬영할 때도 지치고 힘들었어. 낮과 밤으로 계속 촬영해서 아침 7시가 되어서야 끝냈어. 밤새 쉬지 않고 전부 작업했지.",
        "B2", 62, "entertainment_music", "filming_schedule", "speech", "narration", "colloquial", "medium", "code_switching|long_source",
    ),
    item(
        "w 7amdillah neja7 rana nchoufou f chera3 f mdina Wahran.",
        "And thank God, we can see the success in the streets of the city of Oran.",
        "그리고 다행히 오랑시의 거리에서 그 성공을 볼 수 있어.",
        "B1", 42, "entertainment_music", "public_success_of_series", "speech", "opinion", "colloquial", "low", "code_switching",
    ),
    item(
        "w hadou nas li rahom yehdrou w y9oulou la Wahran w ga3 hadou nas baghyin tefr9a baghyin netfer9ou 9anat Nahar ma3roufa b machrou3 ta3ha te7was tefer9 b ga3 toro9.",
        "And these are the people who are speaking and saying 'no Oran.' All these people want division; they want us to be split up. Nahar TV is known for its project and is trying to divide people by every means.",
        "그리고 '오랑이 아니다'라고 말하는 사람들이 있어. 이 사람들은 모두 분열을 원하고 우리를 갈라놓으려 해. 나하르 채널은 자기 프로젝트로 알려져 있고 온갖 방법으로 분열시키려 한다는 말이야.",
        "C1", 76, "politics_public_affairs", "regional_identity_and_division", "speech", "complaint", "offensive", "high", "context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "Wahran mdina dzayriya kima tsawer f Wahran te9der tsawer f Bejaia f Chelf kima te9der tsawer f Constantine Bel Abbes.",
        "Oran is an Algerian city. Just as you can film in Oran, you can film in Bejaia, Chlef, Constantine, or Sidi Bel Abbes.",
        "오랑은 알제리의 도시야. 오랑에서 촬영할 수 있는 것처럼 베자이아, 슐레프, 콘스탄틴, 시디 벨 아베스에서도 촬영할 수 있어.",
        "B1", 45, "entertainment_music", "filming_locations_and_identity", "speech", "opinion", "neutral", "low", "code_switching",
    ),
    item(
        "manash f hada l mostawa donc had l mosalsal la9a neja7 basco fih se9d kbir w fih te3b kbir w ma hdarnash b filtre 7na ma nehderouch b filtre.",
        "We are not at that level. This series found success because it contains great sincerity and great effort; we did not speak through a filter—we do not speak through a filter.",
        "우리는 그런 수준의 사람이 아니야. 이 드라마가 성공한 것은 큰 진정성과 노력이 담겼기 때문이야. 우리는 필터를 거쳐 말하지 않았고 지금도 그렇게 말하지 않아.",
        "B2", 59, "entertainment_music", "authenticity_and_success", "speech", "opinion", "colloquial", "medium", "code_switching",
    ),
    item(
        "5ater fannan lazm يكون sadi9 m3a l mejtama3 ta3ou donc merci 7na rana kol youm ghodwa mam youm f lil ghadi nkounou f blas d arm netmena men public ta3na yerdo hadou li rahom yehdrou b sm Wahran.",
        "Because an artist must be honest with his community. So thank you. Tomorrow night we will also be at Place d'Armes, as we are every day. I hope our public responds to those who are speaking in Oran's name; the schedule wording is unclear.",
        "예술가는 자신의 공동체에 정직해야 해. 고마워. 우리는 매일 그렇듯 내일 밤에도 아르메 광장에 있을 거야. 우리 관객이 오랑의 이름으로 말하는 사람들에게 반응해 주길 바라. 일정에 관한 표현은 불분명해.",
        "C1", 80, "entertainment_music", "artist_authenticity_and_public_response", "speech", "wish", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "ntouma tani 9al ana rani netferrej f Wlad Hlal zkara f 9anat Nahar yghamou ofendou compte basco hadou tesrafat ma ye9derch ydirhom mowaten nzi7 ydirhom ghir mowaten li deretou ta3ou deret ta3 wa7ed 7arki.",
        "You too—I said that I am watching Oulad El Halal as a provocation to Nahar TV. The middle expression is unclear, but these actions cannot be done by an honest citizen; they can only be done by a citizen whose conduct is that of a harki, a term used here as an accusation.",
        "너희도 마찬가지야. 나는 나하르 채널에 대한 도발로 '울라드 할랄'을 보고 있다고 말했어. 중간 표현은 불분명하지만 이런 행동은 정직한 시민이 할 수 없고, 오직 '하르키' 같은 행동을 하는 시민만 할 수 있다는 비난이야.",
        "C1", 88, "politics_public_affairs", "political_accusation_and_series", "speech", "complaint", "offensive", "high", "code_switching|context_heavy|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "ma te9dertch tkoun w ana ma nekhdemsh m3akom ya 9anat Nahar w allah l3adim lokan nmout bcher hedرتou m3aya w rseltouli m3a jmaatkom w 9oltouli arwa7 ma3lich w had l hedra nروح n9oulha f 9anat ta3na arwa7 te9der teنتقدna f 9anat ta3na ana ma nefoutsh f 9anat ta3kom.",
        "I do not think that is possible, and I do not work with you, Nahar TV. By God, if I were to die, you spoke with me, sent your group to me, and told me to come. I will say this on our channel: come, you can criticize us on our channel; I will not go on your channel. Some wording is unclear.",
        "그럴 수는 없다고 생각해. 나는 너희 나하르 채널과 함께 일하지 않아. 맹세코 내가 죽더라도 너희는 나에게 말을 걸고 너희 사람들을 보내 와서 오라고 했잖아. 이 말은 우리 채널에서 할게. 와서 우리 채널에서 우리를 비판해도 돼. 나는 너희 채널에는 나가지 않을 거야. 일부 표현은 불분명해.",
        "C1", 84, "politics_public_affairs", "media_channel_dispute", "speech", "disagreement", "offensive", "high", "code_switching|context_heavy|long_source|source_ambiguity", "flagged",
    ),
    item(
        "w les pages li kanou ysebbouni men 9bel belli dيت 135 milliard w kent did 7irak houma nafs homa pages rahom yehajmou f Wlad Hlal.",
        "The pages that used to insult me, saying that I had taken 135 billion and was against the Hirak, are the same pages now attacking Oulad El Halal.",
        "예전에 내가 1,350억을 가져갔고 히라크에 반대한다고 욕하던 페이지들이 지금은 '울라드 할랄'을 공격하는 바로 그 페이지들이야.",
        "C1", 73, "politics_public_affairs", "online_accusations_and_series_attack", "speech", "complaint", "offensive", "high", "code_switching|context_heavy|long_source",
    ),
    item(
        "basco Wlad Hlal machrou3 naje7 b fadl ga3 nass w fih koubba men mmatlin ray 3in mmatlin top w harbin nivo tal3.",
        "Because Oulad El Halal is a successful project thanks to everyone, and it has a constellation of actors. In my view, they are top actors with a high level.",
        "'울라드 할랄'은 모두의 덕분에 성공한 프로젝트이고 배우들이 훌륭하게 모인 작품이기 때문이야. 내 눈에는 모두 수준이 높은 최고의 배우들이야.",
        "B2", 57, "entertainment_music", "series_cast_and_success", "speech", "opinion", "colloquial", "medium", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "kayen mokhraj khedem m3a mmatlin bezaf w ya3tih esa7a w kayen charika intaj amnet b machrou3 donc machrou3 naje7.",
        "There is a director who worked with many actors—credit to him—and there is a production company that believed in the project. So it is a successful project.",
        "많은 배우와 함께 작업한 감독이 있고 그에게 감사할 만해. 또 이 프로젝트를 믿어 준 제작사가 있어. 그래서 성공한 프로젝트야.",
        "B2", 54, "entertainment_music", "director_and_production_company", "speech", "opinion", "neutral", "medium", "code_switching",
    ),
    item(
        "7na ghadi f lil nkounou ana w s7abi nkounou f Wahran nkounou f blas d arm bdat mor tarawih rana nrou7ou n9asrou tema w ga3 w lli y7eb yji ychoufna mar7ba bih.",
        "Tonight my friends and I will be in Oran, at Place d'Armes. After the tarawih prayer, we will go there to hang out, and anyone who wants to come see us is welcome.",
        "오늘 밤 나와 친구들은 오랑의 아르메 광장에 있을 거야. 타라위 기도 후에 그곳에 가서 함께 시간을 보낼 테니, 우리를 보러 오고 싶은 사람은 누구든 환영해.",
        "B1", 49, "entertainment_music", "public_meeting_invitation", "speech", "suggestion", "colloquial", "medium", "code_switching|idiom_culture",
    ),
    item(
        "ghadi nkoun ana w Zino w Mustapha La3ribi w Khesani w ga3 l equipe ta3na tani Amine Babylon ghadi nkounou tema lli y7eb yji 3andna mar7ba bih w lli marahch did Wlad Hlal yji ychoufna.",
        "I will be there with Zino, Mustapha La3ribi, Khesani, and our whole team; Amine Babylon will also be there. Anyone who wants to come is welcome, and anyone who is not against Oulad El Halal can come see us.",
        "나는 지노, 무스타파 라아리비, 크사니, 우리 팀 전원과 함께 그곳에 있을 거야. 아민 바빌론도 올 거야. 오고 싶은 사람은 환영하고, '울라드 할랄'에 반대하지 않는 사람은 우리를 보러 와도 돼.",
        "B1", 51, "entertainment_music", "cast_meetup_invitation", "speech", "suggestion", "colloquial", "medium", "code_switching|idiom_culture",
    ),
    item(
        "donc merci bou sa7a ramdankom w nzid kima 9olt had l 9anat tebghi fchel w ma tebghich neja7.",
        "So thank you, and Ramadan greetings. I will add, as I said, that this channel wants failure and does not want success.",
        "그러니 고마워. 라마단을 잘 보내. 내가 말했듯이 이 채널은 실패를 원하고 성공은 원하지 않는다고 덧붙일게.",
        "B2", 58, "politics_public_affairs", "media_criticism", "speech", "complaint", "mixed", "medium", "code_switching|idiom_culture",
    ),
    item(
        "hadi tent3ad men 9anawat a3da2 neja7 w nizam fachel ma ysewe9ch l neja7 donc barak allah fikom w tsoumou b se7a w ha inchallah.",
        "This is counted among the channels that are enemies of success, and a failed system does not care about success. So thank you, may God bless you, and may you fast in good health, God willing.",
        "이 채널은 성공의 적인 채널들 가운데 하나로 여겨지고, 실패한 체제는 성공을 중요하게 여기지 않아. 고마워. 하나님의 축복이 있기를, 건강하게 금식하길 바라. 하나님의 뜻이라면.",
        "B2", 64, "politics_public_affairs", "media_criticism_and_ramadan_greeting", "speech", "thanks", "mixed", "medium", "code_switching|idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "wi Houari same7li 3la retard.",
        "Yes, Houari, forgive me for being late.",
        "응, 후아리, 늦어서 미안해.",
        "A1", 25, "daily_life", "apology_for_delay", "conversation", "apology", "casual", "low", "",
    ),
    item(
        "ma tet9al9ich makanesh mouchkil.",
        "Don't worry; there is no problem.",
        "걱정하지 마. 문제없어.",
        "A1", 18, "daily_life", "reassurance", "conversation", "answer", "casual", "low", "",
    ),
    item(
        "7allab.",
        "A milkman.",
        "우유 배달원.",
        "A1", 15, "work", "occupation_word", "conversation", "answer", "colloquial", "medium", "",
    ),
    item(
        "sa7it.",
        "Thanks.",
        "고마워.",
        "A1", 12, "daily_life", "thanks", "conversation", "thanks", "casual", "low", "",
    ),
    item(
        "khalli ana nkhalles.",
        "Let me pay.",
        "내가 계산할게.",
        "A1", 20, "shopping", "offering_to_pay", "conversation", "request", "casual", "low", "",
    ),
    item(
        "oh sa7it.",
        "Oh, thanks.",
        "아, 고마워.",
        "A1", 14, "daily_life", "thanks", "conversation", "thanks", "casual", "low", "",
    ),
    item(
        "fout wa9t chbab m3ak w medabia n3awdou netla9aw.",
        "Time passed nicely with you, and I would like us to meet again.",
        "너와 즐거운 시간을 보냈어. 우리 다시 만나면 좋겠어.",
        "B1", 36, "social_media", "parting_and_future_meeting", "conversation", "wish", "casual", "medium", "",
    ),
    item(
        "ana tani. n3ayetlek yak aya bye bye.",
        "Me too. I will call you, okay? Bye-bye.",
        "나도. 내가 전화할게, 알겠지? 잘 가.",
        "A2", 28, "social_media", "parting_and_call", "conversation", "suggestion", "casual", "low", "",
    ),
    item(
        "aya kifach fatet.",
        "So, how did it go?",
        "그래, 어떻게 됐어?",
        "A1", 18, "daily_life", "asking_how_it_went", "conversation", "question", "casual", "low", "",
    ),
    item(
        "bezaf 7nin bezaf ناس mلاح mi ma chekitsh n3awdou netchoufou.",
        "Very kind—so many good people. I did not think we would see each other again.",
        "정말 다정하고 좋은 사람들이 많아. 우리가 다시 보게 될 줄은 몰랐어.",
        "B1", 41, "social_media", "positive_social_reunion", "conversation", "opinion", "casual", "medium", "source_ambiguity", "flagged",
    ),
    item(
        "safa 45 d9i9a ta3 retard bdit net9al9.",
        "Enough—45 minutes late; I started to worry.",
        "됐어. 45분이나 늦어서 걱정되기 시작했어.",
        "A2", 29, "daily_life", "complaint_about_delay", "conversation", "complaint", "casual", "low", "",
    ),
    item(
        "chouia kont nehder m3a sa7bi.",
        "Nothing; I was talking with my friend.",
        "아무것도 아니야. 친구와 이야기하고 있었어.",
        "A1", 18, "social_media", "explaining_a_pause", "conversation", "answer", "casual", "low", "",
    ),
    item(
        "wi sa7bi aya nrou7ou naklou rani met b jou3. wi ma nsitkesh netla9aw 3and hadak l 9نت 3la zouj.",
        "Yes, my friend. Let's go eat; I am starving. Yes, I have not forgotten you—we will meet at that place at two.",
        "응, 친구야. 우리 먹으러 가자. 배고파 죽겠어. 너를 잊지 않았어. 두 시에 그 장소에서 만나자.",
        "A2", 35, "food", "arranging_a_meal", "conversation", "suggestion", "casual", "medium", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "wi ya wdi hada sa7bek mehboul ma tesma3louch. ghir khallsi ma jbtsh drahem m3aya.",
        "Yes, my friend, this friend of yours is crazy; do not listen to him. Just pay—I did not bring money with me.",
        "그래, 이 친구야. 네 친구는 미쳤으니 그의 말을 듣지 마. 그냥 계산해 줘. 나는 돈을 가져오지 않았어.",
        "A2", 34, "social_media", "friend_warning_and_payment", "conversation", "warning", "casual", "medium", "",
    ),
    item(
        "la kho rani m3ak f telephone ma rani ndir walo.",
        "No, brother, I am with you on the phone; I am not doing anything.",
        "아니, 친구야. 전화로 너와 함께 있고 아무것도 하지 않고 있어.",
        "A2", 27, "social_media", "phone_conversation", "conversation", "answer", "casual", "medium", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "rani nakol b 3in. Souhila ma teza3fich rani n9asser m3ah sa7bi bark. bon ana rayeh ok salam.",
        "I am eating with my eyes. Souhila, do not be upset; I am just joking around with my friend. Well, I am leaving, okay? Goodbye.",
        "나는 눈으로 먹고 있어. 수헤일라, 화내지 마. 친구와 그냥 장난치는 것뿐이야. 그럼 나는 갈게, 알겠지? 잘 가.",
        "B1", 48, "social_media", "teasing_and_reassurance", "conversation", "apology", "casual", "medium", "code_switching|context_heavy|source_ambiguity", "flagged",
    ),
    item(
        "aya ki fatet.",
        "So, how did it go?",
        "그래, 어떻게 됐어?",
        "A1", 16, "daily_life", "asking_how_it_went", "conversation", "question", "casual", "low", "",
    ),
    item(
        "ghamed, rejla, ma ye7lebsh. l9it rajel 7yati.",
        "Mysterious, manly, and he does not drink milk. I found the man of my life. The first descriptors are unclear in the source.",
        "신비롭고 남자답고 우유를 마시지 않아. 내 인생의 남자를 찾았어. 앞의 묘사 표현은 원문에서 불분명해.",
        "B2", 60, "family_relationships", "romantic_partner_description", "conversation", "description", "colloquial", "high", "context_heavy|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "ya 3omri had l 3am ta3ek. testaheli.",
        "My dear, this is your year. You deserve it.",
        "내 사랑, 올해는 네 해인 거야. 너는 그럴 자격이 있어.",
        "A2", 26, "family_relationships", "romantic_encouragement", "conversation", "wish", "colloquial", "low", "idiom_culture",
    ),
    item(
        "3reft wa7ed bezaf chbab f Instagram. chouf haja wa7da daymen yehder f telephone m3a sa7bou aya tfakرت li kanet m3ah tani yehder f telephone hadi hiya 7ala li ykhalleط khallit li yebghiha w yethalla fiha w راحت تجري mor li ma dayrhash fiha.",
        "I met a very handsome man on Instagram. One thing: he was always talking on the phone with his friend, and then I remembered that she was also with him, talking on the phone. This is the kind of situation that gets confused: I left the woman he loved and cared for, and she ran after the one who did not care about her. The references are unclear.",
        "인스타그램에서 아주 잘생긴 남자를 알게 됐어. 한 가지는 그가 늘 친구와 전화로 이야기했다는 거야. 그러다 그와 함께 있던 그녀도 전화하고 있었다는 걸 기억했어. 이런 상황은 뒤엉키기 쉬워. 나는 그가 사랑하고 돌보던 여자를 떠났고, 그녀는 자신을 돌보지 않던 사람을 쫓아갔어. 지시 대상이 불분명해.",
        "C1", 87, "family_relationships", "romantic_relationship_confusion", "narrative", "narration", "colloquial", "high", "code_switching|context_heavy|long_source|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "ch7al bakat ki chafthou m3a wa7ed okhra w temnat لو kan 9a3det m3a louwel gherha fani w material sbou rsa abri two l7ob houwa l ihtimam i7ترام w l7ob w aktar 7aja i7ترام.",
        "How much she cried when she saw him with another woman, and she wished she had stayed with the first one. The remaining wording is corrupted and unclear. Love is care, respect, and love; the most important thing is respect.",
        "그녀는 그가 다른 여자와 함께 있는 것을 보고 많이 울었고, 첫 번째 사람과 계속 있었더라면 좋겠다고 바랐어. 나머지 표현은 손상되어 불분명해. 사랑은 관심과 존중이고, 사랑에서 가장 중요한 것은 존중이야.",
        "C1", 90, "family_relationships", "love_care_and_respect", "narrative", "opinion", "mixed", "high", "code_switching|context_heavy|long_source|source_ambiguity|source_corruption", "flagged",
    ),
    item(
        "w nowsi ma tdiroush kifi w kounou m3a wa7ed li ysebe9 li yebghiha 9blou houwa w inchallah dertou 3ebra.",
        "And I advise you not to do as I did. Be with someone who loved her before you did; I hope you have learned a lesson.",
        "그리고 나처럼 하지 말라고 조언할게. 네가 사랑하기 전에 이미 그녀를 사랑했던 사람과 함께해. 하나님의 뜻이라면 너희가 교훈을 얻었기를 바라.",
        "B2", 59, "family_relationships", "relationship_advice", "speech", "suggestion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "ya ma. chahsek ya weldi.",
        "Oh mother. What is wrong, my son? The exact wording is unclear.",
        "어머니. 무슨 일이니, 얘야? 정확한 표현은 불분명해.",
        "A2", 38, "family_relationships", "parent_child_address", "conversation", "question", "colloquial", "high", "source_ambiguity", "flagged",
    ),
    item(
        "rani baghi netzewwej. la 7mouk la. bsa7 3lah. sa7a nezewjek bent khaltk. ma netzewjehash. bent khalti tetchebeh l Jilali choufili wa7da tkoun chaba.",
        "I want to get married. No, your uncle does not agree. But why? Fine, I will marry you to your aunt's daughter. I will not marry her; my cousin resembles Jilali. Find me someone who is young and attractive.",
        "나 결혼하고 싶어. 안 돼, 네 삼촌이 동의하지 않아. 하지만 왜? 좋아, 네 이모 딸과 결혼시켜 줄게. 그 여자와는 결혼하지 않을 거야. 내 사촌은 질랄리와 닮았어. 젊고 예쁜 사람을 찾아 줘.",
        "B1", 51, "family_relationships", "marriage_partner_negotiation", "conversation", "refusal", "colloquial", "medium", "code_switching|source_ambiguity", "flagged",
    ),
    item(
        "ya weldi ghadi nekhtablek wa7da chaba bezaf. aya trou7 m3aya nekhtablek. aya nrou7ou.",
        "My son, I will propose a very beautiful young woman for you. Come with me and I will propose to her for you. Come on, let's go.",
        "얘야, 아주 예쁜 젊은 여자를 찾아 청혼해 줄게. 나와 함께 가자. 내가 너를 대신해 청혼할게. 자, 가자.",
        "A2", 36, "family_relationships", "arranging_a_marriage", "conversation", "suggestion", "colloquial", "low", "",
    ),
    item(
        "salam 3likom. w 3likom salam.",
        "Peace be upon you. And peace be upon you too.",
        "안녕하세요. 안녕하세요.",
        "A1", 12, "family_relationships", "greeting", "conversation", "greeting", "neutral", "low", "idiom_culture",
    ),
    item(
        "jinaكم b l7seb w nseb bah nekhtbou bentkom bsa7 kayen chourout w chwala hadou chourout.",
        "We have come to you with our family standing and lineage to ask for your daughter in marriage. But there are conditions. What are these conditions?",
        "우리의 가문과 혈통을 갖추고 따님에게 청혼하러 왔습니다. 하지만 조건이 있습니다. 어떤 조건인가요?",
        "B1", 47, "family_relationships", "marriage_proposal_conditions", "conversation", "request", "neutral", "medium", "idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "mehr ta3ha 50 milyon w te3touna 20 milyon. tzid te3ti l khouha 30 milyon 5ater ma rahesh khadem w zid techri laha 80 milyon ta3 dhahab w tzid sekna w loto.",
        "Her bride price is 50 million, and you will give us 20 million. You must also give her brother 30 million because he is not working, buy her 80 million worth of gold, and add a home and a car.",
        "그녀의 마흐르는 5천만이고 우리에게 2천만을 줘. 게다가 그녀의 오빠에게는 일하지 않으니 3천만을 주고, 금 8천만어치를 사 주고, 집과 자동차도 마련해 줘.",
        "B2", 63, "finance", "marriage_dowry_demands", "conversation", "request", "neutral", "medium", "code_switching|idiom_culture|source_ambiguity", "flagged",
    ),
    item(
        "ba3d sa3a men chourout. ya ana zawali w 9lil ma 3andish menin baghi njib drahem. rou7 w khdem w jiblna drahem wla ma n3touksh bentna. nrou7 nekhdem w ki nlem drahem netzewwej bentkom. ok.",
        "An hour after hearing the conditions: I am poor and have little; where am I supposed to get the money? Go work and bring us money, or we will not give you our daughter. I will go work, and when I collect the money I will marry your daughter. Okay.",
        "조건을 들은 지 한 시간 후. 나는 가난하고 가진 것이 거의 없는데 돈을 어디서 구하라는 거야? 가서 일하고 돈을 가져와. 그렇지 않으면 우리 딸을 주지 않을 거야. 일하러 가서 돈을 모으면 당신들 딸과 결혼할게. 좋아.",
        "B2", 68, "family_relationships", "marriage_negotiation_and_money", "conversation", "agreement", "colloquial", "medium", "idiom_culture|long_source",
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
            if not value or value != value.strip() or any(ord(char) in {9, 10, 13} for char in value):
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
