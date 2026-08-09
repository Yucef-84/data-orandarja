"""Apply high-confidence, locator-specific fixes from the independent GPT review.

This deliberately does not delete rows: deleting the entries flagged for later
editorial review would break the published 888-row A1/A2 balance.  It changes
only fields for which the review supplied an explicit replacement value.
"""

from __future__ import annotations

import csv
from pathlib import Path


DATASET = Path(__file__).parents[1] / "data" / "oran_darija_verified.tsv"

# id -> explicit field replacements.  Keep source_form and source_locator intact
# unless the review explicitly identifies them as wrong; they are evidence records.
FIXES: dict[str, dict[str, str]] = {
    "OD-0339": {"topic": "family", "ko": "네 아버지", "en": "your father", "marker_type": "none", "note": "sentence 773에서 بونا(our father)와 병렬인 2SG 소유형; bank가 아님"},
    "OD-0368": {"topic": "metalinguistic", "ko": "화자가 'ugly'에서 왔다고 설명하는 형태", "en": "form the speaker claims derives from 'ugly'", "marker_type": "metalinguistic", "oran_marker": "metalinguistic_mention", "evidence": "MADORAN_METALINGUISTIC", "status": "metalinguistic_only", "note": "실제 외모 평가 용례가 아니라 화자의 민간어원 설명"},
    "OD-0374": {"ko": "그녀는 한다; 지낸다", "en": "she does; gets by", "note": "sentence 22의 كي دير: 3FS 문맥; 명령형 해석 제거"},
    "OD-0392": {"ko": "더 간다; 계속 간다", "en": "go farther; continue", "note": "sentence 12에서는 이동·진행 의미"},
    "OD-0397": {"ko": "너는 들어간다(남성)", "en": "you enter (m.sg.)", "note": "sentence 534의 직접 호칭 خويا로 2MS"},
    "OD-0405": {"ko": "원하는(여성형); 나는 원한다(여성 화자)", "en": "wanting (f.sg.); I want (female speaker)", "note": "능동분사는 성을 표시하지만 해당 locator의 화자는 1SG 여성"},
    "OD-0524": {"topic": "function", "ko": "아무튼; 어쨌든", "en": "anyway; so", "marker_type": "discourse", "note": "sentence 236의 담화표지 용법"},
    "OD-0586": {"ko": "나는 너희에게 준다", "en": "I give you (pl.)", "note": "1SG n- + 2PL object; sentence 1174 단일 화자"},
    "OD-0591": {"ko": "우리는 그녀를 닮았다; 닮는다", "en": "we resemble her", "note": "لها는 비교 대상; 별도 'it' 목적어 없음"},
    "OD-0592": {"ko": "그들은 그들을 ~라고 부른다", "en": "they call/name them", "note": "sentence 1186의 명명 용법; 전화 의미 아님"},
    "OD-0596": {"ko": "그들은 그를 ~라고 부른다", "en": "they call him (a name/label)", "note": "sentence 1192의 naming predicate"},
    "OD-0601": {"ko": "그들은 계속 ~했다", "en": "they kept on; continued", "note": "aspectual قعدوا + IV; literal stayed 아님"},
    "OD-0602": {"ko": "없다; 없었다", "en": "there is/was not", "note": "비인칭 존재 부정 표현; 3MS 인칭 번역 제거"},
    "OD-0610": {"ko": "하느님이 너를 지켜 주시길", "en": "may God protect you", "note": "ربي يحفظك 축원구"},
    "OD-0616": {"ko": "하느님이 그에게 자비를 베푸시길", "en": "may God have mercy on him", "note": "الله يرحمه 축원구"},
    "OD-0619": {"ko": "하느님이 너를 지켜 주시길", "en": "may God keep/bless you", "note": "الله يخليك의 공손·축원 용법"},
    "OD-0636": {"ko": "너희가 그 대가를 치른다", "en": "you will pay for it", "note": "idiomatic تخلصوها"},
    "OD-0641": {"ko": "나는 너를 위해 신부를 구한다; 혼담을 넣는다", "en": "I seek/propose a bride for you", "note": "어머니가 아들에게 말하는 혼담 문맥"},
    "OD-0645": {"oran_marker": "lemma_from_attested", "evidence": "MADORAN_LEMMA_FROM_ATTESTED", "status": "lemma_from_attested", "note": "exact_surface=ندريلك; normalized_lemma=نديرلك; 원문 철자 전도 교정"},
    "OD-0648": {"ko": "그들은 할 수 없었다", "en": "they could not", "note": "sentence 1220의 주제는 Spaniards; 3PL 문맥"},
    "OD-0688": {"ko": "그것을 그대로 둬", "en": "leave it", "note": "2MS imperative + 3MS object -ه"},
    "OD-0699": {"ko": "나에게 말해 줘", "note": "명령형 2MS + 1SG 목적어"},
    "OD-0701": {"ko": "그녀는 너를 위해 요리한다", "en": "she cooks for you", "note": "habitual descriptive context"},
    "OD-0702": {"topic": "function", "ko": "나와 무슨 상관이야?", "en": "what does that have to do with me?", "note": "fixed expression شا دخلني فـ"},
    "OD-0703": {"ko": "너 자신을 위해", "en": "for yourself", "note": "locator-specific reflexive use"},
    "OD-0717": {"ko": "나는 계속한다; 더 한다", "en": "I continue; go on", "note": "نحبس ولا نزيد = stop or continue"},
    "OD-0727": {"ko": "익숙한; ~하는 데 익숙하다", "en": "used to; accustomed", "note": "مداري نقارع وحدي = 혼자 기다리는 데 익숙하다"},
    "OD-0729": {"topic": "metalinguistic", "ko": "인샬라 표현의 일부", "en": "part of the expression inshallah", "marker_type": "fragment", "oran_marker": "fragment_only", "evidence": "MADORAN_FRAGMENT_ONLY", "status": "fragment_only", "note": "إن شاء الله 전체 표현의 일부; 독립 어휘항목 아님"},
    "OD-0731": {"ko": "혼자", "note": "exact surface=وحده"},
    "OD-0755": {"ko": "하느님이 복 주시길", "en": "may God bless", "note": "الله يبارك 축원구"},
    "OD-0756": {"ko": "그는 집을 빌린다", "en": "he rents a place", "note": "tenant sense"},
    "OD-0760": {"ko": "하느님이 보호하시길", "en": "may God protect", "note": "الله يحفظ 축원구"},
    "OD-0762": {"ko": "여러분 어떻게 지내요?", "note": "exact surface=كيراكم"},
    "OD-0781": {"ko": "~의 이름으로", "en": "in the name (of)", "note": "بسم الله 구성요소"},
    "OD-0793": {"ko": "나는 집을 빌린다", "en": "I rent a place", "note": "tenant sense"},
    "OD-0802": {"ko": "누구에게?; 누구를 위해?", "en": "to whom?; for whom?", "note": "لـ + من"},
    "OD-0812": {"topic": "metalinguistic", "ko": "몸을 던지다; 뛰어내리다", "en": "throw oneself; jump", "marker_type": "construction", "oran_marker": "construction_specific", "evidence": "MADORAN_CONSTRUCTION_SPECIFIC", "status": "construction_specific", "note": "يقيس روحه 구성에서만 확인된 의미; 일반 'measure' 항목으로 쓰지 않음"},
    "OD-0813": {"ko": "우리 둥지; 우리 집", "en": "our nest; our home", "note": "عش + نا; 'our life' 분석 제거"},
    "OD-0819": {"ko": "하느님이 자비를 베푸시길", "en": "may God have mercy", "note": "الله يرحم 축원"},
    "OD-0822": {"ko": "그는 구한다; 구해 준다", "en": "he saves; rescues", "note": "locator-specific sense"},
    "OD-0824": {"ko": "너는 촬영한다; 찍는다", "en": "you film; shoot", "note": "sentence 280에서는 filming sense"},
    "OD-0834": {"ko": "그래서; 그 때문에", "note": "exact surface=علابيها"},
    "OD-0846": {"ko": "가 버려!", "en": "go away!", "note": "exact surface=طيري"},
    "OD-0848": {"ko": "혼자", "note": "exact surface=وحدك"},
    "OD-0852": {"note": "비동사적 필요 표현 khas-na; -na=1PL; 완료형(PV) 아님"},
    "OD-0854": {"ko": "결혼에 대해; 결혼을", "en": "about marriage", "note": "f-/PREP + zwaj; locator는 wedding venue가 아님"},
    "OD-0858": {"ko": "안녕히 가세요; 잘 가", "note": "exact surface=بسلامة"},
    "OD-0859": {"ko": "나는 너와 합의한다; 이야기를 풀어 간다", "en": "I settle things / come to an understanding with you", "note": "reciprocal نتفاهم معاك"},
    "OD-0861": {"ko": "나는 들러본다; 살펴보러 간다", "en": "I look in on; check on", "note": "نطل عليها construction"},
    "OD-0875": {"ko": "우리 자신", "note": "exact surface=رواحنا"},
    "OD-0877": {"ko": "하느님이 보답하시길", "en": "may God reward/repay", "note": "الله يخلف 축원구"},
    "OD-0878": {"ko": "하느님이 지켜 주시길", "en": "may God protect/keep safe", "note": "الله يحفظ و يستر 축원"},
    "OD-0884": {"ko": "프로젝트로; 사업과 관련해", "en": "with/by a project", "note": "exact surface includes b-/PREP; bare مشروع 아님"},
    "OD-0885": {"ko": "그는 어울려 논다; 시간을 보낸다", "en": "he hangs out; spends time", "note": "locator socializing sense"},
    "OD-0890": {"ko": "흔들리다; 달랑거리다", "en": "sway; dangle", "note": "sentence 612의 주체는 skirt/bag; 사람의 stagger 아님"},
    "OD-0900": {"ko": "나는 찾았다; 발견했다", "en": "I found", "note": "-t는 중의적이나 sentence 218 문맥은 1SG"},
    "OD-0909": {"ko": "필요하다; 부족하다", "en": "need; lack", "note": "비인칭 ma khas X ghir Y; 3MS 해석 제거"},
    "OD-0956": {"en": "person; human being"},
    "OD-0958": {"en": "person; human being"},
    "OD-0960": {"ko": "나는 할 수 있다", "en": "I can", "note": "sentence 566의 현재 가능"},
    "OD-0971": {"ko": "그는 길렀다; 길게 했다", "en": "he lengthened; let grow", "note": "direct object=ضفاره(nails); transitive sense"},
}


def main() -> None:
    with DATASET.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames
        assert fields is not None
        rows = list(reader)

    ids = {row["id"] for row in rows}
    missing = sorted(set(FIXES) - ids)
    if missing:
        raise SystemExit(f"IDs not found: {', '.join(missing)}")

    changed = 0
    for row in rows:
        updates = FIXES.get(row["id"])
        if updates:
            row.update(updates)
            changed += 1

    temporary = DATASET.with_suffix(".tsv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(DATASET)
    print(f"Updated {changed} rows in {DATASET}")


if __name__ == "__main__":
    main()
