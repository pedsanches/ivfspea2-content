#!/usr/bin/env python3
"""Figuras das quatro famílias de evidência de apoio do Capítulo VII.

Regenera, com rótulos em português, as figuras equivalentes às dos três
manuscritos de origem para as famílias de evidência complementares à suíte
da comparação principal: calibração/ablação (SUP), transferência para engenharia
(ENG), compatibilidade entre hospedeiros (HOST) e decisão de ativação (DEC).
A lógica de cada painel foi adaptada de ``src/python/analysis/`` (não
executado por este módulo); nenhum número é inventado, todos vêm dos
artefatos abaixo.

Lê:
    results/tuning_ivfspea2v2/tuning_phase_ranking.csv
    results/engineering_suite/engineering_suite_raw_main.csv
    results/tables/hosts_{ivfspea2,ivfnsgaiii,ivfnsgaii}_igd_stats.csv
    data/processed/dynamic_signal_test.csv (filtrado por early_frac == 0.2,
        com o caso sem rótulo de OQ-12 descartado)

Escreve, em results/thesis/figures/ (canônico) e em
thesis/masters/generated/figures/ (cópia de build):
    fig_calibracao.pdf
    fig_engenharia.pdf
    fig_hospedeiros_a12.pdf
    fig_ativacao_turnover.pdf
"""

from __future__ import annotations

import hashlib
import sys

import numpy as np
import pandas as pd

import ptbr_format as fmt
from ivfspea2.figstyle import apply_paper_style

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from ivfspea2.figio import save_figure
from ivfspea2.paths import DATA_PROCESSED, RESULTS, RESULTS_TABLES, RESULTS_THESIS, THESIS_GENERATED, ensure_dir

TUNING_CSV = RESULTS / "tuning_ivfspea2v2" / "tuning_phase_ranking.csv"
ENGENHARIA_CSV = RESULTS / "engineering_suite" / "engineering_suite_raw_main.csv"
DINAMICA_CSV = DATA_PROCESSED / "dynamic_signal_test.csv"

HOSTS_STEMS = [
    ("ivfspea2", "IVF/SPEA2"),
    ("ivfnsgaiii", "IVF/NSGA-III"),
    ("ivfnsgaii", "IVF/NSGA-II"),
]

LIMIAR_TURNOVER = 0.216

FIG_OUT = RESULTS_THESIS / "figures"
FIG_MIRROR = THESIS_GENERATED / "figures"


def _fmt(valor: float, casas: int = 2) -> str:
    """Formata um número em ponto-fixo com vírgula decimal pt-BR."""
    return fmt.plain(valor, casas)


def _cor_texto(cmap, norm: Normalize, valor: float) -> str:
    """Preto sobre células claras e branco sobre escuras, pela luminância da cor."""
    r, g, b, _ = cmap(norm(valor))
    return "black" if 0.299 * r + 0.587 * g + 0.114 * b > 0.5 else "white"


def _salvar(fig: plt.Figure, nome: str) -> None:
    save_figure(fig, nome, [ensure_dir(FIG_OUT), ensure_dir(FIG_MIRROR)])
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figura 1 — calibração (família SUP)
# ---------------------------------------------------------------------------

PERFIS_FASE_B = {
    "B01": "AR",
    "B02": "EAR-PA",
    "B03": "EAR-P",
    "B04": "EAR-T",
    "B05": "EAR-N",
}


def _pivotar(df: pd.DataFrame, r_vals: list[float], c_vals: list[float]) -> np.ndarray:
    pivot = df.pivot(index="R", columns="C", values="MeanCombinedRank")
    return pivot.reindex(index=r_vals, columns=c_vals).values


