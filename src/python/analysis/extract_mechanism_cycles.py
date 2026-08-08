#!/usr/bin/env python3
from __future__ import annotations

import warnings

import pandas as pd


def select_progression_cycles(cycles: pd.DataFrame) -> dict[str, pd.Series]:
    """Pick early / mid / late IVF cycles from a single run.

    Criteria (see spec 2026-04-13-ivf-mechanism-figures-design.md):
      * early = smallest generation with collective_improved and ivf_cycle == 1
      * late  = largest generation with collective_improved and ivf_cycle == 1
      * mid   = cycle with generation closest to the median of active generations

    Short-run behavior: when the median-closest mid collapses onto early or late
    (few active cycles), fall back to the second active cycle and emit a
    UserWarning. If fewer than 2 active cycles exist, warn and leave mid = early.
    """
    required = {"generation", "ivf_cycle", "collective_improved"}
    missing = required - set(cycles.columns)
    if missing:
        raise ValueError(f"cycles DataFrame missing columns: {sorted(missing)}")

    active = cycles[
        cycles["collective_improved"] & (cycles["ivf_cycle"] == 1)
    ].sort_values("generation", kind="mergesort").reset_index(drop=True)

    if active.empty:
        raise ValueError("No active cycle found: no row has collective_improved=True.")

    if active["generation"].isna().all():
        raise ValueError("all generation values are NaN in active cycles")

    early = active.iloc[0]
    late = active.iloc[-1]

    median_gen = float(active["generation"].median())
    mid_idx = (active["generation"] - median_gen).abs().idxmin()
    mid = active.loc[mid_idx]

    if mid["generation"] == early["generation"] or mid["generation"] == late["generation"]:
        n_active = len(active)
        if n_active >= 2:
            warnings.warn(
                f"Short run with only {n_active} active cycles; mid collapsed to "
                f"early/late, falling back to second active cycle.",
                UserWarning,
                stacklevel=2,
            )
            mid = active.iloc[1]
        else:
            warnings.warn(
                f"Short run with only {n_active} active cycle; mid collapsed to "
                f"early/late, no fallback possible.",
                UserWarning,
                stacklevel=2,
            )

    return {"early": early, "mid": mid, "late": late}


TOL = 1e-12


def label_child_outcome(frame: pd.DataFrame) -> list[str]:
    """Map delta_to_pf to beneficial / harmful / neutral, matching extract_ivf_trace_cases."""
    labels: list[str] = []
    for delta in frame["delta_to_pf"].to_list():
        if delta < -TOL:
            labels.append("beneficial")
        elif delta > TOL:
            labels.append("harmful")
        else:
            labels.append("neutral")
    return labels
