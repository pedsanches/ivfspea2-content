# Papers

This directory now keeps each manuscript isolated in its own folder:

- `springer-nature/` — Springer Nature / Memetic Computing manuscript
- `ppsn2026/` — PPSN 2026 manuscript
- `clei2026/` — CLEI 2026 manuscript (Intelligent Systems track)

## Common commands

From `paper/`:

```bash
make                 # build the Springer Nature paper
make springer-nature # same as above
make ppsn2026        # build the PPSN paper
make clei2026        # build the CLEI paper
make papers          # build all papers
make clean           # clean all paper build trees
```

## Build outputs

- `springer-nature/build/sn-article.pdf`
- `ppsn2026/build/main.pdf`
- `clei2026/build/main.pdf`
