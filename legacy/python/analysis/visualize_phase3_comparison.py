#!/usr/bin/env python3
"""
Phase 3 Visualization: P2_C05 (H1+H2) vs Baselines on 51 instances
====================================================================
Generates comprehensive comparison plots:
  1. Win/Tie/Loss summary bar chart (IGD + HV)
  2. Heatmap of relative improvement (%) per instance vs each baseline
  3. Per-instance significance dot plot (IGD)
  4. Boxplot comparison on key failure-case instances
"""

import os
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import TwoSlopeNorm

PROJECT_ROOT = Path("/home/pedro/desenvolvimento/ivfspea2")
OUTPUT_DIR = PROJECT_ROOT / "results" / "ablation_v2" / "phase3"

# Load data
igd_df = pd.read_csv(OUTPUT_DIR / "phase3_igd_per_instance.csv")
hv_df = pd.read_csv(OUTPUT_DIR / "phase3_hv_per_instance.csv")
raw_df = pd.read_csv(OUTPUT_DIR / "phase3_raw_metrics.csv")
summary = json.loads((OUTPUT_DIR / "phase3_summary.json").read_text())

# Also load the baseline raw data
baseline_csv = PROJECT_ROOT / "data" / "processed" / "todas_metricas_consolidado.csv"
baseline_df = pd.read_csv(baseline_csv)


def instance_label(row):
    return f"{row['Problem']}({row['M']})"


igd_df["Instance"] = igd_df.apply(instance_label, axis=1)
hv_df["Instance"] = hv_df.apply(instance_label, axis=1)

# ---- Figure 1: Win/Tie/Loss Summary ----------------------------------------

