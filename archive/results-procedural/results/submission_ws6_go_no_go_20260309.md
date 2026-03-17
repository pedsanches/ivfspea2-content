# WS6 Go/No-Go Memo

Date: 2026-03-09
Status: Updated final gate assessment after WS5/WS6 close-out

## Verification summary

### Builds

- Main manuscript PDF: PASS
  - `paper/build/sn-article.pdf`
- Flattened single-file PDF: PASS
  - `paper/build_submission/sn-article_submission.pdf`
- Supplementary tables PDF: PASS
  - `paper/build_submission/ivfspea2_supplementary_tables.pdf`

### Tests

- Python tests: PASS
  - `6/6` passed via `tests/python/test_analysis.py`
- MATLAB tests: PASS
  - `31/31` passed via `tests/matlab/run_tests.m`

### Claim audit

- PASS for the key checked headline claims
  - see `results/submission_ws6_claim_audit_20260309.md`

## Remaining cautions

### Remaining cautions

- The flattened build still uses the repository-local class path
  `../cls/sn-jnl`, which is acceptable for a packaged upload bundle but should
  be kept together with the class file.
- Minor overfull/underfull float-page warnings remain in the manuscript logs,
  but the severe appendix-table overflow issue is gone from both the main and
  flattened manuscript builds.

## Decision

Recommended gate result: `GO`, with packaging discipline.

Reason:

- the manuscript's scientific claims are controlled and audited;
- Python and MATLAB test entrypoints are green;
- the main manuscript, flattened manuscript, and supplementary tables all build;
- the appendix-width blocker was resolved by moving per-instance tables to a
  dedicated supplementary artifact.

## Final packaging steps

1. Assemble the final upload bundle with `paper/build_submission/sn-article_submission.pdf`,
   `paper/src/sn-article_submission.tex`, `paper/build_submission/ivfspea2_supplementary_tables.pdf`,
   figures, class file, BST, and bibliography.
2. Optionally refresh the release manifest/checksums if you want the internal
   provenance package to reflect the new gate state exactly.
