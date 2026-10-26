---
name: web-service
description: 웹 서비스·대시보드·API를 만들어 브라우저 미리보기로 보여 줄 때 — 뼈대 고르기, 0.0.0.0 바인딩, 실제 HTTP 테스트, 화면 확인. "웹으로 만들어 줘", "대시보드", "API"에 쓴다.
---

# 웹 서비스

1. 뼈대: 설치 없이 바로 도는 `agent-workflow-kit/starters/python-web`(표준 라이브러리) 또는 `agent-workflow-kit/starters/node-web`를 작업 공간으로 복사해 시작한다. 프레임워크가 꼭 필요할 때만 설치하고 이유를 `docs/DECISIONS.md`에 적는다.
2. 서버는 반드시 `0.0.0.0`에 바인딩하고 실제 포트를 출력한다. 서버는 별도 터미널에서 띄우고 닫지 않는다.
3. 기능마다 실제 HTTP 테스트를 둔다(`agent-workflow-kit/starters/python-web/test_app.py` 참고: 서버를 띄워 요청). 정상·빈 입력·잘못된 입력·큰 입력을 확인한다.
4. 입력 검증과 출력 이스케이프(XSS), 업로드 크기 제한, 비밀값은 환경변수로.
5. 사용자가 미리보기에서 확인할 경로와 동작(무엇을 누르면 무엇이 보이나)을 안내하고, 확인 결과를 `docs/VERIFY.md`에 남긴다.
6. 화면은 단순하게: 한 화면에 핵심 기능, 빈 상태·오류 메시지를 보이게.
