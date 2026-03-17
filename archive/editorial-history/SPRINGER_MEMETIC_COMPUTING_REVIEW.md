# Review of `paper/src/sn-article.tex` for Springer `Memetic Computing`

Date: 2026-03-09

## Scope of this review

This document records a full reviewer-style assessment of the manuscript in
`paper/src/sn-article.tex`, considering the criteria typically applied by
Springer `Memetic Computing`: journal fit, originality, technical soundness,
experimental methodology, statistical rigor, interpretation, quality of figures
and tables, reproducibility, editorial readiness, and practical contribution.

The review also considers the compiled paper in `paper/build/sn-article.pdf`
and the main figure assets under `paper/figures/`.

## Overall recommendation

Recommendation: `Major Revision`

Current publication potential: `Promising, but not yet submission-ready at the
quality level expected for a strong acceptance without substantial revision.`

Core reason for the recommendation: the experimental package is strong and the
mechanistic interpretation is interesting, but the manuscript still shows
important weaknesses in (i) validation strength for the proposed H1/H2 design
elements, (ii) practical cost-benefit positioning, (iii) consistency across the
method description, flowchart, and pseudocode, and (iv) editorial/presentational
quality.

## Scorecard

Scale used below: `1 = poor`, `2 = weak`, `3 = adequate`, `4 = strong`,
`5 = excellent`.

| Criterion | Score | Assessment |
|---|---:|---|
| Relevance to journal | 4.3/5 | Strong fit for `Memetic Computing`; host-specific memetic hybridization is central to the paper. |
| Originality | 3.5/5 | The value lies in the host-specific coupling and geometric interpretation, not in IVF itself. |
| Technical soundness | 3.2/5 | Generally solid, but weakened by method/presentation inconsistencies and limited validation of H1/H2. |
| Experimental rigor | 4.2/5 | Strong protocol, explicit separation of tuning vs. out-of-sample evidence, and broad benchmark coverage. |
| Statistical rigor | 4.2/5 | Primary endpoint is pre-specified; Holm correction and effect sizes are used appropriately. |
| Writing and structure | 3.4/5 | Scientifically readable, but still dense and occasionally overburdened with protocol language. |
| Figures and tables | 2.8/5 | Some are informative, but several are overloaded, visually weak, or editorially unsuitable. |
| Reproducibility | 4.4/5 | Good code/data transparency and run-cohort discipline. |
| Practical contribution | 3.1/5 | Improvement over SPEA2 is real but modest relative to runtime overhead. |
| Overall | 3.4/5 | Publishable potential after substantial revision. |

## Executive summary

The manuscript makes a meaningful contribution by framing IVF/SPEA2 as a
host-specific memetic enhancement rather than a universally superior MOEA. That
positioning is scientifically credible and well aligned with the journal.

The strongest part of the paper is the experimental protocol: the authors define
IGD as the primary endpoint, use Holm--Bonferroni correction for the main claim,
report effect sizes, separate tuning-informed from out-of-sample evidence, and
discuss negative cases rather than hiding them. This is materially better than
the standard experimental discipline seen in many hybrid-MOEA submissions.

The main scientific limitation is that the paper does not yet validate the new
design elements H1 and H2 as strongly as the title and narrative suggest. The
ablation is partly descriptive, the omnibus factorial test is non-significant,
and the promoted `v2` configuration is nearly equivalent to `v1` on the full
synthetic suite. As a result, the paper more convincingly supports the broad
claim that IVF/SPEA2 improves SPEA2 under certain front geometries than the
stronger claim that the specific H1/H2 redesign is itself decisively validated.

In addition, the reported performance gains against canonical SPEA2 are modest in
magnitude relative to the reported runtime overhead, which weakens the practical
positioning unless the paper directly addresses that trade-off.

## Strengths

1. `Clear scientific question.` The paper asks a specific and relevant question:
   whether a memetic IVF intensification step can improve a density-based host
   such as SPEA2 under a fixed evaluation budget.
