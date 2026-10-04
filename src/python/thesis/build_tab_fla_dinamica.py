#!/usr/bin/env python3
"""Landscape-model, dynamic-separation and threshold-rule tables.

Source note, deliberate and load-bearing:

``data/processed/classifier_comparison.csv`` is NOT used here. Its
``Early-turnover threshold / LOOCV`` row is an in-sample resubstitution fit,
not a leave-one-out estimate: ``compute_classifier_comparison.py`` calls
``fit_best_threshold`` on the whole frame and stores the result under the LOOCV
label. That row reports BA 0.791 where the genuine leave-one-out estimate in
``results/tables/dynamic_signal_loocv.csv`` is 0.691, and the inflated value
inverts the ordering the manuscript argues for (LFO above LOOCV). See
``thesis/masters/REWRITE_SPEC.md`` OQ-13.

The canonical sources are therefore ``fla_model_comparison.csv`` (which matches
the manuscript on every static-model figure) and the two
``dynamic_signal_{loocv,lofo}.csv`` artifacts, both of which hold out properly.

Writes: results/thesis/tab_fla_modelos.tex
        results/thesis/tab_dinamica_separacao.tex
        results/thesis/tab_dinamica_limiar.tex
        results/thesis/tab_dinamica_suite.tex
"""

from __future__ import annotations

import re
import sys

import pandas as pd

from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

MODELS = RESULTS_TABLES / "fla_model_comparison.csv"
MAIN_TESTS = RESULTS_TABLES / "dynamic_signal_main_tests.csv"
LOOCV = RESULTS_TABLES / "dynamic_signal_loocv.csv"
LOFO = RESULTS_TABLES / "dynamic_signal_lofo.csv"
DYNAMIC_TEST = DATA_PROCESSED / "dynamic_signal_test.csv"

OUT_MODELS = RESULTS_THESIS / "tab_fla_modelos.tex"
OUT_SEPARATION = RESULTS_THESIS / "tab_dinamica_separacao.tex"
OUT_THRESHOLD = RESULTS_THESIS / "tab_dinamica_limiar.tex"
OUT_DINAMICA_SUITE = RESULTS_THESIS / "tab_dinamica_suite.tex"

_SUITE_RE = re.compile(r"^[A-Za-z]+")

EARLY_FRAC = 0.20
THRESHOLD_FEATURE = "ivf_turnover_early"
FAMILY_DISPLAY = {"DTLZ": "DTLZ", "MAF": "MaF", "WFG": "WFG", "ZDT": "ZDT"}

FEATURE_SET = "SET_ALL"

MODEL_LABEL = {
    "RF_Regression": "Floresta aleatória (regressão)",
    "RF_Classification": "Floresta aleatória (classificação)",
    "LogisticRegression": "Regressão logística",
    "SVC_RBF": "SVC com núcleo RBF",
    "KNN_5": "$k$-vizinhos ($k=5$)",
}
MODEL_ORDER = ["RF_Regression", "RF_Classification", "LogisticRegression", "SVC_RBF", "KNN_5"]

VALIDATION_LABEL = {"LOOCV": "Deixa-uma-instância", "LOFO": "Deixa-uma-família", "LFO-CV": "Deixa-uma-família"}

FEATURE_LABEL = {
    "ivf_turnover_early": "Renovação do arquivo (IVF/SPEA2)",
    "spea2_turnover_early": "Renovação do arquivo (SPEA2)",
    "hv_final_delta": "Diferença final de HV",
    "igd_final_delta": "Diferença final de IGD",
    "ivf_cycles_early": "Ciclos de IVF na fase inicial",
}


def _missing(path) -> bool:
    if not path.exists():
        print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return True
    return False


# Each model reports the two measures of its task. One row per model and
# measure, one column per validation, so the drop from leave-one-instance-out
# to leave-one-family-out reads along the row.
MODEL_MEASURES = {
    "RF_Regression": [("spearman_r", "$r_s$"), ("r2", "$R^2$")],
    "RF_Classification": [("balanced_acc", "BA"), ("mcc", "MCC")],
    "LogisticRegression": [("balanced_acc", "BA"), ("mcc", "MCC")],
    "SVC_RBF": [("balanced_acc", "BA"), ("mcc", "MCC")],
    "KNN_5": [("balanced_acc", "BA"), ("mcc", "MCC")],
}


