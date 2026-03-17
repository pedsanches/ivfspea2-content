#!/usr/bin/env python3
"""
Analyze phased tuning outputs for IVFSPEA2V2.

Inputs:
  - results/tuning_ivfspea2v2/manifest_phase*_configs.csv
  - results/tuning_ivfspea2v2/manifest_phase*_problems.csv
  - results/tuning_ivfspea2v2/manifest_phase*_cases.csv
  - data/tuning_ivfspea2v2/phase*/IVFSPEA2V2_<ConfigID>_<ProblemTag>/*.mat

Outputs:
  - results/tuning_ivfspea2v2/tuning_runs.csv
  - results/tuning_ivfspea2v2/tuning_case_summary.csv
  - results/tuning_ivfspea2v2/tuning_problem_ranking.csv
  - results/tuning_ivfspea2v2/tuning_phase_ranking.csv
  - results/tuning_ivfspea2v2/tuning_recommendations.csv

Ranking logic:
  - IGD: lower is better
  - HV:  higher is better
  - For each (phase, problem), compute normalized rank for IGD/HV
    and combine as mean(norm_rank_igd, norm_rank_hv).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pymatreader


RUN_RE = re.compile(r"_(\d+)\.mat$")


def parse_run_id(filename: str) -> int | None:
    m = RUN_RE.search(filename)
    if not m:
        return None
    return int(m.group(1))


def final_scalar(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        if value.size == 0:
            return None
        return float(value.flat[-1])
    try:
        return float(value)
    except Exception:
        return None


def load_metrics(mat_path: Path) -> tuple[float | None, float | None]:
    try:
        data = pymatreader.read_mat(str(mat_path))
    except Exception:
        return None, None

    metric = data.get("metric")
    if metric is None or not isinstance(metric, dict):
        return None, None

    igd = final_scalar(metric.get("IGD"))
    hv = final_scalar(metric.get("HV"))
    return igd, hv


def iqr(series: pd.Series) -> float:
    arr = pd.to_numeric(series, errors="coerce").dropna().to_numpy()
    if arr.size == 0:
        return np.nan
    return float(np.percentile(arr, 75) - np.percentile(arr, 25))


def load_phase_frames(
    results_root: Path, phase: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cfg = results_root / f"manifest_phase{phase}_configs.csv"
    prob = results_root / f"manifest_phase{phase}_problems.csv"
    case = results_root / f"manifest_phase{phase}_cases.csv"
    if not (cfg.is_file() and prob.is_file() and case.is_file()):
        raise FileNotFoundError(f"Missing manifest(s) for phase {phase}")
    return pd.read_csv(cfg), pd.read_csv(prob), pd.read_csv(case)


def collect_runs(
    project_root: Path,
    phase: str,
    cfg_df: pd.DataFrame,
    prob_df: pd.DataFrame,
    case_df: pd.DataFrame,
) -> pd.DataFrame:
    data_root = project_root / "data" / "tuning_ivfspea2v2" / f"phase{phase}"
    cfg_map = cfg_df.set_index("ConfigID")
    prob_map = prob_df.set_index("ProblemTag")

    rows: list[dict] = []

    for rec in case_df.itertuples(index=False):
        config_id = rec.ConfigID
        problem_tag = rec.ProblemTag
        run_start = int(rec.RunStart)
        run_end = int(rec.RunEnd)

        if config_id not in cfg_map.index or problem_tag not in prob_map.index:
            continue

        prob_name = str(prob_map.loc[problem_tag, "ProblemName"])
        m_val = int(prob_map.loc[problem_tag, "M"])
        expected_prefix = f"IVFSPEA2V2_{prob_name}_M{m_val}_"

        folder = data_root / f"IVFSPEA2V2_{config_id}_{problem_tag}"
        if not folder.is_dir():
            continue

        files = [f for f in folder.glob("*.mat") if f.name.startswith(expected_prefix)]
        if not files:
            continue

        run_to_file: dict[int, Path] = {}
        for fpath in files:
            rid = parse_run_id(fpath.name)
            if rid is None:
                continue
            # keep first deterministic occurrence
            run_to_file.setdefault(rid, fpath)

        expected_runs = range(run_start, run_end + 1)
        for run_id in expected_runs:
            fpath = run_to_file.get(run_id)
            if fpath is None:
                continue

            igd, hv = load_metrics(fpath)
            if igd is None or hv is None:
                continue
            if np.isnan(igd) or np.isnan(hv):
                continue
            if igd >= 1e12:
                continue

            rows.append(
                {
                    "Phase": phase,
                    "ConfigID": config_id,
                    "ProblemTag": problem_tag,
                    "ProblemName": prob_name,
                    "M": m_val,
                    "Run": run_id,
                    "IGD": igd,
                    "HV": hv,
                    "R": float(cfg_map.loc[config_id, "R"]),
                    "C": float(cfg_map.loc[config_id, "C"]),
                    "Cycles": int(cfg_map.loc[config_id, "Cycles"]),
                    "MutRate": float(cfg_map.loc[config_id, "M"]),
                    "VarRate": float(cfg_map.loc[config_id, "V"]),
                    "EARN": int(cfg_map.loc[config_id, "EARN"]),
                    "N_Offspring": int(cfg_map.loc[config_id, "N_Offspring"]),
                    "Description": str(cfg_map.loc[config_id, "Description"]),
                }
            )

    return pd.DataFrame(rows)


def summarize_cases(runs_df: pd.DataFrame) -> pd.DataFrame:
    if runs_df.empty:
        return pd.DataFrame()

    grouped = runs_df.groupby(
        [
            "Phase",
            "ConfigID",
            "ProblemTag",
            "ProblemName",
            "M",
            "R",
            "C",
            "Cycles",
            "MutRate",
            "VarRate",
            "EARN",
            "N_Offspring",
            "Description",
        ],
        as_index=False,
    ).agg(
        Runs=("Run", "count"),
        IGD_Median=("IGD", "median"),
        IGD_Mean=("IGD", "mean"),
        IGD_IQR=("IGD", iqr),
        HV_Median=("HV", "median"),
        HV_Mean=("HV", "mean"),
        HV_IQR=("HV", iqr),
    )
    return grouped


def rank_within_problem(case_summary: pd.DataFrame) -> pd.DataFrame:
    if case_summary.empty:
        return pd.DataFrame()

    out_frames: list[pd.DataFrame] = []
    for (phase, problem_tag), sub in case_summary.groupby(
        ["Phase", "ProblemTag"], as_index=False
    ):
        sub = sub.copy()
        n = len(sub)

        sub["Rank_IGD"] = sub["IGD_Median"].rank(method="min", ascending=True)
        sub["Rank_HV"] = sub["HV_Median"].rank(method="min", ascending=False)

        denom = max(n - 1, 1)
        sub["NormRank_IGD"] = (sub["Rank_IGD"] - 1) / denom
        sub["NormRank_HV"] = (sub["Rank_HV"] - 1) / denom
        sub["CombinedRank"] = (sub["NormRank_IGD"] + sub["NormRank_HV"]) / 2.0

        out_frames.append(sub)

    return pd.concat(out_frames, ignore_index=True)


def rank_by_phase(
    problem_rank_df: pd.DataFrame, problem_manifest: dict[str, set[str]]
) -> pd.DataFrame:
    if problem_rank_df.empty:
        return pd.DataFrame()

    grouped = problem_rank_df.groupby(
        [
            "Phase",
            "ConfigID",
            "R",
            "C",
            "Cycles",
            "MutRate",
            "VarRate",
            "EARN",
            "N_Offspring",
            "Description",
        ],
        as_index=False,
    ).agg(
        ProblemCoverage=("ProblemTag", "nunique"),
        MeanCombinedRank=("CombinedRank", "mean"),
        MeanNormRankIGD=("NormRank_IGD", "mean"),
        MeanNormRankHV=("NormRank_HV", "mean"),
        MeanIGDMedian=("IGD_Median", "mean"),
        MeanHVMedian=("HV_Median", "mean"),
    )

    grouped["ExpectedProblems"] = grouped["Phase"].map(
        lambda p: len(problem_manifest.get(p, set()))
    )
    grouped["CompleteCoverage"] = (
        grouped["ProblemCoverage"] == grouped["ExpectedProblems"]
    )

    grouped = grouped.sort_values(
        by=[
            "Phase",
            "CompleteCoverage",
            "MeanCombinedRank",
            "MeanNormRankIGD",
            "MeanNormRankHV",
        ],
        ascending=[True, False, True, True, True],
    ).reset_index(drop=True)

    return grouped


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze IVFSPEA2V2 tuning runs")
    parser.add_argument(
        "--project-root",
        default="/home/pedro/desenvolvimento/ivfspea2",
        help="Project root",
    )
    parser.add_argument(
        "--phases",
        default="A,B,C",
        help="Comma-separated phases to include (e.g., A,B,C)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root)
    results_root = project_root / "results" / "tuning_ivfspea2v2"
    results_root.mkdir(parents=True, exist_ok=True)

    phases = [p.strip().upper() for p in args.phases.split(",") if p.strip()]
    phases = [p for p in phases if p in {"A", "B", "C"}]
    if not phases:
        print("No valid phase selected.")
        return 2

    all_runs: list[pd.DataFrame] = []
    problem_manifest: dict[str, set[str]] = {}

    for phase in phases:
        try:
            cfg_df, prob_df, case_df = load_phase_frames(results_root, phase)
        except FileNotFoundError as exc:
            print(f"[WARN] skipping phase {phase}: {exc}")
            continue

        problem_manifest[phase] = set(prob_df["ProblemTag"].astype(str).tolist())
        phase_runs = collect_runs(project_root, phase, cfg_df, prob_df, case_df)
        if phase_runs.empty:
            print(f"[WARN] phase {phase}: no valid run-level metrics found")
            continue

        print(
            f"[Phase {phase}] loaded {len(phase_runs)} runs, "
            f"configs={phase_runs['ConfigID'].nunique()}, problems={phase_runs['ProblemTag'].nunique()}"
        )
        all_runs.append(phase_runs)

    if not all_runs:
        print("No run-level data found across selected phases.")
        return 1

    runs_df = pd.concat(all_runs, ignore_index=True)
    case_summary = summarize_cases(runs_df)
    problem_rank = rank_within_problem(case_summary)
    phase_rank = rank_by_phase(problem_rank, problem_manifest)

    recommendations = (
        phase_rank.groupby("Phase", as_index=False)
        .head(1)
        .copy()
        .sort_values(by="Phase")
        .reset_index(drop=True)
    )

    out_runs = results_root / "tuning_runs.csv"
    out_case = results_root / "tuning_case_summary.csv"
    out_prob_rank = results_root / "tuning_problem_ranking.csv"
    out_phase_rank = results_root / "tuning_phase_ranking.csv"
    out_reco = results_root / "tuning_recommendations.csv"

    runs_df.to_csv(out_runs, index=False)
    case_summary.to_csv(out_case, index=False)
    problem_rank.to_csv(out_prob_rank, index=False)
    phase_rank.to_csv(out_phase_rank, index=False)
    recommendations.to_csv(out_reco, index=False)

    print("\n=== IVFSPEA2V2 Tuning Analysis ===")
    print(f"Run-level rows: {len(runs_df)}")
    print(f"Case summaries : {len(case_summary)}")
    print(f"Problem ranks  : {len(problem_rank)}")
    print(f"Phase ranks    : {len(phase_rank)}")
    print(
        f"Outputs:\n  - {out_runs}\n  - {out_case}\n  - {out_prob_rank}\n  - {out_phase_rank}\n  - {out_reco}"
    )

    if not recommendations.empty:
        print("\nRecommended configs by phase:")
        for row in recommendations.itertuples(index=False):
            print(
                f"  Phase {row.Phase}: {row.ConfigID} "
                f"(complete={row.CompleteCoverage}, mean_combined_rank={row.MeanCombinedRank:.4f}, "
                f"coverage={row.ProblemCoverage}/{row.ExpectedProblems})"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
