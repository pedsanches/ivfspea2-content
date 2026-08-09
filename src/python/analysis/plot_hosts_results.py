#!/usr/bin/env python3
"""
Figures for the IVF host-comparison paper.

Reads:  results/tables/hosts_*_stats.csv
        results/tables/hosts_cross_host_ivf_{metric}.csv
        data/processed/hosts_paper.csv
Writes: results/figures/hosts_fig1_wintieloss.pdf
        results/figures/hosts_fig2_scatter.pdf
        results/figures/hosts_fig3_family.pdf
        results/figures/hosts_fig4_cross_host_ivf.pdf
        paper/ppsn2026-ivf-hosts/figures/hosts_fig*.pdf
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figure_io import save_figure as _save_figure

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
DATA_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_paper.csv")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")

TRACKS = [
    ("IVFSPEA2", "SPEA2", "IVF/SPEA2", "SPEA2"),
    ("IVFNSGAII", "NSGAII", "IVF/NSGA-II", "NSGA-II"),
    ("IVFNSGAIII", "NSGAIII", "IVF/NSGA-III", "NSGA-III"),
]

IVF_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "IVFNSGAII": "IVF/NSGA-II",
    "IVFNSGAIII": "IVF/NSGA-III",
}

COLORS = {"wins": "#2ecc71", "ties": "#95a5a6", "losses": "#e74c3c"}
GROUP_COLORS = {
    "ZDT": "#1f77b4",
    "DTLZ": "#ff7f0e",
    "WFG": "#2ca02c",
    "MaF": "#d62728",
}

for out_dir in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(out_dir, exist_ok=True)


def save_figure(fig: plt.Figure, filename: str) -> None:
    _save_figure(fig, filename, (FIG_DIR, PAPER_FIG_DIR), dpi=None)


def align_paired_runs(ivf_sub: pd.DataFrame, base_sub: pd.DataFrame) -> pd.DataFrame:
    """Align paired samples by sorted run order within each instance."""
    ivf_sorted = ivf_sub.sort_values("run").reset_index(drop=True)
    base_sorted = base_sub.sort_values("run").reset_index(drop=True)
    n = min(len(ivf_sorted), len(base_sorted))
    if n == 0:
        return pd.DataFrame()
    return pd.DataFrame(
        {
            "pair_order": np.arange(n, dtype=int),
            "problem": ivf_sorted.loc[: n - 1, "problem"].to_numpy(),
            "M": ivf_sorted.loc[: n - 1, "M"].to_numpy(),
            "group": ivf_sorted.loc[: n - 1, "group"].to_numpy(),
            "IGD_ivf": ivf_sorted.loc[: n - 1, "IGD"].to_numpy(dtype=float),
            "IGD_base": base_sorted.loc[: n - 1, "IGD"].to_numpy(dtype=float),
        }
    )


def fig_wintieloss() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)

    for ax, (ivf_algo, _, ivf_label, base_label) in zip(axes, TRACKS):
        data = {}
        for metric in ("IGD", "HV"):
            path = os.path.join(
                TABLES_DIR, f"hosts_{ivf_algo.lower()}_{metric.lower()}_stats.csv"
            )
            if not os.path.isfile(path):
                continue
            df = pd.read_csv(path)
            counts = df["sign"].value_counts()
            data[metric] = {
                "wins": counts.get("+", 0),
                "ties": counts.get("=", 0),
                "losses": counts.get("-", 0),
            }

        metrics = list(data.keys())
        n_instances = max(
            (sum(data[m].values()) for m in metrics),
            default=0,
        )
        x = np.arange(len(metrics))
        width = 0.25
        for i, (cat, color) in enumerate(COLORS.items()):
            vals = [data[m][cat] for m in metrics]
            bars = ax.bar(
                x + (i - 1) * width,
                vals,
                width,
                label=cat.capitalize(),
                color=color,
                alpha=0.9,
                edgecolor="white",
                linewidth=0.5,
            )
            for bar, value in zip(bars, vals):
                if value > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.3,
                        str(value),
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=11)
        ax.set_ylabel("Problem instances", fontsize=10)
        ax.set_title(f"{ivf_label}\nvs {base_label}", fontsize=11)
        ax.set_ylim(0, max(n_instances + 3, 10))
        ax.axhline(
            n_instances, color="black", linewidth=0.6, linestyle="--", alpha=0.4
        )
        ax.text(
            len(metrics) - 0.5,
            n_instances + 0.8,
            f"n={n_instances}",
            ha="right",
            fontsize=8,
            color="gray",
        )
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].legend(fontsize=9, loc="upper right")
    fig.suptitle(
        "IVF benefit by host: wins / ties / losses vs base algorithm\n"
        "Wilcoxon signed-rank with BH correction, paired by run order, 30 runs, 51 instances per track",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    save_figure(fig, "hosts_fig1_wintieloss.pdf")
    plt.close(fig)


def fig_scatter() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))

    for col, (ivf_algo, _, ivf_label, base_label) in enumerate(TRACKS):
        for row, metric in enumerate(("IGD", "HV")):
            ax = axes[row, col]
            path = os.path.join(
                TABLES_DIR, f"hosts_{ivf_algo.lower()}_{metric.lower()}_stats.csv"
            )
            if not os.path.isfile(path):
                ax.set_visible(False)
                continue

            df = pd.read_csv(path)
            groups = sorted(df["group"].unique())
            for group in groups:
                sub = df[df["group"] == group]
                ax.scatter(
                    sub["median_base"],
                    sub["median_ivf"],
                    color=GROUP_COLORS.get(group, "#333333"),
                    label=group,
                    alpha=0.85,
                    s=40,
                    zorder=3,
                )

            all_vals = np.concatenate(
                [df["median_base"].to_numpy(), df["median_ivf"].to_numpy()]
            )
            all_vals = all_vals[all_vals > 0]
            if len(all_vals) == 0:
                ax.set_visible(False)
                continue
            lo, hi = all_vals.min() * 0.5, all_vals.max() * 2.0
            ax.plot([lo, hi], [lo, hi], "k--", linewidth=0.8, alpha=0.5)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(f"{base_label} median {metric}", fontsize=9)
            ax.set_ylabel(f"{ivf_label} median {metric}", fontsize=9)
            ax.set_title(f"{ivf_label} vs {base_label} - {metric}", fontsize=10)
            if metric == "IGD":
                ax.text(
                    0.04,
                    0.96,
                    "IVF wins\nbelow diagonal",
                    transform=ax.transAxes,
                    va="top",
                    fontsize=7.5,
                )
            else:
                ax.text(
                    0.96,
                    0.04,
                    "IVF wins\nabove diagonal",
                    transform=ax.transAxes,
                    ha="right",
                    fontsize=7.5,
                )
            ax.spines[["top", "right"]].set_visible(False)
            if row == 0:
                ax.legend(fontsize=7, loc="lower right", ncol=2, markerscale=0.9)

    fig.suptitle("Per-instance median comparison across the three hosts", fontsize=11)
    plt.tight_layout()
    save_figure(fig, "hosts_fig2_scatter.pdf")
    plt.close(fig)


def fig_family_improvement() -> None:
    df = pd.read_csv(DATA_CSV)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

    for ax, (ivf_algo, base_algo, ivf_label, base_label) in zip(axes, TRACKS):
        df_ivf = df[df["algo"] == ivf_algo]
        df_base = df[df["algo"] == base_algo]
        merged_parts = []
        for (problem, m_val), ivf_inst in df_ivf.groupby(["problem", "M"]):
            base_inst = df_base[
                (df_base["problem"] == problem) & (df_base["M"] == m_val)
            ]
            paired = align_paired_runs(
                ivf_inst[["problem", "M", "group", "run", "IGD"]],
                base_inst[["problem", "M", "group", "run", "IGD"]],
            )
            if not paired.empty:
                merged_parts.append(paired)
        merged = (
            pd.concat(merged_parts, ignore_index=True)
            if merged_parts
            else pd.DataFrame()
        )
        if merged.empty:
            ax.set_visible(False)
            continue
        merged["rel_improvement"] = (merged["IGD_base"] - merged["IGD_ivf"]) / merged[
            "IGD_base"
        ]

        families = sorted(merged["group"].unique())
        data_by_family = [
            merged[merged["group"] == fam]["rel_improvement"].to_numpy()
            for fam in families
        ]
        bp = ax.boxplot(
            data_by_family,
            tick_labels=families,
            patch_artist=True,
            medianprops={"color": "black", "linewidth": 1.5},
            showfliers=False,
        )
        for patch, fam in zip(bp["boxes"], families):
            med = np.median(merged[merged["group"] == fam]["rel_improvement"])
            patch.set_facecolor("#2ecc71" if med > 0 else "#e74c3c")
            patch.set_alpha(0.65)

        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_ylabel("Relative IGD improvement  (base - IVF) / base", fontsize=9)
        ax.set_title(f"{ivf_label} vs {base_label}", fontsize=11)
        ax.tick_params(axis="x", labelsize=9)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Relative IGD improvement by benchmark family and host", fontsize=11)
    plt.tight_layout()
    save_figure(fig, "hosts_fig3_family.pdf")
    plt.close(fig)


def fig_family_improvement_by_m() -> None:
    df = pd.read_csv(DATA_CSV)
    m_values = sorted(df["M"].unique())
    fig, axes = plt.subplots(
        len(m_values), 3, figsize=(15, 5 * len(m_values)), sharey="row"
    )
    if len(m_values) == 1:
        axes = axes[np.newaxis, :]

    for row, m_val in enumerate(m_values):
        df_m = df[df["M"] == m_val]
        for col, (ivf_algo, base_algo, ivf_label, base_label) in enumerate(TRACKS):
            ax = axes[row, col]
            df_ivf = df_m[df_m["algo"] == ivf_algo]
            df_base = df_m[df_m["algo"] == base_algo]
            merged_parts = []
            for problem, ivf_inst in df_ivf.groupby("problem"):
                base_inst = df_base[df_base["problem"] == problem]
                paired = align_paired_runs(
                    ivf_inst[["problem", "M", "group", "run", "IGD"]],
                    base_inst[["problem", "M", "group", "run", "IGD"]],
                )
                if not paired.empty:
                    merged_parts.append(paired)
            merged = (
                pd.concat(merged_parts, ignore_index=True)
                if merged_parts
                else pd.DataFrame()
            )
            if merged.empty:
                ax.set_visible(False)
                continue
            merged["rel_improvement"] = (
                merged["IGD_base"] - merged["IGD_ivf"]
            ) / merged["IGD_base"]

            families = sorted(merged["group"].unique())
            data_by_family = [
                merged[merged["group"] == fam]["rel_improvement"].to_numpy()
                for fam in families
            ]
            bp = ax.boxplot(
                data_by_family,
                tick_labels=families,
                patch_artist=True,
                medianprops={"color": "black", "linewidth": 1.5},
                showfliers=False,
            )
            for patch, fam in zip(bp["boxes"], families):
                med = np.median(
                    merged[merged["group"] == fam]["rel_improvement"]
                )
                patch.set_facecolor("#2ecc71" if med > 0 else "#e74c3c")
                patch.set_alpha(0.65)

            ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
            if col == 0:
                ax.set_ylabel(
                    "Relative IGD improvement\n(base − IVF) / base", fontsize=9
                )
            ax.set_title(f"{ivf_label} vs {base_label}  (M={m_val})", fontsize=11)
            ax.tick_params(axis="x", labelsize=9)
            ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Relative IGD improvement by benchmark family, host, and number of objectives",
        fontsize=12,
    )
    plt.tight_layout()
    save_figure(fig, "hosts_fig3b_family_by_m.pdf")
    plt.close(fig)


def fig_cross_host_ivf() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, metric in zip(axes, ("igd", "hv")):
        path = os.path.join(TABLES_DIR, f"hosts_cross_host_ivf_{metric}.csv")
        if not os.path.isfile(path):
            ax.set_visible(False)
            continue
        df = pd.read_csv(path)
        summary = (
            df.groupby(["algo_label"])
            .agg(best_count=("is_best", "sum"), mean_rank=("rank", "mean"))
            .reset_index()
            .sort_values(["mean_rank", "algo_label"])
        )
        x = np.arange(len(summary))
        bars = ax.bar(
            x,
            summary["best_count"],
            color=["#4c72b0", "#55a868", "#c44e52"][: len(summary)],
        )
        for idx, (_, row) in enumerate(summary.iterrows()):
            ax.text(
                idx,
                row["best_count"] + 0.6,
                f"rank={row['mean_rank']:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(summary["algo_label"], rotation=15)
        ax.set_ylim(0, max(summary["best_count"].max() + 5, 10))
        ax.set_ylabel("Instances with best absolute median", fontsize=9)
        ax.set_title(metric.upper(), fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Cross-host absolute ranking among IVF variants", fontsize=11)
    plt.tight_layout()
    save_figure(fig, "hosts_fig4_cross_host_ivf.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_wintieloss()
    fig_scatter()
    fig_family_improvement()
    fig_family_improvement_by_m()
    fig_cross_host_ivf()
    print("\nAll figures written to", FIG_DIR)
