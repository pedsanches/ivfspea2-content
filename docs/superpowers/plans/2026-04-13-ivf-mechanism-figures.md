# IVF Mechanism Figures — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce three scatter-3D figures under `paper/ppsn2026/figures/` (single-cycle, early/mid/late progression, bad-vs-good contrast) that illustrate the IVF-SPEA2 v2 operator on DTLZ4 M=3, mirroring IVF/NSGA-III Figs. 3 and 5–8.

**Architecture:** Two new Python modules under `src/python/analysis/`: (1) `extract_mechanism_cycles.py` reads two `.mat` files (runs 9005 and 9012 of DTLZ4 M=3), applies early/mid/late/anchor criteria, and emits three CSVs to `results/ivf_trace/`; (2) `plot_mechanism_figures.py` reads those CSVs and renders three PDFs. Reusable 3D scatter helpers are lifted from `plot_ivf_trace_cases.py` into `ivf_trace_common.py` so both scripts share them without duplication.

**Tech Stack:** Python 3.12, `numpy`, `pandas`, `pymatreader`, `matplotlib` (Agg backend), `pytest`. Existing conventions: `PROJECT_ROOT` helper, CSV-first data flow, `plt.rcParams` style block, `ensure_directory()`.

**Spec reference:** `docs/superpowers/specs/2026-04-13-ivf-mechanism-figures-design.md`.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `src/python/analysis/ivf_trace_common.py` | Add shared 3D scatter helpers (`COLORS`, `scatter_group_3d`, `scatter_parent_points_3d`, `scatter_child_points_3d`, `compute_axis_limits_3d`) so both plot scripts import them | **Modify** |
| `src/python/analysis/plot_ivf_trace_cases.py` | Remove the private `_scatter_*_3d` helpers, `_compute_axis_limits_3d` and `COLORS`, importing them from the common module instead | **Modify** |
| `src/python/analysis/extract_mechanism_cycles.py` | New CLI script: read two `.mat` files, select early/mid/late cycles from run 9012 + the contrast cycles (9005 g12 c1, 9012 g398 c1), emit `mechanism_figure_{cycles,populations,pairs}.csv` | **Create** |
| `src/python/analysis/plot_mechanism_figures.py` | New CLI script: read those three CSVs, render 3 PDFs (`fig_ivf_mechanism_{single,progression,contrast}.pdf`) to `paper/ppsn2026/figures/` | **Create** |
| `tests/python/test_mechanism_figures.py` | Unit tests (no matplotlib) for: cycle-selection criteria, short-run fallback, beneficial label consistency, CSV schema | **Create** |
| `paper/Makefile` | Add `mechanism-figures` target that runs both scripts | **Modify** |
| `paper/ppsn2026/main.tex` | Insert three `\begin{figure}` blocks with captions that cross-reference Sampaio et al. 2019 | **Modify** |

**Data sources (read-only):**
- `data/raw/ivf_trace_cases/detailed/bimodal_dtlz4_m3/IVFSPEA2V2TRACE_DTLZ4_M3_D12_9005.mat`
- `data/raw/ivf_trace_cases/detailed/bimodal_dtlz4_m3/IVFSPEA2V2TRACE_DTLZ4_M3_D12_9012.mat`
- `data/raw/ivf_trace_cases/reference_pf/DTLZ4_M3_D12_truePF.csv`

---

## Task 1: Lift 3D scatter helpers into shared module

**Files:**
- Modify: `src/python/analysis/ivf_trace_common.py`
- Modify: `src/python/analysis/plot_ivf_trace_cases.py`
- Test: `tests/python/test_mechanism_figures.py`

**Why first:** Both `plot_ivf_trace_cases.py` and the new `plot_mechanism_figures.py` need identical 3D scatter helpers and the same `COLORS` dict. Lift them now so later tasks can import without duplication.

- [ ] **Step 1: Write the failing test for the shared helpers**

Create `tests/python/test_mechanism_figures.py` with only this test at first:

