#!/usr/bin/env python3
"""Per-instance median tables for the results chapter.

Medians and IQRs come from the per-instance generators; the verdict column
comes from the Holm-corrected audit, because the per-instance generators run
uncorrected tests and may not be used for corrected language.

Instances that were part of the 12-problem calibration subset are marked, so
the in-sample and out-of-sample halves stay distinguishable on the page.

Number layout, by metric:

* IGD spans two orders of magnitude across the suite, so each row prints
  mantissas against one power of ten, shown once in the ``Fator`` column: both
  algorithms and both spreads of a row share it, and the row reads in one
  scale. Four significant digits, not three: several instances (DTLZ1 at
  M = 2, for one) separate only in the fourth.
* HV lies in (0, 1) and needs no scale. Five decimals: on several instances
  the medians differ only in the fifth (ZDT6 with M = 2) and the interquartile
  ranges are of order 1e-5.

Median and spread sit in separate columns, so each aligns on its decimal
comma. ``Delta`` is the relative median difference of Table 6.2, computed the
same way from the same medians. Suites are separated by space, because the
text reads the losses by suite.

The builder fails if a row would print identical medians beside a verdict of
difference: the table would claim a difference its digits do not show.

Writes: results/thesis/tab_{igd,hv}_por_instancia_M{2,3}.tex
"""

from __future__ import annotations

import re
import sys

import pandas as pd

from ivfspea2.paths import RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

DETAILS = RESULTS_TABLES / "claims_summary_instance_details.csv"

DIRECTION = {"IGD": "menor é melhor", "HV": "maior é melhor"}

# The audit writes the verdict as a bare +/-/=; in a math column those need
# wrapping so the minus is a real minus sign and not a hyphen.
VERDICT = {"+": "$+$", "-": "$-$", "=": "$=$"}

IGD_SIGNIFICANT_DIGITS = 4
HV_PLACES = 5
DELTA_PLACES = 2
RUNS = 60

_SUITE = re.compile(r"^[A-Za-z]+")


def _suite(problem: str) -> str:
    match = _SUITE.match(problem)
    if not match:
        raise ValueError(f"não foi possível extrair a suíte de {problem!r}")
    return match.group(0).upper()


def _delta(metric: str, ivf: float, base: float) -> float:
    """Relative median difference, in percent of SPEA2, positive favouring IVF/SPEA2."""
    gain = ivf - base if metric == "HV" else base - ivf
    return 100.0 * gain / abs(base)


def _values(metric: str, row: pd.Series) -> tuple[list[str], int | None]:
    """Median and IQR cells of both algorithms, and the row's power of ten (IGD only)."""
    columns = ("IVFSPEA2_median", "IVFSPEA2_iqr", "SPEA2_median", "SPEA2_iqr")
    if metric == "HV":
        return [fmt.decimal(float(row[c]), places=HV_PLACES) for c in columns], None
    power = fmt.exponent(
        float(row["IVFSPEA2_median"]), float(row["SPEA2_median"]), sig=IGD_SIGNIFICANT_DIGITS
    )
    scale = 10.0**power
    places = IGD_SIGNIFICANT_DIGITS - 1
    return [fmt.decimal(float(row[c]) / scale, places=places) for c in columns], power


