#!/usr/bin/env python3
"""
Head-to-head comparison for IVFSPEA2V2 tuning finalists against IVF/SPEA2 v1.

Default comparison:
  - A43 (Phase A winner)
  - C26 (Phase C winner)
  - IVFSPEA2 (v1 baseline from data/processed/todas_metricas_consolidado.csv)

Metrics:
  - IGD (lower is better)
  - HV  (higher is better)

Statistical test:
  - Mann-Whitney U (two-sided), with Holm-Bonferroni correction per
    (metric, pairwise comparison) across all benchmark instances.

Outputs (default prefix: head_to_head_c26_a43_v1):
  - results/tuning_ivfspea2v2/<prefix>_igd.csv
  - results/tuning_ivfspea2v2/<prefix>_hv.csv
  - results/tuning_ivfspea2v2/<prefix>_summary.json
  - results/tuning_ivfspea2v2/<prefix>_report.md
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu


def parse_problem_tag(tag: str) -> tuple[str, int]:
    m = re.match(r"^(.+)_M(\d+)$", str(tag))
    if not m:
        raise ValueError(f"Invalid problem tag format: {tag}")
    return m.group(1), int(m.group(2))


def holm_adjust(p_values: list[float]) -> list[float]:
    m = len(p_values)
    if m == 0:
        return []
    order = np.argsort(p_values)
    adjusted_sorted = np.zeros(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        mult = m - rank
        val = min(1.0, float(p_values[idx]) * mult)
        running = max(running, val)
        adjusted_sorted[rank] = running

    adjusted = np.zeros(m, dtype=float)
    for rank, idx in enumerate(order):
        adjusted[idx] = adjusted_sorted[rank]
    return adjusted.tolist()


def metric_direction_is_better(
    value_a: float, value_b: float, higher_is_better: bool
) -> str:
    if np.isclose(value_a, value_b):
        return "="
    if higher_is_better:
        return "+" if value_a > value_b else "-"
    return "+" if value_a < value_b else "-"


def relative_delta_pct(value_a: float, value_b: float, higher_is_better: bool) -> float:
    if np.isclose(value_b, 0.0):
        return np.nan
    if higher_is_better:
        return (value_a - value_b) / abs(value_b) * 100.0
    return (value_b - value_a) / abs(value_b) * 100.0


def load_tuning_candidate(
    tuning_csv: Path,
    phase: str,
    config_id: str,
    alias: str,
) -> pd.DataFrame:
    if not tuning_csv.is_file():
        raise FileNotFoundError(f"Missing tuning CSV: {tuning_csv}")

    df = pd.read_csv(tuning_csv)
    required = {
        "Phase",
        "ConfigID",
        "ProblemTag",
        "ProblemName",
        "M",
        "Run",
        "IGD",
        "HV",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Tuning CSV missing required columns: {sorted(missing)}")

    sub = df[(df["Phase"] == phase) & (df["ConfigID"] == config_id)].copy()
    if sub.empty:
        raise ValueError(f"No rows found for {phase}/{config_id} in {tuning_csv}")

    sub = sub[["ProblemTag", "ProblemName", "M", "Run", "IGD", "HV"]].copy()
    sub["Problem"] = sub["ProblemName"].astype(str)
    sub["M"] = pd.to_numeric(sub["M"], errors="coerce").astype("Int64")
    sub["Run"] = pd.to_numeric(sub["Run"], errors="coerce").astype("Int64")
    sub["IGD"] = pd.to_numeric(sub["IGD"], errors="coerce")
    sub["HV"] = pd.to_numeric(sub["HV"], errors="coerce")
    sub = sub.dropna(subset=["M", "Run", "IGD", "HV"]).copy()
    sub["M"] = sub["M"].astype(int)
    sub["Run"] = sub["Run"].astype(int)

    sub["Algorithm"] = alias
    sub["Source"] = f"tuning:{phase}/{config_id}"
    return sub[
        ["Algorithm", "Source", "ProblemTag", "Problem", "M", "Run", "IGD", "HV"]
    ]


def load_v1_baseline(
    baseline_csv: Path,
    baseline_algorithm: str,
    allowed_pairs: set[tuple[str, int]],
    alias: str,
) -> pd.DataFrame:
    if not baseline_csv.is_file():
        raise FileNotFoundError(f"Missing baseline CSV: {baseline_csv}")

    df = pd.read_csv(baseline_csv)
    required = {"Algoritmo", "Problema", "M", "Run", "IGD", "HV"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Baseline CSV missing required columns: {sorted(missing)}")

    sub = df[df["Algoritmo"] == baseline_algorithm].copy()
    if sub.empty:
        raise ValueError(f"No baseline rows found for algorithm {baseline_algorithm}")

    sub["Problem"] = sub["Problema"].astype(str)
    sub["M"] = (
        sub["M"].astype(str).str.replace("M", "", regex=False).str.extract(r"(\d+)")[0]
    )
    sub["M"] = pd.to_numeric(sub["M"], errors="coerce").astype("Int64")
    sub["Run"] = pd.to_numeric(sub["Run"], errors="coerce").astype("Int64")
    sub["IGD"] = pd.to_numeric(sub["IGD"], errors="coerce")
    sub["HV"] = pd.to_numeric(sub["HV"], errors="coerce")
    sub = sub.dropna(subset=["M", "Run", "IGD", "HV"]).copy()
    sub["M"] = sub["M"].astype(int)
    sub["Run"] = sub["Run"].astype(int)

    sub = sub[
        sub.apply(lambda r: (r["Problem"], int(r["M"])) in allowed_pairs, axis=1)
    ].copy()
    if sub.empty:
        raise ValueError("Baseline has no rows for the selected tuning problem set")

    sub["ProblemTag"] = sub.apply(lambda r: f"{r['Problem']}_M{int(r['M'])}", axis=1)
    sub["Algorithm"] = alias
    sub["Source"] = f"processed:{baseline_algorithm}"
    return sub[
        ["Algorithm", "Source", "ProblemTag", "Problem", "M", "Run", "IGD", "HV"]
    ]


def problem_sort_key(problem_tag: str) -> tuple[int, str]:
    order = ["ZDT", "DTLZ", "WFG", "MaF"]
    for idx, pref in enumerate(order):
        if problem_tag.startswith(pref):
            return (idx, problem_tag)
    return (len(order), problem_tag)


def compare_pairwise(
    df_all: pd.DataFrame,
    problems: list[str],
    algo_a: str,
    algo_b: str,
    metric: str,
    higher_is_better: bool,
    alpha: float,
) -> tuple[pd.DataFrame, dict]:
    rows = []
    pvals = []

    for problem_tag in problems:
        a_vals = df_all[
            (df_all["Algorithm"] == algo_a) & (df_all["ProblemTag"] == problem_tag)
        ][metric].to_numpy(dtype=float)
        b_vals = df_all[
            (df_all["Algorithm"] == algo_b) & (df_all["ProblemTag"] == problem_tag)
        ][metric].to_numpy(dtype=float)

        if len(a_vals) == 0 or len(b_vals) == 0:
            raise ValueError(
                f"Missing data for pair {algo_a} vs {algo_b} on {problem_tag}"
            )

        med_a = float(np.median(a_vals))
        med_b = float(np.median(b_vals))
        direction = metric_direction_is_better(med_a, med_b, higher_is_better)

        _, p_raw = mannwhitneyu(a_vals, b_vals, alternative="two-sided")
        pvals.append(float(p_raw))

        rows.append(
            {
                "Pair": f"{algo_a}_vs_{algo_b}",
                "Metric": metric,
                "ProblemTag": problem_tag,
                "Problem": parse_problem_tag(problem_tag)[0],
                "M": parse_problem_tag(problem_tag)[1],
                f"N_{algo_a}": int(len(a_vals)),
                f"N_{algo_b}": int(len(b_vals)),
                f"Median_{algo_a}": med_a,
                f"Median_{algo_b}": med_b,
                "DirectionRaw": direction,
                f"DeltaPct_{algo_a}_over_{algo_b}": relative_delta_pct(
                    med_a, med_b, higher_is_better
                ),
                "P_raw": float(p_raw),
            }
        )

    out = pd.DataFrame(rows)
    out["P_adj"] = holm_adjust(pvals)

    indicators = []
    for _, row in out.iterrows():
        if row["P_adj"] < alpha:
            indicators.append(row["DirectionRaw"])
        else:
            indicators.append("=")
    out["Indicator"] = indicators

    summary = {
        "pair": f"{algo_a}_vs_{algo_b}",
        "metric": metric,
        "alpha": alpha,
        "wins": indicators.count("+"),
        "ties": indicators.count("="),
        "losses": indicators.count("-"),
        "wins_raw": int((out["DirectionRaw"] == "+").sum()),
        "ties_raw": int((out["DirectionRaw"] == "=").sum()),
        "losses_raw": int((out["DirectionRaw"] == "-").sum()),
        "mean_delta_pct": float(np.nanmean(out[f"DeltaPct_{algo_a}_over_{algo_b}"])),
        "median_delta_pct": float(
            np.nanmedian(out[f"DeltaPct_{algo_a}_over_{algo_b}"])
        ),
    }
    return out, summary


def coverage_table(df_all: pd.DataFrame) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for algo, sub in df_all.groupby("Algorithm"):
        per_problem = sub.groupby("ProblemTag")["Run"].nunique()
        out[algo] = {
            "problems": int(per_problem.size),
            "min_runs_per_problem": int(per_problem.min()),
            "max_runs_per_problem": int(per_problem.max()),
        }
    return out


def build_report_markdown(
    out_prefix: str,
    output_dir: Path,
    problems: list[str],
    coverage: dict[str, dict],
    igd_frames: list[pd.DataFrame],
    hv_frames: list[pd.DataFrame],
    igd_summaries: list[dict],
    hv_summaries: list[dict],
) -> str:
    lines = []
    lines.append(f"# Head-to-Head Report: {out_prefix}")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Scope")
    lines.append(f"- Problems: {len(problems)} ({', '.join(problems)})")
    lines.append("- Metrics: IGD (lower better), HV (higher better)")
    lines.append("- Test: Mann-Whitney U (two-sided) + Holm-Bonferroni correction")
    lines.append("")
    lines.append("## Coverage")
    for algo, cov in coverage.items():
        lines.append(
            f"- {algo}: problems={cov['problems']}, runs/problem={cov['min_runs_per_problem']}..{cov['max_runs_per_problem']}"
        )
    lines.append("")

    lines.append("## IGD Pairwise Summary (+/=/- from first algorithm perspective)")
    for s in igd_summaries:
        lines.append(
            f"- {s['pair']}: corrected {s['wins']}/{s['ties']}/{s['losses']}, "
            f"raw {s['wins_raw']}/{s['ties_raw']}/{s['losses_raw']}, "
            f"mean delta={s['mean_delta_pct']:.3f}%"
        )
    lines.append("")

    lines.append("## HV Pairwise Summary (+/=/- from first algorithm perspective)")
    for s in hv_summaries:
        lines.append(
            f"- {s['pair']}: corrected {s['wins']}/{s['ties']}/{s['losses']}, "
            f"raw {s['wins_raw']}/{s['ties_raw']}/{s['losses_raw']}, "
            f"mean delta={s['mean_delta_pct']:.3f}%"
        )
    lines.append("")

    lines.append("## Files")
    lines.append(f"- `{output_dir / (out_prefix + '_igd.csv')}`")
    lines.append(f"- `{output_dir / (out_prefix + '_hv.csv')}`")
    lines.append(f"- `{output_dir / (out_prefix + '_summary.json')}`")
    lines.append(f"- `{output_dir / (out_prefix + '_report.md')}`")
    lines.append("")
    lines.append("## Notes")
    lines.append(
        "- Interpretation is per-problem, using medians and corrected significance indicators."
    )
    lines.append(
        "- For final tuning promotion, prioritize IGD summary, then inspect HV as secondary support."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Head-to-head tuning comparison: C26 vs A43 vs IVF/SPEA2 v1"
    )
    parser.add_argument(
        "--project-root", default="/home/pedro/desenvolvimento/ivfspea2"
    )
    parser.add_argument("--phase-a", default="A")
    parser.add_argument("--config-a", default="A43")
    parser.add_argument("--alias-a", default="A43")
    parser.add_argument("--phase-b", default="C")
    parser.add_argument("--config-b", default="C26")
    parser.add_argument("--alias-b", default="C26")
    parser.add_argument("--baseline-algorithm", default="IVFSPEA2")
    parser.add_argument("--alias-baseline", default="IVFSPEA2v1")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--output-prefix", default="head_to_head_c26_a43_v1")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    tuning_csv = project_root / "results" / "tuning_ivfspea2v2" / "tuning_runs.csv"
    baseline_csv = (
        project_root / "data" / "processed" / "todas_metricas_consolidado.csv"
    )
    output_dir = project_root / "results" / "tuning_ivfspea2v2"
    output_dir.mkdir(parents=True, exist_ok=True)

    a_df = load_tuning_candidate(tuning_csv, args.phase_a, args.config_a, args.alias_a)
    b_df = load_tuning_candidate(tuning_csv, args.phase_b, args.config_b, args.alias_b)

    problems_a = set(a_df["ProblemTag"].unique().tolist())
    problems_b = set(b_df["ProblemTag"].unique().tolist())
    common_problems = sorted(list(problems_a & problems_b), key=problem_sort_key)
    if not common_problems:
        raise ValueError("No common problems between selected tuning configs")

    a_df = a_df[a_df["ProblemTag"].isin(common_problems)].copy()
    b_df = b_df[b_df["ProblemTag"].isin(common_problems)].copy()

    allowed_pairs = set(parse_problem_tag(tag) for tag in common_problems)
    v1_df = load_v1_baseline(
        baseline_csv=baseline_csv,
        baseline_algorithm=args.baseline_algorithm,
        allowed_pairs=allowed_pairs,
        alias=args.alias_baseline,
    )

    df_all = pd.concat([a_df, b_df, v1_df], ignore_index=True)

    coverage = coverage_table(df_all)

    pairs = [
        (args.alias_b, args.alias_a),
        (args.alias_b, args.alias_baseline),
        (args.alias_a, args.alias_baseline),
    ]

    igd_frames = []
    hv_frames = []
    igd_summaries = []
    hv_summaries = []

    for algo_a, algo_b in pairs:
        igd_df, igd_summary = compare_pairwise(
            df_all=df_all,
            problems=common_problems,
            algo_a=algo_a,
            algo_b=algo_b,
            metric="IGD",
            higher_is_better=False,
            alpha=args.alpha,
        )
        hv_df, hv_summary = compare_pairwise(
            df_all=df_all,
            problems=common_problems,
            algo_a=algo_a,
            algo_b=algo_b,
            metric="HV",
            higher_is_better=True,
            alpha=args.alpha,
        )

        igd_frames.append(igd_df)
        hv_frames.append(hv_df)
        igd_summaries.append(igd_summary)
        hv_summaries.append(hv_summary)

    igd_out = pd.concat(igd_frames, ignore_index=True)
    hv_out = pd.concat(hv_frames, ignore_index=True)

    igd_csv = output_dir / f"{args.output_prefix}_igd.csv"
    hv_csv = output_dir / f"{args.output_prefix}_hv.csv"
    summary_json = output_dir / f"{args.output_prefix}_summary.json"
    report_md = output_dir / f"{args.output_prefix}_report.md"

    igd_out.to_csv(igd_csv, index=False)
    hv_out.to_csv(hv_csv, index=False)

    summary_payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alpha": args.alpha,
        "problems": common_problems,
        "coverage": coverage,
        "pairs": pairs,
        "igd": igd_summaries,
        "hv": hv_summaries,
        "inputs": {
            "tuning_csv": str(tuning_csv),
            "baseline_csv": str(baseline_csv),
            "phase_a": args.phase_a,
            "config_a": args.config_a,
            "phase_b": args.phase_b,
            "config_b": args.config_b,
            "baseline_algorithm": args.baseline_algorithm,
        },
    }
    summary_json.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    report_text = build_report_markdown(
        out_prefix=args.output_prefix,
        output_dir=output_dir,
        problems=common_problems,
        coverage=coverage,
        igd_frames=igd_frames,
        hv_frames=hv_frames,
        igd_summaries=igd_summaries,
        hv_summaries=hv_summaries,
    )
    report_md.write_text(report_text, encoding="utf-8")

    print("=== IVFSPEA2V2 Tuning Head-to-Head ===")
    print(f"Problems: {len(common_problems)}")
    print(f"IGD CSV : {igd_csv}")
    print(f"HV CSV  : {hv_csv}")
    print(f"Summary : {summary_json}")
    print(f"Report  : {report_md}")
    print("\nIGD corrected summaries (+/=/-):")
    for s in igd_summaries:
        print(
            f"  {s['pair']}: {s['wins']}/{s['ties']}/{s['losses']} (raw {s['wins_raw']}/{s['ties_raw']}/{s['losses_raw']})"
        )
    print("\nHV corrected summaries (+/=/-):")
    for s in hv_summaries:
        print(
            f"  {s['pair']}: {s['wins']}/{s['ties']}/{s['losses']} (raw {s['wins_raw']}/{s['ties_raw']}/{s['losses_raw']})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
