#!/usr/bin/env python3
"""
Generate exploratory Friedman-style average-rank charts (IGD) for M2 and M3.

Methodological scope:
  - Per problem instance, rank algorithms by median IGD (lower is better).
  - Average ranks across instances within each objective-count group (M2, M3).
  - Report Friedman chi-square, p-value, and Kendall's W for each group.

This figure is intended as navigational/exploratory evidence and does not replace
the primary pairwise IVF/SPEA2-vs-SPEA2 inference protocol.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, rankdata

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA = os.path.join(
    ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_TABLES = os.path.join(ROOT, "results", "tables")
OUT_FIG = os.path.join(ROOT, "paper", "figures", "friedman_avg_rank_igd.pdf")

ALGORITHMS = [
    "IVFSPEA2",
    "SPEA2",
    "MFOSPEA2",
    "SPEA2SDE",
    "NSGAII",
    "NSGAIII",
    "MOEAD",
    "AGEMOEAII",
    "ARMOEA",
]

ALGO_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-MOEA-II",
    "ARMOEA": "AR-MOEA",
}

SUITE_ORDER = {"ZDT": 0, "DTLZ": 1, "WFG": 2, "MaF": 3, "RWMOP": 4}


@dataclass
class FriedmanSummary:
    m_group: str
    n_instances: int
    n_algorithms: int
    chi2: float
    p_value: float
    kendalls_w: float


def suite_sort_key(problem: str) -> tuple[int, int, str]:
    for prefix, order in SUITE_ORDER.items():
        if problem.startswith(prefix):
            num_str = problem[len(prefix) :]
            m = re.search(r"\d+", num_str)
            num = int(m.group()) if m else 0
            return order, num, problem
    return 99, 0, problem


def build_rank_matrix(df_m: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (rank_matrix, median_matrix), rows=instances cols=algorithms."""
    problems = sorted(df_m["Problema"].unique(), key=suite_sort_key)

    rank_rows = []
    median_rows = []
    for prob in problems:
        row = {"Problema": prob}
        med = {}
        block = df_m[df_m["Problema"] == prob]

        for algo in ALGORITHMS:
            vals = block[block["Algoritmo"] == algo]["IGD"].dropna().values
            med[algo] = float(np.median(vals)) if len(vals) > 0 else np.inf
            row[f"{algo}_median"] = med[algo]

        median_rows.append(row)

        med_vec = np.array([med[a] for a in ALGORITHMS], dtype=float)
        ranks = rankdata(med_vec, method="average")
        rank_rows.append(
            {"Problema": prob, **{a: float(r) for a, r in zip(ALGORITHMS, ranks)}}
        )

    rank_df = pd.DataFrame(rank_rows).set_index("Problema")
    med_df = pd.DataFrame(median_rows)
    return rank_df, med_df


def friedman_from_rank_matrix(rank_df: pd.DataFrame, m_group: str) -> FriedmanSummary:
    data = [rank_df[a].values for a in ALGORITHMS]
    chi2, p = friedmanchisquare(*data)
    n = rank_df.shape[0]
    k = len(ALGORITHMS)
    w = float(chi2 / (n * (k - 1)))
    return FriedmanSummary(
        m_group=m_group,
        n_instances=n,
        n_algorithms=k,
        chi2=float(chi2),
        p_value=float(p),
        kendalls_w=w,
    )


def plot_rank_panels(
    rank_m2: pd.DataFrame, rank_m3: pd.DataFrame, out_file: str
) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2), sharex=True)

    for ax, rank_df, title in zip(axes, [rank_m2, rank_m3], ["M=2", "M=3"]):
        avg = rank_df.mean(axis=0)
        sd = rank_df.std(axis=0, ddof=1)
        order = avg.sort_values().index.tolist()

        labels = [ALGO_DISPLAY[a] for a in order]
        values = avg[order].values
        errors = sd[order].values

        colors = ["#2166AC" if a == "IVFSPEA2" else "#BDBDBD" for a in order]
        bars = ax.barh(
            np.arange(len(order)),
            values,
            xerr=errors,
            color=colors,
            edgecolor="black",
            linewidth=0.5,
            alpha=0.9,
            error_kw={"elinewidth": 0.8, "capsize": 2, "ecolor": "black"},
        )

        ax.set_yticks(np.arange(len(order)))
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_title(f"Average rank by instance ({title})")
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        for b, v in zip(bars, values):
            ax.text(
                v + 0.05,
                b.get_y() + b.get_height() / 2,
                f"{v:.2f}",
                va="center",
                ha="left",
                fontsize=7,
            )

    axes[0].set_ylabel("Algorithm")
    axes[0].set_xlabel("Average rank (lower is better)")
    axes[1].set_xlabel("Average rank (lower is better)")

    fig.suptitle(
        "Exploratory global ranking: Friedman-style average IGD ranks\n"
        "(ranked per instance by median IGD, then averaged)",
        y=1.03,
    )

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    fig.savefig(out_file)
    plt.close(fig)


