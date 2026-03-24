"""
Generate all 4 publication-quality figures for the PPSN 2026 paper.

Figures:
  1. PCA scatter of FLA features (negative result)
  2. IGD convergence trajectories (4 representative cases)
  3. IVF cycle count and archive turnover dynamics
  4. Dynamic discriminant signal (boxplot + scatter)

Usage:
    python src/python/fla/generate_paper_figures.py
"""
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIGURES_DIR = PROJECT_ROOT / "paper" / "ppsn2026" / "figures"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics"

# Styling constants
BLUE = "#1f77b4"
ORANGE = "#ff7f0e"
DPI = 300
FONT_LABEL = 11
FONT_TICK = 9
FONT_LEGEND = 9
FONT_ANNOTATION = 9

# Apply global style
plt.rcParams.update({
    "font.family": "serif",
    "font.size": FONT_TICK,
    "axes.labelsize": FONT_LABEL,
    "axes.titlesize": FONT_LABEL,
    "xtick.labelsize": FONT_TICK,
    "ytick.labelsize": FONT_TICK,
    "legend.fontsize": FONT_LEGEND,
    "figure.dpi": 100,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# ---------------------------------------------------------------------------
# Utility: load .mat trace data
# ---------------------------------------------------------------------------
def load_mat_generations(mat_path):
    """Load trace_generations from a .mat file."""
    from pymatreader import read_mat
    data = read_mat(str(mat_path))
    gens = data.get("trace_generations", [])
    if isinstance(gens, dict):
        gens = [gens]
    return gens


def load_mat_field(mat_path, field):
    """Load a specific field from a .mat file."""
    from pymatreader import read_mat
    data = read_mat(str(mat_path))
    return data.get(field, None)


def extract_trajectory(gens, key):
    """Extract a time series of a given key from generation snapshots."""
    vals = []
    for g in gens:
        if isinstance(g, dict) and key in g:
            v = g[key]
            if isinstance(v, (int, float, np.integer, np.floating)):
                vals.append(float(v))
            else:
                vals.append(np.nan)
        else:
            vals.append(np.nan)
    return np.array(vals)


def load_case_trajectories(case_id, algo="ivf"):
    """Load all run trajectories for a case. Returns list of generation-dicts lists."""
    root = DATA_RAW / algo / case_id
    if not root.exists():
        return []
    prefix = "IVF_" if algo == "ivf" else "SPEA2_"
    files = sorted(root.glob(f"{prefix}*.mat"))
    trajectories = []
    for f in files:
        try:
            gens = load_mat_generations(f)
            if len(gens) > 5:
                trajectories.append(gens)
        except Exception as e:
            print(f"  WARNING: Failed to load {f.name}: {e}")
    return trajectories


def compute_median_iqr(trajectories, key, n_gen_target=None):
    """Compute median and IQR of a metric across runs, aligned to common length."""
    if not trajectories:
        return None, None, None, None

    all_series = []
    for gens in trajectories:
        s = extract_trajectory(gens, key)
        all_series.append(s)

    # Align to shortest or target length
    if n_gen_target is None:
        n_gen_target = min(len(s) for s in all_series)
    aligned = []
    for s in all_series:
        if len(s) >= n_gen_target:
            aligned.append(s[:n_gen_target])

    if not aligned:
        return None, None, None, None

    mat = np.array(aligned)
    median = np.nanmedian(mat, axis=0)
    q25 = np.nanpercentile(mat, 25, axis=0)
    q75 = np.nanpercentile(mat, 75, axis=0)
    x = np.linspace(0, 1, n_gen_target)
    return x, median, q25, q75


def save_figure(fig, name):
    """Save figure as both PDF and PNG."""
    pdf_path = FIGURES_DIR / f"{name}.pdf"
    png_path = FIGURES_DIR / f"{name}.png"
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=DPI, bbox_inches="tight")
    print(f"  Saved: {pdf_path}")
    print(f"  Saved: {png_path}")
    plt.close(fig)


# ===========================================================================
# Figure 1: PCA Scatter (FLA Negative Result)
# ===========================================================================
def figure1_pca_fla():
    print("\n--- Figure 1: PCA Scatter (FLA) ---")
    csv_path = DATA_PROCESSED / "fla_dataset.csv"
    if not csv_path.exists():
        print(f"  ERROR: {csv_path} not found. Skipping.")
        return

    df = pd.read_csv(csv_path)

    features = [
        "corr_obj_mean", "skewness_mean", "kurtosis_mean", "cv_mean",
        "dom_depth_std", "front_connectivity", "front_diameter", "front_gap_ratio",
        "autocorr_mean", "info_content", "neutrality_ratio", "fdc_mean",
        "n_obj", "n_var",
    ]

    # Check all features exist
    missing = [f for f in features if f not in df.columns]
    if missing:
        print(f"  WARNING: Missing features: {missing}")
        features = [f for f in features if f in df.columns]

    if "label_binary" not in df.columns:
        print("  ERROR: label_binary column missing. Skipping.")
        return

    X = df[features].values
    labels = df["label_binary"].values

    # Drop rows with NaN
    valid = ~np.any(np.isnan(X), axis=1)
    X = X[valid]
    labels = labels[valid]

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    ev1 = pca.explained_variance_ratio_[0] * 100
    ev2 = pca.explained_variance_ratio_[1] * 100

    fig, ax = plt.subplots(figsize=(5, 4))

    helps_mask = labels == "HELPS"
    not_helps_mask = labels == "NOT_HELPS"

    ax.scatter(X_pca[not_helps_mask, 0], X_pca[not_helps_mask, 1],
               c=ORANGE, alpha=0.7, s=40, edgecolors="white", linewidths=0.5,
               label="NOT_HELPS", zorder=2)
    ax.scatter(X_pca[helps_mask, 0], X_pca[helps_mask, 1],
               c=BLUE, alpha=0.7, s=40, edgecolors="white", linewidths=0.5,
               label="HELPS", zorder=3)

    ax.set_xlabel(f"PC1 ({ev1:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({ev2:.1f}% variance)")
    ax.legend(frameon=True, framealpha=0.9, edgecolor="gray")
    ax.grid(True, alpha=0.3, linewidth=0.5)

    fig.tight_layout()
    save_figure(fig, "fig1_pca_fla")


# ===========================================================================
# Figure 2: IGD Convergence Trajectories (4 representative cases)
# ===========================================================================
def figure2_trajectories():
    print("\n--- Figure 2: IGD Convergence Trajectories ---")

    cases = [
        ("strong_pos_dtlz3_m2", "DTLZ3 (M=2) -- Strong positive"),
        ("mod_pos_wfg4_m2", "WFG4 (M=2) -- Moderate positive"),
        ("neutral_wfg8_m2", "WFG8 (M=2) -- Neutral"),
        ("hurts_wfg2_m3", "WFG2 (M=3) -- Hurts"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharex=True)
    axes = axes.flatten()

    any_data = False

    for idx, (case_id, label) in enumerate(cases):
        ax = axes[idx]

        try:
            ivf_trajs = load_case_trajectories(case_id, "ivf")
            spea2_trajs = load_case_trajectories(case_id, "spea2")
        except Exception as e:
            print(f"  ERROR loading {case_id}: {e}")
            ax.text(0.5, 0.5, f"{case_id}\n(data not available)",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=FONT_TICK)
            ax.set_title(label, fontsize=FONT_TICK)
            continue

        if not ivf_trajs or not spea2_trajs:
            print(f"  WARNING: No trajectories for {case_id}")
            ax.text(0.5, 0.5, f"{case_id}\n(data not available)",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=FONT_TICK)
            ax.set_title(label, fontsize=FONT_TICK)
            continue

        any_data = True

        # Align to common length
        n_gen = min(
            min(len(t) for t in ivf_trajs),
            min(len(t) for t in spea2_trajs),
        )

        x_ivf, med_ivf, q25_ivf, q75_ivf = compute_median_iqr(ivf_trajs, "igd", n_gen)
        x_spea2, med_spea2, q25_spea2, q75_spea2 = compute_median_iqr(spea2_trajs, "igd", n_gen)

        if x_ivf is not None:
            ax.semilogy(x_ivf, med_ivf, color=BLUE, linewidth=1.5, label="IVF-SPEA2")
            ax.fill_between(x_ivf, q25_ivf, q75_ivf, color=BLUE, alpha=0.15)

        if x_spea2 is not None:
            ax.semilogy(x_spea2, med_spea2, color=ORANGE, linewidth=1.5, label="SPEA2")
            ax.fill_between(x_spea2, q25_spea2, q75_spea2, color=ORANGE, alpha=0.15)

        ax.set_title(label, fontsize=FONT_TICK)
        ax.grid(True, alpha=0.3, linewidth=0.5, which="both")

        if idx == 0:
            ax.legend(frameon=True, framealpha=0.9, edgecolor="gray",
                      fontsize=FONT_LEGEND - 1, loc="upper right")

    # Common axis labels
    for ax in axes[2:]:
        ax.set_xlabel("Fraction of total generations")
    for ax in [axes[0], axes[2]]:
        ax.set_ylabel("IGD (log scale)")

    fig.tight_layout(h_pad=1.5, w_pad=1.5)

    if any_data:
        save_figure(fig, "fig2_trajectories")
    else:
        print("  WARNING: No data available for any case. Skipping figure.")
        plt.close(fig)


# ===========================================================================
# Figure 3: IVF Cycle Count and Turnover Dynamics
# ===========================================================================
def figure3_ivf_dynamics():
    print("\n--- Figure 3: IVF Cycle Count and Turnover Dynamics ---")

    cases = [
        ("strong_pos_dtlz3_m2", "DTLZ3 (M=2)", BLUE),
        ("neutral_wfg8_m2", "WFG8 (M=2)", "gray"),
        ("hurts_wfg2_m3", "WFG2 (M=3)", ORANGE),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5))

    any_data = False

    for case_id, label, color in cases:
        try:
            ivf_trajs = load_case_trajectories(case_id, "ivf")
            spea2_trajs = load_case_trajectories(case_id, "spea2")
        except Exception as e:
            print(f"  ERROR loading {case_id}: {e}")
            continue

        if not ivf_trajs:
            print(f"  WARNING: No IVF trajectories for {case_id}")
            continue

        any_data = True

        # Common gen count
        n_gen_ivf = min(len(t) for t in ivf_trajs)

        # Left: mean IVF cycle count
        x, med_cycles, q25_c, q75_c = compute_median_iqr(ivf_trajs, "n_ivf_cycles", n_gen_ivf)
        if x is not None:
            # Use mean instead of median for smoother curves
            all_cycles = []
            for t in ivf_trajs:
                s = extract_trajectory(t, "n_ivf_cycles")[:n_gen_ivf]
                all_cycles.append(s)
            mean_cycles = np.nanmean(np.array(all_cycles), axis=0)
            ax1.plot(x, mean_cycles, color=color, linewidth=1.5, label=label)

        # Right: mean archive turnover -- IVF (solid) vs SPEA2 (dashed)
        x_ivf_t, med_ivf_t, _, _ = compute_median_iqr(ivf_trajs, "turnover", n_gen_ivf)

        if spea2_trajs:
            n_gen_spea2 = min(len(t) for t in spea2_trajs)
            n_gen_common = min(n_gen_ivf, n_gen_spea2)
        else:
            n_gen_common = n_gen_ivf

        # Recompute with common length for fair comparison
        x_ivf_t, med_ivf_t, _, _ = compute_median_iqr(ivf_trajs, "turnover", n_gen_common)
        if x_ivf_t is not None:
            # Compute mean turnover for smoother curves
            all_turnover = []
            for t in ivf_trajs:
                s = extract_trajectory(t, "turnover")[:n_gen_common]
                all_turnover.append(s)
            mean_turnover_ivf = np.nanmean(np.array(all_turnover), axis=0)
            ax2.plot(x_ivf_t, mean_turnover_ivf, color=color, linewidth=1.5,
                     linestyle="-", label=f"{label} (IVF)")

        if spea2_trajs:
            x_sp_t, med_sp_t, _, _ = compute_median_iqr(spea2_trajs, "turnover", n_gen_common)
            if x_sp_t is not None:
                all_turnover_sp = []
                for t in spea2_trajs:
                    s = extract_trajectory(t, "turnover")[:n_gen_common]
                    all_turnover_sp.append(s)
                mean_turnover_sp = np.nanmean(np.array(all_turnover_sp), axis=0)
                ax2.plot(x_sp_t, mean_turnover_sp, color=color, linewidth=1.5,
                         linestyle="--", alpha=0.7)

    # Left subplot labels
    ax1.set_xlabel("Fraction of total generations")
    ax1.set_ylabel("Mean IVF cycle count")
    ax1.grid(True, alpha=0.3, linewidth=0.5)
    ax1.legend(frameon=True, framealpha=0.9, edgecolor="gray",
               fontsize=FONT_LEGEND - 1, loc="upper right")

    # Right subplot labels
    ax2.set_xlabel("Fraction of total generations")
    ax2.set_ylabel("Mean archive turnover")
    ax2.grid(True, alpha=0.3, linewidth=0.5)

    # Custom legend for right subplot: solid = IVF, dashed = SPEA2
    legend_elements = [
        Line2D([0], [0], color="black", linewidth=1.5, linestyle="-", label="IVF-SPEA2"),
        Line2D([0], [0], color="black", linewidth=1.5, linestyle="--", alpha=0.7, label="SPEA2"),
    ]
    ax2.legend(handles=legend_elements, frameon=True, framealpha=0.9,
               edgecolor="gray", fontsize=FONT_LEGEND - 1, loc="upper right")

    fig.tight_layout(w_pad=2.0)

    if any_data:
        save_figure(fig, "fig3_ivf_dynamics")
    else:
        print("  WARNING: No data available. Skipping figure.")
        plt.close(fig)


# ===========================================================================
# Figure 4: Dynamic Discriminant Signal
# ===========================================================================
def figure4_discriminant():
    print("\n--- Figure 4: Dynamic Discriminant Signal ---")

    csv_path = DATA_PROCESSED / "dynamic_signal_test.csv"
    if not csv_path.exists():
        print(f"  ERROR: {csv_path} not found. Skipping.")
        return

    df = pd.read_csv(csv_path)

    if "ivf_turnover_early" not in df.columns or "label_binary" not in df.columns:
        print("  ERROR: Required columns missing. Skipping.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5))

    # ---- Left: Boxplot of early turnover by label_binary ----
    helps = df.loc[df.label_binary == "HELPS", "ivf_turnover_early"].dropna()
    not_helps = df.loc[df.label_binary == "NOT_HELPS", "ivf_turnover_early"].dropna()

    bp_data = [helps.values, not_helps.values]
    bp = ax1.boxplot(bp_data, labels=["HELPS", "NOT_HELPS"], widths=0.5,
                     patch_artist=True, medianprops=dict(color="black", linewidth=1.5))
    bp["boxes"][0].set_facecolor(BLUE)
    bp["boxes"][0].set_alpha(0.6)
    bp["boxes"][1].set_facecolor(ORANGE)
    bp["boxes"][1].set_alpha(0.6)

    # Mann-Whitney test
    if len(helps) >= 3 and len(not_helps) >= 3:
        stat, p = stats.mannwhitneyu(helps, not_helps, alternative="two-sided")
        p_str = f"p = {p:.3f}" if p >= 0.001 else f"p = {p:.1e}"
        y_max = max(helps.max(), not_helps.max())
        y_range = y_max - min(helps.min(), not_helps.min())
        ax1.annotate(f"Mann-Whitney\n{p_str}",
                     xy=(1.5, y_max + 0.02 * y_range),
                     ha="center", va="bottom", fontsize=FONT_ANNOTATION,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
                               edgecolor="gray", alpha=0.9))

    ax1.set_ylabel("Early turnover (first 20% gens)")
    ax1.grid(True, alpha=0.3, linewidth=0.5, axis="y")

    # ---- Right: Scatter of early turnover vs final IGD delta ----
    if "igd_final_delta" not in df.columns:
        print("  WARNING: igd_final_delta not found. Right subplot will be empty.")
    else:
        valid = df[["ivf_turnover_early", "igd_final_delta", "label_binary"]].dropna()

        helps_mask = valid.label_binary == "HELPS"
        not_helps_mask = valid.label_binary == "NOT_HELPS"

        ax2.scatter(valid.loc[not_helps_mask, "ivf_turnover_early"],
                    valid.loc[not_helps_mask, "igd_final_delta"],
                    c=ORANGE, alpha=0.7, s=50, edgecolors="white", linewidths=0.5,
                    label="NOT_HELPS", zorder=2)
        ax2.scatter(valid.loc[helps_mask, "ivf_turnover_early"],
                    valid.loc[helps_mask, "igd_final_delta"],
                    c=BLUE, alpha=0.7, s=50, edgecolors="white", linewidths=0.5,
                    label="HELPS", zorder=3)

        # Spearman correlation
        rho, p_rho = stats.spearmanr(valid["ivf_turnover_early"],
                                      valid["igd_final_delta"])
        rho_str = f"Spearman rho = {rho:.3f}"
        p_rho_str = f"p = {p_rho:.3f}" if p_rho >= 0.001 else f"p = {p_rho:.1e}"
        ax2.annotate(f"{rho_str}\n{p_rho_str}",
                     xy=(0.05, 0.95), xycoords="axes fraction",
                     ha="left", va="top", fontsize=FONT_ANNOTATION,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
                               edgecolor="gray", alpha=0.9))

        ax2.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
        ax2.set_xlabel("Early turnover (first 20% gens)")
        ax2.set_ylabel("Final IGD delta (SPEA2 - IVF)")
        ax2.legend(frameon=True, framealpha=0.9, edgecolor="gray",
                   fontsize=FONT_LEGEND - 1, loc="lower right")
        ax2.grid(True, alpha=0.3, linewidth=0.5)

    fig.tight_layout(w_pad=2.0)
    save_figure(fig, "fig4_discriminant")


# ===========================================================================
# Main
# ===========================================================================
def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {FIGURES_DIR}")

    figure1_pca_fla()
    figure2_trajectories()
    figure3_ivf_dynamics()
    figure4_discriminant()

    print("\nDone. All figures saved to:", FIGURES_DIR)


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    main()
