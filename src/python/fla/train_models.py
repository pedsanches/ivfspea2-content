#!/usr/bin/env python3
"""
FLA Predictive Modeling Pipeline for PPSN 2026.

Trains Random Forest models (regression + classification) to predict
IVF-SPEA2 competence from landscape features. Includes ablation across
feature sets, leave-one-family-out CV, permutation tests, SHAP analysis,
and hypothesis testing.

Outputs:
    results/figures/fla_permutation_importance.png
    results/figures/fla_shap_regression.png
    results/figures/fla_shap_classification.png
    results/figures/fla_shap_bar.png
    results/figures/fla_regression_scatter.png
    results/tables/fla_model_comparison.csv
    results/tables/fla_hypothesis_tests.csv
"""

import os
import re
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import rankdata, spearmanr, binom
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    balanced_accuracy_score, matthews_corrcoef, f1_score,
    precision_recall_fscore_support, confusion_matrix,
    r2_score, mean_absolute_error,
)

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "fla_dataset.csv")
FIG_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
TAB_DIR = os.path.join(PROJECT_ROOT, "results", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Feature sets
# ---------------------------------------------------------------------------
SET_ALL = [
    "corr_obj_mean", "skewness_mean", "kurtosis_mean", "cv_mean",
    "dom_depth_std", "front_connectivity", "front_diameter", "front_gap_ratio",
    "autocorr_mean", "info_content", "neutrality_ratio", "fdc_mean",
    "n_obj", "n_var",
]

SET_NO_STRUCTURAL = [
    "corr_obj_mean", "skewness_mean", "kurtosis_mean", "cv_mean",
    "dom_depth_std", "front_connectivity", "front_diameter", "front_gap_ratio",
    "autocorr_mean", "info_content", "neutrality_ratio", "fdc_mean",
]

SET_FRONT_ONLY = [
    "front_connectivity", "front_diameter", "front_gap_ratio", "dom_depth_std",
]

FEATURE_SETS = {
    "SET_ALL": SET_ALL,
    "SET_NO_STRUCTURAL": SET_NO_STRUCTURAL,
    "SET_FRONT_ONLY": SET_FRONT_ONLY,
}

# ---------------------------------------------------------------------------
# RF hyper-parameters (justified for n=51)
# ---------------------------------------------------------------------------
RF_REG_PARAMS = dict(
    n_estimators=500, max_depth=6, min_samples_leaf=3,
    max_features="sqrt", random_state=42,
)
RF_CLF_PARAMS = dict(
    n_estimators=500, max_depth=6, min_samples_leaf=3,
    max_features="sqrt", class_weight="balanced", random_state=42,
)

# ---------------------------------------------------------------------------
# Matplotlib style
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
})


# ===================================================================
# PART 1: DATA PREPARATION
# ===================================================================
def load_data():
    """Load dataset, extract family labels, rank-transform response."""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {df.shape[0]} instances x {df.shape[1]} columns")

    # Extract benchmark family from instance name
    df["family"] = df["instance"].apply(
        lambda x: re.match(r"([A-Za-z]+)", x).group(1)
    )
    print(f"Families: {dict(df['family'].value_counts())}")
    print(f"Label distribution: {dict(df['label_binary'].value_counts())}")

    # Rank-transform delta_igd for regression
    df["rank_delta_igd"] = rankdata(df["delta_igd"])

    return df


# ===================================================================
# PART 2: REGRESSION (PRIMARY ANALYSIS)
# ===================================================================
def loocv_regression(df, features, label="rank_delta_igd"):
    """Leave-one-out CV for RF regression. Returns predictions array."""
    X = df[features].values
    y = df[label].values
    n = len(y)
    preds = np.zeros(n)

    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[mask])
        X_test = scaler.transform(X[i:i+1])
        rf = RandomForestRegressor(**RF_REG_PARAMS)
        rf.fit(X_train, y[mask])
        preds[i] = rf.predict(X_test)[0]

    r_spearman, p_spearman = spearmanr(y, preds)
    r2 = r2_score(y, preds)
    mae = mean_absolute_error(y, preds)
    return preds, r_spearman, p_spearman, r2, mae


