# QA 규칙

## 이미 적용한 규칙

1. `Oran` 지역성이 명시되지 않은 자료는 `ALGERIAN_COMMON` 이상으로 올리지 않는다.
2. 현지 녹음에서 직접 확인된 형태와 연구의 요약 어휘를 구분한다.
3. 연구에서 확인된 낱말을 조합한 새 문장은 `PEDAGOGICAL_COMPOSED`와
   `native_review_required`를 동시에 부여한다.
4. `/q/ → /g/`를 기계적으로 모든 단어에 적용하지 않는다. 연구가 기술한 교대와
   실제 어휘별 관습을 우선한다.
5. 프랑스어·스페인어 차용은 초급 필수성이 낮거나 사회적 사용 범위가 좁으면 핵심 세트에서 제외한다.
6. 욕설, 성적 표현, 농담의 펀치라인, 종교·정치 선동, 개인정보가 있는 소셜미디어 문장은 제외한다.
7. 한국어/영어 번역은 직역보다 초급 상황의 기능 의미를 우선하되, 문화적 직역이 필요한 경우 note에 남긴다.
8. 철자 변이는 오류로 단정하지 않고 대표 표기 하나와 전사 하나를 제공한다.

## 릴리스 전 원어민 검수

- Oran 출생·성장 화자 2명(가능하면 성별·연령대 다르게)이 각 행을 독립 평가:
  `natural / understandable_but_unusual / not_oran / wrong`.
- 두 화자가 모두 `natural` 또는 한 명 `natural` + 한 명 `understandable_but_unusual`인 행만 유지.
- 불일치 행은 즉시 `disputed`로 보류하고 제3의 Oran 화자 또는 문헌 근거로 판정.
- 각 음성은 한 화자에게서만 녹음하지 말고 최소 2개 화자 변이를 보존.
- 발음·표기·번역·CEFR 난이도를 별도 열로 검수하고 변경 이력을 남긴다.

## 자동 검사

- ID 중복, 빈 필드, 허용되지 않은 enum 값 검사
- `PEDAGOGICAL_COMPOSED`인데 `native_review_required`가 아닌 행 탐지
- `ALGERIAN_COMMON`인데 Oran 고유라고 주장하는 note 탐지
- 아랍 문자/Latin/번역 중 하나가 누락된 행 탐지
- 학습·검증 분할 시 같은 어근·동일 패턴의 근접 문장을 서로 다른 분할로 누출하지 않기
- `scripts/build_balanced_dataset.ps1`은 보류·특수 상태(`disputed`, `native_review_required`,
  `metalinguistic_only`, `fragment_only`, `construction_specific`)를
  `data/oran_darija_learner_ready.tsv`에서 제외한다.
- learner-ready export는 현재 883행이며, A1/A2 444/444 균형을 회복하기 전에는 최종 배포본으로 표시하지 않는다.
- 500행 레거시 입력과 388행 추가 파일을 통한 재빌드는 교정 전 값을 되살릴 수 있으므로 릴리스 입력으로 금지한다.

## Contextual expansion QA

Contextual rows are stored separately from the lexical core. Batch 01 must
retain the canonical SHA-256, contain exactly 96 rows with A1/A2 48/48 and
24 rows in each of the four declared domains, and use ODC IDs. Every source
locator must replay the exact MADOran sentence and every row must carry the
MADOran license identifier. Source-backed rows cannot silently become
AI-composed or translated-from-MSA rows.

Batch 01 begins as source_verified and becomes gpt_reviewed after all four GPT
chunks pass; both states keep learner_ready=false. Batch 02 may also contain
explicitly documented review_status=hold rows when no safe, standalone source
is available; those rows remain learner_ready=false and are excluded from
active/learner-ready counts. The validator blocks duplicate IDs, duplicate
normalized Arabic, canonical overlap, missing provenance, invalid enums, source
replay failures, prohibited sources or derivations, and premature learner
release. Native review remains a separate release gate.
