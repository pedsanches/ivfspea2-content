#!/usr/bin/env python3
"""Diagnose FE grid alignment and merge losses for convergence analysis.

Reports per-host-per-run FE grid consistency and quantifies data loss
when merging (run, FE) between IVF and base algorithms.
"""

import os

import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONV_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")
OUT_DIAG = os.path.join(PROJECT_ROOT, "results", "tables", "merge_diagnostic.csv")

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2"),
    ("IVFNSGAIII", "NSGAIII"),
    ("IVFNSGAII", "NSGAII"),
]


def main() -> None:
    print("=== Merge diagnostic ===\n")
    df = pd.read_csv(CONV_CSV)

    rows = []
    for ivf_algo, base_algo in HOST_PAIRS:
        for (prob, m_val), group in df.groupby(["problem", "M"]):
            ivf_sub = group[group["algo"] == ivf_algo]
            base_sub = group[group["algo"] == base_algo]

            if ivf_sub.empty or base_sub.empty:
                continue

            ivf_fe_sets = ivf_sub.groupby("run")["FE"].apply(set)
            base_fe_sets = base_sub.groupby("run")["FE"].apply(set)

            common_runs = set(ivf_fe_sets.index) & set(base_fe_sets.index)

            for run in sorted(common_runs):
                ivf_fes = ivf_fe_sets[run]
                base_fes = base_fe_sets[run]
                common_fes = ivf_fes & base_fes
                ivf_only = ivf_fes - base_fes
                base_only = base_fes - ivf_fes

                n_ivf = len(ivf_fes)
                n_base = len(base_fes)
                n_common = len(common_fes)
                loss_ivf = n_ivf - n_common
                loss_base = n_base - n_common

                rows.append({
                    "ivf_algo": ivf_algo,
                    "base_algo": base_algo,
                    "problem": prob,
                    "M": m_val,
                    "run": run,
                    "n_fe_ivf": n_ivf,
                    "n_fe_base": n_base,
                    "n_fe_common": n_common,
                    "fe_lost_ivf": loss_ivf,
                    "fe_lost_base": loss_base,
                    "match_pct": 100.0 * n_common / max(n_ivf, n_base) if max(n_ivf, n_base) > 0 else 0,
                })

            # Grid consistency: are FE grids identical across runs within same algo?
            ivf_grids = ivf_sub.groupby("run")["FE"].apply(lambda x: tuple(sorted(x)))
            n_unique_ivf_grids = ivf_grids.nunique()
            n_unique_base_grids = base_fe_sets.index.nunique() if not base_sub.empty else 0

            # Add summary row for this (algo pair, problem, M)
            base_grids_unique = base_sub.groupby("run")["FE"].apply(lambda x: tuple(sorted(x))).nunique()

    diag_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_DIAG), exist_ok=True)

    # Summary statistics
    if not diag_df.empty:
        summary = diag_df.groupby(["ivf_algo", "base_algo"]).agg(
            total_runs=("run", "count"),
            mean_match_pct=("match_pct", "mean"),
            min_match_pct=("match_pct", "min"),
            max_lost_ivf=("fe_lost_ivf", "max"),
            max_lost_base=("fe_lost_base", "max"),
        ).reset_index()
        print("Summary by algorithm pair:")
        for _, s in summary.iterrows():
            print(f"  {s['ivf_algo']} vs {s['base_algo']}: "
                  f"{s['total_runs']} runs, "
                  f"mean match={s['mean_match_pct']:.1f}%, "
                  f"min match={s['min_match_pct']:.1f}%")

        diag_df.to_csv(OUT_DIAG, index=False)
        print(f"\nDetailed diagnostic: {OUT_DIAG}")
        print(f"Total rows: {len(diag_df)}")
        print(f"Runs with <100% match: {(diag_df['match_pct'] < 100).sum()}")
    else:
        print("No data to diagnose.")


if __name__ == "__main__":
    main()
