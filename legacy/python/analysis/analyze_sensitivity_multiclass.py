#!/usr/bin/env python3
"""
Multi-class sensitivity analysis for IVF/SPEA2.

Manuscript-aligned problem set:
  - DTLZ2 (M=2)
  - WFG4  (M=2)
  - DTLZ7 (M=3)

Input layout:
  data/sensitivity_multiclass/IVFSPEA2_R<R>_C<C>_<PROB>/*.mat

Outputs:
  - results/sensitivity_multiclass/sensitivity_multiclass_raw.csv
  - results/sensitivity_multiclass/sensitivity_multiclass_aggregated.csv
  - results/sensitivity_multiclass/sensitivity_multiclass_combined.pdf
  - results/sensitivity_multiclass/sensitivity_heatmap_<problem>.pdf

Robustness rules:
  1) Only files matching the folder problem prefix are accepted.
  2) Per (problem, R, C), at most TARGET_RUNS runs are used, selecting the
     smallest run IDs for deterministic coverage.
"""

import os
import re
import sys
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/home/pedro/desenvolvimento/ivfspea2"
SENSITIVITY_DIR = os.path.join(PROJECT_ROOT, "data", "sensitivity_multiclass")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "sensitivity_multiclass")

TARGET_RUNS = 30

R_VALUES = [0, 0.050, 0.075, 0.100, 0.125, 0.150, 0.200, 0.250, 0.300]
C_VALUES = [0.05, 0.07, 0.11, 0.16, 0.21, 0.27, 0.32, 0.42, 0.53, 0.64]

PROBLEMS = [
    ("DTLZ2_M2", "DTLZ2 ($M=2$)"),
    ("WFG4_M2", "WFG4 ($M=2$)"),
    ("DTLZ7_M3", "DTLZ7 ($M=3$)"),
]
PROBLEM_KEYS = {k for k, _ in PROBLEMS}

FOLDER_REGEX = re.compile(r"IVFSPEA2_R([\d.]+)_C([\d.]+)_(\w+_M\d+)")
RUN_REGEX = re.compile(r"_(\d+)\.mat$")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_igd_from_mat(filepath: str) -> float | None:
    try:
        import pymatreader

        data = pymatreader.read_mat(filepath)
        metric = data.get("metric")
        if metric is None:
            return None
        igd = metric.get("IGD")
        if igd is None:
            return None

        if isinstance(igd, np.ndarray):
            return float(igd.flat[-1])
        return float(igd)
    except Exception:
        return None


