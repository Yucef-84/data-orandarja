"""Apply MADOran Batch 07 using the established source-only application gates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch07 import (
    BATCH_ID,
    BATCH_OUT,
    BASE_COMMIT,
    MANIFEST_OUT,
    PROMPT_VERSION,
    TARGET_END,
    TARGET_START,
)
from scripts.build_madoran_enrichment_scaffold import ROOT


engine.BATCH_ID = BATCH_ID
engine.BASE_COMMIT = BASE_COMMIT
engine.PROMPT_VERSION = PROMPT_VERSION
engine.TARGET_START = TARGET_START
engine.TARGET_END = TARGET_END
engine.BATCH_OUT = BATCH_OUT
engine.MANIFEST_OUT = MANIFEST_OUT
engine.BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_qa.json"
engine.EXPECTED_EXISTING_EVENTS = 5413


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(engine.apply(), ensure_ascii=False, indent=2))
