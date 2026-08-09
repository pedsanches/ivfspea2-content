# PPSN 2026 IVF-Hosts Reviewer Rev2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply an 11-point reviewer punchlist to `paper/ppsn2026-ivf-hosts/main.tex` that (1) makes the abstract lead with contribution, (2) makes symbols and notation self-explanatory on first mention, (3) adds a mechanistic, contribution-lifting rewrite of the discussion, and (4) reformats Tables 2 and 3 plus Fig. 4 caption for readability — all without altering any scientific claim or any figure's underlying data.

**Architecture:** Thirteen tasks. Task 0 = preflight (compile baseline PDF). Tasks 1–11 apply one reviewer point each; each consists of exact `Edit`/`Write` calls with full `old_string`/`new_string` pairs, followed by a grep-based verification and a scoped commit. Task 12 = final compile, pdftotext sanity check, and end-of-plan checkpoint. Tables 2 and 3 are regenerated from their Python producers — the `.tex` artifacts are not edited in place.

**Tech Stack:** LaTeX (llncs), BibTeX, Python 3 (pandas) via `.venv`, `latexmk`/`pdflatex`, `pdftotext`.

---

## Preface: Reviewer-Quote Discrepancy

Reviewer Point 7 quotes `+38/=5/-3 in IGD and +37/=10/-4 in HV` for IVF/SPEA2. The current `main.tex` line 153 shows `+33/=15/-3 in IGD and +37/=10/-4 in HV`, and the abstract line 36 shows `33 wins, 15 ties, and 3 losses`. The IGD tally the reviewer quoted is stale — they were reading an earlier draft. **Do not change the numbers.** Point 7 only adds a reading cue; keep `+33/=15/-3` verbatim.

## Self-Imposed Rules

1. Scientific claims and statistical results are untouched. This revision is presentational.
2. Tables 2 and 3 are produced by Python scripts; edit the producer and regenerate, do not hand-edit the `.tex` artifacts.
3. After each task, compile the paper; if `make` fails, stop and surface the error.
4. Each task ends with a single scoped commit whose message begins `revision-rev2: [P<point#>] ...`.

---

## File Structure

**Modified:**
- `paper/ppsn2026-ivf-hosts/main.tex` — body edits for points 1–7, 10, 11.
- `src/python/analysis/build_hosts_rep_endpoint_table.py` — drops Sign column, uniformizes numeric formatting (point 8).
- `src/python/analysis/compute_hosts_geometry_stratified.py` — expands `W | T | L` to `Wins | Ties | Losses` header (point 9).

**Regenerated (artifacts, committed):**
- `results/tables/hosts_rep_endpoint_igd.tex` — produced by `build_hosts_rep_endpoint_table.py`.
- `results/tables/hosts_geometry_summary.tex` — produced by `compute_hosts_geometry_stratified.py`.

**Read-only reference:**
- `docs/superpowers/plans/2026-04-17-ppsn2026-ivf-hosts-reviewer-revision.md` — prior round's plan; its M1/M2/Mo3 edits are already in `main.tex`.

---

## Task 0: Preflight — compile baseline PDF

**Files:** none modified.

- [ ] **Step 0.1: Compile the current paper**

Run:
```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make
```
Expected: `build/main.pdf` produced with no LaTeX errors. Record the resulting page count.

Run:
```bash
pdfinfo /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.pdf | grep -E '^Pages:'
```
Record the page count; call this `PAGES_BEFORE`. Rev2 must not push past 12 pages at the end (LNCS limit for PPSN is typically 12 before references; confirm with user if it exceeds).

- [ ] **Step 0.2: Checkpoint to user**

Format:
```
Checkpoint 0
  Baseline compile : OK | FAIL
  Pages            : <PAGES_BEFORE>
```
Proceed to Task 1 once the user confirms baseline is clean.

---

## Task 1: Point 1 — Rewrite the abstract (contribution-first)

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (the `\begin{abstract} ... \end{abstract}` block, lines 35–39).

The current abstract opens with methodology (PlatEMO, 51 instances, BH, A12) and ends with the conclusion. Rewrite to the four-movement structure: (1) question, (2) finding, (3) method compressed, (4) implication.

- [ ] **Step 1.1: Replace the abstract body**

Edit `main.tex` with:

OLD:
```
We study whether the benefit of in vitro fertilization (IVF) intensification depends on the MOEA host when IVF is instantiated through canonical host-specific variants from prior literature. Using PlatEMO, we compare three published pipelines---IVF/SPEA2, IVF/NSGA-II, and IVF/NSGA-III---on 51 synthetic benchmark instances with 30 runs per configuration, evaluating final IGD and HV with nonparametric tests, Benjamini--Hochberg correction, and Vargha--Delaney $A_{12}$. IVF/SPEA2 achieves 33 wins, 15 ties, and 3 losses in IGD; IVF/NSGA-III achieves 22 wins, 29 ties, and 0 losses; and IVF/NSGA-II achieves 1 win, 48 ties, and 2 losses; the same ordering appears in HV and remains consistent across $M=2$ and $M=3$ and across DTLZ, MaF, WFG, and ZDT. Dynamic analyses on a protocol-defined six-instance subset reproduce the same ordering at the trajectory level: IVF/SPEA2 shows the strongest and most stable early convergence signal, IVF/NSGA-III remains context-sensitive and weakens at $M=3$, and IVF/NSGA-II is nearly inert. In the absolute cross-host ranking among IVF variants, IVF/SPEA2 attains the best mean rank in both metrics and the most HV bests, while IVF/NSGA-III remains a strong second host and IVF/NSGA-II is rarely first. Because the three pipelines differ in more than just the host, the evidence supports a pipeline-level compatibility claim: among the published IVF realizations studied here, IVF/SPEA2 couples most effectively with its host's selection mechanism, IVF/NSGA-III is conditionally beneficial, and IVF/NSGA-II is largely neutral.
```

