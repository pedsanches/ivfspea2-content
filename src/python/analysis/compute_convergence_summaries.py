#!/usr/bin/env python3
"""Compute per-run convergence summary metrics.

For each (algo, problem, M, run) computes:
  - AUC_IGD: trapezoidal integral of IGD(FE)
  - AUC_HV: trapezoidal integral of HV(FE)
  - Final_IGD, Final_HV: last checkpoint values
  - Time-to-target: FE at which IGD first crosses each target threshold
  - Best_IGD: minimum IGD reached across all checkpoints

Targets are defined as multipliers of the best-known final IGD per instance.
"""

import os

import numpy as np
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONV_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")
OUT_SUMMARIES = os.path.join(PROJECT_ROOT, "results", "tables", "convergence_summaries.csv")

TARGET_MULTIPLIERS = [100, 50, 20, 10, 5, 3, 2, 1.5, 1.2, 1.0]


def compute_per_run_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary metrics for each (algo, problem, M, run)."""
    rows = []
    for (algo, prob, m_val, run), group in df.groupby(["algo", "problem", "M", "run"]):
        g = group.sort_values("FE")
        fe = g["FE"].values.astype(float)
        igd = g["IGD"].values.astype(float)
        hv = g["HV"].values.astype(float) if "HV" in g.columns else np.array([])

        if len(fe) < 2:
            continue

        # AUC via trapezoidal rule
        auc_igd = float(np.trapz(igd, fe))
        auc_hv = float(np.trapz(hv, fe)) if hv.size > 0 else np.nan

        # Final values
        final_igd = float(igd[-1])
        final_hv = float(hv[-1]) if hv.size > 0 else np.nan

        # Best (minimum IGD, maximum HV)
        best_igd = float(igd.min())
        best_hv = float(hv.max()) if hv.size > 0 else np.nan

        # Time-to-target: first FE where IGD <= target
        ttt = {}
        for mult in TARGET_MULTIPLIERS:
            target = best_igd * mult
            crossed = fe[igd <= target]
            ttt[f"TTT_igd_x{mult}"] = float(crossed[0]) if len(crossed) > 0 else np.nan

        rows.append({
            "algo": algo,
            "problem": prob,
            "M": int(m_val),
            "run": int(run),
            "n_checkpoints": len(fe),
            "fe_min": float(fe[0]),
            "fe_max": float(fe[-1]),
            "AUC_IGD": auc_igd,
            "AUC_HV": auc_hv,
            "Final_IGD": final_igd,
            "Final_HV": final_hv,
            "Best_IGD": best_igd,
            "Best_HV": best_hv,
            **ttt,
        })

    return pd.DataFrame(rows)


def compute_instance_targets(summaries: pd.DataFrame) -> pd.DataFrame:
    """Compute best-known IGD per (problem, M) across all algorithms."""
    best_per_instance = (
        summaries.groupby(["problem", "M"])["Best_IGD"]
        .min()
        .reset_index()
        .rename(columns={"Best_IGD": "Best_IGD_overall"})
    )
    targets = []
    for _, inst in best_per_instance.iterrows():
        for mult in TARGET_MULTIPLIERS:
            targets.append({
                "problem": inst["problem"],
                "M": inst["M"],
                "multiplier": mult,
                "target_igd": inst["Best_IGD_overall"] * mult,
            })
    return pd.DataFrame(targets)


def main() -> None:
    print("=== Computing convergence summaries ===\n")
    df = pd.read_csv(CONV_CSV)
    print(f"Loaded {len(df)} rows from convergence CSV")

    summaries = compute_per_run_metrics(df)
    print(f"Computed {len(summaries)} per-run summaries")
    print(f"  Algorithms: {sorted(summaries['algo'].unique())}")
    print(f"  Instances: {summaries[['problem','M']].drop_duplicates().shape[0]}")

    targets = compute_instance_targets(summaries)
    n_instances = summaries[["problem", "M"]].drop_duplicates().shape[0]
    print(f"  Targets per instance: {len(targets)} ({len(TARGET_MULTIPLIERS)} multipliers × {n_instances} instances)")

    os.makedirs(os.path.dirname(OUT_SUMMARIES), exist_ok=True)
    summaries.to_csv(OUT_SUMMARIES, index=False)
    print(f"\nSaved to {OUT_SUMMARIES}")

    # Quick sanity check
    print("\nSummary statistics (AUC_IGD):")
    for algo in sorted(summaries["algo"].unique()):
        sub = summaries[summaries["algo"] == algo]
        print(f"  {algo:15s}: mean={sub['AUC_IGD'].mean():.4f}, "
              f"median={sub['AUC_IGD'].median():.4f}, "
              f"std={sub['AUC_IGD'].std():.4f}")


if __name__ == "__main__":
    main()
