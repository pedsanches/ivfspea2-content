#!/usr/bin/env python3
"""Fail when tracked source hardcodes a path from someone's machine.

48 tracked files carried ``/home/pedro/...`` — a Linux path that does not exist on
the machine this repository now lives on, so every one of those scripts was
already broken and nothing said so. Absolute paths are also the single loudest
signal to a reviewer that a pipeline was never run anywhere but its author's
laptop.

``legacy/`` is exempt: those scripts are retained for the record, not for running.
Vendored PlatEMO is exempt because it is not ours to edit.

    python scripts/ci/check_paths.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

FORBIDDEN = [
    (re.compile(r"/home/[a-z][a-z0-9_-]*/"), "absolute path into a user home directory"),
    (re.compile(r"/Users/[a-z][a-z0-9_-]*/"), "absolute path into a macOS home directory"),
]

EXEMPT_PREFIXES = (
    "src/matlab/lib/PlatEMO/",
    "legacy/",
    "artifact/ppsn2026-ivf-hosts-rev1/",
    "docs/history/",
    "scripts/ci/check_paths.py",
)

SCANNED_SUFFIXES = (".py", ".m", ".sh", ".mk", ".toml", ".cfg", ".yml", ".yaml")

# Pre-existing offenders, recorded so the guard can be enforced today instead of
# waiting for a 55-file cleanup. THIS LIST MUST ONLY EVER SHRINK — a new entry
# means a new hardcoded path, which is the thing being prevented.
#
# It empties out across two changes: scripts that are orphaned move to legacy/
# (exempt), and the rest adopt ivfspea2.paths.PROJECT_ROOT.
ALLOWLIST: frozenset[str] = frozenset(
    {
        "experiments/launch_ppsn_controller_oos_lofo.sh",
        "experiments/launch_ppsn_controller_oos_lofo_parallel.sh",
        "experiments/probe_rwmop_feasibility.m",
        "experiments/probe_rwmop_feasibility_v2.m",
        "experiments/process_engineering_suite.m",
        "experiments/run_controlled_short_benchmark.m",
        "experiments/run_engineering_suite_rwmop.m",
        "scripts/build_detailed_tables_with_modern.m",
        "scripts/build_runtime_modern_summary.m",
        "scripts/compute_hv_modern_baselines.m",
        "scripts/compute_missing_hv.m",
        "scripts/experiments/launch_ablation_v2.sh",
        "scripts/experiments/launch_ablation_v2_phase2.sh",
        "scripts/experiments/launch_ablation_v2_phase3.sh",
        "scripts/experiments/preflight_ablation_v2_phase3.py",
        "scripts/experiments/prepare_ivfspea2v2_phase_b.py",
        "scripts/experiments/run_ablation_study.m",
        "scripts/experiments/run_ablation_v2_batch_A.m",
        "scripts/experiments/run_ablation_v2_batch_B.m",
        "scripts/experiments/run_ablation_v2_batch_C.m",
        "scripts/experiments/run_ablation_v2_phase2_batch_A.m",
        "scripts/experiments/run_ablation_v2_phase2_batch_B.m",
        "scripts/experiments/run_ablation_v2_phase2_batch_C.m",
        "scripts/experiments/run_ablation_v2_phase3_batch_A.m",
        "scripts/experiments/run_ablation_v2_phase3_batch_B.m",
        "scripts/experiments/run_ablation_v2_phase3_batch_C.m",
        "scripts/experiments/run_ablation_v2_phase3_batch_common.m",
        "scripts/experiments/run_engineering_rwmop9.m",
        "scripts/experiments/run_ivfspea2v2_tuning.m",
        "scripts/experiments/run_modern_baselines.m",
        "scripts/experiments/run_sensitivity_multiclass.m",
        "scripts/experiments/test_ablation_v2_hard.m",
        "scripts/experiments/test_ablation_v2_variants.m",
        "scripts/experiments/verify_ablation_v2_phase2_integrity.py",
        "scripts/experiments/verify_ablation_v2_phase3_integrity.py",
        "scripts/experiments/verify_ivfspea2v2_tuning_integrity.py",
        "scripts/hv_m2_crosscheck.m",
        "scripts/integrate_modern_baselines_main.m",
        "scripts/run_engineering_suite_main_parallel.sh",
        "scripts/run_rwmop_feasibility_probe_v2_parallel.sh",
        "src/python/analysis/analyze_ablation_v2_phase1.py",
        "src/python/analysis/analyze_ablation_v2_phase2.py",
        "src/python/analysis/analyze_ablation_v2_phase3.py",
        "src/python/analysis/analyze_engineering.py",
        "src/python/analysis/analyze_ivfspea2v2_tuning.py",
        "src/python/analysis/plot_sensitivity.py",
        "src/python/analysis/sensitivity_analysis.py",
    }
)


def tracked(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
    )
    return out.stdout.splitlines()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    offenders: list[tuple[str, int, str, str]] = []

    for name in tracked(root):
        if name.startswith(EXEMPT_PREFIXES) or not name.endswith(SCANNED_SUFFIXES):
            continue
        if name in ALLOWLIST:
            continue
        path = root / name
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern, why in FORBIDDEN:
                if pattern.search(line):
                    offenders.append((name, lineno, why, line.strip()[:100]))
                    break

    if not offenders:
        remaining = len(ALLOWLIST)
        note = f" ({remaining} known offender(s) still allowlisted)" if remaining else ""
        print(f"check_paths: OK — no new hardcoded home directories{note}.")
        return 0

    for name, lineno, why, snippet in offenders:
        print(f"{name}:{lineno}: {why}\n    {snippet}", file=sys.stderr)
    print(
        f"\ncheck_paths: FAILED — {len(offenders)} hardcoded path(s) in "
        f"{len({o[0] for o in offenders})} file(s). "
        "Use ivfspea2.paths.PROJECT_ROOT, or move the script to legacy/.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
