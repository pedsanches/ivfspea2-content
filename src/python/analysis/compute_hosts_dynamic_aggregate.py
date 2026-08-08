#!/usr/bin/env python3
"""Aggregate all-suite dynamic traces for the hosts paper.

Reads `data/processed/hosts_convergence.csv` and `config/hosts_front_geometry.csv`,
builds normalized time-to-target style gap curves for IGD and HV over the full 51-instance
 synthetic suite, and writes:

* `results/tables/hosts_dynamic_aggregate_curves.csv`
* `results/tables/hosts_dynamic_aggregate_summary.csv`
* `results/tables/hosts_dynamic_aggregate_tau10.tex`
* `results/figures/hosts_v2_fig5_dynamic_aggregate.pdf`

The figure is also copied into `paper/ppsn2026-ivf-hosts/figures/` for later manuscript use.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CONV_CSV = PROJECT_ROOT / "data" / "processed" / "hosts_convergence.csv"
GEO_CSV = PROJECT_ROOT / "config" / "hosts_front_geometry.csv"
OUT_TABLES = PROJECT_ROOT / "results" / "tables"
OUT_FIGS = PROJECT_ROOT / "results" / "figures"
PAPER_FIGS = PROJECT_ROOT / "paper" / "ppsn2026-ivf-hosts" / "figures"

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2", "IVF/SPEA2", "#0072B2"),
    ("IVFNSGAIII", "NSGAIII", "IVF/NSGA-III", "#009E73"),
    ("IVFNSGAII", "NSGAII", "IVF/NSGA-II", "#D55E00"),
]
METRICS = ["IGD", "HV"]
TAUS = [0.5, 0.25, 0.1]
FE_GRID = np.linspace(0.1, 1.0, 100)
N_BOOTSTRAP = 1000
RNG_SEED = 42


def save_fig(fig: plt.Figure, name: str) -> None:
    for out_dir in (OUT_FIGS, PAPER_FIGS):
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / name
        fig.savefig(path, bbox_inches="tight", dpi=300)
        print(f"[A7] Wrote figure: {path}")


def compute_scalers(df: pd.DataFrame) -> dict[tuple[str, str, str, int, str], tuple[float, float]]:
    scalers: dict[tuple[str, str, str, int, str], tuple[float, float]] = {}
    for ivf_algo, base_algo, _, _ in HOST_PAIRS:
        pair_name = f"{ivf_algo}_vs_{base_algo}"
        pair_df = df[df["algo"].isin([ivf_algo, base_algo])]
        for (problem, m_val), sub in pair_df.groupby(["problem", "M"], sort=True):
            for metric in METRICS:
                first_vals = sub.sort_values("FE").groupby(["algo", "run"])[metric].first().to_numpy(dtype=float)
                final_vals = sub.sort_values("FE").groupby(["algo", "run"])[metric].last().to_numpy(dtype=float)
                if metric == "IGD":
                    target = float(np.nanmin(final_vals))
                    start = float(np.nanmax(first_vals))
                    scale = max(start - target, 1e-12)
                else:
                    target = float(np.nanmax(final_vals))
                    start = float(np.nanmin(first_vals))
                    scale = max(target - start, 1e-12)
                scalers[(pair_name, problem, int(m_val), metric)] = (target, scale)
    return scalers


def build_trace_curves(df: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    geo_map = geo.set_index(["problem", "M"]).to_dict("index")
    scalers = compute_scalers(df)
    rows: list[dict] = []

    for ivf_algo, base_algo, _, _ in HOST_PAIRS:
        pair_name = f"{ivf_algo}_vs_{base_algo}"
        pair_df = df[df["algo"].isin([ivf_algo, base_algo])]
        for (algo, problem, m_val, run), sub in pair_df.groupby(["algo", "problem", "M", "run"], sort=True):
            sub = sub.sort_values("FE")
            fe_norm = sub["FE"].to_numpy(dtype=float) / float(sub["FE"].max())
            geo_info = geo_map[(problem, int(m_val))]
            for metric in METRICS:
                target, scale = scalers[(pair_name, problem, int(m_val), metric)]
                values = sub[metric].to_numpy(dtype=float)
                if metric == "IGD":
                    progress = np.minimum.accumulate(values)
                    gap = np.clip((progress - target) / scale, 0.0, None)
                else:
                    progress = np.maximum.accumulate(values)
                    gap = np.clip((target - progress) / scale, 0.0, None)
                gap_interp = np.interp(FE_GRID, fe_norm, gap)
                for fe_val, gap_val in zip(FE_GRID, gap_interp, strict=True):
                    rows.append(
                        {
                            "comparison": pair_name,
                            "algo": algo,
                            "problem": problem,
                            "M": int(m_val),
                            "run": int(run),
                            "metric": metric,
                            "fe_norm": float(fe_val),
                            "gap": float(gap_val),
                            "geometry_primary": geo_info["geometry_primary"],
                            "geometry_group": geo_info["geometry_group"],
                        }
                    )
    return pd.DataFrame(rows)


def bootstrap_fraction(matrix: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    main = matrix.mean(axis=0)
    boots = np.empty((N_BOOTSTRAP, matrix.shape[1]), dtype=float)
    for i in range(N_BOOTSTRAP):
        idx = rng.choice(matrix.shape[0], size=matrix.shape[0], replace=True)
        boots[i] = matrix[idx].mean(axis=0)
    return main, np.percentile(boots, 2.5, axis=0), np.percentile(boots, 97.5, axis=0)


def build_curve_outputs(traces: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RNG_SEED)
    curve_rows: list[dict] = []
    summary_rows: list[dict] = []

    for pair_name, pair_sub in traces.groupby("comparison", sort=True):
        ivf_algo, _, _, _ = next(item for item in HOST_PAIRS if f"{item[0]}_vs_{item[1]}" == pair_name)
        base_algo = next(item[1] for item in HOST_PAIRS if f"{item[0]}_vs_{item[1]}" == pair_name)

        for metric in METRICS:
            metric_sub = pair_sub[pair_sub["metric"] == metric]
            for tau in TAUS:
                for algo in [ivf_algo, base_algo]:
                    algo_sub = metric_sub[metric_sub["algo"] == algo]
                    pivot = (
                        algo_sub.pivot_table(
                            index=["problem", "M", "run"],
                            columns="fe_norm",
                            values="gap",
                        )
                        .sort_index(axis=1)
                        .sort_index()
                    )
                    solved = (pivot.to_numpy(dtype=float) <= tau).astype(float)
                    frac, ci_low, ci_high = bootstrap_fraction(solved, rng)
                    for fe_val, frac_val, lo, hi in zip(pivot.columns.to_numpy(dtype=float), frac, ci_low, ci_high, strict=True):
                        curve_rows.append(
                            {
                                "comparison": pair_name,
                                "metric": metric,
                                "tau": tau,
                                "algo": algo,
                                "fe_norm": float(fe_val),
                                "fraction_solved": float(frac_val),
                                "ci_low": float(lo),
                                "ci_high": float(hi),
                                "n_traces": int(solved.shape[0]),
                            }
                        )

                # Summary by M and geometry_group
                for (m_val, geometry_group), stratum in metric_sub.groupby(["M", "geometry_group"], sort=True):
                    pivots = {}
                    for algo in [ivf_algo, base_algo]:
                        algo_sub = stratum[stratum["algo"] == algo]
                        pivot = (
                            algo_sub.pivot_table(
                                index=["problem", "M", "run"],
                                columns="fe_norm",
                                values="gap",
                            )
                            .sort_index(axis=1)
                            .sort_index()
                        )
                        solved = (pivot.to_numpy(dtype=float) <= tau).astype(float)
                        frac = solved.mean(axis=0)
                        pivots[algo] = {
                            "frac": frac,
                            "n_traces": int(solved.shape[0]),
                        }

                    auc_ivf = float(np.trapezoid(pivots[ivf_algo]["frac"], pivot.columns.to_numpy(dtype=float)))
                    auc_base = float(np.trapezoid(pivots[base_algo]["frac"], pivot.columns.to_numpy(dtype=float)))
                    summary_rows.append(
                        {
                            "comparison": pair_name,
                            "ivf_algo": ivf_algo,
                            "base_algo": base_algo,
                            "metric": metric,
                            "tau": tau,
                            "M": int(m_val),
                            "geometry_group": geometry_group,
                            "n_traces_ivf": pivots[ivf_algo]["n_traces"],
                            "n_traces_base": pivots[base_algo]["n_traces"],
                            "auc_ivf": auc_ivf,
                            "auc_base": auc_base,
                            "delta_auc": auc_ivf - auc_base,
                            "final_frac_ivf": float(pivots[ivf_algo]["frac"][-1]),
                            "final_frac_base": float(pivots[base_algo]["frac"][-1]),
                        }
                    )

    return pd.DataFrame(curve_rows), pd.DataFrame(summary_rows)


def plot_main_figure(curves: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
    label_map = {item[0]: item[2] for item in HOST_PAIRS}
    color_map = {item[0]: item[3] for item in HOST_PAIRS}

    for ax, (ivf_algo, base_algo, display, color) in zip(axes, HOST_PAIRS, strict=True):
        pair_name = f"{ivf_algo}_vs_{base_algo}"
        for algo, ls, lw, label in [
            (ivf_algo, "-", 2.4, display),
            (base_algo, "--", 1.8, base_algo.replace("NSGA", "NSGA-") if base_algo != "SPEA2" else "SPEA2"),
        ]:
            sub = curves[
                (curves["comparison"] == pair_name)
                & (curves["metric"] == "IGD")
                & (curves["tau"] == 0.1)
                & (curves["algo"] == algo)
            ].sort_values("fe_norm")
            ax.plot(sub["fe_norm"], sub["fraction_solved"], color=color, linestyle=ls, linewidth=lw, label=label)
            ax.fill_between(sub["fe_norm"], sub["ci_low"], sub["ci_high"], color=color, alpha=0.12)

        ax.set_title(display, fontsize=12, fontweight="bold")
        ax.set_xlabel("FE / max FE", fontsize=11)
        ax.set_xlim(0.1, 1.0)
        ax.set_ylim(0.0, 1.02)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=10)

    axes[0].set_ylabel("Fraction of runs with IGD gap $\\leq 0.1$", fontsize=10)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=11, bbox_to_anchor=(0.5, -0.06), frameon=True, edgecolor="0.8")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save_fig(fig, "hosts_v2_fig5_dynamic_aggregate.pdf")
    plt.close(fig)


def write_tau10_tex(summary: pd.DataFrame, out_path: Path) -> None:
    sub = summary[(summary["tau"] == 0.1)].copy()
    host_order = ["IVFSPEA2", "IVFNSGAIII", "IVFNSGAII"]
    host_display = {item[0]: item[2] for item in HOST_PAIRS}
    newline = r"\\"

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Dynamic all-suite summary at normalized gap threshold $\\tau=0.1$. Positive $\\Delta$AUC favors IVF. Values are stratified by host, objective count, and geometry group.}",
        "\\label{tab:hosts_dynamic_tau10}",
        "\\scriptsize",
        "\\begin{tabular}{llcrr}",
        "\\toprule",
        f"Host & Metric & $M$ & Geometry & $\\Delta$AUC {newline}",
        "\\midrule",
    ]
    for host in host_order:
        first = True
        host_sub = sub[sub["ivf_algo"] == host]
        for metric in METRICS:
            for m_val in [2, 3]:
                for geometry in ["regular", "irregular"]:
                    row = host_sub[(host_sub["metric"] == metric) & (host_sub["M"] == m_val) & (host_sub["geometry_group"] == geometry)]
                    if row.empty:
                        continue
                    r = row.iloc[0]
                    host_cell = host_display[host] if first else ""
                    lines.append(f"{host_cell} & {metric} & {m_val} & {geometry} & {r['delta_auc']:.3f} {newline}")
                    first = False
        lines.append("\\addlinespace")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print(f"[A7] Reading traces: {CONV_CSV}")
    conv = pd.read_csv(CONV_CSV)
    print(f"[A7] Loaded {len(conv)} rows across {conv['algo'].nunique()} algorithms and {conv[['problem','M']].drop_duplicates().shape[0]} instances")
    print(f"[A7] Reading geometry labels: {GEO_CSV}")
    geo = pd.read_csv(GEO_CSV)
    print(f"[A7] Loaded {len(geo)} geometry labels")

    traces = build_trace_curves(conv, geo)
    print(f"[A7] Built {len(traces)} normalized trace rows")
    curves, summary = build_curve_outputs(traces)

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    out_curves = OUT_TABLES / "hosts_dynamic_aggregate_curves.csv"
    out_summary = OUT_TABLES / "hosts_dynamic_aggregate_summary.csv"
    out_tex = OUT_TABLES / "hosts_dynamic_aggregate_tau10.tex"
    traces_out = OUT_TABLES / "hosts_dynamic_normalized_traces.csv"

    traces.to_csv(traces_out, index=False)
    curves.to_csv(out_curves, index=False)
    summary.to_csv(out_summary, index=False)
    write_tau10_tex(summary, out_tex)
    print(f"[A7] Wrote {traces_out} ({len(traces)} rows)")
    print(f"[A7] Wrote {out_curves} ({len(curves)} rows)")
    print(f"[A7] Wrote {out_summary} ({len(summary)} rows)")
    print(f"[A7] Wrote {out_tex}")

    plot_main_figure(curves)


if __name__ == "__main__":
    main()
