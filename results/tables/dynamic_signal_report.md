# Dynamic Signal Report

- Manifest: /Users/pedrosanches/Public/Desenvolvimento/ivfspea2/config/ppsn_dynamics_cases_full.csv
- Main setting: early_frac=0.20, help_cutoff=0.56, alpha=0.05
- Cases in manifest: 52
- Labeled cases used in confirmatory tests: 51
- Features tested in the main family: 18
- Turnover discriminant: p_raw=0.0558, p_bh=0.2439, a12=0.680
- HV robustness: p_raw=0.0092, p_bh=0.1656, a12=0.745
- IGD robustness: p_raw=0.0390, p_bh=0.2439, a12=0.694
- Unlabeled cases excluded from label-based tests: rwmop9_m2

## LOOCV
- Best early-feature threshold rule: igd_early_delta | balanced_accuracy=0.672, mcc=0.318, accuracy=0.549, n_eval=51

## Sensitivity
- Best combo: early_frac=0.10, help_cutoff=0.54, feature=hv_final_delta, p_bh=0.1656
