#!/usr/bin/env python3
"""Dominance evolution faceted by host.

One panel per host pair. Each instance is a thin line showing the fraction
of runs where IVF wins at each FE checkpoint. A thick line shows the
median across instances.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONV_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")
INST_CSV = os.path.join(
    PROJECT_ROOT, "results", "tables", "hosts_convergence_instances.csv"
)
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2", "#4c72b0", "IVF/SPEA2"),
    ("IVFNSGAIII", "NSGAIII", "#55a868", "IVF/NSGA-III"),
    ("IVFNSGAII", "NSGAII", "#c44e52", "IVF/NSGA-II"),
]

INSTANCE_MARKERS = ["o", "s", "^", "D", "v", "P"]

MAX_FE = 100_000

os.makedirs(FIG_DIR, exist_ok=True)


def compute_win_fraction_per_instance(df, ivf_algo, base_algo, prob, m_val, fe_checkpoints):
    """Compute fraction of runs where IGD_IVF < IGD_base at each FE."""
    fractions = []
    for fe_val in fe_checkpoints:
        ivf_sub = df[
            (df["algo"] == ivf_algo) & (df["problem"] == prob) &
            (df["M"] == m_val) & (df["FE"] == fe_val)
        ]
        base_sub = df[
            (df["algo"] == base_algo) & (df["problem"] == prob) &
            (df["M"] == m_val) & (df["FE"] == fe_val)
        ]
        if ivf_sub.empty or base_sub.empty:
            fractions.append(np.nan)
            continue

        merged = ivf_sub.merge(base_sub, on="run", suffixes=("_ivf", "_base"))
        if merged.empty:
            fractions.append(np.nan)
            continue

        wins = (merged["IGD_ivf"] < merged["IGD_base"]).sum()
        fractions.append(wins / len(merged))

    return np.array(fractions)


def main():
    print("=== Dominance evolution by host ===\n")
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")
    fe_checkpoints = sorted(df["FE"].unique())
    fe_norm = np.array(fe_checkpoints) / MAX_FE

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)

    for ax, (ivf_algo, base_algo, color, host_label) in zip(axes, HOST_PAIRS):
        # Reference line
        ax.axhline(0.5, color="black", linewidth=0.8, linestyle="--", alpha=0.4)
        ax.axhspan(0.5, 1.0, color="#2ecc71", alpha=0.04, zorder=0)
        ax.axhspan(0.0, 0.5, color="#e74c3c", alpha=0.04, zorder=0)

        all_fracs = []

        for i, (_, inst) in enumerate(instances.iterrows()):
            prob, m_val = inst["problem"], int(inst["M"])
            inst_label = f"{prob} M={m_val}"

            fracs = compute_win_fraction_per_instance(
                df, ivf_algo, base_algo, prob, m_val, fe_checkpoints
            )

            # Smooth for readability
            fracs_smooth = pd.Series(fracs).rolling(
                5, min_periods=1, center=True
            ).mean().values

            ax.plot(
                fe_norm, fracs_smooth,
                color=color, linewidth=1.0, alpha=0.45,
                label=inst_label if ax == axes[0] else None,
            )

            # Endpoint marker
            valid_idx = ~np.isnan(fracs_smooth)
            if valid_idx.any():
                last_idx = np.where(valid_idx)[0][-1]
                ax.scatter(
                    fe_norm[last_idx], fracs_smooth[last_idx],
                    color=color, marker=INSTANCE_MARKERS[i % len(INSTANCE_MARKERS)],
                    s=30, alpha=0.7, edgecolors="white", linewidths=0.5, zorder=4,
                )

            all_fracs.append(fracs)

        # Median across instances (thick line)
        all_fracs_arr = np.array(all_fracs)
        median_frac = np.nanmedian(all_fracs_arr, axis=0)
        median_smooth = pd.Series(median_frac).rolling(
            5, min_periods=1, center=True
        ).mean().values

        ax.plot(
            fe_norm, median_smooth,
            color=color, linewidth=3.0, alpha=0.9, zorder=5,
        )

        ax.set_title(host_label, fontsize=12, fontweight="bold", color=color)
        ax.set_xlabel("FE / max FE", fontsize=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)

    axes[0].set_ylabel("Fraction of runs won by IVF", fontsize=10)

    # Instance legend from first panel
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(
            handles, labels,
            loc="lower center", ncol=6, fontsize=7.5,
            bbox_to_anchor=(0.5, -0.06), frameon=True, edgecolor="0.8",
        )

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    path = os.path.join(FIG_DIR, "explore_dominance_by_host.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"Wrote {path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
