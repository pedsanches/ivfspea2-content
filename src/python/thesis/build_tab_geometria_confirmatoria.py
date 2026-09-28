#!/usr/bin/env python3
"""A geometria da fronteira explica as derrotas? Tabela das duas famílias.

Esta é a tabela que responde à pergunta mais contestável da dissertação. O
texto afirmava que as derrotas do acoplamento ocorrem em fronteiras
desconectadas ou irregulares; a classificação do próprio projeto,
``config/hosts_front_geometry.csv``, não sustenta isso. A tabela põe lado a
lado as duas famílias que testam a associação, de modo que o leitor veja onde
elas concordam e onde não.

As duas famílias diferem em coorte, em número de execuções e em procedimento
de correção, e por isso as suas contagens **não se somam**. O que a tabela
permite comparar é a direção e a magnitude do efeito, não os totais.

Duas grandezas por grupo de geometria:

* contagens de vitória/empate/derrota, que dependem do poder do teste e do
  procedimento de correção;
* mediana do $A_{12}$ orientado, que não depende de decisão binária.

A distinção importa porque as duas famílias exibem gradiente semelhante na
segunda e contagens diferentes na primeira. Número de execuções, teste,
alinhamento e correção mudam juntos entre as famílias e não foram isolados, e
o par IVF/SPEA2 da família de hospedeiros é um subconjunto da coorte
confirmatória: a semelhança do gradiente não é corroboração independente.

Lê:
    results/tables/claims_summary_instance_details.csv   (desfecho por instância, Holm)
    data/processed/todas_metricas_consolidado_with_modern.csv  (via filtro de coorte)
    config/hosts_front_geometry.csv                      (classificação geométrica)
    results/tables/hosts_geometry_summary.csv            (família de hospedeiros)

Escreve: results/thesis/tab_geometria_confirmatoria.tex
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

import latex_table as lt
import ptbr_format as fmt
from ivfspea2.cohorts import filter_submission_synthetic_cohort
from ivfspea2.paths import CONFIG, DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS

DETALHES = RESULTS_TABLES / "claims_summary_instance_details.csv"
CONSOLIDADO = DATA_PROCESSED / "todas_metricas_consolidado_with_modern.csv"
GEOMETRIA = CONFIG / "hosts_front_geometry.csv"
HOSTS = RESULTS_TABLES / "hosts_geometry_summary.csv"
OUT = RESULTS_THESIS / "tab_geometria_confirmatoria.tex"

GRUPOS = [("regular", "Regular"), ("irregular", "Irregular")]
# Contagens até dez por extenso na nota, como no texto ("as duas derrotas").
_POR_EXTENSO = dict(
    enumerate(["zero", "uma", "duas", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"])
)


def _mapa_geometria() -> dict[str, str]:
    geo = pd.read_csv(GEOMETRIA)
    chave = geo["problem"].str.upper() + "_M" + geo["M"].astype(str)
    return dict(zip(chave, geo["geometry_group"], strict=True))


def _a12_confirmatorio(mapa: dict[str, str]) -> pd.DataFrame:
    """A12 orientado por instância na coorte confirmatória completa.

    Orientado significa que valores acima de 0,5 favorecem o IVF/SPEA2. Como a
    IGD é de minimização, isso é a fração de pares em que a execução do
    IVF/SPEA2 obtém o menor valor, com empates contando meio par.
    """
    bruto = pd.read_csv(CONSOLIDADO)
    coorte = filter_submission_synthetic_cohort(bruto)
    coorte = coorte[coorte["Algoritmo"].isin(["IVFSPEA2", "SPEA2"])]

    linhas = []
    for (problema, m), grupo in coorte.groupby(["Problema", "M"]):
        ivf = grupo.loc[grupo["Algoritmo"] == "IVFSPEA2", "IGD"].dropna().to_numpy()
        base = grupo.loc[grupo["Algoritmo"] == "SPEA2", "IGD"].dropna().to_numpy()
        if ivf.size == 0 or base.size == 0:
            continue
        diferenca = np.subtract.outer(ivf, base)
        a12 = float((diferenca < 0).mean() + 0.5 * (diferenca == 0).mean())
        linhas.append(
            {"Problema": problema, "M": m, "a12": a12, "geo": mapa.get(f"{problema.upper()}_{m}")}
        )
    return pd.DataFrame(linhas).dropna(subset=["geo"])


def main() -> int:
    faltando = [p for p in (DETALHES, CONSOLIDADO, GEOMETRIA, HOSTS) if not p.exists()]
    if faltando:
        for path in faltando:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return 1

    mapa = _mapa_geometria()

    detalhes = pd.read_csv(DETALHES)
    detalhes = detalhes[detalhes["metric"] == "IGD"].copy()
    detalhes["geo"] = (detalhes["Problema"].str.upper() + "_" + detalhes["M"]).map(mapa)
    if detalhes["geo"].isna().any():
        ausentes = sorted(detalhes.loc[detalhes["geo"].isna(), "Problema"].unique())
        print(f"ERRO: sem classificação geométrica para {ausentes}", file=sys.stderr)
        return 1

    a12 = _a12_confirmatorio(mapa)
    hosts = pd.read_csv(HOSTS)
    hosts = hosts[
        (hosts["host"] == "IVFSPEA2")
        & (hosts["metric"] == "IGD")
        & (hosts["geometry_level"] == "geometry_group")
    ]

    rows: list[list[str] | object] = []
    for posicao, (chave, rotulo) in enumerate(GRUPOS):
        bloco = detalhes[detalhes["geo"] == chave]
        vitorias = int((bloco["indicator_holm"] == "+").sum())
        derrotas = int((bloco["indicator_holm"] == "-").sum())
        empates = len(bloco) - vitorias - derrotas
        rows.append(
            [
                "Confirmatória" if posicao == 0 else "",
                rotulo,
                str(len(bloco)),
                fmt.wtl(vitorias, empates, derrotas),
                fmt.decimal(float(a12.loc[a12["geo"] == chave, "a12"].median())),
            ]
        )

    rows.append(lt.Rule)

    for posicao, (chave, rotulo) in enumerate(GRUPOS):
        linha = hosts[hosts["geometry"] == chave].iloc[0]
        rows.append(
            [
                "Hospedeiros" if posicao == 0 else "",
                rotulo,
                str(int(linha["n_instances"])),
                fmt.wtl(int(linha["wins"]), int(linha["ties"]), int(linha["losses"])),
                # median_a12_ivf já vem orientado na fonte: acima de 0,5 favorece o IVF.
                fmt.decimal(float(linha["median_a12_ivf"])),
            ]
        )

    p_conf = float(
        mannwhitneyu(
            a12.loc[a12["geo"] == "regular", "a12"],
            a12.loc[a12["geo"] == "irregular", "a12"],
        ).pvalue
    )
    # A nota afirma que a diferença não atinge significância.
    if p_conf < 0.05:
        print(f"ERRO: a nota supõe p >= 0,05 entre geometrias; p = {p_conf:.4f}", file=sys.stderr)
        return 1

    # Na família confirmatória, as derrotas em fronteira irregular vêm de um só
    # problema; a nota diz isso, e o gerador falha se deixar de ser verdade.
    irregulares = detalhes[detalhes["geo"] == "irregular"]
    derrotas_irr = irregulares[irregulares["indicator_holm"] == "-"]
    problemas_irr = sorted(derrotas_irr["Problema"].unique())
    if len(problemas_irr) != 1:
        print(
            f"ERRO: a nota supõe um único problema entre as derrotas irregulares; há {problemas_irr}",
            file=sys.stderr,
        )
        return 1
    valores_m = " e ".join(f"$M = {m[-1]}$" for m in sorted(derrotas_irr["M"]))
    # MaF7 é implementado como o DTLZ7: cada M em que ambos são irregulares
    # conta uma função a menos.
    repeticoes = sum(
        1
        for m in irregulares["M"].unique()
        if {"DTLZ7", "MaF7"} <= set(irregulares.loc[irregulares["M"] == m, "Problema"])
    )

    # A leitura das duas famílias lado a lado (a taxa de vitória satura com 60
    # execuções e cai com 30) está no texto que cita a tabela; a nota fica com
    # protocolo, definições e as ressalvas sobre o que n e as derrotas contam.
    note = (
        "Famílias com protocolos distintos: a confirmatória usa 60 execuções por configuração "
        "e correção de Holm; a de hospedeiros usa 30 e Benjamini--Hochberg, e o seu par "
        "IVF/SPEA2 usa um subconjunto da coorte confirmatória. As contagens das duas famílias "
        "não se somam. O $A_{12}$ é orientado de modo que valores acima de $0{,}5$ favoreçam o "
        "IVF/SPEA2. A diferença de $A_{12}$ entre geometrias não atinge significância na "
        f"família confirmatória ($p = {fmt.decimal(p_conf).strip('$')}$, Mann--Whitney), e a "
        "estratificação é descritiva nas duas. Na família confirmatória, as "
        f"{_POR_EXTENSO.get(len(derrotas_irr), str(len(derrotas_irr)))} derrotas irregulares "
        f"são um único problema, {problemas_irr[0]}, "
        f"com {valores_m}, e as {len(irregulares)} instâncias irregulares correspondem a "
        f"{_POR_EXTENSO.get(len(irregulares) - repeticoes, str(len(irregulares) - repeticoes))} "
        "funções, porque o MaF7 repete o DTLZ7 "
        "(Seção~\\ref{sec:suites})."
    )

    content = lt.render(
        header=[
            "Família",
            "Geometria",
            "$n$",
            "V/E/D (IGD)",
            "$A_{12}$ mediano",
        ],
        rows=rows,
        colspec="llccc",
        caption=(
            "Vitórias, empates e derrotas em IGD e $A_{12}$ mediano do IVF/SPEA2 contra o "
            "SPEA2, por geometria da fronteira de Pareto, nas duas famílias que testam a "
            "associação."
        ),
        label="tab:geometria_confirmatoria",
        producer=__file__,
        sources=[DETALHES, CONSOLIDADO, GEOMETRIA, HOSTS],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
