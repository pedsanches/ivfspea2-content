---
description: Passagem final pré-envio — checagens determinísticas da dissertação inteira e revisão de consistência entre capítulos; não edita
argument-hint: [foco opcional]
---
Passagem final da dissertação. Foco adicional: $ARGUMENTS

Nada é editado nesta passagem. Registre cada saída na pasta da execução.

1. Pasta `.omp/runs/<AAAA-MM-DD-HHMM>-final/`; `git status --porcelain > <pasta>/status-antes.txt`.
2. Checagens determinísticas:
   - `make thesis-doctor`;
   - `make thesis-tables-check` — regenera `results/thesis/` no lugar: compare
     `git status --porcelain -- results/thesis` antes e depois e relate qualquer diferença;
   - `make thesis` e `python3 scripts/science/latex_check.py` (com `--compare` se houver linha
     de base);
   - `python3 scripts/science/bib_check.py` (sem rede; `--online` só com ok do autor);
   - `python3 scripts/science/prose_audit.py thesis/masters/tex thesis/masters/pre --format json`
     (resuma por capítulo e severidade);
   - `python3 scripts/science/claims.py inventory thesis/masters/tex thesis/masters/pre --json`
     (contagem de números e citações por capítulo);
   - grep de versionamento do `SCIENTIFIC_WRITING_PROFILE.md` §4.1, restrito a `*.tex`;
   - `make verify-release` e `make test`.
3. Consistência entre capítulos: despache `scientific-reviewer` (name `ConsistenciaRev`,
   `schemaMode: "strict"`) para auditar a continuidade objetivos → QPs → protocolo → respostas
   (Cap. 8) → conclusões → resumo/abstract, a regra de resposta única e os números repetidos
   entre capítulos, usando a skill `thesis-structure`.
4. Pendências institucionais: liste os itens abertos de `thesis/masters/REVISION_PLAN.md` §4–§5
   e de `skill://thesis-structure/references/normas-ppgcc-ufg.md` (declaração do formato,
   declaração de IA, folha de aprovação, ficha catalográfica). Não os resolva.
5. Grave `<pasta>/report.md` e entregue o resumo: bloqueantes, achados do revisor sem filtro,
   pendências. Compare `git status --porcelain` com `status-antes.txt` e relate qualquer
   mudança.
