"""Apply the fourth HeadGPT-directed source-close correction for MADOran Batch 20."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch20 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "4df10bd"
BATCH_ID = "MADORAN-ENRICH-020"
CORRECTION_ID = "MADORAN-ENRICH-020-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v20-correction-4"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch20_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch20_correction04_qa.json"
PROVENANCE_BEFORE = 17806

CORRECTIONS = {
    1222: {
        "english": "The speaker says Oran has a great deal of talk and much beautiful talk: when you speak about it, you feel you are speaking about a civilization and a big city, not a village, while keeping the source-close surface ‘si malwghwa’. The speaker says that they do not mean anything by saying this, but mean that everyone living in Oran is Oranian and deserves to live in Oran, and says ‘ma 3ndnash brani’ (‘we have no outsider’). They say ‘mr7ba b tout le monde’ (‘welcome everyone’), ‘mr7ba bli jana w jab m3ah w mam ma jabsh m3ah’ (welcome to whoever came, brought someone with him, and even did not bring someone with him), ‘y a pas de problème’ (‘there is no problem’), and ‘vive Oran’ (‘long live Oran’). They say ‘asm7wli ana ma ghadish nhdr hdra alli maknsh’ (sorry, I will not say words that are not there) and ‘ana nhdr lk sha sra’ (I will tell you what happened), without forcing a good-or-not-good judgment. They end this turn with ‘ana n9wlk sha kan kain w ant allh ishl 3lik’ (I tell you what was there, and may God make things go well for you).",
        "korean": "화자는 오랑에 큰 이야기가 많고 아름다운 이야기도 많아서, 오랑에 대해 말하면 마을이 아니라 문명과 큰 도시에 대해 말하는 느낌이 든다고 해요. 이때 원문의 ‘si malwghwa’ 표면도 그대로 보존해요. 화자는 이렇게 말해도 아무 뜻을 강요하는 것이 아니라, 오랑에 사는 사람은 모두 오랑 사람이고 오랑에 살 자격이 있으며 ‘ma 3ndnash brani’(외부인은 없어요)라고 말해요. 이어 ‘mr7ba b tout le monde’(모두 환영해요), ‘mr7ba bli jana w jab m3ah w mam ma jabsh m3ah’(온 사람과 누군가를 데리고 온 사람, 아무도 데리고 오지 않은 사람 모두를 환영해요), ‘y a pas de problème’(문제없어요), ‘vive Oran’(오랑 만세)이라고 해요. 또 ‘asm7wli ana ma ghadish nhdr hdra alli maknsh’(미안하지만 없는 말은 하지 않을게요), ‘ana nhdr lk sha sra’(무슨 일이 있었는지 말할게요)라고 하며 좋다·좋지 않다는 판단을 강요하지 않아요. 마지막에는 ‘ana n9wlk sha kan kain w ant allh ishl 3lik’(있었던 일을 말할게요. 신의 일이 잘 되길 바라요)라는 turn을 보존해요.",
    },
    1229: {
        "english": "The speaker tells people not to shout and says ‘ma t3rfsh z3a9a’ (‘you do not know shouting’). They ask, ‘why did you betray me?’ and give the answer ‘bash ntlbwa drahm 3lik’—to ask for money on or over you, keeping ‘3lik’ source-close rather than changing it to ‘from you’. The final response is a separate affirmative turn, ‘ah s7a hada makan’, kept source-close as ‘ah, yes, that’s it/that’s what it is’, not as ‘that is not the case’.",
        "korean": "화자는 사람들에게 소리치지 말라고 하며 ‘ma t3rfsh z3a9a’(너는 소리치는 것을 몰라)라고 말해요. 이어 ‘왜 나를 배신했어?’라고 묻고 ‘bash ntlbwa drahm 3lik’(너에게 걸거나 너를 두고 돈을 요구하려고)이라는 답을 말해요. 여기서 ‘3lik’의 방향은 ‘너에게서’라고 바꾸지 않고 원문에 가깝게 보존해요. 마지막의 별도 응답 turn ‘ah s7a hada makan’은 ‘아, 그래, 그게 다야/그렇구나’에 가까운 긍정 응답으로 보존하며 ‘그렇지 않아’로 반전하지 않아요.",
    },
    1244: {
        "english": "The speaker complains that the soup is salty and that no chickpeas were put in it. Then it says ‘saii nadt tl9mli 3jwz’ as a source-close feeding turn, and ‘wldi jib li mra 3mrlha frijidarw tiblk sha rak baghi’: ‘my son, bring me a woman—keep the surface “3mrlha frijidarw”—so she cooks for you what you want’, without changing the surface into a fixed actor or tense. It keeps ‘mama t9sf w la tbali’ as an opaque source-close clause. It then says ‘adrb mr9a w la tsa3fni’ and preserves ‘tsa3fni’ without deciding whether it means help, accompany, or something else, followed by ‘rw7 jib nakws mn 3nd 9dirwa’ so the speaker and listener can share the opaque food surface ‘nakos’.",
        "korean": "화자는 국물이 짜고 그 안에 병아리콩을 넣지 않았다고 말해요. 이어 ‘saii nadt tl9mli 3jwz’라는 먹이는 turn을 원문에 가깝게 보존하고, ‘wldi jib li mra 3mrlha frijidarw tiblk sha rak baghi’라는 절에서 ‘3mrlha frijidarw’ 표면을 특정 행위자나 시제로 바꾸지 않고 ‘아들아, 원문의 “3mrlha frijidarw”를 가진 여자를 데려와 네가 원하는 것을 요리하게 해’라는 식으로 보존해요. ‘mama t9sf w la tbali’도 불투명한 원문에 가까운 절로 남겨요. 이어 ‘adrb mr9a w la tsa3fni’에서 ‘tsa3fni’가 돕다·동행하다·다른 뜻인지 확정하지 않고 표면을 보존하며, ‘rw7 jib nakws mn 3nd 9dirwa’라고 해 화자와 청자가 불투명한 음식 표면 ‘nakos’를 나누도록 해요.",
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
