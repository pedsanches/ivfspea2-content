#!/usr/bin/env python3
"""
Generate Per-Instance IGD and HV Tables with Statistical Tests
================================================================
Produces LaTeX-ready tables showing median (IQR) values per problem
instance, with Wilcoxon rank-sum statistical indicators (+/-/=) and
bold-face best values.  Tables are generated for both IGD (lower is
better) and HV (higher is better).

Designed to address Point H of the review: full auditability of results.

Inputs:
  - data/processed/todas_metricas_consolidado_with_modern.csv
    (all 9 algorithms with 100 % IGD + HV coverage)

Outputs:
  - results/tables/igd_per_instance_M2.tex / .csv
  - results/tables/igd_per_instance_M3.tex / .csv
  - results/tables/hv_per_instance_M2.tex  / .csv
  - results/tables/hv_per_instance_M3.tex  / .csv
"""

import os
import sys
import warnings
import re

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "tables")

# Algorithm ordering and display names
ALGORITHMS_CORE = [
    "IVFSPEA2",
    "SPEA2",
    "MFOSPEA2",
    "SPEA2SDE",
    "NSGAII",
    "NSGAIII",
    "MOEAD",
]
ALGORITHMS_NEW = ["AGEMOEAII", "ARMOEA"]

ALGO_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-II",
    "ARMOEA": "AR-MOEA",
}

# Problem ordering by suite
SUITE_ORDER = {"ZDT": 0, "DTLZ": 1, "WFG": 2, "MaF": 3, "RWMOP": 4}

ALPHA = 0.05  # Significance level for Wilcoxon test


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
def suite_sort_key(problem_name: str) -> tuple:
    """Generate a sort key for problem names (suite order, then numeric)."""
    for prefix, order in SUITE_ORDER.items():
        if problem_name.startswith(prefix):
            num_str = problem_name[len(prefix) :]
            try:
                num = int(num_str)
            except ValueError:
                num = 0
            return (order, num)
    return (99, 0)


def format_sci_compact(median_val: float, iqr_val: float) -> str:
    """Format median(IQR) in compact scientific notation for LaTeX."""
    if pd.isna(median_val) or pd.isna(iqr_val):
        return "---"
    if median_val == 0:
        return "0.00(0.00)e+0"
    exp = int(np.floor(np.log10(abs(median_val))))
    m = median_val / (10**exp)
    i = iqr_val / (10**exp)
    return f"{m:.2f}({i:.2f})e{exp:+d}"


def wilcoxon_test(
    x: np.ndarray, y: np.ndarray, alpha: float = ALPHA, higher_is_better: bool = False
) -> str:
    """
    Two-sided Wilcoxon rank-sum (Mann-Whitney U) test.

    When higher_is_better=False (IGD):
        Returns '+' if x is significantly better (lower) than y.
    When higher_is_better=True (HV):
        Returns '+' if x is significantly better (higher) than y.

    Returns '-' if x is significantly worse, '=' if no significant difference.
    """
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    if len(x) < 3 or len(y) < 3:
        return "="
    try:
        _, p_value = mannwhitneyu(x, y, alternative="two-sided")
        if p_value < alpha:
            med_x, med_y = np.median(x), np.median(y)
            if higher_is_better:
                if med_x > med_y:
                    return "+"
                elif med_x < med_y:
                    return "-"
            else:
                if med_x < med_y:
                    return "+"
                elif med_x > med_y:
                    return "-"
        return "="
    except Exception:
        return "="


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------
def compute_per_instance_table(
    df: pd.DataFrame,
    m_filter: str,
    algorithms: list,
    metric: str = "IGD",
    higher_is_better: bool = False,
) -> pd.DataFrame:
    """
    Compute per-instance statistics table for a given metric.
    Returns DataFrame with one row per problem, columns for each algorithm's
    median, IQR, and Wilcoxon indicator vs IVF/SPEA2.
    """
    subset = df[df["M"] == m_filter].copy()
    problems = sorted(subset["Problema"].unique(), key=suite_sort_key)

    results = []
    for prob in problems:
        prob_data = subset[subset["Problema"] == prob]
        row = {"Problema": prob}

        # Get D value
        d_vals = prob_data["D"].unique()
        if len(d_vals) > 0:
            d_raw = d_vals[0]
            if isinstance(d_raw, str):
                m = re.search(r"\d+", d_raw)
                row["D"] = int(m.group()) if m else 0
            else:
                row["D"] = int(d_raw)
        else:
            row["D"] = 0

        # Get IVF/SPEA2 data for comparison
        ivf_data = (
            prob_data[prob_data["Algoritmo"] == "IVFSPEA2"][metric].dropna().values
        )

        for algo in algorithms:
            algo_data = (
                prob_data[prob_data["Algoritmo"] == algo][metric].dropna().values
            )

            if len(algo_data) > 0:
                median_val = np.median(algo_data)
                q25 = np.percentile(algo_data, 25)
                q75 = np.percentile(algo_data, 75)
                iqr_val = q75 - q25

                row[f"{algo}_median"] = median_val
                row[f"{algo}_iqr"] = iqr_val
                row[f"{algo}_formatted"] = format_sci_compact(median_val, iqr_val)

                # Wilcoxon test vs IVF/SPEA2
                if algo != "IVFSPEA2" and len(ivf_data) > 0:
                    indicator = wilcoxon_test(
                        ivf_data, algo_data, higher_is_better=higher_is_better
                    )
                    row[f"{algo}_indicator"] = indicator
                else:
                    row[f"{algo}_indicator"] = ""
            else:
                row[f"{algo}_median"] = np.nan
                row[f"{algo}_iqr"] = np.nan
                row[f"{algo}_formatted"] = "---"
                row[f"{algo}_indicator"] = ""

        # Determine best algorithm
        medians = {
            algo: row.get(f"{algo}_median", np.inf if not higher_is_better else -np.inf)
            for algo in algorithms
            if not pd.isna(row.get(f"{algo}_median", np.nan))
        }
        if medians:
            if higher_is_better:
                best_algo = max(medians, key=medians.get)
            else:
                best_algo = min(medians, key=medians.get)
            row["best_algo"] = best_algo
        else:
            row["best_algo"] = ""

        results.append(row)

    return pd.DataFrame(results)


