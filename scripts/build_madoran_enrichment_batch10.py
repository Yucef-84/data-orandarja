"""Build source-only MADOran enrichment Batch 10 for Sentno 577..640."""
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

from scripts.apply_madoran_enrichment_batch06 import CEFR_LEVELS, CONTROLLED_VALUES
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
    PROCESSING_FLAG_VALUES,
    ROOT,
    SOURCE_OUT,
    read_tsv,
    source_gate,
)
from scripts.validate_madoran_enrichment import check_layer_contract

BATCH_ID = "MADORAN-ENRICH-010"
BASE_COMMIT = "647fd84"
PROMPT_VERSION = "madoran-source-enrichment-v10"
TARGET_START = 577
TARGET_END = 640
BATCH_DIR = ROOT / "data/master/enrichment/batches"
BATCH_OUT = BATCH_DIR / "batch10_sentno_0577_0640.tsv"
MANIFEST_OUT = BATCH_DIR / "batch10_manifest.json"
QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_generation_qa.json"
BATCH_FIELDS = ["source_uid", "sentno", *EMPTY_FIELDS, "processing_flags", "enrichment_state"]


def item(english, korean, cefr, score, domain, topic, genre, speech, register, context, flags="", state="draft"):
    return {
        "english": english,
        "korean": korean,
        "cefr_level": cefr,
        "difficulty_score": str(score),
        "domain": domain,
        "topic": topic,
        "genre": genre,
        "speech_act": speech,
        "register": register,
        "context_dependency": context,
        "processing_flags": flags,
        "enrichment_state": state,
    }


def latinize(text):
    table = str.maketrans({
        "ا": "a", "أ": "a", "إ": "i", "آ": "a", "ء": "'", "ب": "b", "ت": "t", "ث": "th",
        "ج": "j", "ح": "7", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r", "ز": "z", "س": "s",
        "ش": "sh", "ص": "s", "ض": "d", "ط": "t", "ظ": "z", "ع": "3", "غ": "gh", "ف": "f",
        "ق": "9", "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w", "ي": "i",
        "ى": "a", "ة": "a", "ئ": "i", "ؤ": "w", "،": ",", "؟": "?",
    })
    return " ".join("".join(ch if ord(ch) < 128 else " " for ch in text.translate(table)).split())


