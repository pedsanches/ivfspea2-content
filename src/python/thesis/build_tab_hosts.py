#!/usr/bin/env python3
"""Operator-host compatibility tables.

Aggregates the per-instance host statistics into win/tie/loss counts, renders
the geometry stratification, and stratifies the same counts by problem suite
(DTLZ, MaF, WFG, ZDT).

The counts are pipeline-level: each coupling is a host paired with that host's
own published IVF realisation, so the comparison does not isolate the host from
the implementation differences that come with it.

Pairing differs by pipeline. The two NSGA couplings share run IDs with their
hosts and are paired run by run. IVF/SPEA2 (runs 3001-3030) and SPEA2 (runs
1-30) share none, so the per-instance statistics align them by run order, as
the hosts paper declares. The notes state this, and the builder recomputes the
unpaired alternative with the paper's own sensitivity procedure
(``compute_hosts_pairing_robustness.build_rows``) instead of re-implementing it.
It fails if that recomputation no longer reproduces the statistics the tables
count, so the notes cannot drift from the data.

Writes: results/thesis/tab_hosts_wtl.tex
        results/thesis/tab_hosts_geometria.tex
        results/thesis/tab_hosts_suite.tex
"""

from __future__ import annotations

import runpy
import sys

import pandas as pd

from ivfspea2.paths import CONFIG, DATA_PROCESSED, PROJECT_ROOT, RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

GEOMETRY = RESULTS_TABLES / "hosts_geometry_summary.csv"

OUT_WTL = RESULTS_THESIS / "tab_hosts_wtl.tex"
OUT_GEOMETRY = RESULTS_THESIS / "tab_hosts_geometria.tex"
FRONT_GEOMETRY = CONFIG / "hosts_front_geometry.csv"

OUT_SUITE = RESULTS_THESIS / "tab_hosts_suite.tex"

HOSTS_ENDPOINT = DATA_PROCESSED / "hosts_paper.csv"
PAIRING_PROCEDURE = (
    PROJECT_ROOT / "src" / "python" / "analysis" / "compute_hosts_pairing_robustness.py"
)
# Stats-file stem -> comparison label used by the pairing procedure.
PAIRED_BY_RUN = {"ivfnsgaii": "IVFNSGAII_vs_NSGAII", "ivfnsgaiii": "IVFNSGAIII_vs_NSGAIII"}
ORDER_ALIGNED = ("ivfspea2", "IVFSPEA2_vs_SPEA2")
SIGN_WORD = {"+": "vitória", "=": "empate", "-": "derrota"}

# Order matches the group labels already used in the per-instance stats CSVs.
SUITES = ["DTLZ", "MaF", "WFG", "ZDT"]

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


def _instances(n: int) -> str:
    return {1: "uma instância", 2: "duas instâncias"}.get(n, f"{n} instâncias")


