#!/usr/bin/env python3
"""데이터 분석 보고서 한 장(HTML): 요약표 + 숫자 열 히스토그램 + 범주 열 상위 막대 + (선택) 그룹별 비교.
외부 라이브러리 없이 SVG로 그린다. 결론 문장은 사람이 채우도록 자리를 남긴다(근거 숫자는 표에 있음).
사용:
  python3 scripts/report.py data.csv -o report.html
  python3 scripts/report.py data.csv --group line --value yield -o report.html   # 그룹별 평균·개수 비교
"""
import argparse, html, os, statistics, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profile_data import PII_COL, load, num, mask  # noqa: E402

W, H, PAD = 520, 180, 30


def svg_bars(labels, values, title, fmt="{:g}"):
    if not values:
        return ""
    vmax = max(values) or 1
    bw = (W - 2 * PAD) / len(values)
    out = [f'<svg viewBox="0 0 {W} {H + 40}" width="100%" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>']
    for i, (l, v) in enumerate(zip(labels, values)):
        h = (H - PAD) * v / vmax
        x, y = PAD + i * bw, H - h
        out.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{max(bw - 4, 1):.1f}" height="{h:.1f}" rx="2" fill="#4c6ef5"><title>{html.escape(str(l))}: {fmt.format(v)}</title></rect>')
        if len(values) <= 12:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{H + 14}" font-size="10" text-anchor="middle">{html.escape(str(l))[:10]}</text>')
            out.append(f'<text x="{x + bw / 2:.1f}" y="{y - 3:.1f}" font-size="10" text-anchor="middle">{fmt.format(v)}</text>')
    out.append(f'<line x1="{PAD}" x2="{W - PAD}" y1="{H}" y2="{H}" stroke="#999"/></svg>')
    return "".join(out)


def hist(nums, bins=12):
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return [f"{lo:g}"], [len(nums)]
    step = (hi - lo) / bins
    counts = [0] * bins
    for n in nums:
        counts[min(int((n - lo) / step), bins - 1)] += 1
    return [f"{lo + i * step:.3g}" for i in range(bins)], counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("-o", "--out", default="report.html")
    ap.add_argument("--group")
    ap.add_argument("--value")
    ap.add_argument("--title", default="데이터 분석 보고서")
    a = ap.parse_args()
    rows = [r for r in load(a.file) if isinstance(r, dict)]
    cols = list(dict.fromkeys(k for r in rows for k in r))
    parts = [f"<h1>{html.escape(a.title)}</h1><p class=m>원본: {html.escape(os.path.basename(a.file))} · 행 {len(rows)} · 열 {len(cols)}</p>",
             "<h2>결론 (사람이 확인 후 작성)</h2><ul><li>…</li></ul>", "<h2>열 요약</h2><table><tr><th>열</th><th>타입</th><th>결측</th><th>고유</th><th>최소</th><th>중앙</th><th>최대</th><th>평균</th></tr>"]
    charts = []
    for c in cols:
        vals = [r.get(c) for r in rows]
        present = [v for v in vals if v not in (None, "")]
        nums = [n for n in (num(v) for v in present) if n is not None]
        miss = len(vals) - len(present)
        if present and len(nums) >= 0.9 * len(present) and nums:
            parts.append(f"<tr><td>{html.escape(c)}</td><td>숫자</td><td>{miss}</td><td>{len(set(nums))}</td><td>{min(nums):g}</td><td>{statistics.median(nums):g}</td><td>{max(nums):g}</td><td>{statistics.fmean(nums):.4g}</td></tr>")
            labels, counts = hist(nums)
            charts.append(f"<h3>{html.escape(c)} 분포</h3>" + svg_bars(labels, counts, f"{c} 분포", "{:d}"))
        else:
            if PII_COL.search(str(c)):
                parts.append(f"<tr><td>{html.escape(c)}</td><td>글자</td><td>{miss}</td><td>{len(set(map(str, present)))}</td><td colspan=4>(사람 정보 열이라 값을 싣지 않음)</td></tr>")
                continue
            top = Counter(mask(v) for v in present).most_common(10)
            parts.append(f"<tr><td>{html.escape(c)}</td><td>글자</td><td>{miss}</td><td>{len(set(map(str, present)))}</td><td colspan=4>{html.escape(', '.join(f'{k}({n})' for k, n in top[:5]))}</td></tr>")
            if 1 < len(top) and len(set(map(str, present))) <= 50:
                charts.append(f"<h3>{html.escape(c)} 상위</h3>" + svg_bars([k for k, _ in top], [n for _, n in top], f"{c} 상위", "{:d}"))
    parts.append("</table>")
    if a.group and a.value:
        g = defaultdict(list)
        for r in rows:
            n = num(r.get(a.value))
            if n is not None:
                g[str(r.get(a.group))].append(n)
        keys = sorted(g, key=lambda k: -statistics.fmean(g[k]))
        parts.append(f"<h2>{html.escape(a.group)}별 {html.escape(a.value)}</h2><table><tr><th>{html.escape(a.group)}</th><th>개수</th><th>평균</th><th>표준편차</th></tr>")
        for k in keys:
            sd = statistics.stdev(g[k]) if len(g[k]) > 1 else 0
            parts.append(f"<tr><td>{html.escape(k)}</td><td>{len(g[k])}</td><td>{statistics.fmean(g[k]):.4g}</td><td>{sd:.3g}</td></tr>")
        parts.append("</table>" + svg_bars(keys[:20], [statistics.fmean(g[k]) for k in keys[:20]], f"{a.group}별 평균 {a.value}", "{:.3g}"))
        parts.append("<p class=m>표본이 5개 미만인 그룹은 평균을 믿기 어렵다.</p>")
    parts.append("<h2>분포</h2>" + "".join(charts))
    css = "body{font-family:system-ui,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#222}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid #ddd;padding:4px 6px;text-align:left}.m{color:#666;font-size:13px}h3{font-size:14px;margin:18px 0 4px}"
    open(a.out, "w", encoding="utf-8").write(f"<!doctype html><meta charset=utf-8><title>{html.escape(a.title)}</title><style>{css}</style>" + "".join(parts))
    print(f"썼다: {a.out}")


if __name__ == "__main__":
    main()
