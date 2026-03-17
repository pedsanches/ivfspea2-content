# WS3 - Comparison and Statistics Freeze

Date: 2026-03-09
Status: Frozen for current manuscript
Related files:

- `docs/submission_rerun_protocol_v2.md`
- `results/submission_release_manifest.csv`
- `results/submission_claim_traceability.md`
- `results/submission_comparability_matrix.csv`
- `results/submission_statistics_traceability.md`

## Purpose

WS3 freezes the rules that make the paper's comparisons scientifically fair and
its inferential claims statistically honest.

This workstream does not create stronger evidence by itself. It prevents the
manuscript from overstating what the existing evidence means.

## Frozen scientific question hierarchy

### Q1 - Main confirmatory question

Does `IVF/SPEA2` improve its own host, canonical `SPEA2`, on the synthetic
benchmark suite under fixed evaluation budgets?

This is the only question that receives full confirmatory treatment.

### Q2 - Secondary support question

Does `HV` broadly agree with the main synthetic pattern found under `IGD`?

This is supporting evidence, not the driver of the primary claim.

### Q3 - Exploratory positioning question

How does `IVF/SPEA2` compare with the other seven baselines across synthetic
instances?

This is exploratory positioning, not a multiplicity-controlled headline claim.

### Q4 - Transferability question

Does the synthetic pattern transfer to a small engineering suite under strict
common-run processing?

This is external-support evidence, not the core confirmatory family.

### Q5 - Design-justification question

Do tuning and ablation results justify the promoted implementation and help
interpret when it helps or fails?

This is supportive evidence only.

## Frozen inferential policy

## 1. Synthetic confirmatory family

- Comparison: `IVF/SPEA2` vs `SPEA2`
- Scope: 51 synthetic instances; primary emphasis on the 39 out-of-sample
  instances outside `FULL12`
- Cohort rule: `IVFSPEA2` run IDs `3001..3060`, baselines `1..60`
- Endpoint: `IGD`
- Test: two-sided Wilcoxon rank-sum per instance
- Multiplicity control: Holm--Bonferroni, applied separately within `M=2` and
  `M=3`
- Reporting layers:
  - unadjusted full suite;
  - unadjusted OOS;
  - Holm full suite;
  - Holm OOS.

Allowed wording:

- `confirmatory`, `primary claim`, `Holm-corrected`, `out-of-sample primary evidence`.

Not allowed:

- claiming global superiority over all baselines from this family;
- treating `FULL12` and `OOS` as equally strong evidence layers.

## 2. Synthetic secondary indicator family

- Comparison: `IVF/SPEA2` vs `SPEA2`
- Endpoint: `HV`
- Same filtered synthetic cohort as the IGD family
- Same instance-wise Wilcoxon and Holm machinery is available
- Interpretation rule: `HV` can support, nuance, or flag disagreement with the
  primary `IGD` claim, but it does not replace `IGD` as the primary endpoint.

Honest reading:

- if `HV` disagrees on specific instances, the disagreement must be reported;
- `HV` agreement strengthens confidence, but `HV` alone must not rescue a weak
  primary `IGD` result.

## 3. Synthetic exploratory positioning family

- Comparisons: `IVF/SPEA2` vs all non-host baselines and global nine-algorithm
  rankings
- Artifacts: detailed tables, `A12` heatmaps, Friedman average-rank figure
- Tests: unadjusted pairwise Wilcoxon in tables; Friedman ranking for navigation
- Interpretation rule: exploratory only.

Honest reading:

- these analyses are useful for context and regime interpretation;
- they do not justify a family-wise-corrected claim that `IVF/SPEA2` is broadly
  best among modern baselines.

## 4. Engineering transferability family

- Problems: `RWMOP9`, `RWMOP21`, `RWMOP8`
- Pre-processing: strict common-run matching before metric comparison
- Metrics: `IGD` against empirical Pareto front; `HV` against problem reference
  point
- Tests: problem-wise Wilcoxon rank-sum vs `IVF/SPEA2`
- Multiplicity: none frozen for this family
- Interpretation rule: external-support / transferability only.

