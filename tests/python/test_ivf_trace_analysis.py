import os
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "python", "analysis"))

from ivf_trace_common import (  # noqa: E402
    a12_higher_better,
    a12_lower_better,
    distance_to_reference_pf,
    normalize_m_value,
    pick_nearest_row,
)


def test_a12_lower_better_prefers_smaller_values():
    score = a12_lower_better([1.0, 2.0], [3.0, 4.0])
    assert score == 1.0


def test_a12_higher_better_prefers_larger_values():
    score = a12_higher_better([4.0, 5.0], [1.0, 2.0])
    assert score == 1.0


def test_distance_to_reference_pf_is_zero_on_reference_points():
    pf = np.array([[0.0, 1.0], [1.0, 0.0]])
    pts = np.array([[0.0, 1.0], [1.0, 0.0]])
    distances = distance_to_reference_pf(pts, pf)
    assert np.allclose(distances, 0.0)


def test_normalize_m_value_accepts_string_and_prefixed_forms():
    assert normalize_m_value("M3") == 3
    assert normalize_m_value("2") == 2


def test_pick_nearest_row_uses_target_distance_then_tie_breakers():
    frame = pd.DataFrame(
        {
            "run_id": [10, 11, 12],
            "final_igd": [0.10, 0.12, 0.08],
        }
    )
    row = pick_nearest_row(frame, "final_igd", 0.11, tie_breakers=("run_id",))
    assert int(row["run_id"]) == 10
