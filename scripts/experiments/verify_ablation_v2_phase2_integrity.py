#!/usr/bin/env python3
"""
Verify integrity of ablation v2 phase2 outputs.

Expected layout:
  data/ablation_v2/phase2/IVFSPEA2_P2_C<XX>_<PROB>_M<M>/*.mat

Validation rules:
  - 16 configs x 12 problems folders must exist
  - each folder must contain exactly 60 expected run IDs
  - expected run IDs are derived from config index and run-id base
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROBLEMS = [
    ("ZDT1", 2),
    ("ZDT6", 2),
    ("WFG4", 2),
    ("WFG9", 2),
    ("DTLZ1", 3),
    ("DTLZ2", 3),
    ("DTLZ4", 3),
    ("DTLZ7", 3),
    ("WFG2", 3),
    ("WFG5", 3),
    ("MaF1", 3),
    ("MaF5", 3),
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
        default=100000,
        help="Run ID base used by phase2 batch scripts",
    )
    parser.add_argument(
        "--runs-per-config",
        type=int,
        default=60,
        help="Expected runs per config-problem folder",
    )
    args = parser.parse_args()

    phase2_dir = Path(args.project_root) / "data" / "ablation_v2" / "phase2"
    if not phase2_dir.is_dir():
        print(f"ERROR: missing directory: {phase2_dir}")
        return 2

    total_expected_folders = 16 * len(PROBLEMS)
    bad_folders: list[tuple[str, str]] = []
    ok_folders = 0

    for cfg_idx in range(16):
        cfg_name = f"P2_C{cfg_idx:02d}"
        expected_runs = {
            args.run_id_base + cfg_idx * args.runs_per_config + local_run
            for local_run in range(1, args.runs_per_config + 1)
        }

        for prob_name, m_val in PROBLEMS:
            folder = phase2_dir / f"IVFSPEA2_{cfg_name}_{prob_name}_M{m_val}"
            if not folder.is_dir():
                bad_folders.append((folder.name, "missing folder"))
                continue

            files = sorted(folder.glob("*.mat"))
            run_ids = {
                rid for rid in (parse_run_id(f.name) for f in files) if rid is not None
            }

            missing = sorted(expected_runs - run_ids)
            extra = sorted(run_ids - expected_runs)

            if missing or extra or len(run_ids) != args.runs_per_config:
                reason_parts = []
                if missing:
                    reason_parts.append(f"missing={len(missing)}")
                if extra:
                    reason_parts.append(f"extra={len(extra)}")
                if len(run_ids) != args.runs_per_config:
                    reason_parts.append(
                        f"expected={args.runs_per_config},found={len(run_ids)}"
                    )
                bad_folders.append((folder.name, ", ".join(reason_parts)))
            else:
                ok_folders += 1

    print(f"Checked folders: {ok_folders}/{total_expected_folders} OK")
    if bad_folders:
        print("\nIntegrity FAIL:")
        for name, reason in bad_folders[:40]:
            print(f"  - {name}: {reason}")
        if len(bad_folders) > 40:
            print(f"  ... and {len(bad_folders) - 40} more")
        return 1

    print("Integrity PASS: all phase2 folders are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
