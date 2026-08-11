"""Apply the third HeadGPT-directed semantic corrections for MADOran Batch 16."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "ab2639e"
BATCH_ID = "MADORAN-ENRICH-016"
CORRECTION_ID = "MADORAN-ENRICH-016-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v16-correction-3"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch16_sentno_0961_1024.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch16_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch16_correction03_qa.json"
PROVENANCE_BEFORE = 13917

CORRECTIONS = {
    983: {
        "english": "The exchange contains a question and answer: khbrni ... sha 9ltlhm? asks, ‘Tell me, what did you tell them?’ and ma 9ltlhmsh answers, ‘I did not tell them because I wanted to consult you/her,’ with the exact addressee kept uncertain. The speaker firmly refuses to give the daughter away. The exchange also says, ‘Your mother is nagging,’ before revealing that a group from the Sons of the Day tribe came for their son Bisha, who studied with the speaker; one voice says to give her to him. The question-to-answer direction is preserved.",
        "korean": "이 대화에는 질문과 응답이 나와요. ‘khbrni ... sha 9ltlhm?’은 ‘말해 봐, 그들에게 뭐라고 했어?’라고 묻고, ‘ma 9ltlhmsh’는 ‘아무 말도 안 했어. 너나 그녀와 상의하려고 했어’라고 답하는 구조이며 정확한 청자는 불확실하게 둬요. 화자는 자신의 딸을 절대 주지 않겠다고 단호하게 거절해요. 이어 ‘네 엄마가 잔소리하고 있다’는 절이 나오고, ‘울라드 나하르’ 부족 사람들이 아들 비샤를 위해 왔으며 그가 화자와 함께 공부했다는 사실이 드러나요. 한 목소리는 딸을 그에게 주라고 해요. 질문에서 응답으로 이어지는 방향을 보존해요.",
    },
    984: {
        "english": "The speaker describes the proposed marriage through a chain of explicit, exaggerated or opaque clauses: tzwj m3 khth (‘marry his sister’), ijiha 9laditwr (‘she gets a gladiator’), ijiha alrwnd (‘she gets a roundabout’), and fkrwn t3 alma (‘a water-related object’). The exact referents remain uncertain, but each source surface and clause is retained. The speaker tells the listener to say they will not give the daughter; another voice says Bisha deserves her because his people are good. The exchange also contains mdha lbridatwr w saii, an opaque command-like clause, and later the speaker addresses Dad, says I myself am tired of her, and preserves likidiha as an opaque code-switched form.",
        "korean": "화자는 청혼을 과장되거나 불투명한 여러 명시 절로 묘사해요. ‘tzwj m3 khth’(그의 자매와 결혼한다), ‘ijiha 9laditwr’(그녀에게 검투사가 온다), ‘ijiha alrwnd’(그녀에게 회전목마가 온다), ‘fkrwn t3 alma’(물과 관련된 물건) 같은 표면형과 절을 각각 보존해요. 정확한 지시대상은 불확실하지만 어느 절도 ‘과장된 비교’라는 말로 누락하지 않아요. 화자는 딸을 주지 않겠다고 말하라고 하고, 다른 목소리는 비샤와 그 집안이 좋은 사람들이라 딸을 받을 만하다고 말해요. 이어 ‘mdha lbridatwr w saii’라는 명령처럼 보이는 불투명한 절이 나오며, 뒤에서 화자가 아빠에게 ‘나 자신이 그녀에게 질렸어’라고 말하고 likidiha도 불투명한 코드 스위칭 표현으로 보존해요.",
    },
    985: {
        "english": "The speaker tells someone to leave and uses the direct threat nlikidk, a code-switched or French-derived liquider-like form that may mean I will deal with or liquidate you. The following surface n3milk 3in and the later mshrk alfm are also retained as separate threat or insult clauses; their exact meanings are uncertain and are not silently replaced by a generic ‘deal with them.’ The person is told to go out and to tell the suitor no.",
        "korean": "화자는 누군가에게 나가라고 하며 ‘nlikidk’라는 직접적인 위협을 써요. 이는 ‘너를 처리하거나 없애 버리겠다’는 뜻일 수 있는 코드 스위칭 또는 프랑스어계 liquider 계열 표현이에요. 이어지는 ‘n3milk 3in’과 뒤의 ‘mshrk alfm’도 각각 별도의 위협·모욕 절로 표면형을 보존하며, 정확한 뜻은 불확실하므로 ‘상대를 처리한다’는 일반 표현으로 조용히 대체하지 않아요. 상대에게 밖으로 나가 청혼자에게 안 된다고 말하라고 해요.",
    },
    1015: {
        "english": "The speaker says they are thinking of putting it down as a 3arboun or earnest deposit for a ferme (farm) associated with Khaïlia, then asks why they do not make a wzin ta3 l7lib, a milk factory or dairy plant. The later comparison with the listener's mother remains unclear; the milk-factory meaning is kept distinct from the yogurt factory in Sentno 1016.",
        "korean": "화자는 그것을 카할리아와 관련된 ferme(농장)에 3arboun, 즉 계약금·보증금으로 걸어 두려고 생각한다고 한 뒤, 왜 ‘wzin ta3 l7lib’, 즉 우유 공장이나 유제품 공장을 만들지 않느냐고 물어요. 뒤의 상대 어머니와 비교하는 말은 불분명하게 두고, 1016번의 요구르트 공장과 구별되는 우유 공장 의미를 보존해요.",
        "topic": "farm_earnest_deposit_and_milk_factory_proposal",
    },
    1019: {
        "english": "The exchange opens with the explicit question mal 7ia kifah? (what is it, Hayia? or an uncertain name/address form). The speaker then says they were away for a minute and compares what happened on two days using dawlk; the direction may involve taking, removal, or handing something over and is not fixed as a gift. The later kabwsk surface is retained as an Algerian Arabic kabous-like weapon or gun, while the exact surrounding roles remain uncertain.",
        "korean": "대화는 ‘mal 7ia kifah?’라는 명시적 질문으로 시작해요. 이는 ‘무슨 일이야, 하이아?’ 또는 불확실한 이름·호격일 수 있어 표면형을 보존해요. 이어 잠깐 자리를 비웠다며 ‘dawlk’를 사용해 어느 날과 오늘의 일을 비교하는데, 이 표현의 방향은 무언가를 가져가거나 치우거나 건네는 것일 수 있어 선물로 확정하지 않아요. 뒤의 ‘kabwsk’ 표면형은 알제리어 kabous 계열의 권총·무기 의미로 보존하고, 주변 역할은 불확실하게 둬요.",
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