RAW = {
    577: item("It is important to see whether you are the family of a groom or a bride, so I want to dress formally for your family: with gold embroidery, a decorated piece, or an outfit that looks Arab and presentable.", "신랑 가족인지 신부 가족인지에 따라 달라요. 그래서 여러분 가족 행사에는 금장식이나 장식된 옷처럼 아랍식이고 단정한 정장을 입고 싶어요.", "C1", 78, "family_relationships", "formal_wedding_attire_for_family", "conversation", "opinion", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    578: item("After we finish the procession and dinner, I want to wear another outfit for the evening; we will call it a robe de soirée.", "행렬과 저녁 식사를 마친 뒤에는 저녁용 옷을 입고 싶어요. 그것을 ‘robe de soirée’라고 부를게요.", "B2", 54, "family_relationships", "evening_gown_after_wedding_dinner", "conversation", "suggestion", "mixed", "high", "code_switching|source_ambiguity", "flagged"),
    579: item("For a stylish look, choose something beautiful and coordinated, perhaps with a little elegance because the dancing and the DJ are starting; your makeup should be good, and you should look young, presentable, and beautiful.", "멋을 내고 싶다면 아름답고 잘 어울리는 옷을 골라요. 춤과 디제이 공연이 시작되니 조금 우아한 느낌도 좋고, 화장도 잘해서 젊고 단정하고 예뻐 보이면 돼요.", "C1", 72, "family_relationships", "stylish_wedding_appearance", "conversation", "suggestion", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    580: item("When the end of the wedding is approaching and you are tired, sweaty, or thirsty, wear something simple; do not wear jeans when you are worn out.", "결혼식이 끝나 갈 때 지치고 땀나고 목마르면 간단한 옷을 입어요. 아주 피곤할 때는 청바지를 입지 말아요.", "B2", 58, "family_relationships", "comfortable_clothing_late_in_wedding", "conversation", "suggestion", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    581: item("Is there a proverb that you always go around with?", "늘 마음에 두고 다니는 속담이 있나요?", "A2", 24, "culture_tradition", "question_about_favorite_proverb", "interview", "question", "neutral", "low"),
    582: item("Well, I will tell you a proverb. I do not know many, but when I wanted to film this video I read one and thought, ‘That is my life, just like this.’", "글쎄요, 속담 하나를 말해 볼게요. 많이 알지는 못하지만 이 영상을 찍으려다가 하나를 읽고 ‘이게 바로 내 삶이야’라고 생각했어요.", "B2", 58, "culture_tradition", "proverb_identified_with_personally", "conversation", "opinion", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    583: item("The days are diminishing from my lifetime, and I am counting them. That means we should stop worrying about the future that is coming and live our life from now on.", "내 수명에서 날들이 줄어들고 있는데 나는 그날들을 세고 있어요. 그러니 다가올 미래를 걱정하는 일을 멈추고 지금부터 우리 삶을 살아야 해요.", "B2", 54, "culture_tradition", "living_in_the_present", "speech", "opinion", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    584: item("Our life can stop at any time, so we should enjoy it now and live it fully instead of lying around depressed and watching television; we have to live our life.", "우리 삶은 언제든 멈출 수 있으니 지금 즐기고 온전히 살아야 해요. 누워서 우울해하거나 텔레비전만 보지 말고 삶을 살아야 해요.", "B2", 52, "culture_tradition", "enjoying_life_now", "speech", "suggestion", "mixed", "high", "code_switching|idiom_culture|long_source|source_ambiguity", "flagged"),
    585: item("Is there one more thing that is not found in Algeria, something you would like to exist there?", "알제리에는 없지만 그곳에 있었으면 하는 것이 또 있나요?", "A2", 28, "travel", "question_about_missing_feature_in_algeria", "interview", "question", "neutral", "low"),
    586: item("I am going to talk only about Oran. In this city there are many things to do: first, there are certain norms in Algeria, especially in Oran, and then many other things.", "오랑에 대해서만 이야기할게요. 이 도시에는 할 일이 많아요. 먼저 알제리, 특히 오랑에는 지켜지는 규범이 있고 그 밖에도 많은 것이 있어요.", "C1", 70, "culture_tradition", "social_norms_and_life_in_oran", "speech", "description", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    587: item("The streets are dirty, but they are not a jungle; they are dirty in a way that has gone too far. Some of the wording is unclear.", "거리는 더럽지만 정글은 아니에요. 너무 심하게 더러워진 상태라는 말이에요. 일부 표현은 불분명해요.", "B2", 62, "daily_life", "criticism_of_dirty_streets", "conversation", "opinion", "slang", "high", "source_ambiguity", "flagged"),
    588: item("We are not just putting on an act: we like a fight, but there is a way of life I would die for and I do not want it to change in Algeria—especially the women of Oran. Much of the wording is unclear.", "우리는 단순히 쇼를 하는 게 아니에요. 싸움을 좋아하기도 하지만, 알제리에서 내가 목숨을 걸 만큼 사랑하고 변하지 않기를 바라는 삶이 있어요. 특히 오랑 여성들이 그래요. 많은 표현이 불분명해요.", "C1", 82, "culture_tradition", "oran_identity_and_gendered_social_commentary", "speech", "opinion", "slang", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    589: item("A genuine Oran woman is already dressed for you. Some wear black, grey, yellow, or other colored jilbabs; the clothing itself is being described.", "진짜 오랑 여성은 이미 옷차림을 갖추고 있어요. 어떤 사람은 검은색, 회색, 노란색 등 여러 색의 질밥을 입어요. 옷차림을 설명하는 말이에요.", "B2", 58, "culture_tradition", "oran_womens_clothing", "speech", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    590: item("An Oran woman may be a little full-figured, but if you fall for an Oran woman, your day is over and your life is ruined. This is an exaggerated social joke, not a literal prediction.", "오랑 여성은 조금 통통할 수도 있지만, 오랑 여성에게 빠지면 하루가 끝나고 인생이 망한다는 식으로 과장해서 말해요. 문자 그대로의 예언이 아니라 사회적 농담이에요.", "C1", 74, "culture_tradition", "exaggerated_warning_about_romance", "joke", "warning", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    591: item("Let me explain why: you are dressed in a flashy or attention-catching way, but it is normal here; the rest of the appearance description is unclear.", "왜 그런지 설명해 줄게요. 당신은 눈에 띄는 방식으로 옷을 입었지만 여기서는 평범한 일이에요. 나머지 외모 묘사는 불분명해요.", "B2", 64, "culture_tradition", "appearance_and_local_norms", "conversation", "description", "slang", "high", "source_ambiguity", "flagged"),
    592: item("When she catches your eye, you see her pass in front of you normally; this scene is being compared with life in France, and some details are unclear.", "그녀가 눈에 들어오면 당신 앞을 자연스럽게 지나가는 모습이 보여요. 이 장면을 프랑스에서의 생활과 비교하는 듯하며 일부 세부 내용은 불분명해요.", "C1", 70, "culture_tradition", "comparing_oran_and_france_social_behavior", "conversation", "description", "mixed", "high", "code_switching|source_ambiguity", "flagged"),
    593: item("You can see that she is looking at you, but she pretends not to see you and acts as if she is blind in one eye; the wording is unclear.", "그녀가 당신을 보고 있다는 것을 알 수 있지만, 보지 못한 척하고 한쪽 눈이 먼 사람처럼 행동해요. 표현은 불분명해요.", "C1", 72, "culture_tradition", "indirect_gaze_and_social_teasing", "conversation", "description", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    594: item("Stop—she grabs your hand and puts an arm around you. You say, ‘What should I do with this face?’ and call for something beautiful; the physical comedy is partly unclear.", "잠깐, 그녀가 당신의 손을 잡고 팔을 두르네요. 당신은 ‘이 얼굴로 뭘 해야 하지?’라고 하며 예쁜 것을 해 달라고 말해요. 신체적 코미디 장면의 일부는 불분명해요.", "C1", 82, "humor", "physical_comedy_and_appearance", "joke", "narration", "slang", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    595: item("Then she says something like, ‘Here, like my sister,’ when she can tell you are not interested; the speaker describes people as aggressive, and the exact exchange is unclear.", "그녀는 당신이 관심이 없다는 것을 알아채면 ‘자, 내 동생처럼’이라는 식으로 말해요. 화자는 사람들을 공격적이라고 표현하며 정확한 대화는 불분명해요.", "C1", 78, "culture_tradition", "teasing_and_social_judgment", "conversation", "opinion", "slang", "high", "source_ambiguity", "flagged"),
    596: item("Oran remains my country, my city, and my province; I would die for it, and there is a special breeze or atmosphere in Oran.", "오랑은 여전히 내 나라이고 내 도시이며 내 주예요. 나는 오랑을 위해 죽을 수도 있고, 오랑에는 특별한 바람과 분위기가 있어요.", "B1", 42, "culture_tradition", "pride_in_oran", "speech", "opinion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    597: item("If you are Algerian and want to do this tag, put it here in the comments, make a YouTube video, and send it to me on Instagram, Twitter, or Facebook.", "알제리 사람이고 이 태그를 하고 싶다면 여기 댓글에 남기고, 유튜브 영상을 만들어 인스타그램이나 트위터 또는 페이스북으로 보내 주세요.", "B1", 40, "social_media", "social_media_challenge_call_to_action", "social_media", "request", "colloquial", "low", "code_switching", "draft"),
    598: item("This was my first video; I hope you liked it. I will make more videos in Arabic. I finished the video in three languages and said thank you in French.", "이것은 제 첫 영상이었어요. 마음에 들었기를 바라요. 앞으로 아랍어로 영상을 더 만들게요. 세 언어로 영상을 마치고 프랑스어로 고맙다고 말했어요.", "B1", 44, "social_media", "multilingual_video_signoff", "social_media", "thanks", "mixed", "medium", "code_switching|source_ambiguity", "flagged"),
    599: item("Oran, keep your mind; Naima is a star, not Milan. Your children are connected with the Casbah; the lyric contains names and slang whose exact references are unclear.", "오랑아, 정신을 차려. 나이마는 스타이지 밀라노가 아니야. 너희 아이들은 카스바와 이어져 있어. 가사 속 이름과 속어의 정확한 지칭은 불분명해.", "C1", 82, "entertainment_music", "oran_rap_and_named_references", "song_lyric", "exclamation", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    600: item("Ask about us at the college: five girls, Bahja, Haddad, history, the return, and the podium. The line is a rap or song passage with several unclear names and references.", "우리 이야기를 대학에서 물어봐요. 다섯 명의 여자, 바흐자, 하다드, 역사, 돌아옴과 무대가 나와요. 여러 이름과 지칭이 불분명한 랩 또는 노래 구절이에요.", "C1", 84, "entertainment_music", "oran_rap_named_references", "song_lyric", "description", "slang", "high", "long_source|source_ambiguity", "flagged"),
    601: item("Oran is an independent state; Oran is a place where life becomes beautiful, and we are the capital. The line is boastful regional rhetoric in a lyric or chant.", "오랑은 독립된 국가이고, 오랑에서는 삶이 아름다워져요. 우리는 수도라는 식으로 말해요. 가사나 구호 속의 지역적 자부심을 과장해서 표현한 말이에요.", "C1", 76, "politics_public_affairs", "independent_oran_rhetoric", "song_lyric", "exclamation", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    602: item("Oran is a civilization with a great history; the rest of the praise of the city is partly unclear in the lyric.", "오랑은 위대한 역사를 지닌 문명이에요. 도시를 찬양하는 나머지 가사 일부는 불분명해요.", "B2", 58, "history", "oran_civilization_and_history", "song_lyric", "opinion", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    603: item("The administration is confused and has nothing to do with football; we have cut ties, we are champions, and we love Mouloudia. The line mixes public affairs, football, and lyric wordplay.", "행정은 엉망이고 축구와는 아무 상관이 없어요. 우리는 관계를 끊었고 챔피언이며 물루디아를 사랑한다는 식으로 말해요. 공공 문제와 축구, 가사 속 말장난이 섞여 있어요.", "C1", 86, "politics_public_affairs", "football_and_public_affairs_lyric", "song_lyric", "opinion", "slang", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    604: item("Go, Oran, in peace. I loved you, and now I will burn the heart that used to love you; this is a poetic farewell or reproach.", "가거라, 오랑아, 평안히. 나는 너를 사랑했지만 이제 너를 사랑하던 마음을 태우겠다는 말이에요. 시적인 작별 또는 원망이에요.", "B2", 58, "entertainment_music", "poetic_farewell_to_oran", "song_lyric", "wish", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    605: item("A prayer or invocation to the ancestors: I am afflicted, and whoever transgresses will be taken by it. The exact curse or blessing is unclear.", "조상들에게 드리는 기도 또는 축원이에요. 나는 괴로움을 겪고 있고, 넘어서는 사람은 그것에 붙잡힐 거라는 뜻처럼 들려요. 정확한 저주나 축원의 의미는 불분명해요.", "C1", 80, "culture_tradition", "ancestor_invocation_and_unclear_curse", "song_lyric", "warning", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    606: item("Yes, go, Oran. My invocation to the ancestors is afflicted or charged with trouble; this is a repeated poetic line and its exact wording is unclear.", "그래, 가거라 오랑아. 조상들에게 드리는 내 기도에는 괴로움이 서려 있어요. 반복되는 시적 구절이며 정확한 표현은 불분명해요.", "C1", 72, "culture_tradition", "repeated_ancestor_invocation", "song_lyric", "wish", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    607: item("Whoever transgresses will be taken by it; this line repeats the warning from the preceding lyric.", "넘어서는 사람은 그것에 붙잡힐 거라는 말이에요. 앞의 가사에 나온 경고를 반복하는 구절이에요.", "B2", 52, "culture_tradition", "repeated_lyric_warning", "song_lyric", "warning", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    608: item("In Oran there has been more trouble; the police are mentioned, and when night falls I become afraid for him. The lyric's key noun is unclear.", "오랑에서는 문제가 더 많아졌고 경찰이 언급돼요. 밤이 되면 그가 걱정되고 무서워진다는 말이에요. 가사의 핵심 명사는 불분명해요.", "C1", 78, "crime_safety", "nighttime_fear_and_police_in_oran", "song_lyric", "warning", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    609: item("Nonlexical vocalization; no lexical proposition is present in the source line.", "비언어적 발성입니다. 원문에는 어휘적 명제가 없습니다.", "A1", 18, "entertainment_music", "nonlexical_vocalization", "song_lyric", "exclamation", "colloquial", "high", "source_ambiguity", "flagged"),
    610: item("Even Hamri and Chicago are mentioned: there are bullets and police, and at night I am afraid. The lyric refers to dangerous places or scenes, but some wording is unclear.", "함리와 시카고도 언급돼요. 총알과 경찰이 나오고 밤에는 무서워한다는 내용이에요. 위험한 장소나 장면을 가리키는 가사지만 일부 표현은 불분명해요.", "C1", 82, "crime_safety", "dangerous_night_scene_in_oran", "song_lyric", "warning", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    611: item("Nonlexical vocalization; the line functions as a musical refrain rather than a lexical sentence.", "비언어적 발성입니다. 어휘 문장이라기보다 음악적 후렴으로 기능합니다.", "A1", 18, "entertainment_music", "nonlexical_musical_refrain", "song_lyric", "exclamation", "colloquial", "high", "source_ambiguity", "flagged"),
    612: item("How much I love you, girl. The jiba and the bag are mentioned, and your arm moves like a doll; this is a playful lyric description.", "너를 얼마나 사랑하는지 몰라, 아가씨. 지바와 가방이 나오고 네 팔이 인형처럼 움직인다는 장난스러운 가사예요.", "B2", 66, "entertainment_music", "playful_description_of_a_girl", "song_lyric", "opinion", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    613: item("Nonlexical vocalization; no stable lexical meaning can be recovered from the recorded refrain.", "비언어적 발성입니다. 녹음된 후렴에서 안정적인 어휘 의미를 복원할 수 없습니다.", "A1", 18, "entertainment_music", "nonlexical_vocalization", "song_lyric", "exclamation", "colloquial", "high", "source_ambiguity", "flagged"),
    614: item("Nonlexical vocalization; the source line is a musical sound rather than a complete lexical utterance.", "비언어적 발성입니다. 원문은 완전한 어휘 발화가 아니라 음악적 소리입니다.", "A1", 18, "entertainment_music", "nonlexical_musical_refrain", "song_lyric", "exclamation", "colloquial", "high", "source_ambiguity", "flagged"),
    615: item("Nonlexical vocalization; no additional lexical content is identifiable in this short refrain.", "비언어적 발성입니다. 이 짧은 후렴에서 추가적인 어휘 내용은 식별되지 않습니다.", "A1", 18, "entertainment_music", "nonlexical_vocalization", "song_lyric", "exclamation", "colloquial", "high", "source_ambiguity", "flagged"),
    616: item("Nonlexical vocalization; the repeated sound belongs to the song performance and is not translated as a sentence.", "비언어적 발성입니다. 반복되는 소리는 노래 공연에 속하며 문장으로 번역하지 않습니다.", "A1", 18, "entertainment_music", "nonlexical_song_refrain", "song_lyric", "exclamation", "colloquial", "high", "source_ambiguity", "flagged"),
    617: item("Come, let us take a tour of beautiful Oran: Ahmed Zabana and other landmarks are part of the route.", "아름다운 오랑을 둘러보러 가요. 아흐메드 자바나와 다른 명소들이 이 여정에 포함돼요.", "B1", 44, "travel", "tour_of_oran_landmarks", "speech", "suggestion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    618: item("Larbi Ben M'hidi is also named as part of the tour or historical remembrance of Oran.", "라르비 벤 므히디도 오랑 여행이나 역사적 기억의 일부로 언급돼요.", "B1", 42, "history", "oran_historical_figure_larbi_ben_mhidi", "speech", "information", "neutral", "medium", "source_ambiguity", "flagged"),
    619: item("May God have mercy on them. Bab Rayan and poets are mentioned in a remembrance of people and places connected with Oran.", "하느님께서 그들에게 자비를 베푸시기를 바라요. 바브 라이안과 시인들이 오랑과 관련된 사람과 장소를 기억하는 말 속에 언급돼요.", "B2", 54, "history", "remembrance_of_oran_people_and_places", "speech", "wish", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    620: item("Wahbi, Belaoui, Ahmed Saber, and Ben Zerga are named; there are drums, zorna, and qraqeb instruments in the musical history being described.", "와흐비, 블라위, 아흐메드 사베르, 벤 제르카가 언급돼요. 설명되는 음악사에는 북과 조르나, 그라게브 악기가 나와요.", "C1", 70, "entertainment_music", "oran_musicians_and_instruments", "speech", "information", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    621: item("Gather old and young men and women from Oran, with rai music; the line calls for a shared musical gathering.", "오랑의 나이 든 사람과 젊은이, 여성과 남성을 모두 모아 라이 음악을 함께하자는 말이에요.", "B1", 46, "entertainment_music", "oran_rai_gathering", "song_lyric", "suggestion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    622: item("Sidi Houari and Sidi Hosni are named among Oran's local places or figures; the surrounding lyric is partly unclear.", "시디 후아리와 시디 호스니가 오랑의 지역 장소나 인물로 언급돼요. 주변 가사는 일부 불분명해요.", "B2", 58, "history", "oran_local_places_and_figures", "song_lyric", "information", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    623: item("Moulay Abd al-Qadir and a dome are mentioned in connection with Oran; the line is a heritage reference with unclear details.", "물라이 압델카데르와 돔이 오랑과 관련해 언급돼요. 세부 내용이 불분명한 유산 관련 표현이에요.", "B2", 58, "history", "oran_religious_heritage", "speech", "information", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    624: item("We tell visitors about the places to see and welcome them; we have received them hospitably.", "방문객들에게 볼 만한 곳을 알려 주고 환영해요. 우리는 손님을 따뜻하게 맞이했어요.", "B1", 38, "travel", "welcoming_visitors_to_oran", "speech", "information", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    625: item("El Kerma and the sheikhs are mentioned in a local heritage line; the exact reference is unclear.", "엘 케르마와 셰이크들이 지역 유산을 말하는 구절에서 언급돼요. 정확한 지칭은 불분명해요.", "B2", 60, "history", "oran_area_and_heritage_figures", "song_lyric", "information", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    626: item("We take a rest; this short line appears to continue the tour or travel description.", "잠시 쉬어요. 이 짧은 구절은 여행이나 둘러보기 설명을 이어 가는 말처럼 보여요.", "A2", 24, "travel", "taking_a_rest_during_a_tour", "speech", "suggestion", "colloquial", "high", "source_ambiguity", "flagged"),
    627: item("We are making a small report about Oran; this is an announcement of a short local feature.", "오랑에 대한 짧은 리포트를 만들고 있어요. 지역을 소개하는 짧은 특집을 알리는 말이에요.", "B1", 34, "social_media", "short_report_about_oran", "speech", "information", "colloquial", "medium", "source_ambiguity", "flagged"),
    628: item("Please, I have a son; help him with his police file and defend or handle the paperwork for him. The opening plea and some slang are unclear.", "부탁해요. 제 아들이 있는데 경찰 서류를 처리할 수 있도록 도와주고 그를 위해 변호하거나 절차를 맡아 주세요. 처음의 부탁과 일부 속어는 불분명해요.", "C1", 76, "administration", "request_for_help_with_police_paperwork", "conversation", "request", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    629: item("Yes, that one—we clap for him. My brother, send a message; my sister Marie is also mentioned. The exchange is a social request with unclear names.", "네, 그 사람이요. 그를 위해 박수를 쳐요. 형제에게 메시지를 보내 달라고 하고, 마리라는 자매도 언급돼요. 이름이 포함된 사회적 부탁이며 일부는 불분명해요.", "B2", 64, "daily_life", "social_message_and_named_people", "conversation", "request", "colloquial", "high", "source_ambiguity", "flagged"),
    630: item("My friend needs a vest or work garment for a parking job in Algeria; the exact clothing term and situation are unclear.", "내 친구가 알제리에서 주차 관련 일을 하려면 조끼나 작업복이 필요해요. 정확한 옷 이름과 상황은 불분명해요.", "B2", 58, "work", "work_clothing_and_parking_job", "conversation", "request", "colloquial", "high", "source_ambiguity", "flagged"),
    631: item("I did not see it and I am worried; help me. The line then mentions a show in Frimargou and singers including Redouane, Dalila, and Hasni. Several names are uncertain.", "나는 그것을 보지 못해 걱정돼요. 도와주세요. 이어서 프리마르구의 공연과 레드완, 달릴라, 하스니 같은 가수들이 언급돼요. 몇몇 이름은 불확실해요.", "C1", 80, "entertainment_music", "request_and_oran_music_event", "conversation", "request", "mixed", "high", "long_source|source_ambiguity", "flagged"),
    632: item("What is wrong? There is a singer who is going to sing in the Casbah; the announcement is about a live music appearance.", "무슨 일이에요? 카스바에서 노래할 가수가 있어요. 라이브 음악 공연을 알리는 말이에요.", "B1", 42, "entertainment_music", "announcing_a_singer_in_the_casbah", "conversation", "information", "colloquial", "medium", "source_ambiguity", "flagged"),
    633: item("Our brother has bread, soup with chicken, chicken feet, lentils, and rice; the line humorously lists food being served.", "우리 형제에게 빵, 닭고기 수프, 닭발, 렌틸콩과 밥이 있어요. 차려지는 음식을 장난스럽게 나열하는 말이에요.", "B2", 62, "food", "humorous_listing_of_a_meal", "joke", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    634: item("I want to go to the toilet. You do not need to do that; there is food. The line is a vulgar or comic exchange about the bathroom and eating.", "화장실에 가고 싶어요. 그럴 필요 없어요. 음식이 있잖아요. 화장실과 먹는 일을 연결한 상스러운 코미디 대화예요.", "B2", 64, "humor", "vulgar_bathroom_and_food_joke", "joke", "request", "vulgar", "high", "source_ambiguity", "flagged"),
    635: item("Peace be upon you, everyone. This is Lamine Emilio in Oran, in episode two of Restaurant Rahma, a charitable association connected with helping people.", "여러분, 평안하세요. 오랑의 라민 에밀리오입니다. 사람들을 돕는 자선 단체와 관련된 라흐마 식당 2편이에요.", "B1", 46, "social_media", "charity_restaurant_video_introduction", "social_media", "greeting", "mixed", "medium", "code_switching|source_ambiguity", "flagged"),
    636: item("I am dressed and I am in Hamri with the Nas Khir association; the speaker introduces the charitable activity.", "나는 옷을 갖춰 입고 함리에서 나스 키르 협회와 함께 있어요. 화자가 자선 활동을 소개해요.", "B1", 42, "social_media", "charity_association_in_hamri", "social_media", "information", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    637: item("I am with my dear friend Sofiane; the speaker continues introducing the people involved in the charity visit.", "나는 사랑하는 친구 소피안과 함께 있어요. 화자가 자선 방문에 함께한 사람들을 계속 소개해요.", "A2", 28, "daily_life", "introducing_a_friend_at_charity_event", "narrative", "information", "colloquial", "medium", "source_ambiguity", "flagged"),
    638: item("Stay with us at our place; the menu or meal is mentioned, but the exact food term is unclear.", "우리와 함께 여기 있어요. 메뉴나 식사가 언급되지만 정확한 음식 이름은 불분명해요.", "A2", 30, "food", "hospitality_and_charity_meal", "conversation", "request", "colloquial", "high", "source_ambiguity", "flagged"),
    639: item("We were at the local place, in the kitchen, preparing the meal; this is part of the charity restaurant episode.", "우리는 현지 장소의 주방에서 식사를 준비하고 있었어요. 자선 식당 에피소드의 한 장면이에요.", "B1", 38, "food", "preparing_a_charity_meal", "narrative", "narration", "colloquial", "medium", "source_ambiguity", "flagged"),
    640: item("We are going to the market to get a ram and chickens; the animals are being bought or donated for the charitable meal.", "자선 식사를 위해 시장에 가서 양 한 마리와 닭을 마련하려고 해요. 동물들을 사거나 기부받는 장면이에요.", "B1", 44, "food", "shopping_for_charity_meal", "narrative", "narration", "colloquial", "medium", "source_ambiguity", "flagged"),
}


def validate(source):
    by = {row["sentno"]: row for row in source}
    expected = [str(index) for index in range(TARGET_START, TARGET_END + 1)]
    if sorted(RAW) != list(range(TARGET_START, TARGET_END + 1)):
        raise RuntimeError("raw_coverage")
    rows = []
    for sentno in expected:
        payload = {**RAW[int(sentno)], "latin": latinize(by[sentno]["arabic_original"]), "source_uid": by[sentno]["source_uid"], "sentno": sentno}
        for field in ("domain", "genre", "speech_act", "register", "context_dependency"):
            if payload[field] not in CONTROLLED_VALUES[field]:
                raise RuntimeError(f"controlled:{sentno}:{field}")
        if payload["cefr_level"] not in CEFR_LEVELS:
            raise RuntimeError(f"cefr:{sentno}")
        flags = payload["processing_flags"].split("|") if payload["processing_flags"] else []
        if flags != sorted(flags) or any(flag not in PROCESSING_FLAG_VALUES for flag in flags):
            raise RuntimeError(f"flags:{sentno}")
        if payload["enrichment_state"] == "flagged" and not flags:
            raise RuntimeError(f"flagged_without_reason:{sentno}")
        rows.append(payload)
    return rows


def build():
    if source_gate()["result"] != "PASS" or check_layer_contract()["result"] != "PASS":
        raise RuntimeError("gate_failed")
    rows = validate(read_tsv(SOURCE_OUT))
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    BATCH_OUT.parent.mkdir(parents=True, exist_ok=True)
    with BATCH_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BATCH_FIELDS, delimiter="\t", quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "batch_id": BATCH_ID, "base_commit": BASE_COMMIT, "sentno_start": TARGET_START, "sentno_end": TARGET_END,
        "row_count": 64, "fields": [*EMPTY_FIELDS, "processing_flags", "enrichment_state"], "prompt_version": PROMPT_VERSION,
        "source_dependency": "canonical_source_only", "morphology_dependency": False, "darija_modified": False,
        "schema_version": "1.1.0", "generated_at": generated_at, "review_state": "generated",
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scores = [int(row["difficulty_score"]) for row in rows]
    flags = Counter(flag for row in rows if row["processing_flags"] for flag in row["processing_flags"].split("|"))
    report = {
        "result": "PASS", "batch_id": BATCH_ID, "base_commit": BASE_COMMIT, "sentno_start": TARGET_START, "sentno_end": TARGET_END,
        "target_rows": 64, "draft_rows": sum(row["enrichment_state"] == "draft" for row in rows),
        "flagged_rows": sum(row["enrichment_state"] == "flagged" for row in rows),
        "flagged_row_sentnos": [row["sentno"] for row in rows if row["enrichment_state"] == "flagged"],
        "processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in rows),
        "flag_counts": dict(sorted(flags.items())),
        "difficulty_stats": {"min": min(scores), "max": max(scores), "mean": round(statistics.mean(scores), 2), "median": statistics.median(scores)},
        "required_linguistic_fields": 64 * len(EMPTY_FIELDS), "source_gate": "PASS", "layer_contract": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT", "morphology_reads": 0, "arabic_modified": 0,
        "learning_unit_rows_created": 0, "validator": "PASS", "generated_at": generated_at,
        "outputs": {"batch": BATCH_OUT.relative_to(ROOT).as_posix(), "manifest": MANIFEST_OUT.relative_to(ROOT).as_posix()},
    }
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(build(), ensure_ascii=False, indent=2))
