# Engineering Suite Expansion Protocol (Target: 8 RWMOP Problems)

## Objective

Expand the engineering validation from 3 to 8 problems in a way that is statistically defensible, reproducible, and reviewer-proof.

This protocol is designed to directly address the reviewer concern about practical validation breadth while avoiding post-hoc selection bias.

## Why this protocol is citation-backed

Selection and analysis decisions must be justified by literature, not by convenience.

| Decision | Rationale | Citation key (paper/bib/sn-bibliography.bib) |
|---|---|---|
| Use RWMOP as engineering universe | Standardized real-world constrained MOO benchmark suite | `kumar2021benchmark` |
| Use nonparametric pairwise tests | Recommended methodology for EC algorithm comparison | `derrac2011practical`, `wilcoxon1945` |
| Use multiple-testing correction (MAIN only) | Controls family-wise error in many pairwise tests | `holm1979simple` |
| Report effect size in MAIN | Significance alone does not quantify practical relevance | `vargha2000critique` |
| Keep 60 runs in MAIN | Stronger stability than the common 30-run convention | `eftimov2025adaptive` |

## Scope and constraints

- Problem universe for selection: `RWMOP1..RWMOP50` with `M in {2,3}`.
- Target final set size: exactly 8 problems.
- Metrics required in all new analyses: IGD and HV.
- Baseline set: the same 8 baselines already used in the manuscript.
- Budget parity: `N=100`, `maxFE=100000`, identical to current main protocol.

## Current state (before expansion)

- Current engineering MAIN set in `experiments/run_engineering_suite_rwmop.m` is:
  - `RWMOP9 (M=2)`, `RWMOP21 (M=2)`, `RWMOP8 (M=3)`.
- Current SCREEN shortlist is fixed to 6 candidates.
- Canonical v2 feasibility entrypoint is available as `experiments/probe_rwmop_feasibility_v2.m` (delegates to `probe_rwmop_feasibility.m` with `PROBE_ALGO=IVFSPEA2V2`).

## Pre-registered selection rules (lock before MAIN)

Selection must be deterministic and documented before running the 60-run MAIN.

### Gate A: feasibility eligibility (SCREEN stage)

For each candidate problem `p`, with SCREEN runs (`n_screen = 10` initially):

1. IVF/SPEA2 and SPEA2 both satisfy:
   - `NValidIGD >= 8`
   - `NValidHV >= 8`
2. At least 6 of 9 algorithms satisfy both:
   - `NValidIGD >= 6`
   - `NValidHV >= 6`
3. Common-run coverage:
   - `NCommonRuns >= 8`

Candidates failing Gate A are excluded from final selection.

### Gate B: discriminative value

For each candidate `p`, compute:

- `DI_IGD(p)`: number of non-equal pairwise signs (`+` or `-`) across 8 baselines (max 8)
- `DI_HV(p)`: same for HV
- `DI_total(p) = DI_IGD(p) + DI_HV(p)` (max 16)

**Statistical note (SCREEN stage):** Pairwise signs at the SCREEN stage use uncorrected Wilcoxon rank-sum at alpha=0.05. This is intentional: SCREEN is exploratory filtering, not a formal hypothesis test. The Holm-Bonferroni correction is applied only in the MAIN analysis (see Phase 4 analysis requirements below).

Rules:

- Keep candidates with `DI_total >= 4` (at least modest discriminative signal).
- Label candidate profile using IGD signs:
  - Favorable: `Plus - Minus >= 3`
  - Balanced: `abs(Plus - Minus) <= 1`
  - Adverse: `Minus - Plus >= 3`

### Gate C: composition constraints for final 8

Select 8 candidates ranked by `DI_total` under these constraints:

1. Include at least:
   - 2 favorable,
   - 2 balanced,
   - 1 adverse.
2. Objective-count coverage target:
   - Prefer at least 2 problems with `M=3`.
3. Decision-dimension spread:
   - At least 2 low-D (`D <= 4`),
   - At least 2 mid/high-D (`D >= 7`).

If constraints are infeasible, apply one pre-declared relaxation pass in this order:

1. Relax M=3 target from 2 to 1,
2. Relax balanced minimum from 2 to 1,
3. Fill remaining slots by highest `DI_total` among Gate A passes.

No further relaxation is allowed.

### Contingency: fewer than 8 Gate A passes

If the candidate universe yields fewer than 8 problems passing Gate A:

