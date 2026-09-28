---
description: Redige trecho novo com o agente writer (contexto limpo) a partir de fontes indicadas
argument-hint: <arquivo[:onde]> <o que escrever e com quais fontes>
---
Tarefa de redação: $ARGUMENTS

1. Identifique arquivo, ponto de inserção, função do trecho no argumento e as fontes (tabelas
   em `results/thesis/`, seções, artefatos, referências do `.bib`). Se o conteúdo pedido não tem
   fonte identificável, pergunte antes de despachar.
2. Despache **um** agente `writer` pela ferramenta `task` com: alvo exato, função do trecho,
   fontes a ler, o que não pode mudar e os limites de escopo. Não redija você mesmo.
3. Ao receber o resultado, rode `python3 scripts/science/claims.py diff <arquivo>` e
   `python3 scripts/science/prose_audit.py <arquivo>`. Mostre o diff e os campos `decisions` e
   `pending` do writer.
4. O texto é candidato: recomende `/gate <alvo>` antes de considerá-lo maduro. Se o autor
   aceitar o texto, proponha a entrada do `thesis/masters/AI_ASSISTANCE_LOG.md` no formato do
   arquivo (não grave sem o ok do autor).
