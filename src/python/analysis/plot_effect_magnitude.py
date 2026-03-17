#!/usr/bin/env python3
"""
Generate effect-magnitude figure: median % IGD improvement of IVF/SPEA2
over SPEA2 on each synthetic instance, split by M and OOS status.

Output:
  paper/figures/effect_magnitude_igd.pdf

Usage:
  python src/python/analysis/plot_effect_magnitude.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort

# ---------- paths ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
DATA_PATH = os.path.join(
    PROJECT_ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
OUT_DIR = os.path.join(PROJECT_ROOT, "paper", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- style ----------
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 8,
        "axes.labelsize": 9,
        "axes.titlesize": 9,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    }
)

# ---------- FULL12 tuning subset ----------
FULL12 = {
    ("ZDT1", 2),
    ("ZDT6", 2),
    ("WFG4", 2),
    ("WFG9", 2),
    ("DTLZ1", 3),
    ("DTLZ2", 3),
    ("DTLZ4", 3),
    ("DTLZ7", 3),
    ("WFG2", 3),
    ("WFG5", 3),
    ("MaF1", 3),
    ("MaF5", 3),
}

# Suite ordering
SUITE_ORDER = ["ZDT", "DTLZ", "WFG", "MaF"]


def get_suite(prob):
    for s in SUITE_ORDER:
        if prob.startswith(s):
            return s
    return "Other"


def main():
    raw_df = pd.read_csv(DATA_PATH)
    df = filter_submission_synthetic_cohort(raw_df)

    # Normalize column names (CSV uses Portuguese names)
    col_map = {"Problema": "Problem", "Algoritmo": "Algorithm"}
    df = df.rename(columns=col_map)

    # Normalize algorithm names
    df["Algorithm"] = df["Algorithm"].str.replace("-", "").str.replace("_", "")

    # Normalize M column (may be "M2"/"M3" strings)
    if df["M"].dtype == object:
        df["M_int"] = df["M"].str.replace("M", "").astype(int)
    else:
        df["M_int"] = df["M"]

    # Build per-instance medians
    rows = []
    for (prob, m_str), grp in df.groupby(["Problem", "M"]):
        m = int(str(m_str).replace("M", ""))
        ivf = grp[grp["Algorithm"] == "IVFSPEA2"]["IGD"]
        spea2 = grp[grp["Algorithm"] == "SPEA2"]["IGD"]
        if ivf.empty or spea2.empty:
            continue

        med_ivf = ivf.median()
        med_spea2 = spea2.median()

        if med_spea2 == 0:
            continue

        # Positive = IVF/SPEA2 is better (lower IGD)
        pct_improvement = (med_spea2 - med_ivf) / med_spea2 * 100
        is_oos = (prob, m) not in FULL12
        suite = get_suite(prob)

        rows.append(
            {
                "Problem": prob,
                "M": m,
                "suite": suite,
                "pct_improvement": pct_improvement,
                "is_oos": is_oos,
                "label": f"{prob}",
            }
        )

    results = pd.DataFrame(rows)

    # Sort: by suite order, then by problem name within suite
    results["suite_idx"] = results["suite"].map(
        {s: i for i, s in enumerate(SUITE_ORDER)}
    )
    results = results.sort_values(["suite_idx", "Problem"]).reset_index(drop=True)

    # Create figure: one panel per M
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.5), sharex=False)

    for ax_idx, m_val in enumerate([2, 3]):
        ax = axes[ax_idx]
        sub = results[results["M"] == m_val].reset_index(drop=True)

        colors = []
        for _, row in sub.iterrows():
            if row["pct_improvement"] < 0:
                colors.append("#B2182B")  # red = degradation
            elif row["is_oos"]:
                colors.append("#2166AC")  # blue = OOS improvement
            else:
                colors.append("#92C5DE")  # light blue = FULL12 improvement

        # Clip extreme values for display; annotate outliers
        CLIP = 15  # percent
        display_vals = sub["pct_improvement"].copy()
        clipped = display_vals.abs() > CLIP
        display_vals = display_vals.clip(-CLIP, CLIP)

        bars = ax.barh(
            range(len(sub)), display_vals, color=colors, edgecolor="none", height=0.7
        )

        # Annotate clipped bars with true value
        for i, (idx, row) in enumerate(sub.iterrows()):
            if clipped.iloc[i]:
                val = row["pct_improvement"]
                x_pos = CLIP if val > 0 else -CLIP
                ax.text(
                    x_pos,
                    i,
                    f" {val:+.1f}%",
                    va="center",
                    ha="left" if val > 0 else "right",
                    fontsize=5.5,
                    style="italic",
                    color="gray",
                )

        ax.set_xlim(-CLIP - 1, CLIP + 1)
        ax.set_yticks(range(len(sub)))
        ax.set_yticklabels(sub["label"], fontsize=5.2)
        ax.invert_yaxis()
        ax.axvline(0, color="black", linewidth=0.5, linestyle="-")
        ax.set_xlabel("Median IGD improvement over SPEA2 (%)")
        ax.set_title(f"$M={m_val}$   ({len(sub)} instances)")

        # Add suite separators
        prev_suite = None
        for i, (_, row) in enumerate(sub.iterrows()):
            if prev_suite is not None and row["suite"] != prev_suite:
                ax.axhline(i - 0.5, color="gray", linewidth=0.3, linestyle="--")
            prev_suite = row["suite"]

        # Summary stats (use trimmed mean to exclude extreme bimodal cases)
        med = sub["pct_improvement"].median()
        trimmed = sub["pct_improvement"].clip(-50, 50)
        tmean = trimmed.mean()
        n_pos = (sub["pct_improvement"] > 0).sum()
        n_neg = (sub["pct_improvement"] < 0).sum()
        ax.text(
            0.98,
            0.02,
            f"median={med:+.2f}%  trimmed mean={tmean:+.2f}%  ({n_pos}$\\uparrow$ {n_neg}$\\downarrow$)",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=6.5,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.3", fc="wheat", alpha=0.7),
        )

    # Legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="#2166AC", label="Improvement (OOS)"),
        Patch(facecolor="#92C5DE", label="Improvement (FULL12)"),
        Patch(facecolor="#B2182B", label="Degradation"),
    ]
    fig.legend(
        handles=legend_elements,
        loc="upper center",
        ncol=3,
        frameon=False,
        fontsize=7,
        bbox_to_anchor=(0.5, 1.0),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = os.path.join(OUT_DIR, "effect_magnitude_igd.pdf")
    fig.savefig(out_path)
    print(f"Saved: {out_path}")

    # Also save PNG for quick viewing
    fig.savefig(out_path.replace(".pdf", ".png"))
    print(f"Saved: {out_path.replace('.pdf', '.png')}")

    # Print summary table
    print("\n--- Summary ---")
    for m_val in [2, 3]:
        sub = results[results["M"] == m_val]
        oos = sub[sub["is_oos"]]
        print(
            f"\nM={m_val}: median improvement = {sub['pct_improvement'].median():+.2f}%"
            f" (mean {sub['pct_improvement'].mean():+.2f}%)"
        )
        print(
            f"  OOS only: median = {oos['pct_improvement'].median():+.2f}%"
            f" (mean {oos['pct_improvement'].mean():+.2f}%)"
        )
        print(f"  Positive: {(sub['pct_improvement'] > 0).sum()}/{len(sub)}")


if __name__ == "__main__":
    main()
