"""Apply the first HeadGPT-directed semantic corrections for MADOran Batch 16."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "d3a9c51"
BATCH_ID = "MADORAN-ENRICH-016"
CORRECTION_ID = "MADORAN-ENRICH-016-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v16-correction-1"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch16_sentno_0961_1024.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch16_correction01_qa.json"
PROVENANCE_BEFORE = 13828

CORRECTIONS = {
    966: {
        "english": "The other speaker rejects the ogre idea and lists several household or food-preparation tasks, including cutting meat, making عصبان, washing tripe or skins, and cleaning something. The French-derived form ‘au moins’ (‘at least’) appears in the remaining opaque description, which says another woman is at least working; the rest contains unclear grooming wording.",
        "korean": "상대는 괴물 이야기를 받아들이지 않고 고기를 손질하고 عصبان을 만들며 내장이나 가죽을 씻고 무언가를 닦았다는 식으로 여러 집안일이나 음식 준비를 나열해요. 남은 불투명한 표현에는 프랑스어계 ‘au moins’(‘적어도’)가 나타나며, 다른 여성이 적어도 일하고 있다는 말로 이어져요. 나머지 몸단장 관련 표현은 불분명해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    970: {
        "english": "They welcome the visitors, exchange blessings, and say they have brought honey, a marriage alliance or kinship connection, and jam. Someone tells another person to be quiet and then addresses Dad.",
        "korean": "일행을 환영하고 축복의 말을 주고받으며 꿀과 혼인 관계나 인척 인연, 잼을 가지고 왔다고 해요. 누군가에게 조용히 하라고 한 뒤 아빠를 불러요.",
    },
    971: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    972: {
        "english": "The speaker lists the other group’s chef de service, chef de chantier, directeur général, and secrétaire général, then asks, ‘For whom?’ and answers, ‘For my son Bisha.’ The French-derived titles and the direction toward Bisha are preserved rather than paraphrased as ‘who saw’ something.",
        "korean": "화자는 상대 집단의 chef de service(부서장), chef de chantier(현장 책임자), directeur général(총괄 책임자), secrétaire général(사무총장) 같은 직함을 열거한 뒤 ‘누구를 위한 거야?’라고 묻고 ‘내 아들 비샤를 위한 거야’라고 답해요. 프랑스어계 직함과 비샤를 향한 방향을 ‘누가 보았다’는 식으로 바꾸지 않아요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    976: {
        "english": "One speaker asks, ‘What is happening?’ Another voice responds, ‘God willing, nothing but good.’ The question and the reassurance are kept as separate turns rather than merged into one speaker’s self-question and answer.",
        "korean": "한 화자가 ‘무슨 일이야?’라고 묻고, 다른 목소리가 ‘신의 뜻이라면 좋은 일뿐이야’라고 답해요. 질문과 안심시키는 응답을 한 화자의 자문자답으로 합치지 않고 별도 화행으로 보존해요.",
    },
    978: {
        "english": "The speaker repeats the instruction to go and get a brik from Akasha’s wife, clarifying the source after asking whether it is from Akasha himself. The reply says Akasha’s wife is smoking, followed by an agreement.",
        "korean": "화자는 아카샤의 아내에게서 브리크를 가져오라는 지시를 반복하고, 아카샤 본인에게서 가져오는 것인지 확인해요. 아카샤의 아내가 담배를 피우고 있다는 답이 나오고 서로 동의해요.",
    },
    982: {
        "english": "The other speaker mocks the claim of catching a fox and says that the person should be hunting lions, tigers, and l’ours (‘the bear’) instead. They refer to having lost or released a lion in the valley that time, then insult the other person and their mother or condition. The French-derived animal term and the direction of the opaque story are preserved.",
        "korean": "상대는 여우를 잡았다는 말을 비웃으며 사자와 호랑이, l’ours(‘곰’)를 잡아야 한다고 해요. 그때 계곡에서 사자를 놓쳤거나 잃었다는 방향의 불투명한 이야기를 하고, 상대와 그 어머니 또는 처지를 모욕해요. 프랑스어계 동물 표현과 이야기의 방향을 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    983: {
        "english": "The speaker says the important thing is to tell them what happened, but they did not tell them because they wanted to consult the woman. They firmly refuse to give their daughter away. The exchange also says, ‘Your mother is nagging,’ before revealing that a group from the Sons of the Day tribe came for their son Bisha, who studied with the speaker; one voice says to give her to him.",
        "korean": "화자는 중요한 것은 무슨 말을 했는지 알려 주는 것이라고 하지만, 여성과 상의하려고 상대에게 말하지 않았다고 해요. 자신의 딸을 절대 주지 않겠다고 단호하게 거절해요. 이어 ‘네 엄마가 잔소리하고 있다’는 절이 나오고, ‘울라드 나하르’ 부족 사람들이 아들 비샤를 위해 왔으며 그가 화자와 함께 공부했다는 사실이 드러나요. 한 목소리는 딸을 그에게 주라고 해요.",
    },
    984: {
        "english": "The speaker describes the proposed marriage with a chain of exaggerated or opaque comparisons, including marrying a sister, a gladiator, a roundabout, and a water-related object. They tell the listener to say they will not give the daughter. Another voice says Bisha deserves her because his people are good. Then, addressing Dad, the speaker says, ‘I myself am tired of her,’ while the remaining opaque or code-switched phrase ‘likidiha’ and the speaker-to-Dad direction are preserved.",
        "korean": "화자는 자매와 결혼한다거나 검투사·회전목마·물과 관련된 물건을 말하는 식으로 과장되고 불투명한 비교를 이어가요. 딸을 주지 않겠다고 말하라고 해요. 다른 목소리는 비샤와 그 집안이 좋은 사람들이라 딸을 받을 만하다고 말해요. 이어 화자가 아빠에게 ‘나 자신이 그녀에게 질렸어’라고 말하며, 남은 불투명하거나 코드 스위칭된 표현 ‘likidiha’와 화자→아빠 방향을 보존해요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    989: {
        "english": "The speaker says that when the boy is born, they will name him Saïd.",
        "korean": "화자는 그 아이가 태어나면 이름을 사이드라고 짓겠다고 말해요.",
    },
    996: {
        "english": "The speaker says the girl is still studying, has a licence in law, wants to become a lawyer, and hopes to finish her studies, go to France, and marry there because there is no future here. The speaker adds that it is all right and they can wait for her. The French-derived educational, legal, and waiting expressions are preserved as code-switching.",
        "korean": "화자는 그 여성이 아직 공부 중이고 법학 학위가 있으며 변호사가 되고 싶어 한다고 해요. 공부를 마치면 프랑스에 가서 그곳에서 결혼하고 싶어 한다며 여기에는 더 이상 미래가 없다고 말해요. 이어 괜찮고 자신이 그녀를 기다릴 수 있다고 덧붙여요. 교육·법률·기다림과 관련된 프랑스어계 표현은 코드 스위칭으로 보존해요.",
    },
    1002: {
        "english": "The speaker says that their tribe has never entered a marriage or kinship relationship with the other person’s tribe.",
        "korean": "화자는 자신들의 부족은 상대 부족과 혼인 관계나 인척 관계를 맺은 적이 한 번도 없다고 말해요.",
    },
    1004: {
        "english": "The speaker tells the visitors to leave, saying ‘go, before I throw you out.’ The line is an expulsion command or threat, not a hostile welcome.",
        "korean": "화자가 방문객들에게 ‘내가 쫓아내기 전에 가라, 나가라’고 말해요. 이 발화는 적대적인 환영이 아니라 축출 명령이나 위협이에요.",
        "speech_act": "command",
    },
    1006: {
        "korean": "누군가 외사촌인 그녀에게 무슨 문제가 있느냐고 묻자, 상대는 그녀가 대머리라고 답해요.",
    },
    1007: {
        "english": "Someone refers to the paternal cousin, a woman, and says that she has mange or a skin disease.",
        "korean": "누군가 친사촌인 그녀를 가리키며 그녀에게 옴이나 피부병이 있다고 말해요.",
    },
    1013: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    1015: {
        "english": "The speaker says they are thinking of using it for a ferme (farm) associated with Khaïlia, asks why they do not make a yaourt usine (yogurt factory), and compares it with an unclear reference to the listener’s mother. The French-derived farm, factory, and yogurt terms are kept as code-switching.",
        "korean": "화자는 그것을 카할리아와 관련된 ferme(농장)에 쓰려고 생각한다고 하며, 왜 yaourt usine(요구르트 공장)을 만들지 않느냐고 묻고 상대 어머니와 비교하는 불투명한 말을 해요. 농장·공장·요구르트의 프랑스어계 표현은 코드 스위칭으로 보존해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1016: {
        "english": "The speaker refers to a yaourt usine, a yogurt factory, using the French-derived code-switched expression rather than an unspecified yogurt-related object.",
        "korean": "화자가 프랑스어계 코드 스위칭 표현인 yaourt usine, 즉 요구르트 공장을 언급해요. 불특정한 요구르트 관련 물건으로 처리하지 않아요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    1017: {
        "processing_flags": "code_switching|source_ambiguity",
    },
    1022: {
        "english": "The speaker says Bisha wants to throw himself or jump from a height, using the opaque form ‘trwazim’, which may connect with French troisième (‘third’) and a third floor. They say they knew he wanted to do it because of her and tell the others to follow. This possible jump or self-harm reading is kept as a source-ambiguity hypothesis, not a settled fact, and is not reduced to a competition or rank metaphor.",
        "korean": "화자는 비샤가 몸을 던지거나 높은 곳에서 뛰어내리려 한다고 말하며, ‘trwazim’이라는 불투명한 표현을 써요. 이 표현은 프랑스어 troisième(‘세 번째’) 및 3층과 연결될 가능성이 있지만 확정하지 않아요. 그녀 때문에 그렇게 하려 한다는 것을 알고 있었다며 따라오라고 해요. 투신이나 자해 가능성은 원문 불확실성을 유지한 가설로 남기고, 경쟁이나 지위 비유로 축소하지 않아요.",
        "topic": "opaque_possible_jump_expression_about_bisha",
        "processing_flags": "code_switching|source_ambiguity",
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
    return engine.apply()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
