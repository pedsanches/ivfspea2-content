#!/usr/bin/env python3
"""IVF competence summary figure.

Produces a compact 2-panel figure:
  (a) Win/Tie/Loss counts of IVF/SPEA2 vs SPEA2 by suite (IGD medians per problem)
  (b) IVF/SPEA2 average rank by suite among all algorithms (lower is better)

This is designed as a clear "competence" visual that avoids over-penalizing
single outliers from min-based summaries.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA = os.path.join(
    ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_DIR = os.path.join(ROOT, "paper", "figures")

SUITES = ["ZDT", "DTLZ", "WFG", "MaF"]
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


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for suite in SUITES:
        block = df[df["Grupo"] == suite]
        problems = sorted(block["Problema"].unique())

        wins = 0
        ties = 0
        losses = 0
        ivf_ranks = []

        for prob in problems:
            g = block[block["Problema"] == prob]

            med = {}
            for algo in ALGORITHMS:
                vals = g[g["Algoritmo"] == algo]["IGD"].dropna()
                med[algo] = float(vals.median()) if len(vals) else np.inf

            ivf = med["IVFSPEA2"]
            sp = med["SPEA2"]
            if ivf < sp:
                wins += 1
            elif ivf > sp:
                losses += 1
            else:
                ties += 1

            vec = np.array([med[a] for a in ALGORITHMS], dtype=float)
            r = rankdata(vec, method="average")
            ivf_ranks.append(float(r[ALGORITHMS.index("IVFSPEA2")]))

        n = len(problems)
        rows.append(
            {
                "suite": suite,
                "n_problems": n,
                "wins": wins,
                "ties": ties,
                "losses": losses,
                "win_rate": wins / n if n else np.nan,
                "avg_rank": float(np.mean(ivf_ranks)) if ivf_ranks else np.nan,
            }
        )

    return pd.DataFrame(rows)


def plot(summary: pd.DataFrame, out_pdf: str, out_png: str) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )

    x = np.arange(len(SUITES))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 3.6))

    # (a) Win/Tie/Loss vs SPEA2
    wins = summary["wins"].to_numpy(dtype=float)
    ties = summary["ties"].to_numpy(dtype=float)
    losses = summary["losses"].to_numpy(dtype=float)

    ax1.bar(x, wins, color="#2166AC", label="Wins")
    ax1.bar(x, ties, bottom=wins, color="#BDBDBD", label="Ties")
    ax1.bar(x, losses, bottom=wins + ties, color="#B2182B", label="Losses")
    ax1.set_xticks(x)
    ax1.set_xticklabels(SUITES)
    ax1.set_ylabel("Number of problems")
    ax1.set_title("(a) IVF/SPEA2 vs SPEA2 (IGD)")
    ax1.grid(True, axis="y", linestyle="--", alpha=0.25)

    for i, row in summary.iterrows():
        ax1.text(
            i,
            row["n_problems"] + 0.15,
            f"{int(row['wins'])}/{int(row['n_problems'])}",
            ha="center",
            fontsize=7,
        )

    ax1.legend(loc="upper right", frameon=True)

    # (b) Average rank among all algorithms
    avg_rank = summary["avg_rank"].to_numpy(dtype=float)
    colors = [
        "#2166AC" if r <= 2.0 else ("#67A9CF" if r <= 3.5 else "#BDBDBD")
        for r in avg_rank
    ]

    bars = ax2.bar(x, avg_rank, color=colors, edgecolor="black", linewidth=0.4)
    ax2.set_xticks(x)
    ax2.set_xticklabels(SUITES)
    ax2.set_ylabel("Average rank (1 = best)")
    ax2.set_title("(b) IVF/SPEA2 rank vs all algorithms")
    ax2.set_ylim(0.8, 9.2)
    ax2.invert_yaxis()
    ax2.grid(True, axis="y", linestyle="--", alpha=0.25)
    ax2.axhline(3.0, color="#555555", linestyle=":", linewidth=0.9)

    for b, r in zip(bars, avg_rank):
        ax2.text(
            b.get_x() + b.get_width() / 2,
            r - 0.18,
            f"{r:.2f}",
            ha="center",
            va="top",
            fontsize=7,
        )

    fig.suptitle(
        "IVF/SPEA2 competence summary across benchmark suites", y=1.02, fontsize=10
    )
    plt.tight_layout(w_pad=1.5)

    fig.savefig(out_pdf)
    fig.savefig(out_png)
    plt.close(fig)


def main() -> None:
    if not os.path.isfile(DATA):
        raise FileNotFoundError(f"Data file not found: {DATA}")

    os.makedirs(OUT_DIR, exist_ok=True)

    raw = pd.read_csv(DATA)
    df = filter_submission_synthetic_cohort(raw)
    df = df[df["Grupo"].isin(SUITES)].copy()
    df = df[df["Algoritmo"].isin(ALGORITHMS)].copy()

    summary = compute_summary(df)

    out_pdf = os.path.join(OUT_DIR, "ivf_competence_summary.pdf")
    out_png = os.path.join(OUT_DIR, "ivf_competence_summary.png")
    out_csv = os.path.join(ROOT, "results", "tables", "ivf_competence_summary.csv")

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    summary.to_csv(out_csv, index=False)
    plot(summary, out_pdf=out_pdf, out_png=out_png)

    print(f"Saved: {out_pdf}")
    print(f"Saved: {out_png}")
    print(f"Saved: {out_csv}")


if __name__ == "__main__":
    main()
