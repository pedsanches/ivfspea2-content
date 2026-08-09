#!/usr/bin/env python3
"""
Statistical analysis and LaTeX table generation for IVF host comparisons.

Reads:  data/processed/hosts_paper.csv
Writes: results/tables/hosts_*_m*.tex
        results/tables/hosts_*_stats.csv
        results/tables/hosts_summary.tex
        results/tables/hosts_summary.txt
        results/tables/hosts_cross_host_ivf_{metric}.csv
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_paper.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "results", "tables")

ALPHA = 0.05

PROBLEM_ORDER_M2 = [
    "ZDT1",
    "ZDT2",
    "ZDT3",
    "ZDT4",
    "ZDT6",
    "DTLZ1",
    "DTLZ2",
    "DTLZ3",
    "DTLZ4",
    "DTLZ5",
    "DTLZ6",
    "DTLZ7",
    "WFG1",
    "WFG2",
    "WFG3",
    "WFG4",
    "WFG5",
    "WFG6",
    "WFG7",
    "WFG8",
    "WFG9",
    "MaF1",
    "MaF2",
    "MaF3",
    "MaF4",
    "MaF5",
    "MaF6",
    "MaF7",
]
PROBLEM_ORDER_M3 = [
    "DTLZ1",
    "DTLZ2",
    "DTLZ3",
    "DTLZ4",
    "DTLZ5",
    "DTLZ6",
    "DTLZ7",
    "WFG1",
    "WFG2",
    "WFG3",
    "WFG4",
    "WFG5",
    "WFG6",
    "WFG7",
    "WFG8",
    "WFG9",
    "MaF1",
    "MaF2",
    "MaF3",
    "MaF4",
    "MaF5",
    "MaF6",
    "MaF7",
]

TRACKS = [
    ("IVFSPEA2", "SPEA2", "IVF/SPEA2", "SPEA2"),
    ("IVFNSGAII", "NSGAII", "IVF/NSGA-II", "NSGA-II"),
    ("IVFNSGAIII", "NSGAIII", "IVF/NSGA-III", "NSGA-III"),
]

IVF_ALGOS = ["IVFSPEA2", "IVFNSGAII", "IVFNSGAIII"]
SUMMARY_ORDER = ["IVFSPEA2", "IVFNSGAIII", "IVFNSGAII"]
IVF_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "IVFNSGAII": "IVF/NSGA-II",
    "IVFNSGAIII": "IVF/NSGA-III",
}


def bh_correction(pvals: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    n = len(pvals)
    if n == 0:
        return np.array([], dtype=bool)
    order = np.argsort(pvals)
    ranked_pvals = pvals[order]
    thresholds = np.arange(1, n + 1) / n * alpha
    below = ranked_pvals <= thresholds
    if below.any():
        cutoff = np.where(below)[0].max()
        rejected = np.zeros(n, dtype=bool)
        rejected[order[: cutoff + 1]] = True
    else:
        rejected = np.zeros(n, dtype=bool)
    return rejected


def vargha_delaney_a12(x: np.ndarray, y: np.ndarray) -> float:
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return np.nan
    r = stats.rankdata(np.concatenate([x, y]))
    rx = r[:nx].sum()
    return (rx / nx - (nx + 1) / 2) / ny


def sign_str(ivf_val: float, base_val: float, rejected: bool, metric: str) -> str:
    if not rejected:
        return "="
    if metric == "IGD":
        return "+" if ivf_val < base_val else "-"
    return "+" if ivf_val > base_val else "-"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    required = {"algo", "problem", "group", "M", "D", "run", "IGD", "HV"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def align_paired_runs(
    ivf_sub: pd.DataFrame, base_sub: pd.DataFrame, metric: str
) -> pd.DataFrame:
    """Align paired samples by sorted run order within an instance.

    The unified hosts dataset mixes absolute run-id spaces across hosts
    (e.g. IVFSPEA2 3001-3030 vs SPEA2 1-30), so positional alignment is the
    stable pairing available across all tracks.
    """
    ivf_sorted = ivf_sub[["run", metric]].sort_values("run").reset_index(drop=True)
    base_sorted = base_sub[["run", metric]].sort_values("run").reset_index(drop=True)
    n = min(len(ivf_sorted), len(base_sorted))
    if n < 2:
        return pd.DataFrame()
    paired = pd.DataFrame(
        {
            "pair_order": np.arange(n, dtype=int),
            "run_ivf": ivf_sorted.loc[: n - 1, "run"].to_numpy(),
            f"{metric}_ivf": ivf_sorted.loc[: n - 1, metric].to_numpy(dtype=float),
            "run_base": base_sorted.loc[: n - 1, "run"].to_numpy(),
            f"{metric}_base": base_sorted.loc[: n - 1, metric].to_numpy(dtype=float),
        }
    )
    return paired


def analyze_track(
    df: pd.DataFrame, ivf_algo: str, base_algo: str, metric: str
) -> pd.DataFrame:
    df_ivf = df[df["algo"] == ivf_algo]
    df_base = df[df["algo"] == base_algo]
    problems = df_ivf[["problem", "M"]].drop_duplicates().sort_values(["M", "problem"])

    rows = []
    for _, (problem, m_val) in problems.iterrows():
        ivf_sub = df_ivf[(df_ivf["problem"] == problem) & (df_ivf["M"] == m_val)]
        base_sub = df_base[(df_base["problem"] == problem) & (df_base["M"] == m_val)]
        merged = align_paired_runs(ivf_sub, base_sub, metric)

        if len(merged) < 2:
            continue

        ivf_runs = merged[f"{metric}_ivf"].to_numpy(dtype=float)
        base_runs = merged[f"{metric}_base"].to_numpy(dtype=float)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, pval = stats.wilcoxon(ivf_runs, base_runs, alternative="two-sided")

        rows.append(
            {
                "problem": problem,
                "M": int(m_val),
                "group": ivf_sub["group"].iloc[0],
                "median_ivf": float(np.median(ivf_runs)),
                "iqr_ivf": float(
                    np.percentile(ivf_runs, 75) - np.percentile(ivf_runs, 25)
                ),
                "median_base": float(np.median(base_runs)),
                "iqr_base": float(
                    np.percentile(base_runs, 75) - np.percentile(base_runs, 25)
                ),
                "pval": float(pval),
                "A12": float(vargha_delaney_a12(ivf_runs, base_runs)),
                "n_runs": int(len(merged)),
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    result["significant"] = bh_correction(result["pval"].to_numpy(dtype=float))
    result["sign"] = [
        sign_str(row["median_ivf"], row["median_base"], row["significant"], metric)
        for _, row in result.iterrows()
    ]
    return result


def make_latex_table(
    result: pd.DataFrame, ivf_label: str, base_label: str, metric: str, m_val: int
) -> str:
    sub = result[result["M"] == m_val].copy()
    order = PROBLEM_ORDER_M2 if m_val == 2 else PROBLEM_ORDER_M3
    sub["_order"] = sub["problem"].apply(
        lambda p: order.index(p) if p in order else 999
    )
    sub = sub.sort_values(["_order", "problem"]).reset_index(drop=True)
    newline = r"\\"

    caption = (
        f"Median ({metric}) and IQR for $M={m_val}$ objectives. "
        f"Sign column: \\texttt{{+}} means {ivf_label} wins, "
        f"\\texttt{{-}} means {base_label} wins, "
        f"\\texttt{{=}} means no significant difference "
        f"(Wilcoxon, BH-corrected $\\alpha=0.05$)."
    )
    label = f"tab:{metric.lower()}_m{m_val}_{ivf_label.lower().replace('/', '').replace('-', '')}"

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\scriptsize",
        "\\begin{tabular}{llrrrrl}",
        "\\toprule",
        f"Group & Problem & \\multicolumn{{2}}{{c}}{{{ivf_label}}} & \\multicolumn{{2}}{{c}}{{{base_label}}} & Sign {newline}",
        "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}",
        f" & & Median & IQR & Median & IQR & {newline}",
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
            "\\textbf{+}" if sign == "+" else "\\textbf{-}" if sign == "-" else "="
        )

        def fmt(value: float) -> str:
            if np.isnan(value) or value == 0:
                return "---"
            exp = int(np.floor(np.log10(abs(value))))
            mant = value / 10**exp
            return f"${mant:.2f}\\!\\times\\!10^{{{exp}}}$"

        lines.append(
            f"{row['group']} & {row['problem']} & "
            f"{fmt(row['median_ivf'])} & {fmt(row['iqr_ivf'])} & "
            f"{fmt(row['median_base'])} & {fmt(row['iqr_base'])} & "
            f"{sign_tex} {newline}"
        )

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    return "\n".join(lines)


def summary_counts(result: pd.DataFrame) -> dict:
    counts = result["sign"].value_counts().to_dict()
    return {
        "wins": counts.get("+", 0),
        "ties": counts.get("=", 0),
        "losses": counts.get("-", 0),
    }


def ivf_favoring_a12(a12: float, metric: str) -> float:
    if np.isnan(a12):
        return np.nan
    return 1.0 - a12 if metric == "IGD" else a12


def a12_magnitude(a12_favoring: float) -> str:
    if np.isnan(a12_favoring):
        return "n/a"
    if a12_favoring >= 0.71:
        return "large"
    if a12_favoring >= 0.64:
        return "medium"
    if a12_favoring >= 0.56:
        return "small"
    return "negligible"


def format_magnitude_triplet(counts: dict[str, int]) -> str:
    return f"{counts['small']}/{counts['medium']}/{counts['large']}"


def make_cross_host_summary_tex(cross_summaries: dict[str, pd.DataFrame]) -> str:
    newline = r"\\"
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Absolute cross-host ranking among IVF variants. Best counts report the number of instances in which the IVF variant attains the best absolute median among the three IVF hosts.}",
        "\\label{tab:cross_host_absolute}",
        "\\small",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        f"Track & IGD bests & IGD mean rank & HV bests & HV mean rank {newline}",
        "\\midrule",
    ]

    igd = cross_summaries["IGD"].set_index("algo")
    hv = cross_summaries["HV"].set_index("algo")
    for algo in SUMMARY_ORDER:
        lines.append(
            f"{IVF_DISPLAY[algo]} & "
            f"{int(igd.loc[algo, 'best_count'])}/{int(igd.loc[algo, 'instances'])} & "
            f"{igd.loc[algo, 'mean_rank']:.2f} & "
            f"{int(hv.loc[algo, 'best_count'])}/{int(hv.loc[algo, 'instances'])} & "
            f"{hv.loc[algo, 'mean_rank']:.2f} {newline}"
        )

    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    return "\n".join(lines)


def a12_summary_lines(
    results_by_track_metric: dict[tuple[str, str], pd.DataFrame],
) -> list[str]:
    """Aggregate the oriented effect sizes behind Table~\\ref{tab:a12_summary}.

    The LaTeX table itself lives in ``results/tables/hosts_a12_summary.tex`` and
    is maintained by hand, so these numbers are reported as text only: compare
    them against that file after any data refresh.
    """
    lines = [
        "",
        "  Oriented A12 (>0.5 favors IVF; A12_ivf = 1-A12 for IGD, A12 for HV).",
        "  Triplets count significant wins/losses at magnitude small/medium/large",
        "  using the thresholds 0.56/0.64/0.71.",
    ]

    for algo in SUMMARY_ORDER:
        for metric in ("IGD", "HV"):
            result = results_by_track_metric[(algo, metric)]
            a12_values = result["A12"].apply(lambda val: ivf_favoring_a12(val, metric))
            median_a12 = float(np.nanmedian(a12_values.to_numpy(dtype=float)))

            win_counts = {"small": 0, "medium": 0, "large": 0}
            loss_counts = {"small": 0, "medium": 0, "large": 0}

            for _, row in result.iterrows():
                if not row["significant"]:
                    continue

                ivf_a12 = ivf_favoring_a12(float(row["A12"]), metric)
                if row["sign"] == "+":
                    magnitude = a12_magnitude(ivf_a12)
                    if magnitude in win_counts:
                        win_counts[magnitude] += 1
                elif row["sign"] == "-":
                    magnitude = a12_magnitude(1.0 - ivf_a12)
                    if magnitude in loss_counts:
                        loss_counts[magnitude] += 1

            lines.append(
                f"    {IVF_DISPLAY[algo]:<14} {metric:<3}: median={median_a12:.3f}, "
                f"IVF wins={format_magnitude_triplet(win_counts)}, "
                f"base wins={format_magnitude_triplet(loss_counts)}"
            )

    return lines


def rank_cross_host_ivf(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    higher_is_better = metric == "HV"

    for (problem, m_val), sub in df[df["algo"].isin(IVF_ALGOS)].groupby(
        ["problem", "M"]
    ):
        medians = sub.groupby("algo")[metric].median()
        if set(medians.index) != set(IVF_ALGOS):
            continue

        ranks = medians.rank(method="min", ascending=not higher_is_better)
        best_value = medians.max() if higher_is_better else medians.min()
        group = sub["group"].iloc[0]

        for algo in IVF_ALGOS:
            rows.append(
                {
                    "problem": problem,
                    "M": int(m_val),
                    "group": group,
                    "metric": metric,
                    "algo": algo,
                    "algo_label": IVF_DISPLAY[algo],
                    "median": float(medians[algo]),
                    "rank": int(ranks[algo]),
                    "is_best": bool(np.isclose(medians[algo], best_value)),
                }
            )

    return pd.DataFrame(rows)


def cross_host_summary(cross_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for algo in IVF_ALGOS:
        algo_sub = cross_df[cross_df["algo"] == algo]
        rows.append(
            {
                "algo": algo,
                "algo_label": IVF_DISPLAY[algo],
                "instances": int(len(algo_sub)),
                "best_count": int(algo_sub["is_best"].sum()),
                "mean_rank": float(algo_sub["rank"].mean()),
                "median_rank": float(algo_sub["rank"].median()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=== Hosts Paper - Statistical Analysis ===\n")

    if not os.path.isfile(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found. Run build_hosts_paper_csv.py first.")
        sys.exit(1)

    df = load_data()
    print(f"Loaded {len(df)} rows from {CSV_PATH}\n")

    summary_lines = []
    newline = r"\\"
    results_by_track_metric = {}
    cross_summaries = {}

    for ivf_algo, base_algo, ivf_label, base_label in TRACKS:
        summary_lines.append(f"\n{'=' * 60}")
        summary_lines.append(f"Track: {ivf_label} vs {base_label}")
        summary_lines.append("=" * 60)

        for metric in ("IGD", "HV"):
            result = analyze_track(df, ivf_algo, base_algo, metric)
            if result.empty:
                print(f"  No data for {ivf_algo} vs {base_algo} / {metric}")
                continue

            results_by_track_metric[(ivf_algo, metric)] = result

            counts_all = summary_counts(result)
            summary_lines.append(
                f"\n  {metric}: +{counts_all['wins']} / ={counts_all['ties']} / -{counts_all['losses']}  (total {len(result)})"
            )

            for m_val in sorted(result["M"].unique()):
                sub = result[result["M"] == m_val]
                c = summary_counts(sub)
                summary_lines.append(
                    f"    M={int(m_val)}: +{c['wins']} / ={c['ties']} / -{c['losses']}"
                )

            for m_val in sorted(result["M"].unique()):
                tex = make_latex_table(
                    result, ivf_label, base_label, metric, int(m_val)
                )
                fname = f"hosts_{ivf_algo.lower()}_{metric.lower()}_m{int(m_val)}.tex"
                with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f_out:
                    f_out.write(tex + "\n")
                print(f"  Wrote {fname}")

            stats_name = f"hosts_{ivf_algo.lower()}_{metric.lower()}_stats.csv"
            result.to_csv(os.path.join(OUT_DIR, stats_name), index=False)
            print(f"  Wrote {stats_name}")

    tex_summary = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Win/tie/loss counts (Wilcoxon, BH $\\alpha=0.05$) for IVF variants vs their respective base algorithms across the unified 51-instance host-comparison benchmark.}",
        "\\label{tab:hosts_summary}",
        "\\begin{tabular}{llcrrrr}",
        "\\toprule",
        f"Algorithm & Metric & $M$ & Wins & Ties & Losses & Total {newline}",
        "\\midrule",
    ]

    for ivf_algo, base_algo, ivf_label, _ in TRACKS:
        first_row = True
        for metric in ("IGD", "HV"):
            result = results_by_track_metric.get((ivf_algo, metric))
            if result is None or result.empty:
                continue
            for m_val in sorted(result["M"].unique()):
                sub = result[result["M"] == m_val]
                c = summary_counts(sub)
                algo_str = ivf_label if first_row else ""
                tex_summary.append(
                    f"{algo_str} & {metric} & {int(m_val)} & {c['wins']} & {c['ties']} & {c['losses']} & {len(sub)} {newline}"
                )
                first_row = False
        tex_summary.append("\\addlinespace")

    tex_summary += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]

    with open(
        os.path.join(OUT_DIR, "hosts_summary.tex"), "w", encoding="utf-8"
    ) as f_out:
        f_out.write("\n".join(tex_summary) + "\n")
    print("\n  Wrote hosts_summary.tex")

    summary_lines.append("\n\n" + "=" * 60)
    summary_lines.append("CROSS-HOST IVF SUMMARY")
    summary_lines.append("=" * 60)
    for metric in ("IGD", "HV"):
        cross_df = rank_cross_host_ivf(df, metric)
        cross_name = f"hosts_cross_host_ivf_{metric.lower()}.csv"
        cross_df.to_csv(os.path.join(OUT_DIR, cross_name), index=False)
        cross_sum = cross_host_summary(cross_df).sort_values(
            ["mean_rank", "algo_label"]
        )
        cross_summaries[metric] = cross_sum.copy()
        summary_lines.append(f"\n  {metric} absolute ranking among IVF hosts:")
        for _, row in cross_sum.iterrows():
            summary_lines.append(
                f"    {row['algo_label']}: best={int(row['best_count'])}/{int(row['instances'])}, mean-rank={row['mean_rank']:.2f}"
            )
        print(f"  Wrote {cross_name}")

    cross_tex = make_cross_host_summary_tex(cross_summaries)
    with open(
        os.path.join(OUT_DIR, "hosts_cross_host_summary.tex"), "w", encoding="utf-8"
    ) as f_out:
        f_out.write(cross_tex + "\n")
    print("  Wrote hosts_cross_host_summary.tex")

    # results/tables/hosts_a12_summary.tex is hand-maintained (camera-ready
    # formatting); only its numbers are recomputed here, into hosts_summary.txt.
    summary_lines.append("\n\n" + "=" * 60)
    summary_lines.append("EFFECT-SIZE SUMMARY (tab:a12_summary)")
    summary_lines.append("=" * 60)
    summary_lines += a12_summary_lines(results_by_track_metric)

    with open(
        os.path.join(OUT_DIR, "hosts_summary.txt"), "w", encoding="utf-8"
    ) as f_out:
        f_out.write("\n".join(summary_lines) + "\n")
    print("  Wrote hosts_summary.txt")

    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
