---
name: scientific-writing-ptbr
description: Redigir, reescrever ou revisar prosa científica em português brasileiro da dissertação IVF/SPEA2 (parágrafo, abertura de seção, edição de linha) preservando significado, números, citações, terminologia e a voz do autor. Não valida a ciência do próprio texto.
---

# Escrita científica em PT-BR

Equivale, no OMP, à skill `$write-scientific-manuscripts` citada no perfil do projeto.

## Autoridades (em ordem)

1. Normas do PPGCC/UFG (skill `thesis-structure`).
2. Decisões do autor: `thesis/masters/REWRITE_SPEC.md` §1.1, `REVISION_PLAN.md` §2 e §4.
3. `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md`: §3 voz, §4 vocabulário e proibição de
   versionamento, §8 linguagem de resultados, §9 fórmulas, §10 citações.
4. Esta skill e suas referências.

Conflito entre autoridades: não decidir em silêncio; apontar e perguntar.

## Referências (carregar sob demanda)

- `skill://scientific-writing-ptbr/references/estilo.md` — sempre que revisar prosa.
- `skill://scientific-writing-ptbr/references/voz.md` — sempre que reescrever texto da
  dissertação.
- `skill://scientific-writing-ptbr/references/terminologia.md` — termo técnico, estrangeirismo,
  sigla ou nome de algoritmo.
- Força de afirmação: skill `scientific-argumentation`.

## Modo de edição

Escolher o menos invasivo que atende o pedido e declarar qual foi usado:

- **revisão**: gramática, ortografia, pontuação, consistência óbvia;
- **edição de linha**: clareza, coesão, terminologia, desenho da frase; argumento intacto;
- **edição substantiva**: reorganizar parágrafos ou recalibrar afirmações — só se pedido;
- **edição de desenvolvimento**: só propor; decisões de arquitetura são do autor.

## Procedimento

1. **Foto antes de editar.** `python3 scripts/science/claims.py snapshot <arquivo>`.
2. **Ler o trecho e a vizinhança** (parágrafo anterior e seguinte, seção onde está). Anotar a
   função do parágrafo e o que não pode mudar: números, `\cite`, `\ref`/`\label`, comandos
   LaTeX, termos canônicos, ressalvas, escopo (suíte, coorte, métrica, família).
3. **Reescrever pelo critério de `estilo.md`**, no registro de `voz.md`.
4. **Nada novo sem fonte.** Não acrescentar afirmação, número, citação, exemplo, mecanismo ou
   explicação causal que não esteja no original ou numa fonte indicada e lida. Lacuna → marcador
   visível `[FONTE NECESSÁRIA: …]` ou `[NÃO VERIFICADO: …]` e aviso ao autor; nunca completar
   por plausibilidade.
5. **Verificar.**
   - `python3 scripts/science/claims.py diff <arquivo>` — números, citações, rótulos e
     marcadores de força que mudaram. Toda mudança dessas categorias precisa de justificativa
     explícita; sem justificativa, desfazer.
   - `python3 scripts/science/prose_audit.py <arquivo>` — sinais editoriais; decidir no contexto,
     nunca corrigir mecanicamente.
   - Se tocou `tex/` ou `pre/`: grep de versionamento do perfil §4.1.
6. **Entregar.** Diff unificado (saída do passo 5), modo usado, decisões que alteram ênfase ou
   força (com motivo) e pendências. Texto novo ou reescrita substantiva é candidato: recomendar
   `/gate` antes de considerá-lo maduro.

## Limites

- O escritor não valida cientificamente o próprio texto; essa função é dos revisores (`/gate`).
- Não otimizar para detector de IA nem inserir imperfeição para "parecer humano".
- Resumo e abstract comunicam a mesma evidência, sem tradução literal.
- Artigos em inglês (`paper/*`): mesmos passos 1–6; `terminologia.md` não se aplica.
