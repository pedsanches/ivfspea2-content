"""Shared library code for the IVF-SPEA2 analysis and release pipeline.

The modules here are the supported entry points for anything needing project
paths, figure styling, deterministic IO, cohort filtering or release
verification:

============  =========================================================
``paths``     Project root and the canonical directory layout
``figstyle``  Matplotlib backend and one set of publication rcParams
``figio``     ``save_figure`` — deterministic, byte-stable figure writes
``cohorts``   Canonical run-cohort filtering for submission analyses
``release``   Manifest, checksum and DOI integrity checks
============  =========================================================

The ~90 scripts under ``src/python/analysis/`` predate this package. They keep
working unchanged — ``cohort_filter`` and ``figure_io`` remain importable as
deprecation shims — and are migrated as they are touched, not in a sweep.

Submodules are imported on demand rather than eagerly: ``figstyle`` selects a
matplotlib backend as an import side effect, which should happen only when a
caller actually asks for it.
"""

__all__ = ["cohorts", "figio", "figstyle", "paths", "release"]