def generate_latex_table(
    table_df: pd.DataFrame,
    m_filter: str,
    algorithms: list,
    metric: str = "IGD",
    higher_is_better: bool = False,
) -> str:
    """Generate a LaTeX longtable for the manuscript."""
    n_algo = len(algorithms)
    col_spec = "ll" + "r" * n_algo

    direction_note = "higher" if higher_is_better else "lower"
    metric_display = metric.upper()

    lines = []
    lines.append(r"\begin{longtable}{" + col_spec + "}")
    lines.append(
        r"\caption{Median "
        + metric_display
        + r" (IQR) across all "
        + m_filter
        + r" instances over 60 independent runs. "
        r"Symbols indicate Wilcoxon rank-sum test ($\alpha=0.05$) "
        r"of IVF/SPEA2 vs.\ each baseline: "
        r"$+$ (IVF/SPEA2 significantly better, i.e.\ "
        + direction_note
        + r" "
        + metric_display
        + r"), "
        r"$-$ (significantly worse), "
        r"$\approx$ (no significant difference). "
        r"Best median per instance in \textbf{bold}.}"
    )
    lines.append(
        r"\label{tab:"
        + metric.lower()
        + "_per_instance_"
        + m_filter.lower()
        + "}"
        + r"\\"
    )
    lines.append(r"\toprule")

    # Header
    header_parts = ["Problem", "$D$"]
    for algo in algorithms:
        header_parts.append(ALGO_DISPLAY.get(algo, algo))
    lines.append(" & ".join(header_parts) + r" \\")
    lines.append(r"\midrule")
    lines.append(r"\endfirsthead")

    # Continuation header
    lines.append(
        r"\multicolumn{"
        + str(n_algo + 2)
        + r"}{c}{{\textit{Continued from previous page}}} \\"
    )
    lines.append(r"\toprule")
    lines.append(" & ".join(header_parts) + r" \\")
    lines.append(r"\midrule")
    lines.append(r"\endhead")

    lines.append(r"\midrule")
    lines.append(
        r"\multicolumn{"
        + str(n_algo + 2)
        + r"}{r}{{\textit{Continued on next page}}} \\"
    )
    lines.append(r"\endfoot")
    lines.append(r"\botrule")
    lines.append(r"\endlastfoot")

    # Data rows
    current_suite = None
    for _, row in table_df.iterrows():
        prob = row["Problema"]
        suite = next((k for k in SUITE_ORDER if prob.startswith(k)), "Other")
        if suite != current_suite:
            if current_suite is not None:
                lines.append(r"\midrule")
            current_suite = suite

        parts = [prob, str(int(row["D"]))]
        for algo in algorithms:
            formatted = row.get(f"{algo}_formatted", "---")
            indicator = row.get(f"{algo}_indicator", "")

            # Bold if best
            if row.get("best_algo") == algo:
                cell = r"\textbf{" + formatted + "}"
            else:
                cell = formatted

            # Add indicator
            if indicator == "+":
                cell += r"$^{+}$"
            elif indicator == "-":
                cell += r"$^{-}$"
            elif indicator == "=":
                cell += r"$^{\approx}$"

            parts.append(cell)

        lines.append(" & ".join(parts) + r" \\")

    # Summary row: count wins/ties/losses
    lines.append(r"\midrule")
    summary_parts = [r"\multicolumn{2}{l}{$+/\approx/-$}"]
    for algo in algorithms:
        if algo == "IVFSPEA2":
            summary_parts.append("---")
        else:
            indicators = table_df[f"{algo}_indicator"].tolist()
            wins = indicators.count("+")
            ties = indicators.count("=")
            losses = indicators.count("-")
            summary_parts.append(f"{wins}/{ties}/{losses}")
    lines.append(" & ".join(summary_parts) + r" \\")

    lines.append(r"\end{longtable}")

    return "\n".join(lines)


