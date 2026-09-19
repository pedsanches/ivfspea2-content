#!/usr/bin/env python3
"""Per-instance median tables for the results chapter.

Medians and IQRs come from the per-instance generators; the verdict column
comes from the Holm-corrected audit, because the per-instance generators run
uncorrected tests and may not be used for corrected language.

Instances that were part of the 12-problem calibration subset are marked, so
the in-sample and out-of-sample halves stay distinguishable on the page.

Writes: results/thesis/tab_{igd,hv}_por_instancia_M{2,3}.tex
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

DETAILS = RESULTS_TABLES / "claims_summary_instance_details.csv"

METRIC_LABEL = {"IGD": "IGD", "HV": "HV"}
DIRECTION = {"IGD": "menor é melhor", "HV": "maior é melhor"}

# The audit writes the verdict as a bare +/-/=; in a math column those need
# wrapping so the minus is a real minus sign and not a hyphen.
VERDICT = {"+": "$+$", "-": "$-$", "=": "$=$"}

# Four significant digits, not three: several instances (DTLZ1 at M=2, for one)
# separate only in the fourth digit, and at sig=3 both columns print the same
# value while the verdict column claims a significant difference.
SIGNIFICANT_DIGITS = 4


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

        marker = "$^{\\dagger}$" if bool(verdict_row["is_full12"]) else ""
        rows.append([
            f"{problem}{marker}",
            str(int(row["D"])),
            fmt.median_iqr(row["IVFSPEA2_median"], row["IVFSPEA2_iqr"], sig=SIGNIFICANT_DIGITS),
            fmt.median_iqr(row["SPEA2_median"], row["SPEA2_iqr"], sig=SIGNIFICANT_DIGITS),
            fmt.pvalue(float(verdict_row["p_holm"])),
            VERDICT.get(str(verdict_row["indicator_holm"]), "---"),
        ])

    if not rows:
        print(f"ERRO: nenhuma linha para {metric} M={objectives}", file=sys.stderr)
        return None

    note = (
        f"Mediana (amplitude interquartil) de {METRIC_LABEL[metric]} sobre 60 execuções "
        f"por configuração; {DIRECTION[metric]}. O valor-$p$ é o de Mann--Whitney após "
        "correção de Holm dentro da família de todas as instâncias deste número de "
        "objetivos e desta métrica. O veredito compara o IVF/SPEA2 ao SPEA2 canônico: "
        "$+$ favorece o IVF/SPEA2, $-$ favorece o SPEA2 e $=$ indica ausência de "
        "diferença significativa. $^{\\dagger}$ instância usada na calibração de "
        "parâmetros, portanto fora do recorte de generalização."
    )

    return lt.render(
        header=[
            "Problema", "$D$", "IVF/SPEA2", "SPEA2",
            "$p$ (Holm)", "Veredito",
        ],
        rows=rows,
        colspec="|l|c|c|c|c|c|",
        caption=(
            f"{METRIC_LABEL[metric]} por instância com $M={objectives}$ objetivos: "
            "IVF/SPEA2 contra SPEA2 canônico."
        ),
        label=f"tab:{metric.lower()}_por_instancia_m{objectives}",
        producer=__file__,
        sources=[per_instance, DETAILS],
        note=note,
        resize=True,
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
