#!/usr/bin/env python3
"""Generate the v3 main figures for the hosts paper (bump chart and shared loaders)."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ivfspea2.figio import save_figure


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
PAPER_FIG_DIR = os.path.join(PROJECT_ROOT, "paper", "ppsn2026-ivf-hosts", "figures")
SENSITIVITY_CSV = os.path.join(PROJECT_ROOT, "results", "sensitivity_analysis_igd.csv")
DATA_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "hosts_paper.csv")

TRACKS = [
    ("IVFSPEA2", "IVF/SPEA2"),
    ("IVFNSGAIII", "IVF/NSGA-III"),
    ("IVFNSGAII", "IVF/NSGA-II"),
]

TRACK_COLORS = {
    "IVF/SPEA2": "#4c72b0",
    "IVF/NSGA-III": "#55a868",
    "IVF/NSGA-II": "#c44e52",
}

GROUP_COLORS = {
    "ZDT": "#1f77b4",
    "DTLZ": "#ff7f0e",
    "WFG": "#2ca02c",
    "MaF": "#d62728",
    "RWMOP": "#9467bd",
}

for out_dir in (FIG_DIR, PAPER_FIG_DIR):
    os.makedirs(out_dir, exist_ok=True)


# ---------------------------------------------------------------------------
# Shared infrastructure loaders
# ---------------------------------------------------------------------------

def load_cross_host(metric: str = "IGD") -> pd.DataFrame:
    """Load the cross-host comparison CSV for a given metric (IGD or HV)."""
    filename = f"hosts_cross_host_ivf_{metric.lower()}.csv"
    path = os.path.join(TABLES_DIR, filename)
    return pd.read_csv(path)


def load_all_stats(algo_key: str, metric: str = "igd") -> pd.DataFrame:
    """Load per-algo stats CSV (e.g. hosts_ivfspea2_igd_stats.csv)."""
    filename = f"hosts_{algo_key.lower()}_{metric.lower()}_stats.csv"
    path = os.path.join(TABLES_DIR, filename)
    return pd.read_csv(path)


def load_hosts_paper() -> pd.DataFrame:
    """Load and merge all three tracks' IGD stats into one DataFrame."""
    frames = []
    for algo_key, label in TRACKS:
        df = load_all_stats(algo_key, "igd")
        df["algo"] = algo_key
        df["label"] = label
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_raw_hosts() -> pd.DataFrame:
    """Load the raw hosts_paper.csv with per-run IGD and HV values.

    Returns a DataFrame with columns: algo, problem, group, M, D, run, IGD, HV.
    """
    return pd.read_csv(DATA_CSV)


def load_sensitivity() -> pd.DataFrame:
    """Load sensitivity analysis IGD CSV (c x r grid per problem)."""
    return pd.read_csv(SENSITIVITY_CSV)


# ---------------------------------------------------------------------------
# Figure helpers
# ---------------------------------------------------------------------------

def save_fig(fig: plt.Figure, name: str) -> None:
    save_figure(fig, name, (FIG_DIR, PAPER_FIG_DIR))


# ---------------------------------------------------------------------------
# Bump chart: compute_block_ranks
# ---------------------------------------------------------------------------

def compute_block_ranks() -> pd.DataFrame:
    """Compute mean rank per algo_label for each analytical block.

    Blocks:
      - Global    : all rows in IGD data
      - M=2       : IGD rows where M == 2
      - M=3       : IGD rows where M == 3
      - DTLZ      : IGD rows where group == 'DTLZ'
      - WFG       : IGD rows where group == 'WFG'
      - MaF       : IGD rows where group == 'MaF'
      - ZDT       : IGD rows where group == 'ZDT'
      - IGD       : all rows in IGD data (metric-level)
      - HV        : all rows in HV data

    Returns a DataFrame indexed by (block, algo_label) with column 'mean_rank'.
    """
    igd = load_cross_host("IGD")
    hv = load_cross_host("HV")

    blocks: dict[str, pd.DataFrame] = {
        "Global": igd,
        "M=2": igd[igd["M"] == 2],
        "M=3": igd[igd["M"] == 3],
        "DTLZ": igd[igd["group"] == "DTLZ"],
        "WFG": igd[igd["group"] == "WFG"],
        "MaF": igd[igd["group"] == "MaF"],
        "ZDT": igd[igd["group"] == "ZDT"],
        "IGD": igd,
        "HV": hv,
    }

    records = []
    for block_name, df in blocks.items():
        mean_ranks = df.groupby("algo_label")["rank"].mean()
        for algo_label, mean_rank in mean_ranks.items():
            records.append(
                {"block": block_name, "algo_label": algo_label, "mean_rank": mean_rank}
            )

    result = pd.DataFrame(records).set_index(["block", "algo_label"])
    return result