```python
import os
import sys

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd

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
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: both tests FAIL with `ImportError: cannot import name 'COLORS'` / `'compute_axis_limits_3d'`.

- [ ] **Step 3: Move `COLORS` and helpers into `ivf_trace_common.py`**

Append to `src/python/analysis/ivf_trace_common.py`:

```python
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
    margin: float = 0.05,
) -> tuple[float, float, float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    if not populations.empty:
        xs.extend(populations[x].tolist())
        ys.extend(populations[y].tolist())
        zs.extend(populations[z].tolist())
    for prefix in ("mother", "father", "child"):
        cx, cy, cz = f"{prefix}_{x}", f"{prefix}_{y}", f"{prefix}_{z}"
        if {cx, cy, cz}.issubset(pairs.columns) and not pairs.empty:
            xs.extend(pairs[cx].dropna().tolist())
            ys.extend(pairs[cy].dropna().tolist())
            zs.extend(pairs[cz].dropna().tolist())
    if not xs:
        return (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
    x_lo, x_hi = float(min(xs)), float(max(xs))
    y_lo, y_hi = float(min(ys)), float(max(ys))
    z_lo, z_hi = float(min(zs)), float(max(zs))
    return (
        x_lo - margin, x_hi + margin,
        y_lo - margin, y_hi + margin,
        z_lo - margin, z_hi + margin,
    )


def scatter_group_3d(ax, frame, point_group, x, y, z, color, size, alpha,
                     edgecolor=None, linewidth=0.0):
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


def scatter_parent_points_3d(ax, frame, prefix, x, y, z, marker, color, size):
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


def scatter_child_points_3d(ax, frame, x, y, z, color, size):
    if frame.empty:
        return
    ax.scatter(
        frame[f"child_{x}"], frame[f"child_{y}"], frame[f"child_{z}"],
        s=size, c=color, alpha=0.85, edgecolors="none", depthshade=True,
    )
```

- [ ] **Step 4: Remove duplicates from `plot_ivf_trace_cases.py`**

In `src/python/analysis/plot_ivf_trace_cases.py`:
1. Delete the `COLORS = {...}` block at lines 22–31.
2. Delete the private helpers `_scatter_group_3d`, `_scatter_parent_points_3d`, `_scatter_child_points_3d`, `_compute_axis_limits_3d`.
3. Replace the import block at line 16 with:

```python
from ivf_trace_common import (
    COLORS,
    PROJECT_ROOT,
    compute_axis_limits_3d,
    ensure_directory,
    objective_columns,
    scatter_child_points_3d,
    scatter_group_3d,
    scatter_parent_points_3d,
)
```

4. Rename every call site inside the file: `_scatter_group_3d` → `scatter_group_3d`, `_scatter_parent_points_3d` → `scatter_parent_points_3d`, `_scatter_child_points_3d` → `scatter_child_points_3d`, `_compute_axis_limits_3d` → `compute_axis_limits_3d`.

- [ ] **Step 5: Run the test to verify it passes**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: both tests PASS.

- [ ] **Step 6: Sanity-check that the existing trace plot still imports**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/python -c "import sys; sys.path.insert(0, 'src/python/analysis'); import plot_ivf_trace_cases"
```
Expected: silent exit (no ImportError).

- [ ] **Step 7: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/ivf_trace_common.py src/python/analysis/plot_ivf_trace_cases.py tests/python/test_mechanism_figures.py
git commit -m "Lift 3D scatter helpers into ivf_trace_common"
```

---

## Task 2: Cycle-selection logic and unit tests

**Files:**
- Create: `src/python/analysis/extract_mechanism_cycles.py` (logic only — IO in Task 3)
- Test: `tests/python/test_mechanism_figures.py` (append)

**Why:** The early/mid/late selector is the only non-trivial logic in the pipeline. Tested in isolation before touching `.mat` IO.

- [ ] **Step 1: Append the failing tests for the selector**

Append to `tests/python/test_mechanism_figures.py`:

```python
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
    assert 10 <= picks["mid"]["generation"] <= 200


def test_select_progression_cycles_filters_non_improving():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [1, 2, 3, 4, 5],
            "ivf_cycle":  [1, 1, 1, 1, 1],
            "collective_improved": [False, True, True, True, False],
        }
    )
    picks = select_progression_cycles(cycles)
    assert picks["early"]["generation"] == 2
    assert picks["late"]["generation"] == 4


def test_select_progression_cycles_short_run_fallback():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [5, 10],
            "ivf_cycle":  [1, 1],
            "collective_improved": [True, True],
        }
    )
    picks = select_progression_cycles(cycles)
    assert picks["early"]["generation"] == 5
    assert picks["late"]["generation"] == 10
    assert picks["mid"]["generation"] in (5, 10)


def test_select_progression_cycles_raises_when_no_active_cycle():
    from extract_mechanism_cycles import select_progression_cycles

    cycles = pd.DataFrame(
        {
            "generation": [1, 2, 3],
            "ivf_cycle":  [1, 1, 1],
            "collective_improved": [False, False, False],
        }
    )
    try:
        select_progression_cycles(cycles)
    except ValueError as exc:
        assert "no active cycle" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError when no active cycle exists")
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: 4 new tests FAIL with `ModuleNotFoundError: No module named 'extract_mechanism_cycles'`.

- [ ] **Step 3: Create `extract_mechanism_cycles.py` with only the selector**

Create `src/python/analysis/extract_mechanism_cycles.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import pandas as pd


def select_progression_cycles(cycles: pd.DataFrame) -> dict[str, pd.Series]:
    """Pick early / mid / late IVF cycles from a single run.

    Criteria (see spec 2026-04-13-ivf-mechanism-figures-design.md):
      * early = smallest generation with collective_improved and ivf_cycle == 1
      * late  = largest generation with collective_improved and ivf_cycle == 1
      * mid   = cycle with generation closest to the median of active generations

    Falls back gracefully when fewer than three active cycles exist.
    """
    active = cycles[
        cycles["collective_improved"] & (cycles["ivf_cycle"] == 1)
    ].sort_values("generation", kind="mergesort").reset_index(drop=True)

    if active.empty:
        raise ValueError("No active cycle found: no row has collective_improved=True.")

    early = active.iloc[0]
    late = active.iloc[-1]

    median_gen = float(active["generation"].median())
    mid_idx = (active["generation"] - median_gen).abs().idxmin()
    mid = active.loc[mid_idx]

    return {"early": early, "mid": mid, "late": late}
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: all 6 tests (2 from Task 1 + 4 new) PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/extract_mechanism_cycles.py tests/python/test_mechanism_figures.py
git commit -m "Add select_progression_cycles selector for mechanism figures"
```

---

## Task 3: Beneficial-label consistency test + helper

**Files:**
- Modify: `src/python/analysis/extract_mechanism_cycles.py`
- Test: `tests/python/test_mechanism_figures.py` (append)

**Why:** The plot distinguishes beneficial (blue) from harmful (red) offspring. The label must be derived from `delta_to_pf` (child PF-distance minus best-parent PF-distance) with a small tolerance — same rule used in the existing `extract_ivf_trace_cases.py`.

- [ ] **Step 1: Append the failing test**

Append to `tests/python/test_mechanism_figures.py`:

