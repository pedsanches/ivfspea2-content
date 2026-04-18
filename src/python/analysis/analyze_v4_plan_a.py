#!/usr/bin/env python3
"""Plan A diagnostic for V4 additional metrics.

Scope: IVF/SPEA2 vs SPEA2 only, restricted to instances with valid coverage.
Generates supplementary CSVs with per-instance pairwise diagnostics and
coverage summaries for Spread, IGDp, and Spacing.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA_PATH = os.path.join(
    ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_DIR = os.path.join(ROOT, "results", "tables")

METRICS = ["Spread", "IGDp", "Spacing"]
MIN_VALID_RUNS = 5


def vargha_delaney_a12(x: np.ndarray, y: np.ndarray) -> float:
    nx, ny = len(x), len(y)
    wins = 0.0
    for xi in x:
        wins += float(np.sum(xi < y)) + 0.5 * float(np.sum(xi == y))
    return wins / (nx * ny)


def iqr(values: np.ndarray) -> float:
    q1, q3 = np.quantile(values, [0.25, 0.75])
    return float(q3 - q1)


def analyze_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for m_group in ["M2", "M3"]:
        df_m = df[df["M"] == m_group]
        problems = sorted(df_m["Problema"].unique())

        for problem in problems:
            ivf_vals = (
                df_m[(df_m["Problema"] == problem) & (df_m["Algoritmo"] == "IVFSPEA2")][
                    metric
                ]
                .dropna()
                .to_numpy()
            )
            spea2_vals = (
                df_m[(df_m["Problema"] == problem) & (df_m["Algoritmo"] == "SPEA2")][
                    metric
                ]
                .dropna()
                .to_numpy()
            )

            n_ivf = int(len(ivf_vals))
            n_spea2 = int(len(spea2_vals))

            sign = "NA"
            p_value = np.nan
            a12 = np.nan
            if n_ivf >= MIN_VALID_RUNS and n_spea2 >= MIN_VALID_RUNS:
                _, p_value = mannwhitneyu(ivf_vals, spea2_vals, alternative="two-sided")
                a12 = vargha_delaney_a12(ivf_vals, spea2_vals)
                if p_value < 0.05:
                    sign = "+" if a12 > 0.5 else "-"
                else:
                    sign = "="

            row: dict[str, object] = {
                "metric": metric,
                "M": m_group,
                "problem": problem,
                "n_ivf": n_ivf,
                "n_spea2": n_spea2,
                "median_ivf": float(np.median(ivf_vals)) if n_ivf else np.nan,
                "median_spea2": float(np.median(spea2_vals)) if n_spea2 else np.nan,
                "iqr_ivf": iqr(ivf_vals) if n_ivf else np.nan,
                "iqr_spea2": iqr(spea2_vals) if n_spea2 else np.nan,
                "p_value": p_value,
                "a12": a12,
                "sign": sign,
            }
            rows.append(row)

    return pd.DataFrame(rows)


def build_coverage_summary(df_pairwise: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for metric in METRICS:
        for m_group in ["M2", "M3", "M2+M3"]:
            sub = df_pairwise[df_pairwise["metric"] == metric]
            if m_group != "M2+M3":
                sub = sub[sub["M"] == m_group]

            total_instances = int(len(sub))
            any_coverage = int(((sub["n_ivf"] > 0) & (sub["n_spea2"] > 0)).sum())
            valid_pairwise = int(
                (
                    (sub["n_ivf"] >= MIN_VALID_RUNS)
                    & (sub["n_spea2"] >= MIN_VALID_RUNS)
                ).sum()
            )
            full_coverage = int(((sub["n_ivf"] == 60) & (sub["n_spea2"] == 60)).sum())

            infer_sub = sub[sub["sign"].isin(["+", "=", "-"])]
            wins = int((infer_sub["sign"] == "+").sum())
            ties = int((infer_sub["sign"] == "=").sum())
            losses = int((infer_sub["sign"] == "-").sum())

            rows.append(
                {
                    "metric": metric,
                    "M": m_group,
                    "instances_total": total_instances,
                    "instances_any_coverage": any_coverage,
                    "instances_valid_pairwise": valid_pairwise,
                    "instances_full_60_60": full_coverage,
                    "pairwise_wins": wins,
                    "pairwise_ties": ties,
                    "pairwise_losses": losses,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    raw = pd.read_csv(DATA_PATH)
    df = filter_submission_synthetic_cohort(raw)

    per_metric = [analyze_metric(df, metric) for metric in METRICS]
    pairwise = pd.concat(per_metric, ignore_index=True)
    pairwise.sort_values(["metric", "M", "problem"], inplace=True)

    coverage = build_coverage_summary(pairwise)
    coverage.sort_values(["metric", "M"], inplace=True)

    out_pairwise = os.path.join(OUT_DIR, "v4_planA_pairwise_ivf_vs_spea2.csv")
    out_coverage = os.path.join(OUT_DIR, "v4_planA_coverage_summary.csv")

    pairwise.to_csv(out_pairwise, index=False)
    coverage.to_csv(out_coverage, index=False)

    print(f"Saved: {out_pairwise}")
    print(f"Saved: {out_coverage}")


if __name__ == "__main__":
    main()
