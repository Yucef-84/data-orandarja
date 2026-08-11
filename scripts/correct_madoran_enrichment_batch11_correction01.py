"""Apply the first HeadGPT correction set for MADOran Batch 11."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts.build_madoran_enrichment_batch11 import BATCH_ID, BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import (
    ENRICHMENT_FIELDS, ENRICHMENT_OUT, EVENTS_OUT, ROOT, SOURCE_OUT,
    check_provenance_events, read_tsv, source_gate, write_tsv,
)
from scripts.validate_madoran_enrichment import check_enrichment_provenance

BASE_COMMIT = "f88f40d"
CORRECTION_ID = "MADORAN-ENRICH-011-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v11-correction-1"
MODEL = "codex-unspecified"
SCHEMA_VERSION = "1.1.0"
STATUS_OUT = ROOT / "data/master/state/madoran_layer_status.json"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch11_correction01_qa.json"

# These are deliberately conservative: source wording, named entities, numeric
# strings, body-part references, and unclear speaker/actor relations stay visible.
CORRECTIONS = {
    641: {
        "english": "They brought peas and potatoes as food provisions. The phrase نتأمنش عقلك is an unclear colloquial reaction, so its exact speaker/force is not fixed here. Now we will go shopping and bring only what we need to start cooking and prepare food for poor people.",
        "korean": "완두콩과 감자 같은 식량을 가져왔어요. ‘نتأمنش عقلك’은 화자와 정확한 기능을 확정하지 않은 불분명한 구어적 반응으로 남겨요. 이제 요리를 시작하고 가난한 사람들을 위해 음식을 준비하는 데 필요한 것만 사러 갈 거예요.",
    },
    644: {
        "english": "Welcome to a new episode of the program ‘Very Frank.’ Today we are in Oran Province, talking about how expensive house rent is for young people who are going to marry and asking for their opinions. The explicit interview question is: ‘How do you see house rents in Oran?’",
        "korean": "‘아주 솔직하게’의 새 회차에 오신 것을 환영해요. 오늘은 오랑 주에서 결혼하려는 젊은이들에게 집세가 얼마나 비싼지 이야기하고 그들의 의견을 물어볼 거예요. 명시적인 인터뷰 질문은 ‘오랑의 주택 임대를 어떻게 보세요?’예요.",
    },
    648: {
        "english": "A studio apartment here is rented for two million. I am someone with nothing left as my wedding approaches; I will not lie to you, I cannot rent. I am going to live with my family.",
        "korean": "여기 원룸은 200만에 빌려요. 결혼을 앞두고 가진 것이 남아 있지 않은 사람인데, 솔직히 말하면 집을 빌릴 수가 없어요. 가족과 함께 살 거예요.",
    },
    652: {
        "english": "Rent in Oran is expressed in the source as ‘كات مليون سانسون’ and the line ends with ‘45’; the exact monetary unit and relation between these figures are unclear, so they must not be normalized to ‘about one million’ or omitted. The speaker also mentions paying a year in advance, an F3, and the possibility of finding something reasonably good around Maramar.",
        "korean": "오랑의 임대료는 원문에서 ‘كات مليون سانسون’으로 표현되고 문장 끝에 ‘45’가 나와요. 두 수치의 정확한 화폐 단위와 관계는 불분명하므로 ‘약 100만’으로 정규화하거나 생략하지 않아요. 이어서 1년 치 선불, F3, 마라라마르 부근에서 비교적 괜찮은 집을 찾을 가능성도 언급해요.",
    },
    653: {
        "english": "Can you rent for 45 and get married? Ha—45 and get married? The monetary unit of ‘45’ is not specified, and the exact French/code-switched exchange is unclear. Rent in Oran is then given as four to five million for an F3; someone asked here said an F4 costs six million eight hundred thousand per month.",
        "korean": "45로 집을 빌리고 결혼할 수 있어요? 하하, 45로 결혼한다고요? ‘45’의 화폐 단위는 원문에 지정되어 있지 않고, 프랑스어·코드 스위칭 대화의 정확한 뜻도 불분명해요. 이어서 오랑의 F3 임대료는 400만에서 500만으로 제시되고, 여기서 물어본 사람은 F4가 한 달에 680만이라고 말했어요.",
    },
    654: {
        "english": "Someone with a low salary is described as paying ‘3 ملايين سانسو’ in rent; the amount is a roughly three-to-three-and-a-half-million range in context, while the exact monetary wording remains uncertain. That person cannot rent the place at all.",
        "korean": "급여가 적은 사람은 임대료로 ‘3 ملايين سانسو’를 내는 것으로 언급돼요. 문맥상 약 300만에서 350만대의 금액이지만 정확한 화폐 표현은 불확실해요. 그런 사람은 그 집을 전혀 빌릴 수 없어요.",
    },
    655: {
        "english": "Someone earning two million has to pay rent, support children, and cover all the necessities of life; everything cannot even be counted. Now everything is expensive, so my friend cannot live. That is why people are engaging in harraga or other irregular/unauthorized migration; it is not without reason.",
        "korean": "200만을 버는 사람은 집세와 자녀 부양비, 생활에 필요한 모든 것을 감당해야 해서 전부 셀 수도 없어요. 지금은 모든 것이 비싸서 친구가 살아갈 수 없어요. 그래서 사람들이 하라가(harraga), 즉 비정규·비인가 이주를 하는 거예요. 아무 이유 없이 그러는 것은 아니에요.",
    },
    658: {
        "english": "For two and a half or three million, the place may not be good or properly furnished; it may be damaged. The source says that it is repaired again before it is rented, but it does not establish whether the person doing the repairs is the owner, landlord, or someone else.",
        "korean": "250만이나 300만을 내도 집이 좋지 않거나 제대로 갖춰져 있지 않을 수 있고, 파손되어 있을 수도 있어요. 원문은 임대되기 전에 다시 수리한다고 말하지만, 수리하는 사람이 집주인인지 임대인인지 다른 사람인지는 확정하지 않아요.",
    },
    665: {
        "english": "The opening includes the code-switched phrase ‘جيسك ماتنو / jusqu’à maintenant’ (‘up to now’), whose exact relation to the following advice is uncertain. The speaker then says that marriage is not suitable unless one has a good job and housing that can support one, and that people should arrange a future, housing, and a stable place before thinking about marriage.",
        "korean": "도입부에는 ‘جيسك ماتنو / jusqu’à maintenant’(‘지금까지’)라는 코드 스위칭 표현이 나오며, 뒤의 조언과 정확히 어떻게 연결되는지는 불확실해요. 이어서 화자는 자신을 부양할 수 있는 좋은 직장과 집이 없으면 결혼은 적절하지 않다고 말하고, 결혼을 생각하기 전에 미래와 주거, 안정적인 거처를 마련해야 한다고 말해요.",
    },
    671: {
        "english": "Maybe I have not found a girl who suits me, or perhaps God has not written it yet. I searched and did not find one. Or perhaps I have spotted/noticed a girl from the neighborhood—the phrase مريبيري is uncertain and does not establish an engagement. God knows; I do not know.",
        "korean": "나에게 맞는 여자를 아직 찾지 못했거나 하느님이 아직 정해 주지 않으셨을지도 몰라요. 찾아봤지만 찾지 못했어요. 아니면 동네의 한 여자를 발견했거나 눈여겨본 것일 수도 있어요. ‘مريبيري’의 정확한 표현은 불확실하며 약혼을 확정하지 않아요. 하느님만 아시고, 나는 몰라요.",
    },
    674: {
        "english": "What keeps me from marrying is the lack of a job, a home, and a car. In this country many things are missing and life is expensive. It is not like Europe: Europe is described as ahead, with people living well and having their rights, whereas here they do not; the comparison remains colloquial but its direction is preserved.",
        "korean": "내가 결혼하지 못하는 이유는 직장과 집과 차가 없기 때문이에요. 이 나라에는 부족한 것이 많고 생활비가 비싸요. 유럽과는 달라요. 유럽은 더 앞서 있고 사람들이 잘 살며 자기 권리를 누리지만, 여기서는 그렇지 않다고 말해요. 구어적인 비교이지만 그 방향은 보존해요.",
    },
    675: {
        "english": "Housing? Not yet. My siblings have to marry before me; they are much older, one around thirty and one around twenty-eight, so my turn comes later. Yes, may God reward you. You can see that everyone has their own turn.",
        "korean": "집이요? 아직 없어요. 내 형제들이 나보다 먼저 결혼해야 해요. 그들은 나보다 훨씬 나이가 많아서 한 명은 서른쯤이고 다른 한 명은 스물여덟쯤이라 내 차례는 나중이에요. 네, 하느님이 보답하시길 바라요. 사람마다 자기 차례가 있다는 것을 알 수 있어요.",
    },
    677: {
        "english": "She is with Chachra. In an aggressive comic exchange, the speaker refers to making someone’s thighs blue or bruised; the exact actor and target are unclear. The line then repeats ‘Sardina, Sardina’ and ends with the unclear expression فريتابل, which is retained rather than resolved as a table or bargain.",
        "korean": "그녀는 샤슈라와 함께 있어요. 공격적인 코미디성 말싸움에서 화자는 누군가의 허벅지를 파랗게 만들거나 멍들게 한다는 말을 하지만, 정확한 행위자와 대상은 불분명해요. 이어서 ‘Sardina, Sardina’가 반복되고, ‘فريتابل’이라는 불분명한 표현으로 끝나요. 이를 상이나 거래로 확정하지 않아요.",
    },
    679: {
        "english": "I did not ask you to tell me your life; I asked whether Boulbou exists. People from France wanted me to bring them Boulbou with chermoula, not sardines. I took the sardines from you yesterday and made them into ma‘qouda (معقودة); they are still in my refrigerator.",
        "korean": "나는 네 인생을 말해 달라고 한 게 아니라 불부가 있는지 물었어요. 프랑스에서 온 사람들이 정어리가 아니라 셰르물라를 곁들인 불부를 가져다 달라고 했어요. 어제 네게서 정어리를 가져와 마‘쿠다(معقودة)로 만들었고, 아직 내 냉장고에 있어요.",
    },
    680: {
        "english": "You have a Boulbou face—go inside. I will twist you up; the phrase ‘راكلِطة ... تكرطني’ is an unclear taunt and is not resolved as ‘rocket’ or ‘blow me up.’ Mustafa? Come here, brother. This sardine seller thinks he is Arnold. The threats are comic and not resolved literally.",
        "korean": "너는 불부 같은 얼굴이야. 안으로 들어가. 너를 비틀어 버리겠다는 말이 이어지지만, ‘راكلِطة ... تكرطني’는 ‘로켓’이나 ‘나를 폭파하다’로 확정하지 않는 불분명한 조롱이에요. 무스타파? 이리 와, 형제여. 이 정어리 장수는 자신이 아널드인 줄 알아요. 위협은 코미디성 말싸움이며 문자 그대로 확정하지 않아요.",
    },
    682: {
        "english": "My friend, are you not ashamed to insult a woman? Hey, Hambouk, pretend that I defeat you—may God have mercy on your parents. Listen: the sardine-related phrase ‘براس ما سردينا ياكلها حب حب اليوم’ is retained as an unclear comic line; the actor of ياكلها and its exact target are not fixed.",
        "korean": "친구야, 여자를 욕하면서 부끄럽지도 않아요? 이봐, 함부크, 내가 너를 이기는 척해. 하느님이 네 부모님께 자비를 베푸시길 바라. 들어 봐. 정어리와 관련된 ‘براس ما سردينا ياكلها حب حب اليوم’은 불분명한 코미디성 대사로 보존하며, ‘ياكلها’의 행위자와 정확한 대상은 확정하지 않아요.",
    },
    683: {
        "english": "The line says not to embarrass the speaker in front of the woman and includes Hambouk, the sardine reference سردين, and the name Mustafa. It then threatens or describes showing who Mustafa is, shaking him, rolling him, and hitting him. The exchange is aggressive comic banter, and the exact speaker/actor boundaries remain unclear.",
        "korean": "이 대사는 그 여자 앞에서 화자를 창피하게 하지 말라고 하며, 함부크, 정어리를 뜻하는 ‘سردين’, 무스타파라는 이름을 명시적으로 포함해요. 이어서 무스타파가 어떤 사람인지 보여 주겠다며 그를 흔들고 굴리고 때리겠다는 위협이나 묘사가 나와요. 공격적인 코미디성 말싸움이며 정확한 화자와 행위자 경계는 불분명해요.",
    },
    685: {
        "english": "I am telling you: give it to her or to the feminine-marked target in the command عطيها; the exact referent is unclear. My shirt is tearing, my eyes are turning blue—God. Give it to her/that target; it will not be finished today. The physical details and target remain unclear.",
        "korean": "내가 말하잖아요. ‘عطيها’는 여성형 대상에게 ‘그녀에게/그것을 주라’고 하는 명령이며, 정확한 지시 대상은 불분명해요. 셔츠가 찢어지고 눈이 파래지는 것 같아요. 하느님. 그녀에게, 또는 그 여성형 대상에게 줘요. 오늘은 끝나지 않을 거예요. 신체 묘사와 대상은 여전히 불분명해요.",
    },
    687: {
        "english": "The phrase واحدة زوج تلاتة has the character of a one-two-three count or countdown, and طلقني means ‘let me go/release me’; neither is ‘one, two, three to go’ as a resolved event. The following Oran farewell and speaker changes remain unclear.",
        "korean": "‘واحدة زوج تلاتة’는 하나, 둘, 셋을 세는 말이나 카운트다운 성격의 표현이고, ‘طلقني’는 ‘나를 놓아줘/풀어 줘’라는 뜻이에요. 이를 실제로 한두세 명이 떠난 사건이나 ‘one, two, three to go’로 확정하지 않아요. 이어지는 오랑 작별 인사와 화자 전환은 불분명해요.",
    },
    688: {
        "english": "You mocked Mustafa and looked down on him; today I will settle things with you. You hit or treated him in the preceding comic exchange and tell the other person to go away because you have no words with them. The line ends with the cooking/pot wordplay ‘درتني في قدرة و مطبتش’ (‘you put me in a pot and I did not cook’); the exact speaker boundaries remain unclear.",
        "korean": "무스타파를 놀리고 업신여겼으니 오늘 너와 결판을 내겠다고 해요. 앞선 코미디성 대화에서 그를 때리거나 그렇게 다룬 뒤, 다른 사람에게 할 말이 없으니 가라고 말해요. 마지막에는 ‘درتني في قدرة و مطبتش’(‘나를 냄비에 넣었는데 나는 익지 않았어’)라는 요리·냄비 말장난이 나오며, 정확한 화자 경계는 불분명해요.",
    },
    689: {
        "english": "No one gets away: give him a blow in the eye, and repeat it. The line also explicitly mentions في ليستوما, referring to a body or abdominal area whose exact lexical meaning is uncertain; that stomach/body-impact layer must be retained. The aggressive line is presented as banter, not a verified instruction.",
        "korean": "아무도 빠져나가지 못해요. 그에게 눈을 한 대 때리고, 다시 반복해요. 이 대사는 ‘في ليستوما’도 명시하는데, 이는 정확한 어휘 의미는 불확실하지만 신체 또는 배 부위에 해당하는 표현이에요. 그 복부·신체 타격 층을 보존해요. 공격적인 말이지만 확인된 지시가 아니라 말싸움으로 제시돼요.",
    },
    691: {
        "english": "I am telling you: tease him. Tell me how I can take your head—your head is far from me—and pinch or grab you by the thigh; the remaining threat is unclear. The source explicitly says قرصة من فخاد, a pinch of/from the thigh, not merely an unspecified grab.",
        "korean": "그를 놀리라고 말해요. 네 머리를 어떻게 잡을지 말해 봐요. 네 머리는 나에게서 멀리 있고, 허벅지를 꼬집거나 잡겠다는 말이 이어져요. 나머지 위협은 불분명해요. 원문은 단순한 잡기가 아니라 ‘قرصة من فخاد’, 즉 허벅지를 꼬집는다는 표현을 명시해요.",
    },
    692: {
        "english": "Oh wow, you knocked me down; I am sitting here. The exact action and the comic reaction are unclear, but this canonical row contains no sardine reference, so no sardine or sardine head is added.",
        "korean": "아, 네가 나를 넘어뜨렸어요. 나는 여기 앉아 있어요. 정확한 행동과 코미디성 반응은 불분명하지만, 이 canonical 행에는 정어리 언급이 없으므로 정어리나 정어리 머리를 추가하지 않아요.",
    },
    694: {
        "english": "Until ten in the morning, the line mentions a mirror (مرايا), makeup, and styling; مرايا is not ‘a woman.’ She had not said she would come, so the speaker came to look at what she was doing, but there was nothing; even the man they were talking about was absent. The mirror/makeup scene and speaker relations remain partly unclear.",
        "korean": "아침 10시까지 이 대사는 거울(‘مرايا’), 화장, 스타일링을 언급해요. ‘مرايا’를 ‘여자’로 읽지 않아요. 그녀가 온다고 말하지 않았기 때문에 화자는 그녀가 무엇을 하는지 보러 왔지만 아무것도 없었고, 이야기하던 그 남자도 없었어요. 거울·화장 장면과 화자 관계는 일부 불분명해요.",
    },
    699: {
        "english": "Look at you, scorpion—you have made your tongue sharp. You were not like this on the first day. When you came in, I was talking to you, but now you insult me in my house; when حماك comes, I will settle it with him. حماك is a kinship term for the addressee’s in-law/father-in-law, but the exact family relation depends on the addressee and is not over-specified here.",
        "korean": "너를 봐, 전갈 같아. 혀를 날카롭게 만들었네. 첫날에는 이렇지 않았잖아. 네가 들어왔을 때는 내가 너와 이야기했지만 이제 내 집에서 나를 모욕하니, ‘حماك’이 오면 그와 해결하겠어. ‘حماك’은 상대의 시아버지·장인 등 사돈/배우자 쪽 아버지를 가리키는 친족 표현일 수 있으므로, 정확한 관계는 상대의 성별·관계에 따라 달라진다고 보존해요.",
    },
    701: {
        "english": "Man, fear God. I am talking to her and telling her to get up, take care of it, or do something. When she went out, I saw her; the remaining exchange is unclear. The source does not say that the speaker went out or that he saw an unspecified event.",
        "korean": "이봐요, 하느님을 두려워하세요. 나는 그녀에게 일어나서 처리하거나 무언가를 하라고 말하고 있어요. 그녀가 밖으로 나갔을 때 나는 그녀를 보았어요. 나머지 대화는 불분명해요. 원문은 화자가 밖으로 나갔다거나 정체를 알 수 없는 사건을 보았다고 말하지 않아요.",
    },
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def event(source_uid, field, value, generated_at):
    return {
        "source_uid": source_uid, "field": field,
        "value_hash": "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "method": "llm_source_only_enrichment_correction", "model": MODEL,
        "prompt_version": PROMPT_VERSION, "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at, "review_state": "generated",
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
    if len(CORRECTIONS) != 26 or changed_fields != 52:
        raise RuntimeError(f"correction_shape:{len(CORRECTIONS)}:{changed_fields}")
    existing = EVENTS_OUT.read_text(encoding="utf-8")
    existing_check = check_provenance_events(existing, source_uids)
    if not existing.endswith("\n") or existing_check["result"] != "PASS" or existing_check["events"] != 9420:
        raise RuntimeError(json.dumps(existing_check, ensure_ascii=False))
    generated_at = now()
    master = {row["sentno"]: row for row in after}
    new_events = [event(master[str(sentno)]["source_uid"], field, master[str(sentno)][field], generated_at) for sentno in sorted(CORRECTIONS) for field in CORRECTIONS[sentno]]
    addition = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in new_events)
    combined = existing + addition
    combined_check = check_provenance_events(combined, source_uids)
    trace = check_enrichment_provenance(after, combined)
    if combined_check["result"] != "PASS" or combined_check["events"] != 9472 or trace["result"] != "PASS":
        raise RuntimeError(json.dumps({"events": combined_check, "trace": trace}, ensure_ascii=False))
    write_tsv(ENRICHMENT_OUT, after)
    write_tsv(BATCH_OUT, corrected_batch)
    with EVENTS_OUT.open("ab") as handle:
        handle.write(addition.encode("utf-8"))
    status = json.loads(STATUS_OUT.read_text(encoding="utf-8"))
    status["updated_from_commit"] = BASE_COMMIT
    status["enrichment_correction_id"] = CORRECTION_ID
    evidence = list(status.get("evidence_files", []))
    evidence_path = "data/master/qa/madoran_enrichment_batch11_correction01_qa.json"
    status["evidence_files"] = evidence if evidence_path in evidence else evidence + [evidence_path]
    STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    history = list(qa.get("correction_history", []))
    history.append({"correction_id": CORRECTION_ID, "changed_fields": changed_fields, "state_updates": 0, "rows": len(CORRECTIONS), "provenance_events": changed_fields})
    qa.update({
        "correction_id": CORRECTION_ID, "latest_correction_id": CORRECTION_ID,
        "correction_history": history, "correction_changed_fields": changed_fields,
        "correction_state_updates": 0, "correction_rows": len(CORRECTIONS), "correction_provenance_events": changed_fields,
        "new_provenance_events": int(qa.get("new_provenance_events", 0)) + changed_fields,
        "total_provenance_events": 9472, "expected_total_provenance_events": 9472,
        "content_review_status": "pending_headgpt_correction_review", "latest_event_hash_gate": "PASS",
    })
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction_qa = {
        "result": "PASS", "batch_id": BATCH_ID, "correction_id": CORRECTION_ID, "base_commit": BASE_COMMIT,
        "corrected_rows": [str(sentno) for sentno in sorted(CORRECTIONS)], "changed_fields": changed_fields,
        "state_updates": 0, "new_provenance_events": changed_fields, "provenance_events_before": 9420,
        "provenance_events_after": 9472, "source_gate": "PASS", "morphology_gate": "BLOCKED_UPSTREAM_DEFECT",
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
