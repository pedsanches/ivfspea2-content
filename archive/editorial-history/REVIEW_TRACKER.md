# Revisão do Paper — IVF/SPEA2

## Status Geral

| Fase | Seção | Status | Observações |
|------|-------|--------|-------------|
| 1 | Abstract | Revisada | Vagos nos números, falta tuning pipeline, closing fraco |
| 1 | Introduction (Sec. 1) | Revisada | Fluxo OK; hipótese hedged demais; motivação para SPEA2 fraca |
| 1 | Conclusion (Sec. 5) | Revisada | Repete números; insight principal enterrado; futuros genéricos |
| 2 | Method (Sec. 3) | Revisada | Ver diagnóstico abaixo |
| 2 | Experimental Setup (Sec. 4) | Revisada | Tuning fora de lugar; falta justif. baselines; HV incompleto |
| 2 | Results (Sec. 5) | Revisada | Claim principal comprimida; sem figuras; mistura c/ Discussion |
| 2 | Discussion (Sec. 6) | Revisada | 6.2 excelente; 6.1 repete; tuning fora de lugar; falta positioning |
| 3 | Related Work (Sec. 2) | Revisada | Citation dumping em 2.1; gap 2000-2024 em 2.2; tabela morta |
| 3 | Notação e consistência global | Revisada | Colisão $F$/$M$; terminologia inconsistente; ref cruzadas |
| 3 | Bibliografia | Revisada | 5 suites sem citar paper original; 13 entries órfãs; erros de tipo |

---

## Validação Sênior (A1) — calibragem de justiça

Critério adotado para este tracker:

- **Bloqueador**: reduz credibilidade metodológica/estatística ou pode gerar rejeição direta.
- **Importante**: melhora substancialmente a força do paper, mas não invalida sozinho.
- **Opcional**: polimento editorial; fazer apenas se não comprometer os bloqueadores.

### O que é realmente obrigatório antes da submissão

| Bloco | IDs | Necessidade A1 | Decisão prática |
|------|-----|----------------|-----------------|
| B1 — Integridade de citações e .bib | Bibliografia (linhas 160–182) | **Bloqueador** | Citar papers originais de ZDT/DTLZ/WFG/MaF e MFO-SPEA2 no texto; corrigir tipos/anos/keys do `.bib`; remover entradas órfãs ou reutilizá-las com função clara. |
| B2 — Coerência estrutural (setup vs discussão) | S9, D5, R2 | **Bloqueador** | Mover pipeline de tuning para Setup (nova subseção), deixar em Discussion apenas implicações; eliminar dependência circular Results→Discussion. |
| B3 — Protocolo estatístico explícito e completo | S5, S6, S4 | **Bloqueador** | Formalizar endpoint primário (IGD), multiplicidade (Holm), e política de efeito prático ($A_{12}$). Se ranking global (Friedman + pós-hoc) não for usado, justificar formalmente o porquê. |
| B4 — Evidência visual mínima | R4 | **Bloqueador** | Inserir figuras de suporte (mínimo: boxplots/convergência + exemplos de fronts) para sucessos e falhas. |
| B5 — Consistência formal da notação | N1, N2 (e item 6 da Method) | **Bloqueador** | Eliminar colisões de símbolos ($M$, $F$ etc.) em texto, equações e Algoritmo 1. |
| B6 — Alinhamento claim↔evidência no arco narrativo | A3, A5, I3, C2 | **Bloqueador** | Abrir Abstract/Intro com o mecanismo central (interação intensificação–densidade), incluir números-chave no abstract e retomar o mesmo insight na conclusão. |

### Importante (alto retorno, não bloqueia isoladamente)

| Bloco | IDs | Necessidade A1 | Decisão prática |
|------|-----|----------------|-----------------|
| I1 — Posicionamento frente aos baselines modernos | D6, D7, S1, RW4 | **Importante** | Explicitar quando escolher IVF/SPEA2 vs NSGA-III/AR-MOEA/AGE-MOEA-II; delimitar regime de uso. |
| I2 — Separação Results vs Discussion | R3, D1, D3 | **Importante** | Results: fatos e sinais; Discussion: mecanismo (sucesso e falha de forma simétrica). |
| I3 — Coesão de contribuições | I5, I6, C4 | **Importante** | Diferenciar claramente contribuição metodológica, validação empírica e pipeline de tuning. |
| I4 — Related Work com densidade argumentativa | RW1, RW2 | **Importante** | Menos listagem de citação, mais contraste de achados e lacunas. |

