"""Apply the second HeadGPT correction set for MADOran Batch 08."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch08 import BATCH_OUT
from scripts.build_madoran_enrichment_batch08 import TARGET_END, TARGET_START
from scripts.build_madoran_enrichment_batch08 import BATCH_ID
from scripts.build_madoran_enrichment_batch08 import BASE_COMMIT as GENERATION_BASE_COMMIT
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


BASE_COMMIT = "64b1eac"
CORRECTION_ID = "MADORAN-ENRICH-008-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v8-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_correction02_qa.json"


CORRECTIONS = {
    468: {
        "english": (
            "I am digging his mother's grave for him, and he is running away from me with an axe. The parenthetical "
            "marks this as an eastern or regional expression."
        ),
        "korean": (
            "나는 그를 위해 그의 어머니 무덤을 파고 있는데, 그는 도끼를 들고 나에게서 달아나고 있어요. 괄호는 "
            "이 표현이 동부 지역의 말임을 표시해요."
        ),
    },
    510: {
        "english": (
            "He came trying to put things right and 'left nine behind,' ending up making the loss or problem worse. "
            "Literally, the proverb mentions nine; its implied meaning is an attempt that produces an unintended "
            "negative result."
        ),
        "korean": (
            "일을 바로잡으러 왔다가 ‘아홉을 남겨’ 손해나 문제를 더 키웠다는 뜻이에요. 문자적으로는 아홉이라는 "
            "숫자를 언급하고, 함의는 의도와 달리 부정적인 결과를 낳은 시도를 가리켜요."
        ),
    },
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid: str, field: str, value: str, generated_at: str) -> dict[str, str]:
    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": "llm_source_only_enrichment_correction",
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_state": "generated",
    }


def apply() -> dict[str, object]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if not head.startswith(BASE_COMMIT):
        raise RuntimeError(f"base_commit_mismatch:{head}:{BASE_COMMIT}")
    if source_gate()["result"] != "PASS":
        raise RuntimeError("source_gate_failed")

    source = read_tsv(SOURCE_OUT)
    before = read_tsv(ENRICHMENT_OUT)
    batch = read_tsv(BATCH_OUT)
    if list(before[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    if len(batch) != TARGET_END - TARGET_START + 1 or not all(
        TARGET_START <= int(row["sentno"]) <= TARGET_END for row in batch
    ):
        raise RuntimeError("batch_range_mismatch")

    source_uids = {row["source_uid"] for row in source}
    master_before = {row["sentno"]: row for row in before}
    batch_before = {row["sentno"]: row for row in batch}
    for sentno in batch_before:
        if any(master_before[sentno].get(field) != batch_before[sentno].get(field) for field in ENRICHMENT_FIELDS):
            raise RuntimeError(f"batch_master_mismatch_before:{sentno}")

    after = [dict(row) for row in before]
    changed_fields = 0
    for row in after:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value
            changed_fields += 1

    corrected_batch = [dict(row) for row in batch]
    for row in corrected_batch:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value

    expected_events = sum(len(fields) for fields in CORRECTIONS.values())
    if changed_fields != expected_events:
        raise RuntimeError(f"changed_cell_count:{changed_fields}:{expected_events}")

    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 6999:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))

    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [
        event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at)
        for sentno in sorted(CORRECTIONS)
        for field in CORRECTIONS[sentno]
    ]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if (
        combined_check["result"] != "PASS"
        or combined_check["events"] != 6999 + expected_events
        or trace["result"] != "PASS"
    ):
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"] = {
        "enrichment_completed_rows": sum(row["enrichment_state"] in {"qa_passed", "reviewed"} for row in after),
        "enrichment_draft_rows": sum(row["enrichment_state"] == "draft" for row in after),
        "enrichment_flagged_rows": sum(row["enrichment_state"] == "flagged" for row in after),
        "enrichment_not_started_rows": sum(row["enrichment_state"] == "not_started" for row in after),
        "processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in after),
    }
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch08_correction02_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append(
        {
            "correction_id": CORRECTION_ID,
            "changed_fields": changed_fields,
            "state_updates": 0,
            "rows": len(CORRECTIONS),
            "provenance_events": expected_events,
        }
    )
    qa.update(
        {
            "correction_id": CORRECTION_ID,
            "latest_correction_id": CORRECTION_ID,
            "correction_history": history,
            "correction_changed_fields": changed_fields,
            "correction_state_updates": 0,
            "correction_rows": len(CORRECTIONS),
            "correction_provenance_events": expected_events,
            "new_provenance_events": int(qa.get("new_provenance_events", 0)) + expected_events,
            "total_provenance_events": 6999 + expected_events,
            "expected_total_provenance_events": 6999 + expected_events,
            "content_review_status": "pending_headgpt_correction_review",
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": changed_fields,
        "state_updates": 0,
        "new_provenance_events": expected_events,
        "provenance_events_before": 6999,
        "provenance_events_after": 6999 + expected_events,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": sum(row["enrichment_state"] == "draft" for row in corrected_batch),
        "flagged_rows": sum(row["enrichment_state"] == "flagged" for row in corrected_batch),
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "batch_artifact_sync": "PASS",
        "batch_artifact_sync_changed_fields": changed_fields,
        "batch_artifact_sync_state_updates": 0,
        "generated_at": generated_at,
        "outputs": {
            "batch": BATCH_OUT.relative_to(ROOT).as_posix(),
            "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(),
            "provenance": EVENTS_OUT.relative_to(ROOT).as_posix(),
        },
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
