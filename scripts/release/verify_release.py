#!/usr/bin/env python3
"""Verify — or regenerate — the release manifest and its checksums.

    python scripts/release/verify_release.py            # check, exit 1 on any problem
    python scripts/release/verify_release.py --write     # regenerate the checksum file
    python scripts/release/verify_release.py --quiet     # only the summary line

Run by CI (``release-integrity``) and by ``make verify-release``. Exits non-zero
when anything a reader could follow would lead them to a file that is not there.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

# Importable before `pip install -e .` so a fresh clone can verify itself.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "python"))

from ivfspea2 import release  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate results/submission_release_checksums.sha256 from the manifest",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress the per-problem listing")
    args = parser.parse_args()

    root = release.find_root(Path(__file__))

    if args.write:
        lines = release.write_checksums(root)
        print(f"Wrote {release.CHECKSUMS_RELPATH} with {len(lines)} entries.")

    problems = (
        release.verify_manifest(root) + release.verify_checksums(root) + release.verify_dois(root)
    )

    if not problems:
        print("Release integrity OK: every manifest row resolves and every checksum matches.")
        return 0

    if not args.quiet:
        for problem in problems:
            print(str(problem), file=sys.stderr)
        print(file=sys.stderr)

    counts = Counter(problem.kind for problem in problems)
    summary = ", ".join(f"{kind}={count}" for kind, count in sorted(counts.items()))
    print(f"Release integrity FAILED: {len(problems)} problem(s) — {summary}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
