"""Build source-only MADOran enrichment Batch 09 for Sentno 513..576."""
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

BATCH_ID = "MADORAN-ENRICH-009"
BASE_COMMIT = "6aabeaa"
PROMPT_VERSION = "madoran-source-enrichment-v9"
TARGET_START = 513
TARGET_END = 576
BATCH_DIR = ROOT / "data/master/enrichment/batches"
BATCH_OUT = BATCH_DIR / "batch09_sentno_0513_0576.tsv"
MANIFEST_OUT = BATCH_DIR / "batch09_manifest.json"
QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_generation_qa.json"
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
    513: item("He uses his own beard as incense for him; the proverb wording and exact implication are unclear.", "그는 자기 수염으로 자신을 위한 향을 피워요. 속담의 표현과 정확한 함의는 불분명해요.", "B2", 52, "culture_tradition", "unclear_proverb_about_self_help", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    514: item("A supplication without sins melts on its owner's head; the proverb wording is difficult to interpret literally.", "죄 없는 기도는 그 주인의 머리에서 녹는다는 말이에요. 속담의 문자적 표현은 해석하기 어려워요.", "C1", 66, "religion", "unclear_proverb_about_prayer", "proverb", "description", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    515: item("A little henna and a little softness or moisture of the hands; the exact proverb meaning is unclear.", "약간의 헤나와 손의 약간의 부드러움 또는 촉촉함이라는 말이에요. 정확한 속담의 뜻은 불분명해요.", "B2", 55, "culture_tradition", "unclear_proverb_about_henna", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    516: item("One hand cannot clap. When we support one another and cooperate, we can do the impossible.", "손 하나로는 박수를 칠 수 없어요. 서로 돕고 협력하면 불가능한 일도 할 수 있어요.", "A2", 28, "family_relationships", "proverb_about_cooperation", "proverb", "suggestion", "neutral", "low", "idiom_culture", "flagged"),
    517: item("Go over my head and move on; the exact command is context-dependent.", "내 머리를 넘어 그냥 지나가라는 말이에요. 정확한 명령의 뜻은 문맥에 따라 달라요.", "B1", 42, "daily_life", "unclear_command_to_move_on", "conversation", "command", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    518: item("He covered the sun with a sieve. The expression refers to trying to hide something obvious.", "그는 체로 태양을 가렸어요. 이 표현은 명백한 것을 숨기려는 일을 가리켜요.", "A2", 25, "culture_tradition", "proverb_about_hiding_the_obvious", "proverb", "warning", "neutral", "medium", "idiom_culture", "flagged"),
    519: item("The women's house has a dry serving bowl; the phrase suggests a household without food, but its exact implication is unclear.", "여자들의 집에 마른 그릇만 있다는 말이에요. 음식이 없는 집을 암시하는 듯하지만 정확한 함의는 불분명해요.", "B2", 54, "family_relationships", "unclear_proverb_about_household_food", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    520: item("Nothing remains in the wadi except its stones. The parenthetical explanation says that life is transient and that only one's deeds remain with one, like stones that stay with the wadi even when it dries.", "와디에는 돌만 남아요. 괄호 안의 설명은 삶은 덧없고, 와디가 말라도 곁에 남는 돌처럼 사람에게는 자신의 행동만 남는다는 뜻을 설명해요.", "C1", 72, "culture_tradition", "proverb_about_legacy_and_transience", "proverb", "opinion", "mixed", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    521: item("Tell us about a crazy incident that happened in your life. I got on a bus, the driver was blasting rai music and turning it up a lot, I became annoyed, and none of the other people said anything.", "살면서 겪은 황당한 일을 들려줘요. 버스를 탔는데 운전사가 라이 음악을 크게 틀고 더 키웠어요. 나는 화가 났지만 다른 사람들은 아무 말도 하지 않았어요.", "B2", 62, "transport", "bus_story_with_loud_rai_music", "narrative", "request", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    522: item("My heart told me to talk to him, but then I said, 'What is it to me?' If someone talks to him, I gain nothing; it would be shameful.", "마음은 그에게 말하라고 했지만, 곧 ‘그게 나와 무슨 상관이야?’라고 생각했어요. 누가 그에게 말해도 내게 이득은 없고 부끄러운 일이 될 것 같았어요.", "B2", 58, "daily_life", "hesitation_about_intervening", "conversation", "opinion", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    523: item("I waited, but nothing happened. I became upset and told the driver to lower it a little. I felt ashamed of frightening the driver, while all the passengers stared at me silently; the driver did what I asked.", "기다렸지만 아무 일도 없어서 화가 나 운전사에게 조금 줄여 달라고 했어요. 운전사를 놀라게 한 것 같아 부끄러웠고, 승객들은 모두 말없이 나를 바라봤어요. 운전사는 내 말을 들어줬어요.", "B2", 64, "transport", "bus_complaint_and_embarrassment", "narrative", "complaint", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    524: item("He told me, 'You are riding a family bus. This is my family, and they are going to a wedding.'", "그가 말했어요. ‘당신은 가족이 타는 버스를 타고 있어요. 이 사람들은 내 가족이고 결혼식에 가는 중이에요.’", "A2", 30, "transport", "family_bus_to_wedding", "conversation", "information", "colloquial", "medium"),
    525: item("When I passed by and found you waiting at the bus, I was embarrassed and said I would stop to take you along. Out of shyness I gave a long, broad ululation, then stood clapping and dancing; I felt it in my sides.", "지나가다 네가 버스에서 기다리는 것을 보고 부끄러워서 태워 주려고 멈추겠다고 했어요. 부끄러운 마음에 길고 크게 자그라트를 한 뒤 박수치고 춤췄어요. 옆구리로 그 흥분을 느꼈어요.", "C1", 76, "transport", "wedding_bus_ululation_story", "narrative", "narration", "colloquial", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    526: item("People in the old days lived beautifully and peacefully. Their hearts were white as milk, their dreams red like a flower, their imagination wide like gazelles, and their minds flew like pigeons.", "옛사람들은 아름답고 평화롭게 살았어요. 마음은 우유처럼 하얗고, 꿈은 꽃처럼 붉었으며, 상상력은 가젤처럼 넓고, 생각은 비둘기처럼 날아다녔어요.", "C1", 70, "culture_tradition", "nostalgic_description_of_earlier_generations", "speech", "opinion", "mixed", "high", "long_source|source_ambiguity", "flagged"),
    527: item("Sorry, sister. What are you waiting for, please? What will you drink? Water? I will bring you water and mint too; some words are unclear in the recording.", "미안해요, 언니. 무엇을 기다리고 있어요? 무엇을 마실래요? 물? 물과 민트도 가져다줄게요. 녹음에서 몇몇 표현은 불분명해요.", "B2", 62, "food", "offering_drinks_in_conversation", "conversation", "apology", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    528: item("Do you like it? There is banana and caramel, but some flavors are unavailable. Is there strawberry, chocolate, or vanilla? There is only banana ice cream; caramel is unavailable.", "마음에 들어요? 바나나와 캐러멜은 있지만 어떤 맛은 없어요. 딸기, 초콜릿, 바닐라가 있나요? 바나나 아이스크림만 있고 캐러멜은 없어요.", "B2", 58, "food", "ice_cream_flavor_availability", "conversation", "question", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    529: item("No brownie or Calypso either. What about fish? We have all the usual flavors. Bring me a banana dessert. Is orange juice still available? Is there a cocktail? We only have Hamoud.", "브라우니나 칼립소도 없어요. 생선은요? 보통 있는 것은 다 있어요. 바나나 디저트를 가져다줘요. 오렌지 주스는 아직 있어요? 칵테일은요? 우리에게는 함우드만 있어요.", "B2", 64, "food", "dessert_and_drink_availability", "conversation", "question", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    530: item("Shall I bring you Hamoud? Bring me Hamoud. What is wrong with this one? It bends back on itself. 'Madam?' Some of the wording is unclear.", "함우드를 가져다줄까요? 함우드를 가져다줘요. 이건 뭐가 문제예요? 스스로 휘어지는 것 같아요. ‘마담?’ 몇몇 표현은 불분명해요.", "B2", 58, "food", "unclear_drink_service_exchange", "conversation", "question", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    531: item("Yes, I am talking to you. I am looking for Hamoud. What is this? What is this? Explain it to me; this is my number.", "네, 지금 당신에게 말하고 있어요. 함우드를 찾고 있어요. 이게 뭐예요? 이게 뭐예요? 설명해 줘요. 이건 내 번호예요.", "B1", 50, "food", "confused_drink_order", "conversation", "question", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    532: item("Top up my Flexy, please. Unfortunately I am muted or have no credit. Do not embarrass me by flirting with my friend in front of me, you vulgar woman; I will not let this pass, so go away and leave my friend alone. Several slang phrases are unclear.", "플렉시를 충전해 줘요. 안타깝게도 나는 음소거 상태이거나 크레딧이 없어요. 내 앞에서 내 친구에게 추근대며 나를 망신시키지 마, 이 상스러운 여자야. 그냥 넘기지 않을 테니 멀리 가서 내 친구를 내버려 둬. 몇몇 속어 표현은 불분명해요.", "C1", 82, "daily_life", "vulgar_argument_and_phone_credit", "conversation", "complaint", "slang", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    533: item("There is nothing beautiful in this world like sport. I would remove all the sportswear, but some people have truly ruined it for us.", "이 세상에 스포츠만큼 아름다운 것은 없어요. 스포츠와 관련된 것은 모두 없애고 싶지만, 어떤 사람들이 정말 우리를 위해 그것을 망쳐 놓았어요.", "B2", 56, "sports", "opinion_about_sport", "conversation", "opinion", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    534: item("He has been doing sport for a week. I encourage you, brother, but I do not mean going into a gym and taking thirty-three pictures like this with a two-kilogram weight.", "그는 운동을 시작한 지 일주일 됐어요. 응원할게요, 형제여. 하지만 체육관에 들어가 2킬로그램 아령을 들고 이런 사진을 서른세 장 찍으라는 뜻은 아니에요.", "C1", 76, "sports", "gym_photos_and_exercise", "conversation", "opinion", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    535: item("Then make two sports definitions, not two photographic definitions; the French wording is retained approximately.", "그럼 스포츠에 관한 정의를 두 개 만들고, 사진에 관한 정의를 두 개 만들지는 마세요. 프랑스어 표현은 대략적으로 보존했어요.", "C1", 68, "sports", "unclear_sports_and_photography_wordplay", "conversation", "suggestion", "mixed", "high", "code_switching|source_ambiguity", "flagged"),
    536: item("We photographed ourselves all over the gym with that two-kilogram weight; if I had gone, I would have helped with it.", "우리는 체육관 곳곳에서 그 2킬로그램 무게를 들고 사진을 찍었어요. 내가 갔더라면 그것을 드는 일을 도왔을 거예요.", "B2", 58, "sports", "gym_photo_story", "narrative", "narration", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    537: item("Your mother went up with it; if I had worked outside, it would have been two kilograms of potatoes. The comparison is unclear in the source.", "네 어머니가 그것과 함께 올라갔어요. 내가 밖에서 일했다면 감자 2킬로그램이었을 거예요. 원문의 비교 관계는 불분명해요.", "C1", 72, "sports", "unclear_weight_comparison", "conversation", "opinion", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    538: item("The problem is not here. The problem is when he goes and tells his wife something: she says she always wanted the scene where I put you on my back and make you a King Kong bomb. You are the one; when you got the strength to carry it, tell me. Much of the slang is unclear.", "문제는 여기 있는 게 아니에요. 문제는 그가 아내에게 무언가를 말하러 갈 때예요. 아내는 내가 너를 등에 업고 킹콩 폭탄처럼 만드는 장면을 늘 원했다고 말해요. 네가 바로 그 사람이고, 그것을 들 힘이 생겼다면 말해 줘. 속어가 많아 상당 부분이 불분명해요.", "C2", 88, "family_relationships", "unclear_slang_about_strength_and_partner", "conversation", "narration", "slang", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    539: item("What does she tell him? 'I would never walk with my honor exposed; you are with an ironworker.' The final relationship term is unclear.", "그녀가 그에게 뭐라고 말하나요? ‘나는 내 명예를 드러낸 채로는 절대 걷지 않을 거야. 너는 철공과 함께 있잖아.’ 마지막 관계 표현은 불분명해요.", "C1", 74, "family_relationships", "unclear_relationship_and_honor_dialogue", "conversation", "narration", "slang", "high", "source_ambiguity", "flagged"),
    540: item("Yes, he is alive and with a bodybuilder; his protein is rising only with vitamins, or so she says. The rest of the exchange is unclear.", "네, 그는 살아 있고 보디빌더와 함께 있어요. 그의 단백질은 비타민으로만 올라간다고 그녀가 말하는 듯해요. 나머지 대화는 불분명해요.", "C1", 76, "sports", "unclear_bodybuilding_dialogue", "conversation", "description", "slang", "high", "code_switching|source_ambiguity", "flagged"),
    541: item("Inside it she says only 'my life'; outside, she asks how things are. When people come to prank you, you see only cars and pulling; the wording is largely unclear.", "안에서는 그녀가 ‘내 인생’이라고만 말하고, 밖에서는 어떻게 지내냐고 물어요. 사람들이 당신을 놀리러 오면 자동차와 당기는 모습만 보인다는 듯하지만 표현은 대체로 불분명해요.", "C1", 78, "daily_life", "unclear_teasing_scene", "conversation", "narration", "slang", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    542: item("A beach outing comes by itself. We have girls, and when we go to the beach, generally we go with our family, our parents, and everyone.", "해변에 가는 일은 자연스럽게 생겨요. 우리에게는 여자들이 있고, 해변에 갈 때는 보통 가족과 부모님 모두와 함께 가요.", "B2", 60, "travel", "family_beach_outing", "conversation", "description", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    543: item("Do you want to change your clothes to enter the sea? There is no bikini and only two pieces. We observe modesty, so we wear thirty-three pieces, add a scarf, wrap yourself in a towel, and come dressed.", "바다에 들어가려고 옷을 갈아입을래요? 비키니는 없고 두 조각만 있어요. 우리는 단정함을 지켜서 서른세 조각을 입고, 스카프를 더하고, 수건으로 몸을 감싸서 옷을 입은 채 와요.", "C1", 82, "travel", "modest_beach_clothing_dialogue", "conversation", "suggestion", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    544: item("When you go inside, you will do it like that and think you are Katrina with that hair. Then he starts cutting watermelon, or he only turns to look at you; the scene is unclear.", "안으로 들어가면 그렇게 하고 그 머리로 자신이 카트리나라고 생각할 거예요. 그러면 그는 수박을 자르기 시작하거나 당신만 바라볼 거예요. 장면의 정확한 뜻은 불분명해요.", "C1", 78, "travel", "unclear_beach_scene_and_appearance", "conversation", "narration", "colloquial", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    545: item("Your brother is busy playing ball and makes you stay outside; he says a phrase like 'T-bouj, you will die from it in your head, but you will not die.' The slang is unclear.", "네 형제는 공놀이에 정신이 팔려 너를 밖에 세워 둬요. 그는 ‘티부즈, 머리로는 그것 때문에 죽겠지만 죽지는 않아’ 같은 말을 해요. 속어는 불분명해요.", "C1", 78, "sports", "unclear_sports_teasing", "conversation", "description", "slang", "high", "code_switching|source_ambiguity", "flagged"),
    546: item("I wanted to swim, but you spoiled it for me jokingly. Let me swim like this; perhaps an Algerian shark will come out and bite you quickly. It says, 'I will teach you to swim, will I?'", "수영하고 싶었는데 네가 장난으로 망쳐 버렸어. 이렇게라도 수영하게 해 줘. 어쩌면 알제리 상어가 나타나 너를 재빨리 물지도 몰라. ‘내가 수영을 가르쳐 주겠다고?’라는 식의 말이에요.", "C1", 82, "travel", "teasing_about_swimming_and_shark", "conversation", "warning", "slang", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    547: item("You insist on teaching me to swim, brother, but you are not a swimmer and the wave is too big for you. I am already afraid for you; my father only watches you, so go away.", "형제여, 너는 나에게 수영을 가르치겠다고 고집하지만 수영을 잘하지도 않고 파도가 너에게 너무 커요. 나는 이미 네가 걱정되고, 아버지는 너를 바라보기만 하니 이제 가요.", "B2", 68, "travel", "warning_about_large_wave", "conversation", "warning", "colloquial", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    548: item("When he sees you like that, your brother whistles, takes off his shirt, and comes in. You all act as if you chose this and are only pretending; the wording is unclear.", "그가 당신을 그렇게 보면 형제가 휘파람을 불고 셔츠를 벗고 들어와요. 여러분은 모두 이것을 선택한 척하며 연기하지만, 표현은 불분명해요.", "C1", 76, "travel", "unclear_beach_teasing_scene", "conversation", "narration", "slang", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    549: item("We all cried with Cinderella when we were children, with tears and runny noses. We resembled her only in the sidewalk and broom; we never reached the part where a prince comes to propose and finds a single shoe.", "어릴 때 우리는 모두 신데렐라와 함께 울었고 눈물과 콧물을 흘렸어요. 우리는 보도와 빗자루에서만 신데렐라를 닮았고, 왕자가 청혼하러 와서 신발 한 짝을 찾는 부분에는 이르지 못했어요.", "C1", 78, "entertainment_music", "cinderella_childhood_story", "narrative", "narration", "colloquial", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    550: item("You girls keep hanging around as if a boy from your town will find your shoe. Get that idea out of your head; our girls went to the beach and found it dry.", "너희 여자들은 고향 남자가 신발을 찾아 줄 것처럼 계속 서성여요. 그런 생각은 머리에서 지워요. 우리 여자들은 해변에 갔지만 물이 말라 있는 것을 봤어요.", "B2", 64, "family_relationships", "teasing_about_cinderella_and_beach", "conversation", "warning", "slang", "high", "idiom_culture|source_ambiguity", "flagged"),
    551: item("Write the coordinates and the history yourself. Now we will measure you and show you the girls' mentality: take a canvas, fold it, put it in your bag, and take out whatever you find; an artist can measure it. God asks only for good. Much of the wordplay is unclear.", "좌표와 역사는 직접 써요. 이제 여러분을 재고 여자들의 사고방식을 보여 줄게요. 캔버스를 가져와 접어 가방에 넣고, 찾은 것을 꺼내요. 예술가는 그것을 잴 수 있어요. 하느님은 좋은 것만 요구해요. 말장난의 상당 부분은 불분명해요.", "C1", 84, "culture_tradition", "unclear_art_and_identity_wordplay", "speech", "suggestion", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    552: item("Write the coordinates under the number and buy a new one. Do not bother him; we only want to catch him. If you are walking and it comes at you, understand what is happening; the slang is unclear.", "번호 아래에 좌표를 쓰고 새것을 사요. 그를 괴롭히지 말아요. 우리는 그저 그를 잡고 싶어요. 걷다가 그것이 당신에게 다가오면 무슨 일인지 이해해요. 속어는 불분명해요.", "C1", 78, "daily_life", "unclear_slang_about_catching", "conversation", "suggestion", "slang", "high", "code_switching|source_ambiguity", "flagged"),
    553: item("Peace be upon you; how are you? I am fine, thank God. When I started speaking, you began saying, 'What is wrong with her? What is she speaking? What language is that?'", "안녕하세요, 잘 지내요? 저는 하느님께 감사하게도 잘 지내요. 내가 말하기 시작하자 여러분은 ‘저 사람은 왜 저래? 무슨 말을 하는 거야? 어떤 언어로 말하는 거야?’라고 하기 시작했어요.", "B2", 58, "social_media", "meta_commentary_on_language", "conversation", "greeting", "mixed", "high", "code_switching|source_ambiguity", "flagged"),
    554: item("Today I am bringing you an Algerian tag, and many of you asked me to speak in Algerian.", "오늘은 알제리식 표현을 가져왔어요. 여러분 중 많은 사람이 나에게 알제리어로 말해 달라고 했어요.", "A2", 28, "social_media", "announcing_algerian_language_content", "speech", "information", "colloquial", "medium", "code_switching", "flagged"),
    555: item("So I am going to speak Algerian for you. It may sound a little strange because Oran dialect is not my usual dialect; I have not returned to Algeria for two years, so I have forgotten some of it.", "그래서 여러분에게 알제리어로 말해 볼게요. 오랑 방언은 내가 평소 쓰는 방언이 아니라 조금 이상하게 들릴 수 있어요. 2년 동안 알제리에 가지 않아 조금 잊었어요.", "B2", 56, "social_media", "speaking_algerian_after_time_away", "speech", "information", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    556: item("It is a little difficult for me, as if I slipped on a word—voilà.", "조금 힘들어요. 마치 단어에서 미끄러진 것 같아요. 자, 그럼요.", "B1", 40, "social_media", "difficulty_speaking_a_dialect", "conversation", "opinion", "colloquial", "medium", "code_switching|source_ambiguity", "flagged"),
    557: item("Before we begin this video, I want to say that every country has its own language, and every city in each country has its own language or dialect.", "이 영상을 시작하기 전에, 모든 나라에는 고유한 언어가 있고 각 나라의 도시마다 고유한 언어나 방언이 있다는 말을 하고 싶어요.", "A2", 30, "social_media", "language_and_dialect_diversity", "speech", "information", "neutral", "low"),
    558: item("You are Arabs and you do not understand me; that is normal because you are not from Oran.", "여러분은 아랍인이지만 나를 이해하지 못해요. 오랑 출신이 아니니 당연한 일이에요.", "B1", 42, "social_media", "regional_dialect_comprehension", "conversation", "description", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    559: item("I present Oran; I love you, people of Oran, and we in Algeria talk a lot. Some of the introductory wording is unclear.", "오랑을 소개해요. 오랑 사람들을 사랑해요. 우리 알제리 사람들은 말을 많이 해요. 도입부의 일부 표현은 불분명해요.", "B2", 54, "social_media", "presenting_oran_and_its_people", "speech", "information", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    560: item("We mix a lot of French and Arabic. Everything is normal here; the important thing is 'c'est parti.'", "우리는 프랑스어와 아랍어를 많이 섞어 써요. 여기서는 모든 것이 자연스러워요. 중요한 것은 ‘출발하자’라는 말이에요.", "B2", 52, "social_media", "french_arabic_code_switching", "speech", "opinion", "colloquial", "high", "code_switching", "flagged"),
    561: item("First question: what is the best Algerian song you like?", "첫 번째 질문이에요. 여러분이 좋아하는 가장 좋은 알제리 노래는 무엇인가요?", "A2", 26, "entertainment_music", "question_about_algerian_song", "interview", "question", "neutral", "low"),
    562: item("As I told you, I come from Oran, and it is obvious that in Oran we listen to rai. I made you very angry, and I am angry too, but I do not trust you; you hurt my heart. I cry every day, I love you very much, it was not my intention—please forgive me, my love. The dialogue shifts are partly unclear.", "말했듯이 나는 오랑에서 왔고, 오랑에서 라이 음악을 듣는다는 것은 분명해요. 내가 당신을 아주 화나게 했고 나도 화가 났지만, 당신을 믿지 못해요. 당신은 내 마음을 아프게 했어요. 매일 울고 당신을 아주 사랑해요. 내 의도는 아니었으니 용서해 줘요, 내 사랑. 대화의 주체 전환은 일부 불분명해요.", "C1", 84, "family_relationships", "apology_and_anger_dialogue", "conversation", "apology", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    563: item("Second question: what is the best Algerian food you like?", "두 번째 질문이에요. 여러분이 좋아하는 가장 좋은 알제리 음식은 무엇인가요?", "A2", 26, "food", "question_about_algerian_food", "interview", "question", "neutral", "low"),
    564: item("I have a very long list. First, chorba and harira are obvious. I do not like olive stews at all, but I love olive tagine with peas. I do not like chickpeas very much either. Couscous is obvious, with sauce or plain seffa; that is all.", "목록이 아주 길어요. 먼저 초르바와 하리라는 당연하고, 올리브를 넣은 스튜는 전혀 좋아하지 않지만 완두콩을 넣은 올리브 타진은 정말 좋아해요. 병아리콩도 별로 좋아하지 않아요. 쿠스쿠스는 당연하고, 소스를 곁들이거나 그냥 세파로 먹어요. 이게 다예요.", "B2", 60, "food", "algerian_food_preferences", "interview", "opinion", "colloquial", "high", "long_source|source_ambiguity", "flagged"),
    565: item("Third question: do you know how to cook?", "세 번째 질문이에요. 요리할 줄 아나요?", "A2", 24, "food", "question_about_cooking", "interview", "question", "neutral", "low"),
    566: item("I know how to cook all kinds of stews, but I do not know how to cook everything. I have made couscous once, and it was very good. Everyone who tastes my harira or chorba loves it. I can say I know how to make harira and chorba. Perhaps they want to marry me; I only need a groom, but let us not discuss that topic.", "나는 여러 종류의 스튜를 만들 줄 알지만 모든 요리를 잘하는 것은 아니에요. 쿠스쿠스는 한 번 만들어 봤는데 아주 맛있었어요. 내 하리라나 초르바를 맛본 사람은 모두 좋아해요. 하리라와 초르바는 만들 줄 안다고 말할 수 있어요. 아마 사람들이 나를 결혼시키고 싶어 하나 봐요. 신랑만 있으면 되지만 그 주제는 말하지 말아요.", "C1", 76, "food", "self_description_of_cooking_skills", "interview", "opinion", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    567: item("Fourth question: what Algerian sweet do you like best?", "네 번째 질문이에요. 어떤 알제리 과자가 가장 좋아요?", "A2", 24, "food", "question_about_algerian_sweets", "interview", "question", "neutral", "low"),
    568: item("I share baklava. I loved baklava when I was little, but now it seems much too sweet, too thick, and too long to make. Oh no. Qriouch is excellent, though.", "바클라바를 함께 먹어요. 어릴 때는 바클라바를 정말 좋아했지만, 지금은 너무 달고 너무 두껍고 만들기에도 너무 오래 걸리는 것 같아요. 아, 안 돼요. 그래도 크리우시는 아주 좋아요.", "B2", 58, "food", "opinion_about_baklava_and_qriouch", "interview", "opinion", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    569: item("Fifth question: what sweet have you made?", "다섯 번째 질문이에요. 어떤 과자를 만들어 봤나요?", "A2", 24, "food", "question_about_made_sweets", "interview", "question", "neutral", "low"),
    570: item("I only know how to make samsa; it is very easy and known around the world. I have never tried to make an Algerian sweet. I know how to make American sweets and French cakes, but I do not know how to make Arab sweets.", "나는 삼사를 만들 줄만 알아요. 아주 쉽고 세상 어디서나 알려진 과자예요. 알제리 과자를 만들어 본 적은 없어요. 미국 과자와 프랑스 케이크는 만들 줄 알지만 아랍 과자는 만들 줄 몰라요.", "B2", 64, "food", "samsa_and_cross_cultural_baking", "interview", "description", "colloquial", "high", "code_switching|source_ambiguity", "flagged"),
    571: item("Do you know how to ululate?", "자그라트를 할 줄 아나요?", "A2", 22, "culture_tradition", "question_about_ululation", "interview", "question", "neutral", "low"),
    572: item("No. I have never tried it, and I am shy; how will I explain it to you? I will not try in front of you, so please do not ask me—not even my father. The wording is playful and partly unclear.", "아니요. 한 번도 해 보지 않았고 부끄러워요. 여러분에게 어떻게 설명하겠어요? 여러분 앞에서는 시도하지 않을 테니 묻지 말아요. 아버지에게도 묻지 말고요. 장난스러운 표현이라 일부는 불분명해요.", "B2", 62, "culture_tradition", "shyness_about_ululation", "interview", "refusal", "colloquial", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    573: item("For a wedding, do you wear an evening gown or jeans?", "결혼식에는 이브닝드레스를 입나요, 아니면 청바지를 입나요?", "A2", 24, "family_relationships", "question_about_wedding_clothes", "interview", "question", "neutral", "low"),
    574: item("For a wedding of people I do not know, just a dress is enough. For a family wedding, I wear one Arab outfit. I love wearing Arab clothes; I do not want to dress in a loose or overly casual way. I am modern, but for my family's wedding I make an occasion of it.", "모르는 사람들의 결혼식이면 드레스 하나면 충분해요. 가족 결혼식에는 아랍식 옷 한 벌을 입어요. 아랍식 옷을 입는 것을 정말 좋아하고, 헐렁하거나 지나치게 편한 옷은 입고 싶지 않아요. 나는 현대적이지만 가족 결혼식에는 제대로 차려입어요.", "C1", 70, "family_relationships", "wedding_clothing_preferences", "interview", "opinion", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged"),
    575: item("You are country people and do not know Arab traditions. A bride changes five or seven outfits, sometimes up to nine; nine is a lot.", "여러분은 시골 사람이라 아랍 전통을 잘 모르네요. 신부는 옷을 다섯 벌이나 일곱 벌, 때로는 아홉 벌까지 갈아입어요. 아홉 벌은 정말 많아요.", "B2", 60, "culture_tradition", "wedding_outfit_traditions", "conversation", "description", "colloquial", "high", "code_switching|idiom_culture|source_ambiguity", "flagged"),
    576: item("I change three times at a wedding because there is a system. I am telling you about the procession, especially the family of the bride or the family of the groom; some details are unclear.", "결혼식에서는 정해진 방식이 있어서 세 번 옷을 갈아입어요. 특히 신부 가족이나 신랑 가족의 행렬에 대해 말하는 거예요. 세부 사항은 일부 불분명해요.", "C1", 68, "family_relationships", "wedding_procession_and_outfits", "conversation", "information", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged"),
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
