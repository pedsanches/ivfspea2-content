#!/usr/bin/env python3
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Line3D

from ivf_trace_common import PROJECT_ROOT, ensure_directory, objective_columns


INPUT_DIR = PROJECT_ROOT / "results" / "ivf_trace"
OUT_DIR = PROJECT_ROOT / "paper" / "figures"

COLORS = {
    "reference_pf": "#D0D0D0",
    "population_before": "#C7CBD1",
    "population_after": "#6D6D6D",
    "mother": "#2166AC",
    "father": "#F18F01",
    "beneficial": "#1A9850",
    "harmful": "#D73027",
    "neutral": "#A67C52",
}

# Roles to include in the main (paper) figure
MAIN_ROLES = ["positive", "bimodal_good"]
# Maximum number of mother-father connector lines to draw per panel
MAX_CONNECTOR_LINES = 5
# Default viewing angle for 3D panels (elevation, azimuth)
VIEW_ELEV = 25
VIEW_AZIM = 135


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.titlesize": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 7,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
        }
    )


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    selected = pd.read_csv(INPUT_DIR / "representative_cycles.csv")
    populations = pd.read_csv(INPUT_DIR / "representative_cycle_populations.csv")
    pairs = pd.read_csv(INPUT_DIR / "representative_cycle_pairs.csv")
    children = pd.read_csv(INPUT_DIR / "trace_child_records.csv")
    return selected, populations, pairs, children


def validate_population_snapshots(
    selected: pd.DataFrame, populations: pd.DataFrame
) -> None:
    """Validate that each selected cycle has at least reference PF data."""
    for panel in selected.itertuples(index=False):
        sub = populations[populations["cycle_key"] == panel.cycle_key]
        if sub.empty:
            raise RuntimeError(
                f"No population data for {panel.case_id} run {panel.run_id} "
                f"gen {panel.generation} cycle {panel.ivf_cycle}."
            )


def objective_pairs(m: int) -> list[tuple[str, str]]:
    return list(combinations(objective_columns(m), 2))


# ---------------------------------------------------------------------------
# Axis-limit helpers
# ---------------------------------------------------------------------------


def _compute_axis_limits(
    panel_pop: pd.DataFrame,
    panel_pairs: pd.DataFrame,
    x: str,
    y: str,
    pct_lo: float = 1.0,
    pct_hi: float = 99.0,
    margin: float = 0.08,
) -> tuple[float, float, float, float]:
    """Compute axis limits based on data percentiles to avoid outlier-driven zoom."""
    all_x: list[np.ndarray] = []
    all_y: list[np.ndarray] = []

    # Include reference PF for axis context
    ref = panel_pop[panel_pop["point_group"] == "reference_pf"]
    if not ref.empty:
        all_x.append(ref[x].values)
        all_y.append(ref[y].values)

    for prefix in ("mother", "father", "child"):
        cx, cy = f"{prefix}_{x}", f"{prefix}_{y}"
        if cx in panel_pairs.columns and cy in panel_pairs.columns:
            vals = panel_pairs[[cx, cy]].dropna()
            if not vals.empty:
                all_x.append(vals[cx].values)
                all_y.append(vals[cy].values)

    if not all_x:
        return 0, 1, 0, 1

    xs = np.concatenate(all_x)
    ys = np.concatenate(all_y)
    x_lo, x_hi = float(np.percentile(xs, pct_lo)), float(np.percentile(xs, pct_hi))
    y_lo, y_hi = float(np.percentile(ys, pct_lo)), float(np.percentile(ys, pct_hi))

    dx = max(x_hi - x_lo, 1e-6) * margin
    dy = max(y_hi - y_lo, 1e-6) * margin
    return x_lo - dx, x_hi + dx, y_lo - dy, y_hi + dy


