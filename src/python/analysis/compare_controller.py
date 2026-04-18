#!/usr/bin/env python3
"""
Controller vs IVF vs SPEA2 -- final-metric comparison for PPSN 2026.

For every case in the dynamics manifest, this script:
  1. Loads all .mat traces from ivf/, spea2/, controller/
  2. Extracts the final-generation IGD and HV that MATLAB already computed
  3. Uses paired Wilcoxon signed-rank tests when common run IDs exist
  4. Falls back to Mann-Whitney rank-sum only when pairing is unavailable
  5. Computes Vargha-Delaney A12 effect sizes
  6. Applies Benjamini-Hochberg FDR correction across all cases
  7. Saves a summary CSV to data/processed/ppsn_controller_comparison.csv

Usage:
    python src/python/analysis/compare_controller.py
    python src/python/analysis/compare_controller.py \
        --ctrl-root data/raw/ppsn_dynamics/controller_oos_lofo_parallel_20260326_221909 \
        --output-csv data/processed/ppsn_controller_comparison_oos_20260326_221909.csv
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics"
REF_PF_DIR = RAW_DIR / "reference_pf"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
CASES_CSV = PROJECT_ROOT / "config" / "ppsn_dynamics_cases_full.csv"
OUTPUT_CSV = DATA_PROCESSED / "ppsn_controller_comparison.csv"
ALGO_PREFIXES = {
    "ivf": "IVF_",
    "spea2": "SPEA2_",
    "ctrl": "CTRL_",
}

# Cases to exclude (engineering problems that require special PF handling)
EXCLUDE_CASES = {"rwmop9_m2"}

# Minimum number of runs required per algorithm for a valid comparison
MIN_RUNS = 3

# Alpha level for significance interpretation in the text summary
ALPHA = 0.05
EFFECT_LOW = 0.44
EFFECT_HIGH = 0.56


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare controller traces against IVF and SPEA2 baselines."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=CASES_CSV,
        help="Benchmark manifest CSV. Default: %(default)s",
    )
    parser.add_argument(
        "--ivf-root",
        type=Path,
        default=RAW_DIR / "ivf",
        help="Directory containing IVF trace subdirectories. Default: %(default)s",
    )
    parser.add_argument(
        "--spea2-root",
        type=Path,
        default=RAW_DIR / "spea2",
        help="Directory containing SPEA2 trace subdirectories. Default: %(default)s",
    )
    parser.add_argument(
        "--ctrl-root",
        type=Path,
        default=RAW_DIR / "controller",
        help="Directory containing controller trace subdirectories. Default: %(default)s",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=OUTPUT_CSV,
        help="Output CSV path. Default: %(default)s",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_run_id(mat_path: Path) -> int | None:
    """Extract the numeric run ID from a filename like PREFIX_PROB_M2_D11_70121.mat."""
    match = re.search(r"_(\d+)\.mat$", mat_path.name)
    if match is None:
        return None
    return int(match.group(1))


def load_final_metrics(mat_path: Path) -> dict | None:
    """Load the final-generation IGD and HV from a dynamics trace .mat file.

    Returns a dict with keys 'igd' and 'hv', or None on failure.
    """
    from pymatreader import read_mat

    try:
        data = read_mat(str(mat_path))
    except Exception as exc:
        print(f"  WARN: Could not read {mat_path.name}: {exc}")
        return None

    gens = data.get("trace_generations")
    if gens is None or len(gens) == 0:
        return None

    # pymatreader may return a single dict instead of a list
    if isinstance(gens, dict):
        gens = [gens]

    last = gens[-1]
    igd = last.get("igd")
    hv = last.get("hv")
    if igd is None or hv is None:
        return None
    if not np.isfinite(igd) or not np.isfinite(hv):
        return None

    return {"igd": float(igd), "hv": float(hv)}


def collect_algo_runs(
    algo_dir: Path, case_id: str, prefix: str
) -> dict[int, Path]:
    """Map run_id -> Path for all .mat files of a given algorithm/case."""
    case_dir = algo_dir / case_id
    if not case_dir.is_dir():
        return {}
    result: dict[int, Path] = {}
    for p in case_dir.glob(f"{prefix}*.mat"):
        rid = extract_run_id(p)
        if rid is not None:
            result[rid] = p
    return result


def vargha_delaney_a12(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Vargha-Delaney A12 effect size.

    A12 > 0.5 means x tends to have *larger* values than y.
    For IGD (lower is better), A12 < 0.5 means x is better.
    For HV  (higher is better), A12 > 0.5 means x is better.
    """
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return np.nan
    # Use Mann-Whitney U statistic definition: U = sum of ranks of x - nx*(nx+1)/2
    # A12 = U / (nx * ny)
    # scipy's mannwhitneyu with alternative='two-sided' returns U
    # But to be explicit and avoid confusion with scipy internals:
    more = 0.0
    equal = 0.0
    for xi in x:
        for yj in y:
            if xi > yj:
                more += 1.0
            elif xi == yj:
                equal += 0.5
    return (more + equal) / (nx * ny)


