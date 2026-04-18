#!/usr/bin/env python3
"""Extract IGD and HV convergence traces from PlatEMO .mat files.

This extractor targets the synthetic 51-instance hosts paper suite and reads the
standard per-host run ranges directly from PlatEMO/Data. It is designed for the
all-suite A7 gate, so it excludes engineering-only RWMOP9 by default.
"""

import glob
import os

import numpy as np
import pandas as pd
import pymatreader


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_ROOT = os.path.join(PROJECT_ROOT, "src", "matlab", "lib", "PlatEMO", "Data")
INSTANCES_CSV = os.path.join(
    PROJECT_ROOT, "config", "ppsn_dynamics_cases_full.csv"
)
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")

ALGO_SPECS = {
    "IVFSPEA2V2": {"label": "IVFSPEA2", "run_lo": 3001, "run_hi": 3030},
    "SPEA2": {"label": "SPEA2", "run_lo": 1, "run_hi": 30},
    "IVFNSGAII": {"label": "IVFNSGAII", "run_lo": 4001, "run_hi": 4030},
    "NSGAII": {"label": "NSGAII", "run_lo": 4001, "run_hi": 4030},
    "IVFNSGAIII": {"label": "IVFNSGAIII", "run_lo": 5001, "run_hi": 5030},
    "NSGAIII": {"label": "NSGAIII", "run_lo": 5001, "run_hi": 5030},
}


def to_1d_numeric(values) -> np.ndarray:
    if values is None:
        return np.array([], dtype=float)
    if isinstance(values, (int, float, np.integer, np.floating)):
        return np.array([float(values)], dtype=float)

    arr = np.asarray(values, dtype=object).reshape(-1)
    out = []
    for item in arr:
        if isinstance(item, (list, tuple, np.ndarray)):
            flat = np.asarray(item).reshape(-1)
            if flat.size == 0:
                continue
            out.append(float(flat[-1]))
        else:
            out.append(float(item))
    return np.asarray(out, dtype=float)


def extract_metrics(mat_path: str) -> dict:
    """Extract IGD and HV traces from a single PlatEMO .mat file.

    Returns dict with keys:
        'fe': np.array of function evaluation counts
        'IGD': np.array of IGD values (may be empty)
        'HV': np.array of HV values (may be empty)
    """
    payload = pymatreader.read_mat(mat_path)
    metric = payload.get("metric", {})
    result = payload.get("result")

    igd_values = to_1d_numeric(metric.get("IGD"))
    hv_values = to_1d_numeric(metric.get("HV"))

    fe_values = None
    try:
        if isinstance(result, list):
            first_col = [
                r[0] if isinstance(r, (list, tuple, np.ndarray)) else r for r in result
            ]
            fe_values = to_1d_numeric(first_col)
        elif result is not None:
            result_arr = np.asarray(result, dtype=object)
            if result_arr.ndim == 2:
                fe_values = to_1d_numeric(result_arr[:, 0])
    except Exception:
        fe_values = None

    n_igd = len(igd_values)
    n_hv = len(hv_values)
    n_metrics = max(n_igd, n_hv)

    if n_metrics == 0:
        return {"fe": np.array([], dtype=int), "IGD": np.array([]), "HV": np.array([])}

    if fe_values is None or len(fe_values) != n_metrics:
        fe_values = np.linspace(100000 / n_metrics, 100000, n_metrics)

    # Trim or pad metrics to match FE length
    if n_igd != n_metrics:
        igd_values = np.resize(igd_values, n_metrics) if n_igd > 0 else np.full(n_metrics, np.nan)
    if n_hv != n_metrics:
        hv_values = np.resize(hv_values, n_metrics) if n_hv > 0 else np.full(n_metrics, np.nan)

    return {
        "fe": fe_values.astype(int),
        "IGD": igd_values.astype(float),
        "HV": hv_values.astype(float),
    }


def extract_convergence(mat_path: str) -> list[tuple[int, float]]:
    """Backward-compatible wrapper: returns list of (FE, IGD) pairs."""
    m = extract_metrics(mat_path)
    if m["IGD"].size == 0:
        return []
    return list(zip(m["fe"], m["IGD"]))


def load_instances(csv_path: str) -> pd.DataFrame:
    instances = pd.read_csv(csv_path)
    rename_map = {"m": "M", "d": "D"}
    instances = instances.rename(columns=rename_map)
    required = {"problem", "M", "D", "role"}
    missing = required.difference(instances.columns)
    if missing:
        raise SystemExit(f"Instance manifest missing columns: {sorted(missing)}")
    instances = instances[instances["role"] == "synthetic"].copy()
    instances["M"] = instances["M"].astype(int)
    instances["D"] = instances["D"].astype(int)
    return instances[["problem", "M", "D"]].drop_duplicates().reset_index(drop=True)


def main() -> None:
    print("=== Building hosts_convergence.csv (IGD + HV) ===\n")
    instances = load_instances(INSTANCES_CSV)
    print(f"Synthetic instances to process: {len(instances)}")

    rows: list[dict] = []
    hv_count = 0
    igd_count = 0
    missing_files: list[str] = []
    for algo_dir, spec in ALGO_SPECS.items():
        algo_label = spec["label"]
        algo_path = os.path.join(DATA_ROOT, algo_dir)
        if not os.path.isdir(algo_path):
            print(f"  [WARN] Missing directory: {algo_path}")
            continue

        for _, inst in instances.iterrows():
            prob = inst["problem"]
            m_val = int(inst["M"])
            d_val = int(inst["D"])
            for run in range(spec["run_lo"], spec["run_hi"] + 1):
                pattern = os.path.join(algo_path, f"{algo_dir}_{prob}_M{m_val}_D{d_val}_{run}.mat")
                matches = glob.glob(pattern)
                if not matches:
                    missing_files.append(os.path.basename(pattern))
                    continue
                try:
                    m = extract_metrics(matches[0])
                    for i in range(len(m["fe"])):
                        row = {
                            "algo": algo_label,
                            "problem": prob,
                            "M": m_val,
                            "run": run,
                            "FE": int(m["fe"][i]),
                            "IGD": float(m["IGD"][i]) if not np.isnan(m["IGD"][i]) else None,
                            "HV": float(m["HV"][i]) if not np.isnan(m["HV"][i]) else None,
                        }
                        rows.append(row)
                        if m["IGD"][i] is not None and not np.isnan(m["IGD"][i]):
                            igd_count += 1
                        if m["HV"][i] is not None and not np.isnan(m["HV"][i]):
                            hv_count += 1
                except Exception as exc:
                    print(f"  [WARN] {matches[0]}: {exc}")

    if not rows:
        raise SystemExit(
            "No convergence rows found. Run the trace rerun scripts for the synthetic hosts suite first."
        )

    df = pd.DataFrame(rows).sort_values(["algo", "problem", "M", "run", "FE"])
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} rows to {OUT_CSV}")
    print(f"  Algos: {sorted(df['algo'].unique())}")
    print(f"  Problems: {sorted(df['problem'].unique())}")
    print(f"  IGD values: {igd_count}")
    print(f"  HV values:  {hv_count}")
    if missing_files:
        print(f"  [WARN] Missing expected files: {len(missing_files)}")
    if hv_count == 0:
        print("  [WARN] No HV data found. Ensure 'HV' is saved in PlatEMO metrics.")


if __name__ == "__main__":
    main()
