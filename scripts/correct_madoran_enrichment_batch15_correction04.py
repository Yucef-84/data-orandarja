"""Apply the fourth HeadGPT-directed metadata correction for MADOran Batch 15."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine

BASE_COMMIT = "d975ec4"
BATCH_ID = "MADORAN-ENRICH-015"
CORRECTION_ID = "MADORAN-ENRICH-015-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v15-correction-4"
BATCH_OUT = engine.ROOT / "data/master/enrichment/batches/batch15_sentno_0897_0960.tsv"
BATCH_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_qa.json"
CORRECTION_QA_OUT = engine.ROOT / "data/master/qa/madoran_enrichment_batch15_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch15_correction04_qa.json"
PROVENANCE_BEFORE = 13062

CORRECTIONS = {
    946: {
        "speech_act": "exclamation",
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