def _compute_axis_limits_3d(
    panel_pop: pd.DataFrame,
    panel_pairs: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    pct_lo: float = 1.0,
    pct_hi: float = 99.0,
    margin: float = 0.08,
) -> tuple[float, float, float, float, float, float]:
    """Compute 3-axis limits based on data percentiles."""
    all_vals: dict[str, list[np.ndarray]] = {x: [], y: [], z: []}

    # Include reference PF for axis context
    ref = panel_pop[panel_pop["point_group"] == "reference_pf"]
    if not ref.empty:
        for col in (x, y, z):
            all_vals[col].append(ref[col].values)

    for prefix in ("mother", "father", "child"):
        for col in (x, y, z):
            pc = f"{prefix}_{col}"
            if pc in panel_pairs.columns:
                vals = panel_pairs[pc].dropna().values
                if vals.size > 0:
                    all_vals[col].append(vals)

    limits: list[float] = []
    for col in (x, y, z):
        if not all_vals[col]:
            limits.extend([0.0, 1.0])
            continue
        arr = np.concatenate(all_vals[col])
        lo, hi = float(np.percentile(arr, pct_lo)), float(np.percentile(arr, pct_hi))
        d = max(hi - lo, 1e-6) * margin
        limits.extend([lo - d, hi + d])

    return tuple(limits)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# 2-D scatter helpers (unchanged logic)
# ---------------------------------------------------------------------------


def _scatter_group(
    ax: plt.Axes,
    frame: pd.DataFrame,
    point_group: str,
    x: str,
    y: str,
    color: str,
    size: float,
    alpha: float,
    edgecolor: str | None = None,
    linewidth: float = 0.0,
) -> None:
    group = frame[frame["point_group"] == point_group]
    if group.empty:
        return
    ax.scatter(
        group[x],
        group[y],
        s=size,
        c=color,
        alpha=alpha,
        edgecolors=edgecolor if edgecolor is not None else "none",
        linewidths=linewidth,
        zorder=0,
    )


def _scatter_parent_points(
    ax: plt.Axes,
    frame: pd.DataFrame,
    prefix: str,
    x: str,
    y: str,
    marker: str,
    color: str,
    size: float,
) -> None:
    cols = [f"{prefix}_{x}", f"{prefix}_{y}"]
    unique_points = frame[cols].drop_duplicates()
    if unique_points.empty:
        return
    ax.scatter(
        unique_points[f"{prefix}_{x}"],
        unique_points[f"{prefix}_{y}"],
        s=size,
        c=color,
        marker=marker,
        alpha=0.9,
        edgecolors="#111111",
        linewidths=0.25,
        zorder=3,
    )


def _scatter_child_points(
    ax: plt.Axes, frame: pd.DataFrame, x: str, y: str, color: str, size: float
) -> None:
    if frame.empty:
        return
    ax.scatter(
        frame[f"child_{x}"],
        frame[f"child_{y}"],
        s=size,
        c=color,
        alpha=0.85,
        edgecolors="none",
        zorder=4,
    )


