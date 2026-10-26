#!/usr/bin/env python3
"""품질·공정 데이터용 범용 분석 (제조·운영 어디에나 쓰는 기본 도구).

  pareto  — 불량·오류 유형 파레토(빈도 또는 합계, 누적 비율, 80% 선)
  yield   — 그룹(라인·장비·로트 등)별 수율 = 양품 / 전체, 신뢰구간(윌슨 95%)
  spc     — 관리도(I-MR): 중심선·관리 한계(±3σ, MR 기반), Western Electric 규칙 위반 표시

출력은 마크다운 표(터미널) + 선택적 SVG(--svg 파일). 결론은 사람이 판단한다.
사용 예:
  python scripts/quality.py pareto defects.csv --cat defect_type [--weight count]
  python scripts/quality.py yield lots.csv --group line --good good --total total
  python scripts/quality.py yield units.csv --group tool --pass result --pass-value PASS
  python scripts/quality.py spc measure.csv --value thickness [--order time] --svg spc.svg
"""
import argparse, math, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from profile_data import load, num  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pareto(rows, a):
    agg = defaultdict(float)
    for r in rows:
        k = str(r.get(a.cat, "") or "").strip()
        if not k:
            if not a.keep_empty:
                continue
            k = "(빈 값)"
        agg[k] += (num(r.get(a.weight)) or 0) if a.weight else 1
    total = sum(agg.values()) or 1
    print(f"| {a.cat} | {'합계' if a.weight else '건수'} | 비율 | 누적 |\n|---|---|---|---|")
    cum, cut = 0.0, None
    for k, v in sorted(agg.items(), key=lambda x: -x[1]):
        cum += v
        print(f"| {k} | {v:g} | {v / total:.1%} | {cum / total:.1%} |")
        if cut is None and cum / total >= 0.8:
            cut = k
    print(f"\n누적 80%까지: '{cut}'까지의 유형. 전체 {len(agg)}개 유형, 합계 {total:g}.")


def yld(rows, a):
    g = defaultdict(lambda: [0, 0])
    for r in rows:
        key = str(r.get(a.group, ""))
        if a.good and a.total:
            gd, tt = num(r.get(a.good)), num(r.get(a.total))
            if gd is None or tt is None:
                continue
            g[key][0] += gd; g[key][1] += tt
        else:
            g[key][0] += 1 if str(r.get(a.pass_col, "")).strip().lower() == a.pass_value.lower() else 0
            g[key][1] += 1
    allk = sum(v[0] for v in g.values()); alln = sum(v[1] for v in g.values())
    print(f"| {a.group} | 양품 | 전체 | 수율 | 95% 구간 | 전체 대비 |\n|---|---|---|---|---|---|")
    for k, (gd, tt) in sorted(g.items(), key=lambda x: (x[1][0] / x[1][1]) if x[1][1] else 0):
        lo, hi = wilson(gd, tt)
        flag = "낮음" if alln and hi < allk / alln else ("높음" if alln and lo > allk / alln else "")
        print(f"| {k} | {gd:g} | {tt:g} | {gd / tt:.2%} | {lo:.2%}~{hi:.2%} | {flag} |" if tt else f"| {k} | 0 | 0 | - | - | |")
    if alln:
        print(f"\n전체 수율 {allk / alln:.2%} ({allk:g}/{alln:g}). '낮음/높음'은 95% 구간이 전체 수율과 겹치지 않는 그룹.")


