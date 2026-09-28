#!/usr/bin/env python3
"""Magnitude do efeito confirmatório, por desfecho corrigido.

As contagens confirmatórias dizem com que frequência a diferença é detectável;
não dizem quão grande ela é. Duas magnitudes respondem a perguntas distintas, e
o texto não pode confundi-las:

* o $A_{12}$ orientado mede com que frequência uma execução do IVF/SPEA2 supera
  uma do SPEA2, com meio crédito para empates; o corte descritivo 0,71 permite
  contar instâncias com ordenação de pares nessa intensidade;
* a diferença relativa entre medianas mede quanto o resultado típico se
  desloca, orientada de modo que valores positivos favoreçam o IVF/SPEA2.

Uma diferença pode ter $A_{12}$ elevado e deslocamento pequeno entre medianas:
as execuções do acoplamento vencem as do hospedeiro na maior parte dos pares,
por margem estreita. A tabela agrupa as 51 instâncias pelo desfecho corrigido por
Holm da auditoria canônica, para que o tamanho das vitórias e o das derrotas
possam ser lidos lado a lado.

Lê:
    data/processed/todas_metricas_consolidado_with_modern.csv  (via filtro de coorte)
    results/tables/claims_summary_instance_details.csv         (desfecho por instância, Holm)

Escreve:
    results/thesis/tab_magnitude_confirmatoria.tex
    results/thesis/tab_magnitude_confirmatoria_fora_ajuste.tex
    results/thesis/tab_magnitude_sensibilidade.tex

As duas últimas tabelas separam o recorte fora do ajuste de uma sensibilidade
local; a tabela confirmatória preexistente permanece inalterada.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import latex_table as lt
import ptbr_format as fmt
from ivfspea2.cohorts import filter_submission_synthetic_cohort
from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS

CONSOLIDADO = DATA_PROCESSED / "todas_metricas_consolidado_with_modern.csv"
DETALHES = RESULTS_TABLES / "claims_summary_instance_details.csv"
OUT = RESULTS_THESIS / "tab_magnitude_confirmatoria.tex"
OUT_FORA_AJUSTE = RESULTS_THESIS / "tab_magnitude_confirmatoria_fora_ajuste.tex"
OUT_SENSIBILIDADE = RESULTS_THESIS / "tab_magnitude_sensibilidade.tex"

# Corte descritivo explícito no próprio gerador; não é teste de hipótese.
CORTE_A12 = 0.71

# métrica -> maior é melhor
METRICAS = {"IGD": False, "HV": True}
DESFECHOS = [("+", "Vitórias"), ("=", "Empates"), ("-", "Derrotas")]


# Sensibilidade exploratória: o gerador local torna o intervalo reprodutível
# sem reutilizar a correção de Holm, que pertence aos testes por instância.
BOOTSTRAP_REPS = 10_000
BOOTSTRAP_SEED = 20260927
SENSIBILIDADE_IGD = (("WFG1", "M2"), ("WFG6", "M2"), ("DTLZ4", "M3"), ("MaF5", "M3"))


def _delta_mediana(ivf: np.ndarray, base: np.ndarray, *, maior_melhor: bool) -> float:
    """Diferença relativa das medianas, positiva quando favorece IVF/SPEA2."""
    mediana_ivf = float(np.median(ivf))
    mediana_base = float(np.median(base))
    if mediana_base == 0:
        return np.nan
    ganho = mediana_ivf - mediana_base if maior_melhor else mediana_base - mediana_ivf
    return 100.0 * ganho / abs(mediana_base)


def _resumo_delta(grupo: pd.DataFrame) -> tuple[str, str, str]:
    """Mediana, mínimo e máximo formatados, inclusive para grupo sem instâncias."""
    deltas = grupo["delta"].dropna()
    if deltas.empty:
        return ("---", "---", "---")
    return (
        fmt.signed(float(deltas.median()), places=2),
        fmt.signed(float(deltas.min()), places=2),
        fmt.signed(float(deltas.max()), places=2),
    )

def _por_instancia() -> pd.DataFrame:
    """$A_{12}$ orientado e diferença relativa de medianas, por instância e métrica."""
    bruto = pd.read_csv(CONSOLIDADO)
    coorte = filter_submission_synthetic_cohort(bruto)
    coorte = coorte[coorte["Algoritmo"].isin(["IVFSPEA2", "SPEA2"])]

    linhas = []
    for (problema, m), grupo in coorte.groupby(["Problema", "M"]):
        for metrica, maior_melhor in METRICAS.items():
            ivf = grupo.loc[grupo["Algoritmo"] == "IVFSPEA2", metrica].dropna().to_numpy()
            base = grupo.loc[grupo["Algoritmo"] == "SPEA2", metrica].dropna().to_numpy()
            if ivf.size == 0 or base.size == 0:
                continue
            diferenca = np.subtract.outer(ivf, base)
            favorece = diferenca > 0 if maior_melhor else diferenca < 0
            a12 = float(favorece.mean() + 0.5 * (diferenca == 0).mean())
            mediana_ivf = float(np.median(ivf))
            mediana_base = float(np.median(base))
            ganho = mediana_ivf - mediana_base if maior_melhor else mediana_base - mediana_ivf
            delta = 100.0 * ganho / abs(mediana_base) if mediana_base != 0 else np.nan
            linhas.append(
                {
                    "metric": metrica,
                    "M": m,
                    "Problema": problema,
                    "a12": a12,
                    "delta": delta,
                    "n_ivf": int(ivf.size),
                    "n_base": int(base.size),
                }
            )
    return pd.DataFrame(linhas)


def _linhas_magnitude_fora_ajuste(tabela: pd.DataFrame) -> list[list[str] | object]:
    """Resume os 39 problemas reservados, preservando o Holm da família completa."""
    fora_ajuste = tabela.loc[~tabela["is_full12"]]
    rows: list[list[str] | object] = []
    for indice, metrica in enumerate(METRICAS):
        if indice:
            rows.append(lt.Rule)
        bloco_metrica = fora_ajuste.loc[fora_ajuste["metric"] == metrica]
        for indice_m, m in enumerate(("M2", "M3")):
            if indice_m:
                rows.append(lt.Gap)
            bloco = bloco_metrica.loc[bloco_metrica["M"] == m]
            for posicao, (sinal, rotulo) in enumerate((*DESFECHOS, (None, "Todas"))):
                grupo = bloco if sinal is None else bloco.loc[bloco["indicator_holm"] == sinal]
                resumo_delta = _resumo_delta(grupo)
                rows.append(
                    [
                        metrica if indice_m == 0 and posicao == 0 else "",
                        m if posicao == 0 else "",
                        rotulo,
                        str(len(grupo)),
                        fmt.decimal(float(grupo["a12"].median())),
                        *resumo_delta,
                    ]
                )
            if m == "M3":
                sem_duplicata = bloco.loc[bloco["Problema"] != "MaF7"]
                resumo_delta = _resumo_delta(sem_duplicata)
                rows.append(
                    [
                        "",
                        "",
                        "Todas, sem MaF7$^*$",
                        str(len(sem_duplicata)),
                        fmt.decimal(float(sem_duplicata["a12"].median())),
                        *resumo_delta,
                    ]
                )
    return rows


def _render_magnitude_fora_ajuste(tabela: pd.DataFrame) -> str:
    return lt.render(
        header=[
            [
                lt.Span("", 4),
                lt.Span("$A_{12}$", 1),
                lt.Span("$\\Delta$ (\\%)", 3),
            ],
            [
                "Métrica",
                "$M$",
                "Desfecho (Holm)",
                "$n$",
                "Mediano",
                "Mediano",
                "Mínimo",
                "Máximo",
            ],
        ],
        rows=_linhas_magnitude_fora_ajuste(tabela),
        colspec="lllcrrrr",
        tabcolsep="4pt",
        caption=(
            "Magnitude fora do ajuste entre IVF/SPEA2 e SPEA2, por desfecho "
            "confirmatório corrigido."
        ),
        label="tab:magnitude_confirmatoria_fora_ajuste",
        producer=__file__,
        sources=[DETALHES, CONSOLIDADO],
        note=(
            "Apenas as 39 instâncias não usadas no ajuste (24 com $M=2$ e 15 com $M=3$). "
            "Coorte: IVF/SPEA2 nas execuções 3001--3060 contra SPEA2 nas execuções 1--60, "
            "60 execuções por algoritmo e instância. O desfecho é o de Mann--Whitney com "
            "Holm aplicado à família completa de cada métrica e número de objetivos, antes "
            "do recorte fora do ajuste; portanto, esta tabela não reaplica Holm. "
            "$A_{12}$ e $\\Delta$ seguem as definições da "
            "Tabela~\\ref{tab:magnitude_confirmatoria}; valores positivos de $\\Delta$ "
            "favorecem IVF/SPEA2. $^*$MaF7 com $M=3$ duplica DTLZ7 usado no ajuste; a última "
            "linha de cada métrica mostra o recorte descritivo sem essa instância."
        ),
    )


def _bootstrap_delta_igd(
    ivf: np.ndarray, base: np.ndarray, gerador: np.random.Generator
) -> tuple[float, float]:
    """IC percentil de 95% para a diferença relativa de medianas em IGD."""
    if ivf.size != 60 or base.size != 60:
        raise ValueError(
            "a sensibilidade requer 60 execuções por algoritmo e instância "
            f"(IVF/SPEA2={ivf.size}, SPEA2={base.size})"
        )
    amostras_ivf = ivf[gerador.integers(ivf.size, size=(BOOTSTRAP_REPS, ivf.size))]
    amostras_base = base[gerador.integers(base.size, size=(BOOTSTRAP_REPS, base.size))]
    medianas_ivf = np.median(amostras_ivf, axis=1)
    medianas_base = np.median(amostras_base, axis=1)
    deltas = 100.0 * (medianas_base - medianas_ivf) / np.abs(medianas_base)
    if not np.isfinite(deltas).all():
        raise ValueError("a sensibilidade requer medianas bootstrap não nulas e finitas")
    intervalo = np.quantile(deltas, (0.025, 0.975), method="linear")
    return float(intervalo[0]), float(intervalo[1])


def _render_sensibilidade(coorte: pd.DataFrame) -> str:
    rows: list[list[str]] = []
    gerador = np.random.default_rng(BOOTSTRAP_SEED)
    for problema, m in SENSIBILIDADE_IGD:
        grupo = coorte.loc[(coorte["Problema"] == problema) & (coorte["M"] == m)]
        ivf = grupo.loc[grupo["Algoritmo"] == "IVFSPEA2", "IGD"].dropna().to_numpy()
        base = grupo.loc[grupo["Algoritmo"] == "SPEA2", "IGD"].dropna().to_numpy()
        if ivf.size != 60 or base.size != 60:
            raise ValueError(f"{problema}/{m}: cobertura insuficiente para a sensibilidade")
        limite_inferior, limite_superior = _bootstrap_delta_igd(ivf, base, gerador)
        rows.append(
            [
                problema,
                m,
                fmt.signed(_delta_mediana(ivf, base, maior_melhor=False), places=2),
                f"[{fmt.signed(limite_inferior, places=2)}, {fmt.signed(limite_superior, places=2)}]",
            ]
        )
    return lt.render(
        header=["Instância", "$M$", "$\\Delta$ IGD (\\%)", "IC bootstrap 95\\%"],
        rows=rows,
        colspec="llrr",
        tabcolsep="5pt",
        caption="Sensibilidade exploratória da diferença relativa das medianas de IGD.",
        label="tab:magnitude_sensibilidade",
        producer=__file__,
        sources=[CONSOLIDADO],
        note=(
            "Coorte: IVF/SPEA2 nas execuções 3001--3060 contra SPEA2 nas execuções 1--60, "
            "60 execuções independentes por algoritmo e instância. $\\Delta$ é a diferença "
            "entre medianas em porcentagem da mediana do SPEA2; valores positivos favorecem "
            "IVF/SPEA2. O IC percentil de 95\\% resulta de 10.000 reamostragens independentes "
            "com reposição dentro de cada algoritmo/instância (semente 20260927). Ele não é "
            "ajuste de Holm, não demonstra equivalência e não é intervalo para uma proporção "
            "de problemas; a tabela não sustenta inferência global."
        ),
    )


def main() -> int:
    faltando = [p for p in (CONSOLIDADO, DETALHES) if not p.exists()]
    if faltando:
        for path in faltando:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return 1

    detalhes = pd.read_csv(DETALHES)[
        ["metric", "M", "Problema", "is_full12", "indicator_holm"]
    ]
    magnitudes = _por_instancia()
    tabela = detalhes.merge(magnitudes, on=["metric", "M", "Problema"], how="left")
    if tabela["a12"].isna().any():
        ausentes = tabela.loc[tabela["a12"].isna(), ["metric", "M", "Problema"]]
        print(f"ERRO: instâncias sem dados na coorte:\n{ausentes}", file=sys.stderr)
        return 1
    tamanhos = sorted(set(zip(tabela["n_ivf"], tabela["n_base"], strict=True)))
    if len(tamanhos) != 1:
        print(f"ERRO: coorte com tamanhos heterogêneos: {tamanhos}", file=sys.stderr)
        return 1
    n_execucoes = int(tamanhos[0][0])
    sem_delta = int(tabela["delta"].isna().sum())

    rows: list[list[str] | object] = []
    for indice, metrica in enumerate(METRICAS):
        if indice:
            rows.append(lt.Rule)
        bloco = tabela[tabela["metric"] == metrica]
        grupos = [(bloco[bloco["indicator_holm"] == s], rotulo) for s, rotulo in DESFECHOS]
        grupos.append((bloco, "Todas"))
        for posicao, (grupo, rotulo) in enumerate(grupos):
            deltas = grupo["delta"].dropna()
            rows.append(
                [
                    metrica if posicao == 0 else "",
                    rotulo,
                    str(len(grupo)),
                    fmt.decimal(float(grupo["a12"].median())),
                    str(int((grupo["a12"] >= CORTE_A12).sum())),
                    fmt.signed(float(deltas.median()), places=2),
                    fmt.signed(float(deltas.min()), places=2),
                    fmt.signed(float(deltas.max()), places=2),
                ]
            )

    nota_delta = (
        ""
        if not sem_delta
        else f" Em {sem_delta} instâncias a mediana do SPEA2 é nula e $\\Delta$ não é definido."
    )
    note = (
        "Coorte confirmatória: IVF/SPEA2 nas execuções 3001--3060 contra SPEA2 nas execuções "
        f"1--60, {n_execucoes} execuções por algoritmo e instância, orçamento de 100.000 "
        "avaliações. Desfecho pelo teste de Mann--Whitney com correção de Holm por número de "
        "objetivos e por métrica, como na Tabela~\\ref{tab:confirmatorio_wtl}; $n$: número de "
        "instâncias com o desfecho. $A_{12}$ orientado: fração dos pares de execuções em que o "
        "IVF/SPEA2 obtém o melhor valor, com empates contando meio par. O corte "
        f"$A_{{12}} \\geq {fmt.decimal(CORTE_A12, places=2).strip('$')}$ "
        "é descritivo, não outro teste de hipótese. $\\Delta$: diferença entre "
        "as medianas dos dois algoritmos, em porcentagem da mediana do SPEA2, orientada de modo "
        f"que valores positivos favoreçam o IVF/SPEA2.{nota_delta}"
    )

    content = lt.render(
        header=[
            [lt.Span("", 3), lt.Span("$A_{12}$", 2), lt.Span("$\\Delta$ (\\%)", 3)],
            [
                "Métrica",
                "Desfecho (Holm)",
                "$n$",
                "Mediano",
                "$A_{12}\\geq 0{,}71$",
                "Mediano",
                "Mínimo",
                "Máximo",
            ],
        ],
        rows=rows,
        colspec="llcccrrr",
        tabcolsep="5pt",
        caption=(
            "Magnitude da diferença entre o IVF/SPEA2 e o SPEA2 canônico, por desfecho "
            "corrigido: frequência com que uma execução supera a outra e deslocamento "
            "relativo da mediana."
        ),
        label="tab:magnitude_confirmatoria",
        producer=__file__,
        sources=[DETALHES, CONSOLIDADO],
        note=note,
    )
    try:
        for metrica in METRICAS:
            n_fora_ajuste = int(
                ((tabela["metric"] == metrica) & ~tabela["is_full12"]).sum()
            )
            if n_fora_ajuste != 39:
                raise ValueError(
                    f"{metrica}: esperado 39 problemas fora do ajuste, encontrado {n_fora_ajuste}"
                )
        duplicata_maf7 = tabela.loc[
            (tabela["M"] == "M3") & (tabela["Problema"] == "MaF7") & ~tabela["is_full12"]
        ]
        if len(duplicata_maf7) != len(METRICAS):
            raise ValueError("MaF7/M3 fora do ajuste ausente em uma das métricas")

        bruto = pd.read_csv(CONSOLIDADO)
        coorte = filter_submission_synthetic_cohort(bruto)
        coorte = coorte.loc[coorte["Algoritmo"].isin(["IVFSPEA2", "SPEA2"])]
        content_fora_ajuste = _render_magnitude_fora_ajuste(tabela)
        content_sensibilidade = _render_sensibilidade(coorte)
    except ValueError as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 1

    lt.write(OUT, content)
    lt.write(OUT_FORA_AJUSTE, content_fora_ajuste)
    lt.write(OUT_SENSIBILIDADE, content_sensibilidade)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