### Opcional (fazer só se houver folga)

| Bloco | IDs | Necessidade A1 | Decisão prática |
|------|-----|----------------|-----------------|
| O1 — Polimento de organização local | 1, 4, 5, 7 da Method; S8 | **Opcional** | Ajustes de legibilidade (implementation note, compactação de tabela, microfusão de subseções). |
| O2 — Realocação de "Threats to validity" | S7 | **Opcional** | Não é fatal ficar no Setup; mover apenas se melhorar fluidez do periódico-alvo. |
| O3 — Tabela de RW comentada | RW3 | **Opcional** | Ou ativar com propósito analítico claro, ou remover definitivamente para evitar "código morto". |

### Reclassificação de severidade (justa)

| ID | Severidade atual | Severidade calibrada | Justificativa |
|----|------------------|----------------------|---------------|
| I1 | Alta | Média | A frase "Despite its age" é defensável se vier acompanhada de evidência de adoção atual. |
| S4 | Alta | Média–Alta | HV incompleto não invalida o paper se IGD for endpoint primário pré-definido + limitação formal explícita. |
| S6 | Alta | Média–Alta | Friedman fortalece comparação multialgoritmo; pode ser substituído por justificativa metodológica explícita. |
| D4 | Média | Baixa–Média | A seção deixou de ser "3 linhas" após expansão do pipeline; ainda precisa síntese mais objetiva. |
| RW2 | Média | Baixa | O gap temporal já foi parcialmente mitigado com citações recentes; resta melhorar encadeamento crítico. |
| RW3 | Média | Baixa | Item editorial, não científico. |

### Novo risco identificado (não listado antes)

| ID novo | Risco | Severidade | Ação |
|--------|-------|-----------|------|
| X1 | Build com warnings persistentes de citações/referências indefinidas | Alta | Fechar build "limpo" (`latexmk`) antes da submissão; revista A1 tende a penalizar descuido formal. |

### Plano de execução (ordem refinada)

| Passo | Bloco | Esforço | Status |
|-------|-------|---------|--------|
| 1 | **B1 + B5 + X1** — Higiene científica | Baixo | Concluído |
| 2 | **B4** — Gerar figuras | Médio-Alto | Concluído (Fig. 2/3/4) |
| 3 | **B2 + I2** — Reorganização estrutural (tuning + fronteira Results↔Discussion) | Médio | Concluído (com polimento aplicado) |
| 4 | **B3** — Protocolo estatístico | Médio | Concluído |
| 5 | **B6 + I3** — Narrativa e coerência de contribuições | Médio | Concluído |
| 6 | **I1 + I4** — Positioning e Related Work | Médio | Concluído |

---

## Fase 1 — Esqueleto Argumentativo

### Abstract — REVISADA

Problemas identificados:

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| A1 | Frase de abertura genérica — não diferencia o paper | Média | Reescrever com hook específico |
| A2 | Falta justificativa para melhorar SPEA2 em 2026 | Alta | Adicionar argumento de relevância continuada |
| A3 | Resultados quantitativos vagos ("majority") | Alta | Incluir números: 23/28 bi-obj, 18/23 tri-obj |
| A4 | Closing fraco ("useful memetic enhancement") | Média | Fechar com o insight de geometria do front |
| A5 | Contribuição 3 (tuning pipeline) ausente | Média | Mencionar brevemente |

### Introduction (Sec. 1) — REVISADA

Problemas identificados:

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| I1 | "Despite its age" é contraproducente sem justificativa forte | Alta | Argumentar relevância concreta do SPEA2 (aplicações, propriedades de archiving) |
| I2 | §2 mistura bi-obj e many-obj sem scope boundary | Alta | Separar; reconhecer que experimentos vão só até M=3 |
| I3 | Design challenge (density penalizing IVF offspring) subdesenvolvido | Alta | Expandir o mecanismo — é a motivação central |
| I4 | Hipótese excessivamente hedged, quase se anula | Média | Reformular como falsificável: "melhora em fronts regulares, perde em irregulares" |
| I5 | Contribuição 2 não é diferenciadora ("systematic evaluation") | Baixa | Reformular enfatizando o que é único (51 instâncias, OOS separation) |
| I6 | Contribuição 3 comprime duas ideias em uma | Baixa | Separar tuning pipeline de separação tuning/confirmatory |

