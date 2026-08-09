#!/usr/bin/env python3
"""Classify the analysis scripts as live or orphaned, by rule rather than by eye.

Two manual censuses of ``src/python/analysis/`` disagreed — 30 orphans by one
criterion, 47 by another — which is reason enough not to hardcode a list. A
script is **live** when something can actually reach it:

* named in the root ``Makefile`` or any ``paper/*/Makefile``
* named in a shell launcher under ``experiments/`` or ``scripts/``
* imported by anything under ``tests/python/``
* imported, transitively, by a live script

Everything else is a **candidate**. Candidacy is not a verdict: the two guards
below veto a move regardless, and a human reviews what survives.

Guards (a script naming any of these is never a candidate):

* it appears in ``results/submission_release_manifest.csv`` as a ``producer`` or
  in ``primary_inputs`` — moving it would break the deposit's provenance chain
* it appears in ``results/SUBMISSION_EVIDENCE_MAP.md``
* it is on the ``PROTECTED`` list below

    python scripts/ci/find_orphans.py            # report
    python scripts/ci/find_orphans.py --json     # machine-readable
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

ANALYSIS_REL = Path("src/python/analysis")

# Never candidates, whatever the reachability analysis says.
PROTECTED = {
    # `make analysis` runs this. It reads like the oldest file in the tree
    # (Portuguese comments, bare exit(), ../../../ path chains) and is easy to
    # mistake for dead code, but it is the repository's default analysis target.
    "script",
    # Imported through the deprecation shims rather than by name.
    "cohort_filter",
    "figure_io",
    # Sole producer of six tracked CSVs under results/ivf_trace/ that nothing
    # currently reads. Nothing invoking it is not the same as nothing depending
    # on it: move it and those committed files become unregenerable.
    "prepare_ivf_trace_case_manifest",
}


def run(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def tracked(root: Path) -> list[str]:
    return run(["git", "-C", str(root), "ls-files"]).splitlines()


def referencing_text(root: Path) -> str:
    """Everything that could name a script: makefiles, shell, docs, configs."""
    chunks: list[str] = []
    for name in tracked(root):
        if name.startswith(("src/matlab/lib/PlatEMO/", "legacy/")):
            continue
        is_build = name == "Makefile" or name.endswith(
            ("/Makefile", ".mk", ".sh", ".yml", ".yaml", ".cfg", ".toml")
        )
        is_doc = name.endswith(".md")
        if not (is_build or is_doc):
            continue
        path = root / name
        if not path.exists():
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue
    return "\n".join(chunks)


def imported_names(path: Path) -> set[str]:
    """Module names imported by ``path``, as best a static parse can tell."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[-1])
    return names


def guarded_stems(root: Path) -> set[str]:
    """Stems the release evidence depends on; these can never be moved."""
    text = ""
    for rel in ("results/submission_release_manifest.csv", "results/SUBMISSION_EVIDENCE_MAP.md"):
        path = root / rel
        if path.exists():
            text += path.read_text(encoding="utf-8")
    return {match.group(1) for match in re.finditer(r"(\w+)\.py", text)}


# Matches a quoted filename whether it is bare or embedded in a path, because
# both spellings occur — sensitivity_analysis.py writes to a full absolute path,
# and matching only bare names silently missed it.
_DATAFILE = re.compile(r'["\']([\w/.-]*?[\w.-]+\.(?:csv|tex|json))["\']')
_WRITE_HINT = re.compile(r"to_csv|write_text|savefig|\b(?:OUT|OUTPUT|DEST|TARGET)\w*\s*=")


def _datafile_names(text: str) -> set[str]:
    """Basenames of the data files quoted in ``text``."""
    return {Path(match).name for match in _DATAFILE.findall(text)}