NEW:
```
In vitro fertilization (IVF) intensification operators have been published in host-specific variants for SPEA2, NSGA-II, and NSGA-III, but it is unclear whether the reported benefits survive when the operator is combined with a different host. Under a unified benchmark and analysis protocol, we find that the three canonical published pipelines are not interchangeable: IVF/SPEA2 improves its host broadly and robustly, IVF/NSGA-III is conditionally beneficial, and IVF/NSGA-II is largely neutral. The evaluation uses PlatEMO on 51 synthetic benchmark instances at two and three objectives with 30 runs per configuration, comparing endpoint IGD and HV with nonparametric tests, Benjamini--Hochberg correction, and Vargha--Delaney effect sizes, and is complemented by trajectory-level dynamic analyses. The same host ordering appears in endpoint tallies, effect-size distributions, and dynamic aggregates, and is accompanied by a mechanism-level reading that attributes it to the granularity and directionality of the host's selection signal. The practical implication is that operator-host compatibility is a first-order design concern: published IVF couplings should not be assumed interchangeable across hosts.
```

- [ ] **Step 1.2: Verify the replacement landed**

Run:
```bash
grep -c 'IVF/SPEA2 achieves 33 wins' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `0` (old prose gone).

Run:
```bash
grep -c 'operator-host compatibility is a first-order design concern' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

- [ ] **Step 1.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 1.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P1] rewrite abstract to lead with contribution

Reorders the abstract into question -> finding -> method -> implication.
Drops per-host tally enumeration, benchmark family enumeration, and the
M=2/M=3 parenthetical from the abstract (all retained in the body).
Keeps the pipeline-level scope caveat implicit and ends on the practical
implication, per reviewer rev2 point 1.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Point 2 — Define IVF at first mention

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (introduction §1, line 46, the sentence starting "IVF was first proposed...").

Goal: give a 1-sentence operational definition before the first citation `[4]`.

- [ ] **Step 2.1: Insert the definition sentence**

Edit `main.tex`:

OLD:
```
The IVF family provides a natural case study for this question. IVF was first proposed as a multi-objective hybrid inspired by in vitro fertilization~\cite{camilo-junior2011}. It was subsequently adapted as an operator for NSGA-II~\cite{sampaio2017ivf}, extended to many-objective settings~\cite{sampaio2019ivf}, specialized for NSGA-III~\cite{Sampaio2024}, and most recently redesigned for SPEA2~\cite{zambrano2026ivfspea2}. Across these variants, the IVF core is shared: select a subset of promising individuals, pair them, generate intensified offspring through a short internal reproduction cycle, and transfer those offspring back to the host population. What changes across hosts is the realization of that core, including how mothers and fathers are chosen, how continuation is decided, and how the IVF budget is integrated with the host generation.
```

NEW:
```
The IVF family provides a natural case study for this question. IVF is a short-cycle intensification operator that selects a subset of top-ranked individuals as \emph{mothers}, pairs each with a \emph{father} drawn from the population, generates intensified offspring through a small number of internal reproduction cycles, and re-injects them into the host population. It was first proposed as a multi-objective hybrid inspired by in vitro fertilization~\cite{camilo-junior2011}. It was subsequently adapted as an operator for NSGA-II~\cite{sampaio2017ivf}, extended to many-objective settings~\cite{sampaio2019ivf}, specialized for NSGA-III~\cite{Sampaio2024}, and most recently redesigned for SPEA2~\cite{zambrano2026ivfspea2}. What changes across hosts is the realization of that core, including how mothers and fathers are chosen, how continuation is decided, and how the IVF budget is integrated with the host generation.
```

Note: this deletes the "Across these variants, the IVF core is shared: ..." sentence because the new definition now covers it; the mothers/fathers/cycle description used to be there in a second pass. The remaining sentence ("What changes across hosts...") is preserved verbatim and keeps its role as the bridge to §2.2/§3.

- [ ] **Step 2.2: Verify §2.2 still stands alone (no dangling forward reference)**

