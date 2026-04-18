#!/usr/bin/env python3
"""
IVF/SPEA2 v2 Ablation — Phase 2 Factorial Analysis
=====================================================
Parses PlatEMO .mat result files from the Phase 2 full factorial experiment
(2^4 = 16 combinations of H1/H2/H3/H4) and performs:

  1. Friedman ANOVA for global ranking across all instances
  2. Wilcoxon pairwise tests (with Holm correction) for pairwise comparisons
  3. Factor main-effect analysis (average rank contribution of each factor)
  4. Interaction detection (2-factor synergy/antagonism)

Produces:
  1. Console report with rankings and statistical results
  2. LaTeX table: median(IQR) per config per instance, with best bold
  3. Friedman ranking table (LaTeX)
  4. Pairwise Wilcoxon matrix heatmap
  5. Factor effect bar chart
  6. CSV with per-run IGD values
  7. Summary JSON

Expected input layout:
  data/ablation_v2/phase2/IVFSPEA2_P2_C<XX>_<PROB>_M<X>/*.mat

Usage:
  python src/python/analysis/analyze_ablation_v2_phase2.py
"""

import os
import sys
import json
import warnings
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.stats import friedmanchisquare, mannwhitneyu, rankdata

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/home/pedro/desenvolvimento/ivfspea2"
PHASE2_DIR = os.path.join(PROJECT_ROOT, "data", "ablation_v2", "phase2")
if not os.path.isdir(PHASE2_DIR):
    PHASE2_DIR = os.path.join(PROJECT_ROOT, "data", "legacy", "ablation_v2", "phase2")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "ablation_v2", "phase2")
ALPHA = 0.05

# All 16 factorial combinations: (config_id, label, H1, H2, H3, H4)
CONFIGS = [
    ("P2_C00", "0000 (baseline)", 0, 0, 0, 0),
    ("P2_C01", "1000 (H1)", 1, 0, 0, 0),
    ("P2_C02", "0100 (H2)", 0, 1, 0, 0),
    ("P2_C03", "0010 (H3)", 0, 0, 1, 0),
    ("P2_C04", "0001 (H4)", 0, 0, 0, 1),
    ("P2_C05", "1100 (H1+H2)", 1, 1, 0, 0),
    ("P2_C06", "1010 (H1+H3)", 1, 0, 1, 0),
    ("P2_C07", "1001 (H1+H4)", 1, 0, 0, 1),
    ("P2_C08", "0110 (H2+H3)", 0, 1, 1, 0),
    ("P2_C09", "0101 (H2+H4)", 0, 1, 0, 1),
    ("P2_C10", "0011 (H3+H4)", 0, 0, 1, 1),
    ("P2_C11", "1110 (H1+H2+H3)", 1, 1, 1, 0),
    ("P2_C12", "1101 (H1+H2+H4)", 1, 1, 0, 1),
    ("P2_C13", "1011 (H1+H3+H4)", 1, 0, 1, 1),
    ("P2_C14", "0111 (H2+H3+H4)", 0, 1, 1, 1),
    ("P2_C15", "1111 (all)", 1, 1, 1, 1),
]

FACTOR_NAMES = ["H1 (dissim.)", "H2 (collective)", "H3 (eta10)", "H4 (adaptive)"]

PROBLEMS = [
    ("ZDT1", 2, "Convex continuous"),
    ("ZDT6", 2, "Concave non-uniform"),
    ("WFG4", 2, "Concave multimodal"),
    ("WFG9", 2, "Concave non-separable"),
    ("DTLZ1", 3, "Linear"),
    ("DTLZ2", 3, "Spherical regular"),
    ("DTLZ4", 3, "Spherical biased"),
    ("DTLZ7", 3, "Disconnected"),
    ("WFG2", 3, "Disconnected non-sep."),
    ("WFG5", 3, "Concave degenerate"),
    ("MaF1", 3, "Linear inverted"),
    ("MaF5", 3, "Convex-inverted"),
]


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


