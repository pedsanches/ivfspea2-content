import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

CSV_FILE = "/home/pedro/desenvolvimento/ivfspea2/results/sensitivity_analysis_igd.csv"
OUTPUT_DIR = "/home/pedro/desenvolvimento/ivfspea2/results/figures"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "sensitivity_heatmap_dtlz1.pdf")


def main():
    if not os.path.exists(CSV_FILE):
        print(f"CSV not found: {CSV_FILE}")
        return

    df = pd.read_csv(CSV_FILE)

    # Filter for DTLZ1
    df_dtlz1 = df[df["Problem"] == "DTLZ1"]

    if df_dtlz1.empty:
        print("No data for DTLZ1")
        return

    # Pivot
    pivot_table = df_dtlz1.pivot(index="R", columns="C", values="IGD_Median")

    # Sort index/columns to be sure
    pivot_table.sort_index(axis=0, inplace=True)
    pivot_table.sort_index(axis=1, inplace=True)

    # Plot
    plt.figure(figsize=(10, 8))

    # Use matshow or imshow
    plt.imshow(
        pivot_table.values, cmap="RdYlBu_r", aspect="auto", origin="lower"
    )  # _r for reversed (Blue=Low/Good, Red=High/Bad)?
    # Usually RdYlBu: Red (High) -> Blue (Low).
    # IGD: Lower is better. So Blue is Good. Red is Bad.
    # Default RdYlBu goes Red->Blue. So Low(Blue) is high value? Wait.
    # RdYlBu: Red (negative/low) to Blue (positive/high)?
    # Let's check:
    # In RdYlBu, Red is low, Blue is high.
    # We want Low IGD (Good) to be distinct. Maybe Blue?
    # If Red is Low, then Red is Good.
    # Just use 'viridis_r' or similar?
    # 'RdYlBu' is standard.
    # Let's stick to 'RdYlBu'. If I want Low=Blue (Good), High=Red (Bad).
    # Then I need High=Red.
    # If RdYlBu maps Low->Red, High->Blue: I need to reverse it.

    # Let's use 'viridis_r' (Yellow=Low=Good? No, Viridis: Purple=Low, Yellow=High).
    # 'viridis_r': Yellow=Low, Purple=High.

    # Better: 'coolwarm'. Blue=Low, Red=High.
    # Low IGD (Blue) = Good. High IGD (Red) = Bad.
    # perfect.

    plt.imshow(pivot_table.values, cmap="coolwarm", aspect="auto", origin="lower")

    plt.colorbar(label="IGD (Median)")

    # Ticks
    plt.xlabel("Collection Rate (C)")
    plt.ylabel("Execution Rate (R)")
    plt.title("Parameter Sensitivity Analysis - DTLZ1 (3-Obj)")

    # Set tick labels
    r_labels = pivot_table.index.astype(str)
    c_labels = pivot_table.columns.astype(str)

    plt.xticks(range(len(c_labels)), c_labels)
    plt.yticks(range(len(r_labels)), r_labels)

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    print(f"Saved figure to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