def _draw_panel(
    ax: plt.Axes,
    panel_pop: pd.DataFrame,
    panel_pairs: pd.DataFrame,
    x: str,
    y: str,
    clip_axes: bool = True,
) -> None:
    """Draw a single 2-D scatter panel with all IVF trace elements."""
    beneficial = panel_pairs[panel_pairs["child_outcome"] == "beneficial"]
    harmful = panel_pairs[panel_pairs["child_outcome"] == "harmful"]
    neutral = panel_pairs[panel_pairs["child_outcome"] == "neutral"]
    selected_children = panel_pairs[panel_pairs["selected_child"]]

    _scatter_group(ax, panel_pop, "reference_pf", x, y, COLORS["reference_pf"], 4, 0.35)

    if not panel_pairs.empty:
        mx, my = f"mother_{x}", f"mother_{y}"
        fx, fy = f"father_{x}", f"father_{y}"
        dists = np.sqrt(
            (panel_pairs[mx] - panel_pairs[fx]) ** 2
            + (panel_pairs[my] - panel_pairs[fy]) ** 2
        )
        top_idx = dists.nlargest(MAX_CONNECTOR_LINES).index
        for idx in top_idx:
            pair = panel_pairs.loc[idx]
            ax.plot(
                [pair[mx], pair[fx]],
                [pair[my], pair[fy]],
                linestyle="--",
                linewidth=0.4,
                color="#BBBBBB",
                alpha=0.12,
                zorder=1,
            )

    _scatter_parent_points(
        ax, panel_pairs, "mother", x, y, marker="o", color=COLORS["mother"], size=18
    )
    _scatter_parent_points(
        ax, panel_pairs, "father", x, y, marker="^", color=COLORS["father"], size=22
    )
    _scatter_child_points(ax, beneficial, x, y, COLORS["beneficial"], 20)
    _scatter_child_points(ax, harmful, x, y, COLORS["harmful"], 20)
    _scatter_child_points(ax, neutral, x, y, COLORS["neutral"], 16)

    if not selected_children.empty:
        ax.scatter(
            selected_children[f"child_{x}"],
            selected_children[f"child_{y}"],
            s=34,
            facecolors="none",
            edgecolors="#111111",
            linewidths=0.7,
            zorder=5,
        )

    if clip_axes:
        x_lo, x_hi, y_lo, y_hi = _compute_axis_limits(panel_pop, panel_pairs, x, y)
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)

    ax.set_xlabel(x)
    ax.grid(True, linestyle="--", alpha=0.18)


# ---------------------------------------------------------------------------
# 3-D scatter helpers
# ---------------------------------------------------------------------------


def _scatter_group_3d(
    ax: plt.Axes,
    frame: pd.DataFrame,
    point_group: str,
    x: str,
    y: str,
    z: str,
    color: str,
    size: float,
    alpha: float,
    edgecolor: str | None = None,
    linewidth: float = 0.0,
) -> None:
    group = frame[frame["point_group"] == point_group]
    if group.empty:
        return
    ax.scatter(
        group[x],
        group[y],
        group[z],
        s=size,
        c=color,
        alpha=alpha,
        edgecolors=edgecolor if edgecolor is not None else "none",
        linewidths=linewidth,
        depthshade=True,
    )


def _scatter_parent_points_3d(
    ax: plt.Axes,
    frame: pd.DataFrame,
    prefix: str,
    x: str,
    y: str,
    z: str,
    marker: str,
    color: str,
    size: float,
) -> None:
    cols = [f"{prefix}_{x}", f"{prefix}_{y}", f"{prefix}_{z}"]
    unique_points = frame[cols].drop_duplicates()
    if unique_points.empty:
        return
    ax.scatter(
        unique_points[cols[0]],
        unique_points[cols[1]],
        unique_points[cols[2]],
        s=size,
        c=color,
        marker=marker,
        alpha=0.9,
        edgecolors="#111111",
        linewidths=0.25,
        depthshade=True,
    )


def _scatter_child_points_3d(
    ax: plt.Axes,
    frame: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    color: str,
    size: float,
) -> None:
    if frame.empty:
        return
    ax.scatter(
        frame[f"child_{x}"],
        frame[f"child_{y}"],
        frame[f"child_{z}"],
        s=size,
        c=color,
        alpha=0.85,
        edgecolors="none",
        depthshade=True,
    )


