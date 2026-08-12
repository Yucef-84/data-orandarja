"""Apply Batch 22 with source-only field-level provenance."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch22 import (
    BATCH_OUT,
    BATCH_ID,
    BASE_COMMIT,
    MANIFEST_OUT,
    PROMPT_VERSION,
    TARGET_END,
    TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import ROOT

QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_qa.json"
EXPECTED_EXISTING_EVENTS = 19038


def apply():
    engine.BATCH_ID = BATCH_ID
    engine.BASE_COMMIT = BASE_COMMIT
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    engine.BATCH_OUT = BATCH_OUT
    engine.MANIFEST_OUT = MANIFEST_OUT
    engine.BATCH_QA_OUT = QA_OUT
    engine.EXPECTED_EXISTING_EVENTS = EXPECTED_EXISTING_EVENTS
    result = engine.apply()
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    evidence = list(status.get("evidence_files", []))
    for path in (
        "data/master/qa/madoran_enrichment_batch22_generation_qa.json",
        "data/master/qa/madoran_enrichment_batch22_qa.json",
    ):
        if path not in evidence:
            evidence.append(path)
    status["evidence_files"] = evidence
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    QA_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
