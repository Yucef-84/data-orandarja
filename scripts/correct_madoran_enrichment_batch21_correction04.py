"""Apply the fourth source-close semantic repair for MADOran Batch 21."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch21 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "051a4ed"
BATCH_ID = "MADORAN-ENRICH-021"
CORRECTION_ID = "MADORAN-ENRICH-021-CORRECTION-04"
PROMPT_VERSION = "madoran-source-enrichment-v21-correction-4"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction04_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch21_correction04_qa.json"
PROVENANCE_BEFORE = 18777


SEMANTIC = {
    1281: ("The source-close ledger keeps ‘hwdwli barswl’; restaurant food and eating before going to the sea; ‘n9i btata, shwi flfla’; ‘fl9i dla3’; and ‘hadi m3isha 7sbi allh w n3m alwkil fikm’. The chores, watermelon surface, and religious complaint are all separate source content.", "원문에 가까운 ledger는 ‘hwdwli barswl’, 식당 음식과 바다에 가기 전 먹는 장면, ‘n9i btata, shwi flfla’, ‘fl9i dla3’, ‘hadi m3isha 7sbi allh w n3m alwkil fikm’을 모두 보존해요. 집안일·수박 표면·종교적 불평을 하나의 일반적 묘사로 합치지 않아요."),
    1282: ("The source keeps ‘rak 3a9d 3lia’ and the opaque ‘ktlni 7man’ between the sea argument and ‘drb rask m3 al7it’. Neither surface is omitted or assigned an invented name or actor.", "원문은 바다에 관한 말과 ‘drb rask m3 al7it’ 사이의 ‘rak 3a9d 3lia’와 불투명한 ‘ktlni 7man’을 보존해요. 어느 표면도 삭제하거나 이름·행위자를 발명하지 않아요."),
    1286: ("The source keeps ‘la kwlni khwia’ and ‘rah iz9i 3lia rajli hada’; the latter is a husband raising his voice or shouting against the speaker, not a jealousy claim.", "원문은 ‘la kwlni khwia’와 ‘rah iz9i 3lia rajli hada’를 보존해요. 뒤 절은 남편이 화자에게 소리치거나 고함치는 방향이지 질투라는 주장으로 창작하지 않아요."),
    1291: ("The source keeps ‘tfwa mrhwja 3la jalk’, ‘basit mn nhar alli 3rftk ma sht khir’, and the final chain ‘bsif ... nti brw7k ... 3ittlk jiti tjri’. The complaint, its cause, and the running-arrival sequence are not compressed into a generic food request.", "원문은 ‘tfwa mrhwja 3la jalk’, ‘basit mn nhar alli 3rftk ma sht khir’, 마지막 ‘bsif ... nti brw7k ... 3ittlk jiti tjri’를 보존해요. 불평·그 원인·달려온 순서를 일반적인 음식 요청으로 줄이지 않아요."),
    1292: ("‘3nd jij’ remains an opaque place-like surface. The ledger separately preserves ‘nti ktltih’, ‘ana r7t fi jra’, ‘mashi ana alli ktlth’, and ‘ana ki 3awntk t9isih flwad kan m9ndl’, including the distinct killing actors and later river clause.", "‘3nd jij’은 불투명한 장소 같은 표면으로 남겨요. ‘nti ktltih’, ‘ana r7t fi jra’, ‘mashi ana alli ktlth’, ‘ana ki 3awntk t9isih flwad kan m9ndl’을 각각 보존해 살해 행위자와 뒤의 강 절을 구분해요."),
    1293: ("The source keeps ‘awmwan’ and ‘7asbtni mtlw9a kifk wa9il’ as unresolved comparison or status surfaces, alongside the request for accompaniment and the prison/brother turns. No fixed ‘released’ or ‘divorced’ interpretation is forced.", "원문은 동행 요청과 감옥·형제 turn과 함께 ‘awmwan’, ‘7asbtni mtlw9a kifk wa9il’을 미확정 비교·상태 표면으로 보존해요. ‘풀려났다’나 ‘이혼했다’로 고정하지 않아요."),
    1295: ("The source keeps both ‘mwjilali’ and ‘mwljilali’, the blood line, and ‘awmbiws shaba rahi hna mn alsh3r’. These are opaque/name-like surfaces; no definite named woman or actor is invented.", "원문은 ‘mwjilali’와 ‘mwljilali’ 두 표면, 피에 관한 절, ‘awmbiws shaba rahi hna mn alsh3r’를 보존해요. 불투명하거나 이름 같은 표면을 특정 여성·행위자로 창작하지 않아요."),
    1298: ("The turns remain separate: ‘shwf m3 shaf srfis rani nt9hwa’, ‘m3 mn?’, and ‘m3 bwk’. The source does not collapse them into a claim that the speaker is drinking coffee with the service chief.", "turn을 분리해 ‘shwf m3 shaf srfis rani nt9hwa’, ‘m3 mn?’, ‘m3 bwk’를 보존해요. 서비스 책임자와 커피를 마신다는 하나의 주장으로 합치지 않아요."),
    1299: ("The source separates ‘mt aimn 3ndha al79’ from the reported ‘9altli mk mn 3am da9iws ma d7ktsh’. The speaker’s reported source and Aymen’s mother are not merged, and the opaque time expression remains opaque.", "원문은 ‘mt aimn 3ndha al79’와 전언 ‘9altli mk mn 3am da9iws ma d7ktsh’를 분리해요. 전언의 행위자와 아이만의 어머니를 합치지 않고 불투명한 시간 표현도 유지해요."),
    1301: ("The three source-close parts are ‘t7zn 3lia’, ‘ma tzid thdr’, and ‘nwrilha’. The final verb keeps its unresolved object; ‘what happened’ or another object is not invented.", "세 source-close 부분 ‘t7zn 3lia’, ‘ma tzid thdr’, ‘nwrilha’를 보존해요. 마지막 동사의 목적어는 미확정으로 두고 ‘무슨 일이 있었는지’ 같은 목적어를 만들지 않아요."),
    1302: ("‘sba7 alkhir jarti ki sb7ti?’ is a good-morning address and question to the neighbour, not a person named Sabah. ‘dirlk 3sha’ and ‘wli ghdwa’ remain separate instructions.", "‘sba7 alkhir jarti ki sb7ti?’는 사바라는 인물이 아니라 이웃에게 하는 좋은 아침 인사와 질문이에요. ‘dirlk 3sha’와 ‘wli ghdwa’는 별도 지시로 보존해요."),
    1306: ("The source keeps ‘almkrasha’ and ‘nrw7wa 3shia 3nd mstfa nftrwa’. ‘nftrwa’ remains a meal/iftar surface rather than being normalized specifically as eating breakfast.", "원문은 ‘almkrasha’와 ‘nrw7wa 3shia 3nd mstfa nftrwa’를 보존해요. ‘nftrwa’는 아침 식사로 특정하지 않고 식사·이프타르 표면으로 둬요."),
    1307: ("The direct protective invocation ‘allh i7fz w istr’ and the direct question ‘sha tbl3’ are retained. The invocation is not reduced to a metadata label such as ‘blessing’.", "직접적인 보호 축원 ‘allh i7fz w istr’와 질문 ‘sha tbl3’를 보존해요. 축원을 ‘blessing’이라는 메타 라벨로만 줄이지 않아요."),
    1308: ("The source keeps ‘ia m3ad’, ‘3ndk ghadi tzr9ni’, and ‘ki dair ghiar’, including the jealousy/alteration surface and its unresolved direction. It is not reduced to a generic fear of being hit.", "원문은 ‘ia m3ad’, ‘3ndk ghadi tzr9ni’, ‘ki dair ghiar’를 보존하며 질투·변화와 관련된 미확정 방향도 유지해요. 단순히 맞을까 두렵다는 말로 줄이지 않아요."),
    1309: ("The source keeps ‘fm klb’ as the direct insult or opaque insult surface, ‘brki ma t3wji fi rw7k’, and the question about ‘lisanitr’. The insult is not softened into a generic warning.", "원문은 직접 욕설 또는 불투명한 욕설 표면 ‘fm klb’, ‘brki ma t3wji fi rw7k’, ‘lisanitr’에 관한 질문을 보존해요. 욕설을 일반적인 경고로 순화하지 않아요."),
    1312: ("The direct insult ‘had shrmita’ and the refusals ‘ma nshrwsh, ma nlbswsh, ma nstahlwsh’ remain visible, followed by ‘ma shi bniadm 7na’ and the good-wish friendship line. The abusive register is not softened.", "직접 욕설 ‘had shrmita’, ‘ma nshrwsh, ma nlbswsh, ma nstahlwsh’를 보존하고 ‘ma shi bniadm 7na’와 좋은 말로 친구를 만들겠다는 절도 유지해요. 공격적 register를 순화하지 않아요."),
    1313: ("‘tinisa’ remains an opaque or footwear-like surface, not a created woman or named Tinessa. ‘saii si fini’, ‘ma nkhdmsh 9lit’, and ‘aibiza w tl3’ remain separate unresolved surfaces.", "‘tinisa’는 창작된 여성이나 Tinessa라는 이름이 아니라 불투명하거나 신발을 가리킬 수 있는 표면으로 남겨요. ‘saii si fini’, ‘ma nkhdmsh 9lit’, ‘aibiza w tl3’도 각각 미확정 표면으로 보존해요."),
    1316: ("The source keeps the ‘mk’/your-mother relation in ‘dija hadi hi mk tban msfara’ and the imperative ‘diri dari w7di’. The addressee is told to make their own home; the speaker is not made the actor who builds one alone.", "원문은 ‘dija hadi hi mk tban msfara’의 ‘mk’/네 어머니 관계와 ‘diri dari w7di’ 명령을 보존해요. 상대에게 자기 집을 만들라고 하는 말이지 화자가 혼자 집을 짓는 행위자라고 바꾸지 않아요."),
    1317: ("‘kiasa t3 al7mam’ is kept toward a hammam scrubber or attendant, ‘fkrwna’ toward the turtle-like surface, and ‘shti kmartk’, the mirror sequence, and ‘sha ndir bik 7mbwk’ remain present.", "‘kiasa t3 al7mam’은 목욕탕 때밀이·관리인 방향으로, ‘fkrwna’는 거북이 쪽 표면으로 보존해요. ‘shti kmartk’, 거울 sequence, ‘sha ndir bik 7mbwk’도 빠뜨리지 않아요."),
    1318: ("‘mrt khwia’ and the plural ‘darwha’ remain separate: the source says they put her in the group, without assigning the sole actor to the brother’s wife.", "‘mrt khwia’와 복수 동사 ‘darwha’를 분리해 보존해요. 원문은 그들이 그녀를 그룹에 넣었다는 방향이며 형제의 아내를 유일한 행위자로 만들지 않아요."),
    1320: ("‘kiasa lkhra’ remains another hammam scrubber or attendant, not a kiosk. The final ‘ntrt9 fwta w ntir 3liha’ is kept as a surface-level threat or movement, not compressed to a generic towel joke.", "‘kiasa lkhra’는 키오스크가 아니라 다른 목욕탕 때밀이·관리인으로 보존해요. 마지막 ‘ntrt9 fwta w ntir 3liha’도 표면 수준의 위협·움직임으로 유지하고 일반적인 수건 농담으로 줄이지 않아요."),
    1321: ("‘3r3wr shlaghmh tktfi bihm jml’ remains opaque body imagery. It is not translated as a definite claim about huge teeth or a fixed animal part.", "‘3r3wr shlaghmh tktfi bihm jml’은 불투명한 신체 이미지로 남겨요. 큰 이빨이나 특정 동물 신체 부위라는 확정 번역을 하지 않아요."),
    1322: ("‘hada ... dkhlih’ keeps the masculine object ‘him’, before ‘ihrbli’ and the bath-women reference. The object is not changed to feminine ‘her’.", "‘hada ... dkhlih’는 ‘그를 들여보내’라는 남성 목적어 방향을 ‘ihrbli’와 목욕탕 여성에 관한 말 앞에서 보존해요. 대상을 여성 ‘그녀’로 바꾸지 않아요."),
    1323: ("The code-switch ‘awtas dw lagh: bwnjwgh’ remains in an air-hostess/bonjour greeting direction. ‘inwdwni drwk’, ‘ki rak baghini nsb7’, and the final ‘ala ma rahmsh iwklwk fi frwnsa 93dwa fi bladkm’ are all retained.", "code-switch ‘awtas dw lagh: bwnjwgh’는 항공 승무원·bonjour 인사 방향으로 보존해요. ‘inwdwni drwk’, ‘ki rak baghini nsb7’, 마지막 ‘ala ma rahmsh iwklwk fi frwnsa 93dwa fi bladkm’도 모두 유지해요."),
    1324: ("‘lakwb kari’ remains a la-coupe-carree-like haircut or hair-surface reference, not a rented cup. ‘swnzari’ stays opaque where uncertain.", "‘lakwb kari’는 빌린 컵이 아니라 la coupe carrée 계열의 머리 모양·헤어 표면으로 보존해요. ‘swnzari’는 불확실한 표면으로 남겨요."),
    1325: ("‘twswst’, ‘win t7si’, and the final ‘ma tnsash shhada h’ remain in the plane-fear sequence. ‘shhada’ is kept toward shahada/profession of faith, not certificate.", "‘twswst’, ‘win t7si’, 마지막 ‘ma tnsash shhada h’를 비행 공포 sequence 안에서 보존해요. ‘shhada’는 증명서가 아니라 샤하다·신앙고백 방향으로 둬요."),
    1328: ("‘ma i9dwsh ijibwh il3b ghir matsh haka?’ remains a wish or rhetorical question—whether they cannot bring him to play even one match—not an absolute impossibility statement.", "‘ma i9dwsh ijibwh il3b ghir matsh haka?’는 한 경기라도 뛰게 데려올 수 없느냐는 바람·수사 질문으로 보존하고 절대적 불가능 단정으로 바꾸지 않아요."),
    1330: ("The source keeps ‘rah dair tatwwaj’ as the tattoo surface and ‘tb3h’ as a separate follow/follow-after command. It is not reduced to merely mentioning a tattoo.", "원문은 문신 표면 ‘rah dair tatwwaj’와 별도의 따라가·따라오라는 명령 ‘tb3h’를 보존해요. 문신 언급만 남기지 않아요."),
    1331: ("The direct insult ‘7mara’, the named or opaque ‘iwnja7’, and ‘li itfrj 9lb w rb’ remain visible with the blessing. The insult is not softened to ‘useless words’.", "직접 모욕 ‘7mara’, 이름 또는 불투명 표면 ‘iwnja7’, ‘li itfrj 9lb w rb’를 축원과 함께 보존해요. 욕설을 ‘소용없는 말’로 순화하지 않아요."),
    1332: ("‘mjm3a li m3 traris’ remains a source-close boys/guys or opaque group surface. It is not fixed as the insulting label ‘brats’.", "‘mjm3a li m3 traris’는 boys/guys 또는 불투명한 집단 표면으로 source-close하게 보존해요. ‘장난꾸러기들’ 같은 비하 꼬리표로 고정하지 않아요."),
    1333: ("The source keeps ‘3am bash tkhrji li 3rwsa nti’, ‘ma n9ar3sh’, ‘7ta al3sha ndkhl ldari’, and the late-night ‘hi w bntha fi ns liali’ chain. It is not summarized as simply making a daughter a bride or watching until dinner.", "원문은 ‘3am bash tkhrji li 3rwsa nti’, ‘ma n9ar3sh’, ‘7ta al3sha ndkhl ldari’, 밤중 ‘hi w bntha fi ns liali’ chain을 보존해요. 딸을 신부로 만든다거나 저녁까지 지켜본다는 단순 요약으로 바꾸지 않아요."),
    1335: ("‘baghi trw7i t3ri li fi aljam3a’ keeps the direction that the addressee goes to expose the speaker at the university. No other woman is invented as the object being undressed.", "‘baghi trw7i t3ri li fi aljam3a’는 상대가 대학에서 화자를 노출시키러 간다는 방향으로 보존해요. 벗겨지는 다른 여성을 목적어로 창작하지 않아요."),
    1336: ("The amounts stay distinct: ‘khmsia alf 7aja’, ‘200 alf’, and later ‘50 alf’ with ‘ftzdam’. They are not collapsed into one fifty-thousand amount.", "금액은 ‘khmsia alf 7aja’, ‘200 alf’, 뒤의 ‘50 alf’와 ‘ftzdam’을 각각 보존해요. 모두 하나의 5만 금액으로 합치지 않아요."),
    1339: ("The incomplete clause ‘shashra rahm i9ar3wa’ remains inside the morning complaint, separate from the khimar and covering instruction. It is not deleted or made into a definite accusation.", "불완전한 절 ‘shashra rahm i9ar3wa’를 아침 불평 안에 보존하고 키마르·몸을 가리라는 지시와 분리해요. 삭제하거나 확정적 비난으로 만들지 않아요."),
    1340: ("‘shir amn’ stays opaque or address-like, while ‘rahi iz9i 3lia’ keeps the shouting/raising-voice direction. The line also retains the neighbour’s-son address and the harira command.", "‘shir amn’은 불투명하거나 호칭 같은 표면으로 두고 ‘rahi iz9i 3lia’는 소리치거나 고함치는 방향으로 보존해요. 이웃의 아들이라는 호칭과 하리라 지시도 유지해요."),
    1341: ("‘bit alma’ remains in the bathroom/toilet direction and ‘bash nstja’ in the istinja or post-toilet cleansing direction, with the little-water reply and ‘s7a wldi’. It is not generalized to a water room.", "‘bit alma’는 화장실·변소 방향으로, ‘bash nstja’는 이스틴자·용변 후 세정 방향으로 보존하고 물이 조금뿐이라는 답과 ‘s7a wldi’도 유지해요. 일반적인 물방으로 흐리지 않아요."),
    1344: ("The source keeps the family pickup opening, singular ‘9alk arwa7i nwslk’, opaque ‘hwd 9lh iwli mnb3d’, ‘jaini drwk had win 7lat aljma3a’, the husband turn, ‘sha rah mdkhlk ... raki tm3nili bash nrw7 z3ma’, and ‘frshwli rani baita’. The turns are not rewritten as both parents dragging the speaker.", "원문은 가족이 데리러 오는 초두, 단수 ‘9alk arwa7i nwslk’, 불투명한 ‘hwd 9lh iwli mnb3d’, ‘jaini drwk had win 7lat aljma3a’, 남편 turn, ‘sha rah mdkhlk ... raki tm3nili bash nrw7 z3ma’, ‘frshwli rani baita’를 보존해요. 부모 둘이 화자를 끌고 간다는 식으로 turn을 바꾸지 않아요."),
}

_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
CORRECTIONS = {}
for sentno, (english, korean) in SEMANTIC.items():
    surface = _batch_rows[sentno]["latin"]
    CORRECTIONS[sentno] = {
        "english": f"{english} Canonical surface ledger: `{surface}`.",
        "korean": f"{korean} canonical 표면 ledger: `{surface}`.",
    }
CORRECTIONS[1330]["enrichment_state"] = "flagged"


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
    counts = {"draft": sum(r["enrichment_state"] == "draft" for r in rows), "flagged": sum(r["enrichment_state"] == "flagged" for r in rows), "not_started": sum(r["enrichment_state"] == "not_started" for r in rows)}
    batch_counts = {"draft": sum(r["enrichment_state"] == "draft" for r in batch_rows), "flagged": sum(r["enrichment_state"] == "flagged" for r in batch_rows)}
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    if qa.get("correction_history"):
        qa["correction_history"][-1]["state_updates"] = 1
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 1
    correction["correction_state_updates"] = 1
    correction["batch_artifact_sync_state_updates"] = 1
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 1, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
