# Papers

This directory now keeps each manuscript isolated in its own folder:

- `springer-nature/` — Springer Nature / Memetic Computing manuscript
- `ppsn2026/` — PPSN 2026 manuscript

## Common commands

From `paper/`:

```bash
make                 # build the Springer Nature paper
make springer-nature # same as above
make ppsn2026        # build the PPSN paper
make papers          # build both papers
make clean           # clean both paper build trees
```

## Build outputs

- `springer-nature/build/sn-article.pdf`
- `ppsn2026/build/main.pdf`
