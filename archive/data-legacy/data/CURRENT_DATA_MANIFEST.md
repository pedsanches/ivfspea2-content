# Current Data Manifest

This repository now uses a single canonical algorithm label for the current IVF line:

- `IVFSPEA2` (no `V2` suffix)

## Canonical Sources (current)

- Synthetic canonical raw runs: `src/matlab/lib/PlatEMO/Data/IVFSPEA2/`
- Processed consolidated metrics: `data/processed/todas_metricas_consolidado.csv`
- Processed consolidated metrics (with modern baselines): `data/processed/todas_metricas_consolidado_with_modern.csv`

## Legacy Sources (archived)

- Legacy PlatEMO IVF parameter sweeps and old tracks: `src/matlab/lib/PlatEMO/Data/legacy/`
- Legacy auxiliary experiment folders: `data/legacy/`
  - `data/legacy/engineering/`
  - `data/legacy/engineering_suite/`
  - `data/legacy/engineering_screening/`
  - `data/legacy/engineering_probe/`
  - `data/legacy/tuning_ivfspea2v2/`
  - `data/legacy/ablation_v2/`
  - `data/legacy/temp/`

## Naming Policy

- Current pipeline must read/write algorithm key `IVFSPEA2`.
- `IVFSPEA2V2` is treated as legacy naming and should not be used for new outputs.
