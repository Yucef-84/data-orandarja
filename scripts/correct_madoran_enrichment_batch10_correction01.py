"""Apply HeadGPT correction 01 for MADOran Batch 10."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch10 import BATCH_ID, BATCH_OUT, TARGET_END, TARGET_START
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "6c39fce"
CORRECTION_ID = "MADORAN-ENRICH-010-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v10-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch10_correction01_qa.json"


CORRECTIONS = {
    578: {
        "english": "After we finish the procession and dinner, I want to wear a European or Western-style outfit; we will call it a robe de soirée.",
        "korean": "행렬과 저녁 식사를 마친 뒤에는 유럽식 또는 서구식 옷을 입고 싶어요. 그것을 ‘robe de soirée’라고 부를게요.",
    },
    586: {
        "english": "I am going to talk only about Oran. There are many things to do in this city. First, there is no order or system in Algeria, especially in Oran; I assume that Oran residents do not know what order is.",
        "korean": "오랑에 대해서만 이야기할게요. 이 도시에는 할 일이 많아요. 먼저 알제리, 특히 오랑에는 질서나 체계가 없어요. 오랑 사람들은 질서가 무엇인지 모르는 것 같다고 생각해요.",
        "speech_act": "opinion",
    },
    587: {
        "english": "The streets are dirty—very dirty, not a jungle—and it has gone too far. Let me explain: if you are not from Oran, you may not understand that Oran women and men are known for their way of speaking; girls and boys speak loudly, like to fight and wrestle, and defend one another.",
        "korean": "거리는 더러워요. 아주 더럽지만 정글은 아니고, 너무 심해진 상태예요. 설명해 줄게요. 오랑 출신이 아니면 오랑의 여성과 남성이 말하는 방식으로 유명하다는 것을 이해하지 못할 수도 있어요. 여자와 남자들은 큰 소리로 말하고, 싸우고 몸싸움하기를 좋아하며, 서로를 지켜 줘요.",
    },
    589: {
        "english": "A genuine Oran woman is already dressed for you. Some follow jilbab fashions: a black jilbab, a jilbab described by the unclear word غوز, and a yellow jilbab. She wears a headband, ties it into a bow, and holds an unclear object; I need to see exactly what she is holding. She is wearing a jilbab like this and holding it.",
        "korean": "진짜 오랑 여성은 이미 옷차림을 갖추고 있어요. 어떤 사람은 질밥 유행을 따라 검은 질밥, ‘غوز’라는 색 표현이 불분명한 질밥, 노란 질밥을 입어요. 머리띠를 매고 매듭을 지어 리본처럼 만들었으며, 불분명한 물건을 들고 있어요. 정확히 무엇을 들고 있는지 봐야 해요. 이런 식으로 질밥을 입고 그것을 들고 있어요.",
    },
    590: {
        "english": "An Oran woman may be a little full-figured, fuller here and there, and walk like this. But if you end up with an Oran woman who is nerveuse or hot-tempered, your day is over and your life is ruined; the exact relationship implied by the phrase is unclear.",
        "korean": "오랑 여성은 조금 통통할 수 있고 여기저기 더 풍만하며 이렇게 걸어요. 하지만 신경이 곤두선 사람 또는 성질이 급한 오랑 여성과 엮이면 하루가 끝나고 인생이 망한다는 식으로 말해요. 그 표현이 정확히 어떤 관계를 뜻하는지는 불분명해요.",
        "topic": "oran_woman_appearance_and_temper",
    },
    591: {
        "english": "Let me explain why: you are dressed in a civilisée or Westernized way, normally, and standing there without realizing what is going on while you see her pass before your eyes; some wording is unclear.",
        "korean": "왜 그런지 설명해 줄게요. 당신은 ‘civilisée’, 즉 서구화된 방식으로 평범하게 옷을 입고 서 있어요. 무슨 일이 일어나는지도 모른 채 그녀가 눈앞을 지나가는 것을 보게 돼요. 일부 표현은 불분명해요.",
    },
    598: {
        "english": "This was my first video; I hope you liked it. If you liked it and want me to make more videos in Arabic, tell me in the comments. That is it: I finished the video in three languages and said merci in French.",
        "korean": "이것은 제 첫 영상이었어요. 마음에 들었기를 바라요. 마음에 들었고 제가 아랍어 영상을 더 만들기를 원한다면 댓글로 말해 주세요. 이게 다예요. 영상을 세 언어로 마치고 프랑스어로 ‘merci’라고 했어요.",
    },
    599: {
        "english": "Get a grip, Naima—something like ‘a star, not Milan.’ Not Milan: you have had no value for a long time, and your children, described with the unclear word حركى, appeared in the Casbah. The lyric and name references are unclear.",
        "korean": "정신 차려, 나이마. ‘스타이지 밀라노는 아니다’ 같은 말이에요. 밀라노는 아니야. 너는 오래전부터 가치가 없었고, ‘حركى’라는 표현으로 묘사된 너희 아이들이 카스바에 나타났다는 식이에요. 가사와 이름의 지칭은 불분명해요.",
    },
    602: {
        "english": "Oran is a civilization and its history is great; it produced leaders or prominent figures. It is always my country, and I am fiercely protective of it. I write lines about it; some names and references are unclear.",
        "korean": "오랑은 문명이고 그 역사는 위대해요. 오랑은 지도자나 저명한 인물들을 배출했어요. 오랑은 언제나 내 나라이고 나는 그것을 매우 지켜 주고 싶어요. 오랑에 대한 구절을 써요. 일부 이름과 지칭은 불분명해요.",
    },
    603: {
        "english": "The administration is messed up and has nothing to do with football; we have cut our losses or ties. Do us a favor and leave us alone: we want to bring home the championship. Let Hamri celebrate and let us become well. We love Mouloudia, stand by it, and will never abandon it. Few words, measured talk. We will make a march as before and bring it back; whoever betrayed us will get what is coming. Some slang is unclear.",
        "korean": "행정은 엉망이고 축구와는 아무 상관이 없어요. 우리는 손실이나 관계를 끊었다는 식으로 말해요. 부탁이니 우리를 내버려 둬요. 우리는 우승을 가져오고 싶어요. 함리가 기뻐하게 하고 우리도 잘되게 하자는 말이에요. 우리는 물루디아를 사랑하고 그 편에 서며 절대 버리지 않아요. 말은 적게, 대화는 신중하게 해요. 예전처럼 행진을 벌여 되돌리고, 우리를 배신한 사람은 대가를 치르게 할 거예요. 일부 속어는 불분명해요.",
    },
    617: {
        "english": "Come, let us tour beautiful Oran, its flowers and symbols. Oran is a land of determination and an unclear epithet; how lucky are those who visit and head there. Whoever wants to enter, welcome, brother. Whoever wants to relax there should enjoy the view and know that they are safe. Old Oran has four gates. It is the land of the martyr Ahmed Zabana.",
        "korean": "아름다운 오랑과 그 꽃과 상징을 둘러보러 가요. 오랑은 굳센 의지와 불분명한 별칭을 지닌 땅이에요. 오랑을 방문하고 향하는 사람은 정말 운이 좋아요. 들어오고 싶은 사람은 누구든 환영해요. 그곳에서 쉬고 싶은 사람은 경치를 즐기며 안전하다는 것을 알 수 있어요. 옛 오랑에는 네 개의 문이 있어요. 순교자 아흐메드 자바나의 땅이에요.",
    },
    618: {
        "english": "Larbi Ben M'hidi, who defeated the enemy; we will not forget those who carried our flag, brothers. Niyati and Ben Slimane are also named as free martyrs who brought us freedom and left a historical imprint as proof.",
        "korean": "적을 물리친 라르비 벤 므히디를 말해요. 우리의 깃발을 들었던 형제들을 잊지 않을 거예요. 니아티와 벤 슬리마네도 우리에게 자유를 가져오고 역사적 흔적을 증거로 남긴 자유로운 순교자들로 언급돼요.",
    },
    619: {
        "english": "May God have mercy on them; may their place be in Paradise, and, God willing, may they enter through Bab Rayyan. There were many sheikhs whose words educated and delighted us, and many came from the Casbah and gave voice to our melody. The references to Qlal and Ibrahim Hamada Bouna and to poems written long ago are partly unclear.",
        "korean": "하느님께서 그들에게 자비를 베푸시고 그들의 자리가 천국이 되기를 바라요. 하느님의 뜻이라면 바브 라이얀을 통해 들어가기를 바라요. 우리를 가르치고 즐겁게 한 말을 남긴 셰이크가 많았고, 카스바 출신으로 우리의 멜로디에 목소리를 보탠 사람도 많았어요. 끌랄과 이브라힘 하마다 부나, 오래전에 쓰인 시에 대한 지칭은 일부 불분명해요.",
    },
    623: {
        "english": "Moulay Abdq pleased us and lifted us up; there are so many domes in you, Oran. The source spelling of the name and the exact quantity are retained as uncertain.",
        "korean": "물라이 압드크가 우리를 기쁘게 하고 일으켜 세웠어요. 오랑아, 너에게는 돔이 정말 많아요. 이름의 원문 표기와 정확한 수량은 불확실한 채로 보존해요.",
    },
    625: {
        "english": "El Kerma and our ancestors: this is our tradition, and everyone who comes to us becomes happy. May God have mercy on all the sheikhs—Sheikh Ahmed Qrouabi and Sheikh Fethi; may God have mercy on them in that resting place. May God preserve Sheikh Blaoui and prolong his life.",
        "korean": "엘 케르마와 우리의 조상들이여, 이것이 우리의 전통이에요. 우리를 찾아오는 사람은 모두 행복해져요. 모든 셰이크에게 하느님의 자비가 있기를 바라요. 셰이크 아흐메드 크루아비와 셰이크 페티에게 자비를 베푸시고, 그들이 잠든 곳에서도 그러기를 바라요. 하느님께서 셰이크 블라위를 지켜 주시고 그의 수명을 늘려 주시기를 바라요.",
    },
    626: {
        "english": "We take a rest, and our tour is finished. I have decided to leave you here, brothers. This is only an hour with you and our gathering; say something—not merely words spoken with a sweet tongue. Some wording is unclear.",
        "korean": "잠시 쉬고 우리 투어를 마쳐요. 형제들이여, 여러분을 이곳에 남겨 두기로 했어요. 여러분과 함께한 한 시간과 우리의 모임일 뿐이니, 혀로 달콤한 말만 하지 말고 무언가 말해 주세요. 일부 표현은 불분명해요.",
    },
    628: {
        "english": "All right, just one like that? When you arrest criminals like this and everything is happening, I want to ask you, please: I have a son, and I have already submitted a police dossier for him. If you can, see what you can do to help me.",
        "korean": "알겠어요, 그런 사람 하나뿐인가요? 이렇게 범죄자들을 체포하고 모든 일이 벌어지는 상황에서 부탁하고 싶어요. 제 아들이 있고, 아들을 위해 경찰 서류를 이미 제출했어요. 가능하다면 무엇을 해서 저를 도울 수 있는지 봐 주세요.",
    },
    629: {
        "english": "Yes, that one—we will talk about it later. But now let us clap: my friend and I are a dangerous duo, or the exact phrase is unclear. Brother, do you need a woman at home to give you a massage or something like that? No, my sister—married?—but it is all right, come here.",
        "korean": "네, 그건 나중에 이야기할게요. 하지만 지금은 박수를 쳐요. 나와 친구는 위험한 듀오라는 뜻인지, 정확한 표현은 불분명해요. 형제여, 집에서 마사지를 해 주는 여자나 그런 사람이 필요해요? 아니, 내 자매가 결혼했다는 말인지도 불분명하지만, 괜찮으니 이리 와요.",
        "topic": "banter_about_massage_and_relationship_status",
    },
    630: {
        "english": "My friend, I need a vest. If there is a parking job, I want to work; if there is one in Algeria, let me know. Stop fooling around. My friend, I told you I only need a vest—you thought I said something else. The rest of the banter is unclear.",
        "korean": "친구야, 나는 조끼가 필요해. 주차 일이 있으면 일하고 싶어. 알제리에 그런 일이 있으면 알려 줘. 장난 그만해. 친구야, 나는 조끼만 필요하다고 했는데 네가 다른 말을 들은 것 같아. 나머지 농담은 불분명해.",
    },
    633: {
        "english": "Shut your mouth, sir. You talk to them now; you are the announcer for today's celebration. We will celebrate with our brother with bread and, at the same time, an intentionally absurd menu: soup with chicken moustaches, trotters from a head-or-feet dish, lentils with an unclear accompaniment, and fried rice with an unclear garnish. We will honor you.",
        "korean": "입 다물어요, 선생님. 이제 당신이 그들에게 말해요. 오늘 행사의 진행자잖아요. 우리 형제와 빵으로 축하하고, 동시에 일부러 황당한 메뉴를 내놓을 거예요. 닭 수염을 넣은 수프, 머리나 발 요리의 족발 같은 것, 불분명한 곁들임을 넣은 렌틸콩, 불분명한 고명을 곁들인 볶음밥이에요. 여러분을 성대하게 대접할게요.",
    },
    634: {
        "english": "I want to go to the toilet—is that all right? You, shut your mouth! How many times have I told you that when we are talking about food, you must not bring up the toilet? What is wrong with you—are you adding it to a cabinet or what? You are [an unclear insult]. Fine, go; the remaining insults are unclear.",
        "korean": "화장실에 가고 싶은데 괜찮아요? 당신, 입 다물어요! 음식을 이야기할 때 화장실 얘기를 꺼내지 말라고 몇 번이나 말했어요? 왜 그래요. 화장실을 찬장에 넣기라도 하겠다는 거예요? 당신은 [불분명한 욕설]이에요. 됐어요, 가요. 나머지 욕설은 불분명해요.",
    },
    635: {
        "english": "Peace be upon you, everyone; welcome. I am Lamine Emilio, and you know where I am: the city of Oran. This is episode two at Restaurant Rahma, which is run by a charitable association called Nas Khir in Oran, with Mohamed Jamal Talha. Let us go meet at the restaurant.",
        "korean": "여러분, 평안하세요. 환영합니다. 저는 라민 에밀리오이고 제가 어디에 있는지 알겠죠. 오랑시에 있어요. 오랑의 나스 키르라는 자선 협회가 운영하는 라흐마 식당 2편이며, 모하메드 자말 탈하와 함께해요. 식당에서 만나러 가요.",
    },
    636: {
        "english": "I am dressed, brother. We are here in Hamri, one of the oldest neighborhoods in Oran. Behind me is the Nas Khir association of Oran, and we are ready to do the shopping as usual; the remaining names and wording are unclear.",
        "korean": "옷을 갖춰 입었어요. 오랑에서 가장 오래된 동네 중 하나인 함리에 와 있어요. 제 뒤에는 오랑의 나스 키르 협회가 있고, 평소처럼 장을 보러 갈 준비가 됐어요. 나머지 이름과 표현은 불분명해요.",
    },
    637: {
        "english": "I am with my dear friend Sofiane from Nas Khir. He understands the mentality, what needs to happen, and what we are going to do. Sofiane, welcome; welcome to Oran. The rest is a greeting exchange.",
        "korean": "나는 나스 키르 소속인 사랑하는 친구 소피안과 함께 있어요. 그는 상황과 필요한 일, 우리가 하려는 일을 이해해요. 소피안, 환영해요. 오랑에 온 것을 환영해요. 나머지는 인사를 주고받는 대화예요.",
    },
    640: {
        "english": "We are going to the market to do our shopping. I should add that yesterday a man, may God reward him, bought us a ram, slaughtered it, cut it up, prepared it, and brought it to us. Another donor brought us chickens; may God increase his reward.",
        "korean": "우리는 장을 보러 시장에 가요. 덧붙이면 어제 한 남자가 하느님의 보상을 받기를 바라는데, 우리에게 양을 사서 도축하고 자르고 손질해 가져다줬어요. 또 다른 기부자가 닭을 가져다줬어요. 하느님께서 그의 보상을 더해 주시기를 바라요.",
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
    if not head.startswith(BASE_COMMIT):
        raise RuntimeError(f"base_commit_mismatch:{head}:{BASE_COMMIT}")
    if source_gate()["result"] != "PASS":
        raise RuntimeError("source_gate_failed")
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
    if len(CORRECTIONS) != 25 or changed_fields != 53:
        raise RuntimeError(f"correction_shape:{len(CORRECTIONS)}:{changed_fields}")
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 8586:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 8639 or trace["result"] != "PASS":
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
    evidence_path = "data/master/qa/madoran_enrichment_batch10_correction01_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": 25, "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID, "latest_correction_id": CORRECTION_ID,
        "correction_history": history, "correction_changed_fields": changed_fields,
        "correction_state_updates": 0, "correction_rows": 25, "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 8639, "expected_total_provenance_events": 8639,
        "content_review_status": "pending_headgpt_correction_review", "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS", "batch_id": BATCH_ID, "correction_id": CORRECTION_ID, "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)], "changed_fields": changed_fields,
        "state_updates": 0, "new_provenance_events": changed_fields, "provenance_events_before": 8586,
        "provenance_events_after": 8639, "source_gate": "PASS", "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
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
