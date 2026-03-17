# IVF/SPEA2 v2 — Hypotheses, Rationale, and Ablation Plan

**Created:** 2026-02-25  
**Authors:** Pedro Sanches  
**Status:** Pre-experiment design (registered before execution)

---

## 1. Context and Motivation

IVF/SPEA2 v1 (current paper version) demonstrates statistically significant improvements over canonical SPEA2 on the majority of synthetic benchmark instances (16/0/12 for M=2; 15/2/6 for M=3 under unadjusted Wilcoxon). However, a critical mechanistic analysis of the IVF process identified five structural weaknesses that limit performance, particularly on irregular Pareto front geometries (disconnected, convex-inverted, biased).

The existing ablation study (top-2c vs. 1c/4c/DOM) revealed that performance is **largely insensitive** to the father pool size multiplier, with the only significant difference appearing on WFG2 (M=3, disconnected front). This insensitivity itself is an important finding: it suggests that the **real bottleneck is not pool size but the father-mother pairing mechanism**.

This document formalizes the hypotheses derived from the mechanistic analysis and defines a rigorous ablation study to test them.

---

## 2. Identified Weaknesses and Corresponding Hypotheses

### H1: Inbreeding Structural Bias (Single Father)

**Weakness:** In the current design, a single father is selected per generation and crosses with ALL mothers (lines 60–64, 121 of `IVF.m`). This means:
- All offspring share 50% of their genetic material (from the father)
- Offspring form a correlated cluster in decision space around the father
- SPEA2's density estimator D(i) penalizes these correlated offspring against each other
- Environmental selection eliminates most IVF offspring precisely because they are too similar

**Evidence from data:**
- Section 6.4 of the paper explicitly identifies "interaction between IVF-generated offspring density and SPEA2's truncation mechanism" as the primary failure mode
- On DTLZ4 (M=3), the median IGD is 10× worse than SPEA2 despite a statistical tie (bimodal run behavior)
- On WFG2 (M=3), locally concentrated offspring fall between disconnected segments

**Hypothesis H1:** Selecting a **different father per mother**, chosen to maximize objective-space distance from the mother, will reduce offspring correlation, decrease density-based mutual penalization, and improve performance on irregular fronts without degrading performance on regular fronts.

**Implementation:** For each mother m_i:
1. Candidate pool = all non-dominated individuals in current population
2. Compute Euclidean distance d(m_i, j) in objective space for each candidate j
3. Select top-3 most distant candidates
4. Choose father via binary tournament (by SPEA2 fitness) among these 3

**Rationale for binary tournament:** Pure argmax-distance could select a poorly converged outlier. The tournament balances diversity (distance) with quality (fitness).

---

### H2: Myopic Cycle Continuation Criterion

**Weakness:** The cycle continuation criterion (lines 228–232 of Algorithm 1, lines 182–210 of `IVF.m`) compares the **single best surviving offspring** against the current father. This ignores:
- Whether multiple offspring survived (collective improvement)
- Whether the population as a whole improved
- That SPEA2 fitness F(i) is non-stationary (changes with every environmental selection because D(i) depends on population composition)

**Evidence from data:**
- DTLZ4 (M=3) has IQR of 48.68e-2. This extreme dispersion suggests some runs trigger many unproductive IVF cycles while others converge well—the single-individual criterion fails to distinguish between these regimes.
- On regular fronts (ZDT1, DTLZ2), the criterion works fine because improvements are steady and predictable.

**Hypothesis H2:** A cycle continuation criterion based on **average population fitness improvement** (before vs. after the IVF cycle) will better capture collective benefit, terminate unproductive cycles earlier in failure cases, and allow productive cycles to continue longer.

**Implementation:** 
```matlab
avg_fitness_before = mean(PopFitness_before_cycle);
avg_fitness_after  = mean(PopComparacaoFitness);
if avg_fitness_after < avg_fitness_before
    % Continue: population improved collectively
else
    break; % Terminate: no collective improvement
end
```

---

### H3: Overly Conservative SBX Distribution Index

