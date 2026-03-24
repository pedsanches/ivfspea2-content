"""
Quick signal test: Can early-generation population dynamics discriminate
HELPS vs NOT_HELPS instances?

This script:
1. Reads all 18 cases of paired trajectory data (.mat files)
2. Computes per-instance summary statistics from the FIRST 20% of generations
3. Tests whether these early-dynamic features separate HELPS from NOT_HELPS
4. Reports effect sizes and p-values

If the signal is strong, Option C (hybrid paper) is viable.
If weak, fall back to Option B (pure negative FLA result).
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def load_mat_generations(mat_path):
    """Load trace_generations from a .mat file using pymatreader."""
    from pymatreader import read_mat
    data = read_mat(str(mat_path))
    gens = data.get("trace_generations", [])
    if isinstance(gens, dict):
        # Single generation case -- wrap in list
        gens = [gens]
    return gens


def extract_run_features(ivf_gens, spea2_gens, early_frac=0.20):
    """Extract early-phase dynamic features from a paired run."""
    n_gen = min(len(ivf_gens), len(spea2_gens))
    if n_gen < 10:
        return None

    cutoff = max(int(n_gen * early_frac), 5)

    def safe_mean(gens, key, start, end):
        vals = []
        for g in gens[start:end]:
            if isinstance(g, dict) and key in g:
                v = g[key]
                if isinstance(v, (int, float, np.integer, np.floating)) and np.isfinite(v):
                    vals.append(float(v))
        return np.mean(vals) if vals else np.nan

    def safe_vals(gens, key, start, end):
        vals = []
        for g in gens[start:end]:
            if isinstance(g, dict) and key in g:
                v = g[key]
                if isinstance(v, (int, float, np.integer, np.floating)) and np.isfinite(v):
                    vals.append(float(v))
        return vals

    # Early phase features (first 20%)
    ivf_turnover_early = safe_mean(ivf_gens, "turnover", 1, cutoff)
    spea2_turnover_early = safe_mean(spea2_gens, "turnover", 1, cutoff)

    ivf_nd_early = safe_mean(ivf_gens, "nd_fraction", 1, cutoff)
    spea2_nd_early = safe_mean(spea2_gens, "nd_fraction", 1, cutoff)

    ivf_fitness_early = safe_mean(ivf_gens, "mean_fitness", 1, cutoff)
    spea2_fitness_early = safe_mean(spea2_gens, "mean_fitness", 1, cutoff)

    ivf_spacing_early = safe_mean(ivf_gens, "spacing", 1, cutoff)
    spea2_spacing_early = safe_mean(spea2_gens, "spacing", 1, cutoff)

    # IGD at early cutoff and final
    ivf_igd_early = safe_vals(ivf_gens, "igd", cutoff - 3, cutoff)
    spea2_igd_early = safe_vals(spea2_gens, "igd", cutoff - 3, cutoff)
    ivf_igd_final = safe_vals(ivf_gens, "igd", n_gen - 3, n_gen)
    spea2_igd_final = safe_vals(spea2_gens, "igd", n_gen - 3, n_gen)

    # IVF activation in early phase
    ivf_cycles_early = safe_mean(ivf_gens, "n_ivf_cycles", 1, cutoff)

    # Compute ratios and deltas
    turnover_ratio = ivf_turnover_early / spea2_turnover_early if spea2_turnover_early > 0 else np.nan
    nd_delta = ivf_nd_early - spea2_nd_early
    fitness_delta = spea2_fitness_early - ivf_fitness_early  # positive = IVF has lower (better) fitness
    spacing_ratio = ivf_spacing_early / spea2_spacing_early if spea2_spacing_early > 0 else np.nan

    # Early IGD advantage
    igd_early_delta = (np.mean(spea2_igd_early) - np.mean(ivf_igd_early)) if ivf_igd_early and spea2_igd_early else np.nan
    igd_final_delta = (np.mean(spea2_igd_final) - np.mean(ivf_igd_final)) if ivf_igd_final and spea2_igd_final else np.nan

    return {
        "ivf_turnover_early": ivf_turnover_early,
        "spea2_turnover_early": spea2_turnover_early,
        "turnover_ratio": turnover_ratio,
        "ivf_nd_early": ivf_nd_early,
        "spea2_nd_early": spea2_nd_early,
        "nd_delta": nd_delta,
        "fitness_delta": fitness_delta,
        "spacing_ratio": spacing_ratio,
        "ivf_cycles_early": ivf_cycles_early,
        "igd_early_delta": igd_early_delta,
        "igd_final_delta": igd_final_delta,
    }


def main():
    cases_csv = PROJECT_ROOT / "config" / "ppsn_dynamics_cases.csv"
    response_csv = PROJECT_ROOT / "data" / "processed" / "fla_response.csv"
    ivf_root = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics" / "ivf"
    spea2_root = PROJECT_ROOT / "data" / "raw" / "ppsn_dynamics" / "spea2"

    cases = pd.read_csv(cases_csv)
    response = pd.read_csv(response_csv)

    print("=" * 70)
    print("DYNAMIC SIGNAL TEST -- Can early dynamics discriminate HELPS vs NOT_HELPS?")
    print("=" * 70)

    all_features = []

    for _, case in cases.iterrows():
        case_id = case["case_id"]
        label = case["label_binary"]
        role = case["role"]

        ivf_dir = ivf_root / case_id
        spea2_dir = spea2_root / case_id

        if not ivf_dir.exists() or not spea2_dir.exists():
            print(f"  SKIP {case_id}: directory missing")
            continue

        ivf_files = sorted(ivf_dir.glob("IVF_*.mat"))
        spea2_files = sorted(spea2_dir.glob("SPEA2_*.mat"))

        run_features = []
        n_loaded = 0
        for ivf_f, spea2_f in zip(ivf_files, spea2_files):
            try:
                ivf_gens = load_mat_generations(ivf_f)
                spea2_gens = load_mat_generations(spea2_f)
                feats = extract_run_features(ivf_gens, spea2_gens)
                if feats is not None:
                    run_features.append(feats)
                    n_loaded += 1
            except Exception as e:
                pass  # skip corrupted files

            if n_loaded >= 10:  # Sample 10 runs per case for speed
                break

        if not run_features:
            print(f"  SKIP {case_id}: no valid runs")
            continue

        # Average across runs for this instance
        avg = {}
        for key in run_features[0]:
            vals = [r[key] for r in run_features if np.isfinite(r[key])]
            avg[key] = np.mean(vals) if vals else np.nan

        avg["case_id"] = case_id
        avg["label_binary"] = label
        avg["role"] = role
        all_features.append(avg)
        print(f"  {case_id}: {n_loaded} runs loaded, label={label}")

    df = pd.DataFrame(all_features)
    print(f"\nInstances loaded: {len(df)}")
    print(f"  HELPS: {sum(df.label_binary == 'HELPS')}")
    print(f"  NOT_HELPS: {sum(df.label_binary == 'NOT_HELPS')}")

    # Test each feature
    feature_cols = [c for c in df.columns if c not in ("case_id", "label_binary", "role")]

    print("\n" + "=" * 70)
    print("MANN-WHITNEY U TESTS: HELPS vs NOT_HELPS on early-dynamic features")
    print("=" * 70)
    print(f"{'Feature':<25} {'HELPS mean':>12} {'NOT_HELPS mean':>14} {'U-stat':>8} {'p-value':>10} {'A12':>6} {'Signal':>8}")
    print("-" * 90)

    results = []
    for col in feature_cols:
        helps = df.loc[df.label_binary == "HELPS", col].dropna()
        not_helps = df.loc[df.label_binary == "NOT_HELPS", col].dropna()

        if len(helps) < 3 or len(not_helps) < 3:
            continue

        stat, p = stats.mannwhitneyu(helps, not_helps, alternative="two-sided")
        a12 = stat / (len(helps) * len(not_helps))

        signal = ""
        if p < 0.05:
            signal = "STRONG" if p < 0.01 else "YES"
        elif p < 0.10:
            signal = "WEAK"

        print(f"{col:<25} {helps.mean():>12.4f} {not_helps.mean():>14.4f} {stat:>8.1f} {p:>10.4f} {a12:>6.3f} {signal:>8}")
        results.append({"feature": col, "helps_mean": helps.mean(), "not_helps_mean": not_helps.mean(),
                         "u_stat": stat, "p_value": p, "a12": a12})

    # Spearman correlation with final IGD delta
    print("\n" + "=" * 70)
    print("SPEARMAN CORRELATIONS: Early features vs Final IGD delta")
    print("=" * 70)
    print(f"{'Feature':<25} {'rho':>8} {'p-value':>10} {'Signal':>8}")
    print("-" * 55)

    for col in feature_cols:
        if col == "igd_final_delta":
            continue
        valid = df[[col, "igd_final_delta"]].dropna()
        if len(valid) < 5:
            continue
        rho, p = stats.spearmanr(valid[col], valid["igd_final_delta"])
        signal = ""
        if p < 0.05:
            signal = "STRONG" if p < 0.01 else "YES"
        elif p < 0.10:
            signal = "WEAK"
        print(f"{col:<25} {rho:>8.3f} {p:>10.4f} {signal:>8}")

    # Summary verdict
    sig_features = [r for r in results if r["p_value"] < 0.10]
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print(f"Features tested: {len(results)}")
    print(f"Features with p < 0.10: {len(sig_features)}")
    print(f"Features with p < 0.05: {len([r for r in results if r['p_value'] < 0.05])}")

    if len(sig_features) >= 2:
        print("\n>>> SIGNAL EXISTS. Option C (hybrid paper) is viable. <<<")
    elif len(sig_features) == 1:
        print("\n>>> WEAK SIGNAL. Option C is risky. Consider Option B. <<<")
    else:
        print("\n>>> NO SIGNAL. Fall back to Option B (pure negative FLA result). <<<")

    # Save for reference
    out_path = PROJECT_ROOT / "data" / "processed" / "dynamic_signal_test.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved instance-level features to: {out_path}")


if __name__ == "__main__":
    main()
