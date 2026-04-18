#!/usr/bin/env python3
"""Geometry-stratified analysis of IVF host compatibility.

Joins geometry labels from ``config/hosts_front_geometry.csv`` with the per-host
endpoint stats CSVs, then computes:

* W/T/L and median A12_ivf by host × metric × geometry stratum
* Permutation test for the host × geometry interaction on A12_ivf

Outputs:
    results/tables/hosts_geometry_summary.csv
    results/tables/hosts_geometry_summary.tex
    results/tables/hosts_geometry_interaction.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
GEO_PATH = PROJECT_ROOT / "config" / "hosts_front_geometry.csv"
STATS_DIR = PROJECT_ROOT / "results" / "tables"
OUT_DIR = STATS_DIR

HOSTS = [
    ("IVFSPEA2", "IVF/SPEA2"),
    ("IVFNSGAII", "IVF/NSGA-II"),
    ("IVFNSGAIII", "IVF/NSGA-III"),
]
METRICS = ["IGD", "HV"]
N_PERM = 10_000
RNG_SEED = 42


def ivf_favoring_a12(raw_a12: float, metric: str) -> float:
    """Orient A12 so that values > 0.5 always favor IVF."""
    return 1.0 - raw_a12 if metric == "IGD" else raw_a12


def load_stats() -> pd.DataFrame:
    """Load and stack the six per-host stats CSVs with geometry labels."""
    geo = pd.read_csv(GEO_PATH)
    frames = []
    for algo_key, algo_label in HOSTS:
        for metric in METRICS:
            path = STATS_DIR / f"hosts_{algo_key.lower()}_{metric.lower()}_stats.csv"
            df = pd.read_csv(path)
            df["host"] = algo_key
            df["host_label"] = algo_label
            df["metric"] = metric
            df["a12_ivf"] = df["A12"].apply(
                lambda v, m=metric: ivf_favoring_a12(v, m)
            )
            frames.append(df)
    stacked = pd.concat(frames, ignore_index=True)
    stacked = stacked.merge(
        geo[["problem", "M", "geometry_primary", "geometry_group"]],
        on=["problem", "M"],
        how="left",
    )
    return stacked


def wtl_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """W/T/L counts and median A12_ivf by host × metric × geometry stratum."""
    rows: list[dict] = []
    for (host, host_label, metric, geo_val), sub in df.groupby(
        ["host", "host_label", "metric", group_col]
    ):
        counts = sub["sign"].value_counts().to_dict()
        rows.append(
            {
                "host": host,
                "host_label": host_label,
                "metric": metric,
                "geometry": geo_val,
                "geometry_level": group_col,
                "n_instances": len(sub),
                "wins": counts.get("+", 0),
                "ties": counts.get("=", 0),
                "losses": counts.get("-", 0),
                "median_a12_ivf": float(np.nanmedian(sub["a12_ivf"].to_numpy())),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["geometry_level", "metric", "geometry", "host"]
    )


def _interaction_f(
    a12_vals: np.ndarray,
    host_idx: np.ndarray,
    geo_idx: np.ndarray,
    n_hosts: int,
    n_geos: int,
) -> float:
    """Compute the interaction SS / residual MS for a two-way layout.

    Uses a Type-I-like decomposition: grand mean, host main effect, geometry
    main effect, then interaction.  M is not included as a factor here because
    the permutation shuffles geometry labels across instances (which already
    carry their M value).
    """
    grand = a12_vals.mean()
    n = len(a12_vals)

    # Cell means
    cell_sum = np.zeros((n_hosts, n_geos))
    cell_n = np.zeros((n_hosts, n_geos))
    for i in range(n):
        cell_sum[host_idx[i], geo_idx[i]] += a12_vals[i]
        cell_n[host_idx[i], geo_idx[i]] += 1
    with np.errstate(divide="ignore", invalid="ignore"):
        cell_mean = np.where(cell_n > 0, cell_sum / cell_n, 0.0)

    # Main-effect means
    host_mean = np.zeros(n_hosts)
    for h in range(n_hosts):
        mask = host_idx == h
        if mask.any():
            host_mean[h] = a12_vals[mask].mean()

    geo_mean = np.zeros(n_geos)
    for g in range(n_geos):
        mask = geo_idx == g
        if mask.any():
            geo_mean[g] = a12_vals[mask].mean()

    # Interaction SS
    ss_inter = 0.0
    for h in range(n_hosts):
        for g in range(n_geos):
            if cell_n[h, g] > 0:
                diff = cell_mean[h, g] - host_mean[h] - geo_mean[g] + grand
                ss_inter += cell_n[h, g] * diff**2

    # Residual SS
    ss_resid = 0.0
    for i in range(n):
        ss_resid += (a12_vals[i] - cell_mean[host_idx[i], geo_idx[i]]) ** 2

    df_inter = (n_hosts - 1) * (n_geos - 1)
    df_resid = n - n_hosts * n_geos
    if df_inter == 0 or df_resid <= 0 or ss_resid == 0:
        return 0.0
    return (ss_inter / df_inter) / (ss_resid / df_resid)


def permutation_interaction_test(
    df: pd.DataFrame, metric: str, geo_col: str
) -> dict:
    """Permutation test for host × geometry interaction on A12_ivf.

    Permutation unit: the instance (problem, M).  All three host observations
    for the same instance receive the same permuted geometry label, preserving
    the within-instance correlation structure.
    """
    sub = df[df["metric"] == metric].copy()
    instances = sub[["problem", "M", geo_col]].drop_duplicates()
    inst_keys = list(zip(instances["problem"], instances["M"]))
    inst_geo = dict(zip(inst_keys, instances[geo_col]))

    geo_labels = sorted(sub[geo_col].unique())
    geo_map = {g: i for i, g in enumerate(geo_labels)}
    host_labels = sorted(sub["host"].unique())
    host_map = {h: i for i, h in enumerate(host_labels)}

    a12_vals = sub["a12_ivf"].to_numpy(dtype=float)
    host_idx = sub["host"].map(host_map).to_numpy(dtype=int)
    geo_idx = sub[geo_col].map(geo_map).to_numpy(dtype=int)

    observed_f = _interaction_f(
        a12_vals, host_idx, geo_idx, len(host_labels), len(geo_labels)
    )

    # Build instance-to-row mapping for efficient permutation
    inst_col = list(zip(sub["problem"], sub["M"]))
    inst_to_rows: dict[tuple, list[int]] = {}
    for i, key in enumerate(inst_col):
        inst_to_rows.setdefault(key, []).append(i)

    inst_geos = np.array([inst_geo[k] for k in inst_keys])
    rng = np.random.default_rng(RNG_SEED)

    n_geq = 0
    perm_geo_idx = geo_idx.copy()
    for _ in range(N_PERM):
        perm_geos = rng.permutation(inst_geos)
        for j, key in enumerate(inst_keys):
            new_g = geo_map[perm_geos[j]]
            for row_i in inst_to_rows[key]:
                perm_geo_idx[row_i] = new_g

        perm_f = _interaction_f(
            a12_vals, host_idx, perm_geo_idx, len(host_labels), len(geo_labels)
        )
        if perm_f >= observed_f:
            n_geq += 1

    p_value = (n_geq + 1) / (N_PERM + 1)

    return {
        "metric": metric,
        "geometry_level": geo_col,
        "n_obs": len(sub),
        "n_instances": len(inst_keys),
        "n_hosts": len(host_labels),
        "n_geo_levels": len(geo_labels),
        "observed_F": observed_f,
        "n_permutations": N_PERM,
        "p_value": p_value,
    }


def write_summary_tex(summary: pd.DataFrame, out_path: Path) -> None:
    """Write a compact LaTeX table of W/T/L by host × geometry_group × metric."""
    sub = summary[summary["geometry_level"] == "geometry_group"].copy()
    newline = r"\\"

    host_order = ["IVFSPEA2", "IVFNSGAIII", "IVFNSGAII"]
    host_display = {
        "IVFSPEA2": "IVF/SPEA2",
        "IVFNSGAIII": "IVF/NSGA-III",
        "IVFNSGAII": "IVF/NSGA-II",
    }

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Geometry-stratified win/tie/loss summary and median "
        "$A_{12}^{\\mathrm{IVF}}$. Instances are split into \\emph{regular} "
        "(convex, concave, linear; $n=40$) and \\emph{irregular} (disconnected, "
        "degenerate; $n=11$) Pareto-front geometries.}",
        "\\label{tab:hosts_geometry_summary}",
        "\\scriptsize",
        "\\begin{tabular}{llcrrrc}",
        "\\toprule",
        f"Host & Metric & Geometry & W & T & L & Med.~$A_{{12}}^{{\\mathrm{{IVF}}}}$ {newline}",
        "\\midrule",
    ]

    for host in host_order:
        first = True
        for metric in METRICS:
            for geo in ["regular", "irregular"]:
                row = sub[
                    (sub["host"] == host)
                    & (sub["metric"] == metric)
                    & (sub["geometry"] == geo)
                ]
                if row.empty:
                    continue
                r = row.iloc[0]
                host_str = host_display[host] if first else ""
                lines.append(
                    f"{host_str} & {metric} & {geo} & "
                    f"{int(r['wins'])} & {int(r['ties'])} & {int(r['losses'])} & "
                    f"{r['median_a12_ivf']:.3f} {newline}"
                )
                first = False
        lines.append("\\addlinespace")

    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print("[A5] Loading stats and geometry labels...")
    stacked = load_stats()
    print(
        f"[A5] Stacked {len(stacked)} rows "
        f"({stacked['host'].nunique()} hosts × {stacked['metric'].nunique()} metrics × "
        f"{stacked[['problem','M']].drop_duplicates().shape[0]} instances)"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- W/T/L summaries ---
    frames = []
    for geo_col in ("geometry_primary", "geometry_group"):
        frames.append(wtl_summary(stacked, geo_col))
    summary = pd.concat(frames, ignore_index=True)

    out_csv = OUT_DIR / "hosts_geometry_summary.csv"
    summary.to_csv(out_csv, index=False)
    print(f"[A5] Wrote {out_csv} ({len(summary)} rows)")

    out_tex = OUT_DIR / "hosts_geometry_summary.tex"
    write_summary_tex(summary, out_tex)
    print(f"[A5] Wrote {out_tex}")

    # --- Permutation interaction tests ---
    interaction_rows = []
    for metric in METRICS:
        for geo_col in ("geometry_primary", "geometry_group"):
            print(
                f"[A5] Permutation test: {metric} × {geo_col} "
                f"({N_PERM} permutations)..."
            )
            result = permutation_interaction_test(stacked, metric, geo_col)
            interaction_rows.append(result)
            print(
                f"       F={result['observed_F']:.4f}, "
                f"p={result['p_value']:.4f}"
            )

    interaction_df = pd.DataFrame(interaction_rows)
    out_inter = OUT_DIR / "hosts_geometry_interaction.csv"
    interaction_df.to_csv(out_inter, index=False)
    print(f"[A5] Wrote {out_inter}")

    # --- Console summary ---
    print("\n=== Geometry-stratified W/T/L (geometry_group) ===")
    group_summary = summary[summary["geometry_level"] == "geometry_group"]
    for host, _ in HOSTS:
        for metric in METRICS:
            for geo in ("regular", "irregular"):
                row = group_summary[
                    (group_summary["host"] == host)
                    & (group_summary["metric"] == metric)
                    & (group_summary["geometry"] == geo)
                ]
                if row.empty:
                    continue
                r = row.iloc[0]
                print(
                    f"  {r['host_label']:14s} {metric:3s} {geo:9s}: "
                    f"+{int(r['wins'])}/={int(r['ties'])}/-{int(r['losses'])}  "
                    f"med A12_ivf={r['median_a12_ivf']:.3f}"
                )

    print("\n=== Interaction tests ===")
    for _, row in interaction_df.iterrows():
        print(
            f"  {row['metric']:3s} × {row['geometry_level']:17s}: "
            f"F={row['observed_F']:.4f}, p={row['p_value']:.4f}"
        )


if __name__ == "__main__":
    main()