```python
def test_label_child_outcome_matches_delta_to_pf():
    from extract_mechanism_cycles import label_child_outcome

    frame = pd.DataFrame(
        {"delta_to_pf": [-0.5, -1e-13, 0.0, 1e-13, 0.5]}
    )
    labels = label_child_outcome(frame)
    assert labels == ["beneficial", "neutral", "neutral", "neutral", "harmful"]
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py::test_label_child_outcome_matches_delta_to_pf -v
```
Expected: FAIL with `ImportError: cannot import name 'label_child_outcome'`.

- [ ] **Step 3: Add `label_child_outcome` to `extract_mechanism_cycles.py`**

Append to `src/python/analysis/extract_mechanism_cycles.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/extract_mechanism_cycles.py tests/python/test_mechanism_figures.py
git commit -m "Add label_child_outcome helper aligned with trace extraction"
```

---

## Task 4: Implement `.mat` extraction

**Files:**
- Modify: `src/python/analysis/extract_mechanism_cycles.py`

**Why:** We need a working CLI that reads both `.mat` files, applies the selector, and writes three CSVs matching the schemas of `representative_cycle_*.csv`.

- [ ] **Step 1: Inspect the existing `.mat` structure**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/python - <<'EOF'
import pymatreader
p = pymatreader.read_mat(
    "data/raw/ivf_trace_cases/detailed/bimodal_dtlz4_m3/IVFSPEA2V2TRACE_DTLZ4_M3_D12_9012.mat"
)
tr = p["trace_run"]
print("run_id:", tr.get("run_id"), "n_cycles:", tr.get("n_cycles"))
cycles = tr["cycles"]
# Handle list or ndarray of structs
print("total cycles:", len(cycles) if hasattr(cycles, "__len__") else 1)
EOF
```
Expected: non-zero `n_cycles`, `total cycles` matches. Note the number — we need it for later sanity.

- [ ] **Step 2: Append the full extractor to `extract_mechanism_cycles.py`**

Replace the file contents so it becomes a complete CLI. Keep the already-written `select_progression_cycles` and `label_child_outcome` exactly as they are; add the IO layer around them.

Full file (`src/python/analysis/extract_mechanism_cycles.py`):

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pymatreader

from ivf_trace_common import (
    PROJECT_ROOT,
    coerce_struct_list,
    distance_to_reference_pf,
    ensure_directory,
    final_scalar,
    matrix_to_numpy,
    scalar_bool,
    vector_to_numpy,
)


DETAILED_ROOT = (
    PROJECT_ROOT / "data" / "raw" / "ivf_trace_cases" / "detailed" / "bimodal_dtlz4_m3"
)
REFERENCE_PF_PATH = (
    PROJECT_ROOT / "data" / "raw" / "ivf_trace_cases" / "reference_pf"
    / "DTLZ4_M3_D12_truePF.csv"
)
OUT_DIR = PROJECT_ROOT / "results" / "ivf_trace"

ANCHOR_RUN = 9012
CONTRAST_BAD_RUN = 9005
CONTRAST_BAD_GEN = 12
CONTRAST_GOOD_GEN = 398

TOL = 1e-12


def select_progression_cycles(cycles: pd.DataFrame) -> dict[str, pd.Series]:
    active = cycles[
        cycles["collective_improved"] & (cycles["ivf_cycle"] == 1)
    ].sort_values("generation", kind="mergesort").reset_index(drop=True)
    if active.empty:
        raise ValueError("No active cycle found: no row has collective_improved=True.")
    early = active.iloc[0]
    late = active.iloc[-1]
    median_gen = float(active["generation"].median())
    mid_idx = (active["generation"] - median_gen).abs().idxmin()
    mid = active.loc[mid_idx]
    return {"early": early, "mid": mid, "late": late}


def label_child_outcome(frame: pd.DataFrame) -> list[str]:
    labels: list[str] = []
    for delta in frame["delta_to_pf"].to_list():
        if delta < -TOL:
            labels.append("beneficial")
        elif delta > TOL:
            labels.append("harmful")
        else:
            labels.append("neutral")
    return labels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--detailed-root", type=Path, default=DETAILED_ROOT)
    parser.add_argument("--reference-pf", type=Path, default=REFERENCE_PF_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def read_run(detailed_root: Path, run_id: int) -> tuple[dict, list[dict]]:
    path = detailed_root / f"IVFSPEA2V2TRACE_DTLZ4_M3_D12_{run_id:04d}.mat"
    if not path.is_file():
        raise FileNotFoundError(f"Missing trace mat: {path}")
    payload = pymatreader.read_mat(str(path))
    trace_run = payload.get("trace_run", {})
    metric = payload.get("metric", {})
    run_meta = {
        "run_id": int(trace_run.get("run_id", run_id)),
        "seed": int(trace_run.get("seed", 0)),
        "final_igd": final_scalar(metric.get("IGD")),
        "final_hv": final_scalar(metric.get("HV")),
    }
    cycles = coerce_struct_list(trace_run.get("cycles"))
    return run_meta, cycles


def cycles_to_frame(cycles: list[dict], reference_pf: np.ndarray) -> pd.DataFrame:
    rows: list[dict] = []
    for cycle in cycles:
        generation = int(final_scalar(cycle.get("generation")) or 0)
        ivf_cycle = int(final_scalar(cycle.get("ivf_cycle")) or 0)
        child_objs = matrix_to_numpy(cycle.get("child_objs"))
        mother_objs = matrix_to_numpy(cycle.get("mother_objs"))
        father_objs = matrix_to_numpy(cycle.get("father_objs"))
        selected = vector_to_numpy(cycle.get("child_selected"), bool)

        child_pf = distance_to_reference_pf(child_objs, reference_pf) if child_objs.size else np.asarray([])
        mother_pf = distance_to_reference_pf(mother_objs, reference_pf) if mother_objs.size else np.asarray([])
        father_pf = distance_to_reference_pf(father_objs, reference_pf) if father_objs.size else np.asarray([])
        best_parent_pf = (
            np.minimum(mother_pf, father_pf) if child_pf.size else np.asarray([])
        )
        delta = child_pf - best_parent_pf if child_pf.size else np.asarray([])

        rows.append({
            "generation": generation,
            "ivf_cycle": ivf_cycle,
            "collective_improved": scalar_bool(cycle.get("collective_improved")),
            "num_children": int(child_objs.shape[0]) if child_objs.size else 0,
            "share_better_children": float(np.mean(delta < -TOL)) if delta.size else 0.0,
            "share_worse_children": float(np.mean(delta > TOL)) if delta.size else 0.0,
            "selection_rate": float(np.mean(selected)) if selected.size else 0.0,
            "_cycle_struct": cycle,
            "_mother_objs": mother_objs,
            "_father_objs": father_objs,
            "_child_objs": child_objs,
            "_child_pf": child_pf,
            "_best_parent_pf": best_parent_pf,
            "_delta": delta,
            "_selected": selected,
        })
    return pd.DataFrame(rows)


def population_rows(cycle_key: str, case_id: str, panel_role: str,
                    display_label: str, cycle: dict, reference_pf: np.ndarray) -> list[dict]:
    rows: list[dict] = []
    ref_iter = reference_pf
    for i, point in enumerate(ref_iter, start=1):
        rows.append({
            "cycle_key": cycle_key, "case_id": case_id, "panel_role": panel_role,
            "display_label": display_label, "point_group": "reference_pf",
            "point_index": i,
            "f1": float(point[0]), "f2": float(point[1]), "f3": float(point[2]),
        })
    pop_after = matrix_to_numpy(cycle.get("population_after_objs"))
    for i, point in enumerate(pop_after, start=1):
        rows.append({
            "cycle_key": cycle_key, "case_id": case_id, "panel_role": panel_role,
            "display_label": display_label, "point_group": "population_after",
            "point_index": i,
            "f1": float(point[0]), "f2": float(point[1]), "f3": float(point[2]),
        })
    return rows


def pair_rows(cycle_key: str, case_id: str, panel_role: str, display_label: str,
              row: pd.Series) -> list[dict]:
    rows: list[dict] = []
    mother = row["_mother_objs"]
    father = row["_father_objs"]
    child = row["_child_objs"]
    delta = row["_delta"]
    selected = row["_selected"]
    outcomes = label_child_outcome(pd.DataFrame({"delta_to_pf": delta}))
    n = child.shape[0] if child.size else 0
    for i in range(n):
        rows.append({
            "cycle_key": cycle_key, "case_id": case_id,
            "panel_role": panel_role, "display_label": display_label,
            "child_index": i + 1,
            "mother_f1": float(mother[i, 0]), "mother_f2": float(mother[i, 1]),
            "mother_f3": float(mother[i, 2]),
            "father_f1": float(father[i, 0]), "father_f2": float(father[i, 1]),
            "father_f3": float(father[i, 2]),
            "child_f1":  float(child[i, 0]),  "child_f2":  float(child[i, 1]),
            "child_f3":  float(child[i, 2]),
            "delta_to_pf": float(delta[i]),
            "selected_child": bool(selected[i]) if selected.size else False,
            "child_outcome": outcomes[i],
        })
    return rows


def cycle_manifest_row(cycle_key: str, case_id: str, panel_role: str,
                       display_label: str, run_meta: dict, row: pd.Series) -> dict:
    return {
        "cycle_key": cycle_key, "case_id": case_id, "panel_role": panel_role,
        "display_label": display_label,
        "run_id": run_meta["run_id"], "seed": run_meta["seed"],
        "final_igd": run_meta["final_igd"], "final_hv": run_meta["final_hv"],
        "generation": int(row["generation"]),
        "ivf_cycle": int(row["ivf_cycle"]),
        "collective_improved": bool(row["collective_improved"]),
        "num_children": int(row["num_children"]),
        "share_better_children": float(row["share_better_children"]),
        "share_worse_children": float(row["share_worse_children"]),
        "selection_rate": float(row["selection_rate"]),
    }


def make_cycle_key(case_id: str, run_id: int, generation: int, ivf_cycle: int) -> str:
    return f"{case_id}__run{run_id:04d}__g{generation:04d}__c{ivf_cycle}"


def main() -> None:
    args = parse_args()
    ensure_directory(args.out_dir)

    reference_pf = pd.read_csv(args.reference_pf).to_numpy(dtype=float)
    good_meta, good_cycles_raw = read_run(args.detailed_root, ANCHOR_RUN)
    bad_meta, bad_cycles_raw = read_run(args.detailed_root, CONTRAST_BAD_RUN)
    good_frame = cycles_to_frame(good_cycles_raw, reference_pf)
    bad_frame = cycles_to_frame(bad_cycles_raw, reference_pf)

    manifest: list[dict] = []
    populations: list[dict] = []
    pairs: list[dict] = []

    # Panel set 1: progression (run 9012: early / mid / late)
    progression = select_progression_cycles(good_frame)
    for role in ("early", "mid", "late"):
        row = progression[role]
        cycle_key = make_cycle_key("bimodal_dtlz4_m3", good_meta["run_id"],
                                   int(row["generation"]), int(row["ivf_cycle"]))
        display_label = f"{role.capitalize()} (gen {int(row['generation'])})"
        manifest.append(cycle_manifest_row(cycle_key, "bimodal_dtlz4_m3",
                                           f"progression_{role}", display_label,
                                           good_meta, row))
        populations.extend(population_rows(cycle_key, "bimodal_dtlz4_m3",
                                           f"progression_{role}", display_label,
                                           row["_cycle_struct"], reference_pf))
        pairs.extend(pair_rows(cycle_key, "bimodal_dtlz4_m3",
                               f"progression_{role}", display_label, row))

    # Panel set 2: single anchor — reuse the late-stage cycle closest to gen 398
    anchor_candidates = good_frame[
        (good_frame["ivf_cycle"] == 1) & good_frame["collective_improved"]
    ].copy()
    if anchor_candidates.empty:
        raise RuntimeError("No active cycles found in run 9012.")
    anchor_candidates["_dist"] = (anchor_candidates["generation"] - CONTRAST_GOOD_GEN).abs()
    anchor_row = anchor_candidates.sort_values(["_dist", "generation"],
                                               kind="mergesort").iloc[0]
    anchor_key = make_cycle_key("bimodal_dtlz4_m3", good_meta["run_id"],
                                int(anchor_row["generation"]), int(anchor_row["ivf_cycle"]))
    manifest.append(cycle_manifest_row(anchor_key, "bimodal_dtlz4_m3",
                                       "single_anchor",
                                       f"Anchor (gen {int(anchor_row['generation'])})",
                                       good_meta, anchor_row))
    populations.extend(population_rows(anchor_key, "bimodal_dtlz4_m3",
                                       "single_anchor",
                                       f"Anchor (gen {int(anchor_row['generation'])})",
                                       anchor_row["_cycle_struct"], reference_pf))
    pairs.extend(pair_rows(anchor_key, "bimodal_dtlz4_m3", "single_anchor",
                           f"Anchor (gen {int(anchor_row['generation'])})",
                           anchor_row))

    # Panel set 3: contrast — bad run 9005 at gen 12, good run 9012 at gen 398 (or nearest)
    bad_match = bad_frame[
        (bad_frame["ivf_cycle"] == 1) & bad_frame["collective_improved"]
        & (bad_frame["generation"] == CONTRAST_BAD_GEN)
    ]
    if bad_match.empty:
        bad_match = bad_frame[
            (bad_frame["ivf_cycle"] == 1) & bad_frame["collective_improved"]
        ].iloc[:1]
    bad_row = bad_match.iloc[0]
    bad_key = make_cycle_key("bimodal_dtlz4_m3", bad_meta["run_id"],
                             int(bad_row["generation"]), int(bad_row["ivf_cycle"]))
    manifest.append(cycle_manifest_row(bad_key, "bimodal_dtlz4_m3",
                                       "contrast_bad",
                                       f"Run 9005 — IGD={bad_meta['final_igd']:.3f}",
                                       bad_meta, bad_row))
    populations.extend(population_rows(bad_key, "bimodal_dtlz4_m3", "contrast_bad",
                                       "contrast_bad", bad_row["_cycle_struct"],
                                       reference_pf))
    pairs.extend(pair_rows(bad_key, "bimodal_dtlz4_m3", "contrast_bad",
                           "contrast_bad", bad_row))

    # Contrast-good reuses the anchor cycle (same row) but with a different panel_role
    manifest.append(cycle_manifest_row(anchor_key, "bimodal_dtlz4_m3",
                                       "contrast_good",
                                       f"Run 9012 — IGD={good_meta['final_igd']:.3f}",
                                       good_meta, anchor_row))
    populations.extend(population_rows(anchor_key, "bimodal_dtlz4_m3",
                                       "contrast_good", "contrast_good",
                                       anchor_row["_cycle_struct"], reference_pf))
    pairs.extend(pair_rows(anchor_key, "bimodal_dtlz4_m3", "contrast_good",
                           "contrast_good", anchor_row))

    cycles_df = pd.DataFrame(manifest)
    pops_df = pd.DataFrame(populations)
    pairs_df = pd.DataFrame(pairs)

    cycles_df.to_csv(args.out_dir / "mechanism_figure_cycles.csv", index=False)
    pops_df.to_csv(args.out_dir / "mechanism_figure_populations.csv", index=False)
    pairs_df.to_csv(args.out_dir / "mechanism_figure_pairs.csv", index=False)
    print(f"Wrote {len(cycles_df)} manifest rows, {len(pops_df)} population rows, "
          f"{len(pairs_df)} pair rows to {args.out_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Re-run the selector test suite to confirm no regressions**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: all 7 tests still PASS (the file was extended, not broken).

- [ ] **Step 4: Run the extractor**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/python src/python/analysis/extract_mechanism_cycles.py
```
Expected printout: `Wrote N manifest rows, M population rows, K pair rows to .../results/ivf_trace` with `N == 5` (early, mid, late, contrast_bad, contrast_good — anchor shares a cycle_key with contrast_good intentionally, so `N = 5` rows but 4 distinct cycle_keys).

