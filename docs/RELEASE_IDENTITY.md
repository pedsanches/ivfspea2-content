# Release Identity

The authoritative statement of which DOI means what. Every DOI that appears in a
tracked file must be listed here, and `make verify-release` enforces that.

This document exists because three different Zenodo DOIs were circulating in the
repository with no stated relationship between them, and a fourth — the concept
DOI, the one a citation should normally use — appeared nowhere at all.

## The Zenodo record

There is **one** Zenodo record, titled *IVF-SPEA2*, with seven published
versions, one per GitHub release (the GitHub–Zenodo integration archives each
release). They are not separate deposits.

| DOI | Version label | Published | Corresponding git tag |
|---|---|---|---|
| **`10.5281/zenodo.19071253`** | — **concept** — | resolves to latest | — |
| `10.5281/zenodo.19071254` | `v1.0.1` | 2026-03-17 | `v1.0.0` |
| `10.5281/zenodo.19071388` | `v1.0.0` | 2026-03-17 | `v1.0.0` |
| `10.5281/zenodo.19637623` | `v1.0.2` | 2026-04-18 | `v1.0.2` |
| `10.5281/zenodo.19800600` | `clei2026` | 2026-04-26 | `clei2026` |
| `10.5281/zenodo.20672828` | `ppsn2026` | 2026-06-12 | `ppsn2026` |
| `10.5281/zenodo.23307916` | `dissertacao2026-defesa` | 2026-10-12 | `dissertacao2026-defesa` (superseded) |
| `10.5281/zenodo.23307942` | `dissertacao2026-defesa-r1` | 2026-10-12 | `dissertacao2026-defesa-r1` |

Versions checked against the live record
(`https://zenodo.org/api/records?q=conceptrecid:19071253&all_versions=true`) on
2026-10-12. The `v1.0.1` version links to a `tree/v1.0.1` tag that no longer
exists on the remote; its mapping to `v1.0.0` is kept from the earlier record.

All five authors (Zambrano, Souza, Dantas, Sampaio, Camilo-Junior) are on every
version.

### Which one to use

**Cite the concept DOI, `10.5281/zenodo.19071253`.** It resolves to whatever the
latest version is, so it does not go stale. This is what belongs in the README
badge, in `CITATION.cff`, and in any prose that refers to "the repository".

**Cite a version DOI only when the specific bytes matter** — a manuscript
pointing at the artifact that backs *its own* numbers. In that case state the
version label alongside the DOI, so a reader knows which snapshot is meant:

- `paper/ppsn2026-ivf-hosts/main.tex` cites `20672828` (`ppsn2026`). Correct: that
  version contains the artifact for the accepted PPSN paper.
- `paper/springer-nature/` cites `19071254` (`v1.0.1`). Correct for that
  manuscript's submission snapshot; the bib entry now records the version label.
- `thesis/masters/bib/modelo-tese.bib` (`ivfspea2github`) and the hidden Appendix B
  cite `23307942` (`dissertacao2026-defesa-r1`), the snapshot sent to the defense
  committee. Author's decision on 2026-10-11, replacing the earlier choice of the
  concept DOI. The tag holds the bytes behind the numbers; the commit that writes
  this DOI into the bib necessarily comes after the tag. The bib's `note` repeats
  the DOI because `inf-ufg.bst` does not print the `doi` field.

### Superseded references

`10.5281/zenodo.19637623` (`v1.0.2`) is a real, permanently valid version DOI —
it is not wrong, only older. It appears inside `artifact/ppsn2026-ivf-hosts-rev1/`
because those files are the **deposited bytes** of that version. They are not
edited; a banner in the release notes points forward to `ppsn2026` instead.

`10.5281/zenodo.23307916` (`dissertacao2026-defesa`) is also permanently valid,
but `make verify-release` fails inside it: `CITATION.cff` was edited after the
check ran, so the manifest hash for that file is stale. No evidence file differs
from `dissertacao2026-defesa-r1`, which supersedes it. Do not cite it.

## Non-Zenodo identifiers

| Identifier | What it is | Where it belongs |
|---|---|---|
| `10.21203/rs.3.rs-9431034/v1` | Research Square preprint of the IVF/SPEA2 paper | `references.bib` of the PPSN manuscripts; `related_identifiers` in the deposit metadata |

## Repository URL

The remote is **`https://github.com/pedsanches/ivfspea2-content`**. An earlier
`README.md` cited `pedsanches/IVF-SPEA2`, which is not the remote. `CITATION.cff`
was already correct.

## Git tags

Six tags exist on the remote, all archived by Zenodo versions, and **none may be
moved or deleted**. `backup-main-preconsolidacao` is a local safety point only:

| Tag | Date | Status |
|---|---|---|
| `v1.0.0` | 2026-03-17 | archived as Zenodo `v1.0.0` and `v1.0.1` |
| `backup-main-preconsolidacao` | 2026-03-20 | local safety point |
| `v1.0.2` | 2026-04-17 | archived as Zenodo `v1.0.2` |
| `clei2026` | 2026-04-26 | archived as Zenodo `clei2026`; CLEI submission snapshot |
| `ppsn2026` | 2026-06-12 | archived as Zenodo `ppsn2026`; camera-ready |
| `dissertacao2026-defesa` | 2026-10-11 | archived as Zenodo `dissertacao2026-defesa`; superseded (stale `CITATION.cff` hash) |
| `dissertacao2026-defesa-r1` | 2026-10-11 | archived as Zenodo `dissertacao2026-defesa-r1`; dissertation sent to the committee |

The tag `submission-snapshot-2026-03`, referenced by an older `README.md`, was
never created. The README now cites `v1.0.0`. Minting a tag after the fact to
make stale prose resolve would invent provenance, so it was not done.

## Enforcement

`scripts/release/verify_release.py` scans tracked files for
`10.5281/zenodo.<digits>` and fails if a DOI is not listed above, or appears
somewhere this document does not permit. That check is what stops the drift from
recurring; without it, the next manuscript adds a fourth DOI and nobody notices.

## Deposit metadata

`artifact/zenodo-metadata.json` is the upload metadata for the **next** version.
It previously contradicted every published version — a different title, and one
creator where the record has five — and has been corrected. A Zenodo record's
title is shared by all its versions, so the per-version subject matter belongs in
the description, not the title.

Verify against the live record, not against that file, when the question is what
a published version contains.
