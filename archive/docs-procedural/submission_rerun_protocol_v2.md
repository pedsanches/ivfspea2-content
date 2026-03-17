# Submission Rerun Protocol (IVF/SPEA2 v2 / Current Manuscript)

Date: 2026-03-09
Status: Frozen for WS2

## Scope

This is the canonical evidence protocol for the current manuscript.

It supersedes `docs/submission_rerun_protocol.md` for the present paper. That
older document remains useful as a historical record of the original v1
submission line, but it is not the evidence baseline for the current v2/C26
manuscript.

## Frozen identity mapping

- Display name in paper: `IVF/SPEA2`
- Canonical implementation class: `IVFSPEA2V2`
- Canonical code path: `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/`
- Current processed-data key: `IVFSPEA2`

The paper may use `IVF/SPEA2` for readability, but provenance documents must be
explicit about the class/data-key mapping above.

## Canonical evidence lines

### 1. Main synthetic evidence

- Track: `Track 3 - Submission Evidence Rerun`
- Execution script: `experiments/run_ivfspea2v2_submission.m`
- Algorithm class: `IVFSPEA2V2`
- Frozen profile: `prod_default`
- Frozen defaults: `C=0.12`, `R=0.225`, `M=0.3`, `V=0.1`, `Cycles=2`
- Scope: 51 synthetic instances (`ZDT`, `DTLZ`, `WFG`, `MaF`)
- Run range for IVF/SPEA2: `3001..3060`
- Run range for baselines: `1..60`
- Tag: `SUB20260228_V2`
- FE budget: `100000`
- Mandatory metrics: `IGD`, `HV`

### 2. Engineering transferability evidence

- Source family: dedicated engineering-suite pipeline, not the synthetic rerun
- Canonical raw/summary artifacts:
  - `results/engineering_suite/engineering_suite_raw_main.csv`
  - `results/engineering_suite/engineering_suite_summary_main.csv`
  - `results/engineering_suite/engineering_suite_pairwise_main.csv`
- Key rule: engineering evidence is reported separately and must not be merged
  into synthetic confirmatory claims.

### 3. Supportive discovery/tuning evidence

- Discovery ablation: `results/ablation_v2/phase1/`, `results/ablation_v2/phase2/`, `results/ablation_v2/phase3/`
- Tuning track: `data/tuning_ivfspea2v2/phaseA/`, `data/tuning_ivfspea2v2/phaseB/`, `data/tuning_ivfspea2v2/phaseC/`
- Key rule: these tracks support implementation choice and interpretation; they
  are not the manuscript's main confirmatory evidence line.

## Canonical processed sources used by the paper

- Base consolidated metrics: `data/processed/todas_metricas_consolidado.csv`
- Main paper source with modern baselines: `data/processed/todas_metricas_consolidado_with_modern.csv`

Important honesty note:

- these processed CSVs are not canonical by filename alone;
- canonical synthetic evidence is obtained only after applying
  `src/python/analysis/cohort_filter.py`, which keeps:
  - `IVFSPEA2` rows in `3001..3060`
  - non-`IVFSPEA2` rows in `1..60`
  - no `RWMOP*` rows for synthetic claims.

## Paper-facing frozen artifacts

The current submission release is controlled by the following files:

- `results/submission_release_manifest.csv`
- `results/submission_release_checksums.sha256`
- `results/submission_claim_traceability.md`

Any paper-facing artifact not represented in the release manifest should be
treated as out of scope for submission until added explicitly.

## Path-precedence verification

Before any future rerun that claims to regenerate manuscript evidence, verify in
MATLAB:

```matlab
which IVFSPEA2V2 -all
```

The first resolution must be under:

`src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/`

## Integrity rules

- Do not use `docs/submission_rerun_protocol.md` as the current manuscript's
  frozen evidence baseline.
- Do not claim synthetic results from `data/processed/todas_metricas_consolidado_with_modern.csv`
  without the `cohort_filter.py` windows.
- Do not mix engineering rows into synthetic confirmatory counts.
- Do not mix discovery/tuning artifacts into confirmatory synthetic claims.
- Keep `IGD` and `HV` together in all regenerated final evidence.
- Record provenance changes only through manifest/checksum updates, never by
  undocumented manual replacement.

## Definition of done for WS2

WS2 is complete when all items below are true:

- the current manuscript has one explicit synthetic evidence line;
- the current manuscript has one explicit engineering evidence line;
- processed CSV usage is documented together with the required cohort filter;
- paper-facing artifacts are listed in `results/submission_release_manifest.csv`;
- checksums exist in `results/submission_release_checksums.sha256`;
- main claims are mapped to frozen artifacts in `results/submission_claim_traceability.md`.