1. Accept all Gate-A-passing candidates as the final set (no minimum).
2. Apply Gate C composition constraints on a best-effort basis (report which constraints could not be satisfied and why).
3. Report the reduced count transparently in the manuscript (e.g., "7 of the targeted 8 problems passed feasibility screening").
4. Do **not** lower Gate A thresholds post hoc to inflate the count.

## Execution plan

### Phase 0 - tooling alignment (required first)

1. Add a canonical feasibility probe for v2 (`IVFSPEA2V2`) across all `RWMOP1..50`.
2. Generalize engineering SCREEN runner to accept an external candidate list (instead of hardcoded 6).
3. Create candidate list file (recommended path):
   - `config/engineering_candidates_rwmop_m23.csv`

Command templates:

```bash
# 0.1 Canonical v2 feasibility probe (RWMOP1..50, 1 run)
matlab -batch "run('experiments/probe_rwmop_feasibility_v2.m')"

# 0.2 SCREEN execution using external candidate list
ENG_SUITE_STAGE=SCREEN \
ENG_SUITE_PROBLEMS_FILE=config/engineering_candidates_rwmop_m23.csv \
matlab -batch "run('experiments/run_engineering_suite_rwmop.m')"

# 0.3 SCREEN post-processing with the same candidate list
ENG_SUITE_STAGE=SCREEN \
ENG_SUITE_PROBLEMS_FILE=config/engineering_candidates_rwmop_m23.csv \
matlab -batch "run('experiments/process_engineering_suite.m')"
```

High-throughput option (20-thread machine, MATLAB trial capped at 6 workers/session):

```bash
# Phase 1 in 3 shards (3 MATLAB sessions x 6 workers = 18 workers total)
scripts/run_rwmop_feasibility_probe_v2_parallel.sh

# SCREEN or MAIN in grouped parallel mode (G1/G2/G3 concurrently)
ENG_SUITE_STAGE=SCREEN \
ENG_SUITE_PROBLEMS_FILE=config/engineering_candidates_rwmop_m23.csv \
scripts/run_engineering_suite_main_parallel.sh

ENG_SUITE_STAGE=MAIN \
ENG_SUITE_RUNBASE=11 \
ENG_SUITE_PROBLEMS_FILE=results/engineering_screening/engineering_suite_selection_locked_8.csv \
scripts/run_engineering_suite_main_parallel.sh
```

### Phase 1 - universe scan (fast)

Run feasibility scan on all `M in {2,3}` RWMOP problems and generate:

- `results/engineering_screening/rwmop_feasibility_probe_ivfspea2v2.csv`
- optional per-baseline feasibility summaries.

### Phase 2 - SCREEN on candidate universe

Run SCREEN with `n_screen=10` for all candidates passing basic feasibility and generate:

- `results/engineering_screening/engineering_suite_summary_screen.csv`
- `results/engineering_screening/engineering_suite_pairwise_screen.csv`
- `results/engineering_screening/engineering_suite_raw_screen.csv`

### Phase 3 - lock final set (automated)

Apply Gates A/B/C **via a deterministic script** and freeze selection in:

- `results/engineering_screening/engineering_suite_selection_locked_8.csv`

The selection must be automated (not performed manually) to eliminate ambiguity. Recommended implementation: a Python script (e.g., `src/python/analysis/select_engineering_suite.py`) that reads the SCREEN summary CSV, applies Gates A/B/C exactly as specified above, and writes the locked selection CSV. The script must be committed before MAIN execution begins so that the selection is fully traceable.

Mandatory fields:

- `Problem, M, D, DI_IGD, DI_HV, DI_total, ProfileClass, GateAStatus, Selected, SelectionReason`.

### Phase 4 - MAIN execution and analysis (60 runs)

Run the locked problems with `ENG_SUITE_RUNBASE=11` and `ENG_SUITE_RUNS=60` (run IDs `11..70`, no overlap with SCREEN seeds). The MAIN post-processor must use only `data/engineering_suite/` as its search directory.

Produce:

- `results/engineering_suite/engineering_suite_summary_main.csv`
- `results/engineering_suite/engineering_suite_pairwise_main.csv`
- `results/engineering_suite/engineering_suite_raw_main.csv`

#### MAIN analysis requirements

The MAIN analysis is the formal statistical report and must satisfy:

1. **Multiple-testing correction:** Apply Holm-Bonferroni correction across all pairwise Wilcoxon comparisons per problem (8 baselines = 8 tests per metric per problem). Report both raw and adjusted p-values.

