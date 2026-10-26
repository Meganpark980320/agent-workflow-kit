# AGENTS.md — 작업 규율

이 작업 공간에서 코딩 에이전트가 따를 규칙. 자세한 절차는 `.agents/skills/`의 스킬(kickoff · close-step · data-analysis · web-service · wrap-up)에 있다.

## 원칙
1. **요구사항부터.** 안내문을 읽고 `docs/REQUIREMENTS.md`에 R번호로 적는다. 모호하면 추측하지 말고 `docs/QUESTIONS.md`에 질문으로 모아 사용자에게 보여 준다. (스킬: kickoff)
2. **작게, 하나씩.** `docs/PLAN.md`의 한 단계만 한다. 단계는 **실제 검증 → `docs/VERIFY.md` → 커밋**으로 닫는다. 커밋 메시지는 `R번호: 무엇을 왜`. (스킬: close-step)
3. **결정은 근거와 함께.** 중요한 선택은 `docs/DECISIONS.md`에 결정 / 다른 선택지 / 근거.
4. **검증은 실행한 결과로만.** 실행하지 않은 것은 "미검증". 실패하면 원인 한 줄, 같은 시도 반복 금지.
5. **보안·윤리.** 개인정보·키·토큰을 출력·로그·커밋에 남기지 않는다(필요하면 마스킹). 데이터 결론은 표본·결측·불확실성을 밝힌다.
6. **웹 서버는 `0.0.0.0`.** 실제 포트를 출력하고 띄운 터미널은 닫지 않는다. (스킬: web-service)
7. **아껴 쓰기.** 긴 파일을 다시 출력하지 않고 바꾼 곳과 이유만 말한다. 이미 확인한 사실은 `docs/`를 먼저 본다. 오래 걸릴 작업은 예상 시간을 먼저 말한다.
8. **마감 15분 전 마무리.** `python scripts/trace_check.py` → `docs/REPORT.md` → `docs/BRIEF.md`(사용자가 직접 설명할 한 화면 요약) → 필수 파일 점검 → 마지막 커밋. (스킬: wrap-up)

## 도구
- 데이터 훑기: `python scripts/profile_data.py <파일>`
- HTML 보고서: `python scripts/report.py <파일> [--group 열 --value 열] -o report.html`
- 파레토·수율·관리도: `python scripts/quality.py pareto|yield|spc ...` (스킬: data-analysis)
- 요구사항 추적: `python scripts/trace_check.py`
