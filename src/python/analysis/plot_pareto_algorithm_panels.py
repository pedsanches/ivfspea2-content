#!/usr/bin/env python3
"""Generate per-algorithm Pareto panel figures.

This script creates "one subplot per algorithm" comparisons, following the
visual style commonly used in structural optimization papers where each panel
shows:

1) the same reference front/set; and
2) the final non-dominated solutions of one algorithm.

The goal is to make convergence and spread differences directly comparable
across methods under identical axis limits.

Input files are expected in ``data/processed/fronts`` and are typically created
by ``experiments/extract_fronts_for_paper.m``.

Examples
--------
Generate the two recommended default figures:

    python src/python/analysis/plot_pareto_algorithm_panels.py

Generate a single custom panel figure:

    python src/python/analysis/plot_pareto_algorithm_panels.py \
        --problem DTLZ2 --m M2 --algorithms IVFSPEA2,SPEA2,NSGAIII,MOEAD

Use a specific 2D projection from a 3-objective case:

    python src/python/analysis/plot_pareto_algorithm_panels.py \
        --problem RWMOP8 --m M3 --algorithms IVFSPEA2,SPEA2,NSGAIII,ARMOEA \
        --projection f1,f2 --reference union_nd
"""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass
from string import ascii_lowercase

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
FRONTS_DIR = os.path.join(ROOT, "data", "processed", "fronts")
OUT_DIR = os.path.join(ROOT, "paper", "figures")

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


@dataclass(frozen=True)
class CaseConfig:
    problem: str
    m: str
    algorithms: tuple[str, ...]
    projection: tuple[str, str] = ("f1", "f2")
    reference_mode: str = "auto"  # auto | true_pf | union_nd


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "legend.fontsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )


def _front_path(problem: str, m: str, algorithm: str) -> str:
    return os.path.join(FRONTS_DIR, f"{problem}_{m}_{algorithm}_median.csv")


def _true_pf_path(problem: str, m: str) -> str:
    return os.path.join(FRONTS_DIR, f"{problem}_{m}_truePF.csv")


def _objective_columns(df: pd.DataFrame) -> list[str]:
    cols = [c for c in df.columns if c.lower().startswith("f")]
    if not cols:
        raise ValueError("No objective columns found. Expected columns like f1,f2,...")
    return cols


def _compute_nondominated(points: np.ndarray) -> np.ndarray:
    """Return non-dominated points for minimization objectives.

    Uses a pairwise dominance matrix. For the front sizes used here (typically
    <= a few thousand points), this approach is robust and sufficiently fast.
    """
    if points.size == 0:
        return points

    less_equal = points[:, None, :] <= points[None, :, :]
    strictly_less = points[:, None, :] < points[None, :, :]
    dominates = np.all(less_equal, axis=2) & np.any(strictly_less, axis=2)
    dominated = dominates.any(axis=0)
    nd = points[~dominated]

    # Remove exact duplicates for cleaner plotting.
    return np.unique(nd, axis=0)


def _load_case_fronts(case: CaseConfig) -> tuple[dict[str, pd.DataFrame], list[str]]:
    fronts: dict[str, pd.DataFrame] = {}
    objective_cols: list[str] | None = None

    for algo in case.algorithms:
        path = _front_path(case.problem, case.m, algo)
        if not os.path.isfile(path):
            print(f"  [WARN] Missing front file for {algo}: {path}")
            continue

        df = pd.read_csv(path)
        cols = _objective_columns(df)
        if objective_cols is None:
            objective_cols = cols
        fronts[algo] = df

    if not fronts:
        raise FileNotFoundError(
            f"No algorithm front CSVs found for {case.problem} {case.m}."
        )
    if objective_cols is None:
        raise RuntimeError("Unable to infer objective columns.")

    return fronts, objective_cols


