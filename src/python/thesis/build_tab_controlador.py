#!/usr/bin/env python3
"""Warmup-controller comparison table, with the not-helpful subset split in two.

HV is the declared primary endpoint here, not IGD. The instance labels were
derived from the IGD outcome of the primary comparison, so scoring the controller on IGD
would reuse the labels as their own validation. The table therefore leads with
HV and reports IGD as secondary.

The frozen WTL artifact reports three subsets: all instances, those where the
operator helps, and those where it does not. The last one mixes two situations
a controller treats very differently: instances where the operator is neutral,
where switching it off can gain nothing, and instances where it hurts, the only
ones a controller can rescue. The label file keeps that three-way split
(``compute_response.py``: HELPS, NEUTRAL, HURTS), and the per-case comparison
CSV keeps the paired tests, so the split is recomputed here with the rule of
the producer of the frozen artifact
(``legacy/python/analysis/summarize_controller_comparison.py``): a case counts
as a win or a loss only when the BH-adjusted p-value is below 0.05 *and* A12
leaves the [0.44, 0.56] band. Before publishing the split, the recomputed
counts of the three frozen subsets must reproduce the frozen artifact exactly;
otherwise this builder fails instead of printing a rule that differs from the
one behind the manuscript.

The note states the thresholds the controller actually applied: each family
was controlled with the threshold calibrated without it (leave-one-family-out),
read from ``dynamic_signal_lofo.csv``. Where they bind, suite by suite, is the
table of the threshold rule by suite, which the note cites.

Layout: one row per metric and instance class, one column per comparison, so
the two comparisons of a class sit side by side. The count of instances in
which the controller equals or beats the comparator is ``n`` minus the losses
and is not printed separately.

Writes: results/thesis/tab_controlador_wtl.tex
"""

from __future__ import annotations

import re
import sys

import pandas as pd

import latex_table as lt
import ptbr_format as fmt
from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS

# Frozen out-of-sample artifacts named in data-sources.toml. The undated
# data/processed/ppsn_controller_comparison.csv is an earlier run, made with a
# single in-sample threshold, and must not be substituted for them.
WTL = RESULTS_TABLES / "controller_wtl_oos_20260326_221909.csv"
COMPARISON = DATA_PROCESSED / "ppsn_controller_comparison_oos_20260326_221909.csv"
RESPONSE = DATA_PROCESSED / "fla_response.csv"
LOFO = RESULTS_TABLES / "dynamic_signal_lofo.csv"
OUT = RESULTS_THESIS / "tab_controlador_wtl.tex"

ALPHA = 0.05
EFFECT_LOW = 0.44
EFFECT_HIGH = 0.56
FEATURE = "ivf_turnover_early"

# frozen label -> (adjusted p column, A12 column)
COMPARISONS = {
    "CTRL vs SPEA2": ("p_bh_ctrl_vs_spea2", "a12_ctrl_vs_spea2"),
    "CTRL vs IVF-SPEA2": ("p_bh_ctrl_vs_ivf", "a12_ctrl_vs_ivf"),
}
COMPARISON_ORDER = ["CTRL vs SPEA2", "CTRL vs IVF-SPEA2"]

SUBSETS = [
    ("ALL", "Todas"),
    ("HELPS", "O operador ajuda"),
    ("NOT_HELPS", "O operador não ajuda"),
    ("NEUTRAL", "\\quad neutro"),
    ("HURTS", "\\quad prejudica"),
]
FROZEN_SUBSETS = ("ALL", "HELPS", "NOT_HELPS")

FAMILY_LABEL = {"DTLZ": "DTLZ", "MAF": "MaF", "WFG": "WFG", "ZDT": "ZDT"}


def _outcome(p_bh: float, a12: float, metric: str) -> str:
    """Win/tie/loss of the controller, as the frozen artifact's producer decides it.

    A12 is the probability that the controller yields the larger value, so a
    low A12 favours the controller on IGD (minimized) and a high one on HV.
    """
    if pd.isna(p_bh) or pd.isna(a12):
        return "skip"
    if p_bh >= ALPHA:
        return "tie"
    better = a12 < EFFECT_LOW if metric == "IGD" else a12 > EFFECT_HIGH
    worse = a12 > EFFECT_HIGH if metric == "IGD" else a12 < EFFECT_LOW
    return "win" if better else ("loss" if worse else "tie")


