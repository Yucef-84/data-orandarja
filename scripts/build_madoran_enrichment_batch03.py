"""Build the source-only MADOran enrichment batch for Sentno 129..192."""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from datetime import datetime, timezone

from scripts.apply_madoran_enrichment_batch import CONTROLLED_VALUES, CEFR_LEVELS
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
    PROCESSING_FLAG_VALUES,
    ROOT,
    SOURCE_OUT,
    read_tsv,
    source_gate,
)
from scripts.validate_madoran_enrichment import check_layer_contract


BATCH_ID = "MADORAN-ENRICH-003"
BASE_COMMIT = "f0f7088"
PROMPT_VERSION = "madoran-source-enrichment-v3"
TARGET_START = 129
TARGET_END = 192
BATCH_DIR = ROOT / "data" / "master" / "enrichment" / "batches"
BATCH_OUT = BATCH_DIR / "batch03_sentno_0129_0192.tsv"
MANIFEST_OUT = BATCH_DIR / "batch03_manifest.json"
QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_generation_qa.json"
BATCH_FIELDS = ["source_uid", "sentno", *EMPTY_FIELDS, "processing_flags", "enrichment_state"]


ITEMS = {
    129: {
      "latin": "3ammer rask mli7 w hada l3am choubiona.",
      "english": "Keep it well in your head: this year, the championship.",
      "korean": "잘 기억해 둬. 올해는 챔피언십이야.",
      "cefr_level": "B1",
      "difficulty_score": 40,
      "domain": "sports",
      "topic": "championship_chant",
      "genre": "song_lyric",
      "speech_act": "command",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    130: {
      "latin": "w haya haya dawrou hachbiba dawrou.",
      "english": "Come on, come on, turn around, young people, turn around.",
      "korean": "자, 자, 젊은이들아 돌아라, 돌아라.",
      "cefr_level": "A2",
      "difficulty_score": 25,
      "domain": "entertainment_music",
      "topic": "youth_chant",
      "genre": "song_lyric",
      "speech_act": "command",
      "register": "colloquial",
      "context_dependency": "low",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    131: {
      "latin": "whaya haya wfakkrouna byam zman.",
      "english": "Come on, come on, and remind us of the old days.",
      "korean": "자, 자, 옛날을 우리에게 다시 떠올려 줘.",
      "cefr_level": "A2",
      "difficulty_score": 28,
      "domain": "entertainment_music",
      "topic": "nostalgia_chant",
      "genre": "song_lyric",
      "speech_act": "command",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    132: {
      "latin": "whaya haya 3aytou lsowwara ysawrou.",
      "english": "Come on, come on, call the photographers so they take pictures.",
      "korean": "자, 자, 사진사들을 불러서 사진을 찍게 해.",
      "cefr_level": "A2",
      "difficulty_score": 27,
      "domain": "entertainment_music",
      "topic": "crowd_photographs",
      "genre": "song_lyric",
      "speech_act": "command",
      "register": "colloquial",
      "context_dependency": "low",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    133: {
      "latin": "whaya haya 9olnalkom fort w mazal.",
      "english": "Come on, come on; we told you, 'strong,' and still so.",
      "korean": "자, 자, 우리가 너희에게 '강하다'고 말했고, 여전히 그래.",
      "cefr_level": "A2",
      "difficulty_score": 30,
      "domain": "sports",
      "topic": "strength_chant",
      "genre": "song_lyric",
      "speech_act": "exclamation",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    134: {
      "latin": "3andna jomhour mrid f stad roubla mahboula.",
      "english": "We have a fanatical crowd in the stadium and a crazy 'roubla'; the meaning of 'roubla' is unclear in the source.",
      "korean": "우리에게는 경기장에 열광적인 관중이 있고 미친 듯한 'roubla'가 있어. 원문의 'roubla' 뜻은 분명하지 않아.",
      "cefr_level": "B2",
      "difficulty_score": 58,
      "domain": "sports",
      "topic": "stadium_crowd",
      "genre": "song_lyric",
      "speech_act": "description",
      "register": "slang",
      "context_dependency": "high",
      "processing_flags": "context_heavy|source_ambiguity",
      "enrichment_state": "flagged"
    },
    135: {
      "latin": "n7bes wla nzid wla sayi barkana.",
      "english": "Should I stop or continue, or is that it—enough for us?",
      "korean": "그만할까, 더 할까, 아니면 이제 됐어? 우리 이제 그만할까?",
      "cefr_level": "A2",
      "difficulty_score": 32,
      "domain": "entertainment_music",
      "topic": "chant_continuation",
      "genre": "song_lyric",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    136: {
      "latin": "ma3andnach lfid wmafinach lli yetbela.",
      "english": "We do not have 'lfid,' and there is no one among us who 'yetbela'; the exact meanings of these expressions are unclear.",
      "korean": "우리에게는 'lfid'가 없고 우리 중에는 'yetbela'하는 사람도 없다는 말인데, 이 표현들의 정확한 뜻은 분명하지 않아.",
      "cefr_level": "B2",
      "difficulty_score": 60,
      "domain": "sports",
      "topic": "supporter_identity",
      "genre": "song_lyric",
      "speech_act": "description",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    137: {
      "latin": "kitnoud t7seb 3id t9oul nta Barcelona.",
      "english": "When it gets going, you think it is a festival; you would say you were Barcelona.",
      "korean": "분위기가 달아오르면 축제인 줄 알 정도고, 마치 바르셀로나인 것 같아.",
      "cefr_level": "B1",
      "difficulty_score": 45,
      "domain": "sports",
      "topic": "stadium_atmosphere",
      "genre": "song_lyric",
      "speech_act": "description",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    138: {
      "latin": "ila rbe7na dza9at tetkhabel ga3 l7iya.",
      "english": "If we win, 'dza9at' go wild, all of 'l7iya'; the exact meanings of these expressions are unclear in the source.",
      "korean": "우리가 이기면 'dza9at'가 미쳐 날뛰고 'l7iya' 전체가 그렇다는 말인데, 이 표현들의 정확한 뜻은 원문만으로 분명하지 않아.",
      "cefr_level": "B2",
      "difficulty_score": 62,
      "domain": "sports",
      "topic": "victory_celebration",
      "genre": "song_lyric",
      "speech_act": "description",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    139: {
      "latin": "rroubla w 3alamat wcha n7kilek ya khouya.",
      "english": "The 'roubla' and the signs—what can I tell you, brother? The meaning of 'roubla' is unclear.",
      "korean": "'roubla'와 표식들, 형제여 내가 뭘 더 말하겠어? 'roubla'의 뜻은 분명하지 않아.",
      "cefr_level": "B2",
      "difficulty_score": 55,
      "domain": "sports",
      "topic": "supporter_display",
      "genre": "song_lyric",
      "speech_act": "exclamation",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    140: {
      "latin": "nnar 3liha 9dat hiya mmou 3iniya.",
      "english": "The line says 'the fire on her/it caught' and continues with 'hiya mmou 3iniya'; the exact meaning of the full line is unclear.",
      "korean": "'그것/그녀에게 불이 붙었다'는 표현 뒤에 'hiya mmou 3iniya'가 이어지지만, 전체 구절의 정확한 뜻은 분명하지 않아.",
      "cefr_level": "C1",
      "difficulty_score": 72,
      "domain": "entertainment_music",
      "topic": "ambiguous_chant_line",
      "genre": "song_lyric",
      "speech_act": "description",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    141: {
      "latin": "7naya aloufat saknatna hadi ljniya.",
      "english": "We are thousands; this jinn has taken up residence in us.",
      "korean": "우리는 수천 명이야. 이 진이 우리 안에 들어와 살고 있어.",
      "cefr_level": "B2",
      "difficulty_score": 58,
      "domain": "sports",
      "topic": "supporter_fervor",
      "genre": "song_lyric",
      "speech_act": "description",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    142: {
      "latin": "3ammer rask mli7 w hada l3am choubiona.",
      "english": "Keep it well in your head: this year, the championship.",
      "korean": "잘 기억해 둬. 올해는 챔피언십이야.",
      "cefr_level": "B1",
      "difficulty_score": 40,
      "domain": "sports",
      "topic": "championship_chant",
      "genre": "song_lyric",
      "speech_act": "command",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    143: {
      "latin": "aya men ba3d aya.",
      "english": "Okay, then after that, okay.",
      "korean": "그래, 그다음에, 그래.",
      "cefr_level": "A1",
      "difficulty_score": 10,
      "domain": "daily_life",
      "topic": "discourse_transition",
      "genre": "conversation",
      "speech_act": "narration",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy",
      "enrichment_state": "draft"
    },
    144: {
      "latin": "a rabbi sidi 3yit bzaf ana wallah chkwa lrabbi men3ert 3lach darou lycee? loukan ghir tedreb zenzla machi khir? wga3 lkolijat yti7ou?",
      "english": "Oh my Lord, I am very tired; by God, my complaint is to God. I do not know why they made the high school. Would it not be better if an earthquake struck and all the middle schools fell down?",
      "korean": "주님, 정말 너무 지쳤어. 맹세코 하소연할 곳은 신뿐이야. 왜 고등학교를 만들었는지 모르겠어. 차라리 지진이 나서 중학교들이 전부 무너지는 게 낫지 않을까?",
      "cefr_level": "B2",
      "difficulty_score": 62,
      "domain": "education",
      "topic": "school_frustration",
      "genre": "conversation",
      "speech_act": "complaint",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    145: {
      "latin": "khti mdina jdida 7ta wa7ed ma ra7lha ana ro7tlha 9bel Ramadan bghit nterte9 lghachi bzaf.",
      "english": "Sister, Medina Jdida—nobody goes there. I went there before Ramadan and felt like I was going to burst; there were so many people.",
      "korean": "언니, 메디나 즈디다에는 아무도 안 간다고 하는데, 나는 라마단 전에 거기 갔다가 사람이 너무 많아서 터질 것 같았어.",
      "cefr_level": "B2",
      "difficulty_score": 56,
      "domain": "shopping",
      "topic": "crowded_market_area",
      "genre": "conversation",
      "speech_act": "complaint",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "draft"
    },
    146: {
      "latin": "w les agressions ma telbsi ni dheb ni walou w ma tbaynich portable ta3ek w choufi iyala ykhounouk.",
      "english": "And because of assaults, do not wear gold or anything, do not show your phone, and watch out in case they rob you.",
      "korean": "그리고 습격이나 강도 때문에 금이나 다른 걸 착용하지 말고, 휴대전화도 드러내지 말고, 혹시 털릴 수 있으니 조심해.",
      "cefr_level": "B1",
      "difficulty_score": 45,
      "domain": "crime_safety",
      "topic": "street_safety",
      "genre": "conversation",
      "speech_act": "warning",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    147: {
      "latin": "houma les jeunes ygressiwk ila chafouk tbayni fi douk lkhwatem w lmsayes w raki 3arfa bsah la makan ghir lkhir inchallah.",
      "english": "It is the young people who assault you if they see you showing those rings and bracelets, and you know that; but hopefully there will only be good, God willing.",
      "korean": "젊은 사람들이 네가 그런 반지와 팔찌를 드러내는 걸 보면 덤빌 수 있고, 너도 그걸 알고 있잖아. 그래도 신의 뜻대로 좋은 일만 있기를 바라.",
      "cefr_level": "B1",
      "difficulty_score": 47,
      "domain": "crime_safety",
      "topic": "theft_precautions",
      "genre": "conversation",
      "speech_act": "warning",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    148: {
      "latin": "wi Souad charki dayra fiha kach 3id? ya wedi l3id rah ghir houwa ana chrit serwal jeans w 2 ta3 les body chabin ba9ili ghi sbat ghadi ntla3 lblad wla lchoubo bah nchri cha 9olti rahom ghalyin wla la?",
      "english": "Yes, Souad, 'charki'—are you acting as if there is some Eid? Come on, Eid is right there. I bought jeans and two nice bodysuits; I only have shoes left. I am going up to town or to 'lchoubo' to buy them. What do you think, are they expensive or not?",
      "korean": "응, 수아드, 'charki'라는 표현은 뜻이 분명하지 않아. 무슨 명절이라도 있는 것처럼 준비하는 거야? 아이고, 명절이 바로 코앞이잖아. 나는 청바지와 예쁜 보디 두 개를 샀고 이제 신발만 남았어. 시내나 'lchoubo'에 가서 살 건데, 어떻게 생각해? 비싸 아니야?",
      "cefr_level": "B2",
      "difficulty_score": 62,
      "domain": "shopping",
      "topic": "clothing_shopping",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "code_switching|long_source|source_ambiguity",
      "enrichment_state": "draft"
    },
    149: {
      "latin": "chwiya rahom ghalyin nti saoumi w choufi ma t7assich tti7i fi 7aja chaba 3inek hiya mizank.",
      "english": "They are a little expensive. Bargain and look around; you might come across something nice. Your eye is your measure.",
      "korean": "조금 비싸. 흥정하면서 둘러봐. 괜찮은 물건을 발견할 수도 있어. 네 눈이 곧 기준이야.",
      "cefr_level": "B1",
      "difficulty_score": 38,
      "domain": "shopping",
      "topic": "bargaining_advice",
      "genre": "conversation",
      "speech_act": "suggestion",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    150: {
      "latin": "lyoum dik Dalila 9eblet tetzawaj b wa7ed deja metzawaj w 9abla belli chra3 7allel reb3a bsah koun rajelha yebghi yetzawaj 3liha t9oulou chra3 ta3rfouh ghir f nsa cha wala tetzawaj 3liya ghir hadi li ma tserach arwa7 nta w fham.",
      "english": "Today that Dalila agreed to marry a man who is already married, and she accepts that religious law permits four wives. But if her own husband wanted to marry another woman, she would tell him, 'Do you only know religious law when it comes to women? What, you are going to marry another woman over me? That is the one thing that will not happen.' You figure it out.",
      "korean": "오늘 그 달릴라는 이미 결혼한 남자와 결혼하기로 했고, 종교법에서 네 명까지 허용한다는 것도 받아들였어. 그런데 자기 남편이 또 다른 여자와 결혼하려 하면 '종교법은 여자 문제에서만 아는 거야? 뭐라고, 나를 두고 또 결혼한다고? 그것만큼은 절대 안 돼'라고 할 거야. 네가 알아서 이해해.",
      "cefr_level": "C1",
      "difficulty_score": 72,
      "domain": "family_relationships",
      "topic": "polygamy_double_standard",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "code_switching|context_heavy|idiom_culture|long_source",
      "enrichment_state": "draft"
    },
    151: {
      "latin": "sma7ili khti baghi nse9sik hadi hiya jami3a ta3 3oloum w teknologia isto? wah hadi hiya jami3a 7aja.",
      "english": "Excuse me, sister, I want to ask you: is this the University of Science and Technology, ISTO? Yes, this is the university; the final word 'haja' is unclear.",
      "korean": "실례해요, 누나. 하나 물어보려고 하는데 여기가 과학기술대학교 ISTO예요? 응, 여기가 그 대학이야. 마지막의 'haja'라는 말은 뜻이 분명하지 않아.",
      "cefr_level": "B1",
      "difficulty_score": 42,
      "domain": "education",
      "topic": "university_directions",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "draft"
    },
    152: {
      "latin": "wallah kbira Mesbah, rani ndour hna 3and jami3a nse9si hakka, makan ch ga3 li bgha y9ouli, surtout chiret li n9oulha, meskina t7chem hakka w ana nkhaf.",
      "english": "The opening phrase 'kbira Mesbah' is unclear. I have been going around here by the university asking like this, and nobody wanted to tell me, especially the girls; when I ask one, the poor girl gets shy like that, and I get afraid.",
      "korean": "첫 구절 'kbira Mesbah'의 뜻은 분명하지 않아. 나는 여기 대학 주변을 돌아다니며 이렇게 물어봤는데 아무도 말해 주려고 하지 않았어. 특히 여자애들에게 물으면 불쌍하게도 부끄러워하고, 나도 겁이 나.",
      "cefr_level": "B2",
      "difficulty_score": 58,
      "domain": "education",
      "topic": "asking_on_campus",
      "genre": "conversation",
      "speech_act": "narration",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "code_switching|context_heavy|source_ambiguity",
      "enrichment_state": "draft"
    },
    153: {
      "latin": "la ma fiha walou makan ch mochkil se9sit jami3a hayla jami3a.",
      "english": "No, there is nothing wrong with it, no problem. You asked about the university? It is a great university.",
      "korean": "아니, 아무 문제 없어. 괜찮아. 대학에 대해 물어본 거야? 아주 좋은 대학이야.",
      "cefr_level": "A2",
      "difficulty_score": 27,
      "domain": "education",
      "topic": "university_reassurance",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    154: {
      "latin": "ta3 cha ghadi ykharjou menha had jami3a ghir mkhakh bayna ghadi tkhrouji 7aja kbira ntiya.",
      "english": "What is going to come out of this university? Nothing but brains. Clearly, you are going to become something important.",
      "korean": "이 대학에서 뭐가 나오겠어? 머리 좋은 사람들뿐이지. 너도 분명 크게 될 거야.",
      "cefr_level": "B1",
      "difficulty_score": 42,
      "domain": "education",
      "topic": "academic_encouragement",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "draft"
    },
    155: {
      "latin": "khouya nta baghi tehder ma rakch baghi tse9si. machi telephone rah yssoni la? la khouya ma 3andich telephone. ana 9olt 7ess ta3 telephone. sa7a baghi nse9sik ma dayrinlekoum transport hna.",
      "english": "Brother, you just want to talk; you do not really want to ask something. 'Isn't that a phone ringing?' 'No, brother, I don't have a phone.' 'I thought I heard a phone. Okay, I want to ask you: don't they provide transport for you here?'",
      "korean": "오빠, 그냥 말하고 싶은 거지 정말 뭘 물으려는 건 아니잖아. '전화 울리는 거 아니야?' '아니, 나 전화 없어.' '나는 전화 소리인 줄 알았어. 좋아, 하나 물어볼게. 여기서는 너희에게 교통편을 제공하지 않아?'",
      "cefr_level": "B2",
      "difficulty_score": 60,
      "domain": "education",
      "topic": "university_transport",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "code_switching|context_heavy|long_source",
      "enrichment_state": "draft"
    },
    156: {
      "latin": "3lach tkhammem 3lina nta? drouk rani nse9si hada makan ma fih walou. aya safa wallah kbira jami3a hna. ma sebt ma nehder.",
      "english": "The wording is partly unclear: 'Why are you thinking about us? I am asking now; this place has nothing.' Then: 'Okay, that's it. By God, the university here is big. I couldn't find anything to say.'",
      "korean": "표현 일부가 분명하지 않아. '왜 우리 생각을 하는 거야? 지금 내가 묻고 있잖아. 여기는 아무것도 없어.'라고 한 뒤, '그래, 됐어. 맹세코 여기 대학은 크네. 무슨 말을 해야 할지 못 찾겠어.'라고 이어져.",
      "cefr_level": "B2",
      "difficulty_score": 60,
      "domain": "education",
      "topic": "awkward_campus_conversation",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy|source_ambiguity",
      "enrichment_state": "draft"
    },
    157: {
      "latin": "3labalek men win rani jay.",
      "english": "Do you know where I am coming from?",
      "korean": "내가 어디서 오는 길인지 알아?",
      "cefr_level": "A1",
      "difficulty_score": 15,
      "domain": "daily_life",
      "topic": "origin_question",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "low",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    158: {
      "latin": "khassek 7aja? ma khasni walou khasni ntiya b sara7a.",
      "english": "'Do you need anything?' 'I don't need anything; I need you, honestly.'",
      "korean": "'뭐 필요한 거 있어?' '아무것도 필요 없어. 솔직히 나는 네가 필요해.'",
      "cefr_level": "A2",
      "difficulty_score": 25,
      "domain": "daily_life",
      "topic": "flirting",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    159: {
      "latin": "ana?",
      "english": "Me?",
      "korean": "나?",
      "cefr_level": "A1",
      "difficulty_score": 5,
      "domain": "daily_life",
      "topic": "surprised_response",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy",
      "enrichment_state": "draft"
    },
    160: {
      "latin": "wah wallah 3jbetini nas mla7 3a9la.",
      "english": "Yes, by God, I like you. You seem like a good, sensible person.",
      "korean": "응, 맹세코 네가 마음에 들어. 좋은 사람이고 생각도 깊어 보여.",
      "cefr_level": "A2",
      "difficulty_score": 28,
      "domain": "daily_life",
      "topic": "flirting",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    161: {
      "latin": "yselmek.",
      "english": "May God keep you safe.",
      "korean": "신이 너를 지켜 주시길.",
      "cefr_level": "A1",
      "difficulty_score": 12,
      "domain": "daily_life",
      "topic": "polite_response",
      "genre": "conversation",
      "speech_act": "thanks",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    162: {
      "latin": "9isach tkhrouji had lwe9t ah.",
      "english": "What time do you get out at this time, huh?",
      "korean": "이 시간에는 몇 시에 나가는 거야?",
      "cefr_level": "A2",
      "difficulty_score": 28,
      "domain": "daily_life",
      "topic": "departure_time",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    163: {
      "latin": "khouya cha rak t7awes exactement.",
      "english": "Brother, what exactly are you looking for?",
      "korean": "오빠, 정확히 뭘 찾고 있는 거야?",
      "cefr_level": "A2",
      "difficulty_score": 25,
      "domain": "daily_life",
      "topic": "asking_intention",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    164: {
      "latin": "ma rani n7awes walou b sara7a madam makan ni ghachi ni walou ana wallah ghi n9oulhalek 3labalek belli ana samata ana samet ha raki ted7ki bayna bent 7lal wallah.",
      "english": "Honestly, I am not looking for anything, since there are neither people nor anything here. By God, I will just tell you: you know I am annoying; I am a bore. Ah, you are laughing. Clearly you are a decent girl, by God.",
      "korean": "솔직히 나는 아무것도 찾는 게 없어. 여기에는 사람도 없고 아무것도 없으니까. 맹세코 그냥 말할게. 나 귀찮은 사람이고 재미없는 사람인 거 알지. 아, 웃고 있네. 보니까 정말 괜찮은 여자야.",
      "cefr_level": "B2",
      "difficulty_score": 62,
      "domain": "family_relationships",
      "topic": "flirting",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "slang",
      "context_dependency": "high",
      "processing_flags": "idiom_culture|long_source",
      "enrichment_state": "draft"
    },
    165: {
      "latin": "yselmek.",
      "english": "May God keep you safe.",
      "korean": "신이 너를 지켜 주시길.",
      "cefr_level": "A1",
      "difficulty_score": 12,
      "domain": "daily_life",
      "topic": "polite_response",
      "genre": "conversation",
      "speech_act": "thanks",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    166: {
      "latin": "bsah msrara.",
      "english": "But cheerful.",
      "korean": "그래도 즐거워 보여.",
      "cefr_level": "A2",
      "difficulty_score": 28,
      "domain": "daily_life",
      "topic": "personal_impression",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "draft"
    },
    167: {
      "latin": "khouya ma 3andek ma tekhdem ana kent ne9ra w drouk rani ray7a ldar.",
      "english": "Brother, don't you have anything to do? I was studying, and now I am going home.",
      "korean": "오빠, 할 일 없어? 나는 공부하고 있었고 이제 집에 가는 중이야.",
      "cefr_level": "A2",
      "difficulty_score": 30,
      "domain": "daily_life",
      "topic": "leaving_for_home",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    168: {
      "latin": "ana tani kent nekhdem w rani jay 3andek hnaya. 3labalek bay ani 9rib wa7ed chhar rani nji hna.",
      "english": "I was working too, and I am coming here to you. You know, 'bay ani,' I have been coming here for nearly a month; the expression 'bay ani' is unclear.",
      "korean": "나도 일하고 있었고 여기 너한테 오는 중이야. 거의 한 달째 여기 오고 있다는 말인데, 'bay ani'라는 표현의 정확한 뜻은 분명하지 않아.",
      "cefr_level": "B1",
      "difficulty_score": 45,
      "domain": "daily_life",
      "topic": "repeated_visits",
      "genre": "conversation",
      "speech_act": "information",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "draft"
    },
    169: {
      "latin": "chhar?",
      "english": "A month?",
      "korean": "한 달?",
      "cefr_level": "A1",
      "difficulty_score": 5,
      "domain": "daily_life",
      "topic": "surprised_response",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy",
      "enrichment_state": "draft"
    },
    170: {
      "latin": "mechtinich ga3 mechtinich?",
      "english": "The repeated expression 'mechtinich' is unclear in the source.",
      "korean": "반복된 'mechtinich'라는 표현의 뜻은 원문만으로 분명하지 않아.",
      "cefr_level": "B1",
      "difficulty_score": 48,
      "domain": "daily_life",
      "topic": "unclear_recognition_question",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    171: {
      "latin": "la jamais.",
      "english": "No, never.",
      "korean": "아니, 한 번도.",
      "cefr_level": "A1",
      "difficulty_score": 10,
      "domain": "daily_life",
      "topic": "negative_response",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    172: {
      "latin": "ana wallah la kent metmenni ne9ra hna. koun 9rit hna cha kent t9are3.",
      "english": "By God, I had wished to study here. If I had studied here, the phrase 'cha kent t9are3' is unclear in the source.",
      "korean": "맹세코 나는 여기서 공부하고 싶었어. 내가 여기서 공부했다면 이어지는 'cha kent t9are3'라는 구절의 정확한 뜻은 분명하지 않아.",
      "cefr_level": "B2",
      "difficulty_score": 58,
      "domain": "education",
      "topic": "studying_at_university",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    173: {
      "latin": "ha 9raya 9raya 9raya n9ablou rez9 wla 9raya. t9ar3i troli?",
      "english": "Study, study, study; the phrase 'n9ablou rez9 wla 9raya' is unclear. Are you waiting for the 'troli'?",
      "korean": "공부, 공부, 공부. 'n9ablou rez9 wla 9raya'라는 구절은 뜻이 분명하지 않아. 'troli'를 기다리는 거야?",
      "cefr_level": "B2",
      "difficulty_score": 62,
      "domain": "education",
      "topic": "waiting_after_study",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
    174: {
      "latin": "rani n9are3 transport ta3 jami3a.",
      "english": "I am waiting for the university transport.",
      "korean": "대학 교통편을 기다리고 있어.",
      "cefr_level": "A2",
      "difficulty_score": 24,
      "domain": "transport",
      "topic": "university_transport",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    175: {
      "latin": "ida ma jabouhech bras chbaniya ntir lsma w njiblek loto w njibha chaba 3la khatrek makan ch fiha hedra.",
      "english": "If they do not bring it, the phrase 'bras chbaniya' is unclear; I will fly to the sky, get you a car, and get a nice one for your sake—there is no question about it.",
      "korean": "그들이 그것을 가져오지 않으면 'bras chbaniya'라는 구절의 뜻은 분명하지 않아. 나는 하늘로 날아가서 너에게 차를 가져다주고, 너를 위해 좋은 걸로 가져올 거야. 두말할 것도 없어.",
      "cefr_level": "B2",
      "difficulty_score": 64,
      "domain": "transport",
      "topic": "offering_transport",
      "genre": "conversation",
      "speech_act": "suggestion",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "code_switching|idiom_culture|source_ambiguity",
      "enrichment_state": "flagged"
    },
    176: {
      "latin": "m9al9a? n9are3 m3ak.",
      "english": "Are you upset? I will wait with you.",
      "korean": "기분 안 좋아? 내가 같이 기다릴게.",
      "cefr_level": "A2",
      "difficulty_score": 22,
      "domain": "daily_life",
      "topic": "waiting_together",
      "genre": "conversation",
      "speech_act": "suggestion",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    177: {
      "latin": "ma3lich mdari n9are3 wa7di.",
      "english": "It's okay, I'm used to waiting alone.",
      "korean": "괜찮아, 나는 혼자 기다리는 데 익숙해.",
      "cefr_level": "A2",
      "difficulty_score": 24,
      "domain": "daily_life",
      "topic": "waiting_alone",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    178: {
      "latin": "ya ana samet wah la samet ne93od hna.",
      "english": "So, am I annoying, yes or no? I'll stay here; the exact connection of the final clause is unclear.",
      "korean": "그러니까 내가 귀찮은 사람이야, 아니야? 나는 여기 있겠다는 마지막 절의 정확한 연결은 분명하지 않아.",
      "cefr_level": "B1",
      "difficulty_score": 42,
      "domain": "family_relationships",
      "topic": "awkward_flirting",
      "genre": "conversation",
      "speech_act": "question",
      "register": "slang",
      "context_dependency": "high",
      "processing_flags": "context_heavy|source_ambiguity",
      "enrichment_state": "draft"
    },
    179: {
      "latin": "la makan ch problem n9are3 wa7di.",
      "english": "No, there's no problem; I'll wait alone.",
      "korean": "아니, 문제없어. 혼자 기다릴게.",
      "cefr_level": "A2",
      "difficulty_score": 22,
      "domain": "daily_life",
      "topic": "waiting_alone",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    180: {
      "latin": "la ma3lich. win teskni? teskni hna f Wahran? raki mhawda l la ville? ma 3andekch 7abba 3lek?",
      "english": "No, it's okay. Where do you live? Do you live here in Oran? Are you heading down to the city? Don't you have a piece of chewing gum?",
      "korean": "아니, 괜찮아. 어디 살아? 여기 오란에 살아? 시내로 내려가는 중이야? 껌 한 개 없어?",
      "cefr_level": "B1",
      "difficulty_score": 40,
      "domain": "daily_life",
      "topic": "personal_questions",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "code_switching",
      "enrichment_state": "draft"
    },
    181: {
      "latin": "nta rak baghi tehder w ana ma 3andich lwe9t rasi rah darni mel 9raya.",
      "english": "You just want to talk, and I don't have time; my head is hurting from studying.",
      "korean": "너는 그냥 말하고 싶은 거고, 나는 시간이 없어. 공부 때문에 머리가 아파.",
      "cefr_level": "B1",
      "difficulty_score": 38,
      "domain": "education",
      "topic": "study_fatigue",
      "genre": "conversation",
      "speech_act": "complaint",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    182: {
      "latin": "sa7a 9ouli khti sma7ili Allah yer7am chwabin sma7ili.",
      "english": "Okay, tell me, sister; excuse me. May God have mercy on 'chwabin'; that expression is culturally specific and its exact reference is unclear. Excuse me.",
      "korean": "그래, 말해 줘. 미안해. 'chwabin'에게 신의 자비가 있기를 바란다는 문화적 표현인데 정확히 누구를 가리키는지는 분명하지 않아. 미안해.",
      "cefr_level": "B1",
      "difficulty_score": 40,
      "domain": "daily_life",
      "topic": "polite_apology",
      "genre": "conversation",
      "speech_act": "apology",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "idiom_culture|source_ambiguity",
      "enrichment_state": "draft"
    },
    183: {
      "latin": "wah.",
      "english": "Yes.",
      "korean": "응.",
      "cefr_level": "A1",
      "difficulty_score": 3,
      "domain": "daily_life",
      "topic": "affirmative_response",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "low",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    184: {
      "latin": "baghi ghodwa nchallah n3ardek ftour.",
      "english": "Tomorrow, God willing, I want to invite you to 'ftour'; whether it means breakfast or another meal is not explicit in the source.",
      "korean": "내일 신의 뜻이라면 너를 'ftour'에 초대하고 싶어. 여기서 이것이 아침식사인지 다른 식사인지 원문만으로는 분명하지 않아.",
      "cefr_level": "A2",
      "difficulty_score": 32,
      "domain": "daily_life",
      "topic": "meal_invitation",
      "genre": "conversation",
      "speech_act": "suggestion",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture|source_ambiguity",
      "enrichment_state": "draft"
    },
    185: {
      "latin": "inchallah.",
      "english": "God willing.",
      "korean": "신의 뜻이라면.",
      "cefr_level": "A1",
      "difficulty_score": 8,
      "domain": "daily_life",
      "topic": "hopeful_response",
      "genre": "conversation",
      "speech_act": "answer",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "idiom_culture",
      "enrichment_state": "draft"
    },
    186: {
      "latin": "ya 9alet inchallah amli sir? aya ghodwa nchallah 3la 4 rani hna.",
      "english": "Ah, she said, 'God willing.' The phrase 'amli sir?' is unclear. Okay, tomorrow, God willing, at four I'll be here.",
      "korean": "아, 그녀가 '신의 뜻이라면'이라고 했어. 'amli sir?'라는 구절의 뜻은 분명하지 않아. 그래, 내일 신의 뜻이라면 4시에 여기 있을게.",
      "cefr_level": "B2",
      "difficulty_score": 58,
      "domain": "daily_life",
      "topic": "meeting_arrangement",
      "genre": "conversation",
      "speech_act": "information",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy|idiom_culture|source_ambiguity",
      "enrichment_state": "flagged"
    },
    187: {
      "latin": "sa7a ftourkom. f Wahran f sif fara7 w zwaj hadi mawakel hada haraj w 3ers hers ya loukan ma jach fih zgharid.",
      "english": "Enjoy your 'ftour.' In Oran in summer there is celebration and marriage, food and commotion, followed by the expression '3ers hers'; the final clause mentions ululations, but the exact relation of these phrases is unclear.",
      "korean": "'ftour' 잘 보내. 오란의 여름에는 기쁨과 결혼, 음식과 소란이 있고 이어서 '3ers hers'라는 표현이 나와. 마지막 절은 울림 소리를 언급하지만 이 구절들이 정확히 어떻게 연결되는지는 분명하지 않아.",
      "cefr_level": "C1",
      "difficulty_score": 70,
      "domain": "culture_tradition",
      "topic": "oran_wedding_customs",
      "genre": "conversation",
      "speech_act": "description",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy|idiom_culture|source_ambiguity",
      "enrichment_state": "flagged"
    },
    188: {
      "latin": "w f khref chi3a zwaj 3la 7waj. ha rwa7 n9oulek: ida bghit tekseb, akseb ard kbira, nhar sba tghannik. wla bghit tetzawaj, tetzawaj m3a mra kbira, nhar li teghre9 tdabber 3lik. w 3azeb ila 3wej bgha zwaj.",
      "english": "The opening phrase is unclear. Come, I'll tell you: if you want to acquire something, acquire a large piece of land; on a rainy day it can make you rich. If you want to marry, marry an older woman; when you get into trouble, she will find a way for you. The final phrase about a bachelor and marriage is also unclear.",
      "korean": "첫 구절은 뜻이 분명하지 않아. 자, 내가 말해 줄게. 뭔가를 마련하고 싶다면 큰 땅을 마련해. 비 오는 날에는 그게 너를 부자로 만들어 줄 수 있어. 결혼하고 싶다면 나이 든 여자와 결혼해. 네가 곤경에 빠지는 날 그녀가 방법을 찾아 줄 거야. 마지막의 총각과 결혼에 관한 구절도 뜻이 분명하지 않아.",
      "cefr_level": "C1",
      "difficulty_score": 76,
      "domain": "culture_tradition",
      "topic": "marriage_and_property_advice",
      "genre": "conversation",
      "speech_act": "opinion",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "idiom_culture|long_source|source_ambiguity",
      "enrichment_state": "flagged"
    },
    189: {
      "latin": "a Hazim?",
      "english": "Hazim?",
      "korean": "하지므?",
      "cefr_level": "A1",
      "difficulty_score": 8,
      "domain": "daily_life",
      "topic": "calling_someone",
      "genre": "conversation",
      "speech_act": "question",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy",
      "enrichment_state": "draft"
    },
    190: {
      "latin": "ah Hamid tla3 khouya tla3.",
      "english": "Ah, Hamid, come up, brother, come up.",
      "korean": "아, 하미드, 올라와, 형제여, 올라와.",
      "cefr_level": "A1",
      "difficulty_score": 15,
      "domain": "daily_life",
      "topic": "calling_someone",
      "genre": "conversation",
      "speech_act": "command",
      "register": "colloquial",
      "context_dependency": "medium",
      "processing_flags": "",
      "enrichment_state": "draft"
    },
    191: {
      "latin": "sba7 lkhir Si Hazim aw khouya wallah la rak 3ajebni wallah rak mnawwer rak tcha3el ya der Hazim khouya dik 9adiya. ta3ach had l9adiya?",
      "english": "Good morning, Si Hazim. Brother, by God, I like you; by God, you're glowing, you're shining. The phrase 'ya der Hazim' is unclear, then it mentions 'that matter.' 'What matter is this?'",
      "korean": "좋은 아침이에요, 시 하지므. 형제여, 맹세코 당신이 마음에 들어요. 정말 환하고 빛나 보여요. 'ya der Hazim'이라는 구절은 뜻이 분명하지 않고 이어서 '그 일'을 언급해. '무슨 일인데?'",
      "cefr_level": "B2",
      "difficulty_score": 58,
      "domain": "daily_life",
      "topic": "greeting_and_matter",
      "genre": "conversation",
      "speech_act": "greeting",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "context_heavy|source_ambiguity",
      "enrichment_state": "draft"
    },
    192: {
      "latin": "kifach ta3ach had l9adiya rak baghi t9ar9ejni wla hadak bab li 9otlek 9sedhouli Hazim khouya.",
      "english": "What do you mean, 'what matter'? Are you trying to 't9ar9ejni' or what? That door I told you about—'9sedhouli' for me, Hazim, brother; the exact meanings of those expressions are unclear.",
      "korean": "'무슨 일이냐'니 무슨 말이야? 나한테 't9ar9ejni'하려는 거야? 내가 말했던 그 문 있잖아. 하지므 형제, 그걸 나한테 '9sedhouli'해 줘. 해당 표현들의 정확한 뜻은 분명하지 않아.",
      "cefr_level": "B2",
      "difficulty_score": 62,
      "domain": "housing",
      "topic": "door_request",
      "genre": "conversation",
      "speech_act": "request",
      "register": "colloquial",
      "context_dependency": "high",
      "processing_flags": "source_ambiguity",
      "enrichment_state": "flagged"
    },
}


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_items(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    source_by_sentno = {
        row["sentno"]: row["source_uid"]
        for row in source_rows
        if TARGET_START <= int(row["sentno"]) <= TARGET_END
    }
    expected = [str(number) for number in range(TARGET_START, TARGET_END + 1)]
    if list(map(str, sorted(ITEMS))) != expected:
        raise RuntimeError("batch_item_coverage_mismatch")
    if len(source_by_sentno) != len(expected):
        raise RuntimeError("source_target_coverage_mismatch")
    rows: list[dict[str, str]] = []
    for sentno in expected:
        payload = dict(ITEMS[int(sentno)])
        for field in EMPTY_FIELDS:
            value = str(payload.get(field, ""))
            if not value or value != value.strip() or any(char in value for char in "\t\r\n"):
                raise RuntimeError(f"invalid_value:{sentno}:{field}")
        if not payload["latin"].isascii():
            raise RuntimeError(f"latin_not_ascii:{sentno}")
        if payload["cefr_level"] not in CEFR_LEVELS:
            raise RuntimeError(f"invalid_cefr:{sentno}")
        score = payload["difficulty_score"]
        if not isinstance(score, int) or not 0 <= score <= 100:
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
    existing_rows = read_tsv(
        ROOT / "data" / "master" / "enrichment" / "madoran_sentence_enrichment.tsv"
    )
    existing_topics = {
        row["topic"]
        for row in existing_rows
        if row.get("topic") and not TARGET_START <= int(row["sentno"]) <= TARGET_END
    }
    topics = sorted({row["topic"] for row in rows})
    flag_counts = Counter(
        flag
        for row in rows
        if row["processing_flags"]
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
