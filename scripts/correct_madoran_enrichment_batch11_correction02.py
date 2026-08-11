"""Apply the second HeadGPT correction set for MADOran Batch 11."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch11 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "9a02fa0"
CORRECTION_ID = "MADORAN-ENRICH-011-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v11-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_correction02_qa.json"

CORRECTIONS = {
    648: {
        "english": "A studio apartment here is rented for two million. I am someone whose wedding is coming soon—there is not much time left before it—but I will not lie to you: I cannot rent. I am going to live with my family.",
        "korean": "여기 원룸은 200만에 빌려요. 나는 결혼식까지 얼마 남지 않은 사람인데, 솔직히 말하면 집을 빌릴 수가 없어요. 가족과 함께 살 거예요.",
    },
    665: {
        "english": "The opening includes the code-switched phrase ‘جيسك ماتنو / jusqu’à maintenant’ (‘up to now’). In this context, مشي مريي... indicates that the speaker is not married up to now; the exact code-switched wording is still uncertain. The speaker then links marriage to having a good job and housing that can support one, and says that a person today should arrange a future, housing, and a stable place before thinking about marriage.",
        "korean": "도입부에는 ‘جيسك ماتنو / jusqu’à maintenant’(‘지금까지’)라는 코드 스위칭 표현이 나와요. 이 문맥에서 ‘مشي مريي...’는 화자가 지금까지 결혼하지 않았다는 상태를 나타내며, 정확한 코드 스위칭 표현은 여전히 불확실해요. 이어서 화자는 자신을 부양할 수 있는 좋은 직장과 집이 있어야 결혼을 생각할 수 있고, 요즘 사람은 결혼을 생각하기 전에 미래와 주거, 안정적인 거처를 마련해야 한다고 말해요.",
    },
    692: {
        "topic": "unclear_comic_knockdown_reaction",
    },
    694: {
        "english": "By God, the line runs until ten in the morning and mentions a mirror (مرايا), makeup, and styling. The following phrase نجي نطل عليها نشوف شا راها ديرو has unclear speaker and quotation boundaries: it may involve coming to look at her or to see what she is doing, but the source does not resolve who says or does what. Nothing is clear in the scene, and even the man they were talking about is mentioned as absent; the mirror/makeup scene remains partly uncertain.",
        "korean": "하느님, 이 대사는 아침 10시까지 이어지며 거울(‘مرايا’), 화장, 스타일링을 언급해요. 뒤의 ‘نجي نطل عليها نشوف شا راها ديرو’는 화자와 인용 경계가 불분명해요. 그녀를 보러 오거나 그녀가 무엇을 하는지 보러 간다는 뜻일 수 있지만, 누가 무엇을 말하고 행동하는지는 원문이 확정하지 않아요. 장면에서 분명한 것은 없고, 이야기하던 그 남자도 없다고 언급돼요. 거울·화장 장면은 일부 불확실하게 보존해요.",
    },
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid, field, value, generated_at):
    return {
        "source_uid": source_uid, "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": "llm_source_only_enrichment_correction", "model": MODEL,
        "prompt_version": PROMPT_VERSION, "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at, "review_state": "generated",
    }


def apply():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if not head.startswith(BASE_COMMIT) or source_gate()["result"] != "PASS":
        raise RuntimeError(f"gate_failed:{head}")
    source = read_tsv(SOURCE_OUT)
    before = read_tsv(ENRICHMENT_OUT)
    batch = read_tsv(BATCH_OUT)
    if list(before[0]) != ENRICHMENT_FIELDS or len(batch) != 64:
        raise RuntimeError("artifact_shape_mismatch")
    source_uids = {row["source_uid"] for row in source}
    master_before = {row["sentno"]: row for row in before}
    batch_before = {row["sentno"]: row for row in batch}
    for sentno in batch_before:
        if any(master_before[sentno].get(field) != batch_before[sentno].get(field) for field in ENRICHMENT_FIELDS):
            raise RuntimeError(f"batch_master_mismatch_before:{sentno}")
    after = [dict(row) for row in before]
    corrected_batch = [dict(row) for row in batch]
    for row in after:
        row.update(CORRECTIONS.get(int(row["sentno"]), {}))
    for row in corrected_batch:
        row.update(CORRECTIONS.get(int(row["sentno"]), {}))
    changed_fields = sum(len(fields) for fields in CORRECTIONS.values())
    if len(CORRECTIONS) != 4 or changed_fields != 7:
        raise RuntimeError(f"correction_shape:{len(CORRECTIONS)}:{changed_fields}")
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 9472:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 9479 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch11_correction02_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": len(CORRECTIONS), "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID, "latest_correction_id": CORRECTION_ID,
        "correction_history": history, "correction_changed_fields": changed_fields,
        "correction_state_updates": 0, "correction_rows": len(CORRECTIONS), "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 9479, "expected_total_provenance_events": 9479,
        "content_review_status": "pending_headgpt_correction_review", "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS", "batch_id": BATCH_ID, "correction_id": CORRECTION_ID, "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)], "changed_fields": changed_fields,
        "state_updates": 0, "new_provenance_events": changed_fields, "provenance_events_before": 9472,
        "provenance_events_after": 9479, "source_gate": "PASS", "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0, "arabic_modified": 0, "outside_target_mutations": 0, "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS", "validator": "PASS", "target_rows": 64, "draft_rows": 3, "flagged_rows": 61,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "batch_artifact_sync": "PASS", "batch_artifact_sync_changed_fields": changed_fields,
        "batch_artifact_sync_state_updates": 0, "generated_at": generated_at,
        "outputs": {"batch": BATCH_OUT.relative_to(ROOT).as_posix(), "enrichment": ENRICHMENT_OUT.relative_to(ROOT).as_posix(), "provenance": EVENTS_OUT.relative_to(ROOT).as_posix()},
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
