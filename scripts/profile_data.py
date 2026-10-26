#!/usr/bin/env python3
"""데이터 파일 한눈에 보기: 행·열 수, 열마다 타입·결측·고유값·최소/최대/평균·이상치(IQR) 수, 예시 값.
CSV/TSV/JSON(배열)/JSONL/XLSX(pandas 있으면). pandas가 없어도 CSV·JSON은 표준 라이브러리로 동작한다.
개인정보처럼 보이는 열(이메일·전화·주민번호 형태)은 예시 값을 가린다.
사용: python3 scripts/profile_data.py data.csv [더 많은 파일...]
"""
import csv, json, math, re, statistics, sys
from collections import Counter

PII = [re.compile(p) for p in (r"[\w.+-]+@[\w-]+\.[\w.]+", r"\b01[016789]-?\d{3,4}-?\d{4}\b", r"\b\d{6}-?[1-4]\d{6}\b")]
# 열 이름만 봐도 사람 정보인 열: 예시 값을 통째로 가린다
PII_COL = re.compile(r"(name|operator|user|employee|worker|owner|email|e-mail|phone|mobile|tel|address|ssn|resident|account|이름|성명|작업자|담당자|사원|직원|사용자|연락처|전화|휴대|이메일|주소|주민|계좌)", re.I)

def mask(v):
    s = str(v)
    for p in PII:
        if p.search(s):
            return "<가림>"
    return s[:40]

def load(path):
    low = path.lower()
    if low.endswith((".xlsx", ".xls")):
        import pandas as pd  # noqa
        return pd.read_excel(path).to_dict("records")
    if low.endswith(".jsonl"):
        return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if low.endswith(".json"):
        d = json.load(open(path, encoding="utf-8"))
        if isinstance(d, dict):
            d = next((v for v in d.values() if isinstance(v, list)), [d])
        return d
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096); f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(f, dialect=dialect))

def num(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return None if isinstance(v, float) and math.isnan(v) else float(v)
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None

def profile(path):
    rows = load(path)
    cols = list(dict.fromkeys(k for r in rows if isinstance(r, dict) for k in r))
    print(f"\n## {path} — 행 {len(rows)}, 열 {len(cols)}")
    print("| 열 | 타입 | 결측 | 고유값 | 최소 | 최대 | 평균 | 이상치(IQR) | 예시 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for c in cols:
        vals = [r.get(c) for r in rows if isinstance(r, dict)]
        missing = sum(1 for v in vals if v in (None, ""))
        present = [v for v in vals if v not in (None, "")]
        nums = [n for n in (num(v) for v in present) if n is not None]
        is_num = present and len(nums) >= 0.9 * len(present)
        uniq = len(set(map(str, present)))
        ex = "<가림: 사람 정보 열>" if PII_COL.search(str(c)) else ", ".join(mask(v) for v, _ in Counter(map(str, present)).most_common(3))
        if is_num and nums:
            q = statistics.quantiles(nums, n=4) if len(nums) >= 4 else [min(nums), statistics.median(nums), max(nums)]
            iqr = q[2] - q[0]
            out = sum(1 for n in nums if n < q[0] - 1.5 * iqr or n > q[2] + 1.5 * iqr)
            print(f"| {c} | 숫자 | {missing} | {uniq} | {min(nums):g} | {max(nums):g} | {statistics.fmean(nums):.4g} | {out} | {ex} |")
        else:
            print(f"| {c} | 글자 | {missing} | {uniq} | | | | | {ex} |")
    dup = len(rows) - len({json.dumps(r, sort_keys=True, ensure_ascii=False, default=str) for r in rows})
    print(f"\n중복 행: {dup}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        profile(p)
