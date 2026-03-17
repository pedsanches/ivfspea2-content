#!/usr/bin/env python3
"""
Plot engineering-suite metric profiles with valid-run annotations.

Outputs:
  - paper/figures/engineering_metric_profiles.pdf
  - results/tables/engineering_metric_profiles_summary.csv

Method:
  - Use MAIN engineering raw results (strict common-run cohort).
  - For each problem and algorithm, compute median, Q1, Q3, and valid n.
  - Plot point-range charts (median with IQR interval) for IGD and HV.
  - Annotate each row with valid sample size (n=...).
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
RAW_MAIN = os.path.join(
    ROOT, "results", "engineering_suite", "engineering_suite_raw_main.csv"
)
OUT_FIG = os.path.join(ROOT, "paper", "figures", "engineering_metric_profiles.pdf")
OUT_TABLE = os.path.join(
    ROOT, "results", "tables", "engineering_metric_profiles_summary.csv"
)

PROBLEM_ORDER = ["RWMOP9", "RWMOP21", "RWMOP8"]
PROBLEM_LABELS = {
    "RWMOP9": "RWMOP9 (M=2)",
    "RWMOP21": "RWMOP21 (M=2)",
    "RWMOP8": "RWMOP8 (M=3)",
}

ALGO_ORDER = [
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
    "MFOSPEA2": "MFO/SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-MOEA-II",
    "ARMOEA": "AR-MOEA",
}


def summarize(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    for problem in PROBLEM_ORDER:
        sub_p = df[df["Problem"] == problem]
        for algo in ALGO_ORDER:
            vals = (
                sub_p[sub_p["Algorithm"] == algo][metric]
                .replace([np.inf, -np.inf], np.nan)
                .dropna()
                .values
            )
            if len(vals) == 0:
                rows.append(
                    {
                        "Problem": problem,
                        "Algorithm": algo,
                        "Display": ALGO_DISPLAY[algo],
                        "Metric": metric,
                        "n_valid": 0,
                        "median": np.nan,
                        "q1": np.nan,
                        "q3": np.nan,
                    }
                )
                continue

            q1, med, q3 = np.percentile(vals, [25, 50, 75])
            rows.append(
                {
                    "Problem": problem,
                    "Algorithm": algo,
                    "Display": ALGO_DISPLAY[algo],
                    "Metric": metric,
                    "n_valid": int(len(vals)),
                    "median": float(med),
                    "q1": float(q1),
                    "q3": float(q3),
                }
            )
    return pd.DataFrame(rows)


def plot_panel(ax: plt.Axes, data: pd.DataFrame, metric: str, problem: str) -> None:
    keep = data[(data["Metric"] == metric) & (data["Problem"] == problem)].copy()

    valid = keep[keep["n_valid"] > 0].copy()
    if valid.empty:
        ax.text(0.5, 0.5, "No valid runs", ha="center", va="center")
        return

    ascending = metric == "IGD_PF"
    valid = valid.sort_values("median", ascending=ascending)

    y = np.arange(len(valid))
    med = valid["median"].to_numpy()
    xerr = np.vstack([med - valid["q1"].to_numpy(), valid["q3"].to_numpy() - med])

    colors = ["#2166AC" if a == "IVFSPEA2" else "#A9A9A9" for a in valid["Algorithm"]]
    markers = ["o" if a == "IVFSPEA2" else "s" for a in valid["Algorithm"]]

    for i in range(len(valid)):
        ax.errorbar(
            med[i],
            y[i],
            xerr=[[xerr[0, i]], [xerr[1, i]]],
            fmt=markers[i],
            color=colors[i],
            ecolor=colors[i],
            elinewidth=1.1,
            capsize=2,
            markersize=4,
            markeredgecolor="black",
            markeredgewidth=0.4,
            zorder=3,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(valid["Display"].tolist(), fontsize=8)
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.25)

    if metric == "IGD_PF":
        ax.set_xscale("log")
        ax.set_xlabel("IGD (median, IQR interval)", fontsize=8)
    else:
        ax.set_xlabel("HV (median, IQR interval)", fontsize=8)

    x_min, x_max = ax.get_xlim()
    span = x_max - x_min if np.isfinite(x_max - x_min) else 1.0

    for yi, n in zip(y, valid["n_valid"].to_numpy()):
        if metric == "IGD_PF":
            x_text = x_max / (10**0.03)
        else:
            x_text = x_max - 0.01 * span
        ax.text(
            x_text, yi, f"n={n}", ha="right", va="center", fontsize=7, color="#333333"
        )

    ax.set_title(PROBLEM_LABELS[problem], fontsize=9)


def main() -> None:
    if not os.path.exists(RAW_MAIN):
        raise FileNotFoundError(f"Missing input file: {RAW_MAIN}")

    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_TABLE), exist_ok=True)

    raw = pd.read_csv(RAW_MAIN)
    raw = raw[raw["Stage"] == "MAIN"].copy()

    sum_igd = summarize(raw, "IGD_PF")
    sum_hv = summarize(raw, "HV")
    summary = pd.concat([sum_igd, sum_hv], ignore_index=True)
    summary.to_csv(OUT_TABLE, index=False)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.titlesize": 9,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )

    fig, axes = plt.subplots(3, 2, figsize=(10.8, 9.0))

    for r, problem in enumerate(PROBLEM_ORDER):
        plot_panel(axes[r, 0], summary, "IGD_PF", problem)
        plot_panel(axes[r, 1], summary, "HV", problem)

    axes[0, 0].set_title(f"{PROBLEM_LABELS[PROBLEM_ORDER[0]]} - IGD", fontsize=9)
    axes[0, 1].set_title(f"{PROBLEM_LABELS[PROBLEM_ORDER[0]]} - HV", fontsize=9)
    axes[1, 0].set_title(f"{PROBLEM_LABELS[PROBLEM_ORDER[1]]} - IGD", fontsize=9)
    axes[1, 1].set_title(f"{PROBLEM_LABELS[PROBLEM_ORDER[1]]} - HV", fontsize=9)
    axes[2, 0].set_title(f"{PROBLEM_LABELS[PROBLEM_ORDER[2]]} - IGD", fontsize=9)
    axes[2, 1].set_title(f"{PROBLEM_LABELS[PROBLEM_ORDER[2]]} - HV", fontsize=9)

    fig.suptitle(
        "Engineering-suite metric profiles with valid-run counts\n"
        "(points: median; whiskers: Q1-Q3; labels: valid n per algorithm)",
        y=0.995,
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(OUT_FIG)
    plt.close(fig)

    print("Saved:")
    print(f"  {OUT_FIG}")
    print(f"  {OUT_TABLE}")


if __name__ == "__main__":
    main()