### Conclusion (Sec. 5) — REVISADA

Problemas identificados:

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| C1 | Primeiro parágrafo repete números do abstract/results | Média | Abrir com a síntese interpretativa (linha 517 atual) |
| C2 | Insight principal ("regular geometries → gains") está enterrado | Alta | Promover como abertura da conclusão |
| C3 | Trabalhos futuros genéricos | Média | Substituir por direções específicas (análise teórica da interação IVF-density, outros mecanismos de archiving, regime de transição) |
| C4 | Não retoma o gap/promessa da Intro | Média | Fechar o arco: a interação intensification-density foi compreendida? |

### Diagnóstico Cruzado Fase 1

| Elemento | Abstract | Intro | Conclusion | Alinhado? |
|----------|----------|-------|------------|-----------|
| Gap (density-induced stagnation) | Mencionado | Desenvolvido | Não retomado | Parcial |
| Hipótese (problem-dependent gains) | Implícita | Explícita | Implícita | Fraco |
| Contribuição 1 (hybridization) | Sim | Sim | Sim | OK |
| Contribuição 2 (experimental eval) | Parcial | Sim | Sim (números) | OK |
| Contribuição 3 (tuning pipeline) | Ausente | Sim | Mencionada | Falha |
| Resultados quantitativos | Vagos | N/A | Repetidos | Desbalanceado |
| Takeaway (geometria do front) | Ausente | Ausente | Presente | Invertido |

**Problema estrutural principal:** O insight mais valioso (relação geometria do front ↔ eficácia IVF) está forte na Conclusion mas fraco/ausente no Abstract e Intro. A "promessa" e a "entrega" estão desalinhadas — o revisor forma opinião na primeira página.

---

## Fase 2 — Núcleo Técnico

### Method (Sec. 3) — REVISADA

**Diagnóstico (sessão 1):**

Problemas identificados:

| # | Problema | Severidade | Ação | Implementado? |
|---|----------|-----------|------|---------------|
| 1 | Implementation note no corpo (nomes de classes/diretórios) | Média | Mover para footnote ou Code Availability | [ ] |
| 2 | Parâmetros default citados antes da seção de tuning | Média | Remover valores numéricos; referenciar Sec. 5.6 | [ ] |
| 3 | Contribuição comprimida em 3.4 — falta motivação | Alta | Expandir: *por que* dissimilar father? *Por que* collective criterion? | [ ] |
| 4 | Redundância entre 3.1 e Algorithm 1 | Média | Em 3.1, dar intuição alto nível; detalhes no pseudocódigo | [ ] |
| 5 | Subsection 3.2 vazia (3 linhas) | Baixa | Fundir com parágrafo introdutório ou com 3.1 | [ ] |
| 6 | Colisão notacional $M$ (objectives) vs $m$ (mothers) | Alta | Usar símbolo distinto (e.g., $\mu_m$) | [ ] |
| 7 | Equações de SPEA2 fitness em 3.4 pertencem a Preliminaries | Média | Mover para Sec. 2 ou criar Background | [ ] |
| 8 | Overhead empírico ausente em 3.3 | Baixa | Adicionar wall-clock ou declarar como limitação | [ ] |

**Veredito:** Funcional, mas abaixo do esperado para A1. Descreve *o quê* sem justificar *por quê*. Contribuição genuína subdesenvolvida em relação a detalhes operacionais padrão.

