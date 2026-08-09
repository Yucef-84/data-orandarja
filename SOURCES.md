# 출처와 신뢰도

## S1 — CORVAM: Oran Arabic

- Speech Corpus of Maghrebi Varieties, University of Zaragoza
- URL: https://corvam.unizar.es/en/localities/oran/
- 강점: Oran에서 2014년 녹음, 화자가 Oran 출생·성장임을 명시, 오디오·광범위 음성전사·
  스페인어 번역·화자 메타데이터·언어학적 해설 제공.
- 사용: 최상위 기준. 직접 전사 형태는 `CORVAM_DIRECT`, 논문 기반 해설의 어휘·특징은 `ORAN_STUDY`.
- 한계: 공개 페이지의 상세 표본은 화자 1명의 농담 독백이므로 전체 도시·성별·연령을 대표하지 않음.

## S2 — Guerrero (2015)

- Jairo Guerrero, “Preliminary Notes on the Current Arabic Dialect of Oran
  (Western Algeria),” *Romano-Arabica* 15, 219–233.
- 공개 PDF: https://journals.unibuc.ro/index.php/roar/en/article/download/1945/2062
- 강점: 현대 Oran 방언의 음운·형태·어휘를 현지조사에 근거해 기술.
- 사용: CORVAM의 요약과 교차 확인하는 핵심 학술 문헌.

## S3 — Oran 부정과 ra-

- Amine Smara (2012), *Description morphosyntaxique, en diachronie et en
  synchronie, de la négation et de “ra-” dans le parler d’Oran*,
  Université Paris-Sorbonne Paris IV, 박사학위논문.
- 서지목록: CORVAM Oran 페이지 참조.
- 사용: `ma…ch` 부정과 `ra-` 현존/상태 구문의 구조적 근거.
- 한계: 현재 데이터셋에서는 공개 원문을 문장별 대조하지 못했으므로 조합 문장은 원어민 검수 대기.

## S4 — 범알제리 보조 자료

- Ayoub Kirouane, *Algerian-Darija*, Hugging Face:
  https://huggingface.co/datasets/ayoubkirouane/Algerian-Darija
- CohereLabs, *Aya Collection* Algerian Arabic split:
  https://huggingface.co/datasets/CohereLabs/aya_collection_language_split/tree/main/algerian_arabic
- 사용: 흔한 알제리 기능어·표기 변이를 대조하는 보조 자료.
- 평가: **Oran 지역 근거로는 사용 금지**. 전자는 지역 라벨이 없고 긴 소셜미디어/영상 전사,
  프랑스어·영어·다른 지역 표현·잡음이 섞여 있다. 후자도 국가 수준 언어 분할이지 Oran 코퍼스가 아니다.

## S5 — Oran 방언 연구 안내서

- CORVAM Oran bibliography:
  https://corvam.unizar.es/en/localities/oran/
- 포함 문헌: Bouhadiba(1976) *The Phonology of Oran Arabic*;
  Benallou(1992) *Dictionnaire des hispanismes dans le parler de l’Oranie*;
  Guerrero(2016) “A Phonetical Sketch…”; Zohra(2014)
  *Genealogical koineisation in Oran speech community* 등.
- 사용: 후속 확장과 원어민 검수 설계의 문헌 지도.

## S6 — MADOran V2

- Majdi Sawalha, Faisal Alshargi, Sane Yagi, Wafa Kacha, Abdallah Alshdaifat
  (2025), *Morphologically Annotated Orani-Arbaic Dialect Dataset
  (MADOran)*, Version 2.
- DOI: https://doi.org/10.17632/pgr766jbhp.2
- 원자료: https://data.mendeley.com/datasets/pgr766jbhp/2
- 규모: 1,356문장, 30,919 토큰(소개 페이지 표기 약 33,000단어),
  8,638 word types. 구어 자료 88.17%, 문어 자료 11.83%.
- 주석: 원형, 표준화 Oran 철자, MSA 대응, 접사, 어간·품사, 어근,
  형태 패턴, 수·성, 영어·프랑스어 gloss를 수동 주석.
- 라이선스: CC BY-NC 3.0.
- 사용: A1–A2 어휘 확장의 최상위 직접 코퍼스. 각 항목에 MADOran token ID와
  sentence 번호를 기록한다.
- 주의: Arabic 형태론 코퍼스이며 음성 전사 코퍼스는 아니다. Latin 발음 표기는
  CORVAM·Oran 음운 연구 및 원어민 음성 검수로 보완한다.

## 채택한 출처 우선순위

1. Oran 현지 녹음 + 전사 + 화자 메타데이터(S1)
2. 수동 주석 Oran 전용 코퍼스(S6)
3. 동료검토/학위 수준 Oran 전용 기술(S2, S3, S5)
4. Oran 지역이 명시된 사전·어휘 연구
5. 범알제리 코퍼스(S4): 오직 대조용
6. 커뮤니티 게시물·자동 생성 자료: 예문 근거로 사용하지 않음