Honest reading:

- this family is intentionally smaller and weaker than the synthetic family;
- `RWMOP8` has heterogeneous valid-run coverage and therefore lower evidential
  strength;
- engineering evidence can support bounded transferability but not universal
  real-world effectiveness.

## 5. Tuning and ablation families

- Tuning (`FULL12`, 30 runs, `FE=50000`) is supportive and selection-oriented;
- Ablation Phase 1 and Phase 3 are supportive;
- Ablation Phase 2 is descriptive only because the Friedman omnibus is
  non-significant.

Not allowed:

- turning the H1xH2 interaction into a confirmatory headline claim;
- presenting v2-vs-v1 near-equivalence as decisive proof of a major redesign
  advantage.

## Frozen comparability rules

## Shared rules for synthetic comparisons

- Same evaluation budget: `FE_max = 100000`
- Same run target: `60`
- Same platform: PlatEMO
- Same default-vs-default policy: no per-benchmark retuning in the main
  evaluation
- Mandatory metrics preserved: `IGD` and `HV`

## Population-size rule

- Fixed population size is `N=100` for the fixed-population cases.
- Honest caveat: `NSGA-III` and `MOEA/D` are explicit exceptions because their
  PlatEMO implementations synchronize population size with reference points or
  weight vectors.

This does not invalidate the study, but it must remain documented as a platform
constraint rather than hidden under a false claim of strict identical `N` for
all algorithms.

## Cohort rule for synthetic evidence

- The raw consolidated synthetic CSV is mixed-track for `IVFSPEA2`.
- This is visible in `results/tables/run_cohort_summary.csv` and
  `results/tables/run_cohort_anomalies.csv`.
- Therefore, raw consolidated files are not claim-eligible by themselves.
- Claim-eligible synthetic artifacts are only those regenerated through the
  submission cohort filter.

## Common-run and valid-run rules for engineering evidence

- Common runs are selected first, per problem, across all algorithms.
- Metrics are then computed on those selected runs.
- Valid-run counts are reported explicitly because feasibility can differ.
- Pairwise engineering interpretation must mention coverage asymmetry whenever
  `n_valid` is materially below the common-run target.

## Frozen honesty constraints

The following statements are scientifically acceptable:

- `IVF/SPEA2` improves `SPEA2` on many synthetic `M=2` and `M=3` instances.
- The strongest evidence is the Holm-corrected OOS IGD comparison.
- `HV` is broadly supportive but not identical in every case.
- Multi-baseline results are exploratory.
- Engineering evidence is a transferability check with explicit limitations.
- H1/H2 are supported as implementation refinements, not decisively validated as
  the paper's strongest claim.

The following statements are not scientifically acceptable:

- `IVF/SPEA2` is generally best among all tested algorithms.
- The engineering suite confirms broad practical superiority.
- H1/H2 are decisively proven by the current ablation.
- The raw consolidated CSV alone is a clean canonical evidence source.

## Remaining honest caveats after WS3

1. `results/tables/run_cohort_summary.csv` still shows raw mixed-track
   `IVFSPEA2` groups in the consolidated CSV. This is acceptable only because
   confirmatory paper artifacts are built from the filtered cohort, not from the
   raw aggregate alone.
2. `RWMOP8` remains weaker evidence because valid-run counts differ sharply
   across algorithms.
3. Exploratory multi-baseline claims remain unadjusted.
4. Ablation Phase 2 remains descriptive because the omnibus test is
   non-significant.

## WS3 definition of done

WS3 is complete when all answers below are `yes`.

- Is the primary confirmatory family explicitly limited to `IVF/SPEA2` vs
  `SPEA2` on synthetic data?
- Are `IGD` and `HV` clearly separated into primary and secondary roles?
- Are multi-baseline results clearly marked exploratory?
- Are engineering results clearly marked as external-support evidence with
  common-run and valid-run rules?
- Are tuning and ablation clearly marked supportive?
- Can every comparison block be traced to a frozen cohort rule and test policy?

If any answer is `no`, WS3 is not complete.
