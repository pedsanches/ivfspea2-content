#!/usr/bin/env python3
"""Keep AGENTS.md a faithful mirror of CLAUDE.md.

The two files carry the same repository guidance for different agents, and
CLAUDE.md states the mirroring obligation in its own opening lines. That
obligation was not kept: the pair had drifted by 175 lines, so AGENTS.md still
described two manuscripts and no thesis.

Only the header differs — everything from the first `## ` heading onward must be
identical.

    python scripts/ci/check_agents_mirror.py           # verify, exit 1 on drift
    python scripts/ci/check_agents_mirror.py --write   # regenerate AGENTS.md
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

HEADER = """# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

<!-- Generated from CLAUDE.md by scripts/ci/check_agents_mirror.py --write.
     Edit CLAUDE.md instead; this file is checked for drift in CI. -->
"""


def split_body(text: str) -> str:
    """Everything from the first level-2 heading onward."""
    marker = text.find("\n## ")
    if marker == -1:
        raise SystemExit("expected a '## ' section heading")
    return text[marker:].lstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate AGENTS.md")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    claude = root / "CLAUDE.md"
    agents = root / "AGENTS.md"

    body = split_body(claude.read_text(encoding="utf-8"))
    expected = f"{HEADER}\n{body}"

    if args.write:
        agents.write_text(expected, encoding="utf-8")
        print(f"Wrote {agents.name} from {claude.name} ({len(expected.splitlines())} lines).")
        return 0

    actual = agents.read_text(encoding="utf-8") if agents.exists() else ""
    if actual == expected:
        print("check_agents_mirror: OK — AGENTS.md matches CLAUDE.md.")
        return 0

    diff = difflib.unified_diff(
        actual.splitlines(),
        expected.splitlines(),
        fromfile="AGENTS.md",
        tofile="AGENTS.md (expected from CLAUDE.md)",
        lineterm="",
        n=1,
    )
    print("\n".join(list(diff)[:60]), file=sys.stderr)
    print(
        "\ncheck_agents_mirror: FAILED — AGENTS.md has drifted from CLAUDE.md.\n"
        "Edit CLAUDE.md, then run: python scripts/ci/check_agents_mirror.py --write",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
