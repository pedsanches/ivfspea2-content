# Design: IVF-Hosts Paper Visual Rewrite

**Date:** 2026-04-10
**Paper:** `paper/ppsn2026-ivf-hosts/main.tex`
**Venue:** PPSN 2026 (LNCS, 14 pages excl. references)
**Goal:** Replace redundant aggregate-count figures with argument-driven visualizations that directly sustain the central hypothesis; restructure text to be figure-led.

---

## Context and Problem

The paper argues that IVF benefit depends on the host selection mechanism (Hypothesis H), with ordering SPEA2 > NSGA-III > NSGA-II. The current figures are:

- **Fig 1 (main):** Win/tie/loss bar chart — aggregate counts, repeats Table 2
- **Fig 2 (appendix):** Per-instance median scatter — most informative but buried
- **Fig 3 (appendix):** Family-wise relative IGD boxplots — hard to read, outlier-dominated
- **Fig 4 (main):** Cross-host ranking bar chart — redundant with Fig 1

**Core problems:**
1. Fig 1 and Fig 4 say the same thing (IVF/SPEA2 > NSGA-III > NSGA-II) through different lenses
2. No figure shows effect-size *magnitude* (only counts)
3. No figure separates M=2 vs M=3 (a central finding in the text)
4. No figure provides dynamic/temporal evidence for the mechanistic hypothesis
5. The most informative figure (scatter) is in the appendix

**Identified gaps between text and visual evidence:**

| Gap | Text claim | Visual evidence | Status |
|-----|-----------|----------------|--------|
| L1 | A12 magnitudes differ categorically | Only Table A12 (summary stats) | Missing |
| L2 | M=2 vs M=3 asymmetry for NSGA-III | Not shown anywhere | Missing |
| L3 | Ordering consistent across instances | Only aggregate counts | Missing |
| L4 | Failure cases identifiable | Not shown | Missing |
| L5 | Directional feedback mechanism | No dynamic evidence | Missing |
| L6 | Ordering consistent within families | Fig 3 attempts but poorly | Weak |

---

## Design Decisions

- **Confound (operator vs host differences):** Treated as acknowledged limitation, no ablation experiment.
- **Per-instance tables (Appendix B):** Removed from paper; available in supplementary/repository.
- **Convergence data:** Will be collected via re-execution of a representative subset.

---

## New Figure Architecture

### Fig 1: A12 Strip Plot by Host

**Replaces:** Old Fig 1 (win/tie/loss bars)
**Argument:** "The magnitude of IVF effect is categorically different across hosts."
**Gaps addressed:** L1

**Specification:**
- Single panel, 3 columns: IVF/SPEA2, IVF/NSGA-III, IVF/NSGA-II
- Each point = 1 instance (52 per column)
- Y-axis = A12 oriented for IVF benefit (values > 0.5 favor IVF)
  - Orientation: `A12_ivf = 1 - A12` for IGD (since A12 < 0.5 = IVF better in IGD stats CSVs)
- Metric: IGD only
- Horizontal line at 0.5 (neutral)
- Shaded bands for S/M/L thresholds (0.56, 0.64, 0.71)
- Points colored by family (DTLZ, MaF, WFG, ZDT, RWMOP) — same palette as existing scatter
- Markers: circle for M=2, triangle for M=3
- Thick horizontal line per column = median A12_ivf
- Approximate size: `figsize=(8, 5)`, full `\textwidth`

**Data source:** `results/tables/hosts_{ivfspea2,ivfnsgaii,ivfnsgaiii}_igd_stats.csv`, column `A12`.

### Fig 2: Instance x Host Heatmap

**Replaces:** Tables 2 and 3 (win/tie/loss overall and by family)
**Argument:** "The ordering holds instance by instance; failure cases are few and identifiable."
**Gaps addressed:** L3, L4, L6

**Specification:**
- Matrix: rows = 52 instances, columns = 3 hosts
- Row grouping: by family (DTLZ, MaF, WFG, ZDT, RWMOP), within family by M (M=2 first, then M=3)
- Visual separator between families (horizontal line or spacing)
- Cell color: divergent colormap on oriented A12
  - Dark blue ~ 1.0 (strong IVF benefit)
  - White = 0.5 (neutral)
  - Red ~ 0.0 (IVF harms)