def bh_fdr_adjust(p_values: list[float]) -> np.ndarray:
    """Benjamini-Hochberg FDR correction on a list of p-values."""
    if not p_values:
        return np.array([])
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ordered = p[order]
    adjusted = np.empty_like(ordered)
    running = 1.0
    for i in range(n - 1, -1, -1):
        rank = i + 1
        current = min(1.0, (ordered[i] * n) / rank)
        running = min(running, current)
        adjusted[i] = running
    result = np.empty_like(adjusted)
    result[order] = adjusted
    return result


def compare_p_values(
    x: np.ndarray, y: np.ndarray, paired: bool
) -> tuple[float, str]:
    """Return p-value and test name for one comparison.

    Uses paired Wilcoxon signed-rank when runs are seed-aligned.
    Falls back to Mann-Whitney U only when pairing is unavailable.
    """
    if len(x) < MIN_RUNS or len(y) < MIN_RUNS:
        return np.nan, "insufficient_runs"

    if paired:
        try:
            diff = x - y
            if np.allclose(diff, 0.0):
                return 1.0, "wilcoxon_signed_rank"
            _, p = stats.wilcoxon(
                x,
                y,
                alternative="two-sided",
                zero_method="pratt",
                correction=False,
                mode="auto",
            )
            return float(p), "wilcoxon_signed_rank"
        except ValueError:
            return np.nan, "wilcoxon_signed_rank"

    try:
        _, p = stats.mannwhitneyu(x, y, alternative="two-sided")
        return float(p), "mannwhitneyu"
    except ValueError:
        return np.nan, "mannwhitneyu"


# ---------------------------------------------------------------------------
# Core comparison per case/metric
# ---------------------------------------------------------------------------
def compare_case(
    case_id: str,
    ctrl_values: np.ndarray,
    ivf_values: np.ndarray,
    spea2_values: np.ndarray,
    metric: str,
    paired: bool,
) -> dict:
    """Build a comparison row for one case + metric triple."""
    row: dict = {
        "case_id": case_id,
        "metric": metric,
        "test_method": "wilcoxon_signed_rank" if paired else "mannwhitneyu",
        "n_ctrl": len(ctrl_values),
        "n_ivf": len(ivf_values),
        "n_spea2": len(spea2_values),
        "median_ctrl": float(np.median(ctrl_values)) if len(ctrl_values) else np.nan,
        "iqr_ctrl": float(np.subtract(*np.percentile(ctrl_values, [75, 25]))) if len(ctrl_values) else np.nan,
        "median_ivf": float(np.median(ivf_values)) if len(ivf_values) else np.nan,
        "iqr_ivf": float(np.subtract(*np.percentile(ivf_values, [75, 25]))) if len(ivf_values) else np.nan,
        "median_spea2": float(np.median(spea2_values)) if len(spea2_values) else np.nan,
        "iqr_spea2": float(np.subtract(*np.percentile(spea2_values, [75, 25]))) if len(spea2_values) else np.nan,
    }

    # CTRL vs IVF
    if len(ctrl_values) >= MIN_RUNS and len(ivf_values) >= MIN_RUNS:
        row["p_ctrl_vs_ivf"], _ = compare_p_values(ctrl_values, ivf_values, paired)
        row["a12_ctrl_vs_ivf"] = vargha_delaney_a12(ctrl_values, ivf_values)
    else:
        row["p_ctrl_vs_ivf"] = np.nan
        row["a12_ctrl_vs_ivf"] = np.nan

    # CTRL vs SPEA2
    if len(ctrl_values) >= MIN_RUNS and len(spea2_values) >= MIN_RUNS:
        row["p_ctrl_vs_spea2"], _ = compare_p_values(
            ctrl_values, spea2_values, paired
        )
        row["a12_ctrl_vs_spea2"] = vargha_delaney_a12(ctrl_values, spea2_values)
    else:
        row["p_ctrl_vs_spea2"] = np.nan
        row["a12_ctrl_vs_spea2"] = np.nan

    return row


