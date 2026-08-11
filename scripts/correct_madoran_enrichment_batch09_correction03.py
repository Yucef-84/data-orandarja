"""Apply the final HeadGPT correction for MADOran Batch 09 Sentno 532."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch09 import BATCH_ID, BATCH_OUT, TARGET_END, TARGET_START
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


BASE_COMMIT = "920c84d"
CORRECTION_ID = "MADORAN-ENRICH-009-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v9-correction-3"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_correction03_qa.json"


CORRECTIONS = {
    532: {
        "english": (
            "Top up my Flexy, please! Unfortunately, the next phrase sounds like French 'en même temps' ('at the "
            "same time'); the phrase 'حمبوك بعديني' means 'please, move away from me/leave me alone,' while other "
            "surrounding wording is unclear. Do not embarrass me by flirting with my friend in front of me, you whore; "
            "I will not let this pass. Go away and leave me alone, please ('حمبوك'). Several slang phrases are unclear."
        ),
        "korean": (
            "플렉시를 충전해 줘요! 안타깝게도 다음 표현은 프랑스어 ‘en même temps’(동시에)처럼 들려요. ‘حمبوك بعديني’는 "
            "‘제발, 나에게서 떨어져요/나를 내버려 둬요’라는 뜻이고, 그 밖의 주변 표현은 불분명해요. 내 앞에서 내 "
            "친구에게 추근대며 나를 망신시키지 마, 이 창녀야. 그냥 넘기지 않을 테니 멀리 가서 나를 내버려 둬요, "
            "제발(‘حمبوك’). 몇몇 속어 표현은 불분명해요."
        ),
    }
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
    corrected_batch = [dict(row) for row in batch]
    changed_fields = 0
    for row in after:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value
            changed_fields += 1
    for row in corrected_batch:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value

    expected_events = sum(len(fields) for fields in CORRECTIONS.values())
    if changed_fields != expected_events or expected_events != 2:
        raise RuntimeError(f"correction_shape:{changed_fields}:{expected_events}")

    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 7818:
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
        or combined_check["events"] != 7818 + expected_events
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
    evidence_path = "data/master/qa/madoran_enrichment_batch09_correction03_qa.json"
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
            "total_provenance_events": 7818 + expected_events,
            "expected_total_provenance_events": 7818 + expected_events,
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
        "provenance_events_before": 7818,
        "provenance_events_after": 7818 + expected_events,
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