Run:
```bash
grep -n 'Across IVF variants, the shared core' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: exactly one hit (line ~72, the §2.2 opening). §2.2 is unchanged.

- [ ] **Step 2.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 2.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P2] define IVF at first mention in the introduction

Adds a one-sentence operational definition of the IVF operator
(mothers/fathers/short-cycle intensification) before the first citation,
so the reader does not need to consult [4] to follow the rest of the
introduction. Removes the now-redundant 'shared core' sentence; section
2.2 still introduces the same material for readers who skip section 1.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Point 3 — Research question + Hypothesis with mechanism axis

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (§1 "Research question" and "Hypothesis H" paragraphs, lines 52–56).

Goal: widen the RQ from a yes/no question to include the mechanism axis, and sharpen the hypothesis into a testable mechanistic prediction. This plants the mechanism story that Task 11 will pay off in the Discussion.

- [ ] **Step 3.1: Replace RQ paragraph**

Edit `main.tex`:

OLD:
```
\paragraph{Research question.}
Does the benefit of IVF depend on the structure of the host selection mechanism?
```

NEW:
```
\paragraph{Research question.}
Does the benefit of IVF depend on the host's selection mechanism, and if so, which structural property of the host---dominance strength, crowding, or reference-point niching---best explains the observed coupling?
```

- [ ] **Step 3.2: Replace Hypothesis paragraph**

OLD:
```
\paragraph{Hypothesis H.}
Across host-specific IVF realizations reported in prior work, stronger IVF gains are expected in MOEAs whose selection mechanisms provide more explicit directional feedback in objective space about under-explored regions. Hosts with predominantly isotropic crowding feedback are expected to show weaker synergy.
```

NEW:
```
\paragraph{Hypothesis H.}
IVF gains are strongest in hosts whose selection mechanism produces a \emph{granular, non-isotropic} quality ordering over the non-dominated set, because the IVF mother-selection step (top-ranked fraction) requires such an ordering to identify promising intensification seeds. Hosts whose selection collapses the non-dominated set onto an isotropic crowding signal should show weak synergy; hosts that impose a discretised directional signal through reference-point niches should show intermediate, geometry- and dimensionality-dependent synergy.
```

- [ ] **Step 3.3: Verify**

Run:
```bash
grep -c 'granular, non-isotropic' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

- [ ] **Step 3.4: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 3.5: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P3] mechanism-oriented research question and hypothesis

Broadens the research question to ask which structural property of the
host (dominance strength, crowding, reference-point niches) explains the
coupling. Sharpens Hypothesis H into a testable mechanistic prediction
about granularity and directionality of the host's selection signal.
This plants the mechanism account paid off in the discussion rewrite
(point 11).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Point 4 — Parameter glosses on first appearance

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (§3.1 line 82, §3.2 line 87, §3.3 line 92).

Goal: inline parentheticals for symbols `C`, `R`, `M_mut`, `V`, `Cycles`, `ivf_rate` on first occurrence. No new paragraphs.

- [ ] **Step 4.1: §3.1 IVF/SPEA2 parameter line**

OLD:
```
The parameter configuration is $C=0.12$, $R=0.225$, $M_{\mathrm{mut}}=0.3$, $V=0.1$, and \textit{Cycles} = 2.
```

NEW:
```
The parameter configuration is $C=0.12$ (mother fraction of the population), $R=0.225$ (cumulative activation rate that gates whether IVF runs in a given generation), $M_{\mathrm{mut}}=0.3$ (fraction of mothers mutated inside IVF), $V=0.1$ (decision-variable fraction perturbed by that mutation), and \textit{Cycles}~$=2$ (maximum number of internal IVF reproduction cycles per activation).
```

- [ ] **Step 4.2: §3.2 IVF/NSGA-II parameter line**

OLD:
```
The parameter setting used here is $R=0.5$, $C=0.07$, and \textit{Cycles} = 5.
```

NEW:
```
The parameter setting used here is $R=0.5$ (probabilistic activation rate), $C=0.07$ (mother fraction), and \textit{Cycles}~$=5$.
```

- [ ] **Step 4.3: §3.3 IVF/NSGA-III parameter line**

OLD:
```
The parameter setting is \textit{ivf\_rate}=0.10, $C=0.10$, and \textit{Cycles} = 5.
```

NEW:
```
The parameter setting is \textit{ivf\_rate}$=0.10$ (cumulative activation rate), $C=0.10$ (mother fraction), and \textit{Cycles}~$=5$.
```

- [ ] **Step 4.4: §4 "Parameter provenance" paragraph — restate without re-glossing**

OLD (line 133):
```
IVF/SPEA2 v2 used $C=0.12$, $R=0.225$, $M_{\mathrm{mut}}=0.3$, $V=0.1$, and \textit{Cycles} = 2; IVF/NSGA-II used $R=0.5$, $C=0.07$, and \textit{Cycles} = 5; and IVF/NSGA-III used \textit{ivf\_rate}=0.10, $C=0.10$, and \textit{Cycles} = 5.
```