def needed_datafiles(root: Path, live_stems: set[str]) -> set[str]:
    """Filenames something live depends on: paper inputs, and whatever live code names.

    Scanning live scripts — not only the tests — is what catches the indirect
    case: ``test_hosts_figures_v3.py`` never spells
    ``sensitivity_analysis_igd.csv``; it imports ``load_sensitivity()`` from a
    live script that does.
    """
    needed: set[str] = set()

    for makefile in root.glob("paper/*/Makefile"):
        block = re.search(r"ASSET_INPUTS\s*=((?:.*\\\n)*.*)", makefile.read_text(encoding="utf-8"))
        if block:
            needed.update(
                Path(token).name for token in re.findall(r"[\w/$()\.-]+\.\w+", block.group(1))
            )

    sources = list((root / "tests" / "python").glob("*.py"))
    sources += [(root / ANALYSIS_REL / f"{stem}.py") for stem in live_stems]

    for path in sources:
        if not path.exists():
            continue
        try:
            needed.update(_datafile_names(path.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, OSError):
            continue

    return needed


def data_producers(root: Path, needed: set[str]) -> set[str]:
    """Scripts that *write* a file something live depends on.

    A script can be invoked by nothing and still be load-bearing:

    * nothing calls ``consolidate_nsga_experiments.py``, yet it is the only thing
      that writes ``data/processed/nsga_experiments.csv``, which the accepted PPSN
      paper lists in ``ASSET_INPUTS``;
    * nothing calls ``sensitivity_analysis.py``, yet it writes
      ``results/sensitivity_analysis_igd.csv``, which the test suite reads through
      a live script.

    In both cases the file survives only because it happens to be committed. Move
    the producer and the input silently becomes unregenerable — worse than a
    missing file, because nothing fails until someone needs to rebuild.

    Merely *mentioning* a filename is not enough, or every consumer would count as
    a producer; the name has to appear on a line that also looks like a write.
    """
    if not needed:
        return set()

    producers: set[str] = set()
    for path in (root / ANALYSIS_REL).glob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            names = _datafile_names(line)
            if names and _WRITE_HINT.search(line) and any(n in needed for n in names):
                producers.add(path.stem)
                break
    return producers


def classify(root: Path) -> dict[str, list[str]]:
    analysis_dir = root / ANALYSIS_REL
    stems = sorted(p.stem for p in analysis_dir.glob("*.py"))

    haystack = referencing_text(root)
    guarded = guarded_stems(root)

    # Seed: named by a build file, a launcher or a doc.
    live = {stem for stem in stems if re.search(rf"\b{re.escape(stem)}\b", haystack)}

    # Seed: imported by the test suite.
    for test_file in (root / "tests" / "python").glob("*.py"):
        live |= imported_names(test_file) & set(stems)

    live |= PROTECTED & set(stems)
    live |= guarded & set(stems)

    def close_over_imports() -> None:
        changed = True
        while changed:
            changed = False
            for stem in sorted(live):
                path = analysis_dir / f"{stem}.py"
                if not path.exists():
                    continue
                for name in imported_names(path) & set(stems):
                    if name not in live:
                        live.add(name)
                        changed = True

    # Two passes. The first settles which scripts are reachable; only then is it
    # possible to ask what data those scripts depend on, and so which otherwise
    # unreachable scripts produce it.
    close_over_imports()
    producers = data_producers(root, needed_datafiles(root, live)) & set(stems)
    live |= producers
    close_over_imports()

    return {
        "live": sorted(live),
        "candidates": sorted(set(stems) - live),
        "guarded": sorted(guarded & set(stems)),
        "data_producers": sorted(producers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    result = classify(root)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    total = len(result["live"]) + len(result["candidates"])
    print(
        f"{ANALYSIS_REL}: {total} scripts — {len(result['live'])} live, "
        f"{len(result['candidates'])} orphan candidate(s)\n"
    )
    print("Orphan candidates:")
    for stem in result["candidates"]:
        print(f"  {stem}.py")
    print(
        f"\nGuarded by the release evidence ({len(result['guarded'])}): "
        f"{', '.join(result['guarded']) or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
