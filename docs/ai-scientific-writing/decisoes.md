# Decisões finais — ADOPT / ADAPT / REJECT / EXPERIMENT

Fontes com data e URL: `research.md`; comportamento verificado em `evaluation.md`.

## ADOPT (operando)

- Perfil `scientific-writing` + launcher `scripts/omp-science` (isolamento de sessões e
  settings do perfil padrão).
- Credenciais emprestadas do perfil padrão (2026-09-25): `.omp/science/models.yml` define
  `apiKey: "!env -u OMP_PROFILE … omp token <provedor>"`, e o launcher o instala no perfil.
  Um login só, e só o perfil padrão renova o OAuth. Descartados: login separado no perfil
  (duas concessões, e a Anthropic expira a concessão em ~30 dias, logo dois logins mensais);
  cópia das credenciais (a Anthropic troca o refresh token a cada renovação, e a primeira
  cópia a renovar invalida a outra); auth-broker local (serviço permanente para um caso de
  uma máquina); abandonar o perfil (a `config.yml` pessoal, com `modelRoles`,
  `retry.fallbackChains` e `task.agentModelOverrides`, entraria no ambiente).
- `.omp/RULES.md` — invariantes *sticky*, o único canal que alcança todo subagente.
- 5 agentes em `.omp/agents/` com schema de saída estrita; revisores read-only.
- 7 skills progressivas com `references/` sob demanda (`ai-provenance` incluída).
- 6 comandos de fluxo (`/revise`, `/draft-section`, `/gate`, `/verify-evidence`,
  `/audit-numbers`, `/final-pass`).
- Papéis de modelo + fallbacks em `.omp/config.yml`; `modelRoleStorage: project`.
- Verificadores determinísticos `scripts/science/` + `make thesis-lint`
  (`prose_audit` vendored da skill pessoal do autor; `claims`; `latex_check` com
  baseline; `bib_check` com Crossref, handles do doi.org e Retraction Watch).
- Bash `deny` patterns no overlay para subagentes (`git reset*`, `git stash*`,
  `git commit*`, `git push*`, `rm -rf*`): protege o estado não commitado do autor.
- Padrões de revisão multi-agente da comunidade (backman, poldrack, referee2,
  `paper-review`) como perguntas de contribuição e separação revisor/escritor.
- Checklist de benchmarking de MOEA/ML com fonte por item (25 itens), derivada da
  literatura lida (Bartz-Beielstein, Derrac, Arcuri & Briand, Benavoli, Ishibuchi,
  López-Ibáñez, Lakens, Kapoor & Narayanan, REFORMS, NFL).

## ADAPT (transformado)

- `SCIENTIFIC_WRITING_PROFILE.md`, `REWRITE_SPEC.md`, `REVISION_PLAN.md`,
  `data-sources.toml` continuam canônicos; as skills apontam para **seções** deles
  (§4, §4.1, §6–§8; §3.5; §2) em vez de copiar.
- Skill pessoal Codex `write-scientific-manuscripts`: conteúdo redistribuído nas skills
  OMP; script de auditoria vendored e estendido (dash-density, negation-correction,
  marcador `[NÃO VERIFICADO]`, correção do "TODO" × "para todo j").
- Verificação de citações: reescrita do zero (não instalada) com DOI original,
  handles e retratação; sinônimo de regra "nunca modificar o código do autor" (referee2)
  aplicado ao auditor quantitativo.
- Área de domínio: nada de guidelines médicas; MOEA (não bioinformática/genômica) —
  REFORMS/vazamento só para FLA/controlador, marcado como `[INFERÊNCIA]` aplicada.

## REJECT

- `.omp/AGENTS.md` — sombrearia o `AGENTS.md` da raiz para todos os perfis; contexto
  científico fica no launcher (`--append-system-prompt`).
- Advisor no perfil científico (`advisor.enabled: false` no overlay): misturaria revisor
  à redação. O `WATCHDOG.yml` da raiz (pré-existente, untracked) permanece intocado e
  só age em sessões onde o advisor é ligado.
- Prewalk (`prewalk.enabled: false`): a escrita trocaria para modelo barato na 1ª edição.
- `workflowz`/`orchestrate`/`/vibe`: contratos genéricos ou agentes genéricos; o gate é
  um roteiro explícito com agentes próprios e saída estruturada.
- OpenAlex (exige chave desde fev/2026); LanguageTool/TeXtidote (Java 17 ausente na
  máquina hoje); Vale (sem PT-BR); skills de terceiro instaladas verbatim (CC BY-NC,
  `pip install openaireview`, domínio clínico).
- `omp --alias` como launcher: sem `cd`, sem overlay, sem `--model @writer`.

## EXPERIMENT (planejado)

- LanguageTool local quando houver JRE 17; OpenAlex com chave externa ao repo;
  hunspell/aspell + dicionário pt_BR; e a comparação multi-modelo documentada em
  `evaluation.md` quando a cota de provedor reabrir.

## Pendências registradas para o autor

- `holm1979simple`: DOI não registrado (10.2307/4615733). **Decisão do autor
  (2026-09-25): deixar como está**; fica registrado em `evaluation.md` e em
  `.omp/runs/bib-thesis-online.txt`; a URL JSTOR citada na entrada é estável.
- `ivfspea2github`: título diverge do registro Zenodo (0,38) — conferir qual forma
  é a canônica para a referência.
- 35 entradas sem DOI na bibliografia da tese, 26 com candidato de similaridade 1,0
  (lista em `.omp/runs/bib-thesis-online.txt`); acrescentar é decisão do autor.
- `paper/ppsn2026` fora da reescrita, mantido; nada no ambiente o toca.
