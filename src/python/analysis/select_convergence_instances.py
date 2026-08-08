#!/usr/bin/env python3
"""Select representative instances for the hosts convergence figure."""

import os

import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
TABLES_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
OUT_CSV = os.path.join(TABLES_DIR, "hosts_convergence_instances.csv")

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
        lambda row: (str(row["problem"]), int(row["M"])) not in used,
        axis=1,
    )
    return frame[mask].copy()


def add_selection(
    selections: list[dict],
    used: set[tuple[str, int]],
    problem: str,
    m_val: int,
    role: str,
) -> None:
    key = (str(problem), int(m_val))
    if key in used:
        raise ValueError(f"duplicate convergence instance selected: {key}")
    used.add(key)
    selections.append(
        {
            "slot": len(selections) + 1,
            "problem": str(problem),
            "M": int(m_val),
            "role": role,
        }
    )


def select_instances(df: pd.DataFrame) -> list[dict]:
    piv = pivot_a12(df)
    selections: list[dict] = []
    used: set[tuple[str, int]] = set()

    cand = piv[(piv["group"] == "DTLZ") & (piv["M"] == 2)].copy()
    preferred = cand[(cand["sign_IVFSPEA2"] == "+") & (cand["sign_IVFNSGAIII"] == "+")]
    if not preferred.empty:
        cand = preferred
    cand["combined"] = cand["A12_ivf_IVFSPEA2"] + cand["A12_ivf_IVFNSGAIII"]
    best = cand.sort_values(
        ["combined", "A12_ivf_IVFSPEA2", "A12_ivf_IVFNSGAIII"],
        ascending=False,
    ).iloc[0]
    add_selection(selections, used, best["problem"], best["M"], "strong_both_dtlz")

    cand = piv[(piv["group"] == "MaF") & (piv["M"] == 2)].copy()
    preferred = cand[(cand["sign_IVFSPEA2"] == "+") & (cand["sign_IVFNSGAIII"] == "+")]
    if not preferred.empty:
        cand = preferred
    cand["combined"] = cand["A12_ivf_IVFSPEA2"] + cand["A12_ivf_IVFNSGAIII"]
    best = cand.sort_values(
        ["combined", "A12_ivf_IVFSPEA2", "A12_ivf_IVFNSGAIII"],
        ascending=False,
    ).iloc[0]
    add_selection(selections, used, best["problem"], best["M"], "strong_both_maf")

    cand = unused_instances(piv[(piv["group"] == "WFG") & (piv["M"] == 2)], used)
    cand["tie_count"] = (
        cand[["sign_IVFSPEA2", "sign_IVFNSGAII", "sign_IVFNSGAIII"]].eq("=").sum(axis=1)
    )
    cand["combined"] = (
        cand["A12_ivf_IVFSPEA2"]
        + cand["A12_ivf_IVFNSGAII"]
        + cand["A12_ivf_IVFNSGAIII"]
    )
    best = cand.sort_values(["tie_count", "combined"], ascending=[False, True]).iloc[0]
    add_selection(selections, used, best["problem"], best["M"], "difficult_wfg")

    cand = unused_instances(piv[(piv["group"] == "ZDT") & (piv["M"] == 2)], used)
    preferred = cand[cand["sign_IVFSPEA2"] == "+"]
    if not preferred.empty:
        cand = preferred
    cand["neutrality_nsgaii"] = (cand["A12_ivf_IVFNSGAII"] - 0.5).abs()
    cand["score"] = cand["A12_ivf_IVFSPEA2"] - cand["neutrality_nsgaii"]
    best = cand.sort_values(
        ["score", "A12_ivf_IVFSPEA2", "neutrality_nsgaii"],
        ascending=[False, False, True],
    ).iloc[0]
    add_selection(selections, used, best["problem"], best["M"], "spea2_wins_zdt")

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
    best = merged.sort_values(
        ["drop", "A12_ivf_IVFNSGAIII_m2"], ascending=[False, False]
    ).iloc[0]
    add_selection(selections, used, best["problem"], 3, "nsgaiii_drops_m3")

    spea2_df = unused_instances(
        df[(df["algo"] == "IVFSPEA2") & (df["group"] == "WFG") & (df["M"] == 2)],
        used,
    )
    losses = spea2_df[spea2_df["sign"] == "-"]
    if not losses.empty:
        worst = losses.sort_values("A12_ivf").iloc[0]
        add_selection(selections, used, worst["problem"], worst["M"], "spea2_loss_wfg")
    else:
        worst = spea2_df.sort_values("A12_ivf").iloc[0]
        add_selection(
            selections, used, worst["problem"], worst["M"], "spea2_weakest_wfg"
        )

    return selections


def main() -> None:
    print("=== Selecting convergence instances ===\n")
    df = load_oriented_a12()
    out = pd.DataFrame(select_instances(df))
    if out[["problem", "M"]].duplicated().any():
        raise SystemExit("duplicate (problem, M) pairs found in convergence selection")
    out.to_csv(OUT_CSV, index=False)
    print(f"Selected instances saved to {OUT_CSV}\n")
    for _, row in out.iterrows():
        print(f"  Slot {row['slot']}: {row['problem']} M={row['M']} ({row['role']})")


if __name__ == "__main__":
    main()