### Experimental Setup (Sec. 4) — REVISADA

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| S1 | Falta justificativa para escolha dos 8 baselines | Média | Explicar por que estes e não outros (RVEA, MOEA/D-AWA) |
| S2 | Descrição de benchmarks é lista sem justificativa de cobertura | Média | Ligar cada suite às claims do paper |
| S3 | Engineering Selection Protocol (4.3) quebra fluxo no Setup | Baixa | Mover para perto de 5.3 ou apêndice |
| S4 | HV incompleto tratado como nota, não como limitação formal | Alta | Resolver HV ou tratar como limitação explícita com análise de impacto |
| S5 | Effect size ($A_{12}$) mencionado mas não formalizado no protocolo | Média | Incluir em 4.5 ou remover menção |
| S6 | Falta teste de ranking global (Friedman) para 8 baselines | Alta | Adicionar ou justificar ausência |
| S7 | Threats to validity no Setup (incomum) | Baixa | Mover para após Results ou Discussion |
| S8 | Table 1 excessivamente longa — redundância em "None (PlatEMO default)" | Baixa | Compactar: uma nota geral + só parâmetros que diferem |
| S9 | **Tuning pipeline (6.4) deveria estar no Setup** — dependência circular | Alta | Mover Sec. 6.4 para Sec. 4.7 ou similar |

### Results (Sec. 5) — REVISADA

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| R1 | Claim principal (5.1) comprimida em 6 linhas — sem análise per-suite | Alta | Expandir com distribuição de W/L por suite |
| R2 | Referências a "pure AR operator" sem contexto (tuning ainda não apresentado) | Média | Depende de mover tuning para Setup (S9) |
| R3 | Interpretações mecanísticas nos Results (linhas 434, 437, 466) | Média | Mover para Discussion |
| R4 | Nenhuma figura (box plots, convergence, Pareto fronts) | Alta | Adicionar pelo menos box plots por suite e exemplos de fronts |
| R5 | Redundância entre Table 5 footnote e texto RWMOP8 | Baixa | Eliminar duplicação |
| R6 | Table 2 (claims_summary) é prática excelente | Positivo | Manter |

### Discussion (Sec. 6) — REVISADA

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| D1 | 6.1 repete contagens W/L/T que já estão em 5.1 e Table 2 | Média | Reescrever como síntese de padrões transversais |
| D2 | 6.2 (Mechanistic) é excelente — melhor seção do paper | Positivo | Manter e expandir |
| D3 | 6.2 analisa falhas mas não analisa sucessos simetricamente | Alta | Adicionar análise mecanística de *por que funciona* em fronts regulares |
| D4 | 6.3 (Sensitivity) rasa — 3 linhas, sem evidência de interação entre parâmetros | Média | Adicionar heatmap ou análise de sensibilidade marginal |
| D5 | 6.4 (Tuning Pipeline) é setup, não discussion | Alta | Mover para Sec. 4 (= S9) |
| D6 | Nenhuma discussão dos outros 6 baselines além de SPEA2 | Alta | Adicionar: quando escolher IVF/SPEA2 vs NSGA-III vs AR-MOEA? |
| D7 | Falta positioning statement | Alta | Adicionar parágrafo: "IVF/SPEA2 is best suited for..." |

---

## Fase 3 — Suporte

### Related Work (Sec. 2) — REVISADA

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| RW1 | 2.1 é citation dumping — 4 refs sem dizer o que encontraram | Alta | Desenvolver cada citação com 1 frase de evidência |
| RW2 | 2.2 tem gap de 20 anos (2000 → 2024) no landscape memético | Média | Incluir trabalhos representativos 2005-2020 |
| RW3 | Tabela comparativa comentada (\iffalse) — código morto | Média | Ativar e compactar, ou remover |
| RW4 | Falta cobertura de baselines modernos (AGE-MOEA-II, AR-MOEA) na RW | Média | Adicionar breve cobertura dos baselines que aparecem nas tabelas |
| RW5 | Key "reference2" é não-descritiva — visível ao revisor se gerar warnings | Baixa | Renomear para gadhvi2016suspension |
| RW6 | 2.3 (IVF) é a melhor subsection — gap emerge naturalmente | Positivo | Manter |

### Notação e Consistência Global — REVISADA