def _subset(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    if key == "ALL":
        return frame
    if key in ("HELPS", "NOT_HELPS"):
        return frame[frame["label_binary"] == key]
    return frame[frame["label"] == key]


def _counts(outcomes: pd.Series) -> tuple[int, int, int]:
    return (
        int((outcomes == "win").sum()),
        int((outcomes == "tie").sum()),
        int((outcomes == "loss").sum()),
    )


def _family(case_id: str) -> str:
    """Suite of a case identifier such as ``wfg2_m3``: its alphabetic prefix."""
    match = re.match(r"[a-z]+", case_id.lower())
    return match.group(0).upper() if match else ""


def _cases() -> pd.DataFrame:
    """Per-case outcomes of both comparisons, joined to the primary-comparison labels."""
    comparison = pd.read_csv(COMPARISON)
    response = pd.read_csv(RESPONSE)
    response["case_id"] = response["instance"].str.lower()
    cases = comparison.merge(
        response[["case_id", "label", "label_binary"]], on="case_id", how="inner"
    )
    for key, (p_col, a12_col) in COMPARISONS.items():
        cases[key] = [
            _outcome(p, a12, metric)
            for p, a12, metric in zip(cases[p_col], cases[a12_col], cases["metric"], strict=True)
        ]
    cases["family"] = cases["case_id"].map(_family)
    return cases


def _reproduces_frozen(cases: pd.DataFrame, frozen: pd.DataFrame) -> bool:
    ok = True
    for metric in ("HV", "IGD"):
        block = cases[cases["metric"] == metric]
        for key in COMPARISON_ORDER:
            for subset in FROZEN_SUBSETS:
                hit = frozen[
                    (frozen["metric"] == metric)
                    & (frozen["comparison"] == key)
                    & (frozen["label"] == subset)
                ]
                if len(hit) != 1:
                    print(f"ERRO: {metric}/{key}/{subset} ausente do artefato", file=sys.stderr)
                    ok = False
                    continue
                expected = (int(hit.iloc[0]["wins"]), int(hit.iloc[0]["ties"]),
                            int(hit.iloc[0]["losses"]))
                got = _counts(_subset(block, subset)[key])
                if got != expected:
                    print(
                        f"ERRO: {metric}/{key}/{subset}: recalculado {got}, "
                        f"artefato congelado {expected}",
                        file=sys.stderr,
                    )
                    ok = False
    return ok


def _applied_thresholds() -> str | None:
    """Thresholds the controller applied, per family, as a pt-BR phrase."""
    lofo = pd.read_csv(LOFO)
    row = lofo[lofo["feature"] == FEATURE]
    if len(row) != 1:
        print(f"ERRO: {FEATURE} ausente de {LOFO.name}", file=sys.stderr)
        return None
    rules: dict[str, float] = {}
    for part in str(row.iloc[0]["family_rule_summary"]).split(";"):
        family, threshold, direction = part.split(":")
        if direction != "ge":
            print(f"ERRO: regra inesperada para {family}: {direction}", file=sys.stderr)
            return None
        rules[family.upper()] = float(threshold)

    by_value: dict[float, list[str]] = {}
    for family, threshold in sorted(rules.items()):
        by_value.setdefault(round(threshold, 3), []).append(FAMILY_LABEL[family])
    return ", e ".join(
        f"{fmt.decimal(value)} em {_enumerate(families)}"
        for value, families in sorted(by_value.items())
    )


def _enumerate(items: list[str]) -> str:
    """pt-BR enumeration: ``a``, ``a e b``, ``a, b e c``."""
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " e " + items[-1]


def main() -> int:
    missing = [p for p in (WTL, COMPARISON, RESPONSE, LOFO) if not p.exists()]
    if missing:
        for path in missing:
            print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return 1

    frozen = pd.read_csv(WTL)
    cases = _cases()
    n_frozen = frozen[(frozen["metric"] == "HV") & (frozen["label"] == "ALL")]["n_cases"]
    if cases["case_id"].nunique() != int(n_frozen.iloc[0]):
        print(
            "ERRO: casos da comparação não coincidem com os do artefato congelado",
            file=sys.stderr,
        )
        return 1
    if not _reproduces_frozen(cases, frozen):
        return 1

    applied = _applied_thresholds()
    if applied is None:
        return 1

    # One row per metric and instance class, one column per comparison: the two
    # comparisons of the same class sit side by side. "Iguala ou supera" is n
    # minus the losses, so the table prints V/E/D only.
    rows: list[list[str] | object] = []
    for metric_index, metric in enumerate(("HV", "IGD")):
        if metric_index:
            rows.append(lt.Rule)
        block = cases[cases["metric"] == metric]
        for subset_index, (subset, prose) in enumerate(SUBSETS):
            subset_cases = _subset(block, subset)
            metric_label: str | lt.Multirow
            if subset_index == 0:
                metric_label = lt.Multirow(metric, len(SUBSETS))
            else:
                metric_label = ""
            cells = [metric_label, prose, str(len(subset_cases))]
            for key in COMPARISON_ORDER:
                cells.append(fmt.wtl(*_counts(subset_cases[key])))
            rows.append(cells)

    # Section 7.4.3 states that every HV difference against the always-on
    # operator falls in the WFG; the builder fails if that stops being true.
    hv = cases[cases["metric"] == "HV"]
    differing = hv[hv["CTRL vs IVF-SPEA2"].isin(["win", "loss"])]
    families = sorted({FAMILY_LABEL[f] for f in differing["family"]})
    if families != ["WFG"]:
        print(
            "ERRO: o texto afirma que as diferenças em HV contra o IVF/SPEA2 sempre ativo "
            f"estão todas na WFG; estão em {families}",
            file=sys.stderr,
        )
        return 1

    # Where the thresholds bind, suite by suite, is Table 7.10; why HV is the
    # primary endpoint, and what the counts mean, the text says where it cites
    # the table. The note defines the controller, the test and the rows.
    note = (
        "Controlador de aquecimento: ao fim dos primeiros 20\\% do orçamento, o operador é "
        "desativado de forma irreversível nas execuções cuja renovação média do arquivo fica "
        "abaixo do limiar. Cada família foi controlada com o limiar calibrado sem ela, por "
        f"validação deixa-uma-família: {applied} (Tabela~\\ref{{tab:dinamica_suite}}). Wilcoxon "
        "pareado com correção de Benjamini--Hochberg sobre 30 execuções pareadas por semente; um "
        "caso conta como vitória ou derrota do controlador quando o valor-$p$ ajustado fica "
        "abaixo de $0{,}05$ e o $A_{12}$ sai do intervalo $[0{,}44;\\,0{,}56]$. As linhas "
        "recuadas decompõem as instâncias em que o operador não ajuda segundo o rótulo de três "
        "classes da comparação em IGD da coorte da comparação principal, sem correção de "
        "multiplicidade: "
        "neutro quando o IVF/SPEA2 não difere do SPEA2, prejudica quando perde para ele. O HV é "
        "o desfecho primário declarado desta avaliação."
    )

    content = lt.render(
        header=[
            [lt.Span("", 3), lt.Span("V/E/D do controlador contra", 2)],
            ["Métrica", "Subconjunto", "$n$", "SPEA2 canônico", "IVF/SPEA2 sempre ativo"],
        ],
        rows=rows,
        colspec="llccc",
        caption=(
            "Controlador de aquecimento frente ao SPEA2 canônico e ao IVF/SPEA2 sempre "
            "ativo, por classe de instância segundo o efeito do operador."
        ),
        label="tab:controlador_wtl",
        producer=__file__,
        sources=[WTL, COMPARISON, RESPONSE, LOFO],
        note=note,
    )
    lt.write(OUT, content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
