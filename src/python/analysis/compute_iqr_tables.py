#!/usr/bin/env python3
"""
Compute IQR Tables for IGD Results
====================================
Generates LaTeX-ready tables with median (IQR) for IGD values,
replacing the current median-only tables in the manuscript.

Uses: data/processed/todas_metricas_consolidado.csv
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results")

ALGORITHMS = ["IVFSPEA2", "MFOSPEA2", "SPEA2SDE", "NSGAII", "NSGAIII", "MOEAD", "SPEA2"]
ALGO_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "SPEA2": "SPEA2",
}


def format_sci(val: float, iqr: float) -> str:
    """Format a value in scientific notation with IQR."""
    if pd.isna(val) or pd.isna(iqr):
        return "---"
    exp = int(np.floor(np.log10(abs(val)))) if val != 0 else 0
    mantissa = val / (10**exp)
    iqr_mantissa = iqr / (10**exp)
    return f"{mantissa:.2f} ({iqr_mantissa:.2f})e{exp:+d}"


def compute_dispersion_table(df: pd.DataFrame, m_filter: str) -> pd.DataFrame:
    """
    For each Problem × Algorithm, compute median and IQR of IGD.
    """
    subset = df[df["M"] == m_filter].copy()

    results = []
    for (prob, d), prob_group in subset.groupby(["Problema", "D"]):
        row = {"Problema": prob, "D": d}
        for algo in ALGORITHMS:
            algo_data = prob_group[prob_group["Algoritmo"] == algo]["IGD"].dropna()
            if len(algo_data) > 0:
                median = algo_data.median()
                q25 = algo_data.quantile(0.25)
                q75 = algo_data.quantile(0.75)
                iqr = q75 - q25
                row[f"{algo}_median"] = median
                row[f"{algo}_iqr"] = iqr
                row[f"{algo}_q25"] = q25
                row[f"{algo}_q75"] = q75
                row[f"{algo}_std"] = algo_data.std()
            else:
                row[f"{algo}_median"] = np.nan
                row[f"{algo}_iqr"] = np.nan
        results.append(row)

    return pd.DataFrame(results)


def print_dispersion_summary(disp_df: pd.DataFrame, m_filter: str):
    """Print human-readable summary of dispersion data."""
    print(f"\n{'=' * 60}")
    print(f"IGD Dispersion Summary for {m_filter}")
    print(f"{'=' * 60}")
    for _, row in disp_df.iterrows():
        print(f"\n{row['Problema']} (D={row['D']}):")
        for algo in ALGORITHMS:
            med = row.get(f"{algo}_median", np.nan)
            iqr = row.get(f"{algo}_iqr", np.nan)
            if not pd.isna(med):
                print(f"  {ALGO_DISPLAY[algo]:12s}: median={med:.6e}, IQR={iqr:.6e}")


def main():
    print("=" * 60)
    print("IGD Dispersion (Median + IQR) Table Generator")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    print(f"M values: {sorted(df['M'].unique())}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for m_val in sorted(df["M"].unique()):
        disp_df = compute_dispersion_table(df, m_val)

        # Save CSV
        csv_path = os.path.join(OUTPUT_DIR, f"igd_dispersion_{m_val}.csv")
        disp_df.to_csv(csv_path, index=False)
        print(f"Saved {csv_path}")

        # Print summary
        print_dispersion_summary(disp_df, m_val)

    return disp_df


if __name__ == "__main__":
    main()
