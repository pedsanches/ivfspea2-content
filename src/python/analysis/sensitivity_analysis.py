import os
import re
import numpy as np
import pandas as pd
import scipy.io
from collections import defaultdict

BASE_DIR = "/home/pedro/desenvolvimento/ivfspea2/data/raw/Experimentos_Platemo"
OUTPUT_CSV = "/home/pedro/desenvolvimento/ivfspea2/results/sensitivity_analysis_igd.csv"

# Regex patterns
REGEX_TYPE1 = re.compile(r"IVFSPEA2_2OBJ_R([\d\.]+)_C([\d\.]+)")
REGEX_TYPE2 = re.compile(r"IVFSPEA2_R([\d\.]+)_C(\d+)_([A-Za-z0-9]+)")


def extract_metric(filepath):
    try:
        mat = scipy.io.loadmat(filepath)
        if "metric" not in mat:
            return None

        m = mat["metric"]
        val = None

        # Handle scalar (Type 1)
        if m.shape == (1, 1) and m.dtype.names is None:
            val = m[0, 0]

        # Handle struct (Type 2)
        elif m.shape == (1, 1) and m.dtype.names is not None:
            if "IGD" in m.dtype.names:
                val = m["IGD"][0, 0]
            else:
                val = m[0, 0][0]  # Heuristic

        # Handle flattened struct (void)
        elif m.size == 1 and m.dtype.names is None:
            tup = m[0, 0]
            if isinstance(tup, (tuple, list, np.void)) and len(tup) > 0:
                first = tup[0]
                # If first element is array (history), take min
                if isinstance(first, np.ndarray):
                    val = np.min(first)
                elif hasattr(first, "item"):
                    val = first

        # Final extraction from array/scalar
        if val is not None:
            if isinstance(val, np.ndarray):
                if val.size > 1:
                    return float(np.min(val))  # Take best IGD from history
                return float(val.item())
            return float(val)

        return None
    except Exception:
        return None


def process_folders():
    # Dictionary to collect results: (Problem, R, C) -> list of values
    aggregated_data = defaultdict(list)

    folders = sorted(os.listdir(BASE_DIR))
    print(f"Scanning {BASE_DIR}...")

    count_folders = 0
    for folder in folders:
        full_path = os.path.join(BASE_DIR, folder)
        if not os.path.isdir(full_path):
            continue

        # Parse params
        r, c, folder_problem = None, None, None

        m1 = REGEX_TYPE1.match(folder)
        m2 = REGEX_TYPE2.match(folder)

        if m1:
            r = float(m1.group(1))
            c = float(m1.group(2))
            # folder_problem remains None, will be inferred per file
        elif m2:
            r = float(m2.group(1))
            c_int = int(m2.group(2))
            c = c_int / 100.0 if c_int > 1 else c_int
            folder_problem = m2.group(3)
        else:
            continue

        count_folders += 1
        if count_folders % 20 == 0:
            print(f"Processed {count_folders} matching folders...")

        # Iterate files
        files = [
            f
            for f in os.listdir(full_path)
            if f.endswith(".mat") and f.startswith("IVFSPEA2_")
        ]

        for file in files:
            # Infer problem
            current_problem = folder_problem
            if current_problem is None:  # Type 1
                parts = file.split("_")
                if len(parts) > 2:
                    current_problem = parts[1]  # e.g. DTLZ1

            if not current_problem:
                continue

            val = extract_metric(os.path.join(full_path, file))
            if (
                val is not None and not np.isnan(val) and val < 1000
            ):  # Filter text placeholders or huge errors
                aggregated_data[(current_problem, r, c)].append(val)

    # Convert to DataFrame
    results = []
    for (prob, r, c), vals in aggregated_data.items():
        results.append(
            {
                "Problem": prob,
                "R": r,
                "C": c,
                "IGD_Median": np.median(vals),
                "IGD_Mean": np.mean(vals),
                "IGD_Std": np.std(vals),
                "Count": len(vals),
            }
        )

    if results:
        df = pd.DataFrame(results)
        df.sort_values(by=["Problem", "R", "C"], inplace=True)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Saved {len(df)} configurations to {OUTPUT_CSV}")
        print("\nBreakdown by Problem:")
        print(df.groupby("Problem").size())
    else:
        print("No results found.")


if __name__ == "__main__":
    process_folders()
