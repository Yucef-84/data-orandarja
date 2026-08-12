"""Apply the remaining HeadGPT-directed semantic repairs for Batch 22."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch22 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "8c637ec"
BATCH_ID = "MADORAN-ENRICH-022"
CORRECTION_ID = "MADORAN-ENRICH-022-CORRECTION-01"
PROMPT_VERSION = "madoran-source-enrichment-v22-correction-1"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_correction01_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch22_correction01_qa.json"
PROVENANCE_BEFORE = 19182

CORRECTIONS = {
    1350: {
        "english": "The speaker exchanges peace greetings with a doctor, says ‘whenever you enter, you wink at me’, and asks why the doctor did not return the speaker’s wink. The final relation is kept source-close as the opaque surface ‘tna9rfia’, without assigning it a definite meaning.",
        "korean": "화자는 의사와 평안 인사를 주고받고 ‘당신은 들어올 때마다 나에게 윙크해요’라고 해요. 이어 왜 자신의 윙크에 답하지 않았느냐고 묻고, 마지막 관계 표현 ‘tna9rfia’는 뜻을 확정하지 않고 불투명한 표면으로 보존해요.",
    },
    1352: {
        "english": "A receptionist tells the madam to go ahead and says she will come. The speaker says ‘only I and a female patient will enter’; an opaque ‘ba’ expression is kept source-close, followed by the concern that he may again shut the door in the speaker’s face and the question whether the listener would feel sorry if he stayed home today. The speaker asks ‘Madam, do you want to go in? Really, today?’, advises her not to see him because he is not like before, leaves ‘ta7wlh’ opaque, and ends by telling the sister simply to make an appointment.",
        "korean": "접수자는 부인에게 들어가도 된다고 하고 자신도 가겠다고 해요. 화자는 ‘나와 여성 환자만 들어갈 거야’라고 말하고, 불투명한 ‘ba’ 표현은 원문에 가깝게 둬요. 이어 그가 다시 자신의 얼굴 앞에서 문을 닫을 수 있다는 걱정과 ‘그가 오늘 집에 있으면 나를 안쓰럽게 여기지 않겠느냐’는 질문이 나와요. 화자는 ‘부인, 들어가고 싶어요? 정말 오늘?’이라고 묻고, 그가 예전 같지 않으니 진료받으러 가지 말라고 조언하며 ‘ta7wlh’는 불투명하게 둔 뒤 누이에게 그냥 예약을 잡으라고 해요.",
    },
    1355: {
        "english": "The speaker gives the source-close protective warning, says ‘this woman could take a man from his mother’s belly/womb’, and says ‘she wanted to go to my husband’. The idiomatic bodily image and exact actor relation remain source-close rather than being fixed beyond the source.",
        "korean": "화자는 원문에 가까운 보호 경고를 하고 ‘이 여자는 남자를 그의 어머니 배/태중에서 데려갈 정도야’라고 해요. 이어 ‘그 여자는 내 남편에게 가고 싶어 했어’라고 하며, 관용적인 신체 이미지와 정확한 행위자 관계는 원문을 넘어 확정하지 않고 보류해요.",
    },
}

_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
for sentno, fields in CORRECTIONS.items():
    surface = _batch_rows[sentno]["latin"]
    fields["english"] += f" Canonical surface sequence: `{surface}`."
    fields["korean"] += f" canonical 표면 순서: `{surface}`."


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
        "draft": sum(r["enrichment_state"] == "draft" for r in rows),
        "flagged": sum(r["enrichment_state"] == "flagged" for r in rows),
        "not_started": sum(r["enrichment_state"] == "not_started" for r in rows),
    }
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = sum(r["enrichment_state"] == "draft" for r in batch_rows)
    qa["flagged_rows"] = sum(r["enrichment_state"] == "flagged" for r in batch_rows)
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["draft_rows"] = qa["draft_rows"]
    correction["flagged_rows"] = qa["flagged_rows"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"draft_rows": qa["draft_rows"], "flagged_rows": qa["flagged_rows"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
