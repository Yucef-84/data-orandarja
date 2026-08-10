"""Freeze the HeadGPT-approved MADOran Batch 01 review state."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

try:
    from scripts.build_madoran_enrichment_scaffold import (
        ENRICHMENT_OUT,
        EVENTS_OUT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
        write_tsv,
    )
    from scripts.validate_madoran_enrichment import check_enrichment_provenance
except ModuleNotFoundError:
    from build_madoran_enrichment_scaffold import (  # type: ignore
        ENRICHMENT_OUT,
        EVENTS_OUT,
        SOURCE_OUT,
        check_provenance_events,
        read_tsv,
        source_gate,
        write_tsv,
    )
    from validate_madoran_enrichment import check_enrichment_provenance  # type: ignore


ROOT = ENRICHMENT_OUT.parents[3]
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch01_qa.json"
REVIEW_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch01_review.json"
REVIEW_ID = "MADORAN-ENRICH-001-REVIEW-01"
REVIEWED_COMMIT = "2031147"


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))

    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    event_text = EVENTS_OUT.read_text(encoding="utf-8")
    source_uids = {row["source_uid"] for row in source_rows}
    event_check = check_provenance_events(event_text, source_uids)
    if event_check["result"] != "PASS" or event_check["events"] != 1432:
        raise RuntimeError(json.dumps(event_check, ensure_ascii=False))
    trace = check_enrichment_provenance(before_rows, event_text)
    if trace["result"] != "PASS":
        raise RuntimeError(json.dumps(trace, ensure_ascii=False))

    after_rows = [dict(row) for row in before_rows]
    linguistic_before = [
        tuple(row[field] for field in ("latin", "english", "korean", "cefr_level", "difficulty_score", "domain", "topic", "genre", "speech_act", "register", "context_dependency"))
        for row in before_rows
    ]
    for row in after_rows:
        sentno = int(row["sentno"])
        if 1 <= sentno <= 64:
            if row["enrichment_state"] == "flagged":
                if sentno not in {17, 63}:
                    raise RuntimeError(f"unexpected_flagged_row:{sentno}")
            elif row["enrichment_state"] == "draft":
                row["enrichment_state"] = "qa_passed"
            else:
                raise RuntimeError(f"unexpected_batch01_state:{sentno}:{row['enrichment_state']}")
        elif row["enrichment_state"] != "not_started":
            raise RuntimeError(f"outside_target_state_mutation:{sentno}")

    linguistic_after = [
        tuple(row[field] for field in ("latin", "english", "korean", "cefr_level", "difficulty_score", "domain", "topic", "genre", "speech_act", "register", "context_dependency"))
        for row in after_rows
    ]
    if linguistic_before != linguistic_after:
        raise RuntimeError("linguistic_fields_mutated_during_approval")

    qa_passed_rows = [row for row in after_rows if row["enrichment_state"] == "qa_passed"]
    flagged_rows = [row for row in after_rows if row["enrichment_state"] == "flagged"]
    not_started_rows = [row for row in after_rows if row["enrichment_state"] == "not_started"]
    if len(qa_passed_rows) != 62 or [row["sentno"] for row in flagged_rows] != ["17", "63"] or len(not_started_rows) != 1292:
        raise RuntimeError("unexpected_approved_state_counts")

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["enrichment_review_id"] = REVIEW_ID
    status["counts"].update(
        {
            "enrichment_completed_rows": 62,
            "enrichment_draft_rows": 0,
            "enrichment_flagged_rows": 2,
            "enrichment_not_started_rows": 1292,
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
        "batch_id": "MADORAN-ENRICH-001",
        "reviewed_commit": REVIEWED_COMMIT,
        "reviewer": "HeadGPT",
        "headgpt_result": "PASS",
        "p0": "NONE",
        "p1": "NONE",
        "qa_passed_rows": 62,
        "flagged_rows": ["17", "63"],
        "not_started_rows": 1292,
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "source_gate": "PASS",
        "linguistic_fields_modified": 0,
        "arabic_modified": 0,
        "provenance_events_before": 1432,
        "provenance_events_after": 1432,
        "provenance_modified": 0,
        "outside_target_mutations": 0,
        "reviewed_at": reviewed_at,
        "next_batch": {
            "batch_id": "MADORAN-ENRICH-002",
            "sentno_start": 65,
            "sentno_end": 128,
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
