#!/usr/bin/env python3
"""Generate readability-first front figures for paper review.

This script does not overwrite the current manuscript figures.
It creates candidate alternatives focused on visual interpretability.
"""

from __future__ import annotations

import os
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
FRONTS_DIR = os.path.join(ROOT, "data", "processed", "fronts")
OUT_DIR = os.path.join(ROOT, "paper", "figures")

ALGO_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "ARMOEA": "AR-MOEA",
}

PALETTE = {
    "IVFSPEA2": "#2166AC",
    "SPEA2": "#B2182B",
    "NSGAIII": "#1B9E77",
    "MOEAD": "#E6AB02",
    "ARMOEA": "#6A3D9A",
}

MARKER = {
    "IVFSPEA2": "o",
    "SPEA2": "s",
    "NSGAIII": "^",
    "MOEAD": "D",
    "ARMOEA": "P",
}


def load_csv(name: str) -> pd.DataFrame | None:
    path = os.path.join(FRONTS_DIR, name)
    if not os.path.isfile(path):
        return None
    return pd.read_csv(path)


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.titlesize": 8,
            "axes.labelsize": 8,
            "legend.fontsize": 7,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
        }
    )


def scatter_algorithms(
    ax: plt.Axes,
    datasets: dict[str, pd.DataFrame | None],
    x: str,
    y: str,
    algorithms: Iterable[str],
) -> None:
    for algo in algorithms:
        data = datasets.get(algo)
        if data is None:
            continue
        s = 12 if algo == "IVFSPEA2" else 11
        edge = "#111111" if algo == "IVFSPEA2" else "none"
        ax.scatter(
            data[x],
            data[y],
            s=s,
            marker=MARKER[algo],
            c=PALETTE[algo],
            alpha=0.78,
            edgecolors=edge,
            linewidths=0.2,
            label=ALGO_DISPLAY[algo],
        )


def add_legend(fig: plt.Figure, handles, labels, ncol: int) -> None:
    if not handles:
        return
    fig.legend(
        handles,
        labels,
        ncol=ncol,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.01),
        frameon=True,
    )


def make_pareto_candidate() -> None:
    style()
    os.makedirs(OUT_DIR, exist_ok=True)

    synthetic_algos = ["IVFSPEA2", "SPEA2", "NSGAIII", "MOEAD"]
    engineering_algos = ["IVFSPEA2", "SPEA2", "NSGAIII", "ARMOEA"]

    dtlz2_pf = load_csv("DTLZ2_M2_truePF.csv")
    dtlz2 = {algo: load_csv(f"DTLZ2_M2_{algo}_median.csv") for algo in synthetic_algos}

    wfg2_pf = load_csv("WFG2_M3_truePF.csv")
    wfg2 = {algo: load_csv(f"WFG2_M3_{algo}_median.csv") for algo in synthetic_algos}

    rwmop9 = {
        algo: load_csv(f"RWMOP9_M2_{algo}_median.csv") for algo in engineering_algos
    }

    fig, axes = plt.subplots(1, 3, figsize=(9.4, 3.1))

    # (a) DTLZ2
    ax = axes[0]
    if dtlz2_pf is not None:
        ax.scatter(
            dtlz2_pf["f1"],
            dtlz2_pf["f2"],
            s=3,
            c="#D0D0D0",
            alpha=0.55,
            label="True PF",
            zorder=1,
        )
    scatter_algorithms(ax, dtlz2, "f1", "f2", synthetic_algos)
    ax.set_title("(a) DTLZ2 ($M=2$)")
    ax.set_xlabel("$f_1$")
    ax.set_ylabel("$f_2$")
    ax.grid(True, linestyle="--", alpha=0.22)

    # (b) WFG2 projection f1-f2
    ax = axes[1]
    if wfg2_pf is not None:
        ax.scatter(
            wfg2_pf["f1"],
            wfg2_pf["f2"],
            s=3,
            c="#D0D0D0",
            alpha=0.5,
            label="True PF projection",
            zorder=1,
        )
    scatter_algorithms(ax, wfg2, "f1", "f2", synthetic_algos)
    ax.set_title("(b) WFG2 ($M=3$), projection $f_1$-$f_2$")
    ax.set_xlabel("$f_1$")
    ax.set_ylabel("$f_2$")
    ax.grid(True, linestyle="--", alpha=0.22)

    # (c) RWMOP9
    ax = axes[2]
    scatter_algorithms(ax, rwmop9, "f1", "f2", engineering_algos)
    ax.set_title("(c) RWMOP9 ($M=2$)")
    ax.set_xlabel("$f_1$")
    ax.set_ylabel("$f_2$")
    ax.grid(True, linestyle="--", alpha=0.22)

    handles, labels = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    h3, l3 = axes[2].get_legend_handles_labels()
    seen = set(labels)
    for h, l in zip(h2 + h3, l2 + l3):
        if l not in seen:
            handles.append(h)
            labels.append(l)
            seen.add(l)
    add_legend(fig, handles, labels, ncol=6)

    fig.suptitle(
        "Candidate visual revision: representative fronts", y=1.02, fontsize=10
    )
    plt.tight_layout(rect=[0, 0.09, 1, 0.95], w_pad=1.1)
    out = os.path.join(OUT_DIR, "pareto_fronts_candidate.pdf")
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


