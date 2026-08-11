"""Apply HeadGPT Batch 05 P1 corrections with append-only provenance."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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


BASE_COMMIT = "62aa4c8"
CORRECTION_ID = "MADORAN-ENRICH-005-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v5-correction-1"
METHOD = "llm_source_only_enrichment_correction"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 257
TARGET_END = 320
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_qa.json"
CORRECTION_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch05_correction01_qa.json"

CORRECTIONS = {
    273: {
        "english": "Never mind—there is jealousy and a great deal of something unclear. But some people play the role of critics, such as someone called Slim Agha. I swear I do not think he wrote this electronic-press material, because he writes on those Nahar websites. So Algerians do not know Slim Agha; several links are unclear.",
        "korean": "괜찮아. 질투와 관련된 불분명한 말이 있어. 하지만 어떤 사람들은 비평가인 척하는데, 예를 들면 살림 아가라는 사람이 그래. 맹세코 나는 그가 이 전자 언론 자료를 썼다고는 생각하지 않아. 그는 나하르의 그런 웹사이트에 글을 쓰기 때문이야. 그래서 알제리 사람들은 살림 아가를 모른다는 말인데, 연결 관계가 불분명해.",
    },
    294: {
        "english": "The source is the single word '7allab.' It may literally mean 'milkman,' but in Algerian slang it can refer to a man who fawns over or tries to ingratiate himself with women. The context is insufficient to choose between these readings.",
        "korean": "원문은 '7allab'이라는 한 단어야. 문자 그대로는 '우유 배달원'일 수 있지만, 알제리 슬랭에서는 여성에게 과하게 매달리거나 환심을 사려는 남자를 가리킬 수 있어. 문맥만으로는 두 해석 중 하나를 확정할 수 없어.",
        "domain": "other",
        "topic": "ambiguous_slang_lexeme",
        "register": "slang",
        "context_dependency": "high",
        "processing_flags": "context_heavy|source_ambiguity",
        "enrichment_state": "flagged",
    },
    303: {
        "latin": "choula kont nehder m3a sa7bi.",
        "english": "What? I was talking with my friend.",
        "korean": "뭐? 친구와 이야기하고 있었어.",
        "topic": "asking_for_clarification",
        "speech_act": "question",
        "context_dependency": "medium",
        "processing_flags": "source_ambiguity",
        "enrichment_state": "flagged",
    },
    309: {
        "english": "Mysterious, manly, and he does not fawn over women. I found the man of my life. The slang expression is context-sensitive.",
        "korean": "신비롭고 남자답고 여자에게 과하게 매달리거나 환심을 사려 하지 않아. 내 인생의 남자를 찾았어. 이 슬랭 표현은 문맥에 따라 달라질 수 있어.",
    },
    315: {
        "latin": "rani baghi netzewwej. la 7ambouk la. bsa7 3lah. sa7a nezewjek bent khaltk. ma netzewjehash. bent khalti tetchebeh l Jilali choufili wa7da tkoun chaba.",
        "english": "I want to get married. No, please, no. But why? Fine, I will arrange for you to marry your cousin. I will not marry her; my cousin resembles Jilali. Find me a young woman.",
        "korean": "나 결혼하고 싶어. 안 돼, 제발 안 돼. 하지만 왜? 좋아, 네 사촌과 결혼하도록 해 줄게. 그 여자와는 결혼하지 않을 거야. 내 사촌은 질랄리와 닮았어. 젊은 여자를 찾아 줘.",
        "processing_flags": "idiom_culture|source_ambiguity",
    },
}

OLD_VALUES = {
    (273, "english"): "Never mind—there is jealousy and a great deal of something unclear. But some people play the role of critics, such as someone called Slim Agha. I swear I do not think he wrote this electronic-press material, because he writes on those Nahar websites. So Slim Agha is an Algerian person whom he does not know; several links are unclear.",
    (273, "korean"): "괜찮아. 질투와 관련된 불분명한 말이 있어. 하지만 어떤 사람들은 비평가인 척하는데, 예를 들면 살림 아가라는 사람이 그래. 맹세코 나는 그가 이 전자 언론 자료를 썼다고는 생각하지 않아. 그는 나하르의 그런 웹사이트에 글을 쓰기 때문이야. 그래서 살림 아가는 그가 모르는 알제리 사람이라는 말인데, 연결 관계가 불분명해.",
    (294, "english"): "A milkman.",
    (294, "korean"): "우유 배달원.",
    (294, "domain"): "work",
    (294, "topic"): "occupation_word",
    (294, "register"): "colloquial",
    (294, "context_dependency"): "medium",
    (294, "processing_flags"): "",
    (294, "enrichment_state"): "draft",
    (303, "latin"): "chouia kont nehder m3a sa7bi.",
    (303, "english"): "Nothing; I was talking with my friend.",
    (303, "korean"): "아무것도 아니야. 친구와 이야기하고 있었어.",
    (303, "topic"): "explaining_a_pause",
    (303, "speech_act"): "answer",
    (303, "context_dependency"): "low",
    (303, "processing_flags"): "",
    (303, "enrichment_state"): "draft",
    (309, "english"): "Mysterious, manly, and he does not drink milk. I found the man of my life. The first descriptors are unclear in the source.",
    (309, "korean"): "신비롭고 남자답고 우유를 마시지 않아. 내 인생의 남자를 찾았어. 앞의 묘사 표현은 원문에서 불분명해.",
    (315, "latin"): "rani baghi netzewwej. la 7mouk la. bsa7 3lah. sa7a nezewjek bent khaltk. ma netzewjehash. bent khalti tetchebeh l Jilali choufili wa7da tkoun chaba.",
    (315, "english"): "I want to get married. No, your uncle does not agree. But why? Fine, I will marry you to your aunt's daughter. I will not marry her; my cousin resembles Jilali. Find me someone who is young and attractive.",
    (315, "korean"): "나 결혼하고 싶어. 안 돼, 네 삼촌이 동의하지 않아. 하지만 왜? 좋아, 네 이모 딸과 결혼시켜 줄게. 그 여자와는 결혼하지 않을 거야. 내 사촌은 질랄리와 닮았어. 젊고 예쁜 사람을 찾아 줘.",
    (315, "processing_flags"): "code_switching|source_ambiguity",
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
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def apply() -> dict[str, object]:
    if not current_commit().startswith(BASE_COMMIT):
        raise RuntimeError(f"base_commit_mismatch:{current_commit()}:{BASE_COMMIT}")
    if source_gate()["result"] != "PASS":
        raise RuntimeError("source_gate_failed")
    source_rows = read_tsv(SOURCE_OUT)
    before_rows = read_tsv(ENRICHMENT_OUT)
    if list(before_rows[0]) != ENRICHMENT_FIELDS:
        raise RuntimeError("enrichment_header_mismatch")
    source_links = [(row["source_uid"], row["sentno"]) for row in source_rows]
    if source_links != [(row["source_uid"], row["sentno"]) for row in before_rows]:
        raise RuntimeError("source_linkage_mismatch")
    after_rows = [dict(row) for row in before_rows]
    changed_cells = 0
    for row in after_rows:
        sentno = int(row["sentno"])
        for field, value in CORRECTIONS.get(sentno, {}).items():
            if row[field] != OLD_VALUES[(sentno, field)]:
                raise RuntimeError(f"correction_precondition_failed:{sentno}:{field}")
            row[field] = value
            changed_cells += 1
    if changed_cells != 24:
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
    if not existing_event_text.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 4572:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in after_rows
        for field in CORRECTIONS.get(int(row["sentno"]), {})
    ]
    new_event_text = "".join(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n" for value in new_events)
    combined_event_text = existing_event_text + new_event_text
    combined_check = check_provenance_events(combined_event_text, source_uids)
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if combined_check["result"] != "PASS" or combined_check["events"] != 4596 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(new_event_text.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"].update({
        "enrichment_completed_rows": 199,
        "enrichment_draft_rows": 34,
        "enrichment_flagged_rows": 87,
        "enrichment_not_started_rows": 1036,
        "processing_flags_populated_rows": 205,
    })
    evidence = list(status.get("evidence_files", []))
    correction_path = "data/master/qa/madoran_enrichment_batch05_correction01_qa.json"
    if correction_path not in evidence:
        evidence.append(correction_path)
    status["evidence_files"] = evidence
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validation = subprocess.run([sys.executable, "scripts/validate_madoran_enrichment.py"], cwd=ROOT, check=False, capture_output=True, text=True)
    if validation.returncode != 0:
        raise RuntimeError(validation.stdout + validation.stderr)
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": len(new_events), "rows": len(CORRECTIONS), "provenance_events": len(new_events)})
    qa.update({
        "correction_id": CORRECTION_ID,
        "latest_correction_id": CORRECTION_ID,
        "correction_history": history,
        "correction_changed_fields": len(new_events),
        "correction_rows": len(CORRECTIONS),
        "correction_provenance_events": len(new_events),
        "new_provenance_events": 753 + len(new_events),
        "total_provenance_events": combined_check["events"],
        "expected_total_provenance_events": combined_check["events"],
        "processing_flags_populated_rows": 205,
        "batch_processing_flags_populated_rows": 51,
        "content_review_status": "pending_headgpt_correction_review",
        "draft_rows": 34,
        "flagged_rows": 30,
        "generated_at": generated_at,
        "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-005",
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
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
        "draft_rows": 34,
        "flagged_rows": 30,
        "processing_flags_populated_rows": 51,
        "generated_at": generated_at,
        "outputs": {
            "batch": "data/master/enrichment/batches/batch05_sentno_0257_0320.tsv",
            "enrichment": "data/master/enrichment/madoran_sentence_enrichment.tsv",
            "provenance": "data/master/enrichment/madoran_sentence_enrichment_provenance.jsonl",
        },
    }
    CORRECTION_QA_OUT.write_text(json.dumps(correction_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return correction_qa


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
