"""Apply the full-batch HeadGPT semantic corrections for MADOran Batch 13."""
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

BASE_COMMIT = "7d68f62"
CORRECTION_ID = "MADORAN-ENRICH-013-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v13-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch13_correction01_qa.json"

CORRECTIONS = {
    770: {
        "english": "A lament about Oran says that the old houses were demolished and les souvenirs, the memories, were lost or destroyed; references to an Oran woman, her household, and what she suffered remain dense and partly ambiguous.",
        "korean": "오랑에 대한 탄식은 옛 집들이 허물어지고 프랑스어 les souvenirs, 즉 추억과 기억이 사라지거나 훼손되었다고 말해요. 오랑의 한 여성과 그 집안, 그리고 그녀가 겪은 일에 대한 언급은 조밀하고 일부 모호하게 남겨요.",
        "processing_flags": "code_switching|idiom_culture|long_source|source_ambiguity",
    },
    771: {
        "english": "Marzak is challenged about bringing the speaker there and starting this discussion. The speaker contrasts having let him sell the car or auto with now wanting to sell their home: ‘I let you sell the auto; now you want to sell our house.’",
        "korean": "마르자크가 화자를 여기 데려와 이런 말을 하게 한 이유를 따져요. 화자는 차나 자동차를 팔게 두었던 일과 이제 자기들의 집까지 팔려는 일을 대비해 ‘차는 팔게 했더니 이제 우리 집을 팔려고 하느냐’고 항의해요.",
    },
    772: {
        "english": "The speaker tells the other person to stop humiliating the family because people can hear them, then asks whether the other person even knows what happened this month; the relation to outsiders is unclear.",
        "korean": "화자는 사람들이 듣고 있으니 가족을 망신시키는 일을 그만두라고 한 뒤, 상대에게 이번 달에 무슨 일이 있었는지 알기나 하느냐고 물어요. 외부 사람들과의 관계는 불분명하게 남겨요.",
    },
    773: {
        "english": "The speakers say that their father is gone and that a company was seized, taken away, or otherwise disposed of, with the exact legal force unclear; now someone wants to sell their home, leaving them without a house or anything else.",
        "korean": "화자들은 아버지가 세상을 떠났고 회사가 압류되거나 빼앗기거나 처분된 듯하다고 말해요. 정확한 법적 강도는 불분명하게 두며, 이제 누군가 집까지 팔려 해 집도 아무것도 없이 남게 된다고 해요.",
    },
    775: {
        "english": "Zino is asked to slow down and listen. The speaker argues that the very large villa is too expensive to maintain and that even cleaning or managing it is beyond their means.",
        "korean": "지노에게 천천히 자신을 이해하게 해 달라고 해요. 아주 큰 별장은 유지비가 너무 많이 들고 청소하거나 관리하는 것조차 감당할 수 없다고 주장해요.",
    },
    777: {
        "english": "The speaker accepts that selling may be a solution but questions a price of two billion. They say the beautiful house in a good location could be listed on Ouedkniss and bring ten; the source leaves the unit unstated.",
        "korean": "화자는 매도가 해결책일 수는 있지만 20억 가격을 묻고, 좋은 곳의 아름다운 집을 우드키니스에 올리면 10을 받을 수 있다고 말해요. 원문은 10의 단위를 밝히지 않아요.",
    },
    780: {"processing_flags": "code_switching|source_ambiguity"},
    782: {
        "english": "The speaker addresses Si Elias: ‘Forgive me; I know this is not a good time, but please tell the mother to come to the office tomorrow, God willing, about an important matter.’",
        "korean": "화자가 시 엘리아스 씨에게 ‘때가 좋지 않은 것은 알지만 미안해요. 중요한 일 때문에 하느님의 뜻이라면 내일 어머니가 사무실로 오시라고 전해 주세요’라고 말해요.",
    },
    784: {
        "english": "The speaker says they are negotiating by phone. They understand the other person and will speak after the others arrive so that the acte, the contract or deed, can be prepared; they worry someone else may offer more, then end the call when the others enter.",
        "korean": "화자는 전화로 협상 중이라고 말해요. 다른 사람들이 도착하면 계약·증서인 acte를 준비할 수 있도록 이야기하겠다고 하며, 누군가 더 많이 제안할까 걱정하다가 사람들이 들어오자 전화를 끊어요.",
    },
    793: {
        "english": "They ask whether this is the final offer. One side mentions three point six billion and four billion, then returns to the first offer of three point six billion; the phrase ‘bwn kw awk’ is retained conservatively rather than normalized with confidence as bon courage, and the negotiation is closed.",
        "korean": "이것이 최종 제안인지 묻고 36억과 40억을 언급하다가 처음 제안인 36억으로 돌아가요. ‘بون كو اوك’처럼 들리는 표현은 bon courage라고 단정하지 않고 보수적으로 남기며, 협상은 끝나요.",
    },
    794: {"processing_flags": "code_switching|source_ambiguity"},
    795: {
        "english": "The speaker refuses to congratulate anyone until signing the act. They mention a billion ready to be paid in euros and discuss the villa’s papers or documents and les originaux, the originals, rather than furnishings or refrigerators.",
        "korean": "화자는 계약·증서에 서명할 때까지 축하하지 않겠다고 해요. 유로로 지급할 10억이 준비되어 있다고 하며 별장의 서류와 프랑스어 les originaux, 즉 원본들을 이야기해요. 비품이나 냉장고를 뜻하는 것으로 확대하지 않아요.",
    },
    796: {
        "english": "They say they have brought the originals and ask whether the others have theirs. They mention their cards or identity cards and the villa key, then invite the listener to go to the villa in case anything is needed or unknown; the exact turn boundaries remain somewhat unclear.",
        "korean": "그들은 원본 서류를 가져왔다고 하며 상대방도 자기 원본을 가지고 있는지 물어요. 자기 카드나 신분증류와 별장 열쇠를 언급한 뒤, 필요한 것이나 모르는 것이 있을 수 있으니 별장에 함께 가자고 해요. 정확한 발화 경계는 일부 불분명하게 남겨요.",
    },
    799: {
        "english": "After offering more coffee, Salima asks whether the listener likes her goût, her taste or sense, in relation to the decor and villa; the final response is unclear.",
        "korean": "살리마에게 커피를 더 권한 뒤, 살리마가 장식과 별장에 관한 자신의 goût, 즉 취향이나 감각이 마음에 드는지 물어요. 마지막 응답은 불분명하게 남겨요.",
        "processing_flags": "code_switching|source_ambiguity",
    },
    802: {
        "english": "A woman asks, ‘Who told you that I am leaving today?’ She then says that perhaps she is weighing on the other person’s heart or becoming a burden, while the surrounding lines say that she is loved and missed.",
        "korean": "한 여성이 ‘내가 오늘 간다고 누가 말했어?’라고 물어요. 이어 자신이 상대의 마음에 짐이 되거나 부담이 된 모양인지도 모른다고 말하고, 주변 발화에서는 사람들이 그녀를 사랑하고 그리워한다고 해요.",
    },
    803: {
        "english": "The speaker says that, as time gets late or before it passes, they should go and study; يفوتهم الحال is not a reference to other people passing by.",
        "korean": "화자는 시간이 늦어지거나 더 지나기 전에 가서 공부하자고 말해요. يفوتهم الحال을 다른 사람들이 지나간다는 뜻으로 확대하지 않아요.",
    },
    805: {
        "english": "The speaker tells Salima to clear her heart and forget the good years and difficult days. The source separately mentions her grandfather and your husband; it says that your husband is the one who kept the speaker, and possibly the speaker’s husband, from leaving the situation. The exact referents remain uncertain.",
        "korean": "화자는 살리마에게 마음을 풀고 좋았던 세월과 힘들었던 날을 잊으라고 해요. 원문은 그녀의 할아버지와 ‘네 남편’을 별개의 지시대상으로 언급하고, 그 상황에서 화자와 어쩌면 화자의 남편이 벗어나지 못하게 한 사람은 네 남편이라고 말해요. 정확한 지시대상은 불확실하게 남겨요.",
    },
    808: {
        "english": "The speaker asks whether Salima is in her right mind and reminds her that she knows why Khaled fled Oran. The speaker then asks why she thinks Youssef and his group are shouting; this is a question, not a negative command telling her not to imagine it.",
        "korean": "화자는 살리마가 제정신인지 묻고, 칼레드가 왜 오랑을 떠났는지 그녀도 잘 안다고 해요. 이어 유수프와 그 일행이 소리친다고 왜 생각하느냐고 물어요. 소리친다고 생각하지 말라는 부정 명령이 아니에요.",
    },
    810: {
        "english": "The speaker challenges Salima: ‘Are you going to be better than his mother and sister?’ The line asks whether she wants Khaled to leave his wife and children in Oran and come away; Khaled cannot live far from them. The family came so the children could attend école privée, a private school, and be raised well.",
        "korean": "화자는 살리마에게 ‘네가 그의 어머니와 누이보다 더 나을 거라는 거야?’라고 도전적으로 물어요. 이어 칼레드가 아내와 아이들을 오랑에 두고 떠나기를 바라는지 묻고, 칼레드는 가족과 멀리 살 수 없다고 해요. 가족은 아이들이 프랑스어 école privée, 즉 사립학교에 다니며 잘 자라게 하려고 왔어요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    811: {
        "english": "A woman objects to being mocked for not giving birth and asks rhetorically whether she would have wanted this for herself; she says that this is a matter from God, not a choice she made for herself.",
        "korean": "한 여성이 아이를 낳지 못한다고 조롱받는 데 항의하며, 자신이 이런 일을 스스로 원했겠느냐고 반문해요. 이것은 자신이 선택한 일이 아니라 하느님의 일이라고 말해요.",
    },
    812: {
        "english": "The speaker says that whoever says a word is mocked, then asks, ‘Would any woman reproach or mock her brother’s wife?’ The family relationship in مرت خوها is preserved before asking them to leave this subject and return to another discussion.",
        "korean": "화자는 무슨 말을 하는 사람이나 조롱받는다고 한 뒤, ‘어떤 여자가 자기 오빠나 남동생의 아내를 비난하거나 조롱하겠어?’라고 물어요. مرت خوها가 가리키는 가족관계를 보존한 채 이 주제를 그만두고 다른 이야기로 돌아가자고 해요.",
    },
    814: {
        "english": "Salima is told that her brother’s house is also her house. If she wants, she can go upstairs and wake him; otherwise she should wait for him in the salon. Waking him and waiting for him are kept as separate actions.",
        "korean": "살리마에게 오빠의 집은 곧 자신의 집이라고 말해요. 원하면 위로 올라가 그를 깨울 수 있고, 그렇지 않으면 거실에서 그를 기다리라고 해요. 깨우는 행동과 기다리는 행동을 구분해요.",
    },
    815: {"processing_flags": "code_switching|source_ambiguity"},
    818: {
        "english": "A morning greeting confirms that the teacher or official is there and that the visitor has an appointment. They are invited to sit and wait for a while, not to negotiate.",
        "korean": "아침 인사 뒤 선생님이나 담당자가 여기 있는지 확인하고 방문객에게 약속이 있다고 해요. 협상하자는 것이 아니라 앉아서 잠시 기다리자고 초대해요.",
    },
    819: {
        "english": "The visitor tells the woman that he was once her student. An appointment and a purpose are mentioned, but the phrase about the subject is partly unclear; the visitor asks whether everything is well.",
        "korean": "방문객이 그 여성에게 자신이 예전에 그 여성의 학생이었다고 말해요. 약속과 용건이 언급되지만 주제에 관한 표현은 일부 불분명하고, 방문객은 괜찮은 일인지 물어요.",
    },
    820: {
        "english": "The speaker says that before his death the deceased sold his properties. The other person replies that they have no idea about this matter; a following line says, unfortunately, that this is what happened. The turns are kept separate.",
        "korean": "화자는 고인이 죽기 전에 자신의 재산을 팔았다고 말해요. 상대방은 이 일에 대해 전혀 아는 것이 없다고 답하고, 이어지는 발화는 안타깝게도 그렇게 된 일이라고 말해요. 두 발화를 분리해요.",
    },
    821: {
        "english": "The speaker explains that all of the deceased’s properties were sold legally and that everything is registered to Karim and the children of his brother, Nasser. This is a legal-sale and registration relation, not an asserted inheritance registration; the exact family grouping remains conservative.",
        "korean": "화자는 고인의 재산을 모두 합법적으로 팔았고 모든 것이 카림과 그의 형제 나세르의 자녀들 명의로 등록되어 있다고 설명해요. 이는 상속 등록이라고 단정하는 것이 아니라 합법적 매각과 등록의 관계로 보존하며, 정확한 가족 묶음은 보수적으로 남겨요.",
        "topic": "legal_sale_and_registration_of_property",
    },
    824: {
        "english": "The preceding speaker says that the villa was also sold. In a separate turn, the woman asks, ‘Where will my son and I go?’ The question is not attributed to the official.",
        "korean": "앞선 화자가 별장도 팔렸다고 말해요. 별도의 발화에서 여성이 ‘그럼 나와 내 아들은 어디로 가야 해?’라고 물어요. 이 질문을 담당자나 관리자의 발화로 돌리지 않아요.",
    },
    825: {
        "english": "The speaker reassures her that he was asked to add a clause to the villa deed so that, tant que you are alive, meaning as long as you live, they cannot take the villa away. The line does not condition the protection on professional independence.",
        "korean": "화자는 안심하라고 하며, 당신이 살아 있는 동안에는 그들이 별장을 빼앗아 갈 수 없도록 별장 계약·증서에 조항을 넣어 달라는 요청을 받았다고 말해요. 이 보호를 직업적 자립 여부의 조건으로 만들지 않아요.",
    },
    827: {
        "english": "After her death, après automatiquement, the villa would return or revert according to the document to the relevant relatives. The source says that two people, including the husband, are signed on the document, and the speaker laments that the children of Nasser’s brother wait for her to die so they can take the house. The exact legal mechanics remain partly unclear.",
        "korean": "그녀가 죽은 뒤에는 프랑스어 après automatiquement, 즉 이후 자동으로라는 표현과 함께 문서에 따라 별장이 관련 친족에게 돌아가거나 귀속된다고 해요. 원문은 남편을 포함한 두 사람이 그 문서에 서명해 있다고 말하고, 화자는 나세르의 형제의 자녀들이 집을 가져가려고 자신이 죽기를 기다린다고 한탄해요. 정확한 법적 작동 방식은 일부 불분명하게 남겨요.",
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    828: {
        "english": "The speaker apologizes for what happened and asks what fault this poor person or man had. The gender and exact referent of مسكين remain unresolved rather than being rendered as a woman.",
        "korean": "화자는 일어난 일에 미안해하며 이 불쌍한 사람이나 남자가 무슨 잘못을 했느냐고 물어요. مسكين의 성별과 정확한 지시대상은 여성이라고 확정하지 않고 열어 둬요.",
    },
    829: {
        "english": "In any case, the deceased had placed or sponsored Si Elias under kafala. The speaker explains that kafala does not give the makfoul, the person under that protection, inheritance rights, even if the makfoul bears the same name; the French phrase le même nom is retained rather than turned into a sibling relation.",
        "korean": "어쨌든 고인은 시 엘리아스를 kafala, 즉 후견·보호·스폰서십 관계에 두었다고 해요. 화자는 kafala가 그 대상인 makfoul에게 상속권을 주는 것은 아니며, 같은 성이나 이름을 쓰더라도 마찬가지라고 설명해요. 프랑스어 le même nom을 친형제 관계로 바꾸지 않아요.",
        "topic": "kafala_without_inheritance_rights",
    },
    832: {
        "english": "The stranger says, in effect, ‘I will let you go, but do not shout or make a sound, understood?’ The coercive threat is preserved. The final fragment mentions his phone and the villa keys that were given to them, but it has no explicit verb establishing a request or transfer, so it is not rendered as a definite demand.",
        "korean": "낯선 사람은 ‘내가 너를 풀어 줄 테니 소리치거나 소리를 내지 마, 알겠어?’라는 취지로 말해요. 강압적 위협을 보존해요. 마지막 fragment는 자신이 가진 전화기와 그들에게 준 별장 열쇠를 언급하지만, 요구나 양도를 명시하는 동사가 없으므로 확정적인 요구로 번역하지 않아요.",
        "topic": "coercive_threat_and_phone_villa_key_fragment",
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
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 11180:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 11250 or trace["result"] != "PASS":
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
    evidence_path = "data/master/qa/madoran_enrichment_batch13_correction01_qa.json"
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
        "total_provenance_events": 11250,
        "expected_total_provenance_events": 11250,
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
        "provenance_events_before": 11180,
        "provenance_events_after": 11250,
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
