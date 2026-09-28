---
name: evidence-verification
description: Verificar referências e a correspondência fonte→afirmação em texto científico do projeto — existência, metadados (título, autores, ano, veículo, DOI), retratação/correção, fonte primária e se a fonte citada realmente sustenta o que o texto afirma. Use antes de aceitar ou acrescentar citação e em revisão de evidência externa.
---

# Verificação de evidência externa

## Política

- Uma referência só pode ser usada se (A) já existe válida em `thesis/masters/bib/modelo-tese.bib`
  (ou no `.bib` do artigo) **e** foi conferida, ou (B) foi localizada fora e verificada. Nunca
  gerar entrada BibTeX, DOI, URL, página ou autor por plausibilidade.
- **Existir não é sustentar.** Metadados corretos não provam que a fonte apoia a afirmação;
  as duas conferências são separadas e ambas vão no achado.
- Resultado original → fonte primária. Revisão (*survey*) não substitui o artigo original
  quando este está disponível.
- Não acrescentar ao `.bib` antes de confirmar metadados; a inclusão é decisão do autor.
- Consultas externas levam só metadados bibliográficos (DOI, título, autores), nunca trechos
  do manuscrito.
- Fonte não aberta não foi lida: sem acesso ao texto, o estado é `UNVERIFIABLE`, não "sustenta".

## Procedimento

1. **Inventário do alvo.** `python3 scripts/science/claims.py inventory <arquivo[:ini-fim]>`
   lista as frases com `\cite{…}` e as chaves.
2. **Metadados determinísticos.**
   `python3 scripts/science/bib_check.py --keys <chaves> --online --json` confere, por DOI
   (doi.org e Crossref), título, ano, primeiro autor, tipo e aviso de retratação/correção; sem
   DOI, busca por título no Crossref e reporta o melhor candidato com similaridade. Sem rede,
   rodar sem `--online` (só consistência interna do `.bib`).
3. **Correspondência afirmação→fonte**, para cada par:
   - abrir a fonte com `read` (página do DOI, arXiv, página do editor, PDF aberto) e localizar o
     trecho que sustenta ou contradiz a afirmação; registrar seção/página ou citação curta;
   - classificar: `SUPPORTED` · `PARTIAL` (sustenta parte, ou com escopo menor) ·
     `NOT_SUPPORTED` (não trata do ponto ou diz outra coisa) · `CONTRADICTS` ·
     `UNVERIFIABLE` (sem acesso);
   - conferir força: a afirmação é mais forte, mais geral ou mais causal que a fonte?
   - conferir fonte secundária: o texto cita um levantamento para um resultado original?
4. **Afirmação sem citação** que depende de literatura (fato histórico, resultado alheio,
   "é amplamente usado") também é achado (`citation`, ação "citar fonte verificada ou
   remover").
5. **Retratação/correção**: no registro Crossref da obra citada, campo `updated-by` com `type`
   `retraction` ou `correction` (fonte `retraction-watch` ou `publisher`); o aviso de retratação
   em si traz `update-to`. Achado `critical` se a afirmação depende do resultado retratado.

## Onde procurar

- DOI → `https://doi.org/<doi>` (página) ou `https://api.crossref.org/works/<doi>` (JSON com
  `title`, `author`, `issued`, `container-title`, `updated-by`). DOI que não resolve: conferir
  `https://doi.org/api/handles/<doi>` (`responseCode` 100 = DOI inexistente).
- arXiv → `https://arxiv.org/abs/<id>`.
- Sem DOI → `web_search` com título exato entre aspas; confirmar no site do editor.
- OpenAlex exige chave desde fev/2026: não usar sem chave configurada fora do repositório.

## Tipos de achado

`reference` (entrada inexistente, metadado divergente, quimérica, retratada) · `citation`
(fonte não sustenta, sustenta parcialmente, é secundária, ou falta citação) · `overclaim`
(afirmação mais forte que a fonte). Em cada achado: afirmação literal, chave BibTeX, o que foi
aberto (URL), trecho/localização encontrada, estado e ação mínima.
