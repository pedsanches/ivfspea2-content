# IVF/SPEA2 Knowledge Base

This document condenses the durable knowledge acquired during the development of
the current IVF/SPEA2 manuscript.

## Canonical identity

- Paper-facing name: `IVF/SPEA2`
- Canonical implementation class: `IVFSPEA2V2`
- Canonical MATLAB path:
  `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/`
- Current processed-data key: `IVFSPEA2`

The class name and the processed-data key are intentionally different:

- `IVFSPEA2V2` identifies the canonical implementation.
- `IVFSPEA2` identifies the normalized data label used by the current pipeline.

## Structural knowledge acquired from the v2 redesign

The current implementation is defined by two durable design changes.

### H1 - Dissimilar father per mother

Each mother receives a distinct father chosen from strong candidates with large
objective-space distance. This reduces offspring correlation and weakens the
density-based mutual penalization seen when many mothers share one father.

### H2 - Collective continuation criterion

IVF cycles continue while the average population fitness improves. This replaces
the earlier myopic rule that required a single offspring to beat the father.

## What changed from v1 to v2

| Aspect | v1 (`IVFSPEA2`) | v2 (`IVFSPEA2V2`) |
|---|---|---|
| Father selection | one shared random father | per-mother dissimilar father |
| Continuation rule | single offspring must beat father | average population fitness must improve |
| Father pool | implicit | top 50 percent by fitness, refreshed each cycle |
| Default operational profile | stronger EAR defaults | budget-controlled C26 profile |

## Discovery knowledge

### Phase 1 screening

- `H1` and `H2` were promoted.
- `H5` was rejected.

### Phase 2 factorial study

- `H1 + H2` formed the best-ranked combination.
- Three-or-more-factor combinations tended to degrade performance.
- The useful signal was interaction structure, not a strong omnibus superiority
  result.

### Phase 3 full-suite validation

- Against canonical `SPEA2`, v2 achieved `25/25/1` on `IGD` and `28/21/2` on
  `HV` across the 51-instance synthetic suite.
- Against v1, the result is near-equivalence with one persistent loss, so the
  redesign should be framed as a refinement rather than a dramatic leap.

## Tuning knowledge

The promoted default configuration is `C26`:

- `C = 0.12`
- `R = 0.225`
- `M = 0.3`
- `V = 0.1`
- `Cycles = 2`

Why `C26` was kept:

- it survives the A/B/C tuning pipeline;
- it is not contradicted by the direct `C26` vs `A43` head-to-head check;
- it preserves the current bounded-improvement profile without introducing a new
  corrected-significance loss against the selected tuning center.

## Known limitation

### WFG2(M=3)

`WFG2(M=3)` remains the main structural weakness.

- The issue is linked to disconnected Pareto geometry.
- The penalty appears most clearly in `IGD`.
- This failure mode persists across tested variants, so it should be treated as
  a genuine limitation of the current hybrid rather than as a tuning accident.

## Evidence and data knowledge

Current paper-facing processed sources:

- `data/processed/todas_metricas_consolidado.csv`
- `data/processed/todas_metricas_consolidado_with_modern.csv`
- `results/engineering_suite/engineering_suite_raw_main.csv`
- `results/engineering_suite/engineering_suite_summary_main.csv`
- `results/engineering_suite/engineering_suite_pairwise_main.csv`

Archived raw/supportive sources retained for provenance:

- `data/legacy/ablation_v2/phase1/`
- `data/legacy/ablation_v2/phase2/`
- `data/legacy/ablation_v2/phase3/`
- `data/legacy/tuning_ivfspea2v2/phaseA/`
- `data/legacy/tuning_ivfspea2v2/phaseB/`
- `data/legacy/tuning_ivfspea2v2/phaseC/`

## Interpretation rule

The current manuscript is strongest when it is read as follows:

- `IVF/SPEA2` is a memetic intensification module that improves its host
  `SPEA2` on many synthetic instances under fixed budgets;
- the gains are real but bounded;
- transfer to engineering problems is mixed and must stay framed as external
  support rather than universal practical superiority.
