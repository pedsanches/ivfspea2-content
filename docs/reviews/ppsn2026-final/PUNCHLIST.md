# PPSN 2026 Camera-Ready — Reviewer Punchlist

Single source of truth mapping every actionable reviewer comment to an action,
a manuscript location, a cost/page estimate, and a status. Raw reviews:
[`reviews.md`](reviews.md).

## Context that drives triage

- **Decision = ACCEPT.** Best-effort camera-ready; **no re-review, no rebuttal**.
  → We are *not* obligated to run new experiments; honest framing/limitations
  are sufficient for methodological asks.
- **Deadline: 2026-06-12 AoE** (today 2026-06-06 → ~6 days).
- **14-page hard cap; PDF is already at exactly 14 pages.** Net rule:
  **every addition must be offset by a cut.** Conveniently, R2 + R3 mostly ask
  to *shorten*. Recompile and check `pdfinfo … | grep Pages` after every batch.
- **Reviewer temperature:** R3 = strong accept (5, expert) but a long editorial
  punchlist; R2 = lean accept, wants readability; R1 = wants more controlled
  experiments (the only "hard" reviewer, and out of scope for camera-ready).
- **Weighting (author directive): R3 carries the most weight** — domain expert,
  confidence 5. Target *full coverage* of every R3 item; **when reviewers
  conflict, resolve in R3's favor.** R1's experiment-scale asks stay deferred.

## Conventions

- Reviews live in `docs/reviews/ppsn2026-final/`.
- Commit tag for this pass: **`camera-ready: [ID] short description`**
  (the `revision-rev2` tag was the round-1 response, dated 2026-04-18 — do not reuse).
- One compilable commit per coherent batch; check page count each time.

Status legend: ☐ todo · ◐ in progress · ☑ done · ⊘ won't-do (concede in text).

## Writing principles (apply to EVERY edit)

- **Integrate, don't rebut.** Every change must read as native academic prose
  that was always part of the paper — never as a reply to a reviewer. No "as
  noted", no defensive "we did not do X arbitrarily", no traceable rebuttal
  language. State design decisions **declaratively and positively** (e.g.
  *"We study every host for which an IVF realization has been published…"*, not
  *"These hosts were not chosen freely…"*).
- Limitations/threats are the authors' own measured self-assessment (standard
  practice), not concessions visibly extracted by reviewers.
- Keep tone, register, and terminology consistent with the surrounding text.

---

## Lane 0 — Hygiene & line-level fixes (cheap, mostly length-neutral or shrinking)

| ID | Rev | Location (≈line) | Action | Page Δ | Status |
|----|-----|------------------|--------|--------|--------|
| H1 | R3 | refs.bib `zambrano2026ivfspea2` | Drop `url` when it duplicates the DOI; remove copied page numbers; for [20] avoid claiming formal publication. Done: removed dup `howpublished` URL, note→"preprint, under review". | 0 | ☑ |
| H2 | R3 | references.bib (small venues) | Add date/address; add publisher where non-obvious; strip bogus "p.1" page ranges. Done: stripped `pages={1--N}` from 4 IVF-family conf. entries. Deferred: venue date/address/publisher enrichment. | 0 | ◐ |
| H3 | R3 | §1 p2 (`M-PAES`, l.48); §6 p13 (`IVF/NSGA-II's`, `k-nearest-neighbour`) | Fix bad line breaks via `\mbox{}`/non-breaking hyphen. Done: `\mbox{M-PAES}`, `\mbox{IVF/NSGA-II's}` ×2. Note: "k-nearest-neighbour" not in source (reviewer PDF-extraction artifact). | 0 | ☑ |
| H4 | R3 | author block / Meteor | Verify names, affiliations, author order match | 0 | ☐ |
| H5 | committee | repo upload bundle | Assemble LaTeX source + PDF + figures; remove outdated files; confirm LNCS | 0 | ☐ |
| H6 | R3 | abstract l.36; §1 l.59; §3 l.113; §7 l.237 | Resolve **"published" conflict**: [20] is the authors' own preprint — replace "published reference implementation" (l.82) / over-claims of "published" *for [20]* with e.g. "the prior implementation we build on" / "our reference implementation". Keep "published" only where it refers to Sampaio refs that are genuinely published. Done: l.36/59/237 "published"→"existing"; l.82 →"the implementation introduced in [20] and adopted here"; l.228 dropped "published". | 0 | ☑ |

