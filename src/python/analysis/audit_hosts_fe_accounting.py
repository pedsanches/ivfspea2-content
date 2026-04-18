#!/usr/bin/env python3
"""Audit FE accounting for IVF host pipelines.

Reads the MATLAB host/operator implementations plus `data/processed/hosts_convergence.csv`,
extracts the budget-accounting formulas used by each host-specific IVF pipeline, summarizes
checkpoint FE ranges and pairwise FE-grid drift on the dynamic traces, and writes
`results/tables/hosts_fe_audit.csv` and `results/tables/hosts_fe_audit.tex`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUT_DIR = PROJECT_ROOT / "results" / "tables"
CONV_CSV = PROJECT_ROOT / "data" / "processed" / "hosts_convergence.csv"

PIPELINES = {
    "IVFSPEA2": {
        "base": "SPEA2",
        "host_file": PROJECT_ROOT
        / "src"
        / "matlab"
        / "lib"
        / "PlatEMO"
        / "Algorithms"
        / "Multi-objective optimization"
        / "IVF-SPEA2-V2"
        / "IVFSPEA2V2.m",
        "operator_file": PROJECT_ROOT
        / "src"
        / "matlab"
        / "lib"
        / "PlatEMO"
        / "Algorithms"
        / "Multi-objective optimization"
        / "IVF-SPEA2-V2"
        / "IVF_V2.m",
        "activation_pattern": "if IVF_Total_FE > ivf_rate * Problem.FE",
        "cap_pattern": "Limite_Maximo_Avals = Problem.N",
        "cap_check_pattern": "if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals",
        "mating_pattern": "Mating_N = max(Problem.N - IVF_Gen_FE, 0)",
    },
    "IVFNSGAII": {
        "base": "NSGAII",
        "host_file": PROJECT_ROOT
        / "src"
        / "matlab"
        / "lib"
        / "PlatEMO"
        / "Algorithms"
        / "Multi-objective optimization"
        / "IVF-NSGA-II"
        / "IVFNSGAII.m",
        "operator_file": PROJECT_ROOT
        / "src"
        / "matlab"
        / "lib"
        / "PlatEMO"
        / "Algorithms"
        / "Multi-objective optimization"
        / "IVF-NSGA-II"
        / "IVF_NSGAII.m",
        "activation_pattern": "if rand() > R",
        "cap_pattern": "Limite_Maximo_Avals  = Problem.N",
        "cap_check_pattern": "if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals",
        "mating_pattern": "Mating_N = max(Problem.N - IVF_Gen_FE, 0)",
    },
    "IVFNSGAIII": {
        "base": "NSGAIII",
        "host_file": PROJECT_ROOT
        / "src"
        / "matlab"
        / "lib"
        / "PlatEMO"
        / "Algorithms"
        / "Multi-objective optimization"
        / "IVF-NSGA-III"
        / "IVFNSGAIII.m",
        "operator_file": PROJECT_ROOT
        / "src"
        / "matlab"
        / "lib"
        / "PlatEMO"
        / "Algorithms"
        / "Multi-objective optimization"
        / "IVF-NSGA-III"
        / "IVF_NSGAIII.m",
        "activation_pattern": "if IVF_Total_FE > ivf_rate * Problem.FE",
        "cap_pattern": "Limite_Maximo_Avals  = Problem.N",
        "cap_check_pattern": "if IVF_Gen_FE + Avaliacoes_Por_Ciclo > Limite_Maximo_Avals",
        "mating_pattern": "Mating_N = max(Problem.N - IVF_Gen_FE, 0)",
    },
}


def find_line(lines: list[str], pattern: str) -> tuple[int | None, str | None]:
    for idx, line in enumerate(lines, start=1):
        if pattern in line:
            return idx, line.strip()
    return None, None


def load_text(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def build_static_rows() -> list[dict]:
    rows: list[dict] = []
    for pipeline, cfg in PIPELINES.items():
        host_lines = load_text(cfg["host_file"])
        op_lines = load_text(cfg["operator_file"])
        act_line, act_text = find_line(op_lines, cfg["activation_pattern"])
        cap_line, cap_text = find_line(op_lines, cfg["cap_pattern"])
        cap_check_line, cap_check_text = find_line(op_lines, cfg["cap_check_pattern"])
        mating_line, mating_text = find_line(
            host_lines + op_lines, cfg["mating_pattern"]
        )
        rows.append(
            {
                "section": "static",
                "pipeline": pipeline,
                "base_algo": cfg["base"],
                "problem": None,
                "M": None,
                "run": None,
                "activation_gate_line": act_line,
                "activation_gate": act_text,
                "generation_cap_line": cap_line,
                "generation_cap": cap_text,
                "generation_cap_check_line": cap_check_line,
                "generation_cap_check": cap_check_text,
                "mating_budget_line": mating_line,
                "mating_budget": mating_text,
                "fixed_generation_budget": True,
                "n_checkpoints_ivf": None,
                "fe_min_ivf": None,
                "fe_max_ivf": None,
                "overshoot_ivf": None,
                "n_checkpoints_base": None,
                "fe_min_base": None,
                "fe_max_base": None,
                "overshoot_base": None,
                "mean_abs_fe_drift": None,
                "max_abs_fe_drift": None,
                "exact_match_pct": None,
            }
        )
    return rows


def build_empirical_rows(conv: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    run_summary = {}
    for key, group in conv.groupby(["algo", "problem", "M", "run"], sort=True):
        run_summary[key] = group.sort_values("FE")["FE"].to_numpy(dtype=int)

    for pipeline, cfg in PIPELINES.items():
        base = cfg["base"]
        ivf_keys = [key for key in run_summary if key[0] == pipeline]
        for _, problem, m_val, run in sorted(ivf_keys):
            ivf_fe = run_summary[(pipeline, problem, m_val, run)]
            base_key = (base, problem, m_val, run)
            if base_key not in run_summary:
                continue
            base_fe = run_summary[base_key]
            n = min(len(ivf_fe), len(base_fe))
            if n == 0:
                continue
            drift = np.abs(ivf_fe[:n] - base_fe[:n])
            exact = np.mean(ivf_fe[:n] == base_fe[:n]) * 100.0
            rows.append(
                {
                    "section": "empirical",
                    "pipeline": pipeline,
                    "base_algo": base,
                    "problem": problem,
                    "M": int(m_val),
                    "run": int(run),
                    "activation_gate_line": None,
                    "activation_gate": None,
                    "generation_cap_line": None,
                    "generation_cap": None,
                    "generation_cap_check_line": None,
                    "generation_cap_check": None,
                    "mating_budget_line": None,
                    "mating_budget": None,
                    "fixed_generation_budget": None,
                    "n_checkpoints_ivf": int(len(ivf_fe)),
                    "fe_min_ivf": int(ivf_fe.min()),
                    "fe_max_ivf": int(ivf_fe.max()),
                    "overshoot_ivf": int(ivf_fe.max() - 100000),
                    "n_checkpoints_base": int(len(base_fe)),
                    "fe_min_base": int(base_fe.min()),
                    "fe_max_base": int(base_fe.max()),
                    "overshoot_base": int(base_fe.max() - 100000),
                    "mean_abs_fe_drift": float(drift.mean()),
                    "max_abs_fe_drift": float(drift.max()),
                    "exact_match_pct": float(exact),
                }
            )
    return rows


def write_tex(rows: pd.DataFrame, out_path: Path) -> None:
    empirical = rows[rows["section"] == "empirical"].copy()
    static = rows[rows["section"] == "static"].copy()
    summary = empirical.groupby(["pipeline", "base_algo"], as_index=False).agg(
        n_instance_runs=("run", "count"),
        fe_max_ivf_min=("fe_max_ivf", "min"),
        fe_max_ivf_max=("fe_max_ivf", "max"),
        fe_max_base_min=("fe_max_base", "min"),
        fe_max_base_max=("fe_max_base", "max"),
        mean_abs_fe_drift_mean=("mean_abs_fe_drift", "mean"),
        max_abs_fe_drift_max=("max_abs_fe_drift", "max"),
    )
    merged = summary.merge(
        static[["pipeline", "activation_gate", "mating_budget"]],
        on="pipeline",
        how="left",
    )
    newline = r"\\"
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{FE-accounting audit for the three host-specific IVF pipelines. Static formulas are extracted from the MATLAB implementations; empirical ranges come from the dynamic trace cohort.}",
        "\\label{tab:hosts_fe_audit}",
        "\\scriptsize",
        "\\begin{tabular}{llrrrr}",
        "\\toprule",
        f"Pipeline & Base & IVF max FE range & Base max FE range & Mean |drift| & Max |drift| {newline}",
        "\\midrule",
    ]
    for _, row in merged.iterrows():
        lines.append(
            f"{row['pipeline']} & {row['base_algo']} & "
            f"{int(row['fe_max_ivf_min'])}--{int(row['fe_max_ivf_max'])} & "
            f"{int(row['fe_max_base_min'])}--{int(row['fe_max_base_max'])} & "
            f"{row['mean_abs_fe_drift_mean']:.2f} & {row['max_abs_fe_drift_max']:.0f} {newline}"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print(f"[A1] Reading dynamic traces: {CONV_CSV}")
    conv = pd.read_csv(CONV_CSV)
    print(f"[A1] Loaded {len(conv)} rows across {conv['algo'].nunique()} algorithms")
    rows = build_static_rows()
    rows.extend(build_empirical_rows(conv))
    audit_df = pd.DataFrame(rows).sort_values(
        ["section", "pipeline", "problem", "M", "run"],
        na_position="first",
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "hosts_fe_audit.csv"
    out_tex = OUT_DIR / "hosts_fe_audit.tex"
    audit_df.to_csv(out_csv, index=False)
    write_tex(audit_df, out_tex)
    print(f"[A1] Wrote {out_csv} ({len(audit_df)} rows)")
    print(f"[A1] Wrote {out_tex}")


if __name__ == "__main__":
    main()
