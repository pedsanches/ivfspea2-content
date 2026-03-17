#!/usr/bin/env python3
"""Generate five benchmark figures for IVF/SPEA2.

Figures generated:
  1) Problem-wise normalized profile (IGD + HV)
  2) Problem/algorithm boxplots (normalized IGD)
  3) Multi-algorithm Pareto panel (available synthetic fronts)
  4) Win/Tie/Loss + average rank by suite (IGD + HV)
  5) A12 effect-size heatmaps (IGD + HV)

The script uses only the canonical synthetic cohort:
  - IVF/SPEA2: runs 3001-3060
  - Baselines: runs 1-60
  - Suites: ZDT, DTLZ, WFG, MaF
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import mannwhitneyu, rankdata

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
DATA = os.path.join(
    ROOT, "data", "processed", "todas_metricas_consolidado_with_modern.csv"
)
FRONTS_DIR = os.path.join(ROOT, "data", "processed", "fronts")
OUT_FIG = os.path.join(ROOT, "paper", "figures")
OUT_TABLE = os.path.join(ROOT, "results", "tables")

SUITES = ["ZDT", "DTLZ", "WFG", "MaF"]
ALGORITHMS = [
    "IVFSPEA2",
    "SPEA2",
    "MFOSPEA2",
    "SPEA2SDE",
    "NSGAII",
    "NSGAIII",
    "MOEAD",
    "AGEMOEAII",
    "ARMOEA",
]

ALGO_DISPLAY = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-MOEA-II",
    "ARMOEA": "AR-MOEA",
}

PALETTE = {
    "IVFSPEA2": "#2166AC",
    "SPEA2": "#B2182B",
    "MFOSPEA2": "#D6604D",
    "SPEA2SDE": "#F4A582",
    "NSGAII": "#4DAF4A",
    "NSGAIII": "#984EA3",
    "MOEAD": "#FF7F00",
    "AGEMOEAII": "#A65628",
    "ARMOEA": "#999999",
}


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )


def _problem_number(problem: str) -> int:
    m = re.search(r"(\d+)", str(problem))
    return int(m.group(1)) if m else 0


def _instance_key(problem: str, m: str) -> str:
    return f"{problem}__{m}"


def _instance_label(problem: str, m: str) -> str:
    return f"{problem} ({m})"


def _split_instance(key: str) -> Tuple[str, str]:
    parts = str(key).split("__", 1)
    if len(parts) != 2:
        return str(key), "M?"
    return parts[0], parts[1]


def _suite_instance_order(df: pd.DataFrame, suite: str) -> List[str]:
    sub = df[df["Grupo"] == suite][["Problema", "M"]].drop_duplicates().copy()
    sub["m_order"] = sub["M"].map({"M2": 2, "M3": 3}).fillna(99)
    sub["p_num"] = sub["Problema"].map(_problem_number)
    sub = sub.sort_values(["m_order", "p_num", "Problema"])
    return [_instance_key(r.Problema, r.M) for r in sub.itertuples(index=False)]


def _a12(x: np.ndarray, y: np.ndarray, higher_is_better: bool) -> float:
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return np.nan
    if higher_is_better:
        better = sum(np.sum(xi > y) + 0.5 * np.sum(xi == y) for xi in x)
    else:
        better = sum(np.sum(xi < y) + 0.5 * np.sum(xi == y) for xi in x)
    return float(better / (nx * ny))


def _normalize(values: pd.Series, higher_is_better: bool) -> pd.Series:
    vmin = values.min()
    vmax = values.max()
    if pd.isna(vmin) or pd.isna(vmax) or vmax <= vmin:
        return pd.Series(np.full(len(values), 0.5), index=values.index)
    norm = (values - vmin) / (vmax - vmin)
    return norm if higher_is_better else 1.0 - norm


def load_data() -> pd.DataFrame:
    raw = pd.read_csv(DATA)
    df = filter_submission_synthetic_cohort(raw)
    df = df[df["Grupo"].isin(SUITES)].copy()
    df = df[df["Algoritmo"].isin(ALGORITHMS)].copy()
    df["instance"] = [
        _instance_key(p, m)
        for p, m in zip(df["Problema"].astype(str), df["M"].astype(str))
    ]
    df["instance_label"] = [
        _instance_label(p, m)
        for p, m in zip(df["Problema"].astype(str), df["M"].astype(str))
    ]
    return df


def figure1_profiles(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, higher in [("IGD", False), ("HV", True)]:
        med = (
            df.groupby(
                ["Grupo", "Problema", "M", "instance", "instance_label", "Algoritmo"],
                as_index=False,
            )[metric]
            .median()
            .rename(columns={metric: "value"})
        )
        med["score"] = np.nan
        for _, idx in med.groupby(["Grupo", "instance"]).groups.items():
            med.loc[idx, "score"] = _normalize(med.loc[idx, "value"], higher)
        med["metric"] = metric
        rows.append(med)

    profile = pd.concat(rows, ignore_index=True)
    profile.to_csv(os.path.join(OUT_TABLE, "fig1_profiles_normalized.csv"), index=False)

    _setup_style()
    fig, axes = plt.subplots(2, 4, figsize=(17.0, 7.4), sharey=True)

    for r, (metric, _) in enumerate([("IGD", False), ("HV", True)]):
        for c, suite in enumerate(SUITES):
            ax = axes[r, c]
            sub = profile[(profile["metric"] == metric) & (profile["Grupo"] == suite)]
            order = _suite_instance_order(df, suite)

            x = np.arange(len(order))
            for algo in ALGORITHMS:
                a = sub[sub["Algoritmo"] == algo].set_index("instance").reindex(order)
                if a.empty:
                    continue
                ax.plot(
                    x,
                    a["score"].to_numpy(dtype=float),
                    marker="o",
                    markersize=2.8 if algo == "IVFSPEA2" else 2.1,
                    linewidth=1.9 if algo == "IVFSPEA2" else 1.0,
                    color=PALETTE.get(algo, "#777777"),
                    alpha=0.95,
                )

            labels = [_instance_label(*_split_instance(inst)) for inst in order]
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=90)
            ax.set_ylim(-0.03, 1.03)
            ax.grid(True, axis="y", linestyle="--", alpha=0.22)
            ax.set_title(f"{suite} ({metric})")
            if c == 0:
                ax.set_ylabel("Normalized score")
            if r == 1:
                ax.set_xlabel("Problem (M)")

    handles = [
        Line2D(
            [0],
            [0],
            color=PALETTE.get(a, "#777777"),
            marker="o",
            lw=1.9 if a == "IVFSPEA2" else 1.0,
            markersize=3,
            label=ALGO_DISPLAY.get(a, a),
        )
        for a in ALGORITHMS
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=5,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle("Fig.1 - Normalized performance profiles by problem (IGD, HV)", y=1.01)
    plt.tight_layout(rect=[0, 0.07, 1, 0.96])

    pdf = os.path.join(OUT_FIG, "fig1_profile_igd_hv.pdf")
    png = os.path.join(OUT_FIG, "fig1_profile_igd_hv.png")
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    print(f"Saved: {pdf}")
    print(f"Saved: {png}")
    return profile


def figure2_boxplots(df: pd.DataFrame) -> None:
    box = df[
        [
            "Grupo",
            "Problema",
            "M",
            "instance",
            "instance_label",
            "Algoritmo",
            "Run",
            "IGD",
        ]
    ].copy()
    box["score"] = np.nan
    for _, idx in box.groupby(["Grupo", "instance"]).groups.items():
        box.loc[idx, "score"] = _normalize(box.loc[idx, "IGD"], higher_is_better=False)

    box.to_csv(os.path.join(OUT_TABLE, "fig2_boxplot_data_igd.csv"), index=False)

    _setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(18.0, 10.5), sharey=True)
    axes = axes.flatten()

    for ax, suite in zip(axes, SUITES):
        sub = box[box["Grupo"] == suite].copy()
        order = _suite_instance_order(df, suite)

        sns.boxplot(
            data=sub,
            x="instance",
            y="score",
            hue="Algoritmo",
            order=order,
            hue_order=ALGORITHMS,
            palette=PALETTE,
            showfliers=False,
            linewidth=0.45,
            ax=ax,
        )
        labels = [_instance_label(*_split_instance(inst)) for inst in order]
        ax.set_xticks(np.arange(len(order)))
        ax.set_xticklabels(labels, rotation=90)
        ax.set_ylim(-0.03, 1.03)
        ax.set_title(f"{suite} (IGD)")
        ax.set_xlabel("Problem (M)")
        ax.set_ylabel("Normalized score")
        ax.grid(True, axis="y", linestyle="--", alpha=0.22)
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    handles = [
        Line2D([0], [0], color=PALETTE[a], lw=3, label=ALGO_DISPLAY[a])
        for a in ALGORITHMS
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=5,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle("Fig.2 - Problem/algorithm boxplots (normalized IGD)", y=1.01)
    plt.tight_layout(rect=[0, 0.07, 1, 0.97])

    pdf = os.path.join(OUT_FIG, "fig2_boxplot_problem_algorithm_igd.pdf")
    png = os.path.join(OUT_FIG, "fig2_boxplot_problem_algorithm_igd.png")
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    print(f"Saved: {pdf}")
    print(f"Saved: {png}")


def _read_front(problem: str, m: str, algo: str) -> pd.DataFrame | None:
    path = os.path.join(FRONTS_DIR, f"{problem}_{m}_{algo}_median.csv")
    return pd.read_csv(path) if os.path.isfile(path) else None


def _read_true_pf(problem: str, m: str) -> pd.DataFrame | None:
    path = os.path.join(FRONTS_DIR, f"{problem}_{m}_truePF.csv")
    return pd.read_csv(path) if os.path.isfile(path) else None


def figure3_pareto_panels(df: pd.DataFrame) -> None:
    cases = [
        ("DTLZ2", "M2", ["IVFSPEA2", "SPEA2", "NSGAIII", "MOEAD"], "DTLZ2 (M2)"),
        (
            "WFG2",
            "M3",
            ["IVFSPEA2", "SPEA2", "NSGAIII", "MOEAD"],
            "WFG2 (M3, f1-f2 projection)",
        ),
    ]

    _setup_style()
    fig, axes = plt.subplots(2, 4, figsize=(12.8, 6.2), sharex=False, sharey=False)

    for r, (problem, m, algos, row_title) in enumerate(cases):
        pf = _read_true_pf(problem, m)
        fronts = {a: _read_front(problem, m, a) for a in algos}
        fronts = {k: v for k, v in fronts.items() if v is not None}
        if pf is None or not fronts:
            for c in range(4):
                axes[r, c].axis("off")
                axes[r, c].text(
                    0.5, 0.5, "Front data unavailable", ha="center", va="center"
                )
            continue

        xs = [pf["f1"].to_numpy()]
        ys = [pf["f2"].to_numpy()]
        for d in fronts.values():
            xs.append(d["f1"].to_numpy())
            ys.append(d["f2"].to_numpy())
        xall = np.concatenate(xs)
        yall = np.concatenate(ys)
        xpad = 0.03 * (xall.max() - xall.min() if xall.max() > xall.min() else 1)
        ypad = 0.03 * (yall.max() - yall.min() if yall.max() > yall.min() else 1)
        xlim = (xall.min() - xpad, xall.max() + xpad)
        ylim = (yall.min() - ypad, yall.max() + ypad)

        for c, algo in enumerate(algos):
            ax = axes[r, c]
            ad = fronts.get(algo)
            if ad is None:
                ax.axis("off")
                ax.text(0.5, 0.5, "Missing front", ha="center", va="center")
                continue

            ax.scatter(
                pf["f1"], pf["f2"], s=3, c="#D0D0D0", alpha=0.55, edgecolors="none"
            )
            ax.scatter(
                ad["f1"],
                ad["f2"],
                s=12,
                c=PALETTE.get(algo, "#444444"),
                alpha=0.82,
                edgecolors="none",
            )

            med_igd = df[
                (df["Problema"] == problem) & (df["M"] == m) & (df["Algoritmo"] == algo)
            ]["IGD"].median()
            txt = f"median IGD={med_igd:.3e}" if pd.notna(med_igd) else "median IGD=NA"

            ax.text(
                0.03,
                0.97,
                txt,
                transform=ax.transAxes,
                fontsize=6,
                va="top",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85),
            )
            ax.set_xlim(*xlim)
            ax.set_ylim(*ylim)
            ax.grid(True, linestyle="--", alpha=0.20)
            ax.set_xlabel("$f_1$")
            if c == 0:
                ax.set_ylabel("$f_2$")
            ax.set_title(ALGO_DISPLAY.get(algo, algo), fontsize=8)
            if c == 0:
                ax.text(
                    -0.34,
                    1.08,
                    row_title,
                    transform=ax.transAxes,
                    fontsize=9,
                    fontweight="bold",
                )

    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#D0D0D0",
            markersize=4,
            label="True PF",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#2166AC",
            markersize=4,
            label="Algorithm front",
        ),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=2,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle(
        "Fig.3 - Multi-algorithm Pareto panels (available synthetic fronts)", y=1.01
    )
    plt.tight_layout(rect=[0, 0.07, 1, 0.96], w_pad=1.0, h_pad=1.2)

    pdf = os.path.join(OUT_FIG, "fig3_pareto_algorithm_panels_available.pdf")
    png = os.path.join(OUT_FIG, "fig3_pareto_algorithm_panels_available.png")
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    print(f"Saved: {pdf}")
    print(f"Saved: {png}")


def _competence_summary(
    df: pd.DataFrame, metric: str, higher_is_better: bool
) -> pd.DataFrame:
    rows = []
    for suite in SUITES:
        sub = df[df["Grupo"] == suite]
        instances = sub[["Problema", "M", "instance"]].drop_duplicates()

        wins = ties = losses = 0
        ivf_ranks = []

        for r in instances.itertuples(index=False):
            blk = sub[sub["instance"] == r.instance]
            ivf = blk[blk["Algoritmo"] == "IVFSPEA2"][metric].dropna().to_numpy()
            spea = blk[blk["Algoritmo"] == "SPEA2"][metric].dropna().to_numpy()

            if len(ivf) >= 5 and len(spea) >= 5:
                _, pval = mannwhitneyu(ivf, spea, alternative="two-sided")
                a12 = _a12(ivf, spea, higher_is_better=higher_is_better)
                if pval < 0.05:
                    if a12 > 0.5:
                        wins += 1
                    elif a12 < 0.5:
                        losses += 1
                    else:
                        ties += 1
                else:
                    ties += 1
            else:
                ties += 1

            vals = []
            for algo in ALGORITHMS:
                v = blk[blk["Algoritmo"] == algo][metric].median()
                if pd.isna(v):
                    vals.append(-np.inf if higher_is_better else np.inf)
                else:
                    vals.append(-v if higher_is_better else v)
            ranks = rankdata(np.array(vals, dtype=float), method="average")
            ivf_ranks.append(float(ranks[ALGORITHMS.index("IVFSPEA2")]))

        rows.append(
            {
                "metric": metric,
                "suite": suite,
                "n_instances": int(len(instances)),
                "wins": int(wins),
                "ties": int(ties),
                "losses": int(losses),
                "avg_rank_ivf": float(np.mean(ivf_ranks)) if ivf_ranks else np.nan,
            }
        )
    return pd.DataFrame(rows)


def figure4_competence(df: pd.DataFrame) -> pd.DataFrame:
    igd = _competence_summary(df, metric="IGD", higher_is_better=False)
    hv = _competence_summary(df, metric="HV", higher_is_better=True)
    summary = pd.concat([igd, hv], ignore_index=True)
    summary.to_csv(os.path.join(OUT_TABLE, "fig4_competence_summary.csv"), index=False)

    _setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 6.7))

    def _plot_wtl(ax, sub: pd.DataFrame, title: str) -> None:
        x = np.arange(len(SUITES))
        sub = sub.set_index("suite").reindex(SUITES).reset_index()
        wins = sub["wins"].to_numpy(dtype=float)
        ties = sub["ties"].to_numpy(dtype=float)
        losses = sub["losses"].to_numpy(dtype=float)
        total = sub["n_instances"].to_numpy(dtype=float)

        ax.bar(x, wins, color="#2166AC", label="Wins")
        ax.bar(x, ties, bottom=wins, color="#BDBDBD", label="Ties")
        ax.bar(x, losses, bottom=wins + ties, color="#B2182B", label="Losses")
        ax.set_xticks(x)
        ax.set_xticklabels(SUITES)
        ax.set_ylabel("# instances")
        ax.set_title(title)
        ax.grid(True, axis="y", linestyle="--", alpha=0.22)
        for i, (w, t) in enumerate(zip(wins, total)):
            ax.text(i, t + 0.1, f"{int(w)}/{int(t)}", ha="center", fontsize=7)

    def _plot_rank(ax, sub: pd.DataFrame, title: str) -> None:
        x = np.arange(len(SUITES))
        sub = sub.set_index("suite").reindex(SUITES).reset_index()
        vals = sub["avg_rank_ivf"].to_numpy(dtype=float)
        bars = ax.bar(x, vals, color="#2166AC", alpha=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels(SUITES)
        ax.set_ylabel("Avg rank (1=best)")
        ax.set_ylim(0.8, len(ALGORITHMS) + 0.2)
        ax.invert_yaxis()
        ax.axhline(3.0, color="#555555", linestyle=":", linewidth=0.9)
        ax.set_title(title)
        ax.grid(True, axis="y", linestyle="--", alpha=0.22)
        for b, v in zip(bars, vals):
            ax.text(
                b.get_x() + b.get_width() / 2,
                v - 0.12,
                f"{v:.2f}",
                ha="center",
                va="top",
                fontsize=7,
            )

    _plot_wtl(axes[0, 0], igd, "(a) Win/Tie/Loss IVF vs SPEA2 (IGD)")
    _plot_rank(axes[0, 1], igd, "(b) IVF average rank vs all (IGD)")
    _plot_wtl(axes[1, 0], hv, "(c) Win/Tie/Loss IVF vs SPEA2 (HV)")
    _plot_rank(axes[1, 1], hv, "(d) IVF average rank vs all (HV)")

    handles = [
        Line2D([0], [0], color="#2166AC", lw=6, label="Wins"),
        Line2D([0], [0], color="#BDBDBD", lw=6, label="Ties"),
        Line2D([0], [0], color="#B2182B", lw=6, label="Losses"),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=3,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle("Fig.4 - Competence summary by benchmark suite", y=1.01)
    plt.tight_layout(rect=[0, 0.07, 1, 0.97], w_pad=1.3, h_pad=1.1)

    pdf = os.path.join(OUT_FIG, "fig4_competence_summary_igd_hv.pdf")
    png = os.path.join(OUT_FIG, "fig4_competence_summary_igd_hv.png")
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    print(f"Saved: {pdf}")
    print(f"Saved: {png}")
    return summary


def _all_instances_order(df: pd.DataFrame) -> List[Tuple[str, str, str]]:
    rows = df[["Grupo", "Problema", "M", "instance"]].drop_duplicates().copy()
    rows["suite_idx"] = (
        rows["Grupo"].map({s: i for i, s in enumerate(SUITES)}).fillna(99)
    )
    rows["m_order"] = rows["M"].map({"M2": 2, "M3": 3}).fillna(99)
    rows["p_num"] = rows["Problema"].map(_problem_number)
    rows = rows.sort_values(["suite_idx", "m_order", "p_num", "Problema"])
    return [(r.Grupo, r.Problema, r.M) for r in rows.itertuples(index=False)]


def figure5_heatmap(df: pd.DataFrame) -> None:
    baselines = [a for a in ALGORITHMS if a != "IVFSPEA2"]
    instances = _all_instances_order(df)

    heat_records = []
    mats: Dict[str, np.ndarray] = {}
    sigs: Dict[str, np.ndarray] = {}

    for metric, higher in [("IGD", False), ("HV", True)]:
        mat = np.full((len(instances), len(baselines)), np.nan, dtype=float)
        sig = np.zeros((len(instances), len(baselines)), dtype=bool)

        for i, (suite, prob, m) in enumerate(instances):
            blk = df[(df["Grupo"] == suite) & (df["Problema"] == prob) & (df["M"] == m)]
            ivf = blk[blk["Algoritmo"] == "IVFSPEA2"][metric].dropna().to_numpy()
            for j, base in enumerate(baselines):
                b = blk[blk["Algoritmo"] == base][metric].dropna().to_numpy()
                if len(ivf) >= 5 and len(b) >= 5:
                    val = _a12(ivf, b, higher_is_better=higher)
                    _, pval = mannwhitneyu(ivf, b, alternative="two-sided")
                    mat[i, j] = val
                    sig[i, j] = pval < 0.05
                    heat_records.append(
                        {
                            "metric": metric,
                            "suite": suite,
                            "problem": prob,
                            "M": m,
                            "baseline": base,
                            "A12": val,
                            "significant": bool(pval < 0.05),
                            "p_value": float(pval),
                        }
                    )
        mats[metric] = mat
        sigs[metric] = sig

    pd.DataFrame(heat_records).to_csv(
        os.path.join(OUT_TABLE, "fig5_a12_heatmap_values.csv"), index=False
    )

    _setup_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 13.5), sharey=True)
    norm = mcolors.TwoSlopeNorm(vmin=0.0, vcenter=0.5, vmax=1.0)
    cmap = plt.get_cmap("RdBu")

    for ax, metric in zip(axes, ["IGD", "HV"]):
        mat = mats[metric]
        sig = sigs[metric]
        im = ax.imshow(mat, cmap=cmap, norm=norm, aspect="auto")

        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                if np.isnan(mat[i, j]):
                    continue
                if not sig[i, j]:
                    ax.plot(
                        j,
                        i,
                        marker="x",
                        color="black",
                        markersize=2,
                        markeredgewidth=0.5,
                    )

        ax.set_xticks(np.arange(len(baselines)))
        ax.set_xticklabels(
            [ALGO_DISPLAY[b] for b in baselines], rotation=45, ha="right"
        )
        ylabels = [f"{p} ({m})" for _, p, m in instances]
        ax.set_yticks(np.arange(len(instances)))
        ax.set_yticklabels(ylabels, fontsize=5.5)
        ax.set_title(f"{metric}: A12(IVF better)\n'x' = non-significant")

        prev = instances[0][0]
        for idx, (suite, _, _) in enumerate(instances):
            if idx > 0 and suite != prev:
                ax.axhline(idx - 0.5, color="black", linewidth=0.9)
            prev = suite

    fig.subplots_adjust(right=0.89, wspace=0.08)
    cax = fig.add_axes([0.905, 0.14, 0.03, 0.72])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("A12 effect size")
    fig.suptitle("Fig.5 - Effect-size heatmaps across ZDT/DTLZ/WFG/MaF", y=1.01)

    pdf = os.path.join(OUT_FIG, "fig5_effectsize_heatmap_igd_hv.pdf")
    png = os.path.join(OUT_FIG, "fig5_effectsize_heatmap_igd_hv.png")
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    print(f"Saved: {pdf}")
    print(f"Saved: {png}")


def main() -> None:
    os.makedirs(OUT_FIG, exist_ok=True)
    os.makedirs(OUT_TABLE, exist_ok=True)

    df = load_data()
    print(
        f"Loaded {len(df)} rows | suites={sorted(df['Grupo'].unique())} | "
        f"algorithms={df['Algoritmo'].nunique()}"
    )

    figure1_profiles(df)
    figure2_boxplots(df)
    figure3_pareto_panels(df)
    figure4_competence(df)
    figure5_heatmap(df)

    print("Done.")


if __name__ == "__main__":
    main()
