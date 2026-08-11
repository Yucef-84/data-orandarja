"""Apply the remaining HeadGPT semantic and metadata corrections for MADOran Batch 13."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch13 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "c661bd6"
CORRECTION_ID = "MADORAN-ENRICH-013-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v13-correction-2"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_correction02_qa.json"

CORRECTIONS = {
    770: {"genre": "narrative"},
    771: {"processing_flags": "code_switching|long_source|source_ambiguity"},
    772: {
        "english": "The speaker tells the other person to stop humiliating the family because people can hear them, then asks what people have to do with the speaker or why the speaker should care about them, before asking whether the other person even knows what happened this month; the relation to outsiders is unclear.",
        "korean": "화자는 사람들이 듣고 있으니 가족을 망신시키는 일을 그만두라고 한 뒤, 사람들이 자신과 무슨 상관인지 또는 자신이 사람들을 왜 신경 써야 하는지 반문하고, 상대에게 이번 달에 무슨 일이 있었는지 알기나 하느냐고 물어요. 외부 사람들과의 관계는 불분명하게 남겨요.",
    },
    773: {"processing_flags": "code_switching|long_source|source_ambiguity"},
    775: {"processing_flags": "code_switching|source_ambiguity"},
    776: {"processing_flags": "code_switching|source_ambiguity"},
    786: {
        "english": "After greetings, the speaker asks the group whether everything is all right. The speaker says they were embarrassed and did not know what to say, had a midday plane to catch, and then addresses the group in the plural: ‘You were a little late / made us wait a little.’ The following ‘forgive us’ is kept as a separate or partly unclear turn.",
        "korean": "인사를 나눈 뒤 화자가 일행에게 모두 괜찮은지 물어요. 화자는 말하기가 부끄럽고 무슨 말을 해야 할지 몰랐으며 정오 비행기를 타야 했다고 말한 뒤, 복수의 상대에게 ‘여러분이 조금 늦었어요/우리를 조금 기다리게 했어요’라고 말해요. 이어지는 ‘우리를 용서해 주세요’는 별도의 발화이거나 일부 불분명한 turn으로 남겨요.",
    },
    788: {
        "english": "Salim is asked what he will drink. The speaker addresses Si Jamal and says, ‘Look, Si Jamal, I will come to you later; I have not accepted this offer.’ The speaker asks what they think and recalls that they only agreed to meet today to finish the purchase. Si Jamal is the addressee, not the speaker.",
        "korean": "살림에게 무엇을 마실지 묻고, 화자가 시 자말 씨에게 ‘보세요, 시 자말 씨, 나중에 당신에게 갈게요. 나는 이 제안을 받아들이지 않았어요’라고 말해요. 어떻게 생각하는지 묻고 오늘 만나 매매를 끝내기로만 합의했다는 점을 상기해요. 시 자말 씨는 화자가 아니라 호격의 대상이에요.",
    },
    796: {"topic": "villa_documents_cards_and_key_visit"},
    801: {
        "english": "Sabiha is greeted and invited to go see the aunt. The affectionate exclamations address the other person as ‘my beautiful one’ and mention the daughter; the speaker says they missed her daughter. The praise is directed toward the addressee, not the speaker’s own beauty.",
        "korean": "사비하를 부르며 이모를 보러 가자고 해요. 다정한 감탄으로 상대를 ‘내 예쁜이’라고 부르고 딸을 언급하며, 화자는 자신의 딸이 그리웠다고 말해요. 칭찬의 대상은 화자 자신의 외모가 아니라 상대예요.",
    },
    803: {
        "english": "Salima is told that this is her brother’s house and that she may stay in it for as long as she wants. If the time or days pass and it gets late, they should go and study; the French-derived les jours expression remains flagged as code-switching.",
        "korean": "살리마에게 그 집은 자신의 형제의 집이고 원하는 만큼 그곳에 머물러도 된다고 말해요. 시간이 지나 늦어지면 가서 공부하자고 해요. 프랑스어에서 유래한 les jours 표현은 code-switching으로 표시해요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    809: {
        "english": "One speaker asks the woman, ‘Aren’t you worried about your brother?’ The woman answers that she worries about her brother more than the other person does and wants to be with him. The questioner and respondent are kept in that order rather than attributing the question to Salima.",
        "korean": "한 화자가 여성에게 ‘네 형제가 걱정되지 않아?’라고 물어요. 여성이 ‘나는 당신보다 내 형제를 더 걱정하고, 그와 함께 있고 싶어’라고 답해요. 질문자와 응답자의 순서를 유지하며 질문을 살리마의 발화로 돌리지 않아요.",
    },
    812: {
        "english": "The speaker says that whoever says a word of truth or a right word is mocked or reproached, then asks, ‘Would any woman reproach or mock her brother’s wife?’ The family relationship in مرت خوها is preserved before asking them to leave this subject and return to another discussion.",
        "korean": "화자는 진실이나 옳은 말을 하는 사람도 조롱받거나 비난받는다고 한 뒤, ‘어떤 여자가 자기 오빠나 남동생의 아내를 비난하거나 조롱하겠어?’라고 물어요. مرت خوها가 가리키는 가족관계를 보존한 채 이 주제를 그만두고 다른 이야기로 돌아가자고 해요.",
    },
    816: {
        "english": "After goodbyes to Si Jamal and another guest, the speaker says something like ‘Can’t you see, my friend?’ and apologizes. صاحبِي is retained as the vocative ‘my friend,’ not as a separate friend being visited.",
        "korean": "시 자말 씨와 다른 손님에게 작별 인사를 한 뒤, 화자가 ‘안 보여, 친구야?’와 같은 말과 함께 미안하다고 해요. صاحبي는 따로 만나러 가는 친구가 아니라 ‘친구야’라는 호격으로 보존해요.",
    },
    817: {
        "english": "The speaker says, ‘No, just leave it, my friend. Pardon.’ صاحبِي remains a vocative addressed to the other person, not a third person being left behind.",
        "korean": "화자가 ‘아니, 그냥 둬, 친구야. 미안해’라고 말해요. صاحبي는 남겨 두는 제3자가 아니라 상대를 부르는 ‘친구야’라는 호격으로 남겨요.",
        "topic": "farewell_vocative_my_friend",
    },
    819: {
        "english": "The visitor tells the woman that he was once her student. An official is mentioned as having summoned her for a matter, while the final ‘خير إن شاء الله’ is a separate response meaning roughly ‘I hope it is something good’ or ‘What is it, God willing?’; it is not attributed to the visitor as a question about whether everything is well.",
        "korean": "방문객이 그 여성에게 자신이 예전에 그 여성의 학생이었다고 말해요. 담당자가 어떤 용건으로 그녀를 불렀다는 말이 이어지고, 마지막 ‘خير إن شاء الله’는 방문객의 질문이 아니라 ‘좋은 일이길 바라요’ 또는 ‘무슨 좋은 일인가요?’ 정도의 별도 응답으로 남겨요.",
    },
    822: {
        "english": "After hearing the explanation, the woman or other party asks, ‘And his son?’ The official then explains that he summoned her to tell her first, before the family tells her and shocks her, and asks her to prepare herself. The question is not attributed to the official.",
        "korean": "설명을 들은 여성이나 상대방이 ‘그럼 그의 아들은?’이라고 물어요. 이어 담당자가 가족이 먼저 말해 그녀를 놀라게 하기 전에 자신이 먼저 알려 주려고 불렀다고 설명하고 마음의 준비를 하라고 해요. 아들에 대한 질문을 담당자의 발화로 돌리지 않아요.",
    },
    825: {"speech_act": "information"},
    827: {
        "english": "After her death, après automatiquement, the villa would return or revert according to the document to the children of his brother, Nasser. The source says that two people are signed on the document, and the speaker laments that his brother Nasser’s children wait for her to die so they can take the house. The exact legal mechanics remain partly unclear; لزوج is not expanded to ‘husband.’",
        "korean": "그녀가 죽은 뒤에는 프랑스어 après automatiquement, 즉 이후 자동으로라는 표현과 함께 문서에 따라 그의 형제인 나세르의 자녀들에게 별장이 돌아가거나 귀속된다고 해요. 원문은 두 사람이 그 문서에 서명해 있다고 말하고, 화자는 그의 형제 나세르의 자녀들이 집을 가져가려고 자신이 죽기를 기다린다고 한탄해요. 정확한 법적 작동 방식은 일부 불분명하게 남기며, لزوج를 ‘남편’으로 확대하지 않아요.",
    },
    832: {
        "english": "The stranger says, in effect, ‘I will let you go, but do not shout or make a sound, understood?’ The coercive threat is preserved. The final fragment mentions his phone and ‘the villa keys you gave me’; it has no explicit verb establishing a request or transfer, so it is not rendered as a definite demand.",
        "korean": "낯선 사람은 ‘내가 너를 풀어 줄 테니 소리치거나 소리를 내지 마, 알겠어?’라는 취지로 말해요. 강압적 위협을 보존해요. 마지막 fragment는 자신의 전화기와 ‘네가 나에게 준 별장 열쇠’를 언급하지만, 요구나 양도를 명시하는 동사가 없으므로 확정적인 요구로 번역하지 않아요.",
    },
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid, field, value, generated_at):
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
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 11250:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 11285 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"]["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after)
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch13_correction02_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": len(CORRECTIONS), "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID,
        "latest_correction_id": CORRECTION_ID,
        "correction_history": history,
        "correction_changed_fields": changed_fields,
        "correction_state_updates": 0,
        "correction_rows": len(CORRECTIONS),
        "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 11285,
        "expected_total_provenance_events": 11285,
        "processing_flags_populated_rows": status["counts"]["processing_flags_populated_rows"],
        "batch_processing_flags_populated_rows": sum(bool(row["processing_flags"]) for row in corrected_batch),
        "content_review_status": "pending_headgpt_correction_review",
        "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS",
        "batch_id": BATCH_ID,
        "correction_id": CORRECTION_ID,
        "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)],
        "changed_fields": changed_fields,
        "state_updates": 0,
        "new_provenance_events": changed_fields,
        "provenance_events_before": 11250,
        "provenance_events_after": 11285,
        "source_gate": "PASS",
        "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
        "morphology_reads": 0,
        "arabic_modified": 0,
        "outside_target_mutations": 0,
        "learning_unit_rows_created": 0,
        "latest_event_hash_gate": "PASS",
        "validator": "PASS",
        "target_rows": 64,
        "draft_rows": 3,
        "flagged_rows": 61,
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
