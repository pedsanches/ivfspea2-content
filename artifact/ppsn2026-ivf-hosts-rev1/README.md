# PPSN 2026 - Operator-Host Compatibility for IVF Intensification
## Reproducibility Artifact (rev1)

This archive accompanies the paper:
> Pedro Sanches Zambrano. *Operator-Host Compatibility in Multi-Objective
> Intensification: IVF Across SPEA2, NSGA-II, and NSGA-III.* PPSN 2026.

## Contents

- `data/hosts_paper.csv` - per-run endpoint metrics (IGD, HV) for the 51 synthetic benchmark instances, three IVF variants, three base hosts, 30 runs each.
- `data/hosts_convergence.csv` - per-checkpoint trajectories for the dynamic block.
- `tables/hosts_*.tex`, `tables/hosts_*.csv` - LaTeX and CSV forms of the tables, median/IQR summaries, pairing robustness results, geometry summaries, FE-accounting diagnostics, and dynamic aggregates reported or archived by the paper.
- `figures/*.pdf` - final figure PDFs as they appear in the paper (Fig. 1-5).
- `scripts/*.py` - Python analysis and figure-generation scripts. The main entry points are `build_hosts_paper_csv.py` (rebuilds the endpoint CSV from raw `.mat` files, not included here due to size), `compute_hosts_tables.py` (recreates the LaTeX/CSV summaries), and `plot_hosts_figures_v2.py` (regenerates Fig. 1-3 from `hosts_paper.csv`).

## Reproducing the summaries

With Python 3.11+ and the dependencies in `scripts/requirements.txt`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/compute_hosts_tables.py
python scripts/plot_hosts_figures_v2.py
python scripts/plot_hosts_convergence_v2.py
```

All tables and figures in the paper are produced deterministically from `data/hosts_paper.csv` (endpoint) and `data/hosts_convergence.csv` (dynamic).

## Raw MATLAB runs

The raw `.mat` traces (runs 3001-3030 IVF/SPEA2, 4001-4030 NSGA-II/IVF-NSGA-II, 5001-5030 NSGA-III/IVF-NSGA-III) are not included because of file-size constraints. They are available on request from the corresponding author and can be archived under the same Zenodo record family.

## Citation

If you use this artifact, please cite the paper and the Zenodo record minted for this archive.

## License

Code: MIT. Data: CC-BY-4.0.
