#!/usr/bin/env python3
"""Test ECDF differences between IVF and base algorithms.

For each (problem, M) and (IVF, base) pair, uses the Kolmogorov-Smirnov
two-sample test to compare the aggregated time-to-target distributions
across all target levels.

Also computes a global ECDF gap (max |ECDF_IVF - ECDF_base|) per instance.

Output: results/tables/ecdf_significance.csv
"""

import os

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONV_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")
OUT_ECDF_SIG = os.path.join(PROJECT_ROOT, "results", "tables", "ecdf_significance.csv")

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2"),
    ("IVFNSGAIII", "NSGAIII"),
    ("IVFNSGAII", "NSGAII"),
]

TARGET_MULTIPLIERS = [100, 50, 20, 10, 5, 3, 2, 1.5, 1.2, 1.0]
MAX_FE = 100_000


def compute_time_to_target(
    df: pd.DataFrame,
    prob: str,
    m_val: int,
    algo: str,
    best_igd: float,
    mult: float,
) -> np.ndarray:
    """For each run, find the FE at which IGD first crosses the target."""
    target = best_igd * mult
    sub = df[(df["problem"] == prob) & (df["M"] == m_val) & (df["algo"] == algo)]
    ttt = []
    for run, run_data in sub.groupby("run"):
        run_sorted = run_data.sort_values("FE")
        crossed = run_sorted[run_sorted["IGD"] <= target]
        if len(crossed) > 0:
            ttt.append(float(crossed.iloc[0]["FE"]))
        else:
            ttt.append(MAX_FE)  # Never solved → max budget
    return np.array(ttt)


def main() -> None:
    print("=== ECDF significance tests (KS-test) ===\n")
    df = pd.read_csv(CONV_CSV)
    print(f"Loaded {len(df)} convergence rows")

    instances = df[["problem", "M"]].drop_duplicates().sort_values(["problem", "M"])
    rows = []

    for _, inst in instances.iterrows():
        prob = inst["problem"]
        m_val = int(inst["M"])

        # Best IGD across all algos/runs for this instance
        best_igd = df[
            (df["problem"] == prob) & (df["M"] == m_val)
        ]["IGD"].min()

        for ivf_algo, base_algo in HOST_PAIRS:
            # Collect all time-to-target values across targets
            ivf_ttt_all = []
            base_ttt_all = []

            for mult in TARGET_MULTIPLIERS:
                ivf_ttt = compute_time_to_target(
                    df, prob, m_val, ivf_algo, best_igd, mult
                )
                base_ttt = compute_time_to_target(
                    df, prob, m_val, base_algo, best_igd, mult
                )
                ivf_ttt_all.extend(ivf_ttt)
                base_ttt_all.extend(base_ttt)

            ivf_ttt_all = np.array(ivf_ttt_all)
            base_ttt_all = np.array(base_ttt_all)

            if len(ivf_ttt_all) < 3 or len(base_ttt_all) < 3:
                continue

            # KS two-sample test
            ks_stat, p_value = ks_2samp(ivf_ttt_all, base_ttt_all)

            # ECDF gap: compute at a grid of FE values
            fe_grid = np.linspace(0, MAX_FE, 200)

            def ecdf_at(data, grid):
                n = len(data)
                return np.array([np.sum(data <= g) / n for g in grid])

            ecdf_ivf = ecdf_at(ivf_ttt_all, fe_grid)
            ecdf_base = ecdf_at(base_ttt_all, fe_grid)
            max_gap = float(np.max(np.abs(ecdf_ivf - ecdf_base)))
            gap_fe = float(fe_grid[np.argmax(np.abs(ecdf_ivf - ecdf_base))])

            # Direction: positive means IVF solves more targets earlier
            # (higher ECDF at same FE)
            mean_diff = float(np.mean(ecdf_ivf - ecdf_base))

            rows.append({
                "problem": prob,
                "M": m_val,
                "ivf_algo": ivf_algo,
                "base_algo": base_algo,
                "n_targets": len(TARGET_MULTIPLIERS),
                "n_runs_ivf": len(ivf_ttt_all) // len(TARGET_MULTIPLIERS),
                "n_runs_base": len(base_ttt_all) // len(TARGET_MULTIPLIERS),
                "ks_stat": ks_stat,
                "p_value": p_value,
                "max_ecdf_gap": max_gap,
                "max_gap_fe": gap_fe,
                "mean_ecdf_diff": mean_diff,
                "direction": "IVF faster" if mean_diff > 0 else "base faster",
            })

    ecdf_sig_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_ECDF_SIG), exist_ok=True)
    ecdf_sig_df.to_csv(OUT_ECDF_SIG, index=False)
    print(f"\nSaved {len(ecdf_sig_df)} rows to {OUT_ECDF_SIG}")

    # Summary
    print("\nSignificant ECDF differences (p < 0.05):")
    sig = ecdf_sig_df[ecdf_sig_df["p_value"] < 0.05]
    if sig.empty:
        print("  (none)")
    else:
        for _, r in sig.iterrows():
            print(f"  {r['ivf_algo']} vs {r['base_algo']} on {r['problem']} M={r['M']}: "
                  f"KS={r['ks_stat']:.3f}, p={r['p_value']:.4f}, "
                  f"max_gap={r['max_ecdf_gap']:.3f} at FE={r['max_gap_fe']:.0f} "
                  f"({r['direction']})")

    # BH-like summary: count how many are significant at alpha=0.05
    n_total = len(ecdf_sig_df)
    n_sig = len(sig)
    print(f"\nTotal tests: {n_total}, Significant (uncorrected p<0.05): {n_sig} ({100*n_sig/n_total:.1f}%)")


if __name__ == "__main__":
    main()
