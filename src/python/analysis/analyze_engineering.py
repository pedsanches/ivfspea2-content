#!/usr/bin/env python3
"""
Engineering Problem Analysis (Point I)
========================================
Parses PlatEMO .mat result files from the RWMOP9 experiment and generates:
  1. LaTeX table: median(IQR) per algorithm, Wilcoxon indicators, bold best
  2. CSV with per-run IGD values
  3. Box-plot figure comparing all 9 algorithms

Expected input layout:
  data/engineering/<ALGO>_RWMOP9_M2/*.mat
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/home/pedro/desenvolvimento/ivfspea2"
ENGINEERING_DIR = os.path.join(PROJECT_ROOT, "data", "engineering")
if not os.path.isdir(ENGINEERING_DIR):
    ENGINEERING_DIR = os.path.join(PROJECT_ROOT, "data", "legacy", "engineering")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "engineering")
ALPHA = 0.05

ALGORITHMS = [
    ("IVFSPEA2", "IVF/SPEA2"),
    ("SPEA2", "SPEA2"),
    ("MFOSPEA2", "MFO-SPEA2"),
    ("SPEA2SDE", "SPEA2+SDE"),
    ("NSGAII", "NSGA-II"),
    ("NSGAIII", "NSGA-III"),
    ("MOEAD", "MOEA/D"),
    ("AGEMOEAII", "AGE-II"),
    ("ARMOEA", "AR-MOEA"),
]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_igd_from_mat(filepath: str) -> float | None:
    """Extract the final IGD value from a PlatEMO .mat file."""
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
    except Exception as e:
        print(f"  WARN: Could not read {filepath}: {e}")
        return None


def load_engineering_data() -> pd.DataFrame:
    """Scan engineering directory and collect per-run IGD values."""
    rows = []
    if not os.path.isdir(ENGINEERING_DIR):
        print(f"ERROR: Engineering directory not found: {ENGINEERING_DIR}")
        return pd.DataFrame()

    for folder_name in sorted(os.listdir(ENGINEERING_DIR)):
        folder_path = os.path.join(ENGINEERING_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # Parse: ALGO_RWMOP9_M2
        parts = folder_name.split("_")
        if len(parts) < 3 or "RWMOP9" not in folder_name:
            continue

        algo = parts[0]

        for mat_file in sorted(os.listdir(folder_path)):
            if not mat_file.endswith(".mat"):
                continue
            igd = load_igd_from_mat(os.path.join(folder_path, mat_file))
            if igd is not None:
                rows.append({"Algorithm": algo, "IGD": igd})

    df = pd.DataFrame(rows)
    if len(df) > 0:
        print(f"Loaded {len(df)} IGD values for {df['Algorithm'].nunique()} algorithms")
    return df


# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------


def wilcoxon_test(x: np.ndarray, y: np.ndarray) -> str:
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    if len(x) < 3 or len(y) < 3:
        return "="
    try:
        _, p = mannwhitneyu(x, y, alternative="two-sided")
        if p < ALPHA:
            return "+" if np.median(x) < np.median(y) else "-"
        return "="
    except Exception:
        return "="


def format_median_iqr(values: np.ndarray) -> str:
    med = np.median(values)
    q25, q75 = np.percentile(values, [25, 75])
    iqr = q75 - q25
    if med == 0:
        return "0.00(0.00)e+0"
    exp = int(np.floor(np.log10(abs(med))))
    m = med / (10**exp)
    i = iqr / (10**exp)
    return f"{m:.2f}({i:.2f})e{exp:+d}"


# ---------------------------------------------------------------------------
# Table generation
# ---------------------------------------------------------------------------


def generate_engineering_table(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Generate LaTeX table for RWMOP9 results."""
    algo_keys = [a[0] for a in ALGORITHMS]
    algo_display = {a[0]: a[1] for a in ALGORITHMS}

    # Get baseline data
    base_data = df[df["Algorithm"] == "IVFSPEA2"]["IGD"].values

    row = {"Problem": "RWMOP9"}
    best_median = np.inf
    best_algo = ""

    for algo_key, _ in ALGORITHMS:
        algo_data = df[df["Algorithm"] == algo_key]["IGD"].values
        if len(algo_data) == 0:
            row[f"{algo_key}_formatted"] = "---"
            row[f"{algo_key}_median"] = np.nan
            row[f"{algo_key}_indicator"] = ""
            row[f"{algo_key}_n"] = 0
            continue

        med = np.median(algo_data)
        row[f"{algo_key}_formatted"] = format_median_iqr(algo_data)
        row[f"{algo_key}_median"] = med
        row[f"{algo_key}_n"] = len(algo_data)

        if med < best_median:
            best_median = med
            best_algo = algo_key

        if algo_key != "IVFSPEA2" and len(base_data) > 0:
            row[f"{algo_key}_indicator"] = wilcoxon_test(base_data, algo_data)
        else:
            row[f"{algo_key}_indicator"] = ""

    row["best_algo"] = best_algo
    result_df = pd.DataFrame([row])

    # LaTeX
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(
        r"\caption{RWMOP9 (Four Bar Plane Truss): median IGD (IQR) over 100 runs. "
        r"Symbols: $+$ = IVF/SPEA2 significantly better, "
        r"$-$ = significantly worse, "
        r"$\approx$ = no significant difference (Wilcoxon, $\alpha=0.05$). "
        r"Best median in \textbf{bold}.}"
    )
    lines.append(r"\label{tab:engineering}")
    lines.append(r"\centering\scriptsize")
    lines.append(r"\begin{tabular}{lr@{\hskip 4pt}r}")
    lines.append(r"\toprule")
    lines.append(r"Algorithm & Median IGD (IQR) & $n$ \\")
    lines.append(r"\midrule")

    for algo_key, display in ALGORITHMS:
        cell = row.get(f"{algo_key}_formatted", "---")
        indicator = row.get(f"{algo_key}_indicator", "")
        n_runs = row.get(f"{algo_key}_n", 0)

        if row.get("best_algo") == algo_key:
            cell = r"\textbf{" + cell + "}"

        if indicator == "+":
            cell += r"$^{+}$"
        elif indicator == "-":
            cell += r"$^{-}$"
        elif indicator == "=":
            cell += r"$^{\approx}$"

        lines.append(f"{display} & {cell} & {n_runs} " + r"\\")

    lines.append(r"\botrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return result_df, "\n".join(lines)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_engineering_boxplot(df: pd.DataFrame):
    """Box-plot comparing all algorithms on RWMOP9."""
    fig, ax = plt.subplots(figsize=(10, 5))

    algo_keys = [a[0] for a in ALGORITHMS]
    algo_display = [a[1] for a in ALGORITHMS]
    colors = [
        "#2196F3",  # IVF/SPEA2 (blue)
        "#9E9E9E",  # SPEA2
        "#9E9E9E",  # MFO-SPEA2
        "#9E9E9E",  # SPEA2+SDE
        "#FF9800",  # NSGA-II
        "#FF9800",  # NSGA-III
        "#FF9800",  # MOEA/D
        "#4CAF50",  # AGE-II
        "#4CAF50",  # AR-MOEA
    ]

    data_list = []
    labels = []
    box_colors = []
    for idx, (algo_key, display) in enumerate(ALGORITHMS):
        vals = df[df["Algorithm"] == algo_key]["IGD"].values
        if len(vals) > 0:
            data_list.append(vals)
            labels.append(display)
            box_colors.append(colors[idx])

    bp = ax.boxplot(data_list, labels=labels, patch_artist=True, widths=0.6)
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel("IGD", fontsize=11)
    ax.set_title("RWMOP9 (Four Bar Plane Truss) - IGD Distribution", fontsize=12)
    ax.tick_params(axis="x", rotation=30, labelsize=9)

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_DIR, "engineering_rwmop9_boxplot.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 60)
    print("ENGINEERING PROBLEM ANALYSIS (Point I)")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_engineering_data()
    if df.empty:
        print("No engineering data found. Run experiments first.")
        sys.exit(0)

    # Save raw data
    csv_path = os.path.join(OUTPUT_DIR, "engineering_rwmop9_raw.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved raw data: {csv_path}")

    # Table
    result_df, latex = generate_engineering_table(df)
    tex_path = os.path.join(OUTPUT_DIR, "engineering_rwmop9_table.tex")
    with open(tex_path, "w") as f:
        f.write(latex)
    print(f"Saved LaTeX: {tex_path}")

    # Box plot
    plot_engineering_boxplot(df)

    # Print results
    print("\n--- RWMOP9 Results ---")
    for algo_key, display in ALGORITHMS:
        vals = df[df["Algorithm"] == algo_key]["IGD"].values
        if len(vals) > 0:
            med = np.median(vals)
            iqr = np.percentile(vals, 75) - np.percentile(vals, 25)
            ind = result_df[f"{algo_key}_indicator"].values[0]
            best = " *BEST*" if result_df["best_algo"].values[0] == algo_key else ""
            print(
                f"  {display:12s}: median={med:.6f} IQR={iqr:.6f} {ind}{best} (n={len(vals)})"
            )
        else:
            print(f"  {display:12s}: no data")

    print(f"\n{'=' * 60}")
    print(f"All outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
