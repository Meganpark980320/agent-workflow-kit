#!/usr/bin/env python3
"""요구사항 추적 확인: docs/REQUIREMENTS.md의 R번호가 docs/VERIFY.md에 판정과 함께 있는지,
테스트 코드나 커밋 메시지에서 언급되는지 본다. 빠진 것을 목록으로 보여 준다.
사용: python3 scripts/trace_check.py [작업 공간 경로]
"""
import os, re, subprocess, sys

ws = sys.argv[1] if len(sys.argv) > 1 else "."
rd = lambda p: open(os.path.join(ws, p), encoding="utf-8").read() if os.path.exists(os.path.join(ws, p)) else ""
req = sorted(set(re.findall(r"\bR\d+\b", rd("docs/REQUIREMENTS.md"))), key=lambda r: int(r[1:]))
verify = rd("docs/VERIFY.md")
rows = {m.group(1): m.group(0) for m in re.finditer(r"^\|\s*(R\d+)\s*\|.*$", verify, re.M)}
tests = ""
for root, _, files in os.walk(ws):
    if any(x in root for x in (".git", "node_modules", ".venv", "__pycache__")):
        continue
    for f in files:
        if re.search(r"(test|spec)", f, re.I) and f.endswith((".py", ".js", ".ts", ".tsx", ".sh")):
            tests += open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
try:
    log = subprocess.run(["git", "-C", ws, "log", "--pretty=%s"], capture_output=True, text=True).stdout
except Exception:
    log = ""
if not req:
    sys.exit("docs/REQUIREMENTS.md에 R번호가 없다. 요구사항부터 번호를 붙여 적어라.")
print("| 요구사항 | 검증표 | 판정 | 테스트 언급 | 커밋 언급 |")
print("|---|---|---|---|---|")
missing = 0
for r in req:
    row = rows.get(r, "")
    verdict = "통과" if re.search(r"통과|pass|ok|✅", row, re.I) else ("실패" if re.search(r"실패|fail|❌", row, re.I) else ("대기" if row else "없음"))
    t = "O" if re.search(rf"\b{r}\b", tests) else "-"
    c = "O" if re.search(rf"\b{r}\b", log) else "-"
    if verdict != "통과":
        missing += 1
    print(f"| {r} | {'O' if row else 'X'} | {verdict} | {t} | {c} |")
print(f"\n요구사항 {len(req)}개 중 통과 {len(req) - missing}개." + (" 남은 것을 먼저 닫아라." if missing else " 전부 통과."))
# 마무리 문서가 틀 그대로인지
for doc, mark in (("docs/REPORT.md", "## 무엇을 만들었나\n- \n"), ("docs/BRIEF.md", "1. \n2. ")):
    body = rd(doc)
    if not body or mark in body:
        print(f"아직 비어 있음: {doc} — wrap-up에서 채울 것")
