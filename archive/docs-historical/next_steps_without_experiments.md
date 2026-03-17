# Next Steps Without New Experiments

This checklist captures high-impact tasks that can be completed using existing artifacts.

## Done in this pass

1. Rebuilt ablation from local files with strict filtering and common-run matching:
   - Script: `scripts/rebuild_ablation_from_local_data.m`
   - Outputs:
     - `results/ablation/ablation_filtered_runs.csv`
     - `results/ablation/ablation_raw_igd.csv`
     - `results/ablation/ablation_summary.csv`
     - `results/ablation/ablation_table.tex`

2. Computed partial IGD-HV robustness check for IVF/SPEA2 vs SPEA2 (M=2) from archived consolidated metrics:
   - Script: `scripts/hv_m2_crosscheck.m`
   - Output: `results/tables/hv_igd_crosscheck_m2_ivf_vs_spea2.csv`
   - Key counts:
     - IGD raw: `16/12/0` (+/=/-)
     - HV raw: `13/13/2`
     - HV Holm: `11/16/1`
     - IGD/HV exact sign agreement: `21/28`

3. Updated manuscript text to reflect:
   - strict ablation protocol and bounded conclusions,
   - partial HV cross-check and coverage limitations,
   - updated discussion/conclusion claims.

4. Integrated recent baselines into the main synthetic benchmark from archived local runs:
   - Script: `scripts/integrate_modern_baselines_main.m`
   - Outputs:
     - `data/processed/todas_metricas_consolidado_with_modern.csv`
     - `results/tables/pairwise_vs_spea2_with_modern.csv`
     - `results/tables/pairwise_ivf_vs_modern.csv`
     - `results/tables/modern_baselines_coverage.csv`

5. Added runtime competitiveness summary against modern baselines from archived synthetic runs:
   - Script: `scripts/build_runtime_modern_summary.m`
   - Output:
     - `results/tables/runtime_modern_summary.csv`
   - Key ratios (IVF perspective):
     - `M=2`: `rho(IVF/AGE)=0.82`, `rho(IVF/AR)=0.80`
     - `M=3`: `rho(IVF/AGE)=1.33`, `rho(IVF/AR)=0.90`

6. Regenerated main synthetic boxplots with the full baseline set (including modern baselines) and aligned figure text:
   - Script: `scripts/regenerate_main_boxplots_with_modern.m`
   - Outputs:
     - `results/figures/boxplot_igd_M2_all_problems_with_modern.pdf`
     - `results/figures/boxplot_igd_M3_all_problems_with_modern.pdf`
     - `paper/figures/results_m2.pdf`
     - `paper/figures/results_m3.pdf`

7. Regenerated detailed per-instance synthetic tables with modern baselines and best-per-problem highlighting:
   - Script: `scripts/build_detailed_tables_with_modern.m`
   - Outputs:
      - `results/tables/igd_m2_detailed_with_modern_table.tex`
      - `results/tables/igd_m3_detailed_with_modern_table.tex`
    - Manuscript integration:
      - `paper/src/sn-article.tex` now inputs the regenerated M2/M3 detailed tables.

8. Published frozen non-experimental artifact manifest (commands + hashes):
   - `results/non_experimental_manifest_20260222.txt`

## Still possible without new experiments

1. Add supplementary material table from `results/tables/hv_igd_crosscheck_m2_ivf_vs_spea2.csv`.
2. Add reproducibility appendix with exact commands and artifact paths.
3. Add a short protocol box listing:
   - significance test,
   - Holm correction setup,
   - run-matching rules used in ablation reconstruction.
4. Add commit SHA pinning to `results/non_experimental_manifest_20260222.txt`.

## Requires new experiments (not in this checklist)

1. Fill missing ablation runs for ZDT1 and MaF1 to restore uniform `n=30`.
2. Compute/store HV for M=3 archives.
3. Extend modern-baseline coverage beyond AGE-MOEA-II and AR-MOEA.
4. Add additional real-world benchmarks.
