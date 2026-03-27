# PPSN 2026 Meta-Review Action Plan

Last updated: 2026-03-27

## Objective

Convert the strategic meta-review into a submission rescue plan that is:

- evidence-constrained
- deadline-aware
- easy to execute incrementally
- explicit about what will and will not be done before submission

This plan assumes the current target is the PPSN 2026 submission deadline on
2026-03-28 AoE.

## Operating Principles

1. Correct factual errors before adding new claims.
2. Reduce claims to the current evidence surface before considering new
   experiments.
3. Integrate existing repository evidence before launching expensive reruns.
4. Prefer framing fixes over method inflation when time is short.
5. Treat the controller as a proof-of-concept unless out-of-sample validation
   is completed.
6. Every manuscript claim must map to a concrete artifact in `results/`,
   `data/processed/`, or source code.

## Evidence Already Available

These artifacts already support high-value fixes and should be used before any
new experimentation:

- Modern baseline context:
  `results/tables/pairwise_vs_spea2_with_modern.csv`
- Modern baseline HV context:
  `results/tables/pairwise_vs_spea2_with_modern_hv.csv`
- Direct IVF vs modern algorithms:
  `results/tables/pairwise_ivf_vs_all.csv`
- Direct IVF vs modern algorithms on HV:
  `results/tables/pairwise_ivf_vs_all_hv.csv`
- Runtime and overhead:
  `results/tables/runtime_overhead_baselines.csv`
  `results/tables/runtime_modern_summary.csv`
- Static FLA ablation without structural metadata:
  `results/tables/fla_model_comparison.csv`
- Dynamic-signal main tests:
  `results/tables/dynamic_signal_main_tests.csv`
- Dynamic-signal threshold performance:
  `results/tables/dynamic_signal_loocv.csv`
- Dynamic-signal sensitivity:
  `results/tables/dynamic_signal_sensitivity.csv`
- Controller case-level comparison:
  `data/processed/ppsn_controller_comparison.csv`

## Critical Path

The work is organized into four execution lanes.

### Lane 0 - Submission Hygiene

Goal: remove avoidable credibility losses.

Tasks:

- [x] Fill `\institute` in `paper/ppsn2026/main.tex`
- [ ] Add ORCID if desired by the author metadata style
- [x] Add a short data/code availability statement
- [x] Replace colored links with `hidelinks`
- [x] Fix bibliography entry type for `mersmann2011exploratory`
- [x] Remove uncited references
- [x] Shorten and de-densify the abstract if page pressure appears

Exit criteria:

- No placeholders remain in author metadata
- No LNCS compliance issue is visible in the preamble
- No obvious BibTeX warnings remain

### Lane 1 - Factual and Framing Corrections

Goal: eliminate the strongest reviewer objections without changing the study's
core evidence.

Tasks:

- [x] Correct the IVF trigger description in `paper/ppsn2026/main.tex`
      to match the code in
      `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/IVF_V2.m`
- [x] Rename the mutation-fraction symbol so it no longer collides with the
      number-of-objectives symbol
- [x] Replace "online control" / "adaptive" wording with
      "reactive warmup-based switching", "one-shot warmup controller",
      or similarly precise language
- [x] Reframe the controller section as a proof-of-concept, not a full AOS
      contribution
- [x] Define archive turnover explicitly the first time it appears
- [x] Harmonize FDR language across sections
- [x] Round the threshold value to a defensible precision in prose

Exit criteria:

- No statement in the manuscript contradicts the code
- No section claims continuous adaptation when only one irreversible decision
  is made after warmup
- Terminology is internally consistent

### Lane 2 - Evidence Integration

Goal: answer the highest-value reviewer criticisms using evidence already in the
repository.

Tasks:

- [x] Add a compact "competitive context" paragraph using modern baselines
- [x] Add a compact runtime/overhead paragraph
- [x] Add a static-FLA ablation paragraph explaining the drop from
      `r_s = 0.374` to `r_s = 0.314` without structural metadata
- [x] Add an imbalance-aware sentence comparing against trivial always-on
      behavior
- [x] Add a sensitivity sentence noting that `early_frac = 0.10` loses BH
      significance
- [x] Make clear which modern-baseline comparisons are exploratory and which
      claims remain centered on IVF vs SPEA2

Exit criteria:

- The paper no longer appears isolated from modern MOEA context
- The FLA discussion no longer overstates bespoke feature conclusions
- The dynamic section acknowledges robustness limits directly

### Lane 3 - Minimum New Experiment

Goal: spend remaining time only on the experiment with the highest acceptance
delta per hour.

Primary target:

- [x] Out-of-sample controller validation by family-wise split
- [x] Out-of-family validation for the turnover threshold rule from existing case summaries

Suggested protocol:

1. For each held-out family, calibrate the turnover threshold using only the
   training families.
2. Evaluate the fixed threshold on the held-out family.
3. Report balanced accuracy for the threshold rule and aggregate controller
   behavior conservatively.
4. If results are unstable, keep them in limitations rather than forcing a
   positive claim.

Do not start before Lanes 0-2 are complete unless this work is already mostly
implemented.

Exit criteria:

- Either out-of-sample controller evidence is added
- Or the manuscript explicitly states that controller evaluation remains
  in-sample and is exploratory

## Priority Matrix

### P0 - Must Finish Before Submission

- [x] Metadata and LNCS hygiene
- [x] Correct IVF trigger description
- [x] Remove misleading "adaptive" / "online control" framing
- [x] Resolve symbol collision
- [x] Bibliography cleanup

### P1 - High Leverage, Low Risk

- [x] Add modern-baseline context
- [x] Add runtime/overhead analysis
- [x] Discuss structural-feature ablation
- [x] Discuss imbalance and always-on baseline
- [x] Discuss sensitivity to `early_frac`

### P2 - Only If Time Remains

- [x] Out-of-sample controller validation
- [ ] Random controller baseline
- [ ] Short AOS taxonomy paragraph distinguishing this work from PM/AP/MAB

### P3 - Explicitly Deferred

- [ ] Full AOS benchmark suite with PM, AP, FAUC-MAB
- [ ] Reimplementation of established MO-FLA frameworks for direct comparison
- [ ] Large new rerun campaign with additional algorithms

## Review-Issue Mapping

| Issue | Action | Lane | Status |
|------|--------|------|--------|
| A1 | Add modern-baseline context from existing tables | 2 | Done |
| A2 | Fix trigger description to budget gate | 1 | Done |
| A3 | Add OOS controller validation or downgrade claim | 3 | Done |
| A4 | Reframe as reactive warmup switch | 1 | Done |
| A5 | Downgrade AOS positioning; add taxonomy caveat | 1/3 | Done |
| A6 | Limit the scope of the static-FLA conclusion | 2 | Done |
| A7 | Discuss no-structural ablation result | 2 | Done |
| A8 | Acknowledge imbalance and trivial baseline | 2 | Done |
| A9 | Rename mutation fraction symbol | 1 | Done |
| A10 | Harmonize FDR policy | 1 | Done |
| A11 | Fill metadata and availability | 0 | Partial |
| A12 | Clean BibTeX entries | 0 | Done |
| A13 | Replace "memetic operator" if needed by stricter wording | 1 | Done |
| A14 | Reduce threshold precision in prose | 1 | Done |
| A15 | Shorten abstract if needed | 0 | Done |
| A16 | Define archive turnover | 1 | Done |
| A17 | Add runtime/overhead | 2 | Done |
| A18 | Use `hidelinks` | 0 | Done |
| A19 | Report or remove permutation-test references | 2 | Done (no references found) |
| A20 | Discuss sensitivity to `early_frac = 0.10` | 2 | Done |

## Daily Execution Loop

Run this loop until submission:

1. Open this plan and select one lane only.
2. Finish one coherent batch of edits.
3. Compile the paper.
4. Check page count and warnings.
5. Update the corresponding checkboxes and note any new blocker.
6. Commit only when the manuscript compiles cleanly and the batch is logically
   self-contained.

## Editing Order for `main.tex`

Recommended edit sequence:

1. Title, abstract, keywords
2. Introduction claims and contributions
3. IVF operator description
4. Static FLA discussion
5. Dynamic-signal section
6. Controller section
7. Conclusion and limitations
8. Metadata and bibliography

This order reduces rework because framing decisions made early will propagate
into later sections.

## Decision Rules

Use these rules to avoid spending time on low-yield work:

- If a fix can be solved by wording, do not start a new experiment.
- If a criticism can be answered with an existing table, integrate the table.
- If a result is weak or unstable, move it to limitations instead of defending
  it aggressively.
- If controller OOS validation is not ready by the last editing window before
  submission, freeze the controller as exploratory and stop expanding it.
- Do not claim "adaptive operator selection" unless the implementation
  actually updates decisions during the run.

## Immediate Execution Sequence

Recommended next actions:

1. Finish Lane 0 and Lane 1 completely.
2. Patch Lane 2 with the evidence already available in `results/tables/`.
3. Recompile and inspect page budget.
4. Only then decide whether Lane 3 is still worth attempting.

## Definition of Done

The manuscript is ready to submit when all of the following are true:

- [x] All P0 items are closed
- [x] At least three P1 items are closed
- [x] The controller is framed conservatively
- [x] The manuscript compiles cleanly
- [x] No statement contradicts the implementation or the evidence artifacts
- [x] The conclusion matches the paper's actual empirical support
