#!/usr/bin/env python3
"""Generate the v2 main figures for the hosts paper."""

import hashlib
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import TwoSlopeNorm


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")

TRACKS = [
    ("IVFSPEA2", "IVF/SPEA2"),
    ("IVFNSGAIII", "IVF/NSGA-III"),
    ("IVFNSGAII", "IVF/NSGA-II"),
]
GROUP_COLORS = {
    "ZDT": "#0072B2",
    "DTLZ": "#E69F00",
    "WFG": "#009E73",
    "MaF": "#D55E00",
}
M_MARKERS = {2: "o", 3: "^"}


for out_dir in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(out_dir, exist_ok=True)


def save_fig(fig: plt.Figure, name: str) -> None:
    for out_dir in (FIG_DIR, PAPER_FIG_DIR):
        path = os.path.join(out_dir, name)
        fig.savefig(path, bbox_inches="tight", dpi=300)
        print(f"Wrote {path}")


def stable_jitter(*parts: object, width: float = 0.15) -> float:
    key = "|".join(map(str, parts)).encode("utf-8")
    seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "little")
    rng = np.random.default_rng(seed)
    return float(rng.uniform(-width, width))


def load_all_igd_stats() -> pd.DataFrame:
    frames = []
    for algo_key, label in TRACKS:
        path = os.path.join(TABLES_DIR, f"hosts_{algo_key.lower()}_igd_stats.csv")
        df = pd.read_csv(path)
        df["algo"] = algo_key
        df["label"] = label
        df["A12_ivf"] = 1.0 - df["A12"]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def draw_reference_bands(ax: plt.Axes) -> None:
    for lo, hi, alpha in ((0.56, 0.64, 0.06), (0.64, 0.71, 0.08), (0.71, 1.0, 0.10)):
        ax.axhspan(lo, hi, color="#2166ac", alpha=alpha, linewidth=0)
        ax.axhspan(1 - hi, 1 - lo, color="#e74c3c", alpha=alpha, linewidth=0)
    ax.axhline(0.5, color="black", linewidth=0.8, linestyle="--", alpha=0.6)


def fig1_a12_strip(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    draw_reference_bands(ax)

    labels = [label for _, label in TRACKS]
    x_positions = {label: idx for idx, label in enumerate(labels)}
    for _, row in df.iterrows():
        ax.scatter(
            x_positions[row["label"]]
            + stable_jitter(row["problem"], row["M"], row["label"]),
            row["A12_ivf"],
            color=GROUP_COLORS.get(row["group"], "#333333"),
            marker=M_MARKERS.get(row["M"], "o"),
            s=35,
            alpha=0.82,
            edgecolors="white",
            linewidths=0.35,
            zorder=3,
        )

    for _, label in TRACKS:
        sub = df[df["label"] == label]
        med = sub["A12_ivf"].median()
        x = x_positions[label]
        ax.plot(
            [x - 0.25, x + 0.25], [med, med], color="black", linewidth=2.5, zorder=4
        )

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel(r"$A_{12}^{\mathrm{IVF}}$ (oriented, IGD)", fontsize=11)
    ax.set_ylim(-0.02, 1.02)
    ax.spines[["top", "right"]].set_visible(False)

    family_handles = [
        mpatches.Patch(color=color, label=group)
        for group, color in GROUP_COLORS.items()
    ]
    m_handles = [
        plt.Line2D(
            [],
            [],
            color="gray",
            marker=marker,
            linestyle="None",
            markersize=6,
            label=f"M={m_val}",
        )
        for m_val, marker in M_MARKERS.items()
    ]
    ax.legend(
        handles=family_handles + m_handles,
        fontsize=7.5,
        ncol=6,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        framealpha=0.9,
    )

    fig.subplots_adjust(bottom=0.18)
    save_fig(fig, "hosts_v2_fig1_a12_strip.pdf")
    plt.close(fig)


def fig2_heatmap(df: pd.DataFrame) -> None:
    family_order = ["DTLZ", "MaF", "WFG", "ZDT"]
    label_order = [label for _, label in TRACKS]

    ordered = df.copy()
    ordered["family_rank"] = ordered["group"].map(
        {fam: idx for idx, fam in enumerate(family_order)}
    )
    m_values = sorted(ordered["M"].unique())

    fig, axes = plt.subplots(
        nrows=len(m_values),
        ncols=1,
        figsize=(13.8, 3.2 * len(m_values) + 1.0),
        gridspec_kw={"height_ratios": [1.0] * len(m_values)},
    )
    if len(m_values) == 1:
        axes = [axes]

    im = None
    for ax, m_val in zip(axes, m_values):
        sub = ordered[ordered["M"] == m_val]
        instance_order = (
            sub[["problem", "M", "group", "family_rank"]]
            .drop_duplicates()
            .sort_values(["family_rank", "problem"])
        )
        instance_keys = list(zip(instance_order["problem"], instance_order["M"]))
        index = pd.MultiIndex.from_tuples(instance_keys, names=["problem", "M"])

        pivot = sub.pivot_table(
            index=["problem", "M"], columns="label", values="A12_ivf"
        ).reindex(index=index)[label_order]
        sig_pivot = sub.pivot_table(
            index=["problem", "M"], columns="label", values="significant"
        ).reindex(index=index)[label_order]
        group_map = dict(zip(instance_keys, instance_order["group"]))
        col_labels = [problem for problem, _ in instance_keys]
        heat = pivot.values.T
        heat_sig = sig_pivot.values.T

        im = ax.imshow(
            heat,
            aspect="auto",
            cmap=sns.diverging_palette(10, 240, as_cmap=True),
            norm=TwoSlopeNorm(vmin=0.0, vcenter=0.5, vmax=1.0),
            interpolation="nearest",
        )

        for i in range(heat.shape[0]):
            for j in range(heat.shape[1]):
                if bool(heat_sig[i, j]):
                    ax.text(
                        j,
                        i,
                        "*",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        color="black",
                    )

        prev_group = None
        for j, key in enumerate(instance_keys):
            group = group_map[key]
            if prev_group is not None and group != prev_group:
                ax.axvline(j - 0.5, color="black", linewidth=1.0)
            prev_group = group

        family_spans: dict[str, list[int]] = {}
        for j, key in enumerate(instance_keys):
            group = group_map[key]
            if group not in family_spans:
                family_spans[group] = [j, j]
            family_spans[group][1] = j
        for family, (start, end) in family_spans.items():
            mid = (start + end) / 2
            ax.text(
                mid,
                -0.42,
                family,
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=GROUP_COLORS.get(family, "black"),
                transform=ax.get_xaxis_transform(),
                clip_on=False,
            )

        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, fontsize=9, rotation=90)
        ax.set_yticks(range(len(label_order)))
        ax.set_yticklabels(label_order, fontsize=11)
        ax.set_ylabel(f"$M={m_val}$", fontsize=11, fontweight="bold")

    fig.subplots_adjust(hspace=0.95, bottom=0.18, top=0.97)

    cbar = fig.colorbar(
        im,
        ax=axes,
        orientation="horizontal",
        fraction=0.04,
        pad=0.2,
        shrink=0.7,
    )
    cbar.set_label(r"$A_{12}^{\mathrm{IVF}}$", fontsize=11)
    cbar.ax.axvline(0.5, color="black", linewidth=0.8)

    save_fig(fig, "hosts_v2_fig2_heatmap.pdf")
    plt.close(fig)


