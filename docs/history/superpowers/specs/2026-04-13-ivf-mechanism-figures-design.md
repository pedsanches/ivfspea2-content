# IVF Mechanism Figures — Design Spec

**Date:** 2026-04-13
**Paper target:** `paper/ppsn2026/` (PPSN 2026 main submission)
**Motivation:** The IVF/NSGA-III paper (Sampaio, Dantas, Camilo-Jr., 2019) uses three families of figures to convey the IVF operator's mechanics: a flowchart (Figs. 1–2), 3D scatter plots in objective space showing mother/father/offspring interactions (Figs. 3, 5–8), and parameter-sensitivity heatmaps plus DTLZ boxplots (Figs. 10–19). Of these, our papers already cover the flowchart (TikZ mechanism diagram in the hosts paper), the C×R heatmaps (`hosts_fig3b`, `hosts_v2_fig8_sensitivity`), and the per-instance boxplots (`hosts_v2_fig11_raincloud`). **The one analog that is missing is the 3D scatter visualization of the operator acting in objective space.** This spec designs three such figures for the main paper `ppsn2026`.

## Goal

Produce three scatter-3D figures for `paper/ppsn2026/` that illustrate the IVF-SPEA2 v2 operator in action on DTLZ4 with three objectives, matching the visual language of IVF/NSGA-III Figs. 3–8 so readers can compare mechanisms across papers.

## Non-Goals

- No new MATLAB experiments — reuse existing `data/raw/ivf_trace_cases/detailed/` `.mat` files.
- No refactor of the existing 930-line `plot_ivf_trace_cases.py` — import helpers only.
- No interactive / animated output — static PDF only.
- No new color palette — reuse the `COLORS` dict already established for the supplementary trace figure.

## Deliverables

Three new PDF figures under `paper/ppsn2026/figures/`:

| File | Variant | Panels | LaTeX width |
|------|---------|--------|-------------|
| `fig_ivf_mechanism_single.pdf` | Single-cycle snapshot (analog to IVF/NSGA-III Fig. 3) | 1 | 1 column |
| `fig_ivf_mechanism_progression.pdf` | Early / Mid / Late cycles within one run (analog to Figs. 5–7) | 3 horizontal | 2 columns |
| `fig_ivf_mechanism_contrast.pdf` | Bad-outcome run vs good-outcome run, same problem | 2 horizontal | 1.5 columns |

## Anchor Case

All three figures share one benchmark to keep the narrative coherent:

**`bimodal_dtlz4_m3`** — DTLZ4, M=3, D=12.

- Run **9012** (`final_igd = 0.053`, `share_better_children = 0.75`) anchors variants (i) and (ii).
- Run **9005** (`final_igd = 0.54`, bimodal-bad) anchors the contrast panel in variant (iii) alongside run 9012.

Rationale: DTLZ4 has a spherical PF analogous to DTLZ2 used in IVF/NSGA-III (so the visual language matches); 9012 has the highest `share_better_children` among M=3 beneficial cases (visually striking); 9005 is its natural foil and is already present in `representative_cycles.csv`.

## Cycle Selection

All selected cycles satisfy: `ivf_cycle = 1`, `collective_improved = True`.

| Figure | Run | Cycle(s) selected | Criterion |
|--------|-----|-------------------|-----------|
| (i) single | 9012 | gen 398, c1 | Already the representative cycle for `bimodal_good`; highest `share_better_children = 0.75` among M=3 cases |
| (ii) progression — Early | 9012 | smallest `generation` with `collective_improved=True` | First active IVF cycle of the run |
| (ii) progression — Mid | 9012 | `median(generation)` over active cycles | Splits active IVF window into two halves |
| (ii) progression — Late | 9012 | largest `generation` with `collective_improved=True` | Boundary of the exploitation regime |
| (iii) contrast — Bad | 9005 | gen 12, c1 | Already in `representative_cycles.csv` |
| (iii) contrast — Good | 9012 | gen 398, c1 | Already in `representative_cycles.csv` |

If Early and Mid collapse to the same generation (short run), take the second active cycle as Mid and surface a warning from the extractor.

## Data Pipeline

New stage, written from scratch, consuming raw `.mat` files and producing three CSVs under `results/ivf_trace/`:

```
data/raw/ivf_trace_cases/detailed/bimodal_dtlz4_m3/IVFSPEA2V2TRACE_DTLZ4_M3_D12_{9005,9012}.mat
                                           │
                                           ▼
                           extract_mechanism_cycles.py
                                           │
                                           ▼
   results/ivf_trace/mechanism_figure_cycles.csv      (per-cycle manifest)
   results/ivf_trace/mechanism_figure_populations.csv (f1/f2/f3 per point-group per cycle)
   results/ivf_trace/mechanism_figure_pairs.csv      (mother/father/child triplets per cycle)
                                           │
                                           ▼
                          plot_mechanism_figures.py
                                           │
                                           ▼
          paper/ppsn2026/figures/fig_ivf_mechanism_{single,progression,contrast}.pdf
```

