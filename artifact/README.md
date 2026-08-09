# Artifact provenance ledger

What each item here is, which Zenodo version it belongs to, and what may be
edited. The short version: **nothing under `ppsn2026-ivf-hosts-rev1/` may be
edited**, because those bytes are the deposit.

## Contents

| Item | What it is | Editable? |
|---|---|---|
| `ppsn2026-ivf-hosts-rev1/` | Unpacked contents of the artifact deposited as Zenodo version `v1.0.2` (`10.5281/zenodo.19637623`, 2026-04-18) | **No** — deposited bytes |
| `ppsn2026-ivf-hosts-rev1.zip` | The deposited archive itself, ~20 MB | **No** — deposited bytes |
| `github-release-notes.md` | Release notes for `v1.0.2`, with a forward-pointing banner | Banner only |
| `clei2026-release-notes.md` | Release notes for the CLEI 2026 submission snapshot | Yes |
| `zenodo-metadata.json` | Draft upload metadata (see below) | Yes, as a draft |

## Why the duplicated files are deliberate

Two pairs of files are byte-identical copies, and **neither should be
deduplicated**:

- `ppsn2026-ivf-hosts-rev1/data/hosts_convergence.csv` duplicates
  `data/processed/hosts_convergence.csv`.
- `ppsn2026-ivf-hosts-rev1/scripts/*.py` duplicate scripts in
  `src/python/analysis/`.

A deposit that points at files elsewhere in the repository is not a deposit. The
copies are what make the archive self-contained, which is the entire reason a
reader can reproduce the paper from the Zenodo record alone.

## The scripts here have diverged from `src/python/analysis/`

Seven of the ten copied scripts differ from their current counterparts:

| Script | Differing lines |
|---|---|
| `plot_hosts_figures_v2.py` | 79 |
| `compute_hosts_tables.py` | 49 |
| `plot_hosts_convergence_v2.py` | 37 |
| `build_hosts_rep_endpoint_table.py` | 36 |
| `compute_hosts_dynamic_aggregate.py` | 28 |
| `compute_hosts_geometry_stratified.py` | 28 |
| `plot_hosts_results.py` | 7 |

The differences are cosmetic — a colorblind-safe palette swap
(`#2ecc71` → `#0072B2`), adoption of the shared `figure_io.save_figure` helper,
font-size increases, and one table becoming hand-maintained. **No statistical
method and no reported number changed.**

This divergence is expected and correct. The deposit records the code *as it was
when deposited*; `src/python/analysis/` records the code as it is now.
Re-syncing them would destroy the provenance the deposit exists to provide.

## `zenodo-metadata.json` describes the *next* deposit

It is upload metadata, not a record of a past deposit. It previously disagreed
with every published version in two ways, both now corrected:

- its title was *"Operator-Host Compatibility … PPSN 2026 reproducibility
  artifact (rev1)"*, but the record's title is **IVF-SPEA2**. All versions of a
  Zenodo record share one title; the per-version subject belongs in the
  description, where it now is.
- it listed **one** creator; every published version lists **five**.

To check what a *published* version actually contains, read the Zenodo record
itself, not this file.

## Citing

Use the concept DOI `10.5281/zenodo.19071253` for the repository in general. Use
a version DOI only when the specific bytes matter, and state the version label
alongside it. Full table in `docs/RELEASE_IDENTITY.md`.
