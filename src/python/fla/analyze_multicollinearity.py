#!/usr/bin/env python3
"""
analyze_multicollinearity.py — Multicollinearity analysis for FLA features.

Reads landscape features and performs:
  1. Spearman correlation matrix between all features
  2. Identification of highly correlated pairs (|r| > 0.80)
  3. VIF (Variance Inflation Factor) for each feature
  4. Degenerate feature detection (>90% same value)
  5. Recommended feature set after removing redundant/degenerate features

Outputs:
  - results/tables/fla_correlation_matrix.csv
  - results/figures/fla_correlation_heatmap.png
  - Console report with recommended feature set
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
FEATURES_CSV = Path("data/processed/landscape_features.csv")
CORR_OUTPUT = Path("results/tables/fla_correlation_matrix.csv")
HEATMAP_OUTPUT = Path("results/figures/fla_correlation_heatmap.png")

CORR_THRESHOLD = 0.80   # |r| above this flags a pair as highly correlated
VIF_THRESHOLD = 10.0     # VIF above this indicates severe multicollinearity
DEGEN_THRESHOLD = 0.90   # Fraction of identical values to flag as degenerate


def compute_vif(X):
    """Compute Variance Inflation Factor for each column in X.

    VIF_j = 1 / (1 - R_j^2), where R_j^2 is the R-squared from
    regressing feature j on all other features.

    Uses numpy least-squares to avoid sklearn dependency.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix (n_samples, n_features). Should be finite.

    Returns
    -------
    np.ndarray
        VIF values, one per feature.
    """
    n_features = X.shape[1]
    vif = np.zeros(n_features)

    for j in range(n_features):
        y = X[:, j]
        # Predictors: all other columns plus intercept
        others = np.delete(X, j, axis=1)
        ones = np.ones((others.shape[0], 1))
        design = np.hstack([ones, others])

        # Least squares
        try:
            beta, residuals, rank, sv = np.linalg.lstsq(design, y, rcond=None)
            y_hat = design @ beta
            ss_res = np.sum((y - y_hat) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            if ss_tot < 1e-15:
                # Constant feature => undefined VIF
                vif[j] = np.inf
            else:
                r_squared = 1.0 - ss_res / ss_tot
                r_squared = min(r_squared, 1.0 - 1e-15)  # avoid division by zero
                vif[j] = 1.0 / (1.0 - r_squared)
        except np.linalg.LinAlgError:
            vif[j] = np.inf

    return vif


def find_degenerate_features(df, feature_cols, threshold=DEGEN_THRESHOLD):
    """Identify features where a single value accounts for >threshold of rows."""
    degenerate = []
    for col in feature_cols:
        vals = df[col].dropna()
        if len(vals) == 0:
            degenerate.append((col, 1.0, np.nan))
            continue
        mode_frac = vals.value_counts(normalize=True).iloc[0]
        if mode_frac > threshold:
            mode_val = vals.value_counts().index[0]
            degenerate.append((col, mode_frac, mode_val))
    return degenerate


def main():
    print("=== FLA Multicollinearity Analysis ===\n")

    df = pd.read_csv(FEATURES_CSV)
    feature_cols = [c for c in df.columns if c != "instance"]
    print(f"Loaded {len(df)} instances x {len(feature_cols)} features\n")

    X = df[feature_cols].copy()

    # --- Step 1: Degenerate features ---
    print("--- Degenerate Features (>{:.0f}% same value) ---".format(
        DEGEN_THRESHOLD * 100))
    degenerate = find_degenerate_features(df, feature_cols)
    degenerate_cols = set()
    if degenerate:
        for col, frac, val in degenerate:
            print(f"  {col}: {frac:.1%} identical (value={val})")
            degenerate_cols.add(col)
    else:
        print("  None found.")
    print()

    # --- Step 2: Replace Inf with NaN, then impute with column median ---
    X = X.replace([np.inf, -np.inf], np.nan)
    for col in feature_cols:
        if X[col].isna().any():
            median_val = X[col].median()
            X[col] = X[col].fillna(median_val)

    # --- Step 3: Spearman correlation matrix ---
    print("--- Spearman Correlation Matrix ---")
    corr_matrix, _ = spearmanr(X.values)
    # spearmanr returns a scalar if only 2 features; ensure matrix
    if X.shape[1] == 1:
        corr_matrix = np.array([[1.0]])
    corr_df = pd.DataFrame(corr_matrix, index=feature_cols, columns=feature_cols)

    # Save correlation matrix
    CORR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    corr_df.to_csv(CORR_OUTPUT)
    print(f"  Saved to {CORR_OUTPUT}")

    # --- Step 4: Identify highly correlated pairs ---
    print(f"\n--- Highly Correlated Pairs (|r| > {CORR_THRESHOLD}) ---")
    high_corr_pairs = []
    n = len(feature_cols)
    for i in range(n):
        for j in range(i + 1, n):
            r = corr_matrix[i, j]
            if abs(r) > CORR_THRESHOLD:
                high_corr_pairs.append((feature_cols[i], feature_cols[j], r))
    high_corr_pairs.sort(key=lambda t: abs(t[2]), reverse=True)

    if high_corr_pairs:
        for f1, f2, r in high_corr_pairs:
            print(f"  {f1}  <->  {f2}  r={r:.4f}")
    else:
        print("  None found.")
    print(f"  Total pairs: {len(high_corr_pairs)}")

    # --- Step 5: VIF ---
    # Exclude degenerate features for VIF computation (constant columns break it)
    vif_cols = [c for c in feature_cols if c not in degenerate_cols]
    X_vif = X[vif_cols].values.astype(float)

    # Standardize for numerical stability
    means = X_vif.mean(axis=0)
    stds = X_vif.std(axis=0)
    stds[stds < 1e-15] = 1.0  # avoid division by zero
    X_vif_std = (X_vif - means) / stds

    print(f"\n--- Variance Inflation Factors (excluding degenerate) ---")
    vif_values = compute_vif(X_vif_std)
    vif_df = pd.DataFrame({"feature": vif_cols, "VIF": vif_values})
    vif_df = vif_df.sort_values("VIF", ascending=False)

    for _, row in vif_df.iterrows():
        flag = " ***" if row["VIF"] > VIF_THRESHOLD else ""
        print(f"  {row['feature']:30s}  VIF={row['VIF']:10.2f}{flag}")

    high_vif = vif_df[vif_df["VIF"] > VIF_THRESHOLD]["feature"].tolist()
    print(f"\n  Features with VIF > {VIF_THRESHOLD}: {len(high_vif)}")

    # --- Step 6: Heatmap ---
    print(f"\n--- Generating Heatmap ---")
    HEATMAP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fig_width = max(10, len(feature_cols) * 0.6)
    fig_height = max(8, len(feature_cols) * 0.5)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    mask = np.triu(np.ones_like(corr_df, dtype=bool), k=1)
    sns.heatmap(
        corr_df,
        mask=mask,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0,
        annot=True if len(feature_cols) <= 25 else False,
        fmt=".2f" if len(feature_cols) <= 25 else "",
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.7, "label": "Spearman r"},
        ax=ax,
    )
    ax.set_title("Spearman Correlation Matrix - FLA Features", fontsize=14, pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    fig.savefig(HEATMAP_OUTPUT, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved to {HEATMAP_OUTPUT}")

    # --- Step 7: Recommended feature set ---
    print(f"\n--- Recommended Feature Set ---")

    # Build set of features to remove
    remove = set(degenerate_cols)

    # For highly correlated pairs, remove the one with higher mean |r| with
    # all other features (greedy approach)
    corr_abs = np.abs(corr_matrix)
    mean_abs_corr = {
        feature_cols[i]: np.mean(corr_abs[i, :]) for i in range(n)
    }

    for f1, f2, r in high_corr_pairs:
        if f1 in remove and f2 in remove:
            continue
        if f1 in remove or f2 in remove:
            continue
        # Remove the feature with higher average absolute correlation
        if mean_abs_corr.get(f1, 0) >= mean_abs_corr.get(f2, 0):
            remove.add(f1)
        else:
            remove.add(f2)

    retained = [c for c in feature_cols if c not in remove]

    print(f"  Original features: {len(feature_cols)}")
    print(f"  Removed (degenerate): {sorted(degenerate_cols)}")
    removed_corr = remove - degenerate_cols
    print(f"  Removed (high correlation): {sorted(removed_corr)}")
    print(f"  Retained features ({len(retained)}):")
    for f in retained:
        print(f"    - {f}")

    print("\n=== Analysis Complete ===")


if __name__ == "__main__":
    main()
