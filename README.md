# Oran Darija A1–A2 Safe Core Dataset

알제리 **Oran(وهران) 도시 방언** 입문자를 위한 작은 고신뢰 학습 데이터셋이다.
범알제리 Darija를 Oran 고유형으로 오인하지 않도록 각 행에 근거 수준과 검수 상태를 기록했다.

## 현재 규모

- 검토 후보 코퍼스: **888개** (`data/oran_darija_verified.tsv`)
- learner-ready export: **883개** (`data/oran_darija_learner_ready.tsv`); `disputed`·특수 구성/메타언어 항목 제외
- 수준: A1 444개, A2 444개
- 직접 근거: CORVAM Oran, Guerrero의 Oran 연구, MADOran V2
- 검증: 확장 묶음마다 오른쪽 ChatGPT가 전 행을 검사하고 수정본을 재검증
- 목적: A1–A2 입문 학습, 암기 카드, 짧은 대화·패턴 연습
- 현재 작업 상태: 888행 검토 후보본 완성; 원어민 검수 및 learner-ready A1/A2 재균형 전
- 출판·음성 녹음 전 필수 조건: Oran 출생·성장 화자 2인의 독립 검수

## 라이선스

이 저장소는 **CC BY-NC 3.0** 조건으로 공개한다. MADOran 기반 항목과 포함된
원자료의 저작자·DOI는 `LICENSE.md`와 `SOURCES.md`에 명시되어 있다. 상업적
사용은 허용되지 않으며, 재배포·수정 시 출처 표시가 필요하다.

기존 `data/oran_darija_a1a2.tsv` 128행은 초기 작업 기록이다. 엄격 지역성 조사에서
Oran 직접 근거가 부족한 행이 확인되었으므로 현재 학습·배포용 기준 파일로 사용하지 않는다.

## 파일

- `data/oran_darija_verified.tsv`: 현재 Oran 안전 핵심본
- `data/oran_darija_learner_ready.tsv`: 보류·특수 상태를 제외한 학습용 export (자동 생성)
- `data/oran_darija_a1a2.tsv`: 초기 128행 작업 기록
- `data/madoran_expansion_batch*.tsv`: MADOran 직접 근거 확장 및 검증 단위
- `data/schema.json`: 필드 정의와 허용값
- `SOURCES.md`: 출처, 신뢰도 평가, 사용 범위
- `QA.md`: 품질관리 규칙과 다음 검수 단계
- `ORAN_STRICT_AUDIT.md`: Oran 지역성 전수조사와 확장 검증 기록
- `ORAN_500_SUMMARY.md`: 최종 500개 규모·근거·학습 영역 한눈 요약
- `ORAN_A1_A2_BALANCED_SUMMARY.md`: 현재 888개 균형본 한눈 요약

## 표기

- `arabic`: 학습 친화적인 비표준 아랍 문자 표기
- `source_form`: 직접 확인 항목의 원자료 대응형. 조합/보조 항목은 비움.
- `latin`: ASCII 위주의 일관된 정규화 전사. `3=ع`, `7=ح`, `9=ق`, `gh=غ`, `kh=خ`,
  `ch=ش`, `j=ج`, `g=Oran에서 흔한 /q/의 g 실현`
- 실제 Darija 철자는 표준화되어 있지 않으므로, 하나의 표기를 “유일한 정답”으로 취급하지 않는다.
- Oran의 대표적 음운 특징인 `/q/ → /g/`도 어휘·화자에 따라 `/q/`와 교대할 수 있다.

## 근거 태그

- `CORVAM_DIRECT`: CORVAM Oran 녹음 전사/해설에서 형태가 직접 확인됨
- `MADORAN_DIRECT`: MADOran V2의 실제 token·sentence에서 형태가 직접 확인됨
- `ORAN_STUDY`: Guerrero(2015) 및 CORVAM의 Oran 기술에 근거
- `ALGERIAN_COMMON`: 널리 쓰이는 알제리형이며 Oran 고유성은 주장하지 않음
- `PEDAGOGICAL_COMPOSED`: 확인된 어휘·문법으로 만든 짧은 교육용 조합
- `CORVAM_LEMMA_FROM_ATTESTED` / `MADORAN_LEMMA_FROM_ATTESTED`: 실제 표면형에서 분리한 표제형
- `MADORAN_CONSTRUCTION_SPECIFIC`: 특정 구성에서만 확인된 의미
- `CORVAM_LOCATOR_MISMATCH`: locator와 표면형이 불일치하여 보류

## 검수 상태

- `attested`: 공개 Oran 현지 자료에서 직접 확인
- `study_backed`: Oran 연구의 기술 또는 어휘 목록으로 확인
- `native_review_required`: 자연스러운 교육용 조합이나, 공개 코퍼스의 문장 단위 직접 증거가 부족함
- `disputed`: 두 원어민 검수자가 불일치하여 보류
- `lemma_from_attested`: 원자료 표면형에서 추출한 표제형
- `metalinguistic_only` / `fragment_only` / `construction_specific`: 독립 학습 표제어로 배포하지 않는 특수 상태

`native_review_required` 행은 학습 초안으로는 사용할 수 있지만, 음성 녹음·모델 학습·출판 전에는
반드시 Oran 원어민 검수를 거쳐야 한다.

## Contextual expansion layer

Batch 01 is a separate, source-backed pilot at
data/contextual/oran_darija_contextual_batch01.tsv. It contains 96 MADOran
utterances (A1 48 / A2 48) across school/work, city/transport, body/health,
and food/shopping. The batch uses ODC IDs and references the lexical core
through lexical_refs; it does not modify the 888-row canonical TSV.

Batch 01 starts with review_status=source_verified and learner_ready=false.
Run python scripts/validate_contextual.py for the structural and source-replay
gates. GPT review of all four 24-row chunks and two independent Oran-native
reviews are required before learner release.
