---
name: data-analysis
description: 데이터(CSV·JSON·엑셀·로그)를 분석해 결론·보고서를 낼 때 — 품질 점검, 요약, 그룹 비교, 파레토·수율·관리도, HTML 보고서. "데이터 분석", "원인 찾아 줘", "보고서 만들어 줘"에 쓴다.
---

# 데이터 분석

1. 먼저 점검: `python3 scripts/profile_data.py <파일>` — 결측·이상치·중복·타입. 이상한 점은 `docs/DECISIONS.md`에 처리 방법과 함께 적는다(빼기·채우기·그대로 두기와 근거).
2. 질문을 숫자로 바꾼다: "무엇과 무엇을 비교해 어떤 결정을 돕나". 요구사항 R번호와 연결한다.
3. 도구:
   - 요약 보고서(HTML): `python3 scripts/report.py <파일> --group <열> --value <열> -o report.html`
   - 유형별 비중: `python3 scripts/quality.py pareto <파일> --cat <열> [--weight <열>]`
   - 그룹별 수율(95% 구간): `python3 scripts/quality.py yield <파일> --group <열> --pass <열> --pass-value PASS` 또는 `--good <열> --total <열>`
   - 시간 순 이상 신호(관리도): `python3 scripts/quality.py spc <파일> --value <열> --order <시간열> --svg spc.svg`
4. 결론은 근거 숫자와 함께: "L3 수율 91%(41/45, 95% 구간 79~96%)는 전체 93%와 통계적으로 구분되지 않는다"처럼. 표본이 작으면 단정하지 않는다.
5. 상관과 인과를 구분한다. 원인 주장은 "가설"로 쓰고 확인 방법을 붙인다.
6. 개인정보 열은 집계만 내고 원값을 출력하지 않는다.
7. 결과 숫자 2~3개는 다른 방법(직접 계산·표본 확인)으로 대조하고 `docs/VERIFY.md`에 남긴다.
