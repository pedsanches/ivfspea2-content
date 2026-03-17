# Setup Guide for IVF/SPEA2 Paper

This project contains the LaTeX source code for the "Memetic Computing IVF/SPEA2" paper.

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

To compile the paper, run:

```bash
make
```

The output PDF will be generated in the `build/` directory: `build/sn-article.pdf`.

To view the PDF:
```bash
make view
```

To clean build artifacts:
```bash
make clean
```

## Directory Structure

- `src/`: LaTeX source files (`sn-article.tex`)
- `bib/`: Bibliography files (`.bib`, `.bst`)
- `cls/`: LaTeX class files (`.cls`)
- `figures/`: Images and plots
- `build/`: Generated output files
