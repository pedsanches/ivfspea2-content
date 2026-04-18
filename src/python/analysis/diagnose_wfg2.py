#!/usr/bin/env python3
"""
WFG2(M=3) Diagnostic: Why does IVF/SPEA2 lose to SPEA2 here?
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path("/home/pedro/desenvolvimento/ivfspea2")
OUTPUT_DIR = PROJECT_ROOT / "results" / "ablation_v2" / "phase3"

# Load all data sources
raw_p3 = pd.read_csv(OUTPUT_DIR / "phase3_raw_metrics.csv")
raw_p1 = pd.read_csv(PROJECT_ROOT / "results" / "ablation_v2" / "phase1" / "phase1_raw_igd.csv")
raw_p2 = pd.read_csv(PROJECT_ROOT / "results" / "ablation_v2" / "phase2" / "phase2_raw_igd.csv")
baseline = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "todas_metricas_consolidado.csv")

# Filter WFG2 M=3
wfg2_p3 = raw_p3[(raw_p3["Problem"] == "WFG2") & (raw_p3["M"] == 3)]
wfg2_p1 = raw_p1[(raw_p1["Problem"] == "WFG2") & (raw_p1["M"] == 3)]
wfg2_p2 = raw_p2[(raw_p2["Problem"] == "WFG2") & (raw_p2["M"] == 3)]
wfg2_bl = baseline[(baseline["Problema"] == "WFG2") & (baseline["M"] == 3)]

fig = plt.figure(figsize=(18, 14))
fig.suptitle("WFG2(M=3) Diagnostic: Why IVF/SPEA2 Underperforms",
             fontsize=14, fontweight="bold")

# --- Panel A: Phase 3 IGD distributions (C05 vs IVF v1 vs SPEA2) ---
ax1 = fig.add_subplot(2, 3, 1)

c05_igd = wfg2_p3[wfg2_p3["Algorithm"] == "IVFSPEA2_P2_C05"]["IGD"].values
ivf_igd = wfg2_bl[wfg2_bl["Algoritmo"] == "IVFSPEA2"]["IGD"].dropna().values
spea2_igd = wfg2_bl[wfg2_bl["Algoritmo"] == "SPEA2"]["IGD"].dropna().values

bp = ax1.boxplot([spea2_igd, ivf_igd, c05_igd],
                 tick_labels=["SPEA2", "IVF v1", "C05\n(H1+H2)"],
                 patch_artist=True, widths=0.6,
                 flierprops=dict(marker=".", markersize=4))
for patch, color in zip(bp["boxes"], ["#90CAF9", "#FFE082", "#A5D6A7"]):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

ax1.set_ylabel("IGD (lower is better)")
ax1.set_title("A. IGD Distribution", fontweight="bold")
ax1.axhline(np.median(spea2_igd), color="#1565C0", linestyle="--", alpha=0.5, linewidth=0.8)

# --- Panel B: Phase 3 HV distributions ---
ax2 = fig.add_subplot(2, 3, 2)

c05_hv = wfg2_p3[wfg2_p3["Algorithm"] == "IVFSPEA2_P2_C05"]["HV"].values
ivf_hv = wfg2_bl[wfg2_bl["Algoritmo"] == "IVFSPEA2"]["HV"].dropna().values
spea2_hv = wfg2_bl[wfg2_bl["Algoritmo"] == "SPEA2"]["HV"].dropna().values

bp2 = ax2.boxplot([spea2_hv, ivf_hv, c05_hv],
                  tick_labels=["SPEA2", "IVF v1", "C05\n(H1+H2)"],
                  patch_artist=True, widths=0.6,
                  flierprops=dict(marker=".", markersize=4))
for patch, color in zip(bp2["boxes"], ["#90CAF9", "#FFE082", "#A5D6A7"]):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

ax2.set_ylabel("HV (higher is better)")
ax2.set_title("B. HV Distribution", fontweight="bold")
ax2.axhline(np.median(spea2_hv), color="#1565C0", linestyle="--", alpha=0.5, linewidth=0.8)

# --- Panel C: IGD vs HV scatter (metric discordance) ---
ax3 = fig.add_subplot(2, 3, 3)

for data_igd, data_hv, label, color, marker in [
    (spea2_igd, spea2_hv, "SPEA2", "#1565C0", "o"),
    (ivf_igd, ivf_hv, "IVF v1", "#F57F17", "s"),
    (c05_igd, c05_hv, "C05 (H1+H2)", "#2E7D32", "^"),
]:
    n = min(len(data_igd), len(data_hv))
    ax3.scatter(data_igd[:n], data_hv[:n], c=color, marker=marker,
                alpha=0.5, s=20, label=label, edgecolor="black", linewidth=0.3)

ax3.set_xlabel("IGD (lower=better)")
ax3.set_ylabel("HV (higher=better)")
ax3.set_title("C. IGD vs HV (metric discordance)", fontweight="bold")
ax3.legend(fontsize=7)

# --- Panel D: Phase 1 variant comparison ---
ax4 = fig.add_subplot(2, 3, 4)

p1_configs = wfg2_p1["Config"].unique()
p1_data = []
p1_labels = []
label_map = {
    "IVFSPEA2": "Baseline",
    "IVFSPEA2_V1_DISSIM": "V1 (dissim.)",
    "IVFSPEA2_V2_COLLECTIVE": "V2 (collect.)",
    "IVFSPEA2_V3_ETA10": "V3 (eta10)",
    "IVFSPEA2_V4_ADAPTIVE": "V4 (adaptive)",
    "IVFSPEA2_V5_MUTATION": "V5 (mutation)",
}

for cfg in sorted(p1_configs):
    vals = wfg2_p1[wfg2_p1["Config"] == cfg]["IGD"].values
    if len(vals) > 0:
        p1_data.append(vals)
        p1_labels.append(label_map.get(cfg, cfg))

bp4 = ax4.boxplot(p1_data, tick_labels=p1_labels, patch_artist=True,
                  widths=0.6, flierprops=dict(marker=".", markersize=3))
for patch in bp4["boxes"]:
    patch.set_facecolor("#CE93D8")
    patch.set_alpha(0.7)

ax4.axhline(np.median(spea2_igd), color="#1565C0", linestyle="--",
            alpha=0.5, linewidth=0.8, label="SPEA2 median")
ax4.set_ylabel("IGD")
ax4.set_title("D. Phase 1: Single-Factor Variants", fontweight="bold")
ax4.tick_params(axis="x", rotation=25, labelsize=7)
ax4.legend(fontsize=7)

# --- Panel E: Phase 2 factorial (sorted by median) ---
ax5 = fig.add_subplot(2, 3, 5)

p2_configs = sorted(wfg2_p2["Config"].unique())
p2_medians = {}
for cfg in p2_configs:
    vals = wfg2_p2[wfg2_p2["Config"] == cfg]["IGD"].values
    if len(vals) > 0:
        p2_medians[cfg] = np.median(vals)

sorted_cfgs = sorted(p2_medians, key=p2_medians.get)
p2_sorted_data = [wfg2_p2[wfg2_p2["Config"] == c]["IGD"].values for c in sorted_cfgs]

# Map config IDs to factor labels
cfg_label_map = {
    "P2_C00": "0000\n(base)", "P2_C01": "1000\n(H1)", "P2_C02": "0100\n(H2)",
    "P2_C03": "0010\n(H3)", "P2_C04": "0001\n(H4)", "P2_C05": "1100\n(H1+H2)",
    "P2_C06": "1010\n(H1+H3)", "P2_C07": "1001\n(H1+H4)", "P2_C08": "0110\n(H2+H3)",
    "P2_C09": "0101\n(H2+H4)", "P2_C10": "0011\n(H3+H4)", "P2_C11": "1110\n(H1+H2+H3)",
    "P2_C12": "1101\n(H1+H2+H4)", "P2_C13": "1011\n(H1+H3+H4)",
    "P2_C14": "0111\n(H2+H3+H4)", "P2_C15": "1111\n(all)",
}

p2_labels = [cfg_label_map.get(c, c) for c in sorted_cfgs]
bp5 = ax5.boxplot(p2_sorted_data, tick_labels=p2_labels, patch_artist=True,
                  widths=0.6, flierprops=dict(marker=".", markersize=2))
for patch in bp5["boxes"]:
    patch.set_facecolor("#FFCC80")
    patch.set_alpha(0.7)

ax5.axhline(np.median(spea2_igd), color="#1565C0", linestyle="--",
            alpha=0.5, linewidth=0.8, label="SPEA2 median")
ax5.set_ylabel("IGD")
ax5.set_title("E. Phase 2: All 16 Factorial (sorted)", fontweight="bold")
ax5.tick_params(axis="x", rotation=90, labelsize=5)
ax5.legend(fontsize=7)

# --- Panel F: Diagnosis text summary ---
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis("off")

diagnosis = (
    "ROOT CAUSE ANALYSIS\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "1. DISCONNECTED FRONT GEOMETRY\n"
    "   WFG2's f3 uses disc(x) = 1−x₁cos²(5πx₁)\n"
    "   creating ~5 disjoint segments. SBX between\n"
    "   parents on different segments produces\n"
    "   offspring in dominated inter-segment gaps.\n\n"
    "2. METRIC DISCORDANCE\n"
    "   IGD: significant loss (p≈0.000002)\n"
    "   HV:  no significant difference (p≈0.50)\n"
    "   → IVF loses SPREAD, not CONVERGENCE.\n"
    "   IVF offspring cluster near parent segments,\n"
    "   missing coverage of other segments.\n\n"
    "3. NO VARIANT HELPS\n"
    "   All Phase 1 variants ≥ baseline IGD.\n"
    "   V1 (dissim. father) is WORST: pushing\n"
    "   parents apart increases inter-segment\n"
    "   crossover → more wasted offspring.\n\n"
    "4. MONOTONIC DEGRADATION WITH IVF INTENSITY\n"
    "   Phase 2 shows more IVF = worse IGD.\n"
    "   Only C10 (H3+H4, near-baseline IVF)\n"
    "   matches SPEA2.\n\n"
    "5. STRUCTURAL, NOT PARAMETRIC\n"
    "   The failure is inherent to SBX crossover\n"
    "   on disconnected fronts. Fix requires either:\n"
    "   a) Segment-aware recombination\n"
    "   b) IVF deactivation on detected disconnect\n"
    "   c) Accepting WFG2 as a known limitation"
)

ax6.text(0.02, 0.98, diagnosis, transform=ax6.transAxes,
         fontsize=7.5, verticalalignment="top", fontfamily="monospace",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF9C4",
                  edgecolor="#F57F17", alpha=0.9))

plt.tight_layout(rect=[0, 0, 1, 0.95])
path = OUTPUT_DIR / "phase3_wfg2_diagnostic.pdf"
plt.savefig(path, bbox_inches="tight", dpi=150)
plt.close()
print(f"Saved: {path}")