**Weakness:** SBX with η_c = 20 (line 285 of `IVF.m`) generates offspring extremely close to parents in decision space. The probability of generating an offspring more than 10% of the parent distance away is <5%. This is appropriate for fine-grained local search but prevents IVF from exploring meaningfully different regions.

**Evidence from data:**
- On regular fronts, η_c = 20 works because small perturbations around good parents are sufficient
- On WFG2 (disconnected), offspring from two parents in the same segment NEVER reach other segments because η_c = 20 confines them
- This explains why ABL-DOM helped on WFG2: it occasionally selects parents from different segments, but even then η_c = 20 limits the reach

**Hypothesis H3:** Reducing η_c from 20 to 10 will increase offspring spread, enabling IVF to explore intermediate regions between diverse parents (especially beneficial when combined with H1's dissimilar father selection).

**Note:** η_c = 10 is the default SBX distribution index in NSGA-II and other standard MOEAs. The current η_c = 20 is more conservative than the community standard.

---

### H4: Budget-Based vs. Need-Based Activation

**Weakness:** IVF activation (line 41 of `IVF.m`) is purely budget-driven: `IVF_Total_FE > ivf_rate * Problem.FE`. It does not consider whether the population is currently stagnating (where IVF would help) or actively improving (where IVF would waste evaluations).

**Evidence from data:**
- Early generations show rapid convergence where canonical SPEA2 is naturally effective; IVF at this stage may be counterproductive
- Late generations often show stagnation where IVF intensification would be most valuable, but the budget may already be exhausted

**Hypothesis H4:** Activating IVF only when population fitness **stagnation is detected** (no improvement in avg fitness over a window of k=5 generations) will concentrate IVF evaluations where they are most needed, improving efficiency.

**Implementation:**
```matlab
% Track average fitness history
fitness_history(SPEA2_Gen) = mean(Fitness);
if SPEA2_Gen > 5
    recent_improvement = fitness_history(SPEA2_Gen-5) - fitness_history(SPEA2_Gen);
    if recent_improvement < 1e-6  % Stagnation detected
        % Activate IVF (subject to remaining budget)
    end
end
```

**Caveat:** This is the most speculative hypothesis. The interaction with the budget parameter r is complex, and the stagnation threshold is a new hyperparameter. We test it for completeness but expect it may require more tuning than the other factors.

---

### H5: Missing Post-SBX Mutation

**Weakness:** IVF offspring receive NO mutation after SBX crossover (line 196 of the paper, confirmed in `IVF_Recombination` function). Standard MOEA practice (NSGA-II, SPEA2's own GA operators) always applies polynomial mutation after crossover to ensure offspring can escape the convex hull of the parents.

**Evidence from data:**
- This contributes to the clustering effect described in H1: offspring are strictly confined to the SBX interpolation domain between father and mother
- On problems with coupled decision variables (WFG, MaF), this prevents offspring from exploring regions inaccessible via crossover alone

**Hypothesis H5:** Applying standard polynomial mutation (p_m = 1/D, η_m = 20) to IVF offspring after SBX crossover will increase exploration without fundamentally altering the IVF intensification mechanism.

**Implementation:** Add post-SBX mutation in `IVF_Recombination`:
```matlab
% After SBX crossover, apply polynomial mutation
Offspring = PolyMutate(Offspring, Problem.lower, Problem.upper, 1/D, 20);
```

---

## 3. Factor Interaction Analysis

| Factor Pair | Expected Interaction |
|---|---|
| H1 + H3 | **Strong synergy:** Dissimilar fathers (H1) create wider parent distances; lower η_c (H3) allows offspring to fill the gap. Together they enable directed exploration between diverse regions. |
| H1 + H5 | **Mild synergy:** Mutation (H5) adds random perturbation on top of H1's directed diversity. |
| H3 + H5 | **Potential redundancy:** Both increase offspring spread. Need to verify they don't over-explore and degrade convergence. |
| H2 + H1 | **Complementary:** H1 generates diverse offspring; H2 evaluates their collective contribution rather than judging by a single individual. |
| H4 + all | **Orthogonal:** Activation timing is independent of the offspring generation mechanism. |

---

## 4. Experimental Design

### 4.1 Phase 1: Screening (Add-One-In)

**Objective:** Identify which individual factors improve over the v1 baseline.

**Configurations (6 variants):**

| ID | H1 | H2 | H3 | H4 | H5 | Description |
|----|----|----|----|----|----|----|
| **B** | — | — | — | — | — | IVF/SPEA2 v1 (current, 2c, η_c=20) |
| **V1** | ✓ | — | — | — | — | Dissimilar father per mother |
| **V2** | — | ✓ | — | — | — | Collective continuation criterion |
| **V3** | — | — | ✓ | — | — | η_c = 10 instead of 20 |
| **V4** | — | — | — | ✓ | — | Stagnation-based activation |
| **V5** | — | — | — | — | ✓ | Post-SBX polynomial mutation |

**Benchmark instances (12):**

| Instance | M | Front Type | Role |
|----------|---|-----------|------|
| ZDT1 | 2 | Convex continuous | Positive control |
| ZDT6 | 2 | Concave non-uniform | Regression guard |
| WFG4 | 2 | Concave multimodal | ABL-DOM regressed here |
| WFG9 | 2 | Concave non-separable | Mixed case |
| DTLZ1 | 3 | Linear | Positive control M=3 |
| DTLZ2 | 3 | Spherical regular | Positive control M=3 |
| DTLZ4 | 3 | Spherical biased | **Failure case** (10× worse median) |
| DTLZ7 | 3 | Disconnected | Marginal IVF win |
| WFG2 | 3 | Disconnected non-sep. | **Failure case** in v1 ablation |
| WFG5 | 3 | Concave degenerate | IVF success case |
| MaF1 | 3 | Linear inverted | Diversity test |
| MaF5 | 3 | Convex-inverted | **Failure case** (huge IQR) |

**Runs per config:** 30 (sufficient for Wilcoxon at α=0.05)

**Core metrics (all phases):** Every configuration–instance–run must at least compute and store both **IGD** and **HV**; any new IVF/SPEA2 experiment should treat IGD and HV as mandatory baseline metrics.

**Total Phase 1:** 6 × 12 × 30 = **2,160 runs**

**Promotion criterion:** A factor is promoted to Phase 2 if it:
- Achieves at least 1 significant win ($p < 0.05$) with 0 significant losses, OR
- Shows consistent median improvement in ≥ 7/12 instances (trend signal)

### 4.2 Phase 2: Factorial Combination (Promoted Factors Only)

Full $2^k$ factorial of promoted factors, with 60 runs on the same 12 instances.
Analysis: Friedman ANOVA for global ranking + pairwise Wilcoxon.

### 4.3 Phase 3: Full-Suite Validation

Winner from Phase 2 vs. baseline on all 51 instances, 60 runs, Holm–Bonferroni (with both IGD and HV recorded for each configuration–problem pair).

---

## 5. Parallelization Strategy

**Constraint:** 3 parallel MATLAB processes, each with 6 parpool workers (18 cores total).

**Phase 1 workload:** 6 configs × 12 instances = 72 config-instance pairs × 30 runs each

**Split into 3 balanced batches (24 pairs each):**

- **Batch A (Process 1):** Configs B and V1, all 12 instances → 24 pairs
- **Batch B (Process 2):** Configs V2 and V3, all 12 instances → 24 pairs  
- **Batch C (Process 3):** Configs V4 and V5, all 12 instances → 24 pairs

Each batch runs 24 × 30 = 720 evaluations with 6 workers.

---

## 6. Success Criteria

The v2 ablation is considered successful if the winning configuration:
1. Eliminates or reduces the DTLZ4 (M=3) anomaly (median within 2× of SPEA2 baseline)
2. Improves or neutralizes WFG2 (M=3) degradation
3. Maintains or improves all v1 success cases (zero new regressions on regular fronts)
4. Achieves ≥ 16/0/12 win/loss/tie against SPEA2 on M=2 (same or better than v1)

---

## 7. Risk Assessment

| Risk | Mitigation |
|---|---|
| H1 selects poorly converged distant fathers | Binary tournament among top-3 filters by fitness |
| H3 (lower η_c) degrades convergence on easy problems | Screening phase detects regressions before combination |
| H4 stagnation threshold is problem-dependent | Conservative default (k=5 generations); test as standalone |
| Combined changes interact negatively | Factorial Phase 2 captures pairwise interactions |
| Overfitting to 12 screening instances | Phase 3 validates on full 51-instance suite |

---

## 8. File Organization

```
data/ablation_v2/
├── phase1/
│   ├── B_ZDT1_M2/           # 30 .mat files
│   ├── V1_ZDT1_M2/
│   ├── ...
│   └── V5_MaF5_M3/
├── phase2/                   # Created after Phase 1 analysis
└── phase3/                   # Created after Phase 2 analysis

scripts/experiments/
├── run_ablation_v2_batch_A.m  # B + V1 (12 instances each)
├── run_ablation_v2_batch_B.m  # V2 + V3
├── run_ablation_v2_batch_C.m  # V4 + V5
└── analyze_ablation_v2.m     # Post-experiment analysis

src/matlab/ivf_spea2/
├── IVF.m                     # Current (unchanged, used by B)
├── IVF_V1_DISSIMILAR.m       # H1: dissimilar father
├── IVF_V2_COLLECTIVE.m       # H2: collective criterion
├── IVF_V3_ETA10.m            # H3: η_c = 10
├── IVF_V4_ADAPTIVE.m         # H4: stagnation trigger
└── IVF_V5_MUTATION.m         # H5: post-SBX mutation
```

---

## 9. Conclusions (Post-Experiment)

**Date:** 2026-02-27

### Phase 1 Results

All 5 factors were screened against the v1 baseline on 12 instances (30 runs each). Promotion decisions:

| Factor | W/T/L | Median Improvements | Promoted? |
|--------|-------|---------------------|-----------|
| H1 (dissimilar father) | 2/10/0 | 6/12 | **Yes** (Criterion A: 2W, 0L) |
| H2 (collective criterion) | 2/9/1 | 7/12 | **Yes** (Criterion B: 7/12 trend) |
| H3 (η_c = 10) | 2/10/0 | 8/12 | **Yes** (Criteria A+B) |
| H4 (adaptive activation) | 4/8/0 | 7/12 | **Yes** (Criteria A+B, strongest) |
| H5 (post-SBX mutation) | 2/9/1 | 6/12 | **No** (1 loss, only 6/12 trend) |

### Phase 2 Results

Full 2^4 factorial (16 configs) on 12 instances, 60 runs each:

- **Friedman χ² = 14.54, p = 0.485** — not globally significant
- **Winner:** H1+H2 (avg rank 6.08)
- **Runner-up:** H3+H4 (avg rank 6.17)
- **Key interaction:** H1×H2 synergy (+1.042) — individually marginal, together best
- **Anti-pattern:** H1×H3 (-2.208) and H2×H3 (-2.167) strong antagonism — combining diversity (H1/H2) with wider SBX (H3) over-explores
- No pairwise comparison was significant after Holm correction

### Phase 3 Results

Winner (H1+H2) vs baselines on full 51-instance suite, 60 runs each:

| Metric | vs SPEA2 | vs IVF/SPEA2 v1 |
|--------|----------|------------------|
| IGD | **25W / 25T / 1L** | 0W / 50T / 1L |
| HV | **28W / 21T / 2L** | 0W / 50T / 1L |

### Success Criteria Evaluation

| Criterion | Target | Result |
|-----------|--------|--------|
| 1. DTLZ4(M=3) anomaly | Median within 2× of SPEA2 | **PASS** (ratio = 1.00×) |
| 2. WFG2(M=3) degradation | Neutralize | **FAIL** (1 significant IGD loss persists) |
| 3. Zero new regressions | 0 losses vs SPEA2 | **REVIEW** (1 loss: WFG2 M=3) |
| 4. Win count ≥ 16 | ≥ 16W vs SPEA2 | **PASS** (25W) |

### Final Decision

**H1+H2 consolidated as IVF/SPEA2 v2** at `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/` (class: `IVFSPEA2V2`). The v1 implementation is preserved unchanged at `IVF-SPEA2/`.

See `docs/IVF_V2_CONSOLIDATION.md` for full consolidation details.
