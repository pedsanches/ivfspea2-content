#!/usr/bin/env python3
"""Figuras de resultados do Capítulo VI (Resultados) da dissertação.

Lê artefatos versionados e escreve três figuras. Duas pertencem à família
da comparação principal (``CONF``: IVF/SPEA2 na janela de submissão 3001–3060 contra o
SPEA2 canônico na janela 1–60, 51 instâncias sintéticas, 60 execuções por
configuração) e uma pertence ao Apêndice C (posto médio contra os demais
comparadores, descritivo, sem teste de hipótese):

  fig_dist_igd.pdf
      Distribuição de IGD por instância, IVF/SPEA2 contra SPEA2 canônico, em
      dois painéis (M=2 e M=3), com cada execução dividida pela mediana do
      SPEA2 na mesma instância: as diferenças típicas, de cerca de 1%, ficam
      visíveis numa janela horizontal fixa, e as caixas que a excedem aparecem
      cortadas na borda, com uma seta. Os marcadores são o veredito corrigido
      por Holm e o † a calibração, lidos de
      ``results/tables/claims_summary_instance_details.csv``, a mesma fonte das
      tabelas por instância. Fonte das execuções:
      ``data/processed/todas_metricas_consolidado_with_modern.csv``, lida
      exclusivamente através de ``filter_submission_synthetic_cohort``.

  fig_dtlz4_bimodal.pdf
      Os dois regimes de convergência do IVF/SPEA2 em DTLZ4 (M=3): a fronteira
      obtida na execução mais próxima do primeiro quartil de IGD e a mais
      próxima do terceiro quartil com IGD > 0,1, entre as 60 execuções da
      instância. Fonte: ``data/processed/fronts/DTLZ4_M3_*.csv``. É uma
      figura de mecanismo (fronteiras obtidas ao final de cada execução), não
      de trajetória de convergência por geração.

  fig_posto_medio.pdf
      Posto médio exploratório dos nove algoritmos avaliados, por M, a partir
      da mediana de IGD por instância. Mesma fonte e mesmo filtro de coorte de
      ``fig_dist_igd``.

A lógica de cálculo (extração por instância, matriz de postos de Friedman)
reaproveita a dos scripts de figuras dos manuscritos-fonte
(``src/python/analysis/generate_paper_figures.py``,
``src/python/analysis/plot_dtlz4_bimodal.py``,
``src/python/analysis/plot_friedman_avg_rank.py``), reimplementada aqui para
que este módulo permaneça autocontido e grave apenas nos diretórios de saída
da dissertação. Todo número exibido usa a vírgula decimal, como o texto.

Escreve em ``results/thesis/figures/`` (canônico, versionado) e em
``thesis/masters/generated/figures/`` (cópia de build, ignorada pelo Git).
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

import ptbr_format as fmt
from ivfspea2.cohorts import filter_submission_synthetic_cohort
from ivfspea2.figio import save_figure
from ivfspea2.figstyle import apply_paper_style
from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS, THESIS_GENERATED, ensure_dir

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATA_CSV = DATA_PROCESSED / "todas_metricas_consolidado_with_modern.csv"
DETALHES = RESULTS_TABLES / "claims_summary_instance_details.csv"
# Janela de IGD relativa à mediana do SPEA2: cobre as medianas de todas as
# instâncias salvo WFG1 (M=2), e as caixas que a excedem são sinalizadas.
JANELA = (0.85, 1.15)
FRONTS_DIR = DATA_PROCESSED / "fronts"
DTLZ4_GOOD = FRONTS_DIR / "DTLZ4_M3_IVFSPEA2_good.csv"
DTLZ4_BAD = FRONTS_DIR / "DTLZ4_M3_IVFSPEA2_bad.csv"
DTLZ4_TRUE_PF = FRONTS_DIR / "DTLZ4_M3_truePF.csv"
DTLZ4_META = FRONTS_DIR / "DTLZ4_M3_selection_metadata.csv"

FIG_OUT = ensure_dir(RESULTS_THESIS / "figures")
FIG_MIRROR = ensure_dir(THESIS_GENERATED / "figures")
OUT_DIRS = [FIG_OUT, FIG_MIRROR]

IVF_COLOR = "#2166AC"
SPEA2_COLOR = "#B2182B"
WIN_COLOR = "#1B7837"
LOSS_COLOR = "#B2182B"

ALGORITHMS = [
    "IVFSPEA2",
    "SPEA2",
    "MFOSPEA2",
    "SPEA2SDE",
    "NSGAII",
    "NSGAIII",
    "MOEAD",
    "AGEMOEAII",
    "ARMOEA",
]
ALGO_DISPLAY = {
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

SUITE_ORDER = ["ZDT", "DTLZ", "WFG", "MaF"]
PROBLEM_ORDER = {
    "M2": {
        "ZDT": ["ZDT1", "ZDT2", "ZDT3", "ZDT4", "ZDT6"],
        "DTLZ": ["DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4", "DTLZ5", "DTLZ6", "DTLZ7"],
        "WFG": [
            "WFG1", "WFG2", "WFG3", "WFG4", "WFG5", "WFG6", "WFG7", "WFG8", "WFG9",
        ],
        "MaF": ["MaF1", "MaF2", "MaF3", "MaF4", "MaF5", "MaF6", "MaF7"],
    },
    "M3": {
        "DTLZ": ["DTLZ1", "DTLZ2", "DTLZ3", "DTLZ4", "DTLZ5", "DTLZ6", "DTLZ7"],
        "WFG": [
            "WFG1", "WFG2", "WFG3", "WFG4", "WFG5", "WFG6", "WFG7", "WFG8", "WFG9",
        ],
        "MaF": ["MaF1", "MaF2", "MaF3", "MaF4", "MaF5", "MaF6", "MaF7"],
    },
}


def _ordered_instances(m_label: str) -> list[str]:
    order: list[str] = []
    for suite in SUITE_ORDER:
        order.extend(PROBLEM_ORDER[m_label].get(suite, []))
    return order


def _suite_of(problem: str) -> str:
    for suite in SUITE_ORDER:
        if problem.startswith(suite):
            return suite
    return problem


def _load_cohort() -> pd.DataFrame:
    raw = pd.read_csv(DATA_CSV)
    return filter_submission_synthetic_cohort(raw)


# =====================================================================
# fig_dist_igd
# =====================================================================
def _vereditos_holm() -> tuple[dict[tuple[str, str], str], set[tuple[str, str]]]:
    """Veredito de IGD corrigido por Holm e instâncias de calibração, por (problema, M)."""
    detalhes = pd.read_csv(DETALHES)
    detalhes = detalhes[detalhes["metric"] == "IGD"]
    vereditos = {(r.Problema, r.M): r.indicator_holm for r in detalhes.itertuples()}
    calibracao = {(r.Problema, r.M) for r in detalhes.itertuples() if bool(r.is_full12)}
    return vereditos, calibracao


def _panel_dist_igd(
    ax: plt.Axes,
    df: pd.DataFrame,
    m_label: str,
    vereditos: dict[tuple[str, str], str],
    calibracao: set[tuple[str, str]],
) -> None:
    instances = _ordered_instances(m_label)
    df_m = df[(df["M"] == m_label) & (df["Algoritmo"].isin(["IVFSPEA2", "SPEA2"]))]
    lo, hi = JANELA

    series: dict[str, tuple[list[np.ndarray], list[float]]] = {"IVFSPEA2": ([], []), "SPEA2": ([], [])}
    cortes: list[tuple[float, float, str]] = []
    for idx, prob in enumerate(instances):
        bloco = df_m[df_m["Problema"] == prob]
        base = bloco.loc[bloco["Algoritmo"] == "SPEA2", "IGD"].dropna().to_numpy()
        if base.size == 0:
            raise ValueError(f"instância sem execuções do SPEA2: {prob} {m_label}")
        referencia = float(np.median(base))
        for algo, deslocamento in (("IVFSPEA2", -0.2), ("SPEA2", 0.2)):
            valores = bloco.loc[bloco["Algoritmo"] == algo, "IGD"].dropna().to_numpy() / referencia
            if valores.size == 0:
                raise ValueError(f"instância sem execuções de {algo}: {prob} {m_label}")
            posicao = idx + deslocamento
            series[algo][0].append(valores)
            series[algo][1].append(posicao)
            q1, q3 = np.percentile(valores, [25, 75])
            if q1 < lo:
                cortes.append((lo, posicao, "<"))
            if q3 > hi:
                cortes.append((hi, posicao, ">"))

    for algo, cor in (("IVFSPEA2", IVF_COLOR), ("SPEA2", SPEA2_COLOR)):
        dados, posicoes = series[algo]
        caixas = ax.boxplot(
            dados,
            positions=posicoes,
            widths=0.32,
            orientation="horizontal",
            patch_artist=True,
            showfliers=False,
            medianprops=dict(color="black", linewidth=1.1),
            whiskerprops=dict(linewidth=0.8),
            capprops=dict(linewidth=0.8),
            boxprops=dict(linewidth=0.8),
        )
        for caixa in caixas["boxes"]:
            caixa.set_facecolor(cor)
            caixa.set_alpha(0.75)

    for x, y, seta in cortes:
        ax.plot(x, y, marker=seta, color="black", markersize=4, clip_on=False, zorder=5)

    ax.axvline(1.0, color="#555555", linestyle="--", linewidth=0.8, zorder=0)
    ax.set_xlim(lo, hi)
    ax.set_xticks(np.round(np.arange(lo, hi + 1e-9, 0.05), 2))
    ax.xaxis.set_major_formatter(fmt.axis_formatter())

    for idx, prob in enumerate(instances):
        veredito = vereditos.get((prob, m_label))
        if veredito not in {"+", "-", "="}:
            raise ValueError(f"sem veredito de Holm para {prob} {m_label}")
        if veredito == "=":
            continue
        ax.text(
            1.015, idx, "+" if veredito == "+" else "\u2212",
            transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=11,
            color=WIN_COLOR if veredito == "+" else LOSS_COLOR, fontweight="bold",
        )

    rotulos = [
        f"{prob}$^{{\\dagger}}$" if (prob, m_label) in calibracao else prob for prob in instances
    ]
    ax.set_yticks(range(len(instances)))
    ax.set_yticklabels(rotulos, fontsize=12)
    ax.set_ylim(len(instances), -1)
    ax.set_xlabel("IGD / mediana do SPEA2 na instância", fontsize=12)
    ax.tick_params(axis="x", labelsize=11)
    ax.tick_params(axis="y", length=0)
    ax.set_title(f"$M={m_label[-1]}$", fontsize=13, fontweight="bold")

    # Bandas e rótulos de suíte.
    groups: list[tuple[int, int, str]] = []
    start = 0
    current = _suite_of(instances[0])
    for idx, prob in enumerate(instances):
        suite = _suite_of(prob)
        if suite != current:
            groups.append((start, idx - 1, current))
            start = idx
            current = suite
    groups.append((start, len(instances) - 1, current))

    for i in range(1, len(groups)):
        boundary = (groups[i - 1][1] + groups[i][0]) / 2
        ax.axhline(boundary, color="#888888", linestyle=":", linewidth=0.8)
    for g_start, g_end, suite in groups:
        mid = (g_start + g_end) / 2
        ax.text(
            0.015, mid, suite, transform=ax.get_yaxis_transform(), ha="left",
            va="center", fontsize=12, fontweight="bold", color="#333333",
            bbox=dict(facecolor="white", alpha=0.78, edgecolor="none", pad=1.5),
        )


def make_fig_dist_igd(df: pd.DataFrame) -> None:
    vereditos, calibracao = _vereditos_holm()
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 11.6))
    _panel_dist_igd(axes[0], df, "M2", vereditos, calibracao)
    _panel_dist_igd(axes[1], df, "M3", vereditos, calibracao)

    legend_elements = [
        Patch(facecolor=IVF_COLOR, alpha=0.75, edgecolor="black", linewidth=0.5, label="IVF/SPEA2"),
        Patch(facecolor=SPEA2_COLOR, alpha=0.75, edgecolor="black", linewidth=0.5, label="SPEA2 canônico"),
    ]
    fig.legend(
        handles=legend_elements, loc="lower center", ncol=2, frameon=True,
        fontsize=12, bbox_to_anchor=(0.5, -0.006),
    )
    fig.tight_layout(rect=(0, 0.018, 1, 1), w_pad=3.0)
    save_figure(fig, "fig_dist_igd.pdf", OUT_DIRS)
    plt.close(fig)


# =====================================================================
# fig_dtlz4_bimodal
# =====================================================================
def _load_selection_metadata() -> dict[str, str]:
    if not DTLZ4_META.exists():
        return {}
    meta = pd.read_csv(DTLZ4_META)
    info: dict[str, str] = {}
    for _, row in meta.iterrows():
        sel = str(row.get("selection_type", "")).strip()
        run_id = row.get("run_id")
        igd = row.get("igd")
        if pd.isna(run_id) or pd.isna(igd):
            continue
        info[sel] = f"execução {int(run_id)}, IGD = {fmt.plain(float(igd), 4 if igd < 0.1 else 3)}"
    return info


def make_fig_dtlz4_bimodal() -> None:
    good = pd.read_csv(DTLZ4_GOOD)
    bad = pd.read_csv(DTLZ4_BAD)
    true_pf = pd.read_csv(DTLZ4_TRUE_PF)
    selection_info = _load_selection_metadata()

    fig = plt.figure(figsize=(8.8, 4.6))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    for ax in (ax1, ax2):
        ax.scatter(
            true_pf["f1"], true_pf["f2"], true_pf["f3"], s=4, c="#CCCCCC",
            alpha=0.3, edgecolors="none", label="Fronteira de Pareto verdadeira",
        )

    ax1.scatter(
        good["f1"], good["f2"], good["f3"], s=14, c=IVF_COLOR, alpha=0.85,
        edgecolors="none", label="IVF/SPEA2",
    )
    ax2.scatter(
        bad["f1"], bad["f2"], bad["f3"], s=14, c=SPEA2_COLOR, alpha=0.85,
        edgecolors="none", label="IVF/SPEA2",
    )

    title_good = "(a) Regime de convergência (próximo de Q1)"
    if "good_q1" in selection_info:
        title_good = f"{title_good}\n{selection_info['good_q1']}"

    title_bad = "(b) Regime de estagnação (Q3, IGD > 0,1)"
    if "bad_q3_gt_0p1" in selection_info:
        title_bad = f"{title_bad}\n{selection_info['bad_q3_gt_0p1']}"

    for ax, title in [(ax1, title_good), (ax2, title_bad)]:
        ax.set_xlabel("$f_1$", labelpad=7, fontsize=12)
        ax.set_ylabel("$f_2$", labelpad=7, fontsize=12)
        ax.set_zlabel("$f_3$", labelpad=7, fontsize=12)
        ax.view_init(elev=24, azim=-53)
        ax.set_title(title, pad=10, fontsize=9)
        ax.tick_params(labelsize=12)
        for eixo in (ax.xaxis, ax.yaxis, ax.zaxis):
            eixo.set_major_formatter(fmt.axis_formatter())

    handles1, labels1 = ax1.get_legend_handles_labels()
    fig.legend(
        handles1, labels1, loc="lower center", ncol=2, frameon=True,
        fontsize=13, bbox_to_anchor=(0.5, -0.03),
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.99), w_pad=2.4)
    save_figure(fig, "fig_dtlz4_bimodal.pdf", OUT_DIRS)
    plt.close(fig)


# =====================================================================
# fig_posto_medio
# =====================================================================
def _rank_matrix(df_m: pd.DataFrame) -> pd.DataFrame:
    """Postos por instância (linhas) e algoritmo (colunas), IGD menor = melhor posto."""
    problems = sorted(df_m["Problema"].unique())
    rows = []
    for prob in problems:
        block = df_m[df_m["Problema"] == prob]
        med = {}
        for algo in ALGORITHMS:
            vals = block[block["Algoritmo"] == algo]["IGD"].dropna().values
            med[algo] = float(np.median(vals)) if len(vals) > 0 else np.inf
        med_vec = np.array([med[a] for a in ALGORITHMS], dtype=float)
        ranks = rankdata(med_vec, method="average")
        rows.append({"Problema": prob, **{a: float(r) for a, r in zip(ALGORITHMS, ranks)}})
    return pd.DataFrame(rows).set_index("Problema")


def _panel_avg_rank(ax: plt.Axes, rank_df: pd.DataFrame, title: str) -> None:
    avg = rank_df.mean(axis=0)
    sd = rank_df.std(axis=0, ddof=1)
    order = avg.sort_values().index.tolist()

    labels = [ALGO_DISPLAY[a] for a in order]
    values = avg[order].values
    errors = sd[order].values
    colors = [IVF_COLOR if a == "IVFSPEA2" else "#BDBDBD" for a in order]

    bars = ax.barh(
        np.arange(len(order)), values, xerr=errors, color=colors, edgecolor="black",
        linewidth=0.6, alpha=0.9,
        error_kw={"elinewidth": 1.0, "capsize": 2.5, "ecolor": "black"},
    )
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels(labels, fontsize=15)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=15)
    ax.tick_params(axis="x", labelsize=15)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.xaxis.set_major_formatter(fmt.axis_formatter())

    # Os valores ficam numa coluna à direita do eixo, fora da área de dados,
    # para não cruzar as barras de desvio padrão.
    for bar, v in zip(bars, values):
        ax.text(
            1.02, bar.get_y() + bar.get_height() / 2, fmt.plain(v, 2),
            transform=ax.get_yaxis_transform(), va="center", ha="left", fontsize=13,
        )


def make_fig_posto_medio(df: pd.DataFrame) -> None:
    df_algos = df[df["Algoritmo"].isin(ALGORITHMS)]
    rank_m2 = _rank_matrix(df_algos[df_algos["M"] == "M2"])
    rank_m3 = _rank_matrix(df_algos[df_algos["M"] == "M3"])

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.9), sharex=True)
    _panel_avg_rank(axes[0], rank_m2, "Posto médio por instância ($M=2$)")
    _panel_avg_rank(axes[1], rank_m3, "Posto médio por instância ($M=3$)")
    fig.supxlabel("Posto médio de IGD (menor é melhor)", fontsize=15)
    axes[0].set_ylabel("Algoritmo", fontsize=15)

    fig.tight_layout(rect=(0, 0, 1, 1))
    save_figure(fig, "fig_posto_medio.pdf", OUT_DIRS)
    plt.close(fig)


def main() -> int:
    missing = [p for p in (DATA_CSV, DTLZ4_GOOD, DTLZ4_BAD, DTLZ4_TRUE_PF) if not p.exists()]
    if missing:
        for path in missing:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return 1

    apply_paper_style()

    df = _load_cohort()

    make_fig_dist_igd(df)
    make_fig_dtlz4_bimodal()
    make_fig_posto_medio(df)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
