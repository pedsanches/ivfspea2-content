# Memetic Computing Submission Master Plan

Date: 2026-03-09
Status: Draft control plan
Target journal: Springer `Memetic Computing`
Primary manuscript: `paper/src/sn-article.tex`

## Objective

Deliver a submission-ready article package that is scientifically defensible,
editorially compliant, and auditable from raw runs to final claims.

The final outcome is not only a compiled PDF, but a frozen evidence package with
clear provenance, reproducible comparisons, and a manuscript whose claims match
what the data actually support.

## What this plan controls

- scientific framing and claim discipline;
- canonical data selection and provenance;
- fairness and integrity of algorithm comparisons;
- regeneration of tables and figures from canonical evidence only;
- manuscript revision for submission readiness;
- final packaging and go/no-go gates.

This document is the umbrella plan. Detailed tactical documents remain active and
should be used as companions, not replacements:

- `SPRINGER_MEMETIC_COMPUTING_REVIEW.md`
- `SPRINGER_MEMETIC_COMPUTING_REVIEW_CLAUDE.md`
- `docs/article_audit_2026-03-04.md`
- `docs/IVF_V2_CONSOLIDATION.md`
- `docs/IVFSPEA2V2_EXPERIMENT_TRACKS.md`
- `docs/submission_rerun_protocol.md`
- `docs/springer_graphics_tables_compliance.md`
- `data/CURRENT_DATA_MANIFEST.md`

## Submission success criteria

The paper is ready to submit only when all items below are true:

1. Every main claim is traceable to a canonical table, figure, or script output.
2. No table or figure mixes discovery, tuning, submission, or legacy cohorts.
3. Primary and secondary metrics are both preserved for every final experiment:
   `IGD` and `HV`.
4. Pairwise comparisons use explicit common-run and valid-run rules.
5. Confirmatory claims are clearly separated from exploratory interpretation.
6. Method text, flowchart, pseudocode, and canonical code path are 1:1 aligned.
7. The manuscript is technically compliant with Springer single-file submission
   expectations and compiles cleanly enough for submission.
8. The final package includes a release manifest and checksum record.

## Non-negotiable integrity rules

### Data integrity

- Freeze one canonical evidence line for the paper before any final text update.
- Do not mix data across tracks defined in `docs/IVFSPEA2V2_EXPERIMENT_TRACKS.md`.
- Do not mix historical runs with isolated submission reruns.
- Any regenerated processed CSV must declare exact raw inputs, run ranges, tags,
  script name, and generation timestamp.
- All final manuscript artifacts must be reproducible from tracked scripts plus
  canonical input manifests.
- Any manual patch to a generated table or figure is forbidden; regenerate
  instead.

### Comparison integrity

- Keep `IGD` as the primary endpoint and `HV` as mandatory secondary support.
- Use the same FE budget, stopping rules, run count policy, and reporting window
  across compared algorithms unless a deviation is explicitly justified.
- Keep baseline settings on an explicit policy: either default-vs-default or
  re-tuned-vs-re-tuned. Do not drift between policies inside the same paper.
- Apply common-run matching whenever coverage differs across algorithms.
- When feasibility differs, report valid-run counts in the same table/figure or
  immediately adjacent text.
- Multiplicity control must be stated up front for confirmatory claims.
- Exploratory multi-baseline ranking or interaction analyses must be labeled as
  exploratory everywhere they appear.

### Claim integrity

- No title, abstract, or conclusion claim may be stronger than the strongest
  confirmatory evidence layer.
- If `v2` is near-equivalent to `v1`, the paper must not sell H1/H2 as
  decisively validated unless new confirmatory evidence is produced.
- Runtime overhead must be discussed wherever performance gains are summarized.
- Negative cases stay in the paper; they are not optional.

## Canonical source map to freeze before final revision

This is the minimum source-of-truth map that must be locked and documented.

| Layer | Canonical item | Required action |
|---|---|---|
| Display name | `IVF/SPEA2` | Keep consistent in paper text |
| Canonical implementation | `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/` | Verify path precedence before reruns |
| Canonical class | `IVFSPEA2V2` | State explicitly in code availability and methods |
| Current data key | `IVFSPEA2` in `data/CURRENT_DATA_MANIFEST.md` | Document naming bridge so readers do not confuse v1/v2 |
| Main manuscript | `paper/src/sn-article.tex` | Use as editable source until final flattening |
| Current reviews | `SPRINGER_MEMETIC_COMPUTING_REVIEW.md`, `SPRINGER_MEMETIC_COMPUTING_REVIEW_CLAUDE.md` | Treat as blocker list |

Before final submission, add a short naming note to the manuscript or
supplementary reproducibility section explaining the mapping between display
name, class name, and data key.

## Workstreams and gates

## WS1 - Freeze the scientific story

