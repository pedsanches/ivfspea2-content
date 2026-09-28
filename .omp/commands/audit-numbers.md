---
description: Audita todos os números de um trecho contra dados e artefatos (só auditor quantitativo; não edita)
argument-hint: <arquivo[:ini-fim]>
---
Auditoria quantitativa: $ARGUMENTS

1. Pasta `.omp/runs/<AAAA-MM-DD-HHMM>-numeros/`; `git status --porcelain >
   <pasta>/status-antes.txt`.
2. `python3 scripts/science/claims.py inventory <alvo> --json > <pasta>/inventory.json`.
3. Despache um agente `quant-auditor` (`schemaMode: "strict"`) com o alvo e o caminho de
   `inventory.json`.
4. Mostre todos os achados e a cobertura (números verificados com a fonte), sem filtrar.
5. Compare `git status --porcelain` com `status-antes.txt`; se algo mudou, avise: o auditor é
   somente leitura. Nada é editado; correções seguem por `/gate` ou por decisão do autor.