2. `Good journal fit.` The work is not merely benchmark aggregation; it engages
   with host-dependent memetic design and failure modes.
3. `Strong experimental discipline.` The tuning/OOS split in
   `paper/src/sn-article.tex:396`, the statistical protocol in
   `paper/src/sn-article.tex:360`, and the conservative claim table in
   `paper/src/sn-article.tex:414` are all strong choices.
4. `Mechanistic discussion is unusually valuable.` The interpretation in
   `paper/src/sn-article.tex:593` gives the paper a stronger scientific identity
   than a purely empirical comparison study.
5. `Negative evidence is reported honestly.` WFG2, WFG9, MaF5, DTLZ4, and
   RWMOP8 are discussed directly instead of being minimized.
6. `Reproducibility is above average.` The manuscript documents run cohorts, code
   availability, and engineering-screening logic clearly.

## Major concerns

### 1. The H1/H2 contribution is not validated with the strength implied by the paper

This is the most important issue.

- The paper now correctly treats the factorial interaction evidence as
  descriptive rather than confirmatory in `paper/src/sn-article.tex:446`.
- However, the narrative still gives H1/H2 a central role in the title and in
  the identity of the method.
- The problem is that the full-suite Phase 3 comparison against `v1` in
  `paper/src/sn-article.tex:459` shows `0W/50T/1L` on IGD, i.e. near-equivalence.
- Therefore, the manuscript supports the broad claim that the current
  IVF/SPEA2 configuration improves canonical SPEA2 on many instances, but it does
  not yet strongly support the narrower claim that H1/H2 constitute a clearly
  validated redesign over the prior coupling.

Why this matters for review:

- The title foregrounds `Dissimilar-Father Selection and Collective Cycling`.
- A reviewer will naturally expect the evidence for those two elements to be a
  centerpiece of the paper.
- At present, that evidence is suggestive, but not decisive.

What would strengthen the paper:

- Either moderate the novelty framing further,
- or provide stronger evidence that H1/H2 materially improve the earlier
  configuration under a design that is confirmatory rather than descriptive.

### 2. The practical gain appears modest relative to runtime overhead

- The effect-magnitude figure in `paper/src/sn-article.tex:487` reports a median
  IGD improvement of `+1.25%` for `M=2` and `+0.99%` for `M=3` over SPEA2.
- The runtime analysis in `paper/src/sn-article.tex:254` reports a median
  runtime ratio of `rho = 4.87` relative to SPEA2.
- Since the paper controls function evaluations rather than wall-clock time,
  this does not invalidate the experimental comparison.
- Nevertheless, the practical argument remains incomplete: why should a user pay
  an approximately 5x runtime cost for a typically small median improvement?

This trade-off should be discussed directly and explicitly. Without that, the
paper risks looking scientifically careful but practically weak.

### 3. The method description, flowchart, and pseudocode are not fully aligned

This is a serious presentation issue for an algorithm paper.

- The current flowchart in `paper/figures/flowchart.pdf` still appears to reflect
  an older logic based on transferring `superior` IVF offspring, which does not
  match the current collective selection/cycling story in
  `paper/src/sn-article.tex:183` and `paper/src/sn-article.tex:271`.
- The pseudocode in `paper/src/sn-article.tex:193` is better than before, but it
  still contains notation-level gaps:
  - `O_ivf` and `O_host` are used without explicit initialization;
  - the archive logic is compressed relative to the earlier narrative;
  - notation shifts between `M` and `n_obj`, and between population/archive
    descriptions, require more careful harmonization.

Why this matters:

- For a methodological paper, the algorithm specification must be self-consistent.
- Any mismatch between prose, figure, and pseudocode undermines confidence.

### 4. Real-world validation remains limited and only moderately persuasive

- The engineering suite is transparent and more honest than many papers, but it
  still consists of only three retained instances.
