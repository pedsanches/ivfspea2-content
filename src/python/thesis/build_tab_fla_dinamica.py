#!/usr/bin/env python3
"""Activation-family tables: landscape models, early dynamics, threshold rule.

One protocol per estimate, stated once in the dissertation's text:

* **Static landscape regression.** A random forest predicts the median IGD
  difference (SPEA2 minus IVF/SPEA2) from the 14 landscape descriptors of
  ``fla_dataset.csv``. In every fold a Yeo--Johnson transform of the response
  is fitted on the training response only, and predictions are returned to the
  original scale before the pooled out-of-fold Spearman correlation. The
  leave-one-family-out folds hold DTLZ and MaF out together, so the functional
  duplicate MaF7/DTLZ7 (at M = 2 and M = 3) never straddles a fold. This
  replaces the regression rows of ``fla_model_comparison.csv``, whose response
  was ranked over all 51 instances before the folds.
* **Static classifiers.** Read as recorded in ``fla_model_comparison.csv``;
  their leave-one-family-out folds hold one suite out at a time.
* **Early-renewal threshold rule.** The observable and the 20% window are
  fixed; each fold fits only the threshold and its direction. Leave-one-out
  comes from ``dynamic_signal_loocv.csv``. Leave-one-family-out is refitted
  here with DTLZ and MaF held out together; the builder fails unless it yields
  the same decisions, metrics and thresholds as the suite-by-suite folds of
  ``dynamic_signal_lofo.csv``, whose thresholds the controller applied.
* **Suite partition.** "Switch off in WFG and only there", scored on the same
  labels with nothing fitted: a retrospective yardstick written after the labels
  showed that eight of the ten non-helped instances are WFG.

``data/processed/classifier_comparison.csv`` is NOT used: its
``Early-turnover threshold / LOOCV`` row is an in-sample resubstitution fit
stored under the LOOCV label (BA 0.791 where the genuine leave-one-out estimate
is 0.691). See ``thesis/masters/REWRITE_SPEC.md`` OQ-13.

Writes: results/thesis/tab_fla_modelos.tex
        results/thesis/tab_dinamica_separacao.tex
        results/thesis/tab_dinamica_limiar.tex
        results/thesis/tab_dinamica_suite.tex
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PowerTransformer

from ivfspea2.paths import DATA_PROCESSED, RESULTS_TABLES, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

MODELS = RESULTS_TABLES / "fla_model_comparison.csv"
STATIC = DATA_PROCESSED / "fla_dataset.csv"
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
LABEL = "label_binary_eval"
FAMILY_DISPLAY = {"DTLZ": "DTLZ", "MAF": "MaF", "WFG": "WFG", "ZDT": "ZDT"}
GROUPED = {"DTLZ": "DTLZ+MAF", "MAF": "DTLZ+MAF"}

# Static regression: response and the 14 retained descriptors of fla_dataset.csv.
RESPONSE = "delta_igd"
FEATURES = (
    "corr_obj_mean", "skewness_mean", "kurtosis_mean", "cv_mean",
    "dom_depth_std", "front_connectivity", "front_diameter", "front_gap_ratio",
    "autocorr_mean", "info_content", "neutrality_ratio", "fdc_mean", "n_obj", "n_var",
)
RF_PARAMS = dict(
    n_estimators=500, max_depth=6, min_samples_leaf=3, max_features="sqrt", random_state=42,
)

# Static classifiers, read as recorded.
FEATURE_SET = "SET_ALL"
CLASSIFIER_LABEL = {
    "RF_Classification": "Floresta aleatória (classificação)",
    "LogisticRegression": "Regressão logística",
    "SVC_RBF": "SVC com núcleo RBF",
    "KNN_5": "$k$-vizinhos ($k=5$)",
}

FEATURE_LABEL = {
    "ivf_turnover_early": "Renovação do arquivo (IVF/SPEA2)",
    "spea2_turnover_early": "Renovação do arquivo (SPEA2)",
    "hv_final_delta": "Diferença final de HV",
    "igd_final_delta": "Diferença final de IGD",
    "ivf_cycles_early": "Ciclos de IVF na fase inicial",
}


def _missing(path: Path) -> bool:
    if not path.exists():
        print(f"ERRO: artefato ausente: {path}", file=sys.stderr)
        return True
    return False


def _suite_of(problem: str) -> str:
    match = _SUITE_RE.match(str(problem))
    if not match:
        raise ValueError(f"não foi possível extrair a suíte de {problem!r}")
    return match.group(0).upper()


def _fold_of(problem: str) -> str:
    suite = _suite_of(problem)
    return GROUPED.get(suite, suite)


def _assert_columns(frame: pd.DataFrame, columns: list[str], source: Path) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{source}: colunas ausentes: {missing}")


# =====================================================================
# Static landscape regression
# =====================================================================
def _predict_fold(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    """Fit all learnt transforms on train only; return natural-scale response."""
    transformer = PowerTransformer(method="yeo-johnson", standardize=True)
    transformed_y = transformer.fit_transform(train_y.reshape(-1, 1)).ravel()
    model = RandomForestRegressor(**RF_PARAMS)
    model.fit(train_x, transformed_y)
    return transformer.inverse_transform(model.predict(test_x).reshape(-1, 1)).ravel()


def static_regression() -> dict[str, float]:
    """Pooled out-of-fold Spearman correlation, leave-one-out and by suite."""
    frame = pd.read_csv(STATIC)
    _assert_columns(frame, ["instance", RESPONSE, *FEATURES], STATIC)
    if len(frame) != 51:
        raise ValueError(f"{STATIC}: esperava 51 instâncias, encontrei {len(frame)}")
    x = frame.loc[:, list(FEATURES)].to_numpy(dtype=float)
    y = frame[RESPONSE].to_numpy(dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError(f"{STATIC}: descritores ou resposta não finitos")

    loocv = np.empty(len(frame), dtype=float)
    for held in range(len(frame)):
        train = np.arange(len(frame)) != held
        loocv[held] = _predict_fold(x[train], y[train], x[~train])[0]

    groups = frame["instance"].map(_fold_of).to_numpy()
    lofo = np.empty(len(frame), dtype=float)
    for group in sorted(set(groups)):
        held = groups == group
        lofo[held] = _predict_fold(x[~held], y[~held], x[held])

    r_loocv = float(spearmanr(y, loocv).statistic)
    r_lofo = float(spearmanr(y, lofo).statistic)
    if not np.isfinite(r_loocv) or not np.isfinite(r_lofo):
        raise ValueError("correlação de Spearman estática indefinida")
    return {"LOOCV": r_loocv, "LOFO": r_lofo}


# =====================================================================
# Threshold rule and suite partition
# =====================================================================
def _labelled_cases() -> pd.DataFrame:
    """The 51 labelled synthetic instances at the early window."""
    cases = pd.read_csv(DYNAMIC_TEST)
    _assert_columns(
        cases,
        ["problem", "instance_key", "role", "early_frac", THRESHOLD_FEATURE, LABEL],
        DYNAMIC_TEST,
    )
    cases = cases[
        (cases["early_frac"].sub(EARLY_FRAC).abs() < 1e-9)
        & (cases["role"] == "synthetic")
        & (cases[LABEL].isin(["HELPS", "NOT_HELPS"]))
    ].copy()
    n_helps = int((cases[LABEL] == "HELPS").sum())
    n_not_helps = int((cases[LABEL] == "NOT_HELPS").sum())
    if len(cases) != 51 or n_helps != 41 or n_not_helps != 10:
        raise ValueError(
            f"{DYNAMIC_TEST}: esperava 51 casos rotulados (41 HELPS, 10 NOT_HELPS) com "
            f"early_frac={EARLY_FRAC}, encontrei {len(cases)} ({n_helps} HELPS, "
            f"{n_not_helps} NOT_HELPS)"
        )
    if not np.isfinite(cases[THRESHOLD_FEATURE].to_numpy(dtype=float)).all():
        raise ValueError(f"{DYNAMIC_TEST}: {THRESHOLD_FEATURE} não finito")
    cases["suite"] = cases["problem"].map(_suite_of)
    return cases


def _classification_metrics(y: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    tp = int(((y == 1) & (prediction == 1)).sum())
    tn = int(((y == 0) & (prediction == 0)).sum())
    fp = int(((y == 0) & (prediction == 1)).sum())
    fn = int(((y == 1) & (prediction == 0)).sum())
    sensitivity = tp / (tp + fn) if tp + fn else float("nan")
    specificity = tn / (tn + fp) if tn + fp else float("nan")
    denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = ((tp * tn - fp * fn) / denominator) if denominator else float("nan")
    return {
        "ba": (sensitivity + specificity) / 2,
        "mcc": float(mcc),
        "sensitivity": sensitivity,
        "specificity": specificity,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def _threshold_candidates(values: np.ndarray) -> np.ndarray:
    unique = np.unique(values)
    if len(unique) < 2:
        return unique
    return np.r_[unique[0] - 1e-12, (unique[:-1] + unique[1:]) / 2, unique[-1] + 1e-12]


def _fit_threshold(x: np.ndarray, y: np.ndarray) -> tuple[float, str]:
    best: tuple[tuple[float, float, float], float, str] | None = None
    for direction in ("ge", "le"):
        for threshold in _threshold_candidates(x):
            if direction == "ge":
                pred = (x >= threshold).astype(int)
            else:
                pred = (x <= threshold).astype(int)
            met = _classification_metrics(y, pred)
            key = (met["ba"], met["mcc"], float((pred == y).mean()))
            if best is None or key > best[0]:
                best = (key, float(threshold), direction)
    if best is None:
        raise ValueError("não há limiar ajustável")
    return best[1], best[2]


def grouped_lofo(cases: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    """Leave-one-family-out with DTLZ and MaF held out together.

    Returns the metrics and the threshold each suite was evaluated with.
    """
    x = cases[THRESHOLD_FEATURE].to_numpy(dtype=float)
    y = (cases[LABEL] == "HELPS").to_numpy(dtype=int)
    folds = cases["problem"].map(_fold_of)
    prediction = np.empty(len(cases), dtype=int)
    threshold_by_suite: dict[str, float] = {}
    fold_thresholds: list[float] = []
    for fold in sorted(folds.unique()):
        held = folds.eq(fold).to_numpy()
        threshold, direction = _fit_threshold(x[~held], y[~held])
        if direction != "ge":
            raise ValueError(f"direção inesperada {direction!r} ao reter {fold}")
        prediction[held] = (x[held] >= threshold).astype(int)
        fold_thresholds.append(threshold)
        for suite in set(cases.loc[held, "suite"]):
            threshold_by_suite[suite] = threshold
    metrics = _classification_metrics(y, prediction)
    metrics["median_threshold"] = float(np.median(fold_thresholds))
    return metrics, threshold_by_suite


def wfg_partition(cases: pd.DataFrame) -> dict[str, float]:
    """Switch off in WFG and only there, on the same labels; nothing is fitted."""
    y = (cases[LABEL] == "HELPS").to_numpy(dtype=int)
    keep_on = cases["suite"].ne("WFG").to_numpy(dtype=int)
    return _classification_metrics(y, keep_on)


def _lofo_artifact_row() -> pd.Series:
    lofo = pd.read_csv(LOFO)
    hit = lofo[lofo["feature"] == THRESHOLD_FEATURE]
    if len(hit) != 1:
        raise ValueError(f"{LOFO}: esperava 1 linha para {THRESHOLD_FEATURE}, encontrei {len(hit)}")
    return hit.iloc[0]


def _artifact_thresholds(row: pd.Series) -> dict[str, float]:
    thresholds: dict[str, float] = {}
    for part in str(row["family_rule_summary"]).split(";"):
        family, threshold, direction = part.split(":")
        if direction != "ge":
            raise ValueError(f"direção inesperada {direction!r} para {family} em {LOFO}")
        thresholds[family.upper()] = float(threshold)
    return thresholds


def checked_grouped_lofo(cases: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    """Grouped folds, verified against the suite-by-suite artifact.

    The controller ran with the artifact's thresholds; the text states that
    holding DTLZ and MaF out together leaves decisions, metrics and thresholds
    unchanged. The builder fails if that stops being true.
    """
    metrics, threshold_by_suite = grouped_lofo(cases)
    row = _lofo_artifact_row()
    reference = (int(row["tp"]), int(row["tn"]), int(row["fp"]), int(row["fn"]))
    recomputed = (metrics["tp"], metrics["tn"], metrics["fp"], metrics["fn"])
    if recomputed != reference:
        raise ValueError(f"LOFO agrupado {recomputed} diverge do artefato por suíte {reference}")
    for key, column in (("ba", "balanced_accuracy"), ("mcc", "mcc"),
                        ("sensitivity", "sensitivity"), ("specificity", "specificity")):
        if abs(metrics[key] - float(row[column])) > 1e-9:
            raise ValueError(
                f"LOFO agrupado: {key} {metrics[key]} diverge do artefato {row[column]}"
            )
    artifact = _artifact_thresholds(row)
    if set(artifact) != set(threshold_by_suite) or any(
        round(artifact[s], 3) != round(threshold_by_suite[s], 3) for s in artifact
    ):
        raise ValueError(
            f"limiares agrupados {threshold_by_suite} divergem dos limiares do artefato {artifact}"
        )
    return metrics, threshold_by_suite


# =====================================================================
# Tables
# =====================================================================
def build_models() -> str | None:
    if _missing(MODELS) or _missing(STATIC):
        return None
    regression = static_regression()
    models = pd.read_csv(MODELS)
    subset = models[models["feature_set"] == FEATURE_SET]

    regression_rows: list[list[str | lt.Multirow]] = [[
        "Floresta aleatória (regressão)",
        "$r_s$",
        fmt.decimal(regression["LOOCV"], places=3),
        fmt.decimal(regression["LOFO"], places=3),
    ]]

    rows: list[list[str | lt.Multirow] | object] = [*regression_rows, lt.Rule]
    for index, (model, label) in enumerate(CLASSIFIER_LABEL.items()):
        block = subset[subset["model"] == model]
        if block.empty:
            print(f"ERRO: modelo {model} ausente de {MODELS}", file=sys.stderr)
            return None
        if index:
            rows.append(lt.Gap)
        grupo: list[list[str | lt.Multirow]] = []
        for column, symbol in (("balanced_acc", "BA"), ("mcc", "MCC")):
            cells: list[str | lt.Multirow] = ["", symbol]
            for validation in ("LOOCV", "LOFO"):
                hit = block[block["validation"] == validation]
                if len(hit) != 1 or pd.isna(hit.iloc[0][column]):
                    print(
                        f"ERRO: {model}/{validation}/{column} ausente de {MODELS}",
                        file=sys.stderr,
                    )
                    return None
                cells.append(fmt.decimal(float(hit.iloc[0][column]), places=3))
            grupo.append(cells)
        grupo[0][0] = lt.Multirow(label, len(grupo))
        rows.extend(grupo)

    note = (
        "Modelos treinados sobre 14 descritores estáticos de paisagem nas 51 instâncias "
        "rotuladas. $r_s$: correlação de Spearman entre o ganho previsto e o observado, a "
        "diferença entre as medianas de IGD; BA: acurácia balanceada; MCC: coeficiente de "
        "correlação de Matthews, na classificação em ajuda e não ajuda. Na regressão, a "
        "transformação da resposta é ajustada só no treino de cada dobra, e a validação "
        "deixa-uma-família retém DTLZ e MaF juntas; nos classificadores, retém uma suíte por vez."
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
        sources=[STATIC, MODELS],
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

    n_helps = int(early.iloc[0]["n_helps"])
    n_not = int(early.iloc[0]["n_not_helps"])

    note = (
        "Mediana de cada observável por classe de instância; $A_{12}$ de Vargha--Delaney entre "
        "as classes; $q$: valor-$p$ do teste de Mann--Whitney com correção de "
        f"Benjamini--Hochberg sobre os {n_testados} observáveis testados, dos quais a tabela "
        f"mostra os {len(early)} de menor valor-$p$. Observáveis medidos nos primeiros "
        f"{int(EARLY_FRAC * 100)}\\% das gerações, exceto as diferenças finais de IGD e de HV; "
        "30 execuções pareadas por semente em cada instância."
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


def _fold_sentence(threshold_by_suite: dict[str, float]) -> str:
    """'0,216 ao reter DTLZ e MaF ou ZDT e 0,248 ao reter WFG', from the folds."""
    by_value: dict[float, list[str]] = {}
    for fold in sorted({GROUPED.get(s, s) for s in threshold_by_suite}):
        suites = [s for s in FAMILY_DISPLAY if GROUPED.get(s, s) == fold]
        value = round(threshold_by_suite[suites[0]], 3)
        by_value.setdefault(value, []).append(" e ".join(FAMILY_DISPLAY[s] for s in suites))
    return " e ".join(
        f"{fmt.decimal(value)} ao reter {' ou '.join(folds)}"
        for value, folds in sorted(by_value.items())
    )


def build_threshold() -> str | None:
    if _missing(LOOCV) or _missing(LOFO) or _missing(DYNAMIC_TEST):
        return None
    try:
        cases = _labelled_cases()
        grouped, threshold_by_suite = checked_grouped_lofo(cases)
        partition = wfg_partition(cases)
    except (ValueError, KeyError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return None

    loocv = pd.read_csv(LOOCV)
    hit = loocv[loocv["feature"] == THRESHOLD_FEATURE]
    if len(hit) != 1:
        print(f"ERRO: esperava 1 linha para {THRESHOLD_FEATURE} em {LOOCV}", file=sys.stderr)
        return None
    loo = hit.iloc[0]

    def _row(label: str, ba: float, mcc: float, sens: float, spec: float, limiar: str) -> list[str]:
        return [
            label,
            fmt.decimal(ba, places=3),
            fmt.decimal(mcc, places=3),
            fmt.decimal(sens, places=3),
            fmt.decimal(spec, places=3),
            limiar,
        ]

    rows: list[list[str] | object] = [
        _row(
            "Regra, deixa-uma-instância",
            float(loo["balanced_accuracy"]), float(loo["mcc"]),
            float(loo["sensitivity"]), float(loo["specificity"]),
            fmt.decimal(float(loo["median_threshold"]), places=3),
        ),
        _row(
            "Regra, deixa-uma-família",
            grouped["ba"], grouped["mcc"], grouped["sensitivity"], grouped["specificity"],
            fmt.decimal(grouped["median_threshold"], places=3),
        ),
        lt.Rule,
        _row(
            "Partição WFG/demais",
            partition["ba"], partition["mcc"], partition["sensitivity"], partition["specificity"],
            "---",
        ),
    ]

    note = (
        f"Regra: o operador fica ligado quando a renovação média do arquivo nos primeiros "
        f"{int(EARLY_FRAC * 100)}\\% das gerações atinge o limiar, ajustado sem a instância "
        "retida (deixa-uma-instância) ou sem a suíte retida, com DTLZ e MaF retidas juntas "
        "(deixa-uma-família); a coluna Limiar mostra a mediana dos limiares das dobras, que na "
        f"deixa-uma-família foram {_fold_sentence(threshold_by_suite)}. Partição: o operador é "
        "desligado nas instâncias WFG e só nelas, sem ajuste. BA e MCC como na "
        "Tabela~\\ref{tab:fla_modelos}; sensibilidade: fração das instâncias em que o operador "
        "ajuda que o critério mantém ligado; especificidade: fração das demais que ele desliga."
    )

    return lt.render(
        header=["Critério", "BA", "MCC", "Sensibilidade", "Especificidade", "Limiar"],
        rows=rows,
        colspec="lccccc",
        caption=(
            "Regra de limiar sobre a renovação inicial do arquivo e partição por suíte, como "
            "critérios binários de ativação do operador."
        ),
        label="tab:dinamica_limiar",
        producer=__file__,
        sources=[LOOCV, LOFO, DYNAMIC_TEST],
        note=note,
    )


def build_dinamica_suite() -> str | None:
    if _missing(DYNAMIC_TEST) or _missing(LOFO):
        return None
    try:
        cases = _labelled_cases()
        _metrics, threshold_by_suite = checked_grouped_lofo(cases)
    except (ValueError, KeyError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return None

    n_total = len(cases)
    n_helps = int((cases[LABEL] == "HELPS").sum())
    n_not_helps = n_total - n_helps

    cases["threshold"] = cases["suite"].map(threshold_by_suite)
    cases["kept_on"] = cases[THRESHOLD_FEATURE] >= cases["threshold"]
    cases["actual_helps"] = cases[LABEL] == "HELPS"

    cases["off_by_partition"] = cases["suite"] == "WFG"
    cases["off_by_rule"] = ~cases["kept_on"]
    coincide = cases["off_by_rule"] == cases["off_by_partition"]
    n_coincide = int(coincide.sum())
    differing = cases.loc[~coincide, ["problem", "m", LABEL]]

    cases["rule_correct"] = cases["kept_on"] == cases["actual_helps"]
    partition_kept_on = ~cases["off_by_partition"]
    cases["partition_correct"] = partition_kept_on == cases["actual_helps"]
    subset_ok = bool((~cases["rule_correct"] | cases["partition_correct"]).all())

    differing_display = ", ".join(
        f"{row.problem} (M={row.m}, {getattr(row, LABEL)})" for row in differing.itertuples()
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

    rows: list[list[str] | object] = []
    for suite in FAMILY_DISPLAY:
        sub = cases[cases["suite"] == suite]
        n = len(sub)
        helps = int((sub[LABEL] == "HELPS").sum())
        rows.append([
            FAMILY_DISPLAY[suite],
            str(n),
            str(helps),
            str(n - helps),
            fmt.decimal(float(sub["ivf_turnover_early"].median()), places=3),
            fmt.decimal(float(sub["spea2_turnover_early"].median()), places=3),
            fmt.decimal(threshold_by_suite[suite], places=3),
            str(int((~sub["kept_on"]).sum())),
            str(int((~sub["kept_on"] & sub["actual_helps"]).sum())),
        ])

    rows.append(lt.Rule)
    rows.append([
        "Total",
        str(n_total),
        str(n_helps),
        str(n_not_helps),
        fmt.decimal(float(cases["ivf_turnover_early"].median()), places=3),
        fmt.decimal(float(cases["spea2_turnover_early"].median()), places=3),
        "---",
        str(int((~cases["kept_on"]).sum())),
        str(int((~cases["kept_on"] & cases["actual_helps"]).sum())),
    ])

    note = (
        "Decisão por instância, e não por execução: a regra desliga o operador quando a mediana, "
        "nas 30 execuções da instância, da renovação do arquivo nos primeiros "
        f"{int(EARLY_FRAC * 100)}\\% das gerações fica abaixo do limiar ajustado sem a suíte da "
        "instância (Tabela~\\ref{tab:dinamica_limiar}). Renovação mediana: mediana, entre as "
        "instâncias da suíte, da renovação de cada instância. Desligadas pela regra: total e, "
        "entre elas, as instâncias em que o operador ajuda."
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
        (build_models, OUT_MODELS),
        (build_separation, OUT_SEPARATION),
        (build_threshold, OUT_THRESHOLD),
        (build_dinamica_suite, OUT_DINAMICA_SUITE),
    )
    for builder, path in targets:
        try:
            content = builder()
        except (ValueError, KeyError) as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            content = None
        if content is None:
            failed = True
            continue
        lt.write(path, content)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
