#!/usr/bin/env python3
"""
IVF/SPEA2 v2 Ablation — Phase 1 Screening Analysis
=====================================================
Parses PlatEMO .mat result files from the Phase 1 screening experiment
and determines which factors are promoted to Phase 2 (factorial combination).

Produces:
  1. Console report with promotion decisions
  2. LaTeX table: median(IQR) per variant per instance, Wilcoxon indicators, bold best
  3. CSV with per-run IGD values
  4. Box-plot figure comparing the 6 configurations across 12 instances
  5. Promotion summary (JSON)

Promotion criteria (from IVF_V2_HYPOTHESES_AND_ABLATION_PLAN.md §4.1):
  A factor is promoted if it:
    - Achieves at least 1 significant win (p < 0.05) with 0 significant losses, OR
    - Shows consistent median improvement in >= 7/12 instances (trend signal)

Expected input layout:
  data/ablation_v2/phase1/<CONFIG>_<PROB>_M<X>/*.mat

  CONFIG naming:
    IVFSPEA2              -> Baseline (B)
    IVFSPEA2_V1_DISSIM    -> H1: Dissimilar father
    IVFSPEA2_V2_COLLECTIVE -> H2: Collective criterion
    IVFSPEA2_V3_ETA10     -> H3: η_c = 10
    IVFSPEA2_V4_ADAPTIVE  -> H4: Stagnation trigger
    IVFSPEA2_V5_MUTATION  -> H5: Post-SBX mutation
"""

import os
import sys
import json
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/home/pedro/desenvolvimento/ivfspea2"
PHASE1_DIR = os.path.join(PROJECT_ROOT, "data", "ablation_v2", "phase1")
if not os.path.isdir(PHASE1_DIR):
    PHASE1_DIR = os.path.join(PROJECT_ROOT, "data", "legacy", "ablation_v2", "phase1")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "ablation_v2", "phase1")
ALPHA = 0.05

# (folder_prefix, display_name, hypothesis_id)
CONFIGS = [
    ("IVFSPEA2", "B (v1 baseline)", None),
    ("IVFSPEA2_V1_DISSIM", "V1 (dissim.)", "H1"),
    ("IVFSPEA2_V2_COLLECTIVE", "V2 (collective)", "H2"),
    ("IVFSPEA2_V3_ETA10", r"V3 ($\eta_c=10$)", "H3"),
    ("IVFSPEA2_V4_ADAPTIVE", "V4 (adaptive)", "H4"),
    ("IVFSPEA2_V5_MUTATION", "V5 (mutation)", "H5"),
]

PROBLEMS = [
    ("ZDT1", 2, "Convex continuous"),
    ("ZDT6", 2, "Concave non-uniform"),
    ("WFG4", 2, "Concave multimodal"),
    ("WFG9", 2, "Concave non-separable"),
    ("DTLZ1", 3, "Linear"),
    ("DTLZ2", 3, "Spherical regular"),
    ("DTLZ4", 3, "Spherical biased ★"),
    ("DTLZ7", 3, "Disconnected"),
    ("WFG2", 3, "Disconnected non-sep. ★"),
    ("WFG5", 3, "Concave degenerate"),
    ("MaF1", 3, "Linear inverted"),
    ("MaF5", 3, "Convex-inverted ★"),
]

BASELINE_KEY = "IVFSPEA2"

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_igd_from_mat(filepath: str) -> float | None:
    """Extract the final IGD value from a PlatEMO .mat file."""
    try:
        import pymatreader

        data = pymatreader.read_mat(filepath)
        metric = data.get("metric")
        if metric is None:
            return None
        igd = metric.get("IGD")
        if igd is None:
            return None
        if isinstance(igd, np.ndarray):
            return float(igd.flat[-1])
        return float(igd)
    except Exception as e:
        print(f"  WARN: Could not read {filepath}: {e}")
        return None


