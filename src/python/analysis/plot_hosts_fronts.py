#!/usr/bin/env python3
"""
M=2 Pareto-front overlay figures for the IVF hosts paper.

Reads:
    data/processed/fronts/hosts/<PROBLEM>_M2_<ALGO>_median.csv
    data/processed/fronts/hosts/<PROBLEM>_M2_truePF.csv

Writes:
    results/figures/hosts_v2_fig10_fronts.pdf
    paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig10_fronts.pdf

Each panel shows the true PF (black line) and six algorithm fronts (scatter).
IVF variants use filled markers; base variants use open markers.

Usage:
    python src/python/analysis/plot_hosts_fronts.py
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import pandas as pd

from figure_io import save_figure

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
FRONTS_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "fronts", "hosts")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")

for _d in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(_d, exist_ok=True)

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

ALGO_STYLES: dict[str, dict] = {
    "IVFSPEA2":   {"color": "#4c72b0", "marker": "o", "label": "IVF/SPEA2"},
    "SPEA2":      {"color": "#4c72b0", "marker": "x", "label": "SPEA2"},
    "IVFNSGAIII": {"color": "#55a868", "marker": "o", "label": "IVF/NSGA-III"},
    "NSGAIII":    {"color": "#55a868", "marker": "x", "label": "NSGA-III"},
    "IVFNSGAII":  {"color": "#c44e52", "marker": "o", "label": "IVF/NSGA-II"},
    "NSGAII":     {"color": "#c44e52", "marker": "x", "label": "NSGA-II"},
}

# Draw order: base variants first so IVF variants are rendered on top
ALGO_ORDER = ["SPEA2", "IVFSPEA2", "NSGAIII", "IVFNSGAIII", "NSGAII", "IVFNSGAII"]

# IVF variants get filled markers; base variants get open markers
IVF_ALGOS = {"IVFSPEA2", "IVFNSGAII", "IVFNSGAIII"}

CASES = [
    ("DTLZ2", 2, "Gain"),
    ("WFG4",  2, "Neutral"),
    ("MaF1",  2, "Adverse"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_csv(problem: str, m: int, algo: str) -> pd.DataFrame | None:
    """Load a front CSV; return None with a warning if it doesn't exist."""
    path = os.path.join(FRONTS_DIR, f"{problem}_M{m}_{algo}_median.csv")
    if not os.path.isfile(path):
        print(f"  WARNING: missing {path} — skipping {algo}")
        return None
    return pd.read_csv(path)


def load_true_pf(problem: str, m: int) -> pd.DataFrame | None:
    """Load the true PF CSV; return None with a warning if it doesn't exist."""
    path = os.path.join(FRONTS_DIR, f"{problem}_M{m}_truePF.csv")
    if not os.path.isfile(path):
        print(f"  WARNING: missing {path} — true PF will be omitted")
        return None
    return pd.read_csv(path)


def save_fig(fig: plt.Figure, name: str) -> None:
    """Save a figure to both results/figures/ and the paper figures directory."""
    save_figure(fig, name, (FIG_DIR, PAPER_FIG_DIR))


# ---------------------------------------------------------------------------
# Main plotting function
# ---------------------------------------------------------------------------


def plot_fronts_panel() -> None:
    """3-panel Pareto-front overlay figure for the selected M=2 cases."""
    n_cases = len(CASES)
    fig, axes = plt.subplots(1, n_cases, figsize=(5.0 * n_cases, 4.5))
    if n_cases == 1:
        axes = [axes]

    any_data = False  # track whether we plotted anything at all

    for ax, (problem, m, scenario) in zip(axes, CASES):
        ax.set_title(
            f"{problem} (M={m}, {scenario})",
            fontsize=11,
            fontweight="bold",
        )

        # ---- True PF ----
        pf_df = load_true_pf(problem, m)
        if pf_df is not None and not pf_df.empty:
            # Sort by f1 for a connected line
            pf_sorted = pf_df.sort_values("f1")
            ax.plot(
                pf_sorted["f1"],
                pf_sorted["f2"],
                color="black",
                linewidth=1.0,
                zorder=0,
                label="True PF",
            )
            any_data = True

        # ---- Algorithm fronts ----
        for algo in ALGO_ORDER:
            style = ALGO_STYLES[algo]
            df = load_csv(problem, m, algo)
            if df is None or df.empty:
                continue

            is_ivf = algo in IVF_ALGOS
            ax.scatter(
                df["f1"],
                df["f2"],
                color=style["color"],
                marker=style["marker"],
                s=14 if is_ivf else 18,
                alpha=0.75,
                facecolors=style["color"] if is_ivf else "none",
                edgecolors=style["color"],
                linewidths=0.8,
                zorder=2 if is_ivf else 1,
            )
            any_data = True

        ax.set_xlabel("$f_1$", fontsize=10)
        ax.set_ylabel("$f_2$" if ax is axes[0] else "", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(linestyle=":", alpha=0.35)

    if not any_data:
        print(
            "\nWARNING: No CSV files were found. "
            "Run experiments/extract_hosts_fronts.m first to generate the data."
        )

    # ---- Shared legend ----
    legend_handles: list[mlines.Line2D] = []

    # True PF entry
    legend_handles.append(
        mlines.Line2D([], [], color="black", linewidth=1.5, label="True PF")
    )

    # Algorithm entries (grouped by host colour)
    for algo in ALGO_ORDER:
        style = ALGO_STYLES[algo]
        is_ivf = algo in IVF_ALGOS
        h = mlines.Line2D(
            [],
            [],
            marker=style["marker"],
            color=style["color"],
            markerfacecolor=style["color"] if is_ivf else "none",
            markeredgecolor=style["color"],
            markeredgewidth=0.9,
            markersize=6,
            linestyle="none",
            label=style["label"],
        )
        legend_handles.append(h)

    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=4,
        fontsize=9,
        framealpha=0.9,
        bbox_to_anchor=(0.5, -0.05),
        columnspacing=1.2,
        handletextpad=0.4,
    )

    fig.suptitle(
        "Pareto-front overlays: M=2 representative instances",
        fontsize=12,
        y=1.01,
    )
    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig10_fronts.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("=== Plotting hosts paper Pareto-front overlays ===\n")
    plot_fronts_panel()
    print("\nDone.")


if __name__ == "__main__":
    main()
