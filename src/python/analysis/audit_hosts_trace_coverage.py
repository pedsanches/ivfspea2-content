#!/usr/bin/env python3
"""Audit synthetic hosts trace coverage for the A7 all-suite gate."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pymatreader


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "src" / "matlab" / "lib" / "PlatEMO" / "Data"
INSTANCES_CSV = PROJECT_ROOT / "config" / "ppsn_dynamics_cases_full.csv"
CONV_CSV = PROJECT_ROOT / "data" / "processed" / "hosts_convergence.csv"

ALGO_SPECS = {
    "IVFSPEA2V2": {"label": "IVFSPEA2", "run_lo": 3001, "run_hi": 3030},
    "SPEA2": {"label": "SPEA2", "run_lo": 1, "run_hi": 30},
    "IVFNSGAII": {"label": "IVFNSGAII", "run_lo": 4001, "run_hi": 4030},
    "NSGAII": {"label": "NSGAII", "run_lo": 4001, "run_hi": 4030},
    "IVFNSGAIII": {"label": "IVFNSGAIII", "run_lo": 5001, "run_hi": 5030},
    "NSGAIII": {"label": "NSGAIII", "run_lo": 5001, "run_hi": 5030},
}


def load_instances() -> pd.DataFrame:
    df = pd.read_csv(INSTANCES_CSV)
    df = df.rename(columns={"m": "M", "d": "D"})
    df = df[df["role"] == "synthetic"].copy()
    df["M"] = df["M"].astype(int)
    df["D"] = df["D"].astype(int)
    return df[["problem", "M", "D"]].drop_duplicates().reset_index(drop=True)


def expected_path(algo: str, problem: str, m_val: int, d_val: int, run: int) -> Path:
    return DATA_ROOT / algo / f"{algo}_{problem}_M{m_val}_D{d_val}_{run}.mat"


def metric_len(value) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return 1
    try:
        return len(value)
    except TypeError:
        return 1


def inspect_trace(mat_path: Path) -> tuple[bool, str]:
    payload = pymatreader.read_mat(str(mat_path))
    metric = payload.get("metric", {})
    result = payload.get("result")

    igd_len = metric_len(metric.get("IGD")) if isinstance(metric, dict) else 0
    hv_len = metric_len(metric.get("HV")) if isinstance(metric, dict) else 0

    if result is None:
        result_len = 0
    else:
        try:
            result_len = len(result)
        except TypeError:
            result_len = 1

    ok = igd_len > 1 and hv_len > 1 and result_len > 1
    detail = f"IGD={igd_len} HV={hv_len} result={result_len}"
    return ok, detail


def audit_files(instances: pd.DataFrame) -> tuple[list[str], list[str], list[dict]]:
    findings: list[str] = []
    trace_findings: list[str] = []
    summary_rows: list[dict] = []

    expected_instances = len(instances)
    expected_runs = 30
    expected_files = expected_instances * expected_runs

    for algo, spec in ALGO_SPECS.items():
        present = 0
        missing = 0
        problems_with_full_coverage = 0
        sample_checked = False

        for _, inst in instances.iterrows():
            prob = inst["problem"]
            m_val = int(inst["M"])
            d_val = int(inst["D"])
            present_for_problem = 0

            for run in range(spec["run_lo"], spec["run_hi"] + 1):
                mat_path = expected_path(algo, prob, m_val, d_val, run)
                if mat_path.is_file():
                    present += 1
                    present_for_problem += 1
                    if not sample_checked:
                        ok, detail = inspect_trace(mat_path)
                        status = "OK" if ok else "BAD"
                        trace_findings.append(f"{algo} sample {mat_path.name}: {status} ({detail})")
                        sample_checked = True
                else:
                    missing += 1

            if present_for_problem == expected_runs:
                problems_with_full_coverage += 1

        summary_rows.append(
            {
                "algo": spec["label"],
                "expected_files": expected_files,
                "present_files": present,
                "missing_files": missing,
                "full_problems": problems_with_full_coverage,
                "expected_problems": expected_instances,
            }
        )

        if missing:
            findings.append(
                f"{algo}: missing {missing}/{expected_files} files; complete problems {problems_with_full_coverage}/{expected_instances}"
            )

    return findings, trace_findings, summary_rows


def audit_csv(instances: pd.DataFrame) -> list[str]:
    findings: list[str] = []
    if not CONV_CSV.is_file():
        findings.append("hosts_convergence.csv: missing")
        return findings

    df = pd.read_csv(CONV_CSV)
    expected_algos = sorted(spec["label"] for spec in ALGO_SPECS.values())
    present_algos = sorted(df["algo"].dropna().unique().tolist())
    if present_algos != expected_algos:
        findings.append(f"hosts_convergence.csv: algo set mismatch {present_algos}")

    if "RWMOP9" in set(df["problem"].dropna().unique()):
        findings.append("hosts_convergence.csv: contains RWMOP9")

    expected_instances = len(instances)
    observed_instances = df[["problem", "M"]].drop_duplicates().shape[0]
    expected_problem_m = instances[["problem", "M"]].drop_duplicates().shape[0]
    if observed_instances != expected_problem_m:
        findings.append("hosts_convergence.csv: synthetic instance count mismatch")

    run_counts = df.groupby(["algo", "problem", "M"])["run"].nunique()
    if run_counts.empty or int(run_counts.min()) != 30:
        findings.append("hosts_convergence.csv: some algo/problem cohorts have fewer than 30 runs")

    return findings


def main() -> None:
    instances = load_instances()
    file_findings, trace_findings, summary_rows = audit_files(instances)
    csv_findings = audit_csv(instances)

    print("=== A7 Trace Coverage Audit ===")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Synthetic instances: {len(instances)}")
    print()
    print("Per-algorithm coverage:")
    for row in summary_rows:
        print(
            f"  {row['algo']}: {row['present_files']}/{row['expected_files']} files, "
            f"complete problems {row['full_problems']}/{row['expected_problems']}"
        )

    print()
    print("Sample trace integrity:")
    for line in trace_findings:
        print(f"  {line}")
    if not trace_findings:
        print("  No sample traces inspected")

    all_findings = file_findings + csv_findings
    print()
    if all_findings:
        print("Findings:")
        for line in all_findings:
            print(f"  - {line}")
        print()
        print("A7 status: NOT READY")
    else:
        print("Findings:")
        print("  None")
        print()
        print("A7 status: READY")


if __name__ == "__main__":
    main()
