#!/usr/bin/env python3
"""
analyze_exploratory.py -- Comprehensive exploratory analysis for PPSN 2026 FLA paper.

Produces publication-quality figures and tables examining the relationship between
landscape features and IVF-SPEA2 performance (delta_igd).

Analyses:
  1. Spearman correlations with BH-FDR correction
  2. Correlation heatmap (14 retained features)
  3. Boxplots by binary label with Mann-Whitney tests
  4. PCA visualization (PC1 vs PC2)
  5. Feature stability summary (CV bar plot)
  6. Delta_IGD distribution histogram
  7. Scatter plots of top features vs delta_igd

Outputs:
  - results/tables/fla_spearman_correlations.csv
  - results/figures/fla_feature_correlation_14.png
  - results/figures/fla_boxplots_by_label.png
  - results/figures/fla_pca_scatter.png
  - results/figures/fla_feature_stability.png
  - results/figures/fla_delta_distribution.png
  - results/figures/fla_scatter_top_features.png
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
DATASET_CSV = Path("data/processed/fla_dataset.csv")
CV_CSV = Path("data/processed/landscape_features_cv.csv")
FIG_DIR = Path("results/figures")
TABLE_DIR = Path("results/tables")

RETAINED_FEATURES = [
    "corr_obj_mean",
    "skewness_mean",
    "kurtosis_mean",
    "cv_mean",
    "dom_depth_std",
    "front_connectivity",
    "front_diameter",
    "front_gap_ratio",
    "autocorr_mean",
    "info_content",
    "neutrality_ratio",
    "fdc_mean",
    "n_obj",
    "n_var",
]

FDR_Q = 0.10
DPI = 300
FONT_LABEL = 12
FONT_TICK = 10

# Use a clean academic style
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.size": FONT_TICK,
    "axes.labelsize": FONT_LABEL,
    "axes.titlesize": FONT_LABEL,
    "xtick.labelsize": FONT_TICK,
    "ytick.labelsize": FONT_TICK,
    "legend.fontsize": FONT_TICK,
    "figure.dpi": DPI,
})


def benjamini_hochberg(p_values, q=0.10):
    """Apply Benjamini-Hochberg FDR correction.

    Parameters
    ----------
    p_values : array-like
        Raw p-values.
    q : float
        False discovery rate threshold.

    Returns
    -------
    p_corrected : np.ndarray
        BH-adjusted p-values.
    significant : np.ndarray
        Boolean array indicating significance after correction.
    """
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    sorted_idx = np.argsort(p)
    sorted_p = p[sorted_idx]

    # BH adjusted p-values (step-up)
    adjusted = np.empty(n)
    adjusted[n - 1] = sorted_p[n - 1]
    for i in range(n - 2, -1, -1):
        adjusted[i] = min(adjusted[i + 1], sorted_p[i] * n / (i + 1))
    adjusted = np.minimum(adjusted, 1.0)

    # Map back to original order
    p_corrected = np.empty(n)
    p_corrected[sorted_idx] = adjusted
    significant = p_corrected < q

    return p_corrected, significant


def analysis_1_spearman(df):
    """Spearman correlations between each feature and delta_igd with BH-FDR."""
    print("=== Analysis 1: Spearman Correlations with BH-FDR Correction ===\n")

    results = []
    for feat in RETAINED_FEATURES:
        rho, p_raw = spearmanr(df[feat], df["delta_igd"])
        results.append({"feature": feat, "rho": rho, "p_raw": p_raw})

    results_df = pd.DataFrame(results)
    p_corrected, significant = benjamini_hochberg(
        results_df["p_raw"].values, q=FDR_Q
    )
    results_df["p_corrected"] = p_corrected
    results_df["significant"] = significant
    results_df = results_df.sort_values("p_corrected").reset_index(drop=True)

    out_path = TABLE_DIR / "fla_spearman_correlations.csv"
    results_df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}")

    n_sig = results_df["significant"].sum()
    print(f"  Features tested: {len(RETAINED_FEATURES)}")
    print(f"  Significant after BH-FDR (q={FDR_Q}): {n_sig}")
    print()
    print(f"  {'Feature':<25s} {'rho':>8s} {'p_raw':>12s} {'p_corr':>12s} {'sig':>5s}")
    print(f"  {'-'*25} {'-'*8} {'-'*12} {'-'*12} {'-'*5}")
    for _, row in results_df.iterrows():
        sig_str = "  *" if row["significant"] else ""
        print(
            f"  {row['feature']:<25s} {row['rho']:>8.4f} "
            f"{row['p_raw']:>12.6f} {row['p_corrected']:>12.6f}{sig_str}"
        )
    print()

    return results_df


def analysis_2_heatmap(df):
    """Spearman correlation heatmap of the 14 retained features."""
    print("=== Analysis 2: Feature Correlation Heatmap (14 features) ===\n")

    X = df[RETAINED_FEATURES]
    corr_matrix, _ = spearmanr(X.values)
    corr_df = pd.DataFrame(corr_matrix, index=RETAINED_FEATURES, columns=RETAINED_FEATURES)

    fig, ax = plt.subplots(figsize=(11, 9))
    mask = np.triu(np.ones_like(corr_df, dtype=bool), k=1)
    sns.heatmap(
        corr_df,
        mask=mask,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.7, "label": "Spearman r"},
        ax=ax,
        annot_kws={"size": 8},
    )
    ax.set_title("Spearman Correlation Matrix -- 14 Retained Features", fontsize=13, pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    out_path = FIG_DIR / "fla_feature_correlation_14.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}\n")


def analysis_3_boxplots(df, spearman_df):
    """Boxplots of top 8 features by binary label with Mann-Whitney U test."""
    print("=== Analysis 3: Boxplots by Binary Label ===\n")

    # Top 8 by absolute rho
    top8 = spearman_df.reindex(
        spearman_df["rho"].abs().sort_values(ascending=False).index
    ).head(8)["feature"].tolist()

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    for i, feat in enumerate(top8):
        ax = axes[i]
        helps = df.loc[df["label_binary"] == "HELPS", feat]
        not_helps = df.loc[df["label_binary"] != "HELPS", feat]

        sns.boxplot(
            data=df,
            x="label_binary",
            y=feat,
            ax=ax,
            palette={"HELPS": "#4C72B0", "NOT_HELPS": "#DD8452"},
            order=["HELPS", "NOT_HELPS"],
            width=0.5,
        )
        # Mann-Whitney U test
        stat, p_val = mannwhitneyu(helps, not_helps, alternative="two-sided")
        if p_val < 0.001:
            p_str = f"p = {p_val:.2e}"
        else:
            p_str = f"p = {p_val:.4f}"
        ax.set_title(f"{feat}\nMann-Whitney {p_str}", fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel(feat, fontsize=10)

    plt.suptitle("Feature Distributions by Label (HELPS vs NOT_HELPS)", fontsize=13, y=1.01)
    plt.tight_layout()

    out_path = FIG_DIR / "fla_boxplots_by_label.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}\n")


def analysis_4_pca(df):
    """PCA on 14 standardized features, scatter PC1 vs PC2."""
    print("=== Analysis 4: PCA Visualization ===\n")

    X = df[RETAINED_FEATURES].values
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    pc = pca.fit_transform(X_std)

    ev1, ev2 = pca.explained_variance_ratio_
    print(f"  PC1 explained variance: {ev1:.4f} ({ev1*100:.1f}%)")
    print(f"  PC2 explained variance: {ev2:.4f} ({ev2*100:.1f}%)")
    print(f"  Cumulative: {(ev1+ev2)*100:.1f}%\n")

    fig, ax = plt.subplots(figsize=(8, 6))

    # Map label_binary to color, 3-class label to marker
    color_map = {"HELPS": "#4C72B0", "NOT_HELPS": "#DD8452"}
    marker_map = {"HELPS": "o", "NEUTRAL": "s", "HURTS": "X"}

    for label3 in ["HELPS", "NEUTRAL", "HURTS"]:
        subset = df[df["label"] == label3]
        idx = subset.index
        binary = subset["label_binary"].values
        for lb in ["HELPS", "NOT_HELPS"]:
            mask = binary == lb
            if mask.sum() == 0:
                continue
            sub_idx = idx[mask]
            ax.scatter(
                pc[sub_idx, 0],
                pc[sub_idx, 1],
                c=color_map[lb],
                marker=marker_map[label3],
                s=60,
                edgecolors="k",
                linewidths=0.5,
                label=f"{label3} ({lb})",
                alpha=0.8,
            )

    ax.set_xlabel(f"PC1 ({ev1*100:.1f}% variance)", fontsize=FONT_LABEL)
    ax.set_ylabel(f"PC2 ({ev2*100:.1f}% variance)", fontsize=FONT_LABEL)
    ax.set_title("PCA of 14 Landscape Features", fontsize=13)
    ax.legend(fontsize=9, loc="best", framealpha=0.9)
    plt.tight_layout()

    out_path = FIG_DIR / "fla_pca_scatter.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}\n")


def analysis_5_stability(df_cv):
    """Bar plot of mean CV per retained feature, color-coded by stability."""
    print("=== Analysis 5: Feature Stability Summary ===\n")

    # CV file has one row per instance; compute mean CV across instances
    cv_means = {}
    for feat in RETAINED_FEATURES:
        if feat in df_cv.columns:
            cv_means[feat] = df_cv[feat].mean()
        else:
            print(f"  Warning: {feat} not found in CV file, skipping.")

    cv_df = pd.DataFrame(
        {"feature": list(cv_means.keys()), "mean_cv": list(cv_means.values())}
    ).sort_values("mean_cv", ascending=True).reset_index(drop=True)

    # Color by stability tier
    def stability_color(cv):
        if cv < 0.1:
            return "#2ca02c"  # green
        elif cv < 0.2:
            return "#f0c929"  # yellow
        else:
            return "#d62728"  # red

    colors = cv_df["mean_cv"].apply(stability_color).tolist()

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(cv_df["feature"], cv_df["mean_cv"], color=colors, edgecolor="k", linewidth=0.5)

    # Threshold lines
    ax.axvline(x=0.1, color="gray", linestyle="--", linewidth=0.8, label="CV = 0.1")
    ax.axvline(x=0.2, color="gray", linestyle=":", linewidth=0.8, label="CV = 0.2")

    ax.set_xlabel("Mean Coefficient of Variation (CV)", fontsize=FONT_LABEL)
    ax.set_title("Feature Stability (mean CV across instances)", fontsize=13)
    ax.legend(fontsize=9)
    plt.tight_layout()

    out_path = FIG_DIR / "fla_feature_stability.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")

    print("\n  Stability summary:")
    for _, row in cv_df.iterrows():
        tier = "STABLE" if row["mean_cv"] < 0.1 else ("MODERATE" if row["mean_cv"] < 0.2 else "UNSTABLE")
        print(f"    {row['feature']:<25s}  CV={row['mean_cv']:.4f}  [{tier}]")
    print()


def analysis_6_delta_distribution(df):
    """Histogram of delta_igd colored by binary label."""
    print("=== Analysis 6: Delta_IGD Distribution ===\n")

    fig, ax = plt.subplots(figsize=(8, 5))

    helps = df.loc[df["label_binary"] == "HELPS", "delta_igd"]
    not_helps = df.loc[df["label_binary"] != "HELPS", "delta_igd"]

    bins = np.linspace(df["delta_igd"].min(), df["delta_igd"].max(), 25)
    ax.hist(helps, bins=bins, alpha=0.7, color="#4C72B0", label="HELPS", edgecolor="k", linewidth=0.5)
    ax.hist(not_helps, bins=bins, alpha=0.7, color="#DD8452", label="NOT_HELPS", edgecolor="k", linewidth=0.5)

    ax.axvline(x=0, color="k", linestyle="--", linewidth=1.2, label="No effect (delta=0)")

    ax.set_xlabel("delta_igd (SPEA2 - IVF-SPEA2)", fontsize=FONT_LABEL)
    ax.set_ylabel("Count", fontsize=FONT_LABEL)
    ax.set_title("Distribution of delta_igd by Label", fontsize=13)
    ax.legend(fontsize=10)
    plt.tight_layout()

    out_path = FIG_DIR / "fla_delta_distribution.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    print(f"  Saved: {out_path}")
    print(f"  HELPS:     n={len(helps)}, median={helps.median():.6f}, mean={helps.mean():.6f}")
    print(f"  NOT_HELPS: n={len(not_helps)}, median={not_helps.median():.6f}, mean={not_helps.mean():.6f}")
    print(f"  Overall:   min={df['delta_igd'].min():.6f}, max={df['delta_igd'].max():.6f}\n")


def analysis_7_scatter_top(df, spearman_df):
    """Scatter plots of top 4 features vs delta_igd."""
    print("=== Analysis 7: Scatter Plots of Top Features vs Delta_IGD ===\n")

    top4 = spearman_df.reindex(
        spearman_df["rho"].abs().sort_values(ascending=False).index
    ).head(4)["feature"].tolist()

    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    axes = axes.flatten()

    color_map = {"HELPS": "#4C72B0", "NOT_HELPS": "#DD8452"}

    for i, feat in enumerate(top4):
        ax = axes[i]
        for lb in ["HELPS", "NOT_HELPS"]:
            subset = df[df["label_binary"] == lb]
            ax.scatter(
                subset[feat],
                subset["delta_igd"],
                c=color_map[lb],
                label=lb,
                s=40,
                alpha=0.7,
                edgecolors="k",
                linewidths=0.4,
            )

        rho, p_val = spearmanr(df[feat], df["delta_igd"])
        if p_val < 0.001:
            p_str = f"p = {p_val:.2e}"
        else:
            p_str = f"p = {p_val:.4f}"
        ax.set_xlabel(feat, fontsize=FONT_LABEL)
        ax.set_ylabel("delta_igd", fontsize=FONT_LABEL)
        ax.set_title(f"rho = {rho:.4f}, {p_str}", fontsize=11)
        ax.legend(fontsize=9, loc="best")

    plt.suptitle("Top Features vs delta_igd (Spearman)", fontsize=13, y=1.01)
    plt.tight_layout()

    out_path = FIG_DIR / "fla_scatter_top_features.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}\n")


def main():
    print("=" * 70)
    print("FLA Exploratory Analysis -- PPSN 2026")
    print("=" * 70)
    print()

    # Ensure output directories exist
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(DATASET_CSV)
    print(f"Loaded dataset: {df.shape[0]} instances x {df.shape[1]} columns")
    print(f"  Labels (3-class): {df['label'].value_counts().to_dict()}")
    print(f"  Labels (binary):  {df['label_binary'].value_counts().to_dict()}")
    print(f"  Retained features: {len(RETAINED_FEATURES)}")
    print()

    # Verify all features present
    missing = [f for f in RETAINED_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing features in dataset: {missing}")

    # Analysis 1
    spearman_df = analysis_1_spearman(df)

    # Analysis 2
    analysis_2_heatmap(df)

    # Analysis 3
    analysis_3_boxplots(df, spearman_df)

    # Analysis 4
    analysis_4_pca(df)

    # Analysis 5
    df_cv = pd.read_csv(CV_CSV)
    print(f"Loaded CV data: {df_cv.shape[0]} instances x {df_cv.shape[1]} columns\n")
    analysis_5_stability(df_cv)

    # Analysis 6
    analysis_6_delta_distribution(df)

    # Analysis 7
    analysis_7_scatter_top(df, spearman_df)

    print("=" * 70)
    print("All analyses complete.")
    print(f"  Figures: {FIG_DIR}/")
    print(f"  Tables:  {TABLE_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
