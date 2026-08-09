#!/usr/bin/env python3
"""Keep the boundary between project code and vendored PlatEMO visible.

The project's 18 algorithm directories live *inside* the vendored PlatEMO tree,
because `platemo()` discovers algorithms by scanning that directory. The cost is
that project code and third-party code cannot be told apart by path, so a new
directory added there would blend into ~1,940 upstream files and make a future
upstream diff even harder than it already is.

`VENDOR.md` records the inventory; this check asserts the tree still matches it.

    python scripts/ci/check_platemo_inventory.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALGORITHMS_REL = Path("src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization")
VENDOR_REL = Path("src/matlab/lib/PlatEMO/VENDOR.md")

# Project directories are the IVF* families plus this one, which is project-added
# but does not carry the IVF prefix.
EXTRA_PROJECT_DIRS = {"SPEA2-TRACE"}


def project_dirs_on_disk(root: Path) -> set[str]:
    algorithms = root / ALGORITHMS_REL
    if not algorithms.is_dir():
        raise SystemExit(f"missing {ALGORITHMS_REL}")
    found = {p.name for p in algorithms.iterdir() if p.is_dir() and p.name.startswith("IVF")}
    return found | {d for d in EXTRA_PROJECT_DIRS if (algorithms / d).is_dir()}


def project_dirs_in_vendor_doc(root: Path) -> set[str]:
    """Parse the delimited inventory block, not the prose.

    The prose table groups names (``-ABL-4C``) and mentions class names
    (``IVFSPEA2V2``) that are not directories, so scraping it produces both false
    positives and false negatives. The delimited block is unambiguous.
    """
    text = (root / VENDOR_REL).read_text(encoding="utf-8")
    block = re.search(r"<!-- BEGIN PROJECT-DIRS -->\s*```\n(.*?)\n```", text, re.DOTALL)
    if not block:
        raise SystemExit(f"{VENDOR_REL} has no <!-- BEGIN PROJECT-DIRS --> inventory block")
    return {line.strip() for line in block.group(1).splitlines() if line.strip()}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    on_disk = project_dirs_on_disk(root)
    documented = project_dirs_in_vendor_doc(root)

    undocumented = on_disk - documented
    stale = documented - on_disk

    if not undocumented and not stale:
        m_files = sum(len(list((root / ALGORITHMS_REL / d).glob("*.m"))) for d in sorted(on_disk))
        print(
            f"check_platemo_inventory: OK — {len(on_disk)} project directories "
            f"({m_files} .m files) inside the vendored tree, all documented."
        )
        return 0

    for name in sorted(undocumented):
        print(
            f"undocumented project directory: {ALGORITHMS_REL / name}\n"
            f"    add it to {VENDOR_REL}, or it will be indistinguishable from upstream PlatEMO",
            file=sys.stderr,
        )
    for name in sorted(stale):
        print(
            f"{VENDOR_REL} lists {name}, which no longer exists\n"
            f"    remove the row so the inventory stays trustworthy",
            file=sys.stderr,
        )
    print(
        f"\ncheck_platemo_inventory: FAILED — {len(undocumented)} undocumented, {len(stale)} stale",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
