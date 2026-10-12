# CLEI 2026 — Intelligent Systems Track

Conference: 52nd Latin American Computing Conference (CLEI 2026)
Track: Intelligent Systems
Format: IEEE Conference Proceedings (two-column, letter size)

## Build

```bash
make          # compile → build/main.pdf
make view     # compile and open PDF
make clean    # remove build artifacts
```

## Camera-ready snapshot

`main.tex` and the seven PDFs in `figures/` were restored from the CLEI
snapshot `4b10a61f91769054ab6b836a7f490db70bd1f5e4`. The build was checked
against `2026365578.pdf`: identical extracted text and identical rasterized
content on all nine pages at a 1600-pixel maximum dimension. IEEE PDF eXpress
certification metadata is not reproduced by the local build.

`figures/` is a local directory, not a symlink to the PPSN figure set. This
keeps CLEI restoration and subsequent figure changes isolated from the other
manuscripts and the dissertation.

## Template

- `IEEEtran.cls` — IEEE conference document class
- `IEEEtran.bst` — IEEE bibliography style

## Requirements

- `texlive-full` (or equivalent TeX distribution)
- `latexmk`

## Conference guidelines

- Max 10 pages (full paper)
- Title, abstract, and keywords in English only
- IEEE style bibliographic references
- No page numbers
- Figures: titles centered below
- Tables: titles centered above
- Camera-ready via IEEE PDF eXpress (Conference ID: 67442X)
