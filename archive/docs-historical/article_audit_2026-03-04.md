# Article Audit - Manuscript + References

Date: 2026-03-04
Scope:
- Manuscript: `paper/src/sn-article.tex`
- Linked result tables: `results/tables/` and `results/ablation_v2/`
- References: PDFs in `references/` (text extracted to `/tmp/*.txt`)

## 1) Executive summary

### Top issues (highest risk)
- Claim-to-evidence trace is incomplete in ablation: text at `sn-article.tex:470` (Phase 1) and `:485` (Phase 3) makes specific W/L/T claims, but only Phase 2 ranking table is currently `\input`-embedded (`:474`).
- Appendix asymmetry: HV per-instance longtables are embedded in appendix (`:668,671`), but the matching IGD per-instance longtables (`igd_per_instance_M{2,3}.tex`) exist in repo and are not embedded.
- Notation/presentation inconsistencies remain across components:
  - `AGE-MOEA-II` in body text and IGD detailed `table*` files vs `AGE-II` in all four longtable files (both IGD and HV per-instance).
  - Tie symbol `=` in IGD detailed tables and engineering table header vs `\approx` in all longtables and ablation tables (10 of 12 table files use `\approx`).
  - Sign format order differs: body text uses `wins/losses/ties`, engineering table header uses `+/=/-`, longtable summaries use `+/\approx/-`.
- Phase 2 Friedman omnibus test is non-significant (p=0.485); interaction decomposition that follows is exploratory but not explicitly labeled as such — a reviewable statistical attack vector.
- `tab:claims_summary` caption omits total instance counts (28 for M=2, 23 for M=3); readers see "23/3/2" without the denominator.

### Top improvements (highest impact)
- P0: Embed ablation evidence already generated (`phase1_table.tex`, `phase3_igd_table.tex`, `phase3_hv_table.tex`).
- P0: Embed IGD per-instance appendix tables (`igd_per_instance_M2.tex`, `igd_per_instance_M3.tex`).
- P0: Standardize notation and symbols globally.
- P0: Add Friedman-p exploratory defense sentence in ablation subsection.
- P0: Add total instance counts to `tab:claims_summary` caption.
- P1: Add compact feasibility/coverage table for engineering suite (valid runs per algorithm/problem). *(Downgraded from P0: the manuscript already provides three layers of coverage transparency — table footnote at `:576`, figure annotations in `fig:engineering-profiles`, and prose at `:558,579,599`.)*

### Overall assessment
- Method framing is strong (host-specific mechanism + budget control). *[Editorial assessment]*
- Statistical protocol is strong for primary claim (IGD primary endpoint + Holm correction against SPEA2). *[Verified: dual-layer protocol — unadjusted symbols in per-instance tables, Holm-corrected counts in `tab:claims_summary` — is well-documented in `subsec:stats`.]*
- Reproducibility details are strong (run cohorts, paths, tags, code availability). *[Editorial assessment]*
- Main weakness is not lack of data, but missing insertion of already-produced evidence components. *[Verified: all 12 .tex table files and all 13 figure PDFs exist in repo.]*

---

## 2) Manuscript Component Inventory

### 2.1 Table + notes (embedded components)

