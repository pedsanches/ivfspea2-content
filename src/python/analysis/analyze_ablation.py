#!/usr/bin/env python3
"""
Ablation Study Analysis (Point C)
===================================
Parses PlatEMO .mat result files from the ablation experiments and generates:
  1. LaTeX table: median(IQR) per variant per problem, Wilcoxon indicators, bold best
  2. CSV with per-run IGD values
  3. Box-plot figure comparing the 4 variants across problems

Expected input layout:
  data/ablation/<ALGO>_<PROB>_M<X>/*.mat

Each .mat contains:
  - metric.IGD  (scalar or array; we take the last/only value)
"""

import os
import sys
import warnings
from collections import defaultdict

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
ABLATION_DIR = os.path.join(PROJECT_ROOT, "data", "ablation")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "ablation")
ALPHA = 0.05

VARIANTS = [
    ("IVFSPEA2", "IVF/SPEA2 (top-2c)"),
    ("IVFSPEA2ABL1C", "top-1c"),
    ("IVFSPEA2ABL4C", "top-4c"),
    ("IVFSPEA2ABLDOM", "dominance"),
]

PROBLEMS = [
    ("ZDT1", 2),
    ("WFG4", 2),
    ("DTLZ1", 3),
    ("DTLZ7", 3),
    ("MaF1", 3),
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


def load_ablation_data() -> pd.DataFrame:
    """Scan ablation directory and collect per-run IGD values."""
    rows = []
    if not os.path.isdir(ABLATION_DIR):
        print(f"ERROR: Ablation directory not found: {ABLATION_DIR}")
        return pd.DataFrame()

    for folder_name in sorted(os.listdir(ABLATION_DIR)):
        folder_path = os.path.join(ABLATION_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # Parse folder name: ALGO_PROB_MX
        parts = folder_name.split("_")
        if len(parts) < 3:
            continue
        algo = parts[0]
        prob = parts[1]
        m_str = parts[2]
        m_val = int(m_str.replace("M", ""))

        mat_files = [f for f in os.listdir(folder_path) if f.endswith(".mat")]
        for mat_file in mat_files:
            igd = load_igd_from_mat(os.path.join(folder_path, mat_file))
            if igd is not None:
                rows.append(
                    {
                        "Algorithm": algo,
                        "Problem": prob,
                        "M": m_val,
                        "IGD": igd,
                    }
                )

    df = pd.DataFrame(rows)
    if len(df) > 0:
        print(
            f"Loaded {len(df)} IGD values across {df['Algorithm'].nunique()} variants"
        )
    return df


# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------


def wilcoxon_test(x: np.ndarray, y: np.ndarray) -> str:
    """Mann-Whitney U test. Returns '+' if x < y, '-' if x > y, '=' otherwise."""
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
    """Format as compact scientific notation: m.mm(i.ii)e+E"""
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


def generate_ablation_table(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Generate results DataFrame and LaTeX table."""
    variant_names = [v[0] for v in VARIANTS]
    variant_display = {v[0]: v[1] for v in VARIANTS}

    rows = []
    for prob, m_val in PROBLEMS:
        row = {"Problem": f"{prob}(M={m_val})"}

        # Get baseline (top-2c) data
        base_data = df[
            (df["Algorithm"] == "IVFSPEA2")
            & (df["Problem"] == prob)
            & (df["M"] == m_val)
        ]["IGD"].values

        best_median = np.inf
        best_algo = ""

        for algo_key, _ in VARIANTS:
            algo_data = df[
                (df["Algorithm"] == algo_key)
                & (df["Problem"] == prob)
                & (df["M"] == m_val)
            ]["IGD"].values

            if len(algo_data) == 0:
                row[f"{algo_key}_formatted"] = "---"
                row[f"{algo_key}_median"] = np.nan
                row[f"{algo_key}_indicator"] = ""
                continue

            med = np.median(algo_data)
            row[f"{algo_key}_formatted"] = format_median_iqr(algo_data)
            row[f"{algo_key}_median"] = med

            if med < best_median:
                best_median = med
                best_algo = algo_key

            # Wilcoxon vs baseline (top-2c)
            if algo_key != "IVFSPEA2" and len(base_data) > 0:
                row[f"{algo_key}_indicator"] = wilcoxon_test(base_data, algo_data)
            else:
                row[f"{algo_key}_indicator"] = ""

        row["best_algo"] = best_algo
        rows.append(row)

    result_df = pd.DataFrame(rows)

    # Generate LaTeX
    n_algo = len(variant_names)
    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(
        r"\caption{Ablation study: median IGD (IQR) over 30 runs. "
        r"Symbols: $+$ = top-2c significantly better, "
        r"$-$ = significantly worse, "
        r"$\approx$ = no significant difference (Wilcoxon, $\alpha=0.05$). "
        r"Best median per instance in \textbf{bold}.}"
    )
    lines.append(r"\label{tab:ablation}")
    lines.append(r"\centering\scriptsize")
    lines.append(r"\begin{tabular}{l" + "r" * n_algo + "}")
    lines.append(r"\toprule")

    # Header
    header = ["Problem"] + [variant_display[v] for v in variant_names]
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")

    for _, row in result_df.iterrows():
        parts = [row["Problem"]]
        for algo_key in variant_names:
            cell = row.get(f"{algo_key}_formatted", "---")
            indicator = row.get(f"{algo_key}_indicator", "")

            if row.get("best_algo") == algo_key:
                cell = r"\textbf{" + cell + "}"

            if indicator == "+":
                cell += r"$^{+}$"
            elif indicator == "-":
                cell += r"$^{-}$"
            elif indicator == "=":
                cell += r"$^{\approx}$"

            parts.append(cell)
        lines.append(" & ".join(parts) + r" \\")

    # Summary row
    lines.append(r"\midrule")
    summary_parts = [r"$+/\approx/-$"]
    for algo_key in variant_names:
        if algo_key == "IVFSPEA2":
            summary_parts.append("---")
        else:
            indicators = result_df[f"{algo_key}_indicator"].tolist()
            w = indicators.count("+")
            t = indicators.count("=")
            l = indicators.count("-")
            summary_parts.append(f"{w}/{t}/{l}")
    lines.append(" & ".join(summary_parts) + r" \\")

    lines.append(r"\botrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return result_df, "\n".join(lines)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_ablation_boxplots(df: pd.DataFrame):
    """Generate box-plot figure comparing variants across problems."""
    fig, axes = plt.subplots(
        1, len(PROBLEMS), figsize=(4 * len(PROBLEMS), 4), sharey=False
    )
    if len(PROBLEMS) == 1:
        axes = [axes]

    variant_names = [v[0] for v in VARIANTS]
    variant_display = [v[1] for v in VARIANTS]
    colors = ["#2196F3", "#FF9800", "#4CAF50", "#F44336"]

    for idx, (prob, m_val) in enumerate(PROBLEMS):
        ax = axes[idx]
        data_list = []
        labels = []
        for v_idx, (algo_key, display) in enumerate(VARIANTS):
            vals = df[
                (df["Algorithm"] == algo_key)
                & (df["Problem"] == prob)
                & (df["M"] == m_val)
            ]["IGD"].values
            if len(vals) > 0:
                data_list.append(vals)
                labels.append(display)

        if data_list:
            bp = ax.boxplot(data_list, labels=labels, patch_artist=True, widths=0.6)
            for patch, color in zip(bp["boxes"], colors[: len(data_list)]):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

        ax.set_title(f"{prob} (M={m_val})", fontsize=10)
        ax.set_ylabel("IGD" if idx == 0 else "")
        ax.tick_params(axis="x", rotation=45, labelsize=8)

    plt.suptitle("Ablation Study: Acceptance Criterion Variants", fontsize=12, y=1.02)
    plt.tight_layout()

    fig_path = os.path.join(OUTPUT_DIR, "ablation_boxplots.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 60)
    print("ABLATION STUDY ANALYSIS (Point C)")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_ablation_data()
    if df.empty:
        print("No ablation data found. Run experiments first.")
        sys.exit(0)

    # CSV with all raw values
    csv_path = os.path.join(OUTPUT_DIR, "ablation_raw_igd.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved raw data: {csv_path}")

    # Table
    result_df, latex = generate_ablation_table(df)
    tex_path = os.path.join(OUTPUT_DIR, "ablation_table.tex")
    with open(tex_path, "w") as f:
        f.write(latex)
    print(f"Saved LaTeX: {tex_path}")

    summary_csv = os.path.join(OUTPUT_DIR, "ablation_summary.csv")
    result_df.to_csv(summary_csv, index=False)
    print(f"Saved summary: {summary_csv}")

    # Box plots
    plot_ablation_boxplots(df)

    # Print results to console
    print("\n--- Results Summary ---")
    for _, row in result_df.iterrows():
        print(f"\n{row['Problem']}:")
        for algo_key, display in VARIANTS:
            fmt = row.get(f"{algo_key}_formatted", "---")
            ind = row.get(f"{algo_key}_indicator", "")
            best = " *BEST*" if row.get("best_algo") == algo_key else ""
            print(f"  {display:20s}: {fmt} {ind}{best}")

    print(f"\n{'=' * 60}")
    print(f"All outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
