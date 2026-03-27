# Springer Nature Paper

This directory contains the LaTeX source code for the Springer Nature / Memetic Computing manuscript.

## Prerequisites

You need a LaTeX distribution installed. On Ubuntu/Debian, run:

```bash
sudo apt-get update
sudo apt-get install texlive-full latexmk
```

Or minimally:
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-science texlive-bibtex-extra latexmk
```

## Compilation

To compile the paper from this directory, run:

```bash
make
```

The output PDF is generated in `build/sn-article.pdf`.

To view the PDF:
```bash
make view
```

To clean build artifacts:
```bash
make clean
```

## Layout

- `src/`: LaTeX source files
- `bib/`: bibliography assets
- `cls/`: Springer Nature class files
- `figures/`: figures used by the manuscript
- `scripts/`: helper utilities for manuscript packaging
- `build/`: generated output files