| ID | Type | Caption/Component | What it shows | Primary function | Referenced in text | Dependencies/inputs | Quality check + gap | Priority |
|---|---|---|---|---|---|---|---|---|
| `fig:flow` | Figure | Operational flow | IVF/SPEA2 execution flow under budget | Method grounding | Method section opening | `paper/figures/flowchart.pdf` | Good clarity; could add compact variable legend | P2 |
| `alg:ivf-spea2` | Algorithm | Fixed-budget pseudocode | Trigger, cycles, selection, budget adjustments | Formal reproducibility | IVF operator subsection | Inline algorithm block | Strong; could clarify tie-break details | P2 |
| `tab:runtime_overhead_baselines` | Input table | Runtime overhead | Runtime medians/IQR and `rho` ratios vs SPEA2 | Cost-benefit transparency | Cost/overhead subsection | `results/tables/runtime_overhead_baselines.tex` | Strong; lacks activation-frequency decomposition | P1 |
| `tab:params` | Table | Full parameter list | Shared and algorithm-specific defaults | Fairness + reproducibility | Platform/algorithms subsection | Inline table | Strong; minor readability density | P2 |
| `fig:sensitivity` | Figure | Tuning pipeline A/B/C | Search landscape and promoted config C26 | Justify default config | Sensitivity + discussion | `paper/figures/tuning_heatmap_combined.pdf` | Strong; add compact numeric summary table in text | P1 |
| `tab:claims_summary` | Table | Claim-oriented evidence matrix | Wins/losses/ties for IGD/HV, adjusted/OOS | Main quantitative claim anchor | Results/Discussion/Conclusion (7+ refs) | Inline table (`:442-464`) | Caption mentions OOS counts (24/15/39) but omits total instance counts (28 M=2, 23 M=3). Also add note clarifying that per-instance table symbols use unadjusted tests while this table's Holm rows apply correction. | **P0** |
| `tab:ablation_v2_phase2_ranking` | Input table | Phase 2 Friedman ranking | 2^4 configurations ranking | Design-element validation | Ablation subsection | `results/ablation_v2/phase2/phase2_ranking_table.tex` | Useful; global Friedman non-significant requires careful framing | P1 |
| `fig:ablation-h1h2-interaction` | Figure | Interaction map | H1xH2 synergy + antagonistic pairs | Mechanistic support | Ablation subsection | `results/ablation_v2/phase2/phase2_interactions.pdf` | Strong; no uncertainty intervals shown | P1 |
| `fig:boxplot-m2` | Figure | IGD distributions M=2 | Distribution-level evidence per instance | Primary evidence support | Primary comparison subsection | `paper/figures/boxplot_igd_m2.pdf` | Strong; visually dense | P2 |
| `fig:boxplot-m3` | Figure | IGD distributions M=3 | Distribution-level evidence + DTLZ4 bimodality | Primary evidence support | Primary comparison subsection | `paper/figures/boxplot_igd_m3.pdf` | Strong; visually dense | P2 |
| `fig:effect-magnitude` | Figure | Median IGD improvement (%) | Practical effect by instance | Practical relevance beyond p-values | Primary comparison subsection | `paper/figures/effect_magnitude_igd.pdf` | Good; clipping hides extreme values | P2 |
| `fig:friedman-rank` | Figure | Exploratory global rank | Average rank across 9 algorithms | Competitive positioning (exploratory) | Detailed results subsection | `paper/figures/friedman_avg_rank_igd.pdf` | Fine as exploratory; do not over-claim | P3 |
| `tab:igd_m2_detailed` | Input table | IGD medians M=2 | Per-instance medians across 9 algorithms | Granular synthetic evidence | Detailed results subsection | `results/tables/igd_m2_detailed_with_modern_table.tex` | Strong; heavy table load | P2 |
| `tab:igd_m3_detailed` | Input table | IGD medians M=3 | Per-instance medians across 9 algorithms | Granular synthetic evidence | Detailed results subsection | `results/tables/igd_m3_detailed_with_modern_table.tex` | Strong; heavy table load | P2 |
| `fig:a12-m2` | Figure | A12 heatmap M=2 | Effect size matrix vs baselines | Complement significance with magnitude | Stats + detailed results | `paper/figures/heatmap_a12_M2.pdf` | Strong; cell-level multiplicity caveat | P2 |
| `fig:a12-m3` | Figure | A12 heatmap M=3 | Effect size matrix vs baselines | Complement significance with magnitude | Stats + detailed results | `paper/figures/heatmap_a12_M3.pdf` | Strong; cell-level multiplicity caveat | P2 |
| `tab:engineering` | Table | RWMOP summary signs | Pairwise signs by problem and metric | External validation summary | Engineering subsection | Inline table | Good; add valid-run counts per baseline in table body | P1 |
| `fig:engineering-profiles` | Figure | Metric profiles with `n` | Medians/IQR + valid-run coverage | Coverage transparency | Engineering subsection | `paper/figures/engineering_metric_profiles.pdf` | Very good; could add viability-rate panel | P1 |
| `fig:engineering-fronts` | Figure | Fronts on RWMOP9/8 | Objective-space behavior by algorithm | Qualitative transfer interpretation | Engineering subsection | `paper/figures/engineering_fronts_rwmop9_rwmop8.pdf` | Good; only subset of algorithms shown | P2 |
| `fig:dtlz4-bimodal` | Figure | Good vs bad run regimes | Bimodality evidence on DTLZ4 M=3 | Failure-mode substantiation | Mechanistic discussion | `paper/figures/dtlz4_bimodal_good_bad.pdf` | Strong; instance-specific | P2 |
| `fig:pareto-fronts` | Figure | Success/failure representative fronts | DTLZ2 success, WFG2 failure, RWMOP9 trade-off | Mechanistic interpretation | Mechanistic discussion | `paper/figures/pareto_fronts.pdf` | Strong; include explicit selection rule note for all panels | P1 |
| `tab:hv_per_instance_m2` | Input longtable | HV per-instance M=2 | Complete secondary indicator evidence | Secondary confirmation | Appendix + main refs | `results/tables/hv_per_instance_M2.tex` | Complete; notation inconsistency with main tables | P1 |
| `tab:hv_per_instance_m3` | Input longtable | HV per-instance M=3 | Complete secondary indicator evidence | Secondary confirmation | Appendix + main refs | `results/tables/hv_per_instance_M3.tex` | Complete; notation inconsistency with main tables | P1 |
| EQ-FIT | Equation block | `F(i)=R(i)+D(i)` and terms | SPEA2 fitness formalization | Theoretical basis for host adaptation | Adaptation subsection | Inline equations | Good; no numbered equation labels | P2 |
| EQ-COST | Equation block | Complexity and overhead | Asymptotic SPEA2 + IVF overhead | Cost justification | Cost subsection | Inline equations | Good; add empirical stage-level decomposition | P2 |