- One instance (`RWMOP8`) has heterogeneous feasibility and unbalanced valid-run
  coverage, as discussed in `paper/src/sn-article.tex:535` and
  `paper/src/sn-article.tex:553`.
- The selection protocol is careful, but still partially data-informed through
  screening.

This section is useful as a transferability check, but it does not yet provide
strong external validation. The manuscript already acknowledges this to some
extent; that caution should remain prominent.

### 5. Several figures and tables do not meet strong editorial standards

This is a major weakness for submission readiness.

- The boxplots in `paper/figures/boxplot_igd_m2.pdf` and
  `paper/figures/boxplot_igd_m3.pdf` are information-dense but visually crowded.
- The engineering front figure in `paper/figures/engineering_fronts_rwmop9_rwmop8.pdf`
  adds limited value on RWMOP9 because the fronts overlap almost completely.
- The combined front illustration in `paper/figures/pareto_fronts.pdf` is useful
  conceptually, but cramped.
- Appendix tables are visibly too large and too compressed in the compiled PDF.
- The LaTeX build records float and overflow problems in
  `paper/build/sn-article.log:841`, `paper/build/sn-article.log:851`, and many
  alignment overflows in the appendix tables.

For a high-quality journal submission, these presentation problems should be
fixed rather than tolerated.

### 6. The manuscript is not yet technically compliant with the single-file submission expectation

- The template explicitly states not to use `\input{...}` in
  `paper/src/sn-article.tex:6`.
- The manuscript still depends on many external table inserts, including
  `paper/src/sn-article.tex:252`, `paper/src/sn-article.tex:444`,
  `paper/src/sn-article.tex:461`, `paper/src/sn-article.tex:511`, and
  `paper/src/sn-article.tex:647`.

Even if the journal system accepts the files technically, this is a preventable
submission risk and should be resolved before submission.

## Medium-priority concerns

### 7. The paper could state more clearly what is confirmatory and what is exploratory

The authors already do this better than most papers, but a few sections still
blend strong and weak evidence layers in a way that could confuse readers.

Examples:

- The global ranking in `paper/src/sn-article.tex:499` is explicitly exploratory,
  which is good.
- However, the discussion in `paper/src/sn-article.tex:586` derives fairly strong
  regime recommendations from evidence that is partly exploratory.

This is not fatal, but the distinction should remain tight throughout.

### 8. The trimmed-mean summary is not fully specified

- In `paper/src/sn-article.tex:487`, the effect-magnitude summary reports a
  `trimmed mean`, but the trimming rule is not defined precisely.
- A reviewer should not have to infer how much trimming was applied.

### 9. Some extreme `median(IQR)` presentations are numerically awkward for human interpretation

Examples appear in:

- `results/ablation_v2/phase3/phase3_igd_table.tex:18`
- `results/ablation_v2/phase3/phase3_igd_table.tex:35`
- `results/ablation_v2/phase3/phase3_igd_table.tex:41`
- `results/ablation_v2/phase3/phase3_igd_table.tex:58`

These may be numerically correct, but they are difficult to read and invite
questions about scale, dispersion, and formatting. The paper would benefit from a
clearer formatting policy for extreme-dispersion cases.

### 10. The positioning against modern baselines is plausible but slightly overstated in places

The discussion in `paper/src/sn-article.tex:586` is thoughtful, but the paper
should be careful not to imply a broader regime prescription than the data truly
support. The evidence is strongest for improvement over `SPEA2`, weaker for broad
positioning among all modern baselines.

## Minor concerns

1. The flowchart language is dated and stylistically weak; wording such as
   `offsprings` should be corrected if the figure is regenerated.
2. The visual style of `paper/figures/flowchart.pdf` is markedly less polished
   than the rest of the paper.
3. The manuscript still relies heavily on win/loss/tie counts; the effect sizes
   help, but the narrative could lean slightly more on magnitude and trade-off.
4. The RWMOP9 engineering front panel adds less scientific value than the DTLZ4
   and WFG2 visual diagnostics.

## Evaluation of figures and tables

