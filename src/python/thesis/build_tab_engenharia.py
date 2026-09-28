#!/usr/bin/env python3
"""Engineering-transfer table: host comparison beside multi-baseline positioning.

External support only, and the weakest evidence family in the document: three
constrained problems, not a suite. The table keeps two readings apart because
they answer different questions:

* **against the host (SPEA2)** -- the comparison the dissertation's first
  research question asks about. Read from the per-algorithm summary: the
  rank-sum p-value of SPEA2 against IVF/SPEA2 on the common runs, uncorrected,
  exactly as the family's pipeline computed it. Holm across the three problems
  of each metric is computed here and reported in the note.
* **against every comparator** -- positioning, the counts the manuscript
  reports. On RWMOP8 one comparator has no valid run, so that row counts seven.

The two readings disagree in tone -- the host comparison has no loss, the
positioning is mixed -- so each has its own header group, and the text that
cites the table says which one each claim may use.

The producing pipeline cannot run in a fresh checkout (``data/engineering/`` is
not tracked), so this reads the frozen result artifacts.

Writes: results/thesis/tab_engenharia_wtl.tex
"""

from __future__ import annotations

import sys

import pandas as pd
from statsmodels.stats.multitest import multipletests

import latex_table as lt
import ptbr_format as fmt
from ivfspea2.paths import RESULTS, RESULTS_THESIS

PAIRWISE = RESULTS / "engineering_suite" / "engineering_suite_pairwise_main.csv"
SUMMARY = RESULTS / "engineering_suite" / "engineering_suite_summary_main.csv"
OUT = RESULTS_THESIS / "tab_engenharia_wtl.tex"

# Presentation order follows the manuscript: continuity benchmark first, then
# the two problems selected by the locked screening protocol.
PROBLEM_ORDER = ["RWMOP9", "RWMOP21", "RWMOP8"]
ALPHA = 0.05
# Four decimals: the note prints Holm-adjusted values of the same p-values,
# and with three a reader could not follow the adjustment (0,003 x 3 != 0,010).
P_PLACES = 4

# metric -> (median column, p-value column, symbol column, higher is better)
METRIC_COLUMNS = {
    "IGD": ("MedianIGD_PF", "P_vs_IVF_IGD", "SymbolIGD", False),
    "HV": ("MedianHV", "P_vs_IVF_HV", "SymbolHV", True),
}

# The pipeline writes symbols from the IVF/SPEA2 perspective.
SYMBOL_LABEL = {"+": "Vitória", "=": "Empate", "-": "Derrota"}


HostComparison = dict[tuple[str, str], dict[str, float | str]]


def _host_comparison(summary: pd.DataFrame) -> HostComparison | None:
    """IVF/SPEA2 against SPEA2 per problem and metric, from the frozen summary."""
    host: HostComparison = {}
    for problem in PROBLEM_ORDER:
        ivf = summary[(summary["Problem"] == problem) & (summary["Algorithm"] == "IVFSPEA2")]
        base = summary[(summary["Problem"] == problem) & (summary["Algorithm"] == "SPEA2")]
        if len(ivf) != 1 or len(base) != 1:
            print(
                f"ERRO: {problem}: esperava uma linha de IVF/SPEA2 e uma de SPEA2",
                file=sys.stderr,
            )
            return None
        for metric, (median_col, p_col, symbol_col, higher) in METRIC_COLUMNS.items():
            median_ivf = float(ivf.iloc[0][median_col])
            median_base = float(base.iloc[0][median_col])
            gain = median_ivf - median_base if higher else median_base - median_ivf
            p_value = float(base.iloc[0][p_col])
            symbol = str(base.iloc[0][symbol_col]).strip()
            # The pipeline decides the sign by comparing medians once p < alpha;
            # a mismatch here means the artifact and this reading disagree.
            expected = "=" if p_value >= ALPHA else ("+" if gain > 0 else "-")
            if symbol != expected:
                print(
                    f"ERRO: {problem}/{metric}: símbolo {symbol!r} no artefato, "
                    f"esperado {expected!r} pelo valor-p e pelas medianas",
                    file=sys.stderr,
                )
                return None
            host[(problem, metric)] = {
                "delta_pct": 100.0 * gain / abs(median_base),
                "p": p_value,
                "symbol": symbol,
                "n_ivf": int(ivf.iloc[0]["NValidIGD" if metric == "IGD" else "NValidHV"]),
                "n_base": int(base.iloc[0]["NValidIGD" if metric == "IGD" else "NValidHV"]),
            }

    for metric in METRIC_COLUMNS:
        keys = [(problem, metric) for problem in PROBLEM_ORDER]
        adjusted = multipletests([float(host[k]["p"]) for k in keys], method="holm")[1]
        for key, p_holm in zip(keys, adjusted, strict=True):
            host[key]["p_holm"] = float(p_holm)
    return host


