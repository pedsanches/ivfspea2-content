#!/usr/bin/env python3
"""
Generate all 6 proposed figures for the PPSN 2026 paper.

Figures:
  6. Family-wise early-turnover separability (2x2 boxplots)
  7. Static vs dynamic classifier comparison (bar charts)
  8. Warmup horizon sensitivity (line chart)
  9. WFG failure mode (two-panel dot plot)
  10. IGD-label vs HV-outcome consistency (scatter)
  11. Study design schematic (flowchart)

Usage:
    python src/python/figures/generate_proposed_figures.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

from utils import (
    style_setup,
    save_figure,
    BLUE,
    ORANGE,
    GRAY,
    THRESHOLD_MAIN,
    THRESHOLD_WFG,
    FAMILY_ORDER,
    FAMILY_MARKERS,
    family_of,
    compute_a12,
    FIGURES_DIR,
    DATA_PROCESSED,
    PROJECT_ROOT,
)

style_setup()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats

# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------
DYNAMIC_CSV = DATA_PROCESSED / "dynamic_signal_test.csv"
CLASSIFIER_CSV = DATA_PROCESSED / "classifier_comparison.csv"
WARMUP_CSV = DATA_PROCESSED / "warmup_horizon_sensitivity.csv"
FLA_RESPONSE_CSV = DATA_PROCESSED / "fla_response.csv"
CONTROLLER_CSV = DATA_PROCESSED / "ppsn_controller_comparison.csv"

EARLY_FRAC = 0.20

# ===========================================================================
# Figure 6: Family-wise early-turnover separability
# ===========================================================================
def figure_family_separability() -> None:
    print("\n--- Figure 6: Family-wise early-turnover separability ---")
    if not DYNAMIC_CSV.exists():
        print(f"  ERROR: {DYNAMIC_CSV} not found. Skipping.")
        return

    df = pd.read_csv(DYNAMIC_CSV)
    label_col = "label_binary_eval" if "label_binary_eval" in df.columns else "label_binary"
    df = df.loc[np.isclose(df["early_frac"], EARLY_FRAC)].copy()
    df = df.loc[df[label_col].isin(["HELPS", "NOT_HELPS"])].copy()
    df["family"] = df["case_id"].apply(family_of)

    if df.empty:
        print("  ERROR: No labeled data at early_frac=0.20. Skipping.")
        return

    families_present = [f for f in FAMILY_ORDER if f in df["family"].values]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.0), sharey=False)
    axes = axes.flatten()

    for idx, fam in enumerate(families_present):
        ax = axes[idx]
        fam_df = df[df["family"] == fam].copy()

        helps = fam_df.loc[fam_df[label_col] == "HELPS", "ivf_turnover_early"].dropna()
        not_helps = fam_df.loc[fam_df[label_col] == "NOT_HELPS", "ivf_turnover_early"].dropna()

        bp_data = [helps.values, not_helps.values]
        bp = ax.boxplot(
            bp_data,
            tick_labels=["Helpful", "Not helpful"],
            widths=0.5,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=1.2),
            flierprops=dict(marker="", markersize=0),
        )
        bp["boxes"][0].set_facecolor(BLUE)
        bp["boxes"][0].set_alpha(0.55)
        bp["boxes"][1].set_facecolor(ORANGE)
        bp["boxes"][1].set_alpha(0.55)

        jitter_strength = 0.12
        for _ in range(len(helps)):
            ax.scatter(
                np.random.default_rng().uniform(1 - jitter_strength, 1 + jitter_strength),
                helps.values[_],
                c=BLUE, marker="o", alpha=0.7, s=32,
                edgecolors="white", linewidths=0.4, zorder=3,
            )
        for _ in range(len(not_helps)):
            ax.scatter(
                np.random.default_rng().uniform(2 - jitter_strength, 2 + jitter_strength),
                not_helps.values[_],
                c=ORANGE, marker="^", alpha=0.7, s=32,
                edgecolors="white", linewidths=0.4, zorder=3,
            )

        threshold = THRESHOLD_WFG if fam == "WFG" else THRESHOLD_MAIN
        ax.axhline(y=threshold, color=GRAY, linestyle=":", linewidth=0.8, alpha=0.7,
                   zorder=1)
        ax.text(2.4, threshold + 0.003, rf"$\theta=${threshold:.3f}",
                fontsize=6, color=GRAY, alpha=0.8, ha="right", va="bottom")

        if len(helps) >= 3 and len(not_helps) >= 3:
            a12 = compute_a12(helps.to_numpy(), not_helps.to_numpy())
            ax.annotate(
                f"$n$={len(helps)}/{len(not_helps)}\n$\\hat{{A}}_{{12}}$={a12:.3f}",
                xy=(0.98, 0.95), xycoords="axes fraction",
                ha="right", va="top", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                          edgecolor="lightgray", alpha=0.85),
            )
        else:
            n_str = f"$n$={len(helps)}/{len(not_helps)}"
            if len(not_helps) <= 1:
                n_str += "\n(insufficient\nfor $\\hat{{A}}_{{12}}$)"
            ax.annotate(
                n_str,
                xy=(0.98, 0.95), xycoords="axes fraction",
                ha="right", va="top", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                          edgecolor="lightgray", alpha=0.85),
            )

        ax.set_title(f"({chr(97 + idx)}) {fam}", fontsize=9, fontweight="bold")
        ax.set_ylabel("Early turnover (first 20%)")
        ax.grid(True, alpha=0.25, linewidth=0.4, axis="y")

    # Hide unused subplots
    for idx in range(len(families_present), 4):
        axes[idx].set_visible(False)

    fig.tight_layout(w_pad=2.0, h_pad=2.5)
    save_figure(fig, "fig6_family_separability")


# ===========================================================================
# Figure 7: Static vs dynamic classifier comparison
# ===========================================================================
def figure_classifier_comparison() -> None:
    print("\n--- Figure 7: Static vs dynamic classifier comparison ---")
    if not CLASSIFIER_CSV.exists():
        print(f"  ERROR: {CLASSIFIER_CSV} not found. Run compute_classifier_comparison.py first.")
        return

    df = pd.read_csv(CLASSIFIER_CSV)
    # Use LFO-CV for the primary comparison (cross-family validation)
    lfo = df[df["validation"] == "LFO-CV"].copy()
    if lfo.empty:
        print("  ERROR: No LFO-CV rows in classifier_comparison.csv. Skipping.")
        return

    # Define method order
    method_order = [
        "RF (static features)",
        "LogReg (static features)",
        "RBF-SVC (static features)",
        "Early-turnover threshold",
    ]
    lfo = lfo.set_index("method").reindex(method_order).reset_index()
    lfo = lfo.dropna(subset=["balanced_accuracy", "mcc"])

    fig, axes = plt.subplots(2, 1, figsize=(3.4, 4.0))
    ax1, ax2 = axes

    # Bar params
    bar_w = 0.55
    x = np.arange(len(lfo))
    labels = [m.replace(" (static features)", "") for m in lfo["method"]]
    labels = [lbl.replace("Early-turnover threshold", "Early-turnover\nthreshold") for lbl in labels]

    static_mask = lfo["method"].str.contains("static", na=False).values
    dynamic_mask = ~static_mask

    # Panel (a): Balanced accuracy
    bars_a = ax1.bar(
        x, lfo["balanced_accuracy"], bar_w,
        color=[GRAY if s else BLUE for s in static_mask],
        alpha=0.75, edgecolor="white", linewidth=0.5, zorder=2,
    )
    for i, s in enumerate(static_mask):
        if s:
            bars_a[i].set_hatch("///")
    ax1.axhline(y=0.5, color="black", linestyle="--", linewidth=0.6, alpha=0.6,
                label="Random (0.5)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=6.5)
    ax1.set_ylabel("Balanced accuracy")
    ax1.set_ylim(0, 1.05)
    ax1.set_title("(a) Balanced accuracy", fontsize=9)
    ax1.grid(True, alpha=0.2, linewidth=0.4, axis="y")
    ax1.legend(fontsize=6, loc="lower right", framealpha=0.85)

    # Panel (b): MCC
    bars_b = ax2.bar(
        x, lfo["mcc"], bar_w,
        color=[GRAY if s else BLUE for s in static_mask],
        alpha=0.75, edgecolor="white", linewidth=0.5, zorder=2,
    )
    for i, s in enumerate(static_mask):
        if s:
            bars_b[i].set_hatch("///")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=6.5)
    ax2.set_ylabel("MCC")
    ax2.set_ylim(-0.35, 0.55)
    ax2.set_title("(b) MCC", fontsize=9)
    ax2.grid(True, alpha=0.2, linewidth=0.4, axis="y")

    fig.tight_layout(h_pad=1.2)
    save_figure(fig, "fig7_classifier_comparison")


# ===========================================================================
# Figure 8: Warmup horizon sensitivity
# ===========================================================================
def figure_warmup_horizon() -> None:
    print("\n--- Figure 8: Warmup horizon sensitivity ---")
    if not WARMUP_CSV.exists():
        print(f"  ERROR: {WARMUP_CSV} not found. Run compute_warmup_horizons.py first.")
        return

    df = pd.read_csv(WARMUP_CSV)
    x_pct = df["early_frac_pct"].values

    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(5.5, 5.0), sharex=True)

    # ---- Panel (a): Balanced accuracy ----
    ax_a.plot(x_pct, df["balanced_accuracy"], color=BLUE, linewidth=1.6,
              marker="o", markersize=6, label="Balanced accuracy", zorder=3)
    ax_a.set_ylim(0.55, 0.90)
    ax_a.set_ylabel("Balanced accuracy")
    ax_a.legend(fontsize=8, loc="lower right", framealpha=0.85,
                edgecolor="lightgray")
    ax_a.grid(True, alpha=0.2, linewidth=0.4)

    # 20% warmup marker
    ax_a.axvline(x=20, color=GRAY, linestyle="--", linewidth=1.0, alpha=0.7, zorder=1)
    ax_a.axvspan(18, 22, color=GRAY, alpha=0.07, zorder=0)

    # ---- Panel (b): Â12 discriminative strength ----
    ax_b.plot(x_pct, df["a12"], color=ORANGE, linewidth=1.6,
              marker="D", markersize=5, label=r"$\hat{A}_{12}$", zorder=3)
    ax_b.set_ylim(0.55, 0.95)
    ax_b.set_ylabel(r"$\hat{A}_{12}$")
    ax_b.legend(fontsize=8, loc="lower right", framealpha=0.85,
                edgecolor="lightgray")
    ax_b.grid(True, alpha=0.2, linewidth=0.4)

    # Reference: no discrimination
    ax_b.axhline(y=0.5, color=GRAY, linestyle=":", linewidth=0.6, alpha=0.5)

    # 20% warmup marker
    ax_b.axvline(x=20, color=GRAY, linestyle="--", linewidth=1.0, alpha=0.7, zorder=1)
    ax_b.axvspan(18, 22, color=GRAY, alpha=0.07, zorder=0)

    # Annotation on lower panel
    ax_b.annotate("20% warmup\n(chosen)", xy=(20, 0.825), fontsize=7,
                  color=GRAY, ha="center", va="top",
                  bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                            edgecolor="lightgray", alpha=0.85))

    ax_b.set_xlabel("Warmup horizon (% of generations)")
    ax_b.set_xlim(3, 32)

    fig.tight_layout()
    save_figure(fig, "fig8_warmup_horizon")


# ===========================================================================
# Figure 9: WFG failure mode
# ===========================================================================
def figure_wfg_failure_mode() -> None:
    print("\n--- Figure 9: WFG failure mode ---")
    if not DYNAMIC_CSV.exists():
        print(f"  ERROR: {DYNAMIC_CSV} not found. Skipping.")
        return
    if not CONTROLLER_CSV.exists():
        print(f"  ERROR: {CONTROLLER_CSV} not found. Skipping.")
        return

    # Load turnover data (WFG only, at 20%)
    dyn = pd.read_csv(DYNAMIC_CSV)
    label_col = "label_binary_eval" if "label_binary_eval" in dyn.columns else "label_binary"
    dyn = dyn.loc[np.isclose(dyn["early_frac"], EARLY_FRAC)].copy()
    dyn = dyn.loc[dyn[label_col].isin(["HELPS", "NOT_HELPS"])].copy()
    dyn["family"] = dyn["case_id"].apply(family_of)
    wfg_dyn = dyn[dyn["family"] == "WFG"].copy()
    if wfg_dyn.empty:
        print("  WARNING: No WFG cases in dynamic signal data.")
        return

    # Load controller performance
    ctrl = pd.read_csv(CONTROLLER_CSV)
    hv = ctrl[ctrl["metric"] == "HV"].copy()
    hv["family"] = hv["case_id"].apply(family_of)
    wfg_hv = hv[hv["family"] == "WFG"].copy()
    wfg_hv["delta_hv"] = wfg_hv["median_ctrl"] - wfg_hv["median_ivf"]

    # Merge
    merged = wfg_dyn.merge(
        wfg_hv[["case_id", "delta_hv", "median_ctrl", "median_ivf"]],
        on="case_id", how="left",
    )
    if merged["delta_hv"].isna().all():
        print("  WARNING: No HV data for WFG cases. Skipping.")
        return

    # Determine decision quality per case
    threshold = THRESHOLD_WFG
    merged["decision"] = "N/A"
    for i in merged.index:
        turnover = merged.loc[i, "ivf_turnover_early"]
        label = merged.loc[i, label_col]
        if pd.isna(turnover) or label not in ("HELPS", "NOT_HELPS"):
            continue
        kept = turnover >= threshold
        if label == "HELPS":
            merged.loc[i, "decision"] = "helpful_kept" if kept else "helpful_dropped"
        else:
            merged.loc[i, "decision"] = "nothelpful_dropped" if not kept else "nothelpful_kept"

    merged = merged.dropna(subset=["delta_hv", "decision"]).copy()
    # Sort by turnover for clean visual
    merged = merged.sort_values("ivf_turnover_early").reset_index(drop=True)

    # ── Visual encoding ──
    # Color  = actual usefulness:  BLUE = HELPS, ORANGE = NOT_HELPS
    # Shape  = controller decision: ▽ = dropped (all WFG cases are below θ)
    # Red ×  = controller error (overlaid when decision ≠ helpfulness)

    n = len(merged)
    x_labels = []
    for cid in merged["case_id"]:
        stem = str(cid).lower().replace("wfg", "")
        parts = stem.split("_m")
        x_labels.append(f"WFG{parts[0]}-M{parts[1]}" if len(parts) == 2 else cid)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 4.2), sharex=True)

    # ── Plot data ──
    for i, (_, row) in enumerate(merged.iterrows()):
        label = row[label_col]
        dec = row["decision"]
        is_error = (dec == "helpful_dropped")

        color = BLUE if label == "HELPS" else ORANGE
        marker = "o" if "kept" in dec else "v"

        kw = dict(s=64, alpha=0.9, edgecolors="#333333", linewidths=0.6)

        ax1.scatter(i, row["ivf_turnover_early"], marker=marker,
                    c=color, zorder=3, **kw)
        ax2.scatter(i, row["delta_hv"], marker=marker,
                    c=color, zorder=3, **kw)

        if is_error:
            ax1.scatter(i, row["ivf_turnover_early"],
                        marker="x", c="red", s=28, alpha=0.75, zorder=5,
                        linewidths=1.2)
            ax2.scatter(i, row["delta_hv"],
                        marker="x", c="red", s=28, alpha=0.75, zorder=5,
                        linewidths=1.2)

    # ── Panel (a): early turnover ──
    ax1.axhline(y=threshold, color=GRAY, linestyle=":", linewidth=1.0, alpha=0.7)
    ax1.text(n - 0.3, threshold + 0.006, r"below $\theta$: IVF deactivated",
             fontsize=6.5, color=GRAY, alpha=0.85, ha="right", va="bottom",
             style="italic")
    # Add θ as a y-axis tick at the threshold value
    yticks = [0.16, 0.18, 0.20, 0.22, 0.24, threshold]
    yticklabels = ["0.16", "0.18", "0.20", "0.22", "0.24", r"$\theta$"]
    ax1.set_yticks(yticks)
    ax1.set_yticklabels(yticklabels)
    ax1.grid(True, alpha=0.2, linewidth=0.4, axis="y")

    # ── Panel (b): ΔHV ──
    ax2.axhline(y=0, color="black", linewidth=0.6, linestyle="-", alpha=0.6)
    y_lo = merged["delta_hv"].min()
    ax2.axhspan(y_lo * 1.15, 0, color=ORANGE, alpha=0.06, zorder=0)
    ax2.text(0.5, y_lo + (0 - y_lo) * 0.40,
             r"negative $\Delta$HV: controller loss",
             fontsize=6.5, color=ORANGE, alpha=0.9, ha="left",
             style="italic")
    ax2.grid(True, alpha=0.2, linewidth=0.4, axis="y")

    # ── X-axis ticks ──
    for ax in (ax1, ax2):
        ax.set_xticks(range(n))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=6.5)
        ax.set_xlim(-0.6, n - 0.4)

    # ── Subplot titles ──
    ax1.set_title("(a) Early turnover in WFG instances", fontsize=9, loc="left")
    ax2.set_title("(b) Controller " + r"$\Delta$HV" + " in WFG instances",
                  fontsize=9, loc="left")

    # ── Layout before label placement ──
    fig.tight_layout(h_pad=2.0, rect=[0, 0.08, 1, 1])
    fig.subplots_adjust(bottom=0.24, left=0.14)

    # ── Horizontally aligned y-axis labels ──
    ax1.set_ylabel("")
    ax2.set_ylabel("")
    bbox1 = ax1.get_position()
    bbox2 = ax2.get_position()
    label_x = 0.05  # fixed figure-coordinate x (left of both axes)
    fig.text(label_x, bbox1.y0 + bbox1.height / 2, "Early turnover",
             ha="center", va="center", rotation=90, fontsize=10)
    fig.text(label_x, bbox2.y0 + bbox2.height / 2, r"$\Delta\mathrm{HV}$",
             ha="center", va="center", rotation=90, fontsize=10)
    # ── X-axis label ──
    fig.text(0.53, 0.035, "WFG instances (sorted by early turnover)",
             ha="center", va="center", fontsize=9)

    # ── Simplified legend (observed categories only) ──
    from matplotlib.lines import Line2D
    le_kw = dict(color="w", markeredgecolor="#333333", markeredgewidth=0.6,
                 markersize=8)
    legend_elements = [
        Line2D([0], [0], marker="v", markerfacecolor=BLUE, **le_kw,
               label="IVF helpful (HELPS label)"),
        Line2D([0], [0], marker="v", markerfacecolor=ORANGE, **le_kw,
               label="IVF not helpful (NOT HELPS label)"),
        Line2D([0], [0], marker="x", color="red", markerfacecolor="red",
               markersize=8, linewidth=0,
               label=r"Controller error ($\times$ overlaid)"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=3,
               fontsize=7, framealpha=0.85, edgecolor="lightgray",
               bbox_to_anchor=(0.5, -0.06))

    save_figure(fig, "fig9_wfg_failure_mode")


# ===========================================================================
# Figure 10: IGD-label vs HV-outcome consistency
# ===========================================================================
def figure_igd_hv_consistency() -> None:
    print("\n--- Figure 10: IGD-label vs HV-outcome consistency ---")
    if not FLA_RESPONSE_CSV.exists():
        print(f"  ERROR: {FLA_RESPONSE_CSV} not found. Skipping.")
        return
    if not CONTROLLER_CSV.exists():
        print(f"  ERROR: {CONTROLLER_CSV} not found. Skipping.")
        return

    resp = pd.read_csv(FLA_RESPONSE_CSV)
    resp["case_norm"] = resp["instance"].str.lower().str.replace("_m", "_m")

    ctrl = pd.read_csv(CONTROLLER_CSV)
    hv = ctrl[ctrl["metric"] == "HV"].copy()

    # Merge: IGD from fla_response (independent cohort), HV from controller (paired cohort)
    merged = resp.merge(
        hv[["case_id", "median_ctrl", "median_ivf", "median_spea2"]],
        left_on="case_norm", right_on="case_id", how="inner",
    )
    if merged.empty:
        print("  ERROR: Merge resulted in empty dataframe. Skipping.")
        return

    # Axes
    merged["delta_igd"] = merged["median_igd_spea2"] - merged["median_igd_ivf"]
    merged["delta_hv"] = merged["median_ctrl"] - merged["median_spea2"]
    merged["family"] = merged["case_id"].apply(family_of)

    # Identify quadrant
    merged["quadrant"] = "N/A"
    merged.loc[(merged["delta_igd"] > 0) & (merged["delta_hv"] > 0), "quadrant"] = "Q1"
    merged.loc[(merged["delta_igd"] > 0) & (merged["delta_hv"] < 0), "quadrant"] = "Q2"
    merged.loc[(merged["delta_igd"] < 0) & (merged["delta_hv"] > 0), "quadrant"] = "Q3"
    merged.loc[(merged["delta_igd"] < 0) & (merged["delta_hv"] < 0), "quadrant"] = "Q4"

    fig, ax = plt.subplots(figsize=(5.0, 4.5))

    helps = merged[merged["label_binary"] == "HELPS"]
    not_helps = merged[merged["label_binary"] == "NOT_HELPS"]

    for fam in FAMILY_ORDER:
        marker = FAMILY_MARKERS[fam]
        h_fam = helps[helps["family"] == fam]
        n_fam = not_helps[not_helps["family"] == fam]

        if not h_fam.empty:
            ax.scatter(h_fam["delta_igd"], h_fam["delta_hv"],
                       marker=marker, c=BLUE, s=52, alpha=0.8,
                       edgecolors="white", linewidths=0.5, zorder=3,
                       label=f"Helpful ({fam})" if fam == FAMILY_ORDER[0] else "")
        if not n_fam.empty:
            ax.scatter(n_fam["delta_igd"], n_fam["delta_hv"],
                       marker=marker, c=ORANGE, s=52, alpha=0.8,
                       edgecolors="white", linewidths=0.5, zorder=3,
                       label=f"Not helpful ({fam})" if fam == FAMILY_ORDER[0] else "")

    # Quadrant lines
    ax.axhline(y=0, color="black", linewidth=0.6, linestyle="-", alpha=0.5, zorder=1)
    ax.axvline(x=0, color="black", linewidth=0.6, linestyle="-", alpha=0.5, zorder=1)

    # Quadrant annotations
    xlims = ax.get_xlim()
    ylims = ax.get_ylim()
    for q, xpos, ypos, label in [
        ("Q1", 0.98, 0.98, "+ΔIGD, +ΔHV"),
        ("Q2", 0.98, 0.02, "+ΔIGD, −ΔHV"),
        ("Q3", 0.02, 0.98, "−ΔIGD, +ΔHV"),
        ("Q4", 0.02, 0.02, "−ΔIGD, −ΔHV"),
    ]:
        n_q = int((merged["quadrant"] == q).sum())
        if n_q > 0:
            ax.annotate(f"{label}\n({n_q})",
                        xy=(xpos, ypos), xycoords="axes fraction",
                        ha="right" if xpos > 0.5 else "left",
                        va="top" if ypos > 0.5 else "bottom",
                        fontsize=6.5, alpha=0.6, color=GRAY)

    # Spearman correlation
    valid = merged[["delta_igd", "delta_hv"]].dropna()
    if len(valid) > 5:
        rho, p_rho = stats.spearmanr(valid["delta_igd"], valid["delta_hv"])
        p_str = f"$p$={p_rho:.3f}" if p_rho >= 0.001 else f"$p$={p_rho:.1e}"
        ax.annotate(f"Spearman $\\rho$={rho:.3f}\n{p_str}",
                    xy=(0.03, 0.97), xycoords="axes fraction",
                    ha="left", va="top", fontsize=7.5,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="lightgray", alpha=0.85))

    ax.set_xlabel(r"$\Delta$IGD = IGD(SPEA2) $-$ IGD(IVF-SPEA2)")
    ax.set_ylabel(r"$\Delta$HV = HV(CTRL) $-$ HV(SPEA2)")

    # Legend: shape = family, color = label
    legend_family = [
        plt.Line2D([0], [0], marker=m, color="w", markerfacecolor=GRAY,
                   markersize=8, label=f)
        for f, m in zip(FAMILY_ORDER, [FAMILY_MARKERS[f] for f in FAMILY_ORDER])
    ]
    legend_label = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=BLUE,
                   markersize=8, label="Helpful"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=ORANGE,
                   markersize=8, label="Not helpful"),
    ]
    leg1 = ax.legend(handles=legend_label, loc="lower right", fontsize=7,
                     framealpha=0.85, edgecolor="lightgray", title="Label")
    leg2 = ax.legend(handles=legend_family, loc="lower left", fontsize=7,
                     framealpha=0.85, edgecolor="lightgray", title="Family")
    ax.add_artist(leg1)

    ax.grid(True, alpha=0.2, linewidth=0.4)
    fig.tight_layout()
    save_figure(fig, "fig10_igd_hv_consistency")


# ===========================================================================
# Figure 11: Study design schematic
# ===========================================================================
def figure_study_design() -> None:
    print("\n--- Figure 11: Study design schematic ---")

    # Colors
    COMPANION_FC = "#D6E6F5"   # Light blue — companion data
    NEW_FC = "#FDE4C2"         # Light orange — new in this paper
    EVAL_FC = "#D4EDDA"        # Light green — final evaluation
    LABEL_FC = "#E8E0F0"       # Light purple — derived labels
    EDGE_C = "#3A4A5A"
    TEXT_C = "#334455"
    BRANCH_BG = "#F5F5F5"      # Very light gray for branch backgrounds

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec=EDGE_C, fontsize=6.8, bold=False, dashed=False,
            ha="center", va="center"):
        ls = "--" if dashed else "-"
        patch = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.03,rounding_size=0.06",
            linewidth=1.0, linestyle=ls, edgecolor=ec, facecolor=fc, zorder=2,
        )
        ax.add_patch(patch)
        weight = "bold" if bold else "normal"
        lines = text.split("\n")
        line_h = min(fontsize * 0.0045 * 8, h / (len(lines) + 0.5))
        y_pos = y + h / 2 + (len(lines) - 1) * line_h / 2
        for line in lines:
            ax.text(x + w / 2, y_pos, line, ha=ha, va=va, fontsize=fontsize,
                    weight=weight, color=TEXT_C, zorder=5)
            y_pos -= line_h * 1.3

    def arrow(x1, y1, x2, y2, color=EDGE_C, style="arc3,rad=0"):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=style, arrowstyle="->",
            linewidth=1.0, color=color, zorder=1,
        ))

    def tag(x, y, text, color=TEXT_C, fontsize=5.5):
        ax.text(x, y, text, fontsize=fontsize, color=color, ha="center", va="center",
                style="italic", zorder=6)

    # --- Top: Independent cohort ---
    box(0.5, 6.2, 3.8, 1.2,
        "Independent 60-run cohort\nIVF-SPEA2 vs SPEA2\n(51 synthetic instances)",
        COMPANION_FC, bold=True, fontsize=6.2)
    tag(4.2, 7.4, "Reused from\ncompanion", COMPANION_FC)

    # Arrow down
    arrow(2.4, 6.2, 2.4, 5.65)

    # --- Labels ---
    box(0.5, 4.8, 3.8, 0.85,
        "IGD-based operator-benefit labels\nHELPFUL / NOT HELPFUL",
        LABEL_FC, fontsize=6.2)

    # Branch arrow
    arrow(2.4, 4.8, 2.4, 4.25)

    # --- Bifurcation ---
    ax.text(2.4, 4.05, "▼", fontsize=10, color=EDGE_C, ha="center", va="center", zorder=5)

    # Branch backgrounds
    box(0.2, 1.0, 4.2, 3.0, "", fc=BRANCH_BG, ec="lightgray", fontsize=1, dashed=True)
    box(5.6, 1.0, 4.2, 3.0, "", fc=BRANCH_BG, ec="lightgray", fontsize=1, dashed=True)

    # --- Left branch: Static FLA ---
    arrow(2.4, 4.0, 1.0, 3.7)
    arrow(1.0, 4.0, 1.0, 3.7)  # vertical
    box(0.35, 2.8, 3.9, 1.1,
        "Static FLA branch\n22 raw features → 14 retained\nregression + classification",
        NEW_FC, fontsize=6.2)
    tag(0.35, 3.9, "New in this paper", NEW_FC)

    arrow(2.3, 2.8, 2.3, 1.8)

    box(0.35, 1.1, 3.9, 0.7,
        "Static prediction\n(RF, LogReg, RBF-SVC)",
        NEW_FC, fontsize=6.0)

    # --- Right branch: Dynamic trajectory ---
    arrow(2.4, 4.0, 3.8, 3.7)
    arrow(3.8, 4.0, 3.8, 3.7)
    box(6.0, 2.8, 3.6, 1.1,
        "Dynamic trajectory branch\n30 paired-seed runs\nturnover, cycles, IGD(t), HV",
        NEW_FC, fontsize=6.2)
    tag(6.0, 3.9, "New in this paper", NEW_FC)

    arrow(7.8, 2.8, 7.8, 1.8)

    box(6.0, 1.1, 3.6, 0.7,
        "Early signal testing\n(threshold calibration)",
        NEW_FC, fontsize=6.0)

    # --- Convergence ---
    arrow(2.3, 1.1, 5.0, 0.5)
    arrow(7.8, 1.1, 5.0, 0.5)
    arrow(5.0, 0.5, 5.0, 0.0)
    arrow(5.0, 0.8, 5.0, 0.0)

    # --- Bottom: Controller evaluation ---
    box(1.5, -0.5, 7.0, 0.55,
        "Warmup controller evaluation  ·  HV endpoint  ·  Risk-reduction analysis",
        EVAL_FC, bold=True, fontsize=6.8)
    tag(8.5, -0.2, "Final\nevaluation", EVAL_FC)

    fig.tight_layout(pad=0.5)
    save_figure(fig, "fig11_study_design")


# ===========================================================================
# Main
# ===========================================================================
def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {FIGURES_DIR}")

    figure_family_separability()
    figure_classifier_comparison()
    figure_warmup_horizon()
    figure_wfg_failure_mode()
    figure_igd_hv_consistency()
    figure_study_design()

    print("\nDone. All proposed figures saved.")


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    main()