def load_sensitivity_data() -> pd.DataFrame:
    if not os.path.isdir(SENSITIVITY_DIR):
        print(f"ERROR: missing sensitivity directory: {SENSITIVITY_DIR}")
        return pd.DataFrame()

    # Keep one metric per unique (problem, R, C, run)
    per_run: dict[tuple[str, float, float, int], float] = {}

    for folder_name in sorted(os.listdir(SENSITIVITY_DIR)):
        folder_path = os.path.join(SENSITIVITY_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        match = FOLDER_REGEX.match(folder_name)
        if not match:
            continue

        r_val = float(match.group(1))
        c_val = float(match.group(2))
        prob_label = match.group(3)

        if prob_label not in PROBLEM_KEYS:
            continue

        expected_prefix = f"IVFSPEA2_{prob_label}_"

        for mat_file in os.listdir(folder_path):
            if not mat_file.endswith(".mat"):
                continue
            if not mat_file.startswith(expected_prefix):
                continue

            run_match = RUN_REGEX.search(mat_file)
            if run_match is None:
                continue
            run_id = int(run_match.group(1))

            igd = load_igd_from_mat(os.path.join(folder_path, mat_file))
            if igd is None or np.isnan(igd) or igd >= 1e6:
                continue

            key = (prob_label, r_val, c_val, run_id)
            if key not in per_run:
                per_run[key] = igd

    grouped: dict[tuple[str, float, float], list[tuple[int, float]]] = defaultdict(list)
    for (prob, r_val, c_val, run_id), igd in per_run.items():
        grouped[(prob, r_val, c_val)].append((run_id, igd))

    rows = []
    for (prob, r_val, c_val), vals in grouped.items():
        vals_sorted = sorted(vals, key=lambda x: x[0])
        for run_id, igd in vals_sorted[:TARGET_RUNS]:
            rows.append(
                {
                    "Problem": prob,
                    "R": r_val,
                    "C": c_val,
                    "Run": run_id,
                    "IGD": igd,
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        print(f"Loaded {len(df)} run-level IGD points")
        print("Coverage (problem -> combinations):")
        print(
            df.groupby("Problem").apply(
                lambda x: x[["R", "C"]].drop_duplicates().shape[0]
            )
        )
    return df


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
def aggregate_to_heatmap_data(df: pd.DataFrame, problem: str) -> pd.DataFrame:
    sub = df[df["Problem"] == problem]
    if sub.empty:
        return pd.DataFrame()

    agg = sub.groupby(["R", "C"], as_index=False)["IGD"].median()
    agg.columns = ["R", "C", "IGD_Median"]

    stats = (
        sub.groupby(["R", "C"])["IGD"]
        .agg(Count="count", IQR=lambda x: np.percentile(x, 75) - np.percentile(x, 25))
        .reset_index()
    )

    agg = pd.DataFrame(pd.merge(agg, stats, on=["R", "C"], how="left"))
    agg.insert(0, "Problem", problem)
    return pd.DataFrame(agg[["Problem", "R", "C", "IGD_Median", "Count", "IQR"]])


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_single_heatmap(ax, agg_df: pd.DataFrame, title: str):
    pivot = agg_df.pivot(index="R", columns="C", values="IGD_Median")
    pivot = pivot.reindex(index=R_VALUES, columns=C_VALUES)

    data = pivot.values
    im = ax.imshow(data, cmap="cividis", aspect="auto", origin="lower")

    r_labels = [f"{r:.3f}" for r in R_VALUES]
    c_labels = [f"{c:.2f}" for c in C_VALUES]
    ax.set_xticks(range(len(c_labels)))
    ax.set_xticklabels(c_labels, fontsize=8, rotation=45)
    ax.set_yticks(range(len(r_labels)))
    ax.set_yticklabels(r_labels, fontsize=8)
    ax.set_xlabel("Collection size ($c$)", fontsize=9)
    ax.set_ylabel("Execution rate ($r$)", fontsize=9)
    if title:
        ax.set_title(title, fontsize=9)

    # default point
    try:
        r_idx = R_VALUES.index(0.1)
        c_idx = C_VALUES.index(0.11)
        ax.plot(c_idx, r_idx, marker="*", color="black", markersize=11, zorder=10)
    except ValueError:
        pass

    return im


def plot_combined_heatmaps(all_agg: dict[str, pd.DataFrame]):
    nplots = len(PROBLEMS)
    # Springer large-journal double-column width: ~174 mm = 6.85 in
    fig = plt.figure(figsize=(6.85, 2.75))
    gs = fig.add_gridspec(
        1, nplots + 1, width_ratios=[1] * nplots + [0.06], wspace=0.38
    )
    axes = [fig.add_subplot(gs[0, i]) for i in range(nplots)]
    cax = fig.add_subplot(gs[0, nplots])

    ims = []
    for idx, (prob_key, _prob_title) in enumerate(PROBLEMS):
        agg = all_agg.get(prob_key, pd.DataFrame())
        if agg.empty:
            axes[idx].text(
                0.5,
                0.5,
                f"({chr(97 + idx)}) no data",
                transform=axes[idx].transAxes,
                ha="center",
                va="center",
                fontsize=9,
            )
            axes[idx].set_axis_off()
            continue
        ims.append(plot_single_heatmap(axes[idx], agg, ""))
        axes[idx].text(
            0.02,
            0.98,
            f"({chr(97 + idx)})",
            transform=axes[idx].transAxes,
            ha="left",
            va="top",
            fontsize=9,
            fontweight="bold",
            color="white",
            bbox={
                "boxstyle": "round,pad=0.15",
                "facecolor": "black",
                "edgecolor": "none",
                "alpha": 0.45,
            },
        )

        if idx > 0:
            axes[idx].set_ylabel("")
            axes[idx].set_yticklabels([])

    if ims:
        cbar = fig.colorbar(ims[-1], cax=cax)
        cbar.set_label("Median IGD", fontsize=9)
        cbar.ax.tick_params(labelsize=8)
    else:
        cax.axis("off")

    fig.subplots_adjust(left=0.06, right=0.985, bottom=0.24, top=0.94)

    fig_path = os.path.join(OUTPUT_DIR, "sensitivity_multiclass_combined.pdf")
    plt.savefig(fig_path, dpi=150)

    fig_png = os.path.join(OUTPUT_DIR, "sensitivity_multiclass_combined.png")
    fig_tiff = os.path.join(OUTPUT_DIR, "sensitivity_multiclass_combined.tiff")
    plt.savefig(fig_png, dpi=600)
    plt.savefig(fig_tiff, dpi=600)

    plt.close()
    print(f"Saved combined figure: {fig_path}")
    print(f"Saved combined figure: {fig_png}")
    print(f"Saved combined figure: {fig_tiff}")


def plot_individual_heatmaps(all_agg: dict[str, pd.DataFrame]):
    for prob_key, prob_title in PROBLEMS:
        agg = all_agg.get(prob_key, pd.DataFrame())
        if agg.empty:
            continue
        fig, ax = plt.subplots(1, 1, figsize=(6, 5))
        im = plot_single_heatmap(ax, agg, prob_title)
        fig.colorbar(im, ax=ax, label="Median IGD")
        plt.tight_layout()
        fig_path = os.path.join(
            OUTPUT_DIR, f"sensitivity_heatmap_{prob_key.lower()}.pdf"
        )
        plt.savefig(fig_path, bbox_inches="tight", dpi=150)
        plt.close()
        print(f"Saved: {fig_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("MULTI-CLASS SENSITIVITY ANALYSIS")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_sensitivity_data()
    if df.empty:
        print("No sensitivity data available.")
        sys.exit(0)

    raw_csv = os.path.join(OUTPUT_DIR, "sensitivity_multiclass_raw.csv")
    df.to_csv(raw_csv, index=False)
    print(f"Saved raw data: {raw_csv}")

    all_agg = {}
    for prob_key, _ in PROBLEMS:
        agg = aggregate_to_heatmap_data(df, prob_key)
        if not agg.empty:
            all_agg[prob_key] = agg
            print(f"  {prob_key}: {len(agg)} parameter combinations")

    if all_agg:
        agg_csv = os.path.join(OUTPUT_DIR, "sensitivity_multiclass_aggregated.csv")
        pd.concat(all_agg.values(), ignore_index=True).to_csv(agg_csv, index=False)
        print(f"Saved aggregated data: {agg_csv}")

    plot_combined_heatmaps(all_agg)
    plot_individual_heatmaps(all_agg)

    print("\n--- Default-point ranking summary ---")
    for prob_key, _ in PROBLEMS:
        agg = all_agg.get(prob_key)
        if agg is None or agg.empty:
            print(f"  {prob_key}: no data")
            continue

        best = agg.loc[agg["IGD_Median"].idxmin()]
        default = agg[(agg["R"] == 0.1) & (np.isclose(agg["C"], 0.11))]

        print(
            f"  {prob_key}: best at (r={best['R']:.3f}, c={best['C']:.2f}), "
            f"median IGD={best['IGD_Median']:.6f}"
        )
        if not default.empty:
            dval = default.iloc[0]["IGD_Median"]
            rank = int((agg["IGD_Median"] <= dval).sum())
            total = len(agg)
            print(
                f"    default (0.10,0.11): median IGD={dval:.6f}, rank {rank}/{total}"
            )

    print(f"\nOutputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
