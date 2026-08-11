"""Apply the second HeadGPT content correction set for MADOran Batch 09."""
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


BASE_COMMIT = "8dc3cf3"
CORRECTION_ID = "MADORAN-ENRICH-009-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v9-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_correction02_qa.json"


CORRECTIONS = {
    527: {
        "english": (
            "Sorry, sister. What do you need or want, please? What will you drink—water? Please, I will bring you "
            "[an unclear item or phrase], and the menu too. Some words are unclear in the recording."
        ),
        "korean": (
            "미안해요, 언니. 무엇이 필요해요, 무엇을 원해요? 무엇을 마실래요—물? [불분명한 물건이나 표현]과 "
            "메뉴도 가져다줄게요. 녹음에서 몇몇 단어는 불분명해요."
        ),
    },
    532: {
        "english": (
            "Top up my Flexy, please! Unfortunately, the next phrase sounds like French 'en même temps' ('at the "
            "same time'), and the surrounding wording is unclear. Do not embarrass me by flirting with my friend in "
            "front of me, you whore; I will not let this pass. Go away and leave me alone, please ('حمبوك'). Several "
            "slang phrases are unclear."
        ),
        "korean": (
            "플렉시를 충전해 줘요! 안타깝게도 다음 표현은 프랑스어 ‘en même temps’(동시에)처럼 들리고 주변 표현은 "
            "불분명해요. 내 앞에서 내 친구에게 추근대며 나를 망신시키지 마, 이 창녀야. 그냥 넘기지 않을 테니 멀리 "
            "가서 나를 내버려 둬요, 제발(‘حمبوك’). 몇몇 속어 표현은 불분명해요."
        ),
    },
    562: {
        "domain": "entertainment_music",
        "topic": "rai_reference_and_lyric_like_address",
        "genre": "other",
        "speech_act": "other",
    },
    564: {
        "english": (
            "I have a very long list. First, chorba and harira are obvious. I do not like stews in general, but I love "
            "olive dishes. I do not like pea tagine very much, and I do not like chickpea dishes either. Couscous is "
            "obvious, with sauce or plain seffa; that is all."
        ),
        "korean": (
            "목록이 아주 길어요. 먼저 초르바와 하리라는 당연해요. 스튜는 전반적으로 좋아하지 않지만 올리브 요리는 "
            "정말 좋아해요. 완두콩 타진은 별로 좋아하지 않고 병아리콩 요리도 좋아하지 않아요. 쿠스쿠스는 당연하고, "
            "소스를 곁들이거나 그냥 세파로 먹어요. 이게 다예요."
        ),
    },
    566: {
        "english": (
            "I know how to cook all kinds of stews, but I do not know how to cook couscous well; in fact, I tried making "
            "it once, and it was very good. Everyone who tastes my harira or chorba loves it. I can say I know how to "
            "make harira and chorba. Perhaps they want to marry me; I only need a groom, but let us not discuss that topic."
        ),
        "korean": (
            "나는 여러 종류의 스튜를 만들 줄 알지만 쿠스쿠스를 잘 만들 줄은 몰라요. 사실 한 번 만들어 봤는데 아주 "
            "맛있었어요. 내 하리라나 초르바를 맛본 사람은 모두 좋아해요. 하리라와 초르바는 만들 줄 안다고 말할 수 "
            "있어요. 아마 사람들이 나를 결혼시키고 싶어 하나 봐요. 신랑만 있으면 되지만 그 주제는 말하지 말아요."
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
    if changed_fields != expected_events or expected_events != 12:
        raise RuntimeError(f"correction_shape:{changed_fields}:{expected_events}")

    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 7806:
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
        or combined_check["events"] != 7806 + expected_events
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
    evidence_path = "data/master/qa/madoran_enrichment_batch09_correction02_qa.json"
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
            "total_provenance_events": 7806 + expected_events,
            "expected_total_provenance_events": 7806 + expected_events,
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
        "provenance_events_before": 7806,
        "provenance_events_after": 7806 + expected_events,
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
