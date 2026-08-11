"""Apply the first HeadGPT correction set for MADOran Batch 08."""
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
from scripts.build_madoran_enrichment_scaffold import (
    EMPTY_FIELDS,
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


BASE_COMMIT = "f2d67f6"
CORRECTION_ID = "MADORAN-ENRICH-008-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v8-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 449
TARGET_END = 512
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch08_correction01_qa.json"


CORRECTIONS = {
    457: {
        "english": (
            "The woman with blurred or weak eyesight needs only kohl, and the monkey needs only roses. "
            "The exact shade of the first description is context-dependent."
        ),
        "korean": (
            "눈이 흐리거나 시력이 약한 여자는 콜만 필요하고, 원숭이는 장미만 필요해요. "
            "첫 번째 표현의 정확한 뉘앙스는 문맥에 따라 달라요."
        ),
    },
    458: {
        "english": (
            "They gave the donkey qarnful to smell, and it ate it. The word qarnful may refer to a clove or a "
            "carnation-like item here, so the exact lexical sense is ambiguous."
        ),
        "korean": (
            "사람들이 당나귀에게 냄새 맡으라고 qarnful을 주었더니 당나귀가 먹어 버렸어요. 여기서 qarnful은 "
            "정향이나 카네이션 계열을 가리킬 수 있어 정확한 어휘 의미는 불분명해요."
        ),
    },
    462: {
        "english": (
            "The phrase appears to refer to a living person's share, but its syntax, subject, and referent are "
            "incomplete or ambiguous."
        ),
        "korean": (
            "이 표현은 살아 있는 사람의 몫을 가리키는 듯하지만, 문장 구조와 주체, 지시 대상이 불완전하거나 "
            "모호해요."
        ),
    },
    468: {
        "english": (
            "I am digging his mother's grave, and he is running away from me with an axe. The parenthetical marks "
            "this as an eastern or regional expression."
        ),
        "korean": (
            "나는 그의 어머니 무덤을 파고 있는데, 그는 도끼를 들고 나에게서 달아나고 있어요. 괄호는 이 표현이 "
            "동부 지역의 말임을 표시해요."
        ),
    },
    469: {
        "english": (
            "Act like your neighbor, or change the door of your house—that is, change your place or move house. "
            "The exact proverb implication is context-dependent."
        ),
        "korean": (
            "이웃처럼 행동하든지, 아니면 집의 문, 곧 거처를 바꾸라는 뜻이에요. 정확한 속담의 함의는 문맥에 "
            "따라 달라요."
        ),
    },
    482: {
        "english": (
            "He went to the wadi and found it dry, or the wadi had gone dry; the subject and direction are ambiguous."
        ),
        "korean": (
            "그가 와디에 갔더니 말라 있었거나, 와디가 말라 버렸다는 뜻일 수 있어요. 주체와 방향은 모호해요."
        ),
        "processing_flags": "idiom_culture|source_ambiguity",
    },
    494: {
        "english": (
            "The cat teaches its father to jump. Sleep with the chickens and wake up making a chicken call. The "
            "animal and wake-up expression is colloquial; the exact proverb implication is context-dependent."
        ),
        "korean": (
            "고양이가 자기 아버지에게 뛰는 법을 가르쳐요. 닭들과 함께 자면 아침에 닭 울음소리를 내며 일어나요. "
            "동물과 기상 표현은 구어적이며 정확한 속담의 함의는 문맥에 따라 달라요."
        ),
    },
    510: {
        "english": (
            "He came trying to put things right and ended up making the loss or problem worse; this proverb points to "
            "an attempt that produces an unintended negative result."
        ),
        "korean": (
            "일을 바로잡으려다 오히려 손해나 문제를 더 키웠다는 뜻이에요. 이 속담은 의도와 달리 부정적인 결과를 "
            "낳은 상황을 가리켜요."
        ),
    },
}

STATE_CORRECTIONS = {482: "flagged"}


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
        sentno = int(row["sentno"])
        if sentno in CORRECTIONS:
            for field, value in CORRECTIONS[sentno].items():
                row[field] = value
                changed_fields += 1
        if sentno in STATE_CORRECTIONS:
            row["enrichment_state"] = STATE_CORRECTIONS[sentno]

    corrected_batch = [dict(row) for row in batch]
    for row in corrected_batch:
        sentno = int(row["sentno"])
        for field, value in CORRECTIONS.get(sentno, {}).items():
            row[field] = value
        if sentno in STATE_CORRECTIONS:
            row["enrichment_state"] = STATE_CORRECTIONS[sentno]

    expected_events = sum(len(fields) for fields in CORRECTIONS.values())
    if changed_fields != expected_events:
        raise RuntimeError(f"changed_cell_count:{changed_fields}:{expected_events}")

    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 6982:
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
        or combined_check["events"] != 6982 + expected_events
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
    evidence_path = "data/master/qa/madoran_enrichment_batch08_correction01_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append(
        {
            "correction_id": CORRECTION_ID,
            "changed_fields": changed_fields,
            "state_updates": len(STATE_CORRECTIONS),
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
            "correction_state_updates": len(STATE_CORRECTIONS),
            "correction_rows": len(CORRECTIONS),
            "correction_provenance_events": expected_events,
            "new_provenance_events": int(qa.get("new_provenance_events", 0)) + expected_events,
            "total_provenance_events": 6982 + expected_events,
            "expected_total_provenance_events": 6982 + expected_events,
            "flagged_rows": sum(row["enrichment_state"] == "flagged" for row in corrected_batch),
            "draft_rows": sum(row["enrichment_state"] == "draft" for row in corrected_batch),
            "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
            "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
            "content_review_status": "pending_headgpt_correction_review",
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-008",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": changed_fields,
        "state_updates": len(STATE_CORRECTIONS),
        "new_provenance_events": expected_events,
        "provenance_events_before": 6982,
        "provenance_events_after": 6982 + expected_events,
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
        "batch_artifact_sync_state_updates": len(STATE_CORRECTIONS),
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
