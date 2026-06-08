"""
Shared utilities for the proposed-figures pipeline.

Reuses and adapts code from:
    src/python/fla/test_dynamic_signal.py
    src/python/fla/generate_paper_figures.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
BLUE = "#1f77b4"
ORANGE = "#ff7f0e"
GRAY = "#7f7f7f"
DPI = 300

FAMILY_ORDER = ["ZDT", "DTLZ", "MaF", "WFG"]
FAMILY_MARKERS = {"ZDT": "o", "DTLZ": "s", "MaF": "D", "WFG": "^"}

# Controller thresholds from paper (LFO-CV calibration)
THRESHOLD_MAIN = 0.216        # ZDT, DTLZ, MaF
THRESHOLD_WFG = 0.248         # WFG-specific

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESULTS_TABLES = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR = PROJECT_ROOT / "paper" / "clei2026" / "figures"


def style_setup() -> None:
    matplotlib.use("Agg")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "axes.labelsize": 10,
            "axes.titlesize": 10,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 8,
            "figure.dpi": 100,
            "savefig.dpi": DPI,
            "savefig.bbox": "tight",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURES_DIR / f"{name}.pdf"
    png_path = FIGURES_DIR / f"{name}.png"
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=DPI, bbox_inches="tight")
    print(f"  Saved: {pdf_path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Family derivation
# ---------------------------------------------------------------------------
def family_of(case_id: str) -> str:
    c = str(case_id).lower()
    if c.startswith("zdt"):
        return "ZDT"
    if c.startswith("dtlz"):
        return "DTLZ"
    if c.startswith("wfg"):
        return "WFG"
    if c.startswith("maf"):
        return "MaF"
    return "Other"


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------
def compute_a12(x: np.ndarray, y: np.ndarray) -> float:
    """Vargha-Delaney A12 effect size (stochastic superiority of x over y).

    A12 > 0.5 means x tends to be larger than y.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    if len(x) == 0 or len(y) == 0:
        return np.nan
    u, _ = stats.mannwhitneyu(x, y, alternative="two-sided")
    return float(u / (len(x) * len(y)))


def a12_bootstrap(x: np.ndarray, y: np.ndarray, n_boot: int = 2000, seed: int = 42) -> tuple[float, float, float]:
    """Compute A12 with bootstrap 95% CI."""
    rng = np.random.default_rng(seed)
    a12 = compute_a12(x, y)
    boots = np.zeros(n_boot)
    x_arr, y_arr = np.asarray(x), np.asarray(y)
    for i in range(n_boot):
        bx = rng.choice(x_arr, size=len(x_arr), replace=True)
        by = rng.choice(y_arr, size=len(y_arr), replace=True)
        boots[i] = compute_a12(bx, by)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return a12, lo, hi


# ---------------------------------------------------------------------------
# Classification metrics
# ---------------------------------------------------------------------------
def classification_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    n_pos = tp + fn
    n_neg = tn + fp
    sensitivity = tp / n_pos if n_pos else np.nan
    specificity = tn / n_neg if n_neg else np.nan
    accuracy = (tp + tn) / len(y_true) if y_true else np.nan
    balanced_accuracy = float(np.nanmean([sensitivity, specificity]))
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    mcc = ((tp * tn) - (fp * fn)) / np.sqrt(denom) if denom > 0 else np.nan
    return {
        "tp": float(tp), "tn": float(tn), "fp": float(fp), "fn": float(fn),
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_accuracy),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "mcc": float(mcc),
    }


def threshold_candidates(values: np.ndarray) -> list[float]:
    unique = np.unique(np.asarray(values, dtype=float))
    if len(unique) == 0:
        return []
    if len(unique) == 1:
        return [float(unique[0])]
    mids = ((unique[:-1] + unique[1:]) / 2.0).tolist()
    return [float(unique[0] - 1e-12), *[float(v) for v in mids], float(unique[-1] + 1e-12)]


def predict_binary(values: np.ndarray, threshold: float, direction: str) -> np.ndarray:
    if direction == "ge":
        return (values >= threshold).astype(int)
    return (values <= threshold).astype(int)


def fit_best_threshold(
    train_df: pd.DataFrame, feature: str, label_col: str,
) -> dict[str, Any] | None:
    train = train_df[[feature, label_col]].dropna().copy()
    train = train.loc[train[label_col].isin(["HELPS", "NOT_HELPS"])].copy()
    if len(train) < 6:
        return None
    y = (train[label_col] == "HELPS").astype(int).to_numpy()
    if len(np.unique(y)) < 2:
        return None
    x = pd.to_numeric(train[feature], errors="coerce").to_numpy()
    best = None
    for direction in ("ge", "le"):
        for threshold in threshold_candidates(x):
            preds = predict_binary(x, threshold, direction)
            met = classification_metrics(y.tolist(), preds.tolist())
            key = (met["balanced_accuracy"], met["mcc"], met["accuracy"])
            if best is None or key > best["key"]:
                best = {
                    "feature": feature,
                    "direction": direction,
                    "threshold": float(threshold),
                    "key": key,
                    **met,
                }
    return best


# ---------------------------------------------------------------------------
# .mat trajectory loading
# ---------------------------------------------------------------------------
def load_mat_generations(mat_path: Path) -> list[dict]:
    """Load trace_generations from a .mat file."""
    from pymatreader import read_mat
    data = read_mat(str(mat_path))
    gens = data.get("trace_generations", [])
    if isinstance(gens, dict):
        gens = [gens]
    elif isinstance(gens, np.ndarray):
        gens = list(gens)
    return gens


