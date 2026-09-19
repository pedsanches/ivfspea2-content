#!/usr/bin/env python3
"""Confirmatory win/tie/loss table for the results chapter.

Reads the Holm-corrected audit produced by
``src/python/analysis/compute_claims_summary.py``. That audit is the only
artifact allowed to back Holm-corrected counting language: the per-instance
generators run uncorrected tests and are descriptive only.

Writes: results/thesis/tab_confirmatorio_wtl.tex
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

AUDIT = RESULTS_TABLES / "claims_summary_audit.csv"
OUT = RESULTS_THESIS / "tab_confirmatorio_wtl.tex"

# Display order, and how each audit condition is named in Portuguese.
CONDITIONS = [
    ("unadjusted", "Sem correção", "Suíte completa"),
    ("unadjusted_OOS", "Sem correção", "Fora do ajuste"),
    ("Holm", "Holm", "Suíte completa"),
    ("Holm_OOS", "Holm", "Fora do ajuste"),
]

METRICS = [("IGD", "IGD"), ("HV", "HV")]


def main() -> int:
    if not AUDIT.exists():
        print(f"ERRO: artefato ausente: {AUDIT}", file=sys.stderr)
        print("Regenere com: .venv/bin/python src/python/analysis/compute_claims_summary.py", file=sys.stderr)
        return 1

    audit = pd.read_csv(AUDIT)

    rows: list[list[str] | object] = []
    for m_index, (metric, metric_label) in enumerate(METRICS):
        if m_index:
            rows.append(lt.Rule)
        for cond_index, (condition, correction, scope) in enumerate(CONDITIONS):
            # The metric name is printed once per block; the rule between
            # blocks is what separates them visually.
            cells = [metric_label if cond_index == 0 else "", correction, scope]
            for objectives in ("M2", "M3"):
                hit = audit[
                    (audit["metric"] == metric)
                    & (audit["condition"] == condition)
                    & (audit["M"] == objectives)
                ]
                if len(hit) != 1:
                    print(
                        f"ERRO: esperava 1 linha para {metric}/{condition}/{objectives}, "
                        f"encontrei {len(hit)}",
                        file=sys.stderr,
                    )
                    return 1
                row = hit.iloc[0]
                cells.append(fmt.wtl(row["wins"], row["ties"], row["losses"]))
                cells.append(str(int(row["n"])))
            rows.append(cells)

    note = (
        "Contagens de vitórias/empates/derrotas do IVF/SPEA2 contra o SPEA2 canônico. "
        "Teste bicaudal de Mann--Whitney, $\\alpha = 0{,}05$, correção de Holm aplicada "
        "separadamente por número de objetivos e por métrica. IGD: menor é melhor; "
        "HV: maior é melhor. Coorte: execuções 3001--3060 contra 1--60, 60 execuções por "
        "configuração, orçamento de 100.000 avaliações. O recorte fora do ajuste exclui "
        "as 12 instâncias usadas na calibração e é obtido após a correção da família completa."
    )

    content = lt.render(
        header=[
            "Métrica", "Correção", "Escopo",
            "$M=2$ (V/E/D)", "$n$", "$M=3$ (V/E/D)", "$n$",
        ],
        rows=rows,
        colspec="|l|l|l|c|c|c|c|",
        caption=(
            "Desempenho do IVF/SPEA2 em relação ao SPEA2 canônico na suíte sintética, "
            "por métrica, correção de multiplicidade e escopo de instâncias."
        ),
        label="tab:confirmatorio_wtl",
        producer=__file__,
        sources=[AUDIT],
        note=note,
        # Seven columns overrun the thesis text block by a few points at full
        # size; scaling to the block keeps it inside the margin.
        resize=True,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
