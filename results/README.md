# Results

This directory contains the frozen evidence and generated artifacts used by the
current manuscript, plus a small number of historical outputs retained for
protocol continuity.

Reviewer-facing entry points:

- `results/SUBMISSION_EVIDENCE_MAP.md`
- `results/submission_release_manifest.csv`
- `results/submission_release_checksums.sha256`
- `results/submission_comparability_matrix.csv`
- `results/engineering_suite/`
- `results/tables/`

## Verifying this directory

```bash
make verify-release
```

Checks that every row of `submission_release_manifest.csv` resolves and that
every entry in `submission_release_checksums.sha256` matches. The manifest's
`availability` column says which rows are files in a clone (`in_repo`), which
are regenerated (`build_output`), which ship only in a Zenodo deposit
(`deposit_only`), and which were never distributed (`archived_offline`).

Procedural records and superseded traceability notes are not distributed with
the repository; they are recorded as `archived_offline` rows in the manifest,
which preserves their historical path without shipping workflow history.
