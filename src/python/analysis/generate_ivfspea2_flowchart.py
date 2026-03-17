#!/usr/bin/env python3
"""
Generate a submission-ready flowchart for IVF/SPEA2 (Algorithm 1).

Matches the pseudocode in sn-article.tex exactly:
  1. Init -> SPEA2 fitness -> IVF trigger check
  2. If triggered: Collection + EAR-PA (once) -> [cycle loop: dissimilar-father SBX ->
     IVF env selection -> collective check -> yes: loop / no: exit]
  3. After IVF (or if not triggered): generate host offspring with remaining budget ->
     host env selection -> FE < FE_max? -> yes: next generation / no: return

Output:
  - paper/figures/flowchart.pdf
  - paper/figures/flowchart.png
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
OUT_DIR = os.path.join(ROOT, "paper", "figures")
OUT_PDF = os.path.join(OUT_DIR, "flowchart.pdf")
OUT_PNG = os.path.join(OUT_DIR, "flowchart.png")

# --- Colors ---
COMMON_FC = "#EAF0F6"
IVF_FC = "#DCEAF7"
DECISION_FC = "#F7E7C6"
END_FC = "#E8F2E0"
EDGE_C = "#3A4A5A"
TEXT_C = "#334455"


def rounded_box(ax, x, y, w, h, text, fc, ec=EDGE_C, fontsize=7.5, bold=False):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.0,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
    )
    return patch


def diamond(ax, x, y, w, h, text, fc, ec=EDGE_C, fontsize=7.5):
    verts = [
        (x + w / 2, y + h),
        (x + w, y + h / 2),
        (x + w / 2, y),
        (x, y + h / 2),
    ]
    patch = Polygon(verts, closed=True, linewidth=1.0, edgecolor=ec, facecolor=fc)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)
    return patch


def arrow(
    ax, xy1, xy2, text=None, text_xy=None, connectionstyle="arc3", text_fontsize=6.5
):
    patch = FancyArrowPatch(
        xy1,
        xy2,
        arrowstyle="-|>",
        mutation_scale=11,
        linewidth=0.9,
        color=EDGE_C,
        connectionstyle=connectionstyle,
    )
    ax.add_patch(patch)
    if text and text_xy:
        ax.text(
            text_xy[0],
            text_xy[1],
            text,
            fontsize=text_fontsize,
            ha="center",
            va="center",
            color=TEXT_C,
        )


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )

    fig, ax = plt.subplots(figsize=(14.2, 5.4))
    ax.set_xlim(-0.1, 14.6)
    ax.set_ylim(-0.1, 5.7)
    ax.axis("off")

    bh = 0.82  # standard box height

    # ========== MAIN GENERATION LOOP (top row, y ~ 3.4) ==========

    # Box 1: Initialize
    rounded_box(
        ax, 0.2, 3.4, 1.4, bh, "Initialize\npopulation $P_0$\nand evaluate", COMMON_FC
    )

    # Box 2: Compute SPEA2 fitness
    rounded_box(
        ax, 2.0, 3.4, 1.6, bh, "Compute SPEA2\nfitness $F(i)$\non $P_t$", COMMON_FC
    )

    # Diamond 1: IVF activation trigger
    diamond(
        ax, 4.1, 3.2, 1.5, 1.2, r"$FE_{\mathrm{IVF}} \leq r \cdot FE$?", DECISION_FC
    )

    # Box 5: Generate host offspring
    rounded_box(
        ax,
        6.6,
        3.4,
        1.8,
        bh,
        "Generate $N - n_{\\mathrm{ivf}}$\nhost offspring\n(SPEA2 variation)",
        COMMON_FC,
    )

    # Box 6: Host environmental selection
    rounded_box(
        ax,
        8.8,
        3.4,
        1.75,
        bh,
        "Environmental\nselection\n$P_{t+1} \\to$ size $N$",
        COMMON_FC,
    )

    # Diamond 2: FE < FE_max?
    diamond(ax, 10.95, 3.2, 1.4, 1.2, r"$FE < FE_{\max}$?", DECISION_FC)

    # Box 7: Return
    rounded_box(ax, 12.85, 3.4, 1.05, bh, "Return\nfinal\narchive $P_t$", END_FC)

    # ========== IVF PHASE (bottom row, y ~ 1.2) ==========

    # Box A: Collection + EAR-PA (once before cycle loop)
    rounded_box(
        ax, 2.9, 1.2, 1.9, bh, "Collect mothers,\nfather pool;\nEAR-PA mutation", IVF_FC
    )

    # Box B: Dissimilar-father SBX (inside cycle loop)
    rounded_box(
        ax,
        5.2,
        1.2,
        1.9,
        bh,
        "Dissimilar-father\nselection + SBX\n(one offspring/mother)",
        IVF_FC,
    )

    # Box C: IVF environmental selection
    rounded_box(
        ax, 7.5, 1.2, 1.9, bh, "Environmental\nselection;\nupdate $\\bar{F}$", IVF_FC
    )

    # Diamond 3: Collective improvement?
    diamond(
        ax,
        10.0,
        1.05,
        1.55,
        1.15,
        "$\\bar{F}_{\\mathrm{after}}"
        " < \\bar{F}_{\\mathrm{before}}$\n"
        "& cycle $\\leq \\ell$?",
        DECISION_FC,
        fontsize=6.5,
    )

    # ========== ARROWS: MAIN LOOP ==========

    # Init -> SPEA2 fitness
    arrow(ax, (1.6, 3.81), (2.0, 3.81))

    # SPEA2 fitness -> IVF trigger
    arrow(ax, (3.6, 3.81), (4.1, 3.81))

    # IVF trigger -> (no) -> Host offspring
    arrow(ax, (5.6, 3.81), (6.6, 3.81), text="no", text_xy=(6.05, 4.05))

    # Host offspring -> Host env selection
    arrow(ax, (8.4, 3.81), (8.8, 3.81))

    # Host env selection -> FE check
    arrow(ax, (10.55, 3.81), (10.95, 3.81))

    # FE check -> (no) -> Return
    arrow(ax, (12.35, 3.81), (12.85, 3.81), text="no", text_xy=(12.55, 4.05))

    # FE check -> (yes) -> loop back to SPEA2 fitness (top arc)
    arrow(
        ax,
        (11.65, 4.4),
        (2.8, 4.35),
        text="yes",
        text_xy=(7.0, 5.0),
        connectionstyle="arc3,rad=0.15",
    )

    # ========== ARROWS: IVF PHASE ==========

    # IVF trigger -> (yes) -> Collection + EAR-PA (diagonal down)
    arrow(ax, (4.85, 3.2), (3.85, 2.02), text="yes", text_xy=(3.9, 2.65))

    # Collection -> SBX
    arrow(ax, (4.8, 1.61), (5.2, 1.61))

    # SBX -> IVF env selection
    arrow(ax, (7.1, 1.61), (7.5, 1.61))

    # IVF env selection -> Collective check
    arrow(ax, (9.4, 1.61), (10.0, 1.61))

    # Collective check -> (yes) -> loop back to SBX (arc passing BELOW env selection)
    arrow(
        ax,
        (10.775, 1.05),
        (7.1, 1.2),
        text="yes",
        text_xy=(8.9, 0.37),
        connectionstyle="arc3,rad=-0.25",
    )

    # Collective check -> (no) -> up to Host offspring (clear vertical path)
    # Go up from diamond top to a point, then left to host offspring box
    arrow(
        ax,
        (10.78, 2.2),
        (7.5, 3.4),
        text="no",
        text_xy=(9.4, 2.6),
        connectionstyle="arc3,rad=-0.15",
    )

    # ========== ANNOTATIONS ==========

    # IVF cycle bracket label
    ax.text(
        8.0,
        0.15,
        "IVF cycle loop (up to $\\ell$ cycles per generation)",
        ha="center",
        va="center",
        fontsize=7,
        style="italic",
        color=TEXT_C,
    )

    # Budget annotation at top
    ax.text(
        7.2,
        5.4,
        "Per-generation budget: IVF consumes $n_{\\mathrm{ivf}}$ evaluations; "
        "SPEA2 uses the remaining $N - n_{\\mathrm{ivf}}$. "
        "Total evaluations per generation $= N$.",
        ha="center",
        va="center",
        fontsize=7,
        style="italic",
        color=TEXT_C,
    )

    fig.savefig(OUT_PDF)
    fig.savefig(OUT_PNG)
    plt.close(fig)

    print(f"Saved: {OUT_PDF}")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
