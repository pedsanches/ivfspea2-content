# legacy/

Scripts that nothing in the repository can reach. Kept, not deleted — several
produced figures or numbers that appear in earlier drafts, and the record of how
those were made is worth more than the tidiness of removing them.

**Nothing here is maintained.** These scripts are not linted, not tested, not
covered by the path guard, and not expected to run against current data. Several
still hardcode `/home/pedro/...` paths from the machine they were written on.

## What "unreachable" means here

The classification is a script, not a judgement call — two manual censuses of
`src/python/analysis/` had disagreed, giving 30 orphans by one criterion and 47
by another. `scripts/ci/find_orphans.py` calls a script **live** when anything
can actually reach it:

- named in the root `Makefile` or any `paper/*/Makefile`
- named in a shell launcher under `experiments/` or `scripts/`
- imported by anything under `tests/python/`
- imported, transitively, by a live script

and vetoes the move regardless when the script is:

- named in `results/submission_release_manifest.csv` or
  `results/SUBMISSION_EVIDENCE_MAP.md` — moving it would break the deposit's
  provenance chain
- the sole producer of a file something live depends on

That last guard is the one that matters most, and it caught three scripts that
every reachability measure called dead:

| Script | Why it stayed |
|---|---|
| `consolidate_nsga_experiments.py` | Sole producer of `data/processed/nsga_experiments.csv`, an `ASSET_INPUTS` entry of the **accepted** PPSN paper |
| `sensitivity_analysis.py` | Sole producer of `results/sensitivity_analysis_igd.csv`, which the test suite reads through a live script |
| `prepare_ivf_trace_case_manifest.py` | Sole producer of six tracked CSVs under `results/ivf_trace/` |

In each case the file survived only because it happened to be committed. Moving
the producer would have made it unregenerable — worse than a missing file,
because nothing fails until someone needs to rebuild.

Re-run the classification at any time:

```bash
python scripts/ci/find_orphans.py
```

## Contents

`MANIFEST.csv` records every move: original path, new path, reason, and the last
commit that touched the file. The directory keeps the shape of its origin
(`legacy/python/analysis/`), so `git log --follow` works and a script that still
runs can still be invoked:

```bash
python legacy/python/analysis/<name>.py
```

Sibling imports resolve because the directory sits on `sys.path[0]` under direct
invocation, exactly as `src/python/analysis/` did.

## Bringing one back

Move it to `src/python/analysis/`, wire it into a `Makefile` target or a test,
remove its entry from `MANIFEST.csv`, and clear any hardcoded path — `check_paths`
will start enforcing that the moment it leaves this directory.
