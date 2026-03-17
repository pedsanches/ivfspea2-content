# IVF-SPEA2

Repository for the IVF/SPEA2 manuscript, code, and reproducibility artifacts.

## Reviewer Guide

- Main and only manuscript source: `paper/src/sn-article.tex`
- Main manuscript PDF output: `paper/build/sn-article.pdf`
- Supplement source: `paper/src/ivfspea2_supplementary_tables.tex`
- Algorithm and data knowledge: `docs/IVFSPEA2_KNOWLEDGE_BASE.md`
- Evidence model and claim scope: `docs/IVFSPEA2_EVIDENCE_MODEL.md`
- Human-readable evidence index: `results/SUBMISSION_EVIDENCE_MAP.md`
- Machine-readable release inventory: `results/submission_release_manifest.csv`
- Citation metadata: `CITATION.cff`
- Historical and procedural materials: `archive/`

## Canonical Implementation

- Paper display name: `IVF/SPEA2`
- Canonical class: `IVFSPEA2V2`
- Canonical MATLAB path:
  - `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/`
- Legacy mirror retained only for history:
  - `src/matlab/ivf_spea2/`

For canonical reruns, add only PlatEMO to the MATLAB path and verify:

```matlab
addpath(genpath('src/matlab/lib/PlatEMO'));
which IVFSPEA2V2 -all
```

## Current Default Configuration

| Parameter | Default |
|-----------|---------|
| C | 0.12 |
| R | 0.225 |
| M | 0.3 |
| V | 0.1 |
| Cycles | 2 |

## Reproducing Core Artifacts

### Python setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Canonical synthetic rerun

```matlab
addpath(genpath('src/matlab/lib/PlatEMO'));
run('experiments/run_ivfspea2v2_submission.m');
```

### Tests

```bash
matlab -batch "run('tests/matlab/run_tests.m')"
python3 -m pytest tests/python/ -v
```

### Paper build

```bash
make -C paper
```

## Repository Layout

- `paper/` - manuscript, bibliography, class files, and current figure set
- `docs/` - condensed knowledge docs only
- `src/` - canonical MATLAB implementation and Python analysis code
- `experiments/` - experiment runners and post-processing entry points
- `data/processed/` - processed CSVs and fronts used by the paper
- `results/` - frozen evidence, tables, and machine-readable inventories
- `tests/` - MATLAB and Python regression checks
- `archive/` - historical, superseded, and procedural materials preserved without deletion

## How To Cite

Repository citation metadata is stored in `CITATION.cff` and points to the
frozen release snapshot.

Minimal BibTeX form:

```bibtex
@software{zambrano2026ivfspea2,
  author  = {Zambrano, Pedro Sanches and Souza, Eduardo Faria de and Dantas, Altino and Sampaio, Savio Menezes and Camilo-Junior, Celso G.},
  title   = {IVF-SPEA2},
  version = {submission-snapshot-2026-03},
  year    = {2026},
  url     = {https://github.com/pedsanches/IVF-SPEA2/releases/tag/submission-snapshot-2026-03}
}
```

## Notes

- Procedural records were intentionally moved to `archive/docs-procedural/` and
  `archive/results-procedural/`.
- The visible documentation surface is now limited to condensed knowledge and
  evidence summaries.
- New experiments should preserve both `IGD` and `HV` for every evaluated configuration.

## License

This project uses PlatEMO for research purposes. See PlatEMO's license for details.
