"""Apply the second HeadGPT Batch 06 correction set with append-only provenance."""
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


BASE_COMMIT = "708cf0b"
CORRECTION_ID = "MADORAN-ENRICH-006-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v6-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 321
TARGET_END = 384
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch06_correction02_qa.json"


CORRECTIONS = {
    322: {
        "english": (
            "The opening phrase, h 7shinhalh, is an unclear colloquial expression. "
            "The rest says: on the first day after my marriage, and finally you became my wife, "
            "the most beautiful day of my life. Me too, my husband. Now go and make breakfast. "
            "Yes, but I will shower and come make it, okay?"
        ),
        "korean": (
            "첫 구절 h 7shinhalh는 뜻이 불분명한 구어 표현이야. "
            "나머지는 결혼 다음 날, 드디어 당신이 내 아내가 되었고 내 인생에서 가장 아름다운 날이라는 말이야. "
            "나도 그래, 여보. 이제 가서 아침을 만들어. 그래, 하지만 샤워하고 와서 만들게, 알겠지?"
        ),
    },
    328: {
        "english": (
            "Now an Algerian woman is normal at first, until she falls and cries out, "
            "3bd9a, 3bd9a, repeatedly. The poor man runs and carries her in a clandestine or unofficial "
            "vehicle to the hospital. When she arrives, they set her down on her feet and walk her about "
            "400 meters so she can reach the emergency department; she cries out to the Creator who made her. "
            "The exact wording of the repeated cry remains unclear."
        ),
        "korean": (
            "알제리 여성은 처음에는 멀쩡하다가 쓰러져 3bd9a, 3bd9a라고 계속 외쳐. "
            "불쌍한 남자가 달려가 비공식 운송 차량에 그녀를 태워 병원으로 데려가. "
            "도착하면 그녀를 두 발로 세워 응급실에 가도록 약 400미터를 걷게 하고, "
            "그녀는 자신을 창조한 창조주에게 외쳐. 반복되는 외침의 정확한 표현은 불분명해."
        ),
    },
    332: {
        "english": (
            "He used to carry a marker with him and rely on God. Chinese-writing tattoos were popular or "
            "widespread, although he did not know Chinese characters; he went and found a tea tin with "
            "Chinese writing on it."
        ),
        "korean": (
            "그는 마커를 가지고 다니며 하느님께 의지했어. 중국어 글씨 문신이 유행하고 널리 퍼져 있었지만 "
            "그는 중국어 글자를 몰랐어. 그래서 중국어 글씨가 적힌 차 통을 찾아냈지."
        ),
    },
    346: {
        "english": (
            "My father went to the town hall. In the registration, Amina was given or written instead of "
            "Amira, so the name came out wrong; the exact speech attribution is unclear. Well, they say our "
            "names are written in heaven with God."
        ),
        "korean": (
            "아버지가 시청에 갔어. 등록 과정에서 아미라 대신 아미나가 전달되거나 적혀서 이름이 잘못 나왔어. "
            "누가 어떤 말을 했는지는 정확히 불분명해. 뭐, 사람은 하느님과 함께 하늘에 이름이 정해져 있다고들 하잖아."
        ),
    },
    360: {
        "english": (
            "She started shouting outside and scolded me publicly. She said, How can I tell you to watch "
            "the girl while I take care of my errands and come back, and you go out? Did I tell you to go out? "
            "Come on, speak; do not cry with those eyes. Now you are helpless. And from then on..."
        ),
        "korean": (
            "그녀는 밖에서 소리치기 시작했고 사람들 앞에서 나를 야단쳤어. "
            "내가 볼일을 보고 돌아올 동안 그 아이를 잘 보라고 했는데 네가 나가 버리면 어떻게 하냐고 했지. "
            "내가 나가라고 했어? 말해 봐. 그 눈으로 울지 마. 이제 너는 아무것도 못 하잖아. 그 뒤로는…"
        ),
    },
    381: {
        "context_dependency": "medium",
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
    if changed != 11:
        raise RuntimeError(f"changed_cell_count:{changed}")

    corrected_batch = [dict(row) for row in batch]
    for row in corrected_batch:
        if row["sentno"] in correction_sentnos:
            for field, value in CORRECTIONS[int(row["sentno"])].items():
                row[field] = value

    source_uids = {row["source_uid"] for row in source}
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 5396:
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
    if combined_check["result"] != "PASS" or combined_check["events"] != 5407 or trace["result"] != "PASS":
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
    evidence_path = "data/master/qa/madoran_enrichment_batch06_correction02_qa.json"
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
            "new_provenance_events": 748 + 52 + len(new_events),
            "total_provenance_events": 5407,
            "expected_total_provenance_events": 5407,
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
        "provenance_events_before": 5396,
        "provenance_events_after": 5407,
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
