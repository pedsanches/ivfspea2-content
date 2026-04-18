#!/usr/bin/env python3
"""Apply Benjamini--Hochberg correction to the ECDF KS-test table.

Reads `results/tables/ecdf_significance.csv`, applies BH correction over the full ECDF block,
adds `p_adj` and `significant_bh`, and writes the updated CSV plus
`results/tables/ecdf_significance_bh.tex`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from statsmodels.stats.multitest import multipletests


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CSV_PATH = PROJECT_ROOT / "results" / "tables" / "ecdf_significance.csv"
OUT_TEX = PROJECT_ROOT / "results" / "tables" / "ecdf_significance_bh.tex"


def write_tex(df: pd.DataFrame, out_path: Path) -> None:
    sig = df[df["significant_bh"]].copy()
    newline = r"\\"
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{BH-significant ECDF differences in the dynamic block.}",
        "\\label{tab:ecdf_bh}",
        "\\scriptsize",
        "\\begin{tabular}{llrr}",
        "\\toprule",
        f"Instance & Pair & $p$ & $p_{{\\mathrm{{adj}}}}$ {newline}",
        "\\midrule",
    ]
    if sig.empty:
        lines.append(
            f"\\multicolumn{{4}}{{c}}{{No BH-significant ECDF differences.}} {newline}"
        )
    else:
        for _, row in sig.iterrows():
            label = f"{row['problem']} ($M={int(row['M'])}$)"
            pair = f"{row['ivf_algo']} vs {row['base_algo']}"
            lines.append(
                f"{label} & {pair} & {row['p_value']:.3g} & {row['p_adj']:.3g} {newline}"
            )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    print(f"[A3] Reading ECDF table: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"[A3] Loaded {len(df)} rows")
    p_adj = multipletests(df["p_value"].to_numpy(dtype=float), method="fdr_bh")[1]
    df["p_adj"] = p_adj
    df["significant_bh"] = df["p_adj"] < 0.05
    df.to_csv(CSV_PATH, index=False)
    write_tex(df, OUT_TEX)
    print(f"[A3] Wrote {CSV_PATH} ({len(df)} rows)")
    print(f"[A3] Wrote {OUT_TEX}")


if __name__ == "__main__":
    main()
