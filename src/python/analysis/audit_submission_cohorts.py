#!/usr/bin/env python3
"""
Audit run-ID cohort completeness for consolidated synthetic analyses.

This script inspects `todas_metricas_consolidado_with_modern.csv` and writes
an auditable report that highlights mixed or incomplete run cohorts per
algorithm/problem/M group.
"""

from __future__ import annotations

import os
import sys

import pandas as pd

try:
    from cohort_filter import build_group_coverage
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import build_group_coverage


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_DIR = os.path.join(PROJECT_ROOT, "results", "tables")


def main() -> int:
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: file not found: {DATA_PATH}")
        return 1

    df = pd.read_csv(DATA_PATH)
    coverage = build_group_coverage(df)

    synthetic = coverage[coverage["expected_window"] != "engineering_external"].copy()
    anomalies = synthetic[synthetic["status"] != "ok"].copy()

    summary = (
        synthetic.groupby(["Algoritmo", "status"], as_index=False)
        .size()
        .rename(columns={"size": "n_groups"})
        .sort_values(["Algoritmo", "status"])
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    audit_csv = os.path.join(OUT_DIR, "run_cohort_audit.csv")
    anomalies_csv = os.path.join(OUT_DIR, "run_cohort_anomalies.csv")
    summary_csv = os.path.join(OUT_DIR, "run_cohort_summary.csv")

    coverage.to_csv(audit_csv, index=False)
    anomalies.to_csv(anomalies_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    print(f"Loaded rows: {len(df)}")
    print(f"Coverage groups: {len(coverage)}")
    print(f"Synthetic groups: {len(synthetic)}")
    print(f"Synthetic anomalies: {len(anomalies)}")

    if len(anomalies) > 0:
        print("\nTop anomalies:")
        print(anomalies.head(20).to_string(index=False))

    print(f"\nSaved: {audit_csv}")
    print(f"Saved: {anomalies_csv}")
    print(f"Saved: {summary_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
