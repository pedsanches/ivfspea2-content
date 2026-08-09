# docs/history/

Completed working documents, kept for the record. Nothing here describes the
current state of the repository — read `docs/IVFSPEA2_EVIDENCE_MODEL.md` and
`CLAUDE.md` for that.

## Why the checkboxes are all unchecked

`superpowers/` holds 5 plans and 3 specs, about 6,400 lines, with 283 task
checkboxes — **none ticked**, even though the work they describe shipped. The
plans were written against an external tooling contract that tracked completion
elsewhere; the boxes were never the record. One plan says so outright, noting
that a previous plan's edits "are already in `main.tex`".

Treat the checkboxes as inert. The evidence that the work landed is in the
repository: the figures exist, the tables are committed, and the camera-ready is
tagged `ppsn2026`.

## Why these are kept rather than deleted

`superpowers/plans/2026-04-17-ppsn2026-ivf-hosts-reviewer-revision.md` is the
design record for the reviewer revision of an **accepted** paper. It documents
decisions that are otherwise unrecoverable — among them the choice to cite the
Research Square preprint (decision D2) and the origin of
`artifact/zenodo-metadata.json`. Deleting it would discard the reasoning behind
metadata that is now published.

## Contents

| Path | What it is |
|---|---|
| `superpowers/plans/` | Dated implementation plans, 2026-04-10 → 2026-04-18, all completed |
| `superpowers/specs/` | Specifications those plans worked from |
| `2026-ppsn-hosts-revision-plan.md` | The hosts manuscript's revision plan (pt-BR), formerly `paper/ppsn2026-ivf-hosts/plan.md` |

Historical documents are exempt from the repository's path and language guards:
they record what was true when written, and editing them to satisfy a linter
would falsify the record.
