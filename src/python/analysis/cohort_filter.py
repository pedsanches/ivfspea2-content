#!/usr/bin/env python3
"""
Canonical run-cohort filtering helpers for synthetic submission analyses.

The consolidated CSV currently contains multiple historical tracks for
IVF/SPEA2. For submission-grade synthetic analysis we keep only:

  - IVF/SPEA2: run IDs 3001..3060 (SUB20260228_V2)
  - Baselines: run IDs 1..60

Engineering instances (RWMOP*) are excluded from this filter because they are
processed by a dedicated pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

IVF_ALGORITHM = "IVFSPEA2"

BASELINE_RUN_MIN = 1
BASELINE_RUN_MAX = 60
IVF_RUN_MIN = 3001
IVF_RUN_MAX = 3060

ENGINEERING_PREFIX = "RWMOP"


@dataclass(frozen=True)
class CohortWindow:
    run_min: int
    run_max: int


BASELINE_WINDOW = CohortWindow(BASELINE_RUN_MIN, BASELINE_RUN_MAX)
IVF_WINDOW = CohortWindow(IVF_RUN_MIN, IVF_RUN_MAX)


def _require_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _run_series(df: pd.DataFrame) -> pd.Series:
    runs = pd.to_numeric(df["Run"], errors="coerce")
    if runs.isna().any():
        bad = int(runs.isna().sum())
        raise ValueError(f"Column 'Run' contains {bad} non-numeric rows")
    return runs.astype(int)


def is_engineering_problem(problem: str) -> bool:
    return str(problem).startswith(ENGINEERING_PREFIX)


def filter_submission_synthetic_cohort(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return synthetic-only rows under canonical submission run windows.

    Rules:
      1) Drop engineering rows (RWMOP*)
      2) Keep IVFSPEA2 rows only in [3001, 3060]
      3) Keep non-IVFSPEA2 rows only in [1, 60]
    """
    _require_columns(df, ["Algoritmo", "Problema", "Run"])
    out = df.copy()
    runs = _run_series(out)

    is_eng = out["Problema"].astype(str).str.startswith(ENGINEERING_PREFIX)
    is_ivf = out["Algoritmo"].astype(str) == IVF_ALGORITHM

    keep_ivf = is_ivf & runs.between(IVF_RUN_MIN, IVF_RUN_MAX)
    keep_base = (~is_ivf) & runs.between(BASELINE_RUN_MIN, BASELINE_RUN_MAX)

    keep = (~is_eng) & (keep_ivf | keep_base)
    return out.loc[keep].copy()


def build_group_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-(algorithm, problem, M) run coverage summary."""
    _require_columns(df, ["Algoritmo", "Problema", "M", "Run"])
    runs = _run_series(df)
    tmp = df.copy()
    tmp["Run"] = runs
    tmp["is_engineering"] = (
        tmp["Problema"].astype(str).str.startswith(ENGINEERING_PREFIX)
    )

    grouped = tmp.groupby(
        ["Algoritmo", "Problema", "M", "is_engineering"], as_index=False
    ).agg(
        n_rows=("Run", "size"),
        n_unique_runs=("Run", "nunique"),
        run_min=("Run", "min"),
        run_max=("Run", "max"),
    )

    def classify(row: pd.Series) -> tuple[str, str]:
        algo = str(row["Algoritmo"])
        eng = bool(row["is_engineering"])
        run_min = int(row["run_min"])
        run_max = int(row["run_max"])
        n_runs = int(row["n_unique_runs"])

        if eng:
            return "engineering_external", "external"

        if algo == IVF_ALGORITHM:
            expected = f"{IVF_RUN_MIN}-{IVF_RUN_MAX}"
            ok = n_runs == 60 and run_min >= IVF_RUN_MIN and run_max <= IVF_RUN_MAX
            return expected, "ok" if ok else "mismatch"

        expected = f"{BASELINE_RUN_MIN}-{BASELINE_RUN_MAX}"
        ok = (
            n_runs == 60 and run_min >= BASELINE_RUN_MIN and run_max <= BASELINE_RUN_MAX
        )
        return expected, "ok" if ok else "mismatch"

    expected_status = grouped.apply(classify, axis=1, result_type="expand")
    grouped["expected_window"] = expected_status[0]
    grouped["status"] = expected_status[1]
    return grouped