def main() -> None:
    if not os.path.exists(DATA):
        raise FileNotFoundError(f"Data file not found: {DATA}")

    os.makedirs(OUT_TABLES, exist_ok=True)

    raw = pd.read_csv(DATA)
    df = filter_submission_synthetic_cohort(raw)
    df = df[df["Algoritmo"].isin(ALGORITHMS)].copy()

    # M2
    df_m2 = df[df["M"] == "M2"].copy()
    rank_m2, med_m2 = build_rank_matrix(df_m2)
    sum_m2 = friedman_from_rank_matrix(rank_m2, "M2")

    # M3
    df_m3 = df[df["M"] == "M3"].copy()
    rank_m3, med_m3 = build_rank_matrix(df_m3)
    sum_m3 = friedman_from_rank_matrix(rank_m3, "M3")

    # Combined (51 instances)
    rank_all = pd.concat([rank_m2, rank_m3], axis=0)
    sum_all = friedman_from_rank_matrix(rank_all, "M2+M3")

    # Save rank summaries
    avg_m2 = (
        rank_m2.mean(axis=0)
        .rename("avg_rank")
        .reset_index()
        .rename(columns={"index": "algorithm"})
    )
    avg_m2["display"] = avg_m2["algorithm"].map(ALGO_DISPLAY)
    avg_m2 = avg_m2.sort_values("avg_rank", ascending=True)
    avg_m2.to_csv(os.path.join(OUT_TABLES, "friedman_avg_rank_igd_M2.csv"), index=False)

    avg_m3 = (
        rank_m3.mean(axis=0)
        .rename("avg_rank")
        .reset_index()
        .rename(columns={"index": "algorithm"})
    )
    avg_m3["display"] = avg_m3["algorithm"].map(ALGO_DISPLAY)
    avg_m3 = avg_m3.sort_values("avg_rank", ascending=True)
    avg_m3.to_csv(os.path.join(OUT_TABLES, "friedman_avg_rank_igd_M3.csv"), index=False)

    avg_all = (
        rank_all.mean(axis=0)
        .rename("avg_rank")
        .reset_index()
        .rename(columns={"index": "algorithm"})
    )
    avg_all["display"] = avg_all["algorithm"].map(ALGO_DISPLAY)
    avg_all = avg_all.sort_values("avg_rank", ascending=True)
    avg_all.to_csv(
        os.path.join(OUT_TABLES, "friedman_avg_rank_igd_all.csv"), index=False
    )

    pd.DataFrame(
        [
            vars(sum_m2),
            vars(sum_m3),
            vars(sum_all),
        ]
    ).to_csv(os.path.join(OUT_TABLES, "friedman_igd_summary_stats.csv"), index=False)

    # Save per-instance matrices for auditability
    rank_m2.reset_index().to_csv(
        os.path.join(OUT_TABLES, "friedman_rank_matrix_igd_M2.csv"), index=False
    )
    rank_m3.reset_index().to_csv(
        os.path.join(OUT_TABLES, "friedman_rank_matrix_igd_M3.csv"), index=False
    )
    med_m2.to_csv(os.path.join(OUT_TABLES, "median_igd_matrix_M2.csv"), index=False)
    med_m3.to_csv(os.path.join(OUT_TABLES, "median_igd_matrix_M3.csv"), index=False)

    plot_rank_panels(rank_m2, rank_m3, OUT_FIG)

    print("Saved:")
    print(f"  {OUT_FIG}")
    print(f"  {os.path.join(OUT_TABLES, 'friedman_avg_rank_igd_M2.csv')}")
    print(f"  {os.path.join(OUT_TABLES, 'friedman_avg_rank_igd_M3.csv')}")
    print(f"  {os.path.join(OUT_TABLES, 'friedman_avg_rank_igd_all.csv')}")
    print(f"  {os.path.join(OUT_TABLES, 'friedman_igd_summary_stats.csv')}")
    print("Friedman summaries:")
    print(
        f"  M2: chi2={sum_m2.chi2:.4f}, p={sum_m2.p_value:.3e}, W={sum_m2.kendalls_w:.4f}, n={sum_m2.n_instances}"
    )
    print(
        f"  M3: chi2={sum_m3.chi2:.4f}, p={sum_m3.p_value:.3e}, W={sum_m3.kendalls_w:.4f}, n={sum_m3.n_instances}"
    )
    print(
        f"  All: chi2={sum_all.chi2:.4f}, p={sum_all.p_value:.3e}, W={sum_all.kendalls_w:.4f}, n={sum_all.n_instances}"
    )


if __name__ == "__main__":
    main()
