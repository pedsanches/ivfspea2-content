#!/usr/bin/env python3
"""Build a parameter-provenance audit for the IVF host comparison paper.

Reads the MATLAB IVF host implementations and the current PPSN manuscript, extracts the default
parameter values declared in code and text, compares them parameter-by-parameter, and writes
`results/tables/hosts_parameter_provenance.csv` and `results/tables/hosts_parameter_provenance.tex`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUT_DIR = PROJECT_ROOT / "results" / "tables"
MAIN_TEX = PROJECT_ROOT / "paper" / "ppsn2026-ivf-hosts" / "main.tex"

FILES = {
    "IVFSPEA2": PROJECT_ROOT
    / "src"
    / "matlab"
    / "lib"
    / "PlatEMO"
    / "Algorithms"
    / "Multi-objective optimization"
    / "IVF-SPEA2-V2"
    / "IVFSPEA2V2.m",
    "IVFNSGAII": PROJECT_ROOT
    / "src"
    / "matlab"
    / "lib"
    / "PlatEMO"
    / "Algorithms"
    / "Multi-objective optimization"
    / "IVF-NSGA-II"
    / "IVFNSGAII.m",
    "IVFNSGAIII": PROJECT_ROOT
    / "src"
    / "matlab"
    / "lib"
    / "PlatEMO"
    / "Algorithms"
    / "Multi-objective optimization"
    / "IVF-NSGA-III"
    / "IVFNSGAIII.m",
}


def extract_code_defaults(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"ParameterSet\(([^\)]*)\)", text)
    if not match:
        raise ValueError(f"Could not find ParameterSet(...) in {path}")
    values = [token.strip() for token in match.group(1).split(",")]
    if path.name == "IVFSPEA2V2.m":
        names = ["C", "R", "M_mut", "V", "Cycles", "N_Offspring", "EARN"]
    elif path.name == "IVFNSGAII.m":
        names = ["R", "C", "Cycles"]
    else:
        names = ["ivf_rate", "C", "Cycles"]
    return dict(zip(names, values, strict=True))


def extract_text_defaults(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    line = next(
        candidate
        for candidate in text.splitlines()
        if "No additional instance-wise retuning" in candidate
    )
    patterns = {
        "IVFSPEA2": r"IVF/SPEA2 v2 used \$C=([0-9.]+)\$, \$R=([0-9.]+)\$, \$M_\{\\mathrm\{mut\}\}=([0-9.]+)\$, \$V=([0-9.]+)\$, and \\textit\{Cycles\}=([0-9]+)",
        "IVFNSGAII": r"IVF/NSGA-II used \$R=([0-9.]+)\$, \$C=([0-9.]+)\$, and \\textit\{Cycles\}=([0-9]+)",
        "IVFNSGAIII": r"IVF/NSGA-III used \\textit\{ivf\\_rate\}=([0-9.]+), \$C=([0-9.]+)\$, and \\textit\{Cycles\}=([0-9]+)",
    }
    out: dict[str, dict[str, str]] = {}
    m_spea2 = re.search(patterns["IVFSPEA2"], line)
    m_nsgaii = re.search(patterns["IVFNSGAII"], line)
    m_nsgaiii = re.search(patterns["IVFNSGAIII"], line)
    if not all([m_spea2, m_nsgaii, m_nsgaiii]):
        raise ValueError("Could not parse parameter-provenance line in main.tex")
    out["IVFSPEA2"] = {
        "C": m_spea2.group(1),
        "R": m_spea2.group(2),
        "M_mut": m_spea2.group(3),
        "V": m_spea2.group(4),
        "Cycles": m_spea2.group(5),
    }
    out["IVFNSGAII"] = {
        "R": m_nsgaii.group(1),
        "C": m_nsgaii.group(2),
        "Cycles": m_nsgaii.group(3),
    }
    out["IVFNSGAIII"] = {
        "ivf_rate": m_nsgaiii.group(1),
        "C": m_nsgaiii.group(2),
        "Cycles": m_nsgaiii.group(3),
    }
    return out


def compare_values(code_value: str | None, text_value: str | None) -> str:
    if code_value is None and text_value is None:
        return "missing-both"
    if code_value is None:
        return "text-only"
    if text_value is None:
        return "code-only"
    return "match" if str(code_value) == str(text_value) else "mismatch"


def write_tex(df: pd.DataFrame, out_path: Path) -> None:
    newline = r"\\"
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Parameter provenance audit comparing the values reported in the manuscript against the defaults extracted from the current MATLAB implementations.}",
        "\\label{tab:hosts_parameter_provenance}",
        "\\scriptsize",
        "\\begin{tabular}{llccc}",
        "\\toprule",
        f"Pipeline & Parameter & Code & Text & Status {newline}",
        "\\midrule",
    ]
    for _, row in df.iterrows():
        text_value = row["text_value"] if pd.notna(row["text_value"]) else ""
        lines.append(
            f"{row['pipeline']} & {row['parameter']} & {row['code_value']} & {text_value} & {row['status']} {newline}"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print(f"[A4] Reading manuscript: {MAIN_TEX}")
    text_defaults = extract_text_defaults(MAIN_TEX)

    rows: list[dict] = []
    for pipeline, path in FILES.items():
        print(f"[A4] Reading code defaults: {path}")
        code_defaults = extract_code_defaults(path)
        params = sorted(set(code_defaults) | set(text_defaults.get(pipeline, {})))
        for param in params:
            code_value = code_defaults.get(param)
            text_value = text_defaults.get(pipeline, {}).get(param)
            rows.append(
                {
                    "pipeline": pipeline,
                    "parameter": param,
                    "code_value": code_value,
                    "text_value": text_value,
                    "status": compare_values(code_value, text_value),
                    "code_file": path.name,
                }
            )

    df = (
        pd.DataFrame(rows).sort_values(["pipeline", "parameter"]).reset_index(drop=True)
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "hosts_parameter_provenance.csv"
    out_tex = OUT_DIR / "hosts_parameter_provenance.tex"
    df.to_csv(out_csv, index=False)
    write_tex(df, out_tex)
    print(f"[A4] Wrote {out_csv} ({len(df)} rows)")
    print(f"[A4] Wrote {out_tex}")


if __name__ == "__main__":
    main()