def load_phase1_data() -> pd.DataFrame:
    """Scan phase1 directory and collect per-run IGD values."""
    rows = []
    if not os.path.isdir(PHASE1_DIR):
        print(f"ERROR: Phase 1 directory not found: {PHASE1_DIR}")
        return pd.DataFrame()

    for folder_name in sorted(os.listdir(PHASE1_DIR)):
        folder_path = os.path.join(PHASE1_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # Parse folder name to identify config + problem + M
        # Examples:
        #   IVFSPEA2_ZDT1_M2          -> config=IVFSPEA2, prob=ZDT1, M=2
        #   IVFSPEA2_V1_DISSIM_ZDT1_M2 -> config=IVFSPEA2_V1_DISSIM, prob=ZDT1, M=2
        config_key = None
        prob_name = None
        m_val = None

        # Try matching each config prefix (longest first to avoid ambiguity)
        for cfg_prefix, _, _ in sorted(CONFIGS, key=lambda c: -len(c[0])):
            if folder_name.startswith(cfg_prefix + "_"):
                config_key = cfg_prefix
                remainder = folder_name[len(cfg_prefix) + 1 :]  # e.g., "ZDT1_M2"
                parts = remainder.rsplit("_", 1)
                if len(parts) == 2 and parts[1].startswith("M"):
                    prob_name = parts[0]
                    try:
                        m_val = int(parts[1].replace("M", ""))
                    except ValueError:
                        continue
                break

        if config_key is None or prob_name is None or m_val is None:
            print(f"  WARN: Could not parse folder: {folder_name}")
            continue

        mat_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".mat")])
        for mat_file in mat_files:
            igd = load_igd_from_mat(os.path.join(folder_path, mat_file))
            if igd is not None:
                rows.append(
                    {
                        "Config": config_key,
                        "Problem": prob_name,
                        "M": m_val,
                        "IGD": igd,
                    }
                )

    df = pd.DataFrame(rows)
    if len(df) > 0:
        print(
            f"Loaded {len(df)} IGD values across {df['Config'].nunique()} configurations"
        )
        for cfg, _, _ in CONFIGS:
            n = len(df[df["Config"] == cfg])
            print(f"  {cfg}: {n} values ({n // 12 if n >= 12 else n} per instance avg)")
    return df


# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------


def wilcoxon_test(x: np.ndarray, y: np.ndarray) -> tuple[str, float]:
    """Mann-Whitney U test. Returns (indicator, p_value).
    '+' if variant < baseline (better), '-' if variant > baseline (worse), '=' otherwise.
    """
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    if len(x) < 3 or len(y) < 3:
        return "=", 1.0
    try:
        _, p = mannwhitneyu(x, y, alternative="two-sided")
        if p < ALPHA:
            return ("+" if np.median(y) < np.median(x) else "-"), p
        return "=", p
    except Exception:
        return "=", 1.0


def format_median_iqr(values: np.ndarray) -> str:
    """Format as compact scientific notation: m.mm(i.ii)e+E"""
    values = values[~np.isnan(values)]
    if len(values) == 0:
        return "---"
    med = np.median(values)
    q25, q75 = np.percentile(values, [25, 75])
    iqr = q75 - q25
    if med == 0:
        return "0.00(0.00)e+0"
    exp = int(np.floor(np.log10(abs(med))))
    m = med / (10**exp)
    i = iqr / (10**exp)
    return f"{m:.2f}({i:.2f})e{exp:+d}"


# ---------------------------------------------------------------------------
# Promotion logic
# ---------------------------------------------------------------------------


