# Master's Thesis Revision Plan

The imported manuscript is a historical baseline, not the current scientific
record. Revise it in evidence order.

## 1. Administrative metadata

- Confirm the defense date and set `\dia`, `\mes`, and `\ano` in `main.tex`.
- Re-enable `\publica` in `main.tex` after confirming that date.
- Confirm the examination committee, fill `pre/pre_aprovacao.tex`, and re-enable
  its `\input` in `main.tex`.
- Confirm whether the current INF/UFG class and required front matter are still
  institutionally valid.
- Confirm the monographic or Scandinavian format with the supervisor and add
  the explicit format declaration required by Resolução INF nº 02/2023/PPGCC;
  the imported document does not currently contain it.

## 2. Algorithm identity

Superseded by the author's decision recorded in `REWRITE_SPEC.md` §1. The
dissertation presents a **single** IVF/SPEA2 — the coupling proposed in the
Springer Nature manuscript — and never versions it.

- Do not write "v1" or "v2" in `tex/**` or `pre/**`. Distinguish prior work by its
  **coupling**: which decisions bind the IVF operator to its host.
- Document the two coupling decisions: dissimilar father selection, and the
  collective cycle-continuation criterion.
- State the promoted configuration once: `C=0.12`, `R=0.225`, `M=0.3`, `V=0.1`,
  `Cycles=2`.
- The prior formulation does not enter the text. Its cohort (`2001–2100`) is
  absent from this checkout, so its tables have no reproducible producer. Where
  evidence compares against it — the ablation, and the tuning baseline — write by
  the absent mechanism, per `REWRITE_SPEC.md` §1.3.

## 3. Evidence synchronization

- Rebuild the main synthetic comparison from the frozen 60-run cohort
  (IVF/SPEA2 `3001–3060` against SPEA2 `1–60`).
- Report IGD and HV together.
- Separate confirmatory, exploratory, engineering, tuning, and ablation roles.
- Reconcile the historical 79-instance wording with the current 51-instance
  synthetic evidence model.
- Replace universal-superiority language with the repository's bounded,
  geometry-dependent conclusions.

## 4. Article synthesis

- Integrate the Memetic Computing tuning, ablation, convergence, mechanism, and
  engineering evidence.
- Integrate the PPSN/CLEI landscape-feature and population-dynamics analyses.
- Integrate the warmup/controller evidence without reusing IGD labels as an
  independent validation endpoint.
- Integrate the operator-host compatibility comparison across SPEA2, NSGA-II,
  and NSGA-III.
- Treat PPSN and CLEI as two editorial outputs of one evidence family, not as
  independent replications.
- Reconcile the Hosts manuscript's 100-checkpoint rerun description with the
  current ten-checkpoint `hosts_convergence.csv` before citing trajectory
  counts.

## 5. Reproducibility

- Add a thesis evidence table linking each claim to a dataset and analysis
  script from `data-sources.toml`.
- Record cohort filters, run IDs, pairing status, multiplicity correction, and
  metric direction.
- Record explicit overlaps where one article reuses a subset of another
  article's runs.
- Add an appendix describing how ignored raw data are recovered from the
  corresponding archived releases.

## 6. Final validation

- Run the repository tests relevant to every regenerated artifact.
- Compile with `make thesis`.
- Render with `make thesis-render` and inspect every page.
- Check citations, references, figures, tables, page numbering, and PDF
  metadata before submission.
- Regenerate the five legacy statistical figures with embedded TrueType fonts
  (`matplotlib.rcParams["pdf.fonttype"] = 42`) to replace their current Type 3
  fonts before archival or institutional submission.
- Enable the `nocolorlinks` class option for the final print-ready PDF if
  required by the institution.