def plot_wintieloss():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, metric in zip(axes, ["IGD", "HV"]):
        categories = ["vs IVFSPEA2 v1", "vs SPEA2"]
        wins = [summary[metric]["IVFSPEA2"]["wins"], summary[metric]["SPEA2"]["wins"]]
        ties = [summary[metric]["IVFSPEA2"]["ties"], summary[metric]["SPEA2"]["ties"]]
        losses = [summary[metric]["IVFSPEA2"]["losses"], summary[metric]["SPEA2"]["losses"]]

        x = np.arange(len(categories))
        width = 0.25

        bars_w = ax.bar(x - width, wins, width, label="Win", color="#4CAF50", edgecolor="black", linewidth=0.5)
        bars_t = ax.bar(x, ties, width, label="Tie", color="#FFC107", edgecolor="black", linewidth=0.5)
        bars_l = ax.bar(x + width, losses, width, label="Loss", color="#F44336", edgecolor="black", linewidth=0.5)

        for bars in [bars_w, bars_t, bars_l]:
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, str(int(h)),
                            ha="center", va="bottom", fontsize=11, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylabel("Number of instances (out of 51)", fontsize=10)
        ax.set_title(f"{metric} — P2_C05 (H1+H2)", fontsize=12, fontweight="bold")
        ax.legend(fontsize=9)
        ax.set_ylim(0, 55)

    plt.suptitle("Phase 3: Win/Tie/Loss Summary (Holm-Bonferroni, α=0.05)",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = OUTPUT_DIR / "phase3_wintieloss.pdf"
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ---- Figure 2: Relative Improvement Heatmap ---------------------------------

def plot_improvement_heatmap():
    fig, axes = plt.subplots(1, 2, figsize=(8, 16))

    for ax, (metric_label, df, higher_better) in zip(axes, [
        ("IGD", igd_df, False),
        ("HV", hv_df, True),
    ]):
        instances = df["Instance"].values

        # Compute relative improvement (%)
        c05_med = df["IVFSPEA2_P2_C05_median"].values
        ivf_med = df["IVFSPEA2_median"].values
        spea2_med = df["SPEA2_median"].values

        if higher_better:
            # HV: positive = C05 better
            delta_ivf = ((c05_med - ivf_med) / np.abs(ivf_med)) * 100
            delta_spea2 = ((c05_med - spea2_med) / np.abs(spea2_med)) * 100
        else:
            # IGD: negative IGD change = improvement, so flip sign
            delta_ivf = ((ivf_med - c05_med) / np.abs(ivf_med)) * 100
            delta_spea2 = ((spea2_med - c05_med) / np.abs(spea2_med)) * 100

        data = np.column_stack([delta_ivf, delta_spea2])

        # Clip extreme values for visualization
        vmax = np.percentile(np.abs(data[np.isfinite(data)]), 95)
        vmax = max(vmax, 1.0)
        norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

        im = ax.imshow(data, cmap="RdYlGn", norm=norm, aspect="auto", interpolation="nearest")

        ax.set_yticks(range(len(instances)))
        ax.set_yticklabels(instances, fontsize=6)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["vs IVF v1", "vs SPEA2"], fontsize=9)
        ax.set_title(f"{metric_label}\n(green=C05 better)", fontsize=10, fontweight="bold")

        # Add text annotations
        for i in range(len(instances)):
            for j in range(2):
                val = data[i, j]
                if np.isfinite(val):
                    color = "black" if abs(val) < vmax * 0.6 else "white"
                    ax.text(j, i, f"{val:+.1f}", ha="center", va="center", fontsize=5, color=color)

        plt.colorbar(im, ax=ax, shrink=0.5, label="Improvement (%)")

    plt.suptitle("Phase 3: Relative Improvement of P2_C05 (H1+H2)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    path = OUTPUT_DIR / "phase3_improvement_heatmap.pdf"
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ---- Figure 3: Significance Dot Plot (IGD) ----------------------------------

def plot_significance_dotplot():
    fig, ax = plt.subplots(figsize=(10, 14))

    instances = igd_df["Instance"].values
    n = len(instances)
    y = np.arange(n)

    # Indicators for SPEA2 comparison
    indicators_spea2 = igd_df["SPEA2_indicator"].values
    indicators_ivf = igd_df["IVFSPEA2_indicator"].values

    # Map to colors/markers
    color_map = {"+": "#4CAF50", "=": "#FFC107", "-": "#F44336"}
    marker_map = {"+": "^", "=": "o", "-": "v"}
    label_map = {"+": "C05 wins", "=": "Tie", "-": "C05 loses"}

    # Plot vs SPEA2
    for ind in ["+", "=", "-"]:
        mask = indicators_spea2 == ind
        if mask.any():
            ax.scatter(np.zeros(mask.sum()) - 0.15, y[mask],
                      c=color_map[ind], marker=marker_map[ind], s=60,
                      edgecolor="black", linewidth=0.5, zorder=3,
                      label=f"vs SPEA2: {label_map[ind]} ({mask.sum()})")

    # Plot vs IVF v1
    for ind in ["+", "=", "-"]:
        mask = indicators_ivf == ind
        if mask.any():
            ax.scatter(np.zeros(mask.sum()) + 0.15, y[mask],
                      c=color_map[ind], marker=marker_map[ind], s=60,
                      edgecolor="black", linewidth=0.5, zorder=3,
                      label=f"vs IVF v1: {label_map[ind]} ({mask.sum()})")

    ax.set_yticks(y)
    ax.set_yticklabels(instances, fontsize=7)
    ax.set_xticks([-0.15, 0.15])
    ax.set_xticklabels(["vs SPEA2", "vs IVF v1"], fontsize=10)
    ax.set_xlim(-0.5, 0.5)
    ax.invert_yaxis()

    ax.axvline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.legend(loc="lower right", fontsize=8, ncol=2)
    ax.set_title("Phase 3 IGD: Significance per Instance (Holm-Bonferroni, α=0.05)",
                 fontsize=11, fontweight="bold")

    # Highlight failure cases from the plan
    failure_cases = ["DTLZ4(3)", "WFG2(3)", "MaF5(3)"]
    for i, inst in enumerate(instances):
        if inst in failure_cases:
            ax.axhspan(i - 0.4, i + 0.4, color="lightyellow", alpha=0.5, zorder=0)
            ax.text(0.45, i, "target", fontsize=6, va="center", ha="right",
                   fontstyle="italic", color="gray")

    plt.tight_layout()
    path = OUTPUT_DIR / "phase3_significance_dotplot.pdf"
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ---- Figure 4: Boxplots for Key Instances -----------------------------------

def plot_key_instance_boxplots():
    # Key instances from the ablation plan (Section 6 success criteria)
    key_instances = [
        ("DTLZ4", 3, "Failure case (biased)"),
        ("WFG2", 3, "Failure case (disconnected)"),
        ("MaF5", 3, "Failure case (convex-inverted)"),
        ("ZDT1", 2, "Positive control"),
        ("WFG4", 2, "Regression guard"),
        ("DTLZ7", 3, "Disconnected"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()

    for idx, (prob, m, desc) in enumerate(key_instances):
        ax = axes[idx]

        # Get raw data for each algorithm
        c05_vals = raw_df[
            (raw_df["Algorithm"] == "IVFSPEA2_P2_C05") &
            (raw_df["Problem"] == prob) &
            (raw_df["M"] == m)
        ]["IGD"].values

        ivf_vals = baseline_df[
            (baseline_df["Algoritmo"] == "IVFSPEA2") &
            (baseline_df["Problema"] == prob) &
            (baseline_df["M"] == m)
        ]["IGD"].dropna().values

        spea2_vals = baseline_df[
            (baseline_df["Algoritmo"] == "SPEA2") &
            (baseline_df["Problema"] == prob) &
            (baseline_df["M"] == m)
        ]["IGD"].dropna().values

        data_to_plot = []
        labels = []
        colors = []

        if len(spea2_vals) > 0:
            data_to_plot.append(spea2_vals)
            labels.append(f"SPEA2\n(n={len(spea2_vals)})")
            colors.append("#90CAF9")
        if len(ivf_vals) > 0:
            data_to_plot.append(ivf_vals)
            labels.append(f"IVF v1\n(n={len(ivf_vals)})")
            colors.append("#FFE082")
        if len(c05_vals) > 0:
            data_to_plot.append(c05_vals)
            labels.append(f"C05\n(n={len(c05_vals)})")
            colors.append("#A5D6A7")

        if data_to_plot:
            bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                          widths=0.6, showfliers=True,
                          flierprops=dict(marker=".", markersize=3, alpha=0.5))
            for patch, color in zip(bp["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.8)

        # Get the indicator from the per-instance CSV
        row = igd_df[(igd_df["Problem"] == prob) & (igd_df["M"] == m)]
        if len(row) > 0:
            ind_spea2 = row["SPEA2_indicator"].values[0]
            ind_ivf = row["IVFSPEA2_indicator"].values[0]
            sig_text = f"vs SPEA2: {ind_spea2} | vs IVF v1: {ind_ivf}"
        else:
            sig_text = ""

        ax.set_title(f"{prob}(M={m})\n{desc}", fontsize=9, fontweight="bold")
        ax.set_ylabel("IGD", fontsize=8)
        ax.tick_params(axis="both", labelsize=7)

        if sig_text:
            ax.text(0.5, -0.18, sig_text, transform=ax.transAxes,
                   ha="center", fontsize=7, fontstyle="italic")

    plt.suptitle("Phase 3: IGD Distributions on Key Instances — P2_C05 (H1+H2) vs Baselines",
                 fontsize=12, fontweight="bold")
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])
    path = OUTPUT_DIR / "phase3_key_boxplots.pdf"
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ---- Figure 5: Summary dashboard -------------------------------------------

def plot_dashboard():
    fig = plt.figure(figsize=(16, 10))

    # Layout: 2x3 grid
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)

    # --- Panel A: Win/Tie/Loss bars ---
    ax_wtl = fig.add_subplot(gs[0, 0])
    metrics = ["IGD", "HV"]
    x = np.arange(2)
    width = 0.2

    for i, baseline in enumerate(["IVFSPEA2", "SPEA2"]):
        wins_igd = summary["IGD"][baseline]["wins"]
        wins_hv = summary["HV"][baseline]["wins"]
        losses_igd = summary["IGD"][baseline]["losses"]
        losses_hv = summary["HV"][baseline]["losses"]

        offset = (i - 0.5) * width * 1.5
        ax_wtl.bar(x + offset - width/2, [wins_igd, wins_hv], width * 0.8,
                   color="#4CAF50" if i == 1 else "#81C784", edgecolor="black", linewidth=0.5,
                   label=f"Win vs {baseline.replace('IVFSPEA2','IVF v1')}")
        ax_wtl.bar(x + offset + width/2, [losses_igd, losses_hv], width * 0.8,
                   color="#F44336" if i == 1 else "#EF9A9A", edgecolor="black", linewidth=0.5,
                   label=f"Loss vs {baseline.replace('IVFSPEA2','IVF v1')}")

    ax_wtl.set_xticks(x)
    ax_wtl.set_xticklabels(metrics, fontsize=10)
    ax_wtl.set_ylabel("Instances")
    ax_wtl.legend(fontsize=6, ncol=2)
    ax_wtl.set_title("A. Win/Loss Count", fontweight="bold", fontsize=10)

    # --- Panel B: IGD median delta vs SPEA2 (sorted bar) ---
    ax_delta = fig.add_subplot(gs[0, 1:])

    instances = igd_df["Instance"].values
    c05_med = igd_df["IVFSPEA2_P2_C05_median"].values
    spea2_med = igd_df["SPEA2_median"].values

    delta_pct = ((spea2_med - c05_med) / np.abs(spea2_med)) * 100

    # Sort by delta
    sort_idx = np.argsort(delta_pct)
    sorted_delta = delta_pct[sort_idx]
    sorted_labels = instances[sort_idx]
    sorted_indicators = igd_df["SPEA2_indicator"].values[sort_idx]

    colors = ["#4CAF50" if d > 0 else "#F44336" for d in sorted_delta]
    # Override with significance
    for i, (d, ind) in enumerate(zip(sorted_delta, sorted_indicators)):
        if ind == "+":
            colors[i] = "#2E7D32"  # dark green = significant win
        elif ind == "-":
            colors[i] = "#C62828"  # dark red = significant loss
        elif d > 0:
            colors[i] = "#A5D6A7"  # light green = non-sig improvement
        else:
            colors[i] = "#EF9A9A"  # light red = non-sig degradation

    ax_delta.barh(range(len(sorted_delta)), sorted_delta, color=colors,
                  edgecolor="black", linewidth=0.3, height=0.7)
    ax_delta.set_yticks(range(len(sorted_labels)))
    ax_delta.set_yticklabels(sorted_labels, fontsize=5)
    ax_delta.axvline(0, color="black", linewidth=0.5)
    ax_delta.set_xlabel("IGD Improvement vs SPEA2 (%)")
    ax_delta.set_title("B. Per-Instance IGD Improvement vs SPEA2", fontweight="bold", fontsize=10)

    # Legend for significance
    sig_win = mpatches.Patch(color="#2E7D32", label="Sig. win (p<0.05)")
    nonsig_win = mpatches.Patch(color="#A5D6A7", label="Non-sig. improvement")
    nonsig_loss = mpatches.Patch(color="#EF9A9A", label="Non-sig. degradation")
    sig_loss = mpatches.Patch(color="#C62828", label="Sig. loss (p<0.05)")
    ax_delta.legend(handles=[sig_win, nonsig_win, nonsig_loss, sig_loss],
                    fontsize=6, loc="lower right")

    # --- Panel C: IGD delta vs IVF v1 (sorted bar) ---
    ax_delta2 = fig.add_subplot(gs[1, 1:])

    ivf_med = igd_df["IVFSPEA2_median"].values
    delta_pct2 = ((ivf_med - c05_med) / np.abs(ivf_med)) * 100

    sort_idx2 = np.argsort(delta_pct2)
    sorted_delta2 = delta_pct2[sort_idx2]
    sorted_labels2 = instances[sort_idx2]
    sorted_indicators2 = igd_df["IVFSPEA2_indicator"].values[sort_idx2]

    colors2 = []
    for d, ind in zip(sorted_delta2, sorted_indicators2):
        if ind == "+":
            colors2.append("#2E7D32")
        elif ind == "-":
            colors2.append("#C62828")
        elif d > 0:
            colors2.append("#A5D6A7")
        else:
            colors2.append("#EF9A9A")

    ax_delta2.barh(range(len(sorted_delta2)), sorted_delta2, color=colors2,
                   edgecolor="black", linewidth=0.3, height=0.7)
    ax_delta2.set_yticks(range(len(sorted_labels2)))
    ax_delta2.set_yticklabels(sorted_labels2, fontsize=5)
    ax_delta2.axvline(0, color="black", linewidth=0.5)
    ax_delta2.set_xlabel("IGD Improvement vs IVF/SPEA2 v1 (%)")
    ax_delta2.set_title("C. Per-Instance IGD Improvement vs IVF/SPEA2 v1", fontweight="bold", fontsize=10)
    ax_delta2.legend(handles=[sig_win, nonsig_win, nonsig_loss, sig_loss],
                     fontsize=6, loc="lower right")

    # --- Panel D: Scorecard text ---
    ax_score = fig.add_subplot(gs[1, 0])
    ax_score.axis("off")

    scorecard = (
        "Phase 3 Scorecard\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Winner: P2_C05 (H1+H2)\n"
        f"  H1: Dissimilar father\n"
        f"  H2: Collective criterion\n\n"
        f"IGD vs SPEA2:\n"
        f"  {summary['IGD']['SPEA2']['wins']}W / "
        f"{summary['IGD']['SPEA2']['ties']}T / "
        f"{summary['IGD']['SPEA2']['losses']}L\n\n"
        f"HV vs SPEA2:\n"
        f"  {summary['HV']['SPEA2']['wins']}W / "
        f"{summary['HV']['SPEA2']['ties']}T / "
        f"{summary['HV']['SPEA2']['losses']}L\n\n"
        f"IGD vs IVF v1:\n"
        f"  {summary['IGD']['IVFSPEA2']['wins']}W / "
        f"{summary['IGD']['IVFSPEA2']['ties']}T / "
        f"{summary['IGD']['IVFSPEA2']['losses']}L\n\n"
        f"HV vs IVF v1:\n"
        f"  {summary['HV']['IVFSPEA2']['wins']}W / "
        f"{summary['HV']['IVFSPEA2']['ties']}T / "
        f"{summary['HV']['IVFSPEA2']['losses']}L\n"
    )

    ax_score.text(0.05, 0.95, scorecard, transform=ax_score.transAxes,
                  fontsize=9, verticalalignment="top", fontfamily="monospace",
                  bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow",
                           edgecolor="gray", alpha=0.8))

    plt.suptitle("IVF/SPEA2 v2 Phase 3: Full-Suite Validation (51 instances, 60 runs)",
                 fontsize=13, fontweight="bold")

    path = OUTPUT_DIR / "phase3_dashboard.pdf"
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ---- Main -------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 3 VISUALIZATION")
    print("=" * 60)

    plot_wintieloss()
    plot_improvement_heatmap()
    plot_significance_dotplot()
    plot_key_instance_boxplots()
    plot_dashboard()

    # Print summary to console
    print("\n" + "=" * 60)
    print("PHASE 3 RESULTS SUMMARY")
    print("=" * 60)

    print(f"\nWinner: P2_C05 (H1+H2 = Dissimilar father + Collective criterion)")

    for metric in ["IGD", "HV"]:
        print(f"\n--- {metric} ---")
        for baseline in ["IVFSPEA2", "SPEA2"]:
            s = summary[metric][baseline]
            label = "IVF v1" if baseline == "IVFSPEA2" else baseline
            print(f"  vs {label}: {s['wins']}W / {s['ties']}T / {s['losses']}L")

    # Check success criteria from the plan (Section 6)
    print("\n" + "=" * 60)
    print("SUCCESS CRITERIA CHECK (from ablation plan Section 6)")
    print("=" * 60)

    # Criterion 1: DTLZ4(M=3) anomaly reduced
    row = igd_df[(igd_df["Problem"] == "DTLZ4") & (igd_df["M"] == 3)]
    if len(row) > 0:
        c05 = row["IVFSPEA2_P2_C05_median"].values[0]
        spea2 = row["SPEA2_median"].values[0]
        ratio = c05 / spea2
        print(f"\n1. DTLZ4(M=3): C05 median={c05:.4f}, SPEA2 median={spea2:.4f}, ratio={ratio:.2f}x")
        print(f"   Target: ratio < 2x => {'PASS' if ratio < 2 else 'FAIL'}")

    # Criterion 2: WFG2(M=3)
    row = igd_df[(igd_df["Problem"] == "WFG2") & (igd_df["M"] == 3)]
    if len(row) > 0:
        c05 = row["IVFSPEA2_P2_C05_median"].values[0]
        spea2 = row["SPEA2_median"].values[0]
        ind = row["SPEA2_indicator"].values[0]
        print(f"\n2. WFG2(M=3): C05 median={c05:.4f}, SPEA2 median={spea2:.4f}, indicator={ind}")
        print(f"   Target: no significant loss => {'PASS' if ind != '-' else 'FAIL'}")

    # Criterion 3: No new regressions on regular fronts
    losses_igd = summary["IGD"]["SPEA2"]["losses"]
    print(f"\n3. New regressions vs SPEA2 (IGD): {losses_igd} loss(es)")
    if losses_igd > 0:
        loss_instances = igd_df[igd_df["SPEA2_indicator"] == "-"]["Instance"].tolist()
        print(f"   Loss instances: {loss_instances}")
    print(f"   Target: 0 losses => {'PASS' if losses_igd == 0 else 'REVIEW'}")

    # Criterion 4: Win count vs SPEA2
    wins_igd = summary["IGD"]["SPEA2"]["wins"]
    print(f"\n4. Wins vs SPEA2 (IGD): {wins_igd}/51")
    print(f"   v1 had: 16W on M=2 + 15W on M=3 (different suite)")
    print(f"   Target: >= 16 wins => {'PASS' if wins_igd >= 16 else 'FAIL'}")

    print(f"\nAll figures saved to: {OUTPUT_DIR}")
