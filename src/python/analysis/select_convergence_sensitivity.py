#!/usr/bin/env python3
"""Select alternative (2nd-best) convergence instances for sensitivity analysis.

Uses the same protocol as select_convergence_instances.py but picks the
2nd-best candidate per role instead of the 1st. Compares qualitative
conclusions (IVF vs base direction) between the two selections.

Output:
  results/tables/hosts_convergence_instances_alt2.csv
  results/tables/convergence_selection_sensitivity.csv
"""

import os

import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
OUT_ALT2 = os.path.join(TABLES_DIR, "hosts_convergence_instances_alt2.csv")
OUT_SENS = os.path.join(TABLES_DIR, "convergence_selection_sensitivity.csv")

TRACKS = {
    "IVFSPEA2": "hosts_ivfspea2_igd_stats.csv",
    "IVFNSGAII": "hosts_ivfnsgaii_igd_stats.csv",
    "IVFNSGAIII": "hosts_ivfnsgaiii_igd_stats.csv",
}


def load_oriented_a12() -> pd.DataFrame:
    frames = []
    for algo, fname in TRACKS.items():
        df = pd.read_csv(os.path.join(TABLES_DIR, fname))
        df["algo"] = algo
        df["A12_ivf"] = 1.0 - df["A12"]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def pivot_a12(df: pd.DataFrame) -> pd.DataFrame:
    piv = df.pivot_table(
        index=["problem", "M", "group"],
        columns="algo",
        values=["A12_ivf", "sign"],
        aggfunc="first",
    ).reset_index()
    piv.columns = [f"{a}_{b}" if b else a for a, b in piv.columns]
    return piv


def unused_instances(frame: pd.DataFrame, used: set[tuple[str, int]]) -> pd.DataFrame:
    if frame.empty or not used:
        return frame.copy()
    mask = frame.apply(
        lambda row: (str(row["problem"]), int(row["M"])) not in used, axis=1,
    )
    return frame[mask].copy()


def pick_nth(
    cand: pd.DataFrame, sort_cols: list[str], ascending: list[bool], nth: int = 1,
) -> pd.Series | None:
    """Pick the nth best (0-indexed) candidate from a sorted dataframe."""
    sorted_df = cand.sort_values(sort_cols, ascending=ascending)
    if len(sorted_df) <= nth:
        return None
    return sorted_df.iloc[nth]


