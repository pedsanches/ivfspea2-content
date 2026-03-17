#!/usr/bin/env python3
"""
Generate publication-quality figures for the IVF/SPEA2 paper.

Figures produced:
  Fig 2: IGD boxplots — IVF/SPEA2 vs SPEA2 per instance, faceted by suite (M2 + M3)
  Fig 3: A12 effect-size heatmap — IVF/SPEA2 vs all baselines
  Fig 4: Pareto front examples (requires CSV from MATLAB extraction first)

Usage:
  python src/python/analysis/generate_paper_figures.py
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from scipy.stats import mannwhitneyu

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort

# ---------- paths ----------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA = os.path.join(ROOT, "data/processed/todas_metricas_consolidado_with_modern.csv")
FRONTS_DIR = os.path.join(ROOT, "data/processed/fronts")
OUT_DIR = os.path.join(ROOT, "paper/figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- style ----------
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 8,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    }
)

IVF_COLOR = "#2166AC"  # blue
SPEA2_COLOR = "#B2182B"  # red
PALETTE_ALL = {
    "IVFSPEA2": "#2166AC",
    "SPEA2": "#B2182B",
    "MFOSPEA2": "#D6604D",
    "SPEA2SDE": "#F4A582",
    "NSGAII": "#4DAF4A",
    "NSGAIII": "#984EA3",
    "MOEAD": "#FF7F00",
    "AGEMOEAII": "#A65628",
    "ARMOEA": "#999999",
}

# Display names for algorithms
ALGO_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-MOEA-II",
    "ARMOEA": "AR-MOEA",
}

# Suite ordering for paper
SUITE_ORDER = ["ZDT", "DTLZ", "WFG", "MaF"]

# Canonical problem ordering within each suite
PROBLEM_ORDER_M2 = {
    "ZDT": ["ZDT1", "ZDT2", "ZDT3", "ZDT4", "ZDT6"],
    "DTLZ": ["DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4", "DTLZ5", "DTLZ6", "DTLZ7"],
    "WFG": ["WFG1", "WFG2", "WFG3", "WFG4", "WFG5", "WFG6", "WFG7", "WFG8", "WFG9"],
    "MaF": ["MaF1", "MaF2", "MaF3", "MaF4", "MaF5", "MaF6", "MaF7"],
}
PROBLEM_ORDER_M3 = {
    "DTLZ": ["DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4", "DTLZ5", "DTLZ6", "DTLZ7"],
    "WFG": ["WFG1", "WFG2", "WFG3", "WFG4", "WFG5", "WFG6", "WFG7", "WFG8", "WFG9"],
    "MaF": ["MaF1", "MaF2", "MaF3", "MaF4", "MaF5", "MaF6", "MaF7"],
}


def load_data():
    raw_df = pd.read_csv(DATA)
    df_synth = filter_submission_synthetic_cohort(raw_df)
    return df_synth


def vargha_delaney_a12(x, y):
    """Compute Vargha-Delaney A12 effect size. A12 > 0.5 means x tends to be smaller (better for IGD)."""
    nx, ny = len(x), len(y)
    r = 0
    for xi in x:
        r += np.sum(xi < y) + 0.5 * np.sum(xi == y)
    return r / (nx * ny)


# =====================================================================
# FIG 2: IGD BOXPLOTS — IVF/SPEA2 vs SPEA2 per instance, by suite
# =====================================================================
def make_boxplots(df, m_value, problem_order, outfile):
    """Generate faceted boxplots: one row per suite, one column per instance."""
    algos = ["IVFSPEA2", "SPEA2"]
    df_pair = df[(df["M"] == m_value) & (df["Algoritmo"].isin(algos))].copy()

    suites = [s for s in SUITE_ORDER if s in problem_order]
    max_problems = max(len(problem_order[s]) for s in suites)

    fig, axes = plt.subplots(
        nrows=len(suites),
        ncols=max_problems,
        figsize=(max_problems * 1.1, len(suites) * 1.6),
        squeeze=False,
    )

    for row, suite in enumerate(suites):
        problems = problem_order[suite]
        for col in range(max_problems):
            ax = axes[row, col]
            if col >= len(problems):
                ax.axis("off")
                continue

            prob = problems[col]
            data_ivf = df_pair[
                (df_pair["Problema"] == prob) & (df_pair["Algoritmo"] == "IVFSPEA2")
            ]["IGD"].dropna()
            data_sp = df_pair[
                (df_pair["Problema"] == prob) & (df_pair["Algoritmo"] == "SPEA2")
            ]["IGD"].dropna()

            if data_ivf.empty and data_sp.empty:
                ax.axis("off")
                continue

            bp = ax.boxplot(
                [data_ivf, data_sp],
                positions=[0, 1],
                widths=0.6,
                patch_artist=True,
                showfliers=True,
                flierprops=dict(marker=".", markersize=2, alpha=0.4),
                medianprops=dict(color="black", linewidth=1),
                whiskerprops=dict(linewidth=0.7),
                capprops=dict(linewidth=0.7),
                boxprops=dict(linewidth=0.7),
            )
            bp["boxes"][0].set_facecolor(IVF_COLOR)
            bp["boxes"][0].set_alpha(0.7)
            bp["boxes"][1].set_facecolor(SPEA2_COLOR)
            bp["boxes"][1].set_alpha(0.7)

            # Significance marker
            if len(data_ivf) >= 5 and len(data_sp) >= 5:
                _, pval = mannwhitneyu(data_ivf, data_sp, alternative="two-sided")
                a12 = vargha_delaney_a12(data_ivf.values, data_sp.values)
                if pval < 0.05:
                    marker = r"$\mathbf{+}$" if a12 > 0.5 else r"$\mathbf{-}$"
                    ax.text(
                        0.5,
                        0.97,
                        marker,
                        transform=ax.transAxes,
                        ha="center",
                        va="top",
                        fontsize=7,
                        color="green" if a12 > 0.5 else "red",
                    )

            ax.set_title(prob, fontsize=7, pad=2)
            ax.set_xticks([])
            if col == 0:
                ax.set_ylabel(suite, fontsize=8, fontweight="bold")
            else:
                ax.set_ylabel("")
            ax.tick_params(axis="y", labelsize=6)

    # Legend
    legend_elements = [
        Patch(
            facecolor=IVF_COLOR,
            alpha=0.7,
            edgecolor="black",
            linewidth=0.5,
            label="IVF/SPEA2",
        ),
        Patch(
            facecolor=SPEA2_COLOR,
            alpha=0.7,
            edgecolor="black",
            linewidth=0.5,
            label="SPEA2",
        ),
    ]
    fig.legend(
        handles=legend_elements,
        loc="lower center",
        ncol=2,
        fontsize=7,
        frameon=True,
        bbox_to_anchor=(0.5, -0.02),
    )

    fig.suptitle(
        f"IGD distribution per instance ($M={m_value[-1]}$)", fontsize=10, y=1.01
    )
    plt.tight_layout(h_pad=0.8, w_pad=0.3)
    fig.savefig(outfile)
    print(f"  Saved: {outfile}")
    plt.close(fig)


# =====================================================================
# FIG 3: A12 EFFECT-SIZE HEATMAP — IVF/SPEA2 vs ALL baselines
# =====================================================================
def make_a12_heatmap(df, outfile):
    """Heatmap of A12 effect sizes: IVF/SPEA2 vs each baseline, per instance."""
    baselines = [
        "SPEA2",
        "MFOSPEA2",
        "SPEA2SDE",
        "NSGAII",
        "NSGAIII",
        "MOEAD",
        "AGEMOEAII",
        "ARMOEA",
    ]

    for m_value in ["M2", "M3"]:
        df_m = df[df["M"] == m_value]
        problems = sorted(
            df_m["Problema"].unique(),
            key=lambda p: (
                SUITE_ORDER.index(df_m[df_m["Problema"] == p]["Grupo"].iloc[0])
                if df_m[df_m["Problema"] == p]["Grupo"].iloc[0] in SUITE_ORDER
                else 99,
                p,
            ),
        )

        a12_matrix = pd.DataFrame(index=problems, columns=baselines, dtype=float)
        sig_matrix = pd.DataFrame(index=problems, columns=baselines, dtype=bool)

        ivf_data = df_m[df_m["Algoritmo"] == "IVFSPEA2"]
        for prob in problems:
            ivf_vals = ivf_data[ivf_data["Problema"] == prob]["IGD"].dropna().values
            for base in baselines:
                base_vals = (
                    df_m[(df_m["Algoritmo"] == base) & (df_m["Problema"] == prob)][
                        "IGD"
                    ]
                    .dropna()
                    .values
                )
                if len(ivf_vals) >= 5 and len(base_vals) >= 5:
                    a12_matrix.loc[prob, base] = vargha_delaney_a12(ivf_vals, base_vals)
                    _, pval = mannwhitneyu(ivf_vals, base_vals, alternative="two-sided")
                    sig_matrix.loc[prob, base] = pval < 0.05
                else:
                    a12_matrix.loc[prob, base] = np.nan
                    sig_matrix.loc[prob, base] = False

        # Rename columns for display
        col_labels = [ALGO_DISPLAY.get(b, b) for b in baselines]
        a12_matrix.columns = col_labels
        sig_matrix.columns = col_labels

        fig, ax = plt.subplots(figsize=(5.5, 0.28 * len(problems) + 1.0))
        data = a12_matrix.astype(float).values

        im = ax.imshow(data, cmap="RdBu", vmin=0.0, vmax=1.0, aspect="auto")

        # Annotate cells
        for i in range(len(problems)):
            for j in range(len(col_labels)):
                val = data[i, j]
                if np.isnan(val):
                    ax.text(
                        j, i, "—", ha="center", va="center", fontsize=5, color="gray"
                    )
                else:
                    sig = sig_matrix.iloc[i, j]
                    txt = f"{val:.2f}"
                    weight = "bold" if sig else "normal"
                    color = "white" if abs(val - 0.5) > 0.25 else "black"
                    ax.text(
                        j,
                        i,
                        txt,
                        ha="center",
                        va="center",
                        fontsize=5,
                        fontweight=weight,
                        color=color,
                    )

        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(problems)))
        ax.set_yticklabels(problems, fontsize=6)

        # Add suite separators
        suites_in_order = []
        for p in problems:
            g = df_m[df_m["Problema"] == p]["Grupo"].iloc[0]
            if not suites_in_order or suites_in_order[-1] != g:
                suites_in_order.append(g)

        prev_group = None
        for i, prob in enumerate(problems):
            g = df_m[df_m["Problema"] == prob]["Grupo"].iloc[0]
            if prev_group is not None and g != prev_group:
                ax.axhline(y=i - 0.5, color="black", linewidth=1)
            prev_group = g

        cbar = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
        cbar.set_label("$A_{12}$ (IVF/SPEA2 vs baseline)", fontsize=7)
        cbar.ax.tick_params(labelsize=6)

        ax.set_title(
            f"Vargha–Delaney $A_{{12}}$ effect size ($M={m_value[-1]}$)",
            fontsize=9,
            pad=8,
        )

        outpath = outfile.replace(".pdf", f"_{m_value}.pdf")
        fig.savefig(outpath)
        print(f"  Saved: {outpath}")
        plt.close(fig)


# =====================================================================
# FIG 4: PARETO FRONT EXAMPLES (requires MATLAB extraction CSVs)
# =====================================================================
def make_front_plots(outfile):
    """Plot Pareto front examples from extracted CSV data."""
    if not os.path.isdir(FRONTS_DIR):
        print(
            f"  Skipping front plots: {FRONTS_DIR} not found (run MATLAB extraction first)"
        )
        return

    synthetic_algorithms = ["IVFSPEA2", "SPEA2", "NSGAIII", "MOEAD"]

    # --- Panel A: DTLZ2 M2 (success, 2D) ---
    dtlz2_files = {
        algo: os.path.join(FRONTS_DIR, f"DTLZ2_M2_{algo}_median.csv")
        for algo in synthetic_algorithms
    }
    pf_file = os.path.join(FRONTS_DIR, "DTLZ2_M2_truePF.csv")

    # --- Panel B: WFG2 M3 (failure, 3D) ---
    wfg2_files = {
        algo: os.path.join(FRONTS_DIR, f"WFG2_M3_{algo}_median.csv")
        for algo in synthetic_algorithms
    }
    wfg_pf = os.path.join(FRONTS_DIR, "WFG2_M3_truePF.csv")

    # --- Panel C: RWMOP9 M2 (engineering, multi-algo, 2D) ---
    rwmop_files = {
        algo: os.path.join(FRONTS_DIR, f"RWMOP9_M2_{algo}_median.csv")
        for algo in ["IVFSPEA2", "SPEA2", "NSGAIII", "ARMOEA"]
    }

    # Check availability
    panels_available = []
    if os.path.isfile(pf_file) and any(os.path.isfile(f) for f in dtlz2_files.values()):
        panels_available.append("A")
    if os.path.isfile(wfg_pf) and any(os.path.isfile(f) for f in wfg2_files.values()):
        panels_available.append("B")
    if any(os.path.isfile(f) for f in rwmop_files.values()):
        panels_available.append("C")

    if not panels_available:
        print("  No front CSVs found. Skipping.")
        return

    n_panels = len(panels_available)
    has_3d = "B" in panels_available

    if has_3d:
        fig = plt.figure(figsize=(7, 2.8))
        gs = gridspec.GridSpec(
            1, n_panels, width_ratios=[1, 1.3, 1] if n_panels == 3 else [1] * n_panels
        )
    else:
        fig, axes_flat = plt.subplots(1, n_panels, figsize=(3.5 * n_panels, 2.8))
        if n_panels == 1:
            axes_flat = [axes_flat]

    panel_idx = 0

    # --- Panel A: DTLZ2 M2 ---
    if "A" in panels_available:
        if has_3d:
            ax = fig.add_subplot(gs[panel_idx])
        else:
            ax = axes_flat[panel_idx]
        panel_idx += 1

        pf = pd.read_csv(pf_file)
        ax.scatter(
            pf["f1"], pf["f2"], s=1, c="lightgray", alpha=0.5, label="True PF", zorder=1
        )
        for algo in synthetic_algorithms:
            fpath = dtlz2_files[algo]
            if not os.path.isfile(fpath):
                continue
            data = pd.read_csv(fpath)
            color = PALETTE_ALL.get(algo, "gray")
            label = ALGO_DISPLAY.get(algo, algo)
            s = 9 if algo == "IVFSPEA2" else 7
            z = 3 if algo == "IVFSPEA2" else 2
            ax.scatter(
                data["f1"],
                data["f2"],
                s=s,
                c=color,
                alpha=0.75,
                label=label,
                zorder=z,
                edgecolors="none",
            )
        ax.set_xlabel("$f_1$")
        ax.set_ylabel("$f_2$")
        ax.set_title("(a) DTLZ2 ($M\\!=\\!2$) — success", fontsize=8)
        ax.legend(fontsize=5, loc="upper right", markerscale=1.4, handletextpad=0.3)

    # --- Panel B: WFG2 M3 (3D) ---
    if "B" in panels_available:
        if has_3d:
            ax = fig.add_subplot(gs[panel_idx], projection="3d")
        else:
            ax = axes_flat[panel_idx]
        panel_idx += 1

        pf = pd.read_csv(wfg_pf)
        ax.scatter(
            pf["f1"], pf["f2"], pf["f3"], s=1, c="lightgray", alpha=0.3, label="True PF"
        )
        for algo in synthetic_algorithms:
            fpath = wfg2_files[algo]
            if not os.path.isfile(fpath):
                continue
            data = pd.read_csv(fpath)
            color = PALETTE_ALL.get(algo, "gray")
            label = ALGO_DISPLAY.get(algo, algo)
            s = 8 if algo == "IVFSPEA2" else 6
            ax.scatter(
                data["f1"],
                data["f2"],
                data["f3"],
                s=s,
                c=color,
                alpha=0.75,
                label=label,
                edgecolors="none",
            )
        ax.set_xlabel("$f_1$", fontsize=6, labelpad=1)
        ax.set_ylabel("$f_2$", fontsize=6, labelpad=1)
        ax.set_zlabel("$f_3$", fontsize=6, labelpad=1)
        ax.tick_params(labelsize=5)
        ax.set_title("(b) WFG2 ($M\\!=\\!3$) — failure", fontsize=8, pad=1)
        ax.legend(fontsize=4.8, loc="upper left", markerscale=1.3)

    # --- Panel C: RWMOP9 M2 (multi-algo) ---
    if "C" in panels_available:
        if has_3d:
            ax = fig.add_subplot(gs[panel_idx])
        else:
            ax = axes_flat[panel_idx]
        panel_idx += 1

        for algo, fpath in rwmop_files.items():
            if os.path.isfile(fpath):
                d = pd.read_csv(fpath)
                color = PALETTE_ALL.get(algo, "gray")
                label = ALGO_DISPLAY.get(algo, algo)
                s = 12 if algo == "IVFSPEA2" else 6
                z = 3 if algo == "IVFSPEA2" else 1
                ax.scatter(
                    d["f1"],
                    d["f2"],
                    s=s,
                    c=color,
                    alpha=0.8,
                    label=label,
                    edgecolors="none",
                    zorder=z,
                )
        ax.set_xlabel("$f_1$")
        ax.set_ylabel("$f_2$")
        ax.set_title("(c) RWMOP9 ($M\\!=\\!2$) — engineering", fontsize=8)
        ax.legend(fontsize=5, loc="best", markerscale=1.5, handletextpad=0.3)

    plt.tight_layout(w_pad=1.5)
    fig.savefig(outfile)
    print(f"  Saved: {outfile}")
    plt.close(fig)


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    print("Loading data...")
    df = load_data()
    print(
        f"  {len(df)} rows, {df['Algoritmo'].nunique()} algorithms, "
        f"{df['Problema'].nunique()} problems"
    )

    print("\nFig 2a: IGD boxplots (M=2)...")
    make_boxplots(
        df, "M2", PROBLEM_ORDER_M2, os.path.join(OUT_DIR, "boxplot_igd_m2.pdf")
    )

    print("\nFig 2b: IGD boxplots (M=3)...")
    make_boxplots(
        df, "M3", PROBLEM_ORDER_M3, os.path.join(OUT_DIR, "boxplot_igd_m3.pdf")
    )

    print("\nFig 3: A12 effect-size heatmap...")
    make_a12_heatmap(df, os.path.join(OUT_DIR, "heatmap_a12.pdf"))

    print("\nFig 4: Pareto front examples...")
    make_front_plots(os.path.join(OUT_DIR, "pareto_fronts.pdf"))

    print("\nDone.")
