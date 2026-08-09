# PPSN 2026 Paper Proposal

> **Superseded — the finding inverted this hypothesis.**
>
> This proposal argues for *landscape-aware prediction*: that static fitness-
> landscape features would predict when local intensification helps. The work
> that followed found the opposite. The shipped manuscript is titled *"Early
> Population Dynamics **Outperform** Static Landscape Features for Warmup-Based
> Operator Switching"* (`paper/ppsn2026/main.tex`, and the CLEI variant at
> `paper/clei2026/main.tex`).
>
> The document is kept unedited on purpose. A refuted hypothesis that was
> pre-registered and then overturned by evidence is a result, and rewriting the
> proposal to match the outcome would erase that. Read it as the starting
> position, not as a description of the findings.

## Working Title

**"When Does Local Intensification Help? Landscape-Aware Prediction of Memetic Operator Effectiveness in Multi-Objective Optimization"**

## Research Question

Given a continuous multi-objective optimization problem, can computable fitness
landscape features predict whether a local intensification operator (IVF) will
improve or degrade the performance of an archive-based MOEA (SPEA2)?

## Relationship to Memetic Computing Submission

The Memetic Computing paper (submitted, under review) presents the **design and
empirical validation** of IVF/SPEA2. It documents that IVF improves SPEA2 on
regular Pareto fronts but degrades on disconnected geometries.

This PPSN paper asks a **different question**: not *whether* IVF works, but
*when and why*, answered through fitness landscape analysis. The contributions
are orthogonal:

| Aspect              | Memetic Computing (prior)          | PPSN 2026 (this)                     |
|---------------------|------------------------------------|--------------------------------------|
| Focus               | Operator design & validation       | Landscape characterization & prediction |
| Contribution        | IVF operator + ablation + tuning   | Landscape features + predictive model |
| Novel data          | Algorithm runs (IGD/HV per run)    | Landscape features (computed fresh)  |
| Response variable   | N/A (descriptive study)            | Delta_IGD classified (HELPS/NEUTRAL/HURTS) |
| Methodology         | Wilcoxon tests, A12 effect size    | Feature extraction + classification/regression |

**Reused from prior work (with citation):**
- Performance data (IGD per run) to compute the response variable Delta_IGD
- No other data is reused; all landscape features are computed independently

## Gap in the Literature

- Liefooghe et al. (TEVC 2020, GECCO 2021): landscape-aware prediction for
  selecting between **whole algorithms**, not for activating/deactivating an
  **internal memetic component**
- Deep-ELA (Seiler et al. 2024): learned features for MOO, but no application
  to memetic operator effectiveness
- No prior study uses FLA to predict whether a specific intensification module
  should be activated within a given MOEA

## Proposed Landscape Features

### Group A — Objective Distribution Features
- skewness, kurtosis, coefficient of variation per objective
- Spearman correlation between objectives
- Conflict degree (proportion of pairs with trade-off)

### Group B — Dominance Features
- Proportion of non-dominated points in sample
- Dominance depth (mean, std)
- Sample hypervolume and IGD

### Group C — Front Connectivity Features (MAIN NOVEL CONTRIBUTION)
- Number of clusters in non-dominated front (DBSCAN)
- k-NN graph connectivity of the front
- Graph diameter (longest geodesic distance)
- Gap ratio (largest gap / front span)
- Local curvature variance

### Group D — Local Landscape Features (random walk)
- Autocorrelation per objective (ruggedness)
- Information content
- Neutrality ratio
- Fitness-distance correlation

### Group E — Structural Features (known a priori for benchmarks)
- Number of objectives (M), dimensionality (D)
- Separability, front shape (convex/concave/disconnected)

## Testable Hypotheses

| ID     | Feature              | Prediction                                                |
|--------|----------------------|-----------------------------------------------------------|
| H_FLA1 | front_n_clusters     | More clusters -> IVF less effective                       |
| H_FLA2 | front_connectivity   | Lower connectivity -> IVF less effective                  |
| H_FLA3 | conflict_degree      | Higher conflict -> IVF more effective                     |
| H_FLA4 | autocorr_fi          | Smoother landscape -> IVF more effective                  |
| H_FLA5 | prop_nondominated    | Higher non-dominated proportion -> IVF less impactful     |

## Experimental Design

### Benchmark Instances (n=51)
- ZDT (5, M=2), DTLZ (13, M=2+3), WFG (15, M=2+3), MaF (6, M=3)
- Exclude RWMOP engineering instances (non-standard reference fronts)