### 2.2 Components available in repo but not embedded (critical)

- Ablation evidence not embedded:
  - `results/ablation_v2/phase1/phase1_table.tex` — **insert (P0)**: closes Phase 1 claim-evidence gap.
  - `results/ablation_v2/phase2/phase2_detail_table.tex` — **deliberately excluded from insertion plan**: the ranking summary (`phase2_ranking_table.tex`) is sufficient for the synergy argument; the full 16-configuration detail table adds bulk without strengthening the H1×H2 interaction claim.
  - `results/ablation_v2/phase3/phase3_igd_table.tex` — **insert (P0)**: closes Phase 3 IGD claim-evidence gap.
  - `results/ablation_v2/phase3/phase3_hv_table.tex` — **insert (P0)**: closes Phase 3 HV claim-evidence gap.
- IGD per-instance appendix tables not embedded:
  - `results/tables/igd_per_instance_M2.tex` — **insert (P0)**: restores appendix symmetry with HV.
  - `results/tables/igd_per_instance_M3.tex` — **insert (P0)**: restores appendix symmetry with HV.

### 2.3 Required flags

#### Orphaned components
- No hard `\\ref` breakage detected for currently embedded manuscript components.
- Practical orphaning exists at evidence-level: multiple generated tables are not inserted in the manuscript (see 2.2).
- Dead code: `sn-article.tex:169-189` contains a disabled related-work comparison table (`tab:rw-comparison`) inside an `\\iffalse...\\fi` block. It is internally consistent (its `\\ref` is also inside the block) but should be either removed from the source or re-enabled. Dead code creates confusion during collaborative editing.

#### Claims without direct embedded evidence
- Phase 1 screening claim details (`:470`, specific W/L/T: H1=2/10/0, H2=2/9/1) are discussed but no Phase 1 table is embedded. *Verified against `phase1_table.tex:22` summary row — numbers match.*
- Phase 3 full-suite confirmation claim details (`:485`, specific W/L/T: 0/50/1 vs v1, 25/25/1 vs SPEA2) are discussed but no Phase 3 table is embedded. *Verified against `phase3_igd_table.tex:62` and `phase3_hv_table.tex:62` — numbers match.*
- C26 vs A43 head-to-head confirmation is described in text (`:415`, "0 corrected wins, 12 ties, 0 losses on IGD") and repeated in Discussion (`:647`). The sensitivity figure provides visual context. A dedicated table for a 0/12/0 result adds bulk without new information. **Low priority; no action needed.**
- "mean Δ=+3.0%" in Phase 3 text (`:485`) is not directly computable from the Phase 3 table, which shows per-instance medians, not a mean percentage delta. This value must come from an analysis script. **Either add a footnote explaining the computation, or replace with a statement directly derivable from the table (e.g., "per-instance improvements generally below 1%").**

