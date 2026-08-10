"""Apply the remaining HeadGPT source-fidelity corrections for Batch 02."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from scripts.build_madoran_enrichment_batch02 import BATCH_OUT
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


BASE_COMMIT = "27b41d9"
CORRECTION_ID = "MADORAN-ENRICH-002-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v2-correction-2"
METHOD = "llm_source_only_enrichment_correction"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 65
TARGET_END = 128
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch02_correction02_qa.json"

CHANGED_FIELDS = {
    66: ("latin",),
    67: ("latin", "english", "korean"),
    68: ("latin",),
    69: ("english", "korean"),
    73: ("english", "korean", "topic"),
    74: ("latin",),
    75: ("english", "korean", "processing_flags"),
    78: ("latin",),
    83: ("english", "korean", "topic"),
    84: ("english", "korean", "topic"),
    85: ("english", "korean", "topic"),
    88: ("english", "korean", "processing_flags"),
    89: ("english", "korean", "topic"),
    91: ("english", "korean"),
    95: ("latin", "english", "korean"),
    97: ("english", "korean"),
    98: ("english", "korean"),
    99: ("english", "korean"),
    100: ("latin", "english", "korean"),
    108: ("processing_flags",),
    109: ("latin", "english", "korean", "processing_flags"),
    110: ("english", "korean"),
    114: ("latin", "english", "korean"),
    117: ("latin",),
    121: ("latin", "english", "korean", "processing_flags"),
    122: ("english", "korean"),
    123: ("english", "korean"),
    124: ("genre",),
    125: ("latin",),
    127: ("english", "korean"),
}

OLD_MARKERS = {
    (66, "latin"): "ljandar m",
    (67, "latin"): "lmili tar",
    (67, "english"): "did the same thing",
    (67, "korean"): "똑같이",
    (68, "latin"): "wsln a",
    (69, "english"): "applauding",
    (69, "korean"): "박수를",
    (73, "english"): "breakfast",
    (73, "korean"): "아침",
    (73, "topic"): "breakfast",
    (74, "latin"): "j oghma",
    (75, "english"): "Dublin",
    (75, "korean"): "더블린",
    (75, "processing_flags"): "context_heavy",
    (78, "latin"): "galek wahed nhar",
    (83, "english"): "similar name",
    (83, "korean"): "비슷한 이름",
    (83, "topic"): "name_wordplay",
    (84, "english"): "this man",
    (84, "korean"): "이 사람이",
    (84, "topic"): "name_wordplay",
    (85, "english"): "visitor wondered",
    (85, "korean"): "궁금해했어",
    (85, "topic"): "name_wordplay",
    (88, "english"): "I never said that.",
    (88, "korean"): "그런 말 한 적이 없는데요",
    (88, "processing_flags"): "",
    (89, "english"): "drunk man",
    (89, "korean"): "술에 취한",
    (89, "topic"): "drunkenness",
    (91, "english"): "while he found a solution",
    (91, "korean"): "방법을 찾을 때까지",
    (95, "latin"): "weld 3abbas rayes ta3 7izb",
    (95, "english"): "confused political exchange",
    (95, "korean"): "혼란스러운 정치 대화",
    (97, "english"): "slippers",
    (97, "korean"): "슬리퍼",
    (98, "english"): "slippers",
    (98, "korean"): "슬리퍼",
    (99, "english"): "Because he loved dominoes",
    (99, "korean"): "도미노를 너무 좋아해서",
    (100, "latin"): "baboucha",
    (100, "english"): "slipper",
    (100, "korean"): "슬리퍼",
    (108, "processing_flags"): "",
    (109, "latin"): "ma9t ena",
    (109, "english"): "sweets",
    (109, "korean"): "과자",
    (109, "processing_flags"): "",
    (110, "english"): "for the celebration",
    (110, "korean"): "잔치에 돈",
    (114, "latin"): "Baki",
    (114, "english"): "Baki the tired one",
    (114, "korean"): "지친 바키야",
    (117, "latin"): "li bagha ga3",
    (121, "latin"): "b condition",
    (121, "english"): "if you prove",
    (121, "korean"): "증명한다면",
    (121, "processing_flags"): "context_heavy",
    (122, "english"): "handsome Algerian man",
    (122, "korean"): "잘생긴 알제리 남자",
    (123, "english"): "Sana's sister",
    (123, "korean"): "사나의 자매",
    (124, "genre"): "song_lyric",
    (125, "latin"): "dourou ya chbiba",
    (127, "english"): "we have a sheikh",
    (127, "korean"): "결국 우리에게는 어른이 있어",
}
ABSENT_MARKERS = {
    (78, "latin"): "@@SOURCE_CORRUPTION_1@@",
    (88, "english"): "jamais",
    (88, "korean"): "jamais",
    (95, "latin"): "@@SOURCE_CORRUPTION_1@@",
    (117, "latin"): "@@SOURCE_CORRUPTION_1@@",
    (125, "latin"): "@@SOURCE_CORRUPTION_1@@",
}
FLAGGED_STATE_ROWS = {75, 109, 121}


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


def assert_old_value(sentno: int, field: str, value: str) -> None:
    marker = OLD_MARKERS.get((sentno, field))
    if marker is None:
        raise RuntimeError(f"missing_old_marker:{sentno}:{field}")
    if marker and marker not in value:
        raise RuntimeError(f"correction_precondition_failed:{sentno}:{field}")
    if not marker and value:
        raise RuntimeError(f"correction_precondition_failed:{sentno}:{field}")
    absent = ABSENT_MARKERS.get((sentno, field))
    if absent and absent in value:
        raise RuntimeError(f"correction_already_applied:{sentno}:{field}")


def apply() -> dict[str, object]:
    gate = source_gate()
    if gate["result"] != "PASS":
        raise RuntimeError(json.dumps(gate, ensure_ascii=False))
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    if len(batch_rows) != TARGET_END - TARGET_START + 1:
        raise RuntimeError("batch02_row_count")
    batch_by_sentno = {int(row["sentno"]): row for row in batch_rows}
    if set(batch_by_sentno) != set(range(TARGET_START, TARGET_END + 1)):
        raise RuntimeError("batch02_sentno_coverage")
    if not set(CHANGED_FIELDS).issubset(batch_by_sentno):
        raise RuntimeError("correction_target_mismatch")
    source_keys = [(row["source_uid"], row["sentno"]) for row in source_rows]
    before_keys = [(row["source_uid"], row["sentno"]) for row in before_rows]
    if source_keys != before_keys:
        raise RuntimeError("source_linkage_changed")

    after_rows = [dict(row) for row in before_rows]
    changed_cells = 0
    for row in after_rows:
        sentno = int(row["sentno"])
        if sentno not in CHANGED_FIELDS:
            continue
        if sentno in FLAGGED_STATE_ROWS and row["enrichment_state"] != "draft":
            raise RuntimeError(f"state_precondition_failed:{sentno}")
        for field in CHANGED_FIELDS[sentno]:
            assert_old_value(sentno, field, row[field])
            row[field] = batch_by_sentno[sentno][field]
            changed_cells += 1
        if sentno in FLAGGED_STATE_ROWS:
            row["enrichment_state"] = "flagged"
    if changed_cells != 67:
        raise RuntimeError(f"changed_cell_count:{changed_cells}")
    outside_mutations = sum(
        before != after
        for before, after in zip(before_rows, after_rows)
        if not TARGET_START <= int(after["sentno"]) <= TARGET_END
    )
    if outside_mutations:
        raise RuntimeError(f"outside_target_mutations:{outside_mutations}")

    existing_event_text = EVENTS_OUT.read_text(encoding="utf-8")
    if not existing_event_text.endswith("\n"):
        raise RuntimeError("existing_provenance_log_missing_final_newline")
    source_uids = {row["source_uid"] for row in source_rows}
    existing_check = check_provenance_events(existing_event_text, source_uids)
    if existing_check["result"] != "PASS" or existing_check["events"] != 2189:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in after_rows
        for field in CHANGED_FIELDS.get(int(row["sentno"]), ())
    ]
    combined_event_text = existing_event_text + "".join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
        for item in new_events
    )
    combined_check = check_provenance_events(combined_event_text, source_uids)
    if combined_check["result"] != "PASS":
        raise RuntimeError(json.dumps(combined_check, ensure_ascii=False))
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if trace["result"] != "PASS":
        raise RuntimeError(json.dumps(trace, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(
            "".join(
                json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
                for item in new_events
            ).encode("utf-8")
        )

    counts = {
        "enrichment_completed_rows": sum(row["enrichment_state"] in {"qa_passed", "reviewed"} for row in after_rows),
        "enrichment_draft_rows": sum(row["enrichment_state"] == "draft" for row in after_rows),
        "enrichment_flagged_rows": sum(row["enrichment_state"] == "flagged" for row in after_rows),
        "enrichment_not_started_rows": sum(row["enrichment_state"] == "not_started" for row in after_rows),
        "processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in after_rows),
    }
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"] = counts
    evidence = list(status.get("evidence_files", []))
    correction_path = "data/master/qa/madoran_enrichment_batch02_correction02_qa.json"
    if correction_path not in evidence:
        evidence.append(correction_path)
    status["evidence_files"] = evidence
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    batch_target = [row for row in batch_rows if TARGET_START <= int(row["sentno"]) <= TARGET_END]
    batch_draft = sum(
        not any(flag in row["processing_flags"].split("|") for flag in ("source_ambiguity", "source_corruption"))
        for row in batch_target
    )
    batch_flagged = len(batch_target) - batch_draft
    batch_flags = sum(bool(row["processing_flags"]) for row in batch_target)
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    if not history and qa.get("correction_id"):
        history.append(
            {
                "correction_id": qa["correction_id"],
                "changed_fields": qa.get("correction_changed_fields", 0),
                "rows": qa.get("correction_rows", 0),
                "provenance_events": qa.get("correction_provenance_events", 0),
            }
        )
    history.append(
        {
            "correction_id": CORRECTION_ID,
            "changed_fields": changed_cells,
            "rows": len(CHANGED_FIELDS),
            "provenance_events": len(new_events),
        }
    )
    qa.update(
        {
            "correction_id": CORRECTION_ID,
            "latest_correction_id": CORRECTION_ID,
            "correction_history": history,
            "correction_changed_fields": changed_cells,
            "correction_rows": len(CHANGED_FIELDS),
            "correction_provenance_events": len(new_events),
            "draft_rows": batch_draft,
            "flagged_rows": batch_flagged,
            "processing_flags_populated_rows": batch_flags,
            "new_provenance_events": qa.get("new_provenance_events", 740) + len(new_events),
            "total_provenance_events": existing_check["events"] + len(new_events),
            "generated_at": generated_at,
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-002",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(number) for number in sorted(CHANGED_FIELDS)],
        "changed_fields": changed_cells,
        "new_provenance_events": len(new_events),
        "provenance_events_before": existing_check["events"],
        "provenance_events_after": existing_check["events"] + len(new_events),
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": outside_mutations,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": len(batch_target),
        "draft_rows": batch_draft,
        "flagged_rows": batch_flagged,
        "processing_flags_populated_rows": batch_flags,
        "generated_at": generated_at,
        "outputs": {
            "batch": "data/master/enrichment/batches/batch02_sentno_0065_0128.tsv",
            "enrichment": "data/master/enrichment/madoran_sentence_enrichment.tsv",
            "provenance": "data/master/enrichment/madoran_sentence_enrichment_provenance.jsonl",
        },
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
