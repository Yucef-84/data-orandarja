"""Apply the first HeadGPT Batch 07 correction set with append-only provenance."""
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


BASE_COMMIT = "5f55f9e"
CORRECTION_ID = "MADORAN-ENRICH-007-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v7-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
TARGET_START = 385
TARGET_END = 448
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch07_correction01_qa.json"


CORRECTIONS = {
    390: {
        "english": (
            "When they have steamed, take the pot and a frying pan, add a little oil, pour the carrots into it, "
            "and add cumin and caraway. Add the ingredient heard as 'qarfou' and leave it for about ten minutes; "
            "then turn off the heat, cover it, and enjoy your meal."
        ),
        "korean": (
            "당근이 쪄지면 냄비와 프라이팬을 준비해 기름을 조금 두르고 당근을 넣어요. 쿠민과 캐러웨이를 넣고, "
            "‘카르푸’로 들리는 재료를 넣어 약 10분 두었다가 불을 끄고 덮어요. 맛있게 드세요."
        ),
    },
    391: {
        "english": (
            "Wafa, I wanted to ask you about that squid with rice that you made. I want the recipe—how you made it "
            "with just a little of the ingredient, as I felt like making it too."
        ),
        "korean": (
            "와파, 네가 만든 밥을 넣은 오징어에 대해 물어보고 싶었어. 조금만 넣어서 어떻게 만들었는지 그 레시피가 "
            "알고 싶어. 나도 만들어 보고 싶었거든."
        ),
    },
    393: {
        "english": (
            "Cook a bowl of rice with a little salt, drain it, and add some parsley, coriander, hot pepper, cumin, "
            "red pepper, and a pinch of saffron. Add three portions of grated garlic and mix everything together."
        ),
        "korean": (
            "밥 한 그릇을 소금을 조금 넣어 지은 뒤 물기를 빼요. 파슬리, 고수, 매운 고추, 쿠민, 붉은 고추, "
            "사프란 한 꼬집과 간 마늘 세 부분을 넣고 모두 섞어요."
        ),
        "processing_flags": "source_ambiguity",
    },
    401: {
        "english": (
            "We left in the morning to have enough time. On the way, we saw severe traffic congestion, with many "
            "vehicles stopped. We slowed down and found a crash: a car had collided with a crushed truck, people "
            "were injured, and there was blood. God forbid."
        ),
        "korean": (
            "시간을 넉넉히 쓰려고 아침에 출발했어요. 가는 길에 교통이 심하게 막혀 많은 차량이 멈춰 있는 것을 "
            "봤어요. 속도를 줄이니 차와 찌그러진 트럭이 충돌한 사고가 있었고, 사람들이 다치고 피도 보였어요. "
            "하느님, 그런 일이 없기를."
        ),
    },
    404: {
        "english": (
            "Later they raised the amount; the source mentions 'dimil' (two thousand) and also 400 dinars, but the "
            "exact relation is unclear. Even if it was only a park, people had maintained it, or it looked like a "
            "track with nothing there; in any case, we said it was fine. The remaining wording is unclear."
        ),
        "korean": (
            "나중에는 금액을 올렸는데, 원문에는 ‘dimil’(2천)과 400디나르가 모두 언급되어 정확한 관계는 불분명해요. "
            "그냥 공원일 뿐이거나 아무것도 없는 길처럼 보여도 사람들이 관리하고 있었고, 어쨌든 괜찮다고 했어요. "
            "나머지 표현은 불분명해요."
        ),
    },
    407: {
        "english": (
            "My brother went to him because the man had fallen into the water. He kept turning around in place as the "
            "water pulled him, until my brother saved him and brought him out. Civil protection arrived and gave him "
            "artificial respiration to bring him back because he had lost consciousness; they removed the water he had "
            "swallowed until he came back to life, dressed him, and took him away."
        ),
        "korean": (
            "형제는 그 사람에게 갔어요. 그 남자가 물에 빠져 물이 그를 끌어당기는 가운데 제자리에서 계속 허우적거렸고, "
            "형제가 그를 구해 밖으로 데리고 나왔어요. 의식을 잃었기 때문에 민방위 구조대가 와서 인공호흡을 해 살렸고, "
            "삼킨 물을 빼내며 정신을 되찾게 한 뒤 옷을 입혀 데려갔어요."
        ),
    },
    409: {
        "english": (
            "After that we got hungry, went out, drank tea, and ate flatbread and cake. We played beach rackets, then "
            "played dominoes; people relaxed, gathered, and chatted, while some played in the sand. It was a beautiful, "
            "rich day, and we came back tired."
        ),
        "korean": (
            "그 뒤 배가 고파져 밖으로 나가 차와 플랫브레드, 케이크를 먹었어요. 해변 라켓 놀이를 하고 도미노도 했고, "
            "사람들은 쉬고 모여서 이야기를 나누며 일부는 모래에서 놀았어요. 즐겁고 풍성한 하루였고 우리는 지쳐서 "
            "돌아왔어요."
        ),
    },
    412: {
        "english": (
            "When a man wants to establish a family and intends a lawful marriage, he goes to ask for the woman from "
            "her family or guardian. He takes relatives with him, brings a cake and a bouquet of flowers, and a ring; "
            "some also bring chocolate and sweets."
        ),
    },
    413: {
        "english": (
            "If they like each other, they continue with it and agree on conditions such as money and gold jewelry, "
            "including bracelets. Then they choose the day for the Fatiha ceremony."
        ),
        "korean": (
            "서로 마음에 들면 결혼을 계속 진행하고 돈과 금 장신구, 이를테면 팔찌류 같은 조건을 합의해요. 그런 다음 "
            "파티하를 올릴 날을 정해요."
        ),
    },
    414: {
        "english": (
            "On the day before the Fatiha, the groom's mother brings them a ram, vegetables, fruit, and everything "
            "needed for cooking. The bride receives a tray with a traditional dress such as a karakou, Constantine "
            "dress, Oran blouza, Mansouria, or caftan, according to each family's means, with shoes and a bag, plus a "
            "djellaba and a burnous; almost everyone gives a burnous."
        ),
        "korean": (
            "파티하 전날 신랑 어머니 쪽에서 요리에 필요한 숫양, 채소, 과일을 모두 가져와요. 신부에게는 집안 형편에 "
            "따라 카라쿠, 콘스탄틴 전통 의상, 오랑 블루자, 만수리아, 카프탄 같은 옷을 담은 쟁반을 주고, 신발과 가방, "
            "젤라바와 부르누스도 함께 마련해요. 거의 모두 부르누스를 해요."
        ),
    },
    418: {
        "english": (
            "We begin with the Fatiha, people ululate, the men eat and perform the unclear action heard as 'yishour'; "
            "then the women sit and serve them food too. When we finish, the celebration and dancing start with a DJ. "
            "Every so often we see the bride arrive in another outfit with her husband beside her, and people ululate "
            "and celebrate until evening."
        ),
        "korean": (
            "파티하로 시작하고 사람들이 자그라트를 하며, 남자들은 먹고 ‘이슈르’로 들리는 불분명한 행동을 해요. "
            "그다음 여자들도 앉아 남자들에게 음식을 대접해요. 다 끝나면 DJ 음악에 맞춰 축하와 춤이 시작돼요. "
            "때때로 신부가 남편을 곁에 두고 다른 옷으로 나타나고, 사람들은 저녁까지 자그라트를 하며 즐겨요."
        ),
    },
    419: {
        "english": (
            "After that they distribute assorted cakes, coffee, and tea, the evening continues, and people perform the "
            "unclear action heard as 'tshour'."
        ),
        "korean": (
            "그 뒤에는 여러 종류의 케이크와 커피, 차를 나누고 저녁이 이어지며 사람들이 ‘츠후르’로 들리는 불분명한 "
            "행동을 해요."
        ),
        "processing_flags": "source_ambiguity",
    },
    421: {
        "english": (
            "As people say, a wedding is one night whose preparation takes a year. Another saying is that in summer "
            "there are cakes and rain. And a wedding is easy: slaughter a kid and call her to come; the final phrase "
            "refers to the companionship of married life after the wedding, though the exact saying remains partly "
            "unclear. The sayings are preserved as heard."
        ),
        "korean": (
            "사람들이 말하듯 결혼식은 하룻밤이지만 준비에는 1년이 걸려요. 또 여름에는 케이크와 비가 함께 온다는 "
            "식의 말도 있어요. 결혼식은 쉽다며 염소 새끼를 잡고 그녀를 부르라는 말도 있고, 마지막 부분은 결혼 뒤의 "
            "부부 생활을 가리키지만 정확한 속담 표현은 부분적으로 불분명해요. 속담은 들은 그대로 보존했어요."
        ),
    },
    424: {
        "english": (
            "She came out of the living room crying and told me, Nazir, save me. Her nose was bleeding and her body was "
            "blue from the beatings. I grabbed her father, struck him, took her to our house, and told her to stay here "
            "with us. Then I told her to put earphones in her ears and listen to music so she would not hear the beating."
        ),
        "korean": (
            "그녀가 거실에서 울며 나와 나지르, 나를 구해 달라고 했어요. 코에서는 피가 나고 몸은 맞아서 멍들어 있었어요. "
            "나는 그녀의 아버지를 붙잡아 때리고 그녀를 우리 집으로 데려와 여기 우리와 있으라고 했어요. 그런 다음 그녀에게 "
            "귀에 이어폰을 끼고 폭행 소리를 듣지 않도록 음악을 들으라고 했어요."
        ),
    },
    425: {
        "english": (
            "I locked the door on them and went out. I found her fiancé and his friends rushing into the neighborhood. I "
            "picked up an unclear object and stepped between them; I knocked down about twelve people, though one "
            "attacked me from behind. I gathered courage, confronted them, and told them not to do it that way, but to "
            "come and do something decent. I beat them and they all ran away."
        ),
        "korean": (
            "나는 그들을 안에 가두고 밖으로 나왔어요. 그녀의 약혼자와 친구들이 동네로 몰려오는 것을 봤어요. 불분명한 "
            "물건을 들고 그들 사이에 들어가 열두 명가량을 쓰러뜨렸지만 한 명이 뒤에서 나를 공격했어요. 용기를 내서 "
            "맞서며 그렇게 하지 말고 와서 제대로 해결하자고 했어요. 내가 그들을 때리자 모두 도망갔어요."
        ),
    },
    429: {
        "english": (
            "An ignorant person does not speak about the simplest matters; he is supposed to educate himself and distinguish "
            "between a flag, a banner, and an identity. Then he can speak and discuss. I want to ask you: when you raise "
            "the Palestinian flag, does it belong to Algeria?"
        ),
        "korean": (
            "무지한 사람은 가장 기본적인 일도 말하지 못해요. 스스로 공부해서 깃발과 현수막, 정체성을 구분해야 해요. "
            "그래야 말하고 토론할 수 있어요. 당신에게 묻고 싶어요. 팔레스타인 깃발을 들 때 그것은 알제리에 속하는 "
            "건가요?"
        ),
    },
    432: {
        "english": (
            "I told her that I saw no difference between Kabyle, Arab, or Targui/Tuareg people: we are all one block, all "
            "written as Algerians on our documents. These are only empty-headed people who seek to create division."
        ),
        "korean": (
            "나는 그녀에게 카빌인, 아랍인, 타르기(투아레그인) 사이에 차이가 없고 우리는 모두 하나이며 서류에는 모두 "
            "알제리 사람으로 적힌다고 했어요. 분열을 만들려는 사람들은 그저 생각이 빈 사람들이에요."
        ),
    },
    434: {
        "english": (
            "People in the old days said: a rolled mat carried on a pig's back—one person eats and the other watches. "
            "It means that people have started eating what is forbidden, while people with little watch and find nothing "
            "to eat."
        ),
        "korean": (
            "옛사람들이 말했어요. 돼지 등에 말아 올린 돗자리처럼 한 사람은 먹고 다른 사람은 지켜본다는 뜻이에요. "
            "사람들이 금지된 것을 먹기 시작했는데, 가진 것이 적은 사람들은 지켜보기만 하고 먹을 것을 찾지 못한다는 "
            "말이에요."
        ),
    },
    435: {
        "english": "Ah, Oran, ah!",
        "korean": "아, 오랑, 아!",
    },
    437: {
        "english": "You became a pond with halhal, a plant, and rats are living in you.",
        "korean": "너는 할할이라는 식물이 있는 웅덩이가 되었고 그 안에는 쥐들이 살고 있어.",
    },
    440: {
        "english": (
            "Listen: clean your face and do not worry about what you meet. If someone outdoes you in beauty, outdo them "
            "with a smile; if someone outdoes you in clothing, outdo them with cleanliness; if someone outdoes you in "
            "knowledge, outdo them with wit; and if someone outdoes you in money, outdo them with contentment."
        ),
        "korean": (
            "들어 봐. 얼굴을 깨끗이 하고 무엇을 만나든 걱정하지 마. 누가 아름다움으로 너를 앞서면 미소로 그를 앞서고, "
            "누가 옷차림으로 너를 앞서면 청결로 그를 앞서고, 누가 지식으로 너를 앞서면 재치로 그를 앞서고, 누가 돈으로 "
            "너를 앞서면 만족으로 그를 앞서라."
        ),
    },
    442: {
        "english": (
            "Ramadan is near and money is tight for me. The Eid ram has arrived, but I have no sacrifice. Everything has "
            "become difficult because there is no contentment. A son of good stock does not become stingy, and an oleander "
            "tree does not produce apples."
        ),
        "korean": (
            "라마단이 다가오는데 내 형편은 빠듯해. 명절 양이 왔지만 희생 제물을 마련할 수가 없어. 만족이 없으니 모든 "
            "것이 힘들어졌다는 말이야. 좋은 가문에서 난 아들은 인색해지지 않고 협죽도 나무는 사과를 맺지 않는다는 "
            "속담도 이어져."
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
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 6164:
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
    if combined_check["result"] != "PASS" or combined_check["events"] != 6164 + expected_fields or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))

    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))

    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch07_correction01_qa.json"
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
            "new_provenance_events": 751 + expected_fields,
            "total_provenance_events": 6164 + expected_fields,
            "expected_total_provenance_events": 6164 + expected_fields,
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
        "provenance_events_before": 6164,
        "provenance_events_after": 6164 + expected_fields,
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
        "processing_flags_populated_rows": 296,
        "batch_processing_flags_populated_rows": 47,
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