def _draw_panel_3d(
    ax: plt.Axes,
    panel_pop: pd.DataFrame,
    panel_pairs: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    clip_axes: bool = True,
    elev: float = VIEW_ELEV,
    azim: float = VIEW_AZIM,
) -> None:
    """Draw a single 3-D scatter panel with all IVF trace elements."""
    beneficial = panel_pairs[panel_pairs["child_outcome"] == "beneficial"]
    harmful = panel_pairs[panel_pairs["child_outcome"] == "harmful"]
    neutral = panel_pairs[panel_pairs["child_outcome"] == "neutral"]
    selected_children = panel_pairs[panel_pairs["selected_child"]]

    _scatter_group_3d(
        ax, panel_pop, "reference_pf", x, y, z, COLORS["reference_pf"], 4, 0.25
    )

    if not panel_pairs.empty:
        mx, my, mz = f"mother_{x}", f"mother_{y}", f"mother_{z}"
        fx, fy, fz = f"father_{x}", f"father_{y}", f"father_{z}"
        dists = np.sqrt(
            (panel_pairs[mx] - panel_pairs[fx]) ** 2
            + (panel_pairs[my] - panel_pairs[fy]) ** 2
            + (panel_pairs[mz] - panel_pairs[fz]) ** 2
        )
        top_idx = dists.nlargest(MAX_CONNECTOR_LINES).index
        for idx in top_idx:
            pair = panel_pairs.loc[idx]
            ax.plot(
                [pair[mx], pair[fx]],
                [pair[my], pair[fy]],
                [pair[mz], pair[fz]],
                linestyle="--",
                linewidth=0.4,
                color="#BBBBBB",
                alpha=0.15,
            )

    _scatter_parent_points_3d(
        ax,
        panel_pairs,
        "mother",
        x,
        y,
        z,
        marker="o",
        color=COLORS["mother"],
        size=22,
    )
    _scatter_parent_points_3d(
        ax,
        panel_pairs,
        "father",
        x,
        y,
        z,
        marker="^",
        color=COLORS["father"],
        size=26,
    )
    _scatter_child_points_3d(ax, beneficial, x, y, z, COLORS["beneficial"], 24)
    _scatter_child_points_3d(ax, harmful, x, y, z, COLORS["harmful"], 24)
    _scatter_child_points_3d(ax, neutral, x, y, z, COLORS["neutral"], 18)

    if not selected_children.empty:
        ax.scatter(
            selected_children[f"child_{x}"],
            selected_children[f"child_{y}"],
            selected_children[f"child_{z}"],
            s=40,
            facecolors="none",
            edgecolors="#111111",
            linewidths=0.7,
            depthshade=False,
        )

    if clip_axes:
        x_lo, x_hi, y_lo, y_hi, z_lo, z_hi = _compute_axis_limits_3d(
            panel_pop, panel_pairs, x, y, z
        )
        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        ax.set_zlim(z_lo, z_hi)

    ax.set_xlabel(x, labelpad=4)
    ax.set_ylabel(y, labelpad=4)
    ax.set_zlabel(z, labelpad=4)
    ax.view_init(elev=elev, azim=azim)
    ax.xaxis.pane.set_alpha(0.05)
    ax.yaxis.pane.set_alpha(0.05)
    ax.zaxis.pane.set_alpha(0.05)
    ax.grid(True, linestyle="--", alpha=0.12)


# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------


def _build_legend_handles() -> list[Line2D]:
    return [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["reference_pf"],
            markeredgecolor="none",
            markersize=5,
            label="Reference PF",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["mother"],
            markeredgecolor="none",
            markersize=5,
            label="Mothers",
        ),
        Line2D(
            [0],
            [0],
            marker="^",
            color="none",
            markerfacecolor=COLORS["father"],
            markeredgecolor="none",
            markersize=5,
            label="Selected fathers",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["beneficial"],
            markeredgecolor="none",
            markersize=5,
            label="Beneficial children",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["harmful"],
            markeredgecolor="none",
            markersize=5,
            label="Harmful children",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="none",
            markeredgecolor="#111111",
            markersize=5,
            label="Selected children",
        ),
    ]


# ---------------------------------------------------------------------------
# Panel sorting / filtering
# ---------------------------------------------------------------------------


def _sort_selected(selected: pd.DataFrame) -> pd.DataFrame:
    panel_role_order = {
        "positive": 0,
        "negative": 1,
        "bimodal_good": 2,
        "bimodal_bad": 3,
    }
    selected = selected.copy()
    selected["_panel_order"] = selected["panel_role"].map(panel_role_order).fillna(99)
    return selected.sort_values(["display_order", "_panel_order"]).reset_index(
        drop=True
    )


