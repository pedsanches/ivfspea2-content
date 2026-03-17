# Submission Claim Traceability

Date: 2026-03-09
Status: WS2 frozen map

## Canonical evidence rule

- Synthetic confirmatory claims must trace to `Track 3` artifacts filtered by
  `src/python/analysis/cohort_filter.py`.
- Engineering claims must trace to `results/engineering_suite/*_main.csv`.
- Ablation and tuning claims are supportive only and must stay labeled that way.

## Claim map

| Claim | Strength | Canonical artifacts | Notes |
|---|---|---|---|
| IVF/SPEA2 improves canonical SPEA2 on many out-of-sample synthetic instances under fixed FE budgets | Confirmatory | `results/tables/claims_summary_audit.csv`; `results/tables/claims_summary_instance_details.csv`; `src/python/analysis/compute_claims_summary.py`; `src/python/analysis/cohort_filter.py` | Main claim for abstract, Results, and Conclusion |
| HV provides secondary qualitative confirmation of the main synthetic pattern | Confirmatory support | `results/tables/claims_summary_audit.csv`; `results/tables/hv_per_instance_M2.tex`; `results/tables/hv_per_instance_M3.tex` | Secondary indicator only; does not replace IGD as primary endpoint |
| Gains are bounded rather than universal, with losses concentrated on irregular/disconnected fronts | Confirmatory support | `results/tables/claims_summary_instance_details.csv`; `results/tables/igd_m2_detailed_with_modern_table.tex`; `results/tables/igd_m3_detailed_with_modern_table.tex`; `paper/figures/effect_magnitude_igd.pdf` | Supports the current bounded framing |
| Practical benefit must be read together with substantial runtime overhead | Confirmatory support | `results/tables/runtime_overhead_baselines.tex`; `paper/figures/effect_magnitude_igd.pdf` | Supports the cost-benefit discussion in Results and Discussion |
| Multi-baseline positioning is exploratory, not the paper's main confirmatory inference | Exploratory | `results/tables/igd_m2_detailed_with_modern_table.tex`; `results/tables/igd_m3_detailed_with_modern_table.tex`; `paper/figures/friedman_avg_rank_igd.pdf`; `paper/figures/heatmap_a12_M2.pdf`; `paper/figures/heatmap_a12_M3.pdf` | Keep this label explicit in text and captions |
| Engineering results are a transferability check with uneven success across problems | External support | `results/engineering_suite/engineering_suite_pairwise_main.csv`; `results/engineering_suite/engineering_suite_summary_main.csv`; `results/tables/engineering_metric_profiles_summary.csv`; `paper/figures/engineering_metric_profiles.pdf`; `paper/figures/engineering_fronts_rwmop9_rwmop8.pdf` | Must remain separate from synthetic confirmatory claims |
| The promoted default C26 is justified by a tuning pipeline rather than by arbitrary parameter choice | Supportive | `results/tuning_ivfspea2v2/tuning_phase_ranking.csv`; `paper/figures/tuning_heatmap_combined.pdf` | Supports default selection only; not a confirmatory generalization claim |
| Geometry-dependent mechanism and failure-mode interpretation are illustrated by representative front examples and the DTLZ4 bimodal case | Supportive | `paper/figures/pareto_fronts.pdf`; `paper/figures/dtlz4_bimodal_good_bad.pdf`; `results/ablation_v2/phase2/phase2_interactions.pdf` | Illustrative/mechanistic support, not primary quantitative evidence |
| H1/H2 justify the current implementation but are not decisively validated as the paper's strongest novelty claim | Supportive | `results/ablation_v2/phase1/phase1_summary.csv`; `results/ablation_v2/phase2/phase2_pairwise_adjusted.csv`; `results/ablation_v2/phase3/phase3_raw_metrics.csv`; `results/ablation_v2/phase3/phase3_igd_table.tex`; `results/ablation_v2/phase3/phase3_hv_table.tex` | Supports current WS1 framing: supportive, not central |

## Red-line checks

- Any sentence claiming synthetic improvement must be traceable to a row in
  `results/tables/claims_summary_audit.csv` or to a per-instance table derived
  from the same Track 3 cohort.
- Any sentence about runtime must be traceable to
  `results/tables/runtime_overhead_baselines.tex`.
- Any sentence about engineering transfer must be traceable to
  `results/engineering_suite/*_main.csv`.
- Any sentence about H1/H2 must stay within the strength supported by
  `results/ablation_v2/` artifacts.

If a number in the manuscript cannot be located through this map, it should not
remain in the submission version until its provenance is added.
