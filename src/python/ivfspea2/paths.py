"""Project-root resolution and the canonical directory layout.

Before this module, roughly 93 sites resolved the project root, in six mutually
incompatible idioms:

    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
    BASE_DIR = "/home/pedro/desenvolvimento/ivfspea2/..."      # and 47 like it

Every ``parents[3]`` variant silently breaks the moment a script moves one level
in the tree, and the absolute ones were already broken on any machine but the one
they were written on.

Usage::

    from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, ensure_dir

    frame.to_csv(DATA_PROCESSED / "hosts_paper.csv", index=False)
"""

from __future__ import annotations

import os
from pathlib import Path

# Both must be present: `Makefile` alone also matches paper/ and thesis/masters/.
_ROOT_MARKERS = ("Makefile", "pyproject.toml")

_ENV_OVERRIDE = "IVFSPEA2_ROOT"


def find_root(start: Path | None = None) -> Path:
    """Locate the project root.

    Resolution order:

    1. ``$IVFSPEA2_ROOT``, for callers that run from outside the tree.
    2. Walk upward looking for the marker files. This is what makes the module
       work regardless of how deep the caller sits.
    3. ``parents[3]`` relative to this file, matching the historical assumption.

    Deliberately does **not** test ``.git``: inside a git worktree ``.git`` is a
    file rather than a directory, so the usual ``(p / ".git").is_dir()`` check
    fails exactly where the repository is most often edited.
    """
    override = os.environ.get(_ENV_OVERRIDE)
    if override:
        return Path(override).expanduser().resolve()

    here = (start or Path(__file__)).resolve()
    for candidate in (here, *here.parents):
        if all((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate

    return Path(__file__).resolve().parents[3]


PROJECT_ROOT: Path = find_root()

DATA: Path = PROJECT_ROOT / "data"
DATA_RAW: Path = DATA / "raw"
DATA_PROCESSED: Path = DATA / "processed"

RESULTS: Path = PROJECT_ROOT / "results"
RESULTS_TABLES: Path = RESULTS / "tables"
RESULTS_FIGURES: Path = RESULTS / "figures"

CONFIG: Path = PROJECT_ROOT / "config"
PAPER: Path = PROJECT_ROOT / "paper"
ARTIFACT: Path = PROJECT_ROOT / "artifact"
DOCS: Path = PROJECT_ROOT / "docs"

PLATEMO: Path = PROJECT_ROOT / "src" / "matlab" / "lib" / "PlatEMO"


def paper_figures(slug: str) -> Path:
    """Figure directory for one manuscript, e.g. ``paper_figures("ppsn2026")``."""
    return PAPER / slug / "figures"


def platemo_data() -> Path:
    """PlatEMO's ``.mat`` output directory. Gitignored; may not exist."""
    return PLATEMO / "Data"


def ensure_dir(path: Path) -> Path:
    """Create ``path`` (and parents) if absent and return it, for inline use."""
    path.mkdir(parents=True, exist_ok=True)
    return path


__all__ = [
    "ARTIFACT",
    "CONFIG",
    "DATA",
    "DATA_PROCESSED",
    "DATA_RAW",
    "DOCS",
    "PAPER",
    "PLATEMO",
    "PROJECT_ROOT",
    "RESULTS",
    "RESULTS_FIGURES",
    "RESULTS_TABLES",
    "ensure_dir",
    "find_root",
    "paper_figures",
    "platemo_data",
]
