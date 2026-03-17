# Benchmark Five Figures Protocol

This document describes how to generate and interpret the five synthetic-suite figures used to summarize IVF/SPEA2 performance against modern baselines.

## Scope

- Data source: `data/processed/todas_metricas_consolidado_with_modern.csv`
- Cohort filter: `src/python/analysis/cohort_filter.py` (`filter_submission_synthetic_cohort`)
- Suites: `ZDT`, `DTLZ`, `WFG`, `MaF`
- Metrics (mandatory): `IGD` and `HV`

## Run

From repository root:

```bash
make analysis-benchmark-figures
```

Equivalent direct command:

```bash
python src/python/analysis/generate_ivf_benchmark_five_figures.py
```

## Outputs

Figures (`paper/figures/`):

- `fig1_profile_igd_hv.pdf`
- `fig2_boxplot_problem_algorithm_igd.pdf`
- `fig3_pareto_algorithm_panels_available.pdf`
- `fig4_competence_summary_igd_hv.pdf`
- `fig5_effectsize_heatmap_igd_hv.pdf`

Tables (`results/tables/`):

- `fig1_profiles_normalized.csv`
- `fig2_boxplot_data_igd.csv`
- `fig4_competence_summary.csv`
- `fig5_a12_heatmap_values.csv`

## Interpretation Notes

- Fig.1 and Fig.2 are normalized within each problem instance. They show relative standing, not absolute IGD/HV magnitudes.
- Fig.4 combines two distinct questions:
  - Win/tie/loss: IVF/SPEA2 vs SPEA2 only.
  - Average rank: IVF/SPEA2 vs all algorithms.
- Fig.5 uses Vargha-Delaney A12 where 0.5 means no effect, values above 0.5 favor IVF/SPEA2, values below 0.5 favor baseline.

## Known Data Limitation

- Fig.3 currently uses only available synthetic front CSVs under `data/processed/fronts/`.
- At this moment, synthetic front coverage is limited (not all ZDT/MaF instances have front CSVs), so panel availability is partial by design.

## Reproducibility Checklist

- Confirm synthetic cohort filtering is applied before plotting.
- Confirm both IGD and HV are included in generated summaries.
- Confirm output files were regenerated in `paper/figures/` and `results/tables/`.
