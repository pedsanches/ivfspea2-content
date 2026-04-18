# Phase A Analysis Summary for Phase B Preparation

Generated at: 2026-02-28 00:14:39

## Selected center for Phase B
- ConfigID: `A43`
- R: `0.2`
- C: `0.16`
- Cycles: `2`
- MeanCombinedRank: `0.212766`
- MeanNormRankIGD: `0.210993`
- MeanNormRankHV: `0.214539`

## Top candidates from Phase A

| Rank | ConfigID | R | C | Cycles | MeanCombinedRank | MeanNormRankIGD | MeanNormRankHV |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | A43 | 0.200 | 0.160 | 2 | 0.212766 | 0.210993 | 0.214539 |
| 2 | A39 | 0.200 | 0.070 | 4 | 0.317376 | 0.354610 | 0.280142 |
| 3 | A32 | 0.150 | 0.160 | 3 | 0.350177 | 0.304965 | 0.395390 |
| 4 | A44 | 0.200 | 0.160 | 3 | 0.350177 | 0.382979 | 0.317376 |
| 5 | A41 | 0.200 | 0.110 | 3 | 0.360816 | 0.365248 | 0.356383 |
| 6 | A27 | 0.150 | 0.070 | 4 | 0.366135 | 0.347518 | 0.384752 |
| 7 | A34 | 0.150 | 0.210 | 2 | 0.367021 | 0.430851 | 0.303191 |
| 8 | A29 | 0.150 | 0.110 | 3 | 0.367908 | 0.384752 | 0.351064 |
| 9 | A37 | 0.200 | 0.070 | 2 | 0.381206 | 0.342199 | 0.420213 |
| 10 | A40 | 0.200 | 0.110 | 2 | 0.389184 | 0.462766 | 0.315603 |

## Ready-to-run command (Phase B)
```bash
set -a && source '/home/pedro/desenvolvimento/ivfspea2/results/tuning_ivfspea2v2/phaseB_center_from_phaseA.env' && set +a
LAUNCH_MODE=run V2_TUNE_WORKERS=6 scripts/experiments/launch_ivfspea2v2_tuning.sh B 3
```
