#!/usr/bin/env python3
"""
Verify integrity of IVFSPEA2V2 tuning outputs.

Checks per phase (A/B/C):
  1) Expected case folders exist from case manifest
  2) Run IDs in each folder match expected run range exactly
  3) Output filenames match expected problem prefix
  4) Metric payload contains both IGD and HV
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    import pymatreader
except Exception:  # pragma: no cover
    pymatreader = None


RUN_RE = re.compile(r"_(\d+)\.mat$")


def parse_run_id(filename: str) -> int | None:
    match = RUN_RE.search(filename)
    if not match:
        return None
    return int(match.group(1))


def metric_has_igd_hv(mat_path: Path) -> bool:
    if pymatreader is None:
        raise RuntimeError("pymatreader is required to validate metric payloads")

    data = pymatreader.read_mat(str(mat_path))
    metric = data.get("metric")
    if metric is None:
        return False

    if isinstance(metric, dict):
        return "IGD" in metric and "HV" in metric

    # Fallback for uncommon MATLAB struct representations
    try:
        keys = metric.dtype.names  # type: ignore[attr-defined]
    except Exception:
        keys = None
    if keys is None:
        return False
    return "IGD" in keys and "HV" in keys


def load_phase_manifests(
    results_root: Path, phase: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cfg_path = results_root / f"manifest_phase{phase}_configs.csv"
    prob_path = results_root / f"manifest_phase{phase}_problems.csv"
    case_path = results_root / f"manifest_phase{phase}_cases.csv"

    missing = [str(p) for p in (cfg_path, prob_path, case_path) if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing manifests for phase {phase}: {missing}")

    cfg_df = pd.read_csv(cfg_path)
    prob_df = pd.read_csv(prob_path)
    case_df = pd.read_csv(case_path)
    return cfg_df, prob_df, case_df


def verify_phase(
    project_root: Path,
    results_root: Path,
    phase: str,
    full_metric_scan: bool,
) -> tuple[pd.DataFrame, bool]:
    _, prob_df, case_df = load_phase_manifests(results_root, phase)
    prob_df = prob_df.set_index("ProblemTag")

    phase_data_root = project_root / "data" / "tuning_ivfspea2v2" / f"phase{phase}"
    rows: list[dict] = []

    for rec in case_df.itertuples(index=False):
        config_id = rec.ConfigID
        problem_tag = rec.ProblemTag
        run_start = int(rec.RunStart)
        run_end = int(rec.RunEnd)
        expected_runs = set(range(run_start, run_end + 1))

        folder = phase_data_root / f"IVFSPEA2V2_{config_id}_{problem_tag}"
        folder_exists = folder.is_dir()

        found_runs: set[int] = set()
        prefix_mismatch = 0
        metric_checked = 0
        metric_missing = 0

        if folder_exists:
            if problem_tag not in prob_df.index:
                raise KeyError(
                    f"Problem tag {problem_tag} not present in problem manifest"
                )

            prob_name = str(prob_df.loc[problem_tag, "ProblemName"])
            m_val = int(prob_df.loc[problem_tag, "M"])
            expected_prefix = f"IVFSPEA2V2_{prob_name}_M{m_val}_"

            files = sorted(folder.glob("*.mat"))
            for fpath in files:
                if not fpath.name.startswith(expected_prefix):
                    prefix_mismatch += 1
                    continue

                run_id = parse_run_id(fpath.name)
                if run_id is None:
                    prefix_mismatch += 1
                    continue

                found_runs.add(run_id)

            files_for_metric = sorted(
                fpath
                for fpath in folder.glob("*.mat")
                if fpath.name.startswith(expected_prefix)
            )
            if not full_metric_scan and files_for_metric:
                files_for_metric = [files_for_metric[0]]

            for fpath in files_for_metric:
                metric_checked += 1
                try:
                    ok = metric_has_igd_hv(fpath)
                except Exception:
                    ok = False
                if not ok:
                    metric_missing += 1

        missing_runs = sorted(expected_runs - found_runs)
        extra_runs = sorted(found_runs - expected_runs)

        status = "OK"
        if not folder_exists:
            status = "MISSING_FOLDER"
        elif missing_runs or extra_runs:
            status = "RUNSET_MISMATCH"
        elif prefix_mismatch > 0:
            status = "PREFIX_MISMATCH"
        elif metric_missing > 0:
            status = "METRIC_MISSING"

        rows.append(
            {
                "Phase": phase,
                "ConfigID": config_id,
                "ProblemTag": problem_tag,
                "Folder": str(folder),
                "FolderExists": folder_exists,
                "ExpectedRuns": len(expected_runs),
                "FoundRuns": len(found_runs),
                "MissingRuns": len(missing_runs),
                "ExtraRuns": len(extra_runs),
                "PrefixMismatch": prefix_mismatch,
                "MetricChecked": metric_checked,
                "MetricMissing": metric_missing,
                "Status": status,
            }
        )

    df = pd.DataFrame(rows)
    ok = bool((df["Status"] == "OK").all()) if not df.empty else False
    return df, ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify IVFSPEA2V2 tuning data integrity"
    )
    parser.add_argument(
        "--project-root",
        default="/home/pedro/desenvolvimento/ivfspea2",
        help="Project root path",
    )
    parser.add_argument(
        "--phase",
        default="ALL",
        choices=["A", "B", "C", "ALL"],
        help="Phase to verify",
    )
    parser.add_argument(
        "--full-metric-scan",
        action="store_true",
        help="Validate IGD/HV in all .mat files (default checks one sample per folder)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root)
    results_root = project_root / "results" / "tuning_ivfspea2v2"
    results_root.mkdir(parents=True, exist_ok=True)

    phases = ["A", "B", "C"] if args.phase == "ALL" else [args.phase]

    all_reports: list[pd.DataFrame] = []
    global_ok = True

    print("=== Verify IVFSPEA2V2 Tuning Integrity ===")
    print(f"Project root: {project_root}")
    print(f"Phases: {', '.join(phases)}")
    print(f"Full metric scan: {args.full_metric_scan}")

    for phase in phases:
        try:
            report_df, phase_ok = verify_phase(
                project_root=project_root,
                results_root=results_root,
                phase=phase,
                full_metric_scan=args.full_metric_scan,
            )
        except Exception as exc:
            print(f"[FAIL] Phase {phase}: {exc}")
            global_ok = False
            continue

        all_reports.append(report_df)
        status_counts = report_df["Status"].value_counts().to_dict()
        print(f"[Phase {phase}] cases={len(report_df)} status={status_counts}")

        if not phase_ok:
            global_ok = False
            bad = report_df[report_df["Status"] != "OK"]
            print(f"  -> {len(bad)} problematic case(s)")
            for row in bad.head(15).itertuples(index=False):
                print(
                    f"     - {row.ConfigID}/{row.ProblemTag}: {row.Status} "
                    f"(missing={row.MissingRuns}, extra={row.ExtraRuns}, "
                    f"prefix={row.PrefixMismatch}, metric_missing={row.MetricMissing})"
                )

    if not all_reports:
        print("No report generated.")
        return 2

    final_df = pd.concat(all_reports, ignore_index=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = results_root / f"integrity_tuning_report_{ts}.csv"
    final_df.to_csv(out_csv, index=False)
    print(f"Report: {out_csv}")

    if global_ok:
        print("Integrity PASS: all checked cases are complete and metric-safe.")
        return 0

    print("Integrity FAIL: found incomplete or inconsistent cases.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
