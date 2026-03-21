#!/usr/bin/env python3
"""
build_dataset.py — Merge landscape features with response variable.

Combines:
  - data/processed/landscape_features.csv  (from MATLAB extraction)
  - data/processed/fla_response.csv        (from compute_response.py)

Output:
  - data/processed/fla_dataset.csv         (unified dataset for modeling)

The merge is performed on the 'instance' column (e.g., 'ZDT1_M2').
"""

import pandas as pd
from pathlib import Path

FEATURES_CSV = Path("data/processed/landscape_features.csv")
RESPONSE_CSV = Path("data/processed/fla_response.csv")
OUTPUT_CSV = Path("data/processed/fla_dataset.csv")


def main():
    print("=== Building FLA Dataset ===")

    features = pd.read_csv(FEATURES_CSV)
    response = pd.read_csv(RESPONSE_CSV)

    print(f"Features: {len(features)} instances x {len(features.columns)-1} features")
    print(f"Response: {len(response)} instances")

    # Merge on instance key
    dataset = pd.merge(features, response, on="instance", how="inner")

    n_matched = len(dataset)
    n_features_only = len(features) - n_matched
    n_response_only = len(response) - n_matched

    if n_features_only > 0:
        missing = set(features["instance"]) - set(response["instance"])
        print(f"  WARNING: {n_features_only} instances in features but not response: {missing}")
    if n_response_only > 0:
        missing = set(response["instance"]) - set(features["instance"])
        print(f"  WARNING: {n_response_only} instances in response but not features: {missing}")

    print(f"Merged dataset: {n_matched} instances")
    print(f"Three-class label distribution:")
    counts = dataset["label"].value_counts()
    for lbl in ["HELPS", "NEUTRAL", "HURTS"]:
        print(f"  {lbl}: {counts.get(lbl, 0)}")

    if "label_binary" in dataset.columns:
        counts_bin = dataset["label_binary"].value_counts()
        print(f"Binary label distribution:")
        for lbl in ["HELPS", "NOT_HELPS"]:
            print(f"  {lbl}: {counts_bin.get(lbl, 0)}")

    if "a12" in dataset.columns:
        print(f"A12 effect size: mean={dataset['a12'].mean():.4f}, "
              f"median={dataset['a12'].median():.4f}")

    # Check for NaN/Inf in features
    feature_cols = [c for c in features.columns if c != "instance"]
    n_nan = dataset[feature_cols].isna().sum().sum()
    n_inf = dataset[feature_cols].apply(lambda s: s.isin([float("inf"), float("-inf")])).sum().sum()
    if n_nan > 0:
        print(f"  WARNING: {n_nan} NaN values in features")
    if n_inf > 0:
        print(f"  WARNING: {n_inf} Inf values in features")

    dataset.to_csv(OUTPUT_CSV, index=False)
    print(f"\nExported to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
