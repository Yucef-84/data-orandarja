"""Apply HeadGPT-directed source-close corrections for MADOran Batch 19."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch19 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "22f07bc"
BATCH_ID = "MADORAN-ENRICH-019"
CORRECTION_ID = "MADORAN-ENRICH-019-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v19-correction-1"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch19_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch19_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch19_correction01_qa.json"
PROVENANCE_BEFORE = 16709

CORRECTIONS = {
    1157: {
        "processing_flags": "code_switching",
    },
    1161: {
        "korean": "압델카데르가 오고 있다고 하며 상대에게 무엇인가 가져다줄지 물어요.",
        "processing_flags": "",
        "enrichment_state": "draft",
    },
    1162: {
        "english": "Hawari thanks Abdelkader and says, ‘I am waiting for you.’ The response keeps the waiting direction rather than turning it into a competition or challenge.",
        "korean": "하와리가 압델카데르에게 고맙다고 하며 ‘너를 기다리고 있어’라고 말해요. 시합이나 도전으로 바꾸지 않고 기다리는 방향의 응답을 보존해요.",
        "topic": "waiting_for_an_invited_match",
        "speech_act": "answer",
    },
    1164: {
        "english": "The speaker begins the promised explanation of Wahrani speech, says it could take six years and still not finish, and says they will be direct and shorten the video. They explain that authentic Wahrani speech is now scarce because many people brought their own dialects and languages. The speaker preserves the lexical examples: at an old shop one asked for ljafil and likhia; an old formal outfit was shda, a hat was 7tta, and the speaker says rani drab fiha trakhia. For making someone fall, the source contrasts ndirlek krosh with the direct threat ndrbk nghashik. These surfaces and contrasts are retained rather than summarized away.",
        "korean": "화자는 약속한 와흐라니 말씨 설명을 시작하며 6년을 말해도 끝나지 않을 수 있어서 영상을 짧게 하겠다고 해요. 많은 사람이 자기 방언과 언어를 가져오면서 진짜 와흐라니 말이 이제는 드물어졌다고 설명해요. 예전 가게에서 ljafil과 likhia를 달라고 했다는 예, 전통적인 옷 shda와 모자 7tta, 그리고 rani drab fiha trakhia라는 표현을 보존해요. 누군가를 넘어뜨릴 때 ndirlek krosh라고 하지 않고 ndrbk nghashik이라고 한다는 대비도 그대로 남겨요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1165: {
        "english": "The speaker says Oran people used to call a tall man lar9w and a tall woman lar9a, and mentions bwrdw as another lexical example. They explain that the older Oran speech contained many Spanish elements because Oran had been a Spanish colony during the city's wider history under Ottoman Algeria; the Spanish and historical surfaces remain explicit.",
        "korean": "화자는 오랑에서 키 큰 남자를 lar9w, 키 큰 여자를 lar9a라고 불렀고 bwrdw도 또 다른 어휘 예라고 말해요. 오스만 시대 알제리의 역사 속에서 오랑이 스페인 식민지였기 때문에 예전 오랑 말에 스페인어 요소가 많았다고 설명하며 스페인어·역사 표면을 명시적으로 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1166: {
        "english": "The speaker says the Spanish presence in Oran was a strong population, calling it a fort population and a European urban presence in source-close terms; the exact lexical wording is retained without inventing an urban interpretation.",
        "korean": "화자는 오랑에 있었던 스페인인의 존재를 많은 인구이자 요새 인구, 유럽인들의 도시적 존재라는 원문 표현으로 설명해요. 정확한 어휘를 임의로 ‘유럽 도시 환경’이라고 확장하지 않고 불확실한 표면을 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|source_ambiguity",
    },
    1167: {
        "english": "The speaker recounts the Spanish departure, the Turkish period of about forty years, and the change in the name of Bey Mohamed el Kebir: first albai lk7l, then alkbir. They continue with French entry in 1831 and an 1834 Oran population count of 5,000, saying local inhabitants left for Mascara to join Emir Abdelkader's army and were afraid of the source-close surface liswghti t3 9wr. The named changes and uncertain surface are retained.",
        "korean": "화자는 스페인인의 철수와 약 40년의 튀르크 시기를 말하고, 바이 무함마드 엘 케비르의 명칭이 처음에는 albai lk7l이었다가 나중에 alkbir가 되었다고 설명해요. 1831년 프랑스의 진입과 1834년 오랑의 인구 5천 명을 이어 말하며, 주민들이 마스카라로 떠나 에미르 압델카데르의 군대에 합류했고 liswghti t3 9wr라는 불투명한 대상을 두려워했다고 해요. 명칭 변화와 불투명한 표면을 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1168: {
        "english": "The speaker gives the 1834 figures source-close: Oran had 5,000 inhabitants, including 1,042 Europeans and 3,958 others identified as Arabs, Kabyle people, and Jews. The European breakdown includes 340 French people and 316 Italians; the remaining categories continue in the next line. The numbers and population categories are all retained.",
        "korean": "화자는 1834년 수치를 원문에 가깝게 제시해요. 오랑 인구는 5,000명이고 그중 유럽인이 1,042명, 나머지 3,958명은 아랍인·카빌인·유대인으로 제시돼요. 유럽인 안에는 프랑스인 340명과 이탈리아인 316명이 포함되며, 나머지 범주는 다음 줄에서 이어져요. 모든 수치와 인구 범주를 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|long_source|source_ambiguity",
    },
    1169: {
        "english": "The speaker continues the 1834 population list with 266 Spanish people, 69 English people, 35 Germans, and 16 Portuguese people. They say this mixture made Oran a special city and gave it a local dialect spoken there; every number and group is retained.",
        "korean": "화자는 1834년 인구 목록을 이어 스페인인 266명, 영국인 69명, 독일인 35명, 포르투갈인 16명을 말해요. 이런 혼합으로 오랑이 특별한 도시가 되었고 그곳에서 쓰는 지역 방언이 생겼다고 하며 모든 수치와 집단을 보존해요.",
    },
    1170: {
        "english": "The speaker says each group had its own way of speaking, but Spanish was dominant at more than 60 percent of Wahrani speech. They explicitly name brsianw and kastianw as the Spanish varieties or labels involved; the percentage and labels remain source claims.",
        "korean": "화자는 각 집단이 자기들만의 말을 사용했지만 스페인어가 와흐라니 말의 60% 이상을 차지할 만큼 우세했다고 해요. 관련 스페인어 변종이나 명칭으로 brsianw와 kastianw를 명시하며 백분율과 명칭을 원문상의 주장으로 보존해요.",
    },
    1171: {
        "processing_flags": "idiom_culture",
        "enrichment_state": "draft",
    },
    1172: {
        "english": "The speaker lists Spanish, French, English, German, and Portuguese in Oran, saying Spanish is present in many places—bwkw blis, ‘many places’ in the source wording—and is much more prominent than the others.",
        "korean": "화자는 오랑에 스페인어·프랑스어·영어·독일어·포르투갈어가 모두 있다고 하며, 스페인어는 bwkw blis, 즉 여러 곳에 있고 다른 언어보다 훨씬 더 많다고 말해요.",
    },
    1173: {
        "processing_flags": "code_switching|idiom_culture",
        "enrichment_state": "draft",
    },
    1175: {
        "processing_flags": "code_switching",
        "enrichment_state": "draft",
    },
    1177: {
        "english": "The speaker says Oran is different from the rest of Algeria: the Spanish were there for about forty years, French rule across Algeria is stated as 133 years in the source, and Americans entered Oran on 10 November 1942. The speaker adds that many Americans died there; the Oran-versus-Algeria contrast and the stated number are retained as source claims.",
        "korean": "화자는 오랑이 알제리의 다른 지역과 다르다고 해요. 스페인인이 약 40년 동안 있었고, 알제리 전역의 프랑스 통치는 원문에서 133년으로 제시되며, 미국인은 1942년 11월 10일 오랑에 들어왔다고 말해요. 그곳에서 많은 미국인이 사망했다는 내용도 덧붙이며 오랑과 알제리의 대비와 수치를 원문상의 주장으로 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1178: {
        "english": "The speaker says Oran has an American cemetery, describes its grass or gazon and la croix, and says the cemetery still contains di swntan mwgh, a source-close surface for hundreds of dead or graves. The film-like comparison and all named surfaces are retained.",
        "korean": "화자는 오랑에 미국인 묘지가 있다고 하며 gazon, 즉 잔디와 la croix, 즉 십자가를 언급해요. 그 묘지에는 아직도 di swntan mwgh, 즉 수백 명의 사망자나 무덤을 가리키는 원문 표면이 있다고 말해요. 영화에서 본 것 같다는 비교와 명시된 표면을 모두 보존해요.",
    },
    1180: {
        "processing_flags": "code_switching",
        "enrichment_state": "draft",
    },
    1183: {
        "english": "In a long historical explanation, the speaker distinguishes the American entry into Oran from the entry into Algiers, using the source-close si ba baghai contrast. The French living in Algiers are associated with the Resistance and De Gaulle, while French people in Oran in the 1940s are described as Vichy collaborators under Marshal Pétain. The speaker says the American entry into Oran produced a grande bataille; the places, actors, political alignments, and battle are preserved.",
        "korean": "긴 역사 설명에서 화자는 미국인이 오랑에 들어온 것과 알제에 들어온 것을 si ba baghai라는 원문 대비로 구분해요. 알제에 살던 프랑스인은 레지스탕스와 드골 쪽으로, 1940년대 오랑의 프랑스인은 페탱 원수 아래 비시 협력자로 설명해요. 미국인의 오랑 진입으로 grande bataille, 즉 큰 전투가 일어났다고 하며 장소·행위자·정치적 관계와 전투를 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1184: {
        "english": "The speaker mentions the 30th or 34th American president and identifies Eisenhower, then says his son entered Oran swimming, with the following 3la mdagh surface left uncertain. The swimming action is retained and only the unclear remainder is marked uncertain.",
        "korean": "화자는 미국의 30대 또는 34대 대통령을 언급하고 아이젠하워라고 밝힌 뒤, 그의 아들이 수영해서 오랑에 들어왔다고 말해요. 뒤의 3la mdagh 표면은 불확실하게 두되 수영했다는 행위는 보존해요.",
    },
    1185: {
        "processing_flags": "code_switching",
        "enrichment_state": "draft",
    },
    1186: {
        "english": "The speaker compares regional words for boys: in eastern Algeria the source gives aldr, in the central Algiers region it gives drari, and in the west around Mascara and Oran it gives ghrawin. The three lexical examples are retained rather than generalized to ‘different terms.’",
        "korean": "화자는 소년을 가리키는 지역별 말을 비교해요. 알제리 동부에서는 aldr, 알제 중앙 지역에서는 drari, 마스카라와 오랑을 포함한 서부에서는 ghrawin이라고 한다고 하며 세 어휘 예를 일반화하지 않고 보존해요.",
    },
    1187: {
        "english": "The speaker says people in Oran call boys bzwz, linking it to the English plural ‘boys,’ and says the singular form is bz. The local plural and singular borrowing are both retained.",
        "korean": "화자는 오랑에서 소년들을 bzwz라고 부르며 영어 복수형 ‘boys’와 연결하고, 단수형은 bz라고 설명해요. 지역 복수형과 단수 차용형을 모두 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|source_ambiguity",
    },
    1188: {
        "english": "The speaker gives lasrirwr as an example of the object used to close a door and says Algerians generally call it 9fl. The two lexical surfaces are contrasted explicitly, with the French-derived or code-switched wording retained.",
        "korean": "화자는 문을 닫는 데 쓰는 물건의 예로 lasrirwr를 들고, 알제리 사람들은 보통 그것을 9fl이라고 부른다고 해요. 두 어휘 표면의 대비와 프랑스어 유래 또는 코드스위칭 표현을 명시적으로 보존해요.",
        "processing_flags": "code_switching|idiom_culture|source_ambiguity",
    },
    1191: {
        "processing_flags": "code_switching",
        "enrichment_state": "draft",
    },
    1192: {
        "english": "The speaker explains that the local form Akli comes from an English comparison like good, bad, and ugly: the ugly term was used for someone who was not handsome, and the borrowed form eventually became a personal name. The good/bad/ugly comparison and the name-development claim are retained.",
        "korean": "화자는 지역형 Akli가 good, bad, ugly처럼 좋은 것·나쁜 것·못생긴 것을 비교하는 영어 표현에서 왔다고 설명해요. 못생긴 사람, 즉 잘생기지 않은 사람을 가리키던 차용형이 결국 사람 이름이 되었다고 하며 good/bad/ugly 대비와 이름으로 발전한 주장을 보존해요.",
    },
    1193: {
        "processing_flags": "idiom_culture",
        "enrichment_state": "draft",
    },
    1194: {
        "processing_flags": "code_switching",
        "enrichment_state": "draft",
    },
    1195: {
        "english": "The speaker describes a person with a cart pulled by a donkey. When the cart owner wants the donkey to move, he says the western expression arii man, an English-derived command like ‘hurry, man.’ The animal, cart, and borrowed command are retained.",
        "korean": "화자는 당나귀가 끄는 수레를 가진 사람을 설명해요. 수레 주인이 당나귀를 움직이게 하려고 서부 지역 표현 arii man, 즉 ‘어서, 이봐’와 같은 영어 유래 명령을 한다고 해요. 동물·수레·차용 명령을 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|source_ambiguity",
    },
    1198: {
        "processing_flags": "",
        "enrichment_state": "draft",
    },
    1199: {
        "english": "In a long anecdote, the speaker describes donkey carts carrying vegetables, carts blocking narrow streets, and Americans arriving in jeeps and trucks in the Arab quarters. The Americans were afraid and shouted the English command hariwb or ariiwb man, meaning ‘move quickly.’ Local speakers reduced it in stages: arii, then arii ab, then arii mah, and finally ara, which became a cart-clearing expression. The speaker ends with the explicit teasing comment that they will explain ara but are not making that joke shorter; the full lexical chain and final turn are retained.",
        "korean": "긴 일화에서 화자는 채소를 싣는 당나귀 수레와 수레로 막힌 좁은 길, 아랍인 구역에 지프와 트럭을 타고 온 미국인을 설명해요. 미국인들은 두려워하며 ‘빨리 움직여’라는 뜻의 영어 명령 hariwb 또는 ariiwb man을 외쳤고, 현지인들은 이를 arii, arii ab, arii mah, 마지막으로 ara로 단계적으로 줄였다고 해요. ara는 수레에게 길을 비키라고 하는 표현이 되었으며, 화자는 마지막에 ara를 설명하겠지만 농담을 짧게 줄이고 싶지는 않다고 명시해요. 전체 변형 연쇄와 마지막 turn을 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1200: {
        "english": "The speaker says they will add a little-known detail and that the listener will understand shortly why it is little-known; the source does not add a request to wait.",
        "korean": "화자는 잘 알려지지 않은 이야기를 하나 더 하겠다며 왜 잘 알려지지 않았는지 곧 이해하게 될 것이라고 해요. 원문에 없는 ‘기다리라’는 요청은 추가하지 않아요.",
        "processing_flags": "",
        "enrichment_state": "draft",
    },
    1201: {
        "processing_flags": "code_switching",
        "enrichment_state": "draft",
    },
    1202: {
        "english": "The speaker remembers Harandou and says, may God have mercy on him and grant him peace. Harandou was an Oranian who lived in Oran and had a friend named Ben Yamina; the plural or separate-person direction is not collapsed into a single actor.",
        "korean": "화자는 하란두를 회상하며 하느님이 그에게 자비와 평안을 주시기를 빈다고 해요. 하란두는 오랑에서 살던 오랑 사람이고 벤 야미나라는 친구가 있었다고 하며, 복수 또는 별도의 인물 방향을 하란두 한 사람의 행위로 축소하지 않아요.",
        "processing_flags": "cefr_boundary|idiom_culture",
        "enrichment_state": "draft",
    },
    1203: {
        "english": "The source says Harandou played a guembri, while they moved around the markets in torn clothes and came barefoot, expressed in the local surface kafi. The guembri-playing actor is kept distinct from the plural people in the market description, and kafi is preserved.",
        "korean": "원문은 하란두가 금브리를 연주했다고 하면서, 그들은 찢어진 옷을 입고 시장을 돌아다녔고 맨발로 왔다고 지역 표현 kafi로 말해요. 금브리를 연주한 행위자와 시장을 다닌 복수 인물을 구분하고 kafi 표면을 보존해요.",
    },
    1204: {
        "english": "The speaker says they used to beg in Medina Jdida and sing about two small fish from the market, only lightly washed and fried in an oil pan. The song is known by local people, and the speaker says a full explanation would not end. The plural they-direction is retained rather than making Harandou the sole actor.",
        "korean": "화자는 그들이 메디나 즈디다에서 구걸하고 시장에서 가져온 작은 물고기 두 마리를 조금 씻어 기름 팬에 튀긴 이야기를 노래했다고 해요. 지역 사람들이 그 노래를 알고 있으며 자세히 설명하면 끝나지 않을 것이라고 말해요. 하란두 한 사람만의 행위로 바꾸지 않고 복수 행위자 방향을 보존해요.",
        "processing_flags": "code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1205: {
        "processing_flags": "idiom_culture",
        "enrichment_state": "draft",
    },
    1206: {
        "processing_flags": "",
        "enrichment_state": "draft",
    },
    1207: {
        "processing_flags": "code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1208: {
        "english": "The speaker moves to the Second World War period, 1939–1945, saying French forces called ben klbwn humiliated local people and recruited poor sons of the people to fight in European wars. The source then says this happened in the First World War, preserving its internal First/Second World War contradiction rather than smoothing it away. The French insult ben klbwn remains explicit.",
        "korean": "화자는 1939~1945년 2차 세계대전 시기로 넘어가 프랑스군이 ben klbwn이라고 불릴 만큼 현지인을 모욕했고, 가난한 민중의 아들들을 모집해 유럽 전쟁에 싸우게 했다고 말해요. 이어 원문은 이것이 1차 세계대전에서 일어났다고도 말하므로 1·2차 세계대전의 내부 모순을 매끈하게 제거하지 않고 보존해요. 프랑스군을 모욕적으로 부르는 ben klbwn 표현도 그대로 남겨요.",
        "register": "offensive",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1209: {
        "english": "The speaker explains that Arab families hid or did not register their sons, so many people from that period appear in the family book with a 1940 birth entry. They say this happened because some lived where there was no French administration, while many in large cities such as Oran, Mascara, and Tlemcen were registered. The speaker ends by asking, ‘Do you know why?’; the question is retained.",
        "korean": "화자는 아랍인 가족이 아들을 숨기거나 등록하지 않아 그 시기의 많은 사람이 가족 기록에 1940년생으로 적혔다고 설명해요. 프랑스 행정기관이 없는 곳에 살던 사람들이 있었기 때문이라고 하며, 오랑·마스카라·틀렘센 같은 큰 도시에서는 많은 사람이 등록되어 있었다고 해요. 마지막의 ‘왜인지 알아?’라는 질문도 보존해요.",
    },
    1210: {
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1211: {
        "english": "The speaker says the French took these young men so they could fight in Europe and put them into the army. A period of a week, a month, or six months taught them military matters, including lwghdsiri and wa7d antin as source-close training surfaces; the line ends incompletely at li9 t3lmhm lh. The incomplete ending is preserved and source_corruption is added.",
        "korean": "화자는 프랑스인이 이 젊은이들을 데려가 유럽에서 싸우게 하고 군대에 넣었다고 말해요. 일주일·한 달·6개월 동안 군사적인 일을 가르쳤으며 lwghdsiri와 wa7d antin이라는 원문 표면을 언급하고, 줄은 li9 t3lmhm lh에서 불완전하게 끝나요. 잘린 종결을 보존하고 source_corruption을 추가해요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity|source_corruption",
    },
    1213: {
        "english": "In a long derogatory anecdote, the speaker says the French took a poor rural man as a soldier and brought an intermediary, a bia3 or khrda who was ma iswash, to explain French to people who did not speak it. The intermediary mocked them, called them klb, drilled them in the barracks, and ordered afwnsi—move forward—while treating them like donkeys. The count ‘1, 2, harr’ is presented as the source of Harandou. The speaker then explains that Harandou became a mocking label for someone who looked unsophisticated; a clever person would have escaped, while kafi and the repeated harr command remain explicit. The insults, training turns, lexical chain, and uncertain etymology are preserved.",
        "korean": "긴 모욕적 일화에서 화자는 프랑스인이 가난한 시골 사람을 병사로 데려가고, 프랑스어를 못하는 사람들에게 설명하게 하려고 bia3 또는 khrda, 즉 ma iswash인 중개인을 데려왔다고 해요. 그 중개인은 사람들을 놀리고 klb라고 부르며 병영에서 훈련시키고, 당나귀처럼 대하면서 afwnsi, 즉 앞으로 가라고 명령해요. ‘1, 2, harr’라는 구령이 하란두의 유래로 제시되고, 하란두가 세련되지 못해 보이는 사람을 놀리는 말이 되었다고 설명해요. 영리했다면 도망쳤을 것이라는 말과 kafi, 반복되는 harr 구령도 명시적으로 보존하며 모욕·훈련 turn·어휘 연쇄·불확실한 어원을 그대로 남겨요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1214: {
        "english": "The speaker says the Americans' history has a large history and explains that the problem is not only the Wahrani dialect disappearing. They are angry that people tell lies about Oran's history: Oran is a great city, the source uses the strong phrase ‘whran fil kbira’ or ‘9rwfil,’ and they criticize old nonsense in books and television, including the code-switched si fw and the emphatic ‘kdb flkdb,’ lies upon lies. They ask people to tell Oran's story beautifully and accurately; the strong clauses and code-switched surfaces are retained.",
        "korean": "화자는 미국인의 역사가 큰 역사를 지닌다고 말하며 문제는 와흐라니 방언이 사라지는 것만이 아니라고 해요. 오랑의 역사에 관해 사람들이 거짓말을 하는 것에 화가 났다고 하며, 오랑은 큰 도시라는 whran fil kbira 또는 9rwfil 같은 강한 표현과 책·텔레비전에 쓰인 옛날의 헛소리를 비판해요. si fw와 ‘kdb flkdb’, 즉 거짓말에 거짓말이라는 강조 표현도 보존하고, 오랑의 이야기를 아름답고 정확하게 말하자고 해요. 강한 절과 코드스위칭 표면을 약화하지 않아요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    },
    1215: {
        "english": "The speaker says that if they talk about Oran, they want to speak about it beautifully, then calls Oran traziam mwiyor balkwn awmond: the third-best balcony in the world. The code-switched superlative surface is preserved without expanding it into an alternative ‘third-best city.’",
        "korean": "화자는 오랑을 말한다면 아름다운 방식으로 이야기하고 싶다고 한 뒤 오랑을 traziam mwiyor balkwn awmond, 즉 세계에서 세 번째로 좋은 발코니라고 불러요. 코드스위칭 최상급 표면을 보존하고 이를 ‘세 번째로 좋은 도시’로 확장하지 않아요.",
        "processing_flags": "code_switching|idiom_culture|source_ambiguity",
    },
    1216: {
        "processing_flags": "cefr_boundary|source_ambiguity",
    },
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
    counts = {
        "draft": sum(row["enrichment_state"] == "draft" for row in rows),
        "flagged": sum(row["enrichment_state"] == "flagged" for row in rows),
        "not_started": sum(row["enrichment_state"] == "not_started" for row in rows),
    }
    state_updates = sum("enrichment_state" in fields for fields in CORRECTIONS.values())
    batch_counts = {
        "draft": sum(row["enrichment_state"] == "draft" for row in batch_rows),
        "flagged": sum(row["enrichment_state"] == "flagged" for row in batch_rows),
    }
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    status["enrichment_correction_id"] = CORRECTION_ID
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
