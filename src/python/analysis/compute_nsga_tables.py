#!/usr/bin/env python3
"""
Statistical analysis and LaTeX table generation for IVF/NSGA-II and IVF/NSGA-III.

Reads:  data/processed/nsga_experiments.csv
Writes: results/tables/nsga_igd_table.tex
        results/tables/nsga_hv_table.tex
        results/tables/nsga_summary.tex
        results/tables/nsga_summary.txt  (plain-text summary)

Statistics:
  - Median ± IQR per (algorithm, problem, M)
  - Wilcoxon signed-rank test (paired by problem instance)
  - Effect size: Vargha–Delaney A₁₂
  - Summary counts: wins / ties / losses (+/=/-)
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
from scipy import stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "nsga_experiments.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "results", "tables")

# Significance threshold (after BH correction)
ALPHA = 0.05

PROBLEM_ORDER_M2 = [
    "ZDT1", "ZDT2", "ZDT3", "ZDT4", "ZDT6",
    "DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4", "DTLZ5", "DTLZ6", "DTLZ7",
    "WFG1", "WFG2", "WFG3", "WFG4", "WFG5", "WFG6", "WFG7", "WFG8", "WFG9",
    "MaF1", "MaF2", "MaF3", "MaF4", "MaF5", "MaF6", "MaF7",
]
PROBLEM_ORDER_M3 = [
    "DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4", "DTLZ5", "DTLZ6", "DTLZ7",
    "WFG1", "WFG2", "WFG3", "WFG4", "WFG5", "WFG6", "WFG7", "WFG8", "WFG9",
    "MaF1", "MaF2", "MaF3", "MaF4", "MaF5", "MaF6", "MaF7",
]

TRACKS = [
    ("IVFNSGAII",  "NSGAII",  "IVF/NSGA-II",  "NSGA-II"),
    ("IVFNSGAIII", "NSGAIII", "IVF/NSGA-III", "NSGA-III"),
]


def bh_correction(pvals: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """Benjamini–Hochberg correction. Returns boolean mask of rejected nulls."""
    n = len(pvals)
    if n == 0:
        return np.array([], dtype=bool)
    order = np.argsort(pvals)
    ranked_pvals = pvals[order]
    thresholds = np.arange(1, n + 1) / n * alpha
    below = ranked_pvals <= thresholds
    # all hypotheses up to the last rejection are rejected
    if below.any():
        cutoff = np.where(below)[0].max()
        rejected = np.zeros(n, dtype=bool)
        rejected[order[:cutoff + 1]] = True
    else:
        rejected = np.zeros(n, dtype=bool)
    return rejected


def vargha_delaney_a12(x: np.ndarray, y: np.ndarray) -> float:
    """A₁₂(x > y): probability that a random x exceeds a random y.
    A₁₂ > 0.5 → x tends to be larger than y."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return np.nan
    r = stats.rankdata(np.concatenate([x, y]))
    rx = r[:nx].sum()
    return (rx / nx - (nx + 1) / 2) / ny


def sign_str(ivf_val: float, base_val: float, rejected: bool,
             metric: str) -> str:
    """Return +, -, or = symbol.
    For IGD: lower is better → + means IVF wins (IVF < base).
    For HV:  higher is better → + means IVF wins (IVF > base).
    """
    if not rejected:
        return "="
    if metric == "IGD":
        return "+" if ivf_val < base_val else "-"
    else:  # HV
        return "+" if ivf_val > base_val else "-"


