---
description: Ciclo cotidiano — melhora a prosa de um trecho (edição de linha), sem revisores
argument-hint: <arquivo[:ini-fim]> [instrução]
---
Revisão cotidiana de prosa científica. Alvo e instrução: $ARGUMENTS

Sem alvo claro, pergunte antes de editar.

1. Carregue a skill `scientific-writing-ptbr` e as referências `estilo.md` e `voz.md`
   (`terminologia.md` se houver termo técnico).
2. `python3 scripts/science/claims.py snapshot <arquivo>`.
3. Faça a edição menos invasiva que atende à instrução (padrão: edição de linha), só no trecho
   indicado. Não altere números, citações, rótulos, escopo nem força das afirmações; se a
   instrução exigir isso, pare e pergunte.
4. `python3 scripts/science/claims.py diff <arquivo>` e
   `python3 scripts/science/prose_audit.py <arquivo>`; trate só os sinais que caem no trecho
   editado e decida cada um no contexto.
5. Entregue: diff, modo de edição usado, decisões que mudam ênfase. Sem revisores. Se o trecho
   é novo ou mudou de sentido, recomende `/gate <alvo>`.