#### Statistical framing flags
- Phase 2 Friedman omnibus test: p=0.485 (non-significant). The manuscript reports the p-value (`:472`) and then decomposes interaction effects. A reviewer can legitimately argue that interaction analysis from a non-significant omnibus is post-hoc. **Add one defense sentence after the Friedman report: "We note that the global Friedman test is non-significant; the interaction analysis below is therefore exploratory and should be interpreted as hypothesis-generating rather than confirmatory."** (P0, 15 words, high reviewer-defense value.)
- Statistical layer duality: per-instance table symbols use unadjusted Wilcoxon (`:531`), while `tab:claims_summary` reports both unadjusted and Holm-corrected counts. This is well-designed and documented but could confuse readers who see a `+` symbol in the detailed table and assume it's Holm-corrected. **Add a brief parenthetical in `tab:claims_summary` caption: "(note: per-instance table symbols use unadjusted tests; Holm rows apply family-wise correction across all instances within each M group)."** (P1.)

#### Naming/notation inconsistencies
- `AGE-MOEA-II` vs `AGE-II`: body text and IGD detailed `table*` files use `AGE-MOEA-II`; all four longtable files (`igd_per_instance_M{2,3}.tex`, `hv_per_instance_M{2,3}.tex`) use `AGE-II` in column headers. The inconsistency surface area doubles when IGD longtables are embedded in the appendix (P0 item). **Unify to `AGE-MOEA-II` in all longtable column headers** (4 files, 2 header rows each = 8 edits).
- Tie symbols: `=` in `igd_m2_detailed_with_modern_table.tex` and `igd_m3_detailed_with_modern_table.tex` (2 files); `\\approx` in all 10 other table files (ablation + longtables). **Unify to `\\approx`** (majority convention, 10 of 12 files). This requires replaceAll on the 2 IGD detailed files.
- Engineering table header (`sn-article.tex:568`) uses `+/=/-`; should become `+/\\approx/-` after unification.
- Sign format order: body text uses `wins/losses/ties`, tables use `+/\\approx/-`. These serve different roles (prose vs. tabular summary) and can coexist as long as both are consistently defined. **No action needed**, but ensure every table caption or footnote defines the symbol convention.
- Variant naming: `IVF/SPEA2` (display name throughout), `IVF/SPEA2-v2` (ablation context, `:485`), `IVFSPEA2V2` (PlatEMO class name, `:197,309`). The three forms serve distinct purposes (display, versioned comparison, code reference) and are each used consistently in their respective contexts. **No action needed.**

#### Fairness/comparability issues to tighten
- Proposed method uses tuning pipeline; baselines remain default-only. This is acceptable and is explicitly framed as "defaults-vs-defaults" (`:424`). The 39 OOS instances provide confirmatory evidence. A compact comparability table in the setup section would preempt reviewer concerns. (P1.)
- NSGA-III and MOEA/D use adjusted population size by reference points/weights; the `tab:params` table (`:312`) documents this. Reiterate where aggregate comparisons are interpreted. (P1.)
- Engineering RWMOP8 has heterogeneous validity (`MOEA/D: 0/60`, `SPEA2+SDE: 18/60`), reducing pairwise comparability confidence. The manuscript addresses this in three places: table footnote (`:576`), figure annotations (`fig:engineering-profiles`), and prose (`:558,579,599`). A standalone coverage table is P1 rather than P0 given this existing three-layer transparency.

---

## 3) Reference Feature Map

## 3.1 Per-paper map

### `references/IVF-NSGA2.pdf`
- Core contribution:
  - IVF adaptation/coupling to NSGA-II and GDE3, including synthetic and applied evaluations.
- Argument structure:
  - Method adaptation -> parameterized experiments -> statistical comparison -> practical case.
- Included components:
  - Many parameter tables, flow/algorithm figures, boxplots, HV evolution plots, per-problem result tables.
- Rigor checklist observed:
  - 30 runs, IGD/HV, Wilcoxon usage, explicit parameter sweeps.
- High-impact element to emulate:
  - Clear parameter-sweep storytelling linked to behavior per benchmark family.

### `references/IVF-NSGA3.pdf`
- Core contribution:
  - IVF/NSGA-III coupling with evaluation-budget trigger for many-objective setup.
- Argument structure:
  - Design rationale -> grid search -> heatmap evidence -> promoted setting -> significance table.
- Included components:
  - Parameter grid (576 combinations), heatmaps, summary table with p-values, boxplots.
- Rigor checklist observed:
  - 30 runs, IGD endpoint, Wilcoxon rank-sum.
- High-impact element to emulate:
  - Heatmap-first tuning evidence plus concise promoted-config table.