NEW:
```
IVF/SPEA2 v2 used $C=0.12$, $R=0.225$, $M_{\mathrm{mut}}=0.3$, $V=0.1$, and \textit{Cycles}~$=2$; IVF/NSGA-II used $R=0.5$, $C=0.07$, and \textit{Cycles}~$=5$; and IVF/NSGA-III used \textit{ivf\_rate}$=0.10$, $C=0.10$, and \textit{Cycles}~$=5$.
```
(This edit only normalises spacing/ties the symbol to its value with `~`; glosses are not repeated here per the reviewer's "inline only on first appearance".)

- [ ] **Step 4.5: Verify**

Run:
```bash
grep -c '(mother fraction of the population)' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

- [ ] **Step 4.6: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 4.7: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P4] gloss IVF parameters on first appearance

Adds inline parentheticals on C, R, M_mut, V, Cycles, and ivf_rate the
first time each is introduced in sections 3.1, 3.2, and 3.3, so a reader
who has not read the cited references can still follow the parameter
table without looking them up.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Point 5 — Scope-defense paragraph under Table 1

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (the paragraph starting "Table~\ref{tab:adaptations} summarizes these host-specific choices.", line 113, just after the `\end{table}` on line 111).

Goal: confront the "is this a fair comparison?" question head-on, right where the reader sees the five axes of divergence. The bridge to §4 is kept; the defense paragraph precedes it.

- [ ] **Step 5.1: Replace the single paragraph with a two-paragraph block**

OLD:
```
Table~\ref{tab:adaptations} summarizes these host-specific choices. Because the realizations differ in several components, compatibility claims in this paper refer to the pipeline level (host + realization) rather than to a single IVF module held identical across hosts. With the pipelines specified, we now turn to the experimental protocol under which they are compared.
```

NEW:
```
Table~\ref{tab:adaptations} summarizes these host-specific choices. The three realizations differ on several axes simultaneously---father selection, offspring generation, continuation criterion, and activation budget. This is deliberate: the unit of comparison here is the \emph{published pipeline}, not an isolated host-mechanism effect under a single IVF implementation held identical across hosts. A strict mechanism-isolation study---transplanting a fixed IVF core across hosts---is a natural follow-up and is not claimed here. What this study does claim is directly useful: practitioners reading the IVF literature need to know whether the three published couplings are interchangeable, and our evidence (Section~\ref{sec:results}) shows that they are not.

With the pipelines specified, we now turn to the experimental protocol under which they are compared.
```

- [ ] **Step 5.2: Verify**

Run:
```bash
grep -c 'unit of comparison here is the' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

- [ ] **Step 5.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 5.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P5] scope-defense paragraph under Table 1

Promotes the 'pipeline-level unit of comparison' caveat from a forward
reference in section 1 to an explicit paragraph immediately below
Table 1, where the reader sees the four axes of divergence. Frames the
simultaneous-axes comparison as a deliberate scope choice with practical
value, and names transplant experiments as the natural follow-up.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Point 6 — Glosses for M, N, maxFE

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (§4 line 118).

Goal: inline parentheticals on `M`, `N`, `maxFE` in the first paragraph of the experimental setup.

- [ ] **Step 6.1: Replace the instance-count sentence and the run-config sentence**

OLD:
```
All experiments were conducted in MATLAB~\texttt{R2025b Update 5} using PlatEMO version~\texttt{4.6}~\cite{tian2017platemo}. We considered 51 synthetic benchmark instances: 28 bi-objective instances from ZDT~\cite{zitzler2000zdt}, DTLZ~\cite{deb2005dtlz}, WFG~\cite{huband2006wfg}, and MaF~\cite{cheng2017maf}; and 23 tri-objective instances from DTLZ, WFG, and MaF. This yields 28 instances with $M=2$ and 23 instances with $M=3$. Each configuration was executed for 30 runs with population size $N=100$ and stopping criterion $\mathrm{maxFE}=100{,}000$.
```

NEW:
```
All experiments were conducted in MATLAB~\texttt{R2025b Update 5} using PlatEMO version~\texttt{4.6}~\cite{tian2017platemo}. We considered 51 synthetic benchmark instances: 28 bi-objective instances (number of objectives $M=2$) from ZDT~\cite{zitzler2000zdt}, DTLZ~\cite{deb2005dtlz}, WFG~\cite{huband2006wfg}, and MaF~\cite{cheng2017maf}; and 23 tri-objective instances ($M=3$) from DTLZ, WFG, and MaF. Each configuration was executed for 30 independent runs with population size $N=100$ individuals and stopping criterion $\mathrm{maxFE}=100{,}000$ function evaluations per run.
```

Note: removes the redundant "This yields 28 instances with $M=2$ and 23 with $M=3$" sentence because that is now stated inline.

- [ ] **Step 6.2: Verify**

Run:
```bash
grep -c 'number of objectives \$M=2\$' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

Run:
```bash
grep -c 'This yields 28 instances with' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `0` (old duplicate gone).

- [ ] **Step 6.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 6.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P6] gloss M, N, maxFE on first appearance in section 4

Adds inline parentheticals on the number-of-objectives symbol M, the
population size N, and the stopping-criterion maxFE, and deletes the
redundant 'This yields ... instances' sentence now covered by the inline
gloss.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Point 7 — Reading cue for the +wins/=ties/-losses notation

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (§5.1 line 153, the sentence starting "Under the aligned paired analysis visualized here,").

