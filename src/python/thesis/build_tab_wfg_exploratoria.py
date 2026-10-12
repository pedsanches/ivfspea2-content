#!/usr/bin/env python3
"""Exploração descritiva da suíte WFG: separabilidade declarada e desfecho corrigido.

A família da comparação principal concentra na WFG as quatro derrotas corrigidas do
IVF/SPEA2. Esta tabela abre a suíte por função e por configuração para
restringir a hipótese formulada na Discussão, sem testá-la:

* o desfecho de cada configuração é o veredito de Holm da auditoria canônica,
  calculado na família completa de cada número de objetivos e de cada métrica;
  nenhuma correção é reaplicada aos grupos, formados depois de se observar a
  concentração das derrotas;
* a separabilidade é da função, segundo a tabela dos autores da suíte transcrita
  em ``config/wfg_properties.csv``; as demais propriedades dessa tabela
  (modalidade e viés) são validadas aqui e descritas na prosa da Discussão, não
  na tabela; cada função aparece em duas configurações, e as linhas de resumo
  somam configurações, não funções independentes;
* $\\Delta$ é a diferença relativa das medianas de IGD, calculada como nas
  tabelas por instância, a partir dos mesmos artefatos.

O protocolo, a origem das propriedades, os parâmetros de posição e de distância
e a leitura das linhas de resumo ficam na prosa da seção que cita a tabela; a
nota traz só o que é preciso para ler as células.

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
# Domínios das colunas que a tabela não exibe, mas que a prosa da Discussão
# descreve; validar aqui mantém o CSV e o texto sob a mesma fonte.
MODALIDADE = {
    "unimodal",
    "multimodal",
    "deceptive",
    "multimodal_deceptive",
    "unimodal_fm_multimodal",
}
VIES = {"none", "polynomial_flat", "parameter_dependent"}
# D declarado nas tabelas por instância e nos runners; a prosa da Discussão
# deriva K = M - 1 e L = D - K. O gerador confere D.
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
        celulas: list[str | lt.Span] = [lt.Span(f"{rotulo} ({len(membros)} funções)", 2, "l")]
        for m in (2, 3):
            for metrica in ("IGD", "HV"):
                celulas.append(_vde([por_funcao[f][(metrica, m)] for f in membros]))
            celulas.append("")
        linhas.append(celulas)

    nota = (
        "Vereditos corrigidos das tabelas por instância da comparação principal: $+$ favorece "
        "o IVF/SPEA2, $-$ favorece o SPEA2 e $=$ indica ausência de diferença detectável. "
        "$\\Delta$: diferença relativa das medianas de IGD, positiva quando favorece o "
        "IVF/SPEA2. $^{\\dagger}$ instância usada na calibração."
    )

    header = [
        [
            lt.Span("", 2),
            lt.Span("$M=2$", 3),
            lt.Span("$M=3$", 3),
        ],
        [
            "Função", "Separável",
            "IGD", "HV", "$\\Delta$ (\\%)",
            "IGD", "HV", "$\\Delta$ (\\%)",
        ],
    ]
    return lt.render(
        header=header,
        rows=linhas,
        colspec="llccrccr",
        caption=(
            "Resultado corrigido do IVF/SPEA2 contra o SPEA2 nas instâncias da suíte WFG, por "
            "separabilidade da função."
        ),
        short_caption="Resultado corrigido do IVF/SPEA2 contra o SPEA2 na suíte WFG",
        label="tab:wfg_exploratoria",
        producer=__file__,
        sources=[DETALHES, MEDIANAS[2], MEDIANAS[3], PROPRIEDADES],
        note=nota,
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
