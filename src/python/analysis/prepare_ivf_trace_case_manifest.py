#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ivf_trace_common import (
    PROJECT_ROOT,
    a12_higher_better,
    a12_lower_better,
    ensure_directory,
    normalize_m_value,
)

try:
    from cohort_filter import filter_submission_synthetic_cohort
except ModuleNotFoundError:  # pragma: no cover
    from src.python.analysis.cohort_filter import filter_submission_synthetic_cohort


DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "todas_metricas_consolidado_with_modern.csv"
)
CONFIG_PATH = PROJECT_ROOT / "config" / "ivf_trace_cases.csv"
OUT_DIR = PROJECT_ROOT / "results" / "ivf_trace"


def build_case_screening_table(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (problem, m_raw), group in df.groupby(["Problema", "M"]):
        ivf = group[group["Algoritmo"] == "IVFSPEA2"]
        spea2 = group[group["Algoritmo"] == "SPEA2"]
        if len(ivf) != 60 or len(spea2) != 60:
            continue

        ivf_igd = ivf["IGD"].dropna().to_numpy()
        spea_igd = spea2["IGD"].dropna().to_numpy()
        ivf_hv = ivf["HV"].dropna().to_numpy()
        spea_hv = spea2["HV"].dropna().to_numpy()
        if (
            len(ivf_igd) != 60
            or len(spea_igd) != 60
            or len(ivf_hv) != 60
            or len(spea_hv) != 60
        ):
            continue

        ivf_igd_series = pd.Series(ivf_igd)
        spea_igd_series = pd.Series(spea_igd)
        ivf_hv_series = pd.Series(ivf_hv)
        spea_hv_series = pd.Series(spea_hv)

        rows.append(
            {
                "problem": problem,
                "m": normalize_m_value(m_raw),
                "ivf_median_igd": float(ivf_igd_series.median()),
                "spea2_median_igd": float(spea_igd_series.median()),
                "ivf_median_hv": float(ivf_hv_series.median()),
                "spea2_median_hv": float(spea_hv_series.median()),
                "delta_median_igd": float(
                    spea_igd_series.median() - ivf_igd_series.median()
                ),
                "delta_median_hv": float(
                    ivf_hv_series.median() - spea_hv_series.median()
                ),
                "a12_igd_ivf_better": a12_lower_better(ivf_igd, spea_igd),
                "a12_hv_ivf_better": a12_higher_better(ivf_hv, spea_hv),
                "ivf_q1_igd": float(ivf_igd_series.quantile(0.25)),
                "ivf_q3_igd": float(ivf_igd_series.quantile(0.75)),
                "spea2_q1_igd": float(spea_igd_series.quantile(0.25)),
                "spea2_q3_igd": float(spea_igd_series.quantile(0.75)),
                "ivf_iqr_igd": float(
                    ivf_igd_series.quantile(0.75) - ivf_igd_series.quantile(0.25)
                ),
            }
        )
    out = pd.DataFrame(rows)
    out = out.sort_values(["problem", "m"]).reset_index(drop=True)
    out["positive_rank"] = out["delta_median_igd"].rank(ascending=False, method="min")
    out["negative_rank"] = out["delta_median_igd"].rank(ascending=True, method="min")
    out["bimodal_rank"] = out["ivf_iqr_igd"].rank(ascending=False, method="min")
    return out


def main() -> None:
    ensure_directory(OUT_DIR)

    raw_df = pd.read_csv(DATA_PATH)
    cohort = filter_submission_synthetic_cohort(raw_df)
    screening = build_case_screening_table(cohort)
    screening_path = OUT_DIR / "case_screening_summary.csv"
    screening.to_csv(screening_path, index=False)

    manifest = pd.read_csv(CONFIG_PATH)
    enriched = manifest.merge(
        screening,
        how="left",
        left_on=["problem", "m"],
        right_on=["problem", "m"],
    )
    enriched["supported_by_hv"] = enriched["a12_hv_ivf_better"].fillna(0.0) >= 0.5
    enriched["supported_by_igd"] = enriched["a12_igd_ivf_better"].fillna(0.0) >= 0.5
    enriched_path = OUT_DIR / "case_selection_manifest_enriched.csv"
    enriched.to_csv(enriched_path, index=False)

    print(f"Saved: {screening_path}")
    print(f"Saved: {enriched_path}")
    print("Configured trace cases:")
    for row in enriched.sort_values("display_order").itertuples(index=False):
        print(
            f"  {row.case_id}: {row.problem}(M={row.m}) | "
            f"dIGD={row.delta_median_igd:.6g} | "
            f"A12_IGD={row.a12_igd_ivf_better:.3f} | "
            f"A12_HV={row.a12_hv_ivf_better:.3f} | "
            f"IQR_IVF={row.ivf_iqr_igd:.6g}"
        )


if __name__ == "__main__":
    main()
