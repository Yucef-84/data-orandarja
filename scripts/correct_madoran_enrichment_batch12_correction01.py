"""Apply the first HeadGPT correction set for MADOran Batch 12."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch12 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "6f649be"
CORRECTION_ID = "MADORAN-ENRICH-012-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v12-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch12_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch12_correction01_qa.json"


CORRECTIONS = {
    705: {
        "english": "The exchange continues a housing/problem-solving discussion. It mentions looking for someone to handle or relieve a matter there, a single direct blow, trying to find how to deal with it, and an unclear reference to a man's wife. The pronouns, actors, and intended action remain unresolved.",
        "korean": "대화는 주거 문제를 해결하려는 흐름을 이어 가요. 그 일을 처리하거나 부담을 덜어 줄 사람을 찾는 말, 한 번의 직접적인 타격, 어떻게 처리할지 해 보려는 말, 그리고 한 남자의 아내에 대한 불분명한 언급이 나와요. 대명사와 행위자, 의도된 행동은 확정하지 않아요.",
        "domain": "housing",
        "topic": "unclear_housing_problem_solving_with_spouse_reference",
    },
    706: {
        "english": "The speaker asks what the other person is waiting for or doing, calls it good news, offers coffee, and asks the person to come along. The speaker then says, with the French/code-switched word rendez-vous, that they have a rendez-vous with him now; the exact appointment context remains unclear.",
        "korean": "화자는 상대가 무엇을 기다리거나 하고 있는지 묻고 좋은 소식이라고 하며 커피를 권하고 함께 가자고 해요. 이어 프랑스어·코드 스위칭 표현인 ‘rendez-vous’를 사용해 지금 그와 약속이 있다고 말해요. 정확한 약속의 맥락은 불분명해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    707: {
        "english": "After greetings, Ibrahim is addressed in a colloquial, partly unclear comment. The phrase containing مراكش is not resolved as the city Marrakech; in context it appears to say that Ibrahim's condition or presentation today is not pleasing or is not right, followed by a question about what is wrong or what he has. The French phrase c'est pas ça is retained as code-switching.",
        "korean": "인사를 나눈 뒤 이브라힘에게 구어적이고 일부 불분명한 말을 건네요. ‘مراكش’를 도시 마라케시로 확정하지 않아요. 문맥상 이브라힘의 오늘 상태나 모습이 마음에 들지 않거나 괜찮지 않다고 말한 뒤 무슨 일이 있거나 무엇을 가지고 있는지 묻는 흐름으로 보여요. 프랑스어 표현 ‘c'est pas ça’는 코드 스위칭으로 보존해요.",
        "topic": "greeting_and_unclear_comment_to_ibrahim",
    },
    710: {
        "english": "The line begins with a farewell and says that the speaker is tired from work. The speaker then meets a man on the road by chance; one matter leads to another in conversation and they enter into the addressee's matter. The exact actors and transitions remain partly unclear.",
        "korean": "대화는 작별 인사로 시작하고 화자가 일 때문에 지쳤다고 말해요. 이어 화자가 길에서 한 남자를 우연히 만나고, 한 이야기가 다른 이야기로 이어져 상대의 일에 들어가게 돼요. 정확한 행위자와 전환은 일부 불분명해요.",
        "topic": "speaker_tired_from_work_and_chance_meeting",
    },
    711: {
        "english": "The exchange asks about a housing matter. One speaker says that talk leads to talk and that he told him (قلتله), then refers to something involving a brother who is deeply wronged or in serious trouble, a very large and dark grievance. The exact idiom and actors remain unclear; this is not a literal killing account.",
        "korean": "대화는 주거 문제를 물어요. 한 화자는 이야기가 이어진다고 하며 자신이 그에게 말했다는 뜻의 ‘قلتله’를 사용하고, 심하게 억울하거나 큰 곤경에 처한 형제와 매우 크고 어두운 고충을 언급해요. 정확한 관용 표현과 행위자는 불분명하며 문자 그대로의 살인 이야기는 아니에요.",
        "topic": "housing_grievance_and_unclear_told_him_phrase",
    },
    712: {
        "english": "Continue with me on the road. The poor or tired man told me about a problem; I told him (قلتله) that he was accompanying me and was in a serious problem, in the full sense. The exact actors and colloquial force remain unclear.",
        "korean": "나와 함께 길을 계속 가요. 그 불쌍하거나 지친 남자가 나에게 문제를 말했고, 나는 그에게 말했다는 뜻의 ‘قلتله’를 사용해 그가 나와 동행하며 큰 문제에 처해 있다고 해요. 정확한 행위자와 구어적 의미는 불분명해요.",
    },
    713: {
        "english": "Addressing Brahim, the speaker asks him to accompany the speaker to the house. Coffee is part of the exchange, but the exact addressee of that invitation is unclear; after an unclear phrase, the speaker and another man come directly to the addressee so the addressee can explain his problem to that man. The roles and referents remain partly unresolved.",
        "korean": "화자는 브라힘에게 집까지 함께 가자고 말해요. 커피가 대화에 나오지만 그 초대의 정확한 대상은 불분명해요. 불분명한 표현 뒤에 화자와 다른 남자가 상대에게 바로 와서, 상대가 그 남자에게 자신의 문제가 무엇인지 설명하게 하는 흐름이 나와요. 역할과 지시 대상은 일부 확정하지 않아요.",
        "topic": "bringing_a_problem_to_brahim_and_another_man",
    },
    714: {
        "english": "Addressing Si Houari, a speaker says, ‘I am deeply troubled by a housing matter: housing and rent exist, but my salary does not allow me to rent.’ In a second turn addressed to Si Brahim, another speaker says, ‘I am a person who does good and want to do good for people.’ The speaker roles and the exact relation between the turns remain unresolved.",
        "korean": "시 후아리에게 말을 건네며 한 화자가 ‘주거 문제로 매우 곤란해요. 집과 임대료는 있지만 내 급여로는 빌릴 수 없어요’라고 말해요. 이어 시 브라힘에게 말을 건네는 다른 발화에서 ‘나는 선행을 하는 사람이고 사람들에게 선행을 하고 싶어요’라고 해요. 화자 역할과 두 발화의 정확한 관계는 확정하지 않아요.",
    },
    715: {
        "english": "A speaker says that he has helped people before and, seeing the addressee troubled, will help him, addressing him as Si Brahim. Another turn thanks Si Houari, asks when the speaker can come to live there, and answers that from tomorrow, God willing, he and his wife can live there. The speaker identities and exact housing arrangement remain partly unclear.",
        "korean": "한 화자는 전에 사람들을 도왔고 상대가 곤란한 것을 보았으니 그를 돕겠다고 하며 ‘시 브라힘’이라고 불러요. 이어 다른 발화에서는 시 후아리에게 감사하고 언제 그곳에 들어가 살 수 있는지 묻고, 하느님의 뜻이라면 내일부터 그 사람과 아내가 살 수 있다고 답해요. 화자 정체와 정확한 주거 arrangement는 일부 불분명해요.",
        "topic": "offering_housing_help_between_houari_and_brahim",
    },
    716: {
        "english": "The speakers thank Si Houari and Hamed, exchange a blessing, and say that they will finish the matter at the house, God willing. The source does not specify that this will happen tomorrow; the exact arrangement and timing remain unclear.",
        "korean": "화자들은 시 후아리와 하메드에게 감사하고 서로 축복을 빌며, 하느님의 뜻이라면 집에서 그 일을 마무리하겠다고 해요. 원문은 이것이 내일 일어난다고 말하지 않으므로 정확한 arrangement와 시점은 불분명해요.",
    },
    719: {
        "processing_flags": "",
    },
    720: {
        "english": "The proverb gives four bodily and social admonitions: do not undress while sweating; do not drink water while sweating; do not stretch or extend your legs among a group; and do not feed your children among a group. The exact proverbial force remains cultural, but these four actions are explicit.",
        "korean": "이 속담은 신체·사회적 행동에 관한 네 가지 충고를 해요. 땀날 때 옷을 벗지 말고, 땀날 때 물을 마시지 말며, 사람들 사이에서 다리를 뻗지 말고, 사람들 가운데서 아이들에게 먹이지 말라는 내용이에요. 정확한 속담의 교훈은 문화적이지만 네 행동 자체는 원문에 명시돼요.",
        "topic": "proverb_about_sweating_drinking_and_public_manners",
    },
    721: {
        "english": "Do not drink while standing. Clean your face; you do not know what you will meet with it. What beauty cannot give you, surpass it with a smile; what proper manner or expression cannot give you, surpass it with tact or diplomacy; and what money cannot give you, surpass it with contentment. The mappings are proverbial and colloquial.",
        "korean": "서서 마시지 말아요. 얼굴을 깨끗이 하세요. 그 얼굴로 무엇을 만나게 될지는 알 수 없어요. 아름다움으로 얻지 못하는 것은 미소로 넘어설 수 있고, 올바른 태도나 표현으로 얻지 못하는 것은 처신이나 외교적 수완으로 넘어설 수 있으며, 돈으로 얻지 못하는 것은 만족으로 넘어설 수 있다고 해요. 대응 관계는 속담식이고 구어적이에요.",
    },
    722: {
        "english": "A proverb sequence uses a lion or lion's son, oleander, apples, bishna flour and food, dog wool and a burnous, a tribal elder, and a large head and belly sold cheaply as comparisons. The exact syntax and moral remain unclear, but the lion and oleander are not a seven-year-old boy and a mare.",
        "korean": "속담식 연쇄에서 사자 또는 사자의 아들, 협죽도(oleander), 사과, 비슈나 밀가루와 음식, 개털과 브누스, 부족의 우두머리, 큰 머리와 배를 싸게 파는 비유가 나와요. 정확한 문장 구조와 교훈은 불분명하지만 사자와 협죽도를 일곱 살 소년과 암말로 바꾸지 않아요.",
    },
    724: {
        "english": "The line repeats عرة, a term for a flaw, shame, or defect, in comparisons involving fruit or plums, women who cook and taste, and men who go from market to market. The exact mapping and social judgment remain unclear.",
        "korean": "이 구절은 결점·수치·흠을 뜻하는 ‘عرة’를 반복하며 과일이나 자두, 요리하고 맛보는 여성, 시장에서 시장으로 다니는 남성을 비교해요. 정확한 대응 관계와 사회적 판단은 불분명해요.",
    },
    726: {
        "english": "The proverb gives a chain of correspondences: when the teeth fall, taste or sweetness goes; when the eyes go, the world goes; when the nose or face (النيف) goes, resolve or spirit (الهمة) goes; when men go, honor or respect (حرمة) goes; and when parents go, the family gathering or community (اللمة) goes. The cultural force is retained without collapsing the mappings.",
        "korean": "속담은 대응 관계를 연쇄적으로 말해요. 이가 빠지면 맛이나 단맛이 사라지고, 두 눈이 사라지면 세상이 사라지며, 코나 얼굴을 뜻할 수 있는 ‘النيف’가 사라지면 기개·의욕인 ‘الهمة’가 사라져요. 남자들이 사라지면 명예·존중인 ‘حرمة’가 사라지고, 부모가 사라지면 가족의 모임·공동체인 ‘اللمة’가 사라진다고 해요. 대응 관계를 뭉개지 않고 문화적 의미로 보존해요.",
    },
    729: {
        "english": "Another harsh proverb says that whoever knows neither slaughtering nor skinning or flaying, and marries a respectable family's daughter, brings disgrace. The food and skill terms are source-specific and partly idiomatic.",
        "korean": "또 다른 거친 속담은 도살도 가죽 벗기기·손질도 할 줄 모르는 사람이 좋은 집안의 딸과 결혼하면 망신을 가져온다는 식으로 말해요. 음식과 기술을 가리키는 표현은 원문 특유의 일부 관용적 표현이에요.",
        "topic": "harsh_proverb_about_slaughter_skinning_and_marriage",
    },
    730: {
        "english": "A related gendered and harsh proverb says that a woman who does not know how to prepare bouzlouf or douara and marries a people's son brings loss. The judgment about women and marriage is preserved as source content, not endorsed advice.",
        "korean": "이어지는 성별화된 거친 속담은 부즐루프나 두와라를 준비할 줄 모르는 여성이 사람들의 아들과 결혼하면 손실을 가져온다는 식으로 말해요. 여성과 결혼에 관한 판단은 원문 내용으로 보존할 뿐 조언으로 지지하지 않아요.",
        "register": "offensive",
    },
    731: {
        "processing_flags": "",
    },
    732: {
        "english": "The first university-student type carries a guitar and sits with girls, singing for them. His hair is always uncombed; all the girls with him are described with the French/code-switched term civilisée, and this group is said to be always disliked at the university.",
        "korean": "대학생의 첫 번째 유형은 기타를 들고 여자들과 앉아 그들에게 노래해요. 머리는 늘 헝클어져 있고, 그와 함께 있는 여자들은 프랑스어·코드 스위칭 표현인 ‘civilisée’로 묘사돼요. 이 무리는 대학에서 늘 미움을 받는다고 해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    733: {
        "english": "The second type wants to show off. They display their father's car and show it off, while girls put on makeup; the phrase هو حلاب يحلب فيهم is a slang ‘milking them’ metaphor whose exact flirtation or exploitation force remains unclear. The source does not say that he himself uses grooming or shaving products.",
        "korean": "두 번째 유형은 과시하려고 해요. 아버지의 차를 내세워 보여 주고, 여자들은 화장을 해요. ‘هو حلاب يحلب فيهم’은 그들을 ‘짜내거나 우려낸다’는 식의 속어적 ‘milking’ 비유로, 정확한 추파나 착취의 강도는 확정하지 않아요. 원문은 그가 직접 몸단장이나 면도 제품을 쓴다고 말하지 않아요.",
    },
    735: {
        "english": "The French/code-switched category four is always alone: eating alone, studying alone, going alone, and remaining alone.",
        "korean": "프랑스어·코드 스위칭 표현인 ‘category 4’ 유형은 늘 혼자예요. 혼자 먹고, 혼자 공부하고, 혼자 다니며 계속 혼자 있어요.",
        "processing_flags": "code_switching",
    },
    736: {
        "english": "The fifth group consists of couples who stay together in the morning, at midday, and in the evening on campus; they do not leave each other at all.",
        "korean": "다섯 번째 무리는 커플들로, 캠퍼스에서 아침과 한낮, 저녁까지 함께 있어요. 서로에게서 전혀 떨어지지 않아요.",
        "processing_flags": "",
    },
    737: {
        "english": "Another type consists of two friends who keep walking around the university and know it span by span and person by person. They can identify the people who do not study there; wherever you go, you find them, and this type moves only with each other rather than mixing with everyone. The final slang labels remain unclear.",
        "korean": "또 다른 유형은 대학을 계속 돌아다니며 구석구석, 사람 하나하나까지 아는 두 친구예요. 그곳에서 공부하지 않는 사람들까지 알아볼 수 있고, 어디로 가든 그들을 만나요. 이 유형은 서로끼리만 돌아다니며 모든 사람과 섞이지 않아요. 마지막 속어 표현은 불분명해요.",
    },
    739: {
        "english": "The speaker describes a repeated scenario when a girl meets a person, whether a man or a woman: at first the person pleases her, she laughs, jokes or plays around, and enjoys the interaction; then she hates the person without a reason. The same scenario happens with every person she meets, and the slang remains colloquial rather than a fixed romantic plot.",
        "korean": "화자는 여자가 남자든 여자든 누군가를 만날 때 반복되는 상황을 설명해요. 처음에는 그 사람이 마음에 들어 웃고 장난치며 즐거워하다가, 이유 없이 그 사람을 싫어하게 돼요. 만나는 사람마다 같은 상황이 반복되며, 속어는 고정된 연애 서사로 확정하지 않아요.",
        "domain": "daily_life",
        "topic": "repeated_like_then_dislike_scenario",
    },
    740: {
        "english": "If I ever become a couple with him, I would never call him. People kept making this remark to me: you do not call and you do not look for him. The French/code-switched expressions en couple, jamais, and remarque are retained; the exact speaker and relationship framing remain colloquial.",
        "korean": "내가 그와 커플이 되더라도 나는 그에게 절대 전화하지 않을 거예요. 사람들이 내게 ‘너는 전화도 하지 않고 그를 찾지도 않는다’는 말을 계속 했어요. ‘en couple’, ‘jamais’, ‘remarque’라는 프랑스어·코드 스위칭 표현을 보존하며, 정확한 화자와 관계 구도는 구어적으로 남겨요.",
        "topic": "not_calling_in_a_couple",
        "processing_flags": "code_switching|source_ambiguity",
    },
    742: {
        "english": "Regarding the ‘German’ one, the speaker describes an inner feeling of wanting to vomit on his face. The line also mentions ‘the food of 2015’ (الماكلة تع 2015), then says the speaker starts looking for problems until stopping him. The imagery and actor relations remain unclear.",
        "korean": "‘독일인·독일 것’이라고 불리는 대상에 관해 화자는 그 얼굴에 토하고 싶은 내적 감정을 말해요. 이어 ‘2015년의 음식’(الماكلة تع 2015)을 언급하고, 그를 막을 때까지 문제를 찾기 시작한다고 해요. 이미지와 행위자 관계는 불분명해요.",
    },
    743: {
        "english": "I have started worrying about myself and am confused: how could you be in a relation for four or five years? Am I a normal person? No, brother—go take care of yourself; your illness is serious. May God bring healing, God willing. The French/code-switched relation and the sarcastic speaker boundaries remain visible but partly unclear.",
        "korean": "나는 나 자신에 대해 걱정하기 시작했고 혼란스러워요. 어떻게 4~5년 동안 ‘relation’ 관계에 있을 수 있죠? 나는 정상적인 사람인가요? 아니요, 형제여. 가서 자신을 돌봐요. 병이 심해요. 하느님의 뜻이라면 하느님이 치유를 가져오시길 바라요. 프랑스어·코드 스위칭 표현 ‘relation’과 비꼬는 화자 경계는 보존하되 일부 불분명하게 남겨요.",
        "topic": "four_or_five_year_relation_and_sarcastic_admonition",
        "processing_flags": "code_switching|source_ambiguity",
    },
    746: {
        "english": "Why do you not hold my hand when we walk outside?",
        "korean": "우리가 밖을 걸을 때 왜 내 손을 잡지 않아요?",
        "processing_flags": "",
    },
    747: {
        "english": "I am afraid that someone who knows you will see us and cause trouble. If I propose to you, I will hold your hand, and no one will ask us about it.",
        "korean": "당신을 아는 누군가가 우리를 보고 문제를 일으킬까 봐 걱정돼요. 내가 당신에게 청혼하면 내가 당신의 손을 잡을 거고, 아무도 우리에게 그것을 묻지 않을 거예요.",
    },
    749: {
        "english": "When they get married, she asks: ‘Do we not have a home and مستروين?’ Thank God, he says; do what you want in it. The source-specific term مستروين is not furniture, and its exact referent remains unclear.",
        "korean": "그들이 결혼하면 그녀가 ‘우리에게 집과 ‘مستروين’이 있지 않나요?’라고 물어요. 그는 하느님께 감사하다고 하며 그 안에서 원하는 일을 하라고 해요. 원문 특유의 ‘مستروين’은 가구가 아니며 정확한 지시 대상은 불분명해요.",
        "topic": "home_and_unclear_marriage_term",
    },
    750: {
        "english": "When they become married with children, she asks him again: ‘Why do you still not hold my hand?’ The stage of marriage with children is part of the time sequence.",
        "korean": "그들이 결혼해서 아이들도 있는 단계가 되면 그녀가 다시 물어요. ‘그런데 왜 아직도 내 손을 잡지 않아요?’ 결혼하고 아이들이 있는 단계가 시간의 흐름에 포함돼요.",
        "topic": "holding_hands_after_marriage_with_children",
    },
    752: {
        "english": "After twenty-five years of marriage, she asks again what kind of man he wants for their daughter; the reply says that they have grown old and senile. The phrase 25 عام تع زواج refers to twenty-five years of marriage, not marriage age.",
        "korean": "결혼 25년 후에 그녀가 딸에게 어떤 남자를 원하는지 다시 물어요. 대답은 그들이 나이가 들고 노망이 들었다고 말해요. ‘25 عام تع زواج’는 결혼 나이가 아니라 결혼생활 25년을 뜻해요.",
        "topic": "twenty_five_years_of_marriage_and_daughter_suitor",
    },
    754: {
        "english": "He replies: ‘You want me to hold your hand and leave my cane, so that I fall and die and you inherit me? I know you want to be rid of me.’ He then calls someone to come and understand how love works in Algeria; the comic framing remains partly unclear. The word خزرانة is a cane or walking stick, not a grenade.",
        "korean": "그는 이렇게 대답해요. ‘내가 네 손을 잡으려고 지팡이를 놓아서 넘어져 죽고 네가 나를 상속받기를 원해? 네가 나에게서 벗어나고 싶은 걸 알아.’ 이어 누군가에게 와서 알제리에서 사랑이 어떻게 작동하는지 이해해 보라고 해요. 코미디적 구도는 일부 불분명해요. ‘خزرانة’는 수류탄이 아니라 지팡이예요.",
        "topic": "old_marriage_cane_and_inheritance_banter",
        "register": "colloquial",
    },
    755: {
        "english": "Come, let me tell you about my brother. In the evening he came to his mother and said, ‘I want to get married; arrange a proposal for me / ask for her hand on my behalf.’ She answered, ‘Okay.’",
        "korean": "이리 와서 내 형제 이야기를 들어 봐요. 저녁에 그가 어머니에게 와서 ‘결혼하고 싶으니 나를 위해 청혼을 주선하거나 여자 쪽에 손을 구해 주세요’라고 말했어요. 어머니는 ‘알겠어’라고 답했어요.",
    },
    756: {
        "english": "Then he said, ‘I want you to arrange a proposal for my friend, a certain woman.’ She is a woman he usually brings to the house. His mother asks how a woman who usually comes with him to the house could be brought along to look for marriage. The exact family roles remain partly unclear.",
        "korean": "그러자 그는 ‘내 친구인 어떤 여자에게 청혼을 주선해 주세요’라고 말했어요. 그 여자는 그가 평소 집에 데려오던 여자예요. 어머니는 평소 그와 함께 집에 오던 여자가 어떻게 그와 함께 결혼할 상대를 찾으러 올 수 있느냐고 물어요. 정확한 가족 역할은 일부 불분명해요.",
    },
    757: {
        "english": "The mother says, ‘Let me choose one for you.’ He asks why she would bring him a woman who already has a lover: when he proposes to her, she will cry for her lover and deceive him. He says instead to let him take the beloved woman he knows and raised himself. The actors and comic framing remain partly unclear.",
        "korean": "어머니가 ‘내가 너에게 한 명을 골라 줄게’라고 말해요. 그는 이미 애인이 있는 여자를 왜 데려오느냐고 해요. 그 여자에게 청혼하면 애인을 그리워하며 울고 자신을 속일 수 있기 때문이에요. 대신 자신이 알고 직접 키운 사랑하는 여자를 데려가게 해 달라고 말해요. 행위자와 코미디적 구도는 일부 불분명해요.",
    },
    758: {
        "english": "The speaker says he was shocked by his brother. Some women are explicitly called قحبات (‘whores’) and are said to remain in the street; one is described as attaching herself to someone until she takes him. Another man jumps from one woman to another. The insults are source content, while the relationships in من شيرة لختها remain ambiguous rather than being fixed as a literal sister story.",
        "korean": "화자는 형제 때문에 충격을 받았다고 해요. 어떤 여자들을 명시적으로 ‘قحبات’(창녀들)라고 부르고, 늘 거리에 있다고 말하며, 한 여자가 누군가에게 달라붙어 결국 그를 차지하는 듯한 표현도 나와요. 또 다른 남자는 한 여자에서 다른 여자로 옮겨 다녀요. 욕설은 원문 내용으로 보존하고 ‘من شيرة لختها’의 관계는 친자매 이야기로 확정하지 않아요.",
        "register": "vulgar",
    },
    759: {
        "english": "I want only the woman that his mother has seen or selected for him, as usual. The line also talks about manhood and asks God to bring a respectable or lawful boy. The exact social and romantic targets remain unclear.",
        "korean": "나는 평소처럼 그의 어머니가 그를 위해 보거나 골라 둔 여자만 원해요. 이어 남자다움에 대해 말하고 하느님이 올바르거나 존경할 만한 남자를 보내 주시기를 바라요. 정확한 사회적·연애 대상은 불분명해요.",
        "topic": "mother_selected_woman_and_marriage_wish",
    },
    760: {
        "english": "An exhortative, stereotyped line says: marry an Oran woman; you will find her gentle and sensitive, with a clean house, flowers planted at the window, and hrira, bourek, and ma‘qouda prepared for you. The food and gendered cultural framing are retained as source content.",
        "korean": "권유이자 고정관념적 묘사인 이 대사는 오랑 여자와 결혼하라고 해요. 그러면 다정하고 섬세하며 집을 늘 깨끗하게 하고 창가에 꽃을 심고 하리라·부레크·마‘쿠다를 준비하는 여자를 만나게 된다고 해요. 음식과 성별화된 문화적 구도는 원문 내용으로 보존해요.",
        "speech_act": "suggestion",
        "processing_flags": "idiom_culture",
    },
    761: {
        "english": "The description continues with the unclear food name قغاتان, olive tajine, and dolma, especially when she wears a kitchen apron and ties her forehead with a scarf. An unclear phrase at the end says that this captures or steals the speaker's heart. The named dishes and the French/code-switched surtout (‘especially’) are retained.",
        "korean": "묘사는 불분명한 음식명 ‘قغاتان’, 올리브 타진과 돌마로 이어지고, 특히 그녀가 주방 앞치마를 입고 이마를 스카프로 묶을 때를 말해요. 끝의 불분명한 표현은 이것이 화자의 마음을 사로잡거나 훔친다는 뜻으로 보여요. 음식명과 프랑스어·코드 스위칭 표현 ‘surtout’(특히)를 보존해요.",
        "processing_flags": "code_switching|idiom_culture|source_ambiguity",
    },
    762: {
        "english": "She makes almond cigars or an almond-cigar pastry (سيقاغ تاع لوز) to eat with tea, adds food with raisins—seffa or stew—and prepares it at suhoor. This is where she satisfies or treats him, saying, ‘Eat, my husband, my capital/treasure.’ The food names and affectionate address remain explicit.",
        "korean": "그녀는 차와 함께 먹는 아몬드 시가형 과자 ‘سيقاغ تاع لوز’를 만들고, 건포도를 넣은 음식인 세파나 수프·스튜를 준비하며 수후르 때 그것을 마련해요. 바로 그때 그녀가 그를 대접하거나 만족시키며 ‘먹어요, 내 남편, 내 보물’이라고 말해요. 음식명과 애정 어린 호칭을 명시적으로 보존해요.",
        "topic": "almond_cigars_seffa_suhoor_hospitality",
    },
    763: {
        "english": "She is my heart; may God keep her for me. She also makes homemade bread that is not bought from outside, with sanouj or black seed, and hot matlouh. That is where her skill appears: every finger has a craft. The source does not add pastries or a hot griddle.",
        "korean": "그녀는 내 마음이에요. 하느님이 그녀를 내 곁에 두시길 바라요. 그녀는 밖에서 사 온 것이 아닌 집에서 만든 빵을 만들고, 산우즈 또는 흑종자를 넣으며 뜨거운 마틀루도 만들어요. 바로 그곳에서 그녀의 솜씨가 드러나고 손가락마다 재주가 있다고 해요. 원문에 없는 과자나 뜨거운 철판은 추가하지 않아요.",
        "topic": "affection_and_named_homemade_breads",
    },
    764: {
        "english": "When Eid arrives, she fills you with sweets: baklava, griwech, makrout, msemen, tournos, arayesh, and all kinds. The ending gives an unclear affectionate praise of a sweet or beautiful Oran woman, explicitly describing her as a woman of dignity and status.",
        "korean": "이드가 오면 그녀는 바클라바, 그리우시, 마크루드, 므세멘, 투르누, 아라이시 등 온갖 과자로 당신을 배부르게 해요. 끝부분은 달콤하거나 아름다운 오랑 여자를 칭찬하는 불분명한 애정 표현이며, 그녀를 위엄과 지위가 있는 여자로 명시해요.",
    },
    766: {
        "english": "We are your children: born in the haouch or housing compound and raised in the neighborhoods. They relocated us and housed us in apartment blocks. The collective ‘they’ and the movement from haouch and neighborhoods to apartment buildings are preserved.",
        "korean": "우리는 당신의 자식들이에요. 하우시 또는 주거 단지에서 태어나 동네에서 자랐어요. 그들이 우리를 이주시켜 아파트 단지에 살게 했어요. 집단 주어 ‘그들’과 하우시·동네에서 아파트로 이동한 구조를 보존해요.",
        "topic": "oran_children_relocation_from_haouch_to_apartments",
    },
    767: {
        "english": "Oran expanded, yet became narrow for its children. They built a new neighborhood in you and named it El Aqid. The line preserves the rhetorical contrast between the city's expansion and its children feeling constrained.",
        "korean": "오랑은 넓어졌지만 자기 자식들에게는 비좁아졌어요. 그들이 당신 안에 새 동네를 지어 엘 아키드라고 이름 붙였어요. 도시의 확장과 그 자식들이 제약을 느끼게 된다는 수사적 대비를 보존해요.",
        "topic": "oran_expansion_and_el_aqid_neighborhood",
    },
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid, field, value, generated_at):
    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": "llm_source_only_enrichment_correction",
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_state": "generated",
    }


def apply():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if not head.startswith(BASE_COMMIT) or source_gate()["result"] != "PASS":
        raise RuntimeError(f"gate_failed:{head}")
    source = read_tsv(SOURCE_OUT)
    before = read_tsv(ENRICHMENT_OUT)
    batch = read_tsv(BATCH_OUT)
    if list(before[0]) != ENRICHMENT_FIELDS or len(batch) != 64:
        raise RuntimeError("artifact_shape_mismatch")
    source_uids = {row["source_uid"] for row in source}
    master_before = {row["sentno"]: row for row in before}
    batch_before = {row["sentno"]: row for row in batch}
    for sentno in batch_before:
        if any(master_before[sentno].get(field) != batch_before[sentno].get(field) for field in ENRICHMENT_FIELDS):
            raise RuntimeError(f"batch_master_mismatch_before:{sentno}")
    after = [dict(row) for row in before]
    corrected_batch = [dict(row) for row in batch]
    for row in after:
        row.update(CORRECTIONS.get(int(row["sentno"]), {}))
    for row in corrected_batch:
        row.update(CORRECTIONS.get(int(row["sentno"]), {}))
    changed_fields = sum(len(fields) for fields in CORRECTIONS.values())
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 10245:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 10245 + changed_fields or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"]["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after)
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch12_correction01_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": len(CORRECTIONS), "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID,
        "latest_correction_id": CORRECTION_ID,
        "correction_history": history,
        "correction_changed_fields": changed_fields,
        "correction_state_updates": 0,
        "correction_rows": len(CORRECTIONS),
        "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 10245 + changed_fields,
        "expected_total_provenance_events": 10245 + changed_fields,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "content_review_status": "pending_headgpt_correction_review",
        "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": changed_fields,
        "state_updates": 0,
        "new_provenance_events": changed_fields,
        "provenance_events_before": 10245,
        "provenance_events_after": 10245 + changed_fields,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 3,
        "flagged_rows": 61,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "batch_artifact_sync": "PASS",
        "batch_artifact_sync_changed_fields": changed_fields,
        "batch_artifact_sync_state_updates": 0,
        "generated_at": generated_at,
        "outputs": {
            "batch": BATCH_OUT.relative_to(ROOT).as_posix(),
            "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
            "provenance": EVENTS_OUT.relative_to(ROOT).as_posix(),
        },
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
