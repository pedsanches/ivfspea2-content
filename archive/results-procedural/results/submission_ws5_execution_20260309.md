# WS5 Execution Record

Date: 2026-03-09
Status: Editorial close-out completed for method/package alignment

## What WS5 changed

- regenerated `paper/figures/flowchart.pdf` from a new source script that matches
  the current IVF/SPEA2 logic;
- tightened Algorithm 1 notation in `paper/src/sn-article.tex` by:
  - replacing `n_obj` with `M`,
  - explicitly initializing `P_t`, `O_ivf`, and `O_host`,
  - clarifying the role of the working population after environmental
    selection;
- added an appendix note that `AGE-II` is an intentional width-saving
  abbreviation for `AGE-MOEA-II`;
- generated a flattened submission source at
  `paper/src/sn-article_submission.tex` with no live `\input{...}` commands.
- moved the wide per-instance appendix tables out of the main manuscript and
  replaced them with an explicit supplementary-material note in
  `paper/src/sn-article.tex`;
- created a dedicated supplementary tables source at
  `paper/src/ivfspea2_supplementary_tables.tex`.

## New generation tools

- `src/python/analysis/generate_ivfspea2_flowchart.py`
- `scripts/flatten_sn_article.py`

## Verification status

- Main manuscript build succeeds: `paper/build/sn-article.pdf`.
- Flattened single-file build succeeds locally when compiled with explicit
  bibliography search paths: `paper/build_submission/sn-article_submission.pdf`.
- Supplementary tables build succeeds: `paper/build_submission/ivfspea2_supplementary_tables.pdf`.
- The flattened file contains no active `\input{...}` directives.
- The main and flattened manuscript logs no longer contain the previous wide
  appendix-table overflow warnings; remaining warnings are limited to minor
  layout issues and the repository-local class-path convention.

## Honest remaining issues

Remaining items:

- the flattened local build uses `../cls/sn-jnl` for portability inside the
  repository, which is acceptable for packaging but is a local-compilation
  convenience rather than a scientific issue;
- the package still needs a deliberate upload bundle that includes the
  supplementary PDF together with figures, class/style files, and bibliography
  assets.

## Practical conclusion

WS5 now closes the main editorial risks identified for method alignment and
single-file compliance. The appendix-readability blocker was resolved by moving
the per-instance longtables into a separate supplementary artifact.
