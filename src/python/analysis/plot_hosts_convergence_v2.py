#!/usr/bin/env python3
"""Generate improved convergence figures with bootstrap IC and interpolation.

Fig 4 (v2) — IGD ratio (base / IVF) over FE with:
  - Interpolation-based alignment (fixes FE grid mismatch)
  - Bootstrap IC 95% bands (not just IQR)
  - Optional smoothing toggle

Fig 5 (v2) — ECDF with:
  - Bootstrap uncertainty bands
  - KS-test p-value annotation
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CONV_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_convergence.csv")
INST_CSV = os.path.join(PROJECT_ROOT, "results", "tables", "hosts_convergence_instances.csv")
ECDF_SIG_CSV = os.path.join(PROJECT_ROOT, "results", "tables", "ecdf_significance.csv")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2", "#0072B2", "IVF/SPEA2"),
    ("IVFNSGAIII", "NSGAIII", "#009E73", "IVF/NSGA-III"),
    ("IVFNSGAII", "NSGAII", "#D55E00", "IVF/NSGA-II"),
]

ALGO_STYLES = {
    "IVFSPEA2":   {"color": "#0072B2", "ls": "-",  "lw": 2.5, "label": "IVF/SPEA2"},
    "SPEA2":      {"color": "#0072B2", "ls": "--", "lw": 1.5, "label": "SPEA2"},
    "IVFNSGAIII": {"color": "#009E73", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-III"},
    "NSGAIII":    {"color": "#009E73", "ls": "--", "lw": 1.5, "label": "NSGA-III"},
    "IVFNSGAII":  {"color": "#D55E00", "ls": "-",  "lw": 2.5, "label": "IVF/NSGA-II"},
    "NSGAII":     {"color": "#D55E00", "ls": "--", "lw": 1.5, "label": "NSGA-II"},
}

MAX_FE = 100_000
N_BOOTSTRAP = 1000
SMOOTH_WINDOW = 5
INCLUDE_FIRST_CHECKPOINT = False  # R6 sensitivity toggle

for out_dir in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(out_dir, exist_ok=True)


def save_fig(fig: plt.Figure, name: str) -> None:
    for out_dir in (FIG_DIR, PAPER_FIG_DIR):
        path = os.path.join(out_dir, name)
        fig.savefig(path, bbox_inches="tight", dpi=300)
        print(f"  Wrote {path}")


def interpolate_ratio_per_run(
    df: pd.DataFrame, ivf_algo: str, base_algo: str,
    prob: str, m_val: int, fe_grid: np.ndarray,
) -> np.ndarray | None:
    """Compute mean IGD ratio (base/IVF) on a common FE grid via interpolation.

    For each run, interpolates both IGD curves onto fe_grid, computes ratio,
    then returns mean across runs.
    """
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

        # Filter first checkpoint if configured
        if not INCLUDE_FIRST_CHECKPOINT:
            ivf_run = ivf_run.iloc[1:] if len(ivf_run) > 1 else ivf_run
            base_run = base_run.iloc[1:] if len(base_run) > 1 else base_run

        if len(ivf_run) < 2 or len(base_run) < 2:
            continue

        ivd_igd = np.interp(fe_grid, ivf_run["FE"].values, ivf_run["IGD"].values)
        base_igd = np.interp(fe_grid, base_run["FE"].values, base_run["IGD"].values)

        # Guard against zero/negative
        valid = (ivd_igd > 0) & (base_igd > 0)
        ratio = np.full_like(fe_grid, np.nan, dtype=float)
        ratio[valid] = base_igd[valid] / ivd_igd[valid]
        ratios.append(ratio)

    if not ratios:
        return None

    ratio_matrix = np.array(ratios)  # shape: (n_runs, n_fe_points)
    return np.nanmean(ratio_matrix, axis=0), ratio_matrix


def bootstrap_ratio_ci(
    ratio_matrix: np.ndarray, n_bootstrap: int = N_BOOTSTRAP,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute bootstrap CI 95% for ratio curve.

    ratio_matrix: shape (n_runs, n_fe_points)
    Returns: median, ci_low, ci_high arrays of shape (n_fe_points,)
    """
    rng = np.random.default_rng(42)
    n_runs, n_fe = ratio_matrix.shape

    boot_medians = np.empty((n_bootstrap, n_fe))
    for b in range(n_bootstrap):
        indices = rng.choice(n_runs, size=n_runs, replace=True)
        boot_sample = ratio_matrix[indices]
        boot_medians[b] = np.nanmedian(boot_sample, axis=0)

    median = np.nanmedian(ratio_matrix, axis=0)
    ci_low = np.nanpercentile(boot_medians, 2.5, axis=0)
    ci_high = np.nanpercentile(boot_medians, 97.5, axis=0)

    return median, ci_low, ci_high


