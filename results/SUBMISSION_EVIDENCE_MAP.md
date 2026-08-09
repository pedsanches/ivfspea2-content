# Submission Evidence Map

This document condenses the repository's main claim mapping, inferential roles,
and verified headline numbers.

## Main supported claim

Claim:

- `IVF/SPEA2` improves canonical `SPEA2` on many synthetic out-of-sample
  instances under fixed evaluation budgets.

Canonical artifacts:

- `results/tables/claims_summary_audit.csv`
- `results/tables/claims_summary_instance_details.csv`
- `src/python/analysis/compute_claims_summary.py`
- `src/python/analysis/cohort_filter.py`

Inferential role:

- confirmatory synthetic host comparison

## Secondary supported claims

### HV support

- artifacts:
  - `results/tables/claims_summary_audit.csv`
  - `results/tables/hv_per_instance_M2.tex`
  - `results/tables/hv_per_instance_M3.tex`
- role: confirmatory support only

### Bounded-gain framing and runtime trade-off

- artifacts:
  - `results/tables/claims_summary_instance_details.csv`
  - `results/tables/runtime_overhead_baselines.tex`
  - `paper/springer-nature/figures/effect_magnitude_igd.pdf`
- role: confirmatory support

### Exploratory multi-baseline positioning

- artifacts:
  - `results/tables/igd_m2_detailed_with_modern_table.tex`
  - `results/tables/igd_m3_detailed_with_modern_table.tex`
  - `paper/springer-nature/figures/friedman_avg_rank_igd.pdf`
  - `paper/springer-nature/figures/heatmap_a12_M2.pdf`
  - `paper/springer-nature/figures/heatmap_a12_M3.pdf`
- role: exploratory only

### Engineering transferability

- artifacts:
  - `results/engineering_suite/engineering_suite_pairwise_main.csv`
  - `results/engineering_suite/engineering_suite_summary_main.csv`
  - `results/tables/engineering_metric_profiles_summary.csv`
  - `paper/springer-nature/figures/engineering_metric_profiles.pdf`
  - `paper/springer-nature/figures/engineering_fronts_rwmop9_rwmop8.pdf`
- role: external support only

### Tuning and ablation support

- artifacts:
  - `results/tuning_ivfspea2v2/tuning_phase_ranking.csv`
  - `paper/springer-nature/figures/tuning_heatmap_combined.pdf`
  - `results/ablation_v2/phase1/phase1_summary.csv`
  - `results/ablation_v2/phase2/phase2_pairwise_adjusted.csv`
  - `results/ablation_v2/phase3/phase3_raw_metrics.csv`
  - `results/ablation_v2/phase3/phase3_igd_table.tex`
  - `results/ablation_v2/phase3/phase3_hv_table.tex`
- role: supportive only

## Verified headline numbers

The repository currently supports the following checked headline statements.

- Abstract Holm-corrected out-of-sample `IGD` counts:
  - `M=2`: `19/2/3`
  - `M=3`: `12/0/3`
- Full-suite Holm `IGD` counts:
  - `M=2`: `22/3/3`
  - `M=3`: `15/1/7`
- Engineering `IGD` pairwise summaries:
  - `RWMOP9`: `8/0/0`
  - `RWMOP21`: `3/2/3`
  - `RWMOP8`: `1/1/5`
- Phase 3 framing remains consistent with:
  - `v2 vs v1`: `0/50/1` on `IGD`
  - `v2 vs SPEA2`: `25/25/1` on `IGD`

## Interpretation rule

If a manuscript sentence cannot be linked to one of the artifact groups above,
it should not be treated as part of the frozen evidence surface.

## Locating an artifact

Every artifact named above is a row in `results/submission_release_manifest.csv`,
whose `availability` column states what to expect:

| `availability` | What it means for a reader |
|---|---|
| `in_repo` | Present in a clone; `sha256` in the manifest is authoritative. |
| `build_output` | Not in a clone. Run the command in the `producer` column. |
| `archived_offline` | Not distributed. `archived_path` records where it lived; the content is procedural, not evidential. |
| `deposit_only` | Ships in the Zenodo deposit named in `notes`, not in the repository. |

`make verify-release` checks all of this mechanically, so a broken pointer fails
a build rather than surviving to a reader.

The manuscript figures moved from `paper/figures/` to
`paper/springer-nature/figures/` in commit `9f3e210`, when the paper tree was
reorganized by manuscript. Paths above reflect the current layout; the manifest
records the historical location for anything whose bytes also changed.

Detailed procedural records and packaging notes were deliberately kept out of the
distributed repository so that the visible surface emphasizes knowledge and
evidence rather than workflow history. They are recorded as `archived_offline`
rows in the manifest rather than shipped.