### `references/1-s2.0-S0965997824001595-main.pdf`
- Core contribution:
  - MOEA/D-EpDE for structural optimization under synthetic + engineering benchmarks.
- Argument structure:
  - Method decomposition -> benchmark validation -> real engineering transfer.
- Included components:
  - Many benchmark tables, procedural algorithm steps, metric definitions, boxplots/fronts, objective statistics.
- Rigor checklist observed:
  - Multiple indicators (GD, GD+, IGD, IGD+, HV), Wilcoxon, independent runs, engineering validation.
- High-impact element to emulate:
  - Multi-indicator triangulation with explicit engineering interpretation.

### `references/1-s2.0-S2210650224002050-main.pdf`
- Core contribution:
  - MaOEAIH with interaction-force + hybrid optimization mechanism.
- Argument structure:
  - Mechanism proposal -> broad benchmark -> dedicated mechanism validation subsections.
- Included components:
  - Large IGD tables, significance matrices, perturbation/mechanism analyses, runtime table, complexity section.
- Rigor checklist observed:
  - 30 runs, Wilcoxon, extensive benchmark diversity, complexity + runtime reporting.
- High-impact element to emulate:
  - Explicit "mechanism validity" subsections for each design element.

### `references/An_Inverse_Modeling_Constrained_Multi-Objective_Evolutionary_Algorithm_Based_on_Decomposition.pdf`
- Core contribution:
  - IM-C-MOEA/D for constrained real-world MOPs (RWMOP1-35).
- Argument structure:
  - Componentized algorithm -> complexity -> broad real-world validation.
- Included components:
  - Flow-level decomposition, complexity, large HV tables with problem metadata (`m,d,FE,ng,nh`).
- Rigor checklist observed:
  - 30 runs, Wilcoxon rank-sum, Monte Carlo HV for high objective count.
- High-impact element to emulate:
  - Problem-metadata-rich result tables to support fairness interpretation.

### `references/algorithms_runs.pdf`
- Core contribution:
  - Adaptive online estimation of required run counts in stochastic optimization.
- Argument structure:
  - Methodology -> large-scale empirical validation -> CI/bootstrapping-based accuracy -> green benchmarking.
- Included components:
  - Accuracy tables by threshold/outlier method, CI/error analyses, computational savings table.
- Rigor checklist observed:
  - Very large run volume, explicit CI methodology, repeatability details.
- High-impact element to emulate:
  - Quantitative rationale for run-count protocols and reporting efficiency impact.

## 3.2 Aggregated master checklist (strong-paper elements)

- Explicit claim-evidence trace matrix.
- Mechanism-level validation (not only final performance).
- Primary + secondary metrics, with explicit disagreement handling.
- Full per-instance transparency tables for primary and secondary endpoints.
- Multiplicity-aware statistics for primary claims.
- Effect-size reporting in addition to p-values.
- Runtime/complexity reported both asymptotically and empirically.
- Engineering transfer with feasibility/coverage transparency.
- Reproducibility assets (run cohorts, scripts, data/code paths).

## 3.3 Gap analysis vs current manuscript

- Present and strong:
  - Primary endpoint protocol, Holm correction, effect-size heatmaps, threats-to-validity, runtime overhead.
- Present but needs reinforcement:
  - Mechanism validation exists but is partially embedded (Phase 2 only).
- Missing insertion (highest value):
  - Phase 1 and Phase 3 ablation tables.
  - IGD per-instance appendix tables.
  - Compact engineering feasibility/coverage matrix.

## 3.4 Recommended insertion plan (purpose/content/placement/claim)

Each item below specifies the exact file, insertion point, LaTeX snippet, and bridge sentence.

### PATCH A — Phase 1 table (P0)
- **File:** `paper/src/sn-article.tex`
- **Location:** after line 470 (end of Phase 1 paragraph, before `\textbf{Phase~2}`)
- **Bridge sentence + input:**
  ```latex
  Table~\ref{tab:ablation_v2_phase1} reports the full per-instance Phase~1 screening results.

  \input{../../results/ablation_v2/phase1/phase1_table.tex}
  ```
- **Purpose:** evidence for individual screening claims.
- **Claim supported:** "H1/H2 individually weak, promotion criteria outcomes" — readers can verify W/L/T counts directly.
- **Note:** the table already contains `\label{tab:ablation_v2_phase1}`.

