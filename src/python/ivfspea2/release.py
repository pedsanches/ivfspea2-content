"""Integrity checks for the release manifest and its checksum file.

The manifest at ``results/submission_release_manifest.csv`` is the machine-readable
inventory a reader uses to locate every artifact a claim rests on. It is only
worth anything if every row resolves, so this module turns "every distributed
artifact exists and hashes correctly" into a check that can fail a build.

Availability model
------------------

Not every row can be a file in the working tree, and pretending otherwise is what
let 23 of 52 rows rot unnoticed. Each row declares an ``availability`` that fixes
which invariant applies to it:

``in_repo``
    Path exists, is tracked by git, and matches its recorded ``sha256``.
``build_output``
    Path is generated and gitignored. ``producer`` must name the command that
    rebuilds it. Never checksummed — the bytes depend on the local toolchain.
``archived_offline``
    The artifact is not distributed. ``artifact_path`` is empty and
    ``archived_path`` records where it used to live, so the trail survives.
``deposit_only``
    Lives under ``artifact/`` as part of a frozen Zenodo deposit. Covered by the
    DOI recorded in ``notes``; the bytes are immutable by policy.

A manifest with no ``availability`` column is read as all-``in_repo``, which is
what produces the pre-migration baseline.
"""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

MANIFEST_RELPATH = Path("results/submission_release_manifest.csv")
CHECKSUMS_RELPATH = Path("results/submission_release_checksums.sha256")

IN_REPO = "in_repo"
BUILD_OUTPUT = "build_output"
ARCHIVED_OFFLINE = "archived_offline"
DEPOSIT_ONLY = "deposit_only"

AVAILABILITY_VALUES = frozenset({IN_REPO, BUILD_OUTPUT, ARCHIVED_OFFLINE, DEPOSIT_ONLY})

_ROOT_MARKERS = ("Makefile", "results")


@dataclass(frozen=True)
class Problem:
    """One integrity violation, addressed to whoever has to fix it."""

    kind: str
    subject: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.subject}\n    {self.detail}"