def _filter_by_m(selected: pd.DataFrame, m: int) -> pd.DataFrame:
    return selected[selected["m"] == m].reset_index(drop=True)


def _panel_title(panel, include_projection: str | None = None) -> str:
    base = (
        f"{panel.display_label} | {panel.panel_role}\n"
        f"run {panel.run_id}, gen {panel.generation}, cycle {panel.ivf_cycle}, "
        f"median $\\Delta d_{{PF}}$={panel.median_delta_to_pf:.3g}"
    )
    if include_projection:
        base += f"  [{include_projection}]"
    return base


# ---------------------------------------------------------------------------
# Figure: main 2-D panels (bi-objective, M=2)
# ---------------------------------------------------------------------------


def plot_mechanistic_panels(
    selected: pd.DataFrame, populations: pd.DataFrame, pairs: pd.DataFrame
) -> Path:
    """Main paper figure: bi-objective positive vs negative side-by-side."""
    selected = _sort_selected(selected)
    selected = selected[
        selected["panel_role"].isin(["positive", "negative"])
    ].reset_index(drop=True)
    selected = _filter_by_m(selected, 2)

    if selected.empty:
        raise RuntimeError(
            "No M=2 representative cycles available for the main figure. "
            "Run the bi-objective trace cases first."
        )

    ncols = len(selected)
    fig, axes = plt.subplots(1, ncols, figsize=(4.8 * ncols, 4.0))
    if ncols == 1:
        axes = np.asarray([axes])

    for col_idx, panel in enumerate(selected.itertuples(index=False)):
        ax = axes[col_idx]
        panel_pairs = pairs[pairs["cycle_key"] == panel.cycle_key].copy()
        panel_pop = populations[populations["cycle_key"] == panel.cycle_key].copy()

        _draw_panel(ax, panel_pop, panel_pairs, "f1", "f2", clip_axes=True)
        ax.set_ylabel("f2")
        label = (
            "Locally beneficial cycle"
            if panel.panel_role == "positive"
            else "Detrimental cycle"
        )
        ax.set_title(
            f"({chr(97 + col_idx)}) {label} — {panel.display_label}\n"
            f"run {panel.run_id}, gen {panel.generation}, cycle {panel.ivf_cycle}, "
            f"median $\\Delta d_{{PF}}$={panel.median_delta_to_pf:.3g}"
        )

    fig.legend(
        handles=_build_legend_handles(),
        loc="lower center",
        ncol=6,
        frameon=True,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1.0], w_pad=2.0)

    out_path = OUT_DIR / "ivf_trace_mechanistic_panels.pdf"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Figure: 3-D panels (tri-objective, M=3)
# ---------------------------------------------------------------------------


def plot_mechanistic_panels_3d(
    selected: pd.DataFrame, populations: pd.DataFrame, pairs: pd.DataFrame
) -> Path:
    """3-D scatter figure: tri-objective cases (M=3), MAIN_ROLES only."""
    selected = _sort_selected(selected)
    selected = selected[selected["panel_role"].isin(MAIN_ROLES)].reset_index(drop=True)
    selected = _filter_by_m(selected, 3)

    if selected.empty:
        raise RuntimeError(
            "No M=3 representative cycles available for the 3-D figure. "
            "Run the tri-objective trace cases first."
        )

    nrows = len(selected)
    fig = plt.figure(figsize=(6.0, 4.2 * nrows))

    for row_idx, panel in enumerate(selected.itertuples(index=False)):
        ax = fig.add_subplot(nrows, 1, row_idx + 1, projection="3d")
        panel_pairs = pairs[pairs["cycle_key"] == panel.cycle_key].copy()
        panel_pop = populations[populations["cycle_key"] == panel.cycle_key].copy()

        _draw_panel_3d(ax, panel_pop, panel_pairs, "f1", "f2", "f3", clip_axes=True)
        ax.set_title(_panel_title(panel), pad=12)

    fig.legend(
        handles=_build_legend_handles(),
        loc="lower center",
        ncol=4,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle(
        "Representative IVF intensification episodes in 3-D objective space",
        y=1.02,
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.97], h_pad=2.0)

    out_path = OUT_DIR / "ivf_trace_mechanistic_panels_3d.pdf"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Figure: supplementary (all roles, all projections + 3-D for M>=3)