def build_models() -> str | None:
    if _missing(MODELS):
        return None
    models = pd.read_csv(MODELS)
    subset = models[models["feature_set"] == FEATURE_SET]

    rows: list[list[str] | object] = []
    previous_task = None
    for model in MODEL_ORDER:
        block = subset[subset["model"] == model]
        if block.empty:
            continue
        measures = MODEL_MEASURES[model]
        # A rule between the regression block and the classification block, a
        # space between models of the same task.
        task = measures[0][0]
        if previous_task is not None:
            rows.append(lt.Rule if task != previous_task else lt.Gap)
        previous_task = task
        # Um modelo ocupa duas linhas (BA e MCC): o rótulo da primeira linha
        # vira \multirow centralizado verticalmente sobre as duas.
        grupo: list[list[str] | object] = []
        for measure_index, (column, symbol) in enumerate(measures):
            cells = [MODEL_LABEL.get(model, model) if measure_index == 0 else "", symbol]
            for validation in ("LOOCV", "LOFO"):
                hit = block[block["validation"] == validation]
                value = hit.iloc[0][column] if not hit.empty else float("nan")
                cells.append(fmt.decimal(value, places=3) if pd.notna(value) else "---")
            grupo.append(cells)
        grupo[0][0] = lt.Multirow(MODEL_LABEL.get(model, model), len(grupo))
        rows.extend(grupo)

    # Preserve published rows while flagging the exploratory preprocessing:
    # global ranks of the regression response precede each held-out fold.
    note = (
        "Modelos treinados sobre 14 descritores estáticos de paisagem nas 51 instâncias "
        "rotuladas. $r_s$ é a correlação de Spearman entre ganho previsto e observado, e "
        "$R^2$, o coeficiente de determinação da regressão; BA é a acurácia balanceada e MCC "
        "o coeficiente de correlação de Matthews da classificação em ajuda e não ajuda. "
        "A validação deixa-uma-família retira uma suíte inteira do treino, mas a regressão "
        "original calculou os postos da resposta nas 51 instâncias antes das dobras; MaF7 "
        "e DTLZ7 também têm implementação funcional coincidente e podem cruzar dobras "
        "por suíte. As correlações da regressão nesta tabela são históricas e exploratórias; "
        "a Tabela~\\ref{tab:ativacao_robustez} reestima o desfecho com pré-processamento "
        "da resposta dentro da dobra e retém DTLZ e MaF juntos. "
        "---: valor não registrado no artefato."
    )

    return lt.render(
        header=["Modelo", "Medida", "Deixa-uma-instância", "Deixa-uma-família"],
        rows=rows,
        colspec="llrr",
        caption=(
            "Capacidade preditiva dos descritores estáticos de paisagem sob validação "
            "deixa-uma-instância e deixa-uma-família."
        ),
        label="tab:fla_modelos",
        producer=__file__,
        sources=[MODELS],
        note=note,
    )


def build_separation() -> str | None:
    if _missing(MAIN_TESTS):
        return None
    tests = pd.read_csv(MAIN_TESTS)
    todos = tests[tests["early_frac"].sub(EARLY_FRAC).abs() < 1e-9].copy()
    if todos.empty:
        print(f"ERRO: nenhuma linha em early_frac={EARLY_FRAC}", file=sys.stderr)
        return None
    # A tabela exibe só parte dos observáveis testados; a nota afirma que são os
    # de menor valor-p, e o gerador falha se isso deixar de valer.
    n_testados = len(todos)
    menores = set(todos.nsmallest(len(FEATURE_LABEL), "p_value")["feature"])
    if menores != set(FEATURE_LABEL):
        print(
            f"ERRO: os observáveis exibidos não são os {len(FEATURE_LABEL)} de menor valor-p "
            f"({sorted(menores)})",
            file=sys.stderr,
        )
        return None
    early = todos[todos["feature"].isin(FEATURE_LABEL)].copy()

    early["_order"] = early["feature"].map({f: i for i, f in enumerate(FEATURE_LABEL)})
    early = early.sort_values("_order")

    rows: list[list[str] | object] = []
    for _, row in early.iterrows():
        # "Sobreviver a BH" is q below 0,05: the q column says it, and the
        # builder fails if the artifact's flag ever disagrees.
        if bool(row["significant_bh"]) != (float(row["p_bh"]) < 0.05):
            print(
                f"ERRO: {row['feature']}: significant_bh não corresponde a q < 0,05",
                file=sys.stderr,
            )
            return None
        rows.append([
            FEATURE_LABEL[row["feature"]],
            fmt.smart(row["helps_median"]),
            fmt.smart(row["not_helps_median"]),
            fmt.decimal(row["a12"], places=3),
            fmt.pvalue(float(row["p_bh"])),
        ])

    n_cases = int(early.iloc[0]["n_labeled_cases"])
    n_helps = int(early.iloc[0]["n_helps"])
    n_not = int(early.iloc[0]["n_not_helps"])

    note = (
        f"A tabela reproduz {len(early)} dos {n_testados} observáveis testados, os de menor "
        "valor-$p$ no teste de Mann--Whitney entre as classes, e $q$ é o valor-$p$ após "
        f"correção de Benjamini--Hochberg sobre os {n_testados}, com $\\alpha = 0{{,}}05$. As "
        "diferenças finais de IGD e de HV são medidas ao fim da execução; os demais "
        f"observáveis, nos primeiros {int(EARLY_FRAC * 100)}\\% das gerações. São {n_cases} "
        "instâncias rotuladas, com 30 execuções pareadas por semente; $A_{12}$ é o tamanho de "
        "efeito de Vargha--Delaney. Os rótulos derivam da comparação em IGD da coorte "
        "da comparação principal, sem correção de multiplicidade, e não constituem desfecho "
        "independente."
    )

    return lt.render(
        header=[
            [lt.Span("", 1), lt.Span("Mediana", 2), lt.Span("", 2)],
            [
                "Observável",
                f"Ajuda ($n={n_helps}$)",
                f"Não ajuda ($n={n_not}$)",
                "$A_{12}$",
                "$q$",
            ],
        ],
        rows=rows,
        colspec="lcccr",
        caption=(
            "Separação entre as classes de instância pelos observáveis da dinâmica "
            "inicial da população."
        ),
        label="tab:dinamica_separacao",
        producer=__file__,
        sources=[MAIN_TESTS],
        note=note,
    )


