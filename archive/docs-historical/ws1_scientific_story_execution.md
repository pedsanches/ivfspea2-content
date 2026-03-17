# WS1 - Scientific Story Execution Guide

Date: 2026-03-09
Status: Ready to execute
Related master plan: `docs/memetic_computing_submission_master_plan.md`
Primary manuscript: `paper/src/sn-article.tex`

## Purpose

WS1 exists to make the paper intellectually honest, reviewer-resistant, and
internally consistent before any further polishing.

This workstream is not about new experiments. It is about deciding what the
paper is really allowed to claim, then making the title, abstract,
contributions, results order, discussion, and conclusion all say the same thing.

## Recommended framing decision

Use the conservative framing below as the default.

### Recommended default

The paper's main validated contribution is:

- a host-specific, budget-controlled IVF/SPEA2 coupling;
- robust pairwise improvement over canonical `SPEA2` on many `M=2` and `M=3`
  synthetic instances under fixed evaluation budgets;
- a geometry-dependent explanation of when the coupling helps and when it hurts.

The paper's secondary contribution is:

- the current implementation uses `H1` and `H2` as motivated design refinements;
- the ablation provides descriptive support for these refinements;
- the ablation does not justify selling `H1/H2` as decisively validated headline
  novelties.

### Framing that should be avoided

Do not frame the paper as if its strongest evidence were:

- "H1/H2 are decisively validated";
- "v2 is clearly better than v1";
- "IVF/SPEA2 is broadly superior to modern baselines";
- "the method is practical by default without acknowledging runtime cost".

## The evidence ladder the manuscript should follow

Every major section should respect this order of evidence strength.

### Tier 1 - Main confirmatory claim

- `IVF/SPEA2` vs `SPEA2`
- primary endpoint: `IGD`
- strongest layer: out-of-sample synthetic instances + Holm correction
- message: the method improves its host on many regular-front `M<=3` instances
  under fixed evaluation budgets, but not universally

### Tier 2 - Confirmatory support

- full synthetic suite vs `SPEA2`
- `HV` as secondary indicator
- message: the main pattern largely holds, but uncertainty increases on some
  tri-objective and irregular-front cases

### Tier 3 - Descriptive / supportive evidence

- ablation of `H1/H2`
- tuning pipeline around `C26`
- message: these analyses justify the chosen implementation and help interpret
  behavior, but they are not the paper's strongest claim layer

### Tier 4 - Exploratory / transferability evidence

- modern-baseline ranking and heatmaps
- engineering problems
- message: useful for positioning and transferability checks, not for the core
  confirmatory claim

## Core editorial decision for WS1

The manuscript should be rewritten so the title and opening promise only Tier 1
plus the mechanistic interpretation, not Tier 3.

## Concrete decisions to take first

### Decision 1 - Title policy

Recommended title direction:

- foreground `IVF/SPEA2` as a host-specific memetic hybrid;
- keep fixed-budget control in the title;
- do not foreground `Dissimilar-Father Selection and Collective Cycling` as the
  main title hook.

Recommended title candidate:

`Budget-Controlled IVF/SPEA2: A Host-Specific Memetic Hybrid for Moderate-Objective Multiobjective Optimization`

Strong alternative:

`Budget-Controlled IVF/SPEA2 for Multiobjective Optimization: Host-Specific Memetic Intensification Under Fixed Evaluation Budgets`

Softer mechanism-retaining alternative:

`Budget-Controlled IVF/SPEA2: Host-Specific Memetic Intensification with Dissimilar-Father Selection and Collective Cycling`

Recommendation:

- use the first option unless new confirmatory evidence is produced for `H1/H2`.

### Decision 2 - One-sentence paper claim

Adopt one canonical sentence and reuse it across abstract, introduction,
discussion, and conclusion.

Recommended canonical sentence:

`Under fixed evaluation budgets, IVF/SPEA2 is best understood as a host-specific memetic enhancement that often improves canonical SPEA2 on regular-front moderate-objective problems, but offers modest gains, higher runtime cost, and weaker behavior on irregular or disconnected fronts.`

### Decision 3 - Runtime positioning sentence

The paper needs one plain-spoken sentence that appears in the Discussion and is
consistent with the abstract.

Recommended sentence:

`The method is therefore most attractive when evaluation-normalized solution quality matters more than wall-clock time; when runtime is the main constraint, the observed median gains are too small to justify routine use.`

## What to change in the current manuscript

## A. Title and abstract

### Current problem

- The title at `paper/src/sn-article.tex:100` over-promises direct validation of
  `H1/H2`.
- The abstract at `paper/src/sn-article.tex:123` gives H1/H2 too much headline
  weight and does not acknowledge the runtime trade-off.

### WS1 action

- replace the title with a host-coupling title;
- rewrite the abstract around the evidence ladder;
- report the strongest confirmatory evidence first;
- keep H1/H2 as method details, not as the main selling point;
- add one short scope sentence on modest gains / runtime cost / failure modes.

### Abstract shape to follow

Paragraph logic in one block:

1. SPEA2 is relevant but can suppress local intensification.
2. IVF/SPEA2 inserts a budget-controlled IVF phase into SPEA2.
3. The current implementation uses dissimilar-father selection and collective
   cycling.
4. Main evidence: out-of-sample + Holm-corrected improvement vs `SPEA2`.
5. Mechanistic finding: gains depend on front geometry.
6. Scope statement: moderate-objective, host-specific, not universal, and more
   expensive in runtime.

## B. Introduction and contribution bullets

### Current problem

- The introduction at `paper/src/sn-article.tex:139` makes `H1/H2` too central.
- The contributions at `paper/src/sn-article.tex:141` place method detail at the
  same level as the validated scientific finding.

### WS1 action

