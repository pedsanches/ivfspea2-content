# Merge Diagnostic Report

## Summary

| Algorithm Pair | Runs | Mean Match % | Min Match % | Status |
|---|---|---|---|---|
| IVFSPEA2 vs SPEA2 | 180 | 100.0% | 100.0% | ✅ OK |
| IVFNSGAII vs NSGAII | 180 | 100.0% | 100.0% | ✅ OK |
| IVFNSGAIII vs NSGAIII | 180 | 83.5% | 0.0% | ⚠️ CRITICAL |

## Critical Issue: IVFNSGAIII vs NSGAIII on DTLZ5 (M=3)

All 30 runs show near-zero FE grid overlap (0-3 common points out of 100).

**Root cause**: FE grids are nearly identical but with small per-checkpoint offsets (1-90 FE units). Example run 7001:

| Checkpoint | IVFNSGAIII FE | NSGAIII FE | Offset |
|---|---|---|---|
| 1 | 993 | 991 | 2 |
| 2 | 1985 | 1981 | 4 |
| ... | ... | ... | ... |
| 100 | 100023 | 100081 | 58 |

The offsets accumulate differently because the two algorithms have slightly different per-generation FE consumption patterns, leading to drifted checkpoints.

## Impact on Current Analysis

The current `compute_ratio_stats()` in `plot_hosts_convergence.py` uses exact merge on `(run, FE)`:
```python
merged = base.merge(ivf, on=["run", "FE"], suffixes=("_base", "_ivf"))
```

This means **for DTLZ5 M=3, the IVFNSGAIII vs NSGAIII ratio curve is computed from 0-3 points instead of 100**, making those curves unreliable.

## Recommended Fix

Replace exact FE merge with **interpolation-based alignment**:

```python
def compute_ratio_with_interpolation(ivf_df, base_df):
    """Compute IGD ratio by interpolating base onto IVF's FE grid."""
    ratios_per_run = []
    for run in ivf_df['run'].unique():
        ivf_run = ivf_df[ivf_df['run'] == run].sort_values('FE')
        base_run = base_df[base_df['run'] == run].sort_values('FE')
        # Interpolate base IGD onto IVF's FE grid
        base_interp = np.interp(
            ivf_run['FE'].values,
            base_run['FE'].values,
            base_run['IGD'].values,
        )
        ratio = ivf_run['IGD'].values / base_interp  # or base/ivf
        ratios_per_run.append(pd.DataFrame({'FE': ivf_run['FE'], 'ratio': ratio}))
    return pd.concat(ratios_per_run)
```

Alternatively, use **FE normalization**: round `FE / 1000 * 1000` to align to 1000-FE bins.

## Other Notes

- DTLZ5 M=2 has both IVFNSGAIII and NSGAIII with aligned grids (100% match).
- The issue appears specific to the DTLZ5 M=3 configuration, possibly due to different convergence speeds causing divergent checkpoint spacing in the PlatEMO save mechanism.
