# Relatório da intervenção — comentários do revisor externo (A001–A064)

## Rodada R19 — 2026-10-10

Executor: Claude Code (Anthropic), ambiente omp, com quatro subagentes de revisão independente
(somente leitura). O autor humano responde pelo texto; nenhuma decisão abaixo marcada como
"decisão do executor" foi aprovada pelo autor até a data deste relatório.

---

## A. Escopo e cobertura

**Estado de partida.** Commit `5a52253156a4a76a199c1a1a9abe3bae28174b85` ("thesis: consolidate R18
prose revision and defense notes"). Antes de editar havia alterações do autor já preparadas em
`paper/clei2026/` (README, `main.tex`, troca do symlink `figures` por arquivos) e o arquivo não
rastreado `WATCHDOG.yml`; nenhum deles foi tocado. Nada desta rodada foi commitado: o estado final
é a árvore de trabalho sobre esse commit, e `git diff 5a52253 -- <arquivo>` reproduz cada
alteração.

**Linha de base registrada antes das edições.**

| Item | Comando | Resultado |
|---|---|---|
| PDF | `make -C thesis/masters -B all` | 103 páginas; cópia em `/tmp/altino_base/main_base.pdf` (efêmera) |
| LaTeX | `python3 scripts/science/latex_check.py --save-baseline` | 3 itens, todos *underfull* (`pre/pre_resumo:3`, `tex/cap_V:32`, `main.bbl:222`) → `.omp/runs/latex-baseline.json` |
| Fotos de afirmações | `python3 scripts/science/claims.py snapshot` nos 10 capítulos, resumo, abstract e três apêndices | `.omp/runs/snapshots/thesis/masters/...` |
| Tabelas | `make thesis-tables-check` | "OK: tabelas e figuras estão sincronizadas"; `git status -- results/thesis` vazio antes e depois |

**Lido integralmente (estado atual e de partida):** `tex/cap_I.tex` a `tex/cap_IX.tex`,
`tex/cap_VII_complementares.tex`, `pre/pre_resumo.tex`, `pre/pre_abstract.tex`, `main.tex`,
`pos/apend_I.tex`, `pos/apend_II.tex`, `pos/apend_III.tex`; as tabelas geradas citadas nos
trechos alterados (`results/thesis/tab_controlador_wtl.tex`, `tab_hosts_geometria.tex`,
`tab_ativacao_robustez.tex`, notas das demais via diff); páginas 6–9, 14, 16, 26, 31 e 32 do PDF
de partida (para localizar as marcações do revisor). Lidos parcialmente: `REVISION_PLAN.md` (§1–§8),
`REWRITE_SPEC.md` (§1, §6), `SCIENTIFIC_WRITING_PROFILE.md` (§3–§4), `AI_ASSISTANCE_LOG.md`
(cabeçalho e últimas entradas), `data-sources.toml` (busca por remissões).

**Texto ativo × oculto × histórico.** Ativo: tudo o que `main.tex` inclui. Oculto: `pos/apend_I–III`
(não compilados); só `apend_III` recebeu um comentário LaTeX de advertência (sem alteração de
texto), porque afirma que o posicionamento não tem teste nem QP, o que contradiz a QP5. O
Apêndice A, gerado por `build_apendice_fontes.py`, ainda usa "pipelines publicados" e "desfecho";
não foi alterado (latente, §G). Histórico: blocos datados de `REVISION_PLAN.md`,
`REWRITE_SPEC.md` e `AI_ASSISTANCE_LOG.md` mantêm a numeração da época; foi acrescentada uma
tabela de correspondência em vez de reescrevê-los.

**Arquivos alterados (50, mais este relatório e a entrada proposta no log de IA):**

- Manuscrito: `main.tex`; `tex/cap_I.tex`, `cap_II.tex`, `cap_III.tex`, `cap_IV.tex`, `cap_V.tex`,
  `cap_VI.tex`, `cap_VII_complementares.tex`, `cap_VII.tex`, `cap_VIII.tex`, `cap_IX.tex`;
  `pre/pre_resumo.tex`, `pre/pre_abstract.tex`; `pos/apend_III.tex` (só comentário).
- Geradores (`src/python/thesis/`): `build_tab_tuning_ablacao.py`,
  `build_tab_ativacao_robustez.py`, `build_tab_confirmatorio.py`, `build_tab_controlador.py`,
  `build_tab_engenharia.py`, `build_tab_fla_dinamica.py`, `build_tab_hosts.py`,
  `build_tab_magnitude_confirmatoria.py`, `build_tab_wfg_exploratoria.py`, `build_fig_resultados.py`.
- Saídas regeneradas (`results/thesis/`): 14 tabelas (`tab_ablacao`, `tab_ativacao_robustez`,
  `tab_confirmatorio_wtl`, `tab_controlador_wtl`, `tab_dinamica_limiar`, `tab_dinamica_separacao`,
  `tab_dinamica_suite`, `tab_engenharia_wtl`, `tab_fla_modelos`, `tab_hosts_wtl`,
  `tab_magnitude_confirmatoria`, `tab_magnitude_confirmatoria_fora_ajuste`, `tab_tuning_c26`,
  `tab_wfg_exploratoria`) e `figures/fig_dtlz4_bimodal.pdf`.
- Orientação: `thesis/masters/README.md`, `REVISION_PLAN.md`, `REWRITE_SPEC.md`;
  `.omp/skills/thesis-structure/SKILL.md`, `.omp/skills/scientific-writing-ptbr/references/terminologia.md`,
  `.../references/voz.md`, `.omp/skills/scientific-argumentation/SKILL.md`,
  `.omp/skills/quantitative-audit/SKILL.md`, `.omp/agents/quant-auditor.md`, `.omp/agents/writer.md`,
  `.omp/commands/final-pass.md` (só remissões de capítulo e decisões terminológicas).
- Não alterados: `CLAUDE.md`, `AGENTS.md`, `data/`, `artifact/`, `bib/modelo-tese.bib`, classes,
  `data-sources.toml`, manifesto e checksums de release.

**Não verificado nesta rodada:** texto integral de Vargha–Delaney (2000), AR-MOEA e Mersmann et
al. (2011) (acesso pago/bloqueado); fidelidade das etapas 1 e 7 do IVF original (Cap. 2) à fonte
primária (ver §G-5); figura legada `fig/fluxo_ivf.pdf` (sem fonte editável, título interno em
inglês); demais citações dos Caps. 2–3 fora dos pares listados em §E.

---

## B. Mudanças estruturais

**Mapa origem → destino.**

| Origem (R18) | Destino (R19) | Arquivo | Rótulo |
|---|---|---|---|
| §1.2 Questões de pesquisa (QP1–QP5) | §5.1 Questões de pesquisa e organização da avaliação | `cap_V.tex` | `sec:questoes` (preservado) |
| §1.3 Contribuições | §1.2 | `cap_I.tex` | `sec:contribuicoes` |
| §1.4 Publicações derivadas | §7.8 | `cap_VII.tex` | `sec:publicacoes` (preservado) |
| §1.5 Organização do texto | §1.3 | `cap_I.tex` | `sec:organizacao` |
| Cap. 5 Experimentos | Cap. 5 Experimentação | `cap_V.tex` | `sec:Experiments` (preservado) |
| §5.6 Famílias de evidência e seus protocolos | §5.1.1 Famílias de evidência e respectivos protocolos (seção → subseção) | `cap_V.tex` | `sec:familias` |
| §5.1–§5.5 (plataforma, suítes, métricas, estatística, calibração) | §5.2.1–§5.2.5 sob a nova §5.2 Desenho experimental e protocolos (seção → subseção) | `cap_V.tex` | `sec:plataforma`, `sec:suites`, `sec:metricas`, `sec:estatistica`, `sec:calibracao`; novo `sec:desenho` |
| Cap. 6 Resultados (capítulo) | §5.3 Resultados da avaliação comparativa principal (capítulo → seção) | `cap_VI.tex`, sem `\chapter`, incluído após `cap_V` | `sec:results` |
| §6.1 Comparação principal contra o SPEA2 | §5.3.1 Vitórias, empates e derrotas contra o SPEA2 | `cap_VI.tex` | `sec:confirmatorio` |
| §6.2, §6.3, §6.4 | §5.3.2, §5.3.3, §5.3.4 Síntese da avaliação comparativa principal | `cap_VI.tex` | `sec:magnitude`, `sec:por_instancia`, `sec:sintese_resultados` |
| Caps. 7, 8, 9, 10 | Caps. 6, 7, 8, 9 | inalterados | inalterados |

**Remissões corrigidas.** Todas as ocorrências de `Capítulo~\ref{sec:results}` passaram a
`Seção~\ref{sec:results}`: `cap_VII.tex` (§7.0, §7.2 ×2), `cap_VII_complementares.tex` (abertura,
§6.2, §6.3 ×2, §6.4 ×2), `cap_VIII.tex` (×2), `cap_IX.tex` (×1) e, pelo gerador
`build_tab_tuning_ablacao.py`, a nota da Tabela de ablação. "Os Capítulos~\ref{sec:results}
e~\ref{sec:complementares}" passou a "a Seção ... e o Capítulo ...". `cap_II.tex` (multiplicidade)
mantém a remissão a `sec:publicacoes`, agora à frente (§7.8). `apend_II.tex` (oculto) remete a
`sec:Experiments`, que continua capítulo. `grep "Cap[íi]tulo~\\ref{sec:results}"` não retorna nada
em `tex/`, `pre/` nem `results/thesis/`. Nenhum `\ref` ou `\label` indefinido ou duplicado no log.

**Fontes que perderam função autônoma.** `cap_VI.tex` deixou de ser capítulo; recebeu comentário
de cabeçalho e continua ativo como §5.3 (escolha feita para manter o histórico do arquivo e o diff
revisável). `main.tex` explica a correspondência. Nenhum conteúdo foi apagado na migração: a
seção de QPs foi transferida com reescrita (ver C, A034–A040), a de publicações com reescrita (A053).

**Documentos de orientação.** `REVISION_PLAN.md`: tabela de correspondência de numeração após o
título; objetivo geral vigente (marcado como pendente de aprovação); regra de resposta única
no Cap. 7; novo §3 "Estado em 2026-10-10" (o antigo §3 virou §3a). `REWRITE_SPEC.md`: "Arquitetura
efetiva (R19)" na §6.1 e entrada R19 na §6.2. `README.md`: estado atual. Skills/agentes `.omp`:
mapa de capítulos e remissões ao "Cap. 8" → "Cap. 7"; `terminologia.md` com as decisões da §D.

---

## C. Resolução dos 64 comentários

Estados: **AT** atendido · **SD** diagnóstico atendido por solução diferente · **NA** não aplicado
com justificativa · **FA** fora da rodada por decisão do autor · **MS** marcação sem orientação
suficiente (defeito observável tratado só quando havia evidência própria). "p." = página do PDF de
partida (103 p.). Localização final por arquivo e rótulo; números de linha mudam.

| ID | Local original | Local no fonte de partida | Diagnóstico | Estado | Ação / justificativa | Local final | Verificação / pendência |
|---|---|---|---|---|---|---|---|
| A001 | p.1 título | `main.tex` `\titulo`; `pre_abstract.tex` título | — | FA | Não alterado | idem | `git diff` sem mudança nas duas linhas |
| A002 | p.6 "orçamento fixo" | `pre_resumo.tex:4` | termo não definido em texto autônomo | AT | resumo: "com o mesmo número máximo de avaliações"; corpo define "orçamento de avaliações" (Introdução ¶3; §4.1 distingue orçamento, consumo e cota). Recorrências em §D (N10) | `pre_resumo.tex`; `cap_I.tex` ¶3; `cap_IV.tex` `sec:acoplamento` | grep "orçamento fixo" em `tex/`,`pre/`: 0 |
| A003 | p.6 "comparadores e examina sua ativação" | `pre_resumo.tex:4` | referente indefinido; "sua" ambíguo | AT | resumo nomeia "sete outros algoritmos" e diz o que foi investigado (antecipação, controlador); no corpo "algoritmos comparados" definido em §5.2.1 | `pre_resumo.tex`; `cap_V.tex` `sec:plataforma` | revisão editorial: OK |
| A004 | p.6 "orçamentário" | `pre_resumo.tex:4` | idem A002 | AT | "limita a fração de avaliações do módulo" | `pre_resumo.tex` | — |
| A005 | p.6 "ordenação descritiva entre pipeline" | `pre_resumo.tex:4` | "pipeline" indefinido | AT | resumo: "acoplamentos ... vencem em 33, 22 e 1 ..., ordenação descritiva"; termo "pipeline" retirado de `tex/`/`pre/` e da nota da Tabela 6.4 (§D N12) | `pre_resumo.tex`; `cap_VII_complementares.tex` `sec:hospedeiros` | grep "pipeline" em `tex/`,`pre/`: 0 |
| A006 | p.6 "reanálise" | `pre_resumo.tex:4` | sem antecedente no resumo | SD | resumo não usa mais o termo; no corpo "reanálise" fica onde o estudo de origem é nomeado (§6.4: nova análise dos mesmos dados com validação mais estrita) | `cap_VII_complementares.tex` `sec:ativacao` | — |
| A007 | p.6 "não foi estabelecida" | `pre_resumo.tex:4` | ambíguo: não testada × testada sem êxito | SD | a atribuição foi examinada em parte (ablação, hospedeiros) e não isolada; texto: "sem isolar o papel do módulo, das regras, da configuração ou do hospedeiro" | `pre_resumo.tex`, `pre_abstract.tex` | revisão científica: escopo coerente com §7.2–§7.3 |
| A008 | p.8 "2" | sumário | sem comentário | MS | intenção não inferida; o sumário foi regenerado pela reestruturação | — | — |
| A009 | p.8 "1.4 Publicações derivadas" | `cap_I.tex` `sec:publicacoes` | — | AT | transferida para §7.8 (decisão do autor) | `cap_VII.tex` `sec:publicacoes` | PDF p.94 |
| A010 | p.8 "2 Embasamento Teórico" | `cap_II.tex:4` | ordem sem lógica declarada | SD | ordem mantida (hospedeiro → arranjo de hibridização → método auxiliar → instrumentos); abertura do capítulo explicita a lógica e por que a hibridização precede o IVF | `cap_II.tex` abertura | não reordenado: o IVF usa a classificação da §2.2 |
| A011 | p.9 "Paisagem de aptidão" | sumário 2.6/3.4 | tradução questionada; "aplicada a algoritmos" impreciso | SD | termo mantido (forma da área, palavras-chave, `terminologia.md`) e definido em §2.6; título 3.4 → "Análise de paisagem de aptidão em otimização multiobjetivo" | `cap_II.tex` `sec:paisagem`; `cap_III.tex` `sec:rw_paisagem` | decisão terminológica final do autor (§G-3) |
| A012 | p.9 "orçamento" | sumário 4.1 | sem comentário; título usa termo não definido | MS | título 4.1 → "Inserção do módulo e repartição das avaliações"; §4.1 define as três quantidades | `cap_IV.tex` `sec:acoplamento` | — |
| A013 | p.9 "seu" | sumário 5.6 | pronome ambíguo no título | AT | "Famílias de evidência e respectivos protocolos" | `cap_V.tex` `sec:familias` | — |
| A014 | p.9 "Experimentos" | Cap. 5 | capítulo curto separado dos resultados | AT | Cap. 5 Experimentação (decisão do autor) | `cap_V.tex` + `cap_VI.tex` | sumário PDF p.9 |
| A015 | p.9 "seu" | sumário 7.3 | sem comentário; mesma classe de A013 | MS | "Comparação de cada acoplamento com o respectivo hospedeiro" | `cap_VII_complementares.tex` `sec:hospedeiros` | — |
| A016 | p.9 "paisagem" | sumário | sem comentário; mesma classe de A011 | MS | ver A011 | — | — |
| A017 | p.14 "es45" | Lista de Algoritmos | número da página colado ao título | MS | defeito observável: `\l@algorithm` sem formatação; `main.tex` passa a usar o formato de `\l@figure`; legenda curta "Pseudocódigo do IVF/SPEA2" | `main.tex` (após `\providecommand{\listalgorithmcfname}`); `cap_IV.tex` `alg:ivf_spea2` | PDF p.14 renderizada: número alinhado à direita |
| A018 | p.15 "aproximar esse conjunto" | `cap_I.tex:5` | objeto do verbo ambíguo | AT | "encontrar soluções próximas desse conjunto de compromissos e distribuídas ao longo dele" | `cap_I.tex` ¶1 | — |
| A019 | p.15 "conflitam" | `cap_I.tex:15` | regência | AT | "são conflitantes" | `cap_I.tex` | — |
| A020 | p.16 "e é aí" | `cap_I.tex:22` | coloquial | AT | "é sobretudo nesses mecanismos que eles diferem" | `cap_I.tex` | — |
| A021 | p.16 "para quem" | `cap_I.tex:24` | sujeito indeterminado coloquial | AT | "quando se procura melhorar a convergência" | `cap_I.tex` | — |
| A022 | p.16 "A lacuna tem também" | `cap_I.tex:28` | lacuna não enunciada antes | AT | ¶ anterior termina "essa ausência é a lacuna de que parte esta dissertação"; ¶ seguinte "A escolha do SPEA2 não decorre apenas dessa ausência" | `cap_I.tex` ¶5–6 | — |
| A023 | p.16 "sua" | `cap_I.tex:28` | sem comentário; "a sua seleção ambiental" ambíguo (SPEA2 × hipótese) | MS | "a seleção ambiental do SPEA2" | `cap_I.tex` ¶6 | — |
| A024 | p.16 "Capítulo 4" | `cap_I.tex:28` | remissão interna fora do roteiro | AT | remissão removida do corpo da Introdução; remissões só no roteiro (§1.3) | `cap_I.tex` | grep `ref{` em `cap_I.tex`: única linha com remissões é a do roteiro (§1.3) |
| A025 | p.16 "Sob" | `cap_I.tex:28` | sugestão "sobre" | SD | "sob a aptidão" é correto (sob o regime de); frase reescrita: "Com a aptidão do SPEA2 como critério de seleção" | `cap_I.tex` ¶6 | ocorrências de "sob a aptidão" nos Caps. 3–4 e 7 mantidas (uso correto) |
| A026 | p.16 "os desfavorece uns" | `cap_I.tex:28` | construção pesada | AT | "onde a seleção do SPEA2 penaliza a proximidade entre eles" | `cap_I.tex` ¶6 | — |
| A027 | p.16 "aquelas duas" | `cap_I.tex:30` | referente distante | AT | "substitui as duas decisões herdadas: ..." com as decisões nomeadas | `cap_I.tex` ¶7 | — |
| A028 | p.16 "módulo" | `cap_I.tex:30` | referente | AT | "o módulo IVF" | `cap_I.tex` ¶7 | — |
| A029 | p.16 "ele" | `cap_I.tex:30` | referente | AT | sujeito explícito ("o módulo IVF só é executado ...") | `cap_I.tex` ¶7 | — |
| A030 | p.17 "orçamento" | `cap_I.tex:35` | sem comentário; termo antes da definição | MS | definição movida para antes dos objetivos | `cap_I.tex` ¶3 | — |
| A031 | p.17 "e posicionar o acoplamento ..." | `cap_I.tex:35` | sem comentário; "sete algoritmos comparados" indefinido e objetivo geral sobrecarregado | MS | objetivo geral reescrito (A033); OE6 descreve os tipos de algoritmo | `cap_I.tex` `sec:objetivos` | — |
| A032 | p.17 "orçamento" | `cap_I.tex:38` | idem A030 | AT | ver A030 | — | — |
| A033 | p.17 objetivos | `cap_I.tex` `sec:objetivos` | objetivo geral enumerava as QPs; específicos replicavam | AT | objetivo geral integrador; específicos operacionais (o que será feito) | `cap_I.tex` `sec:objetivos` | **redação pendente de aprovação do autor** (§G-1) |
| A034 | p.17 "é respondida" | `cap_I.tex:48` | sujeito/objeto indefinidos | AT | §5.1: "A QP1 é respondida pela avaliação comparativa principal: a comparação entre ..." | `cap_V.tex` `sec:questoes` | — |
| A035 | p.17 "perguntas comparativas" | `cap_I.tex:48` | a pergunta não é "comparativa" | AT | "referem-se a estudos já realizados e pedem a comparação dos resultados que eles registram, sem enunciar hipóteses fixadas antes desses estudos" (retrospectividade preservada) | `cap_V.tex` `sec:questoes` | revisão científica: coerente com `REWRITE_SPEC` §1.6–§1.7 |
| A036 | p.17 "comparativa principal" | `cap_I.tex:48` | termo indefinido | AT | definido em §5.1 antes do uso; Introdução não o usa | `cap_V.tex` | — |
| A037 | p.18 "configurações e as variantes" | QP2 em `cap_I.tex` | conceitos indefinidos | AT | definições de instância, configuração e variante de acoplamento em §5.1; OE3 explica variante | `cap_V.tex` `sec:questoes`; `cap_I.tex` OE3 | — |
| A038 | p.18 "diferem" | QP2 | sugestão "se diferem" | NA | "diferir" é intransitivo na norma culta; a forma pronominal não é a padrão | `cap_V.tex` QP2 | — |
| A039 | p.18 geral | Introdução | QPs exigem conhecimento ainda não apresentado | AT | QPs transferidas para §5.1 (decisão do autor), após Embasamento e Proposta | `cap_V.tex` | — |
| A040 | p.18 parênteses | QP2 | parênteses quebram a leitura | AT | aposto sem parênteses na QP2; contribuições e OE sem parênteses | `cap_V.tex` QP2 | — |
| A041 | p.19 "comparativa principal" | contribuição 2 | sem comentário; termo indefinido na Introdução | MS | contribuição reescrita sem o termo | `cap_I.tex` §1.2 | — |
| A042 | p.19 "desfecho" | contribuição 2 | jargão; três sentidos no texto | AT | "métrica primária/secundária"; sentidos distintos separados (§D N11), inclusive nas notas de 7 tabelas geradas | todo o texto | grep "desfecho" em `tex/`,`pre/`: 0; em tabelas visíveis: 0 |
| A043 | p.19 "HV" | contribuição 2 | sigla não apresentada | AT | IGD e HV por extenso no OE2 (primeira ocorrência na Introdução), no resumo, no abstract e na abertura de §2.4 | `cap_I.tex`; `pre/`; `cap_II.tex` `sec:indicadores` | revisão editorial: OK |
| A044 | p.19 "configurações e de variantes" | contribuição 3 | idem A037 | AT | ver A037 | — | — |
| A045 | p.19 "Variação entre acoplamentos e alcance" | contribuição 4 | título opaco | AT | "A comparação de acoplamentos do IVF a três hospedeiros" | `cap_I.tex` §1.2 | — |
| A046 | p.19 "acoplamentos publicado" | contribuição 4 | sentido de "publicado" | AT | "acoplamentos do IVF ao NSGA-II e ao NSGA-III propostos na literatura"; §6.3 indica autoria e onde foram propostos | `cap_I.tex`; `cap_VII_complementares.tex` `sec:hospedeiros` | atribuição conferida (EvidenceCheck) |
| A047 | p.19 "Diagnóstico precoce e seu limite" | contribuição 5 | objeto indefinido | AT | "A antecipação do benefício e o controle do módulo" + descrição do que foi investigado | `cap_I.tex` §1.2 | — |
| A048 | p.19 "BA" | contribuição 5 | sigla não definida | AT | sigla fora da Introdução; definida na primeira ocorrência (§6.4), como também MCC | `cap_VII_complementares.tex` `sec:ativacao` | — |
| A049 | p.19 "WFG" | contribuição 5 | sigla não definida | SD | Introdução não usa WFG; no corpo a suíte é apresentada por nome, citação e descrição (§5.2.2). Expansão do nome não feita | `cap_V.tex` `sec:suites` | expansão pendente (§G-4) |
| A050 | p.19 "Uma reanálise ... restringe o alcance ..." | contribuição 5 | frase sem conteúdo informativo | AT | removida; contribuição diz o que foi investigado; o resultado fica em §6.4/§7.4 | `cap_I.tex` | — |
| A051 | p.19 "Posicionamento contra algoritmos comparados" | contribuição 6 | sugestão "comparação com o estado da arte" | SD | "A comparação com outros algoritmos evolutivos multiobjetivo" (sem "estado da arte": conjunto de 2002–2023, inclui algoritmos canônicos) | `cap_I.tex` §1.2 | — |
| A052 | p.20 "demais comparadores" | `cap_I.tex:80` | referente | AT | "os sete algoritmos comparados" (§7.8) e eliminação de "demais comparadores" em todo o texto | `cap_VII.tex` `sec:publicacoes` | grep: 0 |
| A053 | p.20 "A dissertação gera as suas tabelas ..." | `cap_I.tex:80` | sujeito impróprio | AT | "As tabelas e figuras de resultados desta dissertação são produzidas por programas que leem os artefatos versionados ..., e não transcritas dos manuscritos" | `cap_VII.tex` `sec:publicacoes` | — |
| A054 | p.21 "os outros dois hospedeiros comparados" | `cap_II.tex:4` | não especificados | AT | "o NSGA-II e o NSGA-III" | `cap_II.tex` abertura | — |
| A055 | p.26 "ncia" "." | legenda Fig. 2.3 | legenda sem ponto final | MS | ponto final nas Figuras 2.2 e 2.3; legendas curtas na Lista de Figuras | `cap_II.tex` `fig:spea2_flow`, `fig:ivf_flow` | PDF p.11 |
| A056 | p.26 "Procedimento do Método IVF" | `cap_II.tex:115–142` | lista sem contexto | AT | parágrafo de contexto (ciclos, critério de continuação, transferência) antes da figura e da lista | `cap_II.tex` §2.3.1 | ver §G-5 sobre a fonte |
| A057 | p.27 "que diferem n" | `cap_II.tex:157` | sugestão "se diferem" | NA | idem A038 | — | — |
| A058 | p.28 "distância geracional invertida" | `cap_II.tex:180` | sugestão de iniciais maiúsculas | NA | nome comum em minúsculas na prosa; títulos de subseção seguem a convenção de cabeçalho. A ocorrência marcada passou a "A IGD mede", porque a sigla é apresentada na abertura de §2.4 | `cap_II.tex` §2.4.1 | — |
| A059 | p.29 "Por que reportar os dois" | `cap_II.tex:214` | subseção sem substrato; referente "os dois" | AT | subseção eliminada; conteúdo na abertura de §2.4 com "a IGD e o HV" | `cap_II.tex` `sec:indicadores` | — |
| A060 | p.31 "o seu tamanho" | `cap_II.tex:231` | referente | AT | "o tamanho dessa diferença" | `cap_II.tex` §2.5.2 | recorrência em `cap_VII.tex` §7.1 tratada |
| A061 | p.31 "pares de execuções" | `cap_II.tex:231` | definir primeiro em termos estatísticos gerais | AT | definição genérica (duas amostras, probabilidade, metade dos empates, com \cite{ARCURI}) e depois o caso de execuções | `cap_II.tex` §2.5.2 | EvidenceCheck E2 |
| A062 | p.31 "na" | `cap_II.tex:233` | regência | AT | "para a IGD" | `cap_II.tex` | — |
| A063 | p.31 "no" | `cap_II.tex:233` | regência | AT | "para o HV" | `cap_II.tex` | — |
| A064 | p.32 "do orçamento de otimização" | `cap_II.tex:255` | sem comentário; impreciso (amostragem estática tem custo próprio; descritores dinâmicos não "consomem" orçamento, só exigem esperar parte dele) | MS | reformulado nos dois parágrafos | `cap_II.tex` `sec:paisagem` | — |

---

## D. Recorrências e achados novos

Separação: **E** = editorial (sem mudança de significado) · **S** = altera significado ou força
(para mais fraco, salvo indicação). Confiança: alta (lido no fonte/artefato), média (inferido do
texto).

| ID | Passagem anterior (resumo) | Local final | Problema | Classe de comentário | Evidência | Ação | Tipo | Conf. |
|---|---|---|---|---|---|---|---|---|
| N01 | "devolve ao hospedeiro apenas os descendentes que sobrevivem a um critério de continuação" | `cap_I.tex` ¶4; `cap_III.tex` `sec:linhagem_ivf` ¶1; `cap_IV.tex` ¶2; `cap_II.tex` §2.3.1 | confunde sobrevivência/transferência com continuação | conceitos/termos | Cap. 2 passos 5–7; Algoritmo 4.1 | continuação = repetir ciclos; transferência = etapa posterior. Ordem corrigida no Cap. 1 após a revisão científica (R19-1). Formulação neutra "devolve ... as soluções obtidas na manipulação" para não afirmar o que o IVF original transfere (§G-5) | S | alta |
| N02 | "preserva o fluxo operacional do SPEA2"; "o preserva ... sem reabrir o mecanismo de seleção" | `cap_IV.tex` ¶3 e `sec:acoplamento`; `cap_III.tex` §3.3 | oculta o recálculo da aptidão antes do torneio (`OQ-24`) | síntese > detalhe | `cap_VIII.tex` validade interna | declara o recálculo e que a diferença acompanha todas as comparações | S | alta |
| N03 | "o IVF/SPEA2 incorre em custo adicional de relógio" | `cap_IV.tex` `sec:acoplamento` | contradiz §4.5 (efeito líquido não medido) | causalidade/síntese | `cap_IV.tex` `sec:custo` | "executa operações internas adicionais ...; o efeito líquido sobre o tempo de relógio não foi medido" | S (mais fraco) | alta |
| N04 | "teto da fração acumulada" | `cap_II.tex` §2.3.2; Tabela 4.1 | sugere limite rígido; a condição é de ativação | termos | `cap_IV.tex` ("nunca excede ... em mais do que o consumo de uma ativação") | "limiar de uma condição de ativação"; frase explícita de que não é teto rígido | S | alta |
| N05 | "O sentido do resultado não depende do nível de correção; a sua magnitude, sim" | `cap_VI.tex` §5.3.1 | "magnitude" para contagens | contagem × efeito | — | "as contagens, sim" | E | alta |
| N06 | "não se mostram preferíveis" | `cap_VII_complementares.tex` §6.5; `cap_VII.tex` §7.5 | preferência sem critério | contagem × preferência | — | contagens de saldo + "contagens de diferenças detectáveis não definem ... qual algoritmo seria preferível" | S | alta |
| N07 | "a regra não compensa"; "compensa o seu custo"; "vale a pena" | `cap_VII.tex` §7.4; `cap_III.tex` §3.4–3.5; `cap_II.tex` §2.6 | utilidade sem função de custo | contagem × preferência | §7.4 já declara ausência de função de custo | "não produziu resultado melhor que ..."; "melhora o resultado"; "deve permanecer ativo" | S | alta |
| N08 | "as duas vitórias, nas quatro rotuladas como prejudicadas, nas quais ..." | `cap_VII.tex` §7.4; `cap_VII_complementares.tex` §6.4.3 | troca de subconjunto por pronome | referentes | `results/tables/controller_wtl_oos_20260326_221909.csv`; Tabela 6.12 (prejudica: 0/1/3 contra o SPEA2 e 2/2/0 contra o sempre ativo, em HV) | duas frases com subconjuntos explícitos | E | alta |
| N09 | desenhos futuros sem braços/contrastes | `cap_IX.tex` `sec:fw_isolar` | promessa de identificação causal sem desenho | causalidade | — | fatorial 2×2 pareado (+ cruzamento com configuração); terceiro braço SPEA2 com recálculo e dois contrastes; hospedeiros com e sem módulo e teste de interação | S (explicita requisitos) | alta |
| N10 | "orçamento de 60 execuções", "orçamento por geração", "operador auxiliar orçado/sujeito a orçamento", "gatilho de orçamento acumulado", "sob orçamento fixo" | `cap_V.tex` §5.1.1; `cap_IV.tex`; `cap_VII.tex` §7.7; `cap_IX.tex` | "orçamento" com quatro sentidos | termos | — | orçamento × consumo acumulado × cota da geração | E | alta |
| N11 | "desfecho primário/secundário", "desfecho do teste", "desfecho final" | todo o texto; notas de 7 tabelas (6.7, 6.8, 6.11, 6.12, 5.3, 5.4, 7.1) | três sentidos | termos (A042) | — | métrica primária/secundária; resultado (corrigido) do teste; qualidade da aproximação final | E | alta |
| N12 | "pipeline(s)" | Caps. 2, 6, 7, 8, 9; nota da Tabela 6.4 | estrangeirismo indefinido, usado como sinônimo de hospedeiro | termos (A005) | — | "acoplamento, tal como implementado e configurado", definido em §6.3 | E | alta |
| N13 | "família" = suíte ("fora da família de treino", "entre famílias", "Cada família foi controlada") | Caps. 2, 6, 7, 9; notas das Tabelas 6.9, 6.10 e 6.12 | colide com família de evidência e família de hipóteses | termos | — | "suíte"; esquema "deixa-uma-família" definido; LOFO definido na Tabela 6.10; "família de hipóteses" para Holm | E | alta |
| N14 | "12 configurações problema--objetivo", "depende da configuração" (= M), "18 configurações" | `cap_V.tex` §5.2.5; `cap_VII_complementares.tex` §6.2; `cap_VII.tex` §7.6; Tabelas 6.2 e 7.1 | "configuração" = parâmetros e = instância | termos (A037) | — | "instâncias"; "número de objetivos e parâmetros que mudam com ele" | E | alta |
| N15 | IGD "orientada à proximidade", HV "à cobertura"; "proximidade e cobertura não concordam" | `cap_II.tex` §2.4; `cap_VI.tex` §5.3.1; `cap_V.tex` §5.2.3; `cap_VII_complementares.tex` §6.1 | contradiz a definição da IGD no próprio Cap. 2 (pendência da R17) | termos | `cap_II.tex` §2.4.1 | "distâncias a um conjunto de referência" × "volume dominado"; "IGD e HV não concordam" | E | alta |
| N16 | "As seções anteriores tratam o operador como sempre ativo" | `cap_VII_complementares.tex` §6.4; `cap_V.tex` QP4 | "sempre ativo" indefinido; sugere execução em toda geração | conceitos | `cap_IV.tex` §4.4 (suspensão em 1 de 16 gerações no limite) | definição explícita | E | alta |
| N17 | "esperam-se cerca de duas rejeições falsas" | `cap_II.tex` §2.5.3 | aritmética: 51 × 0,05 = 2,55 | número | cálculo | "$51 \times 0{,}05 \approx 2{,}6$" | número corrigido | alta |
| N18 | títulos dos painéis "Regime de convergência/estagnação"; painel (b) em vermelho sem legenda | `build_fig_resultados.py`; Fig. 5.2 | rótulo interpretativo (mecanismo) e cor sem chave | hipótese como fato; legendas | pendência registrada no log de 2026-10-03 | critério de seleção nos títulos; mesma cor nos dois painéis | S (mais fraco) | alta |
| N19 | entrada da Lista de Algoritmos | `main.tex` | A017 | diagramação | PDF p.14 | formatação de `\l@figure` | E | alta |
| N20 | "AGE-MOEA-II e AR-MOEA costumam ser competitivos quando a geometria ... é irregular" | `cap_III.tex` §3.3; `cap_V.tex` §5.2.1 | generalização não sustentada pelas fontes (EvidenceCheck E4) | força > fonte | texto aberto do AGE-MOEA-II (TU Delft) | "foram projetados para se adaptar à geometria da fronteira ou ao conjunto de referência" | S (mais fraco) | média |
| N21 | definição de paisagem de aptidão sem fonte | `cap_II.tex` §2.6 | frase nova desta rodada sem citação própria (E1) | — | EvidenceCheck | marcada como definição de trabalho ("Nesta dissertação, ...") | E | média |
| N22 | "inédito na linhagem do método" | `cap_I.tex` §1.2 | afirmação de ineditismo baseada em ausência (E5) | força | busca sem contraexemplo | "hospedeiro ao qual o método não havia sido acoplado nos trabalhos publicados da sua linhagem" | S (mais fraco) | média |
| N23 | "As famílias corrigidas pelo procedimento de Holm controlam a taxa de erro por família" | `cap_V.tex` §5.1.1 | mistura família de evidência e família de hipóteses | termos | — | "Nas famílias de evidência corrigidas por Holm, controla-se a taxa de erro por família de hipóteses" | E | alta |
| N24 | "a razão pela qual a comparação entre hospedeiros inclui uma coluna a mais" | `cap_III.tex` §3.3 | referente opaco | referentes | — | explicitado | E | alta |
| N25 | "A magnitude da queda não acompanha a magnitude do ganho" | `cap_VII_complementares.tex` §6.3 | "ganho" ambíguo (contagem × efeito) | contagem × efeito | Tabela 6.5 | "a queda não é maior no acoplamento com mais vitórias" | E | alta |
| N26 | síntese "O posicionamento ... é favorável, mas não uniforme" | `cap_VII.tex` §7.7 | mais forte que o detalhe ("na maioria dos contrastes") | síntese > detalhe | §7.5 | "tem saldo favorável ... na maioria dos contrastes" | S (mais fraco) | alta |
| N27 | "A evidência mais relevante para a decisão"; "O fecho é por regime" | `cap_VI.tex` §5.3.1; `cap_VII_complementares.tex` §6.5 | referentes opacos | frases abstratas | — | "para avaliar a generalização"; "A leitura depende do número de objetivos" | E | alta |
| N28 | Apêndice C oculto afirma que nenhuma QP depende do posicionamento | `pos/apend_III.tex` | reintroduziria a arquitetura anterior à QP5 | fontes ocultas | `main.tex` | comentário de advertência, texto intacto | E | alta |
| N29 | atribuição do IVF/NSGA-III a "Sampaio e Camilo-Junior" | `cap_VII_complementares.tex` §6.3 | erro **introduzido por esta rodada** e corrigido antes da entrega | — | `bib` `Sampaio2024` (tese de Sampaio) | "na tese de Sampaio~\cite{Sampaio2024}" | E | alta |
| N30 | resumo/abstract: contagens sem métrica, MaF7, protocolo dos hospedeiros, configuração da ablação (pendências R17) | `pre/` | ambiguidades herdadas | textos autônomos | `REWRITE_SPEC.md` §6.3 | "em IGD"; "uma delas com função calibrada"; "(30 execuções, Benjamini--Hochberg)"; "com os parâmetros iniciais" | E | alta |
| N31 | contribuições com inventário de resultados | `cap_I.tex` §1.2 | duplicação objetivos/contribuições/resultados | duplicação | — | contribuições descrevem o que foi feito; números ficam em §5.3, Cap. 6 e Cap. 7 | E (remoção de repetição) | alta |
| N32 | "ordenam os pipelines"; "os acoplamentos publicados ... não produziram" | `cap_VII.tex` §7.3 | ver N12 | — | — | "acoplamentos" | E | alta |

---

## E. Integridade científica

**Números.** `claims.py diff` por arquivo (saída integral reproduzível com
`python3 scripts/science/claims.py diff <arquivo>`; resumo abaixo):

- `cap_I.tex`: removidos 0,754; 12 ×2; 25; 33; 39; 49; 51 ×3; 60 ×2; 2026 ×2 e numerais por extenso —
  **migração ou remoção de repetição**: o inventário de resultados saiu das contribuições (N31) e a
  seção de publicações (com os anos) foi para §7.8; todos os valores seguem em §5.3, Caps. 6–7 e
  resumo. Acrescentados 2002 e 2023 (contribuição 6; conferidos no `.bib` pela auditoria).
- `cap_II.tex`: + "51 × 0,05 ≈ 2,6" (N17, correção aritmética: 2,55 arredondado; antes "cerca de duas").
- `cap_V.tex`, `cap_VII.tex`: entradas correspondentes às migrações de QPs e publicações.
- `pre_resumo.tex` e `pre_abstract.tex`: **removido 0,150** (Spearman da reanálise estática), para
  caber numa página; a frase passou a "pouco anteciparam"/"weakly associated". O valor continua em
  §6.4 e §7.4. "49/51" virou "49 de 51"; "1,15%" virou "+1,15% para o IVF/SPEA2" (sinal da tabela).
- Demais capítulos: só numerais por extenso de definições ("duas decisões", "três braços").

**Citações.** Acrescentadas: `ARCURI` (§2.5.2, tratamento de empates no $A_{12}$, por indicação do
EvidenceCheck E2), `sampaio2017ivf` e `Sampaio2024` (§6.3, atribuição). Migradas: as três
`zambrano2026*` de §1.4 para §7.8. Nenhuma entrada nova no `.bib`; `bib_check.py`: ok=53.

**Rótulos.** Novo: `sec:desenho`. Migrados: `sec:questoes` (cap_I → cap_V), `sec:publicacoes`
(cap_I → cap_VII). Nenhum removido; nenhum duplicado (log sem "multiply defined").

**Marcadores de força.** Removidos com justificativa: "não isola" das contribuições (o limite
continua em §6.3, §7.3, §8.2 e §7.7, cujo texto foi reforçado em N26); "hipótese/pode" do resumo
substituídos por "Supondo que ... desfavoreça" (modo hipotético preservado). Acrescentados:
"pode/podem" (Cap. 2 e 4, hedges) e "sempre ativo" (definição).

**Remoções de repetição justificadas.** Contribuições sem números (N31); subseção "Por que reportar
os dois" fundida à abertura de §2.4 (A059); definições duplicadas de IGD/HV em §2.4.1–2.4.2
(acrônimos já introduzidos na abertura). Nenhuma limitação foi retirada: recálculo da aptidão,
calibração em 12/51 com metade do orçamento, ablação fora da configuração promovida, sobreposição
de coortes, rótulos de ativação, análises pós-hoc e descritividade da ordenação entre acoplamentos
continuam nos mesmos lugares canônicos (verificado pela revisão científica independente).

**Testes, coortes, parâmetros.** Nenhum alterado. Nenhuma campanha executada. Os 9 geradores de
tabela (14 tabelas) e o de figura tiveram só texto alterado; comparação programática dos números de cada tabela
regenerada contra a cópia de partida (`/tmp/altino_base/results_thesis/`): "numbers identical" em
todas as 14 tabelas alteradas; `make thesis-tables-check`: OK; `make verify-release`: OK (o único
arquivo de `results/thesis/` no manifesto, `tab_posicionamento.tex`, não mudou).

**Auditoria numérica realizada (QuantAudit, independente).** 50+ números conferidos contra
`results/thesis/*.tex`, `results/tables/claims_summary_audit.csv`, `claims_summary_instance_details.csv`,
`hosts_geometry_summary.csv`, `controller_wtl_oos_20260326_221909.csv`,
`ppsn_controller_comparison_oos_20260326_221909.csv`, `fla_response.csv`,
`head_to_head_c26_a43_v1_summary.json` e o consolidado filtrado por
`filter_submission_synthetic_cohort`. Nenhum MISMATCH. Observações menores: sinal de 1,15% no
resumo (corrigido) e 2,55 → 2,6 (arredondamento declarado). A auditoria cobriu os números do
resumo, abstract, Cap. 1, Cap. 5 e dos trechos reescritos — não é uma auditoria integral de todos
os números da dissertação.

**Verificação bibliográfica realizada (EvidenceCheck, independente; consultas só com metadados).**
SUPPORTED: atribuições da linhagem IVF (`camilo-junior2011` texto aberto IntechOpen;
`sampaio2017ivf`, `sampaio2019ivf` via Crossref; `Sampaio2024` via página do PPGCC), intervalo
2002–2023 dos sete algoritmos. PARTIAL/inferência: $A_{12}$ com empates (resumo do artigo; texto
pago) → `ARCURI` acrescentado; AGE-MOEA-II/AR-MOEA "competitivos em fronteiras irregulares" →
enfraquecido (N20). Não acessíveis: AR-MOEA (IEEE), Mersmann et al. (ACM).

**Dados e artefatos.** `data/` e `artifact/` intocados. `results/thesis/` alterado só pelos
geradores (`make thesis-tables`), com o ambiente `.venv` (matplotlib 3.10.8); as demais figuras
saíram byte a byte idênticas (só `fig_dtlz4_bimodal.pdf` mudou).

---

## F. Verificação técnica e visual

| Comando | Resultado | Linha de base |
|---|---|---|
| `make -C thesis/masters -B all` (final) | compila; 106 páginas; 0 *overfull*; 0 referência/citação indefinida | 103 páginas |
| `python3 scripts/science/latex_check.py --compare` | "bloqueantes novos: 0"; 3 *underfull*: `pre/pre_resumo:3` (preexistente), `main.bbl:222` (preexistente), `tex/cap_V:84` (marcado "novo" pelo verificador; é o mesmo parágrafo de `\texttt{Problem.GetOptimum}` que na linha de base estava em `cap_V:32`, listado como "resolvido") | 3 *underfull* |
| `python3 scripts/science/claims.py diff` (13 arquivos) | ver §E | — |
| `python3 scripts/science/prose_audit.py thesis/masters/tex thesis/masters/pre` | 0 alto, 0 médio, 31 avisos (frases longas; "significativa", "superior", "robusta" em contexto citado) | não registrada antes |
| `python3 scripts/science/bib_check.py` | ok=53 | — |
| `make thesis-tables` / `make thesis-tables-check` | 31 arquivos espelhados; "OK: sincronizadas" | OK |
| `make thesis-doctor` | "OK: 9 evidence sources across 5 evidence families and 147 repository paths validated." | — |
| `make verify-release` | "Release integrity OK" | — |
| `make test` | 58 passed | — |
| grep de versionamento (perfil §4.1) em `tex/`, `pre/` | 0 ocorrências | 0 |
| grep `pipeline`, `desfecho`, `orçamento fixo`, `comparadores`, `Capítulo~\ref{sec:results}` em `tex/`, `pre/` | 0 | — |

Durante a rodada surgiram e foram resolvidos: *overfull* do abstract e transbordamento das
palavras-chave do resumo para a página seguinte (resolvidos encurtando os textos); *underfull* no
título da §7.1 e na legenda da Tabela 7.1 (resolvidos reformulando).

**PDF inspecionado.** Visualmente, sobre a renderização a 120 dpi em `thesis/masters/build/render/`
(e 100 dpi para a p.14): p.6 (resumo com palavras-chave na mesma página), p.14 (Lista de
Algoritmos — A017 corrigido), p.48–50 (abertura do Cap. 5, QPs, Tabela 5.1) e p.63 (Figura 5.2
com novos títulos e cor única). Por extração de texto (`pdftotext -layout`): p.7 (abstract e
keywords na mesma página), p.8–10 (sumário: nove capítulos, §5.1–5.3, §7.8), p.11 (Lista de
Figuras com legendas curtas), p.93–94 (Conclusões e §7.8) e o mapa de seções por página de
p.15–95. Defeitos observados e não corrigidos: espaço em branco abaixo da Figura 5.2 e Tabelas
5.9–5.10 depois da Síntese (posicionamento de *floats* igual ao da linha de base).

---

## G. Pendências e decisões humanas

| # | Problema | Evidência | Tentado | Decisão necessária | Impacto |
|---|---|---|---|---|---|
| G-1 | Redação nova do objetivo geral, dos seis objetivos específicos e das seis contribuições | A033; `cap_I.tex` §1.1–§1.2 | reescrita feita pelo executor | aprovar ou ajustar | central para a continuidade objetivos → QPs |
| G-2 | Decisões terminológicas (orçamento/consumo/cota; métrica primária; acoplamento no lugar de *pipeline*; algoritmos comparados; suíte; instância) | `terminologia.md` | aplicadas no texto e nas notas de 14 tabelas geradas | ratificar; se rejeitar alguma, reverter também nos geradores | todo o texto |
| G-3 | "paisagem de aptidão" × "superfície de aptidão" | A011, A016 | termo mantido e definido | escolha terminológica final | palavras-chave, Caps. 2, 3, 6 |
| G-4 | Expansão de WFG (e eventualmente ZDT, DTLZ, MaF) | A049 | não feita sem fonte verificada | decidir se expande e com qual fonte | §5.2.2 |
| G-5 | IVF original: o que a transferência devolve (o doador primário corrente ou todos os descendentes) e se a coleta é das melhores soluções | EvidenceCheck E3: o texto aberto de Camilo-Junior e Yamanaka descreve inserir o "Father" corrente na população do AG | Cap. 1, 3 e 4 reescritos de forma neutra ("o resultado da manipulação"); passos 1 e 7 do Cap. 2 (preexistentes) mantidos | conferir o capítulo original (IntechOpen, acesso aberto) e corrigir §2.3.1 se necessário | descrição do método de partida |
| G-6 | Resumo/abstract sem o valor de Spearman e sem a ressalva de que os dois empates de engenharia não excluem prejuízo | limite de uma página; SciReview R19-2 | compressão; ressalva completa no corpo (§6.1) | aceitar ou trocar outro conteúdo por essas informações | textos autônomos |
| G-7 | Apêndice A gerado ainda usa "pipelines publicados" e "desfecho"; Apêndice C contradiz a QP5 | `build_apendice_fontes.py`; `pos/apend_III.tex` | não alterados (ocultos); comentário no C | ajustar o gerador ao restaurar os apêndices; destino do C | latente |
| G-8 | Figura 2.3 (`fig/fluxo_ivf.pdf`) sem fonte editável, com título interno em inglês | p.25 | não editável | redesenhar ou manter | visual |
| G-9 | Afirmação "60 execuções ... estabiliza conjuntamente o teste de Wilcoxon e as estimativas" (preexistente) só tem apoio parcial em `eftimov2025adaptive` | `cap_V.tex` §5.1.1 | mantida | qualificar ou citar | baixa |
| G-10 | Registro em `AI_ASSISTANCE_LOG.md` | skill `ai-provenance` | entrada proposta gravada, marcada "pendente de autorização" | autorizar, ajustar ou remover | institucional |
| G-11 | Commit das alterações | — | nada commitado | autorizar | — |
| G-12 | Legendas da Fig. 6.4 e da Fig. 5.2 não repetem a chave de leitura (classes, critério de escolha); a chave está dentro da figura | revisão editorial P2; política de legendas concisas (perfil §9) | mantidas | confirmar a política para essas duas | baixa |

A rodada não depende de nenhuma dessas decisões para compilar ou para manter números e
limitações; G-1, G-2 e G-5 afetam a redação que o autor assina.

---

## H. Guia para o revisor

Diffs: `git diff 5a52253 -- thesis/masters/tex thesis/masters/pre thesis/masters/main.tex`
(prosa), `git diff 5a52253 -- src/python/thesis` (geradores), `git diff --word-diff 5a52253 --
results/thesis/*.tex` (saídas). A seção de QPs migrada: compare `git show 5a52253:thesis/masters/tex/cap_I.tex`
(linhas 46–56) com `thesis/masters/tex/cap_V.tex` `sec:questoes`; a de publicações: linhas 77–80 do
mesmo arquivo com `cap_VII.tex` `sec:publicacoes`.

Alterações de maior risco, por ordem:

1. **Objetivos e contribuições** (`cap_I.tex` §1.1–§1.2) — confrontar com `REVISION_PLAN.md` §2 e
   com as respostas do Cap. 7: o objetivo geral ficou mais amplo; nenhuma contribuição pode
   prometer o que §7.7 não entrega.
2. **Descrição do IVF original e da transferência** (`cap_I.tex` ¶4, `cap_II.tex` §2.3.1,
   `cap_III.tex` §3.1, `cap_IV.tex` ¶2) — confrontar com a **referência científica**
   (Camilo-Junior e Yamanaka, 2011) e com o Algoritmo 4.1 (G-5).
3. **Recálculo da aptidão e limiar do gatilho** (`cap_III.tex` §3.3, `cap_IV.tex` ¶3 e §4.1,
   Tabela 4.1) — confrontar com o **código** (`IVF-SPEA2-V2/IVFSPEA2V2.m`, `OQ-23`, `OQ-24`).
4. **Resumo e abstract** (`pre/`) — confrontar números com o **artefato**
   (`results/thesis/tab_confirmatorio_wtl.tex`, `tab_magnitude_confirmatoria.tex`, `tab_hosts_wtl.tex`,
   `tab_posicionamento.tex`, `tab_ativacao_robustez.tex`, `tab_controlador_wtl.tex`) e o **PDF**
   (p.6–7, uma página cada).
5. **Definições de §5.1** (instância, configuração, variante; avaliação comparativa principal;
   natureza retrospectiva da QP2, QP3 e QP5) — confrontar com `REWRITE_SPEC.md` §1.6–§1.7.
6. **Trabalhos futuros** (`cap_IX.tex` `sec:fw_isolar`) — conferir se os contrastes descritos
   identificam o que afirmam.
7. **Notas das tabelas regeneradas** — confrontar o diff de `results/thesis/` (só texto) e a
   Figura 5.2 no **PDF** p.63.
8. **Enfraquecimentos por evidência** (N20, N22, N26, N03, N07) — confrontar com as **fontes**
   indicadas.

Relatórios dos revisores independentes desta rodada (somente leitura): revisão científica (1 achado
maior introduzido pela rodada, corrigido — N01; 1 menor preexistente — G-6), auditoria quantitativa
(sem MISMATCH; 2 menores, um corrigido), verificação de evidência (5 menores: E1, E2, E4, E5
tratados; E3 → G-5), revisão editorial (1 problema novo, "decide como" no resumo/abstract, corrigido
para "coincide com"; 2 preexistentes → G-4 e G-12). As transcrições ficaram na sessão do executor e
não foram copiadas para o repositório.

---

## I. Fechamento da R19 — 2026-10-10, segunda sessão

As seções A–H acima são o registro da primeira sessão e ficam como estavam. Esta seção registra o
fechamento pedido pelo autor (correções F1–F7) e corrige uma divergência da entrega anterior. Quando
uma informação de A–H foi superada, isso está dito aqui, e não editado lá.

### I.1 Estado de partida e linha de base do fechamento

| Item | Comando ou ação | Resultado |
|---|---|---|
| Estado de partida | árvore de trabalho da R19 sobre `5a52253`, nada commitado | alterações preexistentes em `paper/clei2026/` e `WATCHDOG.yml` intocadas |
| Cópia do estado de partida | `tex/`, `pre/`, `main.tex` | `.omp/runs/pre-r19-fechamento/` (local, ignorado pelo git) |
| PDF de partida | `make -C thesis/masters -B all` | 106 páginas, 0 *overfull* |
| Linha de base LaTeX | `latex_check.py --save-baseline` (a anterior, do início da R19, foi copiada para `.omp/runs/pre-r19-fechamento/latex-baseline-r19start.json`) | 3 *underfull*: `pre/pre_resumo:3`, `tex/cap_V:84`, `main.bbl:222` |
| Fotos de afirmações | `claims.py snapshot` em `tex/*.tex`, `pre_resumo.tex`, `pre_abstract.tex` (as fotos do início da R19 foram copiadas antes) | `.omp/runs/snapshots/thesis/masters/` |
| Diff do fechamento | `diff -ru .omp/runs/pre-r19-fechamento/{tex,pre} thesis/masters/{tex,pre}` e `diff -u` em `main.tex` | `.omp/runs/r19-fechamento.diff`: 271 linhas, 18 trechos, 13 arquivos |

O diff do fechamento fica num diretório local e ignorado pelo git. Como nada foi commitado,
`git diff 5a52253` mostra a R19 inteira, primeira sessão e fechamento juntos. Para isolar o
fechamento, use o arquivo acima ou compare com a cópia de partida.

### I.2 Correção da contagem de estados (§C)

A entrega anterior, feita na conversa e não neste relatório, informou 40 comentários atendidos e 9
atendidos por solução diferente. A tabela da §C, que não foi alterada, tem **AT = 42, SD = 7, NA = 3,
FA = 1, MS = 11** (total 64). A contagem foi feita por programa, lendo a coluna "Estado" das linhas
`| A0nn |` (`collections.Counter`), e foi confirmada de forma independente pela auditoria
quantitativa. O erro estava na transcrição do resumo da conversa, não na tabela. Nenhum estado foi
mudado para fechar contagens.

### I.3 Achados do fechamento

Estados: **RESOLVIDO** (a evidência foi conferida e o texto corrigido) · **RESOLVIDO, DECISÃO
PENDENTE** (o texto está correto, mas há uma escolha que cabe ao autor) · **NÃO VERIFICADO** (falta
evidência; o impacto está declarado). Os números de linha referem-se ao estado final. Os trechos do
diff são localizados por arquivo e linha em `.omp/runs/r19-fechamento.diff`.

| ID | Trecho anterior (resumo) | Local final | Evidência conferida | Alteração | Diff | Estado |
|---|---|---|---|---|---|---|
| F1a | §2.3: "copiam-se para o módulo os $c$ indivíduos de melhor qualidade"; "o número de descendentes não excede o tamanho da população"; continuação "se algum descendente superar ... ou se outro critério de parada for atingido"; transferência "os descendentes gerados são transferidos ... ou pela expansão temporária da população"; formulação "tal como adotada pelos acoplamentos anteriores" | `cap_II.tex:111–159` (`sec:ivf`) | Camilo-Junior e Yamanaka (2011), lido integralmente: p.58–59 (devolve **um** indivíduo); p.60, §2.1, tarefas 1–5 ("Find the fittest individual and label it as Father"; inserção "replacing elected individuals, chosen by the elitism process"; sem elitismo, ao acaso); p.61, §2.4 (o pai é o melhor e as demais são mães, em número limitado por *NuIndiv*; um filho por grupo de genes); p.62 ("If not, the algorithm interrupts the loop and inserts the current father"; "returns the current father"); Fig. 4, p.62 ("the mothers are the three individuals after the father"); Tabela 1 ("GO or 250 G"); p.66–67 (codificação binária). A fonte não menciona teto de descendentes nem limite de ciclos. O teto igual ao tamanho da população e o limite de ciclos aparecem nos três códigos (`IVF_V2.m`, `IVF_NSGAII.m:46–55`, `IVF_NSGAIII.m:55–67`) | Passos reescritos segundo a fonte: doador primário = o mais apto; critério de coleta das mães não fixado (com o exemplo da fonte); recombinação por grupos de genes; continuação individual sem limite declarado; transferência = doador primário corrente, sem interferência quando não há melhora. Divergência explícita entre a "visão geral" (plural) e o procedimento detalhado (singular). Novo parágrafo separa o original das implementações comparadas (operadores reais, limite de ciclos, teto $N$, transferência dos descendentes), com `sampaio2017ivf` para a recomendação de transferir mais de um descendente (references/ivfnsga2.pdf, §III-C). "Dois parâmetros" restrito aos acoplamentos multiobjetivo; perfis: "os quatro primeiros já constam da formulação original" | `cap_II.tex` trechos 111, 113, 117, 126–144, 148, 159 | RESOLVIDO |
| F1b | Cap. 1: "copia algumas das melhores soluções ... devolve ... as soluções obtidas na manipulação"; Cap. 3: "coletar material genético de qualidade ... transferir ao hospedeiro o resultado da manipulação"; "compete com ele pelas avaliações do orçamento"; Cap. 4: "transfere ao hospedeiro o resultado da manipulação"; "o melhor indivíduo coletado" | `cap_I.tex:26`; `cap_III.tex:9`; `cap_IV.tex:6`, `:45` | a mesma fonte de F1a; para o IVF/SPEA2, o Algoritmo 4.1 (`SeleçãoAmbiental` sobre a população unida aos descendentes, a cada ciclo) | As sínteses dizem o que o original devolve (o doador primário corrente). O Cap. 3 deixa de atribuir ao original a disputa por avaliações: diz que a fonte não relata repartição de avaliações e que a execução parava no ótimo global ou após 250 gerações. O Cap. 4 separa o original ("na formulação original, devolve ... o doador primário corrente") do IVF/SPEA2 ("os descendentes de cada ciclo entram diretamente na seleção ambiental"). A formulação vaga "o resultado da manipulação", introduzida na primeira sessão, foi eliminada | `cap_I.tex:26`; `cap_III.tex:9`; `cap_IV.tex:6,45` | RESOLVIDO |
| F1c | Figura 2.3 apresentada como fluxograma do método original | `cap_II.tex:117`, `:122` | O PDF legado `fig/fluxo_ivf.pdf`, renderizado, mostra "Critério de Parada?", "Descendentes melhores que Primário?" e "Transfere descendentes gerados", o que contradiz o original (F1a) e coincide com `IVF_NSGAII.m`/`IVF_NSGAIII.m`: limite de ciclos, critério individual e `All_Super_Individuals` transferidos | Texto e legenda atribuem a figura às implementações dos acoplamentos ao NSGA-II e ao NSGA-III; a imagem não foi alterada | `cap_II.tex:117,122` | RESOLVIDO, DECISÃO PENDENTE (redesenhar a figura e traduzir o título interno em inglês, antigo G-8) |
| F2 | "Tampouco existe indicador que ordene aproximações de forma compatível com a relação de dominância em todos os casos" (Cap. 2); "Nenhum indicador isolado ordena aproximações de forma compatível com a relação de dominância em todos os casos" (Cap. 8); e, no Cap. 2, "nenhum indicador isolado captura as duas propriedades", que contradizia §2.4.1 | `cap_II.tex:178` (`sec:indicadores`); `cap_VIII.tex:26` | Zitzler et al. (2003), lido: p.118, §I (lista de resultados); p.123, Teorema 1 (nenhuma combinação finita de indicadores unários é ao mesmo tempo compatível e completa para "melhor que"); p.126 (o HV é o único indicador unário conhecido capaz de detectar "não pior" para todos os pares, e é ⊳-completo; nota 4: espaço de objetivos limitado); Fig. 11 (conjuntos incomparáveis com HV ordenado) | Distingue respeitar a dominância (o HV respeita) de caracterizá-la por indicador (nenhum indicador unário, nem combinação finita, permite concluir "melhor que"). A justificativa para reportar IGD e HV ficou (diferenças operacionais e discordância; seleção pós-hoc). A frase sobre "captura" foi retirada, porque contradizia a §2.4.1 | `cap_II.tex:178`; `cap_VIII.tex:26` | RESOLVIDO |
| F3 | "é uma escolha conservadora ... e estabiliza conjuntamente o teste de Wilcoxon e as estimativas de mediana e amplitude interquartil" | `cap_V.tex:51` | Eftimov e Korošec (2025), lido (arXiv 2507.01629v1): resumo e §1–§2 sustentam que o número de execuções afeta a duração do experimento e a confiabilidade das estimativas. O estudo é monobjetivo (COCO, DE, Nevergrad) e não trata de estabilidade conjunta de Wilcoxon, mediana e IQR. Busca no repositório (`docs/`, `REWRITE_SPEC.md`, `REVISION_PLAN.md`, perfil, Springer): nenhuma análise de potência ou de estabilidade registrada | 60 é declarado como "decisão do protocolo"; a citação ficou só para o ponto geral; o texto declara que não há análise de potência nem de estabilidade e remete à reamostragem exploratória existente (`sec:estatistica`). Nenhuma potência ou estabilidade foi inventada | `cap_V.tex:51` | RESOLVIDO (antigo G-9) |
| F4 | Cap. 3: "o doador primário é substituído quando um descendente não dominado fica mais próximo do nicho-alvo"; Cap. 6: "a realização ... proposta para ele, implementada neste projeto"; "que os seus autores publicaram"; Cap. 8: "reproduz, em implementação deste projeto, a realização publicada" | `cap_III.tex:11` (frase visível nova) e `:12` (comentário de proveniência); `cap_VII_complementares.tex:61`, `:63`; `cap_VIII.tex:20` | Tese de Sampaio (2024), PDF aberto (https://files.cercomp.ufg.br/weby/up/1289/o/Tese_Savio_Menezes_Sampaio_INF_UFG_2024.pdf, link na página do PPGCC), lida no trecho: p.65, §3.3 ("O filho que estiver não-dominado e possuir uma distância para o nicho alvo menor do que a distância do pai corrente ... será considerado o substituto do pai corrente"); coleta das mães em duas estratégias (§3.3.3 e §3.3.4; Figs. 3.7 e 3.9). Artigo do CEC 2023 (`references/ivfnsga3.pdf`, Figs. 2 e 5, §III-C): substituição só por proximidade, sem a condição. Código: `IVF_NSGAIII.m:110–119` (`if min_d < d_father`, sem teste de dominância) e `:41–49` (só mães vizinhas). Campanha: `experiments/run_ivfnsgaiii_submission.m` (etiqueta `SUB20260330_NSGAIII`, execuções 5001–5030, `{@IVFNSGAIII, 0.10, 0.10, 5}`). O histórico git é um único commit compactado (`0de9dd1`, 2026-04-17), posterior à etiqueta; o depósito `artifact/ppsn2026-ivf-hosts-rev1` não traz código | A descrição do Cap. 3 está **sustentada** pela tese e foi mantida. Acrescentou-se frase visível: a implementação usada na §6.3 substitui pelo descendente mais próximo, sem verificar não dominância. §6.3 e Cap. 8: "implementação ... da realização descrita"; "a fidelidade ... não foi verificada integralmente"; a divergência e a coleta parcial foram nomeadas; "o histórico do repositório não permite confirmar que esse código é o que gerou as execuções 5001–5030". Código e resultados não foram alterados | `cap_III.tex:11–12`; `cap_VII_complementares.tex:61,63`; `cap_VIII.tex:20` | RESOLVIDO, DECISÃO PENDENTE (citar ou não o artigo do CEC 2023, que não está no `.bib`; ver I.7) |
| F5 | Cap. 9: "Um desenho que pretendesse isolar o hospedeiro precisaria ... submeter cada acoplamento ao mesmo procedimento de ajuste ... o efeito do hospedeiro corresponderia à interação"; "Medindo a renovação inicial ... separaria ainda duas leituras"; "separaria ainda o efeito das decisões do efeito dos parâmetros"; "tornaria a associação testável"; Cap. 7: "o desenho que separaria essas fontes" | `cap_IX.tex:9`, `:13`, `:15`, `:17`; `cap_VII.tex:47` | lógica do desenho: o mesmo procedimento de ajuste pode escolher configurações diferentes; a renovação é medida, e não manipulada | Cada desenho declara o efeito que estima. Ablação: contrastes pareados de IGD e HV; interação decisões × configuração. Hospedeiro: (i) sob configuração controlada (módulo e parâmetros fixos; o efeito é a interação hospedeiro × presença do módulo, com teste sobre os três contrastes; vale para aquele módulo e configuração); (ii) sob política comum de ajuste (efeito conjunto hospedeiro + configuração escolhida; não isola o hospedeiro). Geometria: efeito da geometria com as demais características fixas. Renovação: "o desenho não identificaria o seu papel causal"; contraste preditivo com limiar fixado antes e avaliado em variantes fora do ajuste, dentro da mesma suíte. Cap. 7: dois desenhos, "nenhum dos dois separa as quatro fontes de uma só vez" | `cap_IX.tex:9,13,15,17`; `cap_VII.tex:47` | RESOLVIDO |
| F6a | "Nesta dissertação, a expressão paisagem de aptidão designa a estrutura que a função objetivo induz sobre o espaço de busca: quais soluções são vizinhas ..." | `cap_II.tex:253` (`sec:paisagem`) | Liefooghe et al. (2020), manuscrito aceito no HAL (hal-02294201), p.3, §III: "we define a multiobjective landscape as a triplet (X, N, f), where X is a solution space, N : X → 2^X is a neighborhood relation, and f ... objective function vector". Código FLA: `src/matlab/fla/sample_and_extract_features.m:21–22, 348–353` (passo das caminhadas fixado pela análise) | Definição pela tripla (espaço, vizinhança, função) com a citação já presente no parágrafo; declara que a função sozinha não define vizinhança; nos espaços contínuos desta dissertação, a vizinhança é fixada pelo procedimento de análise (passo das caminhadas). "Nesta dissertação" deixou de servir de fundamento | `cap_II.tex:253` | RESOLVIDO |
| F6b | "Nas seções anteriores, o módulo IVF está sempre habilitado ... condição de ativação da Equação 4.1" (atribuía o gatilho acumulado a todos os acoplamentos, inclusive à §6.3) | `cap_VII_complementares.tex:97` | `IVF_NSGAII.m:20–23` (probabilidade `R`); `IVF_NSGAIII.m:23–26` (fração acumulada própria); Eq. 4.1 só no IVF/SPEA2 | "o módulo IVF do IVF/SPEA2"; "própria do IVF/SPEA2"; os acoplamentos ao NSGA-II e ao NSGA-III "seguem regras de ativação próprias e não são objeto desta seção" | `cap_VII_complementares.tex:97` | RESOLVIDO |
| F6c | Resumo e abstract: "em três problemas de engenharia, 1/2/0." sem qualificação dos empates | `pre_resumo.tex:4`; `pre_abstract.tex:4` | `results/thesis/tab_engenharia_wtl.tex` (dois empates por teste sem rejeição; nenhum teste de equivalência) | "1/2/0, cujos empates são diferenças não detectadas, não equivalência" / "where the two ties are undetected differences, not equivalence". Para manter uma página por texto foram retirados "que recombina soluções selecionadas" / "that recombines selected solutions", "dele" e "do IVF" (resumo) e "IVF" (abstract), e "mas ... tem acurácia" virou "com acurácia". O valor de Spearman 0,150 continua fora (restauração opcional) | `pre_resumo.tex:4`; `pre_abstract.tex:4` | RESOLVIDO; Spearman: DECISÃO PENDENTE (opcional) |
| F7a | recorrências | Caps. 2, 3, 6, 8 | busca em `tex/`, `pre/` e `results/thesis/` por: "compatível com a relação", "ordena aproximações", "estabiliz", "reproduz", "fiel", "realização publicada", "separaria", "melhores soluções", "descendente não dominado", "resultado da manipulação", "expansão temporária" | recorrências tratadas em F1–F6. Notas geradas: só `tab_hosts_wtl` fala de implementação ("tal como implementados e configurados"), redação compatível; nenhum gerador foi alterado | — | RESOLVIDO |
| F7b | Tabelas 5.9–5.10 (HV por instância) impressas depois da §5.3.4 Síntese | `main.tex:49–51` (`\usepackage{placeins}`, com comentário); `cap_VI.tex:81` (`\FloatBarrier`) | mapa de páginas antes (Síntese na p.62, tabelas nas p.64–65) e depois (tabelas nas p.65–66, Síntese na p.67); `placeins.sty` no cache do Tectonic | barreira de *floats* antes da Síntese | `main.tex`; `cap_VI.tex:81` | RESOLVIDO, DECISÃO PENDENTE (custa 1 página: a Síntese ocupa sozinha a p.67) |
| F7c | riscos latentes dos apêndices ocultos | `pos/`; `build_apendice_fontes.py` | busca nos apêndices pelos termos de F1–F6: nenhuma ocorrência da descrição antiga do IVF, de "estabiliza" ou da impossibilidade universal; seguem latentes "pipelines publicados"/"desfecho" (Apêndice A gerado) e a contradição do Apêndice C com a QP5 | nenhuma (apêndices permanecem ocultos e não foram restaurados) | — | registrado (I.7) |
| F8 | contagem AT/SD da entrega anterior | §I.2 | contagem por programa | registro da correção; a tabela da §C não mudou | — | RESOLVIDO |

Situação dos itens de §G afetados: G-5 resolvido por F1; G-9 resolvido por F3; G-6 parcialmente
(qualificação dos empates feita, Spearman opcional); G-8 com legenda corrigida e figura mantida. O
item "Não verificado nesta rodada: fidelidade das etapas 1 e 7 do IVF original" da §A foi superado
por F1a.

### I.4 Fontes externas consultadas

"Conteúdo" significa que o texto foi lido no trecho indicado. "Metadados" significa consulta só a
DOI, título, autores ou registro institucional. Nenhum trecho do manuscrito foi enviado a serviço
externo.

| Chave / fonte | URL ou local | Seção / página | Tipo | Classificação |
|---|---|---|---|---|
| `camilo-junior2011` | https://cdn.intechopen.com/pdfs/15616.pdf | p.58–62 (§2, §2.1, §2.3, §2.4, Fig. 4), p.63–65 (§4, Tabela 1), p.66–67 (§5) | conteúdo | SUPPORTED para todas as afirmações de F1a/F1b; o texto anterior ("$c$ de melhor qualidade", teto $N$, "descendentes transferidos", "expansão temporária", "outro critério de parada") era NOT_SUPPORTED |
| `zitzler2004performance` | https://sop.tik.ee.ethz.ch/publicationListFiles/ztlf2003a.pdf | p.118 (§I), p.123 (Teorema 1), p.126 (HV; nota 4), Fig. 11 | conteúdo | SUPPORTED (texto novo); a frase anterior era CONTRADICTS quanto ao HV |
| `eftimov2025adaptive` | https://arxiv.org/html/2507.01629v1 | resumo, §1, §2 | conteúdo | PARTIAL: sustenta o ponto geral; a garantia de estabilidade era NOT_SUPPORTED e foi retirada |
| `liefooghe2018landscape` | https://hal.science/hal-02294201/document | p.3, §III | conteúdo | SUPPORTED |
| `sampaio2017ivf` | `references/ivfnsga2.pdf` (cópia rastreada no repositório) | §III-C "Transfer" | conteúdo | SUPPORTED |
| `Sampaio2024` | https://files.cercomp.ufg.br/weby/up/1289/o/Tese_Savio_Menezes_Sampaio_INF_UFG_2024.pdf | p.65, §3.3; sumário (§3.3.3, §3.3.4); ficha catalográfica ("Tese (Doutorado)") | conteúdo | SUPPORTED (condição de não dominância e duas estratégias de coleta) |
| Sampaio, Dantas e Camilo-Junior, CEC 2023 (fora do `.bib`) | `references/ivfnsga3.pdf`; Crossref `10.1109/CEC53210.2023.10254062` | Figs. 2 e 5, §III-A, §III-C | conteúdo (cópia local) + metadados (Crossref: título, autores, 2023, pp. 1–8, sem retratação) | PARTIAL quanto à condição de substituição (omite a não dominância); usada só como evidência, não citada |
| Registro do trabalho de Sampaio | https://ppgcc.inf.ufg.br/p/35374-dissertacoes-defendidas; https://inf.ufg.br/e/35809-22-defesa-de-tese-de-doutorado | listagem; anúncio de defesa de 11/04/2024 | metadados | a página do PPGCC lista o trabalho entre "dissertações", mas o anúncio do INF e a ficha da própria tese indicam doutorado: `@PHDTHESIS` correto |

Metadados por DOI (Crossref; conferidos pelo revisor de evidência e, para o CEC 2023, pelo executor):
`camilo-junior2011` 10.5772/16074, `zitzler2004performance` 10.1109/TEVC.2003.810758,
`eftimov2025adaptive` 10.1145/3712256.3726327, `liefooghe2018landscape` 10.1109/TEVC.2019.2940828.
Títulos, autores, veículos e anos conferem, e não há aviso de retratação. Observação: as chaves
`zitzler2004performance` (ano 2003) e `liefooghe2018landscape` (ano 2020) trazem no nome um ano
diferente do campo `year`. As chaves foram mantidas por invariante.

### I.5 Números conferidos

Nenhum número, coorte, parâmetro, teste ou correção mudou no fechamento. `claims.py diff` por arquivo
registra apenas numerais de texto e valores já existentes: `cap_II.tex` +"metade" (EAR na fonte), +"quatro"
(perfis originais), +"três" ×2 (acoplamentos; elementos da paisagem), −"duas" (frase retirada sobre
"as duas propriedades"); `cap_V.tex` +"60" (repetição do valor na nova frase); `cap_VII_complementares.tex`
+"5001–5030" (faixa existente citada na frase sobre rastreabilidade) e +"duas" (formas de coleta);
`cap_VII.tex` +"dois" ×2 e +"quatro" (desenhos e fontes); `cap_VIII.tex` −"dois" e `cap_IX.tex`
−"duas" (reformulação). Citações acrescentadas: `camilo-junior2011` ×4 e `sampaio2017ivf` (Cap. 2,
F1a) e `liefooghe2018landscape` (Cap. 2, F6a, chave já citada no mesmo parágrafo); nenhuma retirada;
`.bib` intocado. Referências cruzadas acrescentadas: `sec:Proposal`, `sec:linhagem_ivf`,
`sec:acoplamento`, `sec:hospedeiros`, `sec:critério_coletivo`, `sec:estatistica`; nenhum rótulo
criado ou removido. Marcadores de força acrescentados: em contexto negado ou atenuado ("não permite
confirmar", "não identificaria o seu papel causal", "não garante a mesma configuração", "não determina
a paisagem", "pode", "indica"), com uma exceção: "HV maior garante que a aproximação não é pior", que
é a propriedade demonstrada por Zitzler et al. (2003, p.126), e não um reforço novo.

A auditoria quantitativa independente conferiu 46 números dos trechos tocados e do resumo e abstract
contra `results/thesis/*.tex`, `results/tables/claims_summary_audit.csv`, `config/hosts_front_geometry.csv`,
`experiments/run_ivfnsgaiii_submission.m`, `run_hosts_convergence.m` e os códigos MATLAB. Resultado: 45
confirmados e 1 apontado (Q1, abaixo). Conferências do executor:

| Número | Fonte | Operação | Resultado |
|---|---|---|---|
| AT/SD/NA/FA/MS = 42/7/3/1/11 | §C deste relatório | contagem da coluna "Estado" | confere (64) |
| IVF/NSGA-III: taxa 0,10, coleta 0,10, 5 ciclos, execuções 5001–5030 | `run_ivfnsgaiii_submission.m:13–23`; `IVFNSGAIII.m:19` | leitura | confere com `cap_VII_complementares.tex:63` |
| IVF/NSGA-II: 0,5, 0,07, 5 ciclos | `IVFNSGAII.m:19` | leitura | confere |
| teto de descendentes do módulo = $N$ | `IVF_NSGAII.m:46,53`; `IVF_NSGAIII.m:55,65`; Algoritmo 4.1 | leitura | confere |
| 11 instâncias irregulares = 9 funções | `config/hosts_front_geometry.csv` (11 linhas `irregular`) | contagem: 11 linhas, 8 nomes de problema; MaF7 repete DTLZ7 nos dois valores de $M$ (`cap_VI.tex:63`) | 9 = pares distintos (função, $M$), conforme a regra declarada em `cap_VI.tex:63` |
| páginas citadas das fontes | PDFs | `pdftotext` por página | Zitzler: PDF 2/7/10 = p.118/123/126; IntechOpen: PDF 6 = p.62; Sampaio 2024: PDF 66 = p.65 |

### I.6 Verificação técnica e visual do fechamento

| Comando | Resultado |
|---|---|
| `make -C thesis/masters -B all` | 110 páginas (106 na partida; pelo início das seções: +1 no Cap. 2, +1 da barreira de *floats* na §5.3, +1 no Cap. 6 e +1 no Cap. 7); 0 *overfull*; 0 referência ou rótulo indefinido ou duplicado |
| `python3 scripts/science/latex_check.py --compare` | bloqueantes novos: 0; 3 *underfull*, todos preexistentes |
| `claims.py diff` (12 arquivos de `tex/` e `pre/`) | ver I.5 |
| `prose_audit.py tex pre` | 0 alto, 0 médio, 36 avisos (31 no fim da primeira sessão; os novos são frases longas) |
| `bib_check.py` | ok=53 |
| `make thesis-tables-check` | OK; `results/thesis/` idêntico ao estado de partida (`diff -rq`), nenhum gerador tocado |
| `make verify-release` | "Release integrity OK" |
| `make thesis-doctor` | "OK: 9 evidence sources across 5 evidence families and 147 repository paths validated." |
| `make test` | 58 passed |
| Resumo e abstract | uma página cada, com palavras-chave (p.6 e p.7), conferido por `pdftotext` depois de cada compilação. Na compilação intermediária sem cortes, as palavras-chave passaram para a página seguinte, e os cortes de F6c resolveram |

Páginas inspecionadas visualmente (renderizadas): p.25–26 (§2.3, passos e Figura 2.3 com nova
legenda), p.28 (abertura de §2.4), p.63, 64 e 67 (Tabela 5.8, Figura 5.2 e Síntese depois da barreira),
p.73 (§6.3) e p.102 (Cap. 9). Por extração de texto: p.6–8, o mapa de seções das p.1–110 e as p.55–69
(*floats* da §5.3). Defeito remanescente: a Figura 5.2 continua sozinha numa página de *float* (p.64),
como na partida.

### I.7 Revisão independente e integração

| Revisor | Achado | Decisão | Fundamento |
|---|---|---|---|
| Científico | S1 (crítico): a divergência do IVF/NSGA-III estava só num comentário `%`, invisível no PDF | aceito | frase visível acrescentada em `cap_III.tex:11`; depois a tese foi localizada e a descrição do Cap. 3 se confirmou (F4) |
| Científico | S2: o artigo do CEC 2023 estava disponível em `references/ivfnsga3.pdf`, ao contrário do que dizia o comentário | aceito | comentário reescrito como nota de proveniência (`cap_III.tex:12`); falha do executor, que não procurou cópias locais antes de declarar a fonte inacessível |
| Científico | S3: definição de paisagem não conferida no texto integral de Liefooghe et al. | resolvido | o executor e o revisor de evidência leram o manuscrito do HAL, p.3, §III |
| Científico | S4: a atribuição da Figura 2.3 às implementações NSGA não tem fonte gráfica independente | sem ação | atribuição conferida contra o código; redesenho fica para o autor |
| Científico | F1–F3, F5, F6, F7 | OK | — |
| Quantitativo | Q1: "nove funções" com 8 nomes distintos | rejeitado, sem alteração | a unidade é o par (função, $M$), definida em `cap_VI.tex:63`; a ambiguidade de "função" em `cap_IX.tex:15` e `cap_VII_complementares.tex:84` fica como observação editorial ao autor |
| Quantitativo | Q2: nenhuma mudança de valor no diff | informativo | — |
| Evidência | primeira tentativa (`evidence-reviewer`) | falhou por limite de uso do modelo, sem saída | repetida como agente geral, somente leitura, com a skill `evidence-verification` |
| Evidência | todos os pares SUPPORTED; tese de Sampaio localizada em acesso aberto; `@PHDTHESIS` correto | aceito após conferência própria | o executor baixou a tese e confirmou o trecho da p.65 e a ficha "Tese (Doutorado)" |

Nenhum revisor apontou fortalecimento de afirmação, causalidade, equivalência ou remoção de limitação.

### I.8 Arquivos alterados no fechamento

`thesis/masters/main.tex` (pacote `placeins` e comentário); `tex/cap_I.tex`, `cap_II.tex`,
`cap_III.tex`, `cap_IV.tex`, `cap_V.tex`, `cap_VI.tex`, `cap_VII.tex`, `cap_VII_complementares.tex`,
`cap_VIII.tex`, `cap_IX.tex`; `pre/pre_resumo.tex`, `pre/pre_abstract.tex`; este relatório;
`AI_ASSISTANCE_LOG.md` (entrada proposta atualizada); `REWRITE_SPEC.md` (§6.2, entrada R19) e
`REVISION_PLAN.md` (§3), com uma frase de registro cada. Não alterados: geradores, `results/thesis/`,
`bib/modelo-tese.bib`, `data/`, `artifact/`, código MATLAB, apêndices, `CLAUDE.md`, `AGENTS.md`.
Arquivos locais e ignorados pelo git: `.omp/runs/pre-r19-fechamento/`, `.omp/runs/r19-fechamento.diff`,
`.omp/runs/latex-baseline.json` (nova linha de base).

### I.9 Pendências

**Correção científica**

- Nenhuma pendente nos itens F1–F7.
- NÃO VERIFICADO, fora do escopo do fechamento: os números atribuídos à tese de Sampaio em
  `cap_VII.tex:45` (11/8/4 e 5/17/1, 23 instâncias). Na tese, conferiu-se apenas o protocolo (31
  execuções, 25.000 avaliações). Impacto: contraste descritivo da §7.3, sem efeito sobre as QPs.

**Decisão autoral**

- G-1 a G-4 e G-12 da §G seguem abertos.
- Citar ou não o artigo do CEC 2023 (fora do `.bib`), que é a descrição publicada mais próxima do
  código examinado.
- Manter `\FloatBarrier` (+1 página) ou aceitar as Tabelas 5.9–5.10 depois da Síntese.
- Redesenhar a Figura 2.3 (G-8).
- Restaurar ou não o Spearman 0,150 no resumo e no abstract.
- Aceitar os cortes de F6c.
- Explicitar "nove pares de função e número de objetivos" em `cap_IX.tex:15` e
  `cap_VII_complementares.tex:84` (Q1).

**Risco latente**

- Apêndice A gerado com "pipelines publicados" e "desfecho"; Apêndice C em contradição com a QP5
  (G-7). Apêndices mantidos ocultos.
- Vínculo entre o código examinado do IVF/NSGA-III e as execuções 5001–5030 não comprovável pelo
  histórico. A limitação agora está declarada no texto.
- Fidelidade do IVF/NSGA-II à publicação verificada só nos pontos citados (transferência; critério
  num objetivo).
- Nomes de chave BibTeX com ano diferente do campo `year`.

**Procedimento administrativo**

- Autorizar, ajustar ou remover a entrada proposta no `AI_ASSISTANCE_LOG.md` (G-10).
- Autorizar commit (G-11).
- Os arquivos em `.omp/runs/` são locais. Se o diff do fechamento tiver de ser preservado, convém
  commitar a R19 em dois commits (primeira sessão e fechamento), a partir da cópia de partida.

### I.10 Veredito

As sete correções obrigatórias foram feitas com evidência conferida: fonte primária lida no trecho
citado, código lido nas linhas citadas e, onde cabia, artefato conferido. Nenhum item foi dado como
resolvido apenas por atenuação, compilação ou aprovação pedida. A revisão científica, a verificação
de evidência e a auditoria quantitativa foram independentes; o único achado crítico (S1) foi
integrado; a compilação não tem bloqueantes novos; números, coortes e rótulos não mudaram. O
fechamento técnico e científico da R19 está **concluído**. A dissertação **não está pronta para
depósito** enquanto o autor não decidir G-1 (objetivos e contribuições) e G-2 (terminologia), não
autorizar o registro de IA e o commit, e não escolher entre manter ou não a barreira de *floats* e
citar ou não o CEC 2023. Essas escolhas não alteram nenhum resultado.

---

## J. Comparação com o estado da arte (QP5) — decisão do autor, 2026-10-10, terceira sessão

As seções A–I ficam como estavam. Esta seção registra uma decisão do autor posterior ao
fechamento e supera, onde indicado, o registro de A051 (§C) e a regra de `terminologia.md`
("Não chamar os sete de estado da arte").

### J.1 Decisão e contrato de precisão

Decisão do autor: apresentar a QP5 como comparação com o estado da arte em duas frentes, os
aprimoramentos do SPEA2 e os algoritmos de desempenho geral, premissa do manuscrito de origem; e
propagar com precisão a troca de "posicionamento". Contrato adotado pelo executor:

- "estado da arte" designa só quatro algoritmos, como representantes, sem esgotá-lo: MFO-SPEA2 e
  SPEA2+SDE (aprimoramentos do SPEA2) e AGE-MOEA-II e AR-MOEA (propósito geral, definido como "não
  derivados do SPEA2"); NSGA-II, NSGA-III e MOEA/D são "métodos canônicos";
- "hibridizações do SPEA2", termo usado pelo autor na instrução, **não** foi adotado: nenhum dos
  dois é híbrido no sentido do Cap. 2 (o SPEA2+SDE modifica a densidade; o MFO-SPEA2 usa otimização
  multiforme); o texto usa "aprimoramentos do SPEA2", termo já em uso no Cap. 3;
- nenhuma afirmação de superioridade sobre o estado da arte; contagens, coorte, protocolo, papel
  "Contextual" da família e todas as ressalvas preexistentes mantidos;
- rótulos `sec:posicionamento`, `tab:posicionamento`, `sec:resposta_qp5`, o id
  `context-comparator-positioning` e os nomes de arquivo preservados.

Premissa conferida: o manuscrito de origem (`paper/springer-nature/src/sn-article.tex:280`)
agrupa os comparadores em "host-centered SPEA2 variants", "canonical Pareto/decomposition methods"
e "modern adaptive geometry/reference approaches", e justifica o conjunto como "complementary MOEA
families relevant to the host-coupling question". O artigo **não** usa "state of the art". A
caracterização dos quatro como estado da arte é, portanto, decisão do autor, sem fonte externa que
a estabeleça; o critério de seleção citado no texto é o do manuscrito (§5.2.1), conferido no fonte
LaTeX do repositório e não no PDF do *preprint*.

### J.2 Alterações

| Local final | Antes | Depois |
|---|---|---|
| `cap_I.tex:43` (objetivo 6) | "sete outros algoritmos ..., entre variantes do SPEA2 e métodos baseados em dominância, em decomposição e em adaptação de pontos de referência" | "sete algoritmos ..., quatro representantes do estado da arte em duas frentes (...) e três métodos canônicos" |
| `cap_I.tex:62` (contribuição 6) | "A comparação com outros algoritmos evolutivos multiobjetivo" | "A comparação com o estado da arte e com métodos canônicos", com as duas frentes |
| `cap_I.tex:68` (roteiro) | "aos aprimoramentos do SPEA2"; "a comparação com os sete algoritmos" | "aos algoritmos ... tomados na comparação como representantes do estado da arte"; "a comparação com o estado da arte e com os métodos canônicos" |
| `cap_III.tex:4,22,24,26` | seção "Aprimoramentos do SPEA2 e algoritmos incluídos na comparação" | "Representantes do estado da arte: aprimoramentos do SPEA2 e algoritmos de propósito geral"; anos e papel de cada frente; "sem esgotá-lo"; "é por isso que servem de contexto: eles indicam o que se consegue" → "oferecem um termo de comparação" (generalização da classe retirada) |
| `cap_V.tex:4,18,43,48,103` | "QP5 (posicionamento). Como o IVF/SPEA2 se posiciona"; família "Posicionamento"; "Protocolo do posicionamento" | "QP5 (estado da arte e métodos canônicos). Como o IVF/SPEA2 se compara"; família "Estado da arte e métodos canônicos"; protocolo renomeado |
| `cap_V.tex:61` (§5.2.1, definição canônica) | "em três grupos ... duas abordagens modernas" | "quatro representantes do estado da arte em duas frentes e três métodos canônicos"; critério de seleção do manuscrito de origem (`\cite{zambrano2026ivfspea2}`, chave existente); "propósito geral, isto é, não derivados do SPEA2"; "sem esgotá-lo" |
| `cap_VII.tex:15,62,65,71,99,101` | "se posiciona"; "O posicionamento é favorável"; leitura restrita ao AGE-MOEA-II e ao AR-MOEA | título e respostas com "se compara ao estado da arte e aos métodos canônicos"; §7.5:71 relata as duas frentes (MFO-SPEA2 4/4 favoráveis; SPEA2+SDE 3/4, exceção HV $M=3$ 8/1/14; AGE-MOEA-II e AR-MOEA 6/8) e acrescenta que o MFO-SPEA2 e o SPEA2+SDE foram propostos para problemas com restrições e para o regime *many-objective*, que a suíte não exercita; a restrição de leitura passa a valer para os quatro e "nem para o estado da arte como um todo" |
| `cap_VII_complementares.tex:4,147,150,152,165` | "Comparação com outros sete algoritmos evolutivos multiobjetivo"; "se posiciona"; "um posicionamento não uniforme"; "dois de adaptação de geometria" | "Comparação com o estado da arte e com métodos canônicos"; "se compara"; "um resultado não uniforme"; "dois algoritmos de propósito geral"; "classe de métodos que eles representam" |
| `cap_VIII.tex:22,33` | "situa o IVF/SPEA2 diante de sete algoritmos"; "o posicionamento derivam" | "compara ... entre eles representantes do estado da arte"; "a comparação com o estado da arte e com os métodos canônicos derivam" |
| `pre_resumo.tex`, `pre_abstract.tex` | "Diante de sete outros algoritmos" / "Against seven other algorithms" | "Diante de sete algoritmos, entre eles representantes do estado da arte" / "Against seven algorithms, including state-of-the-art representatives"; `\looseness=-1` no resumo (com comentário) para manter resumo e palavras-chave numa página |
| `build_tab_posicionamento.py` (legenda e nota) → `results/thesis/tab_posicionamento.tex` | "Posicionamento do IVF/SPEA2 frente aos sete algoritmos comparados" | "Comparação do IVF/SPEA2 com representantes do estado da arte e com métodos canônicos"; a nota lista os membros de cada grupo e remete à §5.2.1 |
| `build_apendice_fontes.py` → `results/thesis/apendice_fontes.tex` (Apêndice A, oculto) | "Posicionamento frente aos algoritmos comparados" | título e lacunas alinhados ao contrato |
| `main.tex:204–207` (comentário) | "lugar canônico do posicionamento" | "lugar canônico da comparação com o estado da arte (... sob o nome de posicionamento)" |
| `data-sources.toml` (fonte `context-comparator-positioning`), `results/submission_release_manifest.csv:54` | "positioning" | descrição com as duas frentes; id e caminho preservados |
| `results/submission_release_checksums.sha256` | — | `make write-checksums`: mudaram só o hash de `tab_posicionamento.tex` e o do manifesto |

Diff isolado desta sessão: `.omp/runs/r19-estado-da-arte.diff` (33 trechos); cópia de partida em
`.omp/runs/pre-r19-estado-da-arte/` (locais, fora do git). Documentos de governo: `terminologia.md`
(regra nova e linha "positioning"), `REWRITE_SPEC.md` (§1.5, QP5 vigente com histórico; §6.2,
registro), `REVISION_PLAN.md` (§3).

### J.3 Revisão independente e integração

Revisão científica independente (somente leitura) sobre o diff. Confirmou linha a linha os números
novos contra `tab_posicionamento.tex`, a ausência de afirmação de superioridade e de
"posicionamento" visível. Achados e decisão:

| Achado | Decisão |
|---|---|
| S1 (maior): frase nova "As duas frentes do estado da arte dão resultados distintos" sem suporte na tabela (7/8 contra 6/8; contagens não se somam) | aceito: frase removida |
| S2 (maior): os dois aprimoramentos foram propostos para regimes que a suíte não exercita, e a ressalva estava só no Cap. 3 | aceito: ressalva junto da afirmação na §7.5 |
| S3 (maior): critério de seleção dos "representantes" não declarado | parcialmente: critério do manuscrito de origem citado na §5.2.1; a caracterização como estado da arte continua sem fonte externa (J.1) |
| S4: rótulos curtos "estado da arte" cobriam também os canônicos | aceito: forma completa "estado da arte e métodos canônicos" na contribuição, na QP5, na Tabela 5.1, no protocolo e no Cap. 8 |
| S5: apêndice oculto dizia que os sete representam o estado da arte | aceito: corrigido no gerador |
| S6: "resultados dessa comparação" atribuía à QP5 os resultados de engenharia | aceito: remissão à §6.1 |
| S7: enumeração ambígua (canônicos lidos como terceira frente) | aceito: "quatro representantes ... (...) e três métodos canônicos" |
| S8: a mesma frente com três nomes | aceito: "algoritmos de propósito geral" em todo o texto |
| S9: "recentes" para 2018; "propósito geral" para o AGE-MOEA-II | aceito: "recentes" retirado (os anos ficam); "propósito geral" definido como "não derivados do SPEA2" |
| S10: título e roteiro sugeriam cobertura exaustiva | aceito: "Representantes do estado da arte" no título; roteiro com "tomados na comparação como representantes" |
| S11 (maior): resumo e abstract sem a ressalva da política de configuração, agora mais pesada | **não aplicado; decisão do autor (J.5)**: as versões "em configuração padrão" / "at default settings" foram compiladas e empurram as palavras-chave do resumo para a página seguinte, mesmo com `\looseness` |
| S12: legenda nomeia grupos que a tabela não identifica | aceito: a nota da tabela lista os grupos |
| S13 (preexistente): "eles indicam o que se consegue atacando a geometria" generaliza dois algoritmos para a classe | aceito: reformulado |
| S14: QP5 da §1.5 de `REWRITE_SPEC.md` desatualizada | aceito |

### J.4 Verificação

| Verificação | Resultado |
|---|---|
| `make thesis-tables`; comparação com a cópia de partida | só `tab_posicionamento.tex` e `apendice_fontes.tex` mudaram; linhas de dados da tabela idênticas (comparação por `diff`); demais figuras e tabelas sem mudança no `git status` |
| `make write-checksums`, `make verify-release` | "Release integrity OK" |
| `make thesis-tables-check`, `make thesis-doctor` | OK; "9 evidence sources ... 147 repository paths validated" |
| `make -C thesis/masters -B all` | 110 páginas (igual à partida); 0 *overfull* |
| `latex_check.py --compare` | bloqueantes novos: 0; 3 *underfull* preexistentes |
| `claims.py diff` (8 arquivos) | sem mudança de citação ou rótulo; numerais novos: anos 2018 e 2022 (do `.bib`), "8/1/14" (já na tabela), contagens "quatro", "três", "duas"; `pre_resumo` +"−1" (`\looseness`) |
| `bib_check.py` | ok=53 |
| `prose_audit.py` | 0 alto, 0 médio, 38 avisos (36 antes) |
| `make test` | 58 aprovados |
| PDF (imagem) | p.6 (resumo e palavras-chave numa página), p.7 (abstract), p.9 (sumário), p.51 (Tabela 5.1), p.84 (Tabela 6.13 com legenda e nota novas) |

Erro introduzido e corrigido durante a sessão: ao reescrever a nota da Tabela 5.1, a faixa da
família de hospedeiros saiu como "3001--3060"; foi restaurada para "3001--3030" antes da
compilação, e a revisão independente não encontrou outra alteração de número.

### J.5 Pendências desta sessão

**Decisão do autor**

- S11: incluir no resumo e no abstract a ressalva de que os sete rodaram em configuração padrão,
  diante do IVF/SPEA2 calibrado. Exige cortar outro conteúdo de igual tamanho (cerca de uma linha).
- Fonte externa para chamar os quatro de estado da arte, se houver uma verificada; hoje a
  caracterização é decisão do autor, e o artigo de origem não usa o termo.
- Situação do manuscrito de origem: o autor informou que o artigo foi aprovado; a §7.8 e a entrada
  `zambrano2026ivfspea2` do `.bib` ainda dizem *preprint* (Research Square). Atualizar exige o
  veículo e a referência da aceitação, que não estão no repositório.

**Risco latente**

- Apêndice A oculto: o campo "Implementação" vem em inglês de `data-sources.toml` (preexistente,
  G-7).

---

## K. Taxonomia do manuscrito de origem (QP5) — decisão do autor, 2026-10-10, quarta sessão

Esta seção supera o enquadramento da §J ("estado da arte em duas frentes"), que fica registrado
como etapa intermediária. A troca de "posicionamento" feita na §J permanece.

### K.1 Decisão e o que foi espelhado do artigo

Decisão do autor: usar os termos e a estratégia do manuscrito de origem. Fonte conferida:
`paper/springer-nature/src/sn-article.tex:280, 387, 579-584`.

| Estratégia do artigo | Adotada? | Como ficou na dissertação |
|---|---|---|
| Conjunto justificado como "complementary MOEA families relevant to the host-coupling question" (l.280) | sim | §5.2.1: "três famílias complementares relevantes para a questão do acoplamento ao hospedeiro, como no manuscrito de origem~\cite{zambrano2026ivfspea2}" |
| "host-centered SPEA2 variants" | sim | "variantes do SPEA2, centradas no mesmo hospedeiro" (MFO-SPEA2, SPEA2+SDE). O artigo inclui o próprio SPEA2 no grupo; a dissertação o mantém como comparador principal, fora dos sete |
| "canonical Pareto/decomposition methods" | sim | "métodos canônicos de dominância de Pareto e de decomposição" (NSGA-II, NSGA-III, MOEA/D) |
| "modern adaptive geometry/reference approaches" | sim | "abordagens modernas de adaptação de geometria e de pontos de referência" (AGE-MOEA-II, AR-MOEA) |
| Comparadores "contextual ... rather than co-equal hypotheses" (l.387) | já presente | §5.2.4, sem mudança |
| Leitura por família e por regime, não ranking global (l.580-584) | sim | §7.5 relata cada família com as contagens da Tabela 6.13 |
| "often competitive when front geometry is irregular" (l.280) | **não** | enfraquecido na R19 (N20) por falta de suporte; mantido "projetados para se adaptar" |
| Regra de decisão por geometria da fronteira (l.582) | **não** | contrariada pela família da comparação principal (`OQ-22`; §5.3.3) |
| "60 runs ... stabilizes Wilcoxon testing" (l.389) | **não** | retirado no fechamento (§I, F3) |
| "positioning" como nome da análise (l.511, 579) | **não** | comentário A051 do revisor; "comparação com os sete algoritmos comparados" |
| "state of the art" | o artigo não usa | removido da dissertação |

### K.2 Alterações

Mesmos locais da §J.2, com os termos da taxonomia: `cap_I.tex:43,62,68`; `cap_III.tex:4,22,24,26`
(seção "Variantes do SPEA2 e abordagens modernas incluídas na comparação"); `cap_V.tex:4,18,43,48,61,103`
(QP5 "algoritmos comparados"; família "Algoritmos comparados"; §5.2.1 com as três famílias e o
critério do artigo); `cap_VII.tex:15,62,71,99,101` (§7.5 "QP5: como o IVF/SPEA2 se compara às três
famílias de algoritmos?"); `cap_VII_complementares.tex:4,147,150,165` (§6.5 "Variantes do SPEA2,
métodos canônicos e abordagens modernas"); `cap_VIII.tex:22,33`; resumo e abstract ("Diante de
variantes do SPEA2, métodos canônicos e abordagens modernas, o saldo é desfavorável em 4 de 28
comparações" / "Against SPEA2 variants, canonical methods and modern approaches, losses outnumber
wins in 4 of 28 comparisons"); legenda, nota e rótulos de grupo de `build_tab_posicionamento.py`;
`build_apendice_fontes.py`; `data-sources.toml`; nota do manifesto; comentário de `main.tex`;
checksums. Diff isolado: `.omp/runs/r19-familias.diff`; partida em `.omp/runs/pre-r19-familias/`.

Conteúdo novo: a §7.5 passa a relatar também os métodos canônicos, "o saldo favorece o IVF/SPEA2
em 11 dos 12 contrastes, com a exceção do NSGA-III em IGD com $M = 2$ (9/2/17)". Conferido na
Tabela 6.13: NSGA-II 26/2/0, 20/3/0, 24/1/3, 20/2/1; NSGA-III 9/2/17, 18/2/3, 17/3/8, 13/0/10;
MOEA/D 19/1/8, 21/1/1, 24/2/2, 18/2/3. Mantidas as ressalvas da §J (regimes de projeto das
variantes do SPEA2; leitura restrita aos algoritmos assim configurados; política de configuração).

Ajustes de diagramação, testados numa cópia descartável antes de aplicar: o título da §6.5 sem
"Comparação com" e a legenda com os grupos entre parênteses evitam dois *underfull* novos; a
redação do resumo e do abstract foi escolhida entre quatro variantes por ser a que mantém cada
texto numa página; `\looseness=-1` também no abstract, com comentário.

### K.3 Verificação

| Verificação | Resultado |
|---|---|
| `make thesis-tables`; linhas de dados de `tab_posicionamento.tex` contra a partida | idênticas |
| `make write-checksums`, `verify-release`, `thesis-tables-check`, `thesis-doctor` | OK |
| `make -C thesis/masters -B all` | 110 páginas; 0 *overfull*; resumo (p.6) e abstract (p.7) com palavras-chave na mesma página |
| `latex_check.py --compare` | bloqueantes novos: 0; 3 *underfull* preexistentes |
| `claims.py diff` | sem citação ou rótulo novo; numerais novos "11", "12", "9/2/17" (Tabela 6.13); `sec:RW` saiu de uma remissão da §5.2.1 |
| `bib_check.py`; `make test` | ok=53; 58 aprovados |
| PDF (imagem) | p.7 (abstract), p.82 (§6.5), p.92 (§7.5, antes do encurtamento do título) |

Não houve nova revisão científica independente nesta sessão: a mudança troca termos por outros já
conferidos na fonte e acrescenta uma contagem conferida acima. Recomenda-se incluí-la na próxima
revisão.

### K.4 Pendências

- Da §J.5 restam: ressalva de configuração no resumo e no abstract (decisão do autor) e a
  situação do manuscrito de origem (*preprint* na §7.8 e no `.bib`; o autor informa aprovação).
- A pendência "fonte externa para estado da arte" deixou de existir: o termo saiu do texto.

---

## L. Fechamento das decisões pendentes — decisões do autor, 2026-10-11

O executor levantou as pendências registradas em §G, §I.9, §J.5, §K.4, `REWRITE_SPEC.md` §4 e
§6.3, `AI_ASSISTANCE_LOG.md`, `main.tex` e no `.bib`, e as perguntou ao autor em quatro blocos.
Itens já fechados antes desta sessão e não perguntados: G-5 e G-9 (fechamento da R19, §I.3); DOI
inexistente de `holm1979simple` (já ausente do `.bib`); ambiguidades do resumo herdadas da R17
(já corrigidas no texto); remanescentes "proximidade e cobertura" e "comparação exploratória" (já
ausentes do texto).

### L.1 Decisões e execução

| Item | Decisão do autor | Execução |
|---|---|---|
| Situação do manuscrito Memetic Computing | ainda em revisão | nenhuma; continua *preprint* na §7.8 e no `.bib`. Isso corrige a informação de "aprovado" registrada em §J.5 e §K.4 |
| Errata dos manuscritos (`OQ-01`, `-02`, `-04`, `-15`, `-16`, `-19`, `-21`, `-22`, `-24`, `-25`, l.389 e l.582 do Springer) | manter os manuscritos como estão | nenhuma; registro em `REWRITE_SPEC.md` §6.3 |
| `OQ-03` | corrigir o script, sem errata | `test_convergence_significance.py`: pareamento por identificador quando há interseção, alinhamento por ordem quando não há, aviso em todo descarte, colunas `pairing`, `p_value_robustness`, `p_adj_robustness` (Mann–Whitney com BH na própria família). `convergence_significance.csv`: 612 → 918 linhas. Efeito colateral: os `p_adj` dos pares NSGA mudaram com a família maior (NSGA-III 125 → 140; NSGA-II 71 → 77 testes com `p_adj < 0,05`); nenhum manuscrito lê esse CSV. Par IVF/SPEA2 × SPEA2: 229 de 306 no teste principal, 246 de 306 no de robustez |
| Robustez do pareamento por ordem | mesma checagem da família de hospedeiros (`OQ-20`) | incluída na linha acima |
| CEC 2023 | não citar | nenhuma; o comentário de proveniência em `cap_III.tex:12` permanece |
| Números de Sampaio (`cap_VII.tex:45`) | o executor confere na tese | conferidos: 11/8/4 (Tabela 4.56, p.181) e 5/17/1 (Tabela 4.60, p.187); 23 problemas, 31 execuções, 25.000 avaliações, Wilcoxon sem correção, taxa e coleta de 10%. Corrigido só o rótulo "variante sem extensões" → variante base com busca guiada por balizas, fator de escala autoadaptativo e até três ciclos, sem *steady state* nem ruído adaptativo (Tabela 4.54 e descrição do Experimento 6) |
| `OQ-10` (autoria e reúso) | não é necessário | nenhuma |
| G-1 (objetivos e contribuições) | objetivo geral reescrito; o resto aprovado | `cap_I.tex:35`: "avaliar se ele melhora o desempenho do hospedeiro com o mesmo número de avaliações das funções objetivo" (forma escolhida pelo autor entre quatro). Resumo e abstract alinhados ("com o mesmo número de avaliações das funções objetivo" / "under the same number of objective-function evaluations"). Risco apontado ao autor: os objetivos específicos 4 a 6 ficam fora da letra do objetivo geral |
| G-2 (terminologia) | ratificada sem exceção | registro em `terminologia.md` |
| G-3 (paisagem × superfície) | manter "paisagem" | registro em `terminologia.md` |
| G-4 (siglas, A049) | expandir só com fonte | `cap_V.tex:71-72`: ZDT e DTLZ com os autores. WFG e MaF ficam como nomes próprios: a expansão "Walking Fish Group" só aparece em fontes secundárias (documentação de pacotes R), e o artigo de Cheng et al. (2017), lido no editor, não expande MaF |
| Q1 | explicitar os pares | `cap_IX.tex:15`, `cap_VII_complementares.tex:84`: "nove pares de função e número de objetivos" |
| G-12 (legendas) | acrescentar a chave | Fig. 5.2 (critério de escolha das execuções 3019 e 3049) e Fig. 6.4 (ponto = mediana de 30 execuções; classes 41 e 10; limiar 0,216), com os valores já presentes no parágrafo vizinho |
| Resumo e abstract | só a ressalva S11 | "estes em configuração padrão" / "all at default settings" na frase dos sete algoritmos. Para caber: a frase foi para depois da de ativação; saíram "para o IVF/SPEA2" após +1,15%, "de doador e de ciclo" e "nesta suíte" (resumo) e "in favour of IVF/SPEA2" (abstract); "Descritores medidos antes da execução" virou "Descritores estáticos" / "Static descriptors" |
| F6c | aceitos | nenhuma |
| F7b (`\FloatBarrier`) | manter | nenhuma |
| G-8 (Figura 2.3) | manter | nenhuma |
| G-7 (Apêndices A e B) | manter ocultos | comentário de `main.tex` e `REVISION_PLAN.md` §4 atualizados; a declaração de disponibilidade dos dados segue fora do PDF |
| Apêndice C | aposentar | `pos/apend_III.tex` removido; `\input` comentado retirado de `main.tex`; o histórico do git preserva a última versão |
| Data de defesa | 27/10/2026 | `main.tex` (`\dia`, `\mes`). Banca, folha de aprovação, `\publica` e declaração de formato seguem pendentes |
| Pré-textuais | manter os padrões; o autor escreverá | nenhuma |
| Declaração de uso de IA | rascunho para revisão | `rascunho_declaracao_ia.md`, fora da compilação |
| G-10 (log de IA) | autorizado | marcador de pendência substituído pela autorização; entrada desta sessão acrescentada |
| G-11 (commits) | commit único | executado no fim desta sessão, sem `paper/clei2026/` nem `WATCHDOG.yml` |
| `OQ-09` (DOI do código) | manter o DOI de conceito | nenhuma no `.bib`; `OQ-09` fechada |
| DOIs do `.bib` | só correspondência exata | 20 DOIs acrescentados (16 pelo subagente com regra estrita; 4 conferidos pelo executor — `talbi2009metaheuristics`, `knowles2000memetic`, `deb2005scalable`, `platemo` — em que título, autores e páginas batem e o Crossref só difere por tipo "monograph", ano ausente ou sufixo editorial no título). Ficaram sem DOI 9 entradas: relatórios técnicos, a tese de Sampaio, livro de outra edição, obra sem candidato e os três manuscritos próprios. Corrigidos a autoria (eram os autores de outro artigo) e o veículo de `cheng2017benchmark`, pela página do editor |

### L.2 Verificação

| Verificação | Resultado |
|---|---|
| `make -C thesis/masters -B all` | 110 páginas; resumo (p.6) e abstract (p.7) com palavras-chave na mesma página |
| `latex_check.py --compare` | bloqueantes novos: 0; dois *underfull* novos de badness ≤ 2285 (legenda da Fig. 5.2 e uma entrada da bibliografia, deslocada pelos DOIs) |
| `claims.py diff` | números novos só nas legendas (já no parágrafo vizinho) e no parágrafo de Sampaio (conferidos na tese); nenhuma citação ou rótulo mudou |
| `bib_check.py` | ok=53 |
| `make thesis-tables-check`, `make verify-release` | OK |
| `ruff` | sem achados no script alterado |

### L.3 Pendências que continuam

- banca, folha de aprovação, `\publica` e declaração de formato (Resolução INF nº 02/2023);
- agradecimentos e demais pré-textuais (o autor redige);
- aprovação e destino do rascunho de declaração de uso de IA (autor e orientador);
- `OQ-02` e `OQ-04` continuam bloqueadas; os manuscritos não serão alterados;
- revisão das respostas da §8 de `REWRITE_SPEC.md` e das remissões ao Cap. 9 (pendentes desde a R18);
- decidir se a precisão "observável e janela escolhidos antes das dobras" entra no resumo e no abstract (o autor optou, nesta sessão, só pela ressalva S11).

## M. Ajustes pós-R19 — cinco imprecisões locais, 2026-10-11

Escopo fixado pela instrução da tarefa; nenhum número, coorte, teste ou conclusão mudou. Diff em
`.omp/runs/r19-ajustes.diff`.

| Item | Antes | Depois | Evidência | Verificação |
|---|---|---|---|---|
| P1 | `cap_VI.tex:63` "correspondem a nove funções"; `cap_V.tex:77` "49 funções distintas"; nota da Tabela 5.8 "nove funções" | "nove pares de função e número de objetivos"; "49 pares distintos de função e número de objetivos"; nota pelo gerador `build_tab_geometria_confirmatoria.py` | `config/hosts_front_geometry.csv`: 51 linhas, 49 pares (função, $M$) após juntar MaF7 e DTLZ7, 9 pares e 7 funções entre as 11 irregulares. Ocorrências WFG ("nove funções" em `cap_VII.tex:86`, `data-sources.toml`, `build_tab_wfg_exploratoria.py`) e "três funções" (`cap_VII.tex:21`) estão corretas e ficaram | `make thesis-tables`: só `tab_geometria_confirmatoria.tex` mudou |
| P2 | `cap_VII_complementares.tex:135` "A regra e a partição de suítes acertam as mesmas decisões nesse resumo" | "todo acerto da regra é também acerto da partição de suítes, mas a partição acerta ainda o DTLZ6 com $M=2$ e $M=3$, em que a regra erra"; ressalva causal mantida | Recálculo descartável com os limiares de `dynamic_signal_lofo.csv`: 37 acertos da regra (29+8, como tp/tn do artefato), 39 da partição, 0 acertos só da regra, 2 só da partição (DTLZ6, $M=2$ e $3$, "ajuda"); BA 0,7537 e 0,7780; Tabelas 6.10 e 6.11 | `claims.py diff`: números novos só os $M$ já presentes na frase anterior |
| P3 | `cap_II.tex:223` "que explora o pareamento e tem maior poder"; l.225 sem remissão | Afirmação de poder retirada; l.225 remete ao par IVF/SPEA2 da família de hospedeiros: "os dois algoritmos têm o mesmo número de execuções, alinhadas por ordem", Mann–Whitney como robustez, `sec:hospedeiros` (decisão do autor: não dizer que as faixas não coincidem) | Sem fonte para o poder; a exceção está em `cap_VII_complementares.tex:63` e na nota de `tab_hosts_wtl.tex` | Referência cruzada nova resolvida (Seção 6.3) |
| P4 | `cap_V.tex:84` "desses 10.000 pontos de referência" | "dos pontos de referência devolvidos por essa chamada" | `UniformPoint.m:4-8` (quantidade aproximada); NBI com $M=3$ devolve 9.870 pontos (recálculo de `nchoosek`); ZDT3, WFG2 e MaF2 filtram pontos | *Underfull* conhecido em cap_V:84 com a mesma badness (1776); sem *overfull* |
| P5 | `cap_V.tex:63` "o total de avaliações é idêntico para todos" | "o orçamento de avaliações é o mesmo para todos", e a plataforma encerra a execução depois da primeira geração em que o consumo acumulado atinge ou ultrapassa o orçamento | `ALGORITHM.m:101-128` (verificação ao fim da geração); `NSGAIII.m` com `OperatorGA.m` (90 descendentes por geração com $N=91$); `MOEAD.m` (91 por geração). O consumo final da coorte principal não está nos consolidados. Na família de hospedeiros (`results/tables/convergence_summaries.csv`, `fe_max`), o NSGA-III com $M=3$ termina em 100.081 nas 690 execuções, e SPEA2 e IVF/SPEA2 em 100.000. Nenhum valor citado no texto, porque as execuções do NSGA-III e do MOEA/D da comparação principal são outras | `cap_I.tex:35` e o resumo ("mesmo número de avaliações") não foram tocados |

Verificação geral: `make thesis` com 110 páginas e 0 *overfull*; `latex_check.py --compare` sem
bloqueante novo; `thesis-tables-check`, `verify-release`, `bib_check.py`, `thesis-doctor` e
`make test` OK; resumo (p.6) e abstract (p.7) em uma página cada.

### M.1 Faixas de identificadores de execução retiradas do texto — decisão do autor

O autor decidiu que o texto informa só a quantidade de execuções; os identificadores ficam no
repositório (`results/submission_release_manifest.csv`, coluna de coorte, e `data-sources.toml`).

| Local | Antes | Depois |
|---|---|---|
| `cap_V.tex:24` | "As execuções são identificadas por faixas numéricas, e a coorte de cada família é a faixa de execuções que ela usa; a Seção … explica as faixas…" | "A coorte de cada família é o conjunto de execuções que ela usa; a Seção … descreve a da avaliação comparativa principal." |
| `cap_V.tex:38,41` (Tabela 5.1) | "IVF/SPEA2 3001--3060 contra SPEA2 1--60"; "IVF 3001--3030, 4001--4030 e 5001--5030" | "IVF/SPEA2 contra SPEA2"; "Três acoplamentos IVF; 51 instâncias" |
| `cap_V.tex:48` (nota da Tabela 5.1) | "As execuções 3001--3030 e 1--30…"; "(o IVF/SPEA2 nas execuções 3001--3060 e cada algoritmo comparado nas execuções 1--60)" | "As execuções do par IVF/SPEA2…"; parêntese retirado |
| `cap_V.tex:91` | "…por algoritmo e instância: o IVF/SPEA2 nas execuções 3001 a 3060 e o SPEA2 e cada algoritmo comparado nas execuções 1 a 60, com orçamento…" | "…por algoritmo e instância, com orçamento…" |
| `cap_VI.tex:46` | "execuções 3001 a 3060 do IVF/SPEA2 e 1 a 60 do SPEA2, com $n = 60$ por instância e algoritmo" | "com $n = 60$ execuções por instância e algoritmo" |
| `cap_VII_complementares.tex:63` | "as execuções 3001--3030 e 1--30 do par IVF/SPEA2…, e só as execuções 4001--4030 e 5001--5030 acrescentam…"; "gerou as execuções 5001--5030"; "os pares NSGA compartilham a faixa de execuções… no par IVF/SPEA2, as faixas não coincidem e as execuções são alinhadas por ordem" | "as execuções do par IVF/SPEA2…, e só as dos pares IVF/NSGA-II e IVF/NSGA-III acrescentam…"; "gerou as execuções do IVF/NSGA-III"; "nos pares NSGA, acoplamento e hospedeiro compartilham os identificadores de execução… no par IVF/SPEA2, os dois algoritmos têm o mesmo número de execuções, alinhadas por ordem" |
| `cap_VII_complementares.tex:150` | "(o IVF/SPEA2 nas execuções 3001--3060 e cada algoritmo comparado nas execuções 1--60, 60 execuções por instância e algoritmo)" | ", com 60 execuções por instância e algoritmo," |
| Notas geradas: `build_tab_confirmatorio.py`, `build_tab_magnitude_confirmatoria.py` (3 notas), `build_tab_posicionamento.py`, `build_tab_hosts.py` (2 trechos), `build_tab_tuning_ablacao.py` | "execuções 3001--3060 contra 1--60" e variantes; "as faixas não coincidem (3001--3030 e 1--30)"; "execuções 1--60 da formulação anterior" | quantidade ("60 execuções por algoritmo e instância"); "os dois algoritmos têm o mesmo número de execuções, alinhadas por ordem"; "às 60 execuções da formulação anterior" |

Mantidos: `cap_V.tex:91` "execuções de faixas históricas distintas" (justifica a filtragem, sem
identificadores); `cap_VI.tex:37` ("faixas de IGD", outro sentido); o Apêndice A oculto
(`build_apendice_fontes.py`, fora do PDF); docstrings dos geradores; as execuções 3019 e 3049 do
DTLZ4 (`cap_VI.tex:67,73` e rótulos da Figura 5.2), que são identificadores individuais e aguardam
decisão do autor.

Efeito no manifesto: `results/thesis/tab_posicionamento.tex` é linha do manifesto e só a nota
mudou; `make write-checksums` regravou o hash dela (e o do próprio manifesto). A coluna de coorte do
manifesto continua com as faixas, que é onde o leitor as encontra.

Verificação: `make thesis-tables` (8 tabelas mudaram, só nas notas), `thesis-tables-check` OK,
`verify-release` OK após `write-checksums`, `make thesis` com 110 páginas e 0 *overfull*,
`latex_check.py --compare` sem bloqueante novo, `claims.py diff` (números removidos são só faixas;
acrescentados: "51" e "três" na Tabela 5.1, "60" na nota da ablação, conferidos em
`tab_hosts_wtl.tex`, `cap_VII_complementares.tex:61` e na faixa original 1–60).
