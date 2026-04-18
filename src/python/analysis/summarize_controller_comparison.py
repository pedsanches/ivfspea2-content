#!/usr/bin/env python3
"""Summarize controller-vs-baseline comparison results.

Inputs:
  - comparison CSV from compare_controller.py
  - fla_response.csv for HELPS / NOT_HELPS labels

Outputs:
  - enriched per-case CSV with labels/family/outcome columns
  - aggregate W/T/L CSV
  - short markdown summary for paper drafting
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMPARISON_CSV = PROJECT_ROOT / "data" / "processed" / "ppsn_controller_comparison.csv"
DEFAULT_RESPONSE_CSV = PROJECT_ROOT / "data" / "processed" / "fla_response.csv"
DEFAULT_OUT_DIR = PROJECT_ROOT / "results" / "tables"

ALPHA = 0.05
EFFECT_LOW = 0.44
EFFECT_HIGH = 0.56


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize controller comparison results."
    )
    parser.add_argument(
        "--comparison-csv",
        type=Path,
        default=DEFAULT_COMPARISON_CSV,
        help="CSV produced by compare_controller.py. Default: %(default)s",
    )
    parser.add_argument(
        "--response-csv",
        type=Path,
        default=DEFAULT_RESPONSE_CSV,
        help="FLA response CSV with labels. Default: %(default)s",
    )
    parser.add_argument(
        "--tag",
        default="default",
        help="Short tag appended to output filenames.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory. Default: %(default)s",
    )
    return parser.parse_args()


def classify_outcome(p_bh: float, a12: float, metric: str) -> str:
    if np.isnan(p_bh) or np.isnan(a12):
        return "skip"
    if p_bh >= ALPHA:
        return "tie"
    if metric == "IGD":
        if a12 < EFFECT_LOW:
            return "win"
        if a12 > EFFECT_HIGH:
            return "loss"
        return "tie"
    if a12 > EFFECT_HIGH:
        return "win"
    if a12 < EFFECT_LOW:
        return "loss"
    return "tie"


def case_family(case_id: str) -> str:
    match = re.match(r"([a-z]+)", case_id.lower())
    return match.group(1) if match else "unknown"


def outcome_code(outcome: str) -> str:
    return {
        "win": "W",
        "tie": "T",
        "loss": "L",
        "skip": "-",
    }[outcome]


def build_enriched_dataframe(comp: pd.DataFrame, resp: pd.DataFrame) -> pd.DataFrame:
    resp = resp.copy()
    resp["case_id"] = resp["instance"].str.lower()
    resp["label_group"] = resp["label_binary"]

    df = comp.merge(resp[["case_id", "label_group"]], on="case_id", how="left")
    df = df.rename(columns={"label_group": "label"})
    df["label"] = df["label"].fillna("UNLABELED")
    df["family"] = df["case_id"].map(case_family)
    df["m_obj"] = df["case_id"].str.extract(r"_m(\d+)$").astype(float).astype("Int64")
    df["outcome_ctrl_vs_ivf"] = [
        classify_outcome(p, a12, metric)
        for p, a12, metric in zip(
            df["p_bh_ctrl_vs_ivf"], df["a12_ctrl_vs_ivf"], df["metric"]
        )
    ]
    df["outcome_ctrl_vs_spea2"] = [
        classify_outcome(p, a12, metric)
        for p, a12, metric in zip(
            df["p_bh_ctrl_vs_spea2"], df["a12_ctrl_vs_spea2"], df["metric"]
        )
    ]
    df["wtl_ctrl_vs_ivf"] = df["outcome_ctrl_vs_ivf"].map(outcome_code)
    df["wtl_ctrl_vs_spea2"] = df["outcome_ctrl_vs_spea2"].map(outcome_code)
    return df


def make_wtl_rows(df: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    specs = [
        ("CTRL vs IVF-SPEA2", "outcome_ctrl_vs_ivf"),
        ("CTRL vs SPEA2", "outcome_ctrl_vs_spea2"),
    ]
    labels = ["ALL"] + sorted(df["label"].dropna().unique().tolist())
    for metric in sorted(df["metric"].unique()):
        metric_df = df[df["metric"] == metric].copy()
        for comparison, col in specs:
            for label in labels:
                sub = metric_df if label == "ALL" else metric_df[metric_df["label"] == label]
                outcomes = sub[col].tolist()
                rows.append(
                    {
                        "metric": metric,
                        "comparison": comparison,
                        "label": label,
                        "wins": outcomes.count("win"),
                        "ties": outcomes.count("tie"),
                        "losses": outcomes.count("loss"),
                        "skips": outcomes.count("skip"),
                        "n_cases": len(sub),
                        "match_or_beat": outcomes.count("win") + outcomes.count("tie"),
                    }
                )
    return rows


def write_markdown_summary(
    enriched: pd.DataFrame,
    wtl: pd.DataFrame,
    args: argparse.Namespace,
    md_path: Path,
) -> None:
    hv = wtl[wtl["metric"] == "HV"].copy()
    igd = wtl[wtl["metric"] == "IGD"].copy()

    lines: list[str] = []
    lines.append("# Controller Comparison Summary")
    lines.append("")
    lines.append(f"- Comparison CSV: {args.comparison_csv}")
    lines.append(f"- Response CSV: {args.response_csv}")
    lines.append(f"- Tag: {args.tag}")
    lines.append(f"- Cases (all metrics): {enriched['case_id'].nunique()}")
    lines.append("")

    label_counts = (
        enriched[["case_id", "label"]]
        .drop_duplicates()
        .value_counts("label")
        .sort_index()
    )
    lines.append("## Labels")
    for label, count in label_counts.items():
        lines.append(f"- {label}: {count}")
    lines.append("")

    def add_metric_section(metric_name: str, metric_df: pd.DataFrame) -> None:
        lines.append(f"## {metric_name}")
        for comparison in ["CTRL vs IVF-SPEA2", "CTRL vs SPEA2"]:
            lines.append(f"### {comparison}")
            comp_df = metric_df[metric_df["comparison"] == comparison]
            for _, row in comp_df.iterrows():
                lines.append(
                    f"- {row['label']}: W={row['wins']} T={row['ties']} L={row['losses']} "
                    f"(match-or-beat={row['match_or_beat']}/{row['n_cases']})"
                )
        lines.append("")

    add_metric_section("HV", hv)
    add_metric_section("IGD", igd)

    hv_case = enriched[enriched["metric"] == "HV"].copy()
    family = (
        hv_case.groupby(["family", "outcome_ctrl_vs_ivf"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    lines.append("## HV vs IVF by Family")
    for _, row in family.iterrows():
        lines.append(
            f"- {row['family']}: "
            f"W={int(row.get('win', 0))} T={int(row.get('tie', 0))} L={int(row.get('loss', 0))}"
        )
    lines.append("")

    md_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    comp = pd.read_csv(args.comparison_csv)
    resp = pd.read_csv(args.response_csv)
    enriched = build_enriched_dataframe(comp, resp)
    wtl_rows = make_wtl_rows(enriched)
    wtl = pd.DataFrame(wtl_rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    enriched_csv = args.out_dir / f"controller_comparison_enriched_{args.tag}.csv"
    wtl_csv = args.out_dir / f"controller_wtl_{args.tag}.csv"
    summary_md = args.out_dir / f"controller_summary_{args.tag}.md"

    enriched.to_csv(enriched_csv, index=False)
    wtl.to_csv(wtl_csv, index=False)
    write_markdown_summary(enriched, wtl, args, summary_md)

    print(f"Saved: {enriched_csv}")
    print(f"Saved: {wtl_csv}")
    print(f"Saved: {summary_md}")


if __name__ == "__main__":
    main()