- Significance marker: asterisk or dot overlay on cells with BH-corrected significance
- Left margin: family bracket or colored bar
- Extra column indicating M (2 or 3) for each instance
- Row labels: abbreviated problem names (DTLZ1, MaF3, WFG7, etc.)
- Approximate size: `figsize=(6, 12)` or equivalent, full `\textwidth`. Note: 52 rows is dense; may need to use a compact layout or span a full page. Font size for row labels should be ~6pt to fit.

**Data source:** Cross-join of 3 `hosts_*_igd_stats.csv` by (problem, M).

### Fig 3: M=2 vs M=3 Faceted Comparison

**New figure.**
**Argument:** "NSGA-III collapses from robust benefit at M=2 to near-neutrality at M=3; SPEA2 remains strong in both."
**Gaps addressed:** L2

**Specification:**
- Two panels side by side: M=2 (left), M=3 (right)
- Within each panel: X-axis = 3 hosts, Y-axis = oriented A12 (IGD)
- Visualization: box + strip plot combined
  - Boxplot showing quartiles of A12 distribution
  - Jittered individual points overlaid, colored by family
  - Horizontal line at 0.5 (neutral)
  - S/M/L reference bands as in Fig 1
- Approximate size: `figsize=(10, 5)`, full `\textwidth`

**Data source:** Same `hosts_*_igd_stats.csv`, filtered by column `M`.

### Fig 4: Convergence Curves

**New figure. Requires re-execution.**
**Argument:** "IVF accelerates convergence in directional hosts but does not alter the trajectory in isotropic hosts."
**Gaps addressed:** L5

**Specification:**
- Grid of 6 panels (2x3 or 3x2), each panel = 1 representative instance
- Within each panel: 6 curves (IVF/host and host for 3 hosts)
  - X-axis = FEs (0 to 100k)
  - Y-axis = median IGD (log scale)
  - IVF variants: solid lines; base algorithms: dashed lines
  - Color by host: blue (SPEA2), green (NSGA-III), red (NSGA-II)
  - Confidence band: IQR (percentiles 25-75) in low alpha around median
- Panel title = problem name

**Instance selection criteria (6 slots):**

| Slot | Purpose | Selection criterion | Family | M |
|------|---------|-------------------|--------|---|
| 1 | Strong gain SPEA2 + NSGA-III | High A12 for both | DTLZ | 2 |
| 2 | Strong gain, different family | High A12 for both | MaF | 2 |
| 3 | Difficult case (many ties) | Low A12, most ties | WFG | 2 |
| 4 | SPEA2 wins, NSGA-II doesn't | High SPEA2 A12, neutral NSGA-II | ZDT | 2 |
| 5 | NSGA-III loses benefit in M=3 | NSGA-III tie at M=3, win at M=2 | DTLZ | 3 |
| 6 | SPEA2 failure case | SPEA2 loss | WFG | 2 |

**Final instance selection** will be determined programmatically from existing A12 data before re-execution.

**Re-execution requirements:**
- 6 instances x 6 algorithms x 30 runs = 1080 executions
- 100k FEs each, pop=100
- Logging: IGD at every generation (every 100 FEs for pop=100, yielding 1000 data points per run)
- Output format: CSV with columns `algo, problem, M, run, FE, IGD`
- Estimated runtime: 2-4 hours on a single machine

**Approximate figure size:** `figsize=(14, 9)` for 2x3 grid, full `\textwidth`

### Fig A1 (Appendix): Per-Instance Scatter

**Kept from current Fig 2, moved to appendix.**
- 6 panels: 3 hosts x 2 metrics (IGD, HV)
- No changes to current implementation
- Provides complementary per-instance magnitude view with HV

---

## Text Restructuring

### Principle

Each Results subsection opens by referencing its anchor figure, interprets the visual pattern, then quantifies with inline numbers. The flow inverts from "numbers then figure" to "figure then numbers."

### Section-by-section changes