def spc(rows, a):
    if a.order:
        rows = sorted(rows, key=lambda r: str(r.get(a.order, "")))
    xs = [x for x in (num(r.get(a.value)) for r in rows) if x is not None]
    if len(xs) < 5:
        sys.exit("관리도에는 값이 5개 이상 필요하다.")
    mr = [abs(xs[i] - xs[i - 1]) for i in range(1, len(xs))]
    cl = sum(xs) / len(xs)
    sigma = (sum(mr) / len(mr)) / 1.128 if mr else 0
    ucl, lcl = cl + 3 * sigma, cl - 3 * sigma
    z = [(x - cl) / sigma if sigma else 0 for x in xs]
    viol = defaultdict(list)
    for i, v in enumerate(z):
        if abs(v) > 3:
            viol[i].append("1: 3σ 밖")
        # 규칙 2·3은 지금 점도 그 쪽에 있을 때만 (패턴을 완성하는 점에 표시)
        side = 1 if v > 0 else -1
        if i >= 2 and abs(v) > 2 and sum(1 for j in range(i - 2, i + 1) if z[j] * side > 2) >= 2:
            viol[i].append("2: 3점 중 2점 2σ 밖(같은 쪽)")
        if i >= 4 and abs(v) > 1 and sum(1 for j in range(i - 4, i + 1) if z[j] * side > 1) >= 4:
            viol[i].append("3: 5점 중 4점 1σ 밖(같은 쪽)")
        if i >= 7 and (all(z[j] > 0 for j in range(i - 7, i + 1)) or all(z[j] < 0 for j in range(i - 7, i + 1))):
            viol[i].append("4: 8점 연속 한쪽")
    print(f"n={len(xs)} 중심선={cl:.4g} σ(MR/1.128)={sigma:.4g} UCL={ucl:.4g} LCL={lcl:.4g}")
    print("| 순서 | 값 | z | 위반 규칙 |\n|---|---|---|---|")
    for i in sorted(viol):
        print(f"| {i + 1} | {xs[i]:g} | {z[i]:+.2f} | {'; '.join(viol[i])} |")
    print(f"\n위반 지점 {len(viol)}개 / {len(xs)}. 위반은 '원인을 찾아볼 신호'이지 불량 판정이 아니다.")
    if a.svg:
        w, h, p = 640, 220, 30
        lo, hi = min(min(xs), lcl), max(max(xs), ucl)
        X = lambda i: p + i * (w - 2 * p) / max(1, len(xs) - 1)
        Y = lambda v: h - p - (v - lo) / ((hi - lo) or 1) * (h - 2 * p)
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(xs))
        lines = "".join(f'<line x1="{p}" x2="{w - p}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{c}" stroke-dasharray="{d}"/><text x="{w - p + 2}" y="{Y(v) + 3:.1f}" font-size="10">{t}</text>' for v, c, d, t in ((ucl, "#c00", "4 3", "UCL"), (cl, "#666", "", "CL"), (lcl, "#c00", "4 3", "LCL")))
        dots = "".join(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{4 if i in viol else 2.5}" fill="{"#c00" if i in viol else "#4c6ef5"}"><title>{i + 1}: {v:g}</title></circle>' for i, v in enumerate(xs))
        open(a.svg, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w + 30} {h}" width="100%"><title>{a.value} 관리도</title>{lines}<polyline points="{pts}" fill="none" stroke="#4c6ef5"/>{dots}</svg>')
        print(f"SVG: {a.svg}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pareto"); p.add_argument("file"); p.add_argument("--cat", required=True); p.add_argument("--weight"); p.add_argument("--keep-empty", action="store_true", help="빈 값도 한 유형으로 센다")
    y = sub.add_parser("yield"); y.add_argument("file"); y.add_argument("--group", required=True); y.add_argument("--good"); y.add_argument("--total")
    y.add_argument("--pass", dest="pass_col"); y.add_argument("--pass-value", default="PASS")
    s = sub.add_parser("spc"); s.add_argument("file"); s.add_argument("--value", required=True); s.add_argument("--order"); s.add_argument("--svg")
    a = ap.parse_args()
    rows = [r for r in load(a.file) if isinstance(r, dict)]
    {"pareto": pareto, "yield": yld, "spc": spc}[a.cmd](rows, a)


if __name__ == "__main__":
    main()
