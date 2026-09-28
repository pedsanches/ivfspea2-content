# Pesquisa de engenharia — ambiente de escrita científica no Oh My Pi

Consulta: 2026-09-24. OMP instalado: `omp/18.3.0` (Homebrew). Código-fonte lido: tag
`v18.3.0` de <https://github.com/can1357/oh-my-pi> (commit `62bc57b`), docs empacotadas
(`omp://*.md` = `docs/` do mesmo repositório).

Tipos de fonte: **A** documentação oficial · **B** código-fonte atual · **C** diretriz
institucional · **D** literatura/guia científico · **E** comunidade · **F** opinião individual.
Decisões: **ADOPT**, **ADAPT**, **REJECT**, **EXPERIMENT**.

Este documento registra só o que mudou o desenho. Relatórios brutos das buscas não foram
versionados.

## 1. Premissas do pedido que a evidência corrigiu

| Premissa | Evidência atual | Consequência no desenho |
|---|---|---|
| É preciso desabilitar Claude/Codex/Gemini para isolar o ambiente | Raízes **de usuário** estrangeiras (`~/.claude`, `~/.codex`, `~/.gemini`, `~/.config/opencode`, …) já não carregam por padrão: `enabledProviders` vazio (B: `capability/index.ts:45-56,334-342`). Raízes **de projeto** carregam sempre. | O overlay científico fixa `enabledProviders: []` e desliga só *discovery providers*; nenhum *model provider* (`anthropic`, `openai-codex`) é tocado. |
| `.omp/AGENTS.md` é o lugar do contexto do projeto | `.omp/AGENTS.md` (prioridade 100) sombreia o `AGENTS.md` da raiz na mesma profundidade (B: `capability/context-file.ts:30-37`), para **todos** os perfis. Subagentes **nunca** recebem arquivos `AGENTS.md` (B: `task/structured-subagent.ts:506`). | Nenhum `.omp/AGENTS.md`. O `AGENTS.md` de engenharia continua intacto. O mapa científico entra só na sessão principal lançada pelo launcher (`--append-system-prompt`). |
| `RULES.md` é contexto como outro qualquer | `RULES.md` vira regra *always-apply* e é repassado aos subagentes (`rules: session.rules`, B: `structured-subagent.ts:511`); `--append-system-prompt` não é (B: `task/executor.ts`, relatório do scout). | Invariantes vão para `.omp/RULES.md`, o único canal que alcança escritor, revisores e editor. |
| Comandos podem fixar modelo/agente | Comandos de arquivo aceitam só `description`/`argument-hint`; não fixam modelo nem agente (B: `extensibility/slash-commands.ts`, `utils/command-args.ts:50-85`). | Comandos são roteiros para a sessão principal, que despacha agentes pela ferramenta `task`. |
| Perfil nomeado é só configuração | `--profile` isola também autenticação (`agent.db`), sessões e caches; não há *fallback* para as credenciais do perfil padrão (B: `utils/src/dirs.ts:317-320,851-853`). Ao ativar o perfil, o OMP exporta `OMP_PROFILE` e `PI_CODING_AGENT_DIR` para os processos filhos (B: `utils/src/dirs.ts:554-557`). `models.yml` fica no diretório do perfil (B: `sdk.ts:1397`), e `apiKey` com `!` roda um comando em `/bin/sh` a cada token que falta em cache (B: `config/resolve-config-value.ts:54-146`), com precedência sobre credencial guardada (B: `ai/src/auth/cascade.ts:287-307`). A Anthropic troca o refresh token a cada renovação (B: `ai/src/auth/refresh.ts:316-322`) e encerra a concessão ~30 dias depois do login interativo (B: `ai/src/registry/oauth/anthropic-constants.ts:2-8`). | Credenciais emprestadas do perfil padrão por `.omp/science/models.yml` (`omp token` com `env -u` das variáveis do perfil); nenhum login no perfil científico. |
| `workflowz`/`orchestrate` e `/vibe` são primitivas de orquestração | São palavras mágicas que injetam contratos genéricos por turno (A: `magic-keywords.md`); `/vibe` só usa os agentes empacotados `sonic`/`task` (A: `vibe-mode.md`). | Não usados. O *gate* é um roteiro explícito com agentes próprios e saída estruturada. |
| Domínio de ML/genômica | O repositório é de otimização evolutiva multiobjetivo; ML aparece só nos classificadores de FLA e no controlador. | *Checklist* de benchmarking de MOEAs; REFORMS/vazamento só para a parte de FLA. |

