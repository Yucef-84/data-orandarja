"""Freeze the HeadGPT-approved MADOran Batch 09 review state."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import apply_madoran_enrichment_batch06 as engine
from scripts.build_madoran_enrichment_batch09 import BATCH_OUT, TARGET_END, TARGET_START
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS,
    ENRICHMENT_OUT,
    EVENTS_OUT,
    ROOT,
    SOURCE_OUT,
    check_provenance_events,
    read_tsv,
    source_gate,
    write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance


engine.TARGET_START = TARGET_START
engine.TARGET_END = TARGET_END
validate_batch_rows = engine.validate_batch_rows

BATCH_ID = "MADORAN-ENRICH-009"
REVIEW_ID = "MADORAN-ENRICH-009-REVIEW-01"
REVIEWED_COMMIT = "804ddc8dc5543edcf3287572ed2ad008fd99c7a4"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_review.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def apply() -> dict[str, object]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if head != REVIEWED_COMMIT:
        raise RuntimeError(f"reviewed_commit_mismatch:{head}:{REVIEWED_COMMIT}")
    if source_gate()["result"] != "PASS":
        raise RuntimeError("source_gate_failed")

    source = read_tsv(SOURCE_OUT)
    before = read_tsv(ENRICHMENT_OUT)
    batch = read_tsv(BATCH_OUT)
    if list(before[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    batch_check = validate_batch_rows(source, batch)
    if batch_check["result"] != "PASS":
        raise RuntimeError(json.dumps(batch_check, ensure_ascii=False))

    master = {row["sentno"]: row for row in before}
    for batch_row in batch:
        for field, value in batch_row.items():
            if master[batch_row["sentno"]][field] != value:
                raise RuntimeError(f"batch_artifact_mismatch:{batch_row['sentno']}:{field}")

    events = EVENTS_OUT.read_text(encoding="utf-8")
    event_check = check_provenance_events(events, {row["source_uid"] for row in source})
    trace = check_enrichment_provenance(before, events)
    if (
        event_check["result"] != "PASS"
        or event_check["events"] != 7820
        or trace["result"] != "PASS"
        or trace["populated_fields"] != 6739
    ):
        raise RuntimeError(json.dumps({"events": event_check, "trace": trace}, ensure_ascii=False))

    target = [row for row in before if TARGET_START <= int(row["sentno"]) <= TARGET_END]
    flagged = [row["sentno"] for row in target if row["enrichment_state"] == "flagged"]
    drafts = [row["sentno"] for row in target if row["enrichment_state"] == "draft"]
    if len(target) != 64 or len(flagged) != 55 or len(drafts) != 9:
        raise RuntimeError("unexpected_batch09_preapproval_state")

    after = [dict(row) for row in before]
    for row in after:
        if TARGET_START <= int(row["sentno"]) <= TARGET_END and row["enrichment_state"] == "draft":
            row["enrichment_state"] = "qa_passed"
    counts = {
        state: sum(row["enrichment_state"] == state for row in after)
        for state in ("qa_passed", "flagged", "draft", "not_started")
    }
    expected = {"qa_passed": 302, "flagged": 274, "draft": 0, "not_started": 780}
    if counts != expected:
        raise RuntimeError(json.dumps(counts))

    reviewed_at = now()
    review = {
        "review_id": REVIEW_ID,
        "batch_id": BATCH_ID,
        "reviewed_commit": REVIEWED_COMMIT,
        "reviewer": "HeadGPT",
        "headgpt_result": "PASS",
        "p0": "NONE",
        "p1": "NONE",
        "structure": "PASS",
        "provenance": "PASS",
        "isolation": "PASS",
        "next_batch_allowed": True,
        "qa_passed_rows": 9,
        "flagged_rows": flagged,
        "not_started_rows": 780,
        "batch09_state_before": {"draft": 9, "flagged": 55},
        "batch09_state_after": {"qa_passed": 9, "flagged": 55},
        "total_enrichment_state_after": counts,
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "source_gate": "PASS",
        "linguistic_fields_modified": 0,
        "processing_flags_modified": 0,
        "arabic_modified": 0,
        "correction_events_total": 817,
        "provenance_events_before": 7820,
        "provenance_events_after": 7820,
        "provenance_modified": 0,
        "outside_target_mutations": 0,
        "batch_artifact_sync": "PASS",
        "reviewed_batch_rows": 64,
        "reviewed_at": reviewed_at,
        "review_summary": (
            "HeadGPT independently rechecked all 64 rows against canonical Arabic at the final correction commit. "
            "Three correction rounds resolved the identified French/Darija, cultural, speaker, metadata, and "
            "Hamoud/حمبوك interpretation issues; no P0/P1 or regressions remained."
        ),
        "next_batch": {"batch_id": "MADORAN-ENRICH-010", "sentno_start": 577, "sentno_end": 640, "row_count": 64},
    }

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["decision_id"] = "HEAD-MADORAN-2026-08-11-06"
    status["updated_from_commit"] = REVIEWED_COMMIT
    status["enrichment_batch_id"] = BATCH_ID
    status["enrichment_review_id"] = REVIEW_ID
    status["counts"] = {
        "enrichment_completed_rows": 302,
        "enrichment_draft_rows": 0,
        "enrichment_flagged_rows": 274,
        "enrichment_not_started_rows": 780,
        "processing_flags_populated_rows": 403,
    }
    review_path = REVIEW_OUT.relative_to(ROOT).as_posix()
    evidence = list(status.get("evidence_files", []))
    status["evidence_files"] = evidence if review_path in evidence else evidence + [review_path]

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa.update(
        {
            "content_review_status": "headgpt_passed",
            "review_id": REVIEW_ID,
            "reviewed_commit": REVIEWED_COMMIT,
            "reviewed_at": reviewed_at,
            "approved_draft_rows": 9,
            "approved_flagged_rows": 55,
        }
    )

    write_tsv(ENRICHMENT_OUT, after)
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW_OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return review


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
