# Submission Statistics Traceability

Date: 2026-03-09
Status: WS3 frozen

## Inferential families

### Family F1 - Synthetic host comparison

- Question: does `IVF/SPEA2` improve `SPEA2` on synthetic benchmarks?
- Endpoint: `IGD`
- Unit of inference: benchmark instance
- Test: two-sided Wilcoxon rank-sum on run-level values
- Correction: Holm--Bonferroni within `M=2` and within `M=3`
- Strongest reporting layer: `Holm, OOS`
- Canonical artifacts:
  - `results/tables/claims_summary_audit.csv`
  - `results/tables/claims_summary_instance_details.csv`

### Family F2 - Synthetic secondary confirmation

- Question: does `HV` broadly support the synthetic host-comparison pattern?
- Endpoint: `HV`
- Test/correction: same instance-wise machinery as F1 when summarized
- Interpretation: supporting only
- Canonical artifacts:
  - `results/tables/claims_summary_audit.csv`
  - `results/tables/hv_per_instance_M2.tex`
  - `results/tables/hv_per_instance_M3.tex`

### Family F3 - Exploratory synthetic positioning

- Question: how does `IVF/SPEA2` compare to the wider baseline set?
- Endpoints: `IGD`, `HV`, `A12`, ranks
- Tests: unadjusted pairwise Wilcoxon in detailed tables; Friedman for global
  navigation
- Correction: none frozen for this family
- Interpretation: exploratory only
- Canonical artifacts:
  - `results/tables/igd_m2_detailed_with_modern_table.tex`
  - `results/tables/igd_m3_detailed_with_modern_table.tex`
  - `paper/figures/friedman_avg_rank_igd.pdf`
  - `paper/figures/heatmap_a12_M2.pdf`
  - `paper/figures/heatmap_a12_M3.pdf`

### Family F4 - Engineering transferability

- Question: does the synthetic pattern transfer to a small engineering suite?
- Endpoints: `IGD_PF`, `HV`
- Test: two-sided Wilcoxon rank-sum vs `IVF/SPEA2` per problem/metric
- Correction: none frozen for this family
- Additional rule: strict common-run matching before metric computation; valid
  run counts must be reported
- Interpretation: external-support only
- Canonical artifacts:
  - `results/engineering_suite/engineering_suite_pairwise_main.csv`
  - `results/engineering_suite/engineering_suite_summary_main.csv`
  - `results/tables/engineering_metric_profiles_summary.csv`

### Family F5 - Tuning and ablation support

- Question: do the chosen defaults and H1/H2 design decisions have supportive
  backing?
- Endpoints/tests: track-specific
- Correction: track-specific, but no frozen confirmatory manuscript family
- Interpretation: supportive only; Phase 2 ablation remains descriptive because
  the omnibus test is non-significant
- Canonical artifacts:
  - `results/ablation_v2/phase1/phase1_summary.csv`
  - `results/ablation_v2/phase2/phase2_pairwise_adjusted.csv`
  - `results/ablation_v2/phase3/phase3_raw_metrics.csv`

## Red-line wording rules

- F1 may support `robust but bounded improvement over SPEA2`.
- F2 may support `secondary qualitative confirmation`.
- F3 may support `exploratory competitive positioning`.
- F4 may support `transferability check with mixed outcomes`.
- F5 may support `implementation justification`.

The manuscript must not use F3, F4, or F5 to make stronger claims than F1.

## Honest unresolved constraints

- The synthetic consolidated CSV is mixed-track before filtering.
- `NSGA-III` and `MOEA/D` are explicit population-policy exceptions under
  PlatEMO.
- Engineering evidence is weaker than synthetic evidence because it is smaller
  and, on `RWMOP8`, coverage is heterogeneous.