# ---------------------------------------------------------------------------


def plot_mechanistic_panels_supplementary(
    selected: pd.DataFrame, populations: pd.DataFrame, pairs: pd.DataFrame
) -> Path:
    """Supplementary figure: all roles.

    - M=2 rows get a single 2-D panel (f1-f2).
    - M=3 rows get three 2-D projections + one 3-D panel.
    """
    selected = _sort_selected(selected)

    # Determine grid width: max pairwise projections + 1 column for 3-D if any M>=3
    has_3d = (selected["m"] >= 3).any()
    max_2d_pairs = max(len(objective_pairs(int(m))) for m in selected["m"].unique())
    ncols = max_2d_pairs + (1 if has_3d else 0)

    fig = plt.figure(figsize=(3.4 * ncols, 2.55 * len(selected)))

    for row_idx, panel in enumerate(selected.itertuples(index=False)):
        panel_pairs = pairs[pairs["cycle_key"] == panel.cycle_key].copy()
        panel_pop = populations[populations["cycle_key"] == panel.cycle_key].copy()
        proj_pairs = objective_pairs(int(panel.m))

        for col_idx in range(max_2d_pairs):
            ax = fig.add_subplot(len(selected), ncols, row_idx * ncols + col_idx + 1)
            if col_idx >= len(proj_pairs):
                ax.axis("off")
                continue

            x, y = proj_pairs[col_idx]
            _draw_panel(ax, panel_pop, panel_pairs, x, y, clip_axes=True)

            if col_idx == 0:
                ax.set_ylabel(y)
                ax.set_title(_panel_title(panel))
            else:
                ax.set_ylabel("")
                ax.set_title(f"Projection {x}\u2013{y}")

        # 3-D column (last column)
        if has_3d:
            col_3d = max_2d_pairs
            if int(panel.m) >= 3:
                ax3 = fig.add_subplot(
                    len(selected),
                    ncols,
                    row_idx * ncols + col_3d + 1,
                    projection="3d",
                )
                _draw_panel_3d(
                    ax3, panel_pop, panel_pairs, "f1", "f2", "f3", clip_axes=True
                )
                ax3.set_title("3-D view")
            else:
                ax_off = fig.add_subplot(
                    len(selected), ncols, row_idx * ncols + col_3d + 1
                )
                ax_off.axis("off")

    fig.legend(
        handles=_build_legend_handles(),
        loc="lower center",
        ncol=4,
        frameon=True,
        bbox_to_anchor=(0.5, -0.01),
    )
    fig.suptitle(
        "Representative IVF intensification episodes in objective space (all cases)",
        y=1.01,
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.98], h_pad=1.0, w_pad=0.8)

    out_path = OUT_DIR / "ivf_trace_mechanistic_panels_supplementary.pdf"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Figure: distance vs delta
# ---------------------------------------------------------------------------


def binned_profile(frame: pd.DataFrame, n_bins: int = 10) -> pd.DataFrame:
    clean = frame[["parent_distance_obj", "delta_to_pf"]].dropna().copy()
    if clean.empty:
        return pd.DataFrame(columns=["x", "median", "q1", "q3"])
    bins = min(n_bins, clean["parent_distance_obj"].nunique())
    if bins < 2:
        x = float(clean["parent_distance_obj"].iloc[0])
        return pd.DataFrame(
            {
                "x": [x],
                "median": [float(clean["delta_to_pf"].median())],
                "q1": [float(clean["delta_to_pf"].quantile(0.25))],
                "q3": [float(clean["delta_to_pf"].quantile(0.75))],
            }
        )
    clean["bin"] = pd.qcut(clean["parent_distance_obj"], q=bins, duplicates="drop")
    prof = clean.groupby("bin", observed=False).agg(
        x=("parent_distance_obj", "median"),
        median=("delta_to_pf", "median"),
        q1=("delta_to_pf", lambda s: float(s.quantile(0.25))),
        q3=("delta_to_pf", lambda s: float(s.quantile(0.75))),
    )
    return prof.reset_index(drop=True)