def lofo_regression(df, features, label="rank_delta_igd"):
    """Leave-one-family-out CV for RF regression."""
    X = df[features].values
    y = df[label].values
    families = df["family"].values
    unique_families = sorted(set(families))

    preds = np.full(len(y), np.nan)
    family_results = {}

    for fam in unique_families:
        test_mask = families == fam
        train_mask = ~test_mask
        if test_mask.sum() < 2:
            continue
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[train_mask])
        X_test = scaler.transform(X[test_mask])
        rf = RandomForestRegressor(**RF_REG_PARAMS)
        rf.fit(X_train, y[train_mask])
        p = rf.predict(X_test)
        preds[test_mask] = p
        r, _ = spearmanr(y[test_mask], p)
        family_results[fam] = r

    valid = ~np.isnan(preds)
    overall_r, _ = spearmanr(y[valid], preds[valid])
    return family_results, overall_r


def permutation_test_regression(df, features, n_perm=200, label="rank_delta_igd"):
    """Permutation test: shuffle response, rerun LOOCV, build null distribution.

    Uses n_perm=200 (sufficient for p < 0.005 resolution) with lightweight RF
    (100 trees) for the null distribution to keep runtime feasible.
    """
    _, observed_r, _, _, _ = loocv_regression(df, features, label)
    rng = np.random.RandomState(42)
    null_rs = np.zeros(n_perm)

    df_perm = df.copy()
    print(f"    Permutation test: {n_perm} shuffles...", flush=True)
    for k in range(n_perm):
        if (k + 1) % 50 == 0:
            print(f"      {k + 1}/{n_perm}", flush=True)
        df_perm[label] = rng.permutation(df[label].values)
        _, null_rs[k], _, _, _ = loocv_regression(df_perm, features, label)

    p_value = (np.sum(null_rs >= observed_r) + 1) / (n_perm + 1)
    return observed_r, null_rs, p_value


# ===================================================================
# PART 3: BINARY CLASSIFICATION (SECONDARY ANALYSIS)
# ===================================================================
def loocv_classification(df, features, clf_factory=None):
    """LOOCV for classification. Returns predictions, probabilities, metrics dict."""
    if clf_factory is None:
        clf_factory = lambda: RandomForestClassifier(**RF_CLF_PARAMS)

    X = df[features].values
    y = (df["label_binary"] == "HELPS").astype(int).values
    n = len(y)
    preds = np.zeros(n, dtype=int)

    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[mask])
        X_test = scaler.transform(X[i:i+1])
        clf = clf_factory()
        clf.fit(X_train, y[mask])
        preds[i] = clf.predict(X_test)[0]

    ba = balanced_accuracy_score(y, preds)
    mcc = matthews_corrcoef(y, preds)
    f1_mac = f1_score(y, preds, average="macro")
    prec, rec, f1_per, sup = precision_recall_fscore_support(y, preds, labels=[0, 1])
    cm = confusion_matrix(y, preds, labels=[0, 1])

    # 95% CI for balanced accuracy via exact binomial
    n_correct = int(ba * n)
    ci_lo, ci_hi = _binomial_ci(n_correct, n, alpha=0.05)

    metrics = dict(
        balanced_accuracy=ba,
        mcc=mcc,
        f1_macro=f1_mac,
        precision_NOT_HELPS=prec[0],
        recall_NOT_HELPS=rec[0],
        precision_HELPS=prec[1],
        recall_HELPS=rec[1],
        ci_lo=ci_lo,
        ci_hi=ci_hi,
        confusion_matrix=cm,
    )
    return preds, metrics


def _binomial_ci(k, n, alpha=0.05):
    """Wilson score interval for proportion k/n."""
    from statsmodels.stats.proportion import proportion_confint
    try:
        lo, hi = proportion_confint(k, n, alpha=alpha, method="wilson")
    except Exception:
        # Fallback: normal approx
        p_hat = k / n
        z = 1.96
        se = np.sqrt(p_hat * (1 - p_hat) / n)
        lo, hi = p_hat - z * se, p_hat + z * se
    return lo, hi


def lofo_classification(df, features):
    """Leave-one-family-out CV for classification."""
    X = df[features].values
    y = (df["label_binary"] == "HELPS").astype(int).values
    families = df["family"].values
    unique_families = sorted(set(families))

    preds = np.full(len(y), -1, dtype=int)
    family_results = {}

    for fam in unique_families:
        test_mask = families == fam
        train_mask = ~test_mask
        if test_mask.sum() < 2:
            continue
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[train_mask])
        X_test = scaler.transform(X[test_mask])
        clf = RandomForestClassifier(**RF_CLF_PARAMS)
        clf.fit(X_train, y[train_mask])
        p = clf.predict(X_test)
        preds[test_mask] = p

        ba_fam = balanced_accuracy_score(y[test_mask], p)
        mcc_fam = matthews_corrcoef(y[test_mask], p)
        family_results[fam] = {"balanced_accuracy": ba_fam, "mcc": mcc_fam}

    valid = preds >= 0
    overall_ba = balanced_accuracy_score(y[valid], preds[valid])
    overall_mcc = matthews_corrcoef(y[valid], preds[valid])
    return family_results, overall_ba, overall_mcc


