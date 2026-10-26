#!/usr/bin/env bash
# 작업 공간에 규율·문서 틀을 깐다. 이미 있는 파일은 덮어쓰지 않는다.
# 사용: bash <이 저장소>/scripts/init.sh [작업 공간 경로, 기본 = 현재 폴더]
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
WS="${1:-$PWD}"
mkdir -p "$WS/docs" "$WS/scripts"
copy() { if [ -e "$2" ]; then echo "건너뜀(이미 있음): $2"; else cp "$1" "$2"; echo "만듦: $2"; fi; }
copy "$KIT/AGENTS.md" "$WS/AGENTS.md"
for f in REQUIREMENTS QUESTIONS PLAN DECISIONS VERIFY REPORT BRIEF; do copy "$KIT/templates/$f.md" "$WS/docs/$f.md"; done
for f in profile_data.py trace_check.py report.py quality.py; do copy "$KIT/scripts/$f" "$WS/scripts/$f"; done
for d in "$KIT"/.agents/skills/*/; do n=$(basename "$d"); mkdir -p "$WS/.agents/skills/$n"; copy "$d/SKILL.md" "$WS/.agents/skills/$n/SKILL.md"; done
[ -e "$WS/.gitignore" ] || printf '__pycache__/\n*.pyc\nnode_modules/\n.venv/\n.env\n' > "$WS/.gitignore"
if [ ! -d "$WS/.git" ]; then git -C "$WS" init -q && echo "git 저장소 만듦"; fi
echo "완료. 코딩 에이전트를 이 폴더에서 다시 시작하면 AGENTS.md를 읽는다."
