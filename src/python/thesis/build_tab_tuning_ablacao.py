#!/usr/bin/env python3
"""Ablation and calibration comparisons, in one table.

The two studies are presented in the order in which they fixed the coupling:
the ablation chose which coupling decisions stay, then the calibration fixed
the parameters, and the configuration it produced became the default
configuration of the IVF/SPEA2 (``configuração padrão``). Each study is a
group of rows headed by the arm it evaluates; each row names one comparator.

Per the author's decision recorded in ``thesis/masters/REWRITE_SPEC.md`` §1.3,
the dissertation never labels a comparison by version number. Arms are named
by what differs: the ablation compares the coupling *with* both decisions
(dissimilar primary-donor selection and collective cycle continuation) to the
coupling *without* them; the calibration compares the default configuration
(``C26``) to the best configuration of phase A (``A43``).

The calibration artifact also carries contrasts against an earlier arm with
60 runs whose budget and configuration are not recorded (``IVFSPEA2v1`` in
the JSON). By the author's decision of 2026-10-11 those contrasts left the
dissertation; this generator reads only the ``C26_vs_A43`` pair.

Writes: results/thesis/tab_ablacao.tex
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

OUT = RESULTS_THESIS / "tab_ablacao.tex"

# Artifact identifier -> how the dissertation names the comparator.
ABLATION_COMPARATORS = {
    "SPEA2": "SPEA2",
    "IVFSPEA2": "Acoplamento sem as duas decisões",
}
TUNING_PAIR = "C26_vs_A43"
TUNING_COMPARATOR = "Melhor configuração da fase A"

# Runs and budgets from the batch scripts, which the summaries do not record:
# scripts/experiments/run_ablation_v2_phase3_batch_common.m (lines 81-82 and
# 94-98) and scripts/experiments/run_ivfspea2v2_tuning.m (lines 60-61).
ABLATION_RUNS = 60
ABLATION_BUDGET = 100_000
TUNING_BUDGET = 50_000
INITIAL_CONFIG = "$c = 0{,}11$, $r = 0{,}10$, $m = 0$, $v = 0$, $\\ell = 3$"

METRICS = (("IGD", "igd"), ("HV", "hv"))
NCOLS = 5


def _ablation_rows() -> list[list[str]] | None:
    missing = [path for path in (ABLATION, FACTORIAL) if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return None
    summary = json.loads(ABLATION.read_text(encoding="utf-8"))
    factorial = json.loads(FACTORIAL.read_text(encoding="utf-8"))

    # The final phase must carry the factorial winner: the table names that
    # variant as the coupling with both decisions and no other factor.
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
    if sorted(summary["baselines"]) != sorted(ABLATION_COMPARATORS):
        print(f"ERRO: comparadores inesperados: {summary['baselines']!r}", file=sys.stderr)
        return None

    n_instances = int(summary["n_instances"])
    rows: list[list[str]] = []
    for baseline, label in ABLATION_COMPARATORS.items():
        cells = [label, str(n_instances), str(ABLATION_RUNS)]
        for metric, _key in METRICS:
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
    return rows


def _tuning_row() -> list[str] | None:
    if not TUNING.exists():
        print(f"ERRO: artefato ausente: {TUNING}", file=sys.stderr)
        return None
    summary = json.loads(TUNING.read_text(encoding="utf-8"))

    coverage = summary["coverage"]
    runs = {key: coverage[key]["min_runs_per_problem"] for key in ("C26", "A43")}
    if any(coverage[key]["max_runs_per_problem"] != n for key, n in runs.items()):
        print("ERRO: cobertura desigual entre problemas na calibração", file=sys.stderr)
        return None
    if runs["C26"] != runs["A43"]:
        print(f"ERRO: execuções diferentes entre C26 e A43: {runs!r}", file=sys.stderr)
        return None

    cells = [TUNING_COMPARATOR, str(len(summary["problems"])), str(runs["C26"])]
    for _metric, key in METRICS:
        entry = next((e for e in summary[key] if e["pair"] == TUNING_PAIR), None)
        if entry is None:
            print(f"ERRO: par {TUNING_PAIR} sem {key} no artefato", file=sys.stderr)
            return None
        cells.append(fmt.wtl(entry["wins"], entry["ties"], entry["losses"]))
    return cells


def build() -> str | None:
    ablation = _ablation_rows()
    tuning = _tuning_row()
    if ablation is None or tuning is None:
        return None

    rows: list[list[str | lt.Span] | object] = [
        [
            lt.Span(
                "\\textit{Ablação (avaliado: acoplamento com as duas decisões, na "
                "configuração inicial)}",
                NCOLS,
                "l",
            )
        ],
        *ablation,
        lt.Gap,
        [lt.Span("\\textit{Calibração (avaliada: configuração padrão)}", NCOLS, "l")],
        tuning,
    ]

    note = (
        "V/E/D: vitórias/empates/derrotas do braço avaliado contra cada comparador; "
        "$n$: número de instâncias. Teste de Mann--Whitney bicaudal, $\\alpha = 0{,}05$, "
        f"com correção de Holm. Avaliações por execução: {fmt.integer(ABLATION_BUDGET)} "
        "na ablação, no braço avaliado e no SPEA2, e "
        f"{fmt.integer(TUNING_BUDGET)} na calibração. Configuração inicial: {INITIAL_CONFIG}."
    )

    return lt.render(
        header=[
            [lt.Span("", 3), lt.Span("V/E/D", 2)],
            ["Comparador", "$n$", "Execuções", "IGD", "HV"],
        ],
        rows=rows,
        colspec="lcccc",
        caption="Comparações par a par da ablação e da calibração.",
        label="tab:ablacao",
        producer=__file__,
        sources=[ABLATION, FACTORIAL, TUNING],
        note=note,
    )


def main() -> int:
    content = build()
    if content is None:
        return 1
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
