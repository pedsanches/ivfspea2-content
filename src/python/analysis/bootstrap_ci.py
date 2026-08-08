#!/usr/bin/env python3
"""Bootstrap confidence intervals for convergence summary metrics.

For each (algo, problem, M), computes the median and 95% CI (percentile
method) via 10,000 bootstrap resamples of the 30 runs.

Metrics covered: AUC_IGD, AUC_HV, Final_IGD, Final_HV, Best_IGD, Best_HV,
and all TTT_* columns.
"""

import os

import numpy as np
import pandas as pd
from tqdm import tqdm


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
SUMMARIES_CSV = os.path.join(PROJECT_ROOT, "results", "tables", "convergence_summaries.csv")
OUT_CI = os.path.join(PROJECT_ROOT, "results", "tables", "convergence_summaries_bootstrap_ci.csv")

N_BOOTSTRAP = 10_000
RANDOM_SEED = 42

# Core metrics to report CIs for
CORE_METRICS = [
    "AUC_IGD", "AUC_HV",
    "Final_IGD", "Final_HV",
    "Best_IGD", "Best_HV",
]


def bootstrap_ci_group(
    values: np.ndarray,
    n_bootstrap: int = N_BOOTSTRAP,
    rng: np.random.Generator | None = None,
) -> dict:
    """Compute median and 95% CI via percentile bootstrap.

    Returns dict with: median, ci_low, ci_high, n_valid.
    """
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)

    valid = values[~np.isnan(values)]
    n = len(valid)
    if n < 2:
        return {"median": np.nan, "ci_low": np.nan, "ci_high": np.nan, "n_valid": n}

    boot_stats = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        sample = rng.choice(valid, size=n, replace=True)
        boot_stats[b] = np.median(sample)

    return {
        "median": float(np.median(valid)),
        "ci_low": float(np.percentile(boot_stats, 2.5)),
        "ci_high": float(np.percentile(boot_stats, 97.5)),
        "n_valid": n,
    }


def main() -> None:
    print("=== Bootstrap CI for convergence summaries ===\n")
    summaries = pd.read_csv(SUMMARIES_CSV)
    print(f"Loaded {len(summaries)} per-run summaries")

    rng = np.random.default_rng(RANDOM_SEED)

    # Identify all metric columns (everything not in group keys)
    group_keys = ["algo", "problem", "M"]
    metric_cols = [c for c in summaries.columns if c not in group_keys and c != "run"]

    # Also include TTT columns
    ttt_cols = [c for c in metric_cols if c.startswith("TTT_")]
    all_metrics = CORE_METRICS + [c for c in ttt_cols if c not in CORE_METRICS]
    all_metrics = [c for c in all_metrics if c in summaries.columns]

    rows = []
    groups = summaries.groupby(group_keys)
    for (algo, prob, m_val), group in tqdm(groups, desc="Bootstrap"):
        for metric in all_metrics:
            vals = group[metric].values.astype(float)
            ci = bootstrap_ci_group(vals, rng=rng)
            rows.append({
                "algo": algo,
                "problem": prob,
                "M": int(m_val),
                "metric": metric,
                "median": ci["median"],
                "ci_low": ci["ci_low"],
                "ci_high": ci["ci_high"],
                "n_valid": ci["n_valid"],
            })

    ci_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CI), exist_ok=True)
    ci_df.to_csv(OUT_CI, index=False)
    print(f"\nSaved {len(ci_df)} rows to {OUT_CI}")

    # Show example: AUC_IGD for IVFSPEA2
    print("\nExample — AUC_IGD for IVFSPEA2:")
    ex = ci_df[(ci_df["algo"] == "IVFSPEA2") & (ci_df["metric"] == "AUC_IGD")]
    for _, r in ex.iterrows():
        print(f"  {r['problem']} M={r['M']}: "
              f"median={r['median']:.4f} "
              f"[{r['ci_low']:.4f}, {r['ci_high']:.4f}]")


if __name__ == "__main__":
    main()