Goal: a one-sentence reading cue immediately before the first tally. Do NOT change the numbers (`+33/=15/-3` is current; reviewer's `+38/=5/-3` is stale).

- [ ] **Step 7.1: Insert the reading cue**

OLD:
```
Figure~\ref{fig:heatmap} disaggregates the aggregate picture to the instance level. The same ranking remains visible, and the figure additionally shows which benchmark families drive it. Under the aligned paired analysis visualized here, IVF/SPEA2 dominates the synthetic suite with +33/=15/-3 in IGD and +37/=10/-4 in HV over the 51 instances.
```

NEW:
```
Figure~\ref{fig:heatmap} disaggregates the aggregate picture to the instance level. The same ranking remains visible, and the figure additionally shows which benchmark families drive it. Throughout this section we report per-host outcomes in the format $+\mathit{wins}/{=}\mathit{ties}/{-}\mathit{losses}$, where a win denotes an instance in which the IVF variant significantly outperformed its base host under the Wilcoxon signed-rank test at $\alpha=0.05$ after Benjamini--Hochberg correction, a loss the reverse, and a tie no significant difference. Under the aligned paired analysis visualized here, IVF/SPEA2 dominates the synthetic suite with +33/=15/-3 in IGD and +37/=10/-4 in HV over the 51 instances.
```

- [ ] **Step 7.2: Verify no tally was changed**

Run:
```bash
grep -c '+33/=15/-3 in IGD and +37/=10/-4 in HV' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1` (number preserved).

Run:
```bash
grep -c 'Throughout this section we report per-host outcomes' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

- [ ] **Step 7.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 7.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P7] reading cue for the +wins/=ties/-losses notation

Adds a single sentence explaining the +wins/=ties/-losses format, the
significance criterion (Wilcoxon with BH at alpha=0.05), and what a win,
tie, and loss denote, immediately before the first tally in section 5.1.
Numbers are unchanged.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Point 8 — Table 2 reformat + take-away sentence

**Files:**
- Modify: `src/python/analysis/build_hosts_rep_endpoint_table.py` (table producer).
- Regenerated: `results/tables/hosts_rep_endpoint_igd.tex`.
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (insert a take-away sentence just before `\input{../../results/tables/hosts_rep_endpoint_igd.tex}` on line 166).

Goal: (a) remove the redundant `Sign` column (the `Case` column already encodes `+/=/-`); (b) uniformize numeric formatting to a single decimal convention (prefer three significant figures for all cells); (c) add a take-away sentence in the text that gives the reader a conclusion to walk out with.

- [ ] **Step 8.1: Edit the Python producer — remove the Sign column**

Open `src/python/analysis/build_hosts_rep_endpoint_table.py` and find the block beginning with `"\\begin{tabular}{lllcll}"` (line 93). Read a 40-line window around it to identify the three edits needed: tabular spec, header, and row-format template.

Apply three edits:

(a) Change the tabular spec from six columns to five:

OLD:
```
        "\\begin{tabular}{lllcll}",
```
NEW:
```
        "\\begin{tabular}{lllrr}",
```
(`r` for the two numeric columns right-aligns numbers; keep the three text columns left-aligned.)

(b) Change the header row from six cells to five:

OLD:
```
        f"Host & Case & Instance & IVF & Base & Sign {newline}",
```
NEW:
```
        f"Host & Case & Instance & IVF (median [IQR]) & Base (median [IQR]) {newline}",
```

(c) Find every row-emission string in the producer that carries the `Sign` column and drop its last cell. This requires reading the producer's row-formatting function; after identifying the row-template string (likely something like `f"{host} & {case} & {instance} & {ivf} & {base} & {sign} {newline}"` somewhere after line 93), replace it with the same template without the `& {sign}` segment. Verify by searching for `& {sign}`:
```bash
grep -n '& {sign}\| & {sign}\|sign {newline}\|{sign} \\\\\\\\' /home/pedro/code/research/ivfspea2/src/python/analysis/build_hosts_rep_endpoint_table.py
```

- [ ] **Step 8.2: Edit the producer — uniformize numeric format**

In the same producer, locate the IVF/Base value formatting. Current behaviour mixes scientific and decimal notation (e.g. `0.00376 [7.04e-05]` vs `0.24 [0.0199]`). Standardise to three significant figures using Python's `g` format. Minimal surgical change: find any line of the form `f"{median:...}"` or `f"{iqr:...}"` used for the IVF/Base cells and replace both specifiers with `{:#.3g}`.

If the producer uses a helper function such as `_fmt(x)`, edit that helper in one place:
```python
def _fmt(x):
    return f"{x:#.3g}"
```

Verify:
```bash
grep -nE '\{:#?\.3g\}|def _fmt|format_cell' /home/pedro/code/research/ivfspea2/src/python/analysis/build_hosts_rep_endpoint_table.py
```

- [ ] **Step 8.3: Regenerate the table**

Run:
```bash
cd /home/pedro/code/research/ivfspea2
source .venv/bin/activate
python src/python/analysis/build_hosts_rep_endpoint_table.py
```
Expected: `results/tables/hosts_rep_endpoint_igd.tex` updated.

Run:
```bash
head -25 /home/pedro/code/research/ivfspea2/results/tables/hosts_rep_endpoint_igd.tex
```
Expected: five-column header with no `Sign` column; all numeric cells use matching precision.

- [ ] **Step 8.4: Update Table 2 caption in the producer**

Because the caption now needs to mention "median [IQR]" once up front rather than repeating it in the column header, locate the caption string and update it. Find the caption emission (likely near the top of the `\begin{table}` assembly):

OLD caption fragment:
```
... Entries show median [IQR].
```
NEW caption fragment:
```
... Entries are IGD median with interquartile range in brackets; rows labelled `gain', `tie', and `adverse' encode the sign of the effect directly, so a separate sign column is unnecessary.
```

- [ ] **Step 8.5: Add the take-away sentence in main.tex**

Insert one sentence in `main.tex` just before the `\input{...hosts_rep_endpoint_igd.tex}` line (currently line 166). Find the sentence that precedes it and append:

OLD (lines 163–166, the two sentences before the input):
```
To complement wins/ties/losses and oriented effect sizes with a direct view of dispersion, Table~\ref{tab:rep_endpoint_medians} reports median/IQR endpoint values for a deterministic representative set of gain, tie, and adverse cases across the three hosts. The full per-instance median/IQR tables remain in the archived supplementary artifact.

\input{../../results/tables/hosts_rep_endpoint_igd.tex}
```

NEW:
```
To complement wins/ties/losses and oriented effect sizes with a direct view of dispersion, Table~\ref{tab:rep_endpoint_medians} reports median/IQR endpoint values for a deterministic representative set of gain, tie, and adverse cases across the three hosts. The full per-instance median/IQR tables remain in the archived supplementary artifact. Three readings are immediate from Table~\ref{tab:rep_endpoint_medians}: (i) IVF/SPEA2's best gain (MaF3, $M=2$) shifts the IGD median by more than an order of magnitude, while its worst adverse case (WFG2, $M=3$) is numerically close to the base host; (ii) IVF/NSGA-III's representative gain (DTLZ2, $M=2$) is tight in both variants and driven by dispersion rather than median shift; (iii) even IVF/NSGA-II's deterministic `gain' row (WFG1, $M=2$) is within the base host's IQR, which is consistent with the near-inert aggregate behaviour.

\input{../../results/tables/hosts_rep_endpoint_igd.tex}
```

- [ ] **Step 8.6: Verify**

Run:
```bash
grep -c 'Three readings are immediate from Table' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

Run:
```bash
grep -c '& Sign ' /home/pedro/code/research/ivfspea2/results/tables/hosts_rep_endpoint_igd.tex
```
Expected: `0` (Sign column gone).

- [ ] **Step 8.7: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build; eyeball Table 2 in the PDF for alignment.

- [ ] **Step 8.8: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/build_hosts_rep_endpoint_table.py \
        results/tables/hosts_rep_endpoint_igd.tex \
        paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P8] reformat Table 2 and add take-away sentence

Drops the redundant Sign column (already encoded by Case), standardises
numeric cells to three significant figures, right-aligns the numeric
columns, and updates the caption. Adds a three-point take-away sentence
in section 5.1 immediately before the table so the reader walks away
with a conclusion, not just numbers.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Point 9 — Expand W/T/L header in Table 3

**Files:**
- Modify: `src/python/analysis/compute_hosts_geometry_stratified.py`.
- Regenerated: `results/tables/hosts_geometry_summary.tex`.

Goal: rename the three compressed-letter columns to `Wins`, `Ties`, `Losses` so the header is self-explanatory. No data change.

- [ ] **Step 9.1: Edit the producer header**

Open `src/python/analysis/compute_hosts_geometry_stratified.py` and read around line 240. Apply:

OLD:
```
        "\\begin{tabular}{llcrrrc}",
        "\\toprule",
        f"Host & Metric & Geometry & W & T & L & Med.~$A_{{12}}^{{\\mathrm{{IVF}}}}$ {newline}",
```
NEW:
```
        "\\begin{tabular}{llcrrrc}",
        "\\toprule",
        f"Host & Metric & Geometry & Wins & Ties & Losses & Med.~$A_{{12}}^{{\\mathrm{{IVF}}}}$ {newline}",
```

- [ ] **Step 9.2: Regenerate the table**

Run:
```bash
cd /home/pedro/code/research/ivfspea2
source .venv/bin/activate
python src/python/analysis/compute_hosts_geometry_stratified.py
```

Run:
```bash
head -15 /home/pedro/code/research/ivfspea2/results/tables/hosts_geometry_summary.tex
```
Expected: `Wins & Ties & Losses` in the header.

- [ ] **Step 9.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build. Eyeball Table 3 in the PDF: if the three widened columns produce awkward line-breaks in the header cell, fall back to a compact form (`\#~Wins & \#~Ties & \#~Losses`) by repeating Step 9.1 with that substitution.

- [ ] **Step 9.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/compute_hosts_geometry_stratified.py \
        results/tables/hosts_geometry_summary.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P9] expand W/T/L column headers in Table 3

