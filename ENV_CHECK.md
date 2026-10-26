# 새 작업 환경 15분 점검

처음 쓰는 원격 IDE·에이전트 환경에서 본 작업 전에 확인할 것. 위에서부터 순서대로, 항목당 1~2분.

| # | 확인 | 방법 | 결과 |
|---|---|---|---|
| 1 | 저장소 받기 | `git clone https://github.com/Meganpark980320/agent-workflow-kit.git && bash agent-workflow-kit/scripts/init.sh .` | |
| 2 | 에이전트가 규칙을 읽나 | 에이전트를 이 폴더에서 다시 시작하고 "AGENTS.md 규칙 세 줄 요약" | |
| 3 | 스킬이 보이나 | "쓸 수 있는 스킬 이름만 나열" (kickoff·close-step·data-analysis·web-service·wrap-up) | |
| 4 | 모델·권한 | `/status`, `/model`로 모델과 승인 방식 확인. 어떤 명령이 승인 없이 도는지 | |
| 5 | 런타임 | `python3 --version; node --version; pip --version; git --version` | |
| 6 | 패키지 설치 | `pip install --user rich` 같은 작은 것 하나 — 되는지·얼마나 걸리는지 | |
| 7 | 도구 스크립트 | `python3 scripts/profile_data.py <아무 CSV>` | |
| 8 | 웹 미리보기 | `PORT=3000 python3 agent-workflow-kit/starters/python-web/app.py` → 미리보기에 포트 3000, 경로 `/` | |
| 9 | 업무 담당자·도우미 | 메신저에서 담당자에게 질문 하나, 답 형식·속도 확인 | |
| 10 | 파일·커밋 | 새 파일 저장, `git add -A && git commit -m test`, `git log --oneline` | |
| 11 | 응답 속도 | 에이전트에게 짧은 요청 하나 — 몇 초 걸리나 (시간 배분에 반영) | |

확인 못 한 항목은 본 작업 첫 5분에 다시 본다.
