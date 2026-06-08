#!/usr/bin/env python3
"""Build a compact representative IGD endpoint table for the PPSN hosts paper.

Reads the three per-host IGD stats CSVs, selects deterministic representative cases per host
(strongest gain, most neutral tie, and strongest adverse or weakest available case), and writes
`results/tables/hosts_rep_endpoint_igd.csv` plus `results/tables/hosts_rep_endpoint_igd.tex`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
OUT_DIR = PROJECT_ROOT / "results" / "tables"

HOSTS = [
    ("IVFSPEA2", "IVF/SPEA2", OUT_DIR / "hosts_ivfspea2_igd_stats.csv"),
    ("IVFNSGAIII", "IVF/NSGA-III", OUT_DIR / "hosts_ivfnsgaiii_igd_stats.csv"),
    ("IVFNSGAII", "IVF/NSGA-II", OUT_DIR / "hosts_ivfnsgaii_igd_stats.csv"),
]


def ivf_favoring_a12(raw_a12: float) -> float:
    return 1.0 - raw_a12


def fmt_value(value: float) -> str:
    return f"{value:#.3g}"


def fmt_pair(median: float, iqr: float) -> str:
    return f"{fmt_value(median)} [{fmt_value(iqr)}]"


def select_rows(df: pd.DataFrame, host_key: str, host_label: str) -> list[dict]:
    work = df.copy()
    work["a12_ivf"] = work["A12"].apply(ivf_favoring_a12)

    gain = (
        work[work["sign"] == "+"]
        .sort_values(["a12_ivf", "M", "problem"], ascending=[False, True, True])
        .iloc[0]
    )
    neutral = (
        work[work["sign"] == "="]
        .assign(neutral_distance=lambda x: (x["a12_ivf"] - 0.5).abs())
        .sort_values(["neutral_distance", "M", "problem"], ascending=[True, True, True])
        .iloc[0]
    )

    loss_pool = work[work["sign"] == "-"]
    if loss_pool.empty:
        adverse = work.sort_values(["a12_ivf", "M", "problem"], ascending=[True, True, True]).iloc[0]
        adverse_case = "weakest"
    else:
        adverse = loss_pool.sort_values(["a12_ivf", "M", "problem"], ascending=[True, True, True]).iloc[0]
        adverse_case = "adverse"

    rows = []
    for case_label, row in [("gain", gain), ("tie", neutral), (adverse_case, adverse)]:
        rows.append(
            {
                "host": host_key,
                "host_label": host_label,
                "case": case_label,
                "problem": row["problem"],
                "M": int(row["M"]),
                "group": row["group"],
                "median_ivf": float(row["median_ivf"]),
                "iqr_ivf": float(row["iqr_ivf"]),
                "median_base": float(row["median_base"]),
                "iqr_base": float(row["iqr_base"]),
                "sign": row["sign"],
                "a12_ivf": float(row["a12_ivf"]),
            }
        )
    return rows


def write_tex(df: pd.DataFrame, out_path: Path) -> None:
    newline = r"\\"
    case_display = {"gain": "gain", "tie": "neutral", "adverse": "adverse", "weakest": "weakest"}
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Representative IGD endpoint cases per host: strongest significant gain, most neutral case ($A_{12}^{\\mathrm{IVF}}$ closest to 0.5), and strongest adverse case. If a host has no IGD loss, the last row shows its weakest available case. Entries are median [IQR], so each host block can be read directly as gain / neutral / adverse exemplars.}",
        "\\label{tab:rep_endpoint_medians}",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{0pt}",
        "\\renewcommand{\\arraystretch}{1.08}",
        "\\begin{tabular}{@{}l@{\\hspace{0.9em}}l@{\\hspace{0.9em}}l@{\\hspace{1.4em}}r@{\\hspace{1.2em}}r@{}}",
        "\\toprule",
        f"Host & Case & Instance & \\multicolumn{{1}}{{c}}{{IVF}} & \\multicolumn{{1}}{{c}}{{Base}} {newline}",
        "\\midrule",
    ]
    for host_label, group in df.groupby("host_label", sort=False):
        group_rows = list(group.to_dict("records"))
        span = len(group_rows)
        for idx, row in enumerate(group_rows):
            host = f"\\multirow{{{span}}}{{*}}{{{host_label}}}" if idx == 0 else ""
            instance = f"{row['problem']} ($M={int(row['M'])}$)"
            lines.append(
                f"{host} & {case_display[row['case']]} & {instance} & "
                f"{fmt_pair(row['median_ivf'], row['iqr_ivf'])} & "
                f"{fmt_pair(row['median_base'], row['iqr_base'])} {newline}"
            )
        lines.append("\\addlinespace")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows: list[dict] = []
    for host_key, host_label, path in HOSTS:
        print(f"[A6] Reading stats: {path}")
        df = pd.read_csv(path)
        print(f"[A6] Loaded {len(df)} rows for {host_label}")
        rows.extend(select_rows(df, host_key, host_label))

    out_df = pd.DataFrame(rows)
    case_order = {"gain": 0, "tie": 1, "adverse": 2, "weakest": 2}
    host_order = {"IVFSPEA2": 0, "IVFNSGAIII": 1, "IVFNSGAII": 2}
    out_df = out_df.sort_values(
        by=["host", "case", "M", "problem"],
        key=lambda col: col.map(host_order if col.name == "host" else case_order if col.name == "case" else {}) if col.name in {"host", "case"} else col,
    ).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / "hosts_rep_endpoint_igd.csv"
    out_tex = OUT_DIR / "hosts_rep_endpoint_igd.tex"
    out_df.to_csv(out_csv, index=False)
    write_tex(out_df, out_tex)
    print(f"[A6] Wrote {out_csv} ({len(out_df)} rows)")
    print(f"[A6] Wrote {out_tex}")


if __name__ == "__main__":
    main()
