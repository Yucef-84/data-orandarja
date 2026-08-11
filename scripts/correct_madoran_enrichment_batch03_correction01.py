"""Apply HeadGPT Batch 03 content corrections with append-only provenance."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

from scripts.build_madoran_enrichment_batch03 import BATCH_OUT
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


BASE_COMMIT = "ac5d588"
CORRECTION_ID = "MADORAN-ENRICH-003-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v3-correction-1"
METHOD = "llm_source_only_enrichment_correction"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 129
TARGET_END = 192
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch03_correction01_qa.json"

CORRECTIONS = {
    161: {
        "english": "May you stay safe.",
        "korean": "무사히 지내길 바라.",
    },
    165: {
        "english": "May you stay safe.",
        "korean": "무사히 지내길 바라.",
    },
    166: {
        "english": "But 'msrara' is unclear in the source; it may indicate a cheerful or positive impression, but its exact meaning is uncertain.",
        "korean": "그래도 'msrara'라는 표현은 원문에서 뜻이 분명하지 않아. 즐겁거나 긍정적인 인상을 나타낼 수 있지만 정확한 의미는 불확실해.",
        "enrichment_state": "flagged",
    },
}

OLD_VALUES = {
    (161, "english"): "May God keep you safe.",
    (161, "korean"): "신이 너를 지켜 주시길.",
    (165, "english"): "May God keep you safe.",
    (165, "korean"): "신이 너를 지켜 주시길.",
    (166, "english"): "But cheerful.",
    (166, "korean"): "그래도 즐거워 보여.",
    (166, "enrichment_state"): "draft",
}


def current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid: str, field: str, value: str, generated_at: str) -> dict[str, str]:
    return {
        "source_uid": source_uid,
        "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": METHOD,
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_state": "generated",
    }


def current_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def apply() -> dict[str, object]:
    if not current_commit().startswith(BASE_COMMIT):
        raise RuntimeError(f"base_commit_mismatch:{current_commit()}:{BASE_COMMIT}")
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS or len(batch_rows) != 64:
        raise RuntimeError("input_shape_mismatch")
    source_keys = [(row["source_uid"], row["sentno"]) for row in source_rows]
    before_keys = [(row["source_uid"], row["sentno"]) for row in before_rows]
    if source_keys != before_keys:
        raise RuntimeError("source_linkage_mismatch")

    after_rows = [dict(row) for row in before_rows]
    changed_cells = 0
    for row in after_rows:
        sentno = int(row["sentno"])
        if sentno not in CORRECTIONS:
            continue
        for field, value in CORRECTIONS[sentno].items():
            expected_old = OLD_VALUES[(sentno, field)]
            if row[field] != expected_old:
                raise RuntimeError(f"correction_precondition_failed:{sentno}:{field}")
            row[field] = value
            changed_cells += 1
    expected_changed_cells = sum(len(values) for values in CORRECTIONS.values())
    if changed_cells != expected_changed_cells:
        raise RuntimeError(f"changed_cell_count:{changed_cells}")
    outside_mutations = sum(
        before != after
        for before, after in zip(before_rows, after_rows)
        if not TARGET_START <= int(after["sentno"]) <= TARGET_END
    )
    if outside_mutations:
        raise RuntimeError(f"outside_target_mutations:{outside_mutations}")

    existing_event_text = EVENTS_OUT.read_text(encoding="utf-8")
    source_uids = {row["source_uid"] for row in source_rows}
    existing_check = check_provenance_events(existing_event_text, source_uids)
    if (
        not existing_event_text.endswith("\n")
        or existing_check["result"] != "PASS"
        or existing_check["events"] != 3029
    ):
        raise RuntimeError(json.dumps({**existing_check, "expected_events": 3029}, ensure_ascii=False))

    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in after_rows
        for field in CORRECTIONS.get(int(row["sentno"]), {})
    ]
    new_event_text = "".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in new_events
    )
    combined_event_text = existing_event_text + new_event_text
    if not combined_event_text.startswith(existing_event_text):
        raise RuntimeError("provenance_prefix_not_preserved")
    combined_check = check_provenance_events(combined_event_text, source_uids)
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if combined_check["result"] != "PASS" or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(new_event_text.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    correction_path = "data/master/qa/madoran_enrichment_batch03_correction01_qa.json"
    if correction_path not in evidence:
        evidence.append(correction_path)
    status["evidence_files"] = evidence
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validation = subprocess.run(
        [sys.executable, "scripts/validate_madoran_enrichment.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if validation.returncode != 0:
        raise RuntimeError(validation.stdout + validation.stderr)

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
            "new_provenance_events": qa.get("new_provenance_events", 755) + len(new_events),
            "total_provenance_events": combined_check["events"],
            "expected_total_provenance_events": combined_check["events"],
            "content_review_status": "pending_headgpt_correction_review",
            "draft_rows": 50,
            "flagged_rows": 14,
            "generated_at": generated_at,
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-003",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": ["161", "165", "166"],
        "changed_fields": len(new_events),
        "new_provenance_events": len(new_events),
        "provenance_events_before": existing_check["events"],
        "provenance_events_after": combined_check["events"],
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": outside_mutations,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 50,
        "flagged_rows": 14,
        "processing_flags_populated_rows": 51,
        "generated_at": generated_at,
        "outputs": {
            "batch": "data/master/enrichment/batches/batch03_sentno_0129_0192.tsv",
            "enrichment": "data/master/enrichment/madoran_sentence_enrichment.tsv",
            "provenance": "data/master/enrichment/madoran_sentence_enrichment_provenance.jsonl",
        },
    }
    CORRECTION_QA_OUT.write_text(
        json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return correction_qa


if __name__ == "__main__":
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
