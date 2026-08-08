# Master's Thesis - IVF/SPEA2

This is the active, version-controlled home of the IVF/SPEA2 master's thesis.
The initial source was imported from the manuscript snapshot dated 2025-06-15.
The source snapshot in `Downloads` was not modified or deleted.

## Current status

The document compiles, but its scientific content is still the 2025 baseline.
It must not yet be treated as synchronized with the repository's current
evidence. In particular, the current canonical implementation is
`IVFSPEA2V2`, IGD and HV are both mandatory, and claims must follow
`docs/IVFSPEA2_EVIDENCE_MODEL.md`.

See `REVISION_PLAN.md` before changing results or conclusions.

## Scientific writing protocol

Every drafting, revision, translation, synthesis, or review of thesis prose
must invoke the personal skill `$write-scientific-manuscripts` and apply
`SCIENTIFIC_WRITING_PROFILE.md`. The profile fixes the dissertation's
Portuguese style, terminology, evidence hierarchy, article-overlap rules, and
claim boundaries.

The reusable knowledge is installed at
`~/.codex/skills/write-scientific-manuscripts/`; the rules unique to this
research remain version-controlled in `SCIENTIFIC_WRITING_PROFILE.md`.
Material use of generative AI is recorded by session or work batch in
`AI_ASSISTANCE_LOG.md` so that the final institutional or publisher disclosure
does not depend on memory.

The skill deliberately does not optimize text for AI-detector scores. It
produces authorial prose by restoring specific scientific reasoning, verified
evidence, natural Brazilian Portuguese, and calibrated conclusions.

## Commands

From the repository root:

```bash
make thesis-bootstrap # first build only: populate the Tectonic package cache
make thesis-doctor  # validate tools and all declared data sources
make thesis         # compile thesis/masters/build/main.pdf
make thesis-render  # render every PDF page for visual QA
make thesis-clean   # remove thesis build artifacts only
```

The build uses Tectonic and a local compatibility derivative of the legacy UFG
class. The original `inf-ufg.cls` is retained unchanged; `main.tex` uses
`inf-ufg-tectonic.cls`. The first build on a machine without a populated
Tectonic cache requires network access to download the pinned v33 bundle with
`make thesis-bootstrap`. Normal builds are cache-only and reproducible.

## Data policy

- Do not copy article CSV files into this directory.
- Read canonical processed data from repository-level `data/processed/`.
- Add thesis-only analysis code under `src/python/thesis/`.
- Add thesis-only experiment launchers under `experiments/thesis/`.
- Write generated thesis tables and figures under `results/thesis/`.
- Declare every evidence source in `data-sources.toml`.
- Keep synthetic, engineering, tuning, ablation, controller, and host-transfer
  cohorts separate unless an analysis explicitly justifies their combination.

`generated/` is reserved for temporary, build-ready copies of selected
artifacts. Its generated contents are ignored by Git.
