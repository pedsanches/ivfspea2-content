#!/usr/bin/env python3
"""Multi-algorithm Pareto-front comparison panel (2x2).

Generates a single publication-quality figure with four panels showing
algorithm fronts overlaid on the same axes, making convergence and spread
differences directly visible:

  (a) DTLZ2  M=2  — 2-D synthetic (with true PF)
  (b) RWMOP9 M=2  — 2-D engineering (empirical PF)
  (c) WFG2   M=3  — 3-D synthetic (with true PF)
  (d) RWMOP8 M=3  — 3-D engineering (no analytical PF)

Each panel includes a median-IGD annotation box so quantitative differences
are clear even when fronts visually overlap.

Usage:
    python src/python/analysis/plot_front_comparison_panel.py
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort

# ── paths ──────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
FRONTS_DIR = os.path.join(ROOT, "data", "processed", "fronts")
METRICS_CSV = os.path.join(
    ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
ENG_SUMMARY = os.path.join(
    ROOT, "results", "engineering_suite", "engineering_suite_summary_main.csv"
)
OUT_DIR = os.path.join(ROOT, "paper", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── style ──────────────────────────────────────────────────────────────
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

# ── palette & markers ─────────────────────────────────────────────────
PALETTE = {
    "IVFSPEA2": "#2166AC",
    "SPEA2": "#B2182B",
    "NSGAIII": "#984EA3",
    "MOEAD": "#FF7F00",
    "ARMOEA": "#999999",
}

MARKER = {
    "IVFSPEA2": "o",
    "SPEA2": "s",
    "NSGAIII": "^",
    "MOEAD": "D",
    "ARMOEA": "P",
}

DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "ARMOEA": "AR-MOEA",
}

# ── metrics helpers ───────────────────────────────────────────────────
_METRICS_DF: pd.DataFrame | None = None
_ENG_DF: pd.DataFrame | None = None


def _get_metrics() -> pd.DataFrame:
    """Load and cache the consolidated metrics (with cohort filter)."""
    global _METRICS_DF
    if _METRICS_DF is None:
        raw = pd.read_csv(METRICS_CSV)
        synth = raw[raw["Grupo"] != "RWMOP"].copy()
        _METRICS_DF = filter_submission_synthetic_cohort(synth)
    return _METRICS_DF


def _get_eng_summary() -> pd.DataFrame:
    """Load engineering suite summary (has all baselines for RWMOP)."""
    global _ENG_DF
    if _ENG_DF is None and os.path.isfile(ENG_SUMMARY):
        _ENG_DF = pd.read_csv(ENG_SUMMARY)
    return _ENG_DF


def _median_igd(problem: str, m: str, algos: list[str]) -> dict[str, float]:
    """Return {algo: median_IGD} for the given problem/M."""
    out: dict[str, float] = {}

    if problem.startswith("RWMOP"):
        eng = _get_eng_summary()
        if eng is not None:
            sub = eng[eng["Problem"] == problem]
            for algo in algos:
                row = sub[sub["Algorithm"] == algo]
                if not row.empty:
                    val = row["MedianIGD_PF"].values[0]
                    if not np.isnan(val):
                        out[algo] = float(val)
    else:
        df = _get_metrics()
        sub = df[(df["Problema"] == problem) & (df["M"] == m)]
        for algo in algos:
            vals = sub[sub["Algoritmo"] == algo]["IGD"].dropna()
            if len(vals):
                out[algo] = float(vals.median())
    return out


# ── file loaders ──────────────────────────────────────────────────────


def _load(problem: str, m: str, algo: str) -> pd.DataFrame | None:
    path = os.path.join(FRONTS_DIR, f"{problem}_{m}_{algo}_median.csv")
    if os.path.isfile(path):
        return pd.read_csv(path)
    return None


def _load_pf(problem: str, m: str) -> pd.DataFrame | None:
    path = os.path.join(FRONTS_DIR, f"{problem}_{m}_truePF.csv")
    if os.path.isfile(path):
        return pd.read_csv(path)
    return None


# ── annotation ────────────────────────────────────────────────────────


def _igd_annotation(
    ax, algos: list[str], igd: dict[str, float], loc: str = "upper right"
) -> None:
    """Add a small text box with median IGD per algorithm."""
    lines = []
    for algo in algos:
        if algo in igd:
            name = DISPLAY[algo]
            val = igd[algo]
            txt = f"{val:.2e}" if val < 0.01 else f"{val:.4f}"
            # Bold the best (lowest) value
            is_best = val == min(igd.values())
            prefix = ">" if is_best else " "
            lines.append(f"{prefix}{name:<10s} {txt}")
    if not lines:
        return
    text = " IGD (median)\n" + "\n".join(lines)
    props = dict(
        boxstyle="round,pad=0.3", facecolor="white", edgecolor="#AAAAAA", alpha=0.90
    )

    x, y, ha, va = {
        "upper right": (0.97, 0.97, "right", "top"),
        "upper left": (0.03, 0.97, "left", "top"),
        "lower right": (0.97, 0.03, "right", "bottom"),
        "lower left": (0.03, 0.03, "left", "bottom"),
    }.get(loc, (0.97, 0.97, "right", "top"))

    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        fontsize=5.5,
        verticalalignment=va,
        horizontalalignment=ha,
        bbox=props,
        family="monospace",
        zorder=10,
    )


# ── scatter plots ─────────────────────────────────────────────────────


def _scatter_2d(
    ax, algos: list[str], problem: str, m: str, title: str, igd_loc: str = "upper right"
) -> None:
    """Plot 2-D overlaid fronts. IVF/SPEA2 behind so deviations show."""
    pf = _load_pf(problem, m)
    if pf is not None:
        ax.scatter(
            pf["f1"],
            pf["f2"],
            s=3,
            c="#D0D0D0",
            alpha=0.55,
            zorder=0,
            edgecolors="none",
        )

    for idx, algo in enumerate(algos):
        df = _load(problem, m, algo)
        if df is None:
            continue
        is_ivf = algo == "IVFSPEA2"
        s = 18 if is_ivf else 14
        z = 1 if is_ivf else (2 + idx)
        alpha = 0.70 if is_ivf else 0.85
        ec = "#444444" if not is_ivf else "none"
        ew = 0.3 if not is_ivf else 0.0
        ax.scatter(
            df["f1"],
            df["f2"],
            s=s,
            c=PALETTE[algo],
            marker=MARKER[algo],
            alpha=alpha,
            zorder=z,
            edgecolors=ec,
            linewidths=ew,
        )

    ax.set_xlabel("$f_1$")
    ax.set_ylabel("$f_2$")
    ax.set_title(title, fontsize=8, pad=4)
    ax.grid(True, linestyle="--", alpha=0.22)

    igd = _median_igd(problem, m, algos)
    _igd_annotation(ax, algos, igd, loc=igd_loc)


def _scatter_3d(
    ax, algos: list[str], problem: str, m: str, title: str, igd_loc: str = "upper left"
) -> None:
    """Plot 3-D overlaid fronts."""
    pf = _load_pf(problem, m)
    if pf is not None:
        ax.scatter(
            pf["f1"],
            pf["f2"],
            pf["f3"],
            s=2,
            c="#D0D0D0",
            alpha=0.30,
            zorder=0,
            depthshade=False,
        )

    for idx, algo in enumerate(algos):
        df = _load(problem, m, algo)
        if df is None:
            continue
        is_ivf = algo == "IVFSPEA2"
        s = 16 if is_ivf else 10
        alpha = 0.65 if is_ivf else 0.82
        ax.scatter(
            df["f1"],
            df["f2"],
            df["f3"],
            s=s,
            c=PALETTE[algo],
            marker=MARKER[algo],
            alpha=alpha,
            depthshade=False,
            edgecolors="none",
        )

    ax.set_xlabel("$f_1$", fontsize=6, labelpad=1)
    ax.set_ylabel("$f_2$", fontsize=6, labelpad=1)
    ax.set_zlabel("$f_3$", fontsize=6, labelpad=1)
    ax.tick_params(labelsize=5)
    ax.view_init(elev=24, azim=-53)
    ax.set_title(title, fontsize=8, pad=0)
    ax.grid(True, linestyle="--", alpha=0.18)

    # 2D annotation via fig-level text (ax.transAxes unreliable in 3D)
    igd = _median_igd(problem, m, algos)
    if igd:
        lines = []
        for algo in algos:
            if algo in igd:
                val = igd[algo]
                txt = f"{val:.2e}" if val < 0.01 else f"{val:.4f}"
                is_best = val == min(igd.values())
                prefix = ">" if is_best else " "
                lines.append(f"{prefix}{DISPLAY[algo]:<10s} {txt}")
        text = " IGD (median)\n" + "\n".join(lines)
        # Place text in axes coordinates — approximate safe spot
        ax.text2D(
            0.02,
            0.96,
            text,
            transform=ax.transAxes,
            fontsize=5,
            verticalalignment="top",
            family="monospace",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                edgecolor="#AAAAAA",
                alpha=0.90,
            ),
            zorder=10,
        )


# ── main ──────────────────────────────────────────────────────────────


def main() -> None:
    synth_algos = ["IVFSPEA2", "SPEA2", "NSGAIII", "MOEAD"]
    eng_algos = ["IVFSPEA2", "SPEA2", "NSGAIII", "ARMOEA"]

    fig = plt.figure(figsize=(8.0, 7.2))
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1.15], hspace=0.32, wspace=0.30)

    # (a) DTLZ2 M=2 — 2D synthetic
    ax_a = fig.add_subplot(gs[0, 0])
    _scatter_2d(
        ax_a,
        synth_algos,
        "DTLZ2",
        "M2",
        r"(a) DTLZ2 ($M\!=\!2$)",
        igd_loc="upper right",
    )

    # (b) RWMOP9 M=2 — 2D engineering
    ax_b = fig.add_subplot(gs[0, 1])
    _scatter_2d(
        ax_b, eng_algos, "RWMOP9", "M2", r"(b) RWMOP9 ($M\!=\!2$)", igd_loc="upper left"
    )

    # (c) WFG2 M=3 — 3D synthetic
    ax_c = fig.add_subplot(gs[1, 0], projection="3d")
    _scatter_3d(ax_c, synth_algos, "WFG2", "M3", r"(c) WFG2 ($M\!=\!3$)")

    # (d) RWMOP8 M=3 — 3D engineering
    ax_d = fig.add_subplot(gs[1, 1], projection="3d")
    _scatter_3d(ax_d, eng_algos, "RWMOP8", "M3", r"(d) RWMOP8 ($M\!=\!3$)")

    # ── shared legend ─────────────────────────────────────────────────
    all_algos = dict.fromkeys(synth_algos + eng_algos)
    handles = [
        Line2D(
            [],
            [],
            marker="o",
            color="none",
            markerfacecolor="#D0D0D0",
            markersize=4,
            label="True PF",
            markeredgecolor="none",
        )
    ]
    for algo in all_algos:
        handles.append(
            Line2D(
                [],
                [],
                marker=MARKER[algo],
                color="none",
                markerfacecolor=PALETTE[algo],
                markersize=5,
                markeredgecolor="#111111" if algo == "IVFSPEA2" else "none",
                markeredgewidth=0.3,
                label=DISPLAY[algo],
            )
        )

    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=6,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
        columnspacing=1.0,
        handletextpad=0.3,
    )

    outpath = os.path.join(OUT_DIR, "front_comparison_panel.pdf")
    fig.savefig(outpath)
    print(f"Saved: {outpath}")

    png = outpath.replace(".pdf", ".png")
    fig.savefig(png)
    print(f"Saved: {png}")
    plt.close(fig)


if __name__ == "__main__":
    main()
