#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pymatreader

from ivf_trace_common import (
    PROJECT_ROOT,
    coerce_struct_list,
    distance_to_reference_pf,
    ensure_directory,
    final_scalar,
    matrix_to_numpy,
    normalize_m_value,
    objective_columns,
    pick_nearest_row,
    quantile_target,
    scalar_bool,
    vector_to_numpy,
)


CONFIG_PATH = PROJECT_ROOT / "config" / "ivf_trace_cases.csv"
SUMMARY_ROOT = PROJECT_ROOT / "data" / "raw" / "ivf_trace_cases" / "summary"
DETAILED_ROOT = PROJECT_ROOT / "data" / "raw" / "ivf_trace_cases" / "detailed"
REFERENCE_ROOT = PROJECT_ROOT / "data" / "raw" / "ivf_trace_cases" / "reference_pf"
OUT_DIR = PROJECT_ROOT / "results" / "ivf_trace"
TOL = 1e-12


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-root", type=Path, default=SUMMARY_ROOT)
    parser.add_argument("--detailed-root", type=Path, default=DETAILED_ROOT)
    parser.add_argument("--reference-root", type=Path, default=REFERENCE_ROOT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def load_reference_pf(reference_root: Path, problem: str, m: int, d: int) -> np.ndarray:
    path = reference_root / f"{problem}_M{m}_D{d}_truePF.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Missing reference PF: {path}")
    return pd.read_csv(path).to_numpy(dtype=float)


def compute_child_metrics(
    cycle: dict, reference_pf: np.ndarray
) -> tuple[dict, pd.DataFrame]:
    child_objs = matrix_to_numpy(cycle.get("child_objs"))
    mother_objs = matrix_to_numpy(cycle.get("mother_objs"))
    father_objs = matrix_to_numpy(cycle.get("father_objs"))
    parent_dist = vector_to_numpy(cycle.get("child_parent_distance_obj"), float)
    mother_mutated = vector_to_numpy(cycle.get("child_mother_mutated"), bool)
    selected = vector_to_numpy(cycle.get("child_selected"), bool)
    selected_fitness = vector_to_numpy(
        cycle.get("child_selected_fitness_after_env"), float
    )

    if child_objs.size == 0:
        empty = pd.DataFrame(
            columns=[
                "child_index",
                "parent_distance_obj",
                "mother_mutated",
                "selected_child",
                "selected_child_fitness_after_env",
                "child_pf_distance",
                "best_parent_pf_distance",
                "delta_to_pf",
            ]
        )
        return {}, empty

    child_pf_distance = distance_to_reference_pf(child_objs, reference_pf)
    mother_pf_distance = distance_to_reference_pf(mother_objs, reference_pf)
    father_pf_distance = distance_to_reference_pf(father_objs, reference_pf)
    best_parent_pf_distance = np.minimum(mother_pf_distance, father_pf_distance)
    delta_to_pf = child_pf_distance - best_parent_pf_distance

    child_table = pd.DataFrame(
        {
            "child_index": np.arange(1, len(delta_to_pf) + 1, dtype=int),
            "parent_distance_obj": parent_dist,
            "mother_mutated": mother_mutated,
            "selected_child": selected,
            "selected_child_fitness_after_env": selected_fitness,
            "child_pf_distance": child_pf_distance,
            "best_parent_pf_distance": best_parent_pf_distance,
            "delta_to_pf": delta_to_pf,
        }
    )

    cycle_summary = {
        "num_children": int(len(delta_to_pf)),
        "num_selected_children": int(np.sum(selected)),
        "median_delta_to_pf": float(np.median(delta_to_pf)),
        "mean_delta_to_pf": float(np.mean(delta_to_pf)),
        "share_better_children": float(np.mean(delta_to_pf < -TOL)),
        "share_worse_children": float(np.mean(delta_to_pf > TOL)),
        "selection_rate": float(np.mean(selected)),
        "median_parent_distance_obj": float(np.median(parent_dist)),
    }
    return cycle_summary, child_table