| # | Problema | Severidade | Ação |
|---|----------|-----------|------|
| N1 | Colisão $M$ (objectives) vs $m$/$M$ (mothers) — já flagrado em Sec. 3 | Alta | Usar símbolo distinto (e.g., $\mu_m$) globalmente |
| N2 | Colisão $F$: fitness $F(i)$ vs offspring count $F \gets 0$ no Algorithm 1 | Alta | Renomear offspring count (e.g., $n_{\text{off}}$ ou $F_{\text{gen}}$) |
| N3 | "execution rate" vs "activation rate" para o mesmo parâmetro $r$ | Média | Padronizar um termo em todo o paper |
| N4 | "instance" vs "problem" vs "benchmark configuration" intercambiáveis | Média | Definir e padronizar |
| N5 | "function evaluation budget" vs "evaluation budget" | Baixa | Padronizar |
| N6 | Referências cruzadas dependem de estrutura atual (se mover tuning, atualizar) | Baixa | Atualizar após reorganização |

### Bibliografia — REVISADA

**Citações ausentes (GRAVE):**

| Benchmark/Conceito | Paper original no .bib | Citado? |
|---------------------|----------------------|---------|
| ZDT suite | zitzler2000comparison | NÃO |
| DTLZ suite | deb2005scalable | NÃO |
| WFG suite | huband2006review | NÃO |
| MaF suite | cheng2017benchmark | NÃO |
| MFO-SPEA2 (baseline) | jiao2023multiform | NÃO |
| Das-Dennis (Table 1) | das1998normal | NÃO |

**Entradas órfãs (13 keys nunca citadas):** citacaon1, citacaon3, citacaon4, citacaon6, MOPSO, PESA, deb2012analyzing, zitzler1998evolutionary, Chen2021, talbi2009metaheuristics + as 5 acima que deveriam ser citadas

**Erros no .bib:**

| Key | Erro |
|-----|------|
| ishibuchi1998multi | year=2002, key diz 1998 |
| li2014shift | year=2013, key diz 2014 |
| zitzler2004performance | @inproceedings com campo journal |
| ishibuchi2008evolutionary | @article com campo booktitle |
| reference2 | Key não-descritiva |

---

## Perguntas-guia para cada seção

1. **O que um revisor hostil perguntaria?**
2. **O que pode ser cortado sem perda?**
3. **Cada parágrafo tem uma função clara?**

---

## Log de Sessões

### Sessão 1 — 2026-03-01
- Revisada: Seção 3 (Method)
- Definida ordem de revisão (3 fases, 10 etapas)
- Criado este documento de acompanhamento
- Revisada: Fase 1 completa (Abstract, Introduction, Conclusion)
- Identificado problema estrutural principal: insight de geometria ausente no abstract/intro
- Diagnóstico cruzado revela desalinhamento entre promessa e entrega
- Revisada: Fase 2 completa (Setup, Results, Discussion)
- Problemas estruturais graves: tuning fora de lugar (S9/D5), sem figuras (R4), Discussion ignora 6 baselines (D6)
- Ponto forte: Sec. 6.2 (mechanistic interpretation) e Table 2 (claims summary)
- Revisada: Fase 3 completa (Related Work, Notação, Bibliografia)
- Problema grave: 5 benchmark suites + 1 baseline sem citar papers originais
- 13 entradas órfãs no .bib; colisão de $F$ no Algorithm 1; citation dumping em 2.1

### Sessão 2 — 2026-03-01 (validação sênior)
- Reclassificação de severidades para evitar overengineering e viés de rigor excessivo
- Definidos 6 bloqueadores reais para prontidão A1 (B1..B6)
- Adicionado risco novo X1: build LaTeX deve fechar sem warnings críticos
- Definido plano mínimo de execução em 4 passos (higiene científica → estrutura/inferência → narrativa/evidência → posicionamento)

### Sessão 3 — 2026-03-01 (execução do B4)
- Geradas e integradas as figuras de distribuição (boxplots IGD, M2/M3)
- Gerados heatmaps de efeito prático ($A_{12}$) contra os 8 baselines (M2/M3)
- Implementado pipeline de extração de fronts via MATLAB (`experiments/extract_fronts_for_paper.m`) com caminhos robustos por raiz do projeto
- Gerada e integrada a figura de fronts representativos (DTLZ2 M2, WFG2 M3, RWMOP9 M2)

