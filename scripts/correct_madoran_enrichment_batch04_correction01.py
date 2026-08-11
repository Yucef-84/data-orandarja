"""Apply HeadGPT Batch 04 content corrections with append-only provenance."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch04 import BATCH_OUT
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


BASE_COMMIT = "5bbb577"
CORRECTION_ID = "MADORAN-ENRICH-004-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v4-correction-1"
METHOD = "llm_source_only_enrichment_correction"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 193
TARGET_END = 256
STATUS_OUT = ROOT / "data" / "master" / "state" / "madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch04_qa.json"
CORRECTION_QA_OUT = (
    ROOT / "data" / "master" / "qa" / "madoran_enrichment_batch04_correction01_qa.json"
)

CORRECTIONS = {
    206: {
        "latin": "la la manich baghi hakda. rani baghi zin w 3win. oui w 7aya wa9fa w choufou doun lou foun @@Lat@@dans @@Lat@@le @@Lat@@thent. 7aya fort. baghi re9ba ki ternich safya w wej mriya la9i la9i ha rbi la9i nar achwa9i f bent 3ekrimi. ah matlou3a.",
    },
    209: {
        "english": "Listen, Hamid, you are exposing or embarrassing me in front of people early in the morning. Do not tell me that I will expose you or anything. I will drive you mad. By God, she or it is not 'farya.' The phrase 'b ras ma 3ziza' is unclear; she or it is not 'farya' at all, by the truth of God's Messenger.",
        "korean": "들어 봐, 하미드. 아침부터 사람들 앞에서 나를 폭로하거나 망신 주고 있잖아. 내가 너를 폭로하겠다는 식으로 말하지 마. 너를 미치게 할 거야. 맹세코 그 대상은 'farya'가 아니야. 'b ras ma 3ziza'라는 구절은 뜻이 불분명하고, 이어서 그 대상은 전혀 'farya'가 아니라고 하며 하나님의 사도를 두고 맹세해.",
    },
    211: {
        "english": "Am I 'trat9i'? That expression is unclear. Go and complain. The source then says, 'Do not take your money,' followed by, 'Are you leaving or not leaving now?'; the linkage between these clauses is unclear. By God, the phrase about it not being 'farya' is also unclear. All right; every meeting has another after it.",
        "korean": "내가 'trat9i'라고? 그 표현은 불분명해. 가서 신고해. 원문은 이어서 '네 돈을 가져가지 마'라고 한 뒤 '지금 갈 거야, 안 갈 거야?'라고 묻는데 두 절의 연결은 불분명해. 맹세코 'farya가 아니다'라는 부분도 뜻이 불분명해. 좋아, 만남 뒤에는 또 다른 만남이 있다는 말이야.",
    },
    212: {
        "english": "A woman would not obey her mother and came out upset. Her mother asked where she was going; she replied, 'Do not look for me.' The mother threatened to incite her male sibling against her so that he would beat her. The woman answered, 'Send him with them,' slammed the door, made up her mind, and left. Some wording is uncertain.",
        "korean": "한 여성이 어머니 말을 듣지 않고 화가 난 채 나왔어. 어머니가 어디 가느냐고 묻자 '나를 찾지 마'라고 했어. 어머니는 그 여성의 남자 형제가 오면 부추겨서 그녀를 때리게 하겠다고 위협했어. 그녀는 '그도 그들과 함께 보내'라고 답하고 문을 세게 닫은 뒤 마음먹고 나갔어. 일부 표현은 불분명해.",
    },
    213: {
        "korean": "저녁이 되자 남자 형제가 그녀를 기다리고 있었고 주먹으로 공격했어. 그 결과를 나타내는 'n8elha'의 뜻은 불분명해. 그날부터 그녀는 말을 듣고 행동을 바로잡으며 다시는 그러지 않겠다고 했어. 마지막 속담 같은 표현도 불분명해.",
    },
    225: {
        "korean": "나는 '내 서류가 어떻게 없을 수 있죠? 지금 알제에 있어요'라고 물었어. 그녀는 '아니, 우리는 보냈어'라고 했지. 나는 '지금 나한테 소리치는 거예요? 나는 지금 부처에 있고, 여기서는 당신의 서류가 없다고 했어요'라고 말했어. 원문 안에서 '내 서류'와 '당신의 서류'라는 소유 표현이 서로 충돌해.",
        "processing_flags": "context_heavy|long_source|source_ambiguity",
        "enrichment_state": "flagged",
    },
    226: {
        "latin": "aya 9e3det tbeddelli f l hedra w tekdeb 3liya w t9oul rselto 9alha medili accuse wara9a belli wsel 9atlo ma 3andich.",
        "english": "Then a feminine addressee kept changing the story and lying to me, saying it had been sent. The source then shifts the actor forms to 'he told her: give me an acknowledgment, a paper that it arrived,' followed by 'she told him: I do not have one.' The actor sequence may be corrupted.",
        "korean": "그러자 여성형으로 지칭된 상대는 말을 바꾸며 내게 거짓말하고, 서류를 보냈다고 했어. 이어서 원문의 행위자 형태는 '그가 그녀에게 도착 확인서나 증명서를 달라고 말했다'와 '그녀가 그에게 없다고 말했다'로 바뀌어, 행위자 연결이 손상됐을 수 있어.",
        "processing_flags": "code_switching|source_ambiguity|source_corruption",
        "enrichment_state": "flagged",
    },
    253: {
        "korean": "그는 삼촌에게 '내 사촌이 오랑대학교 졸업반 수석을 했는데 문제가 생겨 학교에서 서류를 잃어버렸어'라고 설명했어.",
    },
}

OLD_VALUES = {
    (206, "latin"): "la la manich baghi hakda. rani baghi zin w 3win. oui w 7aya wa9fa w choufou dans le fond [corrupted segment]. 7aya fort. baghi re9ba ki ternich safya w wej mriya la9i la9i ha rbi la9i nar achwa9i f bent 3ekrimi. ah matlou3a.",
    (209, "english"): "Listen, Hamid, you are exposing or embarrassing me in front of people early in the morning. Do not tell me that I will expose you or anything. I will drive you mad. The remaining claims about Aziza and 'farya' are unclear in the source.",
    (209, "korean"): "들어 봐, 하미드. 아침부터 사람들 앞에서 나를 폭로하거나 망신 주고 있잖아. 내가 너를 폭로하겠다는 식으로 말하지 마. 너를 미치게 할 거야. 이어지는 아지자와 'farya'에 관한 주장은 원문만으로 뜻이 불분명해.",
    (211, "english"): "Am I 'trat9i'? That expression is unclear. Go and complain; whether you take your money and leave or do not leave now. By God, the phrase about it not being 'farya' is also unclear. All right; every meeting has another after it.",
    (211, "korean"): "내가 'trat9i'라고? 그 표현은 불분명해. 가서 신고해. 지금 돈을 가져가서 떠나든 떠나지 않든 해. 맹세코 'farya가 아니다'라는 부분도 뜻이 불분명해. 좋아, 만남 뒤에는 또 다른 만남이 있다는 말이야.",
    (212, "english"): "A girl would not obey her mother and came out upset. Her mother asked where she was going; she replied, 'Do not look for me.' The mother threatened to incite her brother against her so that he would beat her. The girl answered, 'Send him with them,' slammed the door, made up her mind, and left. Some wording is uncertain.",
    (212, "korean"): "한 여자가 어머니 말을 듣지 않고 화가 난 채 나왔어. 어머니가 어디 가느냐고 묻자 '나를 찾지 마'라고 했어. 어머니는 오빠가 오면 부추겨서 그녀를 때리게 하겠다고 위협했어. 그녀는 '그도 그들과 함께 보내'라고 답하고 문을 세게 닫은 뒤 마음먹고 나갔어. 일부 표현은 불분명해.",
    (213, "korean"): "저녁이 되자 오빠가 그녀를 기다리고 있었고 주먹으로 공격했어. 그 결과를 나타내는 'n8elha'의 뜻은 불분명해. 그날부터 그녀는 말을 듣고 행동을 바로잡으며 다시는 그러지 않겠다고 했어. 마지막 속담 같은 표현도 불분명해.",
    (225, "korean"): "나는 '내 서류가 어떻게 없을 수 있죠? 지금 알제에 있어요'라고 물었어. 그녀는 '아니, 우리는 보냈어'라고 했지. 나는 '지금 나한테 소리치는 거예요? 나는 지금 부처에 있고, 여기서는 내 서류가 없다고 했어요'라고 말했어.",
    (225, "processing_flags"): "context_heavy|long_source",
    (225, "enrichment_state"): "draft",
    (226, "latin"): "aya 9e3det tbeddelli f l hedra w tekdeb 3liya w t9oul rselto 9oltlha medili accuse wara9a belli wsel 9aletli ma 3andich.",
    (226, "english"): "She kept changing her story and lying to me, saying she had sent it. I told her, 'Give me an acknowledgment, a paper showing it arrived.' She said, 'I do not have one.'",
    (226, "korean"): "그녀는 말을 계속 바꾸며 보냈다고 거짓말했어. 나는 '도착했다는 접수증이나 증명서를 주세요'라고 했고, 그녀는 그런 것이 없다고 했어.",
    (226, "processing_flags"): "code_switching",
    (226, "enrichment_state"): "draft",
    (253, "korean"): "아버지는 삼촌에게 '내 사촌이 오랑대학교 졸업반 수석을 했는데 문제가 생겨 학교에서 서류를 잃어버렸어'라고 설명했어.",
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
    if [(r["source_uid"], r["sentno"]) for r in source_rows] != [
        (r["source_uid"], r["sentno"]) for r in before_rows
    ]:
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
    expected_changed_cells = sum(len(values) for values in CORRECTIONS.values())
    if changed_cells != expected_changed_cells or changed_cells != 17:
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
        or existing_check["events"] != 3802
    ):
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))

    generated_at = current_utc_timestamp()
    new_events = [
        event(row["source_uid"], field, row[field], generated_at)
        for row in after_rows
        for field in CORRECTIONS.get(int(row["sentno"]), {})
    ]
    new_event_text = "".join(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n"
        for value in new_events
    )
    combined_event_text = existing_event_text + new_event_text
    combined_check = check_provenance_events(combined_event_text, source_uids)
    trace = check_enrichment_provenance(after_rows, combined_event_text)
    if (
        combined_check["result"] != "PASS"
        or combined_check["events"] != 3819
        or trace["result"] != "PASS"
    ):
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after_rows)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(new_event_text.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"].update(
        {
            "enrichment_completed_rows": 158,
            "enrichment_draft_rows": 41,
            "enrichment_flagged_rows": 57,
            "enrichment_not_started_rows": 1100,
            "processing_flags_populated_rows": 154,
        }
    )
    evidence = list(status.get("evidence_files", []))
    correction_path = "data/master/qa/madoran_enrichment_batch04_correction01_qa.json"
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
            "new_provenance_events": 766 + len(new_events),
            "total_provenance_events": combined_check["events"],
            "expected_total_provenance_events": combined_check["events"],
            "content_review_status": "pending_headgpt_correction_review",
            "draft_rows": 41,
            "flagged_rows": 23,
            "generated_at": generated_at,
            "latest_event_hash_gate": "PASS",
        }
    )
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction_qa = {
        "result": "PASS",
        "batch_id": "MADORAN-ENRICH-004",
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
        "draft_rows": 41,
        "flagged_rows": 23,
        "processing_flags_populated_rows": 62,
        "generated_at": generated_at,
        "outputs": {
            "batch": "data/master/enrichment/batches/batch04_sentno_0193_0256.tsv",
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