- keep `H1/H2` in the method description, but move the main intellectual center
  to the coupling problem and geometry-dependent behavior;
- rewrite the contributions so they are ordered by evidence strength.

### Recommended contribution structure

1. `Method`: a fixed-budget, host-specific IVF/SPEA2 coupling aligned with
   SPEA2's archive dynamics.
2. `Evidence`: robust pairwise evidence that the method improves canonical
   `SPEA2` on many `M=2` and `M=3` instances, especially with regular fronts,
   under fixed evaluation budgets.
3. `Analysis and protocol`: an evidence-layered protocol with tuning/OOS
   separation, multiplicity-aware testing, and a geometry-based interpretation of
   both gains and failures.

## C. Results structure

### Current problem

- The Results section currently presents ablation before the main pairwise result
  against `SPEA2` (`paper/src/sn-article.tex:438` before `:464`).
- This makes the weaker evidence look more central than the stronger claim.

### WS1 action

Reorder the results narrative so the paper's strongest evidence comes first.

Recommended order:

1. claim summary table;
2. primary comparison vs `SPEA2`;
3. detailed multi-baseline positioning;
4. engineering transferability check;
5. ablation as secondary design-support evidence.

If a full subsection move is too disruptive, keep the current order but add an
explicit opening sentence in the Results section saying that the primary claim of
the paper is the pairwise IVF/SPEA2-vs-SPEA2 comparison, and that the ablation is
supportive rather than central.

## D. Ablation framing

### Current problem

- The ablation text at `paper/src/sn-article.tex:440` is careful, but still too
  prominent relative to its evidential strength.

### WS1 action

- retain the ablation, but demote its rhetorical status;
- explicitly state in the opening sentence that this subsection evaluates design
  refinements for the current implementation and does not constitute the main
  confirmatory claim of the paper;
- keep the `v2` vs `v1` near-equivalence visible, not hidden.

### Recommended opening sentence for the subsection

`This ablation study is used to justify the current IVF/SPEA2 implementation and to interpret its behavior; it is supportive rather than central to the paper's main confirmatory claim, which remains the pairwise comparison against canonical SPEA2.`

## E. Discussion

### Current problem

- The discussion is strong overall, but `paper/src/sn-article.tex:586` still
  risks sounding stronger than the evidence allows.
- The runtime trade-off is present earlier in the manuscript but not integrated
  tightly into the final positioning.

### WS1 action

- lead the discussion with the host-specific geometry-dependent finding;
- explicitly state the trade-off between fixed-FE gains and wall-clock cost;
- keep modern-baseline positioning explicitly exploratory or regime-based;
- turn the discussion into a user-facing positioning statement, not a victory
  lap.

### Recommended discussion structure

1. what is solidly supported;
2. when the method helps;
3. when it hurts;
4. what the runtime cost means in practice;
5. how to position it against other methods without overclaiming.

## F. Conclusion

### Current problem

- The conclusion is close to the correct framing, but it should end more clearly
  on scope and trade-off.

### WS1 action

- keep the geometry-dependent conclusion;
- add one final sentence on practical scope;
- do not end on future work before restating the bounded contribution.

### Recommended closing message

`The paper therefore supports IVF/SPEA2 as a conditional improvement over SPEA2 rather than a universal replacement: its value is highest on regular-front problems at moderate objective counts and in studies where evaluation-normalized solution quality is more important than runtime.`

## Section-by-section edit list

| Section | File location | WS1 edit |
|---|---|---|
| Title | `paper/src/sn-article.tex:100` | Replace H1/H2 headline with host-coupling headline |
| Abstract | `paper/src/sn-article.tex:123` | Rewrite around evidence ladder and add runtime/scope sentence |
| Introduction hypothesis | `paper/src/sn-article.tex:139` | Shift emphasis from H1/H2 novelty to host-specific coupling problem |
| Contributions | `paper/src/sn-article.tex:141` | Reorder by evidence strength |
| Results opening | `paper/src/sn-article.tex:408` | State main confirmatory claim explicitly |
| Ablation opening | `paper/src/sn-article.tex:440` | Mark as supportive/descriptive, not central claim |
| Effect magnitude paragraph | `paper/src/sn-article.tex:487` | Link gains directly to runtime cost and define trimming elsewhere |
| Discussion positioning | `paper/src/sn-article.tex:586` | Soften regime claims and add explicit cost-benefit statement |
| Conclusion | `paper/src/sn-article.tex:629` | End with bounded claim and practical scope |

## Execution sequence for WS1

1. Lock the title decision.
2. Write the one-sentence canonical claim.
3. Rewrite the abstract to match that claim.
4. Rewrite the contribution bullets.
5. Add one explicit evidence-hierarchy sentence at the start of Results.
6. Demote ablation rhetorically and, if feasible, structurally.
7. Add the runtime positioning sentence in Discussion.
8. Rewrite the Conclusion last, using only statements already supported earlier.

## Acceptance gate for WS1

WS1 is complete only if all answers below are `yes`.

- Does the title avoid promising stronger evidence than the paper has?
- Does the abstract foreground the strongest confirmatory result?
- Are `H1/H2` presented as method refinements rather than over-validated
  headline novelties?
- Is the pairwise `IVF/SPEA2` vs `SPEA2` evidence clearly the center of the
  paper?
- Is the runtime cost acknowledged in the final positioning?
- Are engineering and multi-baseline results clearly bounded in strength?
- Can the conclusion be defended without referring to any exploratory-only claim?

## Recommended immediate next edit

If doing WS1 incrementally, start with exactly these four edits in order:

1. change the title;
2. rewrite the abstract;
3. rewrite the three contribution bullets;
4. insert the supportive-not-central sentence at the start of the ablation
   subsection.

That sequence usually resolves most of the framing mismatch before deeper line
editing begins.