def build_threshold() -> str | None:
    if _missing(LOOCV) or _missing(LOFO):
        return None

    rows: list[list[str] | object] = []
    lofo_row = None
    for path, validation in ((LOOCV, "LOOCV"), (LOFO, "LOFO")):
        table = pd.read_csv(path)
        hit = table[table["feature"] == THRESHOLD_FEATURE]
        if len(hit) != 1:
            print(
                f"ERRO: esperava 1 linha para {THRESHOLD_FEATURE} em {path}, "
                f"encontrei {len(hit)}",
                file=sys.stderr,
            )
            return None
        row = hit.iloc[0]
        if validation == "LOFO":
            lofo_row = row
        rows.append([
            VALIDATION_LABEL[validation],
            fmt.decimal(row["balanced_accuracy"], places=3),
            fmt.decimal(row["mcc"], places=3),
            fmt.decimal(row["sensitivity"], places=3),
            fmt.decimal(row["specificity"], places=3),
            fmt.decimal(row["median_threshold"], places=3),
        ])

    # Each leave-one-family-out fold fits the threshold on the *other* families
    # (src/python/fla/test_dynamic_signal.py, run_lofo_threshold_tests), so the
    # evaluated family never informs its own threshold. The per-fold values are
    # the ones the controller later applied.
    by_value: dict[float, list[str]] = {}
    for part in str(lofo_row["family_rule_summary"]).split(";"):
        family, threshold, _direction = part.split(":")
        by_value.setdefault(round(float(threshold), 3), []).append(
            FAMILY_DISPLAY.get(family.upper(), family)
        )

    def _either(names: list[str]) -> str:
        names = sorted(names)
        return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " ou " + names[-1]

    folds = " e ".join(
        f"{fmt.decimal(value)} ao reter {_either(families)}"
        for value, families in sorted(by_value.items())
    )
    # How far the two estimates can be trusted, and what their order means, is
    # argued in the text that cites the table; the note defines the rule, the
    # measures and the thresholds behind the median the column shows.
    note = (
        "Regra de limiar único sobre a renovação média do arquivo nos primeiros "
        f"{int(EARLY_FRAC * 100)}\\% das gerações: o operador fica ligado quando a renovação "
        "atinge o limiar. O limiar é buscado exaustivamente entre os pontos médios de valores "
        "adjacentes, maximizando a acurácia balanceada (BA), e é sempre ajustado sem o que se "
        "avalia: sem a instância retida, na validação deixa-uma-instância, e sem a família "
        "inteira, na deixa-uma-família. MCC: coeficiente de correlação de Matthews; "
        "sensibilidade: fração das instâncias em que o operador ajuda que a regra mantém "
        "ligado; especificidade: fração das demais que ela desliga. A coluna Limiar exibe a "
        "mediana dos limiares de cada validação; na deixa-uma-família, os limiares ajustados "
        f"foram {folds}."
    )

    return lt.render(
        header=[
            "Validação", "BA", "MCC", "Sensibilidade", "Especificidade", "Limiar",
        ],
        rows=rows,
        colspec="lccccc",
        caption=(
            "Regra de limiar sobre a renovação do arquivo na fase inicial, como critério "
            "binário de ativação do operador."
        ),
        label="tab:dinamica_limiar",
        producer=__file__,
        sources=[LOOCV, LOFO],
        note=note,
    )