Goal: make the paper honest, sharp, and review-resistant before polishing.

Tasks:

- Reframe the headline contribution around the strongest supported claim.
- Decide whether H1/H2 stay in the title or move to method-level detail.
- Rewrite abstract, introduction, discussion, and conclusion so they all use the
  same evidence hierarchy.
- Add an explicit confirmatory vs exploratory map for each major result block.
- Define one sentence on when the runtime overhead is acceptable in practice.

Exit gate:

- The title, abstract, contributions list, and conclusion are mutually aligned.
- A skeptical reviewer cannot point to a stronger claim in the title than in the
  confirmatory tables.

Primary blockers from current reviews:

- H1/H2 framing is too strong relative to evidence.
- Runtime-overhead vs gain discussion is incomplete.
- Practical positioning vs modern baselines needs tighter wording.

## WS2 - Freeze canonical evidence and provenance

Goal: ensure every final result comes from a single auditable evidence line.

Tasks:

- Decide the exact canonical submission track for the paper's main evidence.
  For the current manuscript, this should be the v2/C26 line; v1 remains only a
  reference or ablation comparator.
- Create or update a dedicated submission protocol document for the final v2
  evidence if the current protocol still reflects the older v1 submission line.
- Record run ranges, tags, benchmark scope, seeds/run IDs, and mandatory metrics.
- Build a release manifest with: artifact, producer script, raw input roots,
  processed inputs, run range, tag, date, and status.
- Generate a checksum file for canonical processed data and paper-consumed
  outputs.
- Verify that every paper-consuming CSV or table is derived only from canonical
  submission evidence, not from mixed historical datasets.

Recommended release artifacts to create during this workstream:

- `results/submission_release_manifest.csv`
- `results/submission_release_checksums.sha256`
- `results/submission_claim_traceability.md`

Exit gate:

- Every final artifact has one provenance path from raw runs to manuscript.
- No manuscript-consuming artifact is marked mixed, legacy, or ambiguous.
- The final evidence line can be rebuilt without manual intervention.

Hard checks:

- Verify MATLAB path precedence with `which IVFSPEA2V2 -all`.
- Keep `IGD` and `HV` for all new or regenerated final experiments.
- Do not update manuscript claims before the evidence freeze is complete.

## WS3 - Lock comparison fairness and statistics

Goal: make every comparison defensible under reviewer scrutiny.

Tasks:

- Write a one-page comparability matrix for all main baselines covering:
  population policy, FE budget, run count, parameter policy, constraint/validity
  handling, and indicator set.
- State explicitly which claims are confirmatory and which are exploratory.
- Preserve Holm-Bonferroni control for the main pairwise claim vs `SPEA2`.
- Define the trimmed-mean rule wherever it is reported.
- Require common-run matching whenever valid-run coverage differs.
- Add a compact engineering coverage matrix with valid runs per
  algorithm/problem.
- Add a short indicator-disagreement note whenever `IGD` and `HV` diverge.

Exit gate:

- A reviewer can reconstruct how every W/L/T count was computed.
- There is no silent asymmetry in run coverage, validity, or metric usage.
- The engineering section is transparent about missing or infeasible runs.

Minimum comparison policy for the final paper:

- Primary claim: pairwise vs `SPEA2`, `IGD`, Holm-corrected.
- Secondary confirmation: pairwise vs `SPEA2`, `HV`.
- Broader positioning: multi-baseline tables, ranks, and heatmaps labeled
  exploratory unless family-wise control is added.

## WS4 - Regenerate paper artifacts from frozen evidence

Goal: rebuild every paper-facing figure and table from the frozen evidence line.

Tasks:

- Regenerate synthetic benchmark tables and figures from canonical processed data.
- Regenerate engineering tables/figures with explicit valid-run annotations.
- Rebuild ablation tables only from the correct discovery-track roots.
- Ensure appendix tables are either readable in the manuscript or moved to
  supplementary material with clear references.
- Replace any stale figure that no longer matches the method, especially the
  flowchart.
- Record each regenerated artifact in the release manifest.

Key files to verify during this workstream:

- `paper/figures/flowchart.pdf`
- `paper/figures/boxplot_igd_m2.pdf`
- `paper/figures/boxplot_igd_m3.pdf`
- `paper/figures/engineering_metric_profiles.pdf`
- `paper/figures/engineering_fronts_rwmop9_rwmop8.pdf`
- `paper/figures/pareto_fronts.pdf`
- `results/tables/igd_m2_detailed_with_modern_table.tex`
- `results/tables/igd_m3_detailed_with_modern_table.tex`
- `results/ablation_v2/phase1/phase1_table.tex`
- `results/ablation_v2/phase3/phase3_igd_table.tex`
- `results/ablation_v2/phase3/phase3_hv_table.tex`

Exit gate:

