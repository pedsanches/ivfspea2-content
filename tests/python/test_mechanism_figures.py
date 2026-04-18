import os
import sys

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "python", "analysis"))


def test_shared_colors_dict_has_expected_groups():
    from ivf_trace_common import COLORS

    required = {
        "reference_pf",
        "population_before",
        "population_after",
        "mother",
        "father",
        "beneficial",
        "harmful",
        "neutral",
    }
    assert required.issubset(set(COLORS.keys()))


def test_shared_axis_limits_3d_returns_six_floats():
    from ivf_trace_common import compute_axis_limits_3d

    populations = pd.DataFrame(
        {
            "point_group": ["reference_pf"] * 3,
            "f1": [0.0, 0.5, 1.0],
            "f2": [0.0, 0.5, 1.0],
            "f3": [0.0, 0.5, 1.0],
        }
    )
    pairs = pd.DataFrame(
        {
            "mother_f1": [0.2], "mother_f2": [0.3], "mother_f3": [0.4],
            "father_f1": [0.5], "father_f2": [0.6], "father_f3": [0.7],
            "child_f1":  [0.1], "child_f2":  [0.2], "child_f3":  [0.3],
        }
    )
    limits = compute_axis_limits_3d(populations, pairs, "f1", "f2", "f3")
    assert len(limits) == 6
    assert all(isinstance(v, float) for v in limits)


def test_select_progression_cycles_picks_early_mid_late():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [2, 10, 50, 100, 200, 398],
            "ivf_cycle":  [1, 1, 1, 1, 1, 1],
            "collective_improved": [True, True, True, True, True, True],
        }
    )
    picks = select_progression_cycles(cycles)
    assert picks["early"]["generation"] == 2
    assert picks["late"]["generation"] == 398
    assert picks["mid"]["generation"] == 50


def test_select_progression_cycles_filters_non_improving():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [1, 2, 3, 4, 5, 6],
            "ivf_cycle":  [1, 1, 1, 2, 1, 1],
            "collective_improved": [False, True, True, True, True, False],
        }
    )
    picks = select_progression_cycles(cycles)
    assert picks["early"]["generation"] == 2
    assert picks["late"]["generation"] == 5
    # Generation 4 has ivf_cycle=2, so it must not appear in any returned row.
    returned_gens = {picks[k]["generation"] for k in ("early", "mid", "late")}
    assert 4 not in returned_gens
    # Generation 1 and 6 are not collective_improved, must also be excluded.
    assert 1 not in returned_gens
    assert 6 not in returned_gens


def test_select_progression_cycles_short_run_fallback():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [5, 10],
            "ivf_cycle":  [1, 1],
            "collective_improved": [True, True],
        }
    )
    with pytest.warns(UserWarning, match="[Ss]hort"):
        picks = select_progression_cycles(cycles)
    assert picks["early"]["generation"] == 5
    assert picks["late"]["generation"] == 10
    # Explicit fallback: mid takes the second active cycle's generation.
    assert picks["mid"]["generation"] == 10


def test_select_progression_cycles_single_active_cycle_no_fallback():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame({
        "generation": [7],
        "ivf_cycle": [1],
        "collective_improved": [True],
    })
    with pytest.warns(UserWarning, match="no fallback possible"):
        picks = select_progression_cycles(cycles)
    assert (
        picks["early"]["generation"]
        == picks["mid"]["generation"]
        == picks["late"]["generation"]
        == 7
    )


def test_select_progression_cycles_raises_when_no_active_cycle():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [1, 2, 3],
            "ivf_cycle":  [1, 1, 1],
            "collective_improved": [False, False, False],
        }
    )
    with pytest.raises(ValueError, match="(?i)no active cycle"):
        select_progression_cycles(cycles)


def test_label_child_outcome_matches_delta_to_pf():
    from extract_mechanism_cycles import label_child_outcome

    frame = pd.DataFrame(
        {"delta_to_pf": [-0.5, -1e-13, 0.0, 1e-13, 0.5]}
    )
    labels = label_child_outcome(frame)
    assert labels == ["beneficial", "neutral", "neutral", "neutral", "harmful"]