def _build_reference_set(
    case: CaseConfig, fronts: dict[str, pd.DataFrame], objective_cols: list[str]
) -> tuple[pd.DataFrame, str]:
    mode = case.reference_mode.lower()
    true_pf_file = _true_pf_path(case.problem, case.m)

    if mode in {"auto", "true_pf"} and os.path.isfile(true_pf_file):
        ref_df = pd.read_csv(true_pf_file)
        return ref_df, "True Pareto front"

    if mode == "true_pf":
        raise FileNotFoundError(
            f"Requested true_pf reference, but file not found: {true_pf_file}"
        )

    # Union of all loaded algorithm points, then non-dominated filtering.
    union = np.vstack([df[objective_cols].to_numpy() for df in fronts.values()])
    nd = _compute_nondominated(union)
    ref_df = pd.DataFrame(nd, columns=objective_cols)
    return ref_df, "Reference ND set (union of median fronts)"


def _validate_projection(
    projection: tuple[str, str], objective_cols: list[str]
) -> None:
    xcol, ycol = projection
    missing = [c for c in (xcol, ycol) if c not in objective_cols]
    if missing:
        raise ValueError(
            f"Projection columns not found: {missing}. "
            f"Available objective columns: {objective_cols}"
        )


def _axis_limits(
    reference: pd.DataFrame,
    fronts: dict[str, pd.DataFrame],
    projection: tuple[str, str],
) -> tuple[float, float, float, float]:
    xcol, ycol = projection
    xs = [reference[xcol].to_numpy()]
    ys = [reference[ycol].to_numpy()]
    for d in fronts.values():
        xs.append(d[xcol].to_numpy())
        ys.append(d[ycol].to_numpy())

    x = np.concatenate(xs)
    y = np.concatenate(ys)
    xmin, xmax = float(np.min(x)), float(np.max(x))
    ymin, ymax = float(np.min(y)), float(np.max(y))

    xpad = 0.03 * (xmax - xmin) if xmax > xmin else 1e-6
    ypad = 0.03 * (ymax - ymin) if ymax > ymin else 1e-6
    return xmin - xpad, xmax + xpad, ymin - ypad, ymax + ypad


