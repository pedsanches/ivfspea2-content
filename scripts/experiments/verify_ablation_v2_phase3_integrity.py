#!/usr/bin/env python3
"""
Verify integrity of ablation v2 phase3 outputs.

Expected layout:
  data/ablation_v2/phase3/IVFSPEA2_P2_C05_<PROBLEM>_M<M>/*.mat

Validation rules:
  - all 51 expected folders exist
  - each folder has exactly 60 expected run IDs
  - no out-of-range run IDs
  - optional: each MAT has both IGD and HV
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROBLEMS = [
    ("ZDT1", 2, 30),
    ("ZDT2", 2, 30),
    ("ZDT3", 2, 30),
    ("ZDT4", 2, 10),
    ("ZDT6", 2, 10),
    ("DTLZ1", 2, 6),
    ("DTLZ2", 2, 11),
    ("DTLZ3", 2, 11),
    ("DTLZ4", 2, 11),
    ("DTLZ5", 2, 11),
    ("DTLZ6", 2, 11),
    ("DTLZ7", 2, 21),
    ("WFG1", 2, 11),
    ("WFG2", 2, 11),
    ("WFG3", 2, 11),
    ("WFG4", 2, 11),
    ("WFG5", 2, 11),
    ("WFG6", 2, 11),
    ("WFG7", 2, 11),
    ("WFG8", 2, 11),
    ("WFG9", 2, 11),
    ("MaF1", 2, 11),
    ("MaF2", 2, 11),
    ("MaF3", 2, 11),
    ("MaF4", 2, 11),
    ("MaF5", 2, 11),
    ("MaF6", 2, 11),
    ("MaF7", 2, 21),
    ("DTLZ1", 3, 7),
    ("DTLZ2", 3, 12),
    ("DTLZ3", 3, 12),
    ("DTLZ4", 3, 12),
    ("DTLZ5", 3, 12),
    ("DTLZ6", 3, 12),
    ("DTLZ7", 3, 22),
    ("WFG1", 3, 12),
    ("WFG2", 3, 12),
    ("WFG3", 3, 12),
    ("WFG4", 3, 12),
    ("WFG5", 3, 12),
    ("WFG6", 3, 12),
    ("WFG7", 3, 12),
    ("WFG8", 3, 12),
    ("WFG9", 3, 12),
    ("MaF1", 3, 12),
    ("MaF2", 3, 12),
    ("MaF3", 3, 12),
    ("MaF4", 3, 12),
    ("MaF5", 3, 12),
    ("MaF6", 3, 12),
    ("MaF7", 3, 22),
]


def parse_run_id(filename: str) -> int | None:
    match = re.search(r"_(\d+)\.mat$", filename)
    if not match:
        return None
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        default="/home/pedro/desenvolvimento/ivfspea2",
        help="Project root path",
    )
    parser.add_argument(
        "--run-id-base",
        type=int,
        default=300000,
        help="Run ID base for phase3",
    )
    parser.add_argument(
        "--runs-per-problem",
        type=int,
        default=60,
        help="Expected runs per problem",
    )
    parser.add_argument(
        "--check-metrics",
        action="store_true",
        help="Also verify IGD and HV exist in each MAT file",
    )
    args = parser.parse_args()

    phase3_dir = Path(args.project_root) / "data" / "ablation_v2" / "phase3"
    if not phase3_dir.is_dir():
        print(f"ERROR: missing directory: {phase3_dir}")
        return 2

    expected_runs = {args.run_id_base + i for i in range(1, args.runs_per_problem + 1)}
    bad_folders: list[tuple[str, str]] = []
    ok_folders = 0

    metric_failures = 0
    metric_checked = 0
    pymatreader = None
    if args.check_metrics:
        try:
            import pymatreader as _pm

            pymatreader = _pm
        except Exception as exc:
            print(f"ERROR: --check-metrics requires pymatreader: {exc}")
            return 3

    for prob, m, _d in PROBLEMS:
        folder = phase3_dir / f"IVFSPEA2_P2_C05_{prob}_M{m}"
        if not folder.is_dir():
            bad_folders.append((folder.name, "missing folder"))
            continue

        files = sorted(folder.glob("*.mat"))
        run_ids = {
            rid for rid in (parse_run_id(f.name) for f in files) if rid is not None
        }

        missing = sorted(expected_runs - run_ids)
        extra = sorted(run_ids - expected_runs)

        if missing or extra or len(run_ids) != args.runs_per_problem:
            reason_parts = []
            if missing:
                reason_parts.append(f"missing={len(missing)}")
            if extra:
                reason_parts.append(f"extra={len(extra)}")
            if len(run_ids) != args.runs_per_problem:
                reason_parts.append(
                    f"expected={args.runs_per_problem},found={len(run_ids)}"
                )
            bad_folders.append((folder.name, ", ".join(reason_parts)))
            continue

        ok_folders += 1

        if pymatreader is not None:
            for mat_file in files:
                metric_checked += 1
                try:
                    data = pymatreader.read_mat(str(mat_file))
                    metric = data.get("metric")
                    if (
                        not isinstance(metric, dict)
                        or "IGD" not in metric
                        or "HV" not in metric
                    ):
                        metric_failures += 1
                except Exception:
                    metric_failures += 1

    print(f"Checked folders: {ok_folders}/{len(PROBLEMS)} OK")

    if bad_folders:
        print("\nIntegrity FAIL:")
        for name, reason in bad_folders[:40]:
            print(f"  - {name}: {reason}")
        if len(bad_folders) > 40:
            print(f"  ... and {len(bad_folders) - 40} more")
        return 1

    if pymatreader is not None:
        if metric_failures > 0:
            print(
                f"Metric FAIL: {metric_failures}/{metric_checked} files missing IGD and/or HV"
            )
            return 1
        print(f"Metric PASS: {metric_checked} files with IGD+HV")

    print("Integrity PASS: all phase3 folders are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