2. **Effect size:** For every significant pairwise comparison, report the Vargha-Delaney A₁₂ statistic. Interpret using standard thresholds: A₁₂ in [0.44, 0.56] = negligible, [0.56, 0.64) or (0.36, 0.44] = small, [0.64, 0.71) or (0.29, 0.36] = medium, otherwise = large.

3. **HV reference point:** HV is computed using PlatEMO's built-in HV indicator. The reference point is derived from `problem.GetOptimum(10000)` (the problem's analytical or tabulated Pareto front). For problems where only an empirical PF is available (e.g., RWMOP9), state this explicitly in the results.

4. **IGD reference:** IGD is recomputed against the empirical Pareto front (union of all feasible final populations across all algorithms and runs, filtered to the non-dominated set). This is consistent with the SCREEN stage.

### Phase 5 - manuscript and rebuttal integration

Update:

1. Methods section (selection protocol text and citation linkage).
2. Engineering results table (8 problems).
3. Code availability with selection artifacts.
4. Rebuttal matrix entry for real-world validation breadth.

## Data isolation map

Each phase writes to a dedicated directory tree. Raw `.mat` outputs and processed CSV results are strictly separated to prevent cross-phase contamination.

| Phase | Raw data (.mat) | Processed outputs (CSV/TeX) | Run IDs |
|---|---|---|---|
| Phase 1 (probe) | `data/engineering_probe/<ALGO>/` | `results/engineering_screening/` | `1` (single exploratory run) |
| Phase 2 (SCREEN) | `data/engineering_screening/` | `results/engineering_screening/` | `1..10` |
| Phase 3 (lock) | — (no new data) | `results/engineering_screening/` | — |
| Phase 4 (MAIN) | `data/engineering_suite/` | `results/engineering_suite/` | `11..70` |

### Run ID separation (SCREEN / MAIN)

PlatEMO ties the `run` parameter to the RNG seed: each run ID produces a deterministic random stream. If SCREEN and MAIN used overlapping run IDs (e.g., both starting at 1), any problem that passes SCREEN and enters MAIN would have its first 10 MAIN runs **statistically identical** to the SCREEN runs that informed the selection decision. This is data leakage — the selection criterion would be correlated with the reported result.

**Policy:** MAIN run IDs start at `11`, producing the range `11..70` (60 runs). SCREEN uses `1..10`. This guarantees zero seed overlap between phases. The MAIN post-processor must only search `data/engineering_suite/` for `.mat` files (never `data/engineering_screening/`).

### Legacy path exclusion

The MAIN post-processor (`process_engineering_suite.m`) currently includes `data/engineering/` as a fallback search directory. This legacy path must be removed for the expansion protocol to prevent stale or foreign data from entering the MAIN analysis. The only valid MAIN search directory is `data/engineering_suite/`.

## Reproducibility and anti-bias controls

- Pre-register thresholds and relaxations in this file before running MAIN.
- Use non-overlapping run ranges (see Data isolation map above):
  - SCREEN: `1..10`
  - MAIN: `11..70`
- **RNG seeding:** PlatEMO ties the `run` parameter to the random seed (each run ID produces a deterministic seed). The non-overlapping ranges guarantee that no SCREEN seed is reused in MAIN. This mechanism must be stated in the manuscript's reproducibility section.
- Do not replace selected problems after MAIN starts.
- If a selected problem later fails due to unexpected feasibility collapse, keep it and report limitations; do not swap post hoc.

## Acceptance criteria (definition of done)

This expansion is complete only if all criteria below are true:

1. At least 5 (target: 8) engineering problems reported in MAIN (see fewer-than-8 contingency).
2. Selection lock file exists and is traceable to SCREEN outputs via the automated selection script.
3. IGD and HV are both reported for all selected problems (with explicit validity caveats where needed).
4. MAIN results include Holm-corrected p-values and Vargha-Delaney A₁₂ effect sizes for all significant pairwise comparisons.
5. HV reference point derivation and IGD empirical PF construction are documented in the manuscript methods.
6. Manuscript methods/results explicitly describe the selection protocol and cite benchmark/statistics sources.
7. Rebuttal text can claim expanded practical validation without post-hoc selection.

## Practical notes

- The existing 1-run v1 feasibility probe (`rwmop_feasibility_probe_ivfspea2.csv`) is useful for orientation only; it must not be used as the final selector for v2.
- The locked-8 protocol is intentionally conservative: transparency and auditability are prioritized over maximizing favorable outcomes.