def _plot_case(case: CaseConfig, outpath: str) -> None:
    fronts, objective_cols = _load_case_fronts(case)
    _validate_projection(case.projection, objective_cols)
    reference, reference_label = _build_reference_set(case, fronts, objective_cols)

    xcol, ycol = case.projection

    algorithms = [a for a in case.algorithms if a in fronts]
    n_algos = len(algorithms)
    ncols = 2 if n_algos <= 4 else 3
    nrows = int(math.ceil(n_algos / ncols))

    _setup_style()
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(4.0 * ncols, 3.1 * nrows),
        sharex=True,
        sharey=True,
        squeeze=False,
    )

    xlo, xhi, ylo, yhi = _axis_limits(reference, fronts, case.projection)

    ref_color = "#F39C12"
    algo_color = "#1F77B4"

    for idx, algo in enumerate(algorithms):
        ax = axes[idx // ncols, idx % ncols]
        data = fronts[algo]

        ax.scatter(
            reference[xcol],
            reference[ycol],
            s=10,
            c=ref_color,
            alpha=0.75,
            edgecolors="none",
            label=reference_label,
            zorder=1,
        )
        ax.scatter(
            data[xcol],
            data[ycol],
            s=10,
            c=algo_color,
            alpha=0.8,
            edgecolors="none",
            label="Algorithm front",
            zorder=2,
        )

        panel = ascii_lowercase[idx]
        name = ALGO_DISPLAY.get(algo, algo)
        ax.set_title(f"({panel}) {name}")
        ax.set_xlim(xlo, xhi)
        ax.set_ylim(ylo, yhi)
        ax.grid(True, linestyle="--", alpha=0.2)
        ax.set_xlabel(f"${xcol}$")
        ax.set_ylabel(f"${ycol}$")

    # Hide unused axes.
    for idx in range(n_algos, nrows * ncols):
        axes[idx // ncols, idx % ncols].axis("off")

    # Single legend for all panels.
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels,
            ncol=2,
            loc="lower center",
            frameon=True,
            bbox_to_anchor=(0.5, -0.01),
        )

    fig.suptitle(
        (
            f"Per-algorithm Pareto-front comparison: {case.problem} ({case.m})\\n"
            f"Reference: {reference_label}"
        ),
        y=1.02,
        fontsize=10,
    )
    plt.tight_layout(rect=[0, 0.05, 1, 0.95], w_pad=1.0, h_pad=1.0)

    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    fig.savefig(outpath)
    plt.close(fig)

    print(f"  Saved: {outpath}")
    print(f"    Algorithms plotted: {', '.join(algorithms)}")
    print(f"    Reference points: {len(reference)}")


def _parse_projection(raw: str) -> tuple[str, str]:
    items = [x.strip() for x in raw.split(",") if x.strip()]
    if len(items) != 2:
        raise ValueError("Projection must contain exactly two columns, e.g. f1,f2")
    return items[0], items[1]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate per-algorithm Pareto comparison panel figures."
    )
    parser.add_argument("--problem", help="Problem name, e.g., DTLZ2 or RWMOP9")
    parser.add_argument("--m", default="M2", help="Objective-count tag, e.g., M2 or M3")
    parser.add_argument(
        "--algorithms",
        help=(
            "Comma-separated algorithm IDs matching front CSV names, e.g., "
            "IVFSPEA2,SPEA2,NSGAIII,MOEAD"
        ),
    )
    parser.add_argument(
        "--projection",
        default="f1,f2",
        help="Two objective columns to plot, e.g., f1,f2 or f1,f3",
    )
    parser.add_argument(
        "--reference",
        choices=["auto", "true_pf", "union_nd"],
        default="auto",
        help=(
            "Reference set mode: auto uses truePF if available, otherwise union ND; "
            "true_pf requires *_truePF.csv; union_nd computes ND of union fronts."
        ),
    )
    parser.add_argument(
        "--out",
        help="Output PDF path. If omitted, a default name is created in paper/figures/.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Default mode: generate two high-value figures for the manuscript.
    if not args.problem:
        print("Generating default algorithm-panel figures...")
        default_cases = [
            (
                CaseConfig(
                    problem="DTLZ2",
                    m="M2",
                    algorithms=("IVFSPEA2", "SPEA2", "NSGAIII", "MOEAD"),
                    projection=("f1", "f2"),
                    reference_mode="auto",
                ),
                os.path.join(OUT_DIR, "front_panels_dtlz2_m2.pdf"),
            ),
            (
                CaseConfig(
                    problem="RWMOP9",
                    m="M2",
                    algorithms=("IVFSPEA2", "SPEA2", "NSGAIII", "ARMOEA"),
                    projection=("f1", "f2"),
                    reference_mode="union_nd",
                ),
                os.path.join(OUT_DIR, "front_panels_rwmop9_m2.pdf"),
            ),
        ]

        for case, outpath in default_cases:
            print(f"\n- {case.problem} {case.m}")
            _plot_case(case, outpath)
        return

    if not args.algorithms:
        raise ValueError(
            "For custom mode, provide --algorithms. "
            "Example: --algorithms IVFSPEA2,SPEA2,NSGAIII,MOEAD"
        )

    algorithms = tuple(a.strip() for a in args.algorithms.split(",") if a.strip())
    projection = _parse_projection(args.projection)
    outpath = args.out
    if not outpath:
        outpath = os.path.join(
            OUT_DIR, f"front_panels_{args.problem.lower()}_{args.m.lower()}.pdf"
        )

    case = CaseConfig(
        problem=args.problem,
        m=args.m,
        algorithms=algorithms,
        projection=projection,
        reference_mode=args.reference,
    )

    print(f"Generating custom algorithm-panel figure for {case.problem} {case.m}...")
    _plot_case(case, outpath)


if __name__ == "__main__":
    main()
