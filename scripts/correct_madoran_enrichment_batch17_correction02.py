"""Reclassify two clear Batch 17 rows from flagged to draft after HeadGPT review."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch17 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "5c40544"
BATCH_ID = "MADORAN-ENRICH-017"
CORRECTION_ID = "MADORAN-ENRICH-017-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v17-correction-2"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch17_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch17_correction02_qa.json"
PROVENANCE_BEFORE = 14921
CORRECTIONS = {1040: {"enrichment_state": "draft"}, 1052: {"enrichment_state": "draft"}}


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

    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = 5
    status["counts"]["enrichment_flagged_rows"] = 760
    status["enrichment_correction_id"] = CORRECTION_ID
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = 5
    qa["flagged_rows"] = 59
    qa["correction_state_updates"] = 2
    qa["correction_history"][-1]["state_updates"] = 2
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 2
    correction["batch_artifact_sync_state_updates"] = 2
    correction["draft_rows"] = 5
    correction["flagged_rows"] = 59
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 2, "draft_rows": 5, "flagged_rows": 59})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
