#!/usr/bin/env python3
"""Posicionamento do IVF/SPEA2 contra os sete algoritmos comparados (QP5).

Lê:
    data/processed/todas_metricas_consolidado_with_modern.csv  (via filtro de coorte)

Escreve:
    results/thesis/tab_posicionamento.tex

Protocolo, conforme a Seção 5.4: teste de soma de postos de Wilcoxon
(Mann--Whitney U) bicaudal em cada instância, α = 0,05, com correção de
Holm aplicada separadamente por comparador, por número de objetivos e por
métrica. IGD é o desfecho primário e HV o secundário obrigatório.

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
from ivfspea2.paths import DATA_PROCESSED, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

CONSOLIDADO = DATA_PROCESSED / "todas_metricas_consolidado_with_modern.csv"
OUT = RESULTS_THESIS / "tab_posicionamento.tex"

ALVO = "IVFSPEA2"

# Os sete algoritmos comparados, na ordem de grupos da Seção 5.1:
# variantes do próprio hospedeiro, métodos de dominância e decomposição,
# abordagens de adaptação de geometria e de conjunto de referência.
COMPARADORES = [
    ("MFOSPEA2", "MFO-SPEA2", "Variante do hospedeiro"),
    ("SPEA2SDE", "SPEA2+SDE", "Variante do hospedeiro"),
    ("NSGAII", "NSGA-II", "Dominância e decomposição"),
    ("NSGAIII", "NSGA-III", "Dominância e decomposição"),
    ("MOEAD", "MOEA/D", "Dominância e decomposição"),
    ("AGEMOEAII", "AGE-MOEA-II", "Geometria e referências adaptativas"),
    ("ARMOEA", "AR-MOEA", "Geometria e referências adaptativas"),
]

# métrica -> maior é melhor
METRICAS = [("IGD", False), ("HV", True)]
OBJECTIVOS = ["M2", "M3"]

ALFA = 0.05
N_EXECUCOES = 60
N_INSTANCIAS = {"M2": 28, "M3": 23}


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


def _contraste(
    bloco: pd.DataFrame, metrica: str, chave: str, maior_melhor: bool
) -> pd.Series:
    """Contagens de um único contraste:Holm dentro de comparador, M e métrica."""
    valores: list[tuple[float, np.ndarray, np.ndarray]] = []
    for problema, grupo in bloco.groupby("Problema"):
        ivf = grupo.loc[grupo["Algoritmo"] == ALVO, metrica].dropna().to_numpy()
        outro = grupo.loc[grupo["Algoritmo"] == chave, metrica].dropna().to_numpy()
        if ivf.size != N_EXECUCOES or outro.size != N_EXECUCOES:
            raise ValueError(
                f"cobertura inesperada em {problema}/{metrica}/{chave}: "
                f"{ivf.size} contra {outro.size} execuções, esperadas {N_EXECUCOES}"
            )
        _, p = mannwhitneyu(ivf, outro, alternative="two-sided")
        valores.append((float(p), ivf, outro))

    rejeicoes = multipletests([v[0] for v in valores], alpha=ALFA, method="holm")[0]
    vereditos = [
        _veredito(ivf, outro, maior_melhor, bool(rejeita))
        for (_p, ivf, outro), rejeita in zip(valores, rejeicoes, strict=True)
    ]
    n = len(vereditos)
    return pd.Series(
        {
            "wins": vereditos.count("+"),
            "ties": vereditos.count("="),
            "losses": vereditos.count("-"),
            "n": n,
        }
    )


def main() -> int:
    if not CONSOLIDADO.exists():
        print(f"ERRO: artefato ausente: {CONSOLIDADO}", file=sys.stderr)
        return 1

    bruto = pd.read_csv(CONSOLIDADO)
    coorte = filter_submission_synthetic_cohort(bruto)
    presentes = set(coorte["Algoritmo"].unique())
    ausentes = {chave for chave, _, _ in COMPARADORES if chave not in presentes}
    if ausentes:
        print(f"ERRO: comparadores ausentes na coorte: {sorted(ausentes)}", file=sys.stderr)
        return 1

    rows: list[list[str] | object] = []
    for indice_metrica, (metrica, maior_melhor) in enumerate(METRICAS):
        if indice_metrica:
            rows.append(lt.Rule)
        linhas_metrica: list[list[str | object] | object] = []
        for objetivos in OBJECTIVOS:
            grupo_m: list[list[str | object]] = []
            bloco = coorte[coorte["M"] == objetivos]
            if bloco["Problema"].nunique() != N_INSTANCIAS[objetivos]:
                print(
                    f"ERRO: {objetivos} tem {bloco['Problema'].nunique()} instâncias, "
                    f"esperadas {N_INSTANCIAS[objetivos]}",
                    file=sys.stderr,
                )
                return 1
            for chave, rotulo, _grupo in COMPARADORES:
                contagens = _contraste(bloco, metrica, chave, maior_melhor)
                if int(contagens["n"]) != N_INSTANCIAS[objetivos]:
                    print(
                        f"ERRO: {metrica}/{objetivos}/{chave} contrastou "
                        f"{contagens['n']} instâncias",
                        file=sys.stderr,
                    )
                    return 1
                grupo_m.append(
                    [
                        "",
                        "",
                        rotulo,
                        fmt.wtl(contagens["wins"], contagens["ties"], contagens["losses"]),
                        str(int(contagens["n"])),
                    ]
                )
            # O número de objetivos agrupa o bloco inteiro e fica no meio do
            # eixo vertical das sete linhas de comparadores.
            grupo_m[0][1] = lt.Multirow(objetivos.removeprefix("M"), len(grupo_m))
            linhas_metrica.extend(grupo_m)
            linhas_metrica.append(lt.Gap)
        # A métrica agrupa os dois blocos de objetivos; o \addlinespace entre
        # eles não conta como linha.
        linhas_dados = sum(1 for linha in linhas_metrica if linha is not lt.Gap)
        linhas_metrica[0][0] = lt.Multirow(metrica, linhas_dados)
        rows.extend(linhas_metrica)

    note = (
        "V/E/D: vitórias/empates/derrotas do IVF/SPEA2 contra o comparador; "
        "$n$: número de instâncias. Teste de soma de postos de Wilcoxon "
        "(Mann--Whitney U) bicaudal, $\\alpha = 0{,}05$, com correção de Holm "
        "aplicada separadamente por comparador, por número de objetivos e por "
        "métrica. IGD: menor é melhor; HV: maior é melhor. A coorte é a da "
        "comparação principal: IVF/SPEA2 nas execuções 3001--3060 contra cada "
        "comparador nas execuções 1--60, 60 execuções por algoritmo e instância, "
        "orçamento de 100.000 avaliações. Por isso as contagens desta tabela e as "
        "da comparação principal, na Tabela~\\ref{tab:confirmatorio_wtl}, não são observações "
        "independentes. Cada linha é um contraste par a par entre algoritmos "
        "distintos e as contagens não se somam entre comparadores. Um empate é "
        "ausência de diferença detectável, e não equivalência. O posto médio da "
        "Figura~\\ref{fig:posto_medio} é descritivo e não substitui estas contagens."
    )

    content = lt.render(
        header=["Métrica", "$M$", "Comparador", "V/E/D", "$n$"],
        rows=rows,
        colspec="cclcc",
        caption=(
            "Posicionamento do IVF/SPEA2 frente aos sete algoritmos comparados, "
            "por métrica, número de objetivos e comparador, com correção de Holm "
            "dentro de cada contraste."
        ),
        label="tab:posicionamento",
        producer=__file__,
        sources=[CONSOLIDADO],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
