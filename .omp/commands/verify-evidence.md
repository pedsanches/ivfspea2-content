---
description: Verifica referências e a correspondência fonte→afirmação de um trecho (só revisor de evidência; não edita)
argument-hint: <arquivo[:ini-fim] | chave-bibtex>
---
Verificação de evidência externa: $ARGUMENTS

1. Pasta `.omp/runs/<AAAA-MM-DD-HHMM>-evidencia/`.
2. Alvo em arquivo: `python3 scripts/science/claims.py inventory <alvo> --json >
   <pasta>/inventory.json`. Alvo em chave BibTeX: localize as frases que a citam com
   `grep -rn "<chave>" thesis/masters/tex thesis/masters/pre`.
3. `python3 scripts/science/bib_check.py --keys <chaves> --online --json > <pasta>/bib.json`.
4. Despache um agente `evidence-reviewer` (`schemaMode: "strict"`) com o alvo e os caminhos de
   `inventory.json` e `bib.json`. Não opine sobre as referências na tarefa.
5. Mostre todos os achados, a cobertura e o que não foi conferido, sem filtrar. Nada é editado
   nem acrescentado ao `.bib`; correções seguem por `/gate` ou por decisão do autor.
