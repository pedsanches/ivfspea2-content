---
description: Scientific gate — revisores científico, de evidência e quantitativo em paralelo, aceite do autor, editor e checagens
argument-hint: <arquivo[:ini-fim]>
---
Scientific gate do alvo: $ARGUMENTS

Você orquestra. Não revise nem edite a ciência do alvo e não opine sobre ela para os revisores.
Execute todas as etapas.

## 0. Preparação

- Pasta da execução: `.omp/runs/<AAAA-MM-DD-HHMM>-gate/` (`mkdir -p`).
- `git status --porcelain > <pasta>/status-antes.txt`.
- `python3 scripts/science/claims.py snapshot <arquivo>`.
- `python3 scripts/science/claims.py inventory <alvo> --json > <pasta>/inventory.json`.
- `python3 scripts/science/bib_check.py --keys <chaves citadas no alvo> --online --json >
  <pasta>/bib.json` (sem rede, sem `--online`).
- Dissertação com build existente: `python3 scripts/science/latex_check.py --save-baseline`.

## 1. Revisão independente

Uma chamada `task` com três itens em paralelo, cada um com `schemaMode: "strict"`:

- `scientific-reviewer` (name `CientificoRev`): revisar o alvo inteiro.
- `evidence-reviewer` (name `EvidenciaRev`): citações e afirmações que dependem de literatura
  no alvo; informe o caminho de `bib.json`.
- `quant-auditor` (name `QuantRev`): todos os números do alvo; informe o caminho de
  `inventory.json`.

O `context` comum diz só: documento, alvo (arquivo e linhas), que cada revisor trabalha isolado
e que a saída é estruturada. Nenhum revisor vê o resultado de outro.

## 2. Consolidação sem filtro

- Registre o modelo resolvido de cada revisor. Se algum rodou por fallback na família do
  escritor (Anthropic), avise: a independência ficou reduzida.
- Tabela com **todos** os achados (id, severidade, confiança, tipo, local, problema, ação,
  julgamento humano), ordenada por severidade. Não funda, descarte, suavize nem reclassifique;
  duplicatas entre revisores ficam lado a lado.
- Grave `<pasta>/findings.json` (lista integral, com o revisor de origem) e `<pasta>/report.md`
  (tabela, cobertura, não conferidos). Confira: total da tabela = soma dos três revisores.

## 3. Aceite do autor

Mostre a tabela e pergunte (ferramenta `ask`, múltipla escolha) quais achados aceitar. Achado
com `requires_human_judgment: true` só entra com a decisão do autor por escrito. Sem aceite,
encerre com o relatório.

## 4. Edição

Despache o agente `editor` com o alvo, os achados aceitos em JSON integral e as decisões do
autor. Nada além disso.

## 5. Checagens

- `python3 scripts/science/claims.py diff <arquivo>`: cada mudança de número, citação, rótulo ou
  marcador de força corresponde a um achado aplicado; o que não corresponder, mostre ao autor.
- `python3 scripts/science/prose_audit.py <arquivo>`.
- Dissertação: `make thesis`, `python3 scripts/science/latex_check.py --compare` e o grep de
  versionamento do `SCIENTIFIC_WRITING_PROFILE.md` §4.1.
- `git status --porcelain` comparado a `status-antes.txt`: nenhum arquivo além do alvo mudou.

## 6. Entrega

Diff, achados aplicados e pulados, resultado das checagens e pendências de julgamento humano.
Proponha a entrada do `thesis/masters/AI_ASSISTANCE_LOG.md` no formato do arquivo; grave só com
o ok do autor.
