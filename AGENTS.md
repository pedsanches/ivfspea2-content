# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

<!-- Generated from CLAUDE.md by scripts/ci/check_agents_mirror.py --write.
     Edit CLAUDE.md instead; this file is checked for drift in CI. -->

## Project Overview

IVF-SPEA2 is a research project implementing an enhanced multi-objective evolutionary algorithm that integrates an IVF-inspired operator into SPEA2. It is built on the [PlatEMO](https://github.com/BIMK/PlatEMO) framework. The project includes the algorithm implementation (MATLAB), analysis pipeline (Python), four manuscripts and a master's dissertation (LaTeX).

`AGENTS.md` carries the same guidance for Codex and is **generated from this file** — edit `CLAUDE.md`, then run `python scripts/ci/check_agents_mirror.py --write`. CI fails on drift. (The two were previously mirrored by hand and had diverged by 175 lines.)

## Commands

### Setup
```bash
make setup       # Locked environment + `pip install -e .`
make setup-dev   # Same, plus ruff and pytest
```

**Install `requirements.lock.txt`, not `requirements.txt`, when the work touches committed figures or checksums.** The lock records the environment that produced every committed artifact (Python 3.14.2, numpy 2.4.3, **matplotlib 3.10.8**); `requirements.txt` states supported ranges for new work. Every committed PDF carries `/Creator (Matplotlib v3.10.8)`, so building figures under a different matplotlib rewrites all of them while changing no plotted number. See `docs/REPRODUCIBILITY_ENVIRONMENT.md`.

`make setup` also installs the `ivfspea2` package in editable mode, which is what makes `from ivfspea2.paths import PROJECT_ROOT` work from both `python src/python/analysis/X.py` and an installed import.

Every `make` recipe that runs Python sources `.venv/bin/activate` first, so `make setup` is a prerequisite for the analysis and paper-asset targets.

### Testing
`make test` runs the **Python suite only** — MATLAB tests are a separate target and are never reached by `make test`.

```bash
make test                                        # Python tests (pytest)
make test-matlab                                 # MATLAB unit tests
python -m pytest tests/python/ -v                # Python tests directly
python -m pytest tests/python/test_analysis.py -v  # A single test file
matlab -batch "run('tests/matlab/run_tests.m')"  # MATLAB tests directly
```

`pyproject.toml` pins `testpaths = ["tests/python"]`. This matters: `src/python/analysis/test_convergence_significance.py` and `test_ecdf_difference.py` are **pipeline steps, not tests** (they run in `analysis-convergence-tests`), and a bare `pytest` would otherwise import them.

`tests/matlab/run_tests.m` asserts that `CalFitness`, `EnvironmentalSelection` and `CalFitness_V3` resolve to the canonical variant directories before running anything — see *MATLAB path shadowing* below. It raises on failure, so `matlab -batch` returns non-zero.

### Release integrity
```bash
make verify-release    # Every manifest row resolves, every checksum matches, every DOI is declared
make write-checksums   # Regenerate the checksum file from the manifest
```

`results/submission_release_manifest.csv` carries an `availability` column fixing which invariant applies to each row — `in_repo` (exists, tracked, hashes), `build_output` (gitignored; `producer` must name the rebuild command), `archived_offline` (not distributed; `archived_path` keeps the trail), `deposit_only` (frozen under `artifact/`). Adding a row without a valid availability fails the check. `docs/RELEASE_IDENTITY.md` is the single source of truth for which DOI means what, and `verify-release` enforces that no tracked file cites an undeclared one.

### Analysis
```bash
make analysis                                      # Main analysis runner (script.py)
make analysis-benchmark-figures                    # 5 benchmark figures (IGD/HV)
python src/python/analysis/compute_iqr_tables.py   # Generate IQR tables
```

The **convergence-rigor pipeline** (`docs/PLAN_CONVERGENCE_RIGOR.md`) is a staged
dependency chain in the root `Makefile`; each stage depends on the previous one,
so running a later target reruns everything upstream:

```bash
make analysis-convergence            # Full chain end-to-end
make analysis-convergence-build      # .mat traces  → data/processed/hosts_convergence.csv
make analysis-convergence-summaries  # per-run AUC / time-to-target, merge diagnostic, alt-instance selection
make analysis-convergence-tests      # bootstrap CIs, paired Wilcoxon + BH, KS ECDF
make analysis-convergence-plots      # sensitivity, HV ratio, v2 IGD/ECDF plots
```

The build stage reads PlatEMO `.mat` files produced by `experiments/run_hosts_convergence.m`; without them the chain has no input.

### Papers
Each manuscript lives in its own directory under `paper/`, driven by `paper/Makefile`.
The engine is auto-detected in `paper/latex.mk`: `latexmk` when a system TeX is
installed, otherwise Tectonic (`brew install tectonic`, no system TeX needed).
Force one with `make ENGINE=tectonic` or `make ENGINE=latexmk`.

```bash
cd paper && make                    # Springer Nature → paper/springer-nature/build/sn-article.pdf
cd paper && make ppsn2026           # PPSN 2026 (dynamics) → paper/ppsn2026/build/main.pdf
cd paper && make ppsn-hosts         # PPSN 2026 (IVF hosts) → paper/ppsn2026-ivf-hosts/build/main.pdf
cd paper && make clei2026           # CLEI 2026 → paper/clei2026/build/main.pdf
cd paper && make papers             # Build all four
cd paper && make clean              # Remove build artifacts
cd paper && make view               # Open compiled PDF (view-ppsn2026, view-clei, ...)
```

The root `Makefile` now delegates all four: `make paper`, `paper-ppsn`,
`paper-hosts`, `paper-clei`, `paper-all`.

`paper/clei2026/figures` is a **symlink** to `../ppsn2026/figures` — the two
manuscripts share one figure set and only the symlink is tracked, so the CLEI
directory is not self-contained on its own.

**`ppsn2026-ivf-hosts` regenerates its own evidence.** Its `assets` target runs a
fixed sequence of `src/python/analysis/` scripts (hosts CSV → tables → geometry →
figures) before LaTeX, and chains into `make analysis-convergence` when the
convergence `.mat` files exist. The stamp `build/.assets.stamp` tracks the
upstream scripts and inputs only — the generated figures and `results/tables/`
outputs are versioned deliverables, so `make clean` deliberately leaves them
alone (`clean-assets` is the opt-in that removes them). The other three
manuscripts compile straight from committed sources with no asset step.

### Thesis
The master's dissertation (Portuguese, UFG template) is separate from the article manuscripts and builds with Tectonic pinned to `--only-cached`, so the package cache must be primed once per machine:

```bash
make thesis-bootstrap   # First build on a machine: fetch the Tectonic bundle (network)
make thesis             # Compile → thesis/masters/build/main.pdf (offline)
make thesis-doctor      # Check tooling + validate data-sources.toml
make thesis-render      # Rasterize every page to build/render/ for visual QA
```

These root targets delegate to `thesis/masters/Makefile` (`all`, `bootstrap`, `doctor`, `render`, `clean`), which also works directly with `cd thesis/masters && make …`.

`main.tex` uses `inf-ufg-tectonic.cls`, a compatibility derivative; the original `inf-ufg.cls` is retained unchanged.

### MATLAB Experiments
```matlab
% In MATLAB (from project root):
addpath(genpath('src/matlab/lib/PlatEMO'));
run('experiments/run_ivfspea2v2_submission.m');            % Canonical v2 submission run
run('experiments/validate_ivfspea2_submission_matrix.m');  % Validate results
```

Runners are parameterized by **environment variables**, not edited in place, so batches can be scoped without touching sources. Each script defines its own prefix with defaults — e.g. `run_ppsn_dynamics.m` reads `PPSN_RUNS` (30), `PPSN_MAXFE` (100000), `PPSN_POP` (100), `PPSN_WORKERS` (6), `PPSN_CASE_IDS`, `PPSN_MANIFEST`; the engineering suite uses `ENG_SUITE_*`; the feasibility probes use `PROBE_*`. Read the script's `local_env_*` block before launching a long run:

```bash
PPSN_RUNS=2 PPSN_MAXFE=10000 PPSN_CASE_IDS=strong_pos_zdt6_m2 \
  matlab -batch "run('experiments/run_ppsn_dynamics.m')"
```

The `experiments/launch_*.sh` wrappers set these variables for full parallel batches; `scripts/monitor_submission_progress.sh` and `scripts/monitor_ctrl_batch.sh` follow progress.

## Architecture

### MATLAB path shadowing — read before running anything
PlatEMO ships ~57 algorithm directories that each define a file named
`CalFitness.m`, and many also define `EnvironmentalSelection.m`. A plain
`addpath(genpath(...))` therefore resolves those names by genpath ordering, and a
run can silently execute another algorithm's fitness function. Two rules follow:

- `src/matlab/ivf_spea2/` was a **legacy mirror** that shadowed the canonical classes. It no longer exists and is gitignored so it cannot come back. Eight experiment scripts used to `addpath` it; those lines are gone, and `scripts/ci/check_matlab_paths.py` now fails if any `addpath` target does not resolve.
- When several IVF variants must coexist (tests, ablations), prepend the intended variant directory with `addpath(dir, '-begin')`. `tests/matlab/setupCanonicalTestPaths.m` is the reference implementation: it strips the legacy mirror, adds PlatEMO, then prepends V3 and V2 in that order so V2 wins.

Verify resolution before trusting a run:

```matlab
which IVFSPEA2V2 -all
which CalFitness -all
```

### Canonical Implementation Path (v2)
The **primary** algorithm is IVF/SPEA2 v2:
```
src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/
```
Class name: `IVFSPEA2V2`. This version incorporates two validated improvements (see `docs/IVFSPEA2_KNOWLEDGE_BASE.md`):
- **H1 (Dissimilar Father):** Each mother receives a different father, selected for maximum objective-space distance via top-3 candidates + binary tournament by fitness.
- **H2 (Collective Criterion):** IVF cycles continue while average population fitness improves, rather than requiring a single offspring to beat the father.

### Algorithm Components (MATLAB) — v2
- **IVFSPEA2V2.m** — Main PlatEMO ALGORITHM subclass. Runs the IVF v2 phase then standard SPEA2 GA operators each generation.
- **IVF_V2.m** — IVF v2 operator: dissimilar father selection per mother (H1), collective cycle continuation (H2), SBX crossover (eta_c=20).
- **CalFitness.m** — SPEA2 fitness: computes strength S(i), raw fitness R(i), and k-NN distance density D(i).
- **EnvironmentalSelection.m** — Selects archive by fitness < 1 (non-dominated), with distance-based truncation if over capacity.

### Algorithm variant map
All under `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/`.

| Directory | Class | Role |
|-----------|-------|------|
| `IVF-SPEA2-V2` | `IVFSPEA2V2` | **Canonical.** Everything new targets this. |
| `IVF-SPEA2` | `IVFSPEA2` | v1 baseline; use only to reproduce the original submission. |
| `IVF-SPEA2-V3` | `IVFSPEA2V3` | Successor line; has its own `CalFitness_V3` / `EnvironmentalSelection_V3` alongside unsuffixed copies. |
| `IVF-NSGA-II`, `IVF-NSGA-III` | `IVFNSGAII`, `IVFNSGAIII` | IVF operator transplanted into other hosts — the evidence base for the `ppsn2026-ivf-hosts` manuscript. |
| `IVF-SPEA2-V2-TRACE`, `IVF-SPEA2-V2-CTRL-TRACE` | `IVFSPEA2V2TRACE`, `IVFSPEA2V2CTRLTRACE` | Instrumented runs emitting per-generation traces for the dynamics/controller work. `SPEA2-TRACE` is the matching baseline. |
| `IVF-SPEA2-V2-NORM` | `IVFSPEA2V2Norm` | Normalization pilot. |
| `IVFSPEA2-ABL-1C`, `-ABL-4C`, `-ABL-DOM`, `-P2-COMBINED` | — | Factorial ablation harness. |
| `IVFSPEA2-V1-DISSIM`, `-V2-COLLECTIVE`, `-V3-ETA10`, `-V4-ADAPTIVE`, `-V5-MUTATION` | — | Single-hypothesis probes from the tuning pipeline. |

### Key Algorithm Parameters (v2 defaults — config C26, tuned via 3-phase pipeline)
| Parameter | Default | Description |
|-----------|---------|-------------|
| C | 0.12 | Collection rate |
| R | 0.225 | IVF trigger ratio |
| M | 0.3 | Fraction of mothers to mutate (EAR light mode) |
| V | 0.1 | Fraction of decision variables to mutate |
| Cycles | 2 | Max IVF cycles per generation |

### Data Pipeline
```
config/*.csv      → experiment case lists (which problems/instances a runner sweeps)
MATLAB experiments → data/raw/          (gitignored, .mat files)
Python analysis   → data/processed/    (consolidated CSVs, committed)
                  → results/figures/   (plots, gitignored)
                  → results/tables/    (LaTeX tables, committed)
Paper build       → paper/<paper-name>/build/  (gitignored PDFs)
Thesis build      → thesis/masters/build/  (gitignored PDF)
```

`config/` holds the case definitions the runners consume — `ppsn_dynamics_cases*.csv`, `ppsn_ctrl_batch_{A,B,C}.csv` and their out-of-sample counterparts, `ivf_trace_cases.csv`, `engineering_candidates_rwmop_m23*.csv`, `hosts_front_geometry.csv`. Add a case by extending the CSV, not by editing the runner.

Some derived CSVs exceed GitHub's 100 MB limit and are gitignored by explicit path (`results/tables/hosts_dynamic_normalized_traces.csv` and its `artifact/` twin) — regenerate them rather than expecting them in a clone.

### Manuscripts
| Directory | Manuscript |
|-----------|------------|
| `paper/springer-nature/` | Springer Nature / Memetic Computing article (sources under `src/`, class and figures resolved via `TEX_SEARCH_PATHS`) |
| `paper/ppsn2026/` | PPSN 2026 — early population dynamics for operator switching |
| `paper/ppsn2026-ivf-hosts/` | PPSN 2026 — IVF across host algorithms (regenerates its assets; see Papers) |
| `paper/clei2026/` | CLEI 2026 (Intelligent Systems track, IEEEtran) |
| `thesis/masters/` | Master's dissertation (pt-BR, UFG template) |

### Python code (`src/python/`)
| Package | Purpose |
|---------|---------|
| `ivfspea2/` | **The supported library.** `paths` (project root + layout), `figstyle` (backend + one set of publication rcParams), `figio` (`save_figure`, byte-stable), `cohorts` (run-cohort filtering), `release` (manifest/checksum/DOI checks). New code imports from here. |
| `analysis/` | The pipeline scripts: consolidation, statistics, tables, figures. Entry points `script.py` (`make analysis`), `compute_iqr_tables.py`, `gen_graph.py`. Uses `pymatreader` to read `.mat` directly. |
| `dynamics/` | Trajectory extraction and controller analysis for the PPSN dynamics paper. |
| `figures/` | Shared figure generation and helpers (`utils.py`, warmup horizons, classifier comparison). |
| `fla/` | Fitness-landscape-analysis pipeline: `build_dataset.py` → `compute_response.py` → `train_models.py`, fed by `src/matlab/fla/sample_and_extract_features.m`. |

The ~65 scripts in `analysis/` predate `ivfspea2/` and keep working unchanged: `cohort_filter.py` and `figure_io.py` remain importable as **deprecation shims** that re-export from the package, so the existing `try/except` import blocks and bare `from figure_io import save_figure` lines still resolve. Migrate a script when you touch it, not in a sweep.

Use `ivfspea2.cohorts` (via `cohort_filter`) to decide which runs belong to the frozen evidence cohort; never filter run IDs ad hoc.

Do **not** add `src/python/analysis/__init__.py` — direct invocation already puts that directory on `sys.path[0]`, and an `__init__.py` would invite setuptools to export `analysis` as a top-level distribution.

### Unreachable code lives in `legacy/`
`scripts/ci/find_orphans.py` decides by rule what is reachable — named in a Makefile, launcher, doc or test, or transitively imported by something that is. Unreachable scripts moved to `legacy/python/analysis/`, keeping their directory shape so `git log --follow` works; `legacy/MANIFEST.csv` records every move.

Two guards veto a move regardless: a script named in the release manifest or evidence map, and a script that is the **sole producer of a file something live depends on**. The second caught three scripts every reachability measure called dead — `consolidate_nsga_experiments.py` (writes an `ASSET_INPUTS` entry of the accepted paper), `sensitivity_analysis.py` (writes a file the tests read), `prepare_ivf_trace_case_manifest.py` (writes six tracked CSVs). In each case the file survived only because it was committed; moving the producer would have made it unregenerable.

### Metrics for new experiments

- All new experimental scripts (MATLAB or Python) must, at minimum, compute and persist both **IGD** and **HV** for every configuration/problem they evaluate.
- Additional metrics are welcome, but IGD and HV are mandatory baselines and must not be dropped.

### Submission Protocol
The current manuscript evidence model is summarized in `docs/IVFSPEA2_EVIDENCE_MODEL.md` — it fixes the primary endpoint (IGD), the retained cohort, and what the frozen artifacts do and do not justify. Check claims against it before changing results or conclusions. Two submission tracks exist:

**v1 (IVFSPEA2) — original baseline:**
- Run IDs: **2001–2100** (isolated from historical runs)
- Tag: `SUB20260218`
- 52 benchmark configurations × 100 runs each
- Parameters: C=0.11, R=0.10, M=0, V=0, Cycles=3

**v2 (IVFSPEA2V2) — current primary (config C26):**
- Run IDs: **3001–3060**
- Tag: `SUB20260228_V2`
- 52 benchmark configurations × 60 runs each
- Parameters: C=0.12, R=0.225, M=0.3, V=0.1, Cycles=2
- Script: `experiments/run_ivfspea2v2_submission.m`

Common:
- RWMOP9 requires special processing via `experiments/process_rwmop9.m` (empirical Pareto front for IGD)
- Progress monitoring: `scripts/monitor_submission_progress.sh`

### Reference docs
- `docs/IVFSPEA2_KNOWLEDGE_BASE.md` — algorithm and data knowledge
- `docs/IVFSPEA2_EVIDENCE_MODEL.md` — evidence hierarchy and claim scope
- `docs/PLAN_CONVERGENCE_RIGOR.md`, `docs/CONVERGENCE_SELECTION_PROTOCOL.md` — the convergence pipeline's rationale and instance-selection protocol
- `results/SUBMISSION_EVIDENCE_MAP.md`, `results/submission_release_manifest.csv` — human- and machine-readable evidence inventories
- `docs/RELEASE_IDENTITY.md` — which DOI means what; enforced by `make verify-release`
- `docs/REPRODUCIBILITY_ENVIRONMENT.md` — the environment that produced every committed artifact, and why matplotlib is pinned
- `artifact/README.md` — provenance ledger for the frozen Zenodo deposits (do not edit their bytes)
- `legacy/README.md` — what moved out of the live tree and why
- `docs/history/` — completed plans and superseded proposals, kept as record
- `src/matlab/lib/PlatEMO/VENDOR.md` — vendoring record and the inventory of project code inside the vendored tree
