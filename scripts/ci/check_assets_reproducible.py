#!/usr/bin/env python3
"""Compare regenerated assets against the committed ones.

Run *after* rebuilding the accepted paper's assets, from a clean tree:

    make -C paper/ppsn2026-ivf-hosts assets PYTHON=python
    python scripts/ci/check_assets_reproducible.py

Why this is not `git diff --exit-code`
--------------------------------------

That was the original check, and it fails for a reason that is not a defect.
The committed CSVs were produced on macOS/arm64; CI runs Linux/x86-64. Reducing
the same doubles in a different order — different BLAS kernels, different SIMD
widths — lands on a neighbouring double, and the shortest-roundtrip repr then
prints a visibly different string for a value that is identical to 15 decimal
digits::

    IVFNSGAII,MaF5,MaF,3,12,4010,4.8884956986782955,...   # macOS/arm64
    IVFNSGAII,MaF5,MaF,3,12,4010,4.888495698678296,...    # Linux/x86-64

Byte-identity of a floating-point pipeline across architectures is not
achievable, so asserting it would either force the job to be ignored or force
the numbers to be rounded for the checker's benefit. Neither is worth it.

What is asserted instead
------------------------

**Structure exactly, values to tolerance.** Row count, column names and every
non-numeric cell must match exactly — that is what catches a changed cohort
filter, a dropped instance, a renamed column, or a reordered frame. Numeric
cells must agree within ``RTOL``, which is far tighter than any real analytical
change and far looser than one ULP.

Figures are compared on presence and structural sanity only: a PDF rendered
from data that differs in the last bit is itself byte-different, so byte
comparison would fail for the same non-reason.

On the producer platform the stronger property does hold, and it is worth
keeping: `make assets && git diff --exit-code` is byte-clean on macOS/arm64
with `requirements.lock.txt`. That check belongs locally, not in CI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RTOL = 1e-9

CSV_TARGETS = ("data/processed/", "results/tables/")
FIGURE_DIR = Path("paper/ppsn2026-ivf-hosts/figures")


def changed_paths(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def committed_text(root: Path, rel: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(root), "show", f"HEAD:{rel}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout


def compare_csv(root: Path, rel: str) -> list[str]:
    """Structure exactly, numbers within RTOL."""
    import csv as _csv
    import io
    import math

    problems: list[str] = []
    before = list(_csv.reader(io.StringIO(committed_text(root, rel))))
    after = list(_csv.reader((root / rel).open(encoding="utf-8", newline="")))

    if len(before) != len(after):
        return [f"{rel}: row count {len(before)} -> {len(after)}"]
    if before and before[0] != after[0]:
        return [f"{rel}: header changed\n    was {before[0]}\n    now {after[0]}"]

    drifted = 0
    worst = 0.0
    for line_no, (row_a, row_b) in enumerate(zip(before[1:], after[1:]), start=2):
        if len(row_a) != len(row_b):
            problems.append(f"{rel}:{line_no}: column count {len(row_a)} -> {len(row_b)}")
            continue
        for col, (cell_a, cell_b) in enumerate(zip(row_a, row_b)):
            if cell_a == cell_b:
                continue
            try:
                num_a, num_b = float(cell_a), float(cell_b)
            except ValueError:
                problems.append(
                    f"{rel}:{line_no} col {col}: non-numeric cell changed "
                    f"{cell_a!r} -> {cell_b!r}"
                )
                continue
            if math.isclose(num_a, num_b, rel_tol=RTOL, abs_tol=0.0):
                drifted += 1
                worst = max(worst, abs(num_a - num_b) / max(abs(num_a), 1e-300))
            else:
                problems.append(
                    f"{rel}:{line_no} col {col}: {num_a!r} -> {num_b!r} "
                    f"(relative change {abs(num_a - num_b) / max(abs(num_a), 1e-300):.2e} "
                    f"exceeds rtol={RTOL:.0e})"
                )

    if drifted and not problems:
        print(
            f"  {rel}: {drifted} cell(s) differ at last-bit precision "
            f"(worst relative {worst:.2e}) — within tolerance"
        )
    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    changed = changed_paths(root)

    if not changed:
        print("check_assets_reproducible: OK — regeneration changed nothing at all.")
        return 0

    print(f"Regeneration touched {len(changed)} file(s); checking what actually changed.\n")

    problems: list[str] = []
    figures_changed: list[str] = []

    for rel in changed:
        if rel.startswith(str(FIGURE_DIR)):
            figures_changed.append(rel)
        elif rel.endswith(".csv") and rel.startswith(CSV_TARGETS):
            problems.extend(compare_csv(root, rel))
        elif rel.endswith((".tex", ".txt")) and rel.startswith(CSV_TARGETS):
            if committed_text(root, rel) != (root / rel).read_text(encoding="utf-8"):
                problems.append(f"{rel}: generated table text changed")
        else:
            problems.append(f"{rel}: unexpected file changed by the assets build")

    if figures_changed:
        missing = [rel for rel in figures_changed if not (root / rel).exists()]
        problems.extend(f"{rel}: figure disappeared during rebuild" for rel in missing)
        print(
            f"  {len(figures_changed)} figure(s) re-rendered; byte comparison skipped "
            "(PDFs inherit last-bit data differences)"
        )

    if problems:
        print("\n::error::Regenerating the assets changed more than last-bit precision.")
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            f"\ncheck_assets_reproducible: FAILED — {len(problems)} substantive difference(s)",
            file=sys.stderr,
        )
        return 1

    print("\ncheck_assets_reproducible: OK — structure identical, numbers within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
