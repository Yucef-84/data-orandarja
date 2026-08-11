"""Build source-only MADOran enrichment Batch 08 for Sentno 449..512."""
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


BATCH_ID = "MADORAN-ENRICH-008"
BASE_COMMIT = "71bb99f"
PROMPT_VERSION = "madoran-source-enrichment-v8"
TARGET_START = 449
TARGET_END = 512
BATCH_DIR = ROOT / "data/master/enrichment/batches"
BATCH_OUT = BATCH_DIR / "batch08_sentno_0449_0512.tsv"
MANIFEST_OUT = BATCH_DIR / "batch08_manifest.json"
QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_generation_qa.json"
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
    table = str.maketrans(
        {
            "ا": "a",
            "أ": "a",
            "إ": "i",
            "آ": "a",
            "ء": "'",
            "ب": "b",
            "ت": "t",
            "ث": "th",
            "ج": "j",
            "ح": "7",
            "خ": "kh",
            "د": "d",
            "ذ": "dh",
            "ر": "r",
            "ز": "z",
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
            "ئ": "i",
            "ؤ": "w",
            "،": ",",
            "؟": "?",
        }
    )
    return " ".join("".join(ch if ord(ch) < 128 else " " for ch in text.translate(table)).split())


RAW = {
    449: item(
        "Bring your son, whether he is good-looking or not, they will kiss him. The proverb's exact implication is unclear.",
        "네 아들을 데려와. 잘생겼든 아니든 사람들이 그에게 입맞춤할 거야. 속담의 정확한 뜻은 불분명해.",
        "B2", 62, "family_relationships", "proverb_about_children_and_appearance", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"
    ),
    450: item(
        "He learns cupping on the heads of orphans.",
        "그는 고아들의 머리에 부항을 놓으며 부항을 배워.",
        "B1", 52, "health", "proverb_about_experimentation", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"
    ),
    451: item("The cat teaches its father to jump.", "고양이가 자기 아버지에게 뛰는 법을 가르쳐.", "A2", 28, "family_relationships", "proverb_about_reversed_expertise", "proverb", "description", "neutral", "low"),
    452: item("A mouse's offspring turns out to be a digger.", "쥐의 새끼는 굴을 파는 놈이 돼.", "B1", 38, "family_relationships", "proverb_about_inherited_traits", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    453: item("If you see the tall one running, know that the short one is always behind him.", "키 큰 사람이 달리는 것을 보면 키 작은 사람이 늘 그 뒤에 있다는 것을 알아.", "B1", 42, "family_relationships", "proverb_about_dependency", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    454: item("A weed seeking a livelihood.", "먹고살 길을 찾는 풀.", "B1", 36, "daily_life", "proverb_about_livelihood", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    455: item("He is drunk, yet he knows the door of his house.", "그는 취했지만 자기 집 문은 알아.", "A2", 30, "daily_life", "proverb_about_awareness", "proverb", "description", "colloquial", "low"),
    456: item("The cat grew up and put on a tie.", "고양이가 자라서 넥타이를 맸어.", "A2", 26, "culture_tradition", "proverb_about_pretension", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    457: item("The blind woman needs only kohl, and the monkey needs only roses.", "눈먼 여자에게 필요한 것은 콜뿐이고, 원숭이에게 필요한 것은 장미뿐이야.", "B1", 46, "culture_tradition", "proverb_about_misplaced_adornment", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    458: item("They gave the donkey cloves to smell, and it ate them.", "사람들이 당나귀에게 정향을 냄새 맡으라고 주었더니 당나귀가 먹어 버렸어.", "B1", 42, "culture_tradition", "proverb_about_misuse", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    459: item("A bald man needs only someone to scratch his head.", "대머리에게 필요한 것은 머리를 긁어 줄 사람뿐이야.", "A2", 34, "health", "proverb_about_obvious_needs", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    460: item("The stick you despise will hurt you.", "네가 업신여기는 막대기가 너를 아프게 할 거야.", "B1", 37, "culture_tradition", "proverb_about_underestimation", "proverb", "warning", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    461: item("His couscous returns to its origin; the proverb's exact reference is unclear.", "그의 쿠스쿠스는 본래 자리로 돌아가. 속담이 정확히 무엇을 가리키는지는 불분명해.", "B2", 48, "food", "proverb_about_returning_to_origins", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    462: item("The living divide it among themselves.", "살아 있는 사람들이 그것을 나눠 가져.", "B1", 34, "culture_tradition", "proverb_about_distribution", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    463: item("The person who missed the conversation says, 'I heard it'; the person who missed the food says, 'I am full.'", "대화를 놓친 사람은 ‘들었어’라고 하고, 음식을 놓친 사람은 ‘배불러’라고 해.", "B1", 48, "culture_tradition", "proverb_about_excuses", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    464: item("Whoever did it with his hands must undo it with his teeth.", "자기 손으로 한 일은 자기 이로 풀어야 해.", "B1", 45, "culture_tradition", "proverb_about_responsibility", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    465: item("The talk is with me, but the meaning is about my neighbor. People in central Algeria say this often.", "말은 나에게 하지만 뜻은 내 이웃을 두고 하는 말이야. 알제리 중부 사람들이 이 말을 자주 해.", "B2", 58, "culture_tradition", "regional_proverb_about_indirect_speech", "proverb", "description", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    466: item("Crying at the head of the dead. People, especially in the east, say this expression.", "죽은 사람의 머리맡에서 우는 것. 특히 동부 사람들이 이렇게 말해.", "B1", 40, "culture_tradition", "regional_proverb_about_mourning", "proverb", "description", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
    467: item("Whoever wants beauty does not say, 'Ah!' People in Algeria say this expression continually.", "아름다움을 원하는 사람은 ‘아!’라고 하지 않아. 알제리 사람들이 늘 이렇게 말해.", "B1", 45, "culture_tradition", "proverb_about_beauty_and_pain", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    468: item("I am digging him a grave at his mother's, and he is coming at me with a pickaxe. This expression is identified as eastern.", "나는 그의 어머니 무덤에 그를 위한 무덤을 파고 있는데, 그는 곡괭이를 들고 나에게 달려와. 이 표현은 동부 지역의 말로 표시되어 있어.", "C1", 72, "crime_safety", "regional_proverb_about_conflict", "proverb", "narration", "mixed", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    469: item("Act like your neighbor, or go around the door of your house; the exact proverb is unclear.", "이웃처럼 행동하거나 집 문 주위를 돌아. 속담의 정확한 뜻은 불분명해.", "B2", 50, "housing", "proverb_about_neighbors", "proverb", "suggestion", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    470: item("When he was alive, he longed for dates; when he died, they brought him a date-palm cluster.", "살아 있을 때는 대추야자를 그리워하더니, 죽고 나서야 사람들이 대추야자 송이를 가져왔어.", "B1", 48, "culture_tradition", "proverb_about_delayed_gifts", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    471: item("Turn the pot over onto its mouth, and the daughter comes out like her mother.", "냄비를 입 쪽으로 뒤집으면 딸이 어머니를 닮아 나와.", "B1", 43, "family_relationships", "proverb_about_resemblance", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    472: item("Houhou praises himself; the name or expression is preserved as heard.", "후후가 자기 자신을 칭찬해. 이름이나 표현은 들은 그대로 보존해.", "B1", 38, "culture_tradition", "proverb_about_self_praise", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    473: item("The road has eyes, and the forest has ears.", "길에는 눈이 있고 숲에는 귀가 있어.", "A2", 28, "travel", "proverb_about_observation", "proverb", "warning", "neutral", "low"),
    474: item("They asked the blind woman what she needed, and she said, 'Kohl.'", "사람들이 눈먼 여자에게 무엇이 필요하냐고 물었더니, 여자가 ‘콜’이라고 대답했어.", "A2", 34, "culture_tradition", "proverb_about_misplaced_needs", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    475: item("A wedding is one night, but its preparation takes a year.", "결혼식은 하룻밤이지만 준비에는 1년이 걸려.", "A2", 30, "family_relationships", "wedding_preparation_proverb", "proverb", "description", "neutral", "low"),
    476: item("Real beauty is the beauty of one's deeds.", "진짜 아름다움은 행동의 아름다움이야.", "A2", 25, "culture_tradition", "proverb_about_character", "proverb", "opinion", "neutral", "low"),
    477: item("He hit me and cried, then got ahead of me and complained first.", "그가 나를 때리고 울더니, 먼저 가서 나를 두고 하소연했어.", "B1", 43, "crime_safety", "proverb_about_reversal_of_blame", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    478: item("Whoever gets ahead of you by a night gets ahead of you by a trick.", "누가 하룻밤 먼저 앞서면 꾀에서도 너를 앞서.", "B1", 44, "culture_tradition", "proverb_about_advantage_and_cunning", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    479: item("The bride is praised by her mother, or by her own mouth.", "신부는 어머니가 칭찬하거나 자기 입으로 칭찬해.", "B1", 38, "family_relationships", "proverb_about_self_praise", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    480: item("The miser's money is eaten by others at ease.", "구두쇠의 돈은 다른 사람들이 편하게 먹어 치워.", "B1", 40, "finance", "proverb_about_miserliness", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    481: item("Whoever relies on his in-law sleeps without dinner; the exact kinship term is context-dependent.", "인척에게 의지하는 사람은 저녁도 못 먹고 자. 정확한 친족 관계는 문맥에 따라 달라질 수 있어.", "B2", 50, "family_relationships", "proverb_about_dependence", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    482: item("The river went away, and he found it dry.", "강물이 빠지고 나서 그는 강바닥이 말라 있는 것을 발견했어.", "A2", 28, "travel", "proverb_about_missed_opportunity", "proverb", "description", "neutral", "low"),
    483: item("Before you buy a house, buy a neighbor.", "집을 사기 전에 이웃을 사.", "A2", 30, "housing", "proverb_about_neighbors", "proverb", "suggestion", "neutral", "medium", "idiom_culture|source_ambiguity", "flagged"),
    484: item("A single one found its pair.", "짝 하나가 자기 짝을 찾았어.", "A2", 22, "family_relationships", "proverb_about_matching", "proverb", "description", "neutral", "low"),
    485: item("Whoever loved me did not build me a palace, and whoever hated me did not build me a grave. The source contains a trailing annotation marker.", "나를 사랑한 사람은 나에게 궁전을 지어 주지 않았고, 나를 미워한 사람은 나에게 무덤을 지어 주지 않았어. 원문 끝에는 주석 표지가 들어 있어.", "C1", 72, "culture_tradition", "proverb_about_love_and_hate", "proverb", "opinion", "mixed", "high", "idiom_culture|source_ambiguity|source_corruption", "flagged"),
    486: item("Whoever sold you for beans, sell him with their husks. The source contains a trailing annotation marker.", "누가 너를 콩 몇 알에 팔았다면, 너도 콩 껍질로 그를 팔아. 원문 끝에는 주석 표지가 들어 있어.", "B2", 56, "culture_tradition", "proverb_about_reciprocity", "proverb", "suggestion", "colloquial", "high", "idiom_culture|source_ambiguity|source_corruption", "flagged"),
    487: item("Whoever loves us, we love, and we place him above our head like a turban.", "우리를 사랑하는 사람은 우리도 사랑하고, 머리에 두르는 터번처럼 소중히 여겨.", "B1", 42, "family_relationships", "proverb_about_reciprocal_affection", "proverb", "opinion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    488: item("Whoever hates us, we hate, even until the Day of Judgment. The source contains a trailing annotation marker.", "우리를 미워하는 사람은 우리도 미워해, 심판의 날까지라도. 원문 끝에는 주석 표지가 들어 있어.", "B1", 45, "culture_tradition", "proverb_about_reciprocal_hostility", "proverb", "opinion", "colloquial", "high", "idiom_culture|source_ambiguity|source_corruption", "flagged"),
    489: item("Even if your friend is honey, do not lick it all.", "친구가 꿀처럼 달더라도 전부 핥아 먹지는 마.", "A2", 28, "family_relationships", "proverb_about_boundaries", "proverb", "suggestion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    490: item("What is yours is yours, and what is not yours will tire you.", "네 것인 것은 네 것이고, 네 것이 아닌 것은 너를 지치게 해.", "A2", 27, "culture_tradition", "proverb_about_belonging", "proverb", "description", "neutral", "low"),
    491: item("Do good and forget it. The source contains a leading annotation marker.", "선행을 하고 그것을 잊어. 원문 앞에는 주석 표지가 들어 있어.", "A2", 25, "culture_tradition", "proverb_about_charity", "proverb", "suggestion", "neutral", "medium", "idiom_culture|source_ambiguity|source_corruption", "flagged"),
    492: item("The mourning ceremony is large, but the dead person is only a mouse; the world is judged by faces, while the hereafter is judged by deeds.", "조문 행사는 크지만 죽은 사람은 쥐일 뿐이야. 세상은 얼굴로 판단하고, 내세는 행동으로 판단해.", "C1", 76, "culture_tradition", "proverb_about_appearance_and_deeds", "proverb", "opinion", "mixed", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    493: item("The children of a bitch are all dogs.", "암캐의 새끼들은 모두 개야.", "B1", 38, "family_relationships", "proverb_about_inherited_traits", "proverb", "opinion", "offensive", "high", "idiom_culture|source_ambiguity", "flagged"),
    494: item("The cat teaches its father to jump. Sleep with the chickens and wake up crowing.", "고양이가 자기 아버지에게 뛰는 법을 가르쳐. 닭들과 함께 자면 아침에 꼬꼬댁하며 일어나.", "B2", 54, "family_relationships", "proverb_about_reversed_expertise_and_habits", "proverb", "description", "colloquial", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    495: item("The camel laughs at its brother's hump and forgets its own hump.", "낙타가 형제의 혹을 비웃으면서 자기 혹은 잊어버려.", "A2", 30, "family_relationships", "proverb_about_hypocrisy", "proverb", "description", "neutral", "low"),
    496: item("In its mother's eyes, the beetle is a gazelle.", "어미의 눈에는 풍뎅이도 가젤이야.", "A2", 27, "family_relationships", "proverb_about_parental_bias", "proverb", "description", "neutral", "low"),
    497: item("The mourning ceremony is large, but the dead person is a mouse.", "조문 행사는 크지만 죽은 사람은 쥐야.", "A2", 32, "culture_tradition", "proverb_about_overstatement", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    498: item("The son of a mouse is a digger.", "쥐의 아들은 굴을 파는 사람이야.", "A2", 25, "family_relationships", "proverb_about_inherited_traits", "proverb", "description", "neutral", "low"),
    499: item("The wolf needs only the lamenter, and the blind person needs only kohl; the exact term for the wolf's need is unclear.", "늑대에게 필요한 것은 곡하는 사람뿐이고, 눈먼 사람에게 필요한 것은 콜뿐이야. 늑대에게 필요한 것을 가리키는 정확한 말은 불분명해.", "B2", 56, "culture_tradition", "proverb_about_mismatched_needs", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    500: item("Like a rooster: it knows all the times, but it does not pray.", "수탉처럼 모든 시간을 알지만 기도는 하지 않아.", "B1", 38, "religion", "proverb_about_knowledge_without_practice", "proverb", "opinion", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    501: item("When the wolf saw that the bunch of grapes was far away, it said they were sour.", "늑대는 포도송이가 멀리 있는 것을 보고 시다고 말했어.", "A2", 28, "food", "proverb_about_sour_grapes", "proverb", "description", "neutral", "low"),
    502: item("When the cat cannot reach the piece of fat, it says the fat is rotten.", "고양이는 비계 조각에 닿지 못하면 그 비계가 상했다고 말해.", "B1", 40, "food", "proverb_about_sour_grapes", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    503: item("The camel went away and left nothing but dung.", "낙타가 떠나고 똥만 남겼어.", "A2", 25, "travel", "proverb_about_legacy", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    504: item("Until the crow grows gray.", "까마귀가 회색이 될 때까지.", "A2", 22, "culture_tradition", "proverb_about_impossibility", "proverb", "description", "neutral", "low"),
    505: item("One eye watches the cat while the other fries the sardines.", "한쪽 눈은 고양이를 지켜보고 다른 쪽 눈은 정어리를 튀겨.", "B1", 42, "food", "proverb_about_divided_attention", "proverb", "description", "colloquial", "medium", "idiom_culture|source_ambiguity", "flagged"),
    506: item("What the wolf read, the Sloughi memorized.", "늑대가 읽은 것을 슬루기 개가 외웠어.", "B1", 40, "culture_tradition", "proverb_about_learning_and_memory", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    507: item("The person bitten by a snake is afraid of a rope.", "뱀에게 물린 사람은 밧줄도 무서워해.", "A2", 25, "health", "proverb_about_trauma_and_caution", "proverb", "description", "neutral", "low"),
    508: item("Do not be impressed by the oleander's flowers casting shadows in the river, and do not be impressed by a girl's beauty until you see her deeds.", "강물에 그림자를 드리운 협죽도 꽃에 현혹되지 말고, 그 소녀의 행동을 보기 전에는 아름다움에도 현혹되지 마.", "C1", 70, "culture_tradition", "proverb_about_appearance_and_character", "proverb", "warning", "mixed", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    509: item("Working with Christians is better than sitting in loss. Cooperation—even with Christians—is better than sitting in loss; working and earning a living, even with Christians, is better than unemployment and idleness. The parenthetical explanation is preserved as source context.", "기독교인들과 일하는 것이 손해를 보며 앉아 있는 것보다 나아. 기독교인들과라도 협력하는 것이 손해를 보며 앉아 있는 것보다 낫고, 기독교인들과라도 일해서 생계를 잇는 것이 실업과 빈둥거림보다 낫다는 말이야. 괄호 안의 설명도 원문 맥락으로 보존해.", "C1", 78, "work", "proverb_about_work_over_unemployment", "proverb", "opinion", "mixed", "high", "idiom_culture|long_source|source_ambiguity", "flagged"),
    510: item("He came running and left nine behind; the exact verb and implication are unclear.", "그가 달려와서 아홉을 남겼어. 정확한 동사와 뜻은 불분명해.", "B2", 50, "daily_life", "proverb_about_unintended_consequences", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    511: item("He fled from people who cut hands and fell among people who cut heads.", "그는 손을 자르는 사람들에게서 도망쳤다가 머리를 자르는 사람들 사이에 떨어졌어.", "B2", 58, "crime_safety", "proverb_about_worse_danger", "proverb", "description", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged"),
    512: item("He came to apply kohl to her eyes, but he blinded her. It describes someone who comes to fix something and makes it worse; the source includes an explanatory colloquial note.", "그는 그녀의 눈에 콜을 발라 주러 왔지만 그녀를 눈멀게 했어. 무언가를 고치러 온 사람이 오히려 더 망치는 상황을 말하며, 원문에는 구어체 설명이 덧붙어 있어.", "B2", 58, "daily_life", "proverb_about_worsening_a_problem", "proverb", "description", "mixed", "high", "idiom_culture|source_ambiguity", "flagged"),
}


def validate(source):
    by = {row["sentno"]: row for row in source}
    expected = [str(index) for index in range(TARGET_START, TARGET_END + 1)]
    if sorted(RAW) != list(range(TARGET_START, TARGET_END + 1)):
        raise RuntimeError("raw_coverage")
    rows = []
    for sentno in expected:
        payload = {
            **RAW[int(sentno)],
            "latin": latinize(by[sentno]["arabic_original"]),
            "source_uid": by[sentno]["source_uid"],
            "sentno": sentno,
        }
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
        writer = csv.DictWriter(
            handle,
            fieldnames=BATCH_FIELDS,
            delimiter="\t",
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "row_count": 64,
        "fields": [*EMPTY_FIELDS, "processing_flags", "enrichment_state"],
        "prompt_version": PROMPT_VERSION,
        "source_dependency": "canonical_source_only",
        "morphology_dependency": False,
        "darija_modified": False,
        "schema_version": "1.1.0",
        "generated_at": generated_at,
        "review_state": "generated",
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scores = [int(row["difficulty_score"]) for row in rows]
    flags = Counter(flag for row in rows if row["processing_flags"] for flag in row["processing_flags"].split("|"))
    report = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "base_commit": BASE_COMMIT,
        "sentno_start": TARGET_START,
        "sentno_end": TARGET_END,
        "target_rows": 64,
        "draft_rows": sum(row["enrichment_state"] == "draft" for row in rows),
        "flagged_rows": sum(row["enrichment_state"] == "flagged" for row in rows),
        "flagged_row_sentnos": [row["sentno"] for row in rows if row["enrichment_state"] == "flagged"],
        "processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in rows),
        "flag_counts": dict(sorted(flags.items())),
        "difficulty_stats": {
            "min": min(scores),
            "max": max(scores),
            "mean": round(statistics.mean(scores), 2),
            "median": statistics.median(scores),
        },
        "required_linguistic_fields": 64 * len(EMPTY_FIELDS),
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
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