- [ ] **Step 5: Inspect the CSVs**

```bash
cd /home/pedro/code/research/ivfspea2
head -1 results/ivf_trace/mechanism_figure_cycles.csv
awk -F, 'NR>1 {print $3","$11","$12}' results/ivf_trace/mechanism_figure_cycles.csv
wc -l results/ivf_trace/mechanism_figure_populations.csv results/ivf_trace/mechanism_figure_pairs.csv
```
Expected: 5 data rows in `mechanism_figure_cycles.csv`; panel_roles `progression_early`, `progression_mid`, `progression_late`, `single_anchor`/`contrast_good` (same cycle_key), `contrast_bad`; populations and pairs files non-empty.

- [ ] **Step 6: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/extract_mechanism_cycles.py results/ivf_trace/mechanism_figure_*.csv
git commit -m "Add extract_mechanism_cycles CLI and generated CSVs"
```

---

## Task 5: CSV schema test (red/green)

**Files:**
- Test: `tests/python/test_mechanism_figures.py` (append)

**Why:** Prevent silent schema drift between the extractor output and the plotter's expected columns. Test runs against the committed CSVs.

- [ ] **Step 1: Append the failing test**

Append to `tests/python/test_mechanism_figures.py`:

```python
MECH_DIR = os.path.join(PROJECT_ROOT, "results", "ivf_trace")