def evaluate_promotion(df: pd.DataFrame) -> dict:
    """
    Evaluate each variant against baseline using promotion criteria.

    Returns dict: {hypothesis_id: {wins, ties, losses, median_improvements, promoted, reason}}
    """
    results = {}

    for cfg_prefix, display, hyp_id in CONFIGS:
        if hyp_id is None:  # Skip baseline
            continue

        wins = 0
        ties = 0
        losses = 0
        median_better = 0
        instance_details = []

        for prob, m_val, desc in PROBLEMS:
            base_data = df[
                (df["Config"] == BASELINE_KEY)
                & (df["Problem"] == prob)
                & (df["M"] == m_val)
            ]["IGD"].values

            var_data = df[
                (df["Config"] == cfg_prefix)
                & (df["Problem"] == prob)
                & (df["M"] == m_val)
            ]["IGD"].values

            if len(base_data) == 0 or len(var_data) == 0:
                instance_details.append(
                    {
                        "instance": f"{prob}(M={m_val})",
                        "indicator": "?",
                        "p_value": None,
                        "base_median": None,
                        "var_median": None,
                    }
                )
                continue

            indicator, p_val = wilcoxon_test(base_data, var_data)
            base_med = np.median(base_data)
            var_med = np.median(var_data)

            if indicator == "+":
                wins += 1
            elif indicator == "-":
                losses += 1
            else:
                ties += 1

            if var_med < base_med:
                median_better += 1

            instance_details.append(
                {
                    "instance": f"{prob}(M={m_val})",
                    "description": desc,
                    "indicator": indicator,
                    "p_value": round(p_val, 6),
                    "base_median": round(base_med, 8),
                    "var_median": round(var_med, 8),
                    "improvement_pct": round((base_med - var_med) / base_med * 100, 2)
                    if base_med != 0
                    else 0,
                }
            )

        # Apply promotion criteria
        criterion_a = wins >= 1 and losses == 0
        criterion_b = median_better >= 7
        promoted = criterion_a or criterion_b

        reason = []
        if criterion_a:
            reason.append(f"Criterion A: {wins} win(s), 0 losses")
        if criterion_b:
            reason.append(f"Criterion B: median better in {median_better}/12 instances")
        if not promoted:
            reason.append(
                f"NOT promoted: {wins}W/{ties}T/{losses}L, median better in {median_better}/12"
            )

        results[hyp_id] = {
            "config": cfg_prefix,
            "display": display,
            "wins": wins,
            "ties": ties,
            "losses": losses,
            "median_improvements": median_better,
            "promoted": promoted,
            "reason": "; ".join(reason),
            "details": instance_details,
        }

    return results


# ---------------------------------------------------------------------------
# Table generation
# ---------------------------------------------------------------------------


