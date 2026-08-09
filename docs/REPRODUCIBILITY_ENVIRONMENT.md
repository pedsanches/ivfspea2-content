# Reproducibility Environment

This document records the exact Python environment that produced the committed
artifacts, and explains which parts of it are load-bearing.

Until this file existed, the repository shipped a `requirements.txt` that
described a *different* environment from the one actually installed — so a
reader following the README would have built figures that differed byte-for-byte
from the deposited ones, with nothing to warn them.

## The producer environment

| | |
|---|---|
| Python | **3.14.2** (CPython, darwin/arm64) |
| numpy | **2.4.3** |
| matplotlib | **3.10.8** |
| pandas | **2.3.3** |
| scipy | 1.17.1 |
| scikit-learn | 1.8.0 |
| seaborn | 0.13.2 |
| statsmodels | 0.14.6 |
| Captured | 2026-08-09 |

The complete freeze is `requirements.lock.txt` at the repository root.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt
```

## Which pin actually matters

**matplotlib is the one hard pin.** Every committed PDF under
`paper/*/figures/` and `results/` carries the stamp

```
/Creator (Matplotlib v3.10.8, https://matplotlib.org)
```

`src/python/analysis/figure_io.py` already suppresses the `CreationDate` key so
that repeated runs are byte-identical, and its own docstring states the residual
caveat: *"upgrading matplotlib does rewrite every figure once."* The `Creator`
and `Producer` keys carry the version and cannot be suppressed without lying
about provenance.

The practical consequence: **regenerating figures under a different matplotlib
rewrites every figure PDF in the repository**, producing a large diff in which
no plotted number has changed. The CI job `assets-reproducible` depends on this
pin — without it the job flaps on every upstream matplotlib release.

The other pins are ordinary compatibility ranges. Nothing in the analysis code
depends on a specific numpy or pandas patch version.

## Reproducibility is platform-dependent below the last bit

The committed CSVs under `data/processed/` and `results/tables/` were computed
on **macOS/arm64**. Regenerating them on Linux/x86-64 reproduces every value to
roughly 15 decimal digits — but not always to the last bit:

```
IVFNSGAII,MaF5,MaF,3,12,4010,4.8884956986782955,...   # macOS/arm64 (committed)
IVFNSGAII,MaF5,MaF,3,12,4010,4.888495698678296,...    # Linux/x86-64
```

Those are adjacent doubles. Reducing the same numbers in a different order —
different BLAS kernels, different SIMD widths — lands one ULP away, and Python's
shortest-roundtrip `repr` then prints a visibly different string for what is
arithmetically the same result. It shows up on a handful of MaF5 rows, where the
IGD reduction is longest.

What follows from that:

- **Byte-identity of the CSVs is a same-platform property.** On macOS/arm64 with
  `requirements.lock.txt`, `make -C paper/ppsn2026-ivf-hosts assets` followed by
  `git diff --exit-code` is clean. Off that platform it is not, and no amount of
  pinning fixes it.
- **The figures inherit it.** A PDF rendered from data differing in the last bit
  is itself byte-different, though nothing visible changes.
- **CI checks the achievable invariant instead**, via
  `scripts/ci/check_assets_reproducible.py`: structure exactly (row count,
  headers, every non-numeric cell) and numbers within a relative tolerance of
  1e-9. Tight enough to catch any real change in inputs or logic; loose enough
  not to fail on arithmetic that is correct on both machines.

No published number is affected — the reported precision is orders of magnitude
coarser than where the platforms disagree.

## Two files, two purposes

| File | Purpose |
|---|---|
| `requirements.lock.txt` | The one combination known to regenerate the deposit. Use for reproduction, CI, and any work that touches committed figures or checksums. |
| `requirements.txt` | Supported ranges for new development. Use when the goal is to write new analysis, not to reproduce old output. |

## The `numpy<2.0` ceiling was removed

`requirements.txt` previously pinned `numpy>=1.24,<2.0` with no recorded
rationale. The installed environment has run **numpy 2.4.3** throughout, so the
ceiling never described reality — and following it would have *downgraded* a
working environment:

```
$ pip install --dry-run -r requirements.txt
Would install numpy-1.26.4          # from numpy 2.4.3
```

The floor is now `numpy>=1.26`, which is what the current scipy, pandas and
matplotlib versions require anyway.

## Undeclared imports

Three packages are imported by repository code but were absent from
`requirements.txt`. They are installed in the producer environment and are
declared as optional extras in `pyproject.toml`:

| Package | Imported by | Extra |
|---|---|---|
| `shap` | `src/python/fla/train_models.py` (lazy, inside a function) | `fla` |
| `imageio` | `git_top10.py`, `gen_gif.py` | `legacy` |
| `pygmo` | `platemo_script.py` | `pygmo` |

`pymoo` and `moocore` are present in the producer environment as well; they were
installed during the fitness-landscape-analysis work.

## MATLAB

The MATLAB side is not captured here. Runs were executed on **MATLAB R2025b**
against the vendored PlatEMO 4.6 tree; see
`src/matlab/lib/PlatEMO/VENDOR.md` for the vendoring record. MATLAB is
deliberately excluded from CI.
