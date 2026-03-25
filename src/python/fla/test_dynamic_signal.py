"""
Dynamic signal analysis for the PPSN 2026 paper.

This script builds a case-level summary from paired IVF-SPEA2/SPEA2 traces,
tests early-dynamics features with BH-FDR correction, and runs lightweight
sensitivity checks over early-window fractions and HELP cutoffs.

Outputs:
  - data/processed/dynamic_signal_test.csv
  - data/processed/dynamic_signal_sensitivity.csv
  - results/tables/dynamic_signal_main_tests.csv
  - results/tables/dynamic_signal_loocv.csv
  - results/tables/dynamic_signal_integrity.csv
  - results/tables/dynamic_signal_integrity.md
  - results/tables/dynamic_signal_report.md
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESULTS_TABLES = PROJECT_ROOT / "results" / "tables"

DEFAULT_CASES_CSV = PROJECT_ROOT / "config" / "ppsn_dynamics_cases_full.csv"
RESPONSE_CSV = PROJECT_ROOT / "data" / "processed" / "fla_response.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics"

MAIN_EARLY_FRAC = 0.20
MAIN_HELP_CUTOFF = 0.56
LABEL_ALPHA = 0.05
DEFAULT_MAX_RUNS = 30
DEFAULT_MIN_RUNS = 3
DEFAULT_AGGREGATE = "median"
DEFAULT_EARLY_FRACS = [0.10, 0.20, 0.30]
DEFAULT_HELP_CUTOFFS = [0.54, 0.56, 0.58]

FEATURE_COLUMNS = [
    "ivf_turnover_early",
    "spea2_turnover_early",
    "turnover_delta",
    "turnover_ratio",
    "ivf_nd_early",
    "spea2_nd_early",
    "nd_delta",
    "ivf_fitness_early",
    "spea2_fitness_early",
    "fitness_delta",
    "ivf_spacing_early",
    "spea2_spacing_early",
    "spacing_ratio",
    "ivf_cycles_early",
    "igd_early_delta",
    "igd_final_delta",
    "hv_early_delta",
    "hv_final_delta",
]

EARLY_FEATURE_COLUMNS = [
    "ivf_turnover_early",
    "spea2_turnover_early",
    "turnover_delta",
    "turnover_ratio",
    "ivf_nd_early",
    "spea2_nd_early",
    "nd_delta",
    "ivf_fitness_early",
    "spea2_fitness_early",
    "fitness_delta",
    "ivf_spacing_early",
    "spea2_spacing_early",
    "spacing_ratio",
    "ivf_cycles_early",
    "igd_early_delta",
    "hv_early_delta",
]

METADATA_COLUMNS = {
    "case_id",
    "instance_key",
    "problem",
    "m",
    "d",
    "role",
    "label_binary",
    "response_label",
    "response_a12",
    "response_wilcoxon_p",
    "response_delta_igd",
    "response_delta_pct",
    "response_n_runs_ivf",
    "response_n_runs_spea2",
    "early_frac",
    "help_cutoff",
    "label_alpha",
    "aggregate_stat",
    "n_runs_available",
    "n_runs_used",
}


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    value = int(raw)
    if value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return float(raw)


def env_float_list(name: str, default: list[float]) -> list[float]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    values = [float(part.strip()) for part in raw.split(",") if part.strip()]
    if not values:
        raise ValueError(f"{name} did not contain any numeric values")
    return values


def env_path(name: str, default: Path) -> Path:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def normalize_instance_name(value: str) -> str:
    return str(value).strip().upper()


def instance_key_from_case(problem: str, m: int) -> str:
    return f"{str(problem).strip().upper()}_M{int(m)}"


def extract_run_id(mat_path: Path) -> int | None:
    match = re.search(r"_(\d+)\.mat$", mat_path.name)
    if not match:
        return None
    return int(match.group(1))


def load_mat_generations(mat_path: Path) -> list[dict]:
    from pymatreader import read_mat

    data = read_mat(str(mat_path))
    gens = data.get("trace_generations", [])
    if isinstance(gens, dict):
        gens = [gens]
    elif isinstance(gens, np.ndarray):
        gens = list(gens)
    return gens


def window_mean(generations: list[dict], key: str, start: int, end: int) -> float:
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


def window_values(generations: list[dict], key: str, start: int, end: int) -> list[float]:
    values: list[float] = []
    start = max(0, start)
    end = min(len(generations), end)
    for g in generations[start:end]:
        if not isinstance(g, dict) or key not in g:
            continue
        v = g[key]
        if isinstance(v, (int, float, np.integer, np.floating)) and np.isfinite(v):
            values.append(float(v))
    return values


def bh_fdr_adjust(p_values: list[float]) -> np.ndarray:
    if not p_values:
        return np.array([])
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ordered = p[order]
    m = float(len(p))
    adjusted = np.empty_like(ordered)
    running = 1.0
    for i in range(len(ordered) - 1, -1, -1):
        rank = i + 1
        current = min(1.0, (ordered[i] * m) / rank)
        running = min(running, current)
        adjusted[i] = running
    result = np.empty_like(adjusted)
    result[order] = adjusted
    return result


def aggregate_value(values: list[float], method: str) -> float:
    arr = pd.to_numeric(pd.Series(values), errors="coerce").dropna().to_numpy()
    if len(arr) == 0:
        return np.nan
    if method == "mean":
        return float(np.mean(arr))
    return float(np.median(arr))


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
    paired_files: list[tuple[int, Path, Path]],
    max_runs: int,
) -> list[tuple[int, Path, Path]]:
    """Keep the most recent paired run IDs when multiple campaigns coexist.

    Some cases have legacy/smoke-test traces in the same directory. The final
    submission batch uses larger run IDs, so taking the highest max_runs IDs
    preserves the latest 30-run campaign instead of mixing campaigns.
    """
    if max_runs <= 0 or len(paired_files) <= max_runs:
        return paired_files
    return sorted(paired_files, key=lambda item: item[0])[-max_runs:]


def extract_run_features(ivf_gens: list[dict], spea2_gens: list[dict], early_frac: float) -> dict | None:
    n_gen = min(len(ivf_gens), len(spea2_gens))
    if n_gen < 10:
        return None

    early_end = max(int(round(n_gen * early_frac)), 5)
    early_end = min(early_end, n_gen)
    final_window = max(3, int(round(n_gen * 0.10)))
    final_start = max(n_gen - final_window, 0)

    ivf_turnover_early = window_mean(ivf_gens, "turnover", 1, early_end)
    spea2_turnover_early = window_mean(spea2_gens, "turnover", 1, early_end)
    ivf_nd_early = window_mean(ivf_gens, "nd_fraction", 1, early_end)
    spea2_nd_early = window_mean(spea2_gens, "nd_fraction", 1, early_end)
    ivf_fitness_early = window_mean(ivf_gens, "mean_fitness", 1, early_end)
    spea2_fitness_early = window_mean(spea2_gens, "mean_fitness", 1, early_end)
    ivf_spacing_early = window_mean(ivf_gens, "spacing", 1, early_end)
    spea2_spacing_early = window_mean(spea2_gens, "spacing", 1, early_end)
    ivf_cycles_early = window_mean(ivf_gens, "n_ivf_cycles", 1, early_end)

    ivf_igd_early = window_mean(ivf_gens, "igd", 1, early_end)
    spea2_igd_early = window_mean(spea2_gens, "igd", 1, early_end)
    ivf_hv_early = window_mean(ivf_gens, "hv", 1, early_end)
    spea2_hv_early = window_mean(spea2_gens, "hv", 1, early_end)
    ivf_igd_final = window_mean(ivf_gens, "igd", final_start, n_gen)
    spea2_igd_final = window_mean(spea2_gens, "igd", final_start, n_gen)
    ivf_hv_final = window_mean(ivf_gens, "hv", final_start, n_gen)
    spea2_hv_final = window_mean(spea2_gens, "hv", final_start, n_gen)

    turnover_delta = ivf_turnover_early - spea2_turnover_early
    turnover_ratio = ivf_turnover_early / spea2_turnover_early if spea2_turnover_early > 0 else np.nan
    nd_delta = ivf_nd_early - spea2_nd_early
    fitness_delta = spea2_fitness_early - ivf_fitness_early
    spacing_ratio = ivf_spacing_early / spea2_spacing_early if spea2_spacing_early > 0 else np.nan
    igd_early_delta = spea2_igd_early - ivf_igd_early
    igd_final_delta = spea2_igd_final - ivf_igd_final
    hv_early_delta = ivf_hv_early - spea2_hv_early
    hv_final_delta = ivf_hv_final - spea2_hv_final

    return {
        "n_gen": n_gen,
        "early_frac": float(early_frac),
        "ivf_turnover_early": ivf_turnover_early,
        "spea2_turnover_early": spea2_turnover_early,
        "turnover_delta": turnover_delta,
        "turnover_ratio": turnover_ratio,
        "ivf_nd_early": ivf_nd_early,
        "spea2_nd_early": spea2_nd_early,
        "nd_delta": nd_delta,
        "ivf_fitness_early": ivf_fitness_early,
        "spea2_fitness_early": spea2_fitness_early,
        "fitness_delta": fitness_delta,
        "ivf_spacing_early": ivf_spacing_early,
        "spea2_spacing_early": spea2_spacing_early,
        "spacing_ratio": spacing_ratio,
        "ivf_cycles_early": ivf_cycles_early,
        "igd_early_delta": igd_early_delta,
        "igd_final_delta": igd_final_delta,
        "hv_early_delta": hv_early_delta,
        "hv_final_delta": hv_final_delta,
    }


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


def derive_eval_label(response_row: dict, help_cutoff: float, alpha: float) -> str | None:
    if not response_row:
        return None
    if np.isnan(response_row.get("response_a12", np.nan)) or np.isnan(response_row.get("response_wilcoxon_p", np.nan)):
        return None
    if response_row["response_wilcoxon_p"] < alpha and response_row["response_a12"] >= help_cutoff:
        return "HELPS"
    return "NOT_HELPS"


def summarise_case(
    case_row: pd.Series,
    paired_files: list[tuple[int, Path, Path]],
    response_map: dict[str, dict],
    early_fracs: list[float],
    max_runs: int,
    agg_method: str,
) -> list[dict]:
    case_id = str(case_row["case_id"])
    problem = str(case_row["problem"])
    m = int(case_row["m"])
    d = int(case_row["d"])
    role = str(case_row["role"]) if "role" in case_row and pd.notna(case_row["role"]) else "full_suite"
    label_binary_manifest = (
        str(case_row["label_binary"])
        if "label_binary" in case_row and pd.notna(case_row["label_binary"])
        else ""
    )

    key = instance_key_from_case(problem, m)
    response_row = response_map.get(normalize_instance_name(key), {})

    selected_pairs = select_pairs_for_analysis(paired_files, max_runs)
    records_by_frac = {frac: [] for frac in early_fracs}

    for run_id, ivf_path, spea2_path in selected_pairs:
        try:
            ivf_gens = load_mat_generations(ivf_path)
            spea2_gens = load_mat_generations(spea2_path)
        except Exception as exc:
            print(f"  [WARN] {case_id} run {run_id}: {exc}")
            continue

        for frac in early_fracs:
            feats = extract_run_features(ivf_gens, spea2_gens, frac)
            if feats is not None:
                feats["run_id"] = run_id
                feats["case_id"] = case_id
                feats["early_frac"] = float(frac)
                records_by_frac[frac].append(feats)

    summary_rows = []
    for frac, records in records_by_frac.items():
        if len(records) < DEFAULT_MIN_RUNS:
            continue

        row = {
            "case_id": case_id,
            "instance_key": key,
            "problem": problem,
            "m": m,
            "d": d,
            "role": role,
            "label_binary": label_binary_manifest,
            "response_label": response_row.get("response_label", ""),
            "response_a12": response_row.get("response_a12", np.nan),
            "response_wilcoxon_p": response_row.get("response_wilcoxon_p", np.nan),
            "response_delta_igd": response_row.get("response_delta_igd", np.nan),
            "response_delta_pct": response_row.get("response_delta_pct", np.nan),
            "response_n_runs_ivf": response_row.get("response_n_runs_ivf", 0),
            "response_n_runs_spea2": response_row.get("response_n_runs_spea2", 0),
            "early_frac": float(frac),
            "help_cutoff": np.nan,
            "label_alpha": np.nan,
            "aggregate_stat": agg_method,
            "n_runs_available": len(paired_files),
            "n_runs_used": len(records),
            "n_runs_selected": len(selected_pairs),
        }
        for col in FEATURE_COLUMNS:
            row[col] = aggregate_value([r[col] for r in records], agg_method)

        summary_rows.append(row)

    return summary_rows


def run_feature_family_tests(
    summary_df: pd.DataFrame,
    label_col: str,
    feature_columns: list[str],
    help_cutoff: float,
    label_alpha: float,
) -> pd.DataFrame:
    rows = []
    labeled = summary_df.loc[summary_df[label_col].isin(["HELPS", "NOT_HELPS"])].copy()
    helps_df = labeled.loc[labeled[label_col] == "HELPS"].copy()
    not_df = labeled.loc[labeled[label_col] == "NOT_HELPS"].copy()

    for feature in feature_columns:
        helps = pd.to_numeric(helps_df[feature], errors="coerce").dropna()
        not_helps = pd.to_numeric(not_df[feature], errors="coerce").dropna()
        if len(helps) < 3 or len(not_helps) < 3:
            continue

        stat, p_value = stats.mannwhitneyu(helps, not_helps, alternative="two-sided")
        a12 = stat / (len(helps) * len(not_helps))

        rows.append({
            "early_frac": float(summary_df["early_frac"].iloc[0]),
            "help_cutoff": float(help_cutoff),
            "label_alpha": float(label_alpha),
            "feature": feature,
            "n_labeled_cases": int(len(labeled)),
            "n_helps": int(len(helps)),
            "n_not_helps": int(len(not_helps)),
            "helps_median": float(np.median(helps)),
            "not_helps_median": float(np.median(not_helps)),
            "u_stat": float(stat),
            "p_value": float(p_value),
            "a12": float(a12),
        })

    if not rows:
        return pd.DataFrame()

    result = pd.DataFrame(rows)
    result["p_bh"] = bh_fdr_adjust(result["p_value"].tolist())
    result["significant_bh"] = result["p_bh"] < 0.05
    result["signal"] = np.where(
        result["p_bh"] < 0.05,
        "BH-SIG",
        np.where(result["p_value"] < 0.05, "RAW-SIG", np.where(result["p_value"] < 0.10, "WEAK", "")),
    )
    return result


def build_main_label_column(summary_df: pd.DataFrame, response_map: dict[str, dict], help_cutoff: float) -> pd.DataFrame:
    labels = []
    label_available = []
    for _, row in summary_df.iterrows():
        response_row = response_map.get(normalize_instance_name(row["instance_key"]), {})
        label = derive_eval_label(response_row, help_cutoff, LABEL_ALPHA)
        labels.append(label)
        label_available.append(label is not None)
    out = summary_df.copy()
    out["label_binary_eval"] = labels
    out["label_binary_eval_available"] = label_available
    return out


def audit_case_inventory(
    cases: pd.DataFrame,
    response_map: dict[str, dict],
    max_runs: int,
) -> pd.DataFrame:
    ivf_root = RAW_DIR / "ivf"
    spea2_root = RAW_DIR / "spea2"
    rows = []
    for _, case_row in cases.iterrows():
        case_id = str(case_row["case_id"])
        problem = str(case_row["problem"])
        m = int(case_row["m"])
        role = str(case_row["role"]) if "role" in case_row and pd.notna(case_row["role"]) else "full_suite"
        instance_key = instance_key_from_case(problem, m)
        response_row = response_map.get(normalize_instance_name(instance_key), {})

        ivf_dir = ivf_root / case_id
        spea2_dir = spea2_root / case_id
        paired_files = collect_paired_files(ivf_dir, spea2_dir) if ivf_dir.exists() and spea2_dir.exists() else []
        selected_pairs = select_pairs_for_analysis(paired_files, max_runs)
        ivf_files = len(list(ivf_dir.glob("IVF_*.mat"))) if ivf_dir.exists() else 0
        spea2_files = len(list(spea2_dir.glob("SPEA2_*.mat"))) if spea2_dir.exists() else 0
        label_eval = derive_eval_label(response_row, MAIN_HELP_CUTOFF, LABEL_ALPHA)

        rows.append(
            {
                "case_id": case_id,
                "instance_key": instance_key,
                "problem": problem,
                "m": m,
                "role": role,
                "n_ivf_files": ivf_files,
                "n_spea2_files": spea2_files,
                "n_paired_files_raw": len(paired_files),
                "n_selected_pairs": len(selected_pairs),
                "extra_paired_runs": max(0, len(paired_files) - len(selected_pairs)),
                "selected_run_id_min": int(selected_pairs[0][0]) if selected_pairs else np.nan,
                "selected_run_id_max": int(selected_pairs[-1][0]) if selected_pairs else np.nan,
                "response_available": bool(response_row),
                "label_binary_eval": label_eval,
            }
        )
    return pd.DataFrame(rows)


def write_integrity_artifacts(integrity_df: pd.DataFrame, cases_csv: Path, max_runs: int) -> None:
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    integrity_csv = RESULTS_TABLES / "dynamic_signal_integrity.csv"
    integrity_md = RESULTS_TABLES / "dynamic_signal_integrity.md"

    integrity_df = integrity_df.sort_values(["extra_paired_runs", "case_id"], ascending=[False, True]).reset_index(drop=True)
    integrity_df.to_csv(integrity_csv, index=False)

    unlabeled = integrity_df.loc[~integrity_df["response_available"], "case_id"].tolist()
    extras = integrity_df.loc[integrity_df["extra_paired_runs"] > 0, ["case_id", "n_paired_files_raw", "n_selected_pairs"]]
    lines = [
        "# Dynamic Signal Integrity Audit",
        "",
        f"- Manifest: {cases_csv}",
        f"- Cases in manifest: {len(integrity_df)}",
        f"- Cases with >= {max_runs} selected paired runs: {int((integrity_df['n_selected_pairs'] >= max_runs).sum())}",
        f"- Unlabeled cases excluded from label-based tests: {len(unlabeled)}",
        f"- Pair selection policy: keep the highest {max_runs} paired run IDs when more than {max_runs} exist",
    ]
    if unlabeled:
        lines.append(f"- Unlabeled case IDs: {', '.join(unlabeled)}")
    if not extras.empty:
        lines.append("")
        lines.append("## Cases With Extra Paired Runs")
        for _, row in extras.iterrows():
            lines.append(
                f"- {row['case_id']}: raw={int(row['n_paired_files_raw'])}, selected={int(row['n_selected_pairs'])}"
            )

    integrity_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved integrity table: {integrity_csv}")
    print(f"Saved integrity report: {integrity_md}")


def confusion_counts(y_true: list[int], y_pred: list[int]) -> tuple[int, int, int, int]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return tp, tn, fp, fn


def classification_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float]:
    tp, tn, fp, fn = confusion_counts(y_true, y_pred)
    n_pos = tp + fn
    n_neg = tn + fp
    sensitivity = tp / n_pos if n_pos else np.nan
    specificity = tn / n_neg if n_neg else np.nan
    accuracy = (tp + tn) / len(y_true) if y_true else np.nan
    balanced_accuracy = np.nanmean([sensitivity, specificity])
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    mcc = ((tp * tn) - (fp * fn)) / np.sqrt(denom) if denom > 0 else np.nan
    return {
        "tp": float(tp),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
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


def fit_best_threshold(train_df: pd.DataFrame, feature: str, label_col: str) -> dict | None:
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
            metrics = classification_metrics(y.tolist(), preds.tolist())
            key = (
                metrics["balanced_accuracy"],
                -999.0 if np.isnan(metrics["mcc"]) else metrics["mcc"],
                metrics["accuracy"],
            )
            if best is None or key > best["key"]:
                best = {
                    "feature": feature,
                    "direction": direction,
                    "threshold": float(threshold),
                    "key": key,
                    "train_metrics": metrics,
                }
    return best


def run_loocv_threshold_tests(summary_df: pd.DataFrame, label_col: str, feature_columns: list[str]) -> pd.DataFrame:
    labeled = summary_df.loc[summary_df[label_col].isin(["HELPS", "NOT_HELPS"])].copy()
    rows = []

    for feature in feature_columns:
        y_true: list[int] = []
        y_pred: list[int] = []
        thresholds: list[float] = []
        directions: list[str] = []

        for holdout_idx in labeled.index:
            holdout = labeled.loc[[holdout_idx]].copy()
            train = labeled.drop(index=holdout_idx)
            if holdout[feature].isna().all():
                continue
            rule = fit_best_threshold(train, feature, label_col)
            if rule is None:
                continue

            x_hold = float(pd.to_numeric(holdout[feature], errors="coerce").iloc[0])
            pred = int(predict_binary(np.array([x_hold]), rule["threshold"], rule["direction"])[0])
            true = int(holdout[label_col].iloc[0] == "HELPS")

            y_true.append(true)
            y_pred.append(pred)
            thresholds.append(rule["threshold"])
            directions.append(rule["direction"])

        if not y_true:
            continue

        metrics = classification_metrics(y_true, y_pred)
        direction_mode = Counter(directions).most_common(1)[0][0] if directions else ""
        rows.append(
            {
                "feature": feature,
                "n_eval": len(y_true),
                "direction_mode": direction_mode,
                "median_threshold": float(np.median(thresholds)) if thresholds else np.nan,
                **metrics,
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(
        ["balanced_accuracy", "mcc", "accuracy", "feature"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def write_markdown_report(
    main_tests: pd.DataFrame,
    sensitivity: pd.DataFrame,
    loocv_df: pd.DataFrame,
    integrity_df: pd.DataFrame,
    cases_csv: Path,
) -> None:
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_TABLES / "dynamic_signal_report.md"

    turnover = main_tests.loc[main_tests["feature"] == "ivf_turnover_early"]
    hv_final = main_tests.loc[main_tests["feature"] == "hv_final_delta"]
    igd_final = main_tests.loc[main_tests["feature"] == "igd_final_delta"]

    lines = [
        "# Dynamic Signal Report",
        "",
        f"- Manifest: {cases_csv}",
        f"- Main setting: early_frac={MAIN_EARLY_FRAC:.2f}, help_cutoff={MAIN_HELP_CUTOFF:.2f}, alpha={LABEL_ALPHA:.2f}",
        f"- Cases in manifest: {len(integrity_df)}",
        f"- Labeled cases used in confirmatory tests: {int(integrity_df['response_available'].sum())}",
        f"- Features tested in the main family: {len(main_tests)}",
    ]

    if not turnover.empty:
        r = turnover.iloc[0]
        lines.append(
            f"- Turnover discriminant: p_raw={r['p_value']:.4f}, p_bh={r['p_bh']:.4f}, a12={r['a12']:.3f}"
        )
    if not hv_final.empty:
        r = hv_final.iloc[0]
        lines.append(
            f"- HV robustness: p_raw={r['p_value']:.4f}, p_bh={r['p_bh']:.4f}, a12={r['a12']:.3f}"
        )
    if not igd_final.empty:
        r = igd_final.iloc[0]
        lines.append(
            f"- IGD robustness: p_raw={r['p_value']:.4f}, p_bh={r['p_bh']:.4f}, a12={r['a12']:.3f}"
        )
    unlabeled = integrity_df.loc[~integrity_df["response_available"], "case_id"].tolist()
    if unlabeled:
        lines.append(f"- Unlabeled cases excluded from label-based tests: {', '.join(unlabeled)}")

    if not loocv_df.empty:
        best = loocv_df.iloc[0]
        lines.append("")
        lines.append("## LOOCV")
        lines.append(
            f"- Best early-feature threshold rule: {best['feature']} | balanced_accuracy={best['balanced_accuracy']:.3f}, "
            f"mcc={best['mcc']:.3f}, accuracy={best['accuracy']:.3f}, n_eval={int(best['n_eval'])}"
        )

    if not sensitivity.empty:
        best = sensitivity.sort_values(["p_bh", "p_value"]).iloc[0]
        lines.append("")
        lines.append("## Sensitivity")
        lines.append(
            f"- Best combo: early_frac={best['early_frac']:.2f}, help_cutoff={best['help_cutoff']:.2f}, "
            f"feature={best['feature']}, p_bh={best['p_bh']:.4f}"
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved report: {report_path}")


def main() -> None:
    print("=" * 70)
    print("DYNAMIC SIGNAL TEST -- early dynamics, BH-FDR, and sensitivity")
    print("=" * 70)

    cases_csv = env_path("DYN_CASES_CSV", DEFAULT_CASES_CSV)
    if not cases_csv.exists():
        print(f"ERROR: cases file not found: {cases_csv}")
        sys.exit(1)
    if not RESPONSE_CSV.exists():
        print(f"ERROR: response file not found: {RESPONSE_CSV}")
        sys.exit(1)

    cases = pd.read_csv(cases_csv)
    response_df = pd.read_csv(RESPONSE_CSV)
    response_map = build_response_map(response_df)

    max_runs = env_int("DYN_MAX_RUNS_PER_CASE", DEFAULT_MAX_RUNS)
    agg_method = os.getenv("DYN_AGG", DEFAULT_AGGREGATE).strip().lower()
    if agg_method not in {"mean", "median"}:
        raise ValueError("DYN_AGG must be 'mean' or 'median'")
    early_fracs = env_float_list("DYN_EARLY_FRACS", DEFAULT_EARLY_FRACS)
    help_cutoffs = env_float_list("DYN_HELP_CUTOFFS", DEFAULT_HELP_CUTOFFS)

    print(f"Manifest: {cases_csv}")
    print(f"Cases: {len(cases)}")
    print(f"Max runs/case: {max_runs}")
    print(f"Aggregation: {agg_method}")
    print(f"Early fractions: {early_fracs}")
    print(f"Help cutoffs: {help_cutoffs}")

    ivf_root = RAW_DIR / "ivf"
    spea2_root = RAW_DIR / "spea2"

    integrity_df = audit_case_inventory(cases, response_map, max_runs)
    write_integrity_artifacts(integrity_df, cases_csv, max_runs)
    complete_cases = int((integrity_df["n_selected_pairs"] >= max_runs).sum())
    labeled_cases = int(integrity_df["response_available"].sum())
    print(f"Integrity: {complete_cases}/{len(integrity_df)} cases have >= {max_runs} selected paired runs")
    print(f"Labeled for confirmatory tests: {labeled_cases}/{len(integrity_df)} cases")

    all_rows = []
    for _, case_row in cases.iterrows():
        case_id = str(case_row["case_id"])
        ivf_dir = ivf_root / case_id
        spea2_dir = spea2_root / case_id
        if not ivf_dir.exists() or not spea2_dir.exists():
            print(f"  SKIP {case_id}: missing directories")
            continue

        paired_files = collect_paired_files(ivf_dir, spea2_dir)
        if not paired_files:
            print(f"  SKIP {case_id}: no paired traces")
            continue

        rows = summarise_case(case_row, paired_files, response_map, early_fracs, max_runs, agg_method)
        if not rows:
            print(f"  SKIP {case_id}: insufficient valid runs")
            continue

        print(f"  {case_id}: {len(rows)} summaries from {min(max_runs, len(paired_files))} paired runs")
        all_rows.extend(rows)

    if not all_rows:
        print("ERROR: no case-level summaries were produced")
        sys.exit(1)

    summary_df = pd.DataFrame(all_rows)
    summary_df = summary_df.sort_values(["early_frac", "case_id"]).reset_index(drop=True)
    summary_df = build_main_label_column(summary_df, response_map, MAIN_HELP_CUTOFF)

    # Preserve the historical filename used by the figure code.
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    main_out = DATA_PROCESSED / "dynamic_signal_test.csv"
    summary_df.to_csv(main_out, index=False)
    print(f"Saved case summary: {main_out}")

    # Build the main tests on the reference cutoff and fraction.
    main_summary = summary_df.loc[summary_df["early_frac"].round(6) == round(MAIN_EARLY_FRAC, 6)].copy()
    if main_summary.empty:
        print(f"ERROR: main early_frac={MAIN_EARLY_FRAC:.2f} not present in summary output")
        sys.exit(1)

    main_summary["label_eval"] = main_summary["label_binary_eval"]
    main_tests = run_feature_family_tests(
        main_summary,
        "label_eval",
        FEATURE_COLUMNS,
        MAIN_HELP_CUTOFF,
        LABEL_ALPHA,
    )

    loocv_df = run_loocv_threshold_tests(main_summary, "label_eval", EARLY_FEATURE_COLUMNS)
    if not loocv_df.empty:
        loocv_out = RESULTS_TABLES / "dynamic_signal_loocv.csv"
        RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
        loocv_df.to_csv(loocv_out, index=False)
        print(f"Saved LOOCV table: {loocv_out}")

    # Sensitivity over early fractions and HELP cutoffs.
    sensitivity_rows = []
    for frac in early_fracs:
        frac_summary = summary_df.loc[summary_df["early_frac"].round(6) == round(frac, 6)].copy()
        if frac_summary.empty:
            continue
        for cutoff in help_cutoffs:
            frac_summary["label_eval"] = [
                derive_eval_label(response_map.get(normalize_instance_name(key), {}), cutoff, LABEL_ALPHA)
                for key in frac_summary["instance_key"]
            ]
            tests = run_feature_family_tests(
                frac_summary,
                "label_eval",
                FEATURE_COLUMNS,
                cutoff,
                LABEL_ALPHA,
            )
            if tests.empty:
                continue
            sensitivity_rows.append(tests)

    sensitivity_df = pd.concat(sensitivity_rows, ignore_index=True) if sensitivity_rows else pd.DataFrame()

    if not main_tests.empty:
        main_tests = main_tests.sort_values(["p_bh", "p_value", "feature"]).reset_index(drop=True)
        main_tests_out = RESULTS_TABLES / "dynamic_signal_main_tests.csv"
        RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
        main_tests.to_csv(main_tests_out, index=False)
        print(f"Saved main tests: {main_tests_out}")

        print("\n" + "=" * 70)
        print("MAIN FEATURE FAMILY (BH-FDR corrected)")
        print("=" * 70)
        print(f"{'Feature':<22} {'nH':>4} {'nN':>4} {'p_raw':>10} {'p_bh':>10} {'A12':>6} {'Signal':>8}")
        print("-" * 70)
        for _, row in main_tests.iterrows():
            print(
                f"{row['feature']:<22} {int(row['n_helps']):>4d} {int(row['n_not_helps']):>4d} "
                f"{row['p_value']:>10.4f} {row['p_bh']:>10.4f} {row['a12']:>6.3f} {row['signal']:>8}"
            )

        turnover_row = main_tests.loc[main_tests["feature"] == "ivf_turnover_early"]
        hv_row = main_tests.loc[main_tests["feature"] == "hv_final_delta"]
        if not turnover_row.empty:
            r = turnover_row.iloc[0]
            print(
                f"\nTurnover signal: p_raw={r['p_value']:.4f}, p_bh={r['p_bh']:.4f}, "
                f"a12={r['a12']:.3f}, HELPS median={r['helps_median']:.4f}, NOT_HELPS median={r['not_helps_median']:.4f}"
            )
        if not hv_row.empty:
            r = hv_row.iloc[0]
            print(
                f"HV robustness: p_raw={r['p_value']:.4f}, p_bh={r['p_bh']:.4f}, "
                f"a12={r['a12']:.3f}, HELPS median={r['helps_median']:.4f}, NOT_HELPS median={r['not_helps_median']:.4f}"
            )

    if not sensitivity_df.empty:
        sensitivity_out = RESULTS_TABLES / "dynamic_signal_sensitivity.csv"
        sensitivity_df = sensitivity_df.sort_values(["early_frac", "help_cutoff", "p_bh", "p_value", "feature"]).reset_index(drop=True)
        sensitivity_df.to_csv(sensitivity_out, index=False)
        print(f"Saved sensitivity table: {sensitivity_out}")

    write_markdown_report(main_tests, sensitivity_df, loocv_df, integrity_df, cases_csv)

    # Concise verdict for the terminal.
    if not main_tests.empty:
        turnover_row = main_tests.loc[main_tests["feature"] == "ivf_turnover_early"]
        hv_row = main_tests.loc[main_tests["feature"] == "hv_final_delta"]
        turnover_sig = bool(not turnover_row.empty and turnover_row.iloc[0]["p_bh"] < 0.05)
        hv_sig = bool(not hv_row.empty and hv_row.iloc[0]["p_bh"] < 0.05)
        print("\n" + "=" * 70)
        print("VERDICT")
        print("=" * 70)
        print(f"Main setting uses early_frac={MAIN_EARLY_FRAC:.2f} and help_cutoff={MAIN_HELP_CUTOFF:.2f}")
        print(f"Turnover BH-FDR significant: {turnover_sig}")
        print(f"HV robustness BH-FDR significant: {hv_sig}")
        if turnover_sig or hv_sig:
            print(">>> Candidate dynamic signal survives the main correction gate. <<<")
        else:
            print(">>> Candidate signal is exploratory; keep the paper framed conservatively. <<<")
        if not loocv_df.empty:
            best = loocv_df.iloc[0]
            print(
                f"Best LOOCV early feature: {best['feature']} | "
                f"BA={best['balanced_accuracy']:.3f}, MCC={best['mcc']:.3f}, Acc={best['accuracy']:.3f}"
            )


if __name__ == "__main__":
    main()
