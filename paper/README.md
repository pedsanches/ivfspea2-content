# Papers

Each manuscript is isolated in its own folder:

- `springer-nature/` — Springer Nature / Memetic Computing manuscript
- `ppsn2026/` — PPSN 2026, early population dynamics for operator switching
- `ppsn2026-ivf-hosts/` — PPSN 2026, IVF across host algorithms (**accepted**)
- `clei2026/` — CLEI 2026 manuscript (Intelligent Systems track)

## Common commands

From `paper/`:

```bash
make                  # build the Springer Nature paper
make springer-nature  # same as above
make ppsn2026         # build the PPSN dynamics paper
make ppsn-hosts       # build the PPSN IVF-hosts paper (regenerates its assets)
make ppsn-hosts-assets  # regenerate that paper's figures and tables only
make clei2026         # build the CLEI paper
make papers           # build all four
make clean            # clean all paper build trees
```

The same builds are reachable from the repository root as `make paper`,
`paper-ppsn`, `paper-hosts`, `paper-clei` and `paper-all`.

## Build engine

`latex.mk` picks the engine automatically: `latexmk` when a system TeX is
installed, otherwise Tectonic (`brew install tectonic`, no system TeX needed).
Force one with `make ENGINE=tectonic` or `make ENGINE=latexmk`.

## `ppsn2026-ivf-hosts` regenerates its own evidence

Unlike the other three, this manuscript rebuilds the figures and tables it cites
before running LaTeX. Its `assets` target runs a fixed sequence of
`src/python/analysis/` scripts and chains into `make analysis-convergence` when
the convergence `.mat` files are present.

`build/.assets.stamp` deliberately tracks only the upstream scripts and inputs —
never the generated figures, which are versioned deliverables. For the same
reason `make clean` leaves those outputs alone; `make clean-assets` is the
opt-in that removes them.

Because the outputs are committed, a rebuild that changes a single byte shows up
as a diff. That is intentional and is enforced in CI by the
`assets-reproducible` job. It only holds with the pinned matplotlib — see
`docs/REPRODUCIBILITY_ENVIRONMENT.md`.

## Build outputs

- `springer-nature/build/sn-article.pdf`
- `ppsn2026/build/main.pdf`
- `ppsn2026-ivf-hosts/build/main.pdf`
- `clei2026/build/main.pdf`

## Note on shared figures

`clei2026/figures` is a symlink to `../ppsn2026/figures`. The two manuscripts
share a figure set by design, and only the symlink is tracked. A reader
unpacking `clei2026/` on its own will not get the figures with it.
