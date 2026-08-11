"""Apply the third HeadGPT Batch 06 correction set with append-only provenance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch06 import BATCH_OUT
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


BASE_COMMIT = "b8cf476"
CORRECTION_ID = "MADORAN-ENRICH-006-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v6-correction-3"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 321
TARGET_END = 384
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_correction03_qa.json"


CORRECTIONS = {
    337: {
        "english": (
            "The second category is the one who gets up early to study, or gets dressed and puts on makeup; "
            "in short, you find them spending all their time at university, even eating breakfast outside "
            "sometimes when they have money, or at the university restaurant."
        ),
        "korean": (
            "둘째 부류는 일찍 일어나 공부하거나 옷을 입고 화장하는 사람이야. "
            "한마디로 대학에서 시간을 거의 다 보내고, 돈이 있으면 가끔 밖에서 아침을 먹거나 "
            "대학 식당에서 먹지."
        ),
    },
    383: {
        "english": (
            "If you have made lamb, you can add the chicken stock cube with it; it gives a very nice flavor. "
            "I do not add it, but some people like to."
        ),
        "korean": (
            "양고기를 만들었다면 닭고기 육수 큐브를 그것과 함께 넣어도 돼요. 아주 좋은 맛을 내요. "
            "나는 넣지 않지만 좋아하는 사람도 있어요."
        ),
        "topic": "harira_lamb_and_chicken_stock_cube",
        "context_dependency": "high",
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


def apply() -> dict:
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
    if not all(TARGET_START <= int(row["sentno"]) <= TARGET_END for row in batch):
        raise RuntimeError("batch_range_mismatch")

    after = [dict(row) for row in before]
    correction_sentnos = {str(sentno) for sentno in CORRECTIONS}
    changed = 0
    for row in after:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value
            changed += 1
    if changed != 6:
        raise RuntimeError(f"changed_cell_count:{changed}")

    corrected_batch = [dict(row) for row in batch]
    for row in corrected_batch:
        if row["sentno"] in correction_sentnos:
            for field, value in CORRECTIONS[int(row["sentno"])].items():
                row[field] = value

    source_uids = {row["source_uid"] for row in source}
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 5407:
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
    if combined_check["result"] != "PASS" or combined_check["events"] != 5413 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"].update(
        {
            "enrichment_completed_rows": 233,
            "enrichment_draft_rows": 24,
            "enrichment_flagged_rows": 127,
            "enrichment_not_started_rows": 972,
            "processing_flags_populated_rows": 249,
        }
    )
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch06_correction03_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append(
        {
            "correction_id": CORRECTION_ID,
            "changed_fields": len(new_events),
            "rows": len(CORRECTIONS),
            "provenance_events": len(new_events),
        }
    )
    qa.update(
        {
            "correction_id": CORRECTION_ID,
            "latest_correction_id": CORRECTION_ID,
            "correction_history": history,
            "correction_changed_fields": len(new_events),
            "correction_rows": len(CORRECTIONS),
            "correction_provenance_events": len(new_events),
            "new_provenance_events": 748 + 52 + 11 + len(new_events),
            "total_provenance_events": 5413,
            "expected_total_provenance_events": 5413,
            "content_review_status": "pending_headgpt_correction_review",
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-006",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": len(new_events),
        "new_provenance_events": len(new_events),
        "provenance_events_before": 5407,
        "provenance_events_after": 5413,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 24,
        "flagged_rows": 40,
        "processing_flags_populated_rows": 44,
        "batch_artifact_sync": "PASS",
        "batch_artifact_sync_changed_fields": len(new_events),
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
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