CSV schemas mirror the existing `representative_cycle_*` CSVs so the plot helpers already accept them without modification.

## Visual Spec

Point-group conventions (identical across all panels):

| Group | Color | Marker | Size | Alpha |
|-------|-------|--------|------|-------|
| `reference_pf` | light gray | `.` | 4 | 0.35 |
| `population` | mustard yellow | `o` | 30 | 0.6 |
| `mothers` | green | `s` | 80 | 0.9 |
| `father` | orange, black edge | `D` | 140 | 1.0 |
| `offspring_beneficial` | blue | `^` | 60 | 0.9 |
| `offspring_harmful` | red | `v` | 60 | 0.9 |

The IVF/NSGA-III "target niche" point group is intentionally omitted — it is a concept specific to NSGA-III's niche-preservation routine and has no analog in SPEA2 v2, whose father-selection rule H1 operates directly on the archive-wide fitness and objective-space distances.

- All axes clamped to `[0, 1.1]³` (DTLZ4 octant sphere + small margin).
- 3D view angle: `elev=20, azim=-60` (matplotlib default; matches IVF/NSGA-III Fig. 3 orientation).
- Variant-specific layout:
  - **(i)** single axis, legend to the right of the plot box.
  - **(ii)** three subplots, `sharex/sharey/sharez` equivalents via identical `set_xlim/set_ylim/set_zlim`, `wspace=0.02`, legend only on first subplot; panel titles `Early (gen X)` / `Mid (gen Y)` / `Late (gen Z)` plus a single suptitle "Progressão do operador IVF — DTLZ4 M=3, run 9012".
  - **(iii)** two subplots side-by-side, titles "Run 9005 — IGD = 0.54" vs "Run 9012 — IGD = 0.053"; annotation arrow on each pointing at the cluster ("convergência bimodal incorreta" / "correta").

## File Changes

### New files

| Path | Responsibility |
|------|---------------|
| `src/python/analysis/extract_mechanism_cycles.py` | Read 2 `.mat` files, apply Cycle Selection criteria, emit 3 CSVs under `results/ivf_trace/mechanism_figure_*.csv` |
| `src/python/analysis/plot_mechanism_figures.py` | Read those 3 CSVs, render 3 PDFs under `paper/ppsn2026/figures/`. Imports 3D scatter helpers from `plot_ivf_trace_cases.py` (or a shared module) |
| `tests/python/test_mechanism_figures.py` | Unit tests (no matplotlib): validate cycle-selection criteria and CSV schemas |

### Modified files

| Path | Change |
|------|--------|
| `src/python/analysis/plot_ivf_trace_cases.py` | If `_scatter_group_3d`, `_scatter_parent_points_3d`, `_scatter_child_points_3d`, `_compute_axis_limits_3d`, and `COLORS` are not already in `ivf_trace_common.py`, lift them into that shared module; otherwise leave untouched |
| `paper/Makefile` | Add `mechanism-figures` target running `extract_mechanism_cycles.py` then `plot_mechanism_figures.py` |
| `paper/ppsn2026/main.tex` | Insert three `\begin{figure}` blocks after the operator-description paragraphs; captions cross-reference IVF/NSGA-III (Sampaio et al., 2019) |

## Test Plan

`tests/python/test_mechanism_figures.py` (no rendering):

1. `test_early_mid_late_are_distinct_and_ordered` — given a synthetic list of `(generation, collective_improved)` tuples, the selector returns three distinct cycles with `early.gen <= mid.gen <= late.gen`.
2. `test_short_run_fallback` — when median generation coincides with early, selector picks second active cycle and emits a warning.
3. `test_beneficial_label_matches_delta_to_pf` — for each child row, `beneficial iff delta_to_pf < 0` (child strictly closer to PF than its best parent).
4. `test_csv_schemas` — `mechanism_figure_pairs.csv` has columns matching `representative_cycle_pairs.csv`; same for populations and cycles.

Manual acceptance: all three PDFs render without clipping; each panel has visible legend, title, and axis labels; reference PF is visible without overwhelming the operator trace.

## Integration Checklist

- [ ] Extractor produces all 3 CSVs deterministically from the 2 `.mat` files.
- [ ] Plot script renders 3 PDFs without matplotlib warnings.
- [ ] `pytest tests/python/test_mechanism_figures.py` passes.
- [ ] `make -C paper ppsn2026` builds successfully with the three new figures referenced.
- [ ] Visual review: all legends legible, no axis clipping, point groups distinguishable.

## Risks

- **Early / Mid / Late may collapse** on short runs. Mitigated by the fallback rule and test 2.
- **DTLZ4 PF density** may obscure operator points at `elev=20, azim=-60`. Mitigated by `alpha=0.35` on `reference_pf`; if still cluttered, reduce to 256 sampled PF points.
- **`mother_f3` / `father_f3` / `child_f3` may be NaN** for M=2 panels — not applicable here since we hard-pin M=3, but the pair extractor should assert `not all NaN in *_f3` columns.
