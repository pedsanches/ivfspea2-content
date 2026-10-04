#!/usr/bin/env python3
"""Robustness reanalysis for static activation evidence and early renewal.

The static forest predicts the IGD median difference from the 14 pre-specified
landscape descriptors in ``fla_dataset.csv``.  In every fold a Yeo--Johnson
response transformation is fitted *only* on the training response and its
prediction is inverse-transformed before the pooled out-of-fold Spearman
calculation.  Thus all predictions remain in the original IGD-difference
scale; unlike independently ranked fold targets, they can be pooled.

Family holdout treats DTLZ and MaF as one group.  This deliberately puts both
members of the MaF7/DTLZ7 functional duplication (at M=2 and M=3) on the held
out side whenever either family is evaluated.

The dynamic observable and 20% horizon were selected in the earlier analysis
using this evidence family. They are held fixed *for this sensitivity
calculation*, not independently pre-registered. Every fold re-fits only the
threshold and direction on the training partition. This is diagnostic label
reuse, not nested feature/horizon selection or an independent controller test.

The last rows score the fixed partition "switch off in WFG, keep elsewhere"
against the same labels. That rule was written down after the labels showed
that eight of the ten non-helped instances are WFG, so it is a retrospective
yardstick for the renewal rule on this sample, not a validated controller.
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

from ivfspea2.paths import DATA_PROCESSED, RESULTS_THESIS

import latex_table as lt
import ptbr_format as fmt

STATIC = DATA_PROCESSED / "fla_dataset.csv"
DYNAMIC = DATA_PROCESSED / "dynamic_signal_test.csv"
OUT = RESULTS_THESIS / "tab_ativacao_robustez.tex"

EARLY_FRAC = 0.20
RESPONSE = "delta_igd"
TURNOVER = "ivf_turnover_early"
LABEL = "label_binary_eval"
FEATURES = (
    "corr_obj_mean", "skewness_mean", "kurtosis_mean", "cv_mean",
    "dom_depth_std", "front_connectivity", "front_diameter", "front_gap_ratio",
    "autocorr_mean", "info_content", "neutrality_ratio", "fdc_mean", "n_obj", "n_var",
)
RF_PARAMS = dict(
    n_estimators=500, max_depth=6, min_samples_leaf=3, max_features="sqrt", random_state=42,
)


def _family(instance: str) -> str:
    match = re.match(r"[A-Za-z]+", str(instance))
    if match is None:
        raise ValueError(f"família ausente em {instance!r}")
    return match.group(0).upper()


def _grouped_family(instance: str) -> str:
    family = _family(instance)
    return "DTLZ+MAF" if family in {"DTLZ", "MAF"} else family


def _assert_columns(frame: pd.DataFrame, columns: tuple[str, ...] | list[str], source: Path) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{source}: colunas ausentes: {missing}")


def _predict_fold(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    """Fit all learnt transforms on train only; return natural-scale response."""
    transformer = PowerTransformer(method="yeo-johnson", standardize=True)
    transformed_y = transformer.fit_transform(train_y.reshape(-1, 1)).ravel()
    model = RandomForestRegressor(**RF_PARAMS)
    model.fit(train_x, transformed_y)
    return transformer.inverse_transform(model.predict(test_x).reshape(-1, 1)).ravel()


def static_oof() -> dict[str, float]:
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

    groups = frame["instance"].map(_grouped_family).to_numpy()
    lofo = np.empty(len(frame), dtype=float)
    for group in sorted(set(groups)):
        held = groups == group
        lofo[held] = _predict_fold(x[~held], y[~held], x[held])

    r_loocv = float(spearmanr(y, loocv).statistic)
    r_lofo = float(spearmanr(y, lofo).statistic)
    if not np.isfinite(r_loocv) or not np.isfinite(r_lofo):
        raise ValueError("correlação de Spearman estática indefinida")
    return {"loocv_r": r_loocv, "lofo_r": r_lofo, "n": float(len(frame)), "groups": float(len(set(groups)))}


def _classification_metrics(y: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    tp = int(((y == 1) & (prediction == 1)).sum())
    tn = int(((y == 0) & (prediction == 0)).sum())
    fp = int(((y == 0) & (prediction == 1)).sum())
    fn = int(((y == 1) & (prediction == 0)).sum())
    sensitivity = tp / (tp + fn) if tp + fn else float("nan")
    specificity = tn / (tn + fp) if tn + fp else float("nan")
    denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = ((tp * tn - fp * fn) / denominator) if denominator else float("nan")
    return {"ba": (sensitivity + specificity) / 2, "mcc": float(mcc), "tp": float(tp), "tn": float(tn), "fp": float(fp), "fn": float(fn)}


def _threshold_candidates(values: np.ndarray) -> np.ndarray:
    unique = np.unique(values)
    if len(unique) < 2:
        return unique
    return np.r_[unique[0] - 1e-12, (unique[:-1] + unique[1:]) / 2, unique[-1] + 1e-12]


def _fit_threshold(x: np.ndarray, y: np.ndarray) -> tuple[float, str]:
    best: tuple[tuple[float, float, float], float, str] | None = None
    for direction in ("ge", "le"):
        for threshold in _threshold_candidates(x):
            pred = (x >= threshold).astype(int) if direction == "ge" else (x <= threshold).astype(int)
            met = _classification_metrics(y, pred)
            key = (met["ba"], met["mcc"], float((pred == y).mean()))
            if best is None or key > best[0]:
                best = (key, float(threshold), direction)
    if best is None:
        raise ValueError("não há limiar ajustável")
    return best[1], best[2]


def dynamic_lofo(*, grouped: bool) -> dict[str, float]:
    frame = pd.read_csv(DYNAMIC)
    _assert_columns(frame, ["instance_key", "role", "early_frac", TURNOVER, LABEL], DYNAMIC)
    frame = frame.loc[
        (frame["role"] == "synthetic")
        & np.isclose(frame["early_frac"], EARLY_FRAC)
        & frame[LABEL].isin(["HELPS", "NOT_HELPS"])
    ].copy()
    if len(frame) != 51:
        raise ValueError(f"{DYNAMIC}: esperava 51 casos rotulados em early_frac={EARLY_FRAC}, encontrei {len(frame)}")
    frame["group"] = frame["instance_key"].map(_grouped_family if grouped else _family)
    x = frame[TURNOVER].to_numpy(dtype=float)
    y = (frame[LABEL] == "HELPS").to_numpy(dtype=int)
    if not np.isfinite(x).all():
        raise ValueError(f"{DYNAMIC}: {TURNOVER} não finito")

    prediction = np.empty(len(frame), dtype=int)
    for group in sorted(frame["group"].unique()):
        held = frame["group"].eq(group).to_numpy()
        threshold, direction = _fit_threshold(x[~held], y[~held])
        prediction[held] = (x[held] >= threshold).astype(int) if direction == "ge" else (x[held] <= threshold).astype(int)

    metrics = _classification_metrics(y, prediction)
    wfg_partition = frame["instance_key"].map(_family).ne("WFG").to_numpy(dtype=int)
    metrics["coincide"] = float((prediction == wfg_partition).sum())
    metrics["n"] = float(len(frame))
    metrics["groups"] = float(frame["group"].nunique())
    return metrics


def wfg_partition_posthoc() -> dict[str, float]:
    """Fixed suite rule scored on the same labelled sample; nothing is fitted."""
    frame = pd.read_csv(DYNAMIC)
    frame = frame.loc[
        (frame["role"] == "synthetic")
        & np.isclose(frame["early_frac"], EARLY_FRAC)
        & frame[LABEL].isin(["HELPS", "NOT_HELPS"])
    ]
    if len(frame) != 51:
        raise ValueError(f"{DYNAMIC}: esperava 51 casos rotulados em early_frac={EARLY_FRAC}, encontrei {len(frame)}")
    y = (frame[LABEL] == "HELPS").to_numpy(dtype=int)
    keep_on = frame["instance_key"].map(_family).ne("WFG").to_numpy(dtype=int)
    return _classification_metrics(y, keep_on)


def build() -> str:
    static = static_oof()
    suite = dynamic_lofo(grouped=False)
    duplicate_safe = dynamic_lofo(grouped=True)
    partition = wfg_partition_posthoc()
    paisagem: list[list[str] | object] = [
        ["Paisagem", "Floresta: $r_s$", "Deixa-uma-instância", fmt.decimal(static["loocv_r"]), "---"],
        ["", "Floresta: $r_s$", "Deixa-uma-família", fmt.decimal(static["lofo_r"]), "---"],
    ]
    paisagem[0][0] = lt.Multirow("Paisagem", len(paisagem))
    renovacao: list[list[str] | object] = [
        [
            "Renovação",
            "Limiar: BA",
            "LOFO por suíte",
            fmt.decimal(suite["ba"]),
            f"{int(suite['coincide'])}/{int(suite['n'])}",
        ],
        [
            "",
            "Limiar: BA",
            "LOFO DTLZ+MaF",
            fmt.decimal(duplicate_safe["ba"]),
            f"{int(duplicate_safe['coincide'])}/{int(duplicate_safe['n'])}",
        ],
        [
            "",
            "Limiar: MCC",
            "LOFO DTLZ+MaF",
            fmt.decimal(duplicate_safe["mcc"]),
            f"{int(duplicate_safe['coincide'])}/{int(duplicate_safe['n'])}",
        ],
    ]
    renovacao[0][0] = lt.Multirow("Renovação", len(renovacao))
    suíte: list[list[str] | object] = [
        ["Suíte", "Partição: BA", "Pós-hoc, sem ajuste", fmt.decimal(partition["ba"]), "---"],
        ["", "Partição: MCC", "Pós-hoc, sem ajuste", fmt.decimal(partition["mcc"]), "---"],
    ]
    suíte[0][0] = lt.Multirow("Suíte", len(suíte))
    rows: list[list[str] | object] = [
        *paisagem,
        lt.Rule,
        *renovacao,
        lt.Rule,
        *suíte,
    ]
    note = (
        "Reanálise descritiva sobre 51 instâncias. Para os descritores estáticos, a resposta é "
        "a diferença entre as medianas de IGD (SPEA2 menos IVF/SPEA2); em cada dobra, a "
        "transformação Yeo--Johnson é ajustada somente na resposta de treino e a predição é "
        "invertida para essa escala antes de calcular $r_s$ sobre todas as predições fora da "
        "amostra. Portanto, não se agregam postos calculados separadamente nas dobras. A "
        "validação deixa-uma-família agrupa DTLZ e MaF, mantendo MaF7 e DTLZ7 (M=2 e M=3) "
        "do mesmo lado retido. Para a regra dinâmica, o observável e a janela de 20\\% das "
        "gerações foram escolhidos na análise de origem e permanecem fixos nesta reanálise; "
        "em cada dobra, só o limiar e sua direção são ajustados nas famílias de treino. "
        "BA: acurácia balanceada; MCC: coeficiente de Matthews. A última coluna é a "
        "coincidência entre a decisão da regra e a partição WFG desligada/demais ligadas. "
        "As linhas da suíte aplicam essa partição, sem nenhum parâmetro ajustado, aos mesmos "
        "rótulos: ela foi formulada depois de se observar que a WFG concentra as instâncias "
        "não beneficiadas e, por isso, é uma referência retrospectiva, não um controlador "
        "validado nem uma regra avaliada fora da amostra. "
        "Os rótulos reutilizam a comparação em IGD da coorte da comparação principal, sem "
        "correção de "
        "multiplicidade. A tabela não valida a escolha do observável nem da janela fora da "
        "amostra, tampouco a execução do controlador."
    )
    return lt.render(
        header=["Evidência", "Medida", "Protocolo", "Valor", "Partição WFG"],
        rows=rows,
        colspec="llLcc",
        caption="Robustez descritiva da evidência de ativação sob retenção por família.",
        label="tab:ativacao_robustez",
        producer=__file__,
        sources=[STATIC, DYNAMIC],
        note=note,
    )


def main() -> int:
    try:
        lt.write(OUT, build())
    except (ValueError, KeyError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
