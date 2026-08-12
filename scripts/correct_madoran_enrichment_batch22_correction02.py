"""Restore the omitted 1350 clause identified by HeadGPT."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch22 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "a2a4f51"
BATCH_ID = "MADORAN-ENRICH-022"
CORRECTION_ID = "MADORAN-ENRICH-022-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v22-correction-2"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch22_correction02_qa.json"
PROVENANCE_BEFORE = 19188

_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
surface = _batch_rows[1350]["latin"]
CORRECTIONS = {
    1350: {
        "english": f"The speaker exchanges peace greetings with a doctor, says ‘whenever you enter, you wink at me; you don’t like/love me anymore, is that it?’, asks why the doctor did not return the speaker’s wink, and keeps the final relation source-close as the opaque surface ‘tna9rfia’. Canonical surface sequence: `{surface}`.",
        "korean": f"화자는 의사와 평안 인사를 주고받고 ‘당신은 들어올 때마다 나에게 윙크해요. 이제 나를 좋아하지 않는 거예요, 그런 거예요?’라고 해요. 이어 왜 자신의 윙크에 답하지 않았느냐고 묻고 마지막 관계 표현 ‘tna9rfia’는 불확실하게 보존해요. canonical 표면 순서: `{surface}`.",
    }
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
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = sum(r["enrichment_state"] == "draft" for r in batch_rows)
    qa["flagged_rows"] = sum(r["enrichment_state"] == "flagged" for r in batch_rows)
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["draft_rows"] = qa["draft_rows"]
    correction["flagged_rows"] = qa["flagged_rows"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = sum(r["enrichment_state"] == "draft" for r in rows)
    status["counts"]["enrichment_flagged_rows"] = sum(r["enrichment_state"] == "flagged" for r in rows)
    status["counts"]["enrichment_not_started_rows"] = sum(r["enrichment_state"] == "not_started" for r in rows)
    evidence = list(status.get("evidence_files", []))
    if EVIDENCE_PATH not in evidence:
        evidence.append(EVIDENCE_PATH)
    status["evidence_files"] = evidence
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
