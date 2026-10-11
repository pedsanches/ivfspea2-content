#!/usr/bin/env python3
"""Statistical significance tests for convergence: IVF vs base per host.

For each (problem, M) and each (IVF, base) pair, performs:
  - Wilcoxon signed-rank test on AUC_IGD, Final_IGD, Best_IGD, AUC_HV,
    Final_HV, Best_HV, paired by run identifier when the two tracks share run
    identifiers and aligned by sorted run order otherwise (the IVF/SPEA2 and
    SPEA2 tracks use disjoint identifier ranges: 3001-3030 against 1-30);
  - Vargha-Delaney A12 effect size
  - Benjamini-Hochberg FDR correction across all tests per metric

When a pair has no shared run identifiers, the order alignment is arbitrary, so
the script also reports an unpaired Mann-Whitney U test for that pair, corrected
within its own family (per metric), in the columns `p_value_robustness` and
`p_adj_robustness`. Every fallback to order alignment and every skipped pair is
announced on stdout.

Output: results/tables/convergence_significance.csv
"""

import os

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon
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
    pairing: str = "run-id",
) -> dict:
    """Run Wilcoxon + A12 on the aligned data.

    Only includes positions where both values are valid. `pairing` records how
    the two tracks were aligned ("run-id" or "order-aligned") so that the CSV
    states, per row, what the test assumed.
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
            "pairing": pairing,
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
        "pairing": pairing,
    }


def main() -> None:
    print("=== Convergence significance tests ===\n")
    summaries = pd.read_csv(SUMMARIES_CSV)
    print(f"Loaded {len(summaries)} per-run summaries")

    all_rows = []
    # Collect p-values per metric for BH correction of the primary test
    pvalue_pools: dict[str, list[dict]] = {m: [] for m in TEST_METRICS}
    # Separate pool for the unpaired robustness test of order-aligned pairs
    robustness_pools: dict[str, list[dict]] = {m: [] for m in TEST_METRICS}
    reported_alignment: set[tuple[str, str]] = set()

    for prob_m, group in summaries.groupby(["problem", "M"]):
        prob, m_val = prob_m
        for ivf_algo, base_algo in HOST_PAIRS:
            ivf_sub = group[group["algo"] == ivf_algo]
            base_sub = group[group["algo"] == base_algo]

            common_runs = sorted(set(ivf_sub["run"]) & set(base_sub["run"]))
            if len(common_runs) >= 3:
                pairing = "run-id"
                ivf_by_run = ivf_sub.set_index("run")
                base_by_run = base_sub.set_index("run")
                aligned_ivf = ivf_by_run.loc[common_runs]
                aligned_base = base_by_run.loc[common_runs]
                index = common_runs
                unpaired_available = False
            else:
                ivf_sorted = ivf_sub.sort_values("run")
                base_sorted = base_sub.sort_values("run")
                n_align = min(len(ivf_sorted), len(base_sorted))
                if n_align < 3:
                    print(
                        f"  ! skipping {ivf_algo} vs {base_algo} on {prob} M={int(m_val)}: "
                        f"only {len(ivf_sorted)} and {len(base_sorted)} runs, "
                        "fewer than three pairs"
                    )
                    continue
                pairing = "order-aligned"
                if (ivf_algo, base_algo) not in reported_alignment:
                    reported_alignment.add((ivf_algo, base_algo))
                    print(
                        f"  ! {ivf_algo} vs {base_algo}: no shared run identifiers "
                        f"({len(ivf_sorted)} vs {len(base_sorted)} runs); aligning by sorted "
                        "run order and reporting an unpaired Mann-Whitney robustness column"
                    )
                aligned_ivf = ivf_sorted.iloc[:n_align]
                aligned_base = base_sorted.iloc[:n_align]
                index = list(range(n_align))
                unpaired_available = True

            for metric in TEST_METRICS:
                if metric not in summaries.columns:
                    continue
                ivf_vals = aligned_ivf[metric].values.astype(float)
                base_vals = aligned_base[metric].values.astype(float)

                result = test_pair(ivf_vals, base_vals, np.array(index), pairing=pairing)
                row = {
                    "problem": prob,
                    "M": int(m_val),
                    "ivf_algo": ivf_algo,
                    "base_algo": base_algo,
                    "metric": metric,
                    **result,
                }
                if unpaired_available:
                    valid = ~(np.isnan(ivf_vals) | np.isnan(base_vals))
                    ivf_v, base_v = ivf_vals[valid], base_vals[valid]
                    try:
                        _, p_mw = mannwhitneyu(ivf_v, base_v, alternative="two-sided")
                        row["p_value_robustness"] = float(p_mw)
                    except ValueError:
                        row["p_value_robustness"] = np.nan
                else:
                    row["p_value_robustness"] = np.nan
                all_rows.append(row)

                pvalue_pools[metric].append({
                    "idx": len(all_rows) - 1,
                    "p": result["p_value"],
                })
                if unpaired_available:
                    robustness_pools[metric].append({
                        "idx": len(all_rows) - 1,
                        "p": row["p_value_robustness"],
                    })

    sig_df = pd.DataFrame(all_rows)

    # BH correction per metric, for the primary test
    for _metric, pool in pvalue_pools.items():
        valid = [p for p in pool if not np.isnan(p["p"])]
        if len(valid) < 2:
            continue
        p_raw = np.array([p["p"] for p in valid])
        _, p_adj, _, _ = multipletests(p_raw, method="fdr_bh")
        for i, p in enumerate(valid):
            sig_df.loc[p["idx"], "p_adj"] = float(p_adj[i])

    # BH correction per metric, within the order-aligned family only
    for _metric, pool in robustness_pools.items():
        valid = [p for p in pool if not np.isnan(p["p"])]
        if len(valid) < 2:
            continue
        p_raw = np.array([p["p"] for p in valid])
        _, p_adj, _, _ = multipletests(p_raw, method="fdr_bh")
        for i, p in enumerate(valid):
            sig_df.loc[p["idx"], "p_adj_robustness"] = float(p_adj[i])

    os.makedirs(os.path.dirname(OUT_SIG), exist_ok=True)
    sig_df.to_csv(OUT_SIG, index=False)
    print(f"\nSaved {len(sig_df)} rows to {OUT_SIG}")
    print("Pairs by alignment: " + ", ".join(
        f"{ivf} vs {base}: "
        f"{sorted(sig_df[(sig_df.ivf_algo == ivf) & (sig_df.base_algo == base)].pairing.unique())}"
        for ivf, base in HOST_PAIRS
    ))

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

    # Robustness summary for the order-aligned pair
    rob = sig_df[sig_df["pairing"] == "order-aligned"]
    if not rob.empty:
        n_sig_rob = int((rob["p_adj_robustness"] < 0.05).sum())
        print(
            f"\nUnpaired robustness (order-aligned pair, BH per metric): "
            f"{n_sig_rob} of {len(rob)} tests significant"
        )

    # Count summary
    total = len(sig_df)
    n_sig = len(sig)
    print(f"\nTotal tests: {total}, Significant: {n_sig} ({100*n_sig/total:.1f}%)")


if __name__ == "__main__":
    main()
