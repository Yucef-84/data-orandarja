"""Apply the final HeadGPT-directed correction for MADOran Batch 17."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch17 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "c75c231"
BATCH_ID = "MADORAN-ENRICH-017"
CORRECTION_ID = "MADORAN-ENRICH-017-CORRECTION-05"
PROMPT_VERSION = "madoran-source-enrichment-v17-correction-5"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction05_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch17_correction05_qa.json"
PROVENANCE_BEFORE = 14971

CORRECTIONS = {
    1086: {
        "english": "One speaker says, ‘I told you, they did it; rely on us,’ while another voice denies relying on anyone. They ask how they will attack us and answer that there are dogs, only talk, repeating the question about how they will attack. Another speaker says they want to hit you with a flitshat, ground-to-ground, repeating ard ard. The separate opaque surface 3idan 9a3 ma w9fwsh is retained without turning it into a question about the 3idan; the following separate question ard jw kain? is also preserved as an opaque ground-to-air or ground question. A reply says no, the 3idan have slept. The exchange then preserves the explicit hidden-ember clauses and the later opaque surfaces raki 9albtha, 9lbwa khir, and the address ya stwta without compression.",
        "korean": "한 화자는 ‘내가 말했잖아, 그들이 그 일을 했어. 우리에게 의지해’라고 하지만 다른 목소리는 아무에게도 의지하지 않았다고 부인해요. 어떻게 우리를 공격할지 묻고 개들이 있지만 말뿐이라고 답하며 공격 방법을 다시 물어요. 다른 화자는 flitshat으로 너희를 치고, 지대지 방식으로, ard ard라고 반복해요. 불투명한 표면형 ‘3idan 9a3 ma w9fwsh’는 3idan에 대한 질문으로 바꾸지 않고 별도로 보존하며, 뒤의 별도 질문 ‘ard jw kain?’도 불투명한 지대공 또는 지상 관련 질문으로 보존해요. 대답은 아니라고 하며 3idan이 잠들었다고 해요. 이어 숨겨진 불씨 절과 뒤의 불투명한 raki 9albtha, 9lbwa khir, ya stwta 호칭도 압축하지 않고 보존해요.",
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

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = 7
    qa["flagged_rows"] = 57
    qa["correction_state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["draft_rows"] = 7
    correction["flagged_rows"] = 57
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"draft_rows": 7, "flagged_rows": 57})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
