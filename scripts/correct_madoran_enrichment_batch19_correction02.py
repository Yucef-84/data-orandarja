"""Apply the second HeadGPT-directed source-close corrections for MADOran Batch 19."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch19 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ENRICHMENT_OUT, ROOT, read_tsv

BASE_COMMIT = "d34c3a5"
BATCH_ID = "MADORAN-ENRICH-019"
CORRECTION_ID = "MADORAN-ENRICH-019-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v19-correction-2"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch19_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch19_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch19_correction02_qa.json"
PROVENANCE_BEFORE = 16822

CORRECTIONS = {
    1159: {
        "processing_flags": "source_ambiguity|source_corruption",
    },
    1164: {
        "english": "The speaker begins the promised explanation of Wahrani speech, says it could take six years and still not finish, and says they will be direct and shorten the video. They explain that authentic Wahrani speech is now scarce because many people brought their own dialects and languages. The speaker preserves the lexical examples: at an old shop one asked for ljafil and likhia; an old formal outfit was shda, the source gives the opaque clothing surface 7ta, and the speaker says rani drab fiha trakhia. For making someone fall, the source contrasts ndirlek krosh with the direct threat ndrbk nghashik. These surfaces and contrasts are retained without resolving 7ta as a hat.",
        "korean": "화자는 약속한 와흐라니 말씨 설명을 시작하며 6년을 말해도 끝나지 않을 수 있어서 영상을 짧게 하겠다고 해요. 많은 사람이 자기 방언과 언어를 가져오면서 진짜 와흐라니 말이 이제는 드물어졌다고 설명해요. 예전 가게에서 ljafil과 likhia를 달라고 했다는 예, 전통적인 옷 shda와 불투명한 의복 표면 7ta, 그리고 rani drab fiha trakhia라는 표현을 보존해요. 누군가를 넘어뜨릴 때 ndirlek krosh라고 하지 않고 ndrbk nghashik이라고 한다는 대비도 그대로 남겨요. 7ta를 모자로 확정하지 않아요.",
    },
    1166: {
        "english": "The speaker describes the Spanish presence in Oran as a substantial population and preserves the source-close expression lijw awrbian without deciding whether it denotes a European place, population, or urban reference. No extra European urban meaning is added.",
        "korean": "화자는 오랑에 있었던 스페인인의 존재를 상당한 인구로 설명하고 lijw awrbian이라는 원문 표면을 보존해요. 이것이 유럽인·장소·도시를 뜻하는지 확정하지 않으며 ‘유럽 도시적 존재’라는 추가 의미를 만들지 않아요.",
    },
    1172: {
        "english": "The speaker lists Spanish, French, English, German, and Portuguese in Oran, saying Spanish is found much more—bwkw blis, source-close to beaucoup plus—than the others. The comparison is retained without interpreting bwkw blis as ‘many places.’",
        "korean": "화자는 오랑에 스페인어·프랑스어·영어·독일어·포르투갈어가 모두 있다고 하며, 스페인어가 다른 언어보다 훨씬 더 많다고 bwkw blis, 즉 beaucoup plus에 가까운 원문 표면으로 말해요. bwkw blis를 ‘여러 곳’으로 해석하지 않고 비교 의미를 보존해요.",
    },
    1178: {
        "english": "The speaker says Oran has an American cemetery, describes its grass or gazon and la croix, and says it still contains di swntan mwgh, a source-close expression stating that hundreds died there. The film-like comparison and named surfaces remain, without adding graves as an alternative referent.",
        "korean": "화자는 오랑에 미국인 묘지가 있다고 하며 gazon, 즉 잔디와 la croix, 즉 십자가를 언급해요. 그곳에는 아직도 수백 명이 죽었다고 말하는 di swntan mwgh라는 원문 표현이 남아 있다고 해요. 영화에서 본 것 같다는 비교와 명시된 표면을 보존하되 무덤이라는 대체 지시대상은 추가하지 않아요.",
    },
    1182: {
        "english": "The speaker says that when the Americans entered Oran in 1942, the Americans liked or showed goodwill toward the Algerian population, while the Americans disliked the French. The actor direction is Americans toward the Algerian population; it is not changed into the Algerian population welcoming the Americans.",
        "korean": "화자는 미국인이 1942년 오랑에 들어왔을 때 미국인이 알제리 주민을 좋아하거나 호의를 보였다고 말하고, 미국인은 프랑스인을 싫어했다고 해요. 행위자 방향은 미국인에서 알제리 주민을 향하며, 알제리 주민이 미국인을 환영했다는 뜻으로 뒤집지 않아요.",
        "processing_flags": "cefr_boundary|code_switching|idiom_culture|source_ambiguity",
    },
    1184: {
        "english": "The speaker mentions the American president with the source-close composite 30 katriam and identifies Eisenhower, then says his son entered Oran swimming. The following 3la mdagh surface remains uncertain; no alternative ordinal is invented.",
        "korean": "화자는 30 katriam이라는 미국 대통령 관련 원문 복합 표면을 언급하고 아이젠하워라고 밝힌 뒤, 그의 아들이 수영해서 오랑에 들어왔다고 말해요. 뒤의 3la mdagh 표면은 불확실하게 두며 30대 또는 34대라는 대안 서수를 만들지 않아요.",
    },
    1189: {
        "english": "The speaker says that people in Oran do not use the common word for a lock but use the local form zkrwm. They explain it through the English phrase ‘close room’; the zkrwm surface and the folk-etymology claim are both retained.",
        "korean": "화자는 오랑에서는 자물쇠의 일반적인 말을 쓰지 않고 지역형 zkrwm을 쓴다고 해요. 이를 영어 구절 ‘close room’을 변형한 것으로 설명하며 zkrwm 표면과 민간어원 주장을 모두 보존해요.",
    },
    1191: {
        "processing_flags": "",
    },
    1199: {
        "english": "In a long anecdote, the speaker describes donkey carts carrying vegetables, carts blocking narrow streets, and Americans arriving in jeeps and trucks in the Arab quarters. The Americans were afraid and shouted the English command hariwb or ariiwb man, meaning ‘move quickly.’ Local speakers reduced it in stages: arii, then arii ab, then arii mah, and finally ara, which became a cart-clearing expression. The speaker ends with the source-close phrase khatini hada tnaz ibghi i9sr bzaf, preserving its leave-me-out or leave-me direction, joker or teasing surface, and ‘wants to shorten a lot’ wording rather than recasting it as a comment about shortening a joke.",
        "korean": "긴 일화에서 화자는 채소를 싣는 당나귀 수레와 수레로 막힌 좁은 길, 아랍인 구역에 지프와 트럭을 타고 온 미국인을 설명해요. 미국인들은 두려워하며 ‘빨리 움직여’라는 뜻의 영어 명령 hariwb 또는 ariiwb man을 외쳤고, 현지인들은 이를 arii, arii ab, arii mah, 마지막으로 ara로 단계적으로 줄였다고 해요. ara는 수레에게 길을 비키라고 하는 표현이 되었으며, 마지막 khatini hada tnaz ibghi i9sr bzaf라는 원문도 보존해요. 이 표현의 ‘나를 빼 줘/내버려 둬’ 방향, joker·teasing 표면, ‘많이 줄이고 싶어’라는 표현을 농담을 짧게 줄인다는 뜻으로 바꾸지 않아요.",
    },
    1208: {
        "english": "The speaker moves to the Second World War period, 1939–1945, and directly calls the French lfrwnsi bn klbwn, ‘the French, sons of dogs.’ They say the French humiliated local people and recruited poor sons of the people to fight in European wars. The source then says this happened in the First World War, preserving its internal contradiction and the direct insult rather than turning it into a neutral meta-description.",
        "korean": "화자는 1939~1945년 2차 세계대전 시기로 넘어가 프랑스인을 lfrwnsi bn klbwn, 즉 ‘프랑스인, 개들의 아들들’이라고 직접 모욕해요. 프랑스인이 현지인을 모욕하고 가난한 민중의 아들들을 모집해 유럽 전쟁에 싸우게 했다고 말해요. 이어 원문은 이것이 1차 세계대전에서 일어났다고도 하므로 내부 모순과 직접적인 모욕을 중립적인 메타 설명으로 바꾸지 않고 보존해요.",
    },
    1212: {
        "english": "The speaker describes poor people brought from the countryside, living in a small village or forest, knowing little, and owning only a few sheep that they graze, preserving the isr7 grazing action.",
        "korean": "화자는 시골에서 데려온 가난한 사람들이 작은 마을이나 숲에 살며 아무것도 잘 모르고, 양 몇 마리를 가지고 그것들을 방목하는 isr7 행위를 했다고 설명해요.",
    },
    1213: {
        "english": "In a long derogatory anecdote, the speaker says the French took a poor rural man as a soldier and brought an intermediary, a bia3 or khrda who was ma iswash, to explain French to people who did not speak it. The speaker describes and insults this intermediary as klb—‘a dog’—in the turns hw ... klb and hw hada klb; the insult is not assigned to the intermediary as something he said about the local recruits. The source also says klash rah fw9 rash, that a Kalashnikov or rifle is over his head, before the intermediary drills the recruits and orders afwnsi—move forward—while treating them like donkeys. The count ‘1, 2, harr’ is presented as the source of Harandou, which becomes a mocking label; kafi, the escape-if-clever comment, and the repeated harr command remain explicit.",
        "korean": "긴 모욕적 일화에서 화자는 프랑스인이 가난한 시골 사람을 병사로 데려가고, 프랑스어를 못하는 사람들에게 설명하게 하려고 bia3 또는 khrda, 즉 ma iswash인 중개인을 데려왔다고 해요. 화자는 이 중개인을 hw ... klb와 hw hada klb라는 turn에서 klb, 즉 ‘개’라고 직접 모욕해요. 이 모욕을 중개인이 현지 신병들에게 말했다고 뒤집지 않아요. 또한 klash rah fw9 rash, 즉 칼라시니코프나 소총이 그의 머리 위에 있다는 무장 위협 절을 보존한 뒤, 중개인이 신병들을 당나귀처럼 대하고 afwnsi, 즉 앞으로 가라고 훈련시켰다고 해요. ‘1, 2, harr’라는 구령이 하란두의 유래가 되고 놀림말이 되었다는 설명, kafi, 영리했다면 도망쳤을 것이라는 말과 반복되는 harr 구령도 명시적으로 남겨요.",
    },
    1214: {
        "english": "The speaker says the Americans' history is important and that the problem is not only the Wahrani dialect disappearing. They swear w allh al3zim, ‘by Almighty God,’ that what angers them is the false history told about Oran. They describe Oran as a great city, use the source-close whran fil kbira or 9rwfil, and say w allh ala t3if—‘by God, it is disgusting.’ They criticize old nonsense in books and television, including si fw and the emphatic kdb flkdb, lies upon lies, then ask people to tell Oran's story beautifully and accurately. The oaths and disgust are retained at full strength.",
        "korean": "화자는 미국인의 역사가 중요하며 문제는 와흐라니 방언이 사라지는 것만이 아니라고 해요. w allh al3zim, 즉 ‘전능하신 하느님께 맹세컨대’라고 맹세하며 자신을 화나게 하는 것은 오랑에 관해 전해지는 거짓 역사라고 말해요. 오랑을 큰 도시라고 하고 whran fil kbira 또는 9rwfil이라는 원문 표면을 쓰며, w allh ala t3if, 즉 ‘하느님께 맹세컨대 역겹다’고 말해요. 책과 텔레비전에 나오는 옛날의 헛소리를 si fw와 kdb flkdb, 즉 거짓말에 거짓말이라는 표현과 함께 비판하고, 오랑의 이야기를 아름답고 정확하게 말하자고 해요. 맹세와 역겨움의 강도를 약화하지 않아요.",
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
    status["enrichment_correction_id"] = CORRECTION_ID
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = batch_counts["draft"]
    qa["flagged_rows"] = batch_counts["flagged"]
    qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["draft_rows"] = batch_counts["draft"]
    correction["flagged_rows"] = batch_counts["flagged"]
    correction["state_updates"] = 0
    correction["batch_artifact_sync_state_updates"] = 0
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 0, "draft_rows": batch_counts["draft"], "flagged_rows": batch_counts["flagged"]})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
