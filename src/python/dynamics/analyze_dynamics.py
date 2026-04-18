"""Analyze population dynamics: convergence curves, diversity profiles, IVF impact.

Reads ppsn_trajectories.csv and produces publication-quality figures
comparing IVF-SPEA2 vs SPEA2 trajectories across generations.

Output: results/figures/dynamics_*.png, results/tables/dynamics_*.csv
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
FIG_DIR = PROJECT_ROOT / "results" / "figures"
TAB_DIR = PROJECT_ROOT / "results" / "tables"

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

COLORS = {"IVF-SPEA2": "#2171b5", "SPEA2": "#cb181d"}
MANIFEST = PROJECT_ROOT / "config" / "ppsn_dynamics_cases.csv"


def load_data():
    path = DATA_DIR / "ppsn_trajectories.csv"
    if not path.exists():
        print(f"ERROR: {path} not found. Run extract_trajectories.py first.")
        sys.exit(1)
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows, {df['case_id'].nunique()} cases")
    return df


def compute_median_trajectories(df):
    """Compute median and IQR trajectories per (case, algorithm, generation)."""
    grouped = df.groupby(["case_id", "algorithm", "generation"])
    agg = grouped.agg(
        igd_median=("igd", "median"),
        igd_q25=("igd", lambda x: x.quantile(0.25)),
        igd_q75=("igd", lambda x: x.quantile(0.75)),
        hv_median=("hv", "median"),
        hv_q25=("hv", lambda x: x.quantile(0.25)),
        hv_q75=("hv", lambda x: x.quantile(0.75)),
        spread_median=("spread", "median"),
        spread_q25=("spread", lambda x: x.quantile(0.25)),
        spread_q75=("spread", lambda x: x.quantile(0.75)),
        spacing_median=("spacing", "median"),
        turnover_median=("turnover", "median"),
        nd_fraction_median=("nd_fraction", "median"),
        ivf_activated_frac=("ivf_activated", "mean"),
        n_ivf_cycles_median=("n_ivf_cycles", "median"),
    ).reset_index()
    return agg


def plot_convergence_curves(agg, cases, manifest):
    """Plot IGD and HV convergence curves for each case."""
    n_cases = len(cases)
    n_cols = min(3, n_cases)
    n_rows = int(np.ceil(n_cases / n_cols))

    # IGD convergence
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows),
                             squeeze=False)
    for idx, case_id in enumerate(cases):
        ax = axes[idx // n_cols, idx % n_cols]
        role = manifest.loc[manifest["case_id"] == case_id, "role"].iloc[0]

        for algo in ["IVF-SPEA2", "SPEA2"]:
            sub = agg[(agg["case_id"] == case_id) & (agg["algorithm"] == algo)]
            if sub.empty:
                continue
            gen = sub["generation"].values
            ax.plot(gen, sub["igd_median"].values, color=COLORS[algo],
                    label=algo, linewidth=1.5)
            ax.fill_between(gen, sub["igd_q25"].values, sub["igd_q75"].values,
                            color=COLORS[algo], alpha=0.15)

        problem = case_id.split("_")[-2].upper() + "_M" + case_id.split("_m")[-1]
        ax.set_title(f"{problem} ({role})", fontsize=11)
        ax.set_xlabel("Generation")
        ax.set_ylabel("IGD")
        ax.set_yscale("log")
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(n_cases, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle("IGD Convergence: IVF-SPEA2 vs SPEA2", fontsize=14, y=1.01)
    fig.tight_layout()
    out = FIG_DIR / "dynamics_igd_convergence.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out}")

    # HV convergence
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows),
                             squeeze=False)
    for idx, case_id in enumerate(cases):
        ax = axes[idx // n_cols, idx % n_cols]
        role = manifest.loc[manifest["case_id"] == case_id, "role"].iloc[0]

        for algo in ["IVF-SPEA2", "SPEA2"]:
            sub = agg[(agg["case_id"] == case_id) & (agg["algorithm"] == algo)]
            if sub.empty:
                continue
            gen = sub["generation"].values
            ax.plot(gen, sub["hv_median"].values, color=COLORS[algo],
                    label=algo, linewidth=1.5)
            ax.fill_between(gen, sub["hv_q25"].values, sub["hv_q75"].values,
                            color=COLORS[algo], alpha=0.15)

        problem = case_id.split("_")[-2].upper() + "_M" + case_id.split("_m")[-1]
        ax.set_title(f"{problem} ({role})", fontsize=11)
        ax.set_xlabel("Generation")
        ax.set_ylabel("HV")
        ax.legend(loc="lower right", framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)

    for idx in range(n_cases, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle("HV Convergence: IVF-SPEA2 vs SPEA2", fontsize=14, y=1.01)
    fig.tight_layout()
    out = FIG_DIR / "dynamics_hv_convergence.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_diversity_profiles(agg, cases, manifest):
    """Plot spread and turnover profiles."""
    n_cases = len(cases)
    n_cols = min(3, n_cases)
    n_rows = int(np.ceil(n_cases / n_cols))

    # Spread
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows),
                             squeeze=False)
    for idx, case_id in enumerate(cases):
        ax = axes[idx // n_cols, idx % n_cols]
        role = manifest.loc[manifest["case_id"] == case_id, "role"].iloc[0]

        for algo in ["IVF-SPEA2", "SPEA2"]:
            sub = agg[(agg["case_id"] == case_id) & (agg["algorithm"] == algo)]
            if sub.empty:
                continue
            gen = sub["generation"].values
            ax.plot(gen, sub["spread_median"].values, color=COLORS[algo],
                    label=algo, linewidth=1.5)
            ax.fill_between(gen, sub["spread_q25"].values, sub["spread_q75"].values,
                            color=COLORS[algo], alpha=0.15)

        problem = case_id.split("_")[-2].upper() + "_M" + case_id.split("_m")[-1]
        ax.set_title(f"{problem} ({role})", fontsize=11)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Spread (max pairwise dist)")
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)

    for idx in range(n_cases, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle("Population Spread: IVF-SPEA2 vs SPEA2", fontsize=14, y=1.01)
    fig.tight_layout()
    out = FIG_DIR / "dynamics_spread.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out}")

    # Turnover
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows),
                             squeeze=False)
    for idx, case_id in enumerate(cases):
        ax = axes[idx // n_cols, idx % n_cols]
        role = manifest.loc[manifest["case_id"] == case_id, "role"].iloc[0]

        for algo in ["IVF-SPEA2", "SPEA2"]:
            sub = agg[(agg["case_id"] == case_id) & (agg["algorithm"] == algo)]
            if sub.empty:
                continue
            gen = sub["generation"].values
            ax.plot(gen, sub["turnover_median"].values, color=COLORS[algo],
                    label=algo, linewidth=1.5, alpha=0.8)

        problem = case_id.split("_")[-2].upper() + "_M" + case_id.split("_m")[-1]
        ax.set_title(f"{problem} ({role})", fontsize=11)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Archive Turnover")
        ax.set_ylim(0, 1)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)

    for idx in range(n_cases, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle("Archive Turnover: IVF-SPEA2 vs SPEA2", fontsize=14, y=1.01)
    fig.tight_layout()
    out = FIG_DIR / "dynamics_turnover.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_ivf_activation_heatmap(df, cases, manifest):
    """Heatmap of IVF activation frequency across generations."""
    ivf_data = df[df["algorithm"] == "IVF-SPEA2"]

    fig, axes = plt.subplots(1, len(cases), figsize=(3 * len(cases), 4),
                             squeeze=False)

    for idx, case_id in enumerate(cases):
        ax = axes[0, idx]
        sub = ivf_data[ivf_data["case_id"] == case_id]
        if sub.empty:
            ax.set_visible(False)
            continue

        # Pivot: runs x generations, values = n_ivf_cycles
        pivot = sub.pivot_table(
            index="run_id", columns="generation", values="n_ivf_cycles",
            aggfunc="first", fill_value=0
        )

        # Subsample generations for readability
        gen_step = max(1, len(pivot.columns) // 50)
        pivot_sub = pivot.iloc[:, ::gen_step]

        im = ax.imshow(pivot_sub.values, aspect="auto", cmap="YlOrRd",
                       interpolation="nearest", vmin=0, vmax=3)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Run")

        problem = case_id.split("_")[-2].upper() + "_M" + case_id.split("_m")[-1]
        role = manifest.loc[manifest["case_id"] == case_id, "role"].iloc[0]
        ax.set_title(f"{problem}\n({role})", fontsize=10)

        # Fix x-axis labels
        n_ticks = 5
        tick_positions = np.linspace(0, pivot_sub.shape[1] - 1, n_ticks, dtype=int)
        tick_labels = [str(pivot_sub.columns[t]) for t in tick_positions]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, fontsize=8)

    fig.suptitle("IVF Cycle Activation per Generation and Run", fontsize=13, y=1.03)
    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.6, label="IVF cycles")
    fig.tight_layout()
    out = FIG_DIR / "dynamics_ivf_activation_heatmap.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out}")


def plot_delta_igd_over_time(df, cases, manifest):
    """Plot paired delta IGD (SPEA2 - IVF) over generations."""
    n_cases = len(cases)
    n_cols = min(3, n_cases)
    n_rows = int(np.ceil(n_cases / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows),
                             squeeze=False)

    for idx, case_id in enumerate(cases):
        ax = axes[idx // n_cols, idx % n_cols]
        role = manifest.loc[manifest["case_id"] == case_id, "role"].iloc[0]

        ivf = df[(df["case_id"] == case_id) & (df["algorithm"] == "IVF-SPEA2")]
        spea2 = df[(df["case_id"] == case_id) & (df["algorithm"] == "SPEA2")]

        # Pair by seed and generation
        common_seeds = set(ivf["seed"].unique()) & set(spea2["seed"].unique())
        if not common_seeds:
            ax.set_visible(False)
            continue

        deltas = []
        for seed in sorted(common_seeds):
            ivf_s = ivf[ivf["seed"] == seed].sort_values("generation")
            spea2_s = spea2[spea2["seed"] == seed].sort_values("generation")

            # Align by generation
            merged = pd.merge(
                ivf_s[["generation", "igd"]].rename(columns={"igd": "igd_ivf"}),
                spea2_s[["generation", "igd"]].rename(columns={"igd": "igd_spea2"}),
                on="generation",
            )
            merged["delta_igd"] = merged["igd_spea2"] - merged["igd_ivf"]
            deltas.append(merged[["generation", "delta_igd"]])

        delta_df = pd.concat(deltas)
        delta_agg = delta_df.groupby("generation").agg(
            median=("delta_igd", "median"),
            q25=("delta_igd", lambda x: x.quantile(0.25)),
            q75=("delta_igd", lambda x: x.quantile(0.75)),
        ).reset_index()

        gen = delta_agg["generation"].values
        ax.plot(gen, delta_agg["median"].values, color="#2171b5", linewidth=1.5)
        ax.fill_between(gen, delta_agg["q25"].values, delta_agg["q75"].values,
                        color="#2171b5", alpha=0.2)
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

        problem = case_id.split("_")[-2].upper() + "_M" + case_id.split("_m")[-1]
        ax.set_title(f"{problem} ({role})", fontsize=11)
        ax.set_xlabel("Generation")
        ax.set_ylabel("$\\Delta$ IGD (SPEA2 - IVF)")
        ax.grid(True, alpha=0.3)

    for idx in range(n_cases, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].set_visible(False)

    fig.suptitle("Paired $\\Delta$ IGD Over Generations (>0 = IVF better)",
                 fontsize=14, y=1.01)
    fig.tight_layout()
    out = FIG_DIR / "dynamics_delta_igd.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"  Saved: {out}")


def compute_crossover_generation(df, cases):
    """Find the generation where IVF first consistently beats SPEA2."""
    results = []
    for case_id in cases:
        ivf = df[(df["case_id"] == case_id) & (df["algorithm"] == "IVF-SPEA2")]
        spea2 = df[(df["case_id"] == case_id) & (df["algorithm"] == "SPEA2")]

        common_seeds = set(ivf["seed"].unique()) & set(spea2["seed"].unique())
        if not common_seeds:
            continue

        # Compute median IGD per generation per algorithm
        ivf_med = ivf.groupby("generation")["igd"].median()
        spea2_med = spea2.groupby("generation")["igd"].median()

        gens = sorted(set(ivf_med.index) & set(spea2_med.index))

        crossover_gen = None
        for g in gens:
            if ivf_med[g] < spea2_med[g]:
                # Check if IVF stays better for at least 10 consecutive gens
                window = [g2 for g2 in gens if g <= g2 <= g + 10]
                if all(ivf_med.get(g2, 0) < spea2_med.get(g2, 1) for g2 in window):
                    crossover_gen = g
                    break

        role = df[df["case_id"] == case_id]["role"].iloc[0]
        final_ivf = ivf_med.iloc[-1] if len(ivf_med) > 0 else np.nan
        final_spea2 = spea2_med.iloc[-1] if len(spea2_med) > 0 else np.nan

        results.append({
            "case_id": case_id,
            "role": role,
            "crossover_gen": crossover_gen,
            "final_igd_ivf": final_ivf,
            "final_igd_spea2": final_spea2,
            "final_delta_igd": final_spea2 - final_ivf,
            "total_gens": len(gens),
        })

    return pd.DataFrame(results)


def main():
    print("=" * 70)
    print("PPSN 2026 -- Population Dynamics Analysis")
    print("=" * 70)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TAB_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    manifest = pd.read_csv(MANIFEST)

    cases = sorted(df["case_id"].unique())
    print(f"Analyzing {len(cases)} cases\n")

    # Compute aggregated trajectories
    print("Computing median trajectories...")
    agg = compute_median_trajectories(df)

    # Generate figures
    print("\n=== Convergence Curves ===")
    plot_convergence_curves(agg, cases, manifest)

    print("\n=== Diversity Profiles ===")
    plot_diversity_profiles(agg, cases, manifest)

    print("\n=== IVF Activation Heatmap ===")
    plot_ivf_activation_heatmap(df, cases, manifest)

    print("\n=== Paired Delta IGD ===")
    plot_delta_igd_over_time(df, cases, manifest)

    print("\n=== Crossover Generation Analysis ===")
    crossover = compute_crossover_generation(df, cases)
    crossover_path = TAB_DIR / "dynamics_crossover_generations.csv"
    crossover.to_csv(crossover_path, index=False)
    print(f"  Saved: {crossover_path}")
    print(crossover.to_string(index=False))

    print(f"\n{'=' * 70}")
    print("All dynamics analyses complete.")
    print(f"  Figures: {FIG_DIR}/dynamics_*.png")
    print(f"  Tables:  {TAB_DIR}/dynamics_*.csv")


if __name__ == "__main__":
    main()
