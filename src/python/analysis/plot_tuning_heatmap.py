#!/usr/bin/env python3
"""
Generate tuning-pipeline figure for Fig. 7 of the manuscript.

Three panels showing the actual experimental data from the
three-phase tuning pipeline that led to the promoted
configuration C26 (r=0.225, c=0.12, EAR-P light):

  (a) Phase A (broad search): 4×4 heatmap of (r, c) under pure AR
      with Cycles=2 (the winning cycle count), aggregated across
      12 FULL12 problems via MeanCombinedRank.

  (b) Phase B (operator comparison): horizontal bar chart of the
      5 operator profiles evaluated at the Phase A center
      (r=0.20, c=0.16, Cycles=2).

  (c) Phase C (local refinement): 3×3 heatmap of (r, c) under the
      EAR-P light operator profile, same aggregation.

Lower rank (darker) = better.  Stars mark the phase winners:
A43 in panel (a), C26 in panel (c).  The winning bar in panel (b)
is highlighted.

Input:  results/tuning_ivfspea2v2/tuning_phase_ranking.csv
Output: paper/figures/tuning_heatmap_combined.pdf
        results/tuning_ivfspea2v2/tuning_heatmap_combined.pdf  (copy)
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
RANKING_CSV = os.path.join(
    PROJECT_ROOT, "results", "tuning_ivfspea2v2", "tuning_phase_ranking.csv"
)
OUT_PAPER = os.path.join(
    PROJECT_ROOT, "paper", "figures", "tuning_heatmap_combined.pdf"
)
OUT_RESULTS = os.path.join(
    PROJECT_ROOT, "results", "tuning_ivfspea2v2", "tuning_heatmap_combined.pdf"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_pivot(
    df: pd.DataFrame,
    r_vals: list[float],
    c_vals: list[float],
    value_col: str = "MeanCombinedRank",
) -> np.ndarray:
    """Pivot (R, C) -> value into a 2-D array aligned to r_vals × c_vals."""
    pivot = df.pivot(index="R", columns="C", values=value_col)
    pivot = pivot.reindex(index=r_vals, columns=c_vals)
    return pivot.values


def plot_heatmap_panel(
    ax,
    data: np.ndarray,
    r_vals: list[float],
    c_vals: list[float],
    star_r: float,
    star_c: float,
    star_label: str,
    panel_label: str,
    norm: Normalize,
    cmap,
):
    """Draw a single heatmap panel with cell annotations and a star marker."""
    im = ax.imshow(data, cmap=cmap, aspect="auto", origin="lower", norm=norm)

    # Cell value annotations
    for i in range(len(r_vals)):
        for j in range(len(c_vals)):
            val = data[i, j]
            if np.isnan(val):
                continue
            # Choose text color for contrast
            text_color = (
                "white" if val < norm.vmin + 0.55 * (norm.vmax - norm.vmin) else "black"
            )
            ax.text(
                j,
                i,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=7.5,
                color=text_color,
                fontweight="bold",
            )

    # Star marker on the promoted config — offset to upper-right corner
    # so it does not occlude the numeric annotation at cell center
    try:
        r_idx = r_vals.index(star_r)
        c_idx = c_vals.index(star_c)
        ax.plot(
            c_idx + 0.33,
            r_idx + 0.33,
            marker="*",
            color="red",
            markersize=11,
            markeredgecolor="white",
            markeredgewidth=0.7,
            zorder=10,
        )
    except ValueError:
        print(f"WARNING: star at (r={star_r}, c={star_c}) not on grid")

    # Axes
    ax.set_xticks(range(len(c_vals)))
    ax.set_xticklabels([f"{v:.2f}" for v in c_vals], fontsize=8)
    ax.set_yticks(range(len(r_vals)))
    ax.set_yticklabels([f"{v:.3f}" for v in r_vals], fontsize=8)
    ax.set_xlabel("Collection size ($c$)", fontsize=9)
    ax.set_ylabel("Execution rate ($r$)", fontsize=9)

    # Panel label — above the axes
    ax.set_title(panel_label, fontsize=9, fontweight="bold", pad=6)

    return im


# Short labels for Phase B operator profiles
PHASE_B_LABELS = {
    "B01": "AR",
    "B02": "EAR-PA",
    "B03": "EAR-P",
    "B04": "EAR-T",
    "B05": "EAR-N",
}


def plot_bar_panel(
    ax,
    phase_b: pd.DataFrame,
    panel_label: str,
    norm: Normalize,
    cmap,
):
    """Draw a horizontal bar chart for Phase B operator comparison."""
    # Sort by MeanCombinedRank (best first = lowest rank at top visually)
    phase_b = phase_b.sort_values("MeanCombinedRank", ascending=True).copy()

    config_ids = phase_b["ConfigID"].tolist()
    ranks = phase_b["MeanCombinedRank"].values
    labels = [PHASE_B_LABELS.get(cid, cid) for cid in config_ids]

    # Color bars using the shared colormap
    colors = [cmap(norm(v)) for v in ranks]

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, ranks, color=colors, edgecolor="white", linewidth=0.5)

    # Highlight the winner with a star — positioned after the bar end,
    # to the right of the value annotation, avoiding overlap
    best_idx = 0  # already sorted, best is first
    ax.plot(
        ranks[best_idx] + 0.04,
        y_pos[best_idx],
        marker="*",
        color="red",
        markersize=11,
        markeredgecolor="white",
        markeredgewidth=0.7,
        zorder=10,
        clip_on=False,
    )

    # Value annotations inside bars
    for i, (bar, val) in enumerate(zip(bars, ranks)):
        text_color = (
            "white" if val < norm.vmin + 0.55 * (norm.vmax - norm.vmin) else "black"
        )
        ax.text(
            val - 0.015,
            y_pos[i],
            f"{val:.2f}",
            ha="right",
            va="center",
            fontsize=7.5,
            color=text_color,
            fontweight="bold",
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Mean combined rank", fontsize=9)
    ax.set_xlim(0, norm.vmax * 1.08)
    ax.invert_yaxis()  # best (lowest rank) at the top

    # Panel label — above the axes
    ax.set_title(panel_label, fontsize=9, fontweight="bold", pad=6)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not os.path.exists(RANKING_CSV):
        print(f"ERROR: {RANKING_CSV} not found")
        sys.exit(1)

    df = pd.read_csv(RANKING_CSV)

    # ----- Phase A, Cycles=2 -----
    phase_a = df[(df["Phase"] == "A") & (df["Cycles"] == 2)].copy()
    r_a = sorted(phase_a["R"].unique())
    c_a = sorted(phase_a["C"].unique())
    data_a = build_pivot(phase_a, r_a, c_a)

    # ----- Phase B -----
    phase_b = df[df["Phase"] == "B"].copy()

    # ----- Phase C, EARL (EAR-P light: MutRate=0.3, VarRate=0.1) -----
    phase_c = df[
        (df["Phase"] == "C") & (df["MutRate"] == 0.3) & (df["VarRate"] == 0.1)
    ].copy()
    r_c = sorted(phase_c["R"].unique())
    c_c = sorted(phase_c["C"].unique())
    data_c = build_pivot(phase_c, r_c, c_c)

    # Shared color normalization across all three panels (lower rank = better = darker)
    all_vals = np.concatenate(
        [
            data_a[~np.isnan(data_a)],
            phase_b["MeanCombinedRank"].values,
            data_c[~np.isnan(data_c)],
        ]
    )
    vmin, vmax = float(all_vals.min()), float(all_vals.max())
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap("cividis_r")  # reversed: darker = lower rank = better

    # ----- Figure: 3 panels + colorbar -----
    fig = plt.figure(figsize=(8.2, 3.0))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1.05, 0.8, 0.05], wspace=0.50)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    cax = fig.add_subplot(gs[0, 3])

    im_a = plot_heatmap_panel(
        ax_a,
        data_a,
        r_a,
        c_a,
        star_r=0.200,
        star_c=0.16,
        star_label="A43",
        panel_label="(a) Phase A — AR, $\\ell{=}2$",
        norm=norm,
        cmap=cmap,
    )

    plot_bar_panel(
        ax_b,
        phase_b,
        panel_label="(b) Phase B — Operator",
        norm=norm,
        cmap=cmap,
    )

    im_c = plot_heatmap_panel(
        ax_c,
        data_c,
        r_c,
        c_c,
        star_r=0.225,
        star_c=0.12,
        star_label="C26",
        panel_label="(c) Phase C — EAR-PA",
        norm=norm,
        cmap=cmap,
    )
    ax_c.set_ylabel("")  # avoid redundant y-label

    cbar = fig.colorbar(im_c, cax=cax)
    cbar.set_label("Mean combined rank", fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    fig.subplots_adjust(left=0.06, right=0.96, bottom=0.20, top=0.88)

    # Save
    for path in [OUT_PAPER, OUT_RESULTS]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fig.savefig(path, dpi=150)
        print(f"Saved: {path}")

    # Also save high-res PNG
    png_path = OUT_PAPER.replace(".pdf", ".png")
    fig.savefig(png_path, dpi=600)
    print(f"Saved: {png_path}")

    plt.close()

    # Console summary
    print("\n--- Phase A (Cycles=2, AR) ---")
    print(f"  Grid: {len(r_a)}R × {len(c_a)}C = {len(r_a) * len(c_a)} cells")
    best_a = phase_a.loc[phase_a["MeanCombinedRank"].idxmin()]
    print(
        f"  Best: {best_a['ConfigID']} (r={best_a['R']}, c={best_a['C']}, rank={best_a['MeanCombinedRank']:.4f})"
    )

    print("\n--- Phase B (Operator Comparison) ---")
    print(f"  Profiles: {len(phase_b)}")
    best_b = phase_b.loc[phase_b["MeanCombinedRank"].idxmin()]
    print(
        f"  Best: {best_b['ConfigID']} ({PHASE_B_LABELS.get(best_b['ConfigID'], best_b['ConfigID'])}, rank={best_b['MeanCombinedRank']:.4f})"
    )

    print("\n--- Phase C (EARL) ---")
    print(f"  Grid: {len(r_c)}R × {len(c_c)}C = {len(r_c) * len(c_c)} cells")
    best_c = phase_c.loc[phase_c["MeanCombinedRank"].idxmin()]
    print(
        f"  Best: {best_c['ConfigID']} (r={best_c['R']}, c={best_c['C']}, rank={best_c['MeanCombinedRank']:.4f})"
    )


if __name__ == "__main__":
    main()
