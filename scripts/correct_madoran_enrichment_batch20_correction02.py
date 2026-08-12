"""Apply the second HeadGPT-directed source-close correction for MADOran Batch 20."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch20 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "54f98a0"
BATCH_ID = "MADORAN-ENRICH-020"
CORRECTION_ID = "MADORAN-ENRICH-020-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v20-correction-2"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch20_correction02_qa.json"
PROVENANCE_BEFORE = 17754

CORRECTIONS = {
    1217: {
        "english": "The source presents Oran as a premier city with Ottoman architecture and includes the complete source-close surface ‘wzin Bastos’ as a known reference, without deciding whether it names a person, building, or other thing. It then says that when you want to talk about Oran, speak freely.",
        "korean": "원문은 오랑을 오스만 건축이 있는 뛰어난 도시로 제시하고 알려진 지칭인 ‘wzin Bastos’라는 전체 표면을 보존해요. 이것이 인물·건물·다른 대상을 가리키는지는 확정하지 않아요. 이어 오랑에 대해 말하고 싶으면 자유롭게 말하라고 해요.",
    },
    1222: {
        "english": "The speaker says Oran contains a great deal of beautiful talk and makes one feel that one is discussing a civilization and a large city, not a village. They welcome everyone who lives in Oran and everyone who arrived: ‘ma 3ndnash brani’ (we have no outsider), ‘mr7ba b tout le monde’ (welcome everyone), ‘y a pas de problème’ (there is no problem), and ‘vive Oran’ (long live Oran). They say they will tell what happened rather than inventing what is absent or forcing a good-or-bad judgment.",
        "korean": "화자는 오랑에는 크고 아름다운 이야기가 많아 문명과 큰 도시를 말하는 느낌이 들며 작은 마을을 말하는 것이 아니라고 해요. 오랑에 사는 사람과 찾아온 사람을 모두 환영하며 ‘ma 3ndnash brani’(외부인은 없어요), ‘mr7ba b tout le monde’(모두 환영해요), ‘y a pas de problème’(문제없어요), ‘vive Oran’(오랑 만세)이라는 절을 말해요. 없는 말을 만들거나 좋다·나쁘다를 억지로 판단하지 않고 일어난 일을 말하겠다고 해요.",
    },
    1231: {
        "english": "The speaker says that their sister Chahinaz thinks the speaker is good at nothing—not cooking and not cleaning. They recall being mocked after cleaning the house with a face tissue and preserve the source chain ‘nakl bzaf’ (I eat a lot), ‘ndr b ghir mima’, ‘nhrs’, and ‘sha n9wlk’ without replacing the latter surfaces with a vague joke.",
        "korean": "화자는 여동생 샤히나즈가 자신을 요리도 청소도 못하고 아무것도 잘하지 못하는 사람으로 생각한다고 말해요. 얼굴 닦는 티슈로 집을 청소하다가 놀림받은 일을 떠올리고, ‘nakl bzaf’(많이 먹어요), ‘ndr b ghir mima’, ‘nhrs’, ‘sha n9wlk’라는 원문 연쇄를 마지막의 모호한 농담으로 바꾸지 않고 보존해요.",
    },
    1235: {
        "topic": "opaque_complaint_about_distress",
    },
    1238: {
        "english": "The speaker says Aicha has arrived and is teasing them, says a brother has gone to the army and that the clothes are tight, and asks whether these are Nesrine’s trousers and why they are not being worn. The speaker then says ‘ia 7mir flkhdwd’ (you donkey with the cheeks), ‘bikatshw’ (Pikachu), ‘3lik al7md 3ris’ (praise be, you are a groom), ‘khtk wjdt 9blk’ (your sister got ready before you), and ‘rjal t3 akhr zman’ (men of the last age), preserving each turn rather than a noun-list summary.",
        "korean": "화자는 아이샤가 와서 자신을 놀린다고 하고, 형제가 군대에 갔으며 옷이 꽉 끼었다고 말해요. 이것이 네스린의 바지인지 왜 입지 않았는지 묻고, ‘ia 7mir flkhdwd’(볼이 큰 당나귀야), ‘bikatshw’(피카츄), ‘3lik al7md 3ris’(하느님께 감사하게도 신랑이구나), ‘khtk wjdt 9blk’(네 누이가 너보다 먼저 준비했어), ‘rjal t3 akhr zman’(요즘 시대의 남자들)이라는 각 turn을 보존해요.",
    },
    1240: {
        "english": "The speaker greets the woman, asks how she is, and says they are coming and will not stay long. They say she looked like a respectable girl who had suffered a curse, say they do not know what she liked about the listener, and complain that the mixed colors hurt their eyes like a rainbow. They end with the source-close line ‘hahw wjhi ala l9iti rajl’ rather than reducing it to a generic face-and-man joke.",
        "korean": "화자는 여성에게 인사하고 잘 지내는지 물으며 곧 가고 오래 머물지 않겠다고 해요. 여성이 점잖은 사람처럼 보이지만 불운한 일을 당한 듯하다고 말하고, 그 여성이 상대의 무엇을 좋아했는지 모르겠다고 해요. 섞어 놓은 색이 무지개 같아 눈이 아프다고 불평한 뒤 ‘hahw wjhi ala l9iti rajl’이라는 원문 문구를 일반적인 얼굴·남자 농담으로 줄이지 않고 끝까지 보존해요.",
    },
    1244: {
        "english": "The speaker complains that the soup is salty and has no chickpeas. An older woman asks her son to bring a woman who will fill the refrigerator and cook what he wants, and the source then says ‘w la tsa3fni’—a separate help-or-accompaniment clause that is kept rather than omitted. The speaker asks the listener to get the opaque food surface ‘nakos’ from Qadri so they can share it; it is not fixed as nachos.",
        "korean": "화자는 국물이 짜고 병아리콩이 없다고 불평해요. 나이 든 여성이 아들에게 냉장고를 채우고 원하는 음식을 해 줄 여자를 데려오라고 한 뒤, 원문에는 ‘w la tsa3fni’라는 도움이나 동행에 관한 별도 절이 나오며 이를 생략하지 않아요. 화자는 카드리에게서 불투명한 음식 표면 ‘nakos’를 사 와 함께 먹자고 하고 이를 나초로 확정하지 않아요.",
        "topic": "opaque_food_request_in_family_scene",
    },
    1247: {
        "english": "The speaker says that if they were not dieting, they would be hungry enough to dip bread with the others. They explicitly say ‘jw3twni’ (you made me hungry) and ‘jibwa’ (bring it), retain the opaque phrase ‘almut raha ghir arfd arfd’ and source surface ‘bz’, and say that the others drive them crazy by talking only about ‘les jeux’.",
        "korean": "화자는 다이어트 중이 아니라면 일행과 빵을 찍어 먹을 만큼 배고프다고 해요. ‘jw3twni’(너희가 나를 배고프게 했어)와 ‘jibwa’(가져와)를 명시하고, 불투명한 ‘almut raha ghir arfd arfd’와 원문의 ‘bz’를 보존해요. 일행이 ‘les jeux’ 이야기만 해서 자신을 미치게 한다고 말해요.",
    },
    1259: {
        "english": "The speaker says that he will pass to all of them, not only to his wife. They tell the others to follow because there are five in their team. They must score in this goal, but the speaker then says this is their own goal and they will score against themselves. The final exchange asks whether the listener is the speaker’s father or the speaker is the listener’s father; no opposing-player role is added.",
        "korean": "화자는 그가 아내에게만 패스하지 않고 모두에게 패스할 것이라고 해요. 자기 팀은 다섯 명이니 따라오라고 하고, 이 골에 넣어야 한다고 말한 뒤 자기 골대라서 자책골을 넣게 될 것이라고 농담해요. 마지막에는 상대가 자신의 아버지인지 자신이 상대의 아버지인지 묻고, 원문에 없는 상대 선수 역할은 추가하지 않아요.",
    },
    1270: {
        "english": "The speaker says they were walking peacefully when a female beggar approached and asked for money without greeting. They gave her ten thousand as charity, then saw her spit on or in the speaker’s face and turn toward the speaker, saying that she was asking for ten thousand. The speaker says they flew at her by the hair, then jokes to the doctor that if she is ill, the speaker is even more ill.",
        "korean": "화자는 평화롭게 걷다가 한 여성 구걸꾼이 인사도 없이 돈을 요구해 만을 자선으로 주었다고 해요. 이어 그 여성이 화자의 얼굴에 침을 뱉거나 얼굴을 향해 침을 뱉고 자신에게 돌아서서 만을 달라고 했다고 말해요. 화자는 그 여성의 머리카락을 잡고 달려들었다고 한 뒤, 의사에게 여성이 아프다면 자신은 더 아프다고 농담해요.",
    },
    1274: {
        "english": "The speaker says ‘Astaghfirullah’ and jokes that people eat very well there. If they eat well, the speaker will stay there alone; they have not left home or gone to the sea that year. They ask why, during the break, they should be placed with the madman from earlier, who might slap them; ‘9bila’ is not converted into a tribal identity.",
        "korean": "화자는 ‘아스타그피룰라’라고 말하며 그곳에서는 사람들이 아주 잘 먹는다고 농담해요. 잘 먹여 준다면 그곳에 혼자 있겠다고 하며 올해 집 밖이나 바다에 나가지 못했다고 해요. 휴식 시간에 자신을 때릴 수도 있는 조금 전의 미친 사람과 함께 두는 이유가 무엇인지 묻고, ‘9bila’를 부족 출신이라는 정체성으로 바꾸지 않아요.",
    },
    1277: {
        "english": "The speaker addresses the listener with the source-close phrase ‘ma nti 7altlha 3inin’ while commenting on how the woman is talking with the speaker. The gaze or eye-opening relation between the listener and woman is kept in that surface, and the line ends incompletely at ‘khatrsh’ (‘because’); no beach or travel context is added.",
        "korean": "화자는 여성이 자신과 어떻게 이야기하는지 말하면서 상대에게 ‘ma nti 7altlha 3inin’이라는 원문 표현으로 말을 걸어요. 상대와 여성 사이의 시선이나 눈을 뜨게 하는 관계는 그 표면 안에 보존하고, 줄은 ‘khatrsh’(‘왜냐하면’)에서 불완전하게 끝내며 해변이나 여행 맥락을 추가하지 않아요.",
        "domain": "daily_life",
        "topic": "incomplete_comment_about_a_companion",
    },
    1278: {
        "english": "The speaker says it is time to leave and asks how the woman will swim, offering to twist or float in Bourabah and cry in a way that will help her. After the offer, the source has the explicit vocative ‘bwia nta!’ (‘Dad, you!’), which is retained before the remaining joke.",
        "korean": "화자는 이제 떠나자고 하며 여성이 어떻게 수영할지 묻고, 부라바에서 몸을 비틀거나 떠 있으면서 울어 도와주겠다고 해요. 그 제안 뒤에 원문에는 ‘bwia nta!’(‘아빠, 당신이야!’)라는 명시적 호격이 나오며, 나머지 농담 앞에 이를 보존해요.",
    },
    1279: {
        "english": "The speaker tells the others to look and says ‘3hd’ as a source-close surface, then says ‘ma tsktwa’—do not stay silent. They say they will remove their veil and gather a judge from Fez who cannot get them up, tell the others to go to their own beach, retain the opaque ‘dra w msasik’, and request the 2021 rai recording by Mamidou for the road.",
        "korean": "화자는 일행에게 보라고 하며 ‘3hd’라는 원문 표면을 말하고, 이어 ‘ma tsktwa’, 즉 조용히 있지 말라고 해요. 머리 스카프를 벗고 자신을 일으킬 수 없는 페스의 판사를 모아 오겠다고 농담하며, 일행은 자기들 해변으로 가라고 해요. 불투명한 ‘dra w msasik’를 보존하고 길에서 들을 마미두의 2021년 라이 음악을 요청해요.",
    },
}


def apply():
    engine.BASE_COMMIT = BASE_COMMIT
    engine.BATCH_ID = BATCH_ID
    engine.CORRECTION_ID = CORRECTION_ID
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.BATCH_OUT = BATCH_OUT
    engine.BATCH_QA_OUT = BATCH_QA_OUT
    engine.CORRECTION_QA_OUT = CORRECTION_QA_OUT
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.PROVENANCE_BEFORE = PROVENANCE_BEFORE
    engine.CORRECTIONS = CORRECTIONS
    result = engine.apply()

    rows = read_tsv(ENRICHMENT_OUT)
    batch_rows = read_tsv(BATCH_OUT)
    counts = {
        "draft": sum(row["enrichment_state"] == "draft" for row in rows),
        "flagged": sum(row["enrichment_state"] == "flagged" for row in rows),
        "not_started": sum(row["enrichment_state"] == "not_started" for row in rows),
    }
    batch_counts = {
        "draft": sum(row["enrichment_state"] == "draft" for row in batch_rows),
        "flagged": sum(row["enrichment_state"] == "flagged" for row in batch_rows),
    }
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 0
    correction["batch_artifact_sync_state_updates"] = 0
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 0, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