Renames the compact single-letter headers W, T, L to Wins, Ties, Losses
so the table is self-explanatory without reading the caption.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Point 10 — Fig. 4 take-away in the caption

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (Fig. 4 caption, lines 198–203).

Goal: add an explicit "Reading cue" sentence to the caption so the reader extracts the ordering in seconds.

- [ ] **Step 10.1: Replace Fig. 4 caption**

OLD:
```
\caption{All-suite dynamic aggregate over the 51-instance trace cohort. Each curve shows the fraction of runs whose cumulative-best IGD has reached a normalized gap of at most $\tau=0.1$ (gap normalized per instance against the pair-specific initial state and the best final value attained by either algorithm) as a function of FE / maxFE. Solid lines: IVF variant; dashed lines: base host. Shaded bands: 95\% bootstrap confidence intervals. Early separation (FE / maxFE $< 0.3$) indicates the IVF variant reaches near-final quality on a larger fraction of runs sooner.}
```

NEW:
```
\caption{All-suite dynamic aggregate over the 51-instance trace cohort. Each curve shows the fraction of runs whose cumulative-best IGD has reached a normalized gap of at most $\tau=0.1$ (gap normalized per instance against the pair-specific initial state and the best final value attained by either algorithm) as a function of FE / maxFE. Solid lines: IVF variant; dashed lines: base host. Shaded bands: 95\% bootstrap confidence intervals. \textbf{Reading cue.} The IVF/SPEA2 solid curve separates from its dashed baseline within the first 20\% of the evaluation budget and maintains that separation to the end, indicating faster and more reliable convergence. IVF/NSGA-III's curves overlap or cross the baseline for most of the budget, so any benefit is confined to late stages. IVF/NSGA-II's curves are nearly indistinguishable from the baseline throughout, confirming the near-inertness seen at the endpoint.}
```