def main() -> int:
    missing = [path for path in (PAIRWISE, SUMMARY) if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        print(
            "Estes artefatos estão congelados: data/engineering/ não é versionado e o "
            "produtor não roda neste checkout.",
            file=sys.stderr,
        )
        return 1

    pairwise = pd.read_csv(PAIRWISE)
    pairwise = pairwise[pairwise["Stage"] == "MAIN"]
    summary = pd.read_csv(SUMMARY)
    summary = summary[summary["Stage"] == "MAIN"]

    host = _host_comparison(summary)
    if host is None:
        return 1

    rows: list[list[str] | object] = []
    for index, problem in enumerate(PROBLEM_ORDER):
        if index:
            rows.append(lt.Rule)
        subset = pairwise[pairwise["Problem"] == problem]
        if subset.empty:
            print(f"ERRO: {problem} ausente do artefato", file=sys.stderr)
            return 1
        objectives = int(subset.iloc[0]["M"])
        for metric_index, metric in enumerate(METRIC_COLUMNS):
            hit = subset[subset["Metric"] == metric]
            if len(hit) != 1:
                print(
                    f"ERRO: esperava 1 linha para {problem}/{metric}, encontrei {len(hit)}",
                    file=sys.stderr,
                )
                return 1
            row = hit.iloc[0]
            comparison = host[(problem, metric)]
            rows.append([
                problem if metric_index == 0 else "",
                str(objectives) if metric_index == 0 else "",
                metric,
                fmt.signed(float(comparison["delta_pct"]), places=2),
                fmt.pvalue(float(comparison["p"]), places=P_PLACES),
                SYMBOL_LABEL[str(comparison["symbol"])],
                fmt.wtl(row["Plus"], row["Equal"], row["Minus"]),
            ])

    changed = sorted(
        f"{problem}/{metric}"
        for (problem, metric), comparison in host.items()
        if (float(comparison["p"]) < ALPHA) != (float(comparison["p_holm"]) < ALPHA)
    )
    significant = [
        (problem, metric)
        for (problem, metric), comparison in host.items()
        if float(comparison["p_holm"]) < ALPHA
    ]
    holm_detail = "; ".join(
        f"{problem} em {metric}, "
        f"{fmt.pvalue(float(host[(problem, metric)]['p_holm']), places=P_PLACES)}"
        for problem, metric in sorted(
            significant, key=lambda k: (PROBLEM_ORDER.index(k[0]), k[1] != "IGD")
        )
    )
    holm_sentence = (
        "nenhuma decisão muda"
        if not changed
        else f"mudam as decisões de {', '.join(changed)}"
    )
    host_sizes = sorted({(int(c["n_ivf"]), int(c["n_base"])) for c in host.values()})
    host_n = (
        f"{host_sizes[0][0]} execuções de cada algoritmo"
        if len(host_sizes) == 1 and host_sizes[0][0] == host_sizes[0][1]
        else "as execuções válidas de cada algoritmo"
    )

    # Comparators with incomplete valid-run coverage. They are why a positioning
    # row can count fewer comparators than the suite has: a comparator with no
    # valid run yields no test.
    others = summary[summary["Algorithm"] != "IVFSPEA2"]
    n_comparators = int(others["Algorithm"].nunique())
    coverage_sentences = []
    for problem in PROBLEM_ORDER:
        rows_problem = others[others["Problem"] == problem]
        partial = rows_problem[rows_problem["NValidIGD"] < rows_problem["NCommonRuns"]]
        if partial.empty:
            continue
        described = [
            f"{r.Display} tem {int(r.NValidIGD)} de {int(r.NCommonRuns)}"
            if int(r.NValidIGD)
            else f"{r.Display}, nenhuma"
            for r in partial.itertuples()
        ]
        counted = pairwise[pairwise["Problem"] == problem].iloc[0]
        n_counted = int(counted["Plus"] + counted["Equal"] + counted["Minus"])
        coverage_sentences.append(
            f"No {problem}, a cobertura de execuções válidas é heterogênea "
            f"({'; '.join(described)}), e a contagem soma {n_counted} comparadores."
        )

    # Why the positioning answers a different question, and how strong the
    # family is, the text says where it cites the table; the note keeps the
    # definitions, the tests and the coverage that change how a cell reads.
    note = (
        "Contra o SPEA2: $\\Delta$ é a diferença relativa entre as medianas, orientada de modo "
        "que valores positivos favoreçam o IVF/SPEA2, e $p$ é o do teste de soma de postos de "
        f"Wilcoxon bicaudal sobre {host_n}, sem correção e com $\\alpha = 0{{,}}05$, como no "
        "processamento da família. Com correção de Holm entre os três problemas de cada "
        f"métrica, {holm_sentence}; os valores-$p$ ajustados das diferenças significativas "
        f"são: {holm_detail}. Contra os comparadores: vitórias/empates/derrotas (V/E/D) do "
        f"IVF/SPEA2 frente a cada um dos {n_comparators} algoritmos restantes, incluído o "
        f"SPEA2, sob o mesmo teste. {' '.join(coverage_sentences)} As contagens não se somam "
        "às da suíte sintética."
    )

    content = lt.render(
        header=[
            [
                lt.Span("", 3),
                lt.Span("Contra o SPEA2", 3),
                lt.Span("Contra os comparadores", 1, rule=True),
            ],
            ["Problema", "$M$", "Métrica", "$\\Delta$ (\\%)", "$p$", "Resultado", "V/E/D"],
        ],
        rows=rows,
        colspec="lccrrcc",
        caption=(
            "Transferência do IVF/SPEA2 para problemas de engenharia com restrições: "
            "comparação contra o hospedeiro e posicionamento frente aos demais comparadores."
        ),
        label="tab:engenharia_wtl",
        producer=__file__,
        sources=[SUMMARY, PAIRWISE],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
