"""Freeze the HeadGPT-approved MADOran Batch 03 review state.

This evidence-only approval changes only the workflow state of reviewed draft
rows. Source text, linguistic fields, processing flags, and provenance remain
unchanged.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.apply_madoran_enrichment_batch03 import BATCH_OUT, validate_batch_rows
from scripts.build_madoran_enrichment_batch03 import TARGET_END, TARGET_START
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


BATCH_ID = "MADORAN-ENRICH-003"
REVIEW_ID = "MADORAN-ENRICH-003-REVIEW-01"
REVIEWED_COMMIT = "984272d"
TARGET_FLAGGED = [
    "134",
    "136",
    "138",
    "139",
    "140",
    "166",
    "170",
    "172",
    "173",
    "175",
    "186",
    "187",
    "188",
    "192",
]
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_qa.json"
REVIEW_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_review.json"


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))

    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if not before_rows or list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    batch_check = validate_batch_rows(source_rows, batch_rows)
    if batch_check["result"] != "PASS":
        raise RuntimeError(json.dumps(batch_check, ensure_ascii=False))

    source_uids = {row["source_uid"] for row in source_rows}
    event_text = EVENTS_OUT.read_text(encoding="utf-8")
    event_check = check_provenance_events(event_text, source_uids)
    if event_check["result"] != "PASS" or event_check["events"] != 3036:
        raise RuntimeError(json.dumps(event_check, ensure_ascii=False))
    trace = check_enrichment_provenance(before_rows, event_text)
    if trace["result"] != "PASS" or trace["populated_fields"] != 2204:
        raise RuntimeError(json.dumps(trace, ensure_ascii=False))

    target_rows = [
        row for row in before_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END
    ]
    if len(target_rows) != 64:
        raise RuntimeError("unexpected_batch03_row_count")
    flagged_before = [
        row["sentno"] for row in target_rows if row["enrichment_state"] == "flagged"
    ]
    draft_before = [
        row["sentno"] for row in target_rows if row["enrichment_state"] == "draft"
    ]
    if flagged_before != TARGET_FLAGGED or len(draft_before) != 50:
        raise RuntimeError(
            json.dumps(
                {"flagged_before": flagged_before, "draft_count_before": len(draft_before)},
                ensure_ascii=False,
            )
        )

    after_rows = [dict(row) for row in before_rows]
    for before, after in zip(before_rows, after_rows):
        sentno = after["sentno"]
        if TARGET_START <= int(sentno) <= TARGET_END:
            if after["enrichment_state"] == "draft":
                after["enrichment_state"] = "qa_passed"
            elif after["enrichment_state"] == "flagged" and sentno in TARGET_FLAGGED:
                pass
            else:
                raise RuntimeError(f"unexpected_batch03_state:{sentno}:{after['enrichment_state']}")
        elif after != before:
            raise RuntimeError(f"outside_target_mutation:{sentno}")

    non_state_fields = [field for field in ENRICHMENT_FIELDS if field != "enrichment_state"]
    for before, after in zip(before_rows, after_rows):
        for field in non_state_fields:
            if before[field] != after[field]:
                raise RuntimeError(f"non_state_field_mutated:{before['sentno']}:{field}")

    counts = {
        state: sum(row["enrichment_state"] == state for row in after_rows)
        for state in ("qa_passed", "flagged", "draft", "not_started")
    }
    expected_counts = {
        "qa_passed": 158,
        "flagged": 34,
        "draft": 0,
        "not_started": 1164,
    }
    if counts != expected_counts:
        raise RuntimeError(json.dumps({"unexpected_approved_state_counts": counts}))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["decision_id"] = "HEAD-MADORAN-2026-08-11-01"
    status["updated_from_commit"] = REVIEWED_COMMIT
    status["enrichment_review_id"] = REVIEW_ID
    status["counts"].update(
        {
            "enrichment_completed_rows": 158,
            "enrichment_draft_rows": 0,
            "enrichment_flagged_rows": 34,
            "enrichment_not_started_rows": 1164,
            "processing_flags_populated_rows": 92,
        }
    )
    evidence_files = list(status.get("evidence_files", []))
    review_path = REVIEW_OUT.relative_to(ROOT).as_posix()
    if review_path not in evidence_files:
        evidence_files.append(review_path)
    status["evidence_files"] = evidence_files

    reviewed_at = current_utc_timestamp()
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
        "qa_passed_rows": 50,
        "flagged_rows": TARGET_FLAGGED,
        "not_started_rows": 1164,
        "batch03_state_before": {"draft": 50, "flagged": 14},
        "batch03_state_after": {"qa_passed": 50, "flagged": 14},
        "total_enrichment_state_after": counts,
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "source_gate": "PASS",
        "linguistic_fields_modified": 0,
        "processing_flags_modified": 0,
        "arabic_modified": 0,
        "provenance_events_before": 3036,
        "provenance_events_after": 3036,
        "provenance_modified": 0,
        "outside_target_mutations": 0,
        "reviewed_at": reviewed_at,
        "next_batch": {
            "batch_id": "MADORAN-ENRICH-004",
            "sentno_start": 193,
            "sentno_end": 256,
            "row_count": 64,
        },
    }

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["content_review_status"] = "headgpt_passed"
    qa["review_id"] = REVIEW_ID
    qa["reviewed_commit"] = REVIEWED_COMMIT

    write_tsv(ENRICHMENT_OUT, after_rows)
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW_OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return review


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
