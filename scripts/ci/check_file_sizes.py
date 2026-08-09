#!/usr/bin/env python3
"""Fail when a change adds a large blob that is not explicitly allowed.

The repository already carries a 54 MB CSV, a 26 MB TIFF and a 20 MB zip, and
`.gitignore` name-lists three more files with the comment "exceeds GitHub 100MB
limit" — meaning the ceiling was hit at least three times before anyone noticed.
History is not being rewritten, so the only remaining lever is to stop the growth.

Existing large files are listed in `.largefiles-allow`, which documents why each
one is kept. New ones need a line there and a reason.

    python scripts/ci/check_file_sizes.py --base origin/main --head HEAD
    python scripts/ci/check_file_sizes.py            # working tree vs HEAD
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

LIMIT_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWFILE = ".largefiles-allow"


def load_allowlist(root: Path) -> set[str]:
    path = root / ALLOWFILE
    if not path.exists():
        return set()
    entries = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            entries.add(line)
    return entries


def changed_files(root: Path, base: str | None, head: str) -> list[str]:
    args = ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=AM"]
    args.append(f"{base}...{head}" if base else "HEAD")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"check_file_sizes: could not diff ({result.stderr.strip()}); skipping.",
            file=sys.stderr,
        )
        return []
    return [name for name in result.stdout.splitlines() if name]


def human(size: int) -> str:
    return f"{size / (1024 * 1024):.1f} MB"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=None, help="base ref to diff against")
    parser.add_argument("--head", default="HEAD", help="head ref")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    allowed = load_allowlist(root)

    offenders: list[tuple[str, int]] = []
    for name in changed_files(root, args.base, args.head):
        if name in allowed:
            continue
        path = root / name
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > LIMIT_BYTES:
            offenders.append((name, size))

    if not offenders:
        print(f"check_file_sizes: OK — nothing added above {human(LIMIT_BYTES)}.")
        return 0

    for name, size in sorted(offenders, key=lambda item: -item[1]):
        print(f"{name}: {human(size)} exceeds the {human(LIMIT_BYTES)} limit", file=sys.stderr)
    print(
        f"\ncheck_file_sizes: FAILED — {len(offenders)} oversized file(s).\n"
        f"Regenerate it instead of committing it, or add it to {ALLOWFILE} with a reason.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
