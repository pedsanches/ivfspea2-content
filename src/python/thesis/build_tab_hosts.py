#!/usr/bin/env python3
"""Operator-host compatibility tables.

Aggregates the per-instance host statistics into win/tie/loss counts, and
renders the geometry stratification.

The counts are pipeline-level: each column is a host paired with that host's
own published IVF realisation, so the comparison does not isolate the host from
the implementation differences that come with it.

Writes: results/thesis/tab_hosts_wtl.tex
        results/thesis/tab_hosts_geometria.tex
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

GEOMETRY = RESULTS_TABLES / "hosts_geometry_summary.csv"

OUT_WTL = RESULTS_THESIS / "tab_hosts_wtl.tex"
OUT_GEOMETRY = RESULTS_THESIS / "tab_hosts_geometria.tex"

# (stats-file stem, label). Order is the ordering the chapter argues for:
# strongest coupling first.
HOSTS = [
    ("ivfspea2", "IVF/SPEA2", "SPEA2"),
    ("ivfnsgaiii", "IVF/NSGA-III", "NSGA-III"),
    ("ivfnsgaii", "IVF/NSGA-II", "NSGA-II"),
]

GEOMETRY_LABEL = {"regular": "Regular", "irregular": "Irregular"}


def _counts(stats: pd.DataFrame, objectives: int) -> tuple[int, int, int]:
    subset = stats[stats["M"] == objectives]
    signs = subset["sign"].astype(str)
    return (
        int((signs == "+").sum()),
        int((signs == "=").sum()),
        int((signs == "-").sum()),
    )


def build_wtl() -> str | None:
    rows: list[list[str] | object] = []
    for index, (stem, label, base) in enumerate(HOSTS):
        if index:
            rows.append(lt.Rule)
        for metric_index, metric in enumerate(("igd", "hv")):
            path = RESULTS_TABLES / f"hosts_{stem}_{metric}_stats.csv"
            if not path.exists():
                print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
                return None
            stats = pd.read_csv(path)

            cells = [label if metric_index == 0 else "", base if metric_index == 0 else ""]
            cells.append(metric.upper())
            total_w = total_t = total_l = 0
            for objectives in (2, 3):
                wins, ties, losses = _counts(stats, objectives)
                total_w += wins
                total_t += ties
                total_l += losses
                cells.append(fmt.wtl(wins, ties, losses))
            cells.append(f"\\textbf{{{fmt.wtl(total_w, total_t, total_l)}}}")
            rows.append(cells)

    note = (
        "Vitórias/empates/derrotas de cada realização do IVF contra o seu próprio "
        "hospedeiro, nas 51 instâncias sintéticas. Wilcoxon pareado com correção de "
        "Benjamini--Hochberg, $\\alpha = 0{,}05$, 30 execuções por configuração, "
        "orçamento de 100.000 avaliações, PlatEMO 4.6. A unidade de comparação é o par "
        "hospedeiro mais realização do operador, e não um módulo único transplantado sem "
        "alteração: a comparação não isola causalmente o efeito do hospedeiro. "
        "As execuções 3001--3030 e 1--30 do par IVF/SPEA2 são um subconjunto da coorte "
        "confirmatória e não constituem replicação independente."
    )

    return lt.render(
        header=[
            "Acoplamento", "Hospedeiro", "Métrica",
            "$M=2$", "$M=3$", "Total (V/E/D)",
        ],
        rows=rows,
        colspec="|l|l|c|c|c|c|",
        caption=(
            "Compatibilidade entre o operador IVF e três hospedeiros: contagens de "
            "vitórias, empates e derrotas de cada acoplamento contra o seu hospedeiro."
        ),
        label="tab:hosts_wtl",
        producer=__file__,
        sources=[RESULTS_TABLES / f"hosts_{s}_{m}_stats.csv" for s, _, _ in HOSTS for m in ("igd", "hv")],
        note=note,
    )


def build_geometry() -> str | None:
    if not GEOMETRY.exists():
        print(f"ERRO: artefato ausente: {GEOMETRY}", file=sys.stderr)
        return None

    geometry = pd.read_csv(GEOMETRY)
    grouped = geometry[geometry["geometry_level"] == "geometry_group"]

    rows: list[list[str] | object] = []
    for index, (_, label, _) in enumerate(HOSTS):
        if index:
            rows.append(lt.Rule)
        for metric_index, metric in enumerate(("IGD", "HV")):
            cells = [label if metric_index == 0 else "", metric]
            for geometry_key in ("regular", "irregular"):
                hit = grouped[
                    (grouped["host_label"] == label)
                    & (grouped["metric"] == metric)
                    & (grouped["geometry"] == geometry_key)
                ]
                if len(hit) != 1:
                    print(
                        f"ERRO: esperava 1 linha para {label}/{metric}/{geometry_key}, "
                        f"encontrei {len(hit)}",
                        file=sys.stderr,
                    )
                    return None
                row = hit.iloc[0]
                cells.append(fmt.wtl(row["wins"], row["ties"], row["losses"]))
                cells.append(fmt.decimal(float(row["median_a12_ivf"]), places=3))
            rows.append(cells)

    n_regular = int(grouped[grouped["geometry"] == "regular"]["n_instances"].iloc[0])
    n_irregular = int(grouped[grouped["geometry"] == "irregular"]["n_instances"].iloc[0])

    note = (
        f"Estratificação por geometria da fronteira de Pareto: regular "
        f"($n = {n_regular}$: convexa, côncava ou linear) e irregular "
        f"($n = {n_irregular}$: desconectada ou degenerada), conforme "
        "\\texttt{config/hosts\\_front\\_geometry.csv}. $A_{12}$ é a mediana do tamanho "
        "de efeito de Vargha--Delaney orientado a favor do acoplamento IVF; valores "
        "acima de $0{,}5$ favorecem o IVF. Os testes de interação entre hospedeiro e "
        "geometria não atingiram significância, de modo que a estratificação é descritiva."
    )

    return lt.render(
        header=[
            "Acoplamento", "Métrica",
            "Regular (V/E/D)", "$A_{12}$", "Irregular (V/E/D)", "$A_{12}$",
        ],
        rows=rows,
        colspec="|l|c|c|c|c|c|",
        caption=(
            "Compatibilidade operador--hospedeiro estratificada pela geometria da "
            "fronteira de Pareto."
        ),
        label="tab:hosts_geometria",
        producer=__file__,
        sources=[GEOMETRY],
        note=note,
    )


def main() -> int:
    failed = False
    for content, path in ((build_wtl(), OUT_WTL), (build_geometry(), OUT_GEOMETRY)):
        if content is None:
            failed = True
            continue
        lt.write(path, content)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