### Sessão 3 — 2026-03-01 (execução Passo 1 + fechamento Fase 1)
- Concluído B1: citações de ZDT/DTLZ/WFG/MaF/MFO-SPEA2/Das-Dennis adicionadas; .bib limpo (10 órfãs removidas, 2 entry types corrigidos, key reference2→gadhvi2016suspension)
- Concluído B5: $F \gets 0$ → $n_{\text{ivf}} \gets 0$ no Algorithm 1 e Sec. 3.2; resíduo $N-F$ corrigido na linha 247
- Concluído X1: build sem warnings de citação/referência
- Fechamento Fase 1: A3 (números no abstract), A5 (tuning pipeline no abstract), I2 (scope M=2,3), I4 (hipótese falsificável), C2 (conclusão abre com insight de geometria)

### Sessão 4 — 2026-03-01 (execução Passo 3: B2+I2)
- Concluído B2: "Parameter Tuning Pipeline" movida de Discussion (antiga 6.4) para Setup (nova 4.6, antes de Threats to validity). Label `subsec:sensitivity` preservada; todas as 5 referências cruzadas existentes continuam resolvendo.
- Concluído I2 (Discussion 6.1): "Observed Performance Patterns" reescrita como "Cross-Cutting Performance Patterns" — sem repetição de contagens W/L/T; foco em 3 padrões transversais (correlação front-geometria↔ganho, assimetria M=2>M=3, generalização OOS).
- Concluído I2 (Discussion 6.3): "Sensitivity Implications" reescrita como "Sensitivity and Tuning Implications" — foco nas implicações práticas (ortogonalidade EAR-P vs. ativação, ponto operacional robusto, quando re-tuning é justificável).
- Concluído I2 (Results): forward reference mecanística na linha 441 suavizada para observação factual ("indicates coexisting successful and failed convergence regimes") com referência para Discussion preservada.
- Build limpo: sem warnings de referência indefinida ou citação.

### Sessão 5 — 2026-03-01 (polimento cirúrgico Results↔Discussion)
- Aplicado polimento fino em 4 trechos de Results para remover causalidade mecanística residual e manter Results predominantemente descritiva.
- Trechos ajustados: WFG em M=2, comparação M=3 vs AR controle, leitura dos heatmaps $A_{12}$ e discordância IGD--HV em RWMOP9.
- Referências para interpretação mecanística foram explicitamente mantidas/encaminhadas para Sec. 6.2.

### Sessão 6 — 2026-03-01 (execução Passo 4: B3 — Protocolo estatístico)
- Concluído S5: $A_{12}$ (Vargha--Delaney) formalizado no protocolo com definição, limiares interpretativos (0.56/0.64/0.71), e papel complementar aos testes de significância. Citação original adicionada ao .bib (`vargha2000critique`).
- Concluído S6: Justificativa formal para uso de pairwise Wilcoxon + Holm--Bonferroni em vez de omnibus Friedman. Argumento: a pergunta científica primária é IVF/SPEA2 vs. seu próprio host (SPEA2), não ranking global; os 7 baselines restantes são comparadores contextuais, não co-hipóteses num ranking único.
- Concluído S4: HV formalizado como indicador secundário no protocolo estatístico, com descrição explícita da cobertura parcial e da limitação de que conclusões baseadas em IGD podem não generalizar para rankings HV. Parágrafo redundante removido de Performance Metric; referência cruzada para o protocolo adicionada.
- Construct validity (Threats) atualizado para referenciar o protocolo e mencionar $A_{12}$ explicitamente.
- Build limpo: sem warnings de referência/citação.

### Sessão 7 — 2026-03-01 (execução Passo 5: B6 + I3)
- Diagnóstico B6+I3: havia três lacunas residuais de narrativa (abertura do abstract ainda genérica para o mecanismo central, contribuições com diferenciação insuficiente entre método/evidência/protocolo, e fechamento de conclusão sem arco tuning→confirmação plenamente explícito).
- Abstract ajustado para foreground do problema central (intensificação IVF vs truncação por densidade SPEA2) já na frase de abertura.
- Lista de contribuições na Intro reescrita com diferenciação explícita entre: método (acoplamento host-specific), evidência (escopo empírico + 8 baselines) e protocolo (separação tuning-informed vs OOS confirmatório).
- Conclusão fortalecida com fechamento do arco de tuning (promoção em FULL12 + confirmação OOS 39 instâncias) e agenda futura mais específica (HV completo com filtragem harmonizada, modelagem formal da interação intensificação-densidade, variantes com outros mecanismos de archive/seleção).
- Build recompilado com sucesso após os ajustes; sem warnings de referência/citação indefinida.

