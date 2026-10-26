# agent-workflow-kit

코딩 에이전트(Codex CLI 등)와 일할 때 쓰는 범용 작업 규율·문서 틀·도구 모음.
특정 과제의 답은 들어 있지 않다. "요구사항 정의 → 작은 단계 → 단계마다 검증 → 기록"을 에이전트가 기본으로 따르게 만드는 것이 목적이다.

## 쓰는 법

```bash
git clone https://github.com/Meganpark980320/agent-workflow-kit.git
bash agent-workflow-kit/scripts/init.sh .     # 현재 작업 공간에 AGENTS.md·docs/·scripts/를 깐다 (있는 파일은 덮어쓰지 않음)
codex                                          # 작업 공간에서 에이전트를 시작하면 AGENTS.md를 읽는다
```

## 들어 있는 것

| 경로 | 내용 |
|---|---|
| `AGENTS.md` | 에이전트 작업 규율: 요구사항 번호 붙이기, 질문 모으기, 작은 단계·검증·커밋, 결정 기록, 보안·윤리, 웹 서버 0.0.0.0, 토큰 절약, 마무리 체크 |
| `OWNER_PRINCIPLES.md` | 주인의 판단 원칙 25개·물을 것/할 것·보고 방식·완료 전 체크리스트 (에이전트가 스스로 적용) |
| `templates/` | `REQUIREMENTS` `QUESTIONS` `PLAN` `DECISIONS` `VERIFY` `REPORT` `BRIEF` 문서 틀 (init.sh가 `docs/`로 복사) |
| `scripts/profile_data.py` | CSV/JSON/JSONL/XLSX 한눈에 보기: 타입·결측·고유값·범위·IQR 이상치·중복, 개인정보처럼 보이는 값은 가림 |
| `scripts/trace_check.py` | 요구사항(R번호)이 검증표·테스트·커밋에 연결됐는지 확인 |
| `.agents/skills/` | Codex 스킬 7개: kickoff(시작) · close-step(단계 닫기) · self-review(스스로 반박) · ask-owner(묶어서 묻기) · data-analysis · web-service · wrap-up(마무리). init.sh가 작업 공간에 복사 |
| `scripts/report.py` | 데이터 → HTML 보고서 한 장(요약표·분포·그룹 비교, 외부 라이브러리 없이 SVG) |
| `scripts/quality.py` | 파레토 · 그룹별 수율(95% 구간) · 관리도(I-MR, Western Electric 규칙) |
| `PILOT.md` | 사람 쪽 지휘 요령: 단계별 지시문 틀, 결과 의심하기, 판단은 사람이, 시간 배분 |
| `ENV_CHECK.md` | 새 원격 IDE·에이전트 환경 15분 점검표 |
| `starters/python-web` | 표준 라이브러리만 쓰는 최소 웹 서버(정적 + JSON API) + 실제 HTTP 테스트 |
| `starters/node-web` | Node 표준 모듈만 쓰는 같은 구조의 서버 |

## 원칙

- 검증은 실제로 실행한 결과로 한다. 실행하지 않은 것은 "미검증"으로 적는다.
- 결정에는 근거와 다른 선택지를 남긴다. 나중에 사람이 자기 말로 설명할 수 있어야 한다.
- 개인정보·키는 출력·로그·커밋에 남기지 않는다.

MIT License.
