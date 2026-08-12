"""Apply the second HeadGPT-directed source-close correction for MADOran Batch 21."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch21 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "807d3af"
BATCH_ID = "MADORAN-ENRICH-021"
CORRECTION_ID = "MADORAN-ENRICH-021-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v21-correction-2"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch21_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch21_correction02_qa.json"
PROVENANCE_BEFORE = 18699


SEMANTIC = {
    1281: (
        "The source keeps the opening address ‘hwdwli barswl’, the restaurant and pre-sea meal turns, the speaker’s ‘n9i btata, shwi flfla’, ‘fl9i dla3’, and the closing invocation ‘7sbi allh w n3m alwkil fikm’. The chores and religious protest are separate source content, not a generic description of food preparation.",
        "원문은 ‘hwdwli barswl’ 초두 호칭, 식당과 바다에 가기 전 식사 turn, 화자의 ‘n9i btata, shwi flfla’, ‘fl9i dla3’, 마지막 ‘7sbi allh w n3m alwkil fikm’을 보존해요. 집안일과 종교적 항의는 일반적인 음식 준비 묘사로 합치지 않아요.",
    ),
    1286: (
        "The speaker says ‘la kwlni khwia’ and then ‘rah iz9i 3lia rajli hada’: the husband is shouting at or calling out against the speaker. The source does not establish jealousy.",
        "화자는 ‘la kwlni khwia’라고 한 뒤 ‘rah iz9i 3lia rajli hada’라고 해요. 남편이 화자에게 소리치거나 고함치는 방향으로 보존하고 질투라고 확정하지 않아요.",
    ),
    1292: (
        "The phrase ‘3nd jij’ is retained as an opaque place-like surface, not fixed as Jijel. The source separately keeps ‘nti ktltih’, ‘ana r7t fi jra’, ‘mashi ana alli ktlth’, and the later help with measuring the person in the river, ending with ‘kan m9ndl’. The killing actors and the later clause are not merged.",
        "‘3nd jij’은 지젤로 확정하지 않고 장소처럼 보이는 불투명한 표면으로 보존해요. ‘nti ktltih’, ‘ana r7t fi jra’, ‘mashi ana alli ktlth’, 이어서 강에서 그 사람을 재도록 도운 부분과 마지막 ‘kan m9ndl’을 각각 유지해요. 살해 행위자와 후속 절을 합치지 않아요.",
    ),
    1293: (
        "The speaker wants to enter alone, asks for accompaniment and a little entertainment, and keeps the opaque sequence ‘awmwan’ and ‘7asbtni mtlw9a kifk wa9il’ rather than turning it into a fixed claim that the speaker was released. The prison and brother turns remain in their original direction.",
        "화자는 혼자 들어가고 싶지만 동행해 잠시 즐겁게 해 달라고 해요. 불투명한 ‘awmwan’과 ‘7asbtni mtlw9a kifk wa9il’을 보존하며 화자가 풀려났다는 고정된 뜻으로 바꾸지 않아요. 감옥과 형제에 관한 turn의 방향도 원문대로 유지해요.",
    ),
    1295: (
        "The speaker asks where the listener is, repeats the opaque surfaces ‘mwjilali’ and ‘mwljilali’, says whoever wants blood should come, and keeps ‘awmbiws shaba rahi hna mn alsh3r’ without creating a named person or a definite woman.",
        "화자는 상대가 어디 있는지 묻고 불투명한 ‘mwjilali’와 ‘mwljilali’를 반복해요. 피를 원하는 사람은 오라고 하며 ‘awmbiws shaba rahi hna mn alsh3r’를 이름 있는 사람이나 특정 여성으로 창작하지 않고 보존해요.",
    ),
    1298: (
        "The turns remain separate: the request about going with Aymen to the stadium; ‘m3lblish’; ‘shwf m3 shaf srfis rani nt9hwa’; the separate question ‘m3 mn?’; and the answer ‘m3 bwk’. The source does not require the service-chief phrase to mean that the speaker is drinking coffee with him.",
        "turn을 분리해 보존해요. 아이만과 경기장에 가는 말, ‘m3lblish’, ‘shwf m3 shaf srfis rani nt9hwa’, 별도의 ‘m3 mn?’, ‘m3 bwk’라는 답을 각각 유지해요. 서비스 책임자 표현을 그와 커피를 마신다는 뜻으로 합치지 않아요.",
    ),
    1299: (
        "The source separately mentions ‘mt aimn 3ndha al79’ and the reported speech ‘9altli mk mn 3am da9iws ma d7ktsh’. Aymen’s mother and the person who told the speaker are not collapsed into one relation, and the opaque time expression stays opaque.",
        "원문은 ‘mt aimn 3ndha al79’와 ‘9altli mk mn 3am da9iws ma d7ktsh’라는 전언을 분리해요. 아이만의 어머니와 화자에게 말한 사람을 하나의 관계로 합치지 않고 불투명한 시간 표현도 그대로 둬요.",
    ),
    1301: (
        "The utterance is kept as the three source-close parts ‘t7zn 3lia’, ‘ma tzid thdr’, and ‘nwrilha’. The final verb is not supplied with an invented object such as ‘what happened’.",
        "이 발화는 ‘t7zn 3lia’, ‘ma tzid thdr’, ‘nwrilha’라는 세 부분으로 source-close하게 보존해요. 마지막 동사에 ‘무슨 일이 있었는지’ 같은 목적어를 임의로 넣지 않아요.",
    ),
    1302: (
        "The dinner turn keeps ‘sba7 alkhir jarti ki sb7ti?’ as a good-morning address to the neighbour—‘good morning, my neighbour; how did you wake up?’—not as a person named Sabah. ‘dirlk 3sha’ and ‘wli ghdwa’ remain separate instructions.",
        "저녁 대화에서 ‘sba7 alkhir jarti ki sb7ti?’는 사바라는 인물이 아니라 ‘좋은 아침, 이웃아. 잘 잤어?’라는 호칭과 질문으로 보존해요. ‘dirlk 3sha’와 ‘wli ghdwa’도 서로 다른 지시로 유지해요.",
    ),
    1307: (
        "The speaker says they are hungry, cannot concentrate, and have an empty stomach, then keeps ‘allh i7fz w istr’ as the direct protective invocation ‘may God protect and keep [us/you safe]’, followed by the direct question ‘sha tbl3’.",
        "화자는 배가 고프고 집중할 수 없으며 배가 비었다고 해요. 이어 ‘allh i7fz w istr’를 ‘신이 [우리/너를] 보호하고 지켜 주시길’이라는 직접적인 축원으로 보존하고, 뒤의 ‘sha tbl3’ 질문도 직접 유지해요.",
    ),
    1312: (
        "The line keeps the price question, ‘mliwn’, ‘ma 9ash7thash’, the direct insult ‘had shrmita’, the repeated refusals ‘ma nshrwsh, ma nlbswsh, ma nstahlwsh’, ‘ma shi bniadm 7na’, and the final wish to make a friend through a good-wish phrase. The insult is not softened into a generic comic exaggeration.",
        "이 행은 가격 질문, ‘mliwn’, ‘ma 9ash7thash’, 직접적인 욕설 ‘had shrmita’, 반복되는 ‘ma nshrwsh, ma nlbswsh, ma nstahlwsh’, ‘ma shi bniadm 7na’, 좋은 말로 친구를 만들고 싶다는 마지막 말을 보존해요. 욕설을 일반적인 코미디 과장으로 순화하지 않아요.",
    ),
    1313: (
        "The source keeps ‘tinisa’ as an opaque or footwear-like surface, not a named woman, and preserves ‘saii si fini’, ‘ma nkhdmsh 9lit’, and ‘aibiza w tl3’ as separate unresolved surfaces. The father address and the ‘takl fi rw7k’ idiom remain separate turns.",
        "원문은 ‘tinisa’를 이름 있는 여성이 아니라 불투명하거나 신발을 가리킬 수 있는 표면으로 보존해요. ‘saii si fini’, ‘ma nkhdmsh 9lit’, ‘aibiza w tl3’도 각각 미확정 표면으로 유지해요. 아버지 호칭과 ‘takl fi rw7k’ 관용 표현도 서로 다른 turn으로 둬요.",
    ),
    1316: (
        "The source keeps ‘dija hadi hi mk tban msfara’ with its relation to ‘your mother’, then ‘ma nsknsh m3aha hadi’. The imperative ‘diri dari w7di’ tells the addressee to make their own home; it is not rewritten as the speaker deciding to build a home alone.",
        "원문은 ‘dija hadi hi mk tban msfara’에서 ‘네 어머니’ 관계를 보존하고 이어 ‘ma nsknsh m3aha hadi’라고 해요. ‘diri dari w7di’는 상대에게 자기 집을 만들라고 하는 명령이지 화자가 혼자 집을 만들겠다는 결정으로 바꾸지 않아요.",
    ),
    1317: (
        "The comparison ‘kiasa t3 al7mam’ is kept in the direction of a hammam scrubber or attendant, not a generic kiosk. ‘fkrwna’ is kept as the turtle-like surface rather than frog, and the source also retains ‘shti kmartk’, the mirror turn, and ‘sha ndir bik 7mbwk’.",
        "‘kiasa t3 al7mam’은 일반적인 키오스크가 아니라 목욕탕의 때밀이 또는 관리인을 가리키는 방향으로 보존해요. ‘fkrwna’는 개구리가 아니라 거북이 쪽 표면으로 유지하고, ‘shti kmartk’, 거울 turn, ‘sha ndir bik 7mbwk’도 함께 보존해요.",
    ),
    1318: (
        "The source keeps ‘mrt khwia’ as a separate relation and the plural verb ‘darwha’ as ‘they put her’. It does not invent the brother’s wife as the sole actor who placed the sister in the group.",
        "원문은 ‘mrt khwia’라는 관계와 복수 동사 ‘darwha’(그들이 그녀를 넣었다)를 분리해요. 형제의 아내가 누이를 그룹에 넣은 유일한 행위자라고 창작하지 않아요.",
    ),
    1320: (
        "The source keeps ‘kiasa lkhra’ as another hammam scrubber or attendant, not a kiosk, and retains the final surface ‘ntrt9 fwta w ntir 3liha’ without reducing it to a generic towel threat.",
        "원문은 ‘kiasa lkhra’를 키오스크가 아니라 다른 목욕탕 때밀이 또는 관리인으로 보존하고, 마지막 ‘ntrt9 fwta w ntir 3liha’도 일반적인 수건 위협으로 줄이지 않아요.",
    ),
    1321: (
        "The speaker asks for ‘khmslaf’, keeps the extracted ‘aldwd’, and leaves ‘3r3wr shlaghmh tktfi bihm jml’ as opaque body imagery. It is not normalized into a definite claim about huge teeth.",
        "화자는 ‘khmslaf’를 요구하고 꺼낸 ‘aldwd’를 보존하며 ‘3r3wr shlaghmh tktfi bihm jml’은 불투명한 신체 이미지로 남겨요. 이를 큰 이빨이라는 확정된 주장으로 정상화하지 않아요.",
    ),
    1322: (
        "The line keeps ‘hada ... dkhlih’ with a masculine ‘him’ direction, followed by ‘ihrbli’ and the bath-women reference. It does not change the object to a feminine ‘her’.",
        "이 행은 남성 목적어 방향의 ‘hada ... dkhlih’(그를 들여보내)를 ‘ihrbli’와 목욕탕 여성들에 관한 말과 함께 보존해요. 대상을 여성 ‘그녀’로 바꾸지 않아요.",
    ),
    1323: (
        "The long exchange keeps the code-switch surface ‘awtas dw lagh: bwnjwgh’ in the direction of an air-hostess/‘bonjour’ greeting, retains ‘inwdwni drwk’, ‘ki rak baghini nsb7’, and the final ‘ala ma rahmsh iwklwk fi frwnsa 93dwa fi bladkm’. These turns are not compressed into a generic France joke.",
        "긴 대화에서 code-switch 표면 ‘awtas dw lagh: bwnjwgh’를 항공 승무원·‘bonjour’ 인사 쪽 방향으로 보존하고, ‘inwdwni drwk’, ‘ki rak baghini nsb7’, 마지막 ‘ala ma rahmsh iwklwk fi frwnsa 93dwa fi bladkm’도 유지해요. 이 turn들을 일반적인 프랑스 농담으로 줄이지 않아요.",
    ),
    1325: (
        "The speaker keeps ‘twswst’, ‘win t7si’, the plane and pilot sequence, and the final ‘ma tnsash shhada h’. Here ‘shhada’ is retained toward shahada or a religious profession of faith in the fearful flight context, not translated as a certificate.",
        "화자는 ‘twswst’, ‘win t7si’, 비행기와 조종사 sequence, 마지막 ‘ma tnsash shhada h’를 보존해요. 비행 공포 맥락의 ‘shhada’는 증명서가 아니라 샤하다 또는 신앙고백 쪽 의미로 유지해요.",
    ),
    1328: (
        "The source says the listener thinks they are in 2010, says Ziani is no longer there, and keeps ‘ma i9dwsh ijibwh il3b ghir matsh haka?’ as a wish or rhetorical question about whether they cannot bring him to play even one match. It is not an absolute impossibility statement.",
        "원문은 상대가 2010년에 있다고 생각한다고 하고 지아니는 더 이상 없다고 말해요. ‘ma i9dwsh ijibwh il3b ghir matsh haka?’는 한 경기라도 뛰게 데려올 수 없느냐는 바람이나 수사적 질문으로 보존하며 절대적인 불가능 단정으로 바꾸지 않아요.",
    ),
    1330: (
        "The source keeps the woman coming to apply kohl, ‘rah dair tatwwaj’ as the tattoo surface, and ‘tb3h’ as a separate follow/come-after command. The final command is not reduced to merely mentioning a tattoo.",
        "원문은 아이라인을 하러 오는 여성, 문신 표면인 ‘rah dair tatwwaj’, 별도의 따라가거나 따라오라는 명령 ‘tb3h’를 보존해요. 마지막 명령을 단순한 문신 언급으로 줄이지 않아요.",
    ),
    1331: (
        "The source keeps ‘li itfrj 9lb w rb’, the named or opaque surface ‘iwnja7’, the repeated ‘rw7’, and the direct insult ‘7mara’ with the blessing. It is not softened into a claim that the person’s words are merely useless.",
        "원문은 ‘li itfrj 9lb w rb’, 이름 또는 불투명 표면 ‘iwnja7’, 반복되는 ‘rw7’, 축원과 함께 나오는 직접적인 모욕 ‘7mara’를 보존해요. 이를 상대의 말이 단지 소용없다는 표현으로 순화하지 않아요.",
    ),
    1333: (
        "The long family exchange keeps ‘3am bash tkhrji li 3rwsa nti’ addressed to ‘you’, ‘ana nlbs sbati w nkhrj ma n9ar3sh’, the separate ‘khatsh ndir 3lik ntia 7ta al3sha ndkhl ldari’, the late-night ‘hi w bntha fi ns liali’ sequence, and ‘mama ndi hadi w la hadi’. It is not summarized as watching until dinner or simply making a daughter a bride.",
        "긴 가족 대화는 ‘3am bash tkhrji li 3rwsa nti’처럼 ‘너’를 향한 말, ‘ana nlbs sbati w nkhrj ma n9ar3sh’, 별도의 ‘khatsh ndir 3lik ntia 7ta al3sha ndkhl ldari’, ‘hi w bntha fi ns liali’가 들어간 밤중 sequence, ‘mama ndi hadi w la hadi’를 보존해요. 저녁까지 지켜본다거나 딸을 신부로 만든다는 요약으로 바꾸지 않아요.",
    ),
    1335: (
        "The source keeps the clothing choice, the hard-headed remark, and ‘baghi trw7i t3ri li fi aljam3a’ in the direction that the addressee wants to go and expose the speaker at the university. It does not invent another woman as the object being undressed.",
        "원문은 옷 선택과 고집이 세다는 말, ‘baghi trw7i t3ri li fi aljam3a’를 상대가 대학에서 화자를 드러내거나 노출시키려 한다는 방향으로 보존해요. 벗겨지는 다른 여성을 목적어로 창작하지 않아요.",
    ),
    1336: (
        "The price surfaces remain distinct: ‘khmsia alf 7aja’, the separate ‘200 alf’, and the later ‘50 alf’ with ‘ftzdam’. The amounts are not collapsed into one repeated fifty-thousand value, and the mother’s final turn remains separate.",
        "가격 표면은 서로 분리해요. ‘khmsia alf 7aja’, 별도의 ‘200 alf’, 뒤의 ‘50 alf’와 ‘ftzdam’을 각각 보존해요. 금액을 반복되는 동일한 5만으로 합치지 않고 엄마의 마지막 turn도 분리해요.",
    ),
    1339: (
        "The source keeps the incomplete or opaque clause ‘shashra rahm i9ar3wa’ inside the morning complaint, then separately gives the khimar and covering instruction. The clause is not deleted or normalized into a definite accusation.",
        "원문은 아침에 관한 불평 안의 불완전하거나 불투명한 절 ‘shashra rahm i9ar3wa’를 보존하고, 이어 키마르와 몸을 가리라는 지시를 별도로 둬요. 그 절을 삭제하거나 확정적인 비난으로 정상화하지 않아요.",
    ),
    1341: (
        "The speaker asks about ‘bit alma’ in the bathroom or toilet direction, keeps ‘bash nstja’ toward istinja or cleansing after using the toilet, and preserves the little-water reply and ‘s7a wldi’. The exchange is not reduced to a generic water room.",
        "화자는 ‘bit alma’를 화장실이나 변소 방향의 표현으로 묻고, ‘bash nstja’를 용변 후 세정인 이스틴자 방향으로 보존해요. 물이 조금뿐이라는 답과 ‘s7a wldi’도 유지하며 일반적인 물방으로 흐리지 않아요.",
    ),
    1344: (
        "The source keeps ‘mama baba ja idik’ as the family pickup opening, then preserves the singular offer ‘9alk arwa7i nwslk’, the opaque ‘hwd 9lh iwli mnb3d’, ‘jaini drwk had win 7lat aljma3a’, the husband turn, and ‘sha rah mdkhlk ... raki tm3nili bash nrw7 z3ma’. The final ‘frshwli rani baita’ remains the request for a bed and overnight stay; the turns are not rewritten as both parents dragging the speaker along.",
        "원문은 ‘mama baba ja idik’으로 가족이 데리러 오는 초두를 보존하고, 이어 단수 제안 ‘9alk arwa7i nwslk’, 불투명한 ‘hwd 9lh iwli mnb3d’, ‘jaini drwk had win 7lat aljma3a’, 남편 turn, ‘sha rah mdkhlk ... raki tm3nili bash nrw7 z3ma’를 유지해요. 마지막 ‘frshwli rani baita’는 잠자리를 펴 달라는 하룻밤 숙박 요청으로 두고, 부모 둘이 화자를 끌고 간다는 식으로 turn을 바꾸지 않아요.",
    ),
}


FLAG_UPDATES = {
    1281: "context_heavy|idiom_culture|long_source|source_ambiguity",
    1293: "context_heavy|cefr_boundary|idiom_culture|long_source|source_ambiguity",
    1303: "cefr_boundary|context_heavy|source_ambiguity",
    1309: "context_heavy|idiom_culture|source_ambiguity",
    1313: "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    1314: "cefr_boundary|idiom_culture|long_source",
    1316: "cefr_boundary|idiom_culture|source_ambiguity",
    1323: "cefr_boundary|code_switching|idiom_culture|long_source|source_ambiguity",
    1324: "code_switching|idiom_culture|long_source|source_ambiguity",
    1326: "idiom_culture|source_ambiguity",
    1328: "cefr_boundary|context_heavy|idiom_culture|source_ambiguity",
    1329: "cefr_boundary|context_heavy|idiom_culture|source_ambiguity",
    1330: "idiom_culture|source_ambiguity",
    1338: "cefr_boundary|context_heavy|idiom_culture|source_ambiguity",
}
STATE_UPDATES = {1307: "draft", 1314: "draft", 1318: "draft", 1326: "draft", 1330: "draft"}


_batch_rows = {int(row["sentno"]): row for row in read_tsv(BATCH_OUT)}
CORRECTIONS = {}
for sentno, (english, korean) in SEMANTIC.items():
    surface = _batch_rows[sentno]["latin"]
    CORRECTIONS[sentno] = {
        "english": f"{english} Full canonical source surface retained in transliteration: `{surface}`.",
        "korean": f"{korean} canonical 원문 표면 전체를 로마자 표기로 그대로 보존해요: `{surface}`.",
    }
for sentno, flags in FLAG_UPDATES.items():
    if flags != _batch_rows[sentno]["processing_flags"]:
        CORRECTIONS.setdefault(sentno, {})["processing_flags"] = flags
for sentno, state in STATE_UPDATES.items():
    if state != _batch_rows[sentno]["enrichment_state"]:
        CORRECTIONS.setdefault(sentno, {})["enrichment_state"] = state


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
    state_updates = sum("enrichment_state" in fields for fields in CORRECTIONS.values())
    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = counts["draft"]
    status["counts"]["enrichment_flagged_rows"] = counts["flagged"]
    status["counts"]["enrichment_not_started_rows"] = counts["not_started"]
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    qa["correction_state_updates"] = state_updates
    if qa.get("correction_history"):
        qa["correction_history"][-1]["state_updates"] = state_updates
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = state_updates
    correction["correction_state_updates"] = state_updates
    correction["batch_artifact_sync_state_updates"] = state_updates
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": state_updates, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