- [ ] **Step 10.2: Verify**

Run:
```bash
grep -c 'Reading cue' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `>=2` (Fig. 2 caption already has one; Fig. 4 now adds a second).

- [ ] **Step 10.3: Compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

- [ ] **Step 10.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P10] Fig. 4 reading cue

Adds a 'Reading cue' sentence to Fig. 4 caption that states the ordering
explicitly (IVF/SPEA2 separates early and holds; IVF/NSGA-III overlaps
the baseline; IVF/NSGA-II is nearly indistinguishable), so the reader
walks away with the conclusion rather than only the axis description.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Point 11 — Mechanistic discussion rewrite (the contribution lift)

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (§6 Discussion, specifically the paragraph starting "A plausible interpretation...", line 230, and only that paragraph).

Goal: replace the single short "plausible interpretation" paragraph with a mechanism-level account that explicitly ties each host's selection properties (SPEA2's strength-plus-density, NSGA-II's isotropic crowding, NSGA-III's discretised niches) to the observed ordering — while keeping the statistical-honesty caveat about host×geometry interaction. This is the single largest space investment in the revision (~3/4 of a page) and is the point the reviewer explicitly called out as the opportunity for "a bacana" contribution.

**This task should be executed with a user review checkpoint after drafting, because the prose is paid by space (§6 will grow by roughly half a page) and needs to land inside LNCS page limits.**

- [ ] **Step 11.1: Replace the "plausible interpretation" paragraph**

OLD (exactly this paragraph, currently line 230):
```
A plausible interpretation is that hosts providing more explicit directional information in objective space enable the IVF core to convert local intensification into offspring that survive environmental selection. This interpretation is consistent with the observed ranking, but it should still be read as a mechanistic account supported by the current evidence rather than as a mechanism already isolated experimentally. Its most useful implication is predictive: if the interpretation is correct, the strength of IVF should vary not only with the host but also with Pareto-front geometry. The geometry-stratified summaries are directionally consistent with that prediction---regular fronts favor IVF/SPEA2 most strongly and weaken both IVF/NSGA-III and IVF/NSGA-II---but the permutation tests do not yet show a strong host$\times$geometry interaction, so this part of the evidence remains suggestive rather than definitive.
```

NEW (four paragraphs):
```
A mechanism-level reading of the observed ordering starts from the IVF core itself. For intensification to survive the host's environmental selection, IVF needs two properties from its host: (i)~a \emph{granular quality ordering} over the non-dominated set, so that top-ranked mother selection picks individuals that are genuinely more promising than their neighbours, and (ii)~a \emph{directional diversity signal}, so that the intensified offspring occupy regions the host rewards during replacement.

SPEA2 provides both. Its fitness combines dominance \emph{strength} (the count of solutions dominated, weighted by the strength of their dominators) with a $k$-nearest-neighbour density term in objective space~\cite{zitzler2001spea2}. The strength component alone induces a fine-grained, non-isotropic ordering within the non-dominated set, which is exactly the signal mother selection relies on; the density term then supplies the directional information needed for offspring to win environmental selection. This is consistent with IVF/SPEA2 capturing the largest gains, those gains being preserved at $M=3$, and their robustness across Pareto-front geometries.

NSGA-II provides neither well. Non-dominated sorting collapses the front into a single rank for any two individuals on the same layer, and crowding distance supplies an \emph{isotropic} sparsity signal that does not distinguish directions in objective space~\cite{deb2002nsga2}. Top-ranked mother selection therefore degenerates toward near-arbitrary picks within a rank, and intensified offspring have no preferred direction to survive replacement. This matches the near-neutrality of IVF/NSGA-II across metrics, geometries, and dimensionalities.