### Sessão 8 — 2026-03-01 (execução Passo 6: I1 + I4)
- Related Work fortalecida com subsection específica de baselines modernos (NSGA-III, AR-MOEA, AGE-MOEA-II), explicitando princípio de diversidade de cada família e o gap exato em relação ao acoplamento memético host-specific.
- Setup atualizado com justificativa explícita de seleção dos 8 baselines por famílias metodológicas (SPEA2-host, Pareto/decomposição, adaptação geométrica/referência), reduzindo risco de crítica de escolha ad hoc.
- Discussion ampliada com positioning statement operacional (quando escolher IVF/SPEA2 vs AGE-MOEA-II/AR-MOEA/NSGA-III) baseado em regime de problema, objetivo de decisão (convergência IGD vs spread HV) e padrão geométrico do front.
- Bibliografia expandida com citações primárias de AR-MOEA e AGE-MOEA-II (`tian2018armoea`, `panichella2022agemoeaii`) e integração no texto.
- Build recompilado com sucesso após integração; sem warnings de referência/citação indefinida.

### Sessão 9 — 2026-03-01 (polimento final de submissão)
- Table 1 compactada para reduzir altura sem perda de conteúdo científico: removidas redundâncias de parâmetros default e reorganização por blocos (protocolo compartilhado, baselines, IVF/SPEA2).
- Figuras de heatmap redimensionadas para eliminar overflow de float mantendo legibilidade.
- Backmatter reorganizado (`\section*` + `description`) para estabilizar bookmarks e remover warnings de nível do `hyperref`.
- Pacote `mathrsfs` removido por não uso no manuscrito, eliminando warnings de substituição de fonte.
- Build final: sem warnings críticos (`undefined refs/citations`, `Float too large`, `hyperref level difference`); permanecem apenas `Underfull` de composição tipográfica (não bloqueadores). PDF final em 27 páginas.

### Sessão 10 — 2026-03-01 (submission-readiness audit)
- Auditoria formal de prontidão concluída: protocolo estatístico, evidência visual, narrativa e posicionamento estão coerentes com objetivo A1.
- Consistência terminológica refinada em parâmetros de IVF (`execution rate` padronizado, removendo variação residual com `activation rate`).
- Métricas editoriais verificadas: abstract com ~225 palavras; build sem referências/citações indefinidas e sem warnings críticos de float/hyperref.
- Bloqueadores administrativos remanescentes para submissão real: metadados de autoria/afiliação/e-mails ainda em placeholder e seção de contribuições/autorização precisa refletir os autores reais.
- Risco operacional remanescente: manuscrito usa `\input{...}` para tabelas externas; antes do upload final, validar política da revista/sistema (ou consolidar em arquivo único, se exigido).

### Sessão 11 — 2026-03-01 (fortalecimento Passo 5: B6+I3 + justificativa n=60)
- Auditoria narrativa formal do arco Abstract→Intro→Conclusion: todas as 11 claims do abstract rastreadas até evidência factual em Results/Discussion/Conclusion, sem inconsistências numéricas. Partição OOS (51-12=39) e somas W/L/T verificadas.
- Lacuna científica identificada: n=60 runs não tinha justificativa formal no texto. Corrigida com parágrafo expandido em "Replication and run protocol" (Sec. 4.5): justificativa cita exceder convenção de 30 runs, adequação para Wilcoxon rank-sum, e referência a Eftimov & Korošec (GECCO'25) sobre estimativa adaptativa de run count (82–95% accuracy com ~50% menos runs), com ressalva explícita de que o trabalho citado é single-objective.
- Threats to Validity (Internal) atualizada com referência cruzada para o protocolo estatístico onde a justificativa reside.
- Bibliografia expandida com `eftimov2025adaptive` (GECCO'25).
- Build recompilado com sucesso; sem warnings de referência/citação indefinida. PDF em 31 páginas.