def _suite_of(problem: str) -> str:
    match = _SUITE_RE.match(str(problem))
    if not match:
        raise ValueError(f"não foi possível extrair a suíte de {problem!r}")
    return match.group(0).upper()


def build_dinamica_suite() -> str | None:
    if _missing(DYNAMIC_TEST) or _missing(LOFO):
        return None

    cases = pd.read_csv(DYNAMIC_TEST)
    cases = cases[
        (cases["early_frac"].sub(EARLY_FRAC).abs() < 1e-9)
        & (cases["role"] == "synthetic")
        & (cases["label_binary_eval"].isin(["HELPS", "NOT_HELPS"]))
    ].copy()
    n_helps = int((cases["label_binary_eval"] == "HELPS").sum())
    n_not_helps = int((cases["label_binary_eval"] == "NOT_HELPS").sum())
    if len(cases) != 51 or n_helps != 41 or n_not_helps != 10:
        print(
            f"ERRO: esperava 51 casos rotulados (41 HELPS, 10 NOT_HELPS) em "
            f"{DYNAMIC_TEST} com early_frac={EARLY_FRAC}, encontrei {len(cases)} "
            f"({n_helps} HELPS, {n_not_helps} NOT_HELPS)",
            file=sys.stderr,
        )
        return None

    cases["suite"] = cases["problem"].map(_suite_of)

    lofo = pd.read_csv(LOFO)
    lofo_hit = lofo[lofo["feature"] == THRESHOLD_FEATURE]
    if len(lofo_hit) != 1:
        print(
            f"ERRO: esperava 1 linha para {THRESHOLD_FEATURE} em {LOFO}, "
            f"encontrei {len(lofo_hit)}",
            file=sys.stderr,
        )
        return None
    lofo_row = lofo_hit.iloc[0]

    threshold_by_suite: dict[str, float] = {}
    for part in str(lofo_row["family_rule_summary"]).split(";"):
        family, threshold, direction = part.split(":")
        if direction != "ge":
            print(
                f"ERRO: direção inesperada {direction!r} para {family} em "
                f"{THRESHOLD_FEATURE}",
                file=sys.stderr,
            )
            return None
        threshold_by_suite[family.upper()] = float(threshold)

    missing_suites = sorted(set(cases["suite"]) - set(threshold_by_suite))
    if missing_suites:
        print(f"ERRO: sem limiar LOFO para as suítes {missing_suites}", file=sys.stderr)
        return None

    cases["threshold"] = cases["suite"].map(threshold_by_suite)
    cases["kept_on"] = cases["ivf_turnover_early"] >= cases["threshold"]
    cases["actual_helps"] = cases["label_binary_eval"] == "HELPS"

    tp = int((cases["kept_on"] & cases["actual_helps"]).sum())
    tn = int((~cases["kept_on"] & ~cases["actual_helps"]).sum())
    fp = int((cases["kept_on"] & ~cases["actual_helps"]).sum())
    fn = int((~cases["kept_on"] & cases["actual_helps"]).sum())
    reference = (
        int(lofo_row["tp"]), int(lofo_row["tn"]), int(lofo_row["fp"]), int(lofo_row["fn"])
    )
    if (tp, tn, fp, fn) != reference:
        print(
            f"ERRO: tp/tn/fp/fn recomputados {(tp, tn, fp, fn)} divergem do artefato "
            f"LOFO {reference}",
            file=sys.stderr,
        )
        return None

    cases["off_by_partition"] = cases["suite"] == "WFG"
    cases["off_by_rule"] = ~cases["kept_on"]
    coincide = cases["off_by_rule"] == cases["off_by_partition"]
    n_coincide = int(coincide.sum())
    n_total = len(cases)
    differing = cases.loc[~coincide, ["problem", "m", "label_binary_eval"]]

    cases["rule_correct"] = cases["kept_on"] == cases["actual_helps"]
    partition_kept_on = ~cases["off_by_partition"]
    cases["partition_correct"] = partition_kept_on == cases["actual_helps"]
    subset_ok = bool((~cases["rule_correct"] | cases["partition_correct"]).all())

    differing_display = ", ".join(
        f"{row.problem} (M={row.m}, {row.label_binary_eval})" for row in differing.itertuples()
    ) or "nenhuma"

    print(f"[dinamica_suite] coincidência regra/partição WFG: {n_coincide}/{n_total}")
    print(f"[dinamica_suite] instâncias em que regra e partição divergem: {differing_display}")
    print(
        "[dinamica_suite] toda decisão correta da regra também é correta na partição "
        f"WFG/demais: {subset_ok}"
    )
    if not subset_ok:
        print(
            "ERRO: existe decisão correta da regra que a partição WFG/demais não reproduz",
            file=sys.stderr,
        )
        return None

    suites = list(FAMILY_DISPLAY)
    rows: list[list[str] | object] = []
    for suite in suites:
        sub = cases[cases["suite"] == suite]
        n = len(sub)
        helps = int((sub["label_binary_eval"] == "HELPS").sum())
        not_helps = n - helps
        med_ivf = float(sub["ivf_turnover_early"].median())
        med_spea2 = float(sub["spea2_turnover_early"].median())
        off = int((~sub["kept_on"]).sum())
        off_helps = int((~sub["kept_on"] & sub["actual_helps"]).sum())
        rows.append([
            FAMILY_DISPLAY[suite],
            str(n),
            str(helps),
            str(not_helps),
            fmt.decimal(med_ivf, places=3),
            fmt.decimal(med_spea2, places=3),
            fmt.decimal(threshold_by_suite[suite], places=3),
            str(off),
            str(off_helps),
        ])

    total_med_ivf = float(cases["ivf_turnover_early"].median())
    total_med_spea2 = float(cases["spea2_turnover_early"].median())
    total_off = int((~cases["kept_on"]).sum())
    total_off_helps = int((~cases["kept_on"] & cases["actual_helps"]).sum())
    rows.append(lt.Rule)
    rows.append([
        "Total",
        str(n_total),
        str(n_helps),
        str(n_not_helps),
        fmt.decimal(total_med_ivf, places=3),
        fmt.decimal(total_med_spea2, places=3),
        "---",
        str(total_off),
        str(total_off_helps),
    ])

    # The coincidence with the WFG partition reads off the table (every WFG
    # instance switched off, and two outside it) and is argued in the text that
    # cites it; the checks above keep that argument true. The note defines the
    # decision and the columns.
    note = (
        "Decisão no nível da instância: a regra desliga o operador quando a renovação do "
        f"arquivo nos primeiros {int(EARLY_FRAC * 100)}\\% das gerações (mediana de 30 "
        "execuções pareadas por semente, tal como registrada no artefato de origem) fica "
        "abaixo do limiar da suíte da instância. Cada limiar vem da validação "
        "deixa-uma-família da renovação do arquivo do IVF/SPEA2 "
        "(Tabela~\\ref{tab:dinamica_limiar}) e é ajustado sem a suíte que avalia. "
        "Renovação mediana: mediana, entre as instâncias da suíte, da renovação de cada "
        "instância. Desligadas pela regra: total de instâncias classificadas pela mediana e, "
        "entre elas, aquelas em que o operador ajuda; não são decisões por execução do "
        "controlador. Os rótulos derivam da comparação em IGD da coorte da comparação principal, "
        "sem correção de multiplicidade, e não constituem desfecho independente."
    )

    return lt.render(
        header=[
            [
                lt.Span("", 1),
                lt.Span("Instâncias", 3),
                lt.Span("Renovação mediana", 2),
                lt.Span("", 1),
                lt.Span("Desligadas pela regra", 2),
            ],
            [
                "Suíte", "Total", "Ajuda", "Não ajuda",
                "IVF/SPEA2", "SPEA2", "Limiar", "Total", "Ajuda",
            ],
        ],
        rows=rows,
        colspec="l" + "c" * 8,
        tabcolsep="4pt",
        caption=(
            "Regra de limiar sobre a renovação do arquivo, aberta por suíte de "
            "problemas de teste."
        ),
        label="tab:dinamica_suite",
        producer=__file__,
        sources=[DYNAMIC_TEST, LOFO],
        note=note,
    )


def main() -> int:
    failed = False
    targets = (
        (build_models(), OUT_MODELS),
        (build_separation(), OUT_SEPARATION),
        (build_threshold(), OUT_THRESHOLD),
        (build_dinamica_suite(), OUT_DINAMICA_SUITE),
    )
    for content, path in targets:
        if content is None:
            failed = True
            continue
        lt.write(path, content)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
