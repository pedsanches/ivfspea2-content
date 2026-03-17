from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

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