def smooth_curve(vals: np.ndarray, window: int = SMOOTH_WINDOW) -> np.ndarray:
    """Rolling median smoothing."""
    if window <= 1:
        return vals
    result = np.full_like(vals, np.nan)
    half = window // 2
    for i in range(len(vals)):
        start = max(0, i - half)
        end = min(len(vals), i + half + 1)
        result[i] = np.nanmedian(vals[start:end])
    return result


def fig4_convergence_v2(df: pd.DataFrame, instances: pd.DataFrame) -> None:
    """Fig 4 v2 — IGD ratio with bootstrap CI bands and interpolation."""
    fe_grid = np.linspace(1000, MAX_FE, 200)
    fe_norm = fe_grid / MAX_FE

    n_inst = len(instances)
    ncols = 3
    nrows = (n_inst + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.2 * nrows), squeeze=False)

    for idx, (_, inst) in tqdm(list(enumerate(instances.iterrows()))):
        row, col = divmod(idx, ncols)
        ax = axes[row][col]
        prob = inst["problem"]
        m_val = int(inst["M"])

        ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

        for ivf_algo, base_algo, color, label in HOST_PAIRS:
            result = interpolate_ratio_per_run(
                df, ivf_algo, base_algo, prob, m_val, fe_grid
            )
            if result is None:
                continue
            median_curve, ratio_matrix = result

            # Bootstrap CI
            med, ci_low, ci_high = bootstrap_ratio_ci(ratio_matrix)

            # Optional smoothing
            med = smooth_curve(med)
            ci_low = smooth_curve(ci_low)
            ci_high = smooth_curve(ci_high)

            ax.plot(fe_norm, med, color=color, linewidth=2.0, label=label)
            ax.fill_between(fe_norm, ci_low, ci_high, color=color, alpha=0.15,
                          label=f"{label} 95% CI")

        ax.set_title(f"{prob} ($M={m_val}$)", fontsize=12, fontweight="bold")
        ax.set_xlabel("FE / max FE", fontsize=11)
        if col == 0:
            ax.set_ylabel("IGD ratio (base / IVF)", fontsize=11)
        ax.set_xlim(0, 1)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=10)

        ylims = ax.get_ylim()
        ax.axhspan(1.0, ylims[1], color="#2166ac", alpha=0.05, zorder=0)
        ax.axhspan(ylims[0], 1.0, color="#e74c3c", alpha=0.05, zorder=0)
        ax.set_ylim(ylims)

    for idx in range(n_inst, nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row][col].set_visible(False)

    handles, labels = axes[0][0].get_legend_handles_labels()
    # Deduplicate: keep one entry per algorithm (skip CI entries)
    seen = set()
    kept_h, kept_l = [], []
    for h, l in zip(handles, labels):
        key = l.split(" 95%")[0] if "95% CI" in l else l
        if key not in seen:
            seen.add(key)
            kept_h.append(h)
            kept_l.append(l)
    fig.legend(kept_h, kept_l, loc="lower center", ncol=3, fontsize=11,
               bbox_to_anchor=(0.5, -0.01), frameon=True, edgecolor="0.8")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save_fig(fig, "hosts_v2_fig4_convergence.pdf")
    plt.close(fig)


