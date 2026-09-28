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
FACTORIAL = RESULTS / "ablation_v2" / "phase2" / "phase2_summary.json"

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

# Configuration the final ablation phase ran at, from its batch script
# (scripts/experiments/run_ablation_v2_phase3_batch_common.m, lines 81 and 94-98).
# The artifact does not record it, and it is *not* the promoted configuration
# evaluated in the confirmatory chapter, so the note must say so.
ABLATION_RUNS = 60
ABLATION_CONFIG = (
    "$c = 0{,}11$, $r = 0{,}10$, $m = 0$, $v = 0$, $\\ell = 3$"
)


METRICS = ("igd", "hv")


def build_tuning() -> str | None:
    if not TUNING.exists():
        print(f"ERRO: artefato ausente: {TUNING}", file=sys.stderr)
        return None
    summary = json.loads(TUNING.read_text(encoding="utf-8"))

    # One row per compared pair, one column per metric: the reader compares
    # IGD and HV of the same pair side by side.
    counts: dict[str, dict[str, str]] = {}
    for metric_key in METRICS:
        for entry in summary[metric_key]:
            pair = entry["pair"]
            if pair not in PAIR_LABEL:
                print(f"AVISO: par desconhecido no artefato: {pair}", file=sys.stderr)
                continue
            counts.setdefault(pair, {})[metric_key] = fmt.wtl(
                entry["wins"], entry["ties"], entry["losses"]
            )

    rows: list[list[str] | object] = []
    for pair, (left, right) in PAIR_LABEL.items():
        missing = [m for m in METRICS if m not in counts.get(pair, {})]
        if missing:
            print(f"ERRO: par {pair} sem {', '.join(missing)} no artefato", file=sys.stderr)
            return None
        rows.append([left, right, *(counts[pair][m] for m in METRICS)])

    n_problems = len(summary["problems"])
    coverage = summary["coverage"]
    n_promoted = coverage["C26"]["min_runs_per_problem"]
    n_phase_a = coverage["A43"]["min_runs_per_problem"]
    n_historical = coverage["IVFSPEA2v1"]["min_runs_per_problem"]
    if any(
        coverage[key]["max_runs_per_problem"] != n
        for key, n in (("C26", n_promoted), ("A43", n_phase_a), ("IVFSPEA2v1", n_historical))
    ):
        print("ERRO: cobertura desigual entre problemas na calibração", file=sys.stderr)
        return None
    note = (
        "Vitórias/empates/derrotas (V/E/D) da configuração da linha contra o comparador, nas "
        f"{n_problems} configurações problema--objetivo do subconjunto de calibração. "
        f"A configuração promovida tem {n_promoted} execuções por problema e a melhor da fase A, "
        f"{n_phase_a}, sob 50.000 avaliações; o comparador histórico não ajustado tem "
        f"{n_historical} execuções por problema. O orçamento desse braço não consta do "
        "artefato desta comparação. Teste de Mann--Whitney com correção de Holm, "
        "$\\alpha = 0{,}05$. Fase A: a primeira das três fases da calibração "
        "(Seção~\\ref{sec:calibracao}). O contraste contra o braço histórico não isola "
        "apenas o efeito dos parâmetros."
    )

    return lt.render(
        # "V/E/D" once, over both metrics: with it in each header the metric
        # columns grew wide enough to break the configuration names in two.
        header=[
            [lt.Span("", 2), lt.Span("V/E/D", 2)],
            ["Configuração", "Comparador", "IGD", "HV"],
        ],
        rows=rows,
        colspec="llcc",
        caption=(
            "Calibração de parâmetros: a configuração promovida frente à melhor "
            "configuração da fase inicial e à configuração inicial não ajustada."
        ),
        label="tab:tuning_c26",
        producer=__file__,
        sources=[TUNING],
        note=note,
    )


def build_ablation() -> str | None:
    missing = [path for path in (ABLATION, FACTORIAL) if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return None
    summary = json.loads(ABLATION.read_text(encoding="utf-8"))
    factorial = json.loads(FACTORIAL.read_text(encoding="utf-8"))

    # The final phase must carry the factorial winner: the note describes that
    # variant as the one with both coupling decisions and no other factor.
    winner = factorial["winner"]
    expected_flags = {"H1": 1, "H2": 1, "H3": 0, "H4": 0}
    if not summary["winner"].endswith(winner["config_id"]) or any(
        int(winner[flag]) != value for flag, value in expected_flags.items()
    ):
        print(
            f"ERRO: vencedor fatorial {winner!r} não corresponde à fase final "
            f"({summary['winner']!r})",
            file=sys.stderr,
        )
        return None
    n_combinations = len(factorial["ranking"])
    friedman_p = float(factorial["friedman"]["p_value"])

    # SPEA2 first, as in the caption and in the text that reads the table.
    baselines = ["SPEA2", "IVFSPEA2"]
    if sorted(summary["baselines"]) != sorted(baselines):
        print(f"ERRO: comparadores inesperados: {summary['baselines']!r}", file=sys.stderr)
        return None

    rows: list[list[str] | object] = []
    for baseline in baselines:
        cells = [BASELINE_LABEL[baseline]]
        for metric in ("IGD", "HV"):
            stats = summary.get(metric, {}).get(baseline)
            if stats is None:
                print(f"ERRO: {metric}/{baseline} ausente do artefato", file=sys.stderr)
                return None
            # The artifact's "significant" column counts differences in either
            # direction, which is wins plus losses: the table prints only V/E/D.
            if int(stats["significant"]) != int(stats["wins"]) + int(stats["losses"]):
                print(
                    f"ERRO: {metric}/{baseline}: significativas != vitórias + derrotas",
                    file=sys.stderr,
                )
                return None
            cells.append(fmt.wtl(stats["wins"], stats["ties"], stats["losses"]))
        rows.append(cells)

    n_instances = int(summary["n_instances"])
    alpha = fmt.decimal(float(summary["alpha"]), places=2)
    note = (
        "Fase final da ablação fatorial: vitórias/empates/derrotas (V/E/D) da variante com as "
        f"duas decisões de acoplamento contra cada comparador, nas {n_instances} instâncias "
        f"sintéticas, {ABLATION_RUNS} execuções, teste de Mann--Whitney com correção de Holm, "
        f"$\\alpha = {alpha.strip('$')}$. A variante foi a de melhor posto médio entre as "
        f"{n_combinations} combinações da fase fatorial, que não se distinguiram entre si "
        f"(Friedman, $p = {fmt.decimal(friedman_p).strip('$')}$). Limites do desenho: a ablação "
        f"foi executada na configuração inicial não ajustada ({ABLATION_CONFIG}), e não na "
        "configuração promovida avaliada no Capítulo~\\ref{sec:results}; o comparador sem as "
        "duas decisões corresponde às execuções 1--60 da formulação anterior presentes na base "
        "consolidada, produzidas em outra campanha. Evidência de justificativa da "
        "implementação, não da comparação principal."
    )

    return lt.render(
        header=[
            [lt.Span("", 1), lt.Span("V/E/D", 2)],
            ["Comparador", "IGD", "HV"],
        ],
        rows=rows,
        colspec="lcc",
        caption=(
            "Ablação na configuração inicial não ajustada: a variante com seleção de pai "
            "dissimilar e continuação coletiva frente ao SPEA2 canônico e à formulação sem "
            "as duas decisões."
        ),
        label="tab:ablacao",
        producer=__file__,
        sources=[ABLATION, FACTORIAL],
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