### PATCH B — Phase 3 IGD + HV tables (P0)
- **File:** `paper/src/sn-article.tex`
- **Location:** after line 485 (end of Phase 3 paragraph, before `\subsection{Primary Comparison}`)
- **Bridge sentence + inputs:**
  ```latex
  Tables~\ref{tab:ablation_v2_phase3_igd} and~\ref{tab:ablation_v2_phase3_hv} report the full per-instance Phase~3 comparison under IGD and HV respectively.

  \input{../../results/ablation_v2/phase3/phase3_igd_table.tex}
  \input{../../results/ablation_v2/phase3/phase3_hv_table.tex}
  ```
- **Purpose:** explicit full-suite confirmation evidence.
- **Claim supported:** "v2 ~ v1 equivalence (0/50/1 IGD) + v2 > SPEA2 pattern (25/25/1 IGD, 28/21/2 HV)".
- **Note:** labels `tab:ablation_v2_phase3_igd` and `tab:ablation_v2_phase3_hv` already exist in the files.

### PATCH C — IGD per-instance appendix tables (P0)
- **File:** `paper/src/sn-article.tex`
- **Location:** lines 662–673 (appendix section). Replace the current appendix structure.
- **Replace:**
  ```latex
  \section{HV Per-Instance Tables}\label{app:hv-tables}

  	Tables~\ref{tab:hv_per_instance_m2} and~\ref{tab:hv_per_instance_m3} report median HV values ...
  ```
- **With:**
  ```latex
  \section{Per-Instance Tables}\label{app:per-instance-tables}

  Tables~\ref{tab:igd_per_instance_m2} and~\ref{tab:igd_per_instance_m3} report median IGD values per benchmark instance with IQR intervals. Tables~\ref{tab:hv_per_instance_m2} and~\ref{tab:hv_per_instance_m3} report the corresponding HV values. All testing conventions follow the same protocol: unadjusted Wilcoxon rank-sum tests ($\alpha=0.05$), with symbols from IVF/SPEA2's perspective ($+$ better, $-$ worse, $\approx$ no significant difference).

  	{\scriptsize\setlength{\tabcolsep}{3pt}%
  		\input{../../results/tables/igd_per_instance_M2.tex}}

  	{\scriptsize\setlength{\tabcolsep}{3pt}%
  		\input{../../results/tables/igd_per_instance_M3.tex}}

  	{\scriptsize\setlength{\tabcolsep}{3pt}%
  		\input{../../results/tables/hv_per_instance_M2.tex}}

  	{\scriptsize\setlength{\tabcolsep}{3pt}%
  		\input{../../results/tables/hv_per_instance_M3.tex}}
  ```
- **Purpose:** primary endpoint full transparency, appendix symmetry.
- **Claim supported:** all IGD instance-level summaries referenced in results/discussion.
- **Impact:** renames label from `app:hv-tables` to `app:per-instance-tables`. Grep confirms no `\ref{app:hv-tables}` outside the label itself — no breakage.

### PATCH D — Notation unification (P0)
Four targeted sub-edits:
- **D1.** In `results/tables/igd_m2_detailed_with_modern_table.tex` and `igd_m3_detailed_with_modern_table.tex`: `replaceAll` tie symbol `$=$` → `$\approx$` in caption text and all data-cell superscripts. Also update the caption description from `$=$ no significant difference` to `$\approx$ no significant difference`.
- **D2.** In all four longtable files (`igd_per_instance_M{2,3}.tex`, `hv_per_instance_M{2,3}.tex`): change column header `AGE-II` → `AGE-MOEA-II` (2 header rows per file = 8 edits).
- **D3.** In `sn-article.tex:568` (engineering table header): change `IGD ($+/=/-$)` → `IGD ($+/\approx/-$)` and `HV ($+/=/-$)` → `HV ($+/\approx/-$)`.
- **D4.** In `sn-article.tex:531` and analogous text near `:2` of IGD detailed table captions: ensure the symbol description matches the new `\approx` convention.

### PATCH E — Friedman-p defense sentence (P0)
- **File:** `paper/src/sn-article.tex`
- **Location:** line 472, after `($\chi^2=14.54$, $p=0.485$).`
- **Insert:** `Although the omnibus test does not reject the null hypothesis of equal rankings, the interaction decomposition below is exploratory and provides hypothesis-generating evidence for the synergistic mechanism.`