def fig5_ecdf_v2(df: pd.DataFrame, instances: pd.DataFrame) -> None:
    """Fig 5 v2 — ECDF with bootstrap bands and KS-test p-value annotation."""
    target_multipliers = np.array([100, 50, 20, 10, 5, 3, 2, 1.5, 1.2, 1.0])

    ecdf_sig = pd.read_csv(ECDF_SIG_CSV) if os.path.exists(ECDF_SIG_CSV) else None

    # Build per-run "solved at FE" matrix for each (algo, instance, target)
    # Then use bootstrap on this matrix
    fe_grid = np.linspace(1000, MAX_FE, 200)
    algo_names = list(ALGO_STYLES.keys())

    print("  Precomputing per-run time-to-target...")
    # For each (algo, prob, M, run), store the cumulative minimum IGD curve
    # Then compute whether each target is solved at each FE point
    run_ttt = {}  # (algo, prob, M, run) -> array of (n_fe_grid,) cumulative min IGD

    for algo in algo_names:
        for _, inst in instances.iterrows():
            prob, m_val = inst["problem"], int(inst["M"])
            sub = df[(df["algo"] == algo) & (df["problem"] == prob) & (df["M"] == m_val)]
            for run_id, run_data in sub.groupby("run"):
                sorted_run = run_data.sort_values("FE")
                cummin = sorted_run.set_index("FE")["IGD"].cummin()
                # Interpolate onto fe_grid
                interp_vals = np.interp(fe_grid, cummin.index, cummin.values)
                run_ttt[(algo, prob, m_val, run_id)] = interp_vals

    # Precompute targets
    print("  Computing targets...")
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

    print("  Computing ECDF with bootstrap uncertainty...")
    rng = np.random.default_rng(42)
    n_bootstrap = 500  # Reduced for performance

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for algo in algo_names:
        style = ALGO_STYLES[algo]

        # Collect per-run solve fractions at each FE point
        # Shape: (n_runs_effective, n_fe_grid)
        run_fractions = []
        runs_per_algo = set()
        for key in run_ttt:
            if key[0] == algo:
                runs_per_algo.add((key[1], key[2], key[3]))

        for prob, m_val, run_id in runs_per_algo:
            cummin_igd = run_ttt[(algo, prob, m_val, run_id)]
            # For each target, check if solved at each FE
            solve_vector = np.zeros(len(fe_grid))
            count = 0
            for tp, tm, target in instance_targets:
                if tp == prob and tm == m_val:
                    count += 1
                    solve_vector += (cummin_igd <= target).astype(float)
            if count > 0:
                run_fractions.append(solve_vector / count)

        if not run_fractions:
            continue

        run_matrix = np.array(run_fractions)  # (n_runs, n_fe)

        # Main ECDF: average across runs
        main_curve = np.mean(run_matrix, axis=0)

        # Bootstrap CI
        boot_medians = np.empty((n_bootstrap, len(fe_grid)))
        for b in range(n_bootstrap):
            indices = rng.choice(len(run_matrix), size=len(run_matrix), replace=True)
            boot_medians[b] = np.median(run_matrix[indices], axis=0)

        ci_low = np.percentile(boot_medians, 2.5, axis=0)
        ci_high = np.percentile(boot_medians, 97.5, axis=0)

        ax.plot(fe_grid / MAX_FE, main_curve, color=style["color"],
                linestyle=style["ls"], linewidth=style["lw"], label=style["label"])
        ax.fill_between(fe_grid / MAX_FE, ci_low, ci_high,
                       color=style["color"], alpha=0.08)

    ax.set_xlabel("FE / max FE", fontsize=11)
    ax.set_ylabel("Fraction of targets solved", fontsize=11)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.legend(fontsize=9, loc="lower right", framealpha=0.95)

    # Add KS-test annotations if available
    if ecdf_sig is not None:
        y_pos = 0.95
        for _, sig_row in ecdf_sig.iterrows():
            if sig_row["p_value"] < 0.05:
                label = f"{sig_row['ivf_algo']} vs {sig_row['base_algo']}: p={sig_row['p_value']:.3g}"
                ax.text(0.02, y_pos, label, transform=ax.transAxes, fontsize=7, va="top",
                       color="#2e7d32" if sig_row["direction"] == "IVF faster" else "#c62828")
                y_pos -= 0.04

    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig5_ecdf.pdf")
    plt.close(fig)


def main() -> None:
    print("=== Generating improved convergence figures (v2) ===\n")
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")

    print(f"Loaded {len(df)} convergence rows, {len(instances)} instances")
    print(f"Smoothing window: {SMOOTH_WINDOW}")
    print(f"Include first checkpoint: {INCLUDE_FIRST_CHECKPOINT}")
    print(f"Bootstrap replicates: {N_BOOTSTRAP}\n")

    print("Generating Fig 4 v2: IGD ratio with bootstrap CI...")
    fig4_convergence_v2(df, instances)
    print()

    print("Generating Fig 5 v2: ECDF with bootstrap bands + KS-test...")
    fig5_ecdf_v2(df, instances)

    print("\nAll convergence figures (v2) written.")


if __name__ == "__main__":
    main()
