# Operator-Host Compatibility of IVF — PPSN 2026

**Accepted**, PPSN 2026. Camera-ready tagged `ppsn2026` (2026-06-12).

Pedro Sanches Zambrano, Eduardo Faria de Souza, Altino Dantas,
Celso G. Camilo-Junior — Institute of Informatics, Federal University of Goiás.

Artifact DOI: [10.5281/zenodo.20672828](https://doi.org/10.5281/zenodo.20672828)

## Building

```bash
cd paper && make ppsn-hosts     # or, from the root: make paper-hosts
```

## This manuscript regenerates its own evidence

Alone among the four, this build rebuilds what it cites. The `assets` target
runs, in order:

```
build_hosts_paper_csv.py          → data/processed/hosts_paper.csv
compute_hosts_tables.py           → results/tables/hosts_*_stats.csv
build_hosts_rep_endpoint_table.py → results/tables/hosts_rep_endpoint_igd.tex
compute_hosts_geometry_stratified.py
plot_hosts_results.py             → figures/hosts_fig{1..4}*.pdf
select_convergence_instances.py
plot_hosts_figures_v2.py          → figures/hosts_v2_fig*.pdf
```

then chains into `make analysis-convergence` when the convergence `.mat` files
exist under `src/matlab/lib/PlatEMO/Data/`. Without them that stage is skipped
with a message, and the committed convergence figures stand.

`main.tex` reaches outside this directory for three tables, which is why they
must exist before LaTeX runs:

```
../../results/tables/hosts_a12_summary.tex
../../results/tables/hosts_geometry_summary.tex
../../results/tables/hosts_rep_endpoint_igd.tex
```

### Why `clean` does not remove the figures

`build/.assets.stamp` tracks the upstream **scripts and inputs** only. The
figures under `figures/` and the tables under `results/tables/` are versioned
deliverables — committed, cited, and part of the deposit — so `make clean`
removes only `build/`. Use `make clean-assets` to delete the generated outputs
deliberately.

### Rebuilds must be byte-identical

Because the outputs are committed, any rebuild that changes a byte appears as a
diff. `figure_io.save_figure` suppresses the PDF `CreationDate` so repeated runs
match, but the `Creator` key carries the matplotlib version: **every figure here
was written by matplotlib 3.10.8**, and any other version rewrites all of them
while changing no plotted number.

The CI job `assets-reproducible` enforces this by running `make assets` and
requiring `git diff --exit-code`. See `docs/REPRODUCIBILITY_ENVIRONMENT.md`.

## Scope note on RWMOP

The hosts pipeline **excludes RWMOP9 by design** — `build_hosts_paper_csv.py`
filters it out, and the analysis covers 51 synthetic instances over DTLZ, MaF,
WFG and ZDT. Nothing in this manuscript reports an RWMOP stratum.

## Related material

| Path | What |
|---|---|
| `../../artifact/ppsn2026-ivf-hosts-rev1/` | The deposited artifact, frozen. Do not edit — see `artifact/README.md` |
| `../../docs/history/2026-ppsn-hosts-revision-plan.md` | Revision plan (pt-BR), formerly `plan.md` here |
| `../../docs/history/superpowers/plans/2026-04-17-ppsn2026-ivf-hosts-reviewer-revision.md` | Reviewer-revision design record |
| `../../docs/reviews/ppsn2026-final/` | Reviews, punchlist and camera-ready change summary |
