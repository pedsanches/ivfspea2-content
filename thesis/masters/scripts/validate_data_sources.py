#!/usr/bin/env python3
"""Validate the master's thesis evidence-source manifest."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


THESIS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = THESIS_DIR / "data-sources.toml"
PATH_FIELDS = ("manuscripts", "datasets", "scripts", "artifacts")
REQUIRED_FIELDS = {
    "id",
    "evidence_family",
    "manuscripts",
    "role",
    "algorithm_version",
    "cohort",
    "metrics",
    "datasets",
    "scripts",
    "artifacts",
    "notes",
    "raw_status",
    "overlaps",
    "known_gaps",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_relative_path(source_id: str, field: str, value: str) -> None:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        fail(f"{source_id}.{field} must be repository-relative: {value}")
    if not (REPO_ROOT / candidate).exists():
        fail(f"{source_id}.{field} does not exist: {value}")


def main() -> None:
    if not MANIFEST.is_file():
        fail(f"manifest not found: {MANIFEST}")

    with MANIFEST.open("rb") as stream:
        manifest = tomllib.load(stream)

    if manifest.get("schema_version") != 1:
        fail("unsupported or missing schema_version")

    sources = manifest.get("source")
    if not isinstance(sources, list) or not sources:
        fail("manifest must declare at least one [[source]]")

    seen_ids: set[str] = set()
    evidence_families: set[str] = set()
    checked_paths = 0

    for source in sources:
        missing = REQUIRED_FIELDS - source.keys()
        if missing:
            fail(f"source is missing fields: {sorted(missing)}")

        source_id = source["id"]
        if source_id in seen_ids:
            fail(f"duplicate source id: {source_id}")
        seen_ids.add(source_id)
        evidence_families.add(source["evidence_family"])

        metrics = {str(metric).upper() for metric in source["metrics"]}
        if not {"IGD", "HV"}.issubset(metrics):
            fail(f"{source_id} must declare both IGD and HV")

        if not source["manuscripts"]:
            fail(f"{source_id} must reference at least one manuscript")

        for field in PATH_FIELDS:
            values = source[field]
            if not isinstance(values, list):
                fail(f"{source_id}.{field} must be a list")
            for value in values:
                validate_relative_path(source_id, field, value)
                checked_paths += 1

    print(
        f"OK: {len(sources)} evidence sources across "
        f"{len(evidence_families)} evidence families and "
        f"{checked_paths} repository paths validated."
    )


if __name__ == "__main__":
    main()
