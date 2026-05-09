"""
Aggregate annotated sessions into diagnostic-pattern reports.

Input:  annotated jsonl OR json (output of annotate_batch.py, or hand-annotated samples)
Output: markdown report to stdout (or --out)

Reports produced (per category + overall):
  1. Diagnosis ratio (is_diagnostic vs transactional)
  2. Symptom distribution (symptom_normalized counts)
  3. Most-asked information types (info_requested.type top-K)
  4. Avg diagnosis_quality.score, distribution
  5. Top good/bad patterns (frequent strings)
  6. Decision-branch catalog (one line per cluster)
  7. Trigger-phrase index (symptom -> phrases)

Run:
    python aggregate_report.py --input annotated_full.jsonl --out report.md
"""
from __future__ import annotations
import argparse, json, sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


def load(path: Path):
    text = path.read_text()
    if path.suffix == ".jsonl" or "\n{" in text[:200]:
        out = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "_error" not in obj:
                    out.append(obj)
            except json.JSONDecodeError:
                pass
        return out
    return json.loads(text)


def section(title, level=2):
    return "\n" + "#" * level + " " + title + "\n"


def top_counter(items, k=10):
    return Counter(items).most_common(k)


def fmt_pairs(pairs):
    return "\n".join(f"- `{k}`: {v}" for k, v in pairs)


def report_for(rows, label, out):
    if not rows:
        return
    out.append(section(f"分类报告: {label} (n={len(rows)})", 2))

    # diagnosis ratio
    diag = sum(1 for r in rows if r.get("is_diagnostic"))
    trans = sum(1 for r in rows if r.get("is_transactional"))
    out.append(f"- 含诊断过程: {diag} ({diag/len(rows):.0%})")
    out.append(f"- 纯交易类: {trans} ({trans/len(rows):.0%})")

    # symptom distribution
    symptoms = top_counter([r.get("symptom_normalized") for r in rows if r.get("symptom_normalized")])
    out.append(section("症状分布", 3))
    out.append(fmt_pairs(symptoms))

    # info requested
    info_types = []
    for r in rows:
        for ir in r.get("info_requested") or []:
            t = ir.get("type") if isinstance(ir, dict) else None
            if t:
                info_types.append(t)
    out.append(section("必索取信息 Top-K", 3))
    out.append(fmt_pairs(top_counter(info_types, 12)))

    # quality scores
    scores = [r["diagnosis_quality"]["score"] for r in rows
              if r.get("diagnosis_quality") and isinstance(r["diagnosis_quality"].get("score"), int)]
    if scores:
        out.append(section("诊断质量评分", 3))
        out.append(f"- 平均分: {mean(scores):.2f}（n={len(scores)}）")
        out.append(f"- 分布: {dict(Counter(scores))}")

    # patterns
    good, bad = [], []
    for r in rows:
        q = r.get("diagnosis_quality") or {}
        good += q.get("patterns_good") or []
        bad += q.get("patterns_bad") or []
    out.append(section("高频好做法", 3))
    out.append(fmt_pairs(top_counter(good, 10)))
    out.append(section("高频反模式", 3))
    out.append(fmt_pairs(top_counter(bad, 10)))

    # decision branches
    branches = [r["reusable_assets"]["decision_branch"] for r in rows
                if r.get("reusable_assets") and r["reusable_assets"].get("decision_branch")]
    if branches:
        out.append(section("决策分支汇总", 3))
        for b in branches[:20]:
            out.append(f"- {b}")

    # trigger phrases keyed by symptom
    by_symp = defaultdict(list)
    for r in rows:
        sn = r.get("symptom_normalized")
        for tp in (r.get("reusable_assets") or {}).get("trigger_phrases") or []:
            by_symp[sn].append(tp)
    if by_symp:
        out.append(section("触发短语索引（症状→用户口语）", 3))
        for sn, ps in by_symp.items():
            uniq = list(dict.fromkeys(ps))[:8]
            out.append(f"- **{sn}**: " + " / ".join(uniq))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()

    rows = load(Path(args.input))
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r.get("category") or r.get("_category") or "unknown"].append(r)

    out = ["# 客服诊断行为分析报告", f"\n样本数: **{len(rows)}**  覆盖类别: **{len(by_cat)}**\n"]
    report_for(rows, "全部", out)
    for cat, rs in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        report_for(rs, cat, out)

    text = "\n".join(out) + "\n"
    if args.out == "-":
        sys.stdout.write(text)
    else:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