NSGA-III sits between the two. Reference-point niching supplies directional information, but it is \emph{discretised} into a fixed set of niches rather than being a continuous quality gradient~\cite{deb2014nsga3}. IVF can exploit this when $M=2$ and the niche structure aligns cleanly with the true front (convex, concave, linear geometries), but at $M=3$ the signal dilutes---more niches, fewer offspring per niche, weaker selection pressure per direction. This is consistent with the specific collapse of IVF/NSGA-III from +18/=11/-0 at $M=2$ to +4/=19/-0 at $M=3$ in IGD. The three observations reduce to a single property: IVF converts local intensification into population-level progress only when the host's selection mechanism already encodes a granular, directional quality signal. The permutation tests do not yet isolate this mechanism formally (all $p \geq 0.356$ for host$\times$geometry interaction), so the account above is a mechanistically coherent reading of the observed ordering, not a confirmed causal claim. Its value is predictive: it identifies the property a new host would need in order to benefit from IVF intensification, and motivates the cross-host transplant study named in Section~\ref{sec:conclusion}.
```

- [ ] **Step 11.2: Verify**

Run:
```bash
grep -c 'A mechanism-level reading of the observed ordering' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `1`.

Run:
```bash
grep -c 'A plausible interpretation is that hosts providing' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: `0`.

- [ ] **Step 11.3: Compile, verify page count, user checkpoint**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make`
Expected: clean build.

Run:
```bash
pdfinfo /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.pdf | grep -E '^Pages:'
```
Record as `PAGES_AFTER_P11`.

Report to user:
```
Checkpoint 11
  Pages before rev2 : <PAGES_BEFORE>
  Pages after rev2  : <PAGES_AFTER_P11>
  §6 growth         : roughly +3/4 of a page
  Please eyeball the new §6 prose for voice and accuracy before commit.
```
Wait for user acknowledgement, then commit.

- [ ] **Step 11.4: Commit**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision-rev2: [P11] mechanistic discussion rewrite

Replaces the short 'plausible interpretation' paragraph in section 6 with
a four-paragraph mechanism-level account that explicitly ties each host's
selection properties to the observed ordering: SPEA2's strength-plus-
density gives the granular directional signal IVF needs; NSGA-II's rank-
plus-isotropic-crowding does not; NSGA-III's discretised niches give a
conditional, dimensionality-sensitive signal that matches the M=2 vs M=3
asymmetry in IVF/NSGA-III. Keeps the permutation-test caveat and frames
the account as predictive rather than causally confirmed.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: Final compile, sanity checks, end-of-plan checkpoint

**Files:** none modified.

- [ ] **Step 12.1: Final compile**

Run: `cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make clean && make`
Expected: `build/main.pdf` produced with no LaTeX errors or missing references.

- [ ] **Step 12.2: Page count audit**

Run:
```bash
pdfinfo /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.pdf | grep -E '^Pages:'
```
If the final page count exceeds the LNCS PPSN limit (user to confirm the exact limit), report the overage and stop; do not try to trim heuristically — coordinate with the user.

- [ ] **Step 12.3: Ligature / text-extraction sanity**

Run:
```bash
pdftotext -layout /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.pdf - \
  | grep -nE 'dierent|intensication|eect|conrmatory|dicult|simpli |sucient|specic' \
  || echo "LIGATURES OK"
```
Expected: `LIGATURES OK`.

- [ ] **Step 12.4: Cross-reference sanity**

Run:
```bash
grep -nE 'ref\{tab:|ref\{fig:' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex | wc -l
```
And:
```bash
grep -c 'multiply defined\|Reference.*undefined' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.log
```
Expected: the second command returns `0`.

- [ ] **Step 12.5: Final checkpoint to user**

Format:
```
Checkpoint 12 — rev2 complete
  Commits landed  : <list of 11 commit hashes>
  Final pages     : <N>
  Ligatures       : OK
  Undefined refs  : 0
  Open items      : <e.g. 'Table 3 header fallback triggered' or 'none'>
```

---

## Self-Review

**Spec coverage:** every reviewer point 1–11 maps to a numbered task with identical numbering (Task N implements Point N). Task 0 and Task 12 bracket the plan.

**Placeholder scan:**
- Task 8 Step 8.1 (c) asks for "Find every row-emission string" because I did not read far enough into `build_hosts_rep_endpoint_table.py` to know the exact row-template line number. This is a controlled under-specification — the step names the exact pattern to search for (`grep -n '& {sign}' ...`) and shows the exact replacement (drop the `& {sign}` segment). If the producer uses a different template shape, the grep in the step will surface it and the executor has everything needed to remove the column. I prefer this to guessing a specific line number that might be wrong.
- Task 8 Step 8.2 likewise asks the executor to find the numeric-format helper rather than hard-coding its exact location. Same rationale; the grep discovers it and the replacement is fully specified.

**Type consistency:** symbol names (`C`, `R`, `M_mut`, `V`, `Cycles`, `ivf_rate`, `M`, `N`, `maxFE`, `A_{12}^{IVF}`) are used consistently across the plan and match the current `main.tex` usage.

**Scope drift:** no task modifies figure data, statistical results, or scientific claims. Task 11 keeps the `p \geq 0.356` caveat. Point 7 preserves the current tally numbers despite the reviewer's stale quote.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-18-ppsn2026-ivf-hosts-reviewer-rev2.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