def load_phase2_data() -> pd.DataFrame:
    """Scan phase2 directory and collect per-run IGD values."""
    rows = []
    if not os.path.isdir(PHASE2_DIR):
        print(f"ERROR: Phase 2 directory not found: {PHASE2_DIR}")
        return pd.DataFrame()

    config_prefixes = {c[0]: c for c in CONFIGS}

    for folder_name in sorted(os.listdir(PHASE2_DIR)):
        folder_path = os.path.join(PHASE2_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # Parse: IVFSPEA2_P2_C<XX>_<PROB>_M<X>
        config_key = None
        prob_name = None
        m_val = None

        for cfg_id in sorted(config_prefixes.keys(), key=lambda x: -len(x)):
            prefix = f"IVFSPEA2_{cfg_id}_"
            if folder_name.startswith(prefix):
                config_key = cfg_id
                remainder = folder_name[len(prefix) :]  # e.g., "ZDT1_M2"
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
        for cfg_id, label, *_ in CONFIGS:
            n = len(df[df["Config"] == cfg_id])
            if n > 0:
                print(f"  {cfg_id} [{label}]: {n} values")
    return df


# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------


def compute_median_ranks(df: pd.DataFrame) -> pd.DataFrame:
    """Compute median IGD per config per instance, then rank across configs."""
    config_ids = [c[0] for c in CONFIGS]

    rows = []
    for prob, m_val, desc in PROBLEMS:
        medians = {}
        for cfg_id in config_ids:
            vals = df[
                (df["Config"] == cfg_id) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values
            if len(vals) > 0:
                medians[cfg_id] = np.median(vals)
            else:
                medians[cfg_id] = np.inf

        # Rank (lower IGD = better = rank 1)
        med_values = np.array([medians[c] for c in config_ids])
        ranks = rankdata(med_values, method="average")

        row = {"Problem": f"{prob}(M={m_val})"}
        for i, cfg_id in enumerate(config_ids):
            row[f"{cfg_id}_median"] = medians[cfg_id]
            row[f"{cfg_id}_rank"] = ranks[i]
        rows.append(row)

    return pd.DataFrame(rows)


def friedman_test(df: pd.DataFrame) -> tuple[float, float, np.ndarray]:
    """Friedman test across all configs for each instance.

    Returns: (chi2, p_value, average_ranks)
    """
    config_ids = [c[0] for c in CONFIGS]
    n_configs = len(config_ids)
    n_instances = len(PROBLEMS)

    # Build rank matrix: instances × configs
    rank_matrix = np.zeros((n_instances, n_configs))

    for i, (prob, m_val, _) in enumerate(PROBLEMS):
        medians = []
        for cfg_id in config_ids:
            vals = df[
                (df["Config"] == cfg_id) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values
            medians.append(np.median(vals) if len(vals) > 0 else np.inf)

        rank_matrix[i, :] = rankdata(medians, method="average")

    avg_ranks = rank_matrix.mean(axis=0)

    # Friedman test
    try:
        groups = [rank_matrix[:, j] for j in range(n_configs)]
        chi2, p_val = friedmanchisquare(*groups)
    except Exception:
        chi2, p_val = 0.0, 1.0

    return chi2, p_val, avg_ranks


def wilcoxon_pairwise(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pairwise Wilcoxon (Mann-Whitney U) tests between all config pairs.

    Uses median IGD per instance as the comparison unit.
    Returns (p_value_matrix, adjusted_p_matrix) with Holm correction.
    """
    config_ids = [c[0] for c in CONFIGS]
    n = len(config_ids)

    # Collect median IGD vectors (one median per instance)
    median_vectors = {}
    for cfg_id in config_ids:
        vec = []
        for prob, m_val, _ in PROBLEMS:
            vals = df[
                (df["Config"] == cfg_id) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values
            vec.append(np.median(vals) if len(vals) > 0 else np.inf)
        median_vectors[cfg_id] = np.array(vec)

    p_matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            try:
                _, p = mannwhitneyu(
                    median_vectors[config_ids[i]],
                    median_vectors[config_ids[j]],
                    alternative="two-sided",
                )
            except Exception:
                p = 1.0
            p_matrix[i, j] = p
            p_matrix[j, i] = p

    # Holm correction
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((i, j, p_matrix[i, j]))
    pairs.sort(key=lambda x: x[2])

    m_tests = len(pairs)
    adjusted = np.ones((n, n))
    for rank_idx, (i, j, p) in enumerate(pairs):
        adj_p = min(p * (m_tests - rank_idx), 1.0)
        adjusted[i, j] = adj_p
        adjusted[j, i] = adj_p

    idx = pd.Index(config_ids)
    return (
        pd.DataFrame(p_matrix, index=idx, columns=idx),
        pd.DataFrame(adjusted, index=idx, columns=idx),
    )


# ---------------------------------------------------------------------------
# Factor analysis
# ---------------------------------------------------------------------------


def analyze_factor_effects(avg_ranks: np.ndarray) -> dict:
    """Compute main effect of each factor as average rank difference.

    For each factor Hk:
      effect(Hk) = mean_rank(Hk=0) - mean_rank(Hk=1)
      Positive = factor helps (lower rank when ON)
    """
    config_ids = [c[0] for c in CONFIGS]
    factor_flags = {c[0]: (c[2], c[3], c[4], c[5]) for c in CONFIGS}

    effects = {}
    for f_idx, f_name in enumerate(FACTOR_NAMES):
        on_ranks = []
        off_ranks = []
        for i, cfg_id in enumerate(config_ids):
            if factor_flags[cfg_id][f_idx] == 1:
                on_ranks.append(avg_ranks[i])
            else:
                off_ranks.append(avg_ranks[i])

        mean_on = np.mean(on_ranks) if on_ranks else 0
        mean_off = np.mean(off_ranks) if off_ranks else 0
        effects[f_name] = {
            "mean_rank_on": round(mean_on, 3),
            "mean_rank_off": round(mean_off, 3),
            "effect": round(mean_off - mean_on, 3),  # positive = helps
        }

    return effects


def analyze_interactions(avg_ranks: np.ndarray) -> dict:
    """Detect 2-factor interactions (synergy/antagonism).

    Interaction(Hk, Hl) = effect(Hk+Hl together) - effect(Hk alone) - effect(Hl alone)
    Positive = synergy, Negative = antagonism
    """
    config_ids = [c[0] for c in CONFIGS]
    factor_flags = {c[0]: (c[2], c[3], c[4], c[5]) for c in CONFIGS}
    rank_map = {cfg_id: avg_ranks[i] for i, cfg_id in enumerate(config_ids)}

    # Baseline rank
    baseline_rank = rank_map.get("P2_C00", 0)

    interactions = {}
    for fi, fj in combinations(range(4), 2):
        fi_name = FACTOR_NAMES[fi]
        fj_name = FACTOR_NAMES[fj]

        # Find configs where only fi is on
        fi_only_ranks = []
        fj_only_ranks = []
        both_ranks = []
        neither_ranks = []

        for cfg_id, flags in factor_flags.items():
            fi_on = flags[fi] == 1
            fj_on = flags[fj] == 1

            r = rank_map[cfg_id]
            if fi_on and not fj_on:
                fi_only_ranks.append(r)
            elif fj_on and not fi_on:
                fj_only_ranks.append(r)
            elif fi_on and fj_on:
                both_ranks.append(r)
            else:
                neither_ranks.append(r)

        mean_neither = np.mean(neither_ranks) if neither_ranks else 0
        mean_fi = np.mean(fi_only_ranks) if fi_only_ranks else 0
        mean_fj = np.mean(fj_only_ranks) if fj_only_ranks else 0
        mean_both = np.mean(both_ranks) if both_ranks else 0

        # Interaction = observed combined effect vs expected additive
        effect_fi = mean_neither - mean_fi
        effect_fj = mean_neither - mean_fj
        effect_both = mean_neither - mean_both
        interaction = effect_both - effect_fi - effect_fj

        interactions[f"{fi_name} x {fj_name}"] = {
            "effect_fi": round(effect_fi, 3),
            "effect_fj": round(effect_fj, 3),
            "effect_both": round(effect_both, 3),
            "interaction": round(interaction, 3),
            "type": "synergy"
            if interaction > 0.5
            else ("antagonism" if interaction < -0.5 else "additive"),
        }

    return interactions


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_median_iqr(values: np.ndarray) -> str:
    """Format as compact scientific notation."""
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
# Tables & Plots
# ---------------------------------------------------------------------------


def generate_ranking_table(avg_ranks: np.ndarray, chi2: float, p_val: float) -> str:
    """Generate LaTeX table with Friedman rankings."""
    config_ids = [c[0] for c in CONFIGS]
    config_labels = {c[0]: c[1] for c in CONFIGS}

    # Sort by average rank
    sorted_idx = np.argsort(avg_ranks)

    lines = []
    lines.append(r"\begin{table}[t]")
    lines.append(
        r"\caption{Phase 2 Friedman ranking across 12 benchmark instances. "
        f"Friedman $\\chi^2 = {chi2:.2f}$, $p = {p_val:.2e}$.}}"
    )
    lines.append(r"\label{tab:ablation_v2_phase2_ranking}")
    lines.append(r"\centering\small")
    lines.append(r"\begin{tabular}{clccccr}")
    lines.append(r"\toprule")
    lines.append(r"Rank & Config & H1 & H2 & H3 & H4 & Avg.\ Rank \\")
    lines.append(r"\midrule")

    for pos, idx in enumerate(sorted_idx, 1):
        cfg_id = config_ids[idx]
        cfg = next(c for c in CONFIGS if c[0] == cfg_id)
        h1, h2, h3, h4 = cfg[2], cfg[3], cfg[4], cfg[5]

        h1_str = r"\checkmark" if h1 else ""
        h2_str = r"\checkmark" if h2 else ""
        h3_str = r"\checkmark" if h3 else ""
        h4_str = r"\checkmark" if h4 else ""

        rank_str = f"{avg_ranks[idx]:.2f}"
        if pos == 1:
            rank_str = r"\textbf{" + rank_str + "}"

        lines.append(
            f"{pos} & {cfg[1]} & {h1_str} & {h2_str} & {h3_str} & {h4_str} & {rank_str} \\\\"
        )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def generate_detail_table(df: pd.DataFrame) -> str:
    """Generate detailed LaTeX table with median(IQR) per config per instance."""
    config_ids = [c[0] for c in CONFIGS]
    config_labels = {c[0]: c[1] for c in CONFIGS}

    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(
        r"\caption{Phase 2 Factorial: median IGD (IQR) over 60 runs. "
        r"Best median per instance in \textbf{bold}.}"
    )
    lines.append(r"\label{tab:ablation_v2_phase2_detail}")
    lines.append(r"\centering\tiny")
    lines.append(r"\setlength{\tabcolsep}{2pt}")
    lines.append(r"\begin{tabular}{l" + "r" * len(config_ids) + "}")
    lines.append(r"\toprule")

    # Header
    header_parts = ["Instance"]
    for cfg_id in config_ids:
        label = config_labels[cfg_id].split(" ")[0]  # Just the bit pattern
        header_parts.append(label)
    lines.append(" & ".join(header_parts) + r" \\")
    lines.append(r"\midrule")

    for prob, m_val, desc in PROBLEMS:
        parts = [f"{prob}({m_val})"]
        best_median = np.inf
        best_cfg = ""

        # First pass: find best
        for cfg_id in config_ids:
            vals = df[
                (df["Config"] == cfg_id) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values
            if len(vals) > 0:
                med = np.median(vals)
                if med < best_median:
                    best_median = med
                    best_cfg = cfg_id

        # Second pass: format cells
        for cfg_id in config_ids:
            vals = df[
                (df["Config"] == cfg_id) & (df["Problem"] == prob) & (df["M"] == m_val)
            ]["IGD"].values
            if len(vals) > 0:
                cell = format_median_iqr(vals)
                if cfg_id == best_cfg:
                    cell = r"\textbf{" + cell + "}"
            else:
                cell = "---"
            parts.append(cell)

        lines.append(" & ".join(parts) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")

    return "\n".join(lines)


def plot_ranking_bar(avg_ranks: np.ndarray):
    """Bar chart of average Friedman ranks."""
    config_labels = [c[1] for c in CONFIGS]
    sorted_idx = np.argsort(avg_ranks)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(CONFIGS)))

    y_pos = np.arange(len(CONFIGS))
    bars = ax.barh(
        y_pos,
        avg_ranks[sorted_idx],
        color=colors[np.argsort(np.argsort(avg_ranks[sorted_idx]))],
        edgecolor="black",
        linewidth=0.5,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels([config_labels[i] for i in sorted_idx], fontsize=8)
    ax.set_xlabel("Average Friedman Rank (lower is better)")
    ax.set_title("Phase 2: Friedman Ranking of 16 Factorial Combinations")
    ax.invert_yaxis()

    # Add value labels
    for bar, rank in zip(bars, avg_ranks[sorted_idx]):
        ax.text(
            bar.get_width() + 0.1,
            bar.get_y() + bar.get_height() / 2,
            f"{rank:.2f}",
            va="center",
            fontsize=7,
        )

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_DIR, "phase2_friedman_ranking.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


def plot_pairwise_heatmap(adj_p_matrix: pd.DataFrame):
    """Heatmap of adjusted pairwise p-values."""
    config_labels = [c[1].split(" ")[0] for c in CONFIGS]  # Just bit patterns

    fig, ax = plt.subplots(figsize=(12, 10))

    # Use -log10(p) for better visualization
    data = adj_p_matrix.values.copy()
    np.fill_diagonal(data, 1.0)
    log_data = -np.log10(data + 1e-300)

    mask = np.triu(np.ones_like(data, dtype=bool), k=0)
    masked_data = np.ma.array(log_data, mask=mask)

    cmap = plt.cm.YlOrRd
    im = ax.imshow(masked_data, cmap=cmap, aspect="auto", interpolation="nearest")

    ax.set_xticks(range(len(config_labels)))
    ax.set_xticklabels(config_labels, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(config_labels)))
    ax.set_yticklabels(config_labels, fontsize=7)

    # Add significance indicators
    for i in range(len(config_labels)):
        for j in range(i + 1, len(config_labels)):
            p = data[i, j]
            if p < 0.001:
                text = "***"
            elif p < 0.01:
                text = "**"
            elif p < 0.05:
                text = "*"
            else:
                text = ""
            ax.text(j, i, text, ha="center", va="center", fontsize=6, color="black")

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("-log10(adjusted p-value)")

    ax.set_title("Phase 2: Pairwise Wilcoxon (Holm-adjusted)")
    plt.tight_layout()

    fig_path = os.path.join(OUTPUT_DIR, "phase2_pairwise_heatmap.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


def plot_factor_effects(effects: dict):
    """Bar chart of factor main effects."""
    names = list(effects.keys())
    values = [effects[n]["effect"] for n in names]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4CAF50" if v > 0 else "#F44336" for v in values]
    bars = ax.bar(
        names, values, color=colors, edgecolor="black", linewidth=0.5, alpha=0.8
    )

    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_ylabel("Main Effect (avg rank OFF − avg rank ON)\nPositive = factor helps")
    ax.set_title("Phase 2: Factor Main Effects on Friedman Rank")
    ax.tick_params(axis="x", rotation=15)

    for bar, val in zip(bars, values):
        y_offset = 0.1 if val >= 0 else -0.3
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + y_offset,
            f"{val:+.2f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    fig_path = os.path.join(OUTPUT_DIR, "phase2_factor_effects.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


def plot_interaction_heatmap(interactions: dict):
    """Heatmap of 2-factor interactions."""
    n = len(FACTOR_NAMES)
    matrix = np.zeros((n, n))

    for key, info in interactions.items():
        parts = key.split(" x ")
        fi = FACTOR_NAMES.index(parts[0])
        fj = FACTOR_NAMES.index(parts[1])
        matrix[fi, fj] = info["interaction"]
        matrix[fj, fi] = info["interaction"]

    fig, ax = plt.subplots(figsize=(6, 5))

    vmax = max(abs(matrix.min()), abs(matrix.max()), 1.0)
    im = ax.imshow(
        matrix,
        cmap="RdBu_r",
        vmin=-vmax,
        vmax=vmax,
        aspect="auto",
        interpolation="nearest",
    )

    short_names = ["H1", "H2", "H3", "H4"]
    ax.set_xticks(range(n))
    ax.set_xticklabels(short_names, fontsize=10)
    ax.set_yticks(range(n))
    ax.set_yticklabels(short_names, fontsize=10)

    for i in range(n):
        for j in range(n):
            if i != j:
                val = matrix[i, j]
                label = f"{val:+.2f}"
                ax.text(j, i, label, ha="center", va="center", fontsize=9)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Interaction Effect (+ synergy, − antagonism)")

    ax.set_title("Phase 2: 2-Factor Interactions")
    plt.tight_layout()

    fig_path = os.path.join(OUTPUT_DIR, "phase2_interactions.pdf")
    plt.savefig(fig_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Saved figure: {fig_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 70)
    print("IVF/SPEA2 v2 ABLATION — PHASE 2 FACTORIAL ANALYSIS")
    print("=" * 70)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load data
    df = load_phase2_data()
    if df.empty:
        print("No Phase 2 data found. Run experiments first.")
        sys.exit(1)

    # 2. Save raw data
    csv_path = os.path.join(OUTPUT_DIR, "phase2_raw_igd.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nSaved raw data: {csv_path}")

    # 3. Friedman test
    print("\n" + "=" * 70)
    print("FRIEDMAN ANOVA RANKING")
    print("=" * 70)

    chi2, p_val, avg_ranks = friedman_test(df)
    config_ids = [c[0] for c in CONFIGS]
    config_labels = {c[0]: c[1] for c in CONFIGS}

    print(f"\nFriedman chi2 = {chi2:.4f}, p = {p_val:.2e}")
    if p_val < ALPHA:
        print("=> Significant differences exist among configurations.")
    else:
        print("=> No significant differences detected (proceed with caution).")

    # Print ranking
    sorted_idx = np.argsort(avg_ranks)
    print(
        f"\n{'Rank':<6s} {'Config':<25s} {'H1':>3s} {'H2':>3s} {'H3':>3s} {'H4':>3s} {'Avg Rank':>10s}"
    )
    print("-" * 60)
    for pos, idx in enumerate(sorted_idx, 1):
        cfg = next(c for c in CONFIGS if c[0] == config_ids[idx])
        print(
            f"{pos:<6d} {cfg[1]:<25s} {cfg[2]:>3d} {cfg[3]:>3d} {cfg[4]:>3d} {cfg[5]:>3d} {avg_ranks[idx]:>10.2f}"
        )

    # Save ranking table
    ranking_tex = generate_ranking_table(avg_ranks, chi2, p_val)
    tex_path = os.path.join(OUTPUT_DIR, "phase2_ranking_table.tex")
    with open(tex_path, "w") as f:
        f.write(ranking_tex)
    print(f"\nSaved ranking table: {tex_path}")

    # 4. Pairwise Wilcoxon
    print("\n" + "=" * 70)
    print("PAIRWISE WILCOXON (HOLM-ADJUSTED)")
    print("=" * 70)

    p_matrix, adj_matrix = wilcoxon_pairwise(df)

    # Report significant pairs
    sig_pairs = []
    for i in range(len(config_ids)):
        for j in range(i + 1, len(config_ids)):
            if adj_matrix.iloc[i, j] < ALPHA:
                sig_pairs.append((config_ids[i], config_ids[j], adj_matrix.iloc[i, j]))

    print(f"\nSignificant pairs (p_adj < {ALPHA}): {len(sig_pairs)}")
    for ci, cj, p in sorted(sig_pairs, key=lambda x: x[2]):
        li = config_labels[ci]
        lj = config_labels[cj]
        print(f"  {li} vs {lj}: p_adj = {p:.4f}")

    # Save matrices
    adj_csv = os.path.join(OUTPUT_DIR, "phase2_pairwise_adjusted.csv")
    adj_matrix.to_csv(adj_csv)
    print(f"\nSaved pairwise matrix: {adj_csv}")

    # 5. Factor effects
    print("\n" + "=" * 70)
    print("FACTOR MAIN EFFECTS")
    print("=" * 70)

    effects = analyze_factor_effects(avg_ranks)
    print(
        f"\n{'Factor':<25s} {'Rank ON':>10s} {'Rank OFF':>10s} {'Effect':>10s} {'Direction':>12s}"
    )
    print("-" * 70)
    for name, info in effects.items():
        direction = (
            "HELPS"
            if info["effect"] > 0
            else "HURTS"
            if info["effect"] < 0
            else "NEUTRAL"
        )
        print(
            f"{name:<25s} {info['mean_rank_on']:>10.3f} {info['mean_rank_off']:>10.3f} "
            f"{info['effect']:>+10.3f} {direction:>12s}"
        )

    # 6. Interactions
    print("\n" + "=" * 70)
    print("2-FACTOR INTERACTIONS")
    print("=" * 70)

    interactions = analyze_interactions(avg_ranks)
    print(
        f"\n{'Pair':<35s} {'Eff(i)':>8s} {'Eff(j)':>8s} {'Eff(ij)':>8s} {'Inter.':>8s} {'Type':>12s}"
    )
    print("-" * 80)
    for pair, info in interactions.items():
        print(
            f"{pair:<35s} {info['effect_fi']:>+8.3f} {info['effect_fj']:>+8.3f} "
            f"{info['effect_both']:>+8.3f} {info['interaction']:>+8.3f} {info['type']:>12s}"
        )

    # 7. Generate all outputs
    print("\n" + "=" * 70)
    print("GENERATING OUTPUTS")
    print("=" * 70)

    # Detail table
    detail_tex = generate_detail_table(df)
    detail_path = os.path.join(OUTPUT_DIR, "phase2_detail_table.tex")
    with open(detail_path, "w") as f:
        f.write(detail_tex)
    print(f"Saved detail table: {detail_path}")

    # Plots
    plot_ranking_bar(avg_ranks)
    plot_pairwise_heatmap(adj_matrix)
    plot_factor_effects(effects)
    plot_interaction_heatmap(interactions)

    # 8. Winner identification
    print("\n" + "=" * 70)
    print("WINNER IDENTIFICATION")
    print("=" * 70)

    best_idx = sorted_idx[0]
    best_cfg = next(c for c in CONFIGS if c[0] == config_ids[best_idx])
    print(f"\nBest configuration: {best_cfg[1]}")
    print(f"  Config ID: {best_cfg[0]}")
    print(f"  H1={best_cfg[2]}, H2={best_cfg[3]}, H3={best_cfg[4]}, H4={best_cfg[5]}")
    print(f"  Average Friedman rank: {avg_ranks[best_idx]:.2f}")

    # Top 3
    print("\nTop 3 configurations:")
    for pos in range(min(3, len(sorted_idx))):
        idx = sorted_idx[pos]
        cfg = next(c for c in CONFIGS if c[0] == config_ids[idx])
        print(f"  {pos + 1}. {cfg[1]} (rank {avg_ranks[idx]:.2f})")

    # 9. Save summary JSON
    summary = {
        "friedman": {
            "chi2": float(chi2),
            "p_value": float(p_val),
            "significant": bool(p_val < ALPHA),
        },
        "ranking": [
            {
                "rank": pos + 1,
                "config_id": config_ids[sorted_idx[pos]],
                "label": config_labels[config_ids[sorted_idx[pos]]],
                "avg_rank": float(avg_ranks[sorted_idx[pos]]),
            }
            for pos in range(len(sorted_idx))
        ],
        "factor_effects": effects,
        "interactions": interactions,
        "significant_pairs": len(sig_pairs),
        "winner": {
            "config_id": best_cfg[0],
            "label": best_cfg[1],
            "H1": best_cfg[2],
            "H2": best_cfg[3],
            "H3": best_cfg[4],
            "H4": best_cfg[5],
            "avg_rank": float(avg_ranks[best_idx]),
        },
    }

    summary_path = os.path.join(OUTPUT_DIR, "phase2_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary: {summary_path}")
    print(f"All outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
