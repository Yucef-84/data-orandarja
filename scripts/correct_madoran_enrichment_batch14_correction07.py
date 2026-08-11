"""Apply the seventh HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "ad29613"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-07"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-7"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch14_correction07_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch14_correction07_qa.json"
PROVENANCE_BEFORE = 12209

CORRECTIONS = {
    852: {
        "latin": "mnitk ? lwkan jit ml9ta w la ma 3ndish asl blak n9bl bs7 ana 3ndi ma w khti ki ghadi ndir m3ahm . 9lbi rah in7r9 w al7l ? 9wl lmrtk ada 9blt arwa7 tkhtbni tma nshwfw .",
    },
    879: {
        "english": "The speaker tells the other person to go to the café because the speaker is coming. They swear the matter is not finished, then tell the addressee, in effect, ‘If you do not like my situation, go and complain or report it,’ before telling them to go. After that, the speaker says ‘Sorry, here—pay’ using a feminine imperative. The remaining words preserve an opaque payment/change exchange; the exact roles are uncertain, but a follow-up transaction turn is explicit.",
        "korean": "화자는 자신이 가고 있으니 상대에게 카페로 가라고 해요. 일이 끝나지 않았다고 맹세한 뒤, 상대에게 ‘내 상황이 마음에 들지 않으면 가서 항의하거나 신고해’라는 뜻으로 말하고 가라고 해요. 이어 ‘미안해, 자, 지불해’라는 여성형 명령을 하고, 뒤의 말은 지급·거스름돈과 관련된 불투명한 교환으로 보존해요. 정확한 역할은 불확실하지만 후속 거래 turn 자체는 명시돼 있어요.",
    },
}


def apply():
    engine.BASE_COMMIT = BASE_COMMIT
    engine.CORRECTION_ID = CORRECTION_ID
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.CORRECTION_QA_OUT = CORRECTION_QA_OUT
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.PROVENANCE_BEFORE = PROVENANCE_BEFORE
    engine.CORRECTIONS = CORRECTIONS
    return engine.apply()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
