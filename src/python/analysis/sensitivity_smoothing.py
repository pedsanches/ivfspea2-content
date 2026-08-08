#!/usr/bin/env python3
"""Sensitivity analysis for convergence figure choices.

Compares:
  1. With vs without smoothing (rolling median, window=5)
  2. With vs without first checkpoint
  3. Exact FE merge vs interpolation-based alignment

Output: results/figures/sensitivity_smoothing.pdf
        results/tables/sensitivity_report.csv
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
OUT_FIG = os.path.join(PROJECT_ROOT, "results", "figures", "sensitivity_smoothing.pdf")
OUT_REPORT = os.path.join(PROJECT_ROOT, "results", "tables", "sensitivity_report.csv")

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2", "#4c72b0", "IVF/SPEA2"),
    ("IVFNSGAIII", "NSGAIII", "#55a868", "IVF/NSGA-III"),
    ("IVFNSGAII", "NSGAII", "#c44e52", "IVF/NSGA-II"),
]

MAX_FE = 100_000
SMOOTH_WINDOW = 5


def save_fig(fig: plt.Figure, name: str) -> None:
    fig.savefig(name, bbox_inches="tight", dpi=300)
    print(f"  Wrote {name}")


def compute_ratio_curve(
    df: pd.DataFrame, ivf_algo: str, base_algo: str,
    prob: str, m_val: int, fe_grid: np.ndarray,
    smooth: bool = True, skip_first: bool = True,
) -> np.ndarray | None:
    """Compute median IGD ratio on fe_grid with configurable options."""
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

        if skip_first:
            ivf_run = ivf_run.iloc[1:] if len(ivf_run) > 1 else ivf_run
            base_run = base_run.iloc[1:] if len(base_run) > 1 else base_run

        if len(ivf_run) < 2 or len(base_run) < 2:
            continue

        ivf_igd = np.interp(fe_grid, ivf_run["FE"].values, ivf_run["IGD"].values)
        base_igd = np.interp(fe_grid, base_run["FE"].values, base_run["IGD"].values)

        valid = (ivf_igd > 0) & (base_igd > 0)
        ratio = np.full_like(fe_grid, np.nan, dtype=float)
        ratio[valid] = base_igd[valid] / ivf_igd[valid]
        ratios.append(ratio)

    if not ratios:
        return None

    ratio_matrix = np.array(ratios)
    median_curve = np.nanmedian(ratio_matrix, axis=0)

    if smooth:
        half = SMOOTH_WINDOW // 2
        smoothed = np.full_like(median_curve, np.nan)
        for i in range(len(median_curve)):
            smoothed[i] = np.nanmedian(median_curve[max(0, i-half):min(len(median_curve), i+half+1)])
        return smoothed

    return median_curve


def exact_merge_ratio(
    df: pd.DataFrame, ivf_algo: str, base_algo: str,
    prob: str, m_val: int,
) -> pd.DataFrame | None:
    """Compute ratio via exact (run, FE) merge (original method)."""
    ivf = df[(df["algo"] == ivf_algo) & (df["problem"] == prob) & (df["M"] == m_val)]
    base = df[(df["algo"] == base_algo) & (df["problem"] == prob) & (df["M"] == m_val)]

    if ivf.empty or base.empty:
        return None

    merged = base.merge(ivf, on=["run", "FE"], suffixes=("_base", "_ivf"))
    merged = merged[merged["IGD_ivf"] > 0]
    merged["ratio"] = merged["IGD_base"] / merged["IGD_ivf"]

    if merged.empty:
        return None

    stats = merged.groupby("FE")["ratio"].agg(
        median="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
    ).sort_index()

    if len(stats) > 2:
        stats = stats.iloc[1:]  # Skip first checkpoint

    # Smooth
    for col in ["median", "q25", "q75"]:
        stats[col] = stats[col].rolling(5, min_periods=1, center=True).median()

    return stats


def main() -> None:
    print("=== Sensitivity analysis ===\n")
    df = pd.read_csv(CONV_CSV)
    instances = pd.read_csv(INST_CSV).sort_values("slot")
    fe_grid = np.linspace(1000, MAX_FE, 200)
    fe_norm = fe_grid / MAX_FE

    report_rows = []
    n_inst = len(instances)

    # 3-row layout per instance: (default) vs (no smooth) vs (no skip first)
    fig, axes = plt.subplots(n_inst, 3, figsize=(14, 3.5 * n_inst), squeeze=False)

    for idx, (_, inst) in enumerate(instances.iterrows()):
        prob, m_val = inst["problem"], int(inst["M"])

        for col_idx, (smooth, skip_first, title) in enumerate([
            (True, True, "Default (smooth + skip 1st)"),
            (False, True, "No smoothing"),
            (True, False, "Include 1st checkpoint"),
        ]):
            ax = axes[idx][col_idx]
            ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

            for ivf_algo, base_algo, color, label in HOST_PAIRS:
                curve = compute_ratio_curve(
                    df, ivf_algo, base_algo, prob, m_val, fe_grid,
                    smooth=smooth, skip_first=skip_first,
                )
                if curve is None:
                    continue
                ax.plot(fe_norm, curve, color=color, linewidth=1.5, label=label)

                # Quantify difference from default
                if col_idx > 0:
                    default_curve = compute_ratio_curve(
                        df, ivf_algo, base_algo, prob, m_val, fe_grid,
                        smooth=True, skip_first=True,
                    )
                    if default_curve is not None:
                        max_diff = float(np.nanmax(np.abs(curve - default_curve)))
                        report_rows.append({
                            "problem": prob, "M": m_val,
                            "ivf_algo": ivf_algo, "base_algo": base_algo,
                            "variant": title, "max_abs_diff": max_diff,
                        })

            ax.set_title(title, fontsize=9)
            if col_idx == 0:
                ax.set_ylabel(f"{prob} M={m_val}", fontsize=9, fontweight="bold")
            ax.set_xlim(0, 1)
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(labelsize=7)

        # Legend on first column
        if idx == 0:
            handles, labels = axes[0][0].get_legend_handles_labels()
            axes[0][0].legend(handles, labels, fontsize=7, loc="best")

    fig.tight_layout()
    save_fig(fig, OUT_FIG)
    plt.close(fig)

    # Save report
    if report_rows:
        report_df = pd.DataFrame(report_rows)
        os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
        report_df.to_csv(OUT_REPORT, index=False)
        print(f"\nSensitivity report: {OUT_REPORT}")
        print(f"  Max deviations from default:")
        for _, r in report_df.iterrows():
            print(f"    {r['ivf_algo']} vs {r['base_algo']} on {r['problem']} M={r['M']} "
                  f"({r['variant']}): max diff = {r['max_abs_diff']:.4f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
