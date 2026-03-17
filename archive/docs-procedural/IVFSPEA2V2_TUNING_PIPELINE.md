# IVFSPEA2V2 Tuning Pipeline (Integrity-First)

This document defines the dedicated parameter-tuning workflow for `IVFSPEA2V2`.

Scope:
- algorithm: `IVFSPEA2V2`
- metrics: **IGD + HV** (mandatory)
- phases: A (activation/collection), B (operator), C (local joint refinement)

Semantic note:
- These are **Tuning phases (A/B/C)** and are different from the
  **Discovery phases (1/2/3)** used in the v2 ablation work.
- See `docs/IVFSPEA2V2_EXPERIMENT_TRACKS.md` for naming and separation rules.

Primary runner:
- `scripts/experiments/run_ivfspea2v2_tuning.m`

Integrity and analysis:
- `scripts/experiments/verify_ivfspea2v2_tuning_integrity.py`
- `src/python/analysis/analyze_ivfspea2v2_tuning.py`

---

## 1) Phase design

### Phase A — AR grid for activation/collection
- Purpose: tune IVF activation and collection while isolating EAR effects.
- Fixed operator: AR (`M=0`, `V=0`, `EARN=0`).
- Grid:
  - `R ∈ {0.05, 0.10, 0.15, 0.20}`
  - `C ∈ {0.07, 0.11, 0.16, 0.21}`
  - `Cycles ∈ {2, 3, 4}`

### Phase B — EAR operator comparison at fixed center
- Purpose: compare operator families at a fixed (`R`,`C`,`Cycles`) center.
- Profiles:
  - `B01`: AR control
  - `B02`: EAR light (`M=0.3`, `V=0.1`)
  - `B03`: EAR medium (`M=0.5`, `V=0.2`)
  - `B04`: EAR strong (`M=0.7`, `V=0.3`)
  - `B05`: EARN (`M=0.5`, `V=0.2`, `EARN=1`)

### Phase C — local refinement around selected center
- Purpose: refine (`R`,`C`) around a selected center and re-check AR/EAR/EARN profiles.
- Center defaults: `R=0.10`, `C=0.11`, `Cycles=3` (override via env vars).
- Local grids:
  - `R_center ± 0.025`
  - `C_center + {-0.04, 0, +0.05}`
  - profiles: AR, EAR light, EAR medium, EARN

---

## 2) Problem sets

Runner supports:
- `SENTINEL` (default): `ZDT1_M2`, `WFG4_M2`, `DTLZ7_M3`, `WFG2_M3`, `MaF5_M3`
- `FULL12`: the 12-problem representative set used in v2 ablation context

Optional filter:
- `V2_TUNE_PROBLEMS=ZDT1_M2,WFG2_M3,...`

---

## 3) Data layout and manifests

Outputs are phase-isolated:
- `data/tuning_ivfspea2v2/phaseA/`
- `data/tuning_ivfspea2v2/phaseB/`
- `data/tuning_ivfspea2v2/phaseC/`

Each case folder:
- `IVFSPEA2V2_<ConfigID>_<ProblemTag>/`

Manifests (used by integrity checks):
- `results/tuning_ivfspea2v2/manifest_phaseA_configs.csv`
- `results/tuning_ivfspea2v2/manifest_phaseA_problems.csv`
- `results/tuning_ivfspea2v2/manifest_phaseA_cases.csv`
- (same pattern for phases B/C)

Run-ID integrity design:
- case-specific disjoint run IDs are generated deterministically from
  `(phase, config_index, problem_index, runs_per_case)`.
- This prevents collisions when multiple groups run concurrently.

---

## 4) Execution

### 4.1 Print launch commands for a phase
```bash
scripts/experiments/launch_ivfspea2v2_tuning.sh A 4
```

### 4.2 Start all groups in background
```bash
LAUNCH_MODE=run scripts/experiments/launch_ivfspea2v2_tuning.sh A 4
```

### 4.3 Run directly (single group)
```bash
V2_TUNE_PHASE=A V2_TUNE_GROUP=G1 V2_TUNE_NUM_GROUPS=4 \
V2_TUNE_RUNS=30 V2_TUNE_MAXFE=50000 V2_TUNE_PROBLEM_SET=SENTINEL \
matlab -batch "run('scripts/experiments/run_ivfspea2v2_tuning.m')"
```

---

## 5) Integrity verification

Fast check (samples one file per folder for IGD/HV payload):
```bash
python3 scripts/experiments/verify_ivfspea2v2_tuning_integrity.py --phase ALL
```

Full metric payload scan:
```bash
python3 scripts/experiments/verify_ivfspea2v2_tuning_integrity.py --phase ALL --full-metric-scan
```

---

## 6) Analysis and recommendation

```bash
python3 src/python/analysis/analyze_ivfspea2v2_tuning.py --phases A,B,C
```

To prepare Phase B center directly from completed Phase A ranking:

```bash
python3 scripts/experiments/prepare_ivfspea2v2_phase_b.py
set -a && source results/tuning_ivfspea2v2/phaseB_center_from_phaseA.env && set +a
LAUNCH_MODE=run V2_TUNE_WORKERS=6 scripts/experiments/launch_ivfspea2v2_tuning.sh B 3
```

Equivalent helper launcher:

```bash
LAUNCH_MODE=run V2_TUNE_WORKERS=6 scripts/experiments/launch_ivfspea2v2_phaseB_from_phaseA.sh 3
```

Main outputs:
- `results/tuning_ivfspea2v2/tuning_runs.csv`
- `results/tuning_ivfspea2v2/tuning_case_summary.csv`
- `results/tuning_ivfspea2v2/tuning_problem_ranking.csv`
- `results/tuning_ivfspea2v2/tuning_phase_ranking.csv`
- `results/tuning_ivfspea2v2/tuning_recommendations.csv`

Post-Phase-C promotion head-to-head (C winner vs A center vs v1 baseline):

```bash
.venv/bin/python src/python/analysis/analyze_ivfspea2v2_tuning_head_to_head.py
```

Head-to-head outputs:
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_igd.csv`
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_hv.csv`
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_summary.json`
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_report.md`

Ranking rule:
- per `(phase, problem)`: rank by IGD (ascending) and HV (descending)
- normalized combined rank = mean of normalized IGD/HV ranks
- phase recommendation = best mean combined rank with full coverage

Promotion rule:
- Tuning progression remains incremental (`A -> B -> C`), so the promoted
  tuning candidate is selected from **Phase C**.
- The post-Phase-C head-to-head is a validation gate used to ensure the
  promoted C candidate is not contradicted by direct pairwise evidence against
  the A center and IVF/SPEA2 v1 baseline.

---

## 7) Reproducibility checklist

- Use only canonical `IVFSPEA2V2` path under PlatEMO.
- Keep `IGD` and `HV` in every run (`metName` includes both).
- Keep manifests and inventory files generated by runner.
- Run integrity check before any statistical comparison/reporting.
- Prefer `SENTINEL` for screening and `FULL12` for promotion confirmation.
