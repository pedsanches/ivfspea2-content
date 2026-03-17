#!/usr/bin/env python3
"""
Analyze normalization pilot: IVFSPEA2V2 vs IVFSPEA2V2Norm.

Loads .mat results from PlatEMO/Data/ for run IDs 9001..9030,
computes median/IQR for IGD and HV, runs Wilcoxon signed-rank tests,
and prints a comparison table.

Usage:
    python experiments/analyze_norm_pilot.py
"""

import os
import sys
import numpy as np
import pymatreader
from scipy import stats

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(
    PROJECT_ROOT, "src", "matlab", "lib", "PlatEMO", "Data"
)

ALGORITHMS = ["IVFSPEA2V2", "IVFSPEA2V2Norm"]
RUN_BASE = 9001
NUM_RUNS = 30

PROBLEMS = [
    ("RWMOP9", 2, 4),
    ("WFG1", 2, 11),
    ("WFG1", 3, 12),
    ("WFG4", 3, 12),
    ("WFG7", 3, 12),
]

METRICS = ["IGD", "HV"]


def extract_metric(filepath, metric_name):
    """Extract final metric value from a PlatEMO .mat file."""
    try:
        data = pymatreader.read_mat(filepath)
    except Exception:
        return np.nan
    if "metric" not in data or not isinstance(data["metric"], dict):
        return np.nan
    val = data["metric"].get(metric_name)
    if val is None:
        return np.nan
    if isinstance(val, np.ndarray):
        return float(val.flat[-1]) if val.size > 0 else np.nan
    return float(val)


def load_all():
    """Load all pilot results into a nested dict."""
    # results[algo][prob_key][metric] = [values]
    results = {}
    for algo in ALGORITHMS:
        results[algo] = {}
        algo_dir = os.path.join(DATA_DIR, algo)
        for prob_name, M, D in PROBLEMS:
            key = f"{prob_name}_M{M}"
            results[algo][key] = {m: [] for m in METRICS}
            for r in range(RUN_BASE, RUN_BASE + NUM_RUNS):
                fname = f"{algo}_{prob_name}_M{M}_D{D}_{r}.mat"
                fpath = os.path.join(algo_dir, fname)
                for m in METRICS:
                    results[algo][key][m].append(extract_metric(fpath, m))
    return results


def main():
    results = load_all()

    # Check data availability
    for algo in ALGORITHMS:
        algo_dir = os.path.join(DATA_DIR, algo)
        if not os.path.isdir(algo_dir):
            print(f"ERROR: Directory not found: {algo_dir}")
            print("Run the pilot experiment first:")
            print("  matlab -batch \"run('experiments/run_norm_pilot.m')\"")
            sys.exit(1)

    print("=" * 85)
    print("NORMALIZATION PILOT — IVFSPEA2V2 vs IVFSPEA2V2Norm")
    print("=" * 85)

    for metric in METRICS:
        better_dir = "lower" if metric == "IGD" else "higher"
        print(f"\n{'─' * 85}")
        print(f"  {metric} ({better_dir} is better) — median [IQR]")
        print(f"{'─' * 85}")
        print(
            f"  {'Problem':<14} {'V2 (no norm)':<24} {'V2-Norm':<24} "
            f"{'p-value':>8}  {'Winner':>8}"
        )
        print(f"  {'─' * 14} {'─' * 24} {'─' * 24} {'─' * 8}  {'─' * 8}")

        for prob_name, M, _ in PROBLEMS:
            key = f"{prob_name}_M{M}"
            v_base = np.array(results["IVFSPEA2V2"][key][metric])
            v_norm = np.array(results["IVFSPEA2V2Norm"][key][metric])

            # Remove NaNs
            mask = ~(np.isnan(v_base) | np.isnan(v_norm))
            v_base_clean = v_base[mask]
            v_norm_clean = v_norm[mask]

            n = len(v_base_clean)
            if n < 5:
                print(f"  {key:<14} insufficient data ({n} runs)")
                continue

            med_b = np.median(v_base_clean)
            iqr_b = np.percentile(v_base_clean, 75) - np.percentile(v_base_clean, 25)
            med_n = np.median(v_norm_clean)
            iqr_n = np.percentile(v_norm_clean, 75) - np.percentile(v_norm_clean, 25)

            # Wilcoxon signed-rank test
            try:
                stat, pval = stats.wilcoxon(v_base_clean, v_norm_clean)
            except ValueError:
                pval = 1.0

            # Determine winner
            if pval < 0.05:
                if metric == "IGD":
                    winner = "Norm" if med_n < med_b else "Base"
                else:  # HV
                    winner = "Norm" if med_n > med_b else "Base"
            else:
                winner = "≈"

            def fmt(med, iqr):
                return f"{med:.4e} [{iqr:.2e}]"

            print(
                f"  {key:<14} {fmt(med_b, iqr_b):<24} {fmt(med_n, iqr_n):<24} "
                f"{pval:>8.4f}  {winner:>8}"
            )

    # Summary
    print(f"\n{'=' * 85}")
    print("Notes:")
    print("  - 30 independent runs per configuration")
    print("  - Wilcoxon signed-rank test, α = 0.05")
    print("  - 'Norm' = normalization helped, 'Base' = no norm was better, '≈' = no sig. diff.")
    print(f"{'=' * 85}")


if __name__ == "__main__":
    main()
