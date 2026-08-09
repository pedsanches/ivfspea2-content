# IVF-SPEA2

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19071253.svg)](https://doi.org/10.5281/zenodo.19071253)

Repository for the IVF/SPEA2 manuscripts, code, and reproducibility artifacts.

## Reviewer Guide

- Primary manuscript source: `paper/springer-nature/src/sn-article.tex`
- Primary manuscript PDF output: `paper/springer-nature/build/sn-article.pdf`
- Supplement source: `paper/springer-nature/src/ivfspea2_supplementary_tables.tex`
- PPSN 2026 (accepted, IVF across hosts): `paper/ppsn2026-ivf-hosts/main.tex`
- PPSN 2026 (population dynamics): `paper/ppsn2026/main.tex`
- CLEI 2026: `paper/clei2026/main.tex`
- Master's dissertation (pt-BR): `thesis/masters/main.tex`
- Algorithm and data knowledge: `docs/IVFSPEA2_KNOWLEDGE_BASE.md`
- Evidence model and claim scope: `docs/IVFSPEA2_EVIDENCE_MODEL.md`
- Human-readable evidence index: `results/SUBMISSION_EVIDENCE_MAP.md`
- Machine-readable release inventory: `results/submission_release_manifest.csv`
- Producer environment: `docs/REPRODUCIBILITY_ENVIRONMENT.md`
- DOI hierarchy and which one to cite: `docs/RELEASE_IDENTITY.md`
- Citation metadata: `CITATION.cff`
- DOI (all versions): [10.5281/zenodo.19071253](https://doi.org/10.5281/zenodo.19071253)

Verify that every artifact this repository claims to ship is actually present and
unmodified:

```bash
make verify-release
```

## Canonical Implementation

- Paper display name: `IVF/SPEA2`
- Canonical class: `IVFSPEA2V2`
- Canonical MATLAB path:
  - `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/`
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
make paper
make paper-ppsn
make paper-all
```

## Repository Layout

- `paper/` - manuscript folders and paper-specific build entrypoints
- `docs/` - condensed knowledge docs only
- `src/` - canonical MATLAB implementation and Python analysis code
- `experiments/` - experiment runners and post-processing entry points
- `data/processed/` - processed CSVs and fronts used by the paper
- `results/` - frozen evidence, tables, and machine-readable inventories
- `tests/` - MATLAB and Python regression checks
- `thesis/masters/` - master's dissertation sources (pt-BR, UFG template)

## How To Cite

Repository citation metadata is stored in `CITATION.cff` and points to the
frozen release snapshot.

Minimal BibTeX form — the concept DOI resolves to the latest version, so it does
not go stale:

```bibtex
@software{zambrano2026ivfspea2,
  author = {Zambrano, Pedro Sanches and Souza, Eduardo Faria de and Dantas, Altino and Sampaio, Savio Menezes and Camilo-Junior, Celso G.},
  title  = {IVF-SPEA2},
  year   = {2026},
  doi    = {10.5281/zenodo.19071253},
  url    = {https://github.com/pedsanches/ivfspea2-content}
}
```

To cite a specific snapshot instead, use its version DOI and state the version
label; `docs/RELEASE_IDENTITY.md` lists all three.

## Notes

- Procedural records are not distributed with the repository. They are recorded
  as `archived_offline` rows in `results/submission_release_manifest.csv`, which
  preserves the trail without shipping workflow history.
- The visible documentation surface is limited to condensed knowledge and
  evidence summaries.
- New experiments should preserve both `IGD` and `HV` for every evaluated configuration.

## License

This project uses PlatEMO for research purposes. See PlatEMO's license for details.