def test_mechanism_cycles_csv_has_expected_columns():
    df = pd.read_csv(os.path.join(MECH_DIR, "mechanism_figure_cycles.csv"))
    expected = {
        "cycle_key", "case_id", "panel_role", "display_label",
        "run_id", "seed", "final_igd", "final_hv",
        "generation", "ivf_cycle", "collective_improved",
        "num_children", "share_better_children", "share_worse_children",
        "selection_rate",
    }
    assert expected.issubset(set(df.columns))


def test_mechanism_pairs_csv_has_3d_coordinates():
    df = pd.read_csv(os.path.join(MECH_DIR, "mechanism_figure_pairs.csv"))
    for prefix in ("mother", "father", "child"):
        for axis in ("f1", "f2", "f3"):
            assert f"{prefix}_{axis}" in df.columns


def test_mechanism_populations_csv_covers_reference_and_population():
    df = pd.read_csv(os.path.join(MECH_DIR, "mechanism_figure_populations.csv"))
    assert "reference_pf" in df["point_group"].unique()
    assert "population_after" in df["point_group"].unique()


def test_mechanism_cycles_contains_all_five_panel_roles():
    df = pd.read_csv(os.path.join(MECH_DIR, "mechanism_figure_cycles.csv"))
    expected_roles = {
        "progression_early", "progression_mid", "progression_late",
        "single_anchor", "contrast_bad", "contrast_good",
    }
    assert expected_roles.issubset(set(df["panel_role"].unique()))
