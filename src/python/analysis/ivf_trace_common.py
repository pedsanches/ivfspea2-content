from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def normalize_m_value(value: object) -> int:
    text = str(value).strip()
    if text.startswith("M"):
        text = text[1:]
    return int(text)


def final_scalar(value: object) -> float | None:
    if value is None:
        return None
    arr = np.asarray(value)
    if arr.size == 0:
        return None
    scalar = float(arr.reshape(-1)[-1])
    if not np.isfinite(scalar):
        return None
    return scalar


def scalar_bool(value: object) -> bool:
    arr = np.asarray(value)
    if arr.size == 0:
        return False
    return bool(arr.reshape(-1)[0])


def a12_lower_better(x: Sequence[float], y: Sequence[float]) -> float:
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    wins = 0.0
    for xv in x_arr:
        wins += np.sum(xv < y_arr)
        wins += 0.5 * np.sum(xv == y_arr)
    return float(wins / (len(x_arr) * len(y_arr)))


def a12_higher_better(x: Sequence[float], y: Sequence[float]) -> float:
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    wins = 0.0
    for xv in x_arr:
        wins += np.sum(xv > y_arr)
        wins += 0.5 * np.sum(xv == y_arr)
    return float(wins / (len(x_arr) * len(y_arr)))


def matrix_to_numpy(value: object) -> np.ndarray:
    if value is None:
        return np.empty((0, 0), dtype=float)
    arr = np.asarray(value, dtype=float)
    if arr.size == 0:
        return np.empty((0, 0), dtype=float)
    if arr.ndim == 1:
        return arr.reshape(1, -1)
    return arr


def vector_to_numpy(value: object, dtype: type = float) -> np.ndarray:
    if value is None:
        return np.asarray([], dtype=dtype)
    arr = np.asarray(value)
    if arr.size == 0:
        return np.asarray([], dtype=dtype)
    return arr.reshape(-1).astype(dtype)


def coerce_struct_list(value: object) -> list[dict]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        out: list[dict] = []
        for item in value:
            out.extend(coerce_struct_list(item))
        return out
    if isinstance(value, tuple):
        out = []
        for item in value:
            out.extend(coerce_struct_list(item))
        return out
    if isinstance(value, np.ndarray):
        if value.size == 0:
            return []
        return coerce_struct_list(value.tolist())
    return []


def normalize_points(
    points: np.ndarray, lower: np.ndarray, upper: np.ndarray
) -> np.ndarray:
    denom = upper - lower
    denom[denom == 0] = 1.0
    return (points - lower) / denom


def distance_to_reference_pf(
    points: np.ndarray, reference_pf: np.ndarray
) -> np.ndarray:
    if points.size == 0:
        return np.asarray([], dtype=float)
    lower = np.min(reference_pf, axis=0)
    upper = np.max(reference_pf, axis=0)
    points_norm = normalize_points(points, lower, upper)
    pf_norm = normalize_points(reference_pf, lower, upper)
    diff = points_norm[:, None, :] - pf_norm[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=2)).min(axis=1)


def objective_columns(m: int) -> list[str]:
    return [f"f{i}" for i in range(1, m + 1)]


def pick_nearest_row(
    df: pd.DataFrame,
    value_col: str,
    target: float,
    tie_breakers: Iterable[str] = (),
) -> pd.Series:
    ranked = df.copy()
    ranked["_distance_to_target"] = (ranked[value_col] - target).abs()
    sort_cols = ["_distance_to_target", *tie_breakers]
    ranked = ranked.sort_values(sort_cols, kind="mergesort")
    return ranked.iloc[0]


def quantile_target(series: pd.Series, q: float) -> float:
    return float(series.quantile(q))


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 3-D scatter helpers (shared across plot scripts)
# ---------------------------------------------------------------------------

COLORS = {
    "reference_pf": "#D0D0D0",
    "population_before": "#C7CBD1",
    "population_after": "#6D6D6D",
    "mother": "#2166AC",
    "father": "#F18F01",
    "beneficial": "#1A9850",
    "harmful": "#D73027",
    "neutral": "#A67C52",
}


def compute_axis_limits_3d(
    populations: pd.DataFrame,
    pairs: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    pct_lo: float = 1.0,
    pct_hi: float = 99.0,
    margin: float = 0.08,
) -> tuple[float, float, float, float, float, float]:
    """Compute 3-axis limits based on data percentiles."""
    all_vals: dict[str, list[np.ndarray]] = {x: [], y: [], z: []}

    # Include reference PF for axis context
    ref = populations[populations["point_group"] == "reference_pf"]
    if not ref.empty:
        for col in (x, y, z):
            all_vals[col].append(ref[col].values)

    for prefix in ("mother", "father", "child"):
        for col in (x, y, z):
            pc = f"{prefix}_{col}"
            if pc in pairs.columns:
                vals = pairs[pc].dropna().values
                if vals.size > 0:
                    all_vals[col].append(vals)

    limits: list[float] = []
    for col in (x, y, z):
        if not all_vals[col]:
            limits.extend([0.0, 1.0])
            continue
        arr = np.concatenate(all_vals[col])
        lo, hi = float(np.percentile(arr, pct_lo)), float(np.percentile(arr, pct_hi))
        d = max(hi - lo, 1e-6) * margin
        limits.extend([lo - d, hi + d])

    return tuple(limits)  # type: ignore[return-value]


def scatter_group_3d(
    ax: plt.Axes,
    frame: pd.DataFrame,
    point_group: str,
    x: str,
    y: str,
    z: str,
    color: str,
    size: float,
    alpha: float,
    edgecolor: str | None = None,
    linewidth: float = 0.0,
) -> None:
    """Scatter points belonging to a named point_group from a populations frame."""
    group = frame[frame["point_group"] == point_group]
    if group.empty:
        return
    ax.scatter(
        group[x], group[y], group[z],
        s=size, c=color, alpha=alpha,
        edgecolors=edgecolor if edgecolor is not None else "none",
        linewidths=linewidth,
        depthshade=True,
    )


def scatter_parent_points_3d(
    ax: plt.Axes,
    frame: pd.DataFrame,
    prefix: str,
    x: str,
    y: str,
    z: str,
    marker: str,
    color: str,
    size: float,
) -> None:
    """Scatter unique parent (mother or father) points from a pairs frame."""
    cols = [f"{prefix}_{x}", f"{prefix}_{y}", f"{prefix}_{z}"]
    unique_points = frame[cols].drop_duplicates()
    if unique_points.empty:
        return
    ax.scatter(
        unique_points[cols[0]], unique_points[cols[1]], unique_points[cols[2]],
        s=size, c=color, marker=marker,
        alpha=0.9, edgecolors="#111111", linewidths=0.25,
        depthshade=True,
    )


def scatter_child_points_3d(
    ax: plt.Axes,
    frame: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    color: str,
    size: float,
) -> None:
    """Scatter child/offspring points from a pairs frame."""
    if frame.empty:
        return
    ax.scatter(
        frame[f"child_{x}"], frame[f"child_{y}"], frame[f"child_{z}"],
        s=size, c=color, alpha=0.85, edgecolors="none", depthshade=True,
    )