def select_alt2_instances(df: pd.DataFrame) -> list[dict]:
    """Same protocol as original but picks 2nd-best (index 1) per role."""
    piv = pivot_a12(df)
    selections: list[dict] = []
    used: set[tuple[str, int]] = set()

    # Slot 1: strong_both_dtlz
    cand = piv[(piv["group"] == "DTLZ") & (piv["M"] == 2)].copy()
    preferred = cand[(cand["sign_IVFSPEA2"] == "+") & (cand["sign_IVFNSGAIII"] == "+")]
    if not preferred.empty:
        cand = preferred
    cand["combined"] = cand["A12_ivf_IVFSPEA2"] + cand["A12_ivf_IVFNSGAIII"]
    best = pick_nth(cand, ["combined", "A12_ivf_IVFSPEA2", "A12_ivf_IVFNSGAIII"],
                    [False, False, False], nth=1)
    if best is not None:
        used.add((str(best["problem"]), int(best["M"])))
        selections.append({"slot": 1, "problem": str(best["problem"]),
                          "M": int(best["M"]), "role": "strong_both_dtlz"})

    # Slot 2: strong_both_maf
    cand = piv[(piv["group"] == "MaF") & (piv["M"] == 2)].copy()
    preferred = cand[(cand["sign_IVFSPEA2"] == "+") & (cand["sign_IVFNSGAIII"] == "+")]
    if not preferred.empty:
        cand = preferred
    cand["combined"] = cand["A12_ivf_IVFSPEA2"] + cand["A12_ivf_IVFNSGAIII"]
    best = pick_nth(cand, ["combined", "A12_ivf_IVFSPEA2", "A12_ivf_IVFNSGAIII"],
                    [False, False, False], nth=1)
    if best is not None:
        key = (str(best["problem"]), int(best["M"]))
        if key not in used:
            used.add(key)
            selections.append({"slot": 2, "problem": str(best["problem"]),
                              "M": int(best["M"]), "role": "strong_both_maf"})

    # Slot 3: difficult_wfg
    cand = unused_instances(piv[(piv["group"] == "WFG") & (piv["M"] == 2)], used)
    cand["tie_count"] = cand[["sign_IVFSPEA2", "sign_IVFNSGAII", "sign_IVFNSGAIII"]].eq("=").sum(axis=1)
    cand["combined"] = cand["A12_ivf_IVFSPEA2"] + cand["A12_ivf_IVFNSGAII"] + cand["A12_ivf_IVFNSGAIII"]
    best = pick_nth(cand, ["tie_count", "combined"], [False, True], nth=1)
    if best is not None:
        key = (str(best["problem"]), int(best["M"]))
        if key not in used:
            used.add(key)
            selections.append({"slot": 3, "problem": str(best["problem"]),
                              "M": int(best["M"]), "role": "difficult_wfg"})

    # Slot 4: spea2_wins_zdt
    cand = unused_instances(piv[(piv["group"] == "ZDT") & (piv["M"] == 2)], used)
    preferred = cand[cand["sign_IVFSPEA2"] == "+"]
    if not preferred.empty:
        cand = preferred
    cand["neutrality_nsgaii"] = (cand["A12_ivf_IVFNSGAII"] - 0.5).abs()
    cand["score"] = cand["A12_ivf_IVFSPEA2"] - cand["neutrality_nsgaii"]
    best = pick_nth(cand, ["score", "A12_ivf_IVFSPEA2", "neutrality_nsgaii"],
                    [False, False, True], nth=1)
    if best is not None:
        key = (str(best["problem"]), int(best["M"]))
        if key not in used:
            used.add(key)
            selections.append({"slot": 4, "problem": str(best["problem"]),
                              "M": int(best["M"]), "role": "spea2_wins_zdt"})

    # Slot 5: nsgaiii_drops_m3
    cand_m3 = piv[(piv["group"] == "DTLZ") & (piv["M"] == 3)].copy()
    cand_m2 = piv[(piv["group"] == "DTLZ") & (piv["M"] == 2)].copy()
    merged = cand_m3.merge(cand_m2, on="problem", suffixes=("_m3", "_m2"))
    merged = merged[~merged["problem"].apply(lambda p: (str(p), 3) in used)].copy()
    preferred = merged[
        (merged["sign_IVFNSGAIII_m2"] == "+") & (merged["sign_IVFNSGAIII_m3"] == "=")
    ]
    if not preferred.empty:
        merged = preferred
    merged["drop"] = merged["A12_ivf_IVFNSGAIII_m2"] - merged["A12_ivf_IVFNSGAIII_m3"]
    best = pick_nth(merged, ["drop", "A12_ivf_IVFNSGAIII_m2"], [False, False], nth=1)
    if best is not None:
        key = (str(best["problem"]), 3)
        if key not in used:
            used.add(key)
            selections.append({"slot": 5, "problem": str(best["problem"]),
                              "M": 3, "role": "nsgaiii_drops_m3"})

    # Slot 6: spea2_loss_wfg
    spea2_df = unused_instances(
        df[(df["algo"] == "IVFSPEA2") & (df["group"] == "WFG") & (df["M"] == 2)], used,
    )
    losses = spea2_df[spea2_df["sign"] == "-"]
    if not losses.empty:
        best = pick_nth(losses.sort_values("A12_ivf"), ["A12_ivf"], [True], nth=1)
    else:
        best = pick_nth(spea2_df.sort_values("A12_ivf"), ["A12_ivf"], [True], nth=1)
    if best is not None:
        key = (str(best["problem"]), int(best["M"]))
        if key not in used:
            used.add(key)
            selections.append({"slot": 6, "problem": str(best["problem"]),
                              "M": int(best["M"]), "role": "spea2_loss_wfg"})

    return selections


def main() -> None:
    print("=== Selecting alternative (2nd-best) convergence instances ===\n")
    df = load_oriented_a12()

    # Load original selection
    orig = pd.read_csv(os.path.join(TABLES_DIR, "hosts_convergence_instances.csv"))

    # Select alternatives
    alt2 = pd.DataFrame(select_alt2_instances(df))
    alt2.to_csv(OUT_ALT2, index=False)
    print(f"Alternative instances saved to {OUT_ALT2}\n")
    for _, row in alt2.iterrows():
        print(f"  Slot {row['slot']}: {row['problem']} M={row['M']} ({row['role']})")

    # Compare
    orig_set = set(zip(orig["problem"], orig["M"]))
    alt2_set = set(zip(alt2["problem"], alt2["M"]))
    overlap = orig_set & alt2_set
    print(f"\nOverlap: {len(overlap)}/{len(orig_set)} instances in common")
    print(f"  Original only: {orig_set - alt2_set}")
    print(f"  Alt2 only:     {alt2_set - orig_set}")

    # Save sensitivity report
    report = pd.DataFrame({
        "original": [f"{r['problem']}_M{r['M']}" for _, r in orig.iterrows()],
        "alt2": [f"{r['problem']}_M{r['M']}" if (_, r['M']) in alt2_set and r['problem'] in [x[0] for x in alt2_set] else "different"
                for _, r in orig.iterrows()],
        "role": orig["role"].tolist(),
    })
    report.to_csv(OUT_SENS, index=False)
    print(f"\nSensitivity report: {OUT_SENS}")


if __name__ == "__main__":
    main()