def build_trace_tables(
    manifest: pd.DataFrame,
    summary_root: Path,
    reference_root: Path,
    detailed_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    run_rows: list[dict] = []
    cycle_rows: list[dict] = []
    child_rows: list[dict] = []

    for case in manifest.sort_values("display_order").itertuples(index=False):
        case_dir = summary_root / case.case_id
        if not case_dir.is_dir() and detailed_root is not None:
            case_dir = detailed_root / case.case_id
        if not case_dir.is_dir():
            raise FileNotFoundError(
                f"Missing trace directory for {case.case_id} "
                f"(looked in {summary_root} and {detailed_root})"
            )
        reference_pf = load_reference_pf(
            reference_root, case.problem, int(case.m), int(case.d)
        )

        for mat_path in sorted(case_dir.glob("*.mat")):
            payload = pymatreader.read_mat(str(mat_path))
            metric = payload.get("metric", {})
            trace_run = payload.get("trace_run", {})
            cycles = coerce_struct_list(trace_run.get("cycles"))
            run_id = int(trace_run.get("run_id", 0))
            seed = int(trace_run.get("seed", 0))
            final_igd = final_scalar(metric.get("IGD"))
            final_hv = final_scalar(metric.get("HV"))

            run_rows.append(
                {
                    "display_order": int(case.display_order),
                    "case_id": case.case_id,
                    "display_label": case.display_label,
                    "role": case.role,
                    "problem": case.problem,
                    "m": int(case.m),
                    "d": int(case.d),
                    "run_id": run_id,
                    "seed": seed,
                    "summary_mat_path": str(mat_path),
                    "final_igd": final_igd,
                    "final_hv": final_hv,
                    "n_cycles": int(trace_run.get("n_cycles", len(cycles))),
                }
            )

            for cycle in cycles:
                generation = int(final_scalar(cycle.get("generation")) or 0)
                ivf_cycle = int(final_scalar(cycle.get("ivf_cycle")) or 0)
                cycle_key = (
                    f"{case.case_id}__run{run_id:04d}__g{generation:04d}__c{ivf_cycle}"
                )
                cycle_summary, child_table = compute_child_metrics(cycle, reference_pf)

                cycle_rows.append(
                    {
                        "display_order": int(case.display_order),
                        "case_id": case.case_id,
                        "display_label": case.display_label,
                        "role": case.role,
                        "problem": case.problem,
                        "m": int(case.m),
                        "d": int(case.d),
                        "run_id": run_id,
                        "seed": seed,
                        "cycle_key": cycle_key,
                        "generation": generation,
                        "ivf_cycle": ivf_cycle,
                        "avg_fitness_before": float(
                            final_scalar(cycle.get("avg_fitness_before")) or np.nan
                        ),
                        "avg_fitness_after": float(
                            final_scalar(cycle.get("avg_fitness_after")) or np.nan
                        ),
                        "collective_improved": scalar_bool(
                            cycle.get("collective_improved")
                        ),
                        "problem_fe_before": float(
                            final_scalar(cycle.get("problem_fe_before")) or np.nan
                        ),
                        "problem_fe_after": float(
                            final_scalar(cycle.get("problem_fe_after")) or np.nan
                        ),
                        **cycle_summary,
                    }
                )

                if child_table.empty:
                    continue
                child_table["case_id"] = case.case_id
                child_table["display_order"] = int(case.display_order)
                child_table["display_label"] = case.display_label
                child_table["role"] = case.role
                child_table["problem"] = case.problem
                child_table["m"] = int(case.m)
                child_table["d"] = int(case.d)
                child_table["run_id"] = run_id
                child_table["seed"] = seed
                child_table["cycle_key"] = cycle_key
                child_table["generation"] = generation
                child_table["ivf_cycle"] = ivf_cycle
                child_table["collective_improved"] = scalar_bool(
                    cycle.get("collective_improved")
                )
                child_rows.extend(child_table.to_dict(orient="records"))

    return pd.DataFrame(run_rows), pd.DataFrame(cycle_rows), pd.DataFrame(child_rows)


def select_cycles(
    manifest: pd.DataFrame, run_df: pd.DataFrame, cycle_df: pd.DataFrame
) -> pd.DataFrame:
    selected_rows: list[dict] = []

    for case in manifest.sort_values("display_order").itertuples(index=False):
        case_runs = run_df[
            (run_df["case_id"] == case.case_id) & (run_df["n_cycles"] > 0)
        ].copy()
        case_cycles = cycle_df[cycle_df["case_id"] == case.case_id].copy()
        if case_runs.empty or case_cycles.empty:
            raise ValueError(f"No usable trace data for {case.case_id}")

        if case.role in {"positive", "negative"}:
            run_row, best_cycle = _select_run_cycle_joint(
                case_runs, case_cycles, case.role, case.cycle_selection,
                bad_run_min_igd=case.bad_run_min_igd,
            )
            selected_rows.append(
                _build_selected_row(
                    case=case,
                    run_row=run_row,
                    cycle_row=best_cycle,
                    panel_role=case.role,
                    selection_type="joint_run_cycle",
                )
            )
            continue

        if case.role != "bimodal":
            raise ValueError(f"Unsupported role: {case.role}")

        if case.run_selection != "q1_q3":
            raise ValueError(
                f"Unsupported bimodal run selection rule: {case.run_selection}"
            )

        good_run = _select_quantile_run(case_runs, 0.25, None)
        selected_rows.append(
            _select_cycle_row(
                case, good_run,
                case_cycles[case_cycles["run_id"] == good_run["run_id"]],
                "bimodal_good", "q1_run",
            )
        )

        bad_threshold = (
            float(case.bad_run_min_igd) if pd.notna(case.bad_run_min_igd) else None
        )
        bad_run = _select_quantile_run(case_runs, 0.75, bad_threshold)
        selected_rows.append(
            _select_cycle_row(
                case, bad_run,
                case_cycles[case_cycles["run_id"] == bad_run["run_id"]],
                "bimodal_bad", "q3_run",
            )
        )

    return pd.DataFrame(selected_rows)


def _build_selected_row(
    case, run_row, cycle_row, panel_role: str, selection_type: str,
) -> dict:
    return {
        "case_id": case.case_id,
        "display_order": int(case.display_order),
        "display_label": case.display_label,
        "role": case.role,
        "panel_role": panel_role,
        "problem": case.problem,
        "m": int(case.m),
        "d": int(case.d),
        "run_id": int(run_row["run_id"]),
        "seed": int(run_row["seed"]),
        "final_igd": float(run_row["final_igd"]),
        "final_hv": float(run_row["final_hv"]),
        "cycle_key": cycle_row["cycle_key"],
        "generation": int(cycle_row["generation"]),
        "ivf_cycle": int(cycle_row["ivf_cycle"]),
        "selection_type": selection_type,
        "run_selection_rule": case.run_selection,
        "cycle_selection_rule": case.cycle_selection,
        "median_delta_to_pf": float(cycle_row["median_delta_to_pf"]),
        "share_better_children": float(cycle_row["share_better_children"]),
        "share_worse_children": float(cycle_row["share_worse_children"]),
        "selection_rate": float(cycle_row["selection_rate"]),
        "collective_improved": bool(cycle_row["collective_improved"]),
    }


def _select_cycle_row(
    case, run_row, cycle_df: pd.DataFrame, panel_role: str, selection_type: str,
) -> dict:
    if cycle_df.empty:
        raise ValueError(
            f"Selected run has no cycle data: {case.case_id} run {run_row['run_id']}"
        )
    ordered = _ordered_cycles(cycle_df, case.cycle_selection, panel_role)
    return _build_selected_row(case, run_row, ordered.iloc[0], panel_role, selection_type)


def _select_run_cycle_joint(
    case_runs: pd.DataFrame,
    case_cycles: pd.DataFrame,
    role: str,
    cycle_selection: str,
    bad_run_min_igd: float | None = None,
) -> tuple[pd.Series, pd.Series]:
    """Select best (run, cycle) pair jointly across near-median runs."""
    median_igd = float(case_runs["final_igd"].median())
    iqr = float(case_runs["final_igd"].quantile(0.75) - case_runs["final_igd"].quantile(0.25))
    if iqr <= 0:
        iqr = float(case_runs["final_igd"].std(ddof=0))
    if iqr <= 0:
        iqr = 1.0

    # Keep runs within 1 IQR of median
    eligible = case_runs[
        (case_runs["final_igd"] >= median_igd - iqr)
        & (case_runs["final_igd"] <= median_igd + iqr)
    ].copy()
    if eligible.empty:
        eligible = case_runs.copy()

    # Restrict cycles to cycle 1 if available
    c1 = case_cycles[case_cycles["ivf_cycle"] == 1]
    pool = c1 if not c1.empty else case_cycles

    # Only keep cycles from eligible runs
    pool = pool[pool["run_id"].isin(eligible["run_id"])].copy()
    if pool.empty:
        pool = c1 if not c1.empty else case_cycles

    # Rank all eligible cycles by visual clarity
    ordered = _ordered_cycles(pool, cycle_selection, role)
    best_cycle = ordered.iloc[0]
    run_row = eligible[eligible["run_id"] == best_cycle["run_id"]].iloc[0]
    return run_row, best_cycle


def _select_run_row(
    case_runs: pd.DataFrame,
    run_selection: str,
    role: str,
    bad_run_min_igd: float | None,
) -> pd.Series:
    if run_selection != "closest_median":
        raise ValueError(f"Unsupported run selection rule: {run_selection}")

    target_igd = float(case_runs["final_igd"].median())
    target_hv = float(case_runs["final_hv"].median())
    ranked = case_runs.copy()
    if role == "positive":
        hv_supported = ranked[ranked["final_hv"] >= target_hv]
        if not hv_supported.empty:
            ranked = hv_supported
    if role == "negative" and pd.notna(bad_run_min_igd):
        thresholded = ranked[ranked["final_igd"] > float(bad_run_min_igd)]
        if not thresholded.empty:
            ranked = thresholded
    if role == "negative":
        hv_supported = ranked[ranked["final_hv"] <= target_hv]
        if not hv_supported.empty:
            ranked = hv_supported
    ranked["_joint_distance"] = _joint_distance_to_targets(
        ranked,
        target_igd=target_igd,
        target_hv=target_hv,
        scale_igd=_robust_scale(case_runs["final_igd"]),
        scale_hv=_robust_scale(case_runs["final_hv"]),
    )
    return ranked.sort_values(["_joint_distance", "run_id"], kind="mergesort").iloc[0]


def _select_quantile_run(
    case_runs: pd.DataFrame, q: float, bad_threshold: float | None
) -> pd.Series:
    target_igd = quantile_target(case_runs["final_igd"], q)
    target_hv = float(case_runs["final_hv"].median())
    if q <= 0.5:
        eligible = case_runs[case_runs["final_igd"] <= target_igd]
        hv_supported = eligible[eligible["final_hv"] >= target_hv]
        if not hv_supported.empty:
            eligible = hv_supported
    else:
        eligible = case_runs[case_runs["final_igd"] >= target_igd]
        if bad_threshold is not None:
            thresholded = eligible[eligible["final_igd"] > bad_threshold]
            if not thresholded.empty:
                eligible = thresholded
        hv_supported = eligible[eligible["final_hv"] <= target_hv]
        if not hv_supported.empty:
            eligible = hv_supported
    if eligible.empty:
        eligible = case_runs
    eligible = eligible.copy()
    eligible["_joint_distance"] = _joint_distance_to_targets(
        eligible,
        target_igd=target_igd,
        target_hv=target_hv,
        scale_igd=_robust_scale(case_runs["final_igd"]),
        scale_hv=_robust_scale(case_runs["final_hv"]),
    )
    return eligible.sort_values(["_joint_distance", "run_id"], kind="mergesort").iloc[0]


def _ordered_cycles(
    cycle_df: pd.DataFrame, cycle_selection: str, panel_role: str
) -> pd.DataFrame:
    # Restrict to cycle 1 for cleaner visualisation; fall back to all if none.
    c1 = cycle_df[cycle_df["ivf_cycle"] == 1]
    if not c1.empty:
        cycle_df = c1

    if cycle_selection == "min_median_delta":
        return cycle_df.sort_values(
            [
                "share_better_children",
                "median_delta_to_pf",
                "selection_rate",
                "generation",
                "ivf_cycle",
            ],
            ascending=[False, True, False, True, True],
            kind="mergesort",
        )

    if cycle_selection == "max_median_delta":
        return cycle_df.sort_values(
            [
                "share_worse_children",
                "median_delta_to_pf",
                "selection_rate",
                "generation",
                "ivf_cycle",
            ],
            ascending=[False, False, False, True, True],
            kind="mergesort",
        )

    if cycle_selection == "minmax_median_delta":
        if panel_role == "bimodal_good":
            return _ordered_cycles(cycle_df, "min_median_delta", panel_role)
        return _ordered_cycles(cycle_df, "max_median_delta", panel_role)

    raise ValueError(f"Unsupported cycle selection rule: {cycle_selection}")


def _robust_scale(series: pd.Series) -> float:
    scale = float(series.quantile(0.75) - series.quantile(0.25))
    if scale <= 0.0 or not np.isfinite(scale):
        scale = float(series.std(ddof=0))
    if scale <= 0.0 or not np.isfinite(scale):
        scale = 1.0
    return scale


def _joint_distance_to_targets(
    frame: pd.DataFrame,
    target_igd: float,
    target_hv: float,
    scale_igd: float,
    scale_hv: float,
) -> pd.Series:
    igd_term = (frame["final_igd"] - target_igd).abs() / scale_igd
    hv_term = (frame["final_hv"] - target_hv).abs() / scale_hv
    return np.sqrt(igd_term * igd_term + hv_term * hv_term)


def load_cycle_from_trace(path: Path, generation: int, ivf_cycle: int) -> dict:
    payload = pymatreader.read_mat(str(path))
    trace_run = payload.get("trace_run", {})
    cycles = coerce_struct_list(trace_run.get("cycles"))
    for cycle in cycles:
        gen = int(final_scalar(cycle.get("generation")) or 0)
        cyc = int(final_scalar(cycle.get("ivf_cycle")) or 0)
        if gen == generation and cyc == ivf_cycle:
            return cycle
    raise KeyError(f"Cycle g={generation} c={ivf_cycle} not found in {path}")


def build_representative_payloads(
    selected_df: pd.DataFrame,
    run_df: pd.DataFrame,
    detailed_root: Path,
    reference_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    population_rows: list[dict] = []
    pair_rows: list[dict] = []
    selected_rows: list[dict] = []

    for panel in selected_df.sort_values(["case_id", "panel_role"]).itertuples(
        index=False
    ):
        run_row = run_df[
            (run_df["case_id"] == panel.case_id) & (run_df["run_id"] == panel.run_id)
        ].iloc[0]
        summary_path = Path(run_row["summary_mat_path"])
        detailed_path = detailed_root / panel.case_id / summary_path.name
        source_path = detailed_path if detailed_path.is_file() else summary_path
        source_mode = "detailed" if detailed_path.is_file() else "summary"
        cycle = load_cycle_from_trace(source_path, panel.generation, panel.ivf_cycle)
        reference_pf = load_reference_pf(
            reference_root, panel.problem, int(panel.m), int(panel.d)
        )
        _, child_table = compute_child_metrics(cycle, reference_pf)

        child_objs = matrix_to_numpy(cycle.get("child_objs"))
        mother_objs = matrix_to_numpy(cycle.get("mother_objs"))
        father_objs = matrix_to_numpy(cycle.get("father_objs"))
        obj_cols = objective_columns(int(panel.m))

        selected_rows.append(
            {
                **panel._asdict(),
                "source_mode": source_mode,
                "source_path": str(source_path),
            }
        )

        for group_name, arr in [
            ("reference_pf", reference_pf),
            ("population_before", matrix_to_numpy(cycle.get("population_before_objs"))),
            ("population_after", matrix_to_numpy(cycle.get("population_after_objs"))),
        ]:
            if arr.size == 0:
                continue
            for idx, point in enumerate(arr, start=1):
                row = {
                    "cycle_key": panel.cycle_key,
                    "case_id": panel.case_id,
                    "panel_role": panel.panel_role,
                    "display_label": panel.display_label,
                    "point_group": group_name,
                    "point_index": idx,
                }
                row.update({col: float(point[i]) for i, col in enumerate(obj_cols)})
                population_rows.append(row)

        if child_table.empty:
            continue
        for idx, child_meta in child_table.iterrows():
            pair_row = {
                "cycle_key": panel.cycle_key,
                "case_id": panel.case_id,
                "panel_role": panel.panel_role,
                "display_label": panel.display_label,
                "child_index": int(child_meta["child_index"]),
                "parent_distance_obj": float(child_meta["parent_distance_obj"]),
                "mother_mutated": bool(child_meta["mother_mutated"]),
                "selected_child": bool(child_meta["selected_child"]),
                "selected_child_fitness_after_env": float(
                    child_meta["selected_child_fitness_after_env"]
                ),
                "child_pf_distance": float(child_meta["child_pf_distance"]),
                "best_parent_pf_distance": float(child_meta["best_parent_pf_distance"]),
                "delta_to_pf": float(child_meta["delta_to_pf"]),
                "child_outcome": _child_outcome(float(child_meta["delta_to_pf"])),
            }
            pair_row.update(
                {
                    f"mother_{col}": float(mother_objs[idx, i])
                    for i, col in enumerate(obj_cols)
                }
            )
            pair_row.update(
                {
                    f"father_{col}": float(father_objs[idx, i])
                    for i, col in enumerate(obj_cols)
                }
            )
            pair_row.update(
                {
                    f"child_{col}": float(child_objs[idx, i])
                    for i, col in enumerate(obj_cols)
                }
            )
            pair_rows.append(pair_row)

    return (
        pd.DataFrame(selected_rows),
        pd.DataFrame(population_rows),
        pd.DataFrame(pair_rows),
    )


def _child_outcome(delta: float) -> str:
    if delta < -TOL:
        return "beneficial"
    if delta > TOL:
        return "harmful"
    return "neutral"


def main() -> None:
    args = parse_args()
    ensure_directory(args.out_dir)

    manifest = pd.read_csv(CONFIG_PATH)
    manifest["m"] = manifest["m"].map(normalize_m_value)

    run_df, cycle_df, child_df = build_trace_tables(
        manifest, args.summary_root, args.reference_root,
        detailed_root=args.detailed_root,
    )
    selected_df = select_cycles(manifest, run_df, cycle_df)
    representative_df, population_df, pair_df = build_representative_payloads(
        selected_df, run_df, args.detailed_root, args.reference_root
    )

    outputs = {
        "trace_run_summary.csv": run_df,
        "trace_cycle_summary.csv": cycle_df,
        "trace_child_records.csv": child_df,
        "representative_cycles.csv": representative_df,
        "representative_cycle_populations.csv": population_df,
        "representative_cycle_pairs.csv": pair_df,
    }
    for name, frame in outputs.items():
        out_path = args.out_dir / name
        frame.to_csv(out_path, index=False)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
