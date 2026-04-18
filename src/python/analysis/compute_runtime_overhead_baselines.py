#!/usr/bin/env python3
"""
Compute empirical runtime overhead across all baselines (synthetic only).

The analysis uses canonical run cohorts:
  - IVF/SPEA2: run IDs 3001..3060
  - baselines: run IDs 1..60

Outputs:
  - results/tables/runtime_overhead_baselines.csv
  - results/tables/runtime_overhead_baselines.tex
"""

from __future__ import annotations

import os
import sys

import pandas as pd

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_DIR = os.path.join(PROJECT_ROOT, "results", "tables")

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
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-MOEA-II",
    "ARMOEA": "AR-MOEA",
}


def iqr(series: pd.Series) -> float:
    q = series.quantile([0.25, 0.75])
    return float(q.iloc[1] - q.iloc[0])


def main() -> int:
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: file not found: {DATA_PATH}")
        return 1

    df = pd.read_csv(DATA_PATH)
    df = filter_submission_synthetic_cohort(df)

    if "runtime" not in df.columns:
        print("ERROR: runtime column not found")
        return 1

    df = df.dropna(subset=["runtime"]).copy()

    # Per-instance (problem, M) median runtime for each algorithm
    inst = (
        df.groupby(["Problema", "M", "Algoritmo"], as_index=False)["runtime"]
        .median()
        .rename(columns={"runtime": "runtime_median"})
    )

    piv = inst.pivot_table(
        index=["Problema", "M"],
        columns="Algoritmo",
        values="runtime_median",
        aggfunc="first",
    )

    if "SPEA2" not in piv.columns:
        print("ERROR: SPEA2 column missing in runtime pivot")
        return 1

    rows = []
    for algo in ALGO_ORDER:
        if algo not in piv.columns:
            continue

        algo_inst = inst[inst["Algoritmo"] == algo]["runtime_median"]
        ratio_all = (piv[algo] / piv["SPEA2"]).dropna()
        ratio_m2 = (
            piv.xs("M2", level="M")[algo] / piv.xs("M2", level="M")["SPEA2"]
        ).dropna()
        ratio_m3 = (
            piv.xs("M3", level="M")[algo] / piv.xs("M3", level="M")["SPEA2"]
        ).dropna()

        rows.append(
            {
                "Algoritmo": algo,
                "Display": ALGO_DISPLAY.get(algo, algo),
                "n_instances": int(ratio_all.shape[0]),
                "runtime_median_s": float(algo_inst.median()),
                "runtime_iqr_s": iqr(algo_inst),
                "ratio_vs_spea2_median": float(ratio_all.median()),
                "ratio_vs_spea2_iqr": iqr(ratio_all),
                "ratio_vs_spea2_m2_median": float(ratio_m2.median()),
                "ratio_vs_spea2_m3_median": float(ratio_m3.median()),
            }
        )

    out = pd.DataFrame(rows)
    os.makedirs(OUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUT_DIR, "runtime_overhead_baselines.csv")
    out.to_csv(csv_path, index=False)

    tex_path = os.path.join(OUT_DIR, "runtime_overhead_baselines.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n")
        f.write(
            "\\caption{Empirical runtime overhead on synthetic benchmarks under canonical run cohorts (IVF/SPEA2: runs 3001--3060; baselines: runs 1--60). Runtime statistics are medians and IQRs of per-instance median runtime across 51 synthetic instances. $\\rho$ denotes per-instance runtime ratio relative to SPEA2.}\\label{tab:runtime_overhead_baselines}\n"
        )
        f.write("\\centering\\scriptsize\n")
        f.write("\\begin{tabular}{lrrrrr}\n")
        f.write("\\toprule\n")
        f.write(
            "Algorithm & Runtime med. (s) & Runtime IQR (s) & $\\rho$ med. & $\\rho_{M2}$ med. & $\\rho_{M3}$ med. \\\\"
        )
        f.write("\n")
        f.write("\\midrule\n")
        for _, r in out.iterrows():
            f.write(
                f"{r['Display']} & "
                f"{r['runtime_median_s']:.2f} & "
                f"{r['runtime_iqr_s']:.2f} & "
                f"{r['ratio_vs_spea2_median']:.2f} & "
                f"{r['ratio_vs_spea2_m2_median']:.2f} & "
                f"{r['ratio_vs_spea2_m3_median']:.2f} \\\\"
            )
            f.write("\n")
        f.write("\\botrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")

    print(f"Saved: {csv_path}")
    print(f"Saved: {tex_path}")
    print("\nRuntime ratio medians vs SPEA2:")
    print(
        out[
            [
                "Display",
                "ratio_vs_spea2_median",
                "ratio_vs_spea2_m2_median",
                "ratio_vs_spea2_m3_median",
            ]
        ].to_string(index=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
