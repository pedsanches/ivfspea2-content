#!/usr/bin/env python3
"""
Consolidate IVFSPEA2 submission .mat files into the master CSV.

Reads .mat files from PlatEMO Data/IVFSPEA2/, extracts metrics (IGD, HV,
runtime, etc.), and merges them into data/processed/todas_metricas_consolidado.csv.

If IVFSPEA2 rows already exist in the CSV, they are replaced.

Usage:
    python src/python/analysis/consolidate_ivfspea2v2.py
"""

import os
import sys
import numpy as np
import pandas as pd
import pymatreader

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
MAT_DIR = os.path.join(
    PROJECT_ROOT, "src", "matlab", "lib", "PlatEMO", "Data", "IVFSPEA2"
)
CSV_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado.csv"
)

# Benchmark group detection
GROUP_PREFIXES = ["WFG", "MaF", "DTLZ", "ZDT", "UF", "RWMOP"]


def detect_group(problem_name: str) -> str:
    for prefix in GROUP_PREFIXES:
        if problem_name.startswith(prefix):
            return prefix
    return problem_name[:3]


def parse_filename(filename: str) -> dict | None:
    """Parse IVFSPEA2_PROBLEM_M#_D#_RUN.mat into components."""
    parts = filename.replace(".mat", "").split("_")
    if len(parts) < 5:
        print(f"  Skipping unrecognized format: {filename}")
        return None
    algo = parts[0]
    problem = parts[1]
    m_param = parts[2]  # e.g. M2
    d_param = parts[3]  # e.g. D12
    run = int(parts[4])
    return {
        "Algoritmo": algo,
        "Problema": problem,
        "Grupo": detect_group(problem),
        "M": m_param,
        "D": d_param,
        "Run": run,
        "arquivo_original": filename,
    }


def extract_metrics(filepath: str) -> dict:
    """Extract all metrics from a .mat file."""
    metrics = {}
    try:
        data = pymatreader.read_mat(filepath)
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return metrics

    if "metric" in data and isinstance(data["metric"], dict):
        for key, value in data["metric"].items():
            if isinstance(value, np.ndarray):
                if value.size == 1:
                    metrics[key] = float(value.item())
                elif len(value) > 0:
                    metrics[key] = float(value[-1])
                else:
                    metrics[key] = np.nan
            elif isinstance(value, (int, float)):
                metrics[key] = float(value)
    return metrics


def main():
    print("=== Consolidating IVFSPEA2 .mat files ===")

    if not os.path.isdir(MAT_DIR):
        print(f"ERROR: Directory not found: {MAT_DIR}")
        sys.exit(1)

    mat_files = sorted(f for f in os.listdir(MAT_DIR) if f.endswith(".mat"))
    print(f"Found {len(mat_files)} .mat files in {MAT_DIR}")

    if not mat_files:
        print("No files to process.")
        sys.exit(0)

    rows = []
    for i, filename in enumerate(mat_files):
        if (i + 1) % 500 == 0:
            print(f"  Processing {i + 1}/{len(mat_files)}...")

        info = parse_filename(filename)
        if info is None:
            continue

        metrics = extract_metrics(os.path.join(MAT_DIR, filename))
        info.update(metrics)
        rows.append(info)

    df_v2 = pd.DataFrame(rows)
    print(f"Extracted {len(df_v2)} rows from IVFSPEA2 .mat files")
    print(
        f"Metrics found: {[c for c in df_v2.columns if c not in ['Algoritmo', 'Problema', 'Grupo', 'M', 'D', 'Run', 'arquivo_original']]}"
    )

    # Load existing CSV
    if os.path.isfile(CSV_PATH):
        df_existing = pd.read_csv(CSV_PATH)
        print(f"Existing CSV: {len(df_existing)} rows")

        # Remove old IVFSPEA2 rows if any
        n_old = (df_existing["Algoritmo"] == "IVFSPEA2").sum()
        if n_old > 0:
            print(f"  Removing {n_old} existing IVFSPEA2 rows")
            df_existing = df_existing[df_existing["Algoritmo"] != "IVFSPEA2"]

        # Ensure column alignment
        for col in df_existing.columns:
            if col not in df_v2.columns:
                df_v2[col] = np.nan
        for col in df_v2.columns:
            if col not in df_existing.columns:
                df_existing[col] = np.nan

        df_merged = pd.concat([df_existing, df_v2], ignore_index=True)
    else:
        print(f"No existing CSV at {CSV_PATH}, creating new one")
        df_merged = df_v2

    df_merged = df_merged.sort_values(["Grupo", "Algoritmo", "Problema", "Run"])

    # Backup original
    if os.path.isfile(CSV_PATH):
        backup = CSV_PATH + ".bak"
        os.replace(CSV_PATH, backup)
        print(f"Backup saved to {backup}")

    df_merged.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(df_merged)} rows to {CSV_PATH}")

    # Summary
    algo_counts = df_merged.groupby("Algoritmo").size()
    print(f"\nRows per algorithm:")
    for algo, count in algo_counts.items():
        print(f"  {algo}: {count}")


if __name__ == "__main__":
    main()