### Sampling Protocol
- Latin Hypercube Sampling: 1000 points per instance
- Adaptive random walk: 500 steps (step_size=0.01) per instance
- Platform: pymoo (Python) — independent from PlatEMO/MATLAB

### Response Variable
- Delta_IGD = median(IGD_SPEA2) - median(IGD_IVF/SPEA2)
- Classification: HELPS (Wilcoxon p<0.05, Delta>0), HURTS (p<0.05, Delta<0), NEUTRAL (p>=0.05)
- Source: performance data cited from Memetic Computing paper

### Predictive Models
- **Primary:** Random Forest Classifier (LOOCV, F1-macro)
- **Secondary:** Random Forest Regressor (LOOCV, R2, MAE)
- **Baseline:** Logistic Regression (L2 regularized)
- **Interpretation:** Permutation importance + SHAP values

### Validation
- Leave-One-Out Cross-Validation (LOOCV) — required given n=51
- Stratified by class for classification
- Report confidence intervals

## Success Criteria

The paper is publishable if at least one holds:

1. **Strong positive:** F1-macro > 0.6 via LOOCV -> predictive model works
2. **Moderate positive:** Significant Spearman correlation (p<0.05, corrected)
   for >=3 features vs Delta_IGD -> individual features are informative
3. **Informative negative:** Standard FLA features do NOT predict IVF effectiveness
   -> evidence that operator-landscape interaction requires more sophisticated
   features (motivates future Deep-ELA for MOO)

## Paper Structure (14 pages LNCS)

```
1. Introduction                                     (~1.5 pages)
2. Background and Related Work                      (~2 pages)
   2.1 Multi-Objective Fitness Landscape Analysis
   2.2 Memetic Operators in MOEAs
   2.3 IVF/SPEA2 (brief, citing Memetic Computing)
3. Proposed Landscape Features                      (~2 pages)
   3.1 Standard MO Features (Groups A, B, D)
   3.2 Front Connectivity Features (Group C)
   3.3 Structural Features (Group E)
4. Experimental Methodology                         (~2 pages)
   4.1 Benchmark Instances and Performance Data
   4.2 Sampling Protocol
   4.3 Response Variable Construction
   4.4 Predictive Models and Validation
5. Results                                          (~3 pages)
   5.1 Feature-Performance Correlations
   5.2 Classification Accuracy (LOOCV)
   5.3 Feature Importance and Interpretation
   5.4 Hypothesis Testing (H_FLA1-H_FLA5)
6. Discussion                                       (~2 pages)
7. Conclusion                                       (~1 page)
References                                          (no limit)
```

## New Code (to be developed)

```
src/python/fla/
├── sample_landscapes.py      # LHS + random walk via pymoo
├── extract_features.py       # Compute ~25 features (Groups A-E)
├── compute_response.py       # Delta_IGD + classification from existing CSV
├── build_dataset.py          # Merge features + labels
├── analyze_correlations.py   # Spearman, heatmaps, scatter plots
├── train_models.py           # RF classifier/regressor, LOOCV, SHAP
└── generate_figures.py       # Figures for the paper
```

## New Dependencies

```
pymoo>=0.6          # MOO benchmark functions (evaluation only)
shap>=0.42          # SHAP values for interpretation
```

## Execution Timeline

| Day   | Task                                                     |
|-------|----------------------------------------------------------|
| 1-2   | Feature extraction infrastructure (pymoo + extractors)   |
| 3     | Compute features for 51 instances + response variable    |
| 4     | Exploratory analysis (correlations, heatmaps, boxplots)  |
| 5     | Predictive modeling (RF, LOOCV, SHAP, hypothesis tests)  |
| 6-7   | Write paper (LNCS template, tables, figures)             |
| 8     | Review, supplementary on Zenodo, submit                  |

## Risks and Mitigations

| Risk                              | Prob. | Impact | Mitigation                                        |
|-----------------------------------|-------|--------|---------------------------------------------------|
| n=51 insufficient for complex ML  | High  | Medium | LOOCV + simple models; emphasize correlation analysis over accuracy |
| Connectivity features don't discriminate | Medium | High | Keep standard features (Groups A,B,D) as fallback; partial contribution still valid |
| Imbalanced classes (majority HELPS) | High | Medium | F1-macro, stratified LOOCV; consider binary HELPS vs NOT-HELPS |
| Perceived conflict with Memetic Computing | Low | High | Cite explicitly; emphasize orthogonal contribution (FLA, not operator design) |
