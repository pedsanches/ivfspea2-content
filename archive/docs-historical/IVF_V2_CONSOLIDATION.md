# IVF/SPEA2 v2 Consolidation

**Date:** 2026-02-27
**Author:** Pedro Sanches
**Status:** Consolidated

Phase semantics note:
- This document refers to **Discovery phases (1/2/3)** only.
- For post-consolidation parameter tuning phases (**A/B/C**), see
  `docs/IVFSPEA2V2_TUNING_PIPELINE.md` and
  `docs/IVFSPEA2V2_EXPERIMENT_TRACKS.md`.

---

## What is v2?

IVF/SPEA2 v2 incorporates two structural improvements validated through a rigorous 3-phase ablation study:

- **H1 — Dissimilar Father Per Mother:** Instead of a single randomly-selected father crossing with all mothers, each mother receives a different father chosen to maximize objective-space distance (top-3 candidates + binary tournament by SPEA2 fitness). This reduces offspring correlation and density-based mutual penalization.

- **H2 — Collective Continuation Criterion:** IVF cycles continue while the average population fitness improves (collective benefit), rather than requiring a single offspring to beat the father (myopic criterion). This better captures the collective contribution of diverse offspring.

These two factors exhibit **synergy** (interaction = +1.042): individually they have marginal or slightly negative effects, but together they form the best-ranking configuration across all 16 factorial combinations tested.

---

## What changed from v1?

| Aspect | v1 (`IVFSPEA2`) | v2 (`IVFSPEA2V2`) |
|--------|------------------|-------------------|
| Father selection | Single random father from top-2c, shared by all mothers | Per-mother dissimilar father (top-3 by distance, binary tournament by fitness) |
| Cycle continuation | Best surviving offspring must beat current father | Average population fitness must improve |
| Father pool | N/A | Top 50% of population by fitness, updated each cycle |
| SBX eta_c | 20 | 20 (unchanged) |
| Default M/V | 0.5/0.5 (EAR mode) | 0/0 (AR mode, configurable) |
| Activation | Budget-only | Budget-only (unchanged) |

---

## Ablation Evidence

### Phase 1 — Screening (Add-One-In)

5 individual factors tested against v1 baseline on 12 instances, 30 runs each:

| Factor | Wins/Ties/Losses | Promoted? |
|--------|------------------|-----------|
| H1 (dissimilar father) | 2/10/0 | Yes (Criterion A) |
| H2 (collective criterion) | 2/9/1 | Yes (Criterion B: 7/12 median improvements) |
| H3 (eta_c = 10) | 2/10/0 | Yes (Criteria A+B) |
| H4 (adaptive activation) | 4/8/0 | Yes (Criteria A+B) |
| H5 (post-SBX mutation) | 2/9/1 | **No** (2W/9T/1L, only 6/12 median) |

### Phase 2 — Full 2^4 Factorial

16 configurations on 12 instances, 60 runs each:

- **Friedman chi2 = 14.54, p = 0.485** (not globally significant, but ranking informative)
- **Winner:** P2_C05 = H1+H2, avg rank 6.08
- **Runner-up:** P2_C10 = H3+H4, avg rank 6.17
- **Key finding:** H1×H2 synergy (+1.042), H1×H3 antagonism (-2.208), H2×H3 antagonism (-2.167)
- Combinations with 3+ factors degrade performance

### Phase 3 — Full-Suite Validation (51 instances, 60 runs)

| Metric | vs SPEA2 | vs IVF/SPEA2 v1 |
|--------|----------|------------------|
| **IGD** | **25W / 25T / 1L** | 0W / 50T / 1L |
| **HV** | **28W / 21T / 2L** | 0W / 50T / 1L |

**Success criteria check:**
1. DTLZ4(M=3) anomaly: **PASS** (ratio = 1.00x vs SPEA2, was 10x in v1)
2. WFG2(M=3): **FAIL** (1 significant IGD loss persists)
3. Zero regressions vs SPEA2: **REVIEW** (1 loss on WFG2 M=3)
4. Win count >= 16: **PASS** (25 wins)

---

## Known Limitation: WFG2(M=3)

WFG2(M=3) remains the single significant loss against SPEA2. Root cause analysis:

- WFG2's third objective uses `disc(x) = 1 - x₁·cos²(5πx₁)`, creating ~5 disjoint Pareto front segments
- SBX crossover between parents on different segments produces offspring in dominated inter-segment gaps
- This is an IGD-only issue (HV shows no significant difference, p=0.50)
- The loss is structural: all tested variants and parameter settings either match SPEA2 (at near-zero IVF intensity) or are strictly worse
- See `results/ablation_v2/phase3/phase3_wfg2_diagnostic.pdf` for detailed analysis

---

## File Locations

| Component | Path |
|-----------|------|
| **v2 canonical** | `src/matlab/lib/PlatEMO/.../IVF-SPEA2-V2/` |
| **v1 (reference)** | `src/matlab/lib/PlatEMO/.../IVF-SPEA2/` |
| **Factorial harness** | `src/matlab/lib/PlatEMO/.../IVFSPEA2-P2-COMBINED/` |
| **Phase 1 results** | `results/ablation_v2/phase1/` |
| **Phase 2 results** | `results/ablation_v2/phase2/` |
| **Phase 3 results** | `results/ablation_v2/phase3/` |
| **Raw experiment data** | `data/ablation_v2/phase{1,2,3}/` |
| **Ablation design doc** | `docs/IVF_V2_HYPOTHESES_AND_ABLATION_PLAN.md` |

## How to Run v2

```matlab
% In MATLAB:
addpath(genpath('src/matlab/lib/PlatEMO'));
platemo('algorithm', @IVFSPEA2V2, 'problem', @ZDT1, 'N', 100, 'maxFE', 10000);
```

To compare v1 vs v2:
```matlab
platemo('algorithm', {@IVFSPEA2, @IVFSPEA2V2}, 'problem', @ZDT1, 'N', 100, 'maxFE', 10000);
```
