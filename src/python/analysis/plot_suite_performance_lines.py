#!/usr/bin/env python3
"""One figure per suite: algorithms on X, lines for min/center/max.

Workflow:
1) For each (suite, problem, algorithm), aggregate runs using median (default).
2) Normalize values with min-max *inside each suite* considering all
   algorithms + all instances of that suite.
3) Convert to performance score in [0, 1] (higher is better).
4) For each (suite, algorithm), compute three summary lines across instances:
   - min
   - center (mean by default, optional median)
   - max

Outputs:
  - 4 figures (ZDT, DTLZ, WFG, MaF), each with algorithms on X-axis
  - 1 CSV summary table

Usage:
  python src/python/analysis/plot_suite_performance_lines.py
  python src/python/analysis/plot_suite_performance_lines.py --metric HV
  python src/python/analysis/plot_suite_performance_lines.py --center-stat median
"""

from __future__ import annotations

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA = os.path.join(
    ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_FIG_DIR = os.path.join(ROOT, "results", "figures")
OUT_TABLE_DIR = os.path.join(ROOT, "results", "tables")

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate per-suite line charts with X=algorithms and "
            "Y=normalized min/center/max performance."
        )
    )
    parser.add_argument(
        "--metric",
        default="IGD",
        help="Metric column to analyze (default: IGD)",
    )
    parser.add_argument(
        "--instance-agg",
        choices=["median", "mean"],
        default="median",
        help="Aggregation across runs per instance (default: median)",
    )
    parser.add_argument(
        "--center-stat",
        choices=["mean", "median"],
        default="mean",
        help="Center line across instances (default: mean)",
    )
    parser.add_argument(
        "--out-prefix",
        default="suite_perf_algox",
        help="Output filename prefix (without extension)",
    )
    return parser.parse_args()


def metric_lower_is_better(metric: str) -> bool:
    metric_upper = metric.upper()
    return metric_upper in {"IGD", "IGDP", "SPACING", "SPREAD", "RUNTIME"}


def build_normalized_summary(
    df: pd.DataFrame,
    metric: str,
    instance_agg: str,
    center_stat: str,
    lower_is_better: bool,
) -> pd.DataFrame:
    agg_func = "median" if instance_agg == "median" else "mean"

    # Per-instance representative value: (suite, problem, algorithm)
    per_instance = (
        df.groupby(["Grupo", "Problema", "Algoritmo"], as_index=False)[metric]
        .agg(agg_func)
        .rename(columns={metric: "instance_value"})
    )

    # Min-max normalization inside each suite across all algorithms+instances
    suite_ext = per_instance.groupby("Grupo")["instance_value"].agg(["min", "max"])
    suite_ext = suite_ext.rename(columns={"min": "suite_min", "max": "suite_max"})
    per_instance = per_instance.merge(suite_ext, left_on="Grupo", right_index=True)

    denom = per_instance["suite_max"] - per_instance["suite_min"]
    per_instance["normalized"] = np.where(
        denom > 0,
        (per_instance["instance_value"] - per_instance["suite_min"]) / denom,
        0.5,
    )

    # Convert to score where higher is better
    per_instance["score"] = (
        1.0 - per_instance["normalized"]
        if lower_is_better
        else per_instance["normalized"]
    )

    center_func = "mean" if center_stat == "mean" else "median"

    summary = (
        per_instance.groupby(["Grupo", "Algoritmo"], as_index=False)["score"]
        .agg(
            score_min="min", score_mid=center_func, score_max="max", n_instances="count"
        )
        .copy()
    )

    summary["suite_idx"] = summary["Grupo"].map({s: i for i, s in enumerate(SUITES)})
    summary["algo_idx"] = summary["Algoritmo"].map(
        {a: i for i, a in enumerate(ALGORITHMS)}
    )
    summary = summary.sort_values(["suite_idx", "algo_idx"]).reset_index(drop=True)
    summary["center_stat"] = center_stat
    return summary


