#!/usr/bin/env python3
"""Warmup-controller comparison table.

HV is the declared primary endpoint here, not IGD. The instance labels were
derived from the confirmatory IGD outcome, so scoring the controller on IGD
would reuse the labels as their own validation. The table therefore leads with
HV and reports IGD as secondary.

Writes: results/thesis/tab_controlador_wtl.tex
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

# Frozen out-of-sample artifact named in data-sources.toml. The undated
# data/processed/ppsn_controller_comparison.csv is an earlier run and must not
# be substituted for it.
WTL = RESULTS_TABLES / "controller_wtl_oos_20260326_221909.csv"
OUT = RESULTS_THESIS / "tab_controlador_wtl.tex"

COMPARISON_LABEL = {
    "CTRL vs SPEA2": "Controlador contra SPEA2",
    "CTRL vs IVF-SPEA2": "Controlador contra IVF/SPEA2 sempre ativo",
}
COMPARISON_ORDER = ["CTRL vs SPEA2", "CTRL vs IVF-SPEA2"]

LABEL_LABEL = {
    "ALL": "Todas",
    "HELPS": "O operador ajuda",
    "NOT_HELPS": "O operador não ajuda",
}
LABEL_ORDER = ["ALL", "HELPS", "NOT_HELPS"]


def main() -> int:
    if not WTL.exists():
        print(f"ERRO: artefato ausente: {WTL}", file=sys.stderr)
        return 1

    table = pd.read_csv(WTL)

    rows: list[list[str] | object] = []
    for metric_index, metric in enumerate(("HV", "IGD")):
        if metric_index:
            rows.append(lt.Rule)
        block = table[table["metric"] == metric]
        first_in_metric = True
        for comparison in COMPARISON_ORDER:
            for label in LABEL_ORDER:
                hit = block[
                    (block["comparison"] == comparison) & (block["label"] == label)
                ]
                if len(hit) != 1:
                    print(
                        f"AVISO: {metric}/{comparison}/{label}: {len(hit)} linhas; omitida",
                        file=sys.stderr,
                    )
                    continue
                row = hit.iloc[0]
                rows.append([
                    metric if first_in_metric else "",
                    COMPARISON_LABEL[comparison] if label == "ALL" else "",
                    LABEL_LABEL[label],
                    str(int(row["n_cases"])),
                    fmt.wtl(row["wins"], row["ties"], row["losses"]),
                    str(int(row["match_or_beat"])),
                ])
                first_in_metric = False

    note = (
        "Controlador de aquecimento: o operador é desativado de forma irreversível quando "
        "a renovação do arquivo na fase inicial fica abaixo do limiar da família. "
        "Wilcoxon pareado com correção de Benjamini--Hochberg sobre 30 execuções pareadas "
        "por semente. A coluna final conta as instâncias em que o controlador iguala ou "
        "supera o comparador. O HV é o desfecho primário declarado desta avaliação: os "
        "rótulos de instância foram derivados do desfecho confirmatório em IGD, de modo "
        "que pontuar o controlador em IGD reutilizaria os rótulos como sua própria "
        "validação. O ganho do controlador é eliminar as perdas onde o operador não ajuda, "
        "ao custo de abrir mão de ganhos onde ele ajuda."
    )

    content = lt.render(
        header=[
            "Métrica", "Comparação", "Subconjunto", "$n$", "V/E/D", "Iguala ou supera",
        ],
        rows=rows,
        colspec="|c|l|l|c|c|c|",
        caption=(
            "Controlador de aquecimento frente ao SPEA2 canônico e ao IVF/SPEA2 sempre "
            "ativo, por subconjunto de instâncias."
        ),
        label="tab:controlador_wtl",
        resize=True,
        producer=__file__,
        sources=[WTL],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
