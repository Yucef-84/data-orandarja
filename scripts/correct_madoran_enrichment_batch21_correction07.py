"""Apply the remaining HeadGPT-directed semantic repairs for Batch 21."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch21 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "24367ca"
BATCH_ID = "MADORAN-ENRICH-021"
CORRECTION_ID = "MADORAN-ENRICH-021-CORRECTION-07"
PROMPT_VERSION = "madoran-source-enrichment-v21-correction-7"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction07_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch21_correction07_qa.json"
PROVENANCE_BEFORE = 19004

DIRECT = {
    1291: (
        "The speaker says ‘I cannot hear your voices’ and ‘I am hungry’, asks for the opaque food surface ‘mbss’ in a bag, says ‘I am worn out/exhausted because of you’, and says they have seen no good since the day they knew the addressee. The speaker calls the opaque name-like ‘D7s’, says ‘I pulled Bousbaa for you and told you to measure it with me in the river’, says ‘you were only looking for an excuse/pretext’, and ends ‘I called you and you came running’.",
        "화자는 ‘너희 목소리가 안 들려’, ‘배고파’라고 하고 봉지에 든 불투명한 음식 표면 ‘mbss’를 달라고 해요. ‘너 때문에 지쳤어/진이 빠졌어’라고 하고 상대를 안 날부터 좋은 일을 본 적이 없다고 해요. 불투명한 이름 같은 ‘D7s’를 부르고 ‘Bousbaa를 데려와 강에서 나와 함께 재라고 했어’, ‘너는 핑계만 찾고 있었어’라고 한 뒤 ‘내가 불렀더니 네가 달려왔어’라고 끝내요.",
    ),
    1292: (
        "The speaker repeats ‘shut your mouth’, directly insults the addressee as ‘you, all by yourself, Harki/traitor’, and says ‘if you had not sent me to the opaque place “jij”, I would not be here’. The speaker says ‘you killed him’, ‘I went in the opaque/source-close “jra”’, ‘I was not the one who killed him’, and ‘I helped you measure him in the river’, leaving ‘m9ndl’ source-close.",
        "화자는 ‘입을 다물어’라고 반복하고 상대를 ‘너 혼자서, 이 하르키/배신자야’라고 직접 모욕해요. ‘네가 나를 불투명한 장소 “jij”로 보내지 않았다면 나는 여기 없었어’, ‘네가 그를 죽였어’, ‘나는 불투명한 표면 “jra”로 갔어’, ‘그를 죽인 건 내가 아니야’, ‘나는 네가 강에서 그를 재는 것을 도왔어’라고 하며 ‘m9ndl’은 원문에 가깝게 둬요.",
    ),
    1293: (
        "The speaker wants to enter alone, asks for company and a little entertainment, says ‘at least’, asks whether the addressee thought the speaker was divorced like them, and says: ‘If they do not kill me in prison, my brother will kill me the day he gets out’.",
        "화자는 혼자 들어가고 싶지만 상대에게 동행해 조금 즐겁게 해 달라고 해요. ‘적어도’라고 하고 상대가 자신을 상대처럼 이혼한 여자라고 생각했느냐고 물어요. 이어 ‘감옥에서 사람들이 나를 죽이지 않으면, 형이 출소하는 날 나를 죽일 거야’라고 해요.",
    ),
    1306: (
        "Keeping only the opaque title-like opening, the speaker says ‘what I wanted to tell you is: let us go this evening to Mustafa’s to eat/break the fast’, then adds ‘but it is still only/eight o’clock’.",
        "불투명한 제목 같은 초두만 원문에 가깝게 두고 화자는 ‘내가 하려던 말은 오늘 저녁 무스타파에게 가서 먹자/금식을 깨자는 거야’라고 해요. 이어 ‘그런데 아직/겨우 8시야’라고 덧붙여요.",
    ),
    1313: (
        "The speaker addresses father and says the addressee is wearing sneakers/tennis shoes like the person the speaker used to go out with. The speaker asks ‘what?’, says ‘why are you eating yourself?’, says someone kept calling to return, says ‘enough, it is finished’, and says ‘I said I will not work’. The final Ibiza surface and ‘go up/leave’ remain in order.",
        "화자는 아버지를 부르고 상대가 예전에 함께 다니던 사람의 것 같은 테니스화·운동화를 신고 있다고 해요. ‘뭐라고?’라고 묻고 ‘왜 너 자신을 갉아먹어?’라고 해요. 돌아오라고 계속 불렀던 일을 말하고 ‘됐어, 끝났어’, ‘나는 일하지 않겠다고 말했어’라고 한 뒤 이비자 표면과 ‘올라가/나가’로 끝내요.",
    ),
    1316: (
        "The speaker says ‘Dija, this is your mother’; says the woman looks yellow/pale; says ‘I will not live with her’; says ‘make/arrange a separate home for me’; and says ‘I am telling you this in front of her’. The addressee and the woman remain distinct.",
        "화자는 ‘디자, 이 사람이 네 엄마야’라고 말하고 그 여성이 누렇거나 창백해 보인다고 해요. ‘나는 그녀와 살지 않을 거야’, ‘내가 따로 살 집을 마련해 줘’라고 하고 ‘그녀 앞에서 지금 너한테 말하는 거야’라고 해 상대와 여성을 구분해요.",
    ),
    1317: (
        "The speaker compares the friend with a hammam scrubber/attendant, asks why the sister is photographing the speaker, then asks ‘who do you think you are, turtle?’ The speaker says ‘look at your face’, jokes ‘here is a mirror, if you still have not seen yourself’, says they will leave everyone and come photograph the listener, and asks ‘what shall I do with you?’",
        "화자는 친구를 목욕탕 때밀이·관리인에 비유하고 누이가 왜 자신을 찍는지 물어요. 이어 ‘누구라고 생각하는 거야, 이 거북아?’라고 묻고 ‘네 얼굴을 봐’, ‘아직 네 모습을 못 봤으면 여기 거울이 있어’라고 놀려요. 모두를 두고 와서 상대를 찍겠다고 한 뒤 ‘너를 어떻게 해야 하지?’라고 반문해요.",
    ),
    1318: (
        "The speaker says source-close ‘3nddha’—‘it is with her/she has it’—then asks why the sister is afraid, says ‘my brother’s wife’, and says ‘they put her in the group of divorced female teachers at the hammam’, keeping the plural actor.",
        "화자는 불투명한 대상은 보류하되 ‘3nddha’를 ‘그녀에게 있어/그녀가 갖고 있어’로 살려요. 이어 누이가 왜 무서워하는지 묻고 ‘내 형제의 아내’를 말하며 ‘그들이 그녀를 목욕탕의 이혼한 여성 교사들 그룹에 넣었어’라고 해요.",
    ),
    1320: (
        "The speaker says ‘I scrub you; you pay me by the square metre’, says the other hammam scrubber charges the speaker five thousand, then says ‘if you let/release me, I will …’, leaving the comic ‘ntrt9 fwta’ action source-close rather than inventing ‘make me burst’.",
        "화자는 ‘내가 너를 때밀어 주고 너는 제곱미터로 돈을 내’라고 해요. 다른 목욕탕 때밀이가 자신에게 5천을 받는다고 한 뒤 ‘네가 나를 놔주면 나는 …’이라고 하며 코믹한 ‘ntrt9 fwta’ 행동은 원문에 가깝게 둬요.",
    ),
    1321: (
        "The speaker asks for five thousand, says ‘I will feed you the worms I pulled out’, and says ‘you are involved/getting into it with him’ rather than ‘you brought in a small boy’. The speaker calls the boy a poor small son, asks ‘what do you mean, small?’, and exaggerates that his moustache could cover or be enough for a camel, leaving ‘3r3wr’ uncertain.",
        "화자는 5천을 요구하고 ‘내가 꺼낸 벌레들을 너에게 먹일 거야’라고 해요. ‘네가 그와 얽혀 있잖아’라고 하고 불쌍한 작은 아들을 말한 뒤 ‘뭐가 작아?’라고 반문해요. 그의 콧수염이 낙타를 덮거나 낙타에게 충분할 만큼 크다고 과장하며 ‘3r3wr’는 불확실하게 둬요.",
    ),
    1324: (
        "The speaker says the woman is gold-adorned or loaded with gold, even though her back is crooked; calls Karim to come; says it is six in the morning; says ‘hold/take your Karim’; and keeps the uncertain ‘khima ndlih lk mn alta9a’ source-close. The speaker then says ‘oh beauty, the square haircut’ and ‘I think of you continuously’; ‘swnzari’ is translated toward continuously/without stopping.",
        "화자는 그 여성이 금으로 치장했거나 금을 잔뜩 두른 듯하고 등까지 굽었다고 해요. 카림에게 오라고 부르고 오전 6시라고 하며 ‘네 카림을 잡아/데려가’라고 해요. 불확실한 ‘khima ndlih lk mn alta9a’는 원문에 가깝게 두고, 이어 ‘아, 미인이네. 사각 헤어컷’과 ‘나는 계속 너를 생각해’라고 해요. ‘swnzari’는 계속·쉼 없이의 방향으로 번역해요.",
    ),
    1325: (
        "The speaker says they are in the sky and did not manage with the others, invokes protection, asks what it is, and says the plane will not fall. The speaker recalls seeing a National Geographic report and says it made them anxious/obsessed, while keeping ‘win t7si’ source-close. ‘I know as much as you/I do not know either’, even the pilot is lost/confused, then ‘close the doors; go collect/get it, brother, go’, and do not forget the shahada.",
        "화자는 하늘에 있고 일행과 잘 맞지 않았다고 해요. 신의 보호를 빌고 그게 무엇인지 물으며 비행기는 떨어지지 않는다고 해요. 내셔널 지오그래픽 리포트를 보고 불안하거나 강박이 생겼다고 하며 ‘win t7si’는 원문에 가깝게 둬요. ‘나도 너만큼 알아/나도 몰라’, 조종사조차 헤맨다고 한 뒤 ‘문을 닫아, 가서 챙겨/모아 와, 형제야, 가’라고 하고 샤하다를 잊지 말라고 해요.",
    ),
    1333: (
        "The speaker says the source-of-tenderness goes shopping with her daughter, then addresses the female addressee: ‘it takes you a whole year to come out, bride/dressed like a bride’. The speaker says ‘I put on my shoes and leave; I do not wait’, says ‘I will wait for you until dinner and then go home’, and asks whether the listener wants people to say they do not know where she and her daughter were wandering at midnight. The speaker asks mother which item to take.",
        "화자는 ‘다정함의 샘’이 딸과 쇼핑하러 간다고 한 뒤 여성 청자에게 ‘네가 신부처럼 나오려면 1년이 걸리겠다’고 해요. ‘나는 신발을 신고 나가, 기다리지 않아’라고 하고 ‘저녁까지 널 기다렸다가 집에 갈 거야’라고 해요. 이어 ‘엄마와 딸이 한밤중에 어디를 돌아다녔는지 사람들이 모른다고 말하게 하려는 거야?’라고 묻고 엄마에게 어느 물건을 가져갈지 물어요.",
    ),
    1336: (
        "The speaker praises God and says they thought the listener had fainted or passed out, not that the listener was angry. Mother will take the item; the speaker asks its price and says five hundred thousand; compares the neighbour’s two hundred thousand without exchange; asks the son to be kind because the woman has fifty thousand; and ends ‘No, mother, I have money—shut your mouth’. The unclear ‘ftzdam’ surface remains unresolved.",
        "화자는 신을 찬양하며 상대가 화난 것이 아니라 기절한 줄 알았다고 해요. 엄마가 물건을 가져갈 거라고 하고 가격을 묻자 50만이라고 해요. 이웃의 교환 없는 20만과 비교하고 여성에게 5만이 있으니 아들에게 잘해 달라고 한 뒤 ‘아니 엄마, 나 돈 있어. 입 다물어’라고 해요. 불확실한 ‘ftzdam’ 표면은 열어 둬요.",
    ),
    1339: (
        "The speaker keeps the opening ‘darna fi al3rdat’ source-close in a gathering/invitations/feast context, says ‘come quickly’, asks for two plates of harira, reproaches the addressee about what they have done since morning, and asks ‘what are you doing?’ before telling the woman to wear a khimar and cover herself before men. The remaining ‘shashra rahm i9ar3wa’ stays opaque and the source order is preserved.",
        "화자는 초두 ‘darna fi al3rdat’를 모임·초대·잔치 맥락으로 원문에 가깝게 두고 ‘어서 와’라고 해요. 하리라 두 접시를 가져오라고 한 뒤 아침부터 무엇을 했는지 질책하고 ‘너 지금 뭐 하는 거야?’라고 물어요. 이어 여성에게 키마르를 쓰고 남자들 앞에서 몸을 가리라고 하며, 불확실한 ‘shashra rahm i9ar3wa’는 보류해 원문 순서를 지켜요.",
    ),
    1341: (
        "The speaker asks where the bathroom/toilet is, invokes ‘may God protect us’, and asks whether there is anything/water there so they can perform istinja/post-toilet cleansing. The reply says only a little came out—‘here is water’—and the speaker ends ‘thanks, my son’.",
        "화자는 화장실이 어디인지 묻고 ‘신이 우리를 지켜 주시길’이라고 해요. 이어 ‘거기 이스틴자를 할 물이나 뭔가 있어?’라고 요청·질문해요. 응답은 ‘조금밖에 안 나왔어, 여기 물’이라고 하고 화자는 ‘고마워, 아들아’라고 끝내요.",
    ),
    1344: (
        "Mother says the father came to take the listener; he said ‘come, I will take/drop you off before I get to the stadium’. The father came for the speaker now. The speaker keeps ‘go down and tell him to come back later’, says the gathering has just become lively, says the husband will not object, asks ‘what is it to you/why are you interfering?’, asks whether the listener is hinting that the speaker should leave, and ends ‘I will stay here; make me a bed, I am sleeping over’.",
        "엄마는 아버지가 상대를 데리러 왔다고 하고, 아버지가 ‘와, 내가 경기장에 도착하기 전에 너를 데려다줄게’라고 했다고 전해요. 아버지가 지금 자신을 데리러 왔다고 하고, ‘내려가서 나중에 다시 오라고 해’라는 지시를 보존해요. 모임이 이제 막 재미있어졌고 남편은 반대하지 않을 거라고 한 뒤 ‘그게 너랑 무슨 상관이야, 왜 끼어들어?’라고 묻고 ‘내가 가라고 눈치 주는 거야?’라고 해요. ‘난 여기 있을 테니 잘 자리 펴 줘, 자고 갈 거야’로 마무리해요.",
    ),
}

_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
CORRECTIONS = {}
for sentno, (english, korean) in DIRECT.items():
    surface = _batch_rows[sentno]["latin"]
    CORRECTIONS[sentno] = {
        "english": f"{english} Canonical surface sequence: `{surface}`.",
        "korean": f"{korean} canonical 표면 순서: `{surface}`.",
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
        "draft": sum(r["enrichment_state"] == "draft" for r in rows),
        "flagged": sum(r["enrichment_state"] == "flagged" for r in rows),
        "not_started": sum(r["enrichment_state"] == "not_started" for r in rows),
    }
    batch_counts = {
        "draft": sum(r["enrichment_state"] == "draft" for r in batch_rows),
        "flagged": sum(r["enrichment_state"] == "flagged" for r in batch_rows),
    }
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    qa["correction_state_updates"] = 0
    if qa.get("correction_history"):
        qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 0
    correction["correction_state_updates"] = 0
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
