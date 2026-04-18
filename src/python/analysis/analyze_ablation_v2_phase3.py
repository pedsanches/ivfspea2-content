#!/usr/bin/env python3
"""
IVF/SPEA2 v2 Ablation - Phase 3 Full-Suite Validation
======================================================

Compares the Phase 2 winner (P2_C05) against baselines on the full 51-instance
suite with 60 runs per instance, using Holm-Bonferroni correction.

Metrics analyzed:
  - IGD (lower is better)
  - HV  (higher is better)

Inputs:
  - data/ablation_v2/phase3/IVFSPEA2_P2_C05_<PROBLEM>_M<M>/*.mat
  - data/processed/todas_metricas_consolidado.csv (IVFSPEA2, SPEA2)

Outputs:
  - results/ablation_v2/phase3/phase3_raw_metrics.csv
  - results/ablation_v2/phase3/phase3_igd_per_instance.csv
  - results/ablation_v2/phase3/phase3_hv_per_instance.csv
  - results/ablation_v2/phase3/phase3_igd_table.tex
  - results/ablation_v2/phase3/phase3_hv_table.tex
  - results/ablation_v2/phase3/phase3_summary.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu


PROJECT_ROOT = Path("/home/pedro/desenvolvimento/ivfspea2")
PHASE3_DIR = PROJECT_ROOT / "data" / "ablation_v2" / "phase3"
if not PHASE3_DIR.is_dir():
    PHASE3_DIR = PROJECT_ROOT / "data" / "legacy" / "ablation_v2" / "phase3"
BASELINE_CSV = PROJECT_ROOT / "data" / "processed" / "todas_metricas_consolidado.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "ablation_v2" / "phase3"
ALPHA = 0.05

WINNER_ALGO = "IVFSPEA2_P2_C05"
BASELINES = ["IVFSPEA2", "SPEA2"]
BASELINE_RUN_MIN = 1
BASELINE_RUN_MAX = 60

PROBLEMS = [
    ("ZDT1", 2),
    ("ZDT2", 2),
    ("ZDT3", 2),
    ("ZDT4", 2),
    ("ZDT6", 2),
    ("DTLZ1", 2),
    ("DTLZ2", 2),
    ("DTLZ3", 2),
    ("DTLZ4", 2),
    ("DTLZ5", 2),
    ("DTLZ6", 2),
    ("DTLZ7", 2),
    ("WFG1", 2),
    ("WFG2", 2),
    ("WFG3", 2),
    ("WFG4", 2),
    ("WFG5", 2),
    ("WFG6", 2),
    ("WFG7", 2),
    ("WFG8", 2),
    ("WFG9", 2),
    ("MaF1", 2),
    ("MaF2", 2),
    ("MaF3", 2),
    ("MaF4", 2),
    ("MaF5", 2),
    ("MaF6", 2),
    ("MaF7", 2),
    ("DTLZ1", 3),
    ("DTLZ2", 3),
    ("DTLZ3", 3),
    ("DTLZ4", 3),
    ("DTLZ5", 3),
    ("DTLZ6", 3),
    ("DTLZ7", 3),
    ("WFG1", 3),
    ("WFG2", 3),
    ("WFG3", 3),
    ("WFG4", 3),
    ("WFG5", 3),
    ("WFG6", 3),
    ("WFG7", 3),
    ("WFG8", 3),
    ("WFG9", 3),
    ("MaF1", 3),
    ("MaF2", 3),
    ("MaF3", 3),
    ("MaF4", 3),
    ("MaF5", 3),
    ("MaF6", 3),
    ("MaF7", 3),
]


def parse_run_id(filename: str) -> int | None:
    match = re.search(r"_(\d+)\.mat$", filename)
    if not match:
        return None
    return int(match.group(1))


def final_scalar(x) -> float | None:
    if x is None:
        return None
    arr = np.asarray(x)
    if arr.size == 0:
        return None
    val = arr.reshape(-1)[-1]
    if val is None or not np.isfinite(val):
        return None
    return float(val)


def load_phase3_winner() -> pd.DataFrame:
    try:
        import pymatreader
    except Exception as exc:
        print(f"ERROR: pymatreader is required: {exc}")
        return pd.DataFrame()

    rows: list[dict] = []
    for problem, m_val in PROBLEMS:
        folder = PHASE3_DIR / f"{WINNER_ALGO}_{problem}_M{m_val}"
        if not folder.is_dir():
            print(f"ERROR: missing winner folder: {folder}")
            return pd.DataFrame()

        mat_files = sorted(folder.glob("*.mat"))
        if len(mat_files) != 60:
            print(
                f"ERROR: expected 60 MAT files in {folder.name}, found {len(mat_files)}"
            )
            return pd.DataFrame()

        for mat_file in mat_files:
            run = parse_run_id(mat_file.name)
            try:
                data = pymatreader.read_mat(str(mat_file))
            except Exception as exc:
                print(f"ERROR: failed reading {mat_file}: {exc}")
                return pd.DataFrame()

            metric = data.get("metric")
            if not isinstance(metric, dict):
                print(f"ERROR: missing metric dict in {mat_file}")
                return pd.DataFrame()

            igd = final_scalar(metric.get("IGD"))
            hv = final_scalar(metric.get("HV"))
            if igd is None or hv is None:
                print(f"ERROR: missing/faulty IGD or HV in {mat_file}")
                return pd.DataFrame()

            rows.append(
                {
                    "Algorithm": WINNER_ALGO,
                    "Problem": problem,
                    "M": m_val,
                    "Run": run,
                    "IGD": igd,
                    "HV": hv,
                }
            )

    df = pd.DataFrame(rows)
    if len(df) != 51 * 60:
        print(f"ERROR: winner rows mismatch, expected 3060, got {len(df)}")
        return pd.DataFrame()
    return df


def load_baselines() -> pd.DataFrame:
    if not BASELINE_CSV.is_file():
        print(f"ERROR: missing baseline CSV: {BASELINE_CSV}")
        return pd.DataFrame()

    df = pd.read_csv(BASELINE_CSV)
    required_cols = {"Algoritmo", "Problema", "M", "Run", "IGD", "HV"}
    if not required_cols.issubset(df.columns):
        print(f"ERROR: baseline CSV missing columns: {required_cols - set(df.columns)}")
        return pd.DataFrame()

    sub = df[df["Algoritmo"].isin(BASELINES)].copy()
    sub["Run"] = pd.to_numeric(sub["Run"], errors="coerce")
    sub = sub[sub["Run"].between(BASELINE_RUN_MIN, BASELINE_RUN_MAX)].copy()
    sub["M"] = sub["M"].astype(str).str.replace("M", "", regex=False).astype(int)
    sub = sub.rename(columns={"Algoritmo": "Algorithm", "Problema": "Problem"})
    sub = sub[["Algorithm", "Problem", "M", "Run", "IGD", "HV"]]

    valid_pairs = set(PROBLEMS)
    sub = sub[sub.apply(lambda r: (r["Problem"], int(r["M"])) in valid_pairs, axis=1)]

    rows: list[dict] = []
    for algo in BASELINES:
        algo_df = sub[sub["Algorithm"] == algo]
        for problem, m_val in PROBLEMS:
            chunk = algo_df[(algo_df["Problem"] == problem) & (algo_df["M"] == m_val)]
            if chunk["Run"].nunique() != 60:
                print(
                    "ERROR: baseline coverage mismatch for "
                    f"{algo} {problem}(M={m_val}), expected 60 runs, got {chunk['Run'].nunique()}"
                )
                return pd.DataFrame()

            bad_igd = chunk["IGD"].isna().sum()
            bad_hv = chunk["HV"].isna().sum()
            if bad_igd or bad_hv:
                print(
                    "ERROR: baseline NaNs for "
                    f"{algo} {problem}(M={m_val}) IGD={bad_igd} HV={bad_hv}"
                )
                return pd.DataFrame()

            rows.extend(chunk.to_dict(orient="records"))

    out = pd.DataFrame(rows)
    if len(out) != 2 * 51 * 60:
        print(f"ERROR: baseline rows mismatch, expected 6120, got {len(out)}")
        return pd.DataFrame()
    return out


def format_median_iqr(values: np.ndarray) -> str:
    values = values[~np.isnan(values)]
    if len(values) == 0:
        return "---"
    med = np.median(values)
    q25, q75 = np.percentile(values, [25, 75])
    iqr = q75 - q25
    if med == 0:
        return "0.00(0.00)e+0"
    exp = int(np.floor(np.log10(abs(med))))
    m = med / (10**exp)
    i = iqr / (10**exp)
    return f"{m:.2f}({i:.2f})e{exp:+d}"


def holm_adjust(p_values: list[float]) -> list[float]:
    m = len(p_values)
    order = np.argsort(p_values)
    adjusted_sorted = np.zeros(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        mult = m - rank
        val = min(1.0, p_values[idx] * mult)
        running = max(running, val)
        adjusted_sorted[rank] = running

    adjusted = np.zeros(m, dtype=float)
    for rank, idx in enumerate(order):
        adjusted[idx] = adjusted_sorted[rank]
    return adjusted.tolist()


def compare_metric(
    df_all: pd.DataFrame, metric: str, higher_is_better: bool
) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []

    for problem, m_val in PROBLEMS:
        row: dict = {"Problem": problem, "M": m_val}

        medians = {}
        for algo in [WINNER_ALGO] + BASELINES:
            vals = df_all[
                (df_all["Algorithm"] == algo)
                & (df_all["Problem"] == problem)
                & (df_all["M"] == m_val)
            ][metric].to_numpy(dtype=float)
            medians[algo] = float(np.median(vals))
            row[f"{algo}_median"] = medians[algo]
            row[f"{algo}_formatted"] = format_median_iqr(vals)

        for baseline in BASELINES:
            winner_vals = df_all[
                (df_all["Algorithm"] == WINNER_ALGO)
                & (df_all["Problem"] == problem)
                & (df_all["M"] == m_val)
            ][metric].to_numpy(dtype=float)
            base_vals = df_all[
                (df_all["Algorithm"] == baseline)
                & (df_all["Problem"] == problem)
                & (df_all["M"] == m_val)
            ][metric].to_numpy(dtype=float)

            _, p_raw = mannwhitneyu(winner_vals, base_vals, alternative="two-sided")
            row[f"{baseline}_p_raw"] = float(p_raw)

            if higher_is_better:
                better = medians[WINNER_ALGO] > medians[baseline]
                worse = medians[WINNER_ALGO] < medians[baseline]
            else:
                better = medians[WINNER_ALGO] < medians[baseline]
                worse = medians[WINNER_ALGO] > medians[baseline]

            row[f"{baseline}_direction"] = "+" if better else "-" if worse else "="

        rows.append(row)

    result = pd.DataFrame(rows)

    summary = {}
    for baseline in BASELINES:
        pvals = result[f"{baseline}_p_raw"].tolist()
        p_adj = holm_adjust(pvals)
        result[f"{baseline}_p_adj"] = p_adj

        indicators = []
        for _, row in result.iterrows():
            if row[f"{baseline}_p_adj"] < ALPHA:
                indicators.append(row[f"{baseline}_direction"])
            else:
                indicators.append("=")
        result[f"{baseline}_indicator"] = indicators

        summary[baseline] = {
            "wins": indicators.count("+"),
            "ties": indicators.count("="),
            "losses": indicators.count("-"),
            "significant": sum(1 for p in p_adj if p < ALPHA),
            "median_delta_pct_mean": float(
                np.mean(
                    [
                        (
                            (w - b) / abs(b) * 100.0
                            if higher_is_better
                            else (b - w) / abs(b) * 100.0
                        )
                        for w, b in zip(
                            result[f"{WINNER_ALGO}_median"],
                            result[f"{baseline}_median"],
                        )
                        if b != 0
                    ]
                )
            ),
        }

    return result, summary


def latex_table(metric_df: pd.DataFrame, metric: str, caption: str, label: str) -> str:
    lines = []
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\caption{" + caption + r"}")
    lines.append(r"\label{" + label + r"}")
    lines.append(r"\centering\tiny")
    lines.append(r"\setlength{\tabcolsep}{3pt}")
    lines.append(r"\begin{tabular}{lrrr}")
    lines.append(r"\toprule")
    lines.append(r"Instance & IVF/SPEA2-v2 (P2\_C05) & IVF/SPEA2-v1 & SPEA2 \\")
    lines.append(r"\midrule")

    for _, row in metric_df.iterrows():
        instance = f"{row['Problem']}(M={int(row['M'])})"

        winner_cell = row[f"{WINNER_ALGO}_formatted"]
        cells = [winner_cell]
        for baseline in BASELINES:
            cell = row[f"{baseline}_formatted"]
            ind = row[f"{baseline}_indicator"]
            if ind == "+":
                cell += r"$^{+}$"
            elif ind == "-":
                cell += r"$^{-}$"
            else:
                cell += r"$^{\approx}$"
            cells.append(cell)

        medians = {
            WINNER_ALGO: row[f"{WINNER_ALGO}_median"],
            "IVFSPEA2": row["IVFSPEA2_median"],
            "SPEA2": row["SPEA2_median"],
        }
        best = (
            max(medians, key=medians.get)
            if metric == "HV"
            else min(medians, key=medians.get)
        )

        if best == WINNER_ALGO:
            cells[0] = r"\textbf{" + cells[0] + "}"
        elif best == "IVFSPEA2":
            cells[1] = r"\textbf{" + cells[1] + "}"
        else:
            cells[2] = r"\textbf{" + cells[2] + "}"

        lines.append(instance + " & " + " & ".join(cells) + r" \\")

    lines.append(r"\midrule")
    summary_parts = [r"$+ / \approx / -$"]
    summary_parts.append("---")
    for baseline in BASELINES:
        indicators = metric_df[f"{baseline}_indicator"].tolist()
        summary_parts.append(
            f"{indicators.count('+')}/{indicators.count('=')}/{indicators.count('-')}"
        )
    lines.append(" & ".join(summary_parts) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


def main() -> int:
    print("=" * 70)
    print("IVF/SPEA2 v2 ABLATION - PHASE 3 FULL-SUITE VALIDATION")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nLoading winner data (P2_C05)...")
    winner_df = load_phase3_winner()
    if winner_df.empty:
        return 1

    print("Loading baseline data (IVFSPEA2, SPEA2)...")
    base_df = load_baselines()
    if base_df.empty:
        return 1

    df_all = pd.concat([winner_df, base_df], ignore_index=True)
    raw_path = OUTPUT_DIR / "phase3_raw_metrics.csv"
    df_all.to_csv(raw_path, index=False)
    print(f"Saved raw metrics: {raw_path}")

    print("\nAnalyzing IGD (lower is better)...")
    igd_df, igd_summary = compare_metric(df_all, metric="IGD", higher_is_better=False)
    igd_csv = OUTPUT_DIR / "phase3_igd_per_instance.csv"
    igd_df.to_csv(igd_csv, index=False)
    print(f"Saved IGD per-instance CSV: {igd_csv}")

    print("Analyzing HV (higher is better)...")
    hv_df, hv_summary = compare_metric(df_all, metric="HV", higher_is_better=True)
    hv_csv = OUTPUT_DIR / "phase3_hv_per_instance.csv"
    hv_df.to_csv(hv_csv, index=False)
    print(f"Saved HV per-instance CSV: {hv_csv}")

    igd_tex = latex_table(
        igd_df,
        metric="IGD",
        caption=(
            "Phase 3 full-suite IGD comparison (median(IQR), 60 runs). "
            "Superscripts compare IVF/SPEA2-v2 (P2\\_C05) against each baseline "
            "using Mann-Whitney tests with Holm-Bonferroni correction "
            "($\\alpha=0.05$): $+$ better, $-$ worse, $\\approx$ tie."
        ),
        label="tab:ablation_v2_phase3_igd",
    )
    igd_tex_path = OUTPUT_DIR / "phase3_igd_table.tex"
    igd_tex_path.write_text(igd_tex)
    print(f"Saved IGD LaTeX table: {igd_tex_path}")

    hv_tex = latex_table(
        hv_df,
        metric="HV",
        caption=(
            "Phase 3 full-suite HV comparison (median(IQR), 60 runs). "
            "Superscripts compare IVF/SPEA2-v2 (P2\\_C05) against each baseline "
            "using Mann-Whitney tests with Holm-Bonferroni correction "
            "($\\alpha=0.05$): $+$ better, $-$ worse, $\\approx$ tie."
        ),
        label="tab:ablation_v2_phase3_hv",
    )
    hv_tex_path = OUTPUT_DIR / "phase3_hv_table.tex"
    hv_tex_path.write_text(hv_tex)
    print(f"Saved HV LaTeX table: {hv_tex_path}")

    summary = {
        "alpha": ALPHA,
        "n_instances": len(PROBLEMS),
        "winner": WINNER_ALGO,
        "baselines": BASELINES,
        "IGD": igd_summary,
        "HV": hv_summary,
    }
    summary_path = OUTPUT_DIR / "phase3_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Saved summary: {summary_path}")

    print("\n" + "=" * 70)
    print("PHASE 3 SUMMARY (Holm-corrected)")
    print("=" * 70)
    for metric_name, metric_summary in [("IGD", igd_summary), ("HV", hv_summary)]:
        print(f"\n{metric_name}:")
        for baseline in BASELINES:
            s = metric_summary[baseline]
            print(
                f"  vs {baseline:<8s}: "
                f"{s['wins']}+ / {s['ties']}= / {s['losses']}- "
                f"(significant={s['significant']}, mean_delta={s['median_delta_pct_mean']:+.2f}%)"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
