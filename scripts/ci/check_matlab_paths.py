#!/usr/bin/env python3
"""Fail when a MATLAB script adds a path that does not exist.

Eight runners called ``addpath`` on ``src/matlab/ivf_spea2`` — a directory that is
gitignored precisely *because* it shadows the canonical PlatEMO classes. MATLAB
does not complain about adding a nonexistent directory, so this was silent. Worse
than dead: had anyone restored that directory, those eight would have resolved
``CalFitness`` to the wrong implementation and produced plausible, wrong numbers.

Only literal paths built from a project-root variable are checked. Paths assembled
from loop variables or function arguments are skipped — they cannot be resolved
statically, and guessing would produce false failures.

    python scripts/ci/check_matlab_paths.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# addpath(fullfile(ROOTVAR, 'a', 'b'))  /  addpath(genpath(fullfile(ROOTVAR, 'a')))
ADDPATH = re.compile(
    r"addpath\(\s*(?:genpath\(\s*)?fullfile\(\s*(?P<root>\w+)\s*,\s*(?P<parts>[^)]*)\)",
)
QUOTED = re.compile(r"'([^']*)'")

ROOT_VARS = {"PROJECT_ROOT", "PROJECT_DIR", "REPO_ROOT", "ROOT_DIR", "projectRoot", "project_root"}

SCANNED_DIRS = ("experiments/", "scripts/", "tests/matlab/")
EXEMPT_PREFIXES = ("src/matlab/lib/PlatEMO/", "legacy/")


def tracked(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
    )
    return out.stdout.splitlines()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    problems: list[tuple[str, int, str]] = []
    checked = 0

    for name in tracked(root):
        if not name.endswith(".m") or name.startswith(EXEMPT_PREFIXES):
            continue
        if not name.startswith(SCANNED_DIRS):
            continue
        path = root / name
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            match = ADDPATH.search(line)
            if not match or match.group("root") not in ROOT_VARS:
                continue
            parts = QUOTED.findall(match.group("parts"))
            if not parts:
                continue  # dynamically assembled; not statically checkable
            checked += 1
            target = root.joinpath(*parts)
            if not target.is_dir():
                problems.append((name, lineno, "/".join(parts)))

    if not problems:
        print(f"check_matlab_paths: OK — {checked} resolvable addpath target(s), all present.")
        return 0

    for name, lineno, rel in problems:
        print(f"{name}:{lineno}: addpath target does not exist: {rel}", file=sys.stderr)
    print(
        f"\ncheck_matlab_paths: FAILED — {len(problems)} addpath call(s) point at "
        "a directory that is not in the repository.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
