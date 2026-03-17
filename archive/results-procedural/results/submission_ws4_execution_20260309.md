# WS4 Execution Record

Date: 2026-03-09
Status: Completed for data-driven artifacts

## Scope executed

WS4 regenerated the paper's data-driven tables and figures from the frozen
evidence lines defined in WS2 and WS3.

## Commands executed

### Synthetic / statistical regeneration

- `src/python/analysis/audit_submission_cohorts.py`
- `src/python/analysis/compute_claims_summary.py`
- `src/python/analysis/generate_per_instance_tables.py`
- `src/python/analysis/compute_runtime_overhead_baselines.py`
- `src/python/analysis/plot_effect_magnitude.py`
- `src/python/analysis/plot_friedman_avg_rank.py`

### Supportive tuning / ablation regeneration

- `src/python/analysis/plot_tuning_heatmap.py`
- `src/python/analysis/analyze_ablation_v2_phase1.py`
- `src/python/analysis/analyze_ablation_v2_phase2.py`
- `src/python/analysis/analyze_ablation_v2_phase3.py`

### Engineering and front regeneration

- `experiments/process_engineering_suite.m`
- `experiments/extract_fronts_for_paper.m`
- `src/python/analysis/generate_paper_figures.py`
- `src/python/analysis/plot_dtlz4_bimodal.py`
- `src/python/analysis/plot_engineering_metric_profiles.py`
- `src/python/analysis/plot_engineering_fronts_side_by_side.py`

## Scientific notes

- Synthetic confirmatory artifacts were regenerated from the filtered Track 3
  cohort (`IVFSPEA2` 3001--3060; baselines 1--60).
- The raw consolidated synthetic CSV remains mixed-track before filtering; this
  is documented and does not affect the regenerated confirmatory artifacts.
- Engineering artifacts were recomputed with strict common-run matching at
  `n=60` per problem, with valid-run asymmetry preserved in the outputs.
- Front-comparison figures remain illustrative/supportive; they are not used as
  primary inferential evidence.
- Discovery ablation regeneration required explicit fallback to
  `data/legacy/ablation_v2/`, because the archived raw track is no longer stored
  under `data/ablation_v2/` in the current workspace.

## Regenerated manuscript-facing artifacts

- `paper/figures/boxplot_igd_m2.pdf`
- `paper/figures/boxplot_igd_m3.pdf`
- `paper/figures/effect_magnitude_igd.pdf`
- `paper/figures/friedman_avg_rank_igd.pdf`
- `paper/figures/heatmap_a12_M2.pdf`
- `paper/figures/heatmap_a12_M3.pdf`
- `paper/figures/pareto_fronts.pdf`
- `paper/figures/dtlz4_bimodal_good_bad.pdf`
- `paper/figures/tuning_heatmap_combined.pdf`
- `paper/figures/engineering_metric_profiles.pdf`
- `paper/figures/engineering_fronts_rwmop9_rwmop8.pdf`
- `results/ablation_v2/phase1/phase1_table.tex`
- `results/ablation_v2/phase2/phase2_interactions.pdf`
- `results/ablation_v2/phase3/phase3_igd_table.tex`
- `results/ablation_v2/phase3/phase3_hv_table.tex`

## Not covered by WS4

- `paper/figures/flowchart.pdf` is still a manual, non-data figure and was not
  regenerated here.
- Single-file LaTeX packaging and layout cleanup remain WS5 tasks.

## Build verification

- `make clean && make` completed after regeneration.
- The paper now builds with the regenerated artifacts in `paper/build/sn-article.pdf`.
- Remaining issues are editorial/layout warnings (for example wide appendix
  tables and large floats), not missing regenerated artifacts.
