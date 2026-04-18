#!/usr/bin/env python3
"""
compute_response.py — Compute the response variable for the FLA study.

For each of the 51 synthetic benchmark instances, computes:
  - Delta_IGD = median(IGD_SPEA2) - median(IGD_IVFSPEA2)
    Positive means IVF improves (SPEA2 has higher/worse IGD)
  - Statistical classification via Wilcoxon rank-sum test:
      HELPS:   p < 0.05 and Delta > 0
      HURTS:   p < 0.05 and Delta < 0
      NEUTRAL: p >= 0.05
  - Vargha-Delaney A12 effect size:
      A12 = P(IGD_SPEA2 > IGD_IVFSPEA2) + 0.5 * P(IGD_SPEA2 == IGD_IVFSPEA2)
      A12 > 0.5 means SPEA2 has higher (worse) IGD, i.e., IVF helps.
  - Binary label (label_binary):
      HELPS:     p < 0.05 AND A12 > 0.56
      NOT_HELPS: otherwise (merges NEUTRAL + HURTS)
  - Three-class label (label):
      Original classification retained for reference.

Input:  data/processed/todas_metricas_consolidado_with_modern.csv
Output: data/processed/fla_response.csv

NOTE: Performance data comes from the IVF/SPEA2 experiments reported in
the Memetic Computing submission (cited in the PPSN paper). This script
only computes the derived response variable for the FLA study.

To keep the PPSN analysis on the same evidence surface as the main synthetic
comparison, we first apply the canonical submission cohort filter:
  - IVFSPEA2 runs 3001..3060
  - baseline runs 1..60
"""

import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort

# --- Configuration ---
INPUT_CSV = Path("data/processed/todas_metricas_consolidado_with_modern.csv")
OUTPUT_CSV = Path("data/processed/fla_response.csv")
ALPHA = 0.05
A12_THRESHOLD = 0.56  # Small effect size threshold for binary classification

# IVF/SPEA2 v2 runs are IDs 3001-3060; SPEA2 baseline runs are 1-60
IVF_ALGO = "IVFSPEA2"
SPEA2_ALGO = "SPEA2"


def vargha_delaney_a12(x, y):
    """Compute the Vargha-Delaney A12 effect size.

    A12 = P(X > Y) + 0.5 * P(X == Y)

    Here X = IGD_SPEA2, Y = IGD_IVFSPEA2.
    A12 > 0.5 means X tends to be larger (worse), i.e., IVF helps.

    Parameters
    ----------
    x : array-like
        Sample from the first group (SPEA2 IGD values).
    y : array-like
        Sample from the second group (IVF-SPEA2 IGD values).

    Returns
    -------
    float
        A12 statistic in [0, 1].
    """
    m, n = len(x), len(y)
    if m == 0 or n == 0:
        return np.nan
    # Count all pairwise comparisons
    more = 0
    equal = 0
    for xi in x:
        for yj in y:
            if xi > yj:
                more += 1
            elif xi == yj:
                equal += 1
    return (more + 0.5 * equal) / (m * n)


def build_instance_key(row):
    """Build instance key matching MATLAB feature extraction naming."""
    return f"{row['Problema']}_{row['M']}"


def main():
    print("=== Computing FLA Response Variable ===")

    df = pd.read_csv(INPUT_CSV)
    df = filter_submission_synthetic_cohort(df)

    # Keep only IVF/SPEA2 and SPEA2
    df = df[df["Algoritmo"].isin([IVF_ALGO, SPEA2_ALGO])]

    # Build instance key
    df["instance"] = df.apply(build_instance_key, axis=1)

    # Drop rows with missing IGD
    df = df.dropna(subset=["IGD"])

    instances = sorted(df["instance"].unique())
    print(f"Found {len(instances)} synthetic instances")

    results = []

    for inst in instances:
        inst_data = df[df["instance"] == inst]

        igd_spea2 = inst_data.loc[
            inst_data["Algoritmo"] == SPEA2_ALGO, "IGD"
        ].values
        igd_ivf = inst_data.loc[
            inst_data["Algoritmo"] == IVF_ALGO, "IGD"
        ].values

        if len(igd_spea2) == 0 or len(igd_ivf) == 0:
            print(f"  WARNING: {inst} — missing data, skipping")
            continue

        # Delta: positive means IVF is better (SPEA2 has higher IGD)
        median_spea2 = np.median(igd_spea2)
        median_ivf = np.median(igd_ivf)
        delta_igd = median_spea2 - median_ivf

        # Relative improvement (%)
        if abs(median_spea2) > 1e-12:
            delta_pct = (delta_igd / median_spea2) * 100
        else:
            delta_pct = 0.0

        # Wilcoxon rank-sum test (two-sided)
        stat, p_value = mannwhitneyu(
            igd_spea2, igd_ivf, alternative="two-sided"
        )

        # Vargha-Delaney A12 effect size
        a12 = vargha_delaney_a12(igd_spea2, igd_ivf)

        # Three-class classification (original)
        if p_value < ALPHA and delta_igd > 0:
            label = "HELPS"
        elif p_value < ALPHA and delta_igd < 0:
            label = "HURTS"
        else:
            label = "NEUTRAL"

        # Binary classification (stricter: requires both significance and effect size)
        if p_value < ALPHA and a12 > A12_THRESHOLD:
            label_binary = "HELPS"
        else:
            label_binary = "NOT_HELPS"

        # Extract M and D from instance data
        m_val = inst_data["M"].iloc[0]
        d_val = inst_data["D"].iloc[0]

        results.append({
            "instance": inst,
            "M": m_val,
            "D": d_val,
            "n_runs_spea2": len(igd_spea2),
            "n_runs_ivf": len(igd_ivf),
            "median_igd_spea2": median_spea2,
            "median_igd_ivf": median_ivf,
            "delta_igd": delta_igd,
            "delta_pct": delta_pct,
            "wilcoxon_p": p_value,
            "a12": a12,
            "label": label,
            "label_binary": label_binary,
        })

    result_df = pd.DataFrame(results)

    # Summary
    counts = result_df["label"].value_counts()
    print(f"\nThree-class label distribution:")
    for lbl in ["HELPS", "NEUTRAL", "HURTS"]:
        print(f"  {lbl}: {counts.get(lbl, 0)}")

    counts_bin = result_df["label_binary"].value_counts()
    print(f"\nBinary label distribution (p<{ALPHA} AND A12>{A12_THRESHOLD}):")
    for lbl in ["HELPS", "NOT_HELPS"]:
        print(f"  {lbl}: {counts_bin.get(lbl, 0)}")

    # A12 summary
    print(f"\nA12 effect size summary:")
    print(f"  mean={result_df['a12'].mean():.4f}  "
          f"median={result_df['a12'].median():.4f}  "
          f"min={result_df['a12'].min():.4f}  "
          f"max={result_df['a12'].max():.4f}")

    result_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nExported to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