def _pairing_sensitivity() -> dict[str, dict] | None:
    """Per metric: IVF/SPEA2 counts without pairing, and the instances that change.

    Returns ``{"igd": {"counts": (w, t, l), "flips": [(problem, m, suite, aligned,
    unpaired), ...]}, "hv": {...}}``, or None after printing ERRO.
    """
    for path in (HOSTS_ENDPOINT, PAIRING_PROCEDURE):
        if not path.exists():
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
            return None
    procedure = runpy.run_path(str(PAIRING_PROCEDURE), run_name="thesis_builder")
    rows = procedure["build_rows"](pd.read_csv(HOSTS_ENDPOINT))

    def _modes(stem: str, comparison: str, mode: str, metric: str) -> pd.DataFrame | None:
        stats = pd.read_csv(RESULTS_TABLES / f"hosts_{stem}_{metric}_stats.csv")
        recomputed = rows[
            (rows["analysis_mode"] == mode)
            & (rows["comparison"] == comparison)
            & (rows["metric"] == metric.upper())
        ]
        merged = stats[["problem", "M", "group", "sign"]].merge(
            recomputed[["problem", "M", "sign"]],
            on=["problem", "M"],
            suffixes=("", "_recomputed"),
        )
        if len(merged) != len(stats) or not (merged["sign"] == merged["sign_recomputed"]).all():
            print(
                f"ERRO: a análise '{mode}' recomputada de {HOSTS_ENDPOINT.name} não "
                f"reproduz hosts_{stem}_{metric}_stats.csv; a nota sobre o pareamento "
                "deixaria de descrever a tabela",
                file=sys.stderr,
            )
            return None
        return merged

    for stem, comparison in PAIRED_BY_RUN.items():
        for metric in ("igd", "hv"):
            if _modes(stem, comparison, "primary_paired", metric) is None:
                return None

    stem, comparison = ORDER_ALIGNED
    result: dict[str, dict] = {}
    for metric in ("igd", "hv"):
        aligned = _modes(stem, comparison, "sensitivity_order_aligned", metric)
        if aligned is None:
            return None
        unpaired = rows[
            (rows["analysis_mode"] == "primary_unpaired")
            & (rows["comparison"] == comparison)
            & (rows["metric"] == metric.upper())
        ]
        both = aligned.merge(
            unpaired[["problem", "M", "sign"]], on=["problem", "M"], suffixes=("", "_unpaired")
        )
        signs = both["sign_unpaired"].astype(str)
        flips = [
            (row.problem, int(row.M), row.group, row.sign, row.sign_unpaired)
            for row in both.sort_values(["M", "problem"]).itertuples()
            if row.sign != row.sign_unpaired
        ]
        result[metric] = {
            "counts": (
                int((signs == "+").sum()),
                int((signs == "=").sum()),
                int((signs == "-").sum()),
            ),
            "flips": flips,
        }
    return result


def _flip_list(flips: list[tuple]) -> str:
    return "; ".join(
        f"{problem} com $M={m}$, de {SIGN_WORD[aligned]} para {SIGN_WORD[unpaired]}"
        for problem, m, _suite, aligned, unpaired in flips
    )


def _pairing_note_totals(sensitivity: dict[str, dict]) -> str:
    parts = []
    for metric in ("igd", "hv"):
        flips = sensitivity[metric]["flips"]
        if not flips:
            parts.append(f"não mudam em {metric.upper()}")
            continue
        wins, ties, losses = sensitivity[metric]["counts"]
        parts.append(
            f"mudam em {_instances(len(flips))} em {metric.upper()} "
            f"({_flip_list(flips)}), para {fmt.wtl(wins, ties, losses)}"
        )
    return (
        "Os pares IVF/NSGA-II e IVF/NSGA-III compartilham a faixa de execuções com o "
        "hospedeiro e são pareados por execução. No par IVF/SPEA2, as faixas não "
        "coincidem (3001--3030 e 1--30), e as execuções são alinhadas por ordem, como no "
        "artigo de origem~\\cite{zambrano2026hosts}; sem pareamento, com o teste de "
        "Mann--Whitney, as contagens "
        f"do IVF/SPEA2 {parts[0]} e {parts[1]}."
    )


def _pairing_note_suites(sensitivity: dict[str, dict]) -> str:
    flips = [
        (metric, flip) for metric in ("igd", "hv") for flip in sensitivity[metric]["flips"]
    ]
    if not flips:
        return "Sem pareamento, as contagens do IVF/SPEA2 por suíte não mudam."
    changed = sorted({flip[2] for _, flip in flips})
    detail = "; ".join(
        f"{metric.upper()}, {_flip_list([flip])}" for metric, flip in flips
    )
    wfg = "" if "WFG" in changed else ", e as da WFG não mudam"
    return (
        "Sem pareamento, com o teste de Mann--Whitney, as contagens do IVF/SPEA2 por "
        f"suíte mudam apenas na {' e na '.join(changed)} ({detail}){wfg}."
    )