# ---------------------------------------------------------------------------
# Figure 6: bump chart
# ---------------------------------------------------------------------------

BLOCK_ORDER = ["Global", "M=2", "M=3", "DTLZ", "WFG", "MaF", "ZDT", "IGD", "HV"]


def fig_bump_chart() -> None:
    """Bump chart showing rank stability across analytical blocks."""
    block_ranks = compute_block_ranks()

    algo_labels = [label for _, label in TRACKS]

    # Build a pivot: rows = algo_label, columns = block (in BLOCK_ORDER)
    pivot: dict[str, list[float]] = {label: [] for label in algo_labels}
    for block in BLOCK_ORDER:
        for label in algo_labels:
            try:
                rank = float(block_ranks.loc[(block, label), "mean_rank"])
            except KeyError:
                rank = float("nan")
            pivot[label].append(rank)

    x = list(range(len(BLOCK_ORDER)))

    fig, ax = plt.subplots(figsize=(10, 4))

    for label in algo_labels:
        ranks = pivot[label]
        color = TRACK_COLORS[label]
        ax.plot(
            x,
            ranks,
            marker="o",
            markersize=8,
            linewidth=2.0,
            color=color,
            label=label,
            zorder=3,
        )
        # Annotate rank values above each point
        for xi, rank in zip(x, ranks):
            if not (rank != rank):  # not NaN
                ax.text(
                    xi,
                    rank - 0.07,
                    f"{rank:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    color=color,
                )

    # Invert y-axis so rank 1 is at top
    ax.invert_yaxis()
    ax.set_ylim(3.3, 0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(BLOCK_ORDER, fontsize=10)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["1 (best)", "2", "3 (worst)"], fontsize=10)
    ax.set_ylabel("Mean rank position", fontsize=11)
    ax.set_title("Rank stability across analytical blocks", fontsize=12)

    # Vertical separator before IGD/HV blocks
    ax.axvline(6.5, color="gray", linewidth=0.8, linestyle="--", alpha=0.6)

    ax.legend(loc="upper right", fontsize=10, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig6_bump_chart.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Stratified W/T/L: compute_stratified_wtl
# ---------------------------------------------------------------------------

# Display order for benchmark families. Which of these actually appear is a
# property of the cohort, not of this list: the hosts pipeline excludes RWMOP9 by
# design (see build_hosts_paper_csv.py and cohort_filter.py), so the current
# cohort is synthetic-only. Naming families here fixes their order without
# asserting they are present.
FAMILY_ORDER = ["DTLZ", "MaF", "WFG", "ZDT", "RWMOP"]

M_STRATA = ["M=2", "M=3"]

WTL_COLORS = {
    "wins": "#2ecc71",
    "ties": "#95a5a6",
    "losses": "#e74c3c",
}


def strata_present(df: pd.DataFrame) -> list[str]:
    """Strata that ``df`` actually populates, in display order.

    A hardcoded stratum list emitted an empty RWMOP column for every host once
    the cohort became synthetic-only — three bars of zero height, indistinguishable
    from a genuine 0/0/0 result. Deriving the list from the data means the figure
    follows the cohort instead of contradicting it.
    """
    families = [group for group in FAMILY_ORDER if (df["group"] == group).any()]
    return M_STRATA + families


def compute_stratified_wtl(metric: str = "igd") -> pd.DataFrame:
    """Load all 3 track stats and compute W/T/L counts per (stratum, label).

    Strata are "M=2", "M=3", then each benchmark family present in the cohort.

    Returns a DataFrame with columns: stratum, label, wins, ties, losses.
    """
    records = []
    for algo_key, label in TRACKS:
        df = load_all_stats(algo_key, metric)
        for stratum in strata_present(df):
            if stratum.startswith("M="):
                m_val = int(stratum[2:])
                subset = df[df["M"] == m_val]
            else:
                subset = df[df["group"] == stratum]
            wins = (subset["sign"] == "+").sum()
            ties = (subset["sign"] == "=").sum()
            losses = (subset["sign"] == "-").sum()
            records.append(
                {
                    "stratum": stratum,
                    "label": label,
                    "wins": int(wins),
                    "ties": int(ties),
                    "losses": int(losses),
                }
            )
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Figure 7: stratified W/T/L stacked bar chart
# ---------------------------------------------------------------------------


def fig_stratified_wtl(metric: str = "igd") -> None:
    """3-panel stacked bar figure (one panel per host) showing W/T/L by stratum."""
    wtl = compute_stratified_wtl(metric)

    algo_labels = [label for _, label in TRACKS]
    # Read the axis off the computed frame, so the figure cannot disagree with
    # the table it is drawn from.
    strata = list(dict.fromkeys(wtl["stratum"]))
    n_strata = len(strata)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=False)

    for ax, label in zip(axes, algo_labels):
        sub = wtl[wtl["label"] == label].set_index("stratum").reindex(strata)

        x = list(range(n_strata))
        wins = sub["wins"].values
        ties = sub["ties"].values
        losses = sub["losses"].values

        bars_wins = ax.bar(x, wins, color=WTL_COLORS["wins"], label="Win", zorder=3)
        bars_ties = ax.bar(
            x, ties, bottom=wins, color=WTL_COLORS["ties"], label="Tie", zorder=3
        )
        bars_losses = ax.bar(
            x,
            losses,
            bottom=wins + ties,
            color=WTL_COLORS["losses"],
            label="Loss",
            zorder=3,
        )

        # Annotate non-zero counts inside bars
        for xi, (w, t, l) in enumerate(zip(wins, ties, losses)):
            if w > 0:
                ax.text(
                    xi,
                    w / 2,
                    str(w),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )
            if t > 0:
                ax.text(
                    xi,
                    w + t / 2,
                    str(t),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )
            if l > 0:
                ax.text(
                    xi,
                    w + t + l / 2,
                    str(l),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )

        # Vertical dashed separator between M-strata (x=0,1) and family-strata (x=2+)
        ax.axvline(1.5, color="gray", linewidth=1.0, linestyle="--", alpha=0.7)

        ax.set_xticks(x)
        ax.set_xticklabels(strata, fontsize=9, rotation=30, ha="right")
        ax.set_title(label, fontsize=11, fontweight="bold")
        ax.set_ylabel("Count" if ax is axes[0] else "", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", linestyle=":", alpha=0.4)

    # Shared legend on the first panel
    handles, labels_ = axes[0].get_legend_handles_labels()
    axes[0].legend(handles, labels_, loc="upper right", fontsize=9, framealpha=0.9)

    fig.suptitle(
        f"Stratified Win/Tie/Loss ({metric.upper()}) by M and benchmark family",
        fontsize=12,
    )
    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig7_stratified_wtl.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Sensitivity heatmap: compute_sensitivity_relative and fig_sensitivity_heatmap
# ---------------------------------------------------------------------------


def compute_sensitivity_relative(problem: str) -> pd.DataFrame:
    """Compute IGD relative to the SPEA2 baseline for a given problem.

    The baseline is R=0.0 (IVF disabled) when available, otherwise the minimum
    available R value is used as a pseudo-baseline.

    For each (C, R) cell, relative IGD = (IGD_Median - baseline_median) / baseline_median,
    where baseline_median is the median IGD_Median across all baseline rows for this problem.

    Returns a DataFrame with columns: R, C, IGD_Median, rel_igd.
    """
    df = load_sensitivity()
    prob_df = df[df["Problem"] == problem].copy()

    if prob_df.empty:
        raise ValueError(f"No rows found for problem '{problem}'")

    # Use R=0.0 as baseline if present, else minimum available R
    min_r = prob_df["R"].min()
    baseline_rows = prob_df[prob_df["R"] == min_r]
    baseline_median = baseline_rows["IGD_Median"].median()

    prob_df["rel_igd"] = (prob_df["IGD_Median"] - baseline_median) / baseline_median
    return prob_df[["R", "C", "IGD_Median", "rel_igd"]].reset_index(drop=True)


def fig_sensitivity_heatmap() -> None:
    """3-panel c x r sensitivity heatmap showing IGD relative to SPEA2 baseline.

    Auto-selects three representative problems:
      - best gain: lowest median relative IGD at R>0
      - neutral:   median relative IGD at R>0 closest to 0
      - adverse:   highest median relative IGD at R>0

    Axes: C (collection rate) on x, R (IVF trigger ratio) on y.
    Color = relative IGD change (RdYlGn_r diverging, centered at 0).
    Cells are annotated with the relative IGD value.
    Saved as hosts_v2_fig8_sensitivity.pdf.
    """
    df = load_sensitivity()
    problems = df["Problem"].unique()

    # Compute per-problem summary: median of rel_igd at rows above the baseline R
    summaries = []
    for prob in problems:
        rel_df = compute_sensitivity_relative(prob)
        min_r = rel_df["R"].min()
        active = rel_df[rel_df["R"] > min_r]["rel_igd"]
        summaries.append({"problem": prob, "median_rel_igd": active.median()})
    summary_df = pd.DataFrame(summaries).sort_values("median_rel_igd")

    best_gain = summary_df.iloc[0]["problem"]
    adverse = summary_df.iloc[-1]["problem"]
    # neutral: closest to 0
    neutral_row = summary_df.iloc[(summary_df["median_rel_igd"].abs()).argsort().iloc[0]]
    neutral = neutral_row["problem"]

    selected = [best_gain, neutral, adverse]
    panel_titles = [
        f"{best_gain} (gain)",
        f"{neutral} (neutral)",
        f"{adverse} (adverse)",
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, prob, title in zip(axes, selected, panel_titles):
        rel_df = compute_sensitivity_relative(prob)
        # Pivot: rows = R (descending, excluding baseline), columns = C (ascending)
        min_r = rel_df["R"].min()
        pivot = rel_df[rel_df["R"] > min_r].pivot(index="R", columns="C", values="rel_igd")
        pivot = pivot.sort_index(ascending=False)

        # Determine symmetric color limit
        vmax = max(abs(pivot.values[~np.isnan(pivot.values)].max()),
                   abs(pivot.values[~np.isnan(pivot.values)].min()))
        vmax = max(vmax, 0.01)  # guard against near-zero range

        sns.heatmap(
            pivot,
            ax=ax,
            cmap="RdYlGn_r",
            center=0,
            vmin=-vmax,
            vmax=vmax,
            annot=True,
            fmt=".2f",
            annot_kws={"fontsize": 7},
            linewidths=0.3,
            linecolor="lightgray",
            cbar_kws={"label": "Rel. IGD change"},
        )
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("C (collection rate)", fontsize=10)
        ax.set_ylabel("R (IVF trigger ratio)" if ax is axes[0] else "", fontsize=10)
        ax.tick_params(axis="x", labelsize=8, rotation=45)
        ax.tick_params(axis="y", labelsize=8, rotation=0)

    fig.suptitle(
        "Sensitivity of IGD relative to SPEA2 baseline (R=0)",
        fontsize=13,
        y=1.01,
    )
    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig8_sensitivity.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Raincloud plots: fig_raincloud
# ---------------------------------------------------------------------------

RAINCLOUD_ALGO_ORDER = [
    "IVFSPEA2", "SPEA2",
    "IVFNSGAIII", "NSGAIII",
    "IVFNSGAII", "NSGAII",
]

RAINCLOUD_COLORS = {
    "IVFSPEA2": "#4c72b0",
    "SPEA2": "#7faed4",
    "IVFNSGAIII": "#55a868",
    "NSGAIII": "#8fcf9f",
    "IVFNSGAII": "#c44e52",
    "NSGAII": "#e09095",
}

RAINCLOUD_LABELS = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "IVFNSGAIII": "IVF/NSGA-III",
    "NSGAIII": "NSGA-III",
    "IVFNSGAII": "IVF/NSGA-II",
    "NSGAII": "NSGA-II",
}

RAINCLOUD_CASES = [
    ("DTLZ2", 2, "Gain"),
    ("WFG1", 2, "Neutral"),
    ("MaF6", 2, "Adverse"),
]


def _draw_half_violin(ax, data, center, width, color, direction="right"):
    """Draw a half-violin (KDE) for `data` at x=`center`.

    direction='right' means the violin extends to the right of `center`.
    """
    from scipy.stats import gaussian_kde

    if len(data) < 2:
        return
    kde = gaussian_kde(data, bw_method="scott")
    y_min, y_max = data.min(), data.max()
    margin = (y_max - y_min) * 0.1 if y_max > y_min else 1e-10
    ys = np.linspace(y_min - margin, y_max + margin, 200)
    density = kde(ys)
    # Normalise to half-width
    if density.max() > 0:
        density = density / density.max() * width
    if direction == "right":
        xs_fill = center + density
    else:
        xs_fill = center - density
    ax.fill_betweenx(ys, center, xs_fill, alpha=0.5, color=color, linewidth=0)
    ax.plot(xs_fill, ys, color=color, linewidth=0.8)


def fig_raincloud() -> None:
    """3-panel raincloud figure for representative M=2 instances.

    Each panel: half-violin (right) + narrow boxplot (left) + jitter strip (right)
    for 6 algorithms in order: IVFSPEA2, SPEA2, IVFNSGAIII, NSGAIII, IVFNSGAII, NSGAII.
    Saved as hosts_v2_fig11_raincloud.pdf.
    """
    raw = load_raw_hosts()

    n_algos = len(RAINCLOUD_ALGO_ORDER)
    # Vertical spacing between algorithms
    y_positions = list(range(n_algos))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

    for i, (ax, (problem, m_val, scenario)) in enumerate(zip(axes, RAINCLOUD_CASES)):
        subset = raw[(raw["problem"] == problem) & (raw["M"] == m_val)]
        rng = np.random.default_rng(42 + i)

        ax.set_title(f"{problem} (M={m_val}, {scenario})", fontsize=11, fontweight="bold")

        violin_half_width = 0.35
        box_half_width = 0.08

        for yi, algo in enumerate(RAINCLOUD_ALGO_ORDER):
            algo_data = subset[subset["algo"] == algo]["IGD"].dropna().values
            color = RAINCLOUD_COLORS[algo]

            if len(algo_data) == 0:
                continue

            # Half-violin extending to the right
            _draw_half_violin(ax, algo_data, yi, violin_half_width, color, direction="right")

            # Jitter strip inside the violin area
            jitter = rng.uniform(0, violin_half_width * 0.8, size=len(algo_data))
            ax.scatter(
                yi + jitter,
                algo_data,
                color=color,
                alpha=0.3,
                s=8,
                linewidths=0,
                zorder=4,
            )

            # Narrow boxplot to the left of center
            q1, median, q3 = np.percentile(algo_data, [25, 50, 75])
            iqr = q3 - q1
            whisker_lo = max(algo_data.min(), q1 - 1.5 * iqr)
            whisker_hi = min(algo_data.max(), q3 + 1.5 * iqr)

            # Box
            box_rect = plt.Rectangle(
                (yi - box_half_width, q1),
                box_half_width,
                iqr,
                linewidth=1.2,
                edgecolor=color,
                facecolor="white",
                zorder=5,
            )
            ax.add_patch(box_rect)
            # Median line
            ax.plot(
                [yi - box_half_width, yi],
                [median, median],
                color=color,
                linewidth=1.5,
                zorder=6,
            )
            # Whiskers
            ax.plot([yi - box_half_width / 2, yi - box_half_width / 2],
                    [whisker_lo, q1], color=color, linewidth=1.0, zorder=5)
            ax.plot([yi - box_half_width / 2, yi - box_half_width / 2],
                    [q3, whisker_hi], color=color, linewidth=1.0, zorder=5)
            ax.plot([yi - box_half_width, yi],
                    [whisker_lo, whisker_lo], color=color, linewidth=1.0, zorder=5)
            ax.plot([yi - box_half_width, yi],
                    [whisker_hi, whisker_hi], color=color, linewidth=1.0, zorder=5)

        tick_labels = [RAINCLOUD_LABELS[a] for a in RAINCLOUD_ALGO_ORDER]
        ax.set_xticks(y_positions)
        ax.set_xticklabels(tick_labels, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("IGD" if ax is axes[0] else "", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", linestyle=":", alpha=0.4)

        # Vertical separators between host groups (after SPEA2, after NSGAIII)
        ax.axvline(1.5, color="gray", linewidth=0.6, linestyle="--", alpha=0.5)
        ax.axvline(3.5, color="gray", linewidth=0.6, linestyle="--", alpha=0.5)

    fig.suptitle(
        "IGD distributions across algorithms: representative M=2 instances",
        fontsize=12,
    )
    fig.tight_layout()
    save_fig(fig, "hosts_v2_fig11_raincloud.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("=== Generating hosts paper figures v3 ===\n")
    fig_bump_chart()
    fig_stratified_wtl()
    fig_sensitivity_heatmap()
    fig_raincloud()
    print("\nAll v3 figures written.")


if __name__ == "__main__":
    main()
