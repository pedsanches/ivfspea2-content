# Vendoring record — PlatEMO

PlatEMO is **copied into this repository**, not a git submodule. There is no
`.gitmodules`; all ~1,940 files are tracked directly.

| | |
|---|---|
| Upstream | https://github.com/BIMK/PlatEMO |
| Version | **4.6** — inferred from the heading "Release Highlights of PlatEMO 4.6" in the vendored `README.md`. No commit SHA was recorded at import. |
| Imported | on or before 2026-03-17 (commit `a07ca76`, the repository's initial commit; history was later rewritten, so this is the earliest reachable date, not necessarily the download date) |
| License | PlatEMO's own — see the upstream repository. Used for research purposes. |

## Why this file exists

The project's own algorithms live **inside** the vendored tree, so upstream code
and project code are interleaved and cannot be told apart by path alone. Without
the inventory below, there is no way to diff against a fresh PlatEMO or to know
what a re-sync would overwrite.

## Project-owned code inside this tree

**18 algorithm directories, 68 `.m` files** under
`Algorithms/Multi-objective optimization/`.

The list below is the machine-readable inventory —
`scripts/ci/check_platemo_inventory.py` parses exactly this block, so keep one
directory name per line:

<!-- BEGIN PROJECT-DIRS -->
```
IVF-NSGA-II
IVF-NSGA-III
IVF-SPEA2
IVF-SPEA2-V2
IVF-SPEA2-V2-CTRL-TRACE
IVF-SPEA2-V2-NORM
IVF-SPEA2-V2-TRACE
IVF-SPEA2-V3
IVFSPEA2-ABL-1C
IVFSPEA2-ABL-4C
IVFSPEA2-ABL-DOM
IVFSPEA2-P2-COMBINED
IVFSPEA2-V1-DISSIM
IVFSPEA2-V2-COLLECTIVE
IVFSPEA2-V3-ETA10
IVFSPEA2-V4-ADAPTIVE
IVFSPEA2-V5-MUTATION
SPEA2-TRACE
```
<!-- END PROJECT-DIRS -->

Grouped for reading:

| Directory | `.m` | Role |
|---|---|---|
| `IVF-SPEA2-V2` | 4 | **Canonical.** `IVFSPEA2V2` |
| `IVF-SPEA2` | 4 | v1 baseline |
| `IVF-SPEA2-V3` | 6 | Successor line; carries `*_V3` variants alongside unsuffixed copies |
| `IVF-NSGA-II` | 2 | IVF transplanted into NSGA-II |
| `IVF-NSGA-III` | 3 | IVF transplanted into NSGA-III |
| `IVF-SPEA2-V2-TRACE` | 4 | Instrumented v2 |
| `IVF-SPEA2-V2-CTRL-TRACE` | 2 | Instrumented controller variant |
| `SPEA2-TRACE` | 3 | Instrumented baseline (non-IVF, still project-added) |
| `IVF-SPEA2-V2-NORM` | 4 | Normalization pilot |
| `IVFSPEA2-ABL-1C`, `-ABL-4C`, `-ABL-DOM`, `-P2-COMBINED` | 16 | Factorial ablation harness |
| `IVFSPEA2-V1-DISSIM`, `-V2-COLLECTIVE`, `-V3-ETA10`, `-V4-ADAPTIVE`, `-V5-MUTATION` | 20 | Single-hypothesis tuning probes |

Plus, at this directory's root:

| File | Status |
|---|---|
| `run_experiment.m`, `run_one_experiment.m`, `graphics.m` | Project-added drivers |
| `generation_objectives.csv` | Project **output** (10 MB) that was committed here by mistake. Now untracked and gitignored; regenerate from a run. |
| `requirements_platemo.txt` | Was a 0-byte file; PlatEMO is MATLAB-only and has no Python requirements |

`scripts/ci/check_platemo_inventory.py` asserts this list matches the tree, so a
new project directory cannot quietly blend into the vendored code.

## Do not restructure this tree

`platemo()` discovers algorithms by **scanning**
`Algorithms/Multi-objective optimization/`. Moving the project directories out
would break discovery for every runner, and every published path — including
those in the Zenodo deposits and in `CLAUDE.md`'s variant map — refers to the
current layout.

## Path shadowing

`CalFitness.m` is defined in **57** directories across this tree, and many also
define `EnvironmentalSelection.m`. A plain `addpath(genpath(...))` resolves those
names by genpath ordering, so a run can silently execute another algorithm's
fitness function. Prepend the intended variant with `addpath(dir, '-begin')`;
`tests/matlab/setupCanonicalTestPaths.m` is the reference implementation. See
*MATLAB path shadowing* in `CLAUDE.md`.

## Re-syncing with upstream

No patch log was kept, so a re-sync means: fetch PlatEMO at a known tag, diff it
against this tree excluding the directories listed above, review every remaining
difference by hand, and record the new version and SHA here.
