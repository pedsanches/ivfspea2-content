#!/usr/bin/env python3
"""
Compute claim-oriented summary statistics for tab:claims_summary.
=================================================================
Produces wins/losses/ties for the primary comparison (IVF/SPEA2 vs SPEA2)
under four conditions per metric:
  1. All instances, unadjusted Wilcoxon
  2. Out-of-sample instances only (OOS = outside FULL12), unadjusted
  3. All instances, Holm-Bonferroni corrected
  4. OOS instances only, Holm-Bonferroni corrected (Holm applied to all
     instances first, then filtered to OOS)

Metrics: IGD (lower is better), HV (higher is better).

Run-cohort policy (synthetic only):
  - IVF/SPEA2 rows are restricted to run IDs 3001..3060
  - baseline rows are restricted to run IDs 1..60
Engineering rows (RWMOP*) are excluded from this script.

Output:
  - results/tables/claims_summary_audit.csv  (machine-readable)
  - Console report for direct copy into LaTeX
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

try:
    from cohort_filter import (
        BASELINE_RUN_MAX,
        BASELINE_RUN_MIN,
        IVF_ALGORITHM,
        IVF_RUN_MAX,
        IVF_RUN_MIN,
        build_group_coverage,
        filter_submission_synthetic_cohort,
    )
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import (
        BASELINE_RUN_MAX,
        BASELINE_RUN_MIN,
        IVF_ALGORITHM,
        IVF_RUN_MAX,
        IVF_RUN_MIN,
        build_group_coverage,
        filter_submission_synthetic_cohort,
    )

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "tables")

# ---------------------------------------------------------------------------
# FULL12 tuning subset (from Section 4.7 of the paper)
# ---------------------------------------------------------------------------
FULL12 = {
    ("ZDT1", "M2"),
    ("ZDT6", "M2"),
    ("WFG4", "M2"),
    ("WFG9", "M2"),
    ("DTLZ1", "M3"),
    ("DTLZ2", "M3"),
    ("DTLZ4", "M3"),
    ("DTLZ7", "M3"),
    ("WFG2", "M3"),
    ("WFG5", "M3"),
    ("MaF1", "M3"),
    ("MaF5", "M3"),
}

ALPHA = 0.05


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni step-down correction."""
    m = len(p_values)
    if m == 0:
        return []
    order = np.argsort(p_values)
    adjusted_sorted = np.zeros(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        mult = m - rank
        val = min(1.0, float(p_values[idx]) * mult)
        running = max(running, val)
        adjusted_sorted[rank] = running

    adjusted = np.zeros(m, dtype=float)
    for rank, idx in enumerate(order):
        adjusted[idx] = adjusted_sorted[rank]
    return adjusted.tolist()


def compute_pairwise(
    df: pd.DataFrame,
    m_filter: str,
    metric: str,
    higher_is_better: bool,
    alpha: float = ALPHA,
) -> pd.DataFrame:
    """
    Compute per-instance Wilcoxon results for IVF/SPEA2 vs SPEA2.

    Returns DataFrame with columns:
      Problema, M, p_raw, direction_raw, is_full12
    """
    subset = df[df["M"] == m_filter]
    problems = sorted(subset["Problema"].unique())

    rows = []
    for prob in problems:
        prob_data = subset[subset["Problema"] == prob]
        ivf_vals = (
            prob_data[prob_data["Algoritmo"] == "IVFSPEA2"][metric].dropna().values
        )
        spea2_vals = (
            prob_data[prob_data["Algoritmo"] == "SPEA2"][metric].dropna().values
        )

        if len(ivf_vals) < 3 or len(spea2_vals) < 3:
            rows.append(
                {
                    "Problema": prob,
                    "M": m_filter,
                    "p_raw": 1.0,
                    "direction_raw": "=",
                    "is_full12": (prob, m_filter) in FULL12,
                }
            )
            continue

        _, p_raw = mannwhitneyu(ivf_vals, spea2_vals, alternative="two-sided")

        # Determine direction from medians
        med_ivf = np.median(ivf_vals)
        med_spea2 = np.median(spea2_vals)
        if higher_is_better:
            if med_ivf > med_spea2:
                direction = "+"
            elif med_ivf < med_spea2:
                direction = "-"
            else:
                direction = "="
        else:
            if med_ivf < med_spea2:
                direction = "+"
            elif med_ivf > med_spea2:
                direction = "-"
            else:
                direction = "="

        rows.append(
            {
                "Problema": prob,
                "M": m_filter,
                "p_raw": float(p_raw),
                "direction_raw": direction,
                "is_full12": (prob, m_filter) in FULL12,
            }
        )

    result = pd.DataFrame(rows)

    # Holm-Bonferroni correction across all instances in this M
    result["p_holm"] = holm_adjust(result["p_raw"].tolist())

    # Unadjusted indicator
    result["indicator_raw"] = result.apply(
        lambda r: r["direction_raw"] if r["p_raw"] < alpha else "=", axis=1
    )

    # Holm-corrected indicator
    result["indicator_holm"] = result.apply(
        lambda r: r["direction_raw"] if r["p_holm"] < alpha else "=", axis=1
    )

    return result


def count_wlt(series: pd.Series) -> tuple[int, int, int]:
    """Count wins/losses/ties from indicator series."""
    wins = (series == "+").sum()
    losses = (series == "-").sum()
    ties = (series == "=").sum()
    return int(wins), int(losses), int(ties)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Data file not found: {DATA_PATH}")
        sys.exit(1)

    raw_df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(raw_df)} rows")

    df = filter_submission_synthetic_cohort(raw_df)
    print(
        "Applied canonical synthetic run-cohort filter: "
        f"{IVF_ALGORITHM} in [{IVF_RUN_MIN},{IVF_RUN_MAX}], "
        f"baselines in [{BASELINE_RUN_MIN},{BASELINE_RUN_MAX}]"
    )
    print(f"Rows after filter: {len(df)}")

    coverage = build_group_coverage(df)
    synth_cov = coverage[coverage["expected_window"] != "engineering_external"]
    mismatches = synth_cov[synth_cov["status"] != "ok"]
    if len(mismatches) > 0:
        print("WARNING: cohort mismatches detected after filtering:")
        print(mismatches.to_string(index=False))
    else:
        print("Cohort coverage check: all synthetic groups match expected windows")

    pair_cov = (
        df[df["Algoritmo"].isin([IVF_ALGORITHM, "SPEA2"])]
        .groupby(["Problema", "M", "Algoritmo"])["Run"]
        .nunique()
        .unstack(fill_value=0)
        .reset_index()
    )
    print(
        "Pair coverage (IVF/SPEA2 vs SPEA2): "
        f"{len(pair_cov)} instances, "
        f"min runs IVF={pair_cov[IVF_ALGORITHM].min()}, "
        f"min runs SPEA2={pair_cov['SPEA2'].min()}"
    )

    summary_rows = []
    detail_rows = []

    for metric, higher_is_better in [("IGD", False), ("HV", True)]:
        print(f"\n{'=' * 60}")
        print(f"  {metric} — IVF/SPEA2 vs SPEA2 (primary comparison)")
        print(f"{'=' * 60}")

        for m_val in ["M2", "M3"]:
            result = compute_pairwise(df, m_val, metric, higher_is_better)
            n_total = len(result)
            oos = result[~result["is_full12"]]
            n_oos = len(oos)

            # 1. All instances, unadjusted
            w, l, t = count_wlt(result["indicator_raw"])
            label = f"{metric}, unadjusted"
            print(f"\n  {m_val} — {label}: {w}/{l}/{t}  (n={n_total})")
            summary_rows.append(
                {
                    "metric": metric,
                    "condition": "unadjusted",
                    "M": m_val,
                    "wins": w,
                    "losses": l,
                    "ties": t,
                    "n": n_total,
                }
            )

            # 2. OOS only, unadjusted
            w_oos, l_oos, t_oos = count_wlt(oos["indicator_raw"])
            label_oos = f"{metric}, unadjusted, OOS"
            print(f"  {m_val} — {label_oos}: {w_oos}/{l_oos}/{t_oos}  (n={n_oos})")
            summary_rows.append(
                {
                    "metric": metric,
                    "condition": "unadjusted_OOS",
                    "M": m_val,
                    "wins": w_oos,
                    "losses": l_oos,
                    "ties": t_oos,
                    "n": n_oos,
                }
            )

            # 3. All instances, Holm-corrected
            w_h, l_h, t_h = count_wlt(result["indicator_holm"])
            label_holm = f"{metric}, Holm"
            print(f"  {m_val} — {label_holm}: {w_h}/{l_h}/{t_h}  (n={n_total})")
            summary_rows.append(
                {
                    "metric": metric,
                    "condition": "Holm",
                    "M": m_val,
                    "wins": w_h,
                    "losses": l_h,
                    "ties": t_h,
                    "n": n_total,
                }
            )

            # 4. OOS only, Holm-corrected (Holm applied to all, then filtered)
            w_oh, l_oh, t_oh = count_wlt(oos["indicator_holm"])
            label_holm_oos = f"{metric}, Holm, OOS"
            print(f"  {m_val} — {label_holm_oos}: {w_oh}/{l_oh}/{t_oh}  (n={n_oos})")
            summary_rows.append(
                {
                    "metric": metric,
                    "condition": "Holm_OOS",
                    "M": m_val,
                    "wins": w_oh,
                    "losses": l_oh,
                    "ties": t_oh,
                    "n": n_oos,
                }
            )

            # Per-instance detail
            print(f"\n  Per-instance detail ({m_val}):")
            for _, r in result.iterrows():
                full12_mark = " [FULL12]" if r["is_full12"] else ""
                print(
                    f"    {r['Problema']:12s}  "
                    f"p_raw={r['p_raw']:.4e}  p_holm={r['p_holm']:.4e}  "
                    f"raw={r['indicator_raw']}  holm={r['indicator_holm']}"
                    f"{full12_mark}"
                )
                detail_rows.append(
                    {
                        "metric": metric,
                        "M": m_val,
                        "Problema": r["Problema"],
                        "is_full12": bool(r["is_full12"]),
                        "p_raw": float(r["p_raw"]),
                        "p_holm": float(r["p_holm"]),
                        "indicator_raw": r["indicator_raw"],
                        "indicator_holm": r["indicator_holm"],
                    }
                )

    # Save audit CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    audit_df = pd.DataFrame(summary_rows)
    audit_path = os.path.join(OUTPUT_DIR, "claims_summary_audit.csv")
    audit_df.to_csv(audit_path, index=False)
    print(f"\nAudit CSV saved: {audit_path}")

    detail_df = pd.DataFrame(detail_rows)
    detail_path = os.path.join(OUTPUT_DIR, "claims_summary_instance_details.csv")
    detail_df.to_csv(detail_path, index=False)
    print(f"Instance-level detail CSV saved: {detail_path}")

    # Print LaTeX-ready summary
    print("\n" + "=" * 60)
    print("  LaTeX-ready claims_summary rows")
    print("=" * 60)
    print()
    for _, r in audit_df.iterrows():
        label_map = {
            "unadjusted": f"{r['metric']}, unadjusted",
            "unadjusted_OOS": f"{r['metric']}, unadjusted, OOS",
            "Holm": f"{r['metric']}, Holm",
            "Holm_OOS": f"{r['metric']}, Holm, OOS",
        }
        label = label_map.get(r["condition"], r["condition"])
        m2_col = f"{r['wins']}/{r['losses']}/{r['ties']}"
        print(f"  {label:40s} & {r['M']:3s} => {m2_col}")


if __name__ == "__main__":
    main()