```

- [ ] **Step 2: Run tests**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: all tests PASS on first run (extractor already produces the schema). If any fail, fix the extractor in Task 4 before proceeding.

- [ ] **Step 3: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add tests/python/test_mechanism_figures.py
git commit -m "Add schema tests for mechanism figure CSVs"
```

---

## Task 6: Implement the plotter

**Files:**
- Create: `src/python/analysis/plot_mechanism_figures.py`

**Why:** Convert the CSVs into three PDFs. Uses shared 3D helpers lifted in Task 1.

- [ ] **Step 1: Create the plotter**

Create `src/python/analysis/plot_mechanism_figures.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from ivf_trace_common import (
    COLORS,
    PROJECT_ROOT,
    compute_axis_limits_3d,
    ensure_directory,
    scatter_child_points_3d,
    scatter_group_3d,
    scatter_parent_points_3d,
)


INPUT_DIR = PROJECT_ROOT / "results" / "ivf_trace"
OUT_DIR = PROJECT_ROOT / "paper" / "ppsn2026" / "figures"

VIEW_ELEV = 20
VIEW_AZIM = -60


def style() -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 6,
        "ytick.labelsize": 6,
        "legend.fontsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def load_inputs(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cycles = pd.read_csv(input_dir / "mechanism_figure_cycles.csv")
    populations = pd.read_csv(input_dir / "mechanism_figure_populations.csv")
    pairs = pd.read_csv(input_dir / "mechanism_figure_pairs.csv")
    return cycles, populations, pairs


def draw_panel(ax, pops_panel: pd.DataFrame, pairs_panel: pd.DataFrame,
               x: str = "f1", y: str = "f2", z: str = "f3") -> None:
    scatter_group_3d(ax, pops_panel, "reference_pf", x, y, z,
                     COLORS["reference_pf"], 4, 0.30)
    scatter_group_3d(ax, pops_panel, "population_after", x, y, z,
                     COLORS["population_after"], 14, 0.55)

    scatter_parent_points_3d(ax, pairs_panel, "mother", x, y, z,
                             marker="o", color=COLORS["mother"], size=28)
    scatter_parent_points_3d(ax, pairs_panel, "father", x, y, z,
                             marker="D", color=COLORS["father"], size=60)

    beneficial = pairs_panel[pairs_panel["child_outcome"] == "beneficial"]
    harmful = pairs_panel[pairs_panel["child_outcome"] == "harmful"]
    neutral = pairs_panel[pairs_panel["child_outcome"] == "neutral"]
    scatter_child_points_3d(ax, beneficial, x, y, z, COLORS["beneficial"], 20)
    scatter_child_points_3d(ax, harmful, x, y, z, COLORS["harmful"], 20)
    scatter_child_points_3d(ax, neutral, x, y, z, COLORS["neutral"], 14)

    x_lo, x_hi, y_lo, y_hi, z_lo, z_hi = compute_axis_limits_3d(
        pops_panel, pairs_panel, x, y, z, margin=0.05
    )
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.set_zlim(z_lo, z_hi)
    ax.view_init(elev=VIEW_ELEV, azim=VIEW_AZIM)
    ax.set_xlabel(r"$f_1$")
    ax.set_ylabel(r"$f_2$")
    ax.set_zlabel(r"$f_3$")


def legend_handles() -> list:
    return [
        Line2D([0], [0], marker=".", color="w", markerfacecolor=COLORS["reference_pf"],
               markersize=6, label="Reference PF"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["population_after"],
               markersize=6, label="Population"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["mother"],
               markersize=6, label="Mothers"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor=COLORS["father"],
               markeredgecolor="#111", markersize=7, label="Father"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor=COLORS["beneficial"],
               markersize=6, label="Beneficial offspring"),
        Line2D([0], [0], marker="v", color="w", markerfacecolor=COLORS["harmful"],
               markersize=6, label="Harmful offspring"),
    ]


def plot_single(cycles, populations, pairs, out_path: Path) -> None:
    panel_key = cycles[cycles["panel_role"] == "single_anchor"].iloc[0]["cycle_key"]
    pops_panel = populations[populations["cycle_key"] == panel_key]
    pairs_panel = pairs[(pairs["cycle_key"] == panel_key)
                        & (pairs["panel_role"] == "single_anchor")]

    fig = plt.figure(figsize=(5.0, 4.0))
    ax = fig.add_subplot(111, projection="3d")
    draw_panel(ax, pops_panel, pairs_panel)
    ax.set_title(f"IVF cycle on DTLZ4 (M=3) — "
                 f"gen {int(cycles.loc[cycles['panel_role'] == 'single_anchor', 'generation'].iloc[0])}, run 9012")
    fig.legend(handles=legend_handles(), loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(out_path)
    plt.close(fig)


def plot_progression(cycles, populations, pairs, out_path: Path) -> None:
    order = ["progression_early", "progression_mid", "progression_late"]
    fig = plt.figure(figsize=(12.0, 4.2))

    panel_meta = {r: cycles[cycles["panel_role"] == r].iloc[0] for r in order}
    all_pops = populations[populations["panel_role"].isin(order)]
    all_pairs = pairs[pairs["panel_role"].isin(order)]
    x_lo, x_hi, y_lo, y_hi, z_lo, z_hi = compute_axis_limits_3d(
        all_pops, all_pairs, "f1", "f2", "f3", margin=0.05
    )

    for i, role in enumerate(order, start=1):
        ax = fig.add_subplot(1, 3, i, projection="3d")
        key = panel_meta[role]["cycle_key"]
        pops_panel = populations[(populations["cycle_key"] == key)
                                 & (populations["panel_role"] == role)]
        pairs_panel = pairs[(pairs["cycle_key"] == key)
                            & (pairs["panel_role"] == role)]
        draw_panel(ax, pops_panel, pairs_panel)
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_zlim(z_lo, z_hi)
        stage = role.split("_", 1)[1].capitalize()
        ax.set_title(f"{stage} (gen {int(panel_meta[role]['generation'])})")

    fig.suptitle("IVF operator progression — DTLZ4 (M=3), run 9012",
                 fontsize=10, y=0.98)
    fig.legend(handles=legend_handles(), loc="lower center", ncol=6,
               frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(out_path)
    plt.close(fig)


def plot_contrast(cycles, populations, pairs, out_path: Path) -> None:
    order = ["contrast_bad", "contrast_good"]
    fig = plt.figure(figsize=(9.0, 4.2))

    panel_meta = {r: cycles[cycles["panel_role"] == r].iloc[0] for r in order}
    all_pops = populations[populations["panel_role"].isin(order)]
    all_pairs = pairs[pairs["panel_role"].isin(order)]
    x_lo, x_hi, y_lo, y_hi, z_lo, z_hi = compute_axis_limits_3d(
        all_pops, all_pairs, "f1", "f2", "f3", margin=0.05
    )

    for i, role in enumerate(order, start=1):
        ax = fig.add_subplot(1, 2, i, projection="3d")
        key = panel_meta[role]["cycle_key"]
        pops_panel = populations[(populations["cycle_key"] == key)
                                 & (populations["panel_role"] == role)]
        pairs_panel = pairs[(pairs["cycle_key"] == key)
                            & (pairs["panel_role"] == role)]
        draw_panel(ax, pops_panel, pairs_panel)
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_zlim(z_lo, z_hi)
        igd = float(panel_meta[role]["final_igd"])
        run_id = int(panel_meta[role]["run_id"])
        label = "bimodal convergência incorreta" if role == "contrast_bad" else "bimodal convergência correta"
        ax.set_title(f"Run {run_id} — IGD = {igd:.3f}\n({label})")

    fig.legend(handles=legend_handles(), loc="lower center", ncol=6,
               frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    ensure_directory(args.out_dir)
    style()
    cycles, populations, pairs = load_inputs(args.input_dir)
    plot_single(cycles, populations, pairs,
                args.out_dir / "fig_ivf_mechanism_single.pdf")
    plot_progression(cycles, populations, pairs,
                     args.out_dir / "fig_ivf_mechanism_progression.pdf")
    plot_contrast(cycles, populations, pairs,
                  args.out_dir / "fig_ivf_mechanism_contrast.pdf")
    print(f"Wrote fig_ivf_mechanism_{{single,progression,contrast}}.pdf to {args.out_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the plotter**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/python src/python/analysis/plot_mechanism_figures.py
```
Expected: three PDFs created in `paper/ppsn2026/figures/`, no matplotlib warnings.

