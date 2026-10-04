---
name: quantitative-audit
description: Auditar números de texto científico do projeto contra dados, tabelas geradas, logs e código — contagens, métricas, percentuais, p-valores, tamanhos de efeito, tamanhos de amostra, parâmetros — e a consistência cruzada entre capítulos, resumo, tabelas e figuras. Prefere cálculo por código a julgamento.
---

# Auditoria quantitativa

**Se algo pode ser verificado por código, verifique por código.** Não recalcular de cabeça,
não estimar, não arredondar "no olho". Todo valor conferido leva o comando ou o arquivo que o
produziu.

## Mapa das fontes

- `thesis/masters/data-sources.toml` — manifesto: para cada família, `cohort`, `datasets`,
  `artifacts`, `scripts` produtores e `known_gaps` (armadilhas conhecidas). Comece por aqui.
- `results/thesis/*.tex` — tabelas da dissertação, geradas por `src/python/thesis/`. Número de
  tabela nunca é digitado. `make thesis-tables-check` confere a sincronia, mas reescreve
  `results/thesis/` no lugar: é passo do autor ou do `/final-pass`, não da auditoria.
- `results/tables/claims_summary_audit.csv` — única fonte de contagens "corrigidas por Holm"
  do protocolo da comparação principal (colunas `metric, condition, M, wins, losses, ties, n`).
- `data/processed/todas_metricas_consolidado_with_modern.csv` — consolidado; **sempre** filtrar
  com `ivfspea2.cohorts.filter_submission_synthetic_cohort` (o rótulo `IVFSPEA2` mistura as
  execuções `1–60` e `3001–3060`).
- `docs/IVFSPEA2_EVIDENCE_MODEL.md`, `results/SUBMISSION_EVIDENCE_MAP.md` — índices humanos.
- `thesis/masters/REVISION_PLAN.md` §2 — resumo humano das respostas; **não** é fonte primária.

## Procedimento

1. **Inventário.** `python3 scripts/science/claims.py inventory <arquivo[:ini-fim]> --json`
   lista cada número com linha e frase. Nenhum número do alvo fica fora da auditoria.
2. **Classificar** cada número: definicional ("duas decisões"), parâmetro (C26), desenho (51
   instâncias, 60 execuções, 100.000 avaliações), resultado (contagem, mediana, %, p, $A_{12}$),
   referência cruzada (número de tabela, seção).
3. **Localizar a fonte** pelo manifesto e pelo gerador da tabela citada no parágrafo.
4. **Conferir por código**, só leitura, com o ambiente do projeto:

   ```bash
   .venv/bin/python - <<'EOF'
   import pandas as pd
   from ivfspea2.cohorts import filter_submission_synthetic_cohort
   df = filter_submission_synthetic_cohort(
       pd.read_csv("data/processed/todas_metricas_consolidado_with_modern.csv"))
   # ... cálculo explícito do valor afirmado ...
   EOF
   ```

   Arquivos temporários só em `/tmp`. Nunca escrever em `data/`, `results/`, `artifact/`,
   `thesis/` ou `src/`; nunca editar código do autor para "fazer bater".
5. **Classificar o estado**: `VERIFIED` (valor e escopo batem, com arredondamento declarado) ·
   `MISMATCH` (fonte diz outro valor ou outro escopo) · `UNVERIFIED` (fonte não encontrada ou
   inacessível) · `NOT_APPLICABLE` (definicional).
6. **Consistência cruzada**: o mesmo número em resumo, abstract, Cap. 1, capítulo de
   resultados, Cap. 8 e tabela; mesma família de correção; mesma coorte.

## Armadilhas conhecidas

- Notação W/T/L do texto = vitórias/empates/derrotas; o CSV guarda `wins, losses, ties` nessa
  ordem de colunas. Conferir a ordem antes de comparar.
- Contagem Holm × não corrigida (`condition`: `Holm`, `unadjusted`, `*_OOS`).
- Famílias separadas por M (M2, M3) e por métrica (IGD, HV).
- Recorte fora do ajuste: 39 instâncias; o MaF7 com M = 3 repete o DTLZ7 da calibração
  (`OQ-21`).
- Execuções `3001–3030` × `1–30` reutilizadas no estudo de hospedeiros; o teste de convergência
  pareado por identificador descarta o par IVF/SPEA2 × SPEA2 (`OQ-03`).
- `classifier_comparison.csv` tem linha LOOCV mal rotulada (`OQ-13`); usar as tabelas
  declaradas no manifesto.
- Vírgula decimal no texto, ponto no CSV; arredondamento das tabelas em `ptbr_format.py`.
- IGD: menor é melhor; HV: maior é melhor. Diferença relativa com sinal: conferir a convenção
  da tabela.

## Achados

Um achado por número com estado `MISMATCH` ou `UNVERIFIED` material: frase literal, local,
valor no texto, valor e escopo na fonte (caminho e comando), problema e ação mínima (corrigir
para o valor verificado **com a fonte**, ou marcar `[NÃO VERIFICADO]`). `VERIFIED` vai para a
lista de cobertura, com a fonte.