def baseline_classifiers(df, features):
    """Compare alternative classifiers via LOOCV."""
    baselines = {
        "LogisticRegression": lambda: LogisticRegression(
            C=1.0, class_weight="balanced", solver="lbfgs", max_iter=1000
        ),
        "SVC_RBF": lambda: SVC(
            kernel="rbf", class_weight="balanced", probability=True
        ),
        "KNN_5": lambda: KNeighborsClassifier(n_neighbors=5),
    }
    results = {}
    for name, factory in baselines.items():
        _, m = loocv_classification(df, features, clf_factory=factory)
        results[name] = {
            "balanced_accuracy": m["balanced_accuracy"],
            "mcc": m["mcc"],
        }
        print(
            f"    {name}: balanced_acc = {m['balanced_accuracy']:.4f}, "
            f"MCC = {m['mcc']:.4f}"
        )
    return results


def baseline_classifiers_lofo(df, features):
    """Compare alternative classifiers via leave-one-family-out CV."""
    baselines = {
        "LogisticRegression": lambda: LogisticRegression(
            C=1.0, class_weight="balanced", solver="lbfgs", max_iter=1000
        ),
        "SVC_RBF": lambda: SVC(
            kernel="rbf", class_weight="balanced", probability=True
        ),
        "KNN_5": lambda: KNeighborsClassifier(n_neighbors=5),
    }

    X = df[features].values
    y = (df["label_binary"] == "HELPS").astype(int).values
    families = df["family"].values
    unique_families = sorted(set(families))

    results = {}
    for name, factory in baselines.items():
        preds = np.full(len(y), -1, dtype=int)
        for fam in unique_families:
            test_mask = families == fam
            train_mask = ~test_mask
            if test_mask.sum() < 1:
                continue
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[train_mask])
            X_test = scaler.transform(X[test_mask])
            clf = factory()
            clf.fit(X_train, y[train_mask])
            preds[test_mask] = clf.predict(X_test)

        valid = preds >= 0
        ba = balanced_accuracy_score(y[valid], preds[valid])
        mcc = matthews_corrcoef(y[valid], preds[valid])
        results[name] = {"balanced_accuracy": ba, "mcc": mcc}
        print(f"    {name}: balanced_acc = {ba:.4f}, MCC = {mcc:.4f}")

    return results


# ===================================================================
# PART 4: FEATURE IMPORTANCE & INTERPRETATION
# ===================================================================
def plot_permutation_importance(df, features, task="regression"):
    """Fit RF on full data and plot permutation importance."""
    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if task == "regression":
        y = df["rank_delta_igd"].values
        model = RandomForestRegressor(**RF_REG_PARAMS)
    else:
        y = (df["label_binary"] == "HELPS").astype(int).values
        model = RandomForestClassifier(**RF_CLF_PARAMS)

    model.fit(X_scaled, y)

    result = permutation_importance(
        model, X_scaled, y, n_repeats=100, random_state=42,
        scoring="r2" if task == "regression" else "balanced_accuracy",
    )

    sorted_idx = result.importances_mean.argsort()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(
        range(len(features)),
        result.importances_mean[sorted_idx],
        xerr=result.importances_std[sorted_idx],
        color="#4878CF", edgecolor="black", linewidth=0.5,
    )
    ax.set_yticks(range(len(features)))
    ax.set_yticklabels([features[i] for i in sorted_idx])
    ax.set_xlabel("Mean decrease in score")
    ax.set_title(f"Permutation Importance ({task.title()})")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "fla_permutation_importance.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return model, result


