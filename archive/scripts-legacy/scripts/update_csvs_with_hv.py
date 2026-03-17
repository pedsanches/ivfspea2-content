#!/usr/bin/env python3
"""
Update existing experiment CSVs with HV values from the inventory.

Reads results/hv_inventory.csv (produced by compute_missing_hv.m)
and patches HV into:
  1. data/processed/todas_metricas_consolidado.csv
  2. results/ablation/ablation_filtered_runs.csv
  3. results/ablation_v2/phase1/phase1_raw_igd.csv  (adds HV + Run columns)
  4. results/ablation_v2/phase2/phase2_raw_igd.csv   (creates if phase2 data exists)

Usage:
  python scripts/update_csvs_with_hv.py
"""

import os
import re
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = "/home/pedro/desenvolvimento/ivfspea2"
INVENTORY_FILE = os.path.join(PROJECT_ROOT, "results", "hv_inventory.csv")


def load_inventory() -> pd.DataFrame:
    if not os.path.isfile(INVENTORY_FILE):
        print(f"ERROR: Inventory file not found: {INVENTORY_FILE}")
        print("Run compute_missing_hv.m in MATLAB first.")
        sys.exit(1)

    df = pd.read_csv(INVENTORY_FILE)
    print(f"Loaded inventory: {len(df)} rows, {df['HasHV'].sum()} with HV")
    return df


def update_consolidado(inv: pd.DataFrame) -> None:
    """Patch HV in todas_metricas_consolidado.csv by matching arquivo_original."""
    csv_path = os.path.join(
        PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado.csv"
    )
    if not os.path.isfile(csv_path):
        print(f"  [SKIP] Not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    n_before = df["HV"].notna().sum()

    inv_hv = inv[inv["HasHV"] == 1][["Path", "HV"]].copy()
    inv_hv["basename"] = inv_hv["Path"].apply(os.path.basename)
    hv_map = dict(zip(inv_hv["basename"], inv_hv["HV"]))

    filled = 0
    for i, row in df.iterrows():
        fname = row.get("arquivo_original", "")
        if pd.isna(fname) or fname == "":
            continue
        if pd.isna(row["HV"]) or row["HV"] == "":
            if fname in hv_map:
                df.at[i, "HV"] = hv_map[fname]
                filled += 1

    n_after = df["HV"].notna().sum()

    bak_path = csv_path + ".bak"
    if not os.path.exists(bak_path):
        os.rename(csv_path, bak_path)
    else:
        os.remove(csv_path)
    df.to_csv(csv_path, index=False)
    print(
        f"  [CONSOLIDADO] {filled} rows filled (was {n_before}, now {n_after} with HV)"
    )


def update_ablation_v1(inv: pd.DataFrame) -> None:
    """Add HV column to ablation_filtered_runs.csv by matching SourcePath or basename."""
    csv_path = os.path.join(
        PROJECT_ROOT, "results", "ablation", "ablation_filtered_runs.csv"
    )
    if not os.path.isfile(csv_path):
        print(f"  [SKIP] Not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    inv_hv = inv[inv["HasHV"] == 1][["Path", "HV"]].copy()
    hv_by_path = dict(zip(inv_hv["Path"], inv_hv["HV"]))
    inv_hv["basename"] = inv_hv["Path"].apply(os.path.basename)
    hv_by_basename = dict(zip(inv_hv["basename"], inv_hv["HV"]))

    if "HV" not in df.columns:
        df["HV"] = np.nan

    filled = 0
    for i, row in df.iterrows():
        sp = row.get("SourcePath", "")
        if pd.isna(sp) or sp == "":
            continue
        if pd.isna(row["HV"]):
            if sp in hv_by_path:
                df.at[i, "HV"] = hv_by_path[sp]
                filled += 1
            else:
                bn = os.path.basename(sp)
                if bn in hv_by_basename:
                    df.at[i, "HV"] = hv_by_basename[bn]
                    filled += 1

    bak_path = csv_path + ".bak"
    if not os.path.exists(bak_path):
        os.rename(csv_path, bak_path)
    else:
        os.remove(csv_path)
    df.to_csv(csv_path, index=False)
    print(f"  [ABLATION_V1] {filled} rows filled with HV (total rows: {len(df)})")


def update_ablation_v2_phase(inv: pd.DataFrame, phase: str) -> None:
    """Add HV + Run columns to ablation_v2 phase CSV.

    Matches by reconstructing the file iteration order used by
    analyze_ablation_v2_phase1.py (sorted folders → sorted .mat files),
    then looking up HV by .mat basename from the inventory.
    """
    csv_path = os.path.join(
        PROJECT_ROOT, "results", "ablation_v2", phase, f"{phase}_raw_igd.csv"
    )
    if not os.path.isfile(csv_path):
        print(f"  [SKIP] Not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    inv_hv = inv[inv["HasHV"] == 1][["Path", "HV"]].copy()
    inv_hv["basename"] = inv_hv["Path"].apply(os.path.basename)
    hv_by_basename = dict(zip(inv_hv["basename"], inv_hv["HV"]))

    phase_dir = os.path.join(PROJECT_ROOT, "data", "ablation_v2", phase)
    if not os.path.isdir(phase_dir):
        print(f"  [{phase.upper()}] Data directory not found: {phase_dir}")
        return

    file_order = []
    for folder_name in sorted(os.listdir(phase_dir)):
        folder_path = os.path.join(phase_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
        mat_files = sorted(f for f in os.listdir(folder_path) if f.endswith(".mat"))
        for mf in mat_files:
            file_order.append(mf)

    if len(file_order) != len(df):
        print(
            f"  [{phase.upper()}] WARN: file count ({len(file_order)}) != CSV rows ({len(df)})"
        )

    if "HV" not in df.columns:
        df["HV"] = np.nan
    if "Run" not in df.columns:
        df["Run"] = np.nan

    filled = 0
    run_re = re.compile(r"_(\d+)\.mat$")
    for i in range(min(len(df), len(file_order))):
        mf = file_order[i]
        if mf in hv_by_basename:
            df.at[i, "HV"] = hv_by_basename[mf]
            filled += 1
        m = run_re.search(mf)
        if m:
            df.at[i, "Run"] = int(m.group(1))

    bak_path = csv_path + ".bak"
    if not os.path.exists(bak_path):
        os.rename(csv_path, bak_path)
    else:
        os.remove(csv_path)
    df.to_csv(csv_path, index=False)
    print(f"  [{phase.upper()}] {filled} rows filled with HV (total rows: {len(df)})")


def print_summary(inv: pd.DataFrame) -> None:
    print("\n=== Final inventory summary ===")
    for src in sorted(inv["Source"].unique()):
        mask = inv["Source"] == src
        total = mask.sum()
        with_hv = (inv.loc[mask, "HasHV"] == 1).sum()
        print(f"  {src:35s}  total={total:6d}  HV={with_hv:6d}  missing={total - with_hv:6d}")

    total = len(inv)
    with_hv = (inv["HasHV"] == 1).sum()
    print(f"  {'TOTAL':35s}  total={total:6d}  HV={with_hv:6d}  missing={total - with_hv:6d}")


def main():
    print("=" * 60)
    print("Update CSVs with HV from inventory")
    print("=" * 60)

    inv = load_inventory()

    print("\nUpdating CSVs:")
    update_consolidado(inv)
    update_ablation_v1(inv)
    update_ablation_v2_phase(inv, "phase1")
    update_ablation_v2_phase(inv, "phase2")

    print_summary(inv)
    print("\nDone.")


if __name__ == "__main__":
    main()
