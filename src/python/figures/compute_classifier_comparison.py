#!/usr/bin/env python3
"""
Compute classifier comparison data for Figure 2.

Runs RF, Logistic Regression, and RBF-SVC classification on the 14 retained
FLA features under LOOCV and LFO-CV. Extracts balanced accuracy and MCC.
Also includes the early-turnover threshold rule from dynamic_signal_test.csv.

Output: data/processed/classifier_comparison.csv
"""

from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, matthews_corrcoef
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from utils import (
    PROJECT_ROOT,
    DATA_PROCESSED,
    family_of,
    classification_metrics,
    fit_best_threshold,
)

FLA_CSV = PROJECT_ROOT / "data" / "processed" / "fla_dataset.csv"
DYNAMIC_CSV = PROJECT_ROOT / "data" / "processed" / "dynamic_signal_test.csv"
OUT_CSV = DATA_PROCESSED / "classifier_comparison.csv"

RETAINED_FEATURES = [
    "corr_obj_mean", "skewness_mean", "kurtosis_mean", "cv_mean",
    "dom_depth_std", "front_connectivity", "front_diameter", "front_gap_ratio",
    "autocorr_mean", "info_content", "neutrality_ratio", "fdc_mean",
    "n_obj", "n_var",
]

EARLY_FRAC = 0.20
THRESHOLD_FEATURE = "ivf_turnover_early"
LABEL_COL = "label_binary"

RANDOM_STATE = 42


def main() -> None:
    if not FLA_CSV.exists():
        print(f"ERROR: FLA dataset not found: {FLA_CSV}")
        sys.exit(1)

    df = pd.read_csv(FLA_CSV)
    df["family"] = df["instance"].apply(
        lambda x: re.match(r"([A-Za-z]+)", str(x)).group(1)
    )
    print(f"Loaded: {len(df)} instances, {len(df['family'].unique())} families")
    print(f"Labels: {dict(df[LABEL_COL].value_counts())}")

    # Check feature availability
    available = [f for f in RETAINED_FEATURES if f in df.columns]
    missing = set(RETAINED_FEATURES) - set(available)
    if missing:
        print(f"WARNING: Missing features: {missing}")
    print(f"Features available: {len(available)}/{len(RETAINED_FEATURES)}")

    X = df[available].values
    y = (df[LABEL_COL] == "HELPS").astype(int).values
    families = df["family"].values
    n = len(y)

    rows = []

    # --- Static classifiers: LOOCV ---
    classifiers = {
        "RF (static features)": lambda: RandomForestClassifier(
            n_estimators=500, max_depth=6, min_samples_leaf=3,
            max_features="sqrt", class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "LogReg (static features)": lambda: LogisticRegression(
            penalty="l2", solver="liblinear", class_weight="balanced",
            random_state=RANDOM_STATE, max_iter=5000,
        ),
        "RBF-SVC (static features)": lambda: SVC(
            kernel="rbf", class_weight="balanced", random_state=RANDOM_STATE,
        ),
    }

    for clf_name, clf_factory in classifiers.items():
        preds = np.zeros(n, dtype=int)
        for i in range(n):
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[mask])
            X_test = scaler.transform(X[i:i + 1])
            clf = clf_factory()
            clf.fit(X_train, y[mask])
            preds[i] = clf.predict(X_test)[0]

        met = classification_metrics(y.tolist(), preds.tolist())
        rows.append({
            "method": clf_name,
            "validation": "LOOCV",
            "balanced_accuracy": met["balanced_accuracy"],
            "mcc": met["mcc"],
            "sensitivity": met["sensitivity"],
            "specificity": met["specificity"],
        })
        print(f"  {clf_name} LOOCV: BA={met['balanced_accuracy']:.3f}, MCC={met['mcc']:.3f}")

    # --- Static classifiers: LFO-CV ---
    unique_families = sorted(set(families))
    for clf_name, clf_factory in classifiers.items():
        all_preds = np.full(n, -1, dtype=int)
        for fam in unique_families:
            test_mask = families == fam
            train_mask = ~test_mask
            if test_mask.sum() < 1 or train_mask.sum() < 6:
                continue
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[train_mask])
            X_test = scaler.transform(X[test_mask])
            clf = clf_factory()
            try:
                clf.fit(X_train, y[train_mask])
                all_preds[test_mask] = clf.predict(X_test)
            except Exception as exc:
                print(f"  [WARN] {clf_name} family={fam}: {exc}")
                continue

        valid = all_preds >= 0
        if valid.sum() == 0:
            print(f"  {clf_name} LFO-CV: no valid predictions")
            continue
        met = classification_metrics(y[valid].tolist(), all_preds[valid].tolist())
        rows.append({
            "method": clf_name,
            "validation": "LFO-CV",
            "balanced_accuracy": met["balanced_accuracy"],
            "mcc": met["mcc"],
            "sensitivity": met["sensitivity"],
            "specificity": met["specificity"],
        })
        print(f"  {clf_name} LFO-CV: BA={met['balanced_accuracy']:.3f}, MCC={met['mcc']:.3f}")

    # --- Early-turnover threshold rule ---
    if DYNAMIC_CSV.exists():
        dyn = pd.read_csv(DYNAMIC_CSV)
        label_key = "label_binary_eval" if "label_binary_eval" in dyn.columns else "label_binary"
        dyn = dyn.loc[np.isclose(dyn["early_frac"], EARLY_FRAC)].copy()
        dyn = dyn.loc[dyn[label_key].isin(["HELPS", "NOT_HELPS"])].copy()

        if not dyn.empty:
            # LOOCV
            best = fit_best_threshold(dyn, THRESHOLD_FEATURE, label_key)
            if best is not None:
                rows.append({
                    "method": "Early-turnover threshold",
                    "validation": "LOOCV",
                    "balanced_accuracy": best["balanced_accuracy"],
                    "mcc": best["mcc"],
                    "sensitivity": best["sensitivity"],
                    "specificity": best["specificity"],
                })
                print(f"  Early-turnover LOOCV: BA={best['balanced_accuracy']:.3f}, "
                      f"MCC={best['mcc']:.3f}, θ={best['threshold']:.4f}")

            # LFO-CV
            from utils import lofo_threshold_eval as _lofo
            lofo = _lofo(dyn, THRESHOLD_FEATURE, label_key)
            if not np.isnan(lofo.get("balanced_accuracy", np.nan)):
                rows.append({
                    "method": "Early-turnover threshold",
                    "validation": "LFO-CV",
                    "balanced_accuracy": lofo["balanced_accuracy"],
                    "mcc": lofo["mcc"],
                    "sensitivity": lofo["sensitivity"],
                    "specificity": lofo["specificity"],
                })
                print(f"  Early-turnover LFO-CV: BA={lofo['balanced_accuracy']:.3f}, "
                      f"MCC={lofo['mcc']:.3f}")
    else:
        print(f"WARNING: dynamic_signal_test.csv not found at {DYNAMIC_CSV}")

    # --- Save ---
    result_df = pd.DataFrame(rows)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved: {OUT_CSV}")
    print(result_df.to_string(index=False))


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    main()
