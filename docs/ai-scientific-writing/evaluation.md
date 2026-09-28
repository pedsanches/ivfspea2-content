# Avaliação — rodada 2026-09-24/25

Registro de execução dos testes A–J de `tests/omp-science/` (gabarito lá). Sem
modificação do manuscrito em nenhum teste; cota de provedor impediu as execuções que
dependem de modelo, marcadas na tabela com "pendente".

## Resultado por teste

| Teste | Foi executado? | Resultado |
|---|---|---|
| **A** isolamento | sim (RPC, sem login) | 29 checks; 27 PASS; 2 WARN (login ausente, esperado). Sem FAIL: descoberta estrangeira off, `modelRoleStorage: project`, advisor off, 7 skills, 5 agentes, 6 comandos, RULES.md fixado, contexto anexado, CLAUDE.md ausente, zero contaminação de `~/.claude`, `~/.codex`, `~/.agents` (testada positivamente: com `enabledProviders: ["\*"]` o canário detecta 10 nomes estrangeiros). |
| **B** escritor | não (cota) | Pendente — exigiria `writer` (imiteria o modo do `/revise`, sem revisores). Falha não bloqueante; re-executar com cota. |
| **C** revisor (Teste C) | não (cota) | Despachado 2×; ambos falharam ao chamar modelo: o papel `@scientific_review` (gpt-6-astra) sem cota, e o fallback caiu no padrão (`claude-opus-5-5`) com `429 rate_limit` e janela ~3,9 h. Nada indica problema no agente. |
| **D** referência falsa | metade via script | `bib_check.py --online` marca `hollander2023dissimilar` como `not_found` (DOI não registrado, via API de handles) e `deb2002fast` como `mismatch` (ano 2004 no .bib vs 2002 no Crossref; autores divergentes). Revisor em LLM fica pendente. |
| **E** real, claim errado | não | Pendente (cota de provedor). |
| **F** auditor quantitativo | sim (gpt-6-sol, `@quant_audit`) | 2 achados críticos: contagem de vitórias ("em quatro … não perdeu em nenhuma" → 3 vitórias, 2 derrotas, uma significativa após Holm) e a mediana de ZDT1 (0,0213 → 0,0230, recomputada); números corretos listados em `coverage` com comando ou arquivo (n=20/instância, 5,2% em WFG9); α = 0,05 em `not_checked` como `NOT_APPLICABLE` (definicional). Nenhum falso positivo; saída estrita validada. |
| **G** revisores read-only | sim | `git status --porcelain` idêntico antes e depois de 3 revisores; suas listas de ferramentas: scientific/evidence = `read,grep,glob[,web_search]`, quant = `read,grep,glob,bash`. A auditoria escreveu script auxiliar apenas em `/tmp` (`audit_numeros.py`), nada versionado. |
| **H** compilação em cópia | sim | Cópia `/tmp/thesis-copy` (intocada a real), 3,4 s de build; `--save-baseline` e `--compare`: 4 *underfull* preexistentes; depois de injetar rótulo duplicado, `\ref` e `\cite` inexistentes e `\input` de tabela ausente, o comparador acusou exatamente os bloqueantes novos e os preexistentes ficaram de fora (exit 1). Tectonic sai com código 0 em build com referência indefinida — o check adiciona o que faltava. |
| **J** gate (Teste J) | não | Pendente — fluxo completo; revisores individuais falharam por cota de provedor. |

### Limitação de cota de provedor

Na rodada 2026-09-25, `openai-codex` estava com cota esgotada (`usage_limit_reached` em
gpt-6-astra, gpt-6-sol e gpt-5.6-luna) e `anthropic` com `429` e janela de ~3,9 h. Isto
bloqueou os testes B, C, E e J — nada indica defeito no ambiente: o mesmo papel de
modelo resolve e o agente `quant-auditor` completou quando havia cota. Re-executar os
testes pendentes quando a cota reabrir.

### Avaliação multi-modelo (parcial, aguardando cota)

Papéis dos testes A–J em `tests/omp-science/README.md`; para comparação, use os
**agentes temporários** copiando um dos existing agents com `model:` concreto (ex.:
`model: anthropic/claude-opus-5-5:high` ou `openai-codex/gpt-6-astra:high`) e o mesmo
corpo; remover ao fim. O `scripts/science/omp_env_check.py` é read-only: não interfere
em testes de modelo. Estimativa de custo por 1M tokens (via `omp models --json`):
`claude-opus-5-5` = 4/20 USD, `gpt-6-astra` = 10/50 USD (input/output).

## O que já funciona sem modelo

- `make thesis-lint` (prose_audit + latex_check offline + bib offline): nenhum sinal
  bloqueante no estado atual da dissertação; 39 advisory — coerentes com o perfil de
  voz (travessão em 4,9 por mil palavras etc.): o detector sinaliza padrões, o revisor
  humano (ou LLM, com contexto) decide em cada trecho.
- `python3 scripts/science/bib_check.py --online` na tese (53 entradas): 16 `verified`
  com DOI, 1 `mismatch` (título do conceito Zenodo diverge do título do `.bib`,
  similaridade 0,38), **1 `not_found`**: `10.2307/4615733` de `holm1979simple` não está
  registrado no sistema DOI (`responseCode: 100` da API de handles do doi.org) — a URL
  JSTOR citada é estável, o DOI é que não existe. Ação sugerida (decisão do autor):
  remover o campo `doi` ou registrar o DOI da edição correta; sempre conferir antes.
- 35 entradas da tese estão sem DOI, 26 delas com candidato Crossref de similaridade
  1,0 (ex.: `deb2002fast` → `10.1109/4235.996017`). Lista completa em
  `.omp/runs/bib-thesis-online.txt`; acrescentar é decisão do autor, uma a uma.
- `python3 scripts/science/claims.py inventory` no fixture F: 3 frases, 10 números.
  `diff` em texto sintético detecta mudança de número, citação, rótulo e marcador de
  força, com exit 3 em `--strict`.

## Custo por papel (do catálogo `omp models --json`, USD por 1M tokens)

| Papel | Modelo | input | output |
|---|---|---|---|
| writer/editor | claude-opus-5-5 | 4,00 | 20,00 |
| scientific/evidence_review | gpt-6-astra | 10,00 | 50,00 |
| quant_audit | gpt-6-sol | 2,00 | 10,00 |

Um `/gate` sobre uma seção inteira (3 revisores + editor + checagens) gira na faixa de
2–4 USD usando os papéis padrão (gpt-6-astra + editor Opus); um `/gate` de capítulo
completo (30–40 mil tokens por revisor) na faixa de 8–15 USD.

## Limites declarados

1. Testes B, C, E e J: pendentes de cota de provedor — re-run dos testes
   (`tests/omp-science/README.md`) quando a janela de cota reabrir.
2. Sem chave de OpenAlex (a antiga via `mailto` foi descontinuada); toda a via externa
   é `Crossref` + `doi.org`.
3. `latex_check.py --compare` depende de `make thesis` prévio (com `--save-baseline`
   antes da alteração); `make thesis-tables-check` escreve `results/thesis/` no lugar
   (verificado em `build_all.py`) — é etapa do autor, não de revisor.
4. `prose_audit.py` é conservador: 39 sinais na dissertação atual são todos advisory
   — o perfil de voz explica que trechos do texto atual são o registro aprovado; o
   detector sinaliza, o revisor decide (validado com detector negativo no "para todo j").
