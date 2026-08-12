"""Apply the third HeadGPT-directed source-close correction for MADOran Batch 20."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch20 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "4316ee1"
BATCH_ID = "MADORAN-ENRICH-020"
CORRECTION_ID = "MADORAN-ENRICH-020-CORRECTION-03"
PROMPT_VERSION = "madoran-source-enrichment-v20-correction-3"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction03_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch20_correction03_qa.json"
PROVENANCE_BEFORE = 17784

CORRECTIONS = {
    1220: {
        "english": "The speaker argues that the Spanish were not besieged in Oran: they entered and colonized it. The speaker then says that after entering, they could not continue colonizing other cities and could not advance, and presents that inability as the siege: ‘hada 7sar’ (‘this is a siege’). They stayed for three centuries, while the speaker says ‘you are besieged’; even with one of the world’s strongest Ottoman fleets, the speaker asks why Oran was not liberated.",
        "korean": "화자는 스페인인들이 오랑에서 포위된 것이 아니라 들어와 식민화했다고 주장해요. 이어 스페인인들이 다른 도시들을 계속 식민화하지 못했고 더 나아가지 못한 상태를 가리키며 ‘hada 7sar’(이것이 포위다)라고 말해요. 스페인인들은 3세기 동안 머물렀고 화자는 상대에게 포위된 상태라고 말하며, 세계 최강급 오스만 함대가 있었는데도 왜 오랑을 해방하지 못했는지 물어요.",
    },
    1222: {
        "english": "The speaker says everyone living in Oran is Oranian and deserves to live in Oran, and says ‘ma 3ndnash brani’ (‘we have no outsider’). They say ‘mr7ba b tout le monde’ (‘welcome everyone’), ‘mr7ba bli jana w jab m3ah w mam ma jabsh m3ah’ (welcome to whoever came, brought someone with him, and even did not bring someone with him), ‘y a pas de problème’ (‘there is no problem’), and ‘vive Oran’ (‘long live Oran’). They say ‘asm7wli ana ma ghadish nhdr hdra alli maknsh’ (sorry, I will not say words that are not there), ‘ana nhdr lk sha sra’ (I will tell you what happened), and repeat that they are not imposing a good-or-not-good judgment, ending with ‘sha kan kain’ and ‘allah ishl 3lik’.",
        "korean": "화자는 오랑에 사는 사람은 모두 오랑 사람이고 오랑에 살 자격이 있으며 ‘ma 3ndnash brani’(외부인은 없어요)라고 말해요. 이어 ‘mr7ba b tout le monde’(모두 환영해요), ‘mr7ba bli jana w jab m3ah w mam ma jabsh m3ah’(온 사람과 누군가를 데리고 온 사람, 아무도 데리고 오지 않은 사람 모두를 환영해요), ‘y a pas de problème’(문제없어요), ‘vive Oran’(오랑 만세)이라고 말해요. 또 ‘asm7wli ana ma ghadish nhdr hdra alli maknsh’(미안하지만 없는 말은 하지 않을게요), ‘ana nhdr lk sha sra’(무슨 일이 있었는지 말할게요)라고 하며 좋다·좋지 않다는 판단을 강요하지 않고 ‘sha kan kain’(있었던 일)과 ‘allah ishl 3lik’(신의 일이 잘 되길)로 이어 가요.",
    },
    1229: {
        "english": "The speaker tells people not to shout and says ‘ma t3rfsh z3a9a’ (‘you do not know shouting’). They ask, ‘why did you betray me?’ and give the answer ‘bash ntlbwa drahm 3lik’—to ask for money on or over you, keeping ‘3lik’ source-close rather than changing it to ‘from you’. They end with ‘hada makan’ (‘that is not the case’).",
        "korean": "화자는 사람들에게 소리치지 말라고 하며 ‘ma t3rfsh z3a9a’(너는 소리치는 것을 몰라)라고 말해요. 이어 ‘왜 나를 배신했어?’라고 묻고 ‘bash ntlbwa drahm 3lik’(너에게 걸거나 너를 두고 돈을 요구하려고)이라는 답을 말해요. 여기서 ‘3lik’의 방향은 ‘너에게서’라고 바꾸지 않고 원문에 가깝게 보존하며, 마지막에는 ‘hada makan’(그렇지 않아)이라고 해요.",
    },
    1244: {
        "english": "The source says the soup is salty and that no chickpeas were put in it. Then it says ‘saii nadt tl9mli 3jwz’ (an old woman got up to feed me) and ‘wldi jib li mra 3mrlha frijidarw tiblk sha rak baghi’ (my son, bring me a woman who has filled her refrigerator so she can cook what you want). It keeps ‘mama t9sf w la tbali’ as an opaque source-close clause. It then says ‘adrb mr9a w la tsa3fni’ (stir the soup and do not help or accompany me), followed by ‘rw7 jib nakws mn 3nd 9dirwa’ (go get the opaque surface ‘nakos’ from Qadri) so the speaker and listener can share it.",
        "korean": "원문은 국물이 짜고 그 안에 병아리콩을 넣지 않았다고 말해요. 이어 ‘saii nadt tl9mli 3jwz’(한 노년 여성이 나를 먹이려고 일어났어요), ‘wldi jib li mra 3mrlha frijidarw tiblk sha rak baghi’(아들아, 냉장고를 채운 여자를 데려와서 네가 원하는 것을 요리하게 해)라는 절이 나와요. ‘mama t9sf w la tbali’는 불투명한 원문에 가까운 절로 보존해요. 이어 ‘adrb mr9a w la tsa3fni’(국을 저어, 나를 돕거나 함께하지 마)라고 하고, ‘rw7 jib nakws mn 3nd 9dirwa’(카드리에게서 불투명한 표면 ‘nakos’를 가져와)라고 하며 화자와 청자가 나누자고 해요.",
    },
    1247: {
        "english": "The speaker says that if they were not dieting, they would be hungry enough to dip bread with the others. They say ‘jw3twni’ (‘you made me hungry’) and ‘wla jibwa nghms m3akm shwia’ (‘or bring it; I will dip a little with you’), retain the opaque phrase ‘almut raha ghir arfd arfd’ and source surface ‘bz’, then say ‘mzia jm3twni m3akm fi had tabla’ (‘it is good that you gathered me with you at this table’) and ‘ma nbghish njm3 m3 bz fi tabla sghira’ (‘I do not want to gather with bz at a small table’). They say the others drive them crazy by talking only about ‘les jeux’.",
        "korean": "화자는 다이어트 중이 아니라면 일행과 빵을 찍어 먹을 만큼 배고플 거라고 해요. ‘jw3twni’(너희가 나를 배고프게 했어)와 ‘wla jibwa nghms m3akm shwia’(아니면 그것을 가져와, 너희와 조금 찍어 먹을게)를 말하고, 불투명한 ‘almut raha ghir arfd arfd’와 원문의 ‘bz’를 보존해요. 이어 ‘mzia jm3twni m3akm fi had tabla’(너희가 나를 이 식탁에 함께 모아 줘서 좋아)와 ‘ma nbghish njm3 m3 bz fi tabla sghira’(작은 식탁에서 bz와 함께 모이고 싶지 않아)라고 말해요. 일행이 ‘les jeux’ 이야기만 해서 자신을 미치게 한다고 해요.",
    },
    1250: {
        "processing_flags": "source_ambiguity",
    },
    1252: {
        "english": "The speaker says she had not intended to marry until finishing her studies, but marriage is written for her and she does not want to give it up. Another woman says ‘just be quiet, my daughter’; when she heard they were coming, he had dealt with everything, with the source-close surfaces ‘rdd yb9s’ and ‘7itan 7km’ retained. The rugs or carpets (‘tabiat’) were taken to the speaker’s sister, with ‘rghwahm’ kept as a source surface; only ‘jhaz’, the household setup or equipment, remained and had not been prepared.",
        "korean": "화자는 공부를 마칠 때까지 결혼할 생각이 없었지만 자신에게 정해진 결혼을 놓치고 싶지 않다고 말해요. 다른 여성이 ‘그냥 조용히 해, 딸아’라고 하고, 그들이 온다는 말을 들었을 때 그가 모든 일을 처리했다는 내용과 함께 원문의 ‘rdd yb9s’, ‘7itan 7km’ 표면을 보존해요. ‘tabiat’은 화자의 누이에게 가져간 양탄자나 카펫으로 보수적으로 처리하고 ‘rghwahm’은 원문 표면으로 남겨요. ‘jhaz’, 즉 살림 준비물이나 장비만 아직 마련되지 않았다고 해요.",
    },
    1255: {
        "english": "The speaker says there is only a little, says they have been seen, and tells the woman to go to her room. The source says ‘7latlk 93da’, a source-close phrase addressed to ‘you’ about a pleasant sitting or seat; it is not recast as the woman making a pleasant sitting for herself. The listener is told to leave him alone and not bother him, and the poor man is gathered with them.",
        "korean": "화자는 얼마 남지 않았다고 말하고 사람들이 보았으니 여성에게 방으로 가라고 해요. 원문은 ‘7latlk 93da’라고 하며, 이는 ‘너에게’ 향한 즐거운 자리나 앉을 곳에 관한 원문에 가까운 표현이에요. 이를 여성이 자신을 위해 즐거운 자리를 만들었다고 바꾸지 않아요. 상대에게 그 남자를 내버려 두고 방해하지 말라고 하며, 그 불쌍한 사람이 자신들과 함께 모여 있다고 말해요.",
    },
    1266: {
        "english": "One speaker asks whether the other will play goalkeeper in a djellaba. The answer says, ‘No, I will play in shorts’; the following ‘baghi rajli itl9ni’ is directed to the interlocutor as a provocative question—‘Do you want my husband to divorce me because I play in shorts?’—not as the speaker’s statement that she wants a divorce. Their father is then addressed about dividing socks among the players; the speaker says they will do it and become angry or make a mess. Another turn mentions a fruit-mixed yogurt, followed by ‘Run, you will see.’",
        "korean": "한 화자는 상대가 젤라바를 입고 골키퍼를 할 것이냐고 물어요. 상대는 ‘아니, 반바지를 입고 경기할 거야’라고 답하고, 이어지는 ‘baghi rajli itl9ni’는 화자가 이혼을 원한다고 진술하는 말이 아니라 ‘내가 반바지를 입고 경기해서 남편이 나와 이혼하기를 바라?’라고 상대에게 묻는 도발적인 질문이에요. 이어 아버지에게 경기 참가자들에게 양말을 나누라고 말하고, 자신은 그렇게 하며 화를 내거나 엉망으로 만들겠다고 해요. 과일이 섞인 요거트에 관한 turn과 ‘뛰어, 보면 알아’라는 말도 보존해요.",
    },
    1277: {
        "processing_flags": "idiom_culture|source_corruption",
    },
    1278: {
        "english": "The speaker says it is time to leave and asks how the woman will swim, offering to twist or float in Bourabah and cry in a way that will help her. The source then ends with the explicit vocative ‘bwia nta!’ (‘Dad, you!’); no continuation is supplied after this vocative.",
        "korean": "화자는 이제 떠나자고 하며 여성이 어떻게 수영할지 묻고, 부라바에서 몸을 비틀거나 떠 있으면서 울어 도와주겠다고 해요. 원문은 이어 명시적 호격 ‘bwia nta!’(‘아빠, 너야!’)로 끝나며, 그 뒤의 continuation은 추가하지 않아요.",
    },
    1279: {
        "english": "The speaker tells the others to look and says ‘3hd’ as a source-close surface, then says ‘ma tsktwa’—do not stay silent. They say they will remove their veil and gather a judge from Fez who cannot get them up, and tell the others to go alone to their own beach. They say ‘ma tnswlish dra w msasik bash n9il’: the surface ‘dra w msasik’ and the purpose clause ‘bash n9il’ (‘so I can take a nap’) are both retained without forcing a meaning for the opaque surface. They then request the 2021 rai recording by Mamidou for the road.",
        "korean": "화자는 일행에게 보라고 하며 ‘3hd’라는 원문 표면을 말하고, 이어 ‘ma tsktwa’, 즉 조용히 있지 말라고 해요. 머리 스카프를 벗고 자신을 일으킬 수 없는 페스의 판사를 모아 오겠다고 하며, 일행에게 자기들 해변으로 혼자 가라고 해요. ‘ma tnswlish dra w msasik bash n9il’에서 불투명한 ‘dra w msasik’ 표면과 ‘bash n9il’(낮잠을 자려고)이라는 목적절을 모두 보존하고 임의의 의미를 부여하지 않아요. 이어 길에서 들을 마미두의 2021년 라이 음악을 요청해요.",
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