def make_engineering_candidate() -> None:
    style()
    os.makedirs(OUT_DIR, exist_ok=True)

    algos = ["IVFSPEA2", "SPEA2", "NSGAIII", "ARMOEA"]
    rwmop9 = {algo: load_csv(f"RWMOP9_M2_{algo}_median.csv") for algo in algos}
    rwmop8 = {algo: load_csv(f"RWMOP8_M3_{algo}_median.csv") for algo in algos}

    fig, axes = plt.subplots(2, 2, figsize=(8.6, 5.3))

    scatter_algorithms(axes[0, 0], rwmop9, "f1", "f2", algos)
    axes[0, 0].set_title("(a) RWMOP9 ($M=2$): $f_1$-$f_2$")
    axes[0, 0].set_xlabel("$f_1$")
    axes[0, 0].set_ylabel("$f_2$")
    axes[0, 0].grid(True, linestyle="--", alpha=0.22)

    scatter_algorithms(axes[0, 1], rwmop8, "f1", "f2", algos)
    axes[0, 1].set_title("(b) RWMOP8 ($M=3$): $f_1$-$f_2$")
    axes[0, 1].set_xlabel("$f_1$")
    axes[0, 1].set_ylabel("$f_2$")
    axes[0, 1].grid(True, linestyle="--", alpha=0.22)

    scatter_algorithms(axes[1, 0], rwmop8, "f1", "f3", algos)
    axes[1, 0].set_title("(c) RWMOP8 ($M=3$): $f_1$-$f_3$")
    axes[1, 0].set_xlabel("$f_1$")
    axes[1, 0].set_ylabel("$f_3$")
    axes[1, 0].grid(True, linestyle="--", alpha=0.22)

    scatter_algorithms(axes[1, 1], rwmop8, "f2", "f3", algos)
    axes[1, 1].set_title("(d) RWMOP8 ($M=3$): $f_2$-$f_3$")
    axes[1, 1].set_xlabel("$f_2$")
    axes[1, 1].set_ylabel("$f_3$")
    axes[1, 1].grid(True, linestyle="--", alpha=0.22)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    add_legend(fig, handles, labels, ncol=4)
    fig.suptitle("Candidate visual revision: engineering fronts", y=1.01, fontsize=10)
    plt.tight_layout(rect=[0, 0.07, 1, 0.96], h_pad=1.0, w_pad=1.0)
    out = os.path.join(OUT_DIR, "engineering_fronts_candidate.pdf")
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


def make_dtlz4_candidate() -> None:
    style()
    os.makedirs(OUT_DIR, exist_ok=True)

    pf = load_csv("DTLZ4_M3_truePF.csv")
    good = load_csv("DTLZ4_M3_IVFSPEA2_good.csv")
    bad = load_csv("DTLZ4_M3_IVFSPEA2_bad.csv")
    meta = load_csv("DTLZ4_M3_selection_metadata.csv")

    if pf is None or good is None or bad is None:
        print("Skipping DTLZ4 candidate: missing input CSVs")
        return

    label_good = "Good run"
    label_bad = "Bad run"
    if meta is not None:
        mg = meta[meta["selection_type"] == "good_q1"]
        mb = meta[meta["selection_type"] == "bad_q3_gt_0p1"]
        if not mg.empty:
            label_good = f"Good run (RunID {int(mg.iloc[0]['run_id'])}, IGD={mg.iloc[0]['igd']:.3g})"
        if not mb.empty:
            label_bad = f"Bad run (RunID {int(mb.iloc[0]['run_id'])}, IGD={mb.iloc[0]['igd']:.3g})"

    fig, axes = plt.subplots(2, 3, figsize=(9.3, 4.9))
    pairs = [("f1", "f2"), ("f1", "f3"), ("f2", "f3")]

    for col, (x, y) in enumerate(pairs):
        axg = axes[0, col]
        axg.scatter(
            pf[x], pf[y], s=3, c="#CFCFCF", alpha=0.45, label="True PF", zorder=1
        )
        axg.scatter(
            good[x],
            good[y],
            s=12,
            c=PALETTE["IVFSPEA2"],
            marker=MARKER["IVFSPEA2"],
            alpha=0.8,
            edgecolors="#111111",
            linewidths=0.2,
            label="IVF/SPEA2",
            zorder=2,
        )
        axg.set_title(f"(a{col + 1}) {label_good}\nProjection ${x}$-${y}$", fontsize=7)
        axg.set_xlabel(f"${x}$")
        axg.set_ylabel(f"${y}$")
        axg.grid(True, linestyle="--", alpha=0.2)

        axb = axes[1, col]
        axb.scatter(
            pf[x], pf[y], s=3, c="#CFCFCF", alpha=0.45, label="True PF", zorder=1
        )
        axb.scatter(
            bad[x],
            bad[y],
            s=12,
            c=PALETTE["SPEA2"],
            marker=MARKER["SPEA2"],
            alpha=0.8,
            edgecolors="#111111",
            linewidths=0.2,
            label="IVF/SPEA2",
            zorder=2,
        )
        axb.set_title(f"(b{col + 1}) {label_bad}\nProjection ${x}$-${y}$", fontsize=7)
        axb.set_xlabel(f"${x}$")
        axb.set_ylabel(f"${y}$")
        axb.grid(True, linestyle="--", alpha=0.2)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    add_legend(fig, handles, labels, ncol=2)
    fig.suptitle("Candidate visual revision: DTLZ4 bimodal regime", y=1.01, fontsize=10)
    plt.tight_layout(rect=[0, 0.07, 1, 0.96], h_pad=0.9, w_pad=0.7)
    out = os.path.join(OUT_DIR, "dtlz4_bimodal_candidate.pdf")
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


def main() -> None:
    make_pareto_candidate()
    make_engineering_candidate()
    make_dtlz4_candidate()


if __name__ == "__main__":
    main()
