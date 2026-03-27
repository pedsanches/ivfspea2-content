#!/usr/bin/env python3
"""Generate fig5 for PPSN 2026: controller vs IVF vs SPEA2 comparison."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CTRL_CSV = PROJECT_ROOT / "data" / "processed" / "ppsn_controller_comparison.csv"
RESP_CSV = PROJECT_ROOT / "data" / "processed" / "fla_response.csv"
OUT_DIR = PROJECT_ROOT / "paper" / "ppsn2026" / "figures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate controller comparison scatter plots."
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
        help="FLA response CSV for HELPS/NOT_HELPS labels. Default: %(default)s",
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
    hv = hv.merge(resp[["case_norm", "label_binary"]], left_on="case_id", right_on="case_norm", how="left")
    return hv


def make_figure(hv: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"wspace": 0.35})

    # --- Left panel: scatter CTRL vs IVF HV, colored by label ---
    ax = axes[0]
    helps = hv[hv["label_binary"] == "HELPS"]
    not_helps = hv[hv["label_binary"] == "NOT_HELPS"]

    ax.scatter(helps["median_ivf"], helps["median_ctrl"], c="#2196F3", marker="o",
               s=40, alpha=0.8, edgecolors="k", linewidths=0.3, label="HELPS", zorder=3)
    ax.scatter(not_helps["median_ivf"], not_helps["median_ctrl"], c="#F44336", marker="^",
               s=55, alpha=0.9, edgecolors="k", linewidths=0.3, label="NOT_HELPS", zorder=3)

    # diagonal reference
    lo = min(hv["median_ivf"].min(), hv["median_ctrl"].min()) * 0.98
    hi = max(hv["median_ivf"].max(), hv["median_ctrl"].max()) * 1.02
    ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, alpha=0.5, zorder=1)
    ax.set_xlabel("Median HV (IVF-SPEA2)", fontsize=9)
    ax.set_ylabel("Median HV (Controller)", fontsize=9)
    ax.set_title("(a) Controller vs IVF-SPEA2", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.tick_params(labelsize=8)

    # --- Right panel: scatter CTRL vs SPEA2 HV, colored by label ---
    ax = axes[1]
    ax.scatter(helps["median_spea2"], helps["median_ctrl"], c="#2196F3", marker="o",
               s=40, alpha=0.8, edgecolors="k", linewidths=0.3, label="HELPS", zorder=3)
    ax.scatter(not_helps["median_spea2"], not_helps["median_ctrl"], c="#F44336", marker="^",
               s=55, alpha=0.9, edgecolors="k", linewidths=0.3, label="NOT_HELPS", zorder=3)

    lo2 = min(hv["median_spea2"].min(), hv["median_ctrl"].min()) * 0.98
    hi2 = max(hv["median_spea2"].max(), hv["median_ctrl"].max()) * 1.02
    ax.plot([lo2, hi2], [lo2, hi2], "k--", lw=0.8, alpha=0.5, zorder=1)
    ax.set_xlabel("Median HV (SPEA2)", fontsize=9)
    ax.set_ylabel("Median HV (Controller)", fontsize=9)
    ax.set_title("(b) Controller vs SPEA2", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.tick_params(labelsize=8)

    return fig


def main() -> None:
    args = parse_args()
    hv = load_data(args.ctrl_csv, args.response_csv)
    fig = make_figure(hv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Saved: {args.out}")

    # Print summary stats for the paper
    helps = hv[hv["label_binary"] == "HELPS"]
    not_helps = hv[hv["label_binary"] == "NOT_HELPS"]
    print(f"\nHELPS cases: {len(helps)}, NOT_HELPS cases: {len(not_helps)}")

    def classify_outcome(p_bh: pd.Series, a12: pd.Series) -> pd.Series:
        out = pd.Series(["T"] * len(p_bh), index=p_bh.index, dtype=object)
        sig = p_bh < 0.05
        out.loc[sig & (a12 > 0.56)] = "W"
        out.loc[sig & (a12 < 0.44)] = "L"
        return out

    for label, sub in [("HELPS", helps), ("NOT_HELPS", not_helps)]:
        out_ivf = classify_outcome(sub["p_bh_ctrl_vs_ivf"], sub["a12_ctrl_vs_ivf"])
        ctrl_w = int((out_ivf == "W").sum())
        tie = int((out_ivf == "T").sum())
        ivf_w = int((out_ivf == "L").sum())
        print(f"  {label} — CTRL vs IVF (HV): W={ctrl_w} T={tie} L={ivf_w}")

        out_spea2 = classify_outcome(sub["p_bh_ctrl_vs_spea2"], sub["a12_ctrl_vs_spea2"])
        ctrl_w2 = int((out_spea2 == "W").sum())
        tie2 = int((out_spea2 == "T").sum())
        sp_w2 = int((out_spea2 == "L").sum())
        print(f"  {label} — CTRL vs SPEA2 (HV): W={ctrl_w2} T={tie2} L={sp_w2}")


if __name__ == "__main__":
    main()
