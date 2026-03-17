#!/usr/bin/env python3
"""
Generate Vargha-Delaney A12 effect size heatmap: IVF/SPEA2 vs SPEA2.

Reads: data/processed/todas_metricas_consolidado_with_modern.csv
Writes: paper/figures/heatmap_comparacao.pdf
        results/figures/heatmap_a12_ivf_vs_spea2.pdf
"""

import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "figures")
RESULTS_FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")

ALGO_IVF = "IVFSPEA2"
ALGO_BASE = "SPEA2"

# Suite ordering
SUITE_ORDER = {"ZDT": 0, "DTLZ": 1, "WFG": 2, "MaF": 3}


def vargha_delaney_a12(x, y):
    """
    Compute Vargha-Delaney A12 statistic.
    A12 = P(X < Y) + 0.5 * P(X == Y)
    For IGD (lower is better), A12 > 0.5 means x is better than y.
    """
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return np.nan
    r = 0.0
    for xi in x:
        for yj in y:
            if xi < yj:
                r += 1.0
            elif xi == yj:
                r += 0.5
    return r / (nx * ny)


def suite_of(problem_name):
    for prefix in SUITE_ORDER:
        if problem_name.startswith(prefix):
            return prefix
    return "OTHER"


def problem_sort_key(problem_name):
    """Sort key: suite order, then numeric suffix."""
    suite = suite_of(problem_name)
    suite_rank = SUITE_ORDER.get(suite, 99)
    import re

    num = re.search(r"\d+", problem_name)
    num_val = int(num.group()) if num else 0
    return (suite_rank, num_val)


def main():
    df = pd.read_csv(DATA_PATH)
    df = df[~df["Problema"].str.startswith("RWMOP")]

    os.makedirs(PAPER_FIG_DIR, exist_ok=True)
    os.makedirs(RESULTS_FIG_DIR, exist_ok=True)

    for m_val in ["M2", "M3"]:
        dm = df[df["M"] == m_val]
        problems = sorted(dm["Problema"].unique(), key=problem_sort_key)

        a12_vals = []
        labels = []
        suites = []

        for prob in problems:
            ivf = (
                dm[(dm["Algoritmo"] == ALGO_IVF) & (dm["Problema"] == prob)]["IGD"]
                .dropna()
                .values
            )
            base = (
                dm[(dm["Algoritmo"] == ALGO_BASE) & (dm["Problema"] == prob)]["IGD"]
                .dropna()
                .values
            )

            if len(ivf) == 0 or len(base) == 0:
                continue

            a12 = vargha_delaney_a12(ivf, base)
            a12_vals.append(a12)
            labels.append(prob)
            suites.append(suite_of(prob))

        if not a12_vals:
            print(f"No data for {m_val}, skipping.")
            continue

        print(f"\n=== {m_val}: {len(a12_vals)} instances ===")
        for lbl, val in zip(labels, a12_vals):
            magnitude = (
                "large"
                if val > 0.71 or val < 0.29
                else "medium"
                if val > 0.64 or val < 0.36
                else "small"
                if val > 0.56 or val < 0.44
                else "negligible"
            )
            direction = (
                "IVF better" if val > 0.5 else "SPEA2 better" if val < 0.5 else "equal"
            )
            print(f"  {lbl:12s}: A12={val:.4f} ({magnitude}, {direction})")

    # --- Combined figure (M2 top, M3 bottom) like the original ---
    fig, axes = plt.subplots(
        2, 1, figsize=(10, 7), gridspec_kw={"height_ratios": [1.2, 1]}
    )

    for ax_idx, m_val in enumerate(["M2", "M3"]):
        ax = axes[ax_idx]
        dm = df[df["M"] == m_val]
        problems = sorted(dm["Problema"].unique(), key=problem_sort_key)

        a12_vals = []
        labels = []
        suites_list = []

        for prob in problems:
            ivf = (
                dm[(dm["Algoritmo"] == ALGO_IVF) & (dm["Problema"] == prob)]["IGD"]
                .dropna()
                .values
            )
            base = (
                dm[(dm["Algoritmo"] == ALGO_BASE) & (dm["Problema"] == prob)]["IGD"]
                .dropna()
                .values
            )

            if len(ivf) == 0 or len(base) == 0:
                continue

            a12 = vargha_delaney_a12(ivf, base)
            a12_vals.append(a12)
            labels.append(prob)
            suites_list.append(suite_of(prob))

        if not a12_vals:
            ax.set_visible(False)
            continue

        # Create matrix for heatmap (1 row x N columns)
        data_matrix = np.array(a12_vals).reshape(1, -1)

        # Diverging colormap centered at 0.5
        # green = IVF better (A12 > 0.5), red = SPEA2 better (A12 < 0.5)
        cmap = plt.cm.RdYlGn
        norm = mcolors.TwoSlopeNorm(vmin=0.0, vcenter=0.5, vmax=1.0)

        im = ax.imshow(data_matrix, aspect="auto", cmap=cmap, norm=norm)

        # Annotate cells
        for j in range(len(a12_vals)):
            val = a12_vals[j]
            text_color = "white" if val > 0.80 or val < 0.20 else "black"
            ax.text(
                j,
                0,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color=text_color,
                fontweight="bold",
            )

        # Axis labels
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
        ax.set_yticks([0])
        ax.set_yticklabels([f"$M={m_val[1]}$"], fontsize=9)

        # Suite separators
        prev_suite = suites_list[0]
        for j in range(1, len(suites_list)):
            if suites_list[j] != prev_suite:
                ax.axvline(x=j - 0.5, color="black", linewidth=1.2)
                prev_suite = suites_list[j]

        ax.set_title(
            f"Vargha–Delaney $A_{{12}}$ effect size: IVF/SPEA2 vs SPEA2 ({m_val})",
            fontsize=10,
        )

    # Colorbar
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax)
    cbar.set_label("$A_{12}$ (> 0.5 = IVF/SPEA2 better)", fontsize=9)
    cbar.set_ticks([0.0, 0.29, 0.36, 0.44, 0.5, 0.56, 0.64, 0.71, 1.0])
    cbar.set_ticklabels(
        [
            "0.0",
            "0.29\nlarge−",
            "0.36\nmed−",
            "0.44\nsmall−",
            "0.50\nequal",
            "0.56\nsmall+",
            "0.64\nmed+",
            "0.71\nlarge+",
            "1.0",
        ]
    )
    cbar.ax.tick_params(labelsize=6)

    plt.subplots_adjust(left=0.06, right=0.90, top=0.94, bottom=0.12, hspace=0.55)

    out_paper = os.path.join(PAPER_FIG_DIR, "heatmap_comparacao.pdf")
    out_results = os.path.join(RESULTS_FIG_DIR, "heatmap_a12_ivf_vs_spea2.pdf")
    fig.savefig(out_paper, dpi=300, bbox_inches="tight")
    fig.savefig(out_results, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nWrote: {out_paper}")
    print(f"Wrote: {out_results}")


if __name__ == "__main__":
    main()
