#!/usr/bin/env python3
"""Confirmatory win/tie/loss table for the results chapter.

Reads the Holm-corrected audit produced by
``src/python/analysis/compute_claims_summary.py``. That audit is the only
artifact allowed to back Holm-corrected counting language: the per-instance
generators run uncorrected tests and are descriptive only.

Layout: one row per instance scope and number of objectives, one column per
metric and correction level. The uncorrected and Holm counts of a metric sit
side by side, which is the comparison the text makes, and ``n`` appears once
per row: it depends on the scope and on ``M``, never on metric or correction,
and the builder fails if the audit says otherwise.

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

# Row blocks: audit-condition suffix and the scope's name in Portuguese.
SCOPES = [("", "Suíte completa"), ("_OOS", "Fora do ajuste")]
OBJECTIVES = [("M2", "2"), ("M3", "3")]
METRICS = ["IGD", "HV"]
# Column order inside each metric: audit-condition prefix, header label.
CORRECTIONS = [("unadjusted", "Sem correção"), ("Holm", "Holm")]


def main() -> int:
    if not AUDIT.exists():
        print(f"ERRO: artefato ausente: {AUDIT}", file=sys.stderr)
        print("Regenere com: .venv/bin/python src/python/analysis/compute_claims_summary.py", file=sys.stderr)
        return 1

    audit = pd.read_csv(AUDIT)

    rows: list[list[str] | object] = []
    for scope_index, (suffix, scope) in enumerate(SCOPES):
        if scope_index:
            rows.append(lt.Rule)
        for objectives_index, (objectives, m_label) in enumerate(OBJECTIVES):
            counts: list[str] = []
            sizes: set[int] = set()
            for metric in METRICS:
                for prefix, _ in CORRECTIONS:
                    condition = f"{prefix}{suffix}"
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
                    counts.append(fmt.wtl(row["wins"], row["ties"], row["losses"]))
                    sizes.add(int(row["n"]))
            if len(sizes) != 1:
                print(
                    f"ERRO: {scope}/{objectives}: n difere entre métricas e correções: {sorted(sizes)}",
                    file=sys.stderr,
                )
                return 1
            # The scope is printed once per block; the rule between blocks
            # is what separates them visually.
            label = scope if objectives_index == 0 else ""
            rows.append([label, m_label, str(sizes.pop()), *counts])

    note = (
        "V/E/D: vitórias/empates/derrotas do IVF/SPEA2 contra o SPEA2 canônico; $n$: número "
        "de instâncias do escopo. Teste bicaudal de Mann--Whitney, $\\alpha = 0{,}05$; a "
        "correção de Holm é aplicada separadamente por número de objetivos e por métrica. "
        "IGD: menor é melhor; HV: maior é melhor. Coorte: execuções 3001--3060 contra 1--60, "
        "60 execuções por configuração, orçamento de 100.000 avaliações. O recorte fora do "
        "ajuste exclui as 12 instâncias usadas na calibração e é obtido após a correção da "
        "família completa; ele inclui o MaF7 com $M = 3$, mesma função do DTLZ7 com $M = 3$, "
        "usado na calibração (Seção~\\ref{sec:suites})."
    )

    corrections = [label for _, label in CORRECTIONS]
    content = lt.render(
        header=[
            [lt.Span("", 3), *(lt.Span(f"{metric} (V/E/D)", 2) for metric in METRICS)],
            ["Escopo", "$M$", "$n$", *corrections * len(METRICS)],
        ],
        rows=rows,
        colspec="lcc" + "c" * (len(METRICS) * len(CORRECTIONS)),
        caption=(
            "Desempenho do IVF/SPEA2 em relação ao SPEA2 canônico na suíte sintética, "
            "por escopo de instâncias, número de objetivos, métrica e correção de "
            "multiplicidade."
        ),
        label="tab:confirmatorio_wtl",
        producer=__file__,
        sources=[AUDIT],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