def build_wtl(sensitivity: dict[str, dict]) -> str | None:
    # One row per coupling, one column group per metric: the ordering of the
    # couplings reads down the two Total columns. The host is the name after
    # the slash in the coupling's label, so it needs no column of its own.
    rows: list[list[str] | object] = []
    for stem, label, base in HOSTS:
        if not label.endswith(f"/{base}"):
            print(f"ERRO: o rótulo {label!r} não nomeia o hospedeiro {base!r}", file=sys.stderr)
            return None
        cells = [label]
        for metric in ("igd", "hv"):
            path = RESULTS_TABLES / f"hosts_{stem}_{metric}_stats.csv"
            if not path.exists():
                print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
                return None
            stats = pd.read_csv(path)

            total_w = total_t = total_l = 0
            for objectives in (2, 3):
                wins, ties, losses = _counts(stats, objectives)
                total_w += wins
                total_t += ties
                total_l += losses
                cells.append(fmt.wtl(wins, ties, losses))
            cells.append(fmt.wtl(total_w, total_t, total_l))
        rows.append(cells)

    # The overlap and the pipeline-level unit of comparison are stated in the
    # paragraph before the table; the note keeps them in one sentence, so the
    # table still carries its own scope.
    note = (
        "Vitórias/empates/derrotas (V/E/D) de cada acoplamento IVF contra o seu próprio "
        "hospedeiro, nas 51 instâncias sintéticas. Teste de Wilcoxon de postos "
        "sinalizados com correção de Benjamini--Hochberg por acoplamento e métrica, "
        "$\\alpha = 0{,}05$, 30 execuções por configuração, orçamento de 100.000 "
        f"avaliações. {_pairing_note_totals(sensitivity)} A comparação é entre pipelines e "
        "não isola o efeito do hospedeiro; as execuções 3001--3030 e 1--30 do par IVF/SPEA2 "
        "são um subconjunto da coorte da comparação principal e não constituem replicação "
        "independente."
    )

    return lt.render(
        header=[
            [lt.Span("", 1), lt.Span("IGD (V/E/D)", 3), lt.Span("HV (V/E/D)", 3)],
            ["Acoplamento", "$M=2$", "$M=3$", "Total", "$M=2$", "$M=3$", "Total"],
        ],
        rows=rows,
        colspec="lcccccc",
        caption=(
            "Compatibilidade entre o operador IVF e três hospedeiros: contagens de "
            "vitórias, empates e derrotas de cada acoplamento contra o seu hospedeiro."
        ),
        label="tab:hosts_wtl",
        producer=__file__,
        sources=[RESULTS_TABLES / f"hosts_{s}_{m}_stats.csv" for s, _, _ in HOSTS for m in ("igd", "hv")]
        + [HOSTS_ENDPOINT, PAIRING_PROCEDURE],
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
        # Rótulo da coluna Acoplamento centralizado na vertical, agrupando
        # as linhas IGD e HV do acoplamento.
        bloco: list[list[str] | object] = []
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
            bloco.append(cells)
        bloco[0][0] = lt.Multirow(label, len(bloco))
        rows.extend(bloco)

    n_regular = int(grouped[grouped["geometry"] == "regular"]["n_instances"].iloc[0])
    n_irregular = int(grouped[grouped["geometry"] == "irregular"]["n_instances"].iloc[0])

    note = (
        "Vitórias/empates/derrotas (V/E/D) de cada acoplamento contra o seu hospedeiro, com o "
        "mesmo teste, a mesma correção e o mesmo pareamento da Tabela~\\ref{tab:hosts_wtl}, "
        "estratificadas pela geometria da fronteira de Pareto: regular (convexa, côncava ou "
        "linear) e irregular (desconectada ou degenerada), conforme "
        "\\texttt{config/hosts\\_front\\_geometry.csv}. $A_{12}$ é a mediana do tamanho "
        "de efeito de Vargha--Delaney orientado a favor do acoplamento IVF; valores "
        "acima de $0{,}5$ favorecem o IVF. Os testes de interação entre hospedeiro e "
        "geometria não atingiram significância, de modo que a estratificação é descritiva."
    )

    return lt.render(
        header=[
            [
                lt.Span("", 2),
                lt.Span(f"Regular ($n={n_regular}$)", 2),
                lt.Span(f"Irregular ($n={n_irregular}$)", 2),
            ],
            ["Acoplamento", "Métrica", "V/E/D", "$A_{12}$", "V/E/D", "$A_{12}$"],
        ],
        rows=rows,
        colspec="llcccc",
        caption=(
            "Contagens de cada acoplamento IVF contra o seu hospedeiro, estratificadas "
            "pela geometria da fronteira de Pareto."
        ),
        label="tab:hosts_geometria",
        producer=__file__,
        sources=[GEOMETRY],
        note=note,
    )


def _suite_counts(stats: pd.DataFrame, suite: str) -> tuple[int, int, int]:
    subset = stats[stats["group"] == suite]
    signs = subset["sign"].astype(str)
    return (
        int((signs == "+").sum()),
        int((signs == "=").sum()),
        int((signs == "-").sum()),
    )


def build_suite(sensitivity: dict[str, dict]) -> str | None:
    if not FRONT_GEOMETRY.exists():
        print(f"ERRO: artefato ausente: {FRONT_GEOMETRY}", file=sys.stderr)
        return None
    if not GEOMETRY.exists():
        print(f"ERRO: artefato ausente: {GEOMETRY}", file=sys.stderr)
        return None
    front = pd.read_csv(FRONT_GEOMETRY)
    grouped_geo = pd.read_csv(GEOMETRY)
    grouped_geo = grouped_geo[grouped_geo["geometry_level"] == "geometry_group"]

    n_by_suite: dict[str, int] | None = None
    rows: list[list[str] | object] = []
    for index, (stem, label, _) in enumerate(HOSTS):
        if index:
            rows.append(lt.Rule)
        host_key = stem.upper()
        # Rótulo da coluna Acoplamento centralizado na vertical, agrupando
        # as linhas IGD e HV do acoplamento.
        bloco: list[list[str] | object] = []
        for metric_index, metric in enumerate(("igd", "hv")):
            path = RESULTS_TABLES / f"hosts_{stem}_{metric}_stats.csv"
            if not path.exists():
                print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
                return None
            stats = pd.read_csv(path)

            suite_n = {s: int((stats["group"] == s).sum()) for s in SUITES}
            if n_by_suite is None:
                n_by_suite = suite_n
            elif suite_n != n_by_suite:
                print(
                    f"ERRO: contagem de instâncias por suíte diverge em {path}: "
                    f"{suite_n} != {n_by_suite}",
                    file=sys.stderr,
                )
                return None

            cells = [label if metric_index == 0 else "", metric.upper()]
            suite_w = suite_t = suite_l = 0
            for suite in SUITES:
                wins, ties, losses = _suite_counts(stats, suite)
                suite_w += wins
                suite_t += ties
                suite_l += losses
                cells.append(fmt.wtl(wins, ties, losses))

            check_w = check_t = check_l = 0
            for objectives in (2, 3):
                wins, ties, losses = _counts(stats, objectives)
                check_w += wins
                check_t += ties
                check_l += losses
            if (suite_w, suite_t, suite_l) != (check_w, check_t, check_l):
                print(
                    f"ERRO: soma por suíte {suite_w}/{suite_t}/{suite_l} difere do total "
                    f"de build_wtl {check_w}/{check_t}/{check_l} para {label} "
                    f"{metric.upper()}",
                    file=sys.stderr,
                )
                return None

            orient = (lambda v: 1.0 - v) if metric == "igd" else (lambda v: v)
            a12_ivf = stats["A12"].apply(orient)
            wfg_mask = stats["group"] == "WFG"
            cells.append(fmt.decimal(float(a12_ivf[wfg_mask].median()), places=3))
            cells.append(fmt.decimal(float(a12_ivf[~wfg_mask].median()), places=3))
            bloco.append(cells)

            merged = stats.assign(a12_ivf=a12_ivf).merge(
                front[["problem", "M", "geometry_group"]], on=["problem", "M"], how="left"
            )
            for geometry_key in ("regular", "irregular"):
                recomputed = merged.loc[
                    merged["geometry_group"] == geometry_key, "a12_ivf"
                ].median()
                hit = grouped_geo[
                    (grouped_geo["host"] == host_key)
                    & (grouped_geo["metric"] == metric.upper())
                    & (grouped_geo["geometry"] == geometry_key)
                ]
                if len(hit) != 1:
                    print(
                        f"ERRO: esperava 1 linha de referência para {host_key}/"
                        f"{metric.upper()}/{geometry_key}, encontrei {len(hit)}",
                        file=sys.stderr,
                    )
                    return None
                reference = float(hit.iloc[0]["median_a12_ivf"])
                if abs(float(recomputed) - reference) > 1e-9:
                    print(
                        f"ERRO: mediana de A12 recomputada ({recomputed!r}) diverge da "
                        f"referência em hosts_geometry_summary.csv ({reference!r}) para "
                        f"{host_key}/{metric.upper()}/{geometry_key}",
                        file=sys.stderr,
                    )
                    return None

        bloco[0][0] = lt.Multirow(label, len(bloco))
        rows.extend(bloco)

    assert n_by_suite is not None
    # Suite names alone keep the eight columns inside the text block at the
    # house type size; the denominators go to the note.
    header = [
        [lt.Span("", 2), lt.Span("V/E/D por suíte", len(SUITES)), lt.Span("$A_{12}$ mediano", 2)],
        ["Acoplamento", "Métrica", *SUITES, "WFG", "Demais"],
    ]
    denominators = "; ".join(f"{suite}, {n_by_suite[suite]}" for suite in SUITES)

    # Unit of comparison and cohort overlap are those of Table 7.4, which the
    # note cites instead of repeating them.
    note = (
        "Vitórias/empates/derrotas (V/E/D) de cada acoplamento contra o seu hospedeiro, "
        "estratificadas por suíte de problemas de teste, com o mesmo teste, a mesma correção, "
        "o mesmo pareamento e as mesmas ressalvas de comparação e de sobreposição de coortes "
        f"da Tabela~\\ref{{tab:hosts_wtl}}. Instâncias por suíte: {denominators}. "
        f"{_pairing_note_suites(sensitivity)} $A_{{12}}$ é a mediana do tamanho de efeito de "
        "Vargha--Delaney orientada a favor do IVF (valores acima de $0{,}5$ favorecem o IVF), "
        "separada entre as instâncias WFG e as demais. A estratificação por suíte é descritiva: "
        "nenhum teste de interação entre acoplamento e suíte foi conduzido."
    )

    return lt.render(
        header=header,
        rows=rows,
        colspec="ll" + "c" * len(SUITES) + "cc",
        caption=(
            "Contagens de cada acoplamento IVF contra o seu hospedeiro, estratificadas "
            "por suíte de problemas de teste."
        ),
        label="tab:hosts_suite",
        producer=__file__,
        sources=[
            RESULTS_TABLES / f"hosts_{s}_{m}_stats.csv"
            for s, _, _ in HOSTS
            for m in ("igd", "hv")
        ]
        + [GEOMETRY, FRONT_GEOMETRY, HOSTS_ENDPOINT, PAIRING_PROCEDURE],
        note=note,
    )


def main() -> int:
    failed = False
    sensitivity = _pairing_sensitivity()
    if sensitivity is None:
        return 1
    targets = (
        (build_wtl(sensitivity), OUT_WTL),
        (build_geometry(), OUT_GEOMETRY),
        (build_suite(sensitivity), OUT_SUITE),
    )
    for content, path in targets:
        if content is None:
            failed = True
            continue
        lt.write(path, content)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
