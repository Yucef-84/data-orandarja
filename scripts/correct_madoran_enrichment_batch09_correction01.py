"""Apply the first HeadGPT content correction set for MADOran Batch 09."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_madoran_enrichment_batch09 import (
    BATCH_ID,
    BATCH_OUT,
    TARGET_END,
    TARGET_START,
)
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


BASE_COMMIT = "8200bab"
CORRECTION_ID = "MADORAN-ENRICH-009-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v9-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch09_correction01_qa.json"


# HeadGPT identified these 22 rows. Only English/Korean are changed; the
# canonical Arabic, Latin transcription, controlled metadata, flags, and
# state remain untouched.
CORRECTIONS = {
    514: {
        "english": (
            "Literally, 'a supplication without sins melts on its owner's head'; as a proverb, it suggests that an "
            "unfounded prayer or curse returns to the person who uttered it. The exact idiomatic wording is uncertain."
        ),
        "korean": (
            "문자 그대로는 ‘죄 없는 기도는 그 주인의 머리에서 녹는다’는 뜻이고, 속담으로는 근거 없이 한 기도나 "
            "저주가 그것을 말한 사람에게 돌아온다는 의미인 듯해요. 정확한 관용적 표현은 불확실해요."
        ),
    },
    527: {
        "english": (
            "Sorry, sister. What are you waiting for, please? What will you drink—water? Please, I will bring you "
            "[an unclear item or phrase], and the menu too. Some words are unclear in the recording."
        ),
        "korean": (
            "미안해요, 언니. 무엇을 기다리고 있어요, 제발? 무엇을 마실래요—물? [불분명한 물건이나 표현]과 "
            "메뉴도 가져다줄게요. 녹음에서 몇몇 단어는 불분명해요."
        ),
    },
    528: {
        "english": (
            "Do you like it? The wording mentions a 'pêche Melba'-like item and says that some items are unavailable. "
            "Chocolate is unavailable; what about banana and caramel? There is only banana ice cream, and caramel is "
            "unavailable. The exact flavor/product sequence is uncertain."
        ),
        "korean": (
            "마음에 들어요? 표현에는 ‘pêche Melba’ 같은 항목이 나오고 일부 항목은 없다고 해요. 초콜릿은 없고, "
            "바나나와 캐러멜은 어떤가요? 바나나 아이스크림만 있고 캐러멜은 없어요. 정확한 맛·제품 순서는 "
            "불확실해요."
        ),
    },
    529: {
        "english": (
            "No brownie or Calypso either. What about a drink? Yes, we have all the juices. Bring me banana juice. "
            "Is orange juice no longer available? Is the cocktail no longer available? We only have Hamoud."
        ),
        "korean": (
            "브라우니나 칼립소도 없어요. 음료는요? 네, 주스는 모두 있어요. 바나나 주스를 가져다줘요. 오렌지 "
            "주스는 더 이상 없어요? 칵테일도 더 이상 없어요? 우리에게는 함우드만 있어요."
        ),
    },
    532: {
        "english": (
            "Top up my Flexy, please! Unfortunately, the next phrase sounds like French 'en même temps' ('at the "
            "same time'), and the following phrase about Hamoud is unclear. Do not embarrass me by flirting with my "
            "friend in front of me, you whore; I will not let this pass, so go away and leave my friend alone. Several "
            "slang phrases are unclear."
        ),
        "korean": (
            "플렉시를 충전해 줘요! 안타깝게도 다음 표현은 프랑스어 ‘en même temps’(동시에)처럼 들리고, 함우드에 "
            "관한 그다음 표현은 불분명해요. 내 앞에서 내 친구에게 추근대며 나를 망신시키지 마, 이 창녀야. "
            "그냥 넘기지 않을 테니 멀리 가서 내 친구를 내버려 둬요. 몇몇 속어 표현은 불분명해요."
        ),
    },
    533: {
        "english": (
            "There is nothing beautiful in this world like sport. I would remove all the sportspeople or athletes, but "
            "some people have truly ruined it for us."
        ),
        "korean": (
            "이 세상에 스포츠만큼 아름다운 것은 없어요. 모든 스포츠인이나 운동선수들을 없애고 싶지만, 어떤 "
            "사람들이 정말 우리를 위해 그것을 망쳐 놓았어요."
        ),
    },
    535: {
        "english": (
            "Then you say: 'devenir sportif' ('become sporty or athletic'), not 'devenir photographe' ('become a "
            "photographer'); the French wordplay and repeated-word structure are unclear."
        ),
        "korean": (
            "그럼 ‘devenir sportif’(운동을 좋아하거나 운동을 하는 사람이 되다)라고 하지, ‘devenir photographe’(사진작가가 "
            "되다)라고 하는 것은 아니에요. 프랑스어 말장난과 반복 구조는 불분명해요."
        ),
    },
    540: {
        "english": (
            "Yes, he is alive and with someone described as 'Nahaïsi' (نحايسي; the exact occupational or reference "
            "meaning is unclear); his protein is rising only with Mega Mass, not generic vitamins. The rest of the "
            "exchange is unclear."
        ),
        "korean": (
            "네, 그는 살아 있고 ‘나하이시’(نحايسي; 정확한 직업·지칭 의미는 불분명함)라는 표현으로 묘사된 사람과 "
            "함께 있어요. 그의 단백질은 일반적인 비타민이 아니라 Mega Mass로만 올라간다고 해요. 나머지 대화는 "
            "불분명해요."
        ),
    },
    541: {
        "english": (
            "Inside it she says only 'my life'; outside, she asks how things are. When people come to prank you, you "
            "see only speed ('la vitesse') and pulling, haha. The wording is largely unclear."
        ),
        "korean": (
            "안에서는 그녀가 ‘내 인생’이라고만 말하고, 밖에서는 어떻게 지내냐고 물어요. 사람들이 당신을 놀리러 "
            "오면 속도(‘la vitesse’)와 당기는 것만 보인다는 듯해요. 표현은 대체로 불분명해요."
        ),
    },
    543: {
        "english": (
            "Do you want to change your clothes to enter the sea? The source mentions 'maillot' and '2 pièces' "
            "(swimsuit/two-piece wording; their exact relation is unclear). We observe modesty, so we wear thirty-three "
            "pieces, add a scarf, wrap yourself in a towel, and come dressed."
        ),
        "korean": (
            "바다에 들어가려고 옷을 갈아입을래요? 원문에는 ‘maillot’와 ‘2 pièces’(수영복·투피스라는 표현이지만 "
            "둘의 정확한 관계는 불분명함)가 나와요. 우리는 단정함을 지켜서 서른세 조각을 입고, 스카프를 더하고, "
            "수건으로 몸을 감싸서 옷을 입은 채 와요."
        ),
    },
    544: {
        "english": (
            "When you go inside, you will do it like that and think you are Katrina with that hair. Oh, your father—he "
            "is cutting watermelon, or he turns and only looks at you; the scene is unclear."
        ),
        "korean": (
            "안으로 들어가면 그렇게 하고 그 머리로 자신이 카트리나라고 생각할 거예요. 아, 네 아버지는 수박을 "
            "자르고 있거나, 돌아서 당신만 바라봐요. 장면은 불분명해요."
        ),
    },
    546: {
        "english": (
            "I wanted to swim, but you spoiled it for me jokingly. Let me swim like this; perhaps an Algerian shark will "
            "come out and bite you in the leg. It says, 'I will teach you to swim, will I?' The body-part wording is "
            "colloquial and partly unclear."
        ),
        "korean": (
            "수영하고 싶었는데 네가 장난으로 망쳐 버렸어. 이렇게라도 수영하게 해 줘. 어쩌면 알제리 상어가 나타나 "
            "네 다리를 물지도 몰라. ‘내가 수영을 가르쳐 주겠다고?’라는 식의 말이에요. 신체 부위 표현은 구어적이고 "
            "일부는 불분명해요."
        ),
    },
    548: {
        "english": (
            "When your father sees you like that, he whistles; your brother takes off his shirt and comes in. You all "
            "act as if you chose this, and that is all; the wording is unclear."
        ),
        "korean": (
            "네 아버지가 당신을 그렇게 보면 휘파람을 불고, 네 형제는 셔츠를 벗고 들어와요. 여러분은 모두 이것을 "
            "선택한 척 연기하고, 그게 전부예요. 표현은 불분명해요."
        ),
    },
    551: {
        "english": (
            "Hey, I am telling you, sister: do not [unclear verb] the phrase involving 'les histoires' and history; "
            "write the history yourself. Now we will measure you and show you the girls' mentality. The later wordplay "
            "is largely unclear."
        ),
        "korean": (
            "언니, 내가 말할게요. ‘les histoires’와 역사에 관한 표현에서 [동사는 불분명함]이라고 하고, 역사는 직접 "
            "써요. 이제 여러분을 재고 여자들의 사고방식을 보여 줄게요. 뒤의 말장난은 대체로 불분명해요."
        ),
    },
    555: {
        "english": (
            "So I am going to speak Algerian to you. It may sound a little strange because it is not my usual speech; I "
            "speak Algerian at home, but not much, and I have not returned to Algeria for two years, so I have forgotten "
            "some of it."
        ),
        "korean": (
            "그래서 여러분에게 알제리어로 말해 볼게요. 평소 쓰는 말이 아니라서 조금 이상하게 들릴 수 있어요. 집에서 "
            "알제리어를 말하기는 하지만 많이 하지는 않고, 2년 동안 알제리에 가지 않아 조금 잊었어요."
        ),
    },
    562: {
        "english": (
            "As I told you, I come from Oran, and it is clear that in Oran we listen to rai. The following words shift "
            "into an angry, apologetic, or possibly lyric-like address—'I made you very angry ... you hurt my heart ... I "
            "cry every day ... I love you ... forgive me, my love'—but this should not be treated as a confirmed real "
            "romantic dialogue; speaker boundaries are unclear."
        ),
        "korean": (
            "말했듯이 나는 오랑에서 왔고, 오랑에서 라이 음악을 듣는다는 것은 분명해요. 이어지는 말은 화가 난 "
            "사과나 노래 가사 같은 발화로 전환되는 듯해요—‘내가 당신을 아주 화나게 했고… 당신은 내 마음을 아프게 "
            "했고… 매일 울고… 당신을 사랑해요… 용서해 줘요, 내 사랑’—하지만 이를 확인된 실제 연인 대화로 단정해서는 "
            "안 돼요. 발화자 경계는 불분명해요."
        ),
    },
    564: {
        "english": (
            "I have a very long list. First, chorba and harira are obvious. I do not like olive stews at all, but I love "
            "the olive-and-pea tagine. I do not like chickpea dishes very much either. Couscous is obvious, with sauce or "
            "plain seffa; that is all."
        ),
        "korean": (
            "목록이 아주 길어요. 먼저 초르바와 하리라는 당연해요. 올리브 스튜는 전혀 좋아하지 않지만 올리브와 완두콩 "
            "타진은 정말 좋아해요. 병아리콩 요리도 별로 좋아하지 않아요. 쿠스쿠스는 당연하고, 소스를 곁들이거나 그냥 "
            "세파로 먹어요. 이게 다예요."
        ),
    },
    566: {
        "english": (
            "I know how to cook all kinds of stews, but I do not know how to cook ta'am or food in general (in this "
            "Algerian context, couscous); I tried making couscous once, and it was very good. Everyone who tastes my "
            "harira or chorba loves it. I can say I know how to make harira and chorba. Perhaps they want to marry me; I "
            "only need a groom, but let us not discuss that topic."
        ),
        "korean": (
            "나는 여러 종류의 스튜를 만들 줄 알지만 타암, 즉 일반적인 음식(이 알제리 맥락에서는 쿠스쿠스)을 만드는 "
            "법은 잘 몰라요. 쿠스쿠스는 한 번 만들어 봤는데 아주 맛있었어요. 내 하리라나 초르바를 맛본 사람은 모두 "
            "좋아해요. 하리라와 초르바는 만들 줄 안다고 말할 수 있어요. 아마 사람들이 나를 결혼시키고 싶어 하나 봐요. "
            "신랑만 있으면 되지만 그 주제는 말하지 말아요."
        ),
    },
    568: {
        "english": (
            "Tcharek (تشارك), an Algerian pastry, and baklava: I loved baklava when I was little, but now it seems far "
            "too sweet, too thick, and too long to make. Oh no. Qriouch is excellent, though."
        ),
        "korean": (
            "알제리 페이스트리인 타샤렉(Tcharek, تشارك)과 바클라바를 말해요. 어릴 때는 바클라바를 정말 좋아했지만, "
            "지금은 너무 달고 너무 두껍고 만들기에도 너무 오래 걸리는 것 같아요. 아, 안 돼요. 그래도 크리우시는 아주 "
            "좋아요."
        ),
    },
    572: {
        "english": (
            "No. I have never tried it, and I do not know how to explain it to you. I am very, very shy, but I will not "
            "try it in front of you—do not ask me, not even that ('même pas'), haha. I will not try it in front of you. "
            "The playful wording is partly unclear."
        ),
        "korean": (
            "아니요. 한 번도 해 보지 않았고 여러분에게 어떻게 설명할지도 모르겠어요. 아주 아주 부끄럽지만 여러분 앞에서 "
            "시도하지 않을 테니 묻지 말아요—‘même pas’(그것조차 안 돼요)라고 할 정도예요, 하하. 여러분 앞에서는 시도하지 "
            "않을 거예요. 장난스러운 표현이라 일부는 불분명해요."
        ),
    },
    574: {
        "english": (
            "For a wedding of people I do not know, one dress is enough. For a family wedding, I wear one Arab outfit. I "
            "love Arab clothes; I do not want to dress in a 'civilisée' or Westernized way. I am 'émigrée' or part of the "
            "diaspora, but for my family's wedding I make an occasion of it. The dialectal and French-derived terms are "
            "retained because their exact nuance is uncertain."
        ),
        "korean": (
            "모르는 사람들의 결혼식이면 드레스 하나면 충분해요. 가족 결혼식에는 아랍식 옷 한 벌을 입어요. 아랍식 옷을 "
            "입는 것을 정말 좋아하고, ‘civilisée’ 또는 서구화된 방식으로 입고 싶지는 않아요. 나는 ‘émigrée’, 즉 이민·"
            "디아스포라와 관련된 사람이지만 가족 결혼식에는 제대로 차려입어요. 방언·프랑스어에서 온 표현은 정확한 뉘앙스가 "
            "불확실해 그대로 보존해요."
        ),
    },
    575: {
        "english": (
            "No, you are 'gour/gwer'—a term in this context for foreigners, Europeans, or Westerners—and you do not know "
            "Arab traditions. A bride changes five, seven, sometimes up to nine outfits; nine is a lot."
        ),
        "korean": (
            "아니요, 여러분은 ‘gour/gwer’—이 문맥에서 외국인·유럽인·서구인을 가리키는 표현—이고 아랍 전통을 잘 모르네요. "
            "신부는 옷을 다섯 벌이나 일곱 벌, 때로는 아홉 벌까지 갈아입어요. 아홉 벌은 정말 많아요."
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
    if changed_fields != expected_events or len(CORRECTIONS) != 22:
        raise RuntimeError(f"correction_shape:{len(CORRECTIONS)}:{changed_fields}:{expected_events}")

    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 7762:
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
        or combined_check["events"] != 7762 + expected_events
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
    evidence_path = "data/master/qa/madoran_enrichment_batch09_correction01_qa.json"
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
            "total_provenance_events": 7762 + expected_events,
            "expected_total_provenance_events": 7762 + expected_events,
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
        "provenance_events_before": 7762,
        "provenance_events_after": 7762 + expected_events,
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
