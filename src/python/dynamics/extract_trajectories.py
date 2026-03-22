"""Extract per-generation trajectories from PPSN dynamics .mat files.

Reads IVF-SPEA2 and SPEA2 trace files, pairs them by seed, and produces
a single long-format CSV with one row per (case, algorithm, run, generation).

Output: data/processed/ppsn_trajectories.csv
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pymatreader import read_mat


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics"
OUT_DIR = PROJECT_ROOT / "data" / "processed"
MANIFEST = PROJECT_ROOT / "config" / "ppsn_dynamics_cases.csv"

METRICS = [
    "generation", "fe", "igd", "hv", "spread", "spacing",
    "mean_fitness", "nd_fraction", "ivf_activated", "n_ivf_cycles",
    "ivf_fe", "turnover",
]


def extract_generations(mat_path: str) -> list[dict]:
    """Extract per-generation snapshots from a trace .mat file."""
    data = read_mat(mat_path)
    gens = data["trace_generations"]

    # pymatreader returns list of dicts or nested structure
    if isinstance(gens, dict):
        # Single generation edge case
        gens = [gens]
    elif isinstance(gens, np.ndarray):
        gens = list(gens)

    rows = []
    for g in gens:
        if isinstance(g, dict):
            row = {k: g.get(k, np.nan) for k in METRICS}
        else:
            row = {k: np.nan for k in METRICS}
        rows.append(row)
    return rows


def extract_meta(mat_path: str) -> dict:
    """Extract metadata from a trace .mat file."""
    data = read_mat(mat_path)
    meta = data.get("meta", {})
    return {
        "case_id": meta.get("case_id", ""),
        "problem": meta.get("problem", ""),
        "m": int(meta.get("m", 0)),
        "d": int(meta.get("d", 0)),
        "run_id": int(meta.get("run_id", 0)),
        "seed": int(meta.get("seed", 0)),
        "algorithm": meta.get("algorithm", ""),
        "role": meta.get("role", ""),
    }


def process_directory(algo_dir: Path, algorithm: str) -> pd.DataFrame:
    """Process all .mat files in an algorithm directory tree."""
    all_rows = []
    mat_files = sorted(algo_dir.rglob("*.mat"))

    for mat_path in mat_files:
        try:
            meta = extract_meta(str(mat_path))
            gens = extract_generations(str(mat_path))

            for g in gens:
                row = {**meta, **g}
                row["algorithm"] = algorithm
                all_rows.append(row)
        except Exception as e:
            print(f"  [WARN] Failed to read {mat_path.name}: {e}")
            continue

    return pd.DataFrame(all_rows)


def main():
    print("=" * 70)
    print("PPSN 2026 -- Trajectory Extraction")
    print("=" * 70)

    if not RAW_DIR.exists():
        print(f"ERROR: Raw data directory not found: {RAW_DIR}")
        sys.exit(1)

    # Load manifest for role annotations
    manifest = pd.read_csv(MANIFEST)
    print(f"Manifest: {len(manifest)} cases")

    # Process IVF and SPEA2 directories
    ivf_dir = RAW_DIR / "ivf"
    spea2_dir = RAW_DIR / "spea2"

    frames = []
    for algo_dir, algo_name in [(ivf_dir, "IVF-SPEA2"), (spea2_dir, "SPEA2")]:
        if not algo_dir.exists():
            print(f"  [SKIP] {algo_dir} not found")
            continue
        print(f"\nProcessing {algo_name}...")
        df = process_directory(algo_dir, algo_name)
        print(f"  {len(df)} rows from {df['run_id'].nunique()} runs, "
              f"{df['case_id'].nunique()} cases")
        frames.append(df)

    if not frames:
        print("ERROR: No data extracted")
        sys.exit(1)

    df_all = pd.concat(frames, ignore_index=True)

    # Ensure correct types
    for col in ["generation", "fe", "n_ivf_cycles", "ivf_fe", "m", "d", "run_id", "seed"]:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce").astype("Int64")

    # Coerce numeric columns that may have '[]' from MATLAB empty arrays
    for col in ["igd", "hv", "spread", "spacing", "mean_fitness", "nd_fraction",
                "turnover", "ivf_fe"]:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce")

    df_all["ivf_activated"] = df_all["ivf_activated"].map(
        lambda x: bool(x) if not isinstance(x, str) else x not in ("0", "False", "false", "[]", "")
    )

    # Sort for reproducibility
    df_all = df_all.sort_values(
        ["case_id", "algorithm", "run_id", "generation"]
    ).reset_index(drop=True)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"Total rows: {len(df_all)}")
    print(f"Cases: {df_all['case_id'].nunique()}")
    print(f"Algorithms: {df_all['algorithm'].unique().tolist()}")
    print(f"Runs per case (IVF): {df_all[df_all['algorithm'] == 'IVF-SPEA2'].groupby('case_id')['run_id'].nunique().to_dict()}")

    # Per-case summary
    print(f"\n{'Case':<30s} {'Role':<20s} {'IVF runs':>10s} {'SPEA2 runs':>10s} {'Gens':>6s}")
    print("-" * 80)
    for _, row in manifest.iterrows():
        cid = row["case_id"]
        sub = df_all[df_all["case_id"] == cid]
        n_ivf = sub[sub["algorithm"] == "IVF-SPEA2"]["run_id"].nunique()
        n_spea2 = sub[sub["algorithm"] == "SPEA2"]["run_id"].nunique()
        n_gens = sub["generation"].nunique() if len(sub) > 0 else 0
        print(f"  {cid:<28s} {row['role']:<20s} {n_ivf:>10d} {n_spea2:>10d} {n_gens:>6d}")

    # Save
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "ppsn_trajectories.csv"
    df_all.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    print(f"Size: {out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