def plot_distance_vs_delta(children: pd.DataFrame) -> Path:
    case_meta = (
        children[["display_order", "case_id", "display_label", "role", "m"]]
        .drop_duplicates()
        .sort_values(["display_order", "case_id"])
    )
    preferred_panels = [
        ("positive", 2),
        ("negative", 2),
        ("bimodal", 3),
    ]
    selected_cases = []
    for role, m in preferred_panels:
        match = case_meta[(case_meta["role"] == role) & (case_meta["m"] == m)]
        if not match.empty:
            selected_cases.append(match.iloc[0])
    cases = pd.DataFrame(selected_cases)
    if cases.empty:
        cases = case_meta

    fig, axes = plt.subplots(
        len(cases), 1, figsize=(7.2, 2.0 * len(cases)), sharex=False
    )
    if len(cases) == 1:
        axes = np.asarray([axes])

    for ax, case in zip(axes, cases.itertuples(index=False)):
        sub = children[children["case_id"] == case.case_id].copy()
        sel = sub[sub["selected_child"]]
        ax.scatter(
            sub["parent_distance_obj"],
            sub["delta_to_pf"],
            s=8,
            c="#9EA7B3",
            alpha=0.22,
            edgecolors="none",
            rasterized=True,
            label="All children",
        )
        if not sel.empty:
            ax.scatter(
                sel["parent_distance_obj"],
                sel["delta_to_pf"],
                s=11,
                c="#1F4E79",
                alpha=0.35,
                edgecolors="none",
                rasterized=True,
                label="Selected children",
            )
        profile = binned_profile(sub)
        if not profile.empty:
            ax.plot(profile["x"], profile["median"], color="#B2182B", linewidth=1.2)
            ax.fill_between(
                profile["x"], profile["q1"], profile["q3"], color="#F4A582", alpha=0.35
            )
        ax.axhline(0.0, color="#111111", linewidth=0.7, linestyle="--")
        ax.set_title(case.display_label)
        ax.set_xlabel("Parent objective-space distance used by H1")
        ax.set_ylabel(r"$\Delta d_{PF}$")
        ax.grid(True, linestyle="--", alpha=0.18)

    axes[0].legend(loc="upper right", frameon=True)
    fig.suptitle(
        "Relationship between dissimilar-parent distance and child quality",
        y=1.01,
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.98], h_pad=1.0)

    out_path = OUT_DIR / "ivf_trace_distance_vs_delta.pdf"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    style()
    ensure_directory(OUT_DIR)
    selected, populations, pairs, children = load_inputs()
    validate_population_snapshots(selected, populations)

    has_m2 = (selected["m"] == 2).any()
    has_m3 = (selected["m"] == 3).any()

    if has_m2:
        mech = plot_mechanistic_panels(selected, populations, pairs)
        print(f"Saved: {mech}")
    else:
        print("Skipping 2-D main figure (no M=2 cases in representative_cycles).")

    if has_m3:
        mech3d = plot_mechanistic_panels_3d(selected, populations, pairs)
        print(f"Saved: {mech3d}")
    else:
        print("Skipping 3-D figure (no M=3 cases in representative_cycles).")

    supp = plot_mechanistic_panels_supplementary(selected, populations, pairs)
    dist = plot_distance_vs_delta(children)
    print(f"Saved: {supp}")
    print(f"Saved: {dist}")


if __name__ == "__main__":
    main()