> H6 note: round-1 edit had changed "canonical" → "published reference
> implementation" for [20]; R3 explicitly rejects "published" here. Reverse course.

---

## Lane 1 — Readability & de-jargon (R2 + R3; the bulk; net **frees** space)

| ID | Rev | Location (≈line) | Action | Page Δ | Status |
|----|-----|------------------|--------|--------|--------|
| C1 | R3 | abstract l.36 | Remove "is a first-order design concern"; cut waffle; keep only load-bearing words | − | ☐ |
| C2 | R3 | keywords l.38 | Replace keywords that merely repeat the title with non-redundant terms (e.g. memetic/local search, host–operator compatibility, empirical comparison) | 0 | ☐ |
| C3 | R3 | title l.21,24 | **Decided (title A).** New title: *"Operator-Host Compatibility: When Does IVF Help SPEA2, NSGA-II, or NSGA-III?"* (keeps the contribution anchor; question maps onto §5.1–§5.4). Update `\title` and `\titlerunning`; keep keywords (C2) non-redundant with the new title. | 0 | ☑ |
| C4 | R3 | §1 opening l.42–46 | Don't open on "intensification operators"; lead with the plain-language question in PPSN terms, then introduce IVF | ± | ☐ |
| C5 | R3 | §1 l.46 (mother/father) | Add one sentence: mothers/fathers share the **same representation**; "sex" is a transient role assigned per cycle (not fixed per individual). Done: gloss added in §2.2 ("ordinary individuals with the same representation; the labels denote only a role within a pairing"). | + small | ☑ |
| C6 | R3 | §4 l.118 | State population model explicitly: fixed `N=100`, generational; whether offspring are produced by crossover **and** mutation or alternatives | + small | ☐ |
| C7 | R3 | §1 l.48 | Gloss or drop "hybrid and memetic" | 0 | ☐ |
| C8 | R3 | §1 l.55 (Hypothesis H) | Rewrite Hypothesis H paragraph in simpler words | 0 | ☐ |
| C9 | R3 | §1 l.58–59 | Rename "Scope of inference" heading (try "What we compare"); delete "in this paper" (l.59, l.113) | − | ☐ |
| C10 | R2,R3 | §3.1–3.3 l.79–94 | **Biggest lever:** move duplicated technical settings into Table 1; replace freed prose with concept/motivation per host; resolve "high objective-space dissimilarity" + "average fitness improves collectively" (l.82) with concrete definitions. Done: §3.1–3.3 rewritten — dropped numeric param lists (now only in §4 provenance), clarified dissimilar-father + collective-continuation + DE; net length-neutral. | − (net) | ☑ |
| C11 | R3 | §3.2 l.87 | State explicitly: fathers sampled **uniformly at random from the whole population** | 0 | ☑ |
| C12 | R3 | Table 1 l.~100–110 | "Mother selection" row: harmonize "fitness" vs "rank" wording (or footnote why they differ). Done: explained in §3 intro ("Mother selection always follows the host's own primary ordering---scalar fitness for SPEA2, Pareto rank for NSGA-II/III"). | 0 | ☑ |
| C13 | R3 | §3 l.111–113 | Consider promoting the "Table 1" paragraph to a short §3.4 | 0 | ☐ |
| C14 | R3 | §4 headings l.120–135 | Rename weak `\paragraph` titles ("Budget accounting", p5 headings) | 0 | ☐ |
| C15 | R3 | §5/§5.x titles l.150,168,177,191 | Reconsider "Per-Host Compatibility" / "Geometry Stratification" / "Dynamic Evidence" wording | 0 | ☐ |
| C16 | R3 | §5 l.130,158,216 | First use of "BH" is already spelled out (l.130). Reduce bare "BH" in captions; keep one full "Benjamini–Hochberg (BH-FDR)" anchor; trim ECDF/ΔAUC/power-loss jargon where avoidable | − | ☐ |
| C17 | R3 | §5 l.141 | "The ordering is immediate" → plain wording | 0 | ☐ |
| C18 | R3 | §5.3 l.189 | Rephrase sentence starting "At $M=3$…" | 0 | ☐ |
| C19 | R3 | §6 l.228 | Rephrase first sentence of Discussion | 0 | ☐ |
| C20 | R3 | §7 l.237 | Remove "This paper"; make readable | 0 | ☐ |