def compute_summary_table(table_df: pd.DataFrame, algorithms: list) -> dict:
    """Compute aggregate wins/ties/losses summary."""
    summary = {}
    for algo in algorithms:
        if algo == "IVFSPEA2":
            continue
        indicators = table_df[f"{algo}_indicator"].tolist()
        summary[algo] = {
            "wins": indicators.count("+"),
            "ties": indicators.count("="),
            "losses": indicators.count("-"),
        }
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Per-Instance Table Generator (IGD + HV)")
    print("=" * 70)

    # Load consolidated data and apply canonical synthetic run-cohort filter.
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Data file not found: {DATA_PATH}")
        sys.exit(1)

    raw_df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(raw_df)} rows from consolidated data")

    df = filter_submission_synthetic_cohort(raw_df)
    print(f"Rows after canonical synthetic cohort filter: {len(df)}")
    print(f"Algorithms: {sorted(df['Algoritmo'].unique())}")
    print(f"M values: {sorted(df['M'].unique())}")

    # Verify HV coverage
    n_igd = df["IGD"].notna().sum()
    n_hv = df["HV"].notna().sum()
    print(f"IGD coverage: {n_igd}/{len(df)}")
    print(f"HV coverage:  {n_hv}/{len(df)}")

    # Determine available algorithms
    available_algos = set(df["Algoritmo"].unique())
    algorithms = [a for a in ALGORITHMS_CORE + ALGORITHMS_NEW if a in available_algos]
    print(f"\nAlgorithms for tables: {algorithms}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Metric configurations: (metric_name, higher_is_better, file_prefix)
    metrics = [
        ("IGD", False, "igd"),
        ("HV", True, "hv"),
    ]

    for metric_name, higher_is_better, prefix in metrics:
        direction = "higher is better" if higher_is_better else "lower is better"
        print(f"\n{'=' * 50}")
        print(f"Generating {metric_name} tables ({direction})")
        print(f"{'=' * 50}")

        for m_val in sorted(df["M"].unique()):
            print(f"\n--- {metric_name} table for {m_val} ---")

            table_df = compute_per_instance_table(
                df,
                m_val,
                algorithms,
                metric=metric_name,
                higher_is_better=higher_is_better,
            )

            if len(table_df) == 0:
                print(f"  No data for {m_val}, skipping")
                continue

            # Save CSV
            csv_path = os.path.join(OUTPUT_DIR, f"{prefix}_per_instance_{m_val}.csv")
            table_df.to_csv(csv_path, index=False)
            print(f"  Saved CSV: {csv_path}")

            # Generate LaTeX
            latex = generate_latex_table(
                table_df,
                m_val,
                algorithms,
                metric=metric_name,
                higher_is_better=higher_is_better,
            )
            tex_path = os.path.join(OUTPUT_DIR, f"{prefix}_per_instance_{m_val}.tex")
            with open(tex_path, "w") as f:
                f.write(latex)
            print(f"  Saved LaTeX: {tex_path}")

            # Print summary
            summary = compute_summary_table(table_df, algorithms)
            print(f"\n  Summary for {metric_name} {m_val} (IVF/SPEA2 vs baselines):")
            for algo, counts in summary.items():
                display = ALGO_DISPLAY.get(algo, algo)
                print(
                    f"    vs {display:12s}: "
                    f"{counts['wins']}+ / {counts['ties']}= / {counts['losses']}-"
                )

    print(f"\n{'=' * 70}")
    print(f"All tables saved to: {OUTPUT_DIR}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