**Section 5 (Results, opening paragraph):**
- Current: short paragraph pointing to Fig 1 (win/tie/loss)
- New: Opens with Fig 1 (A12 strip plot). "Figure 1 shows the distribution of oriented effect sizes across all 52 instances. The three hosts occupy categorically different regions of the A12 scale." Win/tie/loss numbers become inline quantification.

**Sections 5.1-5.3 (Per-host results):**
- Current: each subsection repeats win/tie/loss by family and M, referencing tables
- New: Anchored on Fig 2 (heatmap). "The instance-level view in Figure 2 confirms that IVF/SPEA2 benefits are broad-based across all families..." Family-level win/tie/loss becomes a *reading* of the heatmap, not separate tabular data.

**Section 5.4 (Cross-host comparison):**
- Current: absolute ranking + old Fig 4 + paragraph on M=2 vs M=3
- New: Two anchor figures:
  - Fig 3 (M=2 vs M=3): "Figure 3 reveals the sharpest structural finding: IVF/NSGA-III collapses from robust benefit at M=2 to near-neutrality at M=3..."
  - Fig 4 (convergence): "Figure 4 provides dynamic evidence for the compatibility hypothesis..."
- Cross-host ranking becomes inline text: "IVF/SPEA2 attains the best mean rank (1.50 IGD, 1.44 HV)..."

**Section 6 (Discussion):**
- References Figs 1-4 as convergent body of evidence
- WFG difficulty now references heatmap directly (visible white band)
- Limitations: maintains operator/host confound as acknowledged limitation

### Elements removed from body

| Element | Destination |
|---------|-------------|
| Table 2 (overall win/tie/loss) | Numbers go inline in text |
| Table 3 (family breakdown) | Absorbed by heatmap (Fig 2) |
| Old Fig 1 (win/tie/loss bars) | Replaced by A12 strip plot |
| Old Fig 4 (cross-host ranking bars) | Inline text or appendix |
| 12 per-instance tables (Appendix B) | Supplementary material / repository |

### Appendix structure

- Fig A1: Per-instance scatter (current Fig 2, IGD + HV, 6 panels)
- Table A1: `hosts_summary` (win/tie/loss by M and metric)
- Table A2: `cross_host_absolute` (ranking numbers)

### Space budget estimate

| Component | Pages |
|-----------|-------|
| Text (Sec 1-6, restructured) | ~8.5 |
| Table 1 (adaptations) | ~0.3 |
| Table A12 (effect sizes) | ~0.3 |
| Fig 1 (A12 strip plot) | ~0.5 |
| Fig 2 (heatmap) | ~0.8 |
| Fig 3 (M=2 vs M=3) | ~0.5 |
| Fig 4 (convergence, 2x3 grid) | ~0.7 |
| Appendix A (Fig A1 + 2 tables) | ~1.5 |
| **Total** | **~13.1** |

Within the 14-page limit with margin for adjustment.

---

## Implementation Sequence

1. **Instance selection for Fig 4** — programmatic selection from existing A12 data
2. **MATLAB convergence logging** — modify/create experiment script with per-generation IGD logging
3. **Re-execution** — run 1080 experiments, collect convergence CSVs
4. **Python figure generation** — implement all 4 new figures + Fig A1
5. **LaTeX restructuring** — rewrite Results and Discussion, remove old tables/figures
6. **Integration and compilation** — build paper, verify page count, adjust spacing

---

## Files to create or modify

### New files
- `experiments/run_hosts_convergence.m` — MATLAB script for convergence re-execution
- `src/python/analysis/plot_hosts_figures_v2.py` — new figure generation script (or extend existing)
- `data/processed/hosts_convergence.csv` — convergence time-series data

### Modified files
- `paper/ppsn2026-ivf-hosts/main.tex` — full text restructuring
- `paper/ppsn2026-ivf-hosts/Makefile` — update assets target for new figures
- `src/python/analysis/plot_hosts_results.py` — keep existing as-is (generates Fig A1); new figures go in v2 script

### Unchanged files
- `src/python/analysis/build_hosts_paper_csv.py`
- `src/python/analysis/compute_hosts_tables.py`
- `results/tables/hosts_*_stats.csv` (existing data reused)
