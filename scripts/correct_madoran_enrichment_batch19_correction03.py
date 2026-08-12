"""Apply the final HeadGPT-directed semantic correction for MADOran Batch 19."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch19 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "e7605a2"
BATCH_ID = "MADORAN-ENRICH-019"
CORRECTION_ID = "MADORAN-ENRICH-019-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v19-correction-3"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch19_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch19_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch19_correction03_qa.json"
PROVENANCE_BEFORE = 16849

CORRECTIONS = {
    1199: {
        "english": "In a long anecdote, the speaker describes donkey carts carrying vegetables, carts blocking narrow streets, and Americans arriving in jeeps and trucks in the Arab quarters. The Americans were afraid and shouted the English command hariwb or ariiwb man, meaning ‘move quickly.’ Local speakers reduced it in stages: arii, then arii ab, then arii mah, and finally ara, which became a cart-clearing expression. The speaker ends with the source-close phrase khatini hada tnaz ibghi i9sr bzaf, preserving the direction ‘leave me out of this; this joker or teaser likes to joke around a lot.’ The phrase is not interpreted as wanting to shorten something.",
        "korean": "긴 일화에서 화자는 채소를 싣는 당나귀 수레와 수레로 막힌 좁은 길, 아랍인 구역에 지프와 트럭을 타고 온 미국인을 설명해요. 미국인들은 두려워하며 ‘빨리 움직여’라는 뜻의 영어 명령 hariwb 또는 ariiwb man을 외쳤고, 현지인들은 이를 arii, arii ab, arii mah, 마지막으로 ara로 단계적으로 줄였다고 해요. ara는 수레에게 길을 비키라고 하는 표현이 되었으며, 마지막 khatini hada tnaz ibghi i9sr bzaf라는 원문은 ‘이 일에서 나를 빼 줘. 이 익살꾼 또는 놀리는 사람은 농담을 아주 많이 해’라는 방향으로 보존해요. 이를 무언가를 줄이고 싶다는 뜻으로 해석하지 않아요.",
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
    qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    correction["state_updates"] = 0
    correction["batch_artifact_sync_state_updates"] = 0
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 0, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
