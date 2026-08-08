#!/usr/bin/env python3
"""Generate convergence figures for the hosts paper.

Fig 4 — IGD ratio (base / IVF) over FE for 6 representative instances.
Fig 5 — ECDF of runtime (COCO-style): fraction of targets solved vs budget.
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
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")

# Each host pair: (IVF algo, base algo, color, label)
HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2", "#4c72b0", "IVF/SPEA2"),
    ("IVFNSGAIII", "NSGAIII", "#55a868", "IVF/NSGA-III"),
    ("IVFNSGAII", "NSGAII", "#c44e52", "IVF/NSGA-II"),
]

# All 6 algorithms for the ECDF
ALGO_STYLES = {
    "IVFSPEA2":   {"color": "#4c72b0", "ls": "-",  "lw": 2.5, "label": "IVF/SPEA2"},
    "SPEA2":      {"color": "#4c72b0", "ls": "--", "lw": 1.5, "label": "SPEA2"},
    "IVFNSGAIII": {"color": "#55a868", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-III"},
    "NSGAIII":    {"color": "#55a868", "ls": "--", "lw": 1.5, "label": "NSGA-III"},
    "IVFNSGAII":  {"color": "#c44e52", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-II"},
    "NSGAII":     {"color": "#c44e52", "ls": "--", "lw": 1.5, "label": "NSGA-II"},
}

MAX_FE = 100_000

for out_dir in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(out_dir, exist_ok=True)


def save_fig(fig: plt.Figure, name: str) -> None:
    for out_dir in (FIG_DIR, PAPER_FIG_DIR):
        path = os.path.join(out_dir, name)
        fig.savefig(path, bbox_inches="tight", dpi=300)
        print(f"  Wrote {path}")


def compute_ratio_stats(
    df: pd.DataFrame, ivf_algo: str, base_algo: str, prob: str, m_val: int
) -> pd.DataFrame | None:
    """Compute median ratio IGD_base / IGD_IVF per FE, with IQR."""
    ivf = df[(df["algo"] == ivf_algo) & (df["problem"] == prob) & (df["M"] == m_val)]
    base = df[(df["algo"] == base_algo) & (df["problem"] == prob) & (df["M"] == m_val)]

    if ivf.empty or base.empty:
        return None

    # Compute per-run ratios by matching (run, FE)
    merged = base.merge(ivf, on=["run", "FE"], suffixes=("_base", "_ivf"))
    # Guard against division by zero
    merged = merged[merged["IGD_ivf"] > 0]
    merged["ratio"] = merged["IGD_base"] / merged["IGD_ivf"]

    stats = (
        merged.groupby("FE")["ratio"]
        .agg(
            median="median",
            q25=lambda x: x.quantile(0.25),
            q75=lambda x: x.quantile(0.75),
        )
        .sort_index()
    )

    # Skip the very first checkpoint (extreme transient)
    if len(stats) > 2:
        stats = stats.iloc[1:]

    # Smooth with rolling median (window=5) to reduce noise from small IGD divisions
    for col in ["median", "q25", "q75"]:
        stats[col] = stats[col].rolling(5, min_periods=1, center=True).median()

    return stats


def fig5_ecdf(df: pd.DataFrame, instances: pd.DataFrame) -> None:
    """ECDF of runtime (COCO-style).

    For multiple IGD target thresholds per instance, plot the fraction of
    (instance, target, run) triples solved as a function of budget fraction.
    The gap between solid (IVF) and dashed (base) lines of each color
    directly shows the IVF benefit.
    """
    # Define target multipliers of each instance's best-known final IGD
    target_multipliers = np.array([100, 50, 20, 10, 5, 3, 2, 1.5, 1.2, 1.0])

    # Precompute targets per instance
    instance_targets = []
    for _, inst in instances.iterrows():
        prob, m_val = inst["problem"], int(inst["M"])
        sub = df[(df["problem"] == prob) & (df["M"] == m_val)]
        best_igd = sub.groupby(["algo", "run"])["IGD"].last().min()
        if best_igd <= 0:
            continue
        for mult in target_multipliers:
            instance_targets.append((prob, m_val, best_igd * mult))

    n_targets = len(instance_targets)
    if n_targets == 0:
        print("  No targets found, skipping ECDF")
        return

    # Precompute per-algo minimum IGD reached at each FE (vectorized)
    fe_grid = np.linspace(1000, MAX_FE, 100)
    algo_names = list(ALGO_STYLES.keys())

    # Build lookup: for each (algo, problem, M, run), store the cumulative
    # minimum IGD at each FE checkpoint
    print("  Precomputing cumulative minima...")
    cummin_cache: dict[tuple, pd.Series] = {}
    for algo in algo_names:
        for _, inst in instances.iterrows():
            prob, m_val = inst["problem"], int(inst["M"])
            sub = df[
                (df["algo"] == algo) & (df["problem"] == prob) & (df["M"] == m_val)
            ]
            for run_id, run_data in sub.groupby("run"):
                sorted_run = run_data.sort_values("FE")
                cummin = sorted_run.set_index("FE")["IGD"].cummin()
                cummin_cache[(algo, prob, m_val, run_id)] = cummin

    # Compute ECDF for each algorithm
    print("  Computing ECDF curves...")
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for algo in algo_names:
        style = ALGO_STYLES[algo]
        fractions = []

        for fe_val in fe_grid:
            solved = 0
            total = 0
            for prob, m_val, target in instance_targets:
                # Find all runs for this (algo, prob, m_val)
                for key, cummin in cummin_cache.items():
                    if key[0] != algo or key[1] != prob or key[2] != m_val:
                        continue
                    total += 1
                    # Check if cummin at or before fe_val is <= target
                    valid = cummin[cummin.index <= fe_val]
                    if not valid.empty and valid.iloc[-1] <= target:
                        solved += 1

            fractions.append(solved / total if total > 0 else 0)

        ax.plot(
            fe_grid / MAX_FE, fractions,
            color=style["color"], linestyle=style["ls"],
            linewidth=style["lw"], label=style["label"],
        )

    ax.set_xlabel("FE / max FE", fontsize=11)
    ax.set_ylabel("Fraction of targets solved", fontsize=11)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=9, loc="lower right", framealpha=0.95)

    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig5_ecdf.pdf")
    plt.close(fig)


def main() -> None:
    print("=== Generating convergence figures ===\n")
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")

    n_inst = len(instances)
    ncols = 3
    nrows = (n_inst + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.2 * nrows), squeeze=False)

    for idx, (_, inst) in enumerate(instances.iterrows()):
        row, col = divmod(idx, ncols)
        ax = axes[row][col]
        prob = inst["problem"]
        m_val = int(inst["M"])

        # Reference line at 1.0 (neutral)
        ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

        for ivf_algo, base_algo, color, label in HOST_PAIRS:
            stats = compute_ratio_stats(df, ivf_algo, base_algo, prob, m_val)
            if stats is None:
                continue

            fe_norm = stats.index / MAX_FE

            ax.plot(
                fe_norm,
                stats["median"],
                color=color,
                linewidth=2.0,
                label=label,
            )
            ax.fill_between(
                fe_norm,
                stats["q25"],
                stats["q75"],
                color=color,
                alpha=0.15,
            )

        ax.set_title(f"{prob} ($M={m_val}$)", fontsize=11, fontweight="bold")
        ax.set_xlabel("FE / max FE", fontsize=9)
        if col == 0:
            ax.set_ylabel("IGD ratio (base / IVF)", fontsize=9)
        ax.set_xlim(0, 1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)

        # Shade above/below 1.0 within the data range
        ylims = ax.get_ylim()
        ax.axhspan(1.0, ylims[1], color="#2ecc71", alpha=0.05, zorder=0)
        ax.axhspan(ylims[0], 1.0, color="#e74c3c", alpha=0.05, zorder=0)
        ax.set_ylim(ylims)

    # Hide unused panels
    for idx in range(n_inst, nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row][col].set_visible(False)

    # Shared legend
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=3,
        fontsize=10,
        bbox_to_anchor=(0.5, -0.01),
        frameon=True,
        edgecolor="0.8",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save_fig(fig, "hosts_v2_fig4_convergence.pdf")
    plt.close(fig)
    print()

    print("Generating Fig 5: ECDF of runtime...")
    fig5_ecdf(df, instances)

    print("\nAll convergence figures written.")


if __name__ == "__main__":
    main()