- Every figure and table used in the paper is current, legible, and tied to the
  frozen evidence manifest.
- The flowchart, pseudocode, and code implementation all describe the same
  algorithm.

## WS5 - Revise the manuscript for journal readiness

Goal: convert good technical content into a paper that survives editorial and
reviewer screening.

Tasks:

- Flatten the submission manuscript into one `.tex` file to comply with the
  Springer template expectation.
- Remove or move overloaded appendix content that hurts readability.
- Tighten long results sections; keep evidence, remove repetition.
- Harmonize notation across text, tables, captions, and pseudocode.
- Add the missing trimmed-mean definition.
- Add the runtime trade-off discussion in Results or Discussion.
- Clarify the engineering-suite limitations and transferability scope.
- Check reference formatting consistency.

Required manuscript-level fixes already identified by audits:

- align title/novelty with actual evidence;
- update flowchart to current logic;
- fix pseudocode notation and object initialization;
- resolve `\input{...}` dependency for final submission form;
- improve crowded figures and appendix table formatting.

Exit gate:

- `paper/src/sn-article.tex` can be flattened into a compliant submission file.
- No critical review blocker remains open in the two Springer review documents.
- The manuscript reads as one coherent argument, not a collection of protocol
  notes.

## WS6 - Build, audit, and freeze the submission package

Goal: produce the exact package that can be uploaded.

Tasks:

- Build the paper and inspect the final PDF at print scale.
- Run Python tests relevant to the analysis pipeline.
- Run MATLAB tests relevant to the algorithm and experiment scripts.
- Prepare the final submission bundle: single-file manuscript, bibliography,
  figures, supplementary material, and release manifest.
- Perform a final claim-to-artifact audit using the traceability document.
- Perform a red-team review with one question only: "What is the strongest claim
  here that the evidence does not fully justify?"

Recommended verification commands:

```bash
python -m pytest tests/python/ -v
matlab -batch "run('tests/matlab/run_tests.m')"
make analysis
```

Build verification:

```bash
make -C paper clean
make -C paper
```

Exit gate:

- Final PDF builds successfully.
- No broken references or stale artifacts remain.
- Release manifest and checksum files are present.
- Submission package is ready without last-minute manual edits.

## Data integrity protocol for the final paper

Use the checklist below as a hard gate, not as a suggestion.

- [ ] One canonical submission track chosen and documented.
- [ ] Run ranges and tags frozen before final figure regeneration.
- [ ] Canonical raw roots listed explicitly.
- [ ] Processed CSV provenance recorded.
- [ ] Every final artifact linked to a producer script.
- [ ] Release checksums generated and stored.
- [ ] No legacy or mixed-cohort artifact used in the paper.
- [ ] `IGD` and `HV` both present for all final experiments.
- [ ] Engineering valid-run counts recorded.
- [ ] Any excluded run or problem has a documented reason.

## Comparison integrity protocol for the final paper

- [ ] One comparison policy frozen and stated explicitly.
- [ ] Same FE budget across compared algorithms.
- [ ] Same run-count target across compared algorithms.
- [ ] Common-run matching rule documented.
- [ ] Valid-run handling documented.
- [ ] Holm correction applied to the primary confirmatory family.
- [ ] Exploratory analyses labeled as exploratory in text and captions.
- [ ] Effect sizes reported alongside significance where claims depend on wins.
- [ ] Runtime cost discussed wherever gains are highlighted.
- [ ] Indicator disagreement discussed rather than ignored.

## Suggested execution order

1. Finish WS1 before making more cosmetic edits.
2. Finish WS2 before regenerating any final paper artifact.
3. Finish WS3 before rewriting results/discussion language.
4. Finish WS4 before final layout cleanup.
5. Finish WS5 before packaging.
6. Finish WS6 only after all earlier gates pass.

## Deliverables expected at the end

- submission-ready manuscript PDF;
- flattened submission `.tex` file;
- frozen release manifest and checksum file;
- claim-to-artifact traceability note;
- final figure/table set with canonical provenance;
- supplementary material package if appendix density remains too high;
- concise internal go/no-go memo with remaining risks set to zero or explicitly
  accepted.

## Definition of done

This plan is complete only when the answer to all questions below is "yes":

- Is the main contribution framed exactly at the level supported by the data?
- Can every claim in the abstract and conclusion be traced to frozen artifacts?
- Are data lineage and comparison rules auditable from repo files alone?
- Are `IGD` and `HV` both preserved in the final evidence package?
- Are engineering-feasibility limits transparent and not hidden in prose?
- Are the method description, pseudocode, flowchart, and code fully aligned?
- Is the paper packaged in a journal-compliant form?
- If a demanding reviewer asked for the provenance of any number in the paper,
  could we answer immediately from the manifest?

If any answer is "no", the paper is not ready to submit.
