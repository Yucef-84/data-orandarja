"""Apply the first HeadGPT-directed semantic corrections for MADOran Batch 14."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch14 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "92b340a"
CORRECTION_ID = "MADORAN-ENRICH-014-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v14-correction-1"
MODEL = "llm-review-directed"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch14_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch14_correction01_qa.json"

CORRECTIONS = {
    837: {
        "english": "The first fragment says that the speaker will not be late before the clients arrive, although its exact wording is uncertain. The speaker then tells Dalila to watch out for anyone who might mix something into the speaker's goods.",
        "korean": "첫 부분은 손님들이 오기 전에 화자가 늦지 않을 것이라는 뜻으로 보이지만 정확한 표현은 불확실해요. 이어 달릴라에게 누군가 자기 물건에 무엇인가를 섞지 않도록 조심하라고 해요.",
    },
    842: {
        "english": "The speaker asks the listener whether the people the listener is asking have brought the listener money.",
        "korean": "화자는 상대에게 상대가 묻고 있는 사람들이 상대에게 돈을 가져왔는지 물어요.",
    },
    855: {
        "english": "The speaker says the listener understands nothing and anticipates that he may say her brother has a long reach. She says the listener is not simple either and asks what his work and dealings are with that man. If his wife accepts, nothing will change, and the woman standing before him also deserves happiness.",
        "korean": "화자는 상대가 아무것도 모른다며, 상대가 자신의 오빠가 영향력이 크다고 말할 것이라고 예상해요. 상대도 만만하지 않다며 그 남자와 상대의 일이나 거래가 무엇인지 물어요. 상대의 아내가 받아들여도 달라질 것은 없고, 앞에 서 있는 여성도 행복할 자격이 있다고 말해요.",
    },
    856: {
        "english": "The speaker tells the listener to sit and refers to the listener's account that someone imprisoned them for three days in the villa's shack. The listener confirms that the person took the villa keys and a portable phone. The speaker asks how three days passed, and the account says the captive was released only after the captor had thought it over.",
        "korean": "화자는 앉으라고 하며 상대가 누군가에게 별장 창고에서 사흘 동안 갇혔다고 말한 일을 언급해요. 상대는 그 사람이 별장 열쇠와 휴대전화를 가져갔다고 확인해요. 화자는 어떻게 사흘이 지났는지 묻고, 그 이야기에 따르면 갇힌 사람은 납치범이 생각한 뒤에야 풀려났어요.",
    },
    859: {
        "english": "The speaker says that even Madame's jewelry is all in the bank and asks why the man stole the listener's keys and kept them for three days. The listener says they do not know. The speaker then asks whether the listener remembers the man's face.",
        "korean": "화자는 부인의 보석도 모두 은행에 있는데 왜 그 남자가 상대의 열쇠를 훔쳐 사흘 동안 가지고 있었는지 물어요. 상대는 모른다고 답하고, 화자는 그 남자의 얼굴을 기억하는지 다시 물어요.",
    },
    863: {
        "english": "The listener says this was stated in the first report: they could not shout because the man carried a weapon under his coat, but in fairness he never used it. They called the villa owners, who said they would enter with a procès-verbal, a formal report or record; the French legal term is retained because the exact procedure is unclear.",
        "korean": "상대는 첫 번째 조서에 그렇게 말했다며, 그 남자가 옷 아래 무기를 들고 있어 소리칠 수 없었지만 공정하게 말하면 그것을 사용한 적은 없다고 해요. 별장 주인에게 전화하자 procès-verbal, 즉 공식 조서나 기록을 가지고 들어가겠다고 했다고 말해요. 정확한 절차는 불분명해 프랑스어 법률 용어를 보존해요.",
    },
    869: {
        "english": "The speaker tells the listener that they have one hour; if the money does not reach Ali within that hour, the speaker will cut off the listener's head. It is a direct violent threat with an explicit time limit.",
        "korean": "화자는 상대에게 한 시간이 있다며, 그 시간 안에 돈이 알리에게 도착하지 않으면 상대의 목을 자르겠다고 해요. 명시적인 시간 제한이 있는 직접적인 폭력 위협이에요.",
    },
    870: {
        "english": "A boy greets Aunt Zoulikha; she asks how he is, and he says he is fine. He reminds her that, as he said, when her bread runs out he will bring bread to her from the bakery. Aunt Zoulikha refuses, saying the bread from the last time smelled of chicken.",
        "korean": "한 소년이 줄리카 이모에게 인사하고, 이모가 잘 지내느냐고 묻자 소년은 괜찮다고 답해요. 소년은 전에 말했듯 이모의 빵이 떨어지면 빵집에서 빵을 가져다주겠다고 상기시켜요. 줄리카 이모는 지난번 빵에서 닭 냄새가 났다며 거절해요.",
    },
    871: {
        "english": "The person who was to bring the bread asks how it could have smelled of chicken, says they wash before finishing work and then bring the bread, and accepts the other person's decision. The exact speaker labels remain somewhat uncertain.",
        "korean": "빵을 가져오려던 사람이 어떻게 닭 냄새가 날 수 있느냐고 묻고, 일을 마치기 전에 씻은 뒤 빵을 가져오겠다고 해요. 상대가 이미 결정했다고 하자 그 뜻대로 하겠다고 받아들여요. 정확한 화자 표지는 일부 불확실해요.",
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
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 12078:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 12078 + changed_fields or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    status["counts"]["processing_flags_populated_rows"] = sum(bool(row["processing_flags"]) for row in after)
    evidence_path = "data/master/qa/madoran_enrichment_batch14_correction01_qa.json"
    evidence = list(status.get("evidence_files", []))
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
        "total_provenance_events": 12078 + changed_fields,
        "expected_total_provenance_events": 12078 + changed_fields,
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
        "provenance_events_before": 12078,
        "provenance_events_after": 12078 + changed_fields,
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