## 2. Oh My Pi

| Fonte | Tipo | Data | Insight | Decisão |
|---|---|---|---|---|
| `docs/config-usage.md`, `docs/settings.md` | A | 2026-09-24 | Precedência `defaults < global/perfil < projeto < --config < runtime`; arrays substituem; `.omp/config.yml` só é lido no **cwd** (sem subir diretórios). | ADOPT: launcher faz `cd` para a raiz. |
| `docs/context-files.md` | A | 2026-09-24 | Contexto sobe até o `.omp/` não vazio mais próximo; `disabledExtensions` desliga um arquivo; `disabledProviders` compartilha o espaço de nomes entre *discovery* e *model providers*. | ADOPT |
| `docs/task-agent-discovery.md`; B `discovery/helpers.ts:281-395` | A/B | 2026-09-24 | Frontmatter de agente: `name`, `description`, `tools`, `spawns`, `model` (lista, aceita `@papel`), `thinking-level`, `output`, `blocking`, `autoloadSkills`, `read-summarize`, `prewalk`, `advisor`; `yield` é adicionado a toda lista explícita de ferramentas. `.claude/agents` não é lido. | ADOPT |
| B `tools/yield.ts`, `task/executor.ts:689-863`, `tools/jtd-to-json-schema.ts` | B | 2026-09-24 | `output` aceita JSON Schema ou JTD; `strict` falha a execução após 3 tentativas inválidas; `permissive` só avisa. | ADOPT: revisores com JSON Schema fechado e `schemaMode: strict`. |
| B `config/model-resolver.ts:1000-1010`; `settings-schema.ts:494-497` | B | 2026-09-24 | Papéis personalizados valem se forem chave de `modelRoles` em qualquer camada; `modelRoleStorage: project` grava as trocas do `/model` em `<cwd>/.omp/config.yml`. | ADOPT: papéis `writer`, `editor`, `scientific_review`, `evidence_review`, `quant_audit`. |
| `docs/skills.md`; B `system-prompt.md:25-33` | A/B | 2026-09-24 | Só `name: description` entra no prompt; o corpo é lido sob demanda por `skill://`; `alwaysApply`/`globs` não afetam skills; `hide` tira da listagem. | ADOPT: *progressive disclosure* com `references/`. |
| `docs/advisor-watchdog.md` | A | 2026-09-24 | O advisor revê cada turno e injeta conselhos na sessão principal; `WATCHDOG.yml` na raiz (existente, não versionado) define um advisor com `gpt-6-astra`. | REJECT no perfil científico: misturaria o revisor à redação. `advisor.enabled: false` fixado. |
| `docs/prewalk.md` | A | 2026-09-24 | Na primeira edição troca para o papel `smol`. | REJECT para escritor/editor: a escrita passaria ao modelo barato. |
| B `modes/rpc/rpc-mode.ts:1286-1330` | B | 2026-09-24 | `omp --mode rpc` + `get_state`/`get_available_commands` devolvem prompt de sistema e comandos sem chamar modelo. | ADOPT como teste de isolamento. |
| B `cli/profile-alias.ts:155-183,301-380` | B | 2026-09-24 | `--alias` grava uma função no `~/.zshrc`, sem `cd` nem overlay. | REJECT como launcher principal; opção documentada. |

## 3. Normas institucionais e integridade

| Fonte | Tipo | Data | Insight | Decisão |
|---|---|---|---|---|
| [PPGCC — Legislação e normativas](https://ppgcc.inf.ufg.br/p/35372-legislacao-e-normativas) | A/C | 2026-09-24 | Página atualizada em 28/05/2026; regulamento por coorte (CEPEC 1983/2026 para ingresso ≥ 2026/1; 1622/2018 para os demais). | ADOPT: índice das normas; ingresso do autor decide o regulamento. |
| [Resolução INF nº 02/2023/PPGCC](https://files.cercomp.ufg.br/weby/up/1289/o/Resolucao_PPGCC_n_02_2023_Formato_de_dissertacoes_teses.pdf) | C | 2026-09-24 | Vigente. Art. 2º: monográfico ou escandinavo; Art. 3º: a opção "deverá constar na contra capa do documento". | ADOPT: modelo monográfico preservado; declaração do formato segue pendente (`REVISION_PLAN.md` §5). |
| [Resolução INF nº 002/2024/PPGCC](https://files.cercomp.ufg.br/weby/up/1289/o/SEI_4897992_Resolucao_002_2024_PPGCC.pdf) | C | 2026-09-24 | Mestrado com 1ª matrícula ≥ 2023/2: um aceite definitivo antes de pedir a defesa. | ADOPT no *checklist* de depósito. |
| [classe-inf](https://ww2.inf.ufg.br/~longo/classe-inf/classe-inf.html) | B | 2026-09-24 | Classe do INF mantida por docente; base de `inf-ufg.cls`. Não há template formalmente declarado "oficial" pelo PPGCC. | ADOPT: preservar `inf-ufg.cls` e o derivado `inf-ufg-tectonic.cls`. |
| [SIBI/UFG — BDTD](https://bc.ufg.br/n/33055-procedimentos-para-envio-das-teses-e-dissertacoes-para-publicacao-na-bdtd), [ficha catalográfica](https://bc.ufg.br/p/3397-ficha-catalografica) | C | 2026-09-24 | TECA via SEI; ficha só pelo gerador oficial. | ADOPT: agentes nunca redigem a ficha. |
| [Portaria CNPq nº 2.664/2026](https://www.in.gov.br/web/dou/-/portaria-cnpq-n-2.664-de-6-de-marco-de-2026-691779232) | A | 2026-09-24 | Art. 9º, I, "c": declarar IAG "em qualquer fase … a ferramenta utilizada e a finalidade"; "d": vedada submissão de conteúdo de IAG como autoria humana. | ADOPT: regra de proveniência; `AI_ASSISTANCE_LOG.md` continua sendo o registro. |
| [Guia de Integridade Acadêmica UFG 2024](https://files.cercomp.ufg.br/weby/up/680/o/Guia_de_integridade_acade%CC%82mica_-_2024_-_com_alterac%CC%A7o%CC%83es.pdf), cap. 9 | C | 2026-09-24 | Orientativo: transparência, verificação humana, IA não é autora. | ADOPT |
| CAPES — Nota Técnica nº 3/2025, Ofício-Circular nº 5/2026 | E | 2026-09-24 | Citados só em fontes secundárias; não localizados na CAPES. | EXPERIMENT: não citar como norma. |
| Políticas IEEE, ACM (CFP GECCO 2026), Springer Nature, arXiv | A | 2026-09-24 | IA nunca é autora; declaração em *Acknowledgments* (IEEE/ACM) ou *Methods* (Springer); Springer veda imagem gerada por IA. | ADOPT: declaração por veículo em `thesis-structure`. |
| ABNT NBR 14724:2024, 10520:2023, 6023 (2018 + errata; 3ª ed. 2025), 6028:2021 | D/E | 2026-09-24 | Edições confirmadas só por bibliotecas universitárias e guias; texto ABNT pago não lido. NBR 10520:2023 trocou o sobrenome em caixa alta por inicial maiúscula; NBR 6028:2021 deixou de exigir voz ativa no resumo. | ADAPT: tratadas como `[INFERÊNCIA]` até conferência na UFG; nenhuma "correção para ABNT" contra o PPGCC ou a classe. |

## 4. Escrita científica em PT-BR

| Fonte | Tipo | Data | Insight | Decisão |
|---|---|---|---|---|
| Gopen & Swan (1990), *The Science of Scientific Writing* ([PDF](https://www.usenix.org/sites/default/files/gopen_and_swan_science_of_scientific_writing.pdf)) | D | 2026-09-24 | Clareza vem da posição: sujeito perto do verbo, informação nova no fim, elo com a frase anterior no início. | ADOPT como critério de revisão de frase. |
| Sword (2012), *Zombie Nouns* ([PDF](https://www.lsu.edu/hss/english/files/university_writing_files/item51054.pdf)) | D | 2026-09-24 | Nominalização é problema quando apaga agente e ação; conceito técnico nominalizado é legítimo. | ADOPT (teste funcional). |
| Kobak et al., *Science Advances* 2025 ([arXiv:2406.07016](https://arxiv.org/abs/2406.07016)) | D | 2026-09-24 | O excesso de vocabulário pós-LLM é de palavras de estilo, não de conteúdo. | ADAPT: justificativa para critério funcional, não lista de palavras. |
| [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | E | 2026-09-24 | Padrões estruturais (ênfase vazia, "não X, mas Y", tríades, travessão em excesso, fecho genérico); a própria página diz que não prova autoria. | ADAPT: catálogo de padrões, nunca detector. |
| Hyland, via [CASRAI](https://casrai.org/guides/hedging-in-academic-writing) | D/E | 2026-09-24 | *Hedge* e *booster* calibram a força da evidência e variam por seção. | ADOPT |
| [USP/SIBiUSP, Diretrizes 2016](http://biblioteca.puspsc.usp.br/wp-content/uploads/2017/04/pdfFiles_Caderno_Estudos_9_PT_1_2016-1.pdf), §2.1 | C | 2026-09-24 | Evitar estrangeirismos, salvo vocabulário técnico padronizado. | ADOPT com a regra de terminologia do perfil. |
| [UnB/FAC, *Vamos Ser Claros?*](https://bdm.unb.br/bitstream/10483/29067/2/2021_DanielDiasAfonso_LucasDeLacerdaLudgero_produto.pdf) (TCC, n = 59) | C/D | 2026-09-24 | 81,4% preferem linguagem objetiva e direta; "uma frase, uma ideia" (Cervo, Bervian e Silva). | ADOPT |
| Estudo quantitativo de marcadores de LLM em PT-BR | — | 2026-09-24 | Não encontrado. | A lista em PT-BR é convenção editorial por analogia, marcada `[INFERÊNCIA]`. |

## 5. Metodologia do domínio (EMO e FLA)

| Fonte | Tipo | Data | Insight | Decisão |
|---|---|---|---|---|
| Bartz-Beielstein et al. (2020), [arXiv:2007.03488](https://arxiv.org/abs/2007.03488) | D | 2026-09-24 | Oito tópicos de benchmarking (objetivos, problemas, algoritmos, medidas, análise, desenho, apresentação, reprodutibilidade). | ADOPT |
| López-Ibáñez, Branke, Paquete (2021), ACM TELO, [arXiv:2102.03380](https://arxiv.org/abs/2102.03380) | D | 2026-09-24 | Repetibilidade × reprodutibilidade × replicabilidade em EC. | ADOPT |
| Derrac et al. (2011), SWEVO | D | 2026-09-24 | Comparações múltiplas sem correção perdem controle do FWER. | ADOPT |
| Arcuri & Briand (2014), STVR | D | 2026-09-24 | Mann–Whitney + Â12 como par mínimo para algoritmos estocásticos. | ADOPT |
| Benavoli, Corani, Mangili (2016), [JMLR](https://jmlr.org/papers/v17/benavoli16a.html) | D | 2026-09-24 | Pós-teste por posto médio depende do conjunto de algoritmos. | ADOPT (Apêndice C já trata o posto como descritivo). |
| Ishibuchi et al. (2018), *Evol. Comput.* | D | 2026-09-24 | O ponto de referência do HV pode inverter rankings. | ADOPT |
| Brockhoff, Tušar et al. (2016), COCO bbob-biobj | D | 2026-09-24 | Conjunto de referência e normalização quando a fronteira é desconhecida. | ADAPT (RWMOP). |
| Eggensperger, Hutter et al., [arXiv:1705.06058](https://arxiv.org/abs/1705.06058) | D | 2026-09-24 | *Over-tuning*: reportar instâncias fora do ajuste. | ADOPT (12 × 39 instâncias). |
| Lakens (2017, 2018) | D | 2026-09-24 | `p > 0,05` não é equivalência; TOST com margem. | ADOPT |
| Kapoor & Narayanan (2023), [Patterns](https://doi.org/10.1016/j.patter.2023.100804); REFORMS (2024), [Sci. Adv.](https://www.science.org/doi/10.1126/sciadv.adk3452) | D | 2026-09-24 | Vazamento entre treino e teste; incerteza; unidade de análise. | ADOPT só para FLA/controlador (validação por família é `[INFERÊNCIA]` aplicada). |
| Wolpert & Macready (1997), NFL | D | 2026-09-24 | Não há superioridade universal. | ADOPT |

## 6. Ferramentas determinísticas

| Fonte | Tipo | Data | Insight | Decisão |
|---|---|---|---|---|
| Log real `thesis/masters/build/main.log`, `main.blg` | B | 2026-09-24 | Tectonic/XeTeX + BibTeX clássico; hoje só 4 `Underfull \hbox`. | ADOPT: verificador de log com linha de base. |
| [LanguageTool — Java API](https://dev.languagetool.org/java-api.html) | A | 2026-09-24 | Requer Java 17 desde 6.6; a máquina tem Java 11; a API pública envia o texto a terceiros. | REJECT agora; EXPERIMENT futuro com servidor local. |
| LTeX+, TeXtidote | A | 2026-09-24 | Mesmo motor LanguageTool; bons mapeamentos LaTeX. | EXPERIMENT (depende de JRE 17 local). |
| Vale | A | 2026-09-24 | Sem estilo PT-BR maduro. | REJECT |
| ChkTeX, `checkcites` | A | 2026-09-24 | Exigem TeX Live, ausente; o `.aux` basta para citações não usadas/indefinidas. | ADAPT: lógica reimplementada em Python stdlib. |
| [Crossref REST](https://github.com/CrossRef/rest-api-doc), [Retraction Watch no Crossref](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/), [conteúdo por DOI](https://support.datacite.org/docs/datacite-content-resolver) | A | 2026-09-24 | Metadados por DOI sem chave. Conferido em registro real (Wakefield 1998): a obra retratada traz `updated-by` (`type: retraction`, `source: retraction-watch`); `update-to` fica no aviso. DOI inexistente: API de *handles* do doi.org (`responseCode` 100). | ADOPT (só metadados; nunca a prosa). |
| OpenAlex | A | 2026-09-24 | `mailto` deixou de valer em fev/2026; exige chave. | REJECT no script (sem segredo versionado). |
| `audit_scientific_text.py` (skill pessoal do autor, Codex) | B | 2026-09-24 | Auditor PT-BR conservador, só leitura, sem rede. | ADOPT: versionado como `scripts/science/prose_audit.py`. |

## 7. Skills e fluxos da comunidade

| Fonte | Tipo | Data | Insight | Decisão |
|---|---|---|---|---|
| `~/.codex/skills/write-scientific-manuscripts` (do autor) | B | 2026-09-24 | Regras de integridade mais fortes do levantamento; modos de edição; *preflight* que lê o perfil do projeto. | ADAPT: redistribuída nas skills OMP, com atribuição. |
| `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md` | C (projeto) | 2026-09-24 | Autoridades, vocabulário, famílias de evidência, linguagem de resultados. | ADOPT como fonte; as skills apontam para suas seções em vez de copiar. |
| `claesbackman/AI-research-feedback` (`backman-review`) | E | 2026-09-24 | Revisores paralelos por eixo com triagem de severidade. | ADAPT: três revisores independentes. |
| `poldrack/ai-peer-review`; relato de Poldrack no Substack | E/F | 2026-09-24 | Meta-revisão sem nome de modelo; Claude "suaviza problemas conceituais". | ADAPT: revisor científico de outra família de modelo. |
| `scunning1975/MixtapeTools` (`referee2`) | E | 2026-09-24 | "Nunca modificar o código do autor"; replicação cruzada. | ADOPT a regra; replicação cruzada fica a critério do auditor. |
| `lcrawfurd/claude-skills` (`paper-review`) | D (agrega) | 2026-09-24 | Frameworks citáveis de revisão (Edmans, Nyhan, Humphreys, Blattman). | ADAPT como perguntas de contribuição. |
| `PHY041/claude-skill-citation-checker`, `TheBoxGuy32/verify-citations` | E | 2026-09-24 | Verificação multi-base e de retratação. | ADAPT: reimplementado (`bib_check.py`), sem instalar. |
| `Imbad0202/academic-research-skills` | E | 2026-09-24 | Suíte grande (CC BY-NC 4.0), custo de contexto alto. | REJECT |
| `andrehuang/academic-writing-agents` (MIT) | E | 2026-09-24 | Agentes no formato do Claude Code (o OMP não os lê). | ADAPT só os papéis. |
| `kgraph57/paper-writer-skill` | E | 2026-09-24 | Domínio clínico; tabela "humanizer" derivada da Wikipedia. | REJECT a skill; ADAPT dois padrões (travessão, negação-contraste). |
| `openai-review` (`ChicagoHAI/OpenAIReview`) | E | 2026-09-24 | Depende de `pip install openaireview`, não auditado. | REJECT |
| "Clara/Claire" | — | 2026-09-24 | Nenhuma ferramenta científica atual identificada com esse nome. | Não integrado. |

## 8. Incertezas abertas

- Edições ABNT não conferidas no texto da ABNT; qual edição o SIBI/UFG exige.
- Data de ingresso do autor (define CEPEC 1622/2018 ou 1983/2026).
- Aplicabilidade formal da Portaria CNPq 2.664/2026 a discente sem bolsa CNPq; orientação CAPES não localizada em fonte primária.
- LanguageTool local depende de JRE 17 (não instalado).
