#!/usr/bin/env python3
"""Statistical significance tests for convergence: IVF vs base per host.

For each (problem, M) and each (IVF, base) pair, performs:
  - Wilcoxon signed-rank test (paired by run) on AUC_IGD, Final_IGD, Best_IGD
  - Vargha-Delaney A12 effect size
  - Benjamini-Hochberg FDR correction across all tests per metric

Output: results/tables/convergence_significance.csv
"""

import os

import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon
from statsmodels.stats.multitest import multipletests


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
SUMMARIES_CSV = os.path.join(PROJECT_ROOT, "results", "tables", "convergence_summaries.csv")
OUT_SIG = os.path.join(PROJECT_ROOT, "results", "tables", "convergence_significance.csv")

# Pairs: (IVF algo, base algo)
HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2"),
    ("IVFNSGAIII", "NSGAIII"),
    ("IVFNSGAII", "NSGAII"),
]

# Metrics to test
TEST_METRICS = ["AUC_IGD", "Final_IGD", "Best_IGD", "AUC_HV", "Final_HV", "Best_HV"]


def vargha_delaney(x: np.ndarray, y: np.ndarray) -> float:
    """Vargha-Delaney A12 effect size.

    P(X > Y) + 0.5 * P(X == Y).
    > 0.5 means X tends to be larger than Y.
    """
    n1 = len(x)
    n2 = len(y)
    count = 0
    for xi in x:
        for yi in y:
            if xi > yi:
                count += 1
            elif xi == yi:
                count += 0.5
    return count / (n1 * n2)


def a12_interpretation(a12: float) -> str:
    """Standard interpretation thresholds based on |A12 - 0.5|."""
    a = abs(a12 - 0.5)
    if a < 0.147:
        return "negligible"
    elif a < 0.33:
        return "small"
    elif a < 0.474:
        return "medium"
    else:
        return "large"


def test_pair(
    ivf_vals: np.ndarray,
    base_vals: np.ndarray,
    runs: np.ndarray,
) -> dict:
    """Run Wilcoxon + A12 on paired data.

    Only includes runs where both values are valid.
    """
    valid = ~(np.isnan(ivf_vals) | np.isnan(base_vals))
    ivf_v = ivf_vals[valid]
    base_v = base_vals[valid]
    n = len(ivf_v)

    if n < 3:
        return {
            "p_value": np.nan,
            "a12": np.nan,
            "a12_label": "n/a",
            "n_pairs": n,
            "median_ivf": float(np.median(ivf_v)) if n > 0 else np.nan,
            "median_base": float(np.median(base_v)) if n > 0 else np.nan,
        }

    # Wilcoxon (two-sided)
    try:
        stat, p_value = wilcoxon(ivf_v, base_v)
    except ValueError:
        p_value = np.nan

    # A12: P(IVF > base) + 0.5*P(IVF == base)
    # For IGD metrics, lower is better; for HV, higher is better
    a12_raw = vargha_delaney(ivf_v, base_v)

    return {
        "p_value": float(p_value),
        "a12": float(a12_raw),
        "a12_label": a12_interpretation(a12_raw),
        "n_pairs": n,
        "median_ivf": float(np.median(ivf_v)),
        "median_base": float(np.median(base_v)),
    }


def main() -> None:
    print("=== Convergence significance tests ===\n")
    summaries = pd.read_csv(SUMMARIES_CSV)
    print(f"Loaded {len(summaries)} per-run summaries")

    all_rows = []
    # Collect p-values per metric for BH correction
    pvalue_pools: dict[str, list[dict]] = {m: [] for m in TEST_METRICS}

    for prob_m, group in summaries.groupby(["problem", "M"]):
        prob, m_val = prob_m
        for ivf_algo, base_algo in HOST_PAIRS:
            ivf_sub = group[group["algo"] == ivf_algo].set_index("run")
            base_sub = group[group["algo"] == base_algo].set_index("run")

            common_runs = sorted(set(ivf_sub.index) & set(base_sub.index))
            if len(common_runs) < 3:
                continue

            runs = np.array(common_runs)
            for metric in TEST_METRICS:
                if metric not in summaries.columns:
                    continue
                ivf_vals = ivf_sub.loc[common_runs, metric].values.astype(float)
                base_vals = base_sub.loc[common_runs, metric].values.astype(float)

                result = test_pair(ivf_vals, base_vals, runs)
                all_rows.append({
                    "problem": prob,
                    "M": int(m_val),
                    "ivf_algo": ivf_algo,
                    "base_algo": base_algo,
                    "metric": metric,
                    **result,
                })

                pvalue_pools[metric].append({
                    "idx": len(all_rows) - 1,
                    "p": result["p_value"],
                })

    sig_df = pd.DataFrame(all_rows)

    # BH correction per metric
    for metric, pool in pvalue_pools.items():
        valid = [p for p in pool if not np.isnan(p["p"])]
        if len(valid) < 2:
            continue
        p_raw = np.array([p["p"] for p in valid])
        _, p_adj, _, _ = multipletests(p_raw, method="fdr_bh")
        for i, p in enumerate(valid):
            sig_df.loc[p["idx"], "p_adj"] = float(p_adj[i])

    os.makedirs(os.path.dirname(OUT_SIG), exist_ok=True)
    sig_df.to_csv(OUT_SIG, index=False)
    print(f"\nSaved {len(sig_df)} rows to {OUT_SIG}")

    # Summary
    print("\nSignificant results (p_adj < 0.05):")
    sig = sig_df[sig_df["p_adj"] < 0.05]
    if sig.empty:
        print("  (none)")
    else:
        for _, r in sig.iterrows():
            direction = "IVF better" if r["a12"] < 0.5 else "base better"
            print(f"  {r['ivf_algo']} vs {r['base_algo']} on {r['problem']} M={r['M']} "
                  f"({r['metric']}): p_adj={r['p_adj']:.4f}, "
                  f"A12={r['a12']:.3f} ({r['a12_label']}, {direction})")

    # Count summary
    total = len(sig_df)
    n_sig = len(sig)
    print(f"\nTotal tests: {total}, Significant: {n_sig} ({100*n_sig/total:.1f}%)")


if __name__ == "__main__":
    main()
