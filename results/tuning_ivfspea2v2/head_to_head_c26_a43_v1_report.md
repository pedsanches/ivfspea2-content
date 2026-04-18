# Head-to-Head Report: head_to_head_c26_a43_v1

Generated at: 2026-02-28 09:03:33

## Scope
- Problems: 12 (ZDT1_M2, ZDT6_M2, DTLZ1_M3, DTLZ2_M3, DTLZ4_M3, DTLZ7_M3, WFG2_M3, WFG4_M2, WFG5_M3, WFG9_M2, MaF1_M3, MaF5_M3)
- Metrics: IGD (lower better), HV (higher better)
- Test: Mann-Whitney U (two-sided) + Holm-Bonferroni correction

## Coverage
- A43: problems=12, runs/problem=30..30
- C26: problems=12, runs/problem=30..30
- IVFSPEA2v1: problems=12, runs/problem=60..60

## IGD Pairwise Summary (+/=/- from first algorithm perspective)
- C26_vs_A43: corrected 0/12/0, raw 5/0/7, mean delta=-0.170%
- C26_vs_IVFSPEA2v1: corrected 4/8/0, raw 8/0/4, mean delta=14.341%
- A43_vs_IVFSPEA2v1: corrected 4/8/0, raw 9/0/3, mean delta=14.502%

## HV Pairwise Summary (+/=/- from first algorithm perspective)
- C26_vs_A43: corrected 1/11/0, raw 7/0/5, mean delta=-0.021%
- C26_vs_IVFSPEA2v1: corrected 4/7/1, raw 7/0/5, mean delta=0.043%
- A43_vs_IVFSPEA2v1: corrected 3/8/1, raw 8/0/4, mean delta=0.065%

## Files
- `/home/pedro/desenvolvimento/ivfspea2/results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_igd.csv`
- `/home/pedro/desenvolvimento/ivfspea2/results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_hv.csv`
- `/home/pedro/desenvolvimento/ivfspea2/results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_summary.json`
- `/home/pedro/desenvolvimento/ivfspea2/results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_report.md`

## Notes
- Interpretation is per-problem, using medians and corrected significance indicators.
- For final tuning promotion, prioritize IGD summary, then inspect HV as secondary support.
