#!/usr/bin/env python3
"""
Compute warmup horizon sensitivity data for Figure 3.

Generates early-turnover statistics and switching performance at 6 horizons
[0.05, 0.10, 0.15, 0.20, 0.25, 0.30] directly from raw .mat trajectory files.

Output: data/processed/warmup_horizon_sensitivity.csv
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from utils import (
    PROJECT_ROOT,
    RAW_DIR,
    DATA_PROCESSED,
    build_response_map,
    collect_paired_files,
    select_pairs_for_analysis,
    extract_run_features,
    aggregate_value,
    compute_a12,
    family_of,
    lofo_threshold_eval,
)

CASES_MANIFEST = PROJECT_ROOT / "config" / "ppsn_dynamics_cases_full.csv"
RESPONSE_CSV = PROJECT_ROOT / "data" / "processed" / "fla_response.csv"
OUT_CSV = DATA_PROCESSED / "warmup_horizon_sensitivity.csv"

EARLY_FRACS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
MAX_RUNS = 30
MIN_RUNS = 3
AGG_METHOD = "median"

LABEL_COL = "label_binary_eval"


def main() -> None:
    if not CASES_MANIFEST.exists():
        print(f"ERROR: cases manifest not found: {CASES_MANIFEST}")
        sys.exit(1)
    if not RESPONSE_CSV.exists():
        print(f"ERROR: response CSV not found: {RESPONSE_CSV}")
        sys.exit(1)

    cases = pd.read_csv(CASES_MANIFEST)
    response_df = pd.read_csv(RESPONSE_CSV)
    response_map = build_response_map(response_df)

    print(f"Cases: {len(cases)}")
    print(f"Horizons: {[f'{h:.0%}' for h in EARLY_FRACS]}")
    print(f"Max runs/case: {MAX_RUNS}")

    ivf_root = RAW_DIR / "ivf"
    spea2_root = RAW_DIR / "spea2"

    # --- Phase 1: compute per-case summaries at each horizon ---
    config_rows = []
    n_total = 0
    n_complete = 0

    for _, case_row in cases.iterrows():
        case_id = str(case_row["case_id"])
        ivf_dir = ivf_root / case_id
        spea2_dir = spea2_root / case_id

        if not ivf_dir.exists() or not spea2_dir.exists():
            print(f"  SKIP {case_id}: missing directories")
            continue

        paired_files = collect_paired_files(ivf_dir, spea2_dir)
        if len(paired_files) < MIN_RUNS:
            print(f"  SKIP {case_id}: only {len(paired_files)} paired runs")
            continue

        selected = select_pairs_for_analysis(paired_files, MAX_RUNS)
        n_total += 1

        # Accumulate per-run features for each horizon
        records_by_frac: dict[float, list[dict]] = {f: [] for f in EARLY_FRACS}

        for run_id, ivf_path, spea2_path in selected:
            try:
                ivf_gens = _load(ivf_path)
                spea2_gens = _load(spea2_path)
            except Exception as exc:
                print(f"  [WARN] {case_id} run {run_id}: {exc}")
                continue
            for frac in EARLY_FRACS:
                feats = extract_run_features(ivf_gens, spea2_gens, frac)
                if feats is not None:
                    feats["run_id"] = run_id
                    records_by_frac[frac].append(feats)

        # Aggregate per horizon
        for frac in EARLY_FRACS:
            recs = records_by_frac[frac]
            if len(recs) < MIN_RUNS:
                continue
            # Get label from the full independent-cohort response
            problem = str(case_row["problem"])
            m = int(case_row["m"])
            key = f"{problem.upper()}_M{m}"
            resp = response_map.get(key, {})

            row = {
                "case_id": case_id,
                "problem": problem,
                "m": m,
                "d": int(case_row["d"]),
                "family": family_of(case_id),
                "early_frac": float(frac),
                "label_binary": resp.get("response_label", ""),
                "n_runs": len(recs),
                "ivf_turnover_early": aggregate_value(
                    [r["ivf_turnover_early"] for r in recs], AGG_METHOD
                ),
                "spea2_turnover_early": aggregate_value(
                    [r["spea2_turnover_early"] for r in recs], AGG_METHOD
                ),
            }
            config_rows.append(row)

        n_complete += 1
        print(f"  [{n_complete}] {case_id}: {len(selected)} paired runs")

    config_df = pd.DataFrame(config_rows)
    print(f"\nConfig rows: {len(config_df)}")
    print(f"Cases with data: {n_complete}/{n_total}")

    # Build evaluation labels (same logic as test_dynamic_signal.py)
    config_df[LABEL_COL] = config_df["label_binary"].apply(
        lambda x: x if x in ("HELPS", "NOT_HELPS") else ""
    )

    # --- Phase 2: per-horizon sensitivity metrics ---
    result_rows = []
    for frac in sorted(config_df["early_frac"].unique()):
        df_frac = config_df[config_df["early_frac"] == frac].copy()
        df_labeled = df_frac[df_frac[LABEL_COL].isin(["HELPS", "NOT_HELPS"])].copy()

        if len(df_labeled) < 10:
            print(f"  WARN: horizon {frac:.0%} has only {len(df_labeled)} labeled cases")
            continue

        helps = df_labeled.loc[df_labeled[LABEL_COL] == "HELPS", "ivf_turnover_early"].dropna()
        not_helps = df_labeled.loc[df_labeled[LABEL_COL] == "NOT_HELPS", "ivf_turnover_early"].dropna()

        # A12 (discriminatory strength)
        a12 = compute_a12(helps.to_numpy(), not_helps.to_numpy())

        # Mann-Whitney p-value
        _, p_raw = stats_ref(helps, not_helps)

        # LFO-CV threshold rule performance
        lofo = lofo_threshold_eval(df_labeled, "ivf_turnover_early", LABEL_COL)

        result_rows.append({
            "early_frac": float(frac),
            "early_frac_pct": float(frac) * 100,
            "n_cases": int(len(df_labeled)),
            "n_helps": int((df_labeled[LABEL_COL] == "HELPS").sum()),
            "n_not_helps": int((df_labeled[LABEL_COL] == "NOT_HELPS").sum()),
            "median_helps": float(helps.median()),
            "median_not_helps": float(not_helps.median()),
            "a12": float(a12),
            "p_mannwhitney": float(p_raw),
            "balanced_accuracy": float(lofo.get("balanced_accuracy", np.nan)),
            "mcc": float(lofo.get("mcc", np.nan)),
            "sensitivity": float(lofo.get("sensitivity", np.nan)),
            "specificity": float(lofo.get("specificity", np.nan)),
        })
        print(f"  frac={frac:.0%}: a12={a12:.3f}, BA={lofo.get('balanced_accuracy', np.nan):.3f}, "
              f"MCC={lofo.get('mcc', np.nan):.3f}")

    result_df = pd.DataFrame(result_rows)
    result_df = result_df.sort_values("early_frac").reset_index(drop=True)

    # Also save the per-case config for reuse
    config_path = DATA_PROCESSED / "warmup_horizon_config.csv"
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    config_df.to_csv(config_path, index=False)
    print(f"Case-level config saved: {config_path}")

    result_df.to_csv(OUT_CSV, index=False)
    print(f"Sensitivity summary saved: {OUT_CSV}")
    print(f"  Columns: {list(result_df.columns)}")
    print(f"  Rows: {len(result_df)}")


def _load(path: Path) -> list[dict]:
    from pymatreader import read_mat
    data = read_mat(str(path))
    gens = data.get("trace_generations", [])
    if isinstance(gens, dict):
        gens = [gens]
    elif isinstance(gens, np.ndarray):
        gens = list(gens)
    return gens


def stats_ref(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    from scipy import stats as st
    u, p = st.mannwhitneyu(x.dropna().to_numpy(), y.dropna().to_numpy(),
                           alternative="two-sided")
    return float(u), float(p)


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    main()