### PATCH F — Claims summary caption n (P0)
- **File:** `paper/src/sn-article.tex`
- **Location:** line 443, beginning of caption body.
- **Prepend:** `Based on 28 bi-objective and 23 tri-objective synthetic instances (51 total).`

### PATCH G — Engineering coverage mini-table (P1, downgraded from P0)
- **File:** `paper/src/sn-article.tex`
- **Location:** after line 577 (engineering table footnote), or as an appendix entry.
- **Content:** a 3-row × 9-column table showing valid run counts per algorithm per RWMOP problem.
- **Rationale for P1:** the manuscript already provides table footnote (`:576`), figure annotations (`fig:engineering-profiles`), and prose (`:558,579,599`). A standalone table is useful but not blocking.

---

## 4) Action Plan (P0/P1/P2)

### P0 (must-do before submission)

| # | Item | Patch | Effort | Impact |
|---|------|-------|--------|--------|
| 1 | Embed Phase 1 ablation table | PATCH A: `\input` + bridge sentence after `sn-article.tex:470` | 5 min | Closes Phase 1 claim-evidence gap |
| 2 | Embed Phase 3 IGD + HV ablation tables | PATCH B: `\input` × 2 + bridge sentence after `sn-article.tex:485` | 5 min | Closes Phase 3 claim-evidence gap |
| 3 | Embed IGD per-instance appendix tables | PATCH C: expand appendix, rename section label, add 2 `\input` blocks before HV tables | 10 min | Eliminates IGD/HV appendix asymmetry |
| 4 | Standardize notation globally | PATCH D: (D1) `=` → `\approx` in 2 IGD detailed files; (D2) `AGE-II` → `AGE-MOEA-II` in 4 longtables; (D3) engineering header; (D4) caption text | 20 min | Eliminates reviewer friction on symbols |
| 5 | Add Friedman-p defense sentence | PATCH E: 1 sentence after `sn-article.tex:472` | 2 min | Preempts statistical critique on Phase 2 |
| 6 | Add total instance count `n` to claims_summary caption | PATCH F: prepend to `sn-article.tex:443` caption | 2 min | Makes central evidence table self-contained |

**Estimated total P0 effort: ~45 minutes.**

### P1 (high value, next revision pass)

| # | Item | Details |
|---|------|---------|
| 1 | Engineering coverage mini-table | PATCH G: 3×9 table of valid-run counts per algorithm/problem; place in engineering subsection or appendix. *(Downgraded from P0: three layers of coverage transparency already exist.)* |
| 2 | Comparability matrix in setup | Compact matrix of `N`, `FE_max`, run counts, adjusted populations, valid-runs policy per algorithm. Preempts fairness critiques. |
| 3 | Stage-level overhead decomposition | Short table with IVF activation rate, median `n_ivf`, and extra selection calls. Strengthens cost-mechanism link. |
| 4 | Failure-mode matrix | Table with instance, geometry type, IGD/HV direction, hypothesized mechanism, linked figure. Improves discussion precision and rebuttal readiness. |
| 5 | "mean Δ=+3.0%" verifiability fix | Either add a footnote explaining the computation method, or replace with a statement directly derivable from Phase 3 table (e.g., "per-instance median improvements generally below 1%"). |
| 6 | Statistical layer clarity note | Add parenthetical in `tab:claims_summary` caption: "(note: per-instance table symbols use unadjusted tests; Holm rows apply family-wise correction across all instances within each M group)." |

### P2 (polish)

| # | Item |
|---|------|
| 1 | Remove or re-enable the `\\iffalse` related-work table block (`sn-article.tex:169-189`). |
| 2 | Archive/clean unused candidate figures in `paper/figures/`. |
| 3 | Optional methodological note on run-count rationale inspired by `references/algorithms_runs.pdf`. |
| 4 | Verify abstract claims match evidence tables (spot-check: conclusion line 656 restates "23 of 28 / 18 of 23" — matches `tab:claims_summary` row 1). |
| 5 | Ensure all figure captions are self-contained (selection rule for representative runs, axis label definitions). |

---

## Evidence paths used for this audit

- Manuscript core: `paper/src/sn-article.tex`
- Main result tables:
  - `results/tables/runtime_overhead_baselines.tex`
  - `results/tables/igd_m2_detailed_with_modern_table.tex`
  - `results/tables/igd_m3_detailed_with_modern_table.tex`
  - `results/tables/hv_per_instance_M2.tex`
  - `results/tables/hv_per_instance_M3.tex`
  - `results/tables/igd_per_instance_M2.tex`
  - `results/tables/igd_per_instance_M3.tex`
