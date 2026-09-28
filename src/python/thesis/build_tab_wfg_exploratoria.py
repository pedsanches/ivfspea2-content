#!/usr/bin/env python3
"""Exploração descritiva da suíte WFG: propriedades declaradas e desfecho corrigido.

A família confirmatória concentra na WFG as quatro derrotas corrigidas do
IVF/SPEA2. Esta tabela abre a suíte por função e por configuração para
restringir a hipótese formulada na Discussão, sem testá-la:

* o desfecho de cada configuração é o veredito de Holm da auditoria canônica,
  calculado na família completa de cada número de objetivos e de cada métrica;
  nenhuma correção é reaplicada aos grupos, formados depois de se observar a
  concentração das derrotas;
* as propriedades (separabilidade, modalidade, viés) são das funções, segundo a
  tabela dos autores da suíte transcrita em ``config/wfg_properties.csv``; cada
  função aparece em duas configurações, e as linhas de resumo somam
  configurações, não funções independentes;
* $\\Delta$ é a diferença relativa das medianas de IGD, calculada como nas
  tabelas por instância, a partir dos mesmos artefatos.

Lê:
    results/tables/claims_summary_instance_details.csv  (veredito de Holm, calibração)
    results/tables/igd_per_instance_M2.csv, igd_per_instance_M3.csv  (medianas, D)
    config/wfg_properties.csv                           (propriedades das funções)

Escreve: results/thesis/tab_wfg_exploratoria.tex
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import CONFIG, RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

DETALHES = RESULTS_TABLES / "claims_summary_instance_details.csv"
MEDIANAS = {m: RESULTS_TABLES / f"igd_per_instance_M{m}.csv" for m in (2, 3)}
PROPRIEDADES = CONFIG / "wfg_properties.csv"
OUT = RESULTS_THESIS / "tab_wfg_exploratoria.tex"

FUNCOES = [f"WFG{i}" for i in range(1, 10)]
VEREDITO = {"+": "$+$", "-": "$-$", "=": "$=$"}
SEPARAVEL = {"yes": "Sim", "no": "Não"}
MODALIDADE = {
    "unimodal": "Unimodal",
    "multimodal": "Multimodal",
    "deceptive": "Enganosa",
    "multimodal_deceptive": "Multimodal, enganosa",
    "unimodal_fm_multimodal": "Unimodal ($f_M$ multimodal)",
}
VIES = {
    "none": "---",
    "polynomial_flat": "Polinomial, plano",
    "parameter_dependent": "Dependente de parâmetro",
}
# D declarado nas tabelas por instância e nos runners; K é o padrão da
# plataforma (M - 1), e L = D - K. O gerador confere D e deriva K e L.
D_ESPERADO = {2: 11, 3: 12}


def _carregar() -> tuple[pd.DataFrame, pd.DataFrame, dict[int, pd.DataFrame]]:
    faltando = [p for p in (DETALHES, PROPRIEDADES, *MEDIANAS.values()) if not p.exists()]
    if faltando:
        raise FileNotFoundError(", ".join(str(p) for p in faltando))
    detalhes = pd.read_csv(DETALHES)
    detalhes = detalhes[detalhes["Problema"].isin(FUNCOES)]
    props = pd.read_csv(PROPRIEDADES, dtype=str).set_index("problem")
    if sorted(props.index) != sorted(FUNCOES):
        raise ValueError(f"{PROPRIEDADES}: esperava exatamente {FUNCOES}")
    for coluna, dominio in (("separable", SEPARAVEL), ("modality", MODALIDADE), ("bias", VIES)):
        desconhecidos = sorted(set(props[coluna]) - set(dominio))
        if desconhecidos:
            raise ValueError(f"{PROPRIEDADES}: valores desconhecidos em {coluna}: {desconhecidos}")
    medianas = {
        m: pd.read_csv(caminho).set_index("Problema").loc[FUNCOES]
        for m, caminho in MEDIANAS.items()
    }
    for m, tabela in medianas.items():
        if not (tabela["D"] == D_ESPERADO[m]).all():
            raise ValueError(f"{MEDIANAS[m]}: D diferente de {D_ESPERADO[m]} em alguma função WFG")
    esperado = len(FUNCOES) * 2 * 2
    if len(detalhes) != esperado:
        raise ValueError(f"{DETALHES}: esperava {esperado} linhas WFG, encontrei {len(detalhes)}")
    return detalhes, props, medianas


def _veredito(detalhes: pd.DataFrame, metrica: str, m: int, funcao: str) -> tuple[str, bool]:
    linha = detalhes[
        (detalhes["metric"] == metrica)
        & (detalhes["M"] == f"M{m}")
        & (detalhes["Problema"] == funcao)
    ]
    if len(linha) != 1:
        raise ValueError(f"{DETALHES}: {funcao} M{m} {metrica} ausente ou duplicado")
    return str(linha["indicator_holm"].iloc[0]), bool(linha["is_full12"].iloc[0])


def _delta_igd(medianas: pd.DataFrame, funcao: str) -> float:
    ivf = float(medianas.loc[funcao, "IVFSPEA2_median"])
    base = float(medianas.loc[funcao, "SPEA2_median"])
    return 100.0 * (base - ivf) / abs(base)


def _vde(vereditos: list[str]) -> str:
    return fmt.wtl(vereditos.count("+"), vereditos.count("="), vereditos.count("-"))


def build() -> str:
    detalhes, props, medianas = _carregar()

    linhas: list[list[str] | object] = []
    por_funcao: dict[str, dict[tuple[str, int], str]] = {}
    for funcao in FUNCOES:
        celulas = [
            funcao,
            SEPARAVEL[props.loc[funcao, "separable"]],
            MODALIDADE[props.loc[funcao, "modality"]],
            VIES[props.loc[funcao, "bias"]],
        ]
        por_funcao[funcao] = {}
        for m in (2, 3):
            for metrica in ("IGD", "HV"):
                veredito, calibracao = _veredito(detalhes, metrica, m, funcao)
                por_funcao[funcao][(metrica, m)] = veredito
                marca = "$^{\\dagger}$" if calibracao and metrica == "IGD" else ""
                celulas.append(f"{VEREDITO[veredito]}{marca}")
            celulas.append(fmt.signed(_delta_igd(medianas[m], funcao), places=2))
        linhas.append(celulas)

    linhas.append(lt.Rule)
    grupos = [
        ("yes", "Separáveis"),
        ("no", "Não separáveis"),
        (None, "WFG"),
    ]
    for chave, rotulo in grupos:
        membros = [f for f in FUNCOES if chave is None or props.loc[f, "separable"] == chave]
        celulas: list[str | lt.Span] = [lt.Span(f"{rotulo} ({len(membros)} funções)", 4, "l")]
        for m in (2, 3):
            for metrica in ("IGD", "HV"):
                celulas.append(_vde([por_funcao[f][(metrica, m)] for f in membros]))
            celulas.append("")
        linhas.append(celulas)

    k = {m: m - 1 for m in (2, 3)}
    l_dist = {m: D_ESPERADO[m] - k[m] for m in (2, 3)}
    if l_dist[2] != l_dist[3]:
        raise ValueError("L difere entre as configurações; a nota precisa ser revista")
    nota = (
        "Exploração descritiva, formulada depois de se observar a concentração das derrotas na "
        "WFG; não é teste de hipótese. Vereditos do IVF/SPEA2 contra o SPEA2 canônico: os das "
        "Tabelas por instância (Mann--Whitney bicaudal, Holm por número de objetivos e por "
        "métrica na família completa, coorte confirmatória de 60 execuções por algoritmo); "
        "$+$ favorece o IVF/SPEA2, $-$ favorece o SPEA2 e $=$ indica ausência de diferença "
        "detectável. Nenhuma correção é reaplicada aos grupos. $\\Delta$: diferença relativa das "
        "medianas de IGD, positiva quando favorece o IVF/SPEA2. $^{\\dagger}$ configuração usada "
        "na calibração de parâmetros. Propriedades das funções segundo a tabela dos autores da "
        "suíte~\\cite{huband2006review}. Cada função aparece em duas configurações: $M=2$ com "
        f"$D={D_ESPERADO[2]}$ e $M=3$ com $D={D_ESPERADO[3]}$; na plataforma, o parâmetro de "
        f"posição é $K=M-1$ ({k[2]} e {k[3]}) e o de distância, $L=D-K={l_dist[2]}$ nos dois "
        "casos. As linhas de resumo contam configurações, e não funções independentes, e as "
        "propriedades variam juntas entre as funções."
    )

    header = [
        [
            lt.Span("", 4),
            lt.Span("$M=2$", 3),
            lt.Span("$M=3$", 3),
        ],
        [
            "Função", "Separável", "Modalidade", "Viés",
            "IGD", "HV", "$\\Delta$ (\\%)",
            "IGD", "HV", "$\\Delta$ (\\%)",
        ],
    ]
    return lt.render(
        header=header,
        rows=linhas,
        colspec="llLLccrccr",
        caption=(
            "Exploração descritiva da suíte WFG: propriedades das funções e desfecho corrigido do "
            "IVF/SPEA2 contra o SPEA2 em cada configuração."
        ),
        short_caption="Exploração descritiva da suíte WFG",
        label="tab:wfg_exploratoria",
        producer=__file__,
        sources=[DETALHES, MEDIANAS[2], MEDIANAS[3], PROPRIEDADES],
        note=nota,
        tabcolsep="4pt",
    )


def main() -> int:
    try:
        lt.write(OUT, build())
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
