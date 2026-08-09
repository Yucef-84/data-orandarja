# Oran Darija A1–A2 균형본 요약

## 한눈에 보기

| 항목 | 결과 |
|---|---:|
| 전체 행 | 888 |
| A1 | 444 |
| A2 | 444 |
| 고유 ID | 888 |
| 고유 Arabic 표제어 | 888 |
| 필수값 누락 | 0 |
| 보류·논쟁 상태 | 0 |
| 신규 MADOran 원문 위치 오류 | 0 |

## 범위와 근거

이 파일은 알제(Algiers) 도시어가 아니라 **Oran/Wahran 도시 방언** 학습용
안전 핵심본이다. CORVAM Oran, Guerrero의 Oran 연구와 MADOran V2를 근거로
하며, 이번 균형 확장 388행은 모두 MADOran의 실제 token과 sentence에 연결된다.

## 검증 흐름

1. 기존 500행과 겹치지 않는 MADOran 후보 1,200개 추출
2. A2 학습 가치가 있는 388행 구조화
3. 오른쪽 ChatGPT 독립 전수감사에서 268개 ID, 589개 필드 수정
4. 수정본을 8구간으로 재전수검사
5. 잔여 수정 29행 재검증 및 마지막 수정행 `ALL PASS`
6. 로컬에서 30,915개 MADOran 토큰과 locator·원문 표면형 전수 대조

## 기준 파일

- 학습·배포 기준: `data/oran_darija_verified.tsv`
- 신규 A2 확장본: `data/madoran_expansion_a2_388_final.tsv`
- 수정행 재검증본: `data/a2_final_corrected_rows_recheck.tsv`

공개 배포·음성 녹음·모델 학습 전에는 Oran 출생·성장 화자 2인의 독립 검수를
추가하는 것이 최종 안전 조건이다.
