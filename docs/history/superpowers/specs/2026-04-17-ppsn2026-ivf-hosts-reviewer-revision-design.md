# PPSN 2026 IVF-Hosts Manuscript — Reviewer Revision Design

**Date:** 2026-04-17
**Author:** Pedro Sanches Zambrano
**Branch:** `ppsn2026-population-dynamics`
**Target:** `paper/ppsn2026-ivf-hosts/main.tex` (246 lines, revision passo 10)

## 1. Goal & Non-Goals

**Goal.** Convert the reviewer punchlist (CRITICAL C1–C2, MAJOR M1–M7, MODERATE Mo1–Mo10, MINOR items, five figure caption rewrites, 20 sentence-level rewrites, three cross-section transitions, Zenodo DOI mint) into a committed, PDF-verified, DOI-archived revision of `main.tex`.

**Non-goals.**
- No new experiments or analyses.
- No changes to scientific claims, effect sizes, or win/tie/loss tallies.
- No figure redesigns beyond splitting Fig. 2 into M=2 / M=3 panels.
- No structural reorganization of §§1–7.
- No silent strengthening of claim language during prose polish (reviewer's explicit warning).

## 2. Decisions Already Made

| ID | Decision | Source |
|----|----------|--------|
| D1 | Fig. 2 treatment: Option (A) — split into two stacked panels (M=2 top, M=3 bottom), keep in main text. | User, 2026-04-17 |
| D2 | Ref [20] (`zambrano2026ivfspea2`) → Research Square preprint DOI `10.21203/rs.3.rs-9431034/v1`. | User, 2026-04-17 |
| D3 | Artifact DOI: mint from current branch via GitHub release + Zenodo webhook. | User, 2026-04-17 |
| D4 | Execution mode: full execution by Claude with per-phase diff checkpoints. | User, 2026-04-17 |

## 3. Phased Plan

### Phase 0 — Preflight & Information Gathering

**Actions.**
- Detect MATLAB release from the installed `matlab -batch "version"` output.
- Detect PlatEMO version from `src/matlab/lib/PlatEMO/` (README, CITATION, or `VERSION`). Fall back to the git submodule commit hash if no explicit version string exists.
- Collect CPU/RAM/OS via `lscpu`, `free -h`, `uname -a`.
- Compile the current PDF with `cd paper && make ppsn2026-ivf-hosts` (or equivalent) and extract text with `pdftotext build/main.pdf -`. Search for ligature tells: `dierent`, `intensication`, `eect`, `conrmatory`, `dicult`.
- Classify ligature outcome:
  - **Real issue** if extracted PDF shows `intensication`. Then add `\usepackage{cmap}` + confirm `T1` fontenc + retest, or switch to `\usepackage{lmodern}`.
  - **Reviewer-side artifact** if text extraction is clean under `pdftotext -layout`. Then no action; note in spec review.

**Checkpoint A.** I report the five values (MATLAB release, PlatEMO version, CPU, RAM, OS) and the ligature classification. You confirm before I paste any of them into §4.

### Phase 1 — Critical + Major Text Edits

**Target addresses** (line numbers relative to current `main.tex`):

| Item | Location | Action |
|------|----------|--------|
| C1 | §4 "Metrics and references" + §7 final paragraph | Replace `[release]`, `[PlatEMO version]`, `[CPU / RAM / OS]`; leave `[artifact URL or DOI]` as a TODO marker pending Phase 6. |
| M1 | Abstract | Replace `+33/=15/-3 IGD outcomes` phrasing with "33 wins, 15 ties, and 3 losses in IGD" across all three triplets. Remove editorializing "only". |
| M2 | Abstract, §1 Scope, §3 last sentence, §6 opener, §7 opener | Keep full statement in §1 Scope + §7 opener. Compress abstract to "pipeline-level compatibility interpretation" phrase only. Replace §3 last sentence with reviewer's proposed rewrite. Replace §6 opener with reviewer's proposed rewrite. |
| M3 (×6) | §5 opener (×2), §5.1 (×2), §5.2 opener, §5.3 | Apply rewrites 6–11 from reviewer Part 5.3. |
| M4 | §4 Budget accounting, §5.4 aggregate sentence | Apply rewrites 4 and 14 from Part 5.3 (also removes "at at most" redundancy). Move trajectory-interpolation sentence from §4 to §5.4. |
| M5 | §3.1 | "IVF/SPEA2 v2 is the canonical implementation in this study" → "IVF/SPEA2 v2 is the published reference implementation used in this study [20]." |
| M6 | §1 "actionable feedback" and all other sites | Replace with "directional feedback" globally; apply rewrite 1 from Part 5.3. |
| M7 | §5.4 Fig. 4 callout + caption | Add reviewer's "early separation (FE/maxFE < 0.3) indicates…" sentence; replace caption with Part 4 version. |

**Checkpoint B.** `git diff main.tex` review.

### Phase 2 — Fig. 2 Split (M=2 / M=3)

**Actions.**
- Locate the script producing `paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf`. Likely candidates: `src/python/analysis/gen_graph.py`, `build_hosts_paper_csv.py`, or a dedicated heatmap script.
- Modify plotting to produce a 2×1 figure: top panel = 28 M=2 instances, bottom panel = 23 M=3 instances. Each panel keeps all three host rows. Use `constrained_layout` or `tight_layout` so asterisks are legible. Preserve the family-sorted column ordering.
- Regenerate PDF in place.
- Update `\caption{...}` in `main.tex` per reviewer Part 4 Fig. 2 revised caption.
- Rewrite the §5.1 callout per Part 5.5.

**Checkpoint C.** Visual review of the regenerated `hosts_v2_fig2_heatmap.pdf`.

### Phase 3 — Moderate + Minor Edits

**Applied in single commit.**

- Mo1: split the five-clause IVF-genealogy sentence in §1.
- Mo2: compress the §2.2 origin sentence (remove the duplicate with §1).
- Mo3: add a one-line gloss on first use of "mothers/fathers" in §1 or §2.2.
- Mo4: remove the §3 intro paragraph's structural overlap with §2.2.
- Mo5: Table 1 row "Offspring operator" header; move crossover parameter to own column or note.
- Mo6: §5 opener → "At the aggregate level, the three pipelines already separate by a large margin (Fig. 1)." (= rewrite 5 from Part 5.3).
- Also apply rewrite 2 (§1 "common IVF core is stable" → "shared"/"unchanged") and rewrite 12 (§5.3 "indicating that the host mechanism governs…" → reviewer's cleaner verb).
- Mo7: §5.4 reorder sentence on IVF/NSGA-II being "no longer completely inert".
- Mo8: §6 "material" → "relevant".
- Mo9: §7 drop "practically useful".
- Mo10: §4 unify tense ("we conducted", "we executed", "are archived").
- Minor: Table 1 caption punctuation; math `\(\,N - \mathrm{FE}_{\mathrm{IVF},\text{gen}}\,\)` spacing; §5.3 title → "Effect of Objective Dimensionality"; §3 title → "Host-Specific IVF Realizations"; `Cycles=2` → `\textit{Cycles} = 2` consistency; abstract "only" removed (already in M1).
- References: `references.bib` — add `doi = {10.21203/rs.3.rs-9431034/v1}` to ref [20], add DOIs to refs [5] (MaF) and [9] (DTLZ) if retrievable from Crossref.

**Checkpoint D.** diff review.

### Phase 4 — Figure Caption & Callout Rewrites

- Fig. 1 caption: add reading guidance sentence (vertical centre-of-mass of each cloud).
- Fig. 2 caption: completed in Phase 2.
- Fig. 3 caption: add quantified collapse (median ≈ 0.70 → ≈ 0.54) per Part 4.
- Fig. 4 caption: completed in Phase 1 M7.
- Fig. 5 caption: update "FE grids aligned…" clause + "30 aligned runs" → "30 runs per algorithm per instance".
- §5 callouts: apply 13, 15–20 from Part 5.3.

**Checkpoint E.** diff review (covers Phases 4 and 5).

### Phase 5 — Cross-Section Transitions

- End §3: add "With the pipelines specified, we now turn to the experimental protocol under which they are compared."
- End §5.3: add "Endpoint analyses alone, however, cannot indicate whether the observed ordering also holds during the search rather than only at its termination."
- End §5 (before §6): add "We now turn from what the evidence shows to what it licenses as interpretation."

Rolled into Checkpoint E.

### Phase 6 — Zenodo Archive Preparation

**Bundle contents.**
```
reproducibility_bundle/
├── README.md                          # how to re-run
├── data/processed/
│   ├── hosts_paper.csv
│   ├── hosts_convergence.csv
│   └── (other per-host CSVs referenced in paper)
├── results/tables/
│   └── (all hosts_*.tex and hosts_*.csv used by the paper)
├── figures/
│   └── (the 5 PDFs referenced in the final main.tex)
└── src/python/analysis/
    ├── build_hosts_paper_csv.py
    ├── build_hosts_convergence_csv.py
    ├── compute_iqr_tables.py
    ├── gen_graph.py
    └── (heatmap script modified in Phase 2)
```

**Release metadata (draft).**
- **Tag:** `ppsn2026-ivf-hosts-rev1`
- **Title:** "IVF-Hosts PPSN 2026 reviewer revision — reproducibility artifact (v1)"
- **Description:** one-paragraph abstract mirror + "This archive contains all processed CSVs, LaTeX tables, figure PDFs, and Python analysis scripts required to reproduce the tables and figures reported in the paper."
- **Authors:** Pedro Henrique Sanches Pelegrino Zambrano (+ supervisors if applicable).
- **Keywords:** mirror paper keywords.
- **License:** MIT (code) + CC-BY-4.0 (data) unless user specifies otherwise.

**Checkpoint F.** User creates GitHub Release with the prepared tag and release notes; authorizes Zenodo webhook if not already enabled; reports back the minted DOI. I then fill the DOI into both manuscript slots (§4 and §7) and into a `\bibitem` for the artifact if appropriate.

### Phase 7 — Verification

- Compile PDF: `cd paper && make ppsn2026-ivf-hosts`.
- Text extraction: `pdftotext -layout build/main.pdf - | grep -E 'dierent|intensication|eect|conrmatory|dicult|simpli' || echo OK`.
- Placeholder sweep: `grep -n '\[.*\]' paper/ppsn2026-ivf-hosts/main.tex` — should match nothing outside intentional brackets.
- Float overflow: open PDF, scan for figures/tables pushed outside page body.
- Final `git diff main.tex` full read.

**Checkpoint G.** Sign-off commit (`revision: [passo 11] reviewer-driven line edit + Fig. 2 split + Zenodo DOI`). Optionally squash-merge into main or keep on branch per user preference.

## 4. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Ligature issue is real in the compiled PDF, not just a reviewer-side artifact. | Phase 0 detects this deterministically; Phase 1 includes a one-line fontenc/lmodern fix if needed. |
| Polishing prose accidentally strengthens a hedged claim. | Every Phase 1/3/4 edit is diff-reviewed (Checkpoints B, D, E) with hedge words (`suggests`, `conditional`, `suggestive`, `not yet`) preserved by explicit grep before commit. |
| Fig. 2 split introduces a visual regression (cells become *smaller*, not larger, if the aspect ratio is mishandled). | Checkpoint C requires visual sign-off before proceeding. Fallback: revert to single panel + keep improved caption (reviewer Option C). |
| Zenodo webhook not pre-authorized on the repo. | Release notes tag `ppsn2026-ivf-hosts-rev1` is reversible; user enables the webhook once and the DOI mints automatically on next release. Interim fallback: manual Zenodo upload of the bundle zip. |
| DOI resolution on Crossref for refs [5] / [9] fails. | Accept no DOI for those two entries; this is not a blocker (reviewer marked it as a minor item). |
| `paper/Makefile` target name differs from assumption. | Phase 0 verifies the actual target by reading `paper/Makefile`. |

## 5. Commit Plan

One commit per phase, message style matching existing `revision: [passo N] ...`:

1. `revision: [passo 11a] placeholders + critical/major edits` (Phase 0 + 1)
2. `revision: [passo 11b] split Fig. 2 by M` (Phase 2)
3. `revision: [passo 11c] moderate/minor edits + bib DOIs` (Phase 3)
4. `revision: [passo 11d] figure captions + transitions` (Phases 4 + 5)
5. `revision: [passo 11e] Zenodo archive` (Phase 6 bundle prep, before DOI mint)
6. `revision: [passo 11f] artifact DOI filled` (Phase 6 post-mint)
7. `revision: [passo 11g] reviewer revision final` (Phase 7 sign-off)

Phases may merge if their diffs are small.

## 6. Success Criteria

- Zero unresolved `[...]` placeholders in `main.tex`.
- `pdftotext -layout` of compiled PDF contains no ligature-extraction tells.
- Fig. 2 renders with asterisks individually legible at 100% print size.
- All 20 reviewer-flagged sentences rewritten per Part 5.3.
- All 5 figure captions match Part 4 revisions (or approved variants).
- Zenodo DOI resolves and is cited in both §4 and §7.
- `git log --oneline` shows clean phased commit history.
- PDF compiles without LaTeX errors or undefined-reference warnings.

## 7. What Remains After This Revision

- PDF submission to PPSN 2026 (user action).
- Memetic Computing submission of the separate IVFSPEA2 standalone paper (referenced as preprint [20] but not the subject of this revision).
- Potential camera-ready pass if the paper is accepted.