### Figures that work well

- `paper/figures/tuning_heatmap_combined.pdf`
  - Clear, informative, and useful for understanding the tuning pipeline.
- `paper/figures/heatmap_a12_M2.pdf`
  - Strong comparative overview with good scientific value.
- `paper/figures/heatmap_a12_M3.pdf`
  - Especially useful for showing the stronger competition from AGE-MOEA-II.
- `paper/figures/engineering_metric_profiles.pdf`
  - Good use of valid-run counts and uncertainty.
- `paper/figures/dtlz4_bimodal_good_bad.pdf`
  - This figure strongly supports the discussion of bimodality.

### Figures that need revision

- `paper/figures/flowchart.pdf`
  - Needs conceptual updating to match the current algorithm.
- `paper/figures/boxplot_igd_m2.pdf`
  - Too crowded; difficult to read in print.
- `paper/figures/boxplot_igd_m3.pdf`
  - Same problem; useful but visually overloaded.
- `paper/figures/engineering_fronts_rwmop9_rwmop8.pdf`
  - RWMOP9 panel has limited discriminative value.
- `paper/figures/pareto_fronts.pdf`
  - Conceptually good, but layout and readability should be improved.

### Tables

- `paper/src/sn-article.tex:414` / claim summary table
  - One of the best tables in the paper; concise and claim-oriented.
- Parameter table in `paper/src/sn-article.tex:283`
  - Improved and clearer than before; acceptable.
- Phase 3 ablation tables
  - Scientifically useful, but currently too large for comfortable reading.
- Appendix tables
  - Comprehensive but not editorially acceptable in current layout.

## Writing assessment

The manuscript is scientifically intelligible and generally well organized. The
abstract is much better focused than before, and the introduction now sets up the
problem clearly. The discussion is analytically stronger than the average paper in
this space.

Remaining writing issues:

- Some sections still feel dense because the paper carries substantial protocol
  and evidence-layer bookkeeping.
- A few claims remain slightly stronger than the evidence justifies, especially
  around H1/H2 and practical positioning.
- Some result paragraphs could be shortened without losing scientific content.

Overall writing judgment: `good but still in need of tightening for a high-end
journal submission`.

## Reproducibility assessment

This is one of the strongest aspects of the work.

- Code availability is good in `paper/src/sn-article.tex:671`.
- Data availability is substantially better than the field average in
  `paper/src/sn-article.tex:669`.
- Run-cohort filtering is explicitly documented in `paper/src/sn-article.tex:374`.

However, reproducibility quality does not fully compensate for conceptual and
presentation weaknesses.

## What must be fixed before a strong submission

1. Align the title, novelty framing, and evidence regarding H1/H2.
2. Discuss the runtime-overhead vs. performance-gain trade-off directly and
   honestly.
3. Regenerate the algorithm flowchart so that it matches the current method.
4. Tighten the pseudocode and ensure all objects and notation are explicit.
5. Improve figure readability and reduce overloaded visual panels.
6. Repair appendix/table formatting issues visible in the current PDF.
7. Remove `\input{...}` dependency for the final submission manuscript.
8. Clarify any derived statistics such as trimming rules.

## Final reviewer-style conclusion

This is a serious and potentially publishable paper with clear relevance to
`Memetic Computing`. It has a stronger methodological identity and better
experimental discipline than many submissions in the hybrid-MOEA literature.
However, it is not yet at the level where I would recommend acceptance.

At present, the most defensible editorial decision is `Major Revision`.

The paper's central scientific contribution should be reframed with slightly more
discipline: the manuscript strongly supports the claim that IVF/SPEA2 can improve
canonical SPEA2 on a broad subset of moderate-objective problems, especially when
front geometry is regular, but it only partially supports the stronger claim that
the specific H1/H2 redesign is decisively validated as the key novelty. If the
authors address that distinction, improve the cost-benefit discussion, and resolve
the remaining presentation issues, the manuscript could become a credible
submission for the journal.