def analyze_track(df: pd.DataFrame, ivf_algo: str, base_algo: str,
                  metric: str) -> pd.DataFrame:
    """
    For each (problem, M), compute: median IVF, median base, Wilcoxon p-value,
    A₁₂, BH-corrected significance, and +/=/- symbol.
    """
    df_ivf  = df[df["algo"] == ivf_algo]
    df_base = df[df["algo"] == base_algo]

    problems = df_ivf[["problem", "M"]].drop_duplicates().sort_values(["M", "problem"])

    rows = []
    for _, (prob, m) in problems.iterrows():
        ivf_runs  = df_ivf [(df_ivf ["problem"] == prob) & (df_ivf ["M"] == m)][metric].values
        base_runs = df_base[(df_base["problem"] == prob) & (df_base["M"] == m)][metric].values

        # Align lengths
        n = min(len(ivf_runs), len(base_runs))
        if n < 2:
            continue
        ivf_runs, base_runs = ivf_runs[:n], base_runs[:n]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, pval = stats.wilcoxon(ivf_runs, base_runs, alternative="two-sided")

        a12 = vargha_delaney_a12(ivf_runs, base_runs)

        rows.append({
            "problem": prob,
            "M": m,
            "group": df_ivf[(df_ivf["problem"] == prob) & (df_ivf["M"] == m)]["group"].iloc[0],
            "median_ivf":  float(np.median(ivf_runs)),
            "iqr_ivf":     float(np.percentile(ivf_runs, 75) - np.percentile(ivf_runs, 25)),
            "median_base": float(np.median(base_runs)),
            "iqr_base":    float(np.percentile(base_runs, 75) - np.percentile(base_runs, 25)),
            "pval":        pval,
            "A12":         a12,
        })

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    # BH correction
    pvals = result["pval"].values
    rejected = bh_correction(pvals)
    result["significant"] = rejected

    result["sign"] = [
        sign_str(r["median_ivf"], r["median_base"], r["significant"], metric)
        for _, r in result.iterrows()
    ]
    return result


def format_sci(val: float, iqr: float) -> str:
    """Format median(IQR) in scientific notation for table cells."""
    def sci(v):
        if np.isnan(v) or v == 0:
            return "—"
        exp = int(np.floor(np.log10(abs(v))))
        mant = v / 10**exp
        return f"${mant:.2f}\\times10^{{{exp}}}$"
    return f"{sci(val)} ({sci(iqr)})"