- [ ] **Step 3: Visually inspect the PDFs**

```bash
cd /home/pedro/code/research/ivfspea2
ls -la paper/ppsn2026/figures/fig_ivf_mechanism_*.pdf
```
Expected: three files with non-trivial size (≥30 KB each). Open and confirm: legends legible, no axis clipping, reference PF visible, point groups distinguishable.

- [ ] **Step 4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/plot_mechanism_figures.py paper/ppsn2026/figures/fig_ivf_mechanism_*.pdf
git commit -m "Add plot_mechanism_figures and rendered PDFs"
```

---

## Task 7: Makefile target

**Files:**
- Modify: `paper/Makefile`

- [ ] **Step 1: Add the target**

Apply this diff to `paper/Makefile`:

```
.PHONY: all springer springer-nature ppsn ppsn2026 ppsn-hosts \
        ppsn2026-ivf-hosts ppsn-hosts-assets papers clean \
        view view-springer view-springer-nature \
        view-ppsn view-ppsn2026 view-ppsn-hosts view-ppsn2026-ivf-hosts \
-        install-deps
+        install-deps mechanism-figures
```

Append after the existing `ppsn2026:` block:

```make
mechanism-figures:
	cd .. && .venv/bin/python src/python/analysis/extract_mechanism_cycles.py
	cd .. && .venv/bin/python src/python/analysis/plot_mechanism_figures.py
