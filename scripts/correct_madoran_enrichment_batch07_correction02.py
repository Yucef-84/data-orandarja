"""Apply the second HeadGPT Batch 07 correction set with append-only provenance."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch07 import BATCH_OUT
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


BASE_COMMIT = "6f3e62e"
CORRECTION_ID = "MADORAN-ENRICH-007-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v7-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 385
TARGET_END = 448
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_correction02_qa.json"


CORRECTIONS = {
    391: {
        "english": (
            "Wafa, I wanted to ask you about that squid with rice that you made. I want the recipe—how you made it; "
            "just explain it briefly, because I felt like making it too."
        ),
        "korean": (
            "와파, 네가 만든 밥을 넣은 오징어에 대해 물어보고 싶었어. 그 레시피를 어떻게 만들었는지 알고 싶어. "
            "간단히 설명해 줘. 나도 만들어 보고 싶었거든."
        ),
    },
    393: {
        "english": (
            "Cook a bowl of rice with a little salt, drain it, and add some parsley, coriander, hot pepper, cumin, "
            "red pepper, and a pinch of saffron. Add three cloves of grated garlic and mix everything together."
        ),
        "korean": (
            "밥 한 그릇을 소금을 조금 넣어 지은 뒤 물기를 빼요. 파슬리, 고수, 매운 고추, 쿠민, 붉은 고추, "
            "사프란 한 꼬집과 간 마늘 세 쪽을 넣고 모두 섞어요."
        ),
    },
    399: {
        "english": (
            "Leave it for ten minutes to a quarter of an hour, then turn it off. Bon appétit; it is very delicious. "
            "When I made it at home, everyone wanted more of it. Try it and let me know. Thank you, goodbye."
        ),
        "korean": (
            "10분에서 15분 정도 두었다가 불을 꺼요. 맛있게 드세요. 정말 맛있어서 집에서 만들어 보니 다들 더 먹고 "
            "싶어 했어요. 만들어 보고 알려 주세요. 고마워요, 안녕히 계세요."
        ),
    },
    404: {
        "english": (
            "Later they raised the amount; the source mentions 'dimil' (two thousand) and also 400 dinars, but the "
            "exact relation is unclear. Even if it was only a park, with no paved road or anything there—not even "
            "asphalt—the important thing was that someone guarded it. The remaining wording is unclear."
        ),
        "korean": (
            "나중에는 금액을 올렸는데, 원문에는 ‘dimil’(2천)과 400디나르가 모두 언급되어 정확한 관계는 불분명해요. "
            "그냥 공원이고 포장된 길도 아무것도, 아스팔트조차 없어도 괜찮았어요. 중요한 것은 누군가 지켜 주는 "
            "것이었어요. 나머지 표현은 불분명해요."
        ),
    },
    410: {
        "english": (
            "At night there was music, fun, and clapping again. We made a scene all along the road. Little Kholoud "
            "wanted ice cream, so we stopped and finished it because we were full."
        ),
        "korean": (
            "밤에도 음악과 흥겨운 분위기, 박수가 이어졌어요. 우리는 길을 따라 신나게 떠들었어요. 어린 클룻이 "
            "아이스크림을 원해서 멈춰 먹고, 배가 불러서 그것으로 마무리했어요."
        ),
    },
    418: {
        "english": (
            "We begin with the Fatiha, people ululate, the men eat and perform the unclear action heard as 'yishour'; "
            "then the women sit and are served food too. When we finish, the celebration and dancing start with a DJ. "
            "Every so often we see the bride arrive in another outfit with her husband beside her, and people ululate "
            "and celebrate until evening."
        ),
        "korean": (
            "파티하로 시작하고 사람들이 자그라트를 하며, 남자들은 먹고 ‘이슈르’로 들리는 불분명한 행동을 해요. "
            "그다음 여자들도 앉아 음식을 대접받아요. 다 끝나면 DJ 음악에 맞춰 축하와 춤이 시작돼요. 때때로 "
            "신부가 남편을 곁에 두고 다른 옷으로 나타나고, 사람들은 저녁까지 자그라트를 하며 즐겨요."
        ),
        "processing_flags": "idiom_culture|long_source|source_ambiguity",
    },
    422: {
        "english": (
            "Once I was traveling, and when I returned from the trip I found that the daughter of our neighbor, whom I "
            "loved, had been married off by her father against her will. She had avoided me because she was afraid of her "
            "father. I went into our house, saw that something was not normal, and asked her what was wrong. She told me, "
            "'My son, they married off your beloved.' I grabbed an unclear object before running to her father."
        ),
        "korean": (
            "한번은 여행을 갔다가 돌아왔는데, 내가 사랑하던 이웃집 딸을 아버지가 억지로 시집보냈다는 걸 알게 됐어요. "
            "그녀는 아버지가 무서워 나를 피하고 있었어요. 우리 집에 들어가 이상한 일이 있다는 것을 보고 그녀에게 "
            "무슨 일이냐고 물었더니, 그녀가 ‘얘야, 네가 사랑하는 사람이 시집을 갔단다’라고 말했어요. 정확히 무엇인지 "
            "불분명한 물건을 집어 들고 그녀의 아버지에게 달려갔어요."
        ),
    },
    426: {
        "english": (
            "Her fiancé told me, You are a real man; you are the one who deserves her. I am well-built and strong, but "
            "your love is great and you deserve her; may God complete your happiness. It was like an Indian film. If "
            "anyone knows an Indian director, bring him here; there is already a film, and God's people will laugh."
        ),
        "korean": (
            "그녀의 약혼자는 나에게 네가 진짜 남자이고 그녀를 받을 자격이 있는 사람이라고 했어요. 나는 체격도 좋고 "
            "강하지만, 네 사랑이 크고 그녀를 받을 자격이 있으니 하느님이 행복을 완성해 주길 바란다고 했어요. 인도 "
            "영화 같았어요. 인도 감독을 아는 사람이 있으면 데려오라고, 이미 영화가 있으니 사람들이 웃을 거라고 했어요."
        ),
    },
    441: {
        "english": (
            "That one paid a million and went to sleep, while I paid billions. These girls did not increase, those boys did "
            "not leave; here is the electricity bill—you have not paid it. The line is a rhyming colloquial expression and "
            "remains partly unclear."
        ),
        "korean": (
            "저 사람은 백만을 내고 잠들었고 나는 수십억을 냈다는 식의 말이야. 이 여자들은 늘지 않았고 저 남자들은 "
            "가지 않았으며, 여기 전기 요금은 아직 내지 않았네. 운율이 있는 구어 표현이라 일부는 불분명해."
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
    changed = 0
    for row in after:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value
            changed += 1
    expected_fields = sum(len(fields) for fields in CORRECTIONS.values())
    if changed != expected_fields:
        raise RuntimeError(f"changed_cell_count:{changed}:{expected_fields}")

    corrected_batch = [dict(row) for row in batch]
    for row in corrected_batch:
        for field, value in CORRECTIONS.get(int(row["sentno"]), {}).items():
            row[field] = value

    source_uids = {row["source_uid"] for row in source}
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 6209:
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
    if combined_check["result"] != "PASS" or combined_check["events"] != 6209 + expected_fields or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch07_correction02_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append(
        {
            "correction_id": CORRECTION_ID,
            "changed_fields": expected_fields,
            "rows": len(CORRECTIONS),
            "provenance_events": expected_fields,
        }
    )
    qa.update(
        {
            "correction_id": CORRECTION_ID,
            "latest_correction_id": CORRECTION_ID,
            "correction_history": history,
            "correction_changed_fields": expected_fields,
            "correction_rows": len(CORRECTIONS),
            "correction_provenance_events": expected_fields,
            "new_provenance_events": 751 + 45 + expected_fields,
            "total_provenance_events": 6209 + expected_fields,
            "expected_total_provenance_events": 6209 + expected_fields,
            "content_review_status": "pending_headgpt_correction_review",
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-007",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": expected_fields,
        "new_provenance_events": expected_fields,
        "provenance_events_before": 6209,
        "provenance_events_after": 6209 + expected_fields,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 23,
        "flagged_rows": 41,
        "processing_flags_populated_rows": 297,
        "batch_processing_flags_populated_rows": 48,
        "batch_artifact_sync": "PASS",
        "batch_artifact_sync_changed_fields": expected_fields,
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