- Ablation:
  - `results/ablation_v2/phase1/phase1_table.tex`
  - `results/ablation_v2/phase2/phase2_ranking_table.tex`
  - `results/ablation_v2/phase2/phase2_detail_table.tex`
  - `results/ablation_v2/phase3/phase3_igd_table.tex`
  - `results/ablation_v2/phase3/phase3_hv_table.tex`
- Reference PDFs:
  - `references/IVF-NSGA2.pdf`
  - `references/IVF-NSGA3.pdf`
  - `references/1-s2.0-S0965997824001595-main.pdf`
  - `references/1-s2.0-S2210650224002050-main.pdf`
  - `references/An_Inverse_Modeling_Constrained_Multi-Objective_Evolutionary_Algorithm_Based_on_Decomposition.pdf`
  - `references/algorithms_runs.pdf`

---

## 5) Verification Log (Patch Execution)

Date: 2026-03-04

### Patches Applied

| Patch | Status | Files Modified | Notes |
|-------|--------|----------------|-------|
| A — Phase 1 table embed | **Done** | `sn-article.tex` | Bridge sentence + `\input` after Phase 1 paragraph. Also fixed Unicode `η` → `$\eta_c{=}10$` in `phase1_table.tex` header row (pdflatex incompatibility). |
| B — Phase 3 IGD+HV tables | **Done** | `sn-article.tex` | Bridge sentence + 2× `\input` after Phase 3 paragraph. Float-too-large warnings (~52--55pt) on these tables are pre-existing (51-row `table*` floats); LaTeX places them on float pages. |
| C — IGD appendix tables | **Done** | `sn-article.tex` | Renamed appendix section label `app:hv-tables` → `app:per-instance-tables`. Added 2× `\input` for IGD longtables before existing HV longtables. Updated in-text reference at former line 518 to mention both IGD and HV appendix tables. |
| D — Notation unification | **Done** | 8 files | D1: `\,^{=}` → `\,^{\approx}` and caption `$=$` → `$\approx$` in 2 IGD detailed files. D2: `AGE-II` → `AGE-MOEA-II` in 4 longtable files (2 header rows each = 8 edits). D3: Engineering table header `$+/=/-$` → `$+/\approx/-$`. D4: Stats protocol text `($+$, $-$, $=$)` → `($+$, $-$, $\approx$)`. |
| E — Friedman-p defense | **Done** | `sn-article.tex` | One sentence after Phase 2 Friedman report: "Although the omnibus test does not reject the null hypothesis of equal rankings, the interaction decomposition below is exploratory and provides hypothesis-generating evidence for the synergistic mechanism." |
| F — Claims summary caption | **Done** | `sn-article.tex` | Prepended "Based on 28 bi-objective and 23 tri-objective synthetic instances (51 total)." to caption. |
| G — Dead code removal | **Done** | `sn-article.tex` | Removed `\iffalse...\fi` block (lines 166–190 of original). 25 lines of dead related-work table code eliminated. |

### Compilation Verification

- `make clean && make`: **Success** (0 errors, 0 undefined references)
- Output: `paper/build/sn-article.pdf` (45 pages, 1.06 MB)
- Tests: `pytest tests/python/ -v` → 6/6 passed
- Pre-existing warnings (not introduced by patches):
  - Overfull hbox on `runtime_overhead_baselines.tex` (10.6pt)
  - Overfull hbox on `phase1_table.tex` (163.8pt) — wide 7-column table
  - Float too large on `phase3_igd_table.tex` (52pt) and `phase3_hv_table.tex` (55pt) — 51-row tables
  - Overfull hboxes on all longtable appendix tables (149–326pt) — known width issue for 11-column longtables at `\scriptsize`

### Remaining P1/P2 Items (not addressed in this pass)

- P1: Engineering coverage mini-table (PATCH G in audit)
- P1: Comparability matrix in setup
- P1: Stage-level overhead decomposition
- P1: Failure-mode matrix
- P1: "mean Δ=+3.0%" verifiability fix
- P1: Statistical layer clarity note in claims_summary caption
- P2: Archive/clean unused candidate figures
- P2: Run-count rationale note
- P2: Abstract claims spot-check
- P2: Self-contained figure captions
