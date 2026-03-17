#!/usr/bin/env python3
"""
Flatten LaTeX: expand all \\input{...} directives into a single self-contained .tex file.

Usage:
    python paper/scripts/flatten_tex.py paper/src/sn-article.tex paper/src/sn-article-flat.tex

The output file can be submitted directly to journal systems that prohibit \\input.
"""

import re
import sys
from pathlib import Path


def resolve_input(match, base_dir):
    """Replace an \\input{path} with the contents of the referenced file."""
    rel_path = match.group(1)
    # Resolve relative to the directory of the source .tex file
    full_path = (base_dir / rel_path).resolve()
    if not full_path.exists():
        print(f"WARNING: {full_path} not found, keeping \\input as-is", file=sys.stderr)
        return match.group(0)
    content = full_path.read_text(encoding="utf-8")
    return f"% --- BEGIN inlined from {rel_path} ---\n{content}\n% --- END inlined from {rel_path} ---"


def flatten(src_path, dst_path):
    src = Path(src_path)
    base_dir = src.parent
    text = src.read_text(encoding="utf-8")

    # Match \input{...} but skip commented-out lines and the template warning line
    pattern = re.compile(r"^(?!%%)(.*)\\input\{([^}]+)\}", re.MULTILINE)

    def replacer(m):
        prefix = m.group(1)
        rel_path = m.group(2)
        full_path = (base_dir / rel_path).resolve()
        if not full_path.exists():
            print(f"WARNING: {full_path} not found, keeping \\input as-is", file=sys.stderr)
            return m.group(0)
        content = full_path.read_text(encoding="utf-8")
        return f"{prefix}% --- BEGIN inlined from {rel_path} ---\n{content}\n% --- END inlined from {rel_path} ---"

    result = pattern.sub(replacer, text)

    Path(dst_path).write_text(result, encoding="utf-8")
    print(f"Flattened: {src_path} -> {dst_path}")

    # Count remaining \input
    remaining = re.findall(r"^[^%].*\\input\{", result, re.MULTILINE)
    if remaining:
        print(f"WARNING: {len(remaining)} \\input directives still remain", file=sys.stderr)
    else:
        print("All \\input directives expanded successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.tex> <output.tex>")
        sys.exit(1)
    flatten(sys.argv[1], sys.argv[2])
