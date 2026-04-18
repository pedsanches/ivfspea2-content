#!/usr/bin/env python3
"""Explore convergence visualization alternatives for the hosts paper.

Generates three candidate figures side by side:
  1. AUC ratio strip plot
  2. Speedup strip plot
  3. ECDF of runtime (COCO-style)

All read from the same hosts_convergence.csv data.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import integrate


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

MAX_FE = 100_000

os.makedirs(FIG_DIR, exist_ok=True)


def load_data():
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")
    return df, instances


# ---------------------------------------------------------------------------
# Metric 1: AUC ratio
# ---------------------------------------------------------------------------

def compute_auc_ratio(df, ivf_algo, base_algo, prob, m_val):
    """Compute AUC_base / AUC_IVF for a single (host, instance) pair.

    AUC is the area under the median IGD convergence curve.
    Ratio > 1 means IVF converged better overall.
    Returns median ratio across runs, plus per-run ratios for strip plot.
    """
    ivf = df[(df["algo"] == ivf_algo) & (df["problem"] == prob) & (df["M"] == m_val)]
    base = df[(df["algo"] == base_algo) & (df["problem"] == prob) & (df["M"] == m_val)]

    if ivf.empty or base.empty:
        return None

    # Per-run AUC using trapezoidal integration
    ratios = []
    for run_id in ivf["run"].unique():
        ivf_run = ivf[ivf["run"] == run_id].sort_values("FE")
        base_run = base[base["run"] == run_id].sort_values("FE")

        if len(ivf_run) < 2 or len(base_run) < 2:
            continue

        auc_ivf = np.trapz(ivf_run["IGD"].values, ivf_run["FE"].values)
        auc_base = np.trapz(base_run["IGD"].values, base_run["FE"].values)

        if auc_ivf > 0:
            ratios.append(auc_base / auc_ivf)

    return ratios if ratios else None


def fig_auc_ratio(df, instances):
    """Strip plot of AUC ratio per instance, grouped by host."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhspan(1.0, 10, color="#2ecc71", alpha=0.04, zorder=0)
    ax.axhspan(0, 1.0, color="#e74c3c", alpha=0.04, zorder=0)

    labels = [l for _, _, _, l in HOST_PAIRS]
    x_positions = {l: i for i, l in enumerate(labels)}

    for ivf_algo, base_algo, color, label in HOST_PAIRS:
        x_base = x_positions[label]
        for _, inst in instances.iterrows():
            ratios = compute_auc_ratio(df, ivf_algo, base_algo,
                                       inst["problem"], int(inst["M"]))
            if ratios is None:
                continue

            median_ratio = np.median(ratios)
            q25, q75 = np.percentile(ratios, [25, 75])

            jitter = np.random.default_rng(
                hash(f"{inst['problem']}_{inst['M']}_{label}") % 2**32
            ).uniform(-0.15, 0.15)

            # Point = median, error bar = IQR
            ax.scatter(
                x_base + jitter, median_ratio,
                color=color, s=60, alpha=0.85,
                edgecolors="white", linewidths=0.5, zorder=3,
            )
            ax.plot(
                [x_base + jitter, x_base + jitter], [q25, q75],
                color=color, linewidth=1.5, alpha=0.4, zorder=2,
            )

    # Median bar per host
    for ivf_algo, base_algo, color, label in HOST_PAIRS:
        all_medians = []
        for _, inst in instances.iterrows():
            ratios = compute_auc_ratio(df, ivf_algo, base_algo,
                                       inst["problem"], int(inst["M"]))
            if ratios:
                all_medians.append(np.median(ratios))
        if all_medians:
            overall_med = np.median(all_medians)
            x = x_positions[label]
            ax.plot([x - 0.25, x + 0.25], [overall_med, overall_med],
                    color="black", linewidth=2.5, zorder=4)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("AUC ratio (base / IVF)", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Option A: AUC Ratio", fontsize=13, fontweight="bold")

    path = os.path.join(FIG_DIR, "explore_auc_ratio.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"  Wrote {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Metric 2: Speedup
# ---------------------------------------------------------------------------

def compute_speedup(df, ivf_algo, base_algo, prob, m_val, threshold_pct=0.95):
    """Compute speedup: how much faster IVF reaches base's final quality.

    For each run:
      1. Find base's final IGD (at max FE)
      2. Find the first FE where IVF reaches that IGD
      3. Speedup = max_FE / FE_ivf_reached (>1 = IVF is faster)

    Also computes the fraction of budget saved: 1 - FE_reached/max_FE.
    """
    ivf = df[(df["algo"] == ivf_algo) & (df["problem"] == prob) & (df["M"] == m_val)]
    base = df[(df["algo"] == base_algo) & (df["problem"] == prob) & (df["M"] == m_val)]

    if ivf.empty or base.empty:
        return None

    budget_savings = []
    for run_id in ivf["run"].unique():
        ivf_run = ivf[ivf["run"] == run_id].sort_values("FE")
        base_run = base[base["run"] == run_id].sort_values("FE")

        if base_run.empty or ivf_run.empty:
            continue

        # Base's final IGD as the target
        target_igd = base_run["IGD"].iloc[-1]

        # Find first FE where IVF reaches target
        reached = ivf_run[ivf_run["IGD"] <= target_igd]
        if reached.empty:
            budget_savings.append(0.0)  # IVF never reaches base quality
        else:
            fe_reached = reached["FE"].iloc[0]
            saving = 1.0 - fe_reached / MAX_FE
            budget_savings.append(saving)

    return budget_savings if budget_savings else None


def fig_speedup(df, instances):
    """Strip plot of budget savings per instance, grouped by host."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhspan(0, 1, color="#2ecc71", alpha=0.04, zorder=0)
    ax.axhspan(-1, 0, color="#e74c3c", alpha=0.04, zorder=0)

    labels = [l for _, _, _, l in HOST_PAIRS]
    x_positions = {l: i for i, l in enumerate(labels)}

    for ivf_algo, base_algo, color, label in HOST_PAIRS:
        x_base = x_positions[label]
        for _, inst in instances.iterrows():
            savings = compute_speedup(df, ivf_algo, base_algo,
                                      inst["problem"], int(inst["M"]))
            if savings is None:
                continue

            median_saving = np.median(savings)
            q25, q75 = np.percentile(savings, [25, 75])

            jitter = np.random.default_rng(
                hash(f"{inst['problem']}_{inst['M']}_{label}") % 2**32
            ).uniform(-0.15, 0.15)

            ax.scatter(
                x_base + jitter, median_saving,
                color=color, s=60, alpha=0.85,
                edgecolors="white", linewidths=0.5, zorder=3,
            )
            ax.plot(
                [x_base + jitter, x_base + jitter], [q25, q75],
                color=color, linewidth=1.5, alpha=0.4, zorder=2,
            )

    # Median bar per host
    for ivf_algo, base_algo, color, label in HOST_PAIRS:
        all_medians = []
        for _, inst in instances.iterrows():
            savings = compute_speedup(df, ivf_algo, base_algo,
                                      inst["problem"], int(inst["M"]))
            if savings:
                all_medians.append(np.median(savings))
        if all_medians:
            overall_med = np.median(all_medians)
            x = x_positions[label]
            ax.plot([x - 0.25, x + 0.25], [overall_med, overall_med],
                    color="black", linewidth=2.5, zorder=4)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Budget saved (fraction)", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Option B: Speedup (budget saved to reach base quality)",
                 fontsize=13, fontweight="bold")

    path = os.path.join(FIG_DIR, "explore_speedup.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"  Wrote {path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Metric 3: ECDF of runtime (COCO-style)
# ---------------------------------------------------------------------------

def fig_ecdf(df, instances):
    """ECDF of runtime: fraction of (instance, run) pairs that reached
    a given target quality, as a function of FE budget fraction.

    One curve per algorithm. IVF variants that converge faster will have
    curves shifted left (reaching targets earlier).
    """
    # Define targets as percentiles of the best-known IGD per instance
    # (union of all algorithms' final IGD across all runs)
    fig, ax = plt.subplots(figsize=(8, 5))

    algo_styles = {
        "IVFSPEA2":   {"color": "#4c72b0", "ls": "-",  "lw": 2.5, "label": "IVF/SPEA2"},
        "SPEA2":      {"color": "#4c72b0", "ls": "--", "lw": 1.5, "label": "SPEA2"},
        "IVFNSGAIII": {"color": "#55a868", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-III"},
        "NSGAIII":    {"color": "#55a868", "ls": "--", "lw": 1.5, "label": "NSGA-III"},
        "IVFNSGAII":  {"color": "#c44e52", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-II"},
        "NSGAII":     {"color": "#c44e52", "ls": "--", "lw": 1.5, "label": "NSGA-II"},
    }

    # For each (instance, run), compute normalized target as fraction of
    # the best IGD achievable across all algorithms for that instance
    all_algos = list(algo_styles.keys())

    # Build target thresholds: for each instance, use the global best final IGD
    # then define targets as multiples: 100x, 10x, 5x, 2x, 1.5x, 1.2x, 1.0x of best
    target_multipliers = np.array([100, 50, 20, 10, 5, 3, 2, 1.5, 1.2, 1.0])

    # Total number of (instance, target) problems
    instance_targets = []
    for _, inst in instances.iterrows():
        prob, m_val = inst["problem"], int(inst["M"])
        sub = df[(df["problem"] == prob) & (df["M"] == m_val)]
        # Best final IGD across all algorithms and runs
        final_igds = sub.groupby(["algo", "run"])["IGD"].last()
        best_igd = final_igds.min()
        if best_igd <= 0:
            continue
        for mult in target_multipliers:
            instance_targets.append((prob, m_val, best_igd * mult))

    n_targets = len(instance_targets)
    if n_targets == 0:
        print("  No targets found, skipping ECDF")
        return

    # For each algorithm, compute the fraction of targets solved at each FE
    fe_grid = np.linspace(1000, MAX_FE, 100)

    for algo, style in algo_styles.items():
        fractions = []
        for fe_val in fe_grid:
            solved = 0
            total = 0
            for prob, m_val, target in instance_targets:
                algo_data = df[
                    (df["algo"] == algo) &
                    (df["problem"] == prob) &
                    (df["M"] == m_val)
                ]
                for run_id in algo_data["run"].unique():
                    total += 1
                    run_data = algo_data[
                        (algo_data["run"] == run_id) & (algo_data["FE"] <= fe_val)
                    ]
                    if not run_data.empty and run_data["IGD"].min() <= target:
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
    ax.legend(fontsize=9, loc="lower right")
    ax.set_title("Option C: ECDF of Runtime (COCO-style)", fontsize=13, fontweight="bold")

    path = os.path.join(FIG_DIR, "explore_ecdf.pdf")
    fig.savefig(path, bbox_inches="tight", dpi=300)
    print(f"  Wrote {path}")
    plt.close(fig)


def main():
    print("=== Exploring convergence visualization alternatives ===\n")
    df, instances = load_data()
    print(f"Loaded {len(df)} rows, {len(instances)} instances\n")

    print("Generating Option A: AUC ratio strip plot...")
    fig_auc_ratio(df, instances)

    print("Generating Option B: Speedup strip plot...")
    fig_speedup(df, instances)

    print("Generating Option C: ECDF of runtime...")
    fig_ecdf(df, instances)

    print("\nAll exploration figures written to results/figures/explore_*.pdf")


if __name__ == "__main__":
    main()
