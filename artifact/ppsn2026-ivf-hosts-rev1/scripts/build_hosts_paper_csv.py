#!/usr/bin/env python3
"""
Build the unified dataset for the hosts-comparison paper.

Sources:
  - data/processed/todas_metricas_consolidado.csv
      IVFSPEA2   runs 3001-3030  → IVF/SPEA2 v2  (30 runs, subsampled from 60)
      SPEA2      runs    1-30    → SPEA2 baseline (30 runs, subsampled from 60)

  - data/processed/nsga_experiments.csv
      IVFNSGAII  runs 4001-4030  → IVF/NSGA-II   (30 runs)
      NSGAII     runs 4001-4030  → NSGA-II        (30 runs)
      IVFNSGAIII runs 5001-5030  → IVF/NSGA-III  (30 runs)
      NSGAIII    runs 5001-5030  → NSGA-III       (30 runs)

Output:
  data/processed/hosts_paper.csv

Schema (unified):
  algo, problem, group, M (int), D (int), run (int), IGD (float), HV (float)

Notes:
  - This paper pipeline excludes RWMOP9 by design and keeps only synthetic
    benchmark instances.
  - 30-run subsampling uses the first 30 run IDs in each set to ensure
    reproducibility (not random sampling).
"""

import os
import sys
import numpy as np
import pandas as pd

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
MAIN_CSV     = os.path.join(PROJECT_ROOT, "data", "processed",
                            "todas_metricas_consolidado.csv")
NSGA_CSV     = os.path.join(PROJECT_ROOT, "data", "processed",
                            "nsga_experiments.csv")
OUT_CSV      = os.path.join(PROJECT_ROOT, "data", "processed",
                            "hosts_paper.csv")
GROUP_PREFIXES = ["WFG", "MaF", "DTLZ", "ZDT"]


def detect_group(name: str) -> str:
    for p in GROUP_PREFIXES:
        if name.startswith(p):
            return p
    return name[:3]


def parse_m(val) -> int:
    """Convert 'M2' or 2 → 2."""
    if isinstance(val, int):
        return val
    return int(str(val).lstrip("M"))


def parse_d(val) -> int:
    """Convert 'D30' or 30 → 30."""
    if isinstance(val, int):
        return val
    return int(str(val).lstrip("D"))


# ─── Load SPEA2 track from main CSV ──────────────────────────────────────────

def load_spea2_track(main_csv: str) -> pd.DataFrame:
    df = pd.read_csv(main_csv)

    rows = []

    # IVF/SPEA2 v2 — runs 3001-3030
    ivf = df[(df["Algoritmo"] == "IVFSPEA2") &
             (df["Run"] >= 3001) & (df["Run"] <= 3030)].copy()
    print(f"  IVFSPEA2 v2 (3001-3030): {len(ivf)} rows, "
          f"{ivf['Problema'].nunique()} problems")
    for _, r in ivf.iterrows():
        rows.append({
            "algo":    "IVFSPEA2",
            "problem": r["Problema"],
            "group":   detect_group(r["Problema"]),
            "M":       parse_m(r["M"]),
            "D":       parse_d(r["D"]),
            "run":     int(r["Run"]),
            "IGD":     float(r["IGD"]) if pd.notna(r["IGD"]) else np.nan,
            "HV":      float(r["HV"])  if pd.notna(r["HV"])  else np.nan,
        })

    # SPEA2 baseline — runs 1-30
    spea2 = df[(df["Algoritmo"] == "SPEA2") &
               (df["Run"] >= 1) & (df["Run"] <= 30)].copy()
    print(f"  SPEA2 baseline (1-30): {len(spea2)} rows, "
          f"{spea2['Problema'].nunique()} problems")
    for _, r in spea2.iterrows():
        rows.append({
            "algo":    "SPEA2",
            "problem": r["Problema"],
            "group":   detect_group(r["Problema"]),
            "M":       parse_m(r["M"]),
            "D":       parse_d(r["D"]),
            "run":     int(r["Run"]),
            "IGD":     float(r["IGD"]) if pd.notna(r["IGD"]) else np.nan,
            "HV":      float(r["HV"])  if pd.notna(r["HV"])  else np.nan,
        })

    return pd.DataFrame(rows)


# ─── Load NSGA tracks ─────────────────────────────────────────────────────────

def load_nsga_track(nsga_csv: str) -> pd.DataFrame:
    df = pd.read_csv(nsga_csv)
    # Already 30 runs, correct schema
    keep = ["algo", "problem", "group", "M", "D", "run", "IGD", "HV"]
    return df[keep].copy()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== Building hosts_paper.csv ===\n")

    if not os.path.isfile(MAIN_CSV):
        print(f"ERROR: {MAIN_CSV} not found."); sys.exit(1)
    if not os.path.isfile(NSGA_CSV):
        print(f"ERROR: {NSGA_CSV} not found."); sys.exit(1)

    print("Loading SPEA2 track...")
    df_spea2 = load_spea2_track(MAIN_CSV)

    print("\nLoading NSGA tracks...")
    df_nsga = load_nsga_track(NSGA_CSV)
    for algo in df_nsga["algo"].unique():
        n = (df_nsga["algo"] == algo).sum()
        p = df_nsga[df_nsga["algo"] == algo]["problem"].nunique()
        print(f"  {algo}: {n} rows, {p} problems")

    df = pd.concat([df_spea2, df_nsga], ignore_index=True)
    df = df[df["problem"] != "RWMOP9"].copy()
    df = df.sort_values(["algo", "group", "problem", "M", "run"]).reset_index(drop=True)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    print(f"\nSaved {len(df)} rows → {OUT_CSV}")
    print("\nRows per algorithm:")
    for algo, cnt in df.groupby("algo").size().items():
        p = df[df["algo"] == algo]["problem"].nunique()
        print(f"  {algo}: {cnt} rows ({p} problems, "
              f"{cnt // p if p else '?'} runs/problem)")

    # Coverage check
    print("\nProblem coverage per algo:")
    problems_by_algo = df.groupby("algo")["problem"].apply(set)
    all_problems = set.union(*problems_by_algo.values)
    for algo, probs in problems_by_algo.items():
        missing = all_problems - probs
        if missing:
            print(f"  {algo} missing: {sorted(missing)}")
        else:
            print(f"  {algo}: complete ({len(probs)} problems)")

    print("\nNaN check:")
    for col in ("IGD", "HV"):
        n = df[col].isna().sum()
        print(f"  {col}: {n} NaN" if n else f"  {col}: OK")


if __name__ == "__main__":
    main()