def make_latex_table(result: pd.DataFrame, ivf_label: str, base_label: str,
                     metric: str, m_val: int) -> str:
    """Generate a LaTeX table for one (metric, M) combination."""
    sub = result[result["M"] == m_val].copy()

    # Sort by group then problem
    order = PROBLEM_ORDER_M2 if m_val == 2 else PROBLEM_ORDER_M3
    sub["_order"] = sub["problem"].apply(
        lambda p: order.index(p) if p in order else 999
    )
    sub = sub.sort_values("_order").reset_index(drop=True)

    caption = (
        f"Median ({metric}) and IQR for $M={m_val}$ objectives. "
        f"Sign column: \\texttt{{+}} means {ivf_label} wins, "
        f"\\texttt{{-}} means {base_label} wins, "
        f"\\texttt{{=}} means no significant difference "
        f"(Wilcoxon, BH-corrected $\\alpha=0.05$)."
    )
    label = f"tab:{metric.lower()}_m{m_val}_{ivf_label.lower().replace('/', '')}"

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\scriptsize",
        "\\begin{tabular}{llrrrrl}",
        "\\toprule",
        f"Group & Problem & \\multicolumn{{2}}{{c}}{{{ivf_label}}} "
        f"& \\multicolumn{{2}}{{c}}{{{base_label}}} & Sign \\\\",
        "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}",
        " & & Median & IQR & Median & IQR & \\\\",
        "\\midrule",
    ]

    current_group = None
    for _, row in sub.iterrows():
        if row["group"] != current_group:
            if current_group is not None:
                lines.append("\\addlinespace")
            current_group = row["group"]

        sign = row["sign"]
        sign_tex = (
            "\\textbf{+}" if sign == "+"
            else "\\textbf{--}" if sign == "-"
            else "="
        )

        def fmt(v):
            if np.isnan(v) or v == 0:
                return "—"
            exp = int(np.floor(np.log10(abs(v)))) if v != 0 else 0
            mant = v / 10**exp
            return f"${mant:.2f}\\!\\times\\!10^{{{exp}}}$"

        lines.append(
            f"{row['group']} & {row['problem']} & "
            f"{fmt(row['median_ivf'])} & {fmt(row['iqr_ivf'])} & "
            f"{fmt(row['median_base'])} & {fmt(row['iqr_base'])} & "
            f"{sign_tex} \\\\"
        )

    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def summary_counts(result: pd.DataFrame) -> dict:
    counts = result["sign"].value_counts().to_dict()
    return {
        "wins":  counts.get("+", 0),
        "ties":  counts.get("=", 0),
        "losses": counts.get("-", 0),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("=== NSGA Experiments — Statistical Analysis ===\n")

    if not os.path.isfile(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found. Run consolidate_nsga_experiments.py first.")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} rows from {CSV_PATH}\n")

    summary_lines = []

    for ivf_algo, base_algo, ivf_label, base_label in TRACKS:
        summary_lines.append(f"\n{'='*60}")
        summary_lines.append(f"Track: {ivf_label} vs {base_label}")
        summary_lines.append('='*60)

        for metric in ("IGD", "HV"):
            result = analyze_track(df, ivf_algo, base_algo, metric)
            if result.empty:
                print(f"  No data for {ivf_algo} vs {base_algo} / {metric}")
                continue

            counts_all = summary_counts(result)
            summary_lines.append(
                f"\n  {metric}: +{counts_all['wins']} / "
                f"={counts_all['ties']} / -{counts_all['losses']}  "
                f"(total {len(result)})"
            )

            for m_val in sorted(result["M"].unique()):
                sub = result[result["M"] == m_val]
                c = summary_counts(sub)
                summary_lines.append(
                    f"    M={m_val}: +{c['wins']} / ={c['ties']} / -{c['losses']}"
                )

            # LaTeX tables per M
            for m_val in sorted(result["M"].unique()):
                tex = make_latex_table(result, ivf_label, base_label, metric, m_val)
                fname = (
                    f"nsga_{ivf_algo.lower()}_{metric.lower()}_m{m_val}.tex"
                )
                fpath = os.path.join(OUT_DIR, fname)
                with open(fpath, "w") as f_out:
                    f_out.write(tex + "\n")
                print(f"  Wrote {fname}")

            # Save full result CSV for downstream use
            result_csv = os.path.join(
                OUT_DIR,
                f"nsga_{ivf_algo.lower()}_{metric.lower()}_stats.csv"
            )
            result.to_csv(result_csv, index=False)

    # Summary table (combined wins/ties/losses)
    summary_lines.append("\n\n" + "="*60)
    summary_lines.append("COMBINED SUMMARY")
    summary_lines.append("="*60)

    tex_summary = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Win/tie/loss counts (Wilcoxon, BH $\\alpha=0.05$) "
        "for IVF variants vs their respective base algorithms across "
        "52 benchmark instances.}",
        "\\label{tab:nsga_summary}",
        "\\begin{tabular}{llcrrrr}",
        "\\toprule",
        "Algorithm & Metric & $M$ & Wins & Ties & Losses & Total \\\\",
        "\\midrule",
    ]

    for ivf_algo, base_algo, ivf_label, base_label in TRACKS:
        first_row = True
        for metric in ("IGD", "HV"):
            result = analyze_track(df, ivf_algo, base_algo, metric)
            if result.empty:
                continue
            for m_val in sorted(result["M"].unique()):
                sub = result[result["M"] == m_val]
                c = summary_counts(sub)
                algo_str = ivf_label if first_row else ""
                metric_str = metric if m_val == sorted(result["M"].unique())[0] else ""
                tex_summary.append(
                    f"{algo_str} & {metric} & {m_val} & "
                    f"{c['wins']} & {c['ties']} & {c['losses']} & {len(sub)} \\\\"
                )
                first_row = False
        tex_summary.append("\\addlinespace")

    tex_summary += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]

    summary_tex_path = os.path.join(OUT_DIR, "nsga_summary.tex")
    with open(summary_tex_path, "w") as f_out:
        f_out.write("\n".join(tex_summary) + "\n")
    print(f"\n  Wrote nsga_summary.tex")

    summary_txt_path = os.path.join(OUT_DIR, "nsga_summary.txt")
    with open(summary_txt_path, "w") as f_out:
        f_out.write("\n".join(summary_lines) + "\n")
    print(f"  Wrote nsga_summary.txt")

    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