def plot_shap_values(df, features):
    """SHAP beeswarm and bar plots for regression and classification."""
    try:
        import shap
    except ImportError:
        print("  [WARN] shap not installed -- skipping SHAP plots.")
        print("         Install with: pip install shap")
        return

    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    feature_names = features

    # --- Regression SHAP ---
    y_reg = df["rank_delta_igd"].values
    rf_reg = RandomForestRegressor(**RF_REG_PARAMS)
    rf_reg.fit(X_scaled, y_reg)
    try:
        explainer_reg = shap.TreeExplainer(rf_reg)
        shap_reg = explainer_reg.shap_values(X_scaled)

        fig, ax = plt.subplots(figsize=(8, 6))
        shap.summary_plot(shap_reg, X_scaled, feature_names=feature_names, show=False)
        plt.title("SHAP Beeswarm -- Regression (rank delta_igd)")
        plt.tight_layout()
        path = os.path.join(FIG_DIR, "fla_shap_regression.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close("all")
        print(f"  Saved: {path}")
    except Exception as e:
        print(f"  [WARN] SHAP regression plot failed: {e}")

    # --- Classification SHAP ---
    y_clf = (df["label_binary"] == "HELPS").astype(int).values
    rf_clf = RandomForestClassifier(**RF_CLF_PARAMS)
    rf_clf.fit(X_scaled, y_clf)
    try:
        explainer_clf = shap.TreeExplainer(rf_clf)
        shap_clf = explainer_clf.shap_values(X_scaled)

        # For binary classification, shap_values returns list of 2 arrays
        if isinstance(shap_clf, list):
            shap_clf_vals = shap_clf[1]  # class=1 (HELPS)
        else:
            shap_clf_vals = shap_clf

        fig, ax = plt.subplots(figsize=(8, 6))
        shap.summary_plot(shap_clf_vals, X_scaled, feature_names=feature_names, show=False)
        plt.title("SHAP Beeswarm -- Classification (HELPS)")
        plt.tight_layout()
        path = os.path.join(FIG_DIR, "fla_shap_classification.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close("all")
        print(f"  Saved: {path}")

        # Bar plot (mean |SHAP|)
        fig, ax = plt.subplots(figsize=(7, 5))
        shap.summary_plot(shap_clf_vals, X_scaled, feature_names=feature_names,
                          plot_type="bar", show=False)
        plt.title("SHAP Mean |value| -- Classification (HELPS)")
        plt.tight_layout()
        path = os.path.join(FIG_DIR, "fla_shap_bar.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close("all")
        print(f"  Saved: {path}")
    except Exception as e:
        print(f"  [WARN] SHAP classification plots failed: {e}")


# ===================================================================
# PART 5: HYPOTHESIS TESTING
# ===================================================================
def test_hypotheses(df):
    """Test 5 specific FLA hypotheses via Spearman correlation."""
    delta = df["delta_igd"].values

    hypotheses = [
        {
            "id": "H_FLA1",
            "feature": "front_diameter",
            "description": "More front clusters (proxy: front_diameter) -> IVF less effective",
            "expected_sign": "negative",
        },
        {
            "id": "H_FLA2",
            "feature": "front_connectivity",
            "description": "Lower front connectivity -> IVF less effective (positive corr expected)",
            "expected_sign": "positive",
        },
        {
            "id": "H_FLA3",
            "feature": "dom_depth_std",
            "description": "Higher conflict (proxy: dom_depth_std, inverse) -> IVF more effective",
            "expected_sign": "negative",
        },
        {
            "id": "H_FLA4",
            "feature": "autocorr_mean",
            "description": "Smoother landscape (higher autocorr) -> IVF more effective",
            "expected_sign": "positive",
        },
        {
            "id": "H_FLA5",
            "feature": "dom_depth_std",
            "description": "Higher non-dominated proportion (proxy: dom_depth_std) -> IVF less impactful",
            "expected_sign": "negative",
        },
    ]

    rows = []
    for h in hypotheses:
        x = df[h["feature"]].values
        r, p = spearmanr(x, delta)
        # Effect size interpretation (|r|)
        abs_r = abs(r)
        if abs_r < 0.1:
            effect = "negligible"
        elif abs_r < 0.3:
            effect = "small"
        elif abs_r < 0.5:
            effect = "medium"
        else:
            effect = "large"

        # Determine support
        observed_sign = "positive" if r > 0 else "negative"
        supported = (observed_sign == h["expected_sign"]) and (p < 0.05)
        conclusion = "SUPPORTED" if supported else "NOT SUPPORTED"
        if p >= 0.05:
            conclusion += " (p >= 0.05)"
        elif observed_sign != h["expected_sign"]:
            conclusion += " (wrong sign)"

        row = {
            "hypothesis": h["id"],
            "feature": h["feature"],
            "description": h["description"],
            "expected_sign": h["expected_sign"],
            "spearman_r": round(r, 4),
            "p_value": round(p, 6),
            "effect_size": effect,
            "conclusion": conclusion,
        }
        rows.append(row)
        print(f"  {h['id']}: r={r:.4f}, p={p:.6f}, effect={effect} -> {conclusion}")

    ht_df = pd.DataFrame(rows)
    path = os.path.join(TAB_DIR, "fla_hypothesis_tests.csv")
    ht_df.to_csv(path, index=False)
    print(f"  Saved: {path}")
    return ht_df


# ===================================================================
# PART 6: SCATTER PLOT
# ===================================================================
def plot_regression_scatter(df, preds_dict):
    """Scatter plot of predicted vs actual rank-delta_igd for each feature set."""
    y = df["rank_delta_igd"].values
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for ax, (name, preds) in zip(axes, preds_dict.items()):
        r, _ = spearmanr(y, preds)
        ax.scatter(y, preds, alpha=0.6, edgecolors="black", linewidth=0.3, s=30)
        # Identity line
        lo, hi = min(y.min(), preds.min()), max(y.max(), preds.max())
        ax.plot([lo, hi], [lo, hi], "k--", alpha=0.4, linewidth=0.8)
        ax.set_xlabel("Actual rank(delta_igd)")
        ax.set_ylabel("Predicted rank(delta_igd)")
        ax.set_title(f"{name}\nSpearman r = {r:.3f}")
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "fla_regression_scatter.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ===================================================================
# MAIN
# ===================================================================
def main():
    print("=" * 70)
    print("FLA PREDICTIVE MODELING PIPELINE")
    print("=" * 70)

    # ------------------------------------------------------------------
    # PART 1
    # ------------------------------------------------------------------
    print("\n--- PART 1: Data Preparation ---")
    df = load_data()

    # ------------------------------------------------------------------
    # Collectors for summary table
    # ------------------------------------------------------------------
    summary_rows = []
    reg_preds = {}

    # ------------------------------------------------------------------
    # PART 2: REGRESSION
    # ------------------------------------------------------------------
    print("\n--- PART 2: Regression (Primary Analysis) ---")
    for set_name, feats in FEATURE_SETS.items():
        print(f"\n  Feature set: {set_name} ({len(feats)} features)")

        # 2a. LOOCV
        print("  [2a] LOOCV RF Regression:")
        preds, r_sp, p_sp, r2, mae = loocv_regression(df, feats)
        print(f"       Spearman r = {r_sp:.4f} (p = {p_sp:.6f})")
        print(f"       R2 = {r2:.4f}, MAE = {mae:.4f}")
        reg_preds[set_name] = preds

        summary_rows.append(dict(
            feature_set=set_name, model="RF_Regression", validation="LOOCV",
            balanced_acc=np.nan, mcc=np.nan,
            spearman_r=round(r_sp, 4), r2=round(r2, 4), mae=round(mae, 4),
        ))

        # 2b. LOFO
        print("  [2b] Leave-One-Family-Out CV:")
        fam_res, overall_r = lofo_regression(df, feats)
        for fam, r in sorted(fam_res.items()):
            print(f"       {fam}: Spearman r = {r:.4f}")
        print(f"       Overall Spearman r = {overall_r:.4f}")

        summary_rows.append(dict(
            feature_set=set_name, model="RF_Regression", validation="LOFO",
            balanced_acc=np.nan, mcc=np.nan,
            spearman_r=round(overall_r, 4), r2=np.nan, mae=np.nan,
        ))

    # 2c. Permutation test (only for SET_ALL -- expensive)
    print("\n  [2c] Permutation test (SET_ALL, 200 permutations) ...")
    obs_r, null_dist, perm_p = permutation_test_regression(df, SET_ALL, n_perm=200)
    print(f"       Observed Spearman r = {obs_r:.4f}")
    print(f"       Permutation p-value = {perm_p:.4f}")
    print(f"       Null distribution: mean={np.mean(null_dist):.4f}, "
          f"std={np.std(null_dist):.4f}, max={np.max(null_dist):.4f}")

    # Scatter plot
    print("\n  Generating regression scatter plot ...")
    plot_regression_scatter(df, reg_preds)

    # ------------------------------------------------------------------
    # PART 3: CLASSIFICATION
    # ------------------------------------------------------------------
    print("\n--- PART 3: Binary Classification (Secondary Analysis) ---")
    majority_baseline = df["label_binary"].value_counts().max() / len(df)
    print(f"  Majority-class baseline accuracy: {majority_baseline:.4f}")

    for set_name, feats in FEATURE_SETS.items():
        print(f"\n  Feature set: {set_name} ({len(feats)} features)")

        # 3a. LOOCV
        print("  [3a] LOOCV RF Classification:")
        preds_clf, m = loocv_classification(df, feats)
        print(f"       Balanced accuracy = {m['balanced_accuracy']:.4f} "
              f"[95% CI: {m['ci_lo']:.3f} - {m['ci_hi']:.3f}]")
        print(f"       MCC = {m['mcc']:.4f}")
        print(f"       F1-macro = {m['f1_macro']:.4f}")
        print(f"       Precision(NOT_HELPS) = {m['precision_NOT_HELPS']:.4f}, "
              f"Recall(NOT_HELPS) = {m['recall_NOT_HELPS']:.4f}")
        print(f"       Precision(HELPS) = {m['precision_HELPS']:.4f}, "
              f"Recall(HELPS) = {m['recall_HELPS']:.4f}")
        print(f"       Confusion matrix:\n{m['confusion_matrix']}")

        summary_rows.append(dict(
            feature_set=set_name, model="RF_Classification", validation="LOOCV",
            balanced_acc=round(m["balanced_accuracy"], 4),
            mcc=round(m["mcc"], 4),
            spearman_r=np.nan, r2=np.nan, mae=np.nan,
        ))

        # 3b. LOFO
        print("  [3b] Leave-One-Family-Out CV:")
        fam_clf, overall_ba, overall_mcc = lofo_classification(df, feats)
        for fam, res in sorted(fam_clf.items()):
            print(f"       {fam}: BA = {res['balanced_accuracy']:.4f}, "
                  f"MCC = {res['mcc']:.4f}")
        print(f"       Overall: BA = {overall_ba:.4f}, MCC = {overall_mcc:.4f}")

        summary_rows.append(dict(
            feature_set=set_name, model="RF_Classification", validation="LOFO",
            balanced_acc=round(overall_ba, 4), mcc=round(overall_mcc, 4),
            spearman_r=np.nan, r2=np.nan, mae=np.nan,
        ))

    # 3c. Alternative classifiers
    print("\n  [3c] Alternative classifiers (SET_ALL, LOOCV):")
    bl_results = baseline_classifiers(df, SET_ALL)
    for name, res in bl_results.items():
        summary_rows.append(dict(
            feature_set="SET_ALL", model=name, validation="LOOCV",
            balanced_acc=round(res["balanced_accuracy"], 4),
            mcc=round(res["mcc"], 4),
            spearman_r=np.nan, r2=np.nan, mae=np.nan,
        ))

    print("\n  [3d] Alternative classifiers (SET_ALL, LOFO):")
    bl_lofo_results = baseline_classifiers_lofo(df, SET_ALL)
    for name, res in bl_lofo_results.items():
        summary_rows.append(dict(
            feature_set="SET_ALL", model=name, validation="LOFO",
            balanced_acc=round(res["balanced_accuracy"], 4),
            mcc=round(res["mcc"], 4),
            spearman_r=np.nan, r2=np.nan, mae=np.nan,
        ))

    # ------------------------------------------------------------------
    # PART 4: FEATURE IMPORTANCE
    # ------------------------------------------------------------------
    print("\n--- PART 4: Feature Importance & Interpretation ---")
    print("  [4a] Permutation importance (regression, SET_ALL) ...")
    plot_permutation_importance(df, SET_ALL, task="regression")

    print("  [4b] SHAP values ...")
    plot_shap_values(df, SET_ALL)

    # ------------------------------------------------------------------
    # PART 5: HYPOTHESIS TESTING
    # ------------------------------------------------------------------
    print("\n--- PART 5: Hypothesis Testing ---")
    test_hypotheses(df)

    # ------------------------------------------------------------------
    # PART 6: SUMMARY TABLE
    # ------------------------------------------------------------------
    print("\n--- PART 6: Output Summary ---")
    summary_df = pd.DataFrame(summary_rows)
    path = os.path.join(TAB_DIR, "fla_model_comparison.csv")
    summary_df.to_csv(path, index=False)
    print(f"  Saved: {path}")
    print("\n  Model comparison table:")
    print(summary_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
