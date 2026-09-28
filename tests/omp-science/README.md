# Kit de testes do ambiente de escrita científica (Oh My Pi)

Procedimento dos testes A–J descritos em `docs/ai-scientific-writing/arquitetura.md`
(§Matriz de testes). As fixtures abaixo são **deliberadamente sintéticas** — não trechos da
dissertação — e o gabarito diz o que cada revisor deve achar. Resultados de cada rodada:
`docs/ai-scientific-writing/evaluation.md` (2026-09-25).

A sessão de referência é a do perfil científico (`scripts/omp-science`); diagnóstico sem
chamada de modelo: `scripts/omp-science --check`.

## Fixtures (`fixtures/`)

| Fixture | Teste | Conteúdo |
|---|---|---|
| `overclaim.tex` | C | Resultados falsos com: prova sem ablação, generalização a "problemas de otimização multiobjetivo", `p>0,05` tratado como "nunca pior". |
| `ref_falsa.tex` + `ref_falsa.bib` | D | `hollander2023dissimilar` inventada (DOI não registrado) e `deb2002fast` com ano e coautor errados (DOI verdadeiro). |
| `ref_claim.tex` + `ref_claim.bib` | E | Referências reais com metadados corretos; duas afirmações não são sustentadas (Holm como controle de FDR; NFL sobre fronteira de Pareto) e uma correta (Wilcoxon pareado). |
| `numeros.tex` + `numeros.csv` | F | Fonte declarada com semente fixa; texto com duas divergências (contagem de vitórias; mediana de ZDT1) e um número correto (5,2% em WFG9). |
| `escrita.tex` | B | Parágrafo com prosa formulaica ("Neste contexto", "é importante destacar", "não é apenas X, mas Y"), números e citação corretos a preservar. |
| `gate.tex` | J | Alvo do fluxo completo: uma divergência numérica à esquerda do `numeros.csv`, uma afirmação causal sem ablação e uma citação real que não sustenta a frase (`ref_claim.bib`). |
| `testcase_d.bib`, `testcase_e.bib` | — | Cópias usadas apenas na verificação direta do `bib_check.py` (E é a forma corrigida; a .bib da dissertação tem o DOI não registrado de `holm1979simple`, apontado no relatório). |

## Gabarito

| Teste | O que deve aparecer |
|---|---|
| **A** — isolamento | `scripts/omp-science --check`: PASS em descoberta estrangeira, papéis, perfil, credenciais emprestadas do perfil padrão, skills, comandos e agentes `.omp/`, e "nada de outros harnesses"; credencial ausente no OMP normal aparece como WARN.
| **B** — escritor | `escrita.tex` editado preservando 37, 51, 0,804, `\cite{vargha2000critique}` e o escopo; fórmulas de abertura e adjetivos vazios removidos; o bloco "guarda" de `claims.py diff` lista mudanças de força apenas quando explicitamente justificadas.
| **C** — revisor científico (Teste C) | Achados de `overclaim`: sobre-afirmação derivada de contagem sem correção, causalidade sem ablação, `p>0,05` como "nunca pior", recomendação de uso sem evidência.
| **D** — referência falsa | `bib_check`: `not_found` no DOI de `hollander2023dissimilar`; `mismatch` em `deb2002fast` pelos campos divergentes (determinístico) — e o revisor de evidência confere a natureza da divergência.
| **E** — real, claim errado | Revisor distingue: Wilcoxon OK; Holm não controla FDR (é FWER); Wolpert & Macready não tratam de fronteira de Pareto descontínua; existência ≠ suporte em todos os casos.
| **F** — auditor quantitativo | Dois achados críticos de números (contagem e mediana de ZDT1), os números corretos listados em cobertura com comando ou arquivo, α = 0,05 como `NOT_APPLICABLE` (definicional).
| **G** — revisores somente leitura | `git status --porcelain` idêntico antes e depois de revisores; suas listas de ferramentas não contêm `edit`/`write`.
| **H** — compilação em cópia | Injete `Seção~\ref{sec:inexistente}`, `\cite{inexistente2026}` e rótulo duplicado numa cópia `thesis/masters` em `/tmp`, compile e rode `latex_check.py --compare`: três bloqueantes novos; os quatro *underfull* preexistentes permanecem "preexistente".
| **I** — economia de contexto | RULES.md e bloco de contexto anexados; sete skills, cinco agentes, seis comandos; zero nome de skill/agente/comando de `~/.claude`, `~/.codex`, `~/.agents`; `latency/tokens` comparados no registro da rodada.
| **J** — gate completo | `/gate fixtures/gate.tex` → inventário + bib dele; três revisores de modelos distintos rodam em paralelo; todo achado na tabela consolidada; editor altera apenas os aceitos; `claims.py diff` mostra só mudanças correspondentes a achados; compilação e `prose_audit` sem regressão nova. |

## Ordem rápida

Sem modelo: A (`scripts/omp-science --check`), H (precisa da saída do Tectonic), a parte
determinística de D e os testes de `scripts/science`
(`python -m pytest tests/python/test_science_checks.py -q`). Conferência direta com as
fixtures:

```bash
python3 scripts/science/prose_audit.py tests/omp-science/fixtures/escrita.tex
python3 scripts/science/claims.py inventory tests/omp-science/fixtures/numeros.tex
python3 scripts/science/bib_check.py --bib tests/omp-science/fixtures/testcase_d.bib \
  --aux /dev/null --online
```

Os testes que precisam de modelo (B, C, D, E, F, G, J) rodam em sessões do perfil:
`/gate <fixture>` para o J; para os individuais, peça na sessão "despache o agente X para o
alvo Y com schemaMode strict", que é exatamente o que o `/gate` faz nos passos 1 e 4.

## Custos e limites

- Cada revisor consome o modelo do seu papel; rodadas grandes de comparação multi-modelo
  devem usar agentes temporários com `model:` explícito (`docs/ai-scientific-writing/
  evaluation.md` faz isso com `zz-eval-*` e os remove ao fim).
- Contas de provedor têm ciclos de cota; se a rodada falhar com `usage_limit_reached`
  (OpenAI/Codex) ou `429`, espere o ciclo e rode de novo a partir de `evaluation.md`.
