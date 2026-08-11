"""Freeze the HeadGPT-approved MADOran Batch 05 review state."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
if __package__ in {None, ""}: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apply_madoran_enrichment_batch05 import BATCH_OUT, validate_batch_rows
from scripts.build_madoran_enrichment_batch05 import TARGET_END, TARGET_START
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT, check_provenance_events, read_tsv, source_gate, write_tsv
from scripts.validate_madoran_enrichment import check_enrichment_provenance
BATCH_ID = "MADORAN-ENRICH-005"
REVIEW_ID = "MADORAN-ENRICH-005-REVIEW-01"
REVIEWED_COMMIT = "3817d23ea9a5afbfc2f03316d66e4184c459d485"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch05_qa.json"
REVIEW_OUT = ROOT / "data/master/qa/madoran_enrichment_batch05_review.json"
def now(): return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
def apply():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if head != REVIEWED_COMMIT: raise RuntimeError(f"reviewed_commit_mismatch:{head}:{REVIEWED_COMMIT}")
    if source_gate()["result"] != "PASS": raise RuntimeError("source_gate_failed")
    source = read_tsv(SOURCE_OUT); before = read_tsv(ENRICHMENT_OUT); batch = read_tsv(BATCH_OUT)
    if list(before[0]) != ENRICHMENT_FIELDS: raise RuntimeError("enrichment_header_mismatch")
    check = validate_batch_rows(source, batch)
    if check["result"] != "PASS": raise RuntimeError(json.dumps(check, ensure_ascii=False))
    master = {r["sentno"]: r for r in before}
    for b in batch:
        for field, value in b.items():
            if master[b["sentno"]][field] != value: raise RuntimeError(f"batch_artifact_mismatch:{b['sentno']}:{field}")
    events = EVENTS_OUT.read_text(encoding="utf-8")
    ec = check_provenance_events(events, {r["source_uid"] for r in source})
    trace = check_enrichment_provenance(before, events)
    if ec["result"] != "PASS" or ec["events"] != 4596 or trace["result"] != "PASS" or trace["populated_fields"] != 3725: raise RuntimeError(json.dumps({"events": ec, "trace": trace}, ensure_ascii=False))
    target = [r for r in before if TARGET_START <= int(r["sentno"]) <= TARGET_END]
    flagged = [r["sentno"] for r in target if r["enrichment_state"] == "flagged"]
    drafts = [r["sentno"] for r in target if r["enrichment_state"] == "draft"]
    if len(target) != 64 or len(flagged) != 30 or len(drafts) != 34: raise RuntimeError("unexpected_batch05_preapproval_state")
    after = [dict(r) for r in before]
    for row in after:
        if TARGET_START <= int(row["sentno"]) <= TARGET_END and row["enrichment_state"] == "draft": row["enrichment_state"] = "qa_passed"
    counts = {s: sum(r["enrichment_state"] == s for r in after) for s in ("qa_passed", "flagged", "draft", "not_started")}
    expected = {"qa_passed": 233, "flagged": 87, "draft": 0, "not_started": 1036}
    if counts != expected: raise RuntimeError(json.dumps(counts))
    reviewed_at = now()
    review = {"review_id": REVIEW_ID, "batch_id": BATCH_ID, "reviewed_commit": REVIEWED_COMMIT, "reviewer": "HeadGPT", "headgpt_result": "PASS", "p0": "NONE", "p1": "NONE", "structure": "PASS", "provenance": "PASS", "isolation": "PASS", "next_batch_allowed": True, "qa_passed_rows": 34, "flagged_rows": flagged, "not_started_rows": 1036, "batch05_state_before": {"draft": 34, "flagged": 30}, "batch05_state_after": {"qa_passed": 34, "flagged": 30}, "total_enrichment_state_after": counts, "morphology_gate": "BLOCKED_UPSTREAM_DEFECT", "source_gate": "PASS", "linguistic_fields_modified": 0, "processing_flags_modified": 0, "arabic_modified": 0, "provenance_events_before": 4596, "provenance_events_after": 4596, "provenance_modified": 0, "outside_target_mutations": 0, "batch_artifact_sync": "PASS", "reviewed_batch_rows": 64, "reviewed_at": reviewed_at, "next_batch": {"batch_id": "MADORAN-ENRICH-006", "sentno_start": 321, "sentno_end": 384, "row_count": 64}}
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8")); status["decision_id"] = "HEAD-MADORAN-2026-08-11-03"; status["updated_from_commit"] = REVIEWED_COMMIT; status["enrichment_batch_id"] = BATCH_ID; status["enrichment_review_id"] = REVIEW_ID; status["counts"] = {"enrichment_completed_rows": 233, "enrichment_draft_rows": 0, "enrichment_flagged_rows": 87, "enrichment_not_started_rows": 1036, "processing_flags_populated_rows": 205}
    review_path = REVIEW_OUT.relative_to(ROOT).as_posix(); status.setdefault("evidence_files", []); status["evidence_files"] = [*status["evidence_files"], review_path] if review_path not in status["evidence_files"] else status["evidence_files"]
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8")); qa.update({"content_review_status": "headgpt_passed", "review_id": REVIEW_ID, "reviewed_commit": REVIEWED_COMMIT, "reviewed_at": reviewed_at, "approved_draft_rows": 34, "approved_flagged_rows": 30})
    write_tsv(ENRICHMENT_OUT, after); STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); REVIEW_OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return review
if __name__ == "__main__": print(json.dumps(apply(), ensure_ascii=False, indent=2))
