#!/usr/bin/env python3
"""Generate Fig 4 HV — HV ratio (IVF / base) over FE with bootstrap IC.

Mirror of Fig 4 IGD but for hypervolume.
Ratio > 1 means IVF achieves higher HV (better).
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from figure_io import save_figure


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONV_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")
INST_CSV = os.path.join(PROJECT_ROOT, "results", "tables", "hosts_convergence_instances.csv")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2", "#4c72b0", "IVF/SPEA2"),
    ("IVFNSGAIII", "NSGAIII", "#55a868", "IVF/NSGA-III"),
    ("IVFNSGAII", "NSGAII", "#c44e52", "IVF/NSGA-II"),
]

MAX_FE = 100_000
N_BOOTSTRAP = 1000
SMOOTH_WINDOW = 5

for out_dir in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(out_dir, exist_ok=True)


def save_fig(fig: plt.Figure, name: str) -> None:
    save_figure(fig, name, (FIG_DIR, PAPER_FIG_DIR), log_prefix="  ")


def interpolate_hv_ratio_per_run(
    df: pd.DataFrame, ivf_algo: str, base_algo: str,
    prob: str, m_val: int, fe_grid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Compute HV ratio (IVF/base) per run on a common FE grid."""
    ivf_all = df[(df["algo"] == ivf_algo) & (df["problem"] == prob) & (df["M"] == m_val)]
    base_all = df[(df["algo"] == base_algo) & (df["problem"] == prob) & (df["M"] == m_val)]

    if ivf_all.empty or base_all.empty:
        return None

    common_runs = set(ivf_all["run"].unique()) & set(base_all["run"].unique())
    if not common_runs:
        return None

    ratios = []
    for run in sorted(common_runs):
        ivf_run = ivf_all[ivf_all["run"] == run].sort_values("FE")
        base_run = base_all[base_all["run"] == run].sort_values("FE")

        # Skip first checkpoint
        ivf_run = ivf_run.iloc[1:] if len(ivf_run) > 1 else ivf_run
        base_run = base_run.iloc[1:] if len(base_run) > 1 else base_run

        if len(ivf_run) < 2 or len(base_run) < 2:
            continue

        ivf_hv = np.interp(fe_grid, ivf_run["FE"].values, ivf_run["HV"].values)
        base_hv = np.interp(fe_grid, base_run["FE"].values, base_run["HV"].values)

        valid = (ivf_hv > 0) & (base_hv > 0)
        ratio = np.full_like(fe_grid, np.nan, dtype=float)
        ratio[valid] = ivf_hv[valid] / base_hv[valid]  # IVF/base, >1 = IVF better
        ratios.append(ratio)

    if not ratios:
        return None
    return np.array(ratios)


def bootstrap_ci(ratio_matrix: np.ndarray, n_bootstrap: int = N_BOOTSTRAP):
    rng = np.random.default_rng(42)
    n_runs, n_fe = ratio_matrix.shape
    boot_medians = np.empty((n_bootstrap, n_fe))
    for b in range(n_bootstrap):
        indices = rng.choice(n_runs, size=n_runs, replace=True)
        boot_medians[b] = np.nanmedian(ratio_matrix[indices], axis=0)
    return (np.nanmedian(ratio_matrix, axis=0),
            np.nanpercentile(boot_medians, 2.5, axis=0),
            np.nanpercentile(boot_medians, 97.5, axis=0))


def smooth(vals: np.ndarray, window: int = SMOOTH_WINDOW) -> np.ndarray:
    if window <= 1:
        return vals
    result = np.full_like(vals, np.nan)
    half = window // 2
    for i in range(len(vals)):
        result[i] = np.nanmedian(vals[max(0, i-half):min(len(vals), i+half+1)])
    return result


def main() -> None:
    print("=== Generating Fig 4 v2: HV ratio ===\n")
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")

    fe_grid = np.linspace(1000, MAX_FE, 200)
    fe_norm = fe_grid / MAX_FE

    n_inst = len(instances)
    ncols, nrows = 3, (n_inst + 2) // 3
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.2 * nrows), squeeze=False)

    for idx, (_, inst) in tqdm(list(enumerate(instances.iterrows()))):
        row, col = divmod(idx, ncols)
        ax = axes[row][col]
        prob, m_val = inst["problem"], int(inst["M"])

        ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

        for ivf_algo, base_algo, color, label in HOST_PAIRS:
            ratio_matrix = interpolate_hv_ratio_per_run(
                df, ivf_algo, base_algo, prob, m_val, fe_grid
            )
            if ratio_matrix is None:
                continue
            med, ci_low, ci_high = bootstrap_ci(ratio_matrix)
            med, ci_low, ci_high = smooth(med), smooth(ci_low), smooth(ci_high)

            ax.plot(fe_norm, med, color=color, linewidth=2.0, label=label)
            ax.fill_between(fe_norm, ci_low, ci_high, color=color, alpha=0.15)

        ax.set_title(f"{prob} ($M={m_val}$)", fontsize=11, fontweight="bold")
        ax.set_xlabel("FE / max FE", fontsize=9)
        if col == 0:
            ax.set_ylabel("HV ratio (IVF / base)", fontsize=9)
        ax.set_xlim(0, 1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)

        ylims = ax.get_ylim()
        ax.axhspan(1.0, ylims[1], color="#2ecc71", alpha=0.05, zorder=0)
        ax.axhspan(ylims[0], 1.0, color="#e74c3c", alpha=0.05, zorder=0)
        ax.set_ylim(ylims)

    for idx in range(n_inst, nrows * ncols):
        axes[idx // ncols][idx % ncols].set_visible(False)

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=10,
               bbox_to_anchor=(0.5, -0.01), frameon=True, edgecolor="0.8")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save_fig(fig, "hosts_v2_fig4_hv_ratio.pdf")
    plt.close(fig)
    print("\nDone.")


if __name__ == "__main__":
    main()
