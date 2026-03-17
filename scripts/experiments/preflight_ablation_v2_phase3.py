#!/usr/bin/env python3
"""
Preflight checks for ablation v2 phase3 execution.

Goals:
- confirm phase2 winner is P2_C05
- confirm phase2 dataset integrity (192/192)
- confirm baseline coverage (IVFSPEA2 + SPEA2) is complete on 51 instances
- confirm phase3 target directory is safe (no foreign folders, no foreign run IDs)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


EXPECTED_WINNER = "P2_C05"
RUN_ID_BASE = 300000
RUNS_PER_PROBLEM = 60

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


def normalize_m(value: str) -> int:
    text = str(value).strip()
    if text.startswith("M"):
        text = text[1:]
    return int(text)


def has_metric(value: str) -> bool:
    text = str(value).strip()
    if text == "":
        return False
    if text.lower() in {"nan", "none", "null"}:
        return False
    return True


def check_phase2_winner(project_root: Path) -> list[str]:
    errors: list[str] = []
    summary_path = (
        project_root / "results" / "ablation_v2" / "phase2" / "phase2_summary.json"
    )
    if not summary_path.is_file():
        return [f"Missing phase2 summary: {summary_path}"]

    with summary_path.open() as f:
        summary = json.load(f)

    winner = summary.get("winner", {}).get("config_id")
    if winner != EXPECTED_WINNER:
        errors.append(
            f"Unexpected phase2 winner: {winner!r} (expected {EXPECTED_WINNER!r})"
        )
    return errors


def check_phase2_integrity(project_root: Path, python_exec: str) -> list[str]:
    errors: list[str] = []
    checker = (
        project_root
        / "scripts"
        / "experiments"
        / "verify_ablation_v2_phase2_integrity.py"
    )
    if not checker.is_file():
        return [f"Missing phase2 integrity checker: {checker}"]

    proc = subprocess.run(
        [python_exec, str(checker)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        head = (proc.stdout or "").splitlines()[:6]
        msg = " | ".join(head) if head else (proc.stderr.strip() or "unknown error")
        errors.append(f"Phase2 integrity check failed: {msg}")
    return errors


def check_baseline_coverage(project_root: Path) -> list[str]:
    errors: list[str] = []
    csv_path = project_root / "data" / "processed" / "todas_metricas_consolidado.csv"
    if not csv_path.is_file():
        return [f"Missing consolidated CSV: {csv_path}"]

    required_algs = ("IVFSPEA2", "SPEA2")
    expected_pairs = {(prob, m) for prob, m, _ in PROBLEMS}

    stats: dict[str, dict[tuple[str, int], dict[str, object]]] = {
        alg: defaultdict(lambda: {"rows": 0, "runs": set(), "igd": 0, "hv": 0})
        for alg in required_algs
    }

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alg = row.get("Algoritmo", "")
            if alg not in stats:
                continue
            prob = row.get("Problema", "").strip()
            if not prob:
                continue
            try:
                m = normalize_m(row.get("M", ""))
            except Exception:
                continue

            key = (prob, m)
            entry = stats[alg][key]
            entry["rows"] = int(entry["rows"]) + 1

            run_text = str(row.get("Run", "")).strip()
            if run_text:
                entry["runs"].add(run_text)

            if has_metric(row.get("IGD", "")):
                entry["igd"] = int(entry["igd"]) + 1
            if has_metric(row.get("HV", "")):
                entry["hv"] = int(entry["hv"]) + 1

    for alg in required_algs:
        alg_pairs = set(stats[alg].keys())
        missing_pairs = sorted(expected_pairs - alg_pairs)
        extra_pairs = sorted(alg_pairs - expected_pairs)

        if missing_pairs:
            errors.append(f"{alg}: missing {len(missing_pairs)} problem-M pairs")
        if extra_pairs:
            errors.append(f"{alg}: found {len(extra_pairs)} unexpected problem-M pairs")

        bad_rows: list[str] = []
        for pair in sorted(expected_pairs):
            entry = stats[alg].get(pair)
            if not entry:
                continue
            rows = int(entry["rows"])
            runs = len(entry["runs"])
            igd = int(entry["igd"])
            hv = int(entry["hv"])
            if (
                rows != RUNS_PER_PROBLEM
                or runs != RUNS_PER_PROBLEM
                or igd != RUNS_PER_PROBLEM
                or hv != RUNS_PER_PROBLEM
            ):
                bad_rows.append(
                    f"{pair[0]}(M={pair[1]}): rows={rows}, runs={runs}, IGD={igd}, HV={hv}"
                )

        if bad_rows:
            errors.append(
                f"{alg}: {len(bad_rows)} incomplete pairs (sample: {', '.join(bad_rows[:3])})"
            )

    return errors


def check_phase3_target(project_root: Path) -> list[str]:
    errors: list[str] = []
    phase3_dir = project_root / "data" / "ablation_v2" / "phase3"
    expected_folders = {
        f"IVFSPEA2_{EXPECTED_WINNER}_{prob}_M{m}" for prob, m, _ in PROBLEMS
    }
    expected_runs = {RUN_ID_BASE + i for i in range(1, RUNS_PER_PROBLEM + 1)}

    if not phase3_dir.exists():
        return errors
    if not phase3_dir.is_dir():
        return [f"Phase3 target path exists but is not a directory: {phase3_dir}"]

    actual_folders = {p.name for p in phase3_dir.iterdir() if p.is_dir()}
    unexpected = sorted(actual_folders - expected_folders)
    if unexpected:
        errors.append(
            f"Unexpected folders in phase3 directory ({len(unexpected)}): {', '.join(unexpected[:5])}"
        )

    run_pat = re.compile(r"_(\d+)\.mat$")
    for folder_name in sorted(actual_folders & expected_folders):
        folder = phase3_dir / folder_name
        run_ids = set()
        for f in folder.glob("*.mat"):
            m = run_pat.search(f.name)
            if m:
                run_ids.add(int(m.group(1)))

        outside = sorted(run_ids - expected_runs)
        if outside:
            errors.append(
                f"{folder_name}: found {len(outside)} out-of-range run IDs (sample: {outside[:5]})"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        default="/home/pedro/desenvolvimento/ivfspea2",
        help="Project root path",
    )
    parser.add_argument(
        "--python-exec",
        default=sys.executable,
        help="Python executable to run sub-checks",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root)
    all_errors: list[str] = []

    all_errors.extend(check_phase2_winner(project_root))
    all_errors.extend(check_phase2_integrity(project_root, args.python_exec))
    all_errors.extend(check_baseline_coverage(project_root))
    all_errors.extend(check_phase3_target(project_root))

    if all_errors:
        print("Preflight FAIL")
        for err in all_errors:
            print(f" - {err}")
        return 1

    print("Preflight PASS")
    print(f" - phase2 winner confirmed: {EXPECTED_WINNER}")
    print(" - phase2 integrity confirmed")
    print(" - baseline coverage confirmed (IVFSPEA2 + SPEA2, 51x60, IGD+HV)")
    print(
        f" - phase3 target validated (run range {RUN_ID_BASE + 1}-{RUN_ID_BASE + RUNS_PER_PROBLEM})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
