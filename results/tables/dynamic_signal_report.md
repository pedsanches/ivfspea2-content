# Dynamic Signal Report

- Manifest: /home/pedro/desenvolvimento/ivfspea2/config/ppsn_dynamics_cases_full.csv
- Main setting: early_frac=0.20, help_cutoff=0.56, alpha=0.05
- Cases in manifest: 52
- Labeled cases used in confirmatory tests: 51
- Features tested in the main family: 18
- Turnover discriminant: p_raw=0.0007, p_bh=0.0130, a12=0.849
- HV robustness: p_raw=0.0282, p_bh=0.1692, a12=0.727
- IGD robustness: p_raw=0.0733, p_bh=0.2948, a12=0.685
- Unlabeled cases excluded from label-based tests: rwmop9_m2

## LOOCV
- Best early-feature threshold rule: spea2_turnover_early | balanced_accuracy=0.704, mcc=0.334, accuracy=0.706, n_eval=51

## LOFO
- Best out-of-family threshold rule: ivf_turnover_early | balanced_accuracy=0.754, mcc=0.413, accuracy=0.725, n_eval=51, n_families=4

## Sensitivity
- Best combo: early_frac=0.20, help_cutoff=0.54, feature=ivf_turnover_early, p_bh=0.0130
