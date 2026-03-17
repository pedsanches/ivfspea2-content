# IVF/SPEA2 Evidence Model

This document condenses the durable evidence logic behind the current
manuscript. It states what the repository's frozen artifacts justify and what
they do not justify.

## Evidence hierarchy

### 1. Main confirmatory evidence

Question:

- does `IVF/SPEA2` improve canonical `SPEA2` on the synthetic benchmark suite
  under fixed evaluation budgets?

Frozen basis:

- processed source: `data/processed/todas_metricas_consolidado_with_modern.csv`
- cohort filter: `src/python/analysis/cohort_filter.py`
- retained synthetic cohort:
  - `IVFSPEA2` runs `3001..3060`
  - baseline runs `1..60`
  - no `RWMOP*` rows

Primary endpoint:

- `IGD`

Secondary supporting endpoint:

- `HV`

## Supportive evidence families

### Exploratory multi-baseline positioning

- useful for context and regime interpretation;
- not a family-wise-corrected headline claim.

### Engineering transferability

- based on strict common-run processing;
- supportive only;
- weaker than the synthetic evidence because the suite is smaller and coverage is
  heterogeneous on some problems.

### Tuning and ablation

- justify the promoted implementation and parameter profile;
- support interpretation;
- do not replace the main host-comparison claim.

## Frozen defaults and scope

- canonical class: `IVFSPEA2V2`
- paper-facing label: `IVF/SPEA2`
- defaults: `C=0.12`, `R=0.225`, `M=0.3`, `V=0.1`, `Cycles=2`
- synthetic scope: 51 instances across `ZDT`, `DTLZ`, `WFG`, and `MaF`
- engineering scope: `RWMOP9`, `RWMOP21`, `RWMOP8`

## Comparability constraints that matter

- same synthetic evaluation budget: `100000` function evaluations;
- same target run count: `60`;
- same platform: PlatEMO;
- same default-vs-default comparison policy;
- `IGD` and `HV` remain mandatory together.

PlatEMO caveat:

- `NSGA-III` and `MOEA/D` are explicit population-policy exceptions because
  their effective population size follows reference points or weight vectors.

## Honest caveats

- the raw consolidated synthetic CSV is mixed-track before cohort filtering;
- engineering evidence must stay separate from synthetic confirmatory claims;
- `RWMOP8` carries lower evidential strength because valid-run coverage is more
  uneven;
- the ablation supports implementation refinement, not a decisive stand-alone
  proof of the paper's strongest claim.

## Wording guardrails

Scientifically supported:

- `robust but bounded improvement over SPEA2`
- `secondary HV support`
- `exploratory multi-baseline positioning`
- `transferability check with mixed outcomes`
- `implementation justification`

Not scientifically supported:

- `generally best among all tested algorithms`
- `broad practical superiority`
- `decisively proven mechanism`
- `clean canonical evidence directly from the raw consolidated CSV`

## Human-readable evidence index

For claim-to-artifact mapping and verified headline numbers, see:

- `results/SUBMISSION_EVIDENCE_MAP.md`