def window_mean(generations: list[dict], key: str, start: int, end: int) -> float:
    """Mean of a field over a window of generations."""
    values: list[float] = []
    start = max(0, start)
    end = min(len(generations), end)
    for g in generations[start:end]:
        if not isinstance(g, dict) or key not in g:
            continue
        v = g[key]
        if isinstance(v, (int, float, np.integer, np.floating)) and np.isfinite(v):
            values.append(float(v))
    return float(np.mean(values)) if values else np.nan


def extract_run_id(mat_path: Path) -> int | None:
    match = re.search(r"_(\d+)\.mat$", mat_path.name)
    if not match:
        return None
    return int(match.group(1))


def aggregate_value(values: list[float], method: str = "median") -> float:
    arr = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy()
    if len(arr) == 0:
        return np.nan
    if method == "mean":
        return float(np.mean(arr))
    return float(np.median(arr))


# ---------------------------------------------------------------------------
# File pairing
# ---------------------------------------------------------------------------
def collect_paired_files(ivf_dir: Path, spea2_dir: Path) -> list[tuple[int, Path, Path]]:
    ivf_map = {}
    for path in ivf_dir.glob("IVF_*.mat"):
        run_id = extract_run_id(path)
        if run_id is not None:
            ivf_map[run_id] = path
    spea2_map = {}
    for path in spea2_dir.glob("SPEA2_*.mat"):
        run_id = extract_run_id(path)
        if run_id is not None:
            spea2_map[run_id] = path
    paired = []
    for run_id in sorted(ivf_map.keys() & spea2_map.keys()):
        paired.append((run_id, ivf_map[run_id], spea2_map[run_id]))
    return paired


def select_pairs_for_analysis(
    paired_files: list[tuple[int, Path, Path]], max_runs: int,
) -> list[tuple[int, Path, Path]]:
    if max_runs <= 0 or len(paired_files) <= max_runs:
        return paired_files
    return sorted(paired_files, key=lambda item: item[0])[-max_runs:]


# ---------------------------------------------------------------------------
# Per-run feature extraction
# ---------------------------------------------------------------------------
def extract_run_features(
    ivf_gens: list[dict], spea2_gens: list[dict], early_frac: float,
) -> dict[str, float] | None:
    n_gen = min(len(ivf_gens), len(spea2_gens))
    if n_gen < 10:
        return None
    early_end = max(int(round(n_gen * early_frac)), 5)
    early_end = min(early_end, n_gen)
    ivf_turnover_early = window_mean(ivf_gens, "turnover", 1, early_end)
    spea2_turnover_early = window_mean(spea2_gens, "turnover", 1, early_end)
    return {
        "n_gen": float(n_gen),
        "early_frac": float(early_frac),
        "ivf_turnover_early": ivf_turnover_early,
        "spea2_turnover_early": spea2_turnover_early,
        "turnover_delta": ivf_turnover_early - spea2_turnover_early,
    }


# ---------------------------------------------------------------------------
# FLA label helpers
# ---------------------------------------------------------------------------
def normalize_instance_name(value: str) -> str:
    return str(value).strip().upper()


def build_response_map(response_df: pd.DataFrame) -> dict[str, dict]:
    response_map: dict[str, dict] = {}
    for _, row in response_df.iterrows():
        key = normalize_instance_name(row["instance"])
        response_map[key] = {
            "response_label": str(row.get("label_binary", row.get("label", ""))),
            "response_a12": float(row.get("a12", np.nan)),
            "response_wilcoxon_p": float(row.get("wilcoxon_p", np.nan)),
            "response_delta_igd": float(row.get("delta_igd", np.nan)),
            "response_delta_pct": float(row.get("delta_pct", np.nan)),
            "response_n_runs_ivf": int(row.get("n_runs_ivf", 0)),
            "response_n_runs_spea2": int(row.get("n_runs_spea2", 0)),
        }
    return response_map


# ---------------------------------------------------------------------------
# Leave-one-family-out CV for threshold rules
# ---------------------------------------------------------------------------
def lofo_threshold_eval(
    df: pd.DataFrame, feature: str, label_col: str,
) -> dict[str, Any]:
    df = df.copy()
    df["family"] = df["case_id"].apply(family_of)
    df = df[df[label_col].isin(["HELPS", "NOT_HELPS"])].copy()
    df = df.reset_index(drop=True)
    families = sorted(set(df["family"]))
    all_preds = np.full(len(df), -1, dtype=int)
    thresholds = {}

    for fam in families:
        test = df["family"] == fam
        train = df[~test]
        if len(train) < 6 or test.sum() < 1:
            continue
        best = fit_best_threshold(train, feature, label_col)
        if best is None:
            continue
        thresholds[fam] = best["threshold"]
        for pos in range(len(df)):
            if not test.iloc[pos]:
                continue
            val = pd.to_numeric(df.iloc[pos][feature], errors="coerce")
            if np.isfinite(val):
                all_preds[pos] = int(
                    val >= best["threshold"] if best["direction"] == "ge"
                    else val <= best["threshold"]
                )

    y_true = (df[label_col] == "HELPS").astype(int).to_numpy()
    valid = all_preds >= 0
    if valid.sum() == 0:
        return {"balanced_accuracy": np.nan, "mcc": np.nan, "thresholds": {}}
    met = classification_metrics(y_true[valid].tolist(), all_preds[valid].tolist())
    met["thresholds"] = thresholds
    return met
