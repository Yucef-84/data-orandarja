"""Build source-only MADOran enrichment Batch 22 for Sentno 1345..1356."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import build_madoran_enrichment_batch10 as engine
from scripts.build_madoran_enrichment_scaffold import ROOT

BATCH_ID = "MADORAN-ENRICH-022"
BASE_COMMIT = "d8534e7"
PROMPT_VERSION = "madoran-source-enrichment-v22"
TARGET_START = 1345
TARGET_END = 1356
BATCH_OUT = ROOT / "data/master/enrichment/batches/batch22_sentno_1345_1356.tsv"
MANIFEST_OUT = ROOT / "data/master/enrichment/batches/batch22_manifest.json"
QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch22_generation_qa.json"


def r(english, korean, domain, topic, genre="conversation", speech="description",
      register="colloquial", context="high", flags="source_ambiguity",
      state="flagged", cefr="B1", score=50):
    normalized_flags = "|".join(sorted(filter(None, flags.split("|"))))
    return engine.item(english, korean, cefr, score, domain, topic, genre, speech, register, context, normalized_flags, state)


RAW = {
    1345: r("The speaker says the food is not simply at home, tells the listener to go to their mother and bring the opaque surface ‘rwa’, and asks the mother to prepare a little raisins and a piece of meat on a plate.", "화자는 음식이 단순히 집에 있는 것이 아니라고 하고 상대에게 엄마에게 가서 불투명한 표면 ‘rwa’를 가져오라고 해요. 엄마에게 건포도 조금과 고기 한 덩이를 접시에 마련해 달라고 해요.", "food", "asking_for_raisins_and_meat", "conversation", "request", "colloquial", "high", "source_ambiguity", "flagged", "B1", 52),
    1346: r("The speaker tells the sister that she ate all the meat for them and still wants more, then addresses ‘Yachicha’ and jokes that the listener envied the speaker over the meat.", "화자는 누이에게 우리 몫의 고기를 다 먹고도 더 원하느냐고 해요. 이어 ‘야시샤’를 부르며 상대가 그 고기 때문에 자신을 질투했다고 농담해요.", "food", "teasing_about_eating_all_the_meat", "joke", "complaint", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged", "B1", 50),
    1347: r("The speaker jokes: ‘If your wife were your secretary.’ The comparison is short and context-dependent.", "화자는 ‘네 아내가 네 비서라면’이라고 농담해요. 짧고 맥락 의존적인 비교예요.", "work", "joking_about_a_wife_as_a_secretary", "joke", "opinion", "colloquial", "high", "source_ambiguity", "flagged", "A2", 28),
    1348: r("A caller greets the medical office of the speaker’s husband and Dr Ghandessi. The caller wants to bring their sister in to see Dr Ghandessi, learns that he is not there today but will be there tomorrow if desired, and asks why and where he is.", "화자는 남편과 간드세시 의사의 메디컬 사무실에 전화해 인사해요. 누이를 간드세시 의사에게 진료받게 데려가고 싶다고 하고, 의사가 오늘은 없고 원하면 내일 온다는 말을 들은 뒤 왜 그런지, 의사가 어디 있는지 물어요.", "health", "calling_a_doctors_office_for_a_sister", "conversation", "question", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged", "C1", 78),
    1349: r("The speaker asks what the listener is getting involved in, says the listener has access because it is open, and offers to give the address of a house, telling the listener to inspect it and finish the matter.", "화자는 상대가 무슨 일에 끼어드는지 묻고, 상대에게 열려 있으니 들어갈 수 있다고 해요. 집 주소를 알려 주겠다고 하며 가서 살펴보고 일을 끝내라고 해요.", "housing", "giving_a_house_address", "conversation", "warning", "colloquial", "high", "source_ambiguity", "flagged", "B1", 52),
    1350: r("The speaker exchanges peace greetings with a doctor, says the doctor usually winks at the speaker wherever he goes, and teases him for not returning a wink because he is annoyed with the speaker.", "화자는 의사와 평안 인사를 주고받고, 의사가 어디를 가든 평소 자신에게 윙크한다고 해요. 이번에는 왜 윙크를 돌려주지 않았느냐며 자신 때문에 귀찮아한다고 농담해요.", "health", "teasing_a_doctor_about_winking", "conversation", "complaint", "colloquial", "medium", "code_switching|source_ambiguity", "flagged", "B1", 54),
    1351: r("The speaker says that if the listener is ashamed of the speaker, they should fire them, then asks to leave that talk. They request today’s files because they work for the listener, greet the doctor in French, and asks whether they are not late.", "화자는 상대가 자신을 부끄러워한다면 해고하라고 하고 그런 이야기는 그만두자고 해요. 자신이 상대를 위해 일하고 있으니 오늘 서류를 가져다 달라고 하며 의사에게 프랑스어로 인사하고 자신이 늦지 않았는지 물어요.", "work", "requesting_work_files_from_a_doctor", "conversation", "request", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged", "B2", 66),
    1352: r("A receptionist tells the madam to go ahead and says she will come. Only the receptionist and the patient will enter; an opaque ‘ba’ expression is kept source-close. The caller asks whether the doctor is coming today, receives advice not to go to him because he is not as before, and is told simply to make an appointment.", "접수자는 부인에게 들어가도 된다고 하고 자신도 가겠다고 해요. 접수자와 환자만 들어갈 것이며 불투명한 ‘ba’ 표현은 원문에 가깝게 둬요. 오늘 의사가 오는지 묻자, 예전 같지 않으니 그에게 가지 말라는 조언을 듣고 그냥 진료 예약을 하라는 말을 들어요.", "health", "making_a_doctors_appointment", "conversation", "request", "mixed", "high", "code_switching|long_source|source_ambiguity", "flagged", "C1", 88),
    1353: r("The speaker says: ‘Let me do it.’ The short utterance is context-dependent.", "화자는 ‘내가 할게’라고 해요. 짧고 맥락 의존적인 발화예요.", "daily_life", "offering_to_do_something", "conversation", "suggestion", "colloquial", "medium", "source_ambiguity", "flagged", "A1", 18),
    1354: r("The speaker says that yesterday a woman died inside. A man went in to perform an operation on her based on his own judgment; instead of removing her gallbladder, he removed a kidney. The speaker then offers a blessing and says goodbye to the madam.", "화자는 어제 안에서 한 여성이 죽었다고 해요. 한 남자가 자기 판단으로 그녀에게 수술을 하러 들어갔는데 담낭을 제거하는 대신 신장을 제거했다고 말해요. 이어 축복을 빌고 부인에게 작별 인사를 해요.", "health", "comic_warning_about_a_botched_surgery", "joke", "narration", "colloquial", "high", "idiom_culture|long_source|source_ambiguity", "flagged", "C1", 84),
    1355: r("The speaker gives a source-close protective warning, says that this woman takes a man from his belly or body, and says she did not want to go to the speaker’s husband; the exact bodily and actor relations remain uncertain.", "화자는 원문에 가까운 보호 경고를 하고, 이 여성이 남자를 배나 몸에서 데려간다고 말하며, 그 여성이 자신의 남편에게 가고 싶어 하지 않았다고 해요. 정확한 신체 표현과 행위자 관계는 불확실해요.", "health", "source_close_warning_about_a_woman_and_a_husband", "conversation", "warning", "colloquial", "high", "idiom_culture|source_ambiguity", "flagged", "C1", 76),
    1356: r("The speaker says they take the meat and measure the bones of young men. The short medical or body-related image is preserved directly without adding a procedure.", "화자는 고기를 가져가고 젊은 남자들의 뼈를 잰다고 해요. 짧은 의료·신체 이미지를 별도의 시술로 확대하지 않고 직접 보존해요.", "health", "measuring_young_mens_bones", "conversation", "description", "colloquial", "high", "source_ambiguity", "flagged", "B1", 48),
}


def build():
    engine.BATCH_ID = BATCH_ID
    engine.BASE_COMMIT = BASE_COMMIT
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.TARGET_START = TARGET_START
    engine.TARGET_END = TARGET_END
    engine.BATCH_OUT = BATCH_OUT
    engine.MANIFEST_OUT = MANIFEST_OUT
    engine.QA_OUT = QA_OUT
    engine.RAW = RAW
    report = engine.build()
    row_count = TARGET_END - TARGET_START + 1
    manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
    manifest["row_count"] = row_count
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["target_rows"] = row_count
    report["required_linguistic_fields"] = row_count * len(engine.EMPTY_FIELDS)
    QA_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(build(), ensure_ascii=False, indent=2))
