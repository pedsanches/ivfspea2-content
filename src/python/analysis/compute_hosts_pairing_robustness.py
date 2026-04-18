#!/usr/bin/env python3
"""Recompute host-comparison endpoint tests under pairing-aware robustness rules.

Reads `data/processed/hosts_paper.csv`, applies Wilcoxon signed-rank tests on the strictly
paired NSGA tracks, Mann--Whitney U on the unpaired IVF/SPEA2 track, and an order-aligned
Wilcoxon sensitivity analysis for IVF/SPEA2. Results are written to
`results/tables/hosts_pairing_robustness.csv` and `results/tables/hosts_pairing_robustness.tex`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wilcoxon
from statsmodels.stats.multitest import multipletests


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "hosts_paper.csv"
OUT_DIR = PROJECT_ROOT / "results" / "tables"

HOST_PAIRS = [
    ("IVFSPEA2", "SPEA2"),
    ("IVFNSGAII", "NSGAII"),
    ("IVFNSGAIII", "NSGAIII"),
]
METRICS = ["IGD", "HV"]


def vargha_delaney_a12(x: np.ndarray, y: np.ndarray) -> float:
    count = 0.0
    for xv in x:
        count += np.sum(xv > y)
        count += 0.5 * np.sum(xv == y)
    return count / (len(x) * len(y))


def oriented_a12(metric: str, raw_a12: float) -> float:
    return 1.0 - raw_a12 if metric == "IGD" else raw_a12


def sign_label(
    metric: str, median_ivf: float, median_base: float, significant: bool
) -> str:
    if not significant:
        return "="
    if metric == "IGD":
        return "+" if median_ivf < median_base else "-"
    return "+" if median_ivf > median_base else "-"


def paired_rows(
    ivf_sub: pd.DataFrame, base_sub: pd.DataFrame, metric: str
) -> tuple[np.ndarray, np.ndarray, int]:
    common = sorted(set(ivf_sub["run"]) & set(base_sub["run"]))
    if len(common) < 2:
        return np.array([]), np.array([]), 0
    ivf_vals = ivf_sub.set_index("run").loc[common, metric].to_numpy(dtype=float)
    base_vals = base_sub.set_index("run").loc[common, metric].to_numpy(dtype=float)
    return ivf_vals, base_vals, len(common)


def aligned_rows(
    ivf_sub: pd.DataFrame, base_sub: pd.DataFrame, metric: str
) -> tuple[np.ndarray, np.ndarray, int]:
    ivf_vals = ivf_sub.sort_values("run")[metric].to_numpy(dtype=float)
    base_vals = base_sub.sort_values("run")[metric].to_numpy(dtype=float)
    n = min(len(ivf_vals), len(base_vals))
    return ivf_vals[:n], base_vals[:n], n


def run_test(test_name: str, ivf_vals: np.ndarray, base_vals: np.ndarray) -> float:
    if len(ivf_vals) < 2 or len(base_vals) < 2:
        return np.nan
    if test_name == "wilcoxon":
        try:
            return float(wilcoxon(ivf_vals, base_vals, alternative="two-sided").pvalue)
        except ValueError:
            return 1.0
    try:
        return float(mannwhitneyu(ivf_vals, base_vals, alternative="two-sided").pvalue)
    except ValueError:
        return 1.0


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    problems = (
        df[["problem", "M", "group"]].drop_duplicates().sort_values(["M", "problem"])
    )

    for ivf_algo, base_algo in HOST_PAIRS:
        df_ivf = df[df["algo"] == ivf_algo]
        df_base = df[df["algo"] == base_algo]

        for _, inst in problems.iterrows():
            problem = inst["problem"]
            m_val = int(inst["M"])
            group = inst["group"]
            ivf_sub = df_ivf[(df_ivf["problem"] == problem) & (df_ivf["M"] == m_val)]
            base_sub = df_base[
                (df_base["problem"] == problem) & (df_base["M"] == m_val)
            ]
            if ivf_sub.empty or base_sub.empty:
                continue

            for metric in METRICS:
                if ivf_algo == "IVFSPEA2":
                    primary_ivf = ivf_sub[metric].to_numpy(dtype=float)
                    primary_base = base_sub[metric].to_numpy(dtype=float)
                    p_primary = run_test("mannwhitney", primary_ivf, primary_base)
                    a12_primary = vargha_delaney_a12(primary_ivf, primary_base)
                    rows.append(
                        {
                            "analysis_mode": "primary_unpaired",
                            "comparison": f"{ivf_algo}_vs_{base_algo}",
                            "ivf_algo": ivf_algo,
                            "base_algo": base_algo,
                            "problem": problem,
                            "M": m_val,
                            "group": group,
                            "metric": metric,
                            "test": "mannwhitneyu",
                            "n_ivf": len(primary_ivf),
                            "n_base": len(primary_base),
                            "n_pairs": 0,
                            "p_value": p_primary,
                            "a12_raw": a12_primary,
                            "a12_ivf": oriented_a12(metric, a12_primary),
                            "median_ivf": float(np.median(primary_ivf)),
                            "median_base": float(np.median(primary_base)),
                        }
                    )

                    sens_ivf, sens_base, n_pairs = aligned_rows(
                        ivf_sub, base_sub, metric
                    )
                    p_sens = run_test("wilcoxon", sens_ivf, sens_base)
                    a12_sens = vargha_delaney_a12(sens_ivf, sens_base)
                    rows.append(
                        {
                            "analysis_mode": "sensitivity_order_aligned",
                            "comparison": f"{ivf_algo}_vs_{base_algo}",
                            "ivf_algo": ivf_algo,
                            "base_algo": base_algo,
                            "problem": problem,
                            "M": m_val,
                            "group": group,
                            "metric": metric,
                            "test": "wilcoxon",
                            "n_ivf": len(sens_ivf),
                            "n_base": len(sens_base),
                            "n_pairs": n_pairs,
                            "p_value": p_sens,
                            "a12_raw": a12_sens,
                            "a12_ivf": oriented_a12(metric, a12_sens),
                            "median_ivf": float(np.median(sens_ivf))
                            if len(sens_ivf)
                            else np.nan,
                            "median_base": float(np.median(sens_base))
                            if len(sens_base)
                            else np.nan,
                        }
                    )
                else:
                    paired_ivf, paired_base, n_pairs = paired_rows(
                        ivf_sub, base_sub, metric
                    )
                    p_primary = run_test("wilcoxon", paired_ivf, paired_base)
                    a12_primary = vargha_delaney_a12(paired_ivf, paired_base)
                    rows.append(
                        {
                            "analysis_mode": "primary_paired",
                            "comparison": f"{ivf_algo}_vs_{base_algo}",
                            "ivf_algo": ivf_algo,
                            "base_algo": base_algo,
                            "problem": problem,
                            "M": m_val,
                            "group": group,
                            "metric": metric,
                            "test": "wilcoxon",
                            "n_ivf": len(paired_ivf),
                            "n_base": len(paired_base),
                            "n_pairs": n_pairs,
                            "p_value": p_primary,
                            "a12_raw": a12_primary,
                            "a12_ivf": oriented_a12(metric, a12_primary),
                            "median_ivf": float(np.median(paired_ivf))
                            if len(paired_ivf)
                            else np.nan,
                            "median_base": float(np.median(paired_base))
                            if len(paired_base)
                            else np.nan,
                        }
                    )

    out = pd.DataFrame(rows)
    for _, sub_idx in out.groupby(
        ["analysis_mode", "comparison", "metric"]
    ).groups.items():
        pvals = out.loc[list(sub_idx), "p_value"].to_numpy(dtype=float)
        valid = ~np.isnan(pvals)
        padj = np.full_like(pvals, np.nan, dtype=float)
        if valid.sum() > 0:
            padj[valid] = multipletests(pvals[valid], method="fdr_bh")[1]
        out.loc[list(sub_idx), "p_adj"] = padj

    out["significant"] = out["p_adj"].fillna(1.0) < 0.05
    out["sign"] = [
        sign_label(row.metric, row.median_ivf, row.median_base, bool(row.significant))
        for row in out.itertuples(index=False)
    ]
    return out.sort_values(
        ["analysis_mode", "comparison", "metric", "M", "problem"]
    ).reset_index(drop=True)


def write_summary_tex(df: pd.DataFrame, out_path: Path) -> None:
    summary = (
        df.groupby(["analysis_mode", "comparison", "metric", "sign"], as_index=False)
        .size()
        .pivot(
            index=["analysis_mode", "comparison", "metric"],
            columns="sign",
            values="size",
        )
        .fillna(0)
        .reset_index()
    )
    for col in ["+", "=", "-"]:
        if col not in summary.columns:
            summary[col] = 0

    newline = r"\\"
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Pairing-robustness summary for the endpoint analyses. Primary uses Wilcoxon on strict run-ID pairs for NSGA tracks and Mann--Whitney on the unpaired IVF/SPEA2 block; the order-aligned Wilcoxon is reported only as sensitivity for IVF/SPEA2.}",
        "\\label{tab:hosts_pairing_robustness}",
        "\\scriptsize",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        f"Analysis & Comparison/metric & Wins & Ties & Losses {newline}",
        "\\midrule",
    ]
    for _, row in summary.iterrows():
        label = f"{row['comparison']} ({row['metric']})"
        lines.append(
            f"{row['analysis_mode']} & {label} & {int(row['+'])} & {int(row['='])} & {int(row['-'])} {newline}"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print(f"[A2] Reading endpoint data: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(
        f"[A2] Loaded {len(df)} rows across {df['algo'].nunique()} algorithms and {df[['problem', 'M']].drop_duplicates().shape[0]} instances"
    )

    out_df = build_rows(df)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "hosts_pairing_robustness.csv"
    out_tex = OUT_DIR / "hosts_pairing_robustness.tex"
    out_df.to_csv(out_csv, index=False)
    write_summary_tex(out_df, out_tex)
    print(f"[A2] Wrote {out_csv} ({len(out_df)} rows)")
    print(f"[A2] Wrote {out_tex}")


if __name__ == "__main__":
    main()
