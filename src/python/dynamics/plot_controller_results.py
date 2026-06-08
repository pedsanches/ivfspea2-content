#!/usr/bin/env python3
"""Generate fig5 for CLEI 2026: controller vs IVF vs SPEA2 with delta-HV dot plot."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE = "#1f77b4"
ORANGE = "#ff7f0e"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "xtick.labelsize": 7,
        "ytick.labelsize": 9,
        "legend.fontsize": 8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CTRL_CSV = PROJECT_ROOT / "data" / "processed" / "ppsn_controller_comparison.csv"
RESP_CSV = PROJECT_ROOT / "data" / "processed" / "fla_response.csv"
OUT_DIR = PROJECT_ROOT / "paper" / "ppsn2026" / "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate controller comparison delta-HV dot plot."
    )
    parser.add_argument(
        "--ctrl-csv",
        type=Path,
        default=CTRL_CSV,
        help="Controller comparison CSV. Default: %(default)s",
    )
    parser.add_argument(
        "--response-csv",
        type=Path,
        default=RESP_CSV,
        help="FLA response CSV for label. Default: %(default)s",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_DIR / "fig5_controller.pdf",
        help="Output figure path. Default: %(default)s",
    )
    return parser.parse_args()


def load_data(ctrl_csv: Path, response_csv: Path) -> pd.DataFrame:
    ctrl = pd.read_csv(ctrl_csv)
    resp = pd.read_csv(response_csv)
    resp["case_norm"] = resp["instance"].str.lower().str.replace("_m", "_m")
    hv = ctrl[ctrl["metric"] == "HV"].copy()
    hv = hv.merge(
        resp[["case_norm", "label_binary"]],
        left_on="case_id",
        right_on="case_norm",
        how="left",
    )
    return hv


def make_figure(hv: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.6), gridspec_kw={"wspace": 0.38})

    # Compute deltas
    hv["delta_ivf"] = hv["median_ctrl"] - hv["median_ivf"]
    hv["delta_spea2"] = hv["median_ctrl"] - hv["median_spea2"]

    # Extract family from case_id (e.g., "dtlz3_m2" -> "DTLZ")
    def family_of(case_id: str) -> str:
        c = case_id.lower()
        if c.startswith("zdt"):
            return "ZDT"
        if c.startswith("dtlz"):
            return "DTLZ"
        if c.startswith("wfg"):
            return "WFG"
        if c.startswith("maf"):
            return "MaF"
        return "Other"

    hv["family"] = hv["case_id"].apply(family_of)

    helps = hv[hv["label_binary"] == "HELPS"]
    not_helps = hv[hv["label_binary"] == "NOT_HELPS"]

    for ax_idx, (delta_col, comparator_label) in enumerate(
        [("delta_ivf", "IVF-SPEA2"), ("delta_spea2", "SPEA2")]
    ):
        ax = axes[ax_idx]

        # Sort all cases by delta for visual clarity
        hv_sorted = hv.sort_values(delta_col)
        x_positions = list(range(len(hv_sorted)))

        for i, (_, row) in enumerate(hv_sorted.iterrows()):
            is_wfg = row["family"] == "WFG"
            is_helpful = row["label_binary"] == "HELPS"
            delta = row[delta_col]

            if is_helpful:
                color = BLUE
                marker = "D" if is_wfg else "o"
            else:
                color = ORANGE
                marker = "s" if is_wfg else "^"

            ax.axvline(x=i, color="lightgray", linewidth=0.3, alpha=0.4)
            ax.scatter(
                i,
                delta,
                c=color,
                marker=marker,
                s=36,
                alpha=0.85,
                edgecolors="white",
                linewidths=0.3,
                zorder=3,
            )

        # Zero reference line
        ax.axhline(y=0, color="black", linewidth=0.6, linestyle="-", alpha=0.7)

        # Shaded regions: above zero = controller wins, below = controller loses
        y_min = min(hv_sorted[delta_col].min() * 1.2, -0.01)
        y_max = max(hv_sorted[delta_col].max() * 1.2, 0.01)
        ax.fill_between(
            [-1, len(hv_sorted)],
            0,
            y_max,
            color=BLUE,
            alpha=0.04,
            zorder=0,
        )
        ax.fill_between(
            [-1, len(hv_sorted)],
            y_min,
            0,
            color=ORANGE,
            alpha=0.04,
            zorder=0,
        )

        ax.set_xlim(-0.8, len(hv_sorted) - 0.2)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(r"Instance (sorted by $\Delta$HV)")
        ax.set_ylabel(
            rf"$\Delta$HV = HV(CTRL) $-$ HV({comparator_label})"
        )
        ax.set_title(f"(a) Controller vs {comparator_label}" if ax_idx == 0
                     else f"(b) Controller vs {comparator_label}")

        ax.grid(True, alpha=0.2, linewidth=0.4, axis="y")

    # Shared legend below figure
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=BLUE,
                    markersize=8, label="Helpful (non-WFG)"),
        plt.Line2D([0], [0], marker="D", color="w", markerfacecolor=BLUE,
                    markersize=8, label="Helpful (WFG)"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor=ORANGE,
                    markersize=8, label="Not helpful (non-WFG)"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=ORANGE,
                    markersize=8, label="Not helpful (WFG)"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=4,
        frameon=True,
        framealpha=0.85,
        edgecolor="lightgray",
        bbox_to_anchor=(0.5, -0.02),
    )

    return fig


def main() -> None:
    args = parse_args()
    hv = load_data(args.ctrl_csv, args.response_csv)
    fig = make_figure(hv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Saved: {args.out}")

    # Print summary stats
    helps = hv[hv["label_binary"] == "HELPS"]
    not_helps = hv[hv["label_binary"] == "NOT_HELPS"]
    print(f"\nHelpful cases: {len(helps)}, Not helpful cases: {len(not_helps)}")

    hv["delta_ivf"] = hv["median_ctrl"] - hv["median_ivf"]
    hv["delta_spea2"] = hv["median_ctrl"] - hv["median_spea2"]
    print(f"  Delta IVF: above={int((hv['delta_ivf'] > 0).sum())}, below={int((hv['delta_ivf'] < 0).sum())}")
    print(f"  Delta SPEA2: above={int((hv['delta_spea2'] > 0).sum())}, below={int((hv['delta_spea2'] < 0).sum())}")

    # WFG-specific breakdown
    wfg = hv[hv["case_id"].str.lower().str.startswith("wfg")]
    if len(wfg) > 0:
        print(f"\nWFG cases ({len(wfg)}):")
        print(f"  Delta IVF WFG: above={int((wfg['delta_ivf'] > 0).sum())}, below={int((wfg['delta_ivf'] < 0).sum())}")
        print(f"  Delta SPEA2 WFG: above={int((wfg['delta_spea2'] > 0).sum())}, below={int((wfg['delta_spea2'] < 0).sum())}")


if __name__ == "__main__":
    main()