def fig3_m2_vs_m3(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharey=True)
    label_order = [label for _, label in TRACKS]

    for ax, m_val, title in zip(axes, [2, 3], [r"$M = 2$", r"$M = 3$"]):
        sub = df[df["M"] == m_val]
        draw_reference_bands(ax)

        box_data = [
            sub[sub["label"] == label]["A12_ivf"].to_numpy() for label in label_order
        ]
        ax.boxplot(
            box_data,
            positions=range(len(label_order)),
            widths=0.5,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "black", "linewidth": 2},
            boxprops={"facecolor": "#cccccc", "alpha": 0.4},
        )

        for idx, label in enumerate(label_order):
            lsub = sub[sub["label"] == label]
            for _, row in lsub.iterrows():
                ax.scatter(
                    idx + stable_jitter(row["problem"], row["M"], row["label"], m_val),
                    row["A12_ivf"],
                    color=GROUP_COLORS.get(row["group"], "#333333"),
                    s=30,
                    alpha=0.82,
                    edgecolors="white",
                    linewidths=0.35,
                    zorder=3,
                )

        ax.set_xticks(range(len(label_order)))
        ax.set_xticklabels(label_order, fontsize=10)
        ax.set_title(title, fontsize=12)
        ax.set_ylim(-0.02, 1.02)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel(r"$A_{12}^{\mathrm{IVF}}$ (oriented, IGD)", fontsize=11)
    axes[1].legend(
        handles=[
            mpatches.Patch(color=color, label=group)
            for group, color in GROUP_COLORS.items()
        ],
        fontsize=8,
        loc="lower left",
        framealpha=0.9,
    )

    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig3_m2_vs_m3.pdf")
    plt.close(fig)


def main() -> None:
    print("=== Generating hosts paper figures v2 ===\n")
    df = load_all_igd_stats()
    print(f"Loaded {len(df)} rows across {df['algo'].nunique()} tracks\n")
    fig1_a12_strip(df)
    fig2_heatmap(df)
    fig3_m2_vs_m3(df)
    print("\nAll v2 figures written.")


if __name__ == "__main__":
    main()
