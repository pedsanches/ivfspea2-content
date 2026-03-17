# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IVF-SPEA2 is a research project implementing an enhanced multi-objective evolutionary algorithm that integrates an IVF-inspired operator into SPEA2. It is built on the [PlatEMO](https://github.com/BIMK/PlatEMO) framework. The project includes the algorithm implementation (MATLAB), analysis pipeline (Python), and the manuscript (LaTeX).

## Commands

### Setup
```bash
make setup          # Create Python venv and install dependencies
# or manually:
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### Testing
```bash
make test                                        # Run all Python tests
python -m pytest tests/python/ -v               # Run Python tests (single suite)
python -m pytest tests/python/test_analysis.py -v  # Run a single test file
matlab -batch "run('tests/matlab/run_tests.m')" # Run MATLAB unit tests
```

### Analysis
```bash
make analysis                                           # Generate all analysis outputs
python src/python/analysis/compute_iqr_tables.py       # Generate IQR tables
python src/python/analysis/script.py                   # Main analysis runner
```

### Paper
```bash
cd paper && make        # Compile LaTeX → paper/build/sn-article.pdf
cd paper && make clean  # Remove build artifacts
cd paper && make view   # Open compiled PDF
```

### MATLAB Experiments
```matlab
% In MATLAB (from project root):
addpath(genpath('src/matlab/lib/PlatEMO'));
run('experiments/run_ivfspea2_all_benchmarks_submission.m');  % Full submission run
run('experiments/validate_ivfspea2_submission_matrix.m');      % Validate results
```

## Architecture

### Canonical Implementation Path (v2)
The **primary** algorithm is IVF/SPEA2 v2:
```
src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/
```
Class name: `IVFSPEA2V2`. This version incorporates two validated improvements (see `docs/IVFSPEA2_KNOWLEDGE_BASE.md`):
- **H1 (Dissimilar Father):** Each mother receives a different father, selected for maximum objective-space distance via top-3 candidates + binary tournament by fitness.
- **H2 (Collective Criterion):** IVF cycles continue while average population fitness improves, rather than requiring a single offspring to beat the father.

The original v1 is preserved at:
```
src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2/
```
Class name: `IVFSPEA2`. Use v1 only for baseline comparisons or reproducing the original submission results.

`src/matlab/ivf_spea2/` is a **legacy mirror** — do NOT add it to the MATLAB path for canonical runs, as it will shadow the correct classes.

### Algorithm Components (MATLAB) — v2
- **IVFSPEA2V2.m** — Main PlatEMO ALGORITHM subclass. Runs the IVF v2 phase then standard SPEA2 GA operators each generation.
- **IVF_V2.m** — IVF v2 operator: dissimilar father selection per mother (H1), collective cycle continuation (H2), SBX crossover (eta_c=20).
- **CalFitness.m** — SPEA2 fitness: computes strength S(i), raw fitness R(i), and k-NN distance density D(i).
- **EnvironmentalSelection.m** — Selects archive by fitness < 1 (non-dominated), with distance-based truncation if over capacity.

Ablation variants in sibling directories: `IVFSPEA2-ABL-1C`, `IVFSPEA2-ABL-4C`, `IVFSPEA2-ABL-DOM`, `IVFSPEA2-P2-COMBINED` (factorial experiment harness).

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
MATLAB experiments → data/raw/          (gitignored, .mat files)
Python analysis   → data/processed/    (consolidated CSVs)
                  → results/figures/   (plots, gitignored)
                  → results/tables/    (LaTeX tables)
Paper build       → paper/build/       (gitignored PDF)
```

### Python Analysis (`src/python/analysis/`)
Scripts consume `data/processed/` CSVs and produce `results/`. Key scripts: `compute_iqr_tables.py`, `gen_graph.py`, `plot_sensitivity.py`, `analyze_engineering.py`, `script.py` (main runner). Uses `pymatreader` to load `.mat` files directly where needed.

### Metrics for new experiments

- All new experimental scripts (MATLAB or Python) must, at minimum, compute and persist both **IGD** and **HV** for every configuration/problem they evaluate.
- Additional metrics are welcome, but IGD and HV are mandatory baselines and must not be dropped.

### Submission Protocol
The current manuscript evidence model is summarized in `docs/IVFSPEA2_EVIDENCE_MODEL.md`.
Archived execution procedures remain under `archive/docs-procedural/`. Two submission tracks exist:

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
