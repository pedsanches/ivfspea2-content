#!/usr/bin/env python3
"""Comparação do IVF/SPEA2 com os sete algoritmos comparados (QP5).

Lê:
    data/processed/todas_metricas_consolidado_with_modern.csv  (via filtro de coorte)
    results/tables/claims_summary_instance_details.csv         (``is_full12``: instâncias
        fora do ajuste da calibração, Seção~\\ref{sec:calibracao})

Escreve:
    results/thesis/tab_posicionamento.tex               (matriz completa, 51 instâncias)
    results/thesis/tab_posicionamento_fora_ajuste.tex    (mesmas decisões, restritas às
        39 instâncias fora do ajuste: 24 com M=2, 15 com M=3)

Protocolo, conforme a Seção 5.4: teste de soma de postos de Wilcoxon
(Mann--Whitney U) bicaudal em cada instância, α = 0,05, com correção de
Holm aplicada separadamente por comparador, por número de objetivos e por
métrica. IGD é o desfecho primário e HV o secundário obrigatório. O
``tab_posicionamento_fora_ajuste`` usa as mesmas decisões de Holm da família
completa (28 ou 23 instâncias): a correção nunca é recalculada sobre o
subconjunto fora do ajuste, só filtrada depois.

Para cada contraste, calcula também o tamanho de efeito $A_{12}$ de
Vargha--Delaney orientado (acima de 0,5 favorece o IVF/SPEA2), na mesma
convenção de ``build_tab_magnitude_confirmatoria.py``, e reporta a mediana
entre as instâncias do grupo — sem seleção por significância.

Proibido o reuso de ``results/tables/pairwise_ivf_vs_all.csv``,
``pairwise_ivf_vs_all_hv.csv`` e ``pairwise_vs_spea2_with_modern*.csv``: eles
foram calculados sobre o rótulo misto ``IVFSPEA2`` (execuções 1--60 e
3001--3060) e sem correção de multiplicidade. Este gerador reprocessa o
consolidado a partir do filtro de coorte e falha se a cobertura por
instância, o número de instâncias ou o número de execuções divergirem do
protocolo.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

from ivfspea2.cohorts import filter_submission_synthetic_cohort
from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

CONSOLIDADO = DATA_PROCESSED / "todas_metricas_consolidado_with_modern.csv"
DETALHES = RESULTS_TABLES / "claims_summary_instance_details.csv"
OUT = RESULTS_THESIS / "tab_posicionamento.tex"
OUT_FORA_AJUSTE = RESULTS_THESIS / "tab_posicionamento_fora_ajuste.tex"

ALVO = "IVFSPEA2"

# Os sete algoritmos comparados, nas três famílias da Seção 5.2.1: variantes
# do SPEA2, métodos canônicos de dominância de Pareto e de decomposição,
# abordagens modernas de adaptação de geometria e de pontos de referência.
COMPARADORES = [
    ("MFOSPEA2", "MFO-SPEA2", "Variante do SPEA2"),
    ("SPEA2SDE", "SPEA2+SDE", "Variante do SPEA2"),
    ("NSGAII", "NSGA-II", "Método canônico"),
    ("NSGAIII", "NSGA-III", "Método canônico"),
    ("MOEAD", "MOEA/D", "Método canônico"),
    ("AGEMOEAII", "AGE-MOEA-II", "Abordagem moderna"),
    ("ARMOEA", "AR-MOEA", "Abordagem moderna"),
]
ROTULOS = {chave: rotulo for chave, rotulo, _familia in COMPARADORES}

# A ordem das linhas da matriz: família (título em itálico) -> algoritmos.
# Reaproveitada por ``build_fig_resultados.py`` para o heatmap de A12.
FAMILIAS = [
    ("Variantes do SPEA2", ["MFOSPEA2", "SPEA2SDE"]),
    ("Métodos canônicos", ["NSGAII", "NSGAIII", "MOEAD"]),
    ("Abordagens modernas", ["AGEMOEAII", "ARMOEA"]),
]

# métrica -> maior é melhor
METRICAS = [("IGD", False), ("HV", True)]
OBJETIVOS = ["M2", "M3"]

ALFA = 0.05
N_EXECUCOES = 60
N_INSTANCIAS = {"M2": 28, "M3": 23}
N_FORA_AJUSTE = {"M2": 24, "M3": 15}


def _veredito(
    ivf: np.ndarray, outro: np.ndarray, maior_melhor: bool, rejeita: bool
) -> str:
    """Desfecho de uma instância, na convenção canônica do projeto.

    A direção vem da diferença entre as medianas --- menor mediana de IGD e
    maior mediana de HV favorecem o IVF/SPEA2 ---, e o veredito só existe
    quando o teste rejeita. Fora dele a instância é um empate, nos mesmos
    termos de ``compute_claims_summary.py``.
    """
    if not rejeita:
        return "="
    mediana_ivf, mediana_outro = float(np.median(ivf)), float(np.median(outro))
    if mediana_ivf == mediana_outro:
        return "="
    favorece = mediana_ivf > mediana_outro if maior_melhor else mediana_ivf < mediana_outro
    return "+" if favorece else "-"


def _a12(ivf: np.ndarray, outro: np.ndarray, maior_melhor: bool) -> float:
    """Tamanho de efeito $A_{12}$ de Vargha--Delaney, orientado ao IVF/SPEA2.

    Fração de pares de execuções em que o IVF/SPEA2 é favorecido (IGD menor
    ou HV maior, conforme ``maior_melhor``), empates contando meio. Acima de
    0,5 favorece o IVF/SPEA2. Mesma fórmula de
    ``build_tab_magnitude_confirmatoria.py``.
    """
    diferenca = np.subtract.outer(ivf, outro)
    favorece = diferenca > 0 if maior_melhor else diferenca < 0
    return float(favorece.mean() + 0.5 * (diferenca == 0).mean())


def _contraste(
    bloco: pd.DataFrame, metrica: str, chave: str, maior_melhor: bool
) -> tuple[pd.Series, pd.Series]:
    """Veredito e $A_{12}$ orientado por instância de um contraste.

    Holm é aplicado uma única vez, sobre todas as instâncias do bloco (a
    família completa); quem precisa de um subconjunto filtra depois estas
    séries, sem recalcular a correção.
    """
    problemas: list[str] = []
    pvalores: list[float] = []
    pares: list[tuple[np.ndarray, np.ndarray]] = []
    for problema, grupo in bloco.groupby("Problema"):
        ivf = grupo.loc[grupo["Algoritmo"] == ALVO, metrica].dropna().to_numpy()
        outro = grupo.loc[grupo["Algoritmo"] == chave, metrica].dropna().to_numpy()
        if ivf.size != N_EXECUCOES or outro.size != N_EXECUCOES:
            raise ValueError(
                f"cobertura inesperada em {problema}/{metrica}/{chave}: "
                f"{ivf.size} contra {outro.size} execuções, esperadas {N_EXECUCOES}"
            )
        _, p = mannwhitneyu(ivf, outro, alternative="two-sided")
        problemas.append(problema)
        pvalores.append(float(p))
        pares.append((ivf, outro))

    rejeicoes = multipletests(pvalores, alpha=ALFA, method="holm")[0]
    vereditos = {
        problema: _veredito(ivf, outro, maior_melhor, bool(rejeita))
        for problema, (ivf, outro), rejeita in zip(problemas, pares, rejeicoes, strict=True)
    }
    a12s = {
        problema: _a12(ivf, outro, maior_melhor)
        for problema, (ivf, outro) in zip(problemas, pares, strict=True)
    }
    return pd.Series(vereditos, name="veredito"), pd.Series(a12s, name="a12")


def _contagens(veredito: pd.Series) -> tuple[int, int, int]:
    return (
        int((veredito == "+").sum()),
        int((veredito == "=").sum()),
        int((veredito == "-").sum()),
    )


def _familia_italica(familia: str, largura: int) -> lt.Span:
    return lt.Span(f"\\textit{{{familia}}}", width=largura, align="l")


def _tabela_completa(
    resultados: dict[tuple[str, str, str], tuple[pd.Series, pd.Series]],
    blocos: dict[str, pd.DataFrame],
) -> str:
    header = [
        ["", lt.Span("IGD", width=4, rule=True), lt.Span("HV", width=4, rule=True)],
        [
            "",
            lt.Span("$M = 2$", width=2, rule=True),
            lt.Span("$M = 3$", width=2, rule=True),
            lt.Span("$M = 2$", width=2, rule=True),
            lt.Span("$M = 3$", width=2, rule=True),
        ],
        [
            "Algoritmo",
            "V/E/D", "$A_{12}$",
            "V/E/D", "$A_{12}$",
            "V/E/D", "$A_{12}$",
            "V/E/D", "$A_{12}$",
        ],
    ]

    rows: list[list[object] | object] = []
    for indice_familia, (familia, chaves) in enumerate(FAMILIAS):
        if indice_familia:
            rows.append(lt.Rule)
        rows.append([_familia_italica(familia, 9)])
        for chave in chaves:
            linha: list[object] = [ROTULOS[chave]]
            for metrica, maior_melhor in METRICAS:
                for m in OBJETIVOS:
                    veredito, a12 = resultados[(metrica, m, chave)]
                    # Recomputa o contraste de forma independente, pelo mesmo
                    # procedimento, e confere contra ``resultados`` para
                    # proteger a montagem da matriz de erro de indexação.
                    conferencia, _ = _contraste(blocos[m], metrica, chave, maior_melhor)
                    if not veredito.equals(conferencia):
                        raise ValueError(
                            f"contagens divergentes em {metrica}/{m}/{chave}: a matriz "
                            "não reproduz o procedimento original"
                        )
                    wins, ties, losses = _contagens(veredito)
                    linha.append(fmt.wtl(wins, ties, losses))
                    linha.append(fmt.decimal(float(a12.median())))
            rows.append(linha)

    note = (
        "V/E/D: vitórias/empates/derrotas do IVF/SPEA2 contra cada algoritmo, em "
        f"{N_INSTANCIAS['M2']} instâncias com $M = 2$ e {N_INSTANCIAS['M3']} com $M = 3$; "
        "$A_{12}$: mediana, entre as instâncias, do $A_{12}$ orientado, em que valores "
        "acima de $0{,}5$ favorecem o IVF/SPEA2. Teste de Mann--Whitney bicaudal, "
        "$\\alpha = 0{,}05$, com correção de Holm por algoritmo, por número de "
        f"objetivos e por métrica; {N_EXECUCOES} execuções por algoritmo e instância, "
        "com 100.000 avaliações cada."
    )

    return lt.render(
        header=header,
        rows=rows,
        colspec="l" + "cc" * 4,
        caption=(
            "Comparação do IVF/SPEA2 com os sete algoritmos comparados, por métrica e "
            "número de objetivos."
        ),
        label="tab:posicionamento",
        producer=__file__,
        sources=[CONSOLIDADO],
        note=note,
        tabcolsep="4pt",
    )


def _tabela_fora_ajuste(
    resultados: dict[tuple[str, str, str], tuple[pd.Series, pd.Series]],
    fora_ajuste: dict[str, pd.Index],
) -> str:
    header = [
        ["", lt.Span("IGD", width=2, rule=True), lt.Span("HV", width=2, rule=True)],
        ["Algoritmo", "$M = 2$", "$M = 3$", "$M = 2$", "$M = 3$"],
    ]

    rows: list[list[object] | object] = []
    for indice_familia, (familia, chaves) in enumerate(FAMILIAS):
        if indice_familia:
            rows.append(lt.Rule)
        rows.append([_familia_italica(familia, 5)])
        for chave in chaves:
            linha: list[object] = [ROTULOS[chave]]
            for metrica, _maior_melhor in METRICAS:
                for m in OBJETIVOS:
                    veredito, _a12s = resultados[(metrica, m, chave)]
                    subconjunto = veredito.loc[veredito.index.isin(fora_ajuste[m])]
                    if len(subconjunto) != N_FORA_AJUSTE[m]:
                        raise ValueError(
                            f"{metrica}/{m}/{chave} fora do ajuste tem "
                            f"{len(subconjunto)} instâncias, esperadas {N_FORA_AJUSTE[m]}"
                        )
                    wins, ties, losses = _contagens(subconjunto)
                    linha.append(fmt.wtl(wins, ties, losses))
            rows.append(linha)

    note = (
        f"V/E/D nas {N_FORA_AJUSTE['M2']} instâncias com $M = 2$ e nas "
        f"{N_FORA_AJUSTE['M3']} com $M = 3$ que não participaram da calibração "
        "(Seção~\\ref{sec:calibracao}); decisões da Tabela~\\ref{tab:posicionamento}, "
        "com a correção de Holm calculada na família completa, antes do recorte."
    )

    return lt.render(
        header=header,
        rows=rows,
        colspec="l" + "c" * 4,
        caption=(
            "Comparação do IVF/SPEA2 com os sete algoritmos comparados nas instâncias "
            "fora do ajuste."
        ),
        label="tab:posicionamento_fora_ajuste",
        producer=__file__,
        sources=[CONSOLIDADO, DETALHES],
        note=note,
        tabcolsep="6pt",
    )


def main() -> int:
    if not CONSOLIDADO.exists():
        print(f"ERRO: artefato ausente: {CONSOLIDADO}", file=sys.stderr)
        return 1
    if not DETALHES.exists():
        print(f"ERRO: artefato ausente: {DETALHES}", file=sys.stderr)
        return 1

    bruto = pd.read_csv(CONSOLIDADO)
    coorte = filter_submission_synthetic_cohort(bruto)
    presentes = set(coorte["Algoritmo"].unique())
    ausentes = {chave for chave, _, _ in COMPARADORES if chave not in presentes}
    if ausentes:
        print(f"ERRO: comparadores ausentes na coorte: {sorted(ausentes)}", file=sys.stderr)
        return 1

    detalhes = pd.read_csv(DETALHES)[["metric", "M", "Problema", "is_full12"]]
    inconsistente = detalhes.groupby(["M", "Problema"])["is_full12"].nunique()
    if (inconsistente != 1).any():
        print(
            "ERRO: is_full12 diverge entre métricas para a mesma instância",
            file=sys.stderr,
        )
        return 1
    calibracao = (
        detalhes.drop_duplicates(subset=["M", "Problema"])
        .set_index(["M", "Problema"])["is_full12"]
        .astype(bool)
    )

    blocos: dict[str, pd.DataFrame] = {}
    fora_ajuste: dict[str, pd.Index] = {}
    for m in OBJETIVOS:
        bloco = coorte[coorte["M"] == m]
        blocos[m] = bloco
        if bloco["Problema"].nunique() != N_INSTANCIAS[m]:
            print(
                f"ERRO: {m} tem {bloco['Problema'].nunique()} instâncias, "
                f"esperadas {N_INSTANCIAS[m]}",
                file=sys.stderr,
            )
            return 1
        calibracao_m = calibracao.loc[m]
        instancias_fora = calibracao_m[~calibracao_m].index
        if len(instancias_fora) != N_FORA_AJUSTE[m]:
            print(
                f"ERRO: {m} tem {len(instancias_fora)} instâncias fora do ajuste, "
                f"esperadas {N_FORA_AJUSTE[m]}",
                file=sys.stderr,
            )
            return 1
        fora_ajuste[m] = instancias_fora

    resultados: dict[tuple[str, str, str], tuple[pd.Series, pd.Series]] = {}
    for metrica, maior_melhor in METRICAS:
        for m in OBJETIVOS:
            bloco = blocos[m]
            for chave, _rotulo, _familia in COMPARADORES:
                veredito, a12 = _contraste(bloco, metrica, chave, maior_melhor)
                if len(veredito) != N_INSTANCIAS[m]:
                    print(
                        f"ERRO: {metrica}/{m}/{chave} contrastou "
                        f"{len(veredito)} instâncias",
                        file=sys.stderr,
                    )
                    return 1
                resultados[(metrica, m, chave)] = (veredito, a12)

    lt.write(OUT, _tabela_completa(resultados, blocos))
    lt.write(OUT_FORA_AJUSTE, _tabela_fora_ajuste(resultados, fora_ajuste))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
