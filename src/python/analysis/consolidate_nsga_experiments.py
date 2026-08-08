#!/usr/bin/env python3
"""
Consolidate IVF/NSGA-II and IVF/NSGA-III experiment results into a single CSV.

Run ranges:
  NSGA-II track : IVFNSGAII (4001-4030) and NSGAII  (4001-4030)
  NSGA-III track: IVFNSGAIII (5001-5030) and NSGAIII (5001-5030)

Output: data/processed/nsga_experiments.csv
"""

import os
import sys
import re
import numpy as np
import pandas as pd
import pymatreader

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "src", "matlab", "lib", "PlatEMO", "Data")
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "nsga_experiments.csv")

GROUP_PREFIXES = ["WFG", "MaF", "DTLZ", "ZDT", "RWMOP"]

ALGO_RUN_RANGES = {
    "IVFNSGAII":  (4001, 4030),
    "NSGAII":     (4001, 4030),
    "IVFNSGAIII": (5001, 5030),
    "NSGAIII":    (5001, 5030),
}


def detect_group(name: str) -> str:
    for p in GROUP_PREFIXES:
        if name.startswith(p):
            return p
    return name[:3]


def parse_filename(filename: str) -> dict | None:
    """Parse ALGO_PROBLEM_M#_D#_RUN.mat → dict. Returns None on mismatch."""
    m = re.match(r"^(.+?)_(.+?)_(M\d+)_(D\d+)_(\d+)\.mat$", filename)
    if not m:
        return None
    algo, problem, m_param, d_param, run = m.groups()
    return {
        "algo": algo,
        "problem": problem,
        "group": detect_group(problem),
        "M": int(m_param[1:]),
        "D": int(d_param[1:]),
        "run": int(run),
    }


def extract_final_metrics(filepath: str) -> dict:
    """Return final IGD, HV, and runtime from a .mat file."""
    out = {"IGD": np.nan, "HV": np.nan, "runtime": np.nan}
    try:
        d = pymatreader.read_mat(filepath)
    except Exception as e:
        print(f"  [WARN] Cannot read {os.path.basename(filepath)}: {e}")
        return out
    met = d.get("metric", {})
    for key in ("IGD", "HV", "runtime"):
        val = met.get(key, np.nan)
        if isinstance(val, np.ndarray) and val.size > 0:
            out[key] = float(val.flat[-1])
        elif isinstance(val, (int, float)):
            out[key] = float(val)
    return out


def load_algo(algo: str, run_lo: int, run_hi: int) -> list[dict]:
    algo_dir = os.path.join(DATA_DIR, algo)
    if not os.path.isdir(algo_dir):
        print(f"  [WARN] Directory not found: {algo_dir}")
        return []

    mat_files = [f for f in os.listdir(algo_dir) if f.endswith(".mat")]
    rows = []
    skipped = 0
    for fname in sorted(mat_files):
        info = parse_filename(fname)
        if info is None:
            skipped += 1
            continue
        if not (run_lo <= info["run"] <= run_hi):
            continue
        metrics = extract_final_metrics(os.path.join(algo_dir, fname))
        rows.append({**info, **metrics})

    print(f"  {algo}: {len(rows)} rows loaded "
          f"(runs {run_lo}–{run_hi}, {skipped} files skipped)")
    return rows


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)

    print("=== Consolidating NSGA experiments ===\n")
    all_rows = []
    for algo, (lo, hi) in ALGO_RUN_RANGES.items():
        rows = load_algo(algo, lo, hi)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df = df.sort_values(["algo", "group", "problem", "M", "run"]).reset_index(drop=True)

    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df)} rows → {OUT_CSV}")

    print("\nRows per algorithm:")
    for algo, cnt in df.groupby("algo").size().items():
        print(f"  {algo}: {cnt}")

    print("\nMissing metrics:")
    for col in ("IGD", "HV"):
        n = df[col].isna().sum()
        if n:
            print(f"  {col}: {n} NaN")
        else:
            print(f"  {col}: OK")


if __name__ == "__main__":
    main()
