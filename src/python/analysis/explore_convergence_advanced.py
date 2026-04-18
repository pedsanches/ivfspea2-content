#!/usr/bin/env python3
"""Advanced convergence visualizations for the hosts paper.

Generates two candidate figures:
  1. ΔECDF — difference in ECDF between IVF and base per host
  2. Dominance evolution — fraction of runs where IVF wins, per host over FE
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

ALGO_STYLES = {
    "IVFSPEA2":   {"color": "#4c72b0", "ls": "-",  "lw": 2.5, "label": "IVF/SPEA2"},
    "SPEA2":      {"color": "#4c72b0", "ls": "--", "lw": 1.5, "label": "SPEA2"},
    "IVFNSGAIII": {"color": "#55a868", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-III"},
    "NSGAIII":    {"color": "#55a868", "ls": "--", "lw": 1.5, "label": "NSGA-III"},
    "IVFNSGAII":  {"color": "#c44e52", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-II"},
    "NSGAII":     {"color": "#c44e52", "ls": "--", "lw": 1.5, "label": "NSGA-II"},
}

MAX_FE = 100_000

os.makedirs(FIG_DIR, exist_ok=True)


def load_data():
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")
    return df, instances


# ---------------------------------------------------------------------------
# Figure 1: ΔECDF
# ---------------------------------------------------------------------------

def fig_delta_ecdf(df, instances):
    """Plot ECDF_IVF - ECDF_base for each host pair.

    Positive values = IVF solves more targets at that budget fraction.
    """
    target_multipliers = np.array([100, 50, 20, 10, 5, 3, 2, 1.5, 1.2, 1.0])

    # Build targets per instance
    instance_targets = []
    for _, inst in instances.iterrows():
        prob, m_val = inst["problem"], int(inst["M"])
        sub = df[(df["problem"] == prob) & (df["M"] == m_val)]
        best_igd = sub.groupby(["algo", "run"])["IGD"].last().min()
        if best_igd <= 0:
            continue
        for mult in target_multipliers:
            instance_targets.append((prob, m_val, best_igd * mult))

    # Precompute cumulative minima
    print("  Precomputing cumulative minima...")
    cummin_cache = {}
    all_algos = set()
    for ivf, base, _, _ in HOST_PAIRS:
        all_algos.add(ivf)
        all_algos.add(base)

    for algo in all_algos:
        for _, inst in instances.iterrows():
            prob, m_val = inst["problem"], int(inst["M"])
            sub = df[
                (df["algo"] == algo) & (df["problem"] == prob) & (df["M"] == m_val)
            ]
            for run_id, run_data in sub.groupby("run"):
                sorted_run = run_data.sort_values("FE")
                cummin = sorted_run.set_index("FE")["IGD"].cummin()
                cummin_cache[(algo, prob, m_val, run_id)] = cummin

    def compute_ecdf(algo, fe_grid):
        fractions = []
        for fe_val in fe_grid:
            solved = 0
            total = 0
            for prob, m_val, target in instance_targets:
                for key, cummin in cummin_cache.items():
                    if key[0] != algo or key[1] != prob or key[2] != m_val:
                        continue
                    total += 1
                    valid = cummin[cummin.index <= fe_val]
                    if not valid.empty and valid.iloc[-1] <= target:
                        solved += 1
            fractions.append(solved / total if total > 0 else 0)
        return np.array(fractions)

    fe_grid = np.linspace(1000, MAX_FE, 100)
    fe_norm = fe_grid / MAX_FE

    print("  Computing ECDF curves for each algorithm...")
    ecdf_cache = {}
    for algo in all_algos:
        print(f"    {algo}...")
        ecdf_cache[algo] = compute_ecdf(algo, fe_grid)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhspan(0, 0.5, color="#2ecc71", alpha=0.04, zorder=0)
    ax.axhspan(-0.5, 0, color="#e74c3c", alpha=0.04, zorder=0)

    for ivf_algo, base_algo, color, label in HOST_PAIRS:
        delta = ecdf_cache[ivf_algo] - ecdf_cache[base_algo]

        ax.plot(fe_norm, delta, color=color, linewidth=2.5, label=label)
        ax.fill_between(fe_norm, 0, delta, color=color, alpha=0.12)

    ax.set_xlabel("FE / max FE", fontsize=11)
    ax.set_ylabel("$\\Delta$ECDF  (IVF $-$ base)", fontsize=11)
    ax.set_xlim(0, 1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=10, loc="upper right", framealpha=0.95)

    fig.tight_layout()
    path = os.path.join(FIG_DIR, "explore_delta_ecdf.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"  Wrote {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2: Dominance Evolution
# ---------------------------------------------------------------------------

def fig_dominance_evolution(df, instances):
    """For each host pair and FE checkpoint, compute the fraction of
    (instance, run) pairs where IGD_IVF < IGD_base.

    Values > 0.5 = IVF wins more often than it loses.
    """
    fe_checkpoints = sorted(df["FE"].unique())

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.axhline(0.5, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhspan(0.5, 1.0, color="#2ecc71", alpha=0.04, zorder=0)
    ax.axhspan(0.0, 0.5, color="#e74c3c", alpha=0.04, zorder=0)

    for ivf_algo, base_algo, color, label in HOST_PAIRS:
        win_fractions = []

        for fe_val in fe_checkpoints:
            wins = 0
            total = 0

            for _, inst in instances.iterrows():
                prob, m_val = inst["problem"], int(inst["M"])

                ivf_sub = df[
                    (df["algo"] == ivf_algo) & (df["problem"] == prob) &
                    (df["M"] == m_val) & (df["FE"] == fe_val)
                ]
                base_sub = df[
                    (df["algo"] == base_algo) & (df["problem"] == prob) &
                    (df["M"] == m_val) & (df["FE"] == fe_val)
                ]

                if ivf_sub.empty or base_sub.empty:
                    continue

                # Match by run
                merged = ivf_sub.merge(
                    base_sub, on="run", suffixes=("_ivf", "_base")
                )

                for _, row in merged.iterrows():
                    total += 1
                    if row["IGD_ivf"] < row["IGD_base"]:
                        wins += 1

            win_fractions.append(wins / total if total > 0 else 0.5)

        fe_norm = np.array(fe_checkpoints) / MAX_FE

        # Smooth slightly for readability
        win_arr = pd.Series(win_fractions).rolling(3, min_periods=1, center=True).mean().values

        ax.plot(fe_norm, win_arr, color=color, linewidth=2.5, label=label)
        ax.fill_between(fe_norm, 0.5, win_arr, color=color, alpha=0.12)

    ax.set_xlabel("FE / max FE", fontsize=11)
    ax.set_ylabel("Fraction of runs where IVF wins", fontsize=11)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=10, loc="lower right", framealpha=0.95)

    # Add annotations
    ax.text(0.95, 0.52, "IVF wins", ha="right", va="bottom", fontsize=8,
            color="#27ae60", alpha=0.7)
    ax.text(0.95, 0.48, "base wins", ha="right", va="top", fontsize=8,
            color="#c0392b", alpha=0.7)

    fig.tight_layout()
    path = os.path.join(FIG_DIR, "explore_dominance_evolution.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"  Wrote {path}")
    plt.close(fig)


def main():
    print("=== Advanced convergence visualizations ===\n")
    df, instances = load_data()
    print(f"Loaded {len(df)} rows, {len(instances)} instances\n")

    print("Generating ΔECDF...")
    fig_delta_ecdf(df, instances)

    print("\nGenerating Dominance Evolution...")
    fig_dominance_evolution(df, instances)

    print("\nAll advanced figures written to results/figures/explore_*.pdf")


if __name__ == "__main__":
    main()