---

## Lane 2 — Scholarly additions (cheap content that satisfies the expert R3)

| ID | Rev | Location | Action | Page Δ | Status |
|----|-----|----------|--------|--------|--------|
| S1 | R3 | §2 related work | Add **Tackett soft brood selection** (WCCI 1994, doi:10.1109/ICEC.1994.350023) + 1 sentence positioning IVF vs brood selection | + small | ☐ |
| S2 | R3 | §3.3 / Table 1 l.92 | Define **DE = Differential Evolution** at first use + citation; one clause on how DE/current-to-best relates to the NSGA-III population. Done: DE defined + cited (storn1997de) in §3.3 with current-to-best gloss. | + small | ☑ |
| S3 | R3 | §4 l.118 / §5.1 | Strengthen benchmark answerability: confirm suite/M/N/maxFE (mostly present) and add explicit pointer that per-instance "which technique won where" is in Fig. 2 + the archived artifact | + small | ☐ |

---

## Lane 3 — Framing concessions for methodology (R1 + R3; **no new experiments**)

| ID | Rev | Location | Action | Page Δ | Status |
|----|-----|----------|--------|--------|--------|
| **F0** | **R1.1**,R3 | §1 l.50; §7 l.239 | **Highest-value framing fix.** Make the host-**inclusion criterion** explicit: the three hosts are exactly the MOEAs with an existing IVF realization (NSGA-II, NSGA-III, SPEA2-preprint-under-review); to our knowledge no IVF/RVEA or IVF/MOEA/D exists, so including them means *designing* new operators → future work. Cite RVEA + MOEA/D (refs don't count to the 14pp cap). Reframes R1's "swap NSGA-III" from a flaw to out-of-scope. Also fixes "published"→"under review" for [20] (see H6). **Phrase declaratively** (positive inclusion criterion), never as a rebuttal. Done: §1 l.50 rewritten ("We study IVF across the three hosts for which a realization has been proposed…"; RVEA/MOEA/D not proposed → future work). Also covers F3. | + small | ☑ |
| F1 | R1.2,R3 | §6 threats-to-validity l.228 | Name explicitly the **SBX-vs-DE variation-operator confound** (already partially conceded — make it a named threat) | + small | ☐ |
| F2 | R1.4 | §6 | Add the **absolute-performance / weak-baseline** caveat: relative IVF gain may partly reflect host baseline strength; point to absolute IGD/HV in artifact | + small | ☐ |
| F3 | R1.1 | §6/§7 future work | Concede limited host set (now mainly handled by **F0**); keep one future-work line on RVEA/MOEA/D as a controlled comparison requiring new IVF operators | + small | ☐ |
| F4 | R1.3,R1 overall | §6/§7 | State that a fully **controlled factorial** (host × operator × IVF strategy) is future work; keep current claims at the pipeline level | 0 | ☐ |
| F5 | R3 | §6 | Acknowledge alternative explanation: differences could stem from **selection pressure / diversity preservation**, not only host compatibility | + small | ☐ |
| F6 | R3 | §1 p2 "host" term | **Decided: partial rename (b)** — keep "host" in the title; in prose soften and add a justifying line at first use, preferring EMO-community phrasing (host MOEA / base algorithm) where natural. | 0 | ◐ |

---

## Lane 4 — Figures (costliest; touch Python plotting scripts)

| ID | Rev | Target | Action | Status |
|----|-----|--------|--------|--------|
| G1 | R3 | all figs, esp. Fig 5 | Replace **red/green** with colorblind-safe palette (Fig 5 convergence shading is the real red/green offender; Fig 2 blue/red is borderline — verify) | ☐ |
| G2 | R3 | Fig 2, Fig 4, Fig 5 | Increase font sizes for print legibility | ☐ |
| G3 | R3 | Fig 4, Fig 2, Fig 1 | Shorten over-long captions (l.158, l.185, others) | ☐ |
| G4 | R3 | Fig 1 | Y-axis: spell out abbreviation; clarify legend; explain "4 things" (3 hosts + ?); | ☐ |
| G5 | R3 | Fig 1 + Fig 3 | Evaluate merging Fig 1 and Fig 3 (also helps page budget) | ☐ |

> Scripts: `src/python/analysis/plot_hosts_figures_v2.py`,
> `plot_hosts_convergence_v2.py`. Regenerate via `.venv/bin/python …`.

---

## ⊘ Won't-do for camera-ready (concede in text, don't attempt)

| ID | Rev | Why not | Where conceded |
|----|-----|---------|----------------|
| X1 | R1.1 | Replace NSGA-III with RVEA/MOEA/D → new full campaign, infeasible in 6 days; paper is accepted as-is | F3 (future work) |
| X2 | R1.3 | Expand scale + controlled factorial → new experiments | F4 (future work) |
| X3 | R1.2 | Equalize SBX/DE across hosts → re-running all pipelines | F1 (named threat) |
| X4 | R3 | §2.2 "perhaps a picture" → new figure costs page budget we don't have | — (skip) |

---

## Suggested execution order (6-day, deadline-aware)

> **Priority rule: full R3 coverage is the target.** Lanes 0/1/2/4 are almost
> entirely R3-driven, so the order below already front-loads R3. Lane 3 (R1
> framing) is secondary but cheap. Do not close the revision with any R3 item
> still ☐ unless it is an explicit author decision (C3, F6, G5).

1. **Lane 0 + Lane 3** first (hygiene + concessions): cheap, de-risks the
   "published"/[20] credibility hit (R3), and answers R1 honestly. ~1 sitting.
2. **Lane 1 (C10 first)**: the §3.1–3.3 trim is the highest-leverage move —
   satisfies both R2 and R3 and *creates* the page budget for everything else.
3. **Lane 1 remainder + Lane 2**: clarity rewrites + Tackett/DE/benchmark adds.
4. **Lane 4 (figures)** last: most effort, least risk to acceptance; do as many
   as time allows in priority G1 → G2 → G3 → G4 → G5.
5. Recompile + `Pages` check after **every** batch; freeze when ≤14pp and clean.

## Optional "summary of changes" (no rebuttal channel exists)

Since there is no re-review, prepare at most a short internal changelog
(`docs/reviews/ppsn2026-final/changes.md`): one line per ID above, grouped by
reviewer, e.g. "R3-abstract: removed 'first-order design concern', cut waffle
(C1)". Useful for the camera-ready cover note if the system allows one, and as a
record. Not a formal point-by-point rebuttal.

---

## Open questions for the author

- **C3 (title):** R3 (top weight) calls it confusing/jargon-laden — keep, or
  soften? If softening, I can propose candidates.
- **F6 ("host" term):** R3 (top weight) says "host" is wrong; R2 liked it.
  Keep+justify, partial rename, or full rename? (recommend partial rename)
- **G5 (merge Fig 1 + Fig 3):** merge to save space, or keep separate?
- Will the camera-ready system accept a cover note / summary of changes?
