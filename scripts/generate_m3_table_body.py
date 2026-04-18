#!/usr/bin/env python3
"""Generate LaTeX table body rows from IGD per-instance CSV files."""

import csv
import math
import sys
import os


def format_scientific(value: float) -> str:
    """Format a float as 'mantissa\\times 10^{exponent}' with 4 decimal digits in the mantissa."""
    if value == 0.0:
        return r"0.0000\times 10^{0}"
    exponent = math.floor(math.log10(abs(value)))
    mantissa = value / (10**exponent)
    return rf"{mantissa:.4f}\times 10^{{{exponent}}}"


def indicator_superscript(indicator: str) -> str:
    """Map indicator symbol to LaTeX superscript."""
    indicator = indicator.strip()
    if indicator == "+":
        return "^{+}"
    elif indicator == "-":
        return "^{-}"
    elif indicator == "=":
        return "^{=}"
    return ""


def format_cell(
    median: float, is_best: bool, indicator: str = "", is_reference: bool = False
) -> str:
    """Format a single cell value as LaTeX."""
    sci = format_scientific(median)
    if is_best:
        sci = rf"\textbf{{{sci}}}"
    sup = "" if is_reference else indicator_superscript(indicator)
    return rf"\(\,{sci}\,{sup}\)"


def generate_table_rows(csv_path: str) -> list[str]:
    """Read a CSV and produce LaTeX table rows.

    CSV column order: IVFSPEA2, SPEA2, MFOSPEA2, SPEA2SDE, NSGAII, NSGAIII, MOEAD
    Manuscript column order: IVF/SPEA2, MFO-SPEA2, SPEA2+SDE, NSGA-II, NSGA-III, MOEA/D, SPEA2

    IVF/SPEA2 indicator is relative to SPEA2 (uses SPEA2_indicator column from CSV — but
    note: the CSV stores the indicator for SPEA2 *against* IVF/SPEA2 in SPEA2_indicator;
    and IVF/SPEA2 has no indicator column filled in the CSV because it's the reference
    *within the CSV layout*.  However, the manuscript uses SPEA2 as the reference.
    So IVF/SPEA2's indicator in the manuscript = SPEA2_indicator column value).

    For baselines (MFO-SPEA2, SPEA2+SDE, NSGA-II, NSGA-III, MOEA/D): use their
    respective _indicator columns from the CSV.
    SPEA2 (last column in manuscript): no indicator (reference).
    """
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            problem = row["Problema"]
            d = row["D"]
            best_algo = row["best_algo"].strip()

            # Algorithm keys in CSV and their display mapping
            # CSV key -> (median col, indicator col, manuscript name)
            algos = [
                # Manuscript order: IVF/SPEA2, MFO-SPEA2, SPEA2+SDE, NSGA-II, NSGA-III, MOEA/D, SPEA2
                (
                    "IVFSPEA2",
                    "SPEA2_indicator",
                    "IVFSPEA2",
                ),  # indicator from SPEA2_indicator
                ("MFOSPEA2", "MFOSPEA2_indicator", "MFOSPEA2"),
                ("SPEA2SDE", "SPEA2SDE_indicator", "SPEA2SDE"),
                ("NSGAII", "NSGAII_indicator", "NSGAII"),
                ("NSGAIII", "NSGAIII_indicator", "NSGAIII"),
                ("MOEAD", "MOEAD_indicator", "MOEAD"),
                ("SPEA2", None, "SPEA2"),  # reference — no indicator
            ]

            cells = []
            for csv_key, ind_col, best_name in algos:
                median = float(row[f"{csv_key}_median"])
                is_best = best_algo == best_name
                is_reference = ind_col is None
                indicator = row[ind_col] if ind_col else ""
                cells.append(format_cell(median, is_best, indicator, is_reference))

            latex_row = f"{problem} & ${d}$ & " + " & ".join(cells) + r" \\"
            rows.append(latex_row)
    return rows


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # M=3
    m3_path = os.path.join(base, "results", "tables", "igd_per_instance_M3.csv")
    print("% ===== M=3 TABLE BODY =====")
    for row in generate_table_rows(m3_path):
        print(row)

    print()

    # M=2
    m2_path = os.path.join(base, "results", "tables", "igd_per_instance_M2.csv")
    print("% ===== M=2 TABLE BODY =====")
    for row in generate_table_rows(m2_path):
        print(row)


if __name__ == "__main__":
    main()