def plot_one_suite(
    summary: pd.DataFrame,
    suite: str,
    metric: str,
    center_stat: str,
    out_pdf: str,
    out_png: str,
) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
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

    sub = summary[summary["Grupo"] == suite].set_index("Algoritmo").reindex(ALGORITHMS)
    sub = sub.dropna(subset=["score_min", "score_mid", "score_max"])

    if sub.empty:
        return

    algos = sub.index.tolist()
    x = np.arange(len(algos))
    labels = [ALGO_DISPLAY.get(a, a) for a in algos]

    y_min = sub["score_min"].to_numpy(dtype=float)
    y_mid = sub["score_mid"].to_numpy(dtype=float)
    y_max = sub["score_max"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(9.8, 4.6))

    ax.plot(
        x,
        y_min,
        color="#B2182B",
        marker="v",
        linewidth=1.5,
        markersize=5,
        label="Min",
    )
    ax.plot(
        x,
        y_mid,
        color="#2166AC",
        marker="o",
        linewidth=2.1,
        markersize=5.5,
        label="Medio" if center_stat == "mean" else "Mediana",
    )
    ax.plot(
        x,
        y_max,
        color="#1B9E77",
        marker="^",
        linewidth=1.5,
        markersize=5,
        label="Max",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(-0.03, 1.03)
    ax.set_ylabel("Desempenho normalizado (0-1)")
    ax.set_xlabel("Algoritmo")
    ax.set_title(f"{suite}: min / {center_stat} / max por algoritmo ({metric})")
    ax.grid(True, axis="y", linestyle="--", alpha=0.25)

    direction = (
        "lower is better" if metric_lower_is_better(metric) else "higher is better"
    )
    ax.text(
        0.01,
        0.02,
        f"Normalizacao min-max na suite ({metric}: {direction}).",
        transform=ax.transAxes,
        fontsize=6.5,
        style="italic",
        va="bottom",
    )

    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()

    fig.savefig(out_pdf)
    fig.savefig(out_png)
    plt.close(fig)


def main() -> None:
    args = parse_args()

    if not os.path.isfile(DATA):
        raise FileNotFoundError(f"Data file not found: {DATA}")

    os.makedirs(OUT_FIG_DIR, exist_ok=True)
    os.makedirs(OUT_TABLE_DIR, exist_ok=True)

    raw = pd.read_csv(DATA)
    df = filter_submission_synthetic_cohort(raw)
    df = df[df["Grupo"].isin(SUITES)].copy()
    df = df[df["Algoritmo"].isin(ALGORITHMS)].copy()

    metric = args.metric
    if metric not in df.columns:
        raise ValueError(
            f"Metric '{metric}' not found. Available metrics include: "
            f"{', '.join(c for c in ['IGD', 'HV', 'IGDp', 'Spread', 'Spacing', 'runtime'] if c in df.columns)}"
        )

    df = df.dropna(subset=[metric])
    lower_is_better = metric_lower_is_better(metric)

    summary = build_normalized_summary(
        df=df,
        metric=metric,
        instance_agg=args.instance_agg,
        center_stat=args.center_stat,
        lower_is_better=lower_is_better,
    )

    metric_tag = metric.lower()
    out_csv = os.path.join(OUT_TABLE_DIR, f"{args.out_prefix}_{metric_tag}.csv")
    summary.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

    for suite in SUITES:
        out_pdf = os.path.join(
            OUT_FIG_DIR, f"{args.out_prefix}_{suite.lower()}_{metric_tag}.pdf"
        )
        out_png = os.path.join(
            OUT_FIG_DIR, f"{args.out_prefix}_{suite.lower()}_{metric_tag}.png"
        )
        plot_one_suite(
            summary=summary,
            suite=suite,
            metric=metric,
            center_stat=args.center_stat,
            out_pdf=out_pdf,
            out_png=out_png,
        )
        print(f"Saved: {out_pdf}")
        print(f"Saved: {out_png}")


if __name__ == "__main__":
    main()
