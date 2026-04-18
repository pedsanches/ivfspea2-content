#!/usr/bin/env python3
"""Prepare Phase B center from completed Phase A analysis."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


def _load_phase_a_ranking(results_root: Path) -> pd.DataFrame:
    ranking_path = results_root / "tuning_phase_ranking.csv"
    if not ranking_path.is_file():
        raise FileNotFoundError(f"Missing ranking file: {ranking_path}")

    df = pd.read_csv(ranking_path)
    if "Phase" not in df.columns:
        raise ValueError("tuning_phase_ranking.csv missing 'Phase' column")

    phase_a = df.loc[df["Phase"] == "A"].copy()
    if phase_a.empty:
        raise ValueError("No Phase A rows in tuning_phase_ranking.csv")

    if "CompleteCoverage" in phase_a.columns:
        phase_a = phase_a.loc[phase_a["CompleteCoverage"].astype(bool)].copy()
        if phase_a.empty:
            raise ValueError("Phase A has no complete-coverage configs")

    order_cols = [
        "MeanCombinedRank",
        "MeanNormRankIGD",
        "MeanNormRankHV",
    ]
    for col in order_cols:
        if col not in phase_a.columns:
            raise ValueError(f"Phase ranking missing required column: {col}")

    phase_a = phase_a.sort_values(
        by=order_cols,
        ascending=[True, True, True],
    ).reset_index(drop=True)
    return phase_a


def _write_env_file(
    env_path: Path, best: pd.Series, source_csv: Path, phase_b_runbase: int
) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Auto-generated from Phase A ranking",
        f"# Generated at: {now}",
        f"# Source: {source_csv}",
        f"# Selected ConfigID: {best['ConfigID']}",
        f"# MeanCombinedRank: {best['MeanCombinedRank']:.6f}",
        "",
        "export V2_TUNE_PHASE=B",
        f"export V2_TUNE_FIXED_R={best['R']}",
        f"export V2_TUNE_FIXED_C={best['C']}",
        f"export V2_TUNE_FIXED_CYCLES={int(best['Cycles'])}",
        "",
        "# Recommended execution defaults",
        "export V2_TUNE_PROBLEM_SET=FULL12",
        "export V2_TUNE_ONLY_MISSING=1",
        "export V2_TUNE_RUNS=30",
        "export V2_TUNE_MAXFE=50000",
        f"export V2_TUNE_RUNBASE={phase_b_runbase}",
    ]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary(
    summary_path: Path, best: pd.Series, top_df: pd.DataFrame, env_path: Path
) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = [
        "# Phase A Analysis Summary for Phase B Preparation",
        "",
        f"Generated at: {now}",
        "",
        "## Selected center for Phase B",
        f"- ConfigID: `{best['ConfigID']}`",
        f"- R: `{best['R']}`",
        f"- C: `{best['C']}`",
        f"- Cycles: `{int(best['Cycles'])}`",
        f"- MeanCombinedRank: `{best['MeanCombinedRank']:.6f}`",
        f"- MeanNormRankIGD: `{best['MeanNormRankIGD']:.6f}`",
        f"- MeanNormRankHV: `{best['MeanNormRankHV']:.6f}`",
        "",
        "## Top candidates from Phase A",
        "",
        "| Rank | ConfigID | R | C | Cycles | MeanCombinedRank | MeanNormRankIGD | MeanNormRankHV |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]

    rows = []
    for rank, row in enumerate(
        top_df.reset_index(drop=True).to_dict("records"), start=1
    ):
        rows.append(
            "| {rank} | {cfg} | {r:.3f} | {c:.3f} | {cy} | {mcr:.6f} | {igd:.6f} | {hv:.6f} |".format(
                rank=rank,
                cfg=row["ConfigID"],
                r=row["R"],
                c=row["C"],
                cy=int(row["Cycles"]),
                mcr=row["MeanCombinedRank"],
                igd=row["MeanNormRankIGD"],
                hv=row["MeanNormRankHV"],
            )
        )

    footer = [
        "",
        "## Ready-to-run command (Phase B)",
        "```bash",
        f"set -a && source '{env_path}' && set +a",
        "LAUNCH_MODE=run V2_TUNE_WORKERS=6 scripts/experiments/launch_ivfspea2v2_tuning.sh B 3",
        "```",
        "",
    ]

    summary_path.write_text("\n".join(header + rows + footer), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare Phase B center from Phase A results"
    )
    parser.add_argument(
        "--project-root",
        default="/home/pedro/desenvolvimento/ivfspea2",
        help="Project root directory",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of top Phase A candidates to include in summary",
    )
    parser.add_argument(
        "--phase-b-runbase",
        type=int,
        default=800001,
        help="Isolated run-id base for scientific Phase B execution",
    )
    args = parser.parse_args()

    if args.top_k < 1:
        raise ValueError("--top-k must be >= 1")
    if args.phase_b_runbase < 1:
        raise ValueError("--phase-b-runbase must be >= 1")

    project_root = Path(args.project_root)
    results_root = project_root / "results" / "tuning_ivfspea2v2"

    phase_a = _load_phase_a_ranking(results_root)
    best = phase_a.iloc[0]
    top_df = phase_a.head(args.top_k).copy()

    env_path = results_root / "phaseB_center_from_phaseA.env"
    summary_path = results_root / "phaseB_preparation_from_phaseA.md"
    top_csv_path = results_root / "phaseA_top_candidates_for_phaseB.csv"

    _write_env_file(
        env_path,
        best,
        results_root / "tuning_phase_ranking.csv",
        args.phase_b_runbase,
    )
    top_df.to_csv(top_csv_path, index=False)
    _write_summary(summary_path, best, top_df, env_path)

    print("=== Phase B Preparation Ready ===")
    print(f"Selected ConfigID: {best['ConfigID']}")
    print(f"Center: R={best['R']}, C={best['C']}, Cycles={int(best['Cycles'])}")
    print(f"Env file: {env_path}")
    print(f"Top candidates CSV: {top_csv_path}")
    print(f"Summary: {summary_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
