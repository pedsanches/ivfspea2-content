#!/usr/bin/env python3
"""Engineering-transfer table.

External support only, and the weakest evidence family in the document: three
constrained problems, mixed outcomes, and heterogeneous valid-run coverage on
RWMOP8. The caption and note say so, because the counts on their own read
stronger than the evidence is.

The producing pipeline cannot run in a fresh checkout (``data/engineering/`` is
not tracked), so this reads the frozen result artifact.

Writes: results/thesis/tab_engenharia_wtl.tex
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import RESULTS, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

PAIRWISE = RESULTS / "engineering_suite" / "engineering_suite_pairwise_main.csv"
OUT = RESULTS_THESIS / "tab_engenharia_wtl.tex"

# Presentation order follows the manuscript: continuity benchmark first, then
# the two problems selected by the locked screening protocol.
PROBLEM_ORDER = ["RWMOP9", "RWMOP21", "RWMOP8"]


def main() -> int:
    if not PAIRWISE.exists():
        print(f"ERRO: artefato ausente: {PAIRWISE}", file=sys.stderr)
        print(
            "Este artefato está congelado: data/engineering/ não é versionado e o "
            "produtor não roda neste checkout.",
            file=sys.stderr,
        )
        return 1

    pairwise = pd.read_csv(PAIRWISE)
    main_stage = pairwise[pairwise["Stage"] == "MAIN"]

    rows: list[list[str] | object] = []
    for index, problem in enumerate(PROBLEM_ORDER):
        if index:
            rows.append(lt.Rule)
        subset = main_stage[main_stage["Problem"] == problem]
        if subset.empty:
            print(f"ERRO: {problem} ausente do artefato", file=sys.stderr)
            return 1
        objectives = int(subset.iloc[0]["M"])
        for metric_index, metric in enumerate(("IGD", "HV")):
            hit = subset[subset["Metric"] == metric]
            if len(hit) != 1:
                print(
                    f"ERRO: esperava 1 linha para {problem}/{metric}, encontrei {len(hit)}",
                    file=sys.stderr,
                )
                return 1
            row = hit.iloc[0]
            rows.append([
                problem if metric_index == 0 else "",
                str(objectives) if metric_index == 0 else "",
                metric,
                fmt.wtl(row["Plus"], row["Equal"], row["Minus"]),
            ])

    note = (
        "Vitórias/empates/derrotas do IVF/SPEA2 contra cada comparador nos problemas de "
        "engenharia com restrições, sob processamento estrito de execuções comuns. "
        "Esta é evidência de transferência externa, com força inferior à da suíte "
        "sintética e resultados mistos; ela não sustenta a afirmação confirmatória e não "
        "pode ser somada às contagens sintéticas. O RWMOP8 tem cobertura heterogênea de "
        "execuções válidas entre algoritmos, o que reduz ainda mais o peso probatório da "
        "sua linha. Os problemas foram fixados antes da observação dos resultados."
    )

    content = lt.render(
        header=["Problema", "$M$", "Métrica", "V/E/D"],
        rows=rows,
        colspec="|l|c|c|c|",
        caption=(
            "Transferência do IVF/SPEA2 para problemas de engenharia com restrições: "
            "contagens por problema e métrica."
        ),
        label="tab:engenharia_wtl",
        producer=__file__,
        sources=[PAIRWISE],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
