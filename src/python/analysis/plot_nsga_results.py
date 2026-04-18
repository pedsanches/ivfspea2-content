#!/usr/bin/env python3
"""
Figures for the IVF/NSGA-II and IVF/NSGA-III paper.

Figure 1: Win/tie/loss bar chart (both tracks, IGD and HV)
Figure 2: Per-problem IGD scatter (IVF vs base, log scale), one subplot per track
Figure 3: Aggregate performance profile (Pareto ranking across problems)

Reads:  results/tables/nsga_*_stats.csv
        data/processed/nsga_experiments.csv
Writes: results/figures/nsga_fig1_wintieloss.pdf
        results/figures/nsga_fig2_scatter.pdf
        results/figures/nsga_fig3_profile.pdf
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
DATA_CSV  = os.path.join(PROJECT_ROOT, "data", "processed", "nsga_experiments.csv")
FIG_DIR   = os.path.join(PROJECT_ROOT, "results", "figures")

TRACKS = [
    ("IVFNSGAII",  "NSGAII",  "IVF/NSGA-II",  "NSGA-II"),
    ("IVFNSGAIII", "NSGAIII", "IVF/NSGA-III", "NSGA-III"),
]

COLORS = {"wins": "#2ecc71", "ties": "#95a5a6", "losses": "#e74c3c"}

os.makedirs(FIG_DIR, exist_ok=True)


# ────────────────────────────────────────────────────────────────────────────
# Figure 1: Win / tie / loss grouped bar chart
# ────────────────────────────────────────────────────────────────────────────
def fig_wintieloss():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=False)

    for ax, (ivf_algo, base_algo, ivf_label, base_label) in zip(axes, TRACKS):
        data = {}
        for metric in ("IGD", "HV"):
            path = os.path.join(TABLES_DIR,
                                f"nsga_{ivf_algo.lower()}_{metric.lower()}_stats.csv")
            if not os.path.isfile(path):
                continue
            df = pd.read_csv(path)
            counts = df["sign"].value_counts()
            data[metric] = {
                "wins":   counts.get("+", 0),
                "ties":   counts.get("=", 0),
                "losses": counts.get("-", 0),
            }

        metrics = list(data.keys())
        x = np.arange(len(metrics))
        width = 0.25

        for i, (cat, color) in enumerate(COLORS.items()):
            vals = [data[m][cat] for m in metrics]
            bars = ax.bar(x + (i - 1) * width, vals, width,
                          label=cat.capitalize(), color=color, alpha=0.85,
                          edgecolor="white", linewidth=0.5)
            for bar, v in zip(bars, vals):
                if v > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.3, str(v),
                            ha="center", va="bottom", fontsize=8)

        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=11)
        ax.set_ylabel("Problem instances", fontsize=10)
        ax.set_title(f"{ivf_label}\nvs {base_label}", fontsize=11)
        ax.set_ylim(0, 55)
        ax.axhline(52, color="black", linewidth=0.5, linestyle="--", alpha=0.4)
        ax.text(len(metrics) - 0.5, 53, "n=52", ha="right",
                fontsize=8, color="gray")
        ax.legend(fontsize=9, loc="upper right")
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("IVF Operator Benefit: Wins / Ties / Losses vs Base Algorithm\n"
                 "(Wilcoxon rank-sum, BH $\\alpha=0.05$, 30 runs, 52 instances)",
                 fontsize=11)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "nsga_fig1_wintieloss.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out}")


# ────────────────────────────────────────────────────────────────────────────
# Figure 2: Per-problem scatter (median IVF vs median base, log scale)
# ────────────────────────────────────────────────────────────────────────────
def fig_scatter():
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    # axes[row=metric, col=track]

    for col, (ivf_algo, base_algo, ivf_label, base_label) in enumerate(TRACKS):
        for row, metric in enumerate(("IGD", "HV")):
            ax = axes[row, col]
            path = os.path.join(TABLES_DIR,
                                f"nsga_{ivf_algo.lower()}_{metric.lower()}_stats.csv")
            if not os.path.isfile(path):
                ax.set_visible(False)
                continue
            df = pd.read_csv(path)

            groups = df["group"].unique()
            cmap = plt.cm.tab10(np.linspace(0, 0.9, len(groups)))
            gcolor = {g: c for g, c in zip(sorted(groups), cmap)}

            for g in sorted(groups):
                sub = df[df["group"] == g]
                ax.scatter(sub["median_base"], sub["median_ivf"],
                           color=gcolor[g], label=g, alpha=0.8,
                           s=40, zorder=3)

            # Diagonal (equality line)
            all_vals = np.concatenate([df["median_base"].values,
                                       df["median_ivf"].values])
            all_vals = all_vals[all_vals > 0]
            if len(all_vals) == 0:
                continue
            lo, hi = all_vals.min() * 0.5, all_vals.max() * 2
            ax.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, alpha=0.5)

            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(f"{base_label} median {metric}", fontsize=9)
            ax.set_ylabel(f"{ivf_label} median {metric}", fontsize=9)

            # Lower-left annotation for IGD (better = lower), upper-right for HV
            if metric == "IGD":
                ax.text(0.04, 0.96,
                        "IVF wins\n(below diagonal)",
                        transform=ax.transAxes, fontsize=7.5, va="top",
                        color="#2ecc71")
            else:
                ax.text(0.96, 0.04,
                        "IVF wins\n(above diagonal)",
                        transform=ax.transAxes, fontsize=7.5, ha="right",
                        color="#2ecc71")

            ax.set_title(f"{ivf_label} vs {base_label} — {metric}", fontsize=10)
            ax.legend(fontsize=7, loc="lower right" if metric == "IGD" else "upper left",
                      ncol=2, markerscale=0.9)
            ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Per-instance median comparison (log scale)\n"
                 "Points below/above diagonal → IVF wins on IGD/HV",
                 fontsize=11)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "nsga_fig2_scatter.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out}")


# ────────────────────────────────────────────────────────────────────────────
# Figure 3: Relative IGD improvement per benchmark family
# ────────────────────────────────────────────────────────────────────────────
def fig_family_improvement():
    """
    Box plot of relative IGD improvement = (base - ivf) / base per family.
    Positive = IVF improves; negative = IVF hurts.
    """
    df = pd.read_csv(DATA_CSV)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    for ax, (ivf_algo, base_algo, ivf_label, base_label) in zip(axes, TRACKS):
        df_ivf  = df[df["algo"] == ivf_algo]
        df_base = df[df["algo"] == base_algo]

        # Merge on (problem, M, run)
        merged = pd.merge(
            df_ivf [["problem", "M", "group", "run", "IGD"]],
            df_base[["problem", "M", "run", "IGD"]],
            on=["problem", "M", "run"], suffixes=("_ivf", "_base")
        )
        merged["rel_improvement"] = (
            (merged["IGD_base"] - merged["IGD_ivf"]) / merged["IGD_base"]
        )

        families = sorted(merged["group"].unique())
        data_by_family = [
            merged[merged["group"] == g]["rel_improvement"].values
            for g in families
        ]

        bp = ax.boxplot(data_by_family, labels=families, patch_artist=True,
                        medianprops={"color": "black", "linewidth": 1.5},
                        flierprops={"marker": ".", "markersize": 3, "alpha": 0.4})

        for patch, fam in zip(bp["boxes"], families):
            med = np.median(merged[merged["group"] == fam]["rel_improvement"])
            patch.set_facecolor("#2ecc71" if med > 0 else "#e74c3c")
            patch.set_alpha(0.6)

        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_ylabel("Relative IGD improvement  (base − IVF) / base", fontsize=9)
        ax.set_title(f"{ivf_label} vs {base_label}", fontsize=11)
        ax.tick_params(axis="x", labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)

        # Annotate median per family
        for i, fam in enumerate(families):
            med = np.median(merged[merged["group"] == fam]["rel_improvement"])
            ax.text(i + 1, med, f"{med:.2f}",
                    ha="center", va="bottom" if med >= 0 else "top",
                    fontsize=7, color="black")

    fig.suptitle("Relative IGD improvement by benchmark family\n"
                 "Positive = IVF reduces IGD (wins), negative = IVF increases IGD (loses)",
                 fontsize=11)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "nsga_fig3_family.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out}")


if __name__ == "__main__":
    fig_wintieloss()
    fig_scatter()
    fig_family_improvement()
    print("\nAll figures written to", FIG_DIR)