def _painel_grade(
    ax: plt.Axes,
    dados: np.ndarray,
    r_vals: list[float],
    c_vals: list[float],
    estrela_r: float,
    estrela_c: float,
    titulo: str,
    norm: Normalize,
    cmap,
):
    im = ax.imshow(dados, cmap=cmap, aspect="auto", origin="lower", norm=norm)
    for i in range(len(r_vals)):
        for j in range(len(c_vals)):
            val = dados[i, j]
            if np.isnan(val):
                continue
            ax.text(j, i, _fmt(val), ha="center", va="center", fontsize=7.5, color=_cor_texto(cmap, norm, val), fontweight="bold")

    try:
        r_idx = r_vals.index(estrela_r)
        c_idx = c_vals.index(estrela_c)
        ax.plot(
            c_idx + 0.33, r_idx + 0.33, marker="*", color="red", markersize=11,
            markeredgecolor="white", markeredgewidth=0.7, zorder=10,
        )
    except ValueError:
        print(f"AVISO: estrela em (r={estrela_r}, c={estrela_c}) fora da grade", file=sys.stderr)

    ax.set_xticks(range(len(c_vals)))
    ax.set_xticklabels([_fmt(v) for v in c_vals], fontsize=8)
    ax.set_yticks(range(len(r_vals)))
    ax.set_yticklabels([_fmt(v, 3) for v in r_vals], fontsize=8)
    ax.set_xlabel("Tamanho da coleta ($c$)", fontsize=9)
    ax.set_ylabel("Taxa de execução ($r$)", fontsize=9)
    ax.set_title(titulo, fontsize=9, fontweight="bold", pad=6)
    ax.grid(False)
    return im


