#!/usr/bin/env python3
"""
Computational Overhead Analysis: IVF/SPEA2 vs SPEA2
====================================================
Computes runtime ratio and overhead statistics from existing experimental data.
Generates a LaTeX-ready table for inclusion in the manuscript.

Uses: data/processed/metrica_runtime.csv (21k rows, 100 runs × 7 algorithms × all problems)
"""

import pandas as pd
import numpy as np
import os
import sys

# Resolve paths relative to the project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "metrica_runtime.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results")


def load_runtime_data(path: str) -> pd.DataFrame:
    """Load runtime data and validate structure."""
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from {path}")
    print(f"Algorithms: {sorted(df['Algoritmo'].unique())}")
    print(f"Problems: {sorted(df['Problema'].unique())}")
    print(f"Objectives: {sorted(df['M'].unique())}")
    return df


def compute_overhead_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute runtime overhead: ratio IVF/SPEA2 runtime / SPEA2 runtime.
    Returns a table with per-problem, per-M statistics.
    """
    # Filter to IVFSPEA2 and SPEA2 only
    ivf = df[df["Algoritmo"] == "IVFSPEA2"].copy()
    spea2 = df[df["Algoritmo"] == "SPEA2"].copy()

    # Group by Problem, M, D and compute statistics
    ivf_stats = (
        ivf.groupby(["Problema", "M", "D"])["runtime"]
        .agg(
            [
                "mean",
                "std",
                "median",
                lambda x: x.quantile(0.25),
                lambda x: x.quantile(0.75),
            ]
        )
        .reset_index()
    )
    ivf_stats.columns = [
        "Problema",
        "M",
        "D",
        "ivf_mean",
        "ivf_std",
        "ivf_median",
        "ivf_q25",
        "ivf_q75",
    ]

    spea2_stats = (
        spea2.groupby(["Problema", "M", "D"])["runtime"]
        .agg(
            [
                "mean",
                "std",
                "median",
                lambda x: x.quantile(0.25),
                lambda x: x.quantile(0.75),
            ]
        )
        .reset_index()
    )
    spea2_stats.columns = [
        "Problema",
        "M",
        "D",
        "spea2_mean",
        "spea2_std",
        "spea2_median",
        "spea2_q25",
        "spea2_q75",
    ]

    # Merge
    merged = ivf_stats.merge(spea2_stats, on=["Problema", "M", "D"], how="inner")

    # Compute ratio
    merged["ratio_mean"] = merged["ivf_mean"] / merged["spea2_mean"]
    merged["ratio_median"] = merged["ivf_median"] / merged["spea2_median"]

    # Per-run ratios for confidence interval
    results = []
    for (prob, m, d), group_ivf in ivf.groupby(["Problema", "M", "D"]):
        group_spea2 = spea2[
            (spea2["Problema"] == prob) & (spea2["M"] == m) & (spea2["D"] == d)
        ]
        if len(group_spea2) == 0:
            continue
        ivf_runs = group_ivf["runtime"].values
        spea2_runs = group_spea2["runtime"].values
        # Use paired ratios if same number of runs, otherwise use mean ratio
        if len(ivf_runs) == len(spea2_runs):
            ratios = ivf_runs / spea2_runs
            results.append(
                {
                    "Problema": prob,
                    "M": m,
                    "D": d,
                    "ratio_mean_paired": np.mean(ratios),
                    "ratio_std_paired": np.std(ratios, ddof=1),
                    "ratio_median_paired": np.median(ratios),
                    "n_runs": len(ratios),
                }
            )

    ratio_df = pd.DataFrame(results)
    merged = merged.merge(ratio_df, on=["Problema", "M", "D"], how="left")

    return merged


def compute_aggregate_summary(df: pd.DataFrame, overhead_df: pd.DataFrame) -> dict:
    """Compute aggregate overhead statistics across all problems."""
    # Overall ratio
    ivf_total = df[df["Algoritmo"] == "IVFSPEA2"]["runtime"]
    spea2_total = df[df["Algoritmo"] == "SPEA2"]["runtime"]

    summary = {
        "ivf_mean_runtime": ivf_total.mean(),
        "ivf_std_runtime": ivf_total.std(),
        "spea2_mean_runtime": spea2_total.mean(),
        "spea2_std_runtime": spea2_total.std(),
        "overall_ratio": ivf_total.mean() / spea2_total.mean(),
    }

    # Per-M aggregates
    for m_val in sorted(overhead_df["M"].unique()):
        subset = overhead_df[overhead_df["M"] == m_val]
        if "ratio_mean_paired" in subset.columns:
            ratios = subset["ratio_mean_paired"].dropna()
            summary[f"ratio_mean_{m_val}"] = ratios.mean()
            summary[f"ratio_min_{m_val}"] = ratios.min()
            summary[f"ratio_max_{m_val}"] = ratios.max()

    return summary


def generate_latex_table(overhead_df: pd.DataFrame) -> str:
    """Generate a LaTeX table for the manuscript."""
    # Sort by suite order, then problem
    suite_order = {"ZDT": 0, "DTLZ": 1, "WFG": 2, "MaF": 3}
    overhead_df = overhead_df.copy()
    overhead_df["suite"] = overhead_df["Problema"].apply(
        lambda x: next((k for k in suite_order if x.startswith(k)), "Other")
    )
    overhead_df["suite_order"] = overhead_df["suite"].map(suite_order)
    overhead_df = overhead_df.sort_values(["M", "suite_order", "Problema"])

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(
        r"\caption{Runtime overhead of IVF/SPEA2 relative to SPEA2. Values report mean runtime (seconds) over 100 independent runs and the ratio $\rho = \bar{t}_{\mathrm{IVF/SPEA2}} / \bar{t}_{\mathrm{SPEA2}}$.}\label{tab:runtime_overhead}"
    )
    lines.append(r"\centering")
    lines.append(r"\scriptsize")
    lines.append(r"\begin{tabular}{llrrr}")
    lines.append(r"\toprule")
    lines.append(
        r"Problem & $M$ & $\bar{t}_{\mathrm{IVF/SPEA2}}$ (s) & $\bar{t}_{\mathrm{SPEA2}}$ (s) & $\rho$ \\"
    )
    lines.append(r"\midrule")

    current_m = None
    for _, row in overhead_df.iterrows():
        if row["M"] != current_m:
            if current_m is not None:
                lines.append(r"\midrule")
            current_m = row["M"]

        ratio_val = row.get("ratio_mean_paired", row["ratio_mean"])
        lines.append(
            f"{row['Problema']} & ${row['M']}$ & "
            f"{row['ivf_mean']:.2f} & {row['spea2_mean']:.2f} & "
            f"{ratio_val:.2f} \\\\"
        )

    lines.append(r"\botrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("Computational Overhead Analysis: IVF/SPEA2 vs SPEA2")
    print("=" * 60)

    df = load_runtime_data(DATA_PATH)

    print("\n--- Computing overhead table ---")
    overhead_df = compute_overhead_table(df)

    print("\n--- Aggregate Summary ---")
    summary = compute_aggregate_summary(df, overhead_df)
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    print("\n--- Per-problem overhead (sorted by M) ---")
    display_cols = ["Problema", "M", "D", "ivf_mean", "spea2_mean", "ratio_mean"]
    if "ratio_mean_paired" in overhead_df.columns:
        display_cols.append("ratio_mean_paired")
    print(
        overhead_df[display_cols].sort_values(["M", "Problema"]).to_string(index=False)
    )

    # Save CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "runtime_overhead.csv")
    overhead_df.to_csv(csv_path, index=False)
    print(f"\nSaved overhead data to {csv_path}")

    # Generate LaTeX
    latex = generate_latex_table(overhead_df)
    latex_path = os.path.join(OUTPUT_DIR, "runtime_overhead_table.tex")
    with open(latex_path, "w") as f:
        f.write(latex)
    print(f"Saved LaTeX table to {latex_path}")

    print("\n--- LaTeX table preview ---")
    print(latex)

    return overhead_df, summary


if __name__ == "__main__":
    overhead_df, summary = main()
