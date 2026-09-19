#!/usr/bin/env python3
"""Configuration and ablation tables.

Both evidence blocks compare against the earlier formulation of the operator.
Per the author's decision recorded in ``thesis/masters/REWRITE_SPEC.md`` §1.3,
the dissertation never labels that comparison by version number. It is named by
what actually differs:

  * the tuning baseline is the *configuração inicial não ajustada* inherited
    from the IVF literature, not "the previous version";
  * the ablation contrast is the variant *without dissimilar-father selection
    and without collective cycle continuation*, which is what the factorial
    harness actually removed.

The artifacts still carry the old identifier internally (``IVFSPEA2v1`` in the
tuning JSON, ``IVFSPEA2`` in the ablation JSON); the mapping to prose labels is
declared in ``BASELINE_LABEL`` below and applied on the way out.

Writes: results/thesis/tab_tuning_c26.tex
        results/thesis/tab_ablacao.tex
"""

from __future__ import annotations

import json
import sys

from ivfspea2.paths import RESULTS, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

TUNING = RESULTS / "tuning_ivfspea2v2" / "head_to_head_c26_a43_v1_summary.json"
ABLATION = RESULTS / "ablation_v2" / "phase3" / "phase3_summary.json"

OUT_TUNING = RESULTS_THESIS / "tab_tuning_c26.tex"
OUT_ABLATION = RESULTS_THESIS / "tab_ablacao.tex"

# Artifact identifier -> how the dissertation names it. Never a version number.
BASELINE_LABEL = {
    "IVFSPEA2v1": "Configuração inicial não ajustada",
    "IVFSPEA2": "Sem pai dissimilar e sem continuação coletiva",
    "SPEA2": "SPEA2 canônico",
}

PAIR_LABEL = {
    "C26_vs_A43": ("Configuração promovida", "Melhor configuração da fase A"),
    "C26_vs_IVFSPEA2v1": ("Configuração promovida", BASELINE_LABEL["IVFSPEA2v1"]),
    "A43_vs_IVFSPEA2v1": ("Melhor configuração da fase A", BASELINE_LABEL["IVFSPEA2v1"]),
}


def build_tuning() -> str | None:
    if not TUNING.exists():
        print(f"ERRO: artefato ausente: {TUNING}", file=sys.stderr)
        return None
    summary = json.loads(TUNING.read_text(encoding="utf-8"))

    rows: list[list[str] | object] = []
    for index, metric_key in enumerate(("igd", "hv")):
        if index:
            rows.append(lt.Rule)
        for entry_index, entry in enumerate(summary[metric_key]):
            pair = entry["pair"]
            if pair not in PAIR_LABEL:
                print(f"AVISO: par desconhecido no artefato: {pair}", file=sys.stderr)
                continue
            left, right = PAIR_LABEL[pair]
            rows.append([
                metric_key.upper() if entry_index == 0 else "",
                left,
                right,
                fmt.wtl(entry["wins"], entry["ties"], entry["losses"]),
            ])

    n_problems = len(summary["problems"])
    note = (
        f"Comparações par a par sobre as {n_problems} configurações problema--objetivo do "
        "subconjunto de calibração, 30 execuções cada, orçamento de 50.000 avaliações. "
        "Teste de Mann--Whitney com correção de Holm, $\\alpha = 0{,}05$. A configuração "
        "promovida não é distinguível da melhor configuração da fase A em nenhuma "
        "instância, e ambas superam a configuração inicial não ajustada em quatro delas: "
        "a calibração escolhe entre configurações equivalentes sem introduzir perda. "
        "Esta é evidência de justificativa da implementação, não da comparação principal."
    )

    return lt.render(
        header=["Métrica", "Configuração", "Comparador", "V/E/D"],
        rows=rows,
        colspec="|c|l|l|c|",
        caption=(
            "Calibração de parâmetros: a configuração promovida frente à melhor "
            "configuração da fase inicial e à configuração inicial não ajustada."
        ),
        label="tab:tuning_c26",
        resize=True,
        producer=__file__,
        sources=[TUNING],
        note=note,
    )


def build_ablation() -> str | None:
    if not ABLATION.exists():
        print(f"ERRO: artefato ausente: {ABLATION}", file=sys.stderr)
        return None
    summary = json.loads(ABLATION.read_text(encoding="utf-8"))

    rows: list[list[str] | object] = []
    for index, metric in enumerate(("IGD", "HV")):
        if index:
            rows.append(lt.Rule)
        block = summary.get(metric, {})
        for baseline_index, baseline in enumerate(summary["baselines"]):
            stats = block.get(baseline)
            if stats is None:
                print(f"AVISO: {metric}/{baseline} ausente do artefato", file=sys.stderr)
                continue
            rows.append([
                metric if baseline_index == 0 else "",
                BASELINE_LABEL.get(baseline, baseline),
                fmt.wtl(stats["wins"], stats["ties"], stats["losses"]),
                str(int(stats["significant"])),
            ])

    n_instances = int(summary["n_instances"])
    note = (
        f"Acoplamento completo contra cada comparador nas {n_instances} instâncias "
        "sintéticas, $\\alpha = {}$. A coluna final conta as instâncias com diferença "
        "significativa em qualquer direção. O acoplamento completo supera o SPEA2 "
        "canônico em metade da suíte, mas não se distingue da variante sem as duas "
        "decisões de acoplamento: o ganho vem da estrutura de interação entre elas e não "
        "de um efeito isolado de cada uma. Evidência de justificativa da implementação."
    ).format(fmt.decimal(float(summary["alpha"]), places=2).strip("$"))

    return lt.render(
        header=["Métrica", "Comparador", "V/E/D", "Significativas"],
        rows=rows,
        colspec="|c|l|c|c|",
        caption=(
            "Ablação fatorial: o acoplamento completo frente ao SPEA2 canônico e à "
            "variante sem seleção de pai dissimilar e sem continuação coletiva."
        ),
        label="tab:ablacao",
        producer=__file__,
        sources=[ABLATION],
        note=note,
    )


def main() -> int:
    failed = False
    for content, path in ((build_tuning(), OUT_TUNING), (build_ablation(), OUT_ABLATION)):
        if content is None:
            failed = True
            continue
        lt.write(path, content)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