def _painel_barras(ax: plt.Axes, fase_b: pd.DataFrame, titulo: str, norm: Normalize, cmap) -> None:
    fase_b = fase_b.sort_values("MeanCombinedRank", ascending=True).copy()
    rotulos = [PERFIS_FASE_B.get(cid, cid) for cid in fase_b["ConfigID"]]
    postos = fase_b["MeanCombinedRank"].to_numpy()
    cores = [cmap(norm(v)) for v in postos]

    y = np.arange(len(rotulos))
    barras = ax.barh(y, postos, color=cores, edgecolor="white", linewidth=0.5)
    ax.plot(
        postos[0] + 0.04, y[0], marker="*", color="red", markersize=11,
        markeredgecolor="white", markeredgewidth=0.7, zorder=10, clip_on=False,
    )
    for i, val in enumerate(postos):
        ax.text(val - 0.015, y[i], _fmt(val), ha="right", va="center", fontsize=7.5, color=_cor_texto(cmap, norm, val), fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(rotulos, fontsize=8)
    ax.set_xlabel("Posto médio combinado", fontsize=9)
    ax.set_xlim(0, norm.vmax * 1.08)
    ax.xaxis.set_major_formatter(fmt.axis_formatter())
    ax.invert_yaxis()
    ax.set_title(titulo, fontsize=9, fontweight="bold", pad=6)
    ax.grid(False)
    del barras


def figura_calibracao() -> bool:
    if not TUNING_CSV.exists():
        print(f"ERRO: artefato ausente: {TUNING_CSV}", file=sys.stderr)
        return False

    df = pd.read_csv(TUNING_CSV)

    fase_a = df[(df["Phase"] == "A") & (df["Cycles"] == 2)].copy()
    r_a = sorted(fase_a["R"].unique())
    c_a = sorted(fase_a["C"].unique())
    dados_a = _pivotar(fase_a, r_a, c_a)

    fase_b = df[df["Phase"] == "B"].copy()

    fase_c = df[(df["Phase"] == "C") & (df["MutRate"] == 0.3) & (df["VarRate"] == 0.1)].copy()
    r_c = sorted(fase_c["R"].unique())
    c_c = sorted(fase_c["C"].unique())
    dados_c = _pivotar(fase_c, r_c, c_c)

    todos = np.concatenate(
        [dados_a[~np.isnan(dados_a)], fase_b["MeanCombinedRank"].to_numpy(), dados_c[~np.isnan(dados_c)]]
    )
    norm = Normalize(vmin=float(todos.min()), vmax=float(todos.max()))
    cmap = plt.get_cmap("cividis_r")

    fig = plt.figure(figsize=(8.6, 3.3))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1.05, 0.8, 0.05], wspace=0.55)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    cax = fig.add_subplot(gs[0, 3])

    _painel_grade(ax_a, dados_a, r_a, c_a, 0.200, 0.16, "(a) Fase A \u2014 varredura ampla", norm, cmap)
    _painel_barras(ax_b, fase_b, "(b) Fase B \u2014 perfil de operador", norm, cmap)
    im_c = _painel_grade(ax_c, dados_c, r_c, c_c, 0.225, 0.12, "(c) Fase C \u2014 refinamento local", norm, cmap)
    ax_c.set_ylabel("")

    cbar = fig.colorbar(im_c, cax=cax)
    cbar.set_label("Posto médio combinado\n(menor é melhor)", fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    cbar.ax.yaxis.set_major_formatter(fmt.axis_formatter())

    fig.subplots_adjust(left=0.07, right=0.95, bottom=0.20, top=0.86)
    _salvar(fig, "fig_calibracao.pdf")
    return True


# ---------------------------------------------------------------------------
# Figura 2 — engenharia (família ENG)
# ---------------------------------------------------------------------------

PROBLEMAS_ENG = ["RWMOP9", "RWMOP21", "RWMOP8"]
ROTULOS_PROBLEMA_ENG = {
    "RWMOP9": "RWMOP9 ($M=2$)",
    "RWMOP21": "RWMOP21 ($M=2$)",
    "RWMOP8": "RWMOP8 ($M=3$)",
}
ORDEM_ALGORITMO_ENG = [
    "IVFSPEA2", "SPEA2", "MFOSPEA2", "SPEA2SDE", "NSGAII", "NSGAIII", "MOEAD", "AGEMOEAII", "ARMOEA",
]
ROTULO_ALGORITMO_ENG = {
    "IVFSPEA2": "IVF/SPEA2",
    "SPEA2": "SPEA2",
    "MFOSPEA2": "MFO-SPEA2",
    "SPEA2SDE": "SPEA2+SDE",
    "NSGAII": "NSGA-II",
    "NSGAIII": "NSGA-III",
    "MOEAD": "MOEA/D",
    "AGEMOEAII": "AGE-MOEA-II",
    "ARMOEA": "AR-MOEA",
}


def _resumir_engenharia(df: pd.DataFrame, metrica: str) -> pd.DataFrame:
    linhas = []
    for problema in PROBLEMAS_ENG:
        sub = df[df["Problem"] == problema]
        for algo in ORDEM_ALGORITMO_ENG:
            vals = sub[sub["Algorithm"] == algo][metrica].replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
            if len(vals) == 0:
                linhas.append(
                    {"Problema": problema, "Algoritmo": algo, "Exibicao": ROTULO_ALGORITMO_ENG[algo],
                     "n_valido": 0, "mediana": np.nan, "q1": np.nan, "q3": np.nan}
                )
                continue
            q1, mediana, q3 = np.percentile(vals, [25, 50, 75])
            linhas.append(
                {"Problema": problema, "Algoritmo": algo, "Exibicao": ROTULO_ALGORITMO_ENG[algo],
                 "n_valido": int(len(vals)), "mediana": float(mediana), "q1": float(q1), "q3": float(q3)}
            )
    return pd.DataFrame(linhas)


def _painel_engenharia(ax: plt.Axes, dados: pd.DataFrame, metrica: str, problema: str) -> None:
    keep = dados[dados["Problema"] == problema].copy()
    validos = keep[keep["n_valido"] > 0].copy()
    if validos.empty:
        ax.text(0.5, 0.5, "Sem execuções válidas", ha="center", va="center", fontsize=15)
        return

    ascendente = metrica == "IGD"
    validos = validos.sort_values("mediana", ascending=ascendente)

    y = np.arange(len(validos))
    med = validos["mediana"].to_numpy()
    xerr = np.vstack([med - validos["q1"].to_numpy(), validos["q3"].to_numpy() - med])

    cores = ["#2166AC" if a == "IVFSPEA2" else "#A9A9A9" for a in validos["Algoritmo"]]
    marcadores = ["o" if a == "IVFSPEA2" else "s" for a in validos["Algoritmo"]]

    for i in range(len(validos)):
        ax.errorbar(
            med[i], y[i], xerr=[[xerr[0, i]], [xerr[1, i]]], fmt=marcadores[i],
            color=cores[i], ecolor=cores[i], elinewidth=1.3, capsize=2.5, markersize=5,
            markeredgecolor="black", markeredgewidth=0.5, zorder=3,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(validos["Exibicao"].tolist(), fontsize=12)
    ax.invert_yaxis()
    ax.tick_params(axis="x", labelsize=12)

    # A direção de cada indicador está na legenda LaTeX; repeti-la aqui produzia
    # um rótulo largo o bastante para ser cortado na borda direita da página.
    if metrica == "IGD":
        ax.set_xscale("log")
        ax.set_xlabel("IGD: mediana e quartis", fontsize=12)
    else:
        ax.set_xlabel("HV: mediana e quartis", fontsize=12)
        ax.xaxis.set_major_formatter(fmt.axis_formatter())

    # Os rótulos "n=" vivem fora da área de dados (coordenada de eixo em x,
    # dado em y), para nunca colidir com o marcador de mediana ou a barra de
    # IQR do algoritmo mais próximo da borda direita --- ambos podem chegar
    # perto de x_max, especialmente na coluna de HV.
    ax.margins(x=0.10)
    trans_rotulo = ax.get_yaxis_transform()
    for yi, n in zip(y, validos["n_valido"].to_numpy()):
        ax.text(
            1.04, yi, f"$n$={n}", transform=trans_rotulo, ha="left", va="center",
            fontsize=11, color="#333333", clip_on=False,
        )

    ax.set_title(ROTULOS_PROBLEMA_ENG[problema], fontsize=14)


def figura_engenharia() -> bool:
    if not ENGENHARIA_CSV.exists():
        print(f"ERRO: artefato ausente: {ENGENHARIA_CSV}", file=sys.stderr)
        return False

    df = pd.read_csv(ENGENHARIA_CSV)
    df = df[df["Stage"] == "MAIN"].copy()

    resumo_igd = _resumir_engenharia(df, "IGD_PF")
    resumo_hv = _resumir_engenharia(df, "HV")

    fig, axes = plt.subplots(3, 2, figsize=(10.2, 9.6))
    for r, problema in enumerate(PROBLEMAS_ENG):
        _painel_engenharia(axes[r, 0], resumo_igd, "IGD", problema)
        _painel_engenharia(axes[r, 1], resumo_hv, "HV", problema)

    fig.subplots_adjust(left=0.11, right=0.90, top=0.97, bottom=0.06, wspace=0.85, hspace=0.55)
    _salvar(fig, "fig_engenharia.pdf")
    return True


# ---------------------------------------------------------------------------
# Figura 3 — hospedeiros (família HOST)
# ---------------------------------------------------------------------------

GRUPO_CORES = {"ZDT": "#0072B2", "DTLZ": "#E69F00", "WFG": "#009E73", "MaF": "#CC79A7"}
M_MARCADORES = {2: "o", 3: "^"}
COR_BENEFICIO = "#0072B2"
COR_PREJUIZO = "#D55E00"


def _jitter_estavel(*partes: object, largura: float = 0.15) -> float:
    chave = "|".join(map(str, partes)).encode("utf-8")
    semente = int.from_bytes(hashlib.sha256(chave).digest()[:8], "little")
    rng = np.random.default_rng(semente)
    return float(rng.uniform(-largura, largura))


def _bandas_referencia(ax: plt.Axes) -> None:
    for lo, hi, alpha in ((0.56, 0.64, 0.06), (0.64, 0.71, 0.08), (0.71, 1.0, 0.10)):
        ax.axhspan(lo, hi, color=COR_BENEFICIO, alpha=alpha, linewidth=0)
        ax.axhspan(1 - hi, 1 - lo, color=COR_PREJUIZO, alpha=alpha, linewidth=0)
    ax.axhline(0.5, color="black", linewidth=0.8, linestyle="--", alpha=0.6)


def figura_hospedeiros() -> bool:
    quadros = []
    for stem, rotulo in HOSTS_STEMS:
        caminho = RESULTS_TABLES / f"hosts_{stem}_igd_stats.csv"
        if not caminho.exists():
            print(f"ERRO: artefato ausente: {caminho}", file=sys.stderr)
            return False
        quadro = pd.read_csv(caminho)
        quadro["rotulo"] = rotulo
        quadro["A12_ivf"] = 1.0 - quadro["A12"]
        quadros.append(quadro)
    dados = pd.concat(quadros, ignore_index=True)

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    _bandas_referencia(ax)

    rotulos = [r for _, r in HOSTS_STEMS]
    posicoes_x = {r: i for i, r in enumerate(rotulos)}
    for _, linha in dados.iterrows():
        ax.scatter(
            posicoes_x[linha["rotulo"]] + _jitter_estavel(linha["problem"], linha["M"], linha["rotulo"]),
            linha["A12_ivf"],
            color=GRUPO_CORES.get(linha["group"], "#333333"),
            marker=M_MARCADORES.get(linha["M"], "o"),
            s=35, alpha=0.82, edgecolors="white", linewidths=0.35, zorder=3,
        )

    for rotulo in rotulos:
        sub = dados[dados["rotulo"] == rotulo]
        mediana = sub["A12_ivf"].median()
        x = posicoes_x[rotulo]
        ax.plot([x - 0.25, x + 0.25], [mediana, mediana], color="black", linewidth=2.5, zorder=4)

    ax.set_xticks(range(len(rotulos)))
    ax.set_xticklabels(rotulos, fontsize=12)
    ax.set_ylabel("$A_{12}$ orientado do IGD\n(> 0,5 favorece o IVF)", fontsize=10)
    ax.set_ylim(-0.02, 1.02)
    ax.yaxis.set_major_formatter(fmt.axis_formatter())
    ax.tick_params(labelsize=10)
    ax.spines[["top", "right"]].set_visible(False)

    alcas_familia = [mpatches.Patch(color=cor, label=grupo) for grupo, cor in GRUPO_CORES.items()]
    alcas_m = [
        plt.Line2D([], [], color="gray", marker=marcador, linestyle="None", markersize=6, label=f"{m} objetivos")
        for m, marcador in M_MARCADORES.items()
    ]
    ax.legend(
        handles=alcas_familia + alcas_m, fontsize=8.5, ncol=6, loc="upper center",
        bbox_to_anchor=(0.5, -0.14), framealpha=0.9,
    )

    fig.subplots_adjust(bottom=0.24)
    _salvar(fig, "fig_hospedeiros_a12.pdf")
    return True


# ---------------------------------------------------------------------------
# Figura 4 — ativação (família DEC)
# ---------------------------------------------------------------------------

COR_HELPS = "#0072B2"
COR_NOT_HELPS = "#D55E00"


def figura_ativacao() -> bool:
    if not DINAMICA_CSV.exists():
        print(f"ERRO: artefato ausente: {DINAMICA_CSV}", file=sys.stderr)
        return False

    df = pd.read_csv(DINAMICA_CSV)
    df = df[df["early_frac"] == 0.2].copy()
    df = df[df["response_label"].notna()].copy()

    helps = df.loc[df["response_label"] == "HELPS", "ivf_turnover_early"].to_numpy()
    not_helps = df.loc[df["response_label"] == "NOT_HELPS", "ivf_turnover_early"].to_numpy()

    if len(helps) != 41 or len(not_helps) != 10:
        print(
            f"ERRO: contagem inesperada de rótulos (HELPS={len(helps)}, NOT_HELPS={len(not_helps)}); "
            "esperado 41/10 sobre as 51 instâncias rotuladas.",
            file=sys.stderr,
        )
        return False

    fig, ax = plt.subplots(figsize=(7.6, 4.5))

    partes = ax.violinplot(
        [helps, not_helps], positions=[0, 1], orientation="horizontal", showmedians=True, widths=0.7,
    )
    for corpo, cor in zip(partes["bodies"], (COR_HELPS, COR_NOT_HELPS)):
        corpo.set_facecolor(cor)
        corpo.set_alpha(0.35)
        corpo.set_edgecolor(cor)
    for chave in ("cmedians", "cbars", "cmins", "cmaxes"):
        partes[chave].set_color("#333333")
        partes[chave].set_linewidth(1.1)

    rng = np.random.default_rng(20260919)
    for i, (valores, cor) in enumerate(((helps, COR_HELPS), (not_helps, COR_NOT_HELPS))):
        y_jit = i + rng.uniform(-0.12, 0.12, size=len(valores))
        ax.scatter(valores, y_jit, color=cor, s=24, alpha=0.75, edgecolors="white", linewidths=0.4, zorder=3)

    ax.axvline(LIMIAR_TURNOVER, color="black", linestyle="--", linewidth=1.2, zorder=4)
    ax.text(LIMIAR_TURNOVER, 1.62, f"limiar = {_fmt(LIMIAR_TURNOVER, 3)}", ha="center", fontsize=8.5)

    ax.set_yticks([0, 1])
    ax.set_yticklabels([f"Ajuda ($n$ = {len(helps)})", f"Não ajuda ($n$ = {len(not_helps)})"], fontsize=10)
    ax.set_xlabel("Renovação do arquivo na fase inicial da execução", fontsize=10)
    ax.set_ylim(-0.6, 1.85)
    ax.xaxis.set_major_formatter(fmt.axis_formatter())
    ax.spines[["top", "right"]].set_visible(False)

    _salvar(fig, "fig_ativacao_turnover.pdf")
    return True


def main() -> int:
    apply_paper_style()

    ok = True
    for construir in (figura_calibracao, figura_engenharia, figura_hospedeiros, figura_ativacao):
        if not construir():
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