def build(metric: str, objectives: int, details: pd.DataFrame) -> str | None:
    per_instance = RESULTS_TABLES / f"{metric.lower()}_per_instance_M{objectives}.csv"
    if not per_instance.exists():
        print(f"ERRO: artefato ausente: {per_instance}", file=sys.stderr)
        return None

    medians = pd.read_csv(per_instance)
    subset = details[
        (details["metric"] == metric) & (details["M"] == f"M{objectives}")
    ].set_index("Problema")

    rows: list[list[str] | object] = []
    example = ""
    previous_suite = None
    for _, row in medians.iterrows():
        problem = str(row["Problema"])
        if problem not in subset.index:
            print(
                f"AVISO: {problem} (M={objectives}, {metric}) ausente da auditoria Holm; "
                "linha omitida",
                file=sys.stderr,
            )
            continue
        verdict_row = subset.loc[problem]
        verdict = str(verdict_row["indicator_holm"])

        values, power = _values(metric, row)
        if values[0] == values[2] and verdict != "=":
            print(
                f"ERRO: {problem} (M={objectives}, {metric}): medianas impressas iguais "
                f"({values[0]}) com veredito {verdict!r}",
                file=sys.stderr,
            )
            return None

        suite = _suite(problem)
        if previous_suite is not None and suite != previous_suite:
            rows.append(lt.Gap)
        previous_suite = suite

        marker = "$^{\\dagger}$" if bool(verdict_row["is_full12"]) else ""
        scale = [] if power is None else [fmt.power_of_ten(power)]
        if power is not None and not example:
            example = (
                f"no {problem}, a mediana do IVF/SPEA2 é "
                f"${values[0].strip('$')} \\times 10^{{{power}}}$"
            )
        delta = _delta(metric, float(row["IVFSPEA2_median"]), float(row["SPEA2_median"]))
        rows.append([
            f"{problem}{marker}",
            str(int(row["D"])),
            *scale,
            *values,
            fmt.signed(delta, places=DELTA_PLACES),
            fmt.pvalue(float(verdict_row["p_holm"])),
            VERDICT.get(verdict, "---"),
        ])

    if not rows:
        print(f"ERRO: nenhuma linha para {metric} M={objectives}", file=sys.stderr)
        return None

    if metric == "IGD":
        values_note = (
            f"Mediana e amplitude interquartil (AIQ) de IGD sobre {RUNS} execuções por "
            f"algoritmo, em múltiplos do fator da linha ({example}); {DIRECTION[metric]}."
        )
    else:
        values_note = (
            f"Mediana e amplitude interquartil (AIQ) de HV sobre {RUNS} execuções por "
            f"algoritmo; {DIRECTION[metric]}."
        )
    note = (
        f"{values_note} $D$: número de variáveis de decisão. $\\Delta$: diferença entre as "
        "medianas, em porcentagem da mediana do SPEA2, orientada de modo que valores positivos "
        "favoreçam o IVF/SPEA2, como na Tabela~\\ref{tab:magnitude_confirmatoria}. O valor-$p$ "
        "é o de Mann--Whitney após correção de Holm dentro da família de todas as instâncias "
        "deste número de objetivos e desta métrica. O veredito compara o IVF/SPEA2 ao SPEA2 "
        "canônico: $+$ favorece o IVF/SPEA2, $-$ favorece o SPEA2 e $=$ indica ausência de "
        "diferença significativa. $^{\\dagger}$ instância usada na calibração de parâmetros, "
        "portanto fora do recorte de generalização."
    )

    scale_columns = 1 if metric == "IGD" else 0
    identity = ["Problema", "$D$"] + (["Fator"] if scale_columns else [])
    header = [
        [
            lt.Span("", len(identity)),
            lt.Span("IVF/SPEA2", 2),
            lt.Span("SPEA2", 2),
            lt.Span("", 3),
        ],
        [
            *identity,
            "Mediana", "AIQ", "Mediana", "AIQ",
            "$\\Delta$ (\\%)", "$p$ (Holm)", "Veredito",
        ],
    ]

    return lt.render(
        header=header,
        rows=rows,
        colspec="lr" + "c" * scale_columns + "rrrr" + "rr" + "c",
        caption=(
            f"{metric} por instância com $M={objectives}$ objetivos: mediana e dispersão do "
            "IVF/SPEA2 e do SPEA2 canônico, diferença relativa e veredito corrigido por Holm."
        ),
        short_caption=f"{metric} por instância com $M={objectives}$ objetivos",
        # Ten columns: the minimum gap goes from 12 pt to 8 pt, and the free
        # width is spread between the columns as in every other table.
        tabcolsep="4pt",
        label=f"tab:{metric.lower()}_por_instancia_m{objectives}",
        producer=__file__,
        sources=[per_instance, DETAILS],
        note=note,
    )


def main() -> int:
    if not DETAILS.exists():
        print(f"ERRO: artefato ausente: {DETAILS}", file=sys.stderr)
        print(
            "Regenere com: .venv/bin/python src/python/analysis/compute_claims_summary.py",
            file=sys.stderr,
        )
        return 1

    details = pd.read_csv(DETAILS)

    failed = False
    for metric in ("IGD", "HV"):
        for objectives in (2, 3):
            content = build(metric, objectives, details)
            if content is None:
                failed = True
                continue
            lt.write(
                RESULTS_THESIS / f"tab_{metric.lower()}_por_instancia_M{objectives}.tex",
                content,
            )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