```

- [ ] **Step 2: Run the target**

```bash
cd /home/pedro/code/research/ivfspea2
make -C paper mechanism-figures
```
Expected: both scripts run successfully, CSVs and PDFs regenerated.

- [ ] **Step 3: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/Makefile
git commit -m "Add mechanism-figures Makefile target"
```

---

## Task 8: Integrate figures into `paper/ppsn2026/main.tex`

**Files:**
- Modify: `paper/ppsn2026/main.tex`

**Why:** The PDFs are useless until referenced in the paper body.

- [ ] **Step 1: Locate the insertion point**

```bash
cd /home/pedro/code/research/ivfspea2
grep -n "IVF dynamics\|fig:cycles\|fig3_ivf" paper/ppsn2026/main.tex
```
Expected: shows lines around 410–423 where `fig3_ivf_dynamics.pdf` is inserted. Insert the three new figures **immediately after** the `\end{figure}` at line 423.

- [ ] **Step 2: Insert the three figure blocks**

After `\end{figure}` on line 423, insert:

```latex
\begin{figure}[t]
	\centering
	\includegraphics[width=0.85\textwidth]{figures/fig_ivf_mechanism_single.pdf}
	\caption{One IVF cycle of IVF-SPEA2 v2 operating on DTLZ4 with three
	objectives (run 9012, late generation). Mothers (blue), the current
	father (orange diamond), beneficial offspring (green triangles) and
	harmful offspring (red triangles) are plotted against the reference
	Pareto front (light grey) and the host archive (dark grey). The
	visual language follows Sampaio et al.~\cite{sampaio2019ivfnsga3}
	Fig.~3.}
	\label{fig:ivf-mechanism-single}
\end{figure}

\begin{figure}[t]
	\centering
	\includegraphics[width=\textwidth]{figures/fig_ivf_mechanism_progression.pdf}
	\caption{Progression of a single IVF-SPEA2 v2 run on DTLZ4 (M=3, run
	9012). Left to right: first active cycle (exploration), median
	generation (breakthrough), and last active cycle (exploitation).
	Analogous to Figs.~5--7 of Sampaio
	et~al.~\cite{sampaio2019ivfnsga3}.}
	\label{fig:ivf-mechanism-progression}
\end{figure}

\begin{figure}[t]
	\centering
	\includegraphics[width=0.95\textwidth]{figures/fig_ivf_mechanism_contrast.pdf}
	\caption{Two outcomes of IVF-SPEA2 v2 on DTLZ4 (M=3): a run that
	converged to an incorrect bimodal basin (left, IGD = 0.54) and a run
	that reached the true front (right, IGD = 0.05). Same operator, same
	seed family, different stochastic trajectory.}
	\label{fig:ivf-mechanism-contrast}
\end{figure}
```

- [ ] **Step 3: Verify the BibTeX key exists; add it if missing**

```bash
cd /home/pedro/code/research/ivfspea2
grep -n "sampaio2019ivfnsga3" paper/ppsn2026/references.bib
```

If the key is missing, append to `paper/ppsn2026/references.bib`:

```bibtex
@inproceedings{sampaio2019ivfnsga3,
  author    = {Sampaio, S\'avio Menezes and Dantas, Altino and Camilo-Junior, Celso G.},
  title     = {IVF/NSGA-III: In Vitro Fertilization method coupled to NSGA-III},
  booktitle = {2019 IEEE Congress on Evolutionary Computation (CEC)},
  year      = {2019},
  pages     = {2066--2073},
  doi       = {10.1109/CEC.2019.8790234},
}
```

- [ ] **Step 4: Build the paper**

```bash
cd /home/pedro/code/research/ivfspea2
make -C paper ppsn2026
```
Expected: build succeeds; check output for `Overfull \hbox`, undefined references, or missing file warnings for the three figures. Fix any issues before committing.

- [ ] **Step 5: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026/main.tex paper/ppsn2026/references.bib
git commit -m "Integrate IVF mechanism figures into ppsn2026 main body"
```

---

## Task 9: Final sanity sweep

**Files:**
- None (verification only)

- [ ] **Step 1: Full test suite passes**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/pytest tests/python/test_mechanism_figures.py -v
```
Expected: all tests PASS.

- [ ] **Step 2: Existing trace plot still builds without regressions**

```bash
cd /home/pedro/code/research/ivfspea2
.venv/bin/python src/python/analysis/plot_ivf_trace_cases.py
```
Expected: original `ivf_trace_mechanistic_panels_supplementary.pdf` (or equivalent) regenerates without errors — the Task 1 refactor must not have broken it.

- [ ] **Step 3: Paper build clean**

```bash
cd /home/pedro/code/research/ivfspea2
make -C paper ppsn2026
```
Expected: `paper/ppsn2026/build/main.pdf` present, all three new `\ref{fig:ivf-mechanism-*}` resolve, no missing-figure warnings.

- [ ] **Step 4: Commit any cleanup (if needed)**

If nothing changed, skip. Otherwise:

```bash
cd /home/pedro/code/research/ivfspea2
git add <files>
git commit -m "Cleanup after mechanism figure integration"
```
