---
name: latex-scientific-quality
description: Compilar e validar o LaTeX da dissertação e dos artigos — erros, referências e citações indefinidas, rótulos duplicados, arquivos ausentes, bibliografia, legendas, tabelas e figuras geradas — distinguindo avisos preexistentes dos introduzidos pela alteração. Use depois de qualquer edição em .tex/.bib e antes de entregar uma revisão.
---

# Qualidade LaTeX

## Toolchain (não substituir)

- Dissertação: Tectonic 0.16.9, XeTeX, BibTeX clássico com `inf-ufg.bst`; classe
  `inf-ufg-tectonic.cls` (derivada; `inf-ufg.cls` original não é editado).
- `make thesis` compila offline em `thesis/masters/build/main.pdf` (primeira vez na máquina:
  `make thesis-bootstrap`, com rede). `make thesis-render` rasteriza as páginas para inspeção.
- Artigos: `cd paper && make <alvo>` (motor detectado em `paper/latex.mk`).
- `make thesis-tables-check` falha se tabela ou figura versionada divergir do artefato, mas
  regenera `results/thesis/` no lugar: conferir `git status -- results/thesis` antes e depois.
  `make thesis-doctor` valida `data-sources.toml`.

## Linha de base × alteração

Antes de editar, com o build atual:

```bash
make thesis
python3 scripts/science/latex_check.py --save-baseline
```

Depois de editar:

```bash
make thesis
python3 scripts/science/latex_check.py --compare
```

O verificador lê `main.log`, `main.blg` e `main.aux` e classifica: erro (`! …`), referência e
citação indefinidas, rótulo duplicado, arquivo ausente, chave citada fora do `.bib`, avisos do
BibTeX, *overfull*/*underfull* por arquivo, página só com *floats*. Com `--compare`, sai com
código 1 se surgir item bloqueante novo; aviso que já existia na linha de base é relatado como
preexistente, não como regressão. Sem linha de base, relata o estado absoluto.

Bibliografia: `python3 scripts/science/bib_check.py` (sem rede) confere chaves duplicadas,
campos obrigatórios por tipo, chaves citadas sem entrada e entradas nunca citadas.

## Regras do projeto

- Tabela e figura de resultado vêm de `results/thesis/` via `\input{generated/…}` e
  `generated/figures/…`; mudar número exige mudar o gerador em `src/python/thesis/` e rodar
  `make thesis-tables` — nunca editar `generated/` nem `results/thesis/` à mão.
- Legenda de tabela acima (`position=top`), de figura abaixo; toda tabela e figura é citada no
  texto antes de aparecer (`Tabela~\ref{…}`).
- Preservar `\label`, `\ref`, `\cite`, comandos e ambientes; novo rótulo segue o prefixo em uso
  (`sec:`, `tab:`, `fig:`, `eq:`, `apend:`).
- Vírgula decimal `{,}` em modo matemático; espaço inseparável antes de `\ref` e `\cite`.
- Aceite do projeto (`REVISION_PLAN.md` §6): zero aviso LaTeX, zero *overfull*, sem página de
  texto só com *floats*; as quatro linhas *underfull* conhecidas são toleradas.
- Mudança de layout exige `make thesis-render` e inspeção das páginas afetadas.
