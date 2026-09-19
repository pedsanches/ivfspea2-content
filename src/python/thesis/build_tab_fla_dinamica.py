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
"""

from __future__ import annotations

import sys

import pandas as pd

from ivfspea2.paths import RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

MODELS = RESULTS_TABLES / "fla_model_comparison.csv"
MAIN_TESTS = RESULTS_TABLES / "dynamic_signal_main_tests.csv"
LOOCV = RESULTS_TABLES / "dynamic_signal_loocv.csv"
LOFO = RESULTS_TABLES / "dynamic_signal_lofo.csv"

OUT_MODELS = RESULTS_THESIS / "tab_fla_modelos.tex"
OUT_SEPARATION = RESULTS_THESIS / "tab_dinamica_separacao.tex"
OUT_THRESHOLD = RESULTS_THESIS / "tab_dinamica_limiar.tex"

EARLY_FRAC = 0.20
THRESHOLD_FEATURE = "ivf_turnover_early"

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


def build_models() -> str | None:
    if _missing(MODELS):
        return None
    models = pd.read_csv(MODELS)
    subset = models[models["feature_set"] == FEATURE_SET]

    rows: list[list[str] | object] = []
    for index, model in enumerate(MODEL_ORDER):
        block = subset[subset["model"] == model]
        if block.empty:
            continue
        if index:
            rows.append(lt.Rule)
        for validation_index, validation in enumerate(("LOOCV", "LOFO")):
            hit = block[block["validation"] == validation]
            if hit.empty:
                continue
            row = hit.iloc[0]
            rows.append([
                MODEL_LABEL.get(model, model) if validation_index == 0 else "",
                VALIDATION_LABEL.get(validation, validation),
                fmt.decimal(row["spearman_r"], places=3) if pd.notna(row["spearman_r"]) else "---",
                fmt.decimal(row["r2"], places=3) if pd.notna(row["r2"]) else "---",
                fmt.decimal(row["balanced_acc"], places=3) if pd.notna(row["balanced_acc"]) else "---",
                fmt.decimal(row["mcc"], places=3) if pd.notna(row["mcc"]) else "---",
            ])

    note = (
        "Modelos treinados sobre os 14 descritores estáticos de paisagem retidos, nas 51 "
        "instâncias rotuladas. $r_s$ é a correlação de Spearman entre ganho previsto e "
        "observado; BA é a acurácia balanceada e MCC o coeficiente de correlação de "
        "Matthews. A validação deixa-uma-família retira uma suíte inteira do treino, e é "
        "sob ela que a classificação binária deixa de generalizar: todos os modelos caem "
        "para a vizinhança do acaso, enquanto a regressão preserva o sinal. Os "
        "descritores estáticos servem, portanto, como prior sobre a magnitude do ganho, "
        "não como regra de decisão."
    )

    return lt.render(
        header=["Modelo", "Validação", "$r_s$", "$R^2$", "BA", "MCC"],
        rows=rows,
        colspec="|l|l|c|c|c|c|",
        caption=(
            "Capacidade preditiva dos descritores estáticos de paisagem sob validação "
            "deixa-uma-instância e deixa-uma-família."
        ),
        label="tab:fla_modelos",
        resize=True,
        producer=__file__,
        sources=[MODELS],
        note=note,
    )


def build_separation() -> str | None:
    if _missing(MAIN_TESTS):
        return None
    tests = pd.read_csv(MAIN_TESTS)
    early = tests[
        (tests["early_frac"].sub(EARLY_FRAC).abs() < 1e-9)
        & (tests["feature"].isin(FEATURE_LABEL))
    ].copy()
    if early.empty:
        print(f"ERRO: nenhuma linha em early_frac={EARLY_FRAC}", file=sys.stderr)
        return None

    early["_order"] = early["feature"].map({f: i for i, f in enumerate(FEATURE_LABEL)})
    early = early.sort_values("_order")

    rows: list[list[str] | object] = []
    for _, row in early.iterrows():
        rows.append([
            FEATURE_LABEL[row["feature"]],
            fmt.smart(row["helps_median"]),
            fmt.smart(row["not_helps_median"]),
            fmt.decimal(row["a12"], places=3),
            fmt.pvalue(float(row["p_bh"])),
            "sim" if bool(row["significant_bh"]) else "não",
        ])

    n_cases = int(early.iloc[0]["n_labeled_cases"])
    n_helps = int(early.iloc[0]["n_helps"])
    n_not = int(early.iloc[0]["n_not_helps"])

    note = (
        f"Observáveis medidos nos primeiros {int(EARLY_FRAC * 100)}\\% das gerações, sobre "
        f"{n_cases} instâncias rotuladas ({n_helps} em que o operador ajuda e {n_not} em "
        "que não ajuda), com 30 execuções pareadas por semente. $A_{12}$ é o tamanho de "
        "efeito de Vargha--Delaney e $q$ o valor-$p$ após correção de "
        "Benjamini--Hochberg. Apenas a renovação do arquivo sobrevive à correção. Os "
        "rótulos derivam do desfecho confirmatório em IGD e não constituem desfecho "
        "independente, razão pela qual a avaliação do controlador adota o HV."
    )

    return lt.render(
        header=[
            "Observável", "Mediana (ajuda)", "Mediana (não ajuda)",
            "$A_{12}$", "$q$", "Sobrevive a BH",
        ],
        rows=rows,
        colspec="|l|c|c|c|c|c|",
        caption=(
            "Separação entre as classes de instância pelos observáveis da dinâmica "
            "inicial da população."
        ),
        label="tab:dinamica_separacao",
        resize=True,
        producer=__file__,
        sources=[MAIN_TESTS],
        note=note,
    )


def build_threshold() -> str | None:
    if _missing(LOOCV) or _missing(LOFO):
        return None

    rows: list[list[str] | object] = []
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
        rows.append([
            VALIDATION_LABEL[validation],
            fmt.decimal(row["balanced_accuracy"], places=3),
            fmt.decimal(row["mcc"], places=3),
            fmt.decimal(row["sensitivity"], places=3),
            fmt.decimal(row["specificity"], places=3),
            fmt.decimal(row["median_threshold"], places=3),
        ])

    note = (
        "Regra de limiar único sobre a renovação média do arquivo nos primeiros "
        f"{int(EARLY_FRAC * 100)}\\% das gerações. O limiar é buscado exaustivamente entre "
        "os pontos médios de valores adjacentes, maximizando a acurácia balanceada. A "
        "acurácia é maior sob validação deixa-uma-família do que sob "
        "deixa-uma-instância porque o limiar é reajustado para cada família retida, e as "
        "famílias diferem no nível de renovação. O limiar exibido é a mediana dos "
        "limiares ajustados. Este resultado exige conhecer a família da instância; um "
        "limiar global único seria mais fraco."
    )

    return lt.render(
        header=[
            "Validação", "BA", "MCC", "Sensibilidade", "Especificidade", "Limiar",
        ],
        rows=rows,
        colspec="|l|c|c|c|c|c|",
        caption=(
            "Regra de limiar sobre a renovação do arquivo na fase inicial, como critério "
            "binário de ativação do operador."
        ),
        label="tab:dinamica_limiar",
        producer=__file__,
        sources=[LOOCV, LOFO],
        note=note,
    )


def main() -> int:
    failed = False
    targets = (
        (build_models(), OUT_MODELS),
        (build_separation(), OUT_SEPARATION),
        (build_threshold(), OUT_THRESHOLD),
    )
    for content, path in targets:
        if content is None:
            failed = True
            continue
        lt.write(path, content)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