def generate_phase1_table(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Generate results DataFrame and LaTeX table for Phase 1 screening."""
    config_names = [c[0] for c in CONFIGS]
    config_display = {c[0]: c[1] for c in CONFIGS}

    rows = []
    for prob, m_val, desc in PROBLEMS:
        row = {"Problem": f"{prob}(M={m_val})"}

        base_data = df[
            (df["Config"] == BASELINE_KEY)
            & (df["Problem"] == prob)
            & (df["M"] == m_val)
        ]["IGD"].values

        best_median = np.inf
        best_cfg = ""

        for cfg_key, _, _ in CONFIGS:
            cfg_data = df[
                (df["Config"] == cfg_key) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values

            if len(cfg_data) == 0:
                row[f"{cfg_key}_formatted"] = "---"
                row[f"{cfg_key}_median"] = np.nan
                row[f"{cfg_key}_indicator"] = ""
                continue

            med = np.median(cfg_data)
            row[f"{cfg_key}_formatted"] = format_median_iqr(cfg_data)
            row[f"{cfg_key}_median"] = med

            if med < best_median:
                best_median = med
                best_cfg = cfg_key

            # Wilcoxon vs baseline
            if cfg_key != BASELINE_KEY and len(base_data) > 0:
                indicator, _ = wilcoxon_test(base_data, cfg_data)
                row[f"{cfg_key}_indicator"] = indicator
            else:
                row[f"{cfg_key}_indicator"] = ""

        row["best_cfg"] = best_cfg
        rows.append(row)

    result_df = pd.DataFrame(rows)

    # Generate LaTeX
    n_cfg = len(config_names)
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(
        r"\caption{Phase 1 Screening: median IGD (IQR) over 30 runs. "
        r"Symbols: $+$ = variant significantly better than baseline, "
        r"$-$ = significantly worse, "
        r"$\approx$ = no significant difference (Wilcoxon, $\alpha=0.05$). "
        r"Best median per instance in \textbf{bold}.}"
    )
    lines.append(r"\label{tab:ablation_v2_phase1}")
    lines.append(r"\centering\scriptsize")
    lines.append(r"\resizebox{\textwidth}{!}{%")
    lines.append(r"\begin{tabular}{l" + "r" * n_cfg + "}")
    lines.append(r"\toprule")

    # Header
    header = ["Instance"] + [config_display[c] for c in config_names]
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\midrule")

    for _, row in result_df.iterrows():
        parts = [row["Problem"]]
        for cfg_key in config_names:
            cell = row.get(f"{cfg_key}_formatted", "---")
            indicator = row.get(f"{cfg_key}_indicator", "")

            if row.get("best_cfg") == cfg_key:
                cell = r"\textbf{" + cell + "}"

            if indicator == "+":
                cell += r"$^{+}$"
            elif indicator == "-":
                cell += r"$^{-}$"
            elif indicator == "=":
                cell += r"$^{\approx}$"

            parts.append(cell)
        lines.append(" & ".join(parts) + r" \\")

    # Summary row
    lines.append(r"\midrule")
    summary_parts = [r"$+/\approx/-$"]
    for cfg_key in config_names:
        if cfg_key == BASELINE_KEY:
            summary_parts.append("---")
        else:
            indicators = result_df[f"{cfg_key}_indicator"].tolist()
            w = indicators.count("+")
            t = indicators.count("=")
            l = indicators.count("-")
            summary_parts.append(f"{w}/{t}/{l}")
    lines.append(" & ".join(summary_parts) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}%")
    lines.append(r"}")
    lines.append(r"\end{table*}")

    return result_df, "\n".join(lines)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_phase1_boxplots(df: pd.DataFrame):
    """Generate box-plot figure comparing variants across the 12 instances."""
    n_probs = len(PROBLEMS)
    ncols = 4
    nrows = (n_probs + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
    axes = axes.flatten()

    config_names = [c[0] for c in CONFIGS]
    config_display = [c[1] for c in CONFIGS]
    colors = ["#607D8B", "#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336"]

    for idx, (prob, m_val, desc) in enumerate(PROBLEMS):
        ax = axes[idx]
        data_list = []
        labels = []
        for c_idx, (cfg_key, display, _) in enumerate(CONFIGS):
            vals = df[
                (df["Config"] == cfg_key) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values
            if len(vals) > 0:
                data_list.append(vals)
                labels.append(display)

        if data_list:
            bp = ax.boxplot(data_list, labels=labels, patch_artist=True, widths=0.6)
            for patch, color in zip(bp["boxes"], colors[: len(data_list)]):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

        ax.set_title(f"{prob} (M={m_val})\n{desc}", fontsize=9)
        ax.set_ylabel("IGD" if idx % ncols == 0 else "")
        ax.tick_params(axis="x", rotation=60, labelsize=6)

    # Hide unused subplots
    for idx in range(n_probs, len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle(
        "Phase 1 Screening: IVF/SPEA2 v2 Variants vs. Baseline", fontsize=13, y=1.02
    )
    plt.tight_layout()

    fig_path = os.path.join(OUTPUT_DIR, "phase1_boxplots.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


def plot_promotion_summary(promotion: dict):
    """Visual summary of promotion decisions."""
    fig, ax = plt.subplots(figsize=(10, 4))

    hyp_ids = list(promotion.keys())
    x = np.arange(len(hyp_ids))
    width = 0.25

    wins = [promotion[h]["wins"] for h in hyp_ids]
    ties = [promotion[h]["ties"] for h in hyp_ids]
    losses = [promotion[h]["losses"] for h in hyp_ids]
    median_imps = [promotion[h]["median_improvements"] for h in hyp_ids]

    bars1 = ax.bar(x - width, wins, width, label="Wins (+)", color="#4CAF50", alpha=0.8)
    bars2 = ax.bar(x, ties, width, label="Ties (≈)", color="#FFC107", alpha=0.8)
    bars3 = ax.bar(
        x + width, losses, width, label="Losses (−)", color="#F44336", alpha=0.8
    )

    # Add median improvement line
    ax2 = ax.twinx()
    ax2.plot(x, median_imps, "ko--", label="Median better (of 12)", markersize=8)
    ax2.axhline(y=7, color="gray", linestyle=":", alpha=0.5, label="Threshold (7/12)")
    ax2.set_ylabel("Instances with better median")
    ax2.set_ylim(0, 13)
    ax2.legend(loc="upper right", fontsize=8)

    # Highlight promoted
    for i, h in enumerate(hyp_ids):
        if promotion[h]["promoted"]:
            ax.axvspan(i - 0.4, i + 0.4, alpha=0.1, color="green")
            ax.text(
                i,
                max(wins + ties + losses) + 0.3,
                "✓ PROMOTED",
                ha="center",
                fontsize=8,
                color="green",
                fontweight="bold",
            )
        else:
            ax.text(
                i,
                max(wins + ties + losses) + 0.3,
                "✗ NOT PROMOTED",
                ha="center",
                fontsize=8,
                color="red",
            )

    labels = [f"{h}\n{promotion[h]['display']}" for h in hyp_ids]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Count (of 12 instances)")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Phase 1 Screening: Promotion Decisions", fontsize=12)

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_DIR, "phase1_promotion_summary.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 70)
    print("IVF/SPEA2 v2 ABLATION — PHASE 1 SCREENING ANALYSIS")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load data
    df = load_phase1_data()
    if df.empty:
        print("No Phase 1 data found. Run experiments first.")
        sys.exit(1)

    # 2. Save raw data
    csv_path = os.path.join(OUTPUT_DIR, "phase1_raw_igd.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nSaved raw data: {csv_path}")

    # 3. Generate table
    result_df, latex = generate_phase1_table(df)
    tex_path = os.path.join(OUTPUT_DIR, "phase1_table.tex")
    with open(tex_path, "w") as f:
        f.write(latex)
    print(f"Saved LaTeX table: {tex_path}")

    summary_csv = os.path.join(OUTPUT_DIR, "phase1_summary.csv")
    result_df.to_csv(summary_csv, index=False)
    print(f"Saved summary CSV: {summary_csv}")

    # 4. Generate plots
    plot_phase1_boxplots(df)

    # 5. Evaluate promotion
    print("\n" + "=" * 70)
    print("PROMOTION EVALUATION")
    print("=" * 70)

    promotion = evaluate_promotion(df)
    promoted_factors = []

    for hyp_id in ["H1", "H2", "H3", "H4", "H5"]:
        info = promotion[hyp_id]
        status = "✅ PROMOTED" if info["promoted"] else "❌ NOT PROMOTED"
        print(f"\n{'─' * 50}")
        print(f"  {hyp_id} — {info['display']}: {status}")
        print(f"  Wins/Ties/Losses: {info['wins']}/{info['ties']}/{info['losses']}")
        print(f"  Median improvements: {info['median_improvements']}/12")
        print(f"  Reason: {info['reason']}")

        if info["promoted"]:
            promoted_factors.append(hyp_id)

        # Per-instance details
        print(
            f"  {'Instance':<20s} {'Indic':>5s} {'p-value':>10s} {'Base med':>12s} {'Var med':>12s} {'Δ%':>8s}"
        )
        for det in info["details"]:
            p_str = f"{det['p_value']:.4f}" if det["p_value"] is not None else "N/A"
            b_str = (
                f"{det['base_median']:.6f}" if det["base_median"] is not None else "N/A"
            )
            v_str = (
                f"{det['var_median']:.6f}" if det["var_median"] is not None else "N/A"
            )
            d_str = (
                f"{det.get('improvement_pct', 0):+.1f}%"
                if det.get("improvement_pct") is not None
                else "N/A"
            )
            print(
                f"  {det['instance']:<20s} {det['indicator']:>5s} {p_str:>10s} {b_str:>12s} {v_str:>12s} {d_str:>8s}"
            )

    plot_promotion_summary(promotion)

    # Summary
    print(f"\n{'=' * 70}")
    print("PHASE 1 RESULTS SUMMARY")
    print(f"{'=' * 70}")
    print(f"\nPromoted factors: {promoted_factors if promoted_factors else 'NONE'}")
    if promoted_factors:
        k = len(promoted_factors)
        combos = 2**k
        total_runs = combos * 12 * 60
        print(f"\nPhase 2 design: 2^{k} = {combos} factorial combinations")
        print(f"Phase 2 total runs: {combos} × 12 instances × 60 runs = {total_runs:,}")
    else:
        print("\n⚠  No factors promoted. Consider:")
        print("   - Relaxing the promotion criteria")
        print("   - Investigating factor interactions directly")
        print("   - Reviewing the experimental setup")

    # Save promotion results
    promotion_path = os.path.join(OUTPUT_DIR, "phase1_promotion.json")
    # Remove numpy types for JSON serialization
    promotion_clean = {}
    for k, v in promotion.items():
        promotion_clean[k] = {
            key: (val if not isinstance(val, (np.integer, np.floating)) else val.item())
            for key, val in v.items()
        }
    with open(promotion_path, "w") as f:
        json.dump(promotion_clean, f, indent=2, default=str)
    print(f"\nSaved promotion results: {promotion_path}")
    print(f"All outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