# ---------------------------------------------------------------------------
# Win / Tie / Loss counting
# ---------------------------------------------------------------------------
def classify_outcome(
    p_bh: float, a12: float, metric: str
) -> str:
    """Classify a comparison as win / tie / loss for the first algorithm (CTRL).

    Convention:
      - IGD  (lower is better):  A12 < 0.44 means CTRL is better -> 'win'
      - HV   (higher is better): A12 > 0.56 means CTRL is better -> 'win'
    Significance gate: p_bh < ALPHA and non-negligible effect size.
    """
    if np.isnan(p_bh) or np.isnan(a12):
        return "skip"
    if p_bh >= ALPHA:
        return "tie"
    # Significant difference exists
    if metric == "IGD":
        if a12 < EFFECT_LOW:
            return "win"
        if a12 > EFFECT_HIGH:
            return "loss"
        return "tie"
    else:  # HV
        if a12 > EFFECT_HIGH:
            return "win"
        if a12 < EFFECT_LOW:
            return "loss"
        return "tie"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    args = parse_args()
    algo_dirs = {
        "ivf": args.ivf_root,
        "spea2": args.spea2_root,
        "ctrl": args.ctrl_root,
    }

    print("=" * 70)
    print("CONTROLLER vs IVF vs SPEA2 -- final-metric comparison")
    print("=" * 70)
    print(f"CTRL root:  {algo_dirs['ctrl']}")
    print(f"IVF root:   {algo_dirs['ivf']}")
    print(f"SPEA2 root: {algo_dirs['spea2']}")
    print(f"Output CSV: {args.output_csv}")

    # ---- Load manifest ----
    if not args.manifest.exists():
        print(f"ERROR: manifest not found: {args.manifest}")
        sys.exit(1)

    cases = pd.read_csv(args.manifest)
    cases = cases[~cases["case_id"].isin(EXCLUDE_CASES)].reset_index(drop=True)
    print(f"Manifest: {args.manifest}")
    print(f"Cases after exclusions: {len(cases)}")

    # ---- Iterate cases ----
    all_rows: list[dict] = []
    cases_processed = 0
    cases_skipped_missing = 0
    cases_skipped_runs = 0

    for _, case_row in cases.iterrows():
        case_id = str(case_row["case_id"])

        # Collect run files for each algorithm
        algo_runs: dict[str, dict[int, Path]] = {}
        for algo_key in ("ctrl", "ivf", "spea2"):
            algo_runs[algo_key] = collect_algo_runs(
                algo_dirs[algo_key], case_id, ALGO_PREFIXES[algo_key]
            )

        # Check that all three algorithms have data
        algo_counts = {k: len(v) for k, v in algo_runs.items()}
        missing_algos = [k for k, c in algo_counts.items() if c == 0]
        if missing_algos:
            print(f"  SKIP {case_id}: no data for {', '.join(missing_algos)}")
            cases_skipped_missing += 1
            continue

        # Find common run IDs (paired across all three algorithms)
        common_run_ids = sorted(
            set(algo_runs["ctrl"].keys())
            & set(algo_runs["ivf"].keys())
            & set(algo_runs["spea2"].keys())
        )

        # If no common IDs, fall back to using all available runs per algorithm
        use_paired = len(common_run_ids) >= MIN_RUNS
        if use_paired:
            run_ids_per_algo = {
                "ctrl": common_run_ids,
                "ivf": common_run_ids,
                "spea2": common_run_ids,
            }
            pairing_note = f"paired, n={len(common_run_ids)}"
        else:
            # Use all available runs per algorithm (unpaired comparison)
            run_ids_per_algo = {
                k: sorted(v.keys()) for k, v in algo_runs.items()
            }
            pairing_note = (
                f"unpaired, ctrl={algo_counts['ctrl']}, "
                f"ivf={algo_counts['ivf']}, spea2={algo_counts['spea2']}"
            )

        # Load final metrics for selected runs
        algo_metrics: dict[str, list[dict]] = {"ctrl": [], "ivf": [], "spea2": []}
        for algo_key in ("ctrl", "ivf", "spea2"):
            for rid in run_ids_per_algo[algo_key]:
                mat_path = algo_runs[algo_key].get(rid)
                if mat_path is None:
                    continue
                metrics = load_final_metrics(mat_path)
                if metrics is not None:
                    algo_metrics[algo_key].append(metrics)

        # Check minimum runs
        valid_counts = {k: len(v) for k, v in algo_metrics.items()}
        insufficient = [k for k, c in valid_counts.items() if c < MIN_RUNS]
        if insufficient:
            print(
                f"  SKIP {case_id}: insufficient valid runs for "
                f"{', '.join(insufficient)} ({valid_counts})"
            )
            cases_skipped_runs += 1
            continue

        # Extract arrays per metric
        for metric in ("IGD", "HV"):
            key = metric.lower()
            ctrl_vals = np.array([m[key] for m in algo_metrics["ctrl"]])
            ivf_vals = np.array([m[key] for m in algo_metrics["ivf"]])
            spea2_vals = np.array([m[key] for m in algo_metrics["spea2"]])

            row = compare_case(
                case_id, ctrl_vals, ivf_vals, spea2_vals, metric, paired=use_paired
            )
            row["pairing"] = "paired" if use_paired else "unpaired"
            all_rows.append(row)

        cases_processed += 1
        print(
            f"  {case_id}: OK ({pairing_note}, "
            f"ctrl={valid_counts['ctrl']}, ivf={valid_counts['ivf']}, "
            f"spea2={valid_counts['spea2']})"
        )

    # ---- Summary stats ----
    print(f"\nCases processed: {cases_processed}")
    print(f"Cases skipped (missing algorithm data): {cases_skipped_missing}")
    print(f"Cases skipped (insufficient runs): {cases_skipped_runs}")

    if not all_rows:
        print("\nERROR: No cases had sufficient data for all three algorithms.")
        print("The controller experiment may still be running. Re-run when data arrives.")
        sys.exit(0)

    df = pd.DataFrame(all_rows)

    # ---- Benjamini-Hochberg correction across all cases ----
    for p_col, bh_col in [
        ("p_ctrl_vs_ivf", "p_bh_ctrl_vs_ivf"),
        ("p_ctrl_vs_spea2", "p_bh_ctrl_vs_spea2"),
    ]:
        valid_mask = df[p_col].notna()
        if valid_mask.sum() > 0:
            adjusted = bh_fdr_adjust(df.loc[valid_mask, p_col].tolist())
            df.loc[valid_mask, bh_col] = adjusted
        else:
            df[bh_col] = np.nan

    # ---- Save CSV ----
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    # Column ordering for clarity
    col_order = [
        "case_id",
        "metric",
        "pairing",
        "test_method",
        "n_ctrl",
        "n_ivf",
        "n_spea2",
        "median_ctrl",
        "iqr_ctrl",
        "median_ivf",
        "iqr_ivf",
        "median_spea2",
        "iqr_spea2",
        "p_ctrl_vs_ivf",
        "p_bh_ctrl_vs_ivf",
        "a12_ctrl_vs_ivf",
        "p_ctrl_vs_spea2",
        "p_bh_ctrl_vs_spea2",
        "a12_ctrl_vs_spea2",
    ]
    # Only keep columns that exist (in case BH columns were not created)
    col_order = [c for c in col_order if c in df.columns]
    df = df[col_order].sort_values(["metric", "case_id"]).reset_index(drop=True)

    df.to_csv(args.output_csv, index=False)
    print(f"\nSaved: {args.output_csv}")

    # ---- Text summary of wins / ties / losses ----
    print("\n" + "=" * 70)
    print("WIN / TIE / LOSS SUMMARY  (BH-corrected, alpha={:.2f})".format(ALPHA))
    print("=" * 70)

    for metric in ("IGD", "HV"):
        metric_df = df[df["metric"] == metric]
        if metric_df.empty:
            continue

        print(f"\n--- {metric} ---")

        for comparison, p_bh_col, a12_col in [
            ("CTRL vs IVF", "p_bh_ctrl_vs_ivf", "a12_ctrl_vs_ivf"),
            ("CTRL vs SPEA2", "p_bh_ctrl_vs_spea2", "a12_ctrl_vs_spea2"),
        ]:
            if p_bh_col not in metric_df.columns:
                continue

            outcomes = []
            for _, row in metric_df.iterrows():
                p_bh = row.get(p_bh_col, np.nan)
                a12 = row.get(a12_col, np.nan)
                outcomes.append(classify_outcome(p_bh, a12, metric))

            wins = outcomes.count("win")
            ties = outcomes.count("tie")
            losses = outcomes.count("loss")
            skips = outcomes.count("skip")
            total = wins + ties + losses

            print(
                f"  {comparison:16s}: "
                f"W={wins:2d}  T={ties:2d}  L={losses:2d}  "
                f"(of {total} testable cases"
                + (f", {skips} skipped" if skips else "")
                + ")"
            )

    # ---- Per-case detail table ----
    print("\n" + "=" * 70)
    print("PER-CASE DETAIL")
    print("=" * 70)
    header = (
        f"{'Case':<16} {'Metric':<5} "
        f"{'Med CTRL':>10} {'Med IVF':>10} {'Med SP2':>10} "
        f"{'p(C-I)':>8} {'A12(C-I)':>8} "
        f"{'p(C-S)':>8} {'A12(C-S)':>8}"
    )
    print(header)
    print("-" * len(header))

    for _, row in df.iterrows():
        p_ci = row.get("p_bh_ctrl_vs_ivf", np.nan)
        p_cs = row.get("p_bh_ctrl_vs_spea2", np.nan)
        a12_ci = row.get("a12_ctrl_vs_ivf", np.nan)
        a12_cs = row.get("a12_ctrl_vs_spea2", np.nan)

        p_ci_s = f"{p_ci:.4f}" if np.isfinite(p_ci) else "  --  "
        p_cs_s = f"{p_cs:.4f}" if np.isfinite(p_cs) else "  --  "
        a12_ci_s = f"{a12_ci:.3f}" if np.isfinite(a12_ci) else "  --  "
        a12_cs_s = f"{a12_cs:.3f}" if np.isfinite(a12_cs) else "  --  "

        med_ctrl = f"{row['median_ctrl']:.6e}" if np.isfinite(row["median_ctrl"]) else "    --    "
        med_ivf = f"{row['median_ivf']:.6e}" if np.isfinite(row["median_ivf"]) else "    --    "
        med_spea2 = f"{row['median_spea2']:.6e}" if np.isfinite(row["median_spea2"]) else "    --    "

        print(
            f"{row['case_id']:<16} {row['metric']:<5} "
            f"{med_ctrl:>10} {med_ivf:>10} {med_spea2:>10} "
            f"{p_ci_s:>8} {a12_ci_s:>8} "
            f"{p_cs_s:>8} {a12_cs_s:>8}"
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