def find_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` to the directory holding the project markers.

    Deliberately does not look for ``.git``: in a git worktree ``.git`` is a file,
    not a directory, and a naive ``is_dir()`` check fails there.
    """
    here = (start or Path(__file__)).resolve()
    for candidate in (here, *here.parents):
        if all((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate
    raise RuntimeError(
        f"could not locate the project root above {here} (looked for {' + '.join(_ROOT_MARKERS)})"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(root: Path) -> list[dict[str, str]]:
    with (root / MANIFEST_RELPATH).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def manifest_fieldnames(root: Path) -> list[str]:
    with (root / MANIFEST_RELPATH).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle).fieldnames or [])


def tracked_files(root: Path) -> set[str]:
    """Every path git tracks, as repo-relative POSIX strings."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.splitlines())


def _availability(row: dict[str, str]) -> str:
    return (row.get("availability") or "").strip() or IN_REPO


def verify_manifest(root: Path) -> list[Problem]:
    """Check every manifest row against the invariant its availability declares."""
    problems: list[Problem] = []
    rows = load_manifest(root)
    tracked = tracked_files(root)

    for index, row in enumerate(rows, start=2):  # row 1 is the header
        availability = _availability(row)
        path_value = (row.get("artifact_path") or "").strip()
        where = f"{MANIFEST_RELPATH}:{index}"

        if availability not in AVAILABILITY_VALUES:
            problems.append(
                Problem(
                    "unknown-availability",
                    where,
                    f"{availability!r} is not one of {sorted(AVAILABILITY_VALUES)}",
                )
            )
            continue

        if availability == ARCHIVED_OFFLINE:
            if path_value:
                problems.append(
                    Problem(
                        "archived-row-has-path",
                        where,
                        f"archived_offline rows must leave artifact_path empty, "
                        f"got {path_value!r}; use archived_path instead",
                    )
                )
            elif not (row.get("archived_path") or "").strip():
                problems.append(
                    Problem(
                        "archived-row-has-no-origin",
                        where,
                        "archived_offline rows must record archived_path",
                    )
                )
            continue

        if not path_value:
            problems.append(
                Problem("empty-path", where, f"{availability} rows require artifact_path")
            )
            continue

        target = root / path_value

        if not target.exists():
            problems.append(
                Problem(
                    "missing-artifact",
                    path_value,
                    f"declared {availability} at {where}, but no such file",
                )
            )
            continue

        if availability == BUILD_OUTPUT:
            if not (row.get("producer") or "").strip():
                problems.append(
                    Problem(
                        "build-output-has-no-producer",
                        path_value,
                        "build_output rows must name a runnable producer command",
                    )
                )
            continue

        if availability == DEPOSIT_ONLY:
            if not path_value.startswith("artifact/"):
                problems.append(
                    Problem(
                        "deposit-row-outside-artifact",
                        path_value,
                        "deposit_only rows must live under artifact/",
                    )
                )
            continue

        # in_repo
        if path_value not in tracked:
            problems.append(
                Problem(
                    "untracked-artifact",
                    path_value,
                    "declared in_repo but git does not track it; a clone would not receive it",
                )
            )
            continue

        expected = (row.get("sha256") or "").strip()
        if expected:
            actual = sha256_file(target)
            if actual != expected:
                problems.append(
                    Problem(
                        "hash-mismatch",
                        path_value,
                        f"manifest says {expected[:16]}…, file is {actual[:16]}…",
                    )
                )

    return problems


IDENTITY_RELPATH = Path("docs/RELEASE_IDENTITY.md")

_ZENODO_DOI = re.compile(r"10\.5281/zenodo\.(\d+)")

# Binary and vendored trees are not prose and are not where a DOI is authored.
_DOI_SCAN_SKIP_PREFIXES = (
    "src/matlab/lib/PlatEMO/",
    "artifact/ppsn2026-ivf-hosts-rev1/",
    "legacy/",
)
_DOI_SCAN_SUFFIXES = (".md", ".tex", ".bib", ".cff", ".json", ".py", ".txt", ".yml", ".yaml")


def declared_dois(root: Path) -> set[str]:
    """Zenodo record IDs listed in docs/RELEASE_IDENTITY.md."""
    path = root / IDENTITY_RELPATH
    if not path.exists():
        return set()
    return set(_ZENODO_DOI.findall(path.read_text(encoding="utf-8")))


def verify_dois(root: Path) -> list[Problem]:
    """Fail on any Zenodo DOI that RELEASE_IDENTITY.md does not account for.

    Four DOIs were circulating with no stated relationship, one of them long
    superseded and one — the concept DOI, the one a citation should normally use —
    absent entirely. Nothing detected that, because nothing was looking. This is
    the thing that looks.
    """
    declared = declared_dois(root)
    if not declared:
        return [
            Problem(
                "no-declared-dois",
                str(IDENTITY_RELPATH),
                "missing or lists no Zenodo DOI; every DOI in the tree is unaccounted for",
            )
        ]

    problems: list[Problem] = []
    for name in sorted(tracked_files(root)):
        if name.startswith(_DOI_SCAN_SKIP_PREFIXES) or not name.endswith(_DOI_SCAN_SUFFIXES):
            continue
        target = root / name
        if not target.exists():
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for record_id in sorted(set(_ZENODO_DOI.findall(text))):
            if record_id not in declared:
                problems.append(
                    Problem(
                        "undeclared-doi",
                        name,
                        f"cites 10.5281/zenodo.{record_id}, which {IDENTITY_RELPATH} does not list",
                    )
                )
    return problems


def parse_checksums(root: Path) -> list[tuple[str, str]]:
    """Read the sha256 file as ``(digest, relative_path)`` pairs."""
    entries: list[tuple[str, str]] = []
    path = root / CHECKSUMS_RELPATH
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, name = line.partition("  ")
        if not name:
            digest, _, name = line.partition(" ")
        entries.append((digest.strip(), name.strip()))
    return entries


def verify_checksums(root: Path) -> list[Problem]:
    problems: list[Problem] = []
    for digest, name in parse_checksums(root):
        target = root / name
        if not target.exists():
            problems.append(
                Problem("checksum-target-missing", name, "listed in the checksum file but absent")
            )
            continue
        actual = sha256_file(target)
        if actual != digest:
            problems.append(
                Problem(
                    "checksum-mismatch",
                    name,
                    f"recorded {digest[:16]}…, file is {actual[:16]}…",
                )
            )
    return problems


def write_checksums(root: Path) -> list[str]:
    """Refresh every recorded hash, in the only order that can be self-consistent.

    Two passes, and the order is the whole point:

    1. Recompute the ``sha256`` column for every ``in_repo`` row and rewrite the
       manifest. The manifest and the checksum file must not be independent
       records of the same fact — that is precisely how the previous pair drifted
       apart, leaving the manifest's own recorded hash wrong.
    2. Hash the *now-final* manifest and emit the checksum file covering the
       ``in_repo`` rows plus the manifest itself.

    Hashing the manifest before it is final is the bug this ordering removes
    structurally, rather than by remembering to redo it.
    """
    manifest_path = root / MANIFEST_RELPATH
    fieldnames = manifest_fieldnames(root)
    rows = load_manifest(root)

    # Pass 1 — the manifest becomes the single source of truth for hashes.
    for row in rows:
        if _availability(row) != IN_REPO:
            continue
        name = (row.get("artifact_path") or "").strip()
        if not name:
            continue
        target = root / name
        if target.exists():
            row["sha256"] = sha256_file(target)

    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Pass 2 — the checksum file mirrors the finalized manifest.
    lines = [
        f"{row['sha256']}  {row['artifact_path'].strip()}"
        for row in rows
        if _availability(row) == IN_REPO and (row.get("sha256") or "").strip()
    ]
    lines.append(f"{sha256_file(manifest_path)}  {MANIFEST_RELPATH.as_posix()}")
    lines.sort(key=lambda line: line.split("  ", 1)[1])

    (root / CHECKSUMS_RELPATH).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines
