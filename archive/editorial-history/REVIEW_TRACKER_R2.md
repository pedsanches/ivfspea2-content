# Revisão R2 — Observações Manuais do Autor + Histórico Elsevier

## Contexto

Este documento registra a segunda rodada de revisão do manuscrito IVF/SPEA2, composta por:

1. **Revisão manual do autor** sobre o texto atual (pós todas as correções do REVIEW_TRACKER.md)
2. **Revisões dos pareceristas Elsevier** recebidas sobre a versão incipiente anterior

A R1 (REVIEW_TRACKER.md) tratou da reestruturação interna do paper. A R2 trata do polimento para submissão, incorporando tanto a visão do autor quanto os pontos levantados pelos revisores originais.

---

## Status Geral

| ID | Seção | Problema | Severidade | Status |
|----|-------|----------|-----------|--------|
| G1 | Global | Em-dashes (`---`) em texto acadêmico | Média | Concluído |
| G2 | Global | Uso excessivo de parênteses | Média | Concluído |
| G3 | Global | Abreviações repetidas em parênteses | Baixa | Concluído |
| G4 | Global | Figuras empurradas para o final do PDF | Alta | Concluído |
| G5 | Global | Itens flutuantes (tabelas/figuras/algoritmos) sem contextualização adequada | Alta | Concluído |
| G6 | Global | Referências repetidas a "three-phase tuning pipeline (Section 4.6)" | Média | Concluído |
| M1 | Secs. 1, 2.1, 2.3 | Referências a many-objective em paper focado em multi-objective | Média | Concluído |
| S3 | Sec. 3 | Implementation note excessivamente técnico para artigo de revista | Média | Concluído |
| S33 | Sec. 3.3 | Revisar fórmulas de complexidade; diferenciar custo IVF/SPEA2 vs SPEA2 puro | Média | Concluído |
| S34 | Sec. 3.4 | Verificar integridade e atualidade do Algorithm 1 | Alta | Concluído |
| S41 | Sec. 4.1 | Parágrafo sobre AGE-MOEA-II/AR-MOEA parece desnecessário | Média | Concluído |
| S42a | Sec. 4.2 | Falta explicitar que usamos defaults do PlatEMO para comparação justa | Média | Concluído |
| S42b | Sec. 4.2 | Table 1 confusa/grande demais; considerar reduzir ou eliminar | Média | Concluído |
| S43 | Sec. 4.3 | Texto do Engineering Selection Protocol grande e pouco científico | Média | Concluído |
| S45a | Sec. 4.5 | Justificar 60 runs (30 já seriam suficientes; 60 reforça segurança) | Baixa | Concluído |
| S45b | Sec. 4.5 | Faltam citações para Wilcoxon, Holm-Bonferroni | Alta | Concluído |
| S45c | Sec. 4.5 | "Rationale for pairwise" sem citação de suporte | Média | Concluído |
| S45d | Sec. 4.5 | Parágrafo redundante sobre HV como indicador secundário | Baixa | Concluído |
| S46a | Sec. 4.6 | Risco de viés: tuning sobre subset que faz parte da experimentação | Alta | Concluído |
| S46b | Sec. 4.6 | Faltam heatmaps de sensibilidade mencionados no texto | Média | Concluído |
| S51 | Sec. 5.1 | Verificar se IGD + OOS + Holm fazem sentido juntos na Table 2 | Média | Concluído |
| S52 | Sec. 5.2 | Redundância entre texto e descrição das tabelas | Média | Concluído |
| S53 | Sec. 5.3 | Referência a pastas/diretórios no texto; tom pouco científico | Média | Concluído |

---

## Detalhamento das Observações

### G1 — Em-dashes (`---`) em texto acadêmico

**Problema:** O caractere em-dash (renderizado como "---" em LaTeX) não é padrão em redação acadêmica formal. Preferir reestruturação da frase ou uso de vírgulas/ponto-e-vírgula.

**Ação:** Buscar todas as ocorrências de `---` no manuscrito e substituir por construções mais formais (vírgulas, ponto-e-vírgula, ou frases reestruturadas).

### G2 — Uso excessivo de parênteses

**Problema:** Parênteses em excesso prejudicam a fluidez da leitura acadêmica. Informações entre parênteses podem frequentemente ser integradas ao texto principal.

**Ação:** Revisar passagem por passagem; integrar conteúdo parentético ao texto quando possível, ou converter em frases subordinadas.

### G3 — Abreviações repetidas em parênteses

**Problema:** O ideal é introduzir cada abreviação uma única vez, na primeira ocorrência, e depois usar apenas a sigla.

**Ação:** Auditar todas as abreviações; garantir definição única na primeira ocorrência.

### G4 — Posicionamento de figuras

**Problema:** Todas as 6 figuras estão usando `[t]` ou similar, mas o LaTeX pode empurrá-las para o final se não houver espaço. As figuras devem aparecer próximas ao texto que as referencia para máximo impacto.

**Localização atual das figuras:**
- Fig. 1 (flowchart): linha 197 — Sec. 3
- Fig. 2 (boxplot IGD M=2): linha 430 — Sec. 5.1
- Fig. 3 (boxplot IGD M=3): linha 436 — Sec. 5.1
- Fig. 4 (heatmap A12 M=2): linha 458 — Sec. 5.2
- Fig. 5 (heatmap A12 M=3): linha 464 — Sec. 5.2
- Fig. 6 (pareto fronts): linha 522 — Sec. 6.3

**Ação:** Verificar o PDF compilado; se necessário, usar `[!htbp]` ou `\FloatBarrier` para forçar posicionamento. Garantir que cada figura aparece na mesma página ou página seguinte à sua primeira menção.

### G5 — Contextualização de itens flutuantes

**Problema:** Tabelas, figuras e algoritmos precisam de: (1) introdução contextual antes da referência, (2) evidenciação do que o item mostra e por que está ali.

**Ação:** Revisar cada `\ref{fig:...}` e `\ref{tab:...}` para garantir que há frase introdutória + frase interpretativa.

### G6 — Referências repetitivas ao tuning pipeline

**Problema:** 9 ocorrências de "three-phase tuning pipeline" no texto. Após a primeira definição, usar forma abreviada.

**Ação:** Definir na primeira menção; usar "the tuning pipeline" ou "the pipeline (Section 4.6)" nas demais.

---

### M1 — Referências a many-objective

**Problema:** O paper testa apenas M=2 e M=3 (multi-objective). Referências a many-objective (M>=4) aparecem em:
- Sec. 1, linha 138: "In many-objective settings this effect is further amplified..."
- Sec. 2.1, linha 149: "In many-objective settings, dominance pressure weakens..."
- Sec. 2.3: contexto da tabela comentada

**Discussão necessária:** Manter como motivação contextual (por que density matters) é defensável, mas deve ficar explícito que não é o foco do paper. Alternativa: reformular para "as the number of objectives grows" sem usar o termo "many-objective" diretamente, evitando expectativa de experimentos com M>=4.

**Ação:** Decidir entre (a) manter com disclaimer explícito ou (b) reformular sem o termo. Recomendação: opção (b) nas Secs. 1 e 2.1; manter em 2.3 apenas se relevante para o gap.

---

### S3 — Implementation note técnico demais

**Problema:** O parágrafo na linha 191 menciona nomes de classes (`IVFSPEA2V2`), diretórios (`IVF-SPEA2-V2/`) e detalhes de implementação. Isso é mais adequado para um repositório do que para um artigo de revista.

**Ação:** Mover detalhes de classe/diretório para uma nota de rodapé ou para a seção de Code/Data Availability. No corpo, manter apenas a distinção conceitual (dissimilar father + collective criterion).

### S33 — Complexidade computacional

**Problema:** As fórmulas de complexidade precisam revisão. Seria valioso mostrar explicitamente o custo adicional do IVF sobre o SPEA2 puro (delta de complexidade).

**Ação:** Revisar fórmulas; adicionar comparação explícita $O(\text{IVF/SPEA2}) - O(\text{SPEA2})$ para evidenciar overhead marginal.

### S34 — Integridade do Algorithm 1

**Problema:** O pseudocódigo precisa estar 100% alinhado com a implementação v2 (IVFSPEA2V2). Verificar se todas as mudanças (dissimilar father, collective criterion, $n_{\text{ivf}}$) estão refletidas.

**Ação:** Comparar linha a linha com `IVFSPEA2V2.m` e `IVF_V2.m`.

### S41 — Parágrafo sobre AGE-MOEA-II/AR-MOEA em 4.1

**Problema:** O parágrafo que explica avaliações extras para AGE-MOEA-II e AR-MOEA parece deslocado e desnecessário.

**Ação:** Avaliar se a informação pode ser compactada em uma nota de rodapé ou integrada à Table 1.

### S42a — Defaults do PlatEMO

**Problema:** Falta declaração explícita de que todos os baselines usam parâmetros default do PlatEMO para garantir comparação justa.

**Ação:** Adicionar frase clara: "All baseline algorithms use their default PlatEMO parameter settings to ensure a fair comparison."

### S42b — Table 1 (parâmetros)

**Problema:** A tabela é grande e redundante se todos usam defaults. Considerar compactar drasticamente ou substituir por uma nota textual.

**Ação:** Avaliar: (a) manter compacta com apenas parâmetros que diferem do default, ou (b) substituir por frase + nota de rodapé.

### S43 — Engineering Selection Protocol

**Problema:** Seção 4.3 é longa e o tom não parece suficientemente científico para um artigo de revista.

**Ação:** Revisar e compactar. Focar no critério de seleção (por que esses problemas e não outros) com linguagem mais formal.

### S45a — Justificativa para 60 runs

**Ação:** Adicionar frase: "While 30 independent runs are generally considered sufficient for statistical reliability in MOEA comparisons [ref], we use 60 runs to further strengthen confidence in the reported statistics."

### S45b — Citações para testes estatísticos

**Problema:** Wilcoxon rank-sum e Holm-Bonferroni são usados sem citação dos papers originais.

**Ação:** Adicionar:
- Wilcoxon: `wilcoxon1945individual` (ou referência adequada)
- Holm: `holm1979simple`

### S45c — Rationale sem citação

**Problema:** O texto diz que pairwise testing é recomendado mas não cita fonte.

**Ação:** Adicionar citação de suporte (e.g., Derrac et al. 2011, ou Garcia et al. 2009 — referências padrão para testes estatísticos em metaheurísticas).

### S45d — Parágrafo redundante sobre HV

**Problema:** HV como indicador secundário já foi introduzido anteriormente; parágrafo dedicado pode ser redundante.

**Ação:** Avaliar se pode ser compactado em 1-2 frases integradas ao parágrafo principal de métricas.

### S46a — Viés de tuning

**Problema crítico:** Se o tuning foi feito sobre um subset (FULL12) que faz parte do benchmark experimental, há risco de viés. Os baselines não foram tuned no mesmo subset.

**Discussão necessária:** O paper já separa FULL12 (tuning) de OOS (confirmação com 39 instâncias). Mas precisa ficar mais explícito que: (1) os baselines usam seus defaults publicados (que também foram tuned em algum benchmark), e (2) a separação FULL12/OOS mitiga o risco.

**Ação:** Reforçar a argumentação de fairness: explicitar que defaults dos baselines também foram tuned por seus autores em benchmarks similares, e que a validação OOS é a evidência primária de generalização.

### S46b — Heatmaps de sensibilidade ausentes

**Problema:** A Sec. 4.6 descreve o pipeline de tuning com fases A/B/C mas não inclui visualizações dos resultados de sensibilidade.

**Ação:** Avaliar se heatmaps de sensibilidade (já existentes em `results/figures/`) devem ser incluídos no paper ou em material suplementar.

### S51 — Composição da Table 2

**Problema:** Verificar se ter IGD, indicador OOS e correção de Holm na mesma tabela é coerente e não sobrecarrega.

**Ação:** Revisar Table 2. Se necessário, separar em sub-tabelas ou simplificar.

### S52 — Redundância texto-tabela em 5.2

**Problema:** O texto repete informações que já estão nas tabelas detalhadas.

**Ação:** Reescrever parágrafos de 5.2 para: (1) contextualizar a tabela antes de referenciá-la, (2) destacar apenas os padrões principais (não repetir números), (3) interpretar o que os números significam.

### S53 — Referências a diretórios em 5.3

**Problema:** Menções a caminhos de arquivos/pastas no texto de resultados quebram o tom acadêmico.

**Ação:** Remover referências a pastas; substituir por referências ao protocolo ou à seção de disponibilidade de código.

---

## Mapeamento: Revisores Elsevier vs. Observações Atuais

As revisões Elsevier foram sobre uma **versão anterior e incipiente** do manuscrito. Muitos pontos já foram tratados na R1. A tabela abaixo mapeia o que foi resolvido e o que permanece relevante.

### Reviewer #1

| # | Ponto do Reviewer | Status pós-R1 | Relevância na R2 |
|---|-------------------|--------------|-------------------|
| 1 | Qual operador IVF foi usado? Não especificado | **Resolvido** — Sec. 3.1 agora especifica EAR-P com config C26 | Verificar clareza (S34) |
| 2 | Falta caso compelling para SPEA2 como host | **Resolvido** — Intro reescrita com mecanismo density-truncation | -- |
| 3 | Falta análise mecanística de por que funciona/falha | **Resolvido** — Sec. 6.3 (Mechanistic Interpretation) adicionada | -- |
| 4 | Conclusões overstated | **Parcialmente resolvido** — Abstract e Conclusion revisados | Vigilância contínua |
| 5 | Parâmetros sem sensitivity analysis | **Resolvido** — Pipeline de tuning 3 fases + Sec. 4.6 | Verificar S46a (viés) |
| 6 | Baselines desatualizados | **Resolvido** — AGE-MOEA-II, AR-MOEA adicionados | -- |

### Reviewer #2

| # | Ponto do Reviewer | Status pós-R1 | Relevância na R2 |
|---|-------------------|--------------|-------------------|
| 1 | Falta sensitivity analysis | **Resolvido** — Sec. 4.6 + 6.4 | S46a, S46b |
| 2 | Operador não especificado | **Resolvido** | S34 (verificar Algorithm 1) |
| 3 | Falta explicação da adaptação para SPEA2 | **Resolvido** — Sec. 3.4 expandida | -- |
| 4 | Posição invertida nas tabelas + screenshots | **Resolvido** — Tabelas LaTeX refeitas | -- |
| 5 | Faltam problemas reais | **Resolvido** — RWMOP suite adicionada (Sec. 5.3) | S53 (tom) |
| 6 | Falta análise de complexidade | **Parcialmente resolvido** — Sec. 3.3 adicionada | S33 (delta de custo) |

### Reviewer #3

| # | Ponto do Reviewer | Status pós-R1 | Relevância na R2 |
|---|-------------------|--------------|-------------------|
| 1 | Novidade limitada | **Mitigado** — H1 (dissimilar father) + H2 (collective criterion) + mecanismo clarificado | Vigilância contínua |
| 2 | Falta pseudocódigo + parâmetros dos comparados | **Resolvido** — Algorithm 1 + Table 1 | S34, S42b |
| 3 | SPEA2 puro supera outros (estranho) | **Mitigado** — Discussão ampliada; resultados com 60 runs | -- |
| 4 | Faltam problemas práticos | **Resolvido** — RWMOP suite | S53 |

---

## Plano de Execução R2

| Passo | IDs | Descrição | Esforço | Status |
|-------|-----|-----------|---------|--------|
| 1 | G1, G2, G3 | Limpeza editorial global (em-dashes, parênteses, abreviações) | Médio | Concluído |
| 2 | G4, G5 | Posicionamento e contextualização de figuras/tabelas | Médio | Concluído |
| 3 | M1, S3, S53 | Ajuste de tom: many-objective, implementation note, referências a pastas | Baixo | Concluído |
| 4 | S34, S33 | Integridade do Algorithm 1 + revisão de complexidade | Médio | Concluído |
| 5 | S41, S42a, S42b, S43 | Limpeza do Setup (parágrafos desnecessários, Table 1, tom) | Médio | Concluído |
| 6 | S45a, S45b, S45c, S45d | Protocolo estatístico: citações e justificativas | Baixo | Concluído |
| 7 | S46a, S46b | Argumentação de fairness no tuning + heatmaps | Médio | Concluído |
| 8 | S51, S52 | Revisão de tabelas de resultados e redundância | Médio | Concluído |
| 9 | G6 | Reduzir repetição de "three-phase tuning pipeline" | Baixo | Concluído |

---

## Log de Sessões R2

### Sessão 1 — 2026-03-01
- Documento criado a partir de revisão manual do autor sobre o manuscrito pós-R1
- Mapeamento completo das revisões Elsevier originais vs. estado atual
- 22 itens catalogados (7 globais + 15 por seção)
- Plano de execução em 9 passos definido

### Sessão 2 — 2026-03-01 (Passo 1: G1 + G2 + G3)
- **G1 concluído:** 4 em-dashes removidos. Linha 136: `---` → `, i.e.,`; linha 158: `---...---` → `, namely...,`; linha 366: `---...---` → `, with...and...,`; linha 570 (CRediT): `---` → parênteses (formato Springer).
- **G2 concluído:** 20 parênteses explicativos convertidos em construções integradas (vírgulas apositivas, cláusulas subordinadas, `such as`, `specifically against`, `particularly`, etc.). Parênteses para definições de abreviações (MOPs, MOEAs, IGD) e valores matemáticos mantidos como padrão.
- **G3 concluído:** Auditoria de abreviações confirma definição única por termo. EAR-P: expansão movida para primeira ocorrência (Sec. 3.1) e removida da segunda (Sec. 4.1). SBX: expansão "Simulated Binary Crossover" adicionada na primeira ocorrência (Sec. 3.1). AR: expansão "Assisted Recombination" adicionada na primeira ocorrência. IVF definido no abstract e body separadamente (convenção editorial aceitável).
- Build limpo: sem warnings de referência/citação indefinida.

### Sessão 3 — 2026-03-01 (Passo 2: G4 + G5)
- **G4 concluído:** Duas `\FloatBarrier` adicionadas: antes do parágrafo dos heatmaps A12 (Sec. 5.2) e antes da subsection Engineering (Sec. 5.3). Figs. 4-5 passaram de 4-5 páginas de gap para 1-2 páginas. Todas as figuras agora aparecem dentro de 1-2 páginas da primeira referência. Corrigida dupla vírgula residual na linha 197 (artefato do Passo 1).
- **G5 concluído:** Auditoria de contextualização em 12 itens flutuantes (6 figuras, 5 tabelas, 1 algoritmo). Melhorias aplicadas em: Table 1 (adicionado propósito de replicação), Algorithm 1 (frase introdutória com destaque dos três elementos-chave do pseudocódigo), Fig. 6 (referência solta convertida em frase interpretativa contrastando sucesso DTLZ2 vs. falha WFG2). Demais itens já tinham contextualização adequada (Table 2, Tables 3-4, Figs. 2-3, Figs. 4-5, Table 5, Tables A1-A2).
- Build limpo: sem warnings de referência/citação indefinida.

### Sessão 4 — 2026-03-01 (Passo 3: M1 + S3 + S53)
- **M1 concluído:** 4 de 5 ocorrências de "many-objective" reformuladas para evitar expectativa de experimentos M≥4. Linha 142: "In many-objective settings" → "As the number of objectives grows". Linha 153: "In many-objective settings" → "As the number of objectives increases". Linha 159: "Recent many-objective baselines" → "Recent baselines originally designed for higher-dimensional objective spaces". Linha 158: "In many-objective optimization" → "In higher-dimensional objective settings". Linha 336: MaF clarificado que usamos configurações M=3. Linha 388 (External Validity): mantida como disclaimer legítimo.
- **S3 concluído:** Linha 191 reescrita — nomes de classes (`IVFSPEA2V2`) e diretórios (`IVF-SPEA2-V2/`) movidos para nota de rodapé. Corpo mantém apenas informação conceitual (dissimilar father + collective criterion) com referência cruzada para Sec. 3.1.
- **S53 concluído:** Linha 473 — referências a `\texttt{data/engineering\_suite/}` e caminho de script removidas; substituídas por descrição genérica + nota de rodapé apontando para Code Availability. Verificação: `\texttt{OperatorGAhalf}` na Table 1 (linha 315) mantido — nome de operador PlatEMO necessário para reprodutibilidade. Seção Code Availability (linha 571) mantém caminhos — backmatter é o local adequado para detalhes técnicos.
- Build limpo: 31 páginas, sem erros.

### Sessão 5 — 2026-03-01 (Passo 4: S34 + S33)
- **S34 concluído:** Auditoria linha a linha do Algorithm 1 contra `IVFSPEA2V2.m` e `IVF_V2.m`. Todos os 15 elementos verificados: parâmetros, ativação, seleção de mães, father pool, ciclos, dissimilar father (top-3 + torneio binário), critério coletivo, fallback SPEA2. **Uma discrepância corrigida:** linha 231 do pseudocódigo dizia "randomly selected mothers" mas a implementação (`IVF_V2.m:259`) seleciona as piores-fitness no conjunto de mães (`(N-NumMothersToMutate+1):N`). Corrigido para "the lowest-ranked mothers".
- **S33 concluído:** Seção 3.3 reescrita com diferenciação explícita de custo. Adicionado: (1) custo baseline do SPEA2 canônico por geração: $\mathcal{O}(N^2(M + \log N) + ND)$, detalhando dominância pairwise, k-NN e variação; (2) custo IVF por geração ativada: $\mathcal{O}(\ell N^2(M + \log N))$, mesma classe assintótica escalada pelo constante $\ell$; (3) argumento de amortização: trigger $FE_{\text{IVF}} \le r \cdot FE$ torna ativação progressivamente mais rara. Em-dash acidental corrigido para consistência com G1.
- Build limpo: 32 páginas (1 página adicionada pela expansão da complexidade), sem erros.

### Sessão 6 — 2026-03-01 (Passo 5: S41 + S42a + S42b + S43; adiantamento S45a do Passo 6)
- **S45a concluído (adiantado do Passo 6):** Parágrafo "Replication and run protocol" (Sec. 4.5) expandido com justificativa formal para $n=60$ runs, citando Eftimov & Korošec (GECCO 2025). Entrada `eftimov2025adaptive` adicionada ao `.bib`. Threats to Validity (Internal) atualizado com referência cruzada ao protocolo. Trabalho válido mas pertence ao Passo 6.
- **S41 concluído:** Parágrafo standalone sobre AGE-MOEA-II/AR-MOEA (Sec. 4.1) convertido em nota de rodapé no parágrafo de famílias de baseline.
- **S42a concluído:** Frase de fairness adicionada à Sec. 4.1: baselines usam defaults do PlatEMO para garantir comparação justa sob configurações recomendadas pelos autores originais, sem tuning adicional que pudesse favorecer ou desfavorecer métodos específicos.
- **S42b concluído (sem alteração):** Table 1 avaliada — já compacta (11 linhas, 3 blocos lógicos, `\scriptsize`). Reviewer #3 solicitou explicitamente parâmetros dos algoritmos. Decisão: manter como está.
- **S43 concluído:** Sec. 4.3 (Engineering Selection Protocol) reescrita de 3 parágrafos para 2. Removidos termos informais ("MAIN comparison", "Stage 1", "Stage 2", "inclusion rules"). Protocolo agora descrito como feasibility probe + screening phase em formato integrado. Preservados: critérios de inclusão, justificativa das 3 instâncias RWMOP, viés reduzido via RWMOP8, cobertura de ambos $M$.
- Build limpo: 31 páginas, sem warnings de referência/citação indefinida.

### Sessão 7 — 2026-03-01 (Passo 6: S45b + S45c + S45d; S45a já concluído na Sessão 6)
- **S45b concluído:** Três entradas canônicas adicionadas ao `.bib`: `wilcoxon1945` (Wilcoxon, 1945, *Biometrics Bulletin*), `holm1979simple` (Holm, 1979, *Scandinavian J. Statistics*), `derrac2011practical` (Derrac et al., 2011, *Swarm and Evolutionary Computation*). Citações inseridas: `\cite{wilcoxon1945}` após "Wilcoxon rank-sum test" no parágrafo Pairwise significance testing; `\cite{holm1979simple}` após "Holm--Bonferroni step-down procedure" no parágrafo Multiplicity correction.
- **S45c concluído:** `\cite{derrac2011practical}` inserido no parágrafo Rationale for pairwise testing, após "Friedman with post-hoc Nemenyi is often recommended to control global Type~I error". Derrac et al. (2011) é a referência padrão para frameworks de testes não-paramétricos em metaheurísticas.
- **S45d concluído:** Parágrafo "HV as secondary indicator" compactado. Removidas duas frases redundantes com o parágrafo "Primary endpoint" ("IGD remains the primary indicator by design..." e "HV is designated as a secondary confirmatory indicator"). Preservada informação nova: cobertura 100%, locais de reporte (appendix + claims summary), rationale para dual-indicator reporting (IGD vs HV podem divergir em fronts irregulares).
- Build limpo: 31 páginas, zero warnings.

### Sessão 8 — 2026-03-01 (Passo 7: S46a + S46b)
- **S46a concluído (sessão anterior):** Parágrafo "Separation of tuning and confirmatory evaluation" expandido com reconhecimento explícito de que os defaults dos baselines do PlatEMO também foram calibrados por seus respectivos autores em famílias de benchmark que se sobrepõem às usadas aqui; condição simétrica reconhecida. OOS (39 instâncias) reposicionado como "primary confirmatory evidence for generalization".
- **S46b concluído:** Heatmap combinado de sensibilidade (`sensitivity_multiclass_combined.pdf`) inserido como nova `figure*` entre os parágrafos Validation e Separation of tuning na Sec. 4.6. Caption descreve os 3 painéis (DTLZ2 $M=2$, WFG4 $M=2$, DTLZ7 $M=3$), grid $(r,c)$ sob AR puro, estrela no default v1, e conclusão de que a região de baixo-IGD é ampla. Duas referências textuais adicionadas: (1) no parágrafo Phase~A, após descrição do grid; (2) na Sec. 6.4 (Sensitivity and Tuning Implications), reforçando a evidência visual de robustez paramétrica. Caminho corrigido de `figures/` para `../figures/` (padrão do projeto). Figura renderizada na p.13 do PDF.
- Build limpo: 32 páginas (+1 pela nova figura), zero warnings.

### Sessão 8 (cont.) — 2026-03-01 (Passo 8: S51 + S52)
- **S51 concluído (sem alteração):** Table `claims_summary` avaliada — estrutura coerente com 3 camadas de evidência por indicador (unadjusted para sinal bruto, OOS para generalização, Holm para controle de multiplicidade). Cada linha serve propósito distinto e está claramente rotulada. Nenhuma alteração necessária.
- **S52 concluído:** Parágrafos da Sec. 5.2 (Detailed Results) reescritos para eliminar redundância com Sec. 5.1. Removidos: contagens agregadas de win/loss/tie já apresentadas na Sec. 5.1 (20/2/6, 18/1/4, OOS breakdowns). Substituídos por: decomposição per-suite (ZDT 5/5 wins, DTLZ 6/7, WFG losses concentradas em WFG2/WFG9, MaF ties/wins) e padrões qualitativos dos dados tabulados (EAR-P gains mais fortes em DTLZ M=3 7/0/0, MaF 5/1/0). Frase sobre "verified against raw pipeline outputs" removida (desnecessária para artigo). Informação sobre high-dispersion instances (DTLZ4, MaF5) preservada e integrada ao parágrafo M=3.
- Build limpo: 32 páginas, zero warnings.

### Sessão 8 (cont.) — 2026-03-01 (Passo 9: G6)
- **G6 concluído:** 8 ocorrências de "three-phase" reduzidas para 3. Mantidas nos 3 locais de definição: abstract (l.127), contributions list (l.144), e parágrafo canônico da Sec. 4.6 (l.369). Substituídas por "the tuning pipeline" em 5 locais: Sec. 3 (l.202), Sec. 4.2 (l.297), Threats to Validity (l.389), Discussion cross-cutting patterns (l.509), Conclusion (l.546).
- Build limpo: 32 páginas, zero warnings.
- **Todos os 9 passos da R2 estão concluídos.** Todos os 22 itens (7 globais + 15 por seção) estão com status Concluído.

### Sessão 9 — 2026-03-01 (Pós-plano: Holm OOS na claims_summary)
- **Holm OOS adicionado à Table claims_summary:** Identificada lacuna — tabela tinha 3 camadas de evidência (unadjusted, unadjusted OOS, Holm) mas faltava a 4ª camada mais conservadora: Holm corrigido filtrado para OOS. Metodologia: Holm-Bonferroni aplicado a TODAS as instâncias dentro de cada grupo $M$ (correção mais severa), depois filtrado para OOS. Números obtidos via `compute_claims_summary.py` atualizado (condição 4 + `label_map` corrigido): IGD 15/1/8 ($M=2$), 11/0/4 ($M=3$); HV 17/2/5 ($M=2$), 13/0/2 ($M=3$).
- **LaTeX atualizado:** (1) Duas novas linhas `(Holm, OOS)` inseridas na tabela (IGD e HV); (2) caption expandido com descrição da metodologia Holm→OOS; (3) Sec. 5.1 parágrafo primário expandido com frase sobre Holm OOS (15/1/8 e 11/0/4); (4) Conclusão — parágrafo quantitativo recebe frase sobre "most conservative evidence layer" com contagens Holm OOS e destaque de 0 losses em $M=3$; (5) parágrafo tuning arc atualizado com contagens Holm OOS ao lado das OOS unadjusted existentes.
- **Audit CSV atualizado:** `results/tables/claims_summary_audit.csv` agora tem 16 linhas (4 condições × 2 métricas × 2 M-values).
- Build limpo: 32 páginas, zero warnings.

### Sessão 10 — 2026-03-01 (Pós-plano: Substituição do heatmap de sensibilidade)
- **Figura substituída e expandida para 3 painéis:** `sensitivity_multiclass_combined.pdf` (heatmap de grid estendido 9R×10C, 3 problemas representativos, estrela no default v1) substituído por `tuning_heatmap_combined.pdf` com 3 painéis cobrindo todo o pipeline de tuning:
  - (a) Phase A broad search: heatmap 4×4 (r×c), Cycles=2, AR puro, estrela em A43 (r=0.20, c=0.16)
  - (b) Phase B operator comparison: bar chart horizontal com 5 perfis de operador, estrela em B02 (EAR-P light, rank=0.33)
  - (c) Phase C local refinement: heatmap 3×3 (r×c), EAR-P light, estrela em C26 (r=0.225, c=0.12)
  - Cor/barras = MeanCombinedRank sobre FULL12 (12 problemas, 30 runs). Colormap cividis_r compartilhado. Valores anotados.
- **Script `plot_tuning_heatmap.py` reescrito:** Adicionadas funções `plot_bar_panel` para Phase B e reestruturado layout para `gridspec(1,4)` com 3 painéis + colorbar.
- **Caption reescrita:** Descreve os 3 painéis, métrica (mean combined rank, lower=better=darker), grids, bar chart e configurações marcadas com estrela.
- **Referências textuais atualizadas:**
  - Sec. 4.6, Phase A: "extended grid for three representative instances" → "Fig. 7(a) displays the Phase A landscape for the Cycles=2 slice"
  - Sec. 4.6, Phase B: adicionado "As shown in Fig. 7(b)" antes da frase sobre o resultado
  - Sec. 4.6, Phase C: adicionado "Fig. 7(c) displays the corresponding EAR-P light slice"
  - Sec. 6.4: "sensitivity heatmaps" → "tuning landscape"; adicionada menção ao bar chart de Phase B e separação entre perfis
- **Verificação:** Nenhuma referência residual ao conteúdo antigo encontrada no manuscrito.
- Build limpo: 32 páginas, zero warnings. Figura renderizada na p.13.
- **Layout fix aplicado:** Três problemas visuais corrigidos no `plot_tuning_heatmap.py`:
  1. **Clipping lateral:** `figsize` ampliado de `(7.2, 2.9)` para `(8.2, 3.0)`; margens ajustadas (`left=0.06, right=0.96, bottom=0.20, top=0.88`).
  2. **Labels de Phase B invadindo Phase A:** `width_ratios` de Phase B aumentado de `0.85` para `1.05`; `wspace` aumentado de `0.42` para `0.50`.
  3. **Rótulos (a)/(b)/(c) dentro dos plots:** `ax.text()` com bbox semi-transparente substituído por `ax.set_title()` (rótulos agora acima dos painéis); `top` margin reduzido para `0.88` para acomodar títulos.
- Figura regenerada (PDF + PNG 600 dpi). Build limpo: 32 páginas, zero warnings.
- **Estrela deslocada para não cobrir valor numérico:** No heatmap, estrela movida para canto superior-direito da célula (offset +0.33 em x/y, tamanho 11pt); no bar chart, estrela movida para após o fim da barra (offset +0.04, clip_on=False).
- **Nomes de operadores corrigidos em todo o manuscrito e na figura:**
  - Nomes inventados ("EAR-P light/medium/strong", "EARN neogenesis") substituídos pelos nomes corretos da literatura IVF:
    - B01 = AR, B02 = **EAR-PA** (m=0.3, v=0.1), B03 = EAR-P (m=0.5, v=0.2), B04 = EAR-T (m=0.7, v=0.3), B05 = EAR-N (m=0.5, v=0.2, random re-init)
  - **20 ocorrências** de "EAR-P" no manuscrito referindo-se ao operador de C26/B02 corrigidas para "EAR-PA" (linhas 202, 205, 207, 210, 221, 231, 297, 321, 369, 373, 375, 382, 400, 431, 458, 519, 539×2, 548)
  - "EAR-P" mantido apenas na listagem da família (l.205) e na referência a B03 (l.373, 375)
  - Phase B (l.373): "(B01)~AR control; (B02)~EAR-P light; (B03)~EAR-P medium; (B04)~EAR-P strong; (B05)~EARN neogenesis" → "(B01)~AR; (B02)~EAR-PA; (B03)~EAR-P; (B04)~EAR-T; (B05)~EAR-N"
  - Phase C (l.375): "(AR, EAR-P light, EAR-P medium, EARN)" → "(AR, EAR-PA, EAR-P, EAR-N)"
  - `PHASE_B_LABELS` no script Python e título do painel (c) atualizados de forma consistente
  - Caption da figura e Sec. 6.4 atualizados
- Figura regenerada com nomes corretos. Build limpo: 32 páginas, zero warnings.
