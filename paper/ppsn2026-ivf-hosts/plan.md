## 1. Triagem por natureza

| ID | Item do parecer v2 | Parte executável | Tipo | Observação |
|---|---|---|---|---|
| MV1 | Reposicionar a contribuição como comparação entre pipelines e ampliar o related work | Reenquadramento pipeline-level no abstract, introdução, discussão e conclusões | T | Não exige nova análise |
| MV1 | Reposicionar a contribuição como comparação entre pipelines e ampliar o related work | Inserir âncoras bibliográficas concretas e ajustar `references.bib` | T | Exige novas entradas BibTeX, mas não nova análise |
| MV2 | Declarar FE accounting e demonstrar comparabilidade real de budget | Explicar no texto que as três variantes debitam FEs do IVF do orçamento do host | T | Já há evidência no código MATLAB |
| MV2 | Declarar FE accounting e demonstrar comparabilidade real de budget | Auditar empiricamente `FE`, `fe_max`, checkpoints e drift entre pipelines | A | Usa código existente + `.mat`/traces já disponíveis |
| MV3 | Esclarecer proveniência dos hiperparâmetros e separar seed-paired de order-aligned | Explicitar no texto a origem dos parâmetros e o risco de tuning leakage | T | Depende de confirmar se houve ou não retuning |
| MV3 | Esclarecer proveniência dos hiperparâmetros e separar seed-paired de order-aligned | Reanalisar endpoint separando blocos strict seed-paired e order-aligned | A | Usa `hosts_paper.csv` |
| MV4 | Especificar estrutura de correção múltipla e documentar métricas/artefatos | Declarar famílias de hipóteses do BH, racional FDR vs FWER, HV/IGD, normalização, versão, seeds, hardware, artifact | T | Boa parte pode ser reaproveitada do outro manuscrito |
| MV4 | Especificar estrutura de correção múltipla e documentar métricas/artefatos | Harmonizar ECDF com correção BH e regenerar saídas | A | O script atual de ECDF está sem `p_adj` |
| MV5 | Fortalecer Results com geometria, variabilidade e distribuição | Qualificar o bloco dinâmico de 6 instâncias como diagnóstico/case-study | T | Sem nova análise |
| MV5 | Fortalecer Results com geometria, variabilidade e distribuição | Rotular as 51 instâncias por geometria e reanalisar endpoint por estrato | A | Usa dados existentes + metadata manual |
| MV5 | Fortalecer Results com geometria, variabilidade e distribuição | Promover uma tabela compacta de medianas/IQR ao corpo principal | A | A-light: seleção determinística a partir das tabelas já geradas |
| MV5 | Fortalecer Results com geometria, variabilidade e distribuição | Sumarização dinâmica alternativa sobre toda a suíte | A | Viável se os `.mat` 3001/4001/5001 preservarem trilhas temporais; se preservarem só endpoint, vira E |
| EXT1 | Ablação cruzada com núcleo IVF compartilhado entre hosts | Implementar/transplantar núcleo comum e rerodar | E | Não cabe como revisão rápida para o mesmo PPSN |
| EXT2 | Estender para many-objective `M>=4` | Novos runs em novos `M` | E | Mesmo host, nova campanha experimental |
| EXT2 | Estender para hosts adicionais como MOEA/D | Implementar IVF/MOEA-D e avaliar | E | Novo acoplamento + nova campanha |
| EXT3 | Testar além da família IVF | Implementar outras famílias de intensificação/local search/mating-guided | E | Muda o escopo do artigo |
| EXT4 | Tornar a interpretação geométrica confirmatória | Formalizar geometria e analisar toda a suíte sintética atual | A | Isto pode ser absorvido já no mínimo viável |
| EXT4 | Tornar a interpretação geométrica confirmatória | Validar em problemas reais/aplicações adicionais | E | Melhor para periódico |

## 2. Rascunhos textuais prontos

### Abstract
**Destino:** `main.tex`, linhas `35–38`  
**Ação:** substituir o abstract inteiro

```latex
\begin{abstract}
We study whether the benefit of in vitro fertilization (IVF) intensification depends on the MOEA host when IVF is instantiated through canonical host-specific variants from prior literature. Using PlatEMO, we compare three published pipelines---IVF/SPEA2, IVF/NSGA-II, and IVF/NSGA-III---on 51 synthetic benchmark instances with 30 runs per configuration, evaluating final IGD and HV with nonparametric tests, Benjamini--Hochberg correction, and Vargha--Delaney $A_{12}$. IVF/SPEA2 records +33/=15/-3 IGD outcomes, IVF/NSGA-III records +22/=29/-0, and IVF/NSGA-II records only +1/=48/-2; the same ordering appears in HV and remains consistent across $M=2$ and $M=3$ and across DTLZ, MaF, WFG, and ZDT. Dynamic analyses on a protocol-defined six-instance subset reproduce the same ordering at the trajectory level: IVF/SPEA2 shows the strongest and most stable early convergence signal, IVF/NSGA-III remains context-sensitive and weakens at $M=3$, and IVF/NSGA-II is nearly inert. In the absolute cross-host ranking among IVF variants, IVF/SPEA2 attains the best mean rank in both metrics and the most HV bests, while IVF/NSGA-III remains a strong second host and IVF/NSGA-II is rarely first. Taken together, these results support a pipeline-level compatibility interpretation: among the host-specific IVF realizations studied here, IVF/SPEA2 couples most effectively to its host, IVF/NSGA-III is conditionally beneficial, and IVF/NSGA-II is largely neutral.
\keywords{Multi-objective evolutionary algorithms \and Intensification \and IVF operator \and SPEA2 \and NSGA-II \and NSGA-III}
\end{abstract}
```

- Endereça: inflação retórica do claim central; mantém contribuição forte em nível de pipeline.

### Introduction
**Destino:** `main.tex`, linhas `46–59`  
**Ação:** substituir o bloco entre a apresentação da família IVF e o `\paragraph{Scope of inference.}`

```latex
The IVF family provides a natural case study for this question. IVF was first proposed as a multi-objective hybrid inspired by in vitro fertilization~\cite{camilo-junior2011} and later adapted as an operator for NSGA-II~\cite{sampaio2017ivf}, extended toward many-objective settings~\cite{sampaio2019ivf}, specialized for NSGA-III~\cite{Sampaio2024}, and recently redesigned for SPEA2~\cite{zambrano2026ivfspea2}. Across these variants, the common IVF core is stable: select a subset of promising individuals, pair them, generate intensified offspring through a short internal reproduction cycle, and transfer those offspring back to the host population. What changes across hosts is the realization of that core, including how mothers and fathers are chosen, how continuation is decided, and how the IVF budget is integrated with the host generation.

The broader hybrid and memetic MOEA literature already suggests that intensification should be judged by how it couples to the host search process rather than by intensification strength alone. Classical memetic MOEAs such as M-PAES~\cite{knowles2000memetic}, component-wise MOEA design studies~\cite{bezerra2016automatic}, and hybrid-metaheuristic taxonomies and surveys~\cite{talbi2002taxonomy,blum2011hybrid} all point to the same design question: which host properties make a given intensification module useful? More recent mating-policy work reinforces this view by showing that structured pairing strategies can materially change multi-objective search behaviour~\cite{Lu2025}.

This paper addresses that gap through a controlled comparison across three hosts: SPEA2~\cite{zitzler2001spea2}, NSGA-II~\cite{deb2002nsga2}, and NSGA-III~\cite{deb2014nsga3}. The three algorithms differ precisely in the kind of signal they provide during survival and diversity maintenance. SPEA2 combines strength and density, NSGA-II relies on non-dominated sorting plus crowding distance, and NSGA-III organizes selection around reference-point niches.

\paragraph{Research question.}
Does the benefit of IVF depend on the structure of the host selection mechanism?

\paragraph{Hypothesis H.}
Across host-specific IVF realizations reported in prior work, stronger IVF gains are expected in MOEAs whose selection mechanisms provide more explicit directional feedback in objective space about under-explored regions. Hosts with predominantly isotropic crowding feedback are expected to show weaker synergy.

\paragraph{Scope of inference.}
The unit of comparison in this paper is the \emph{host + host-specific IVF realization} pipeline. This is a valid contribution in its own right: the paper compares three canonical couplings from the literature under a unified benchmark and analysis protocol. Our conclusions are therefore about comparative compatibility patterns across published pipelines, not about isolating a pure host-mechanism effect under a single identical IVF implementation transplanted unchanged across hosts.
```

- Endereça: pipeline-level framing; lacuna bibliográfica concreta; preserva a lógica central comum do IVF.

**Nota operacional:** este bloco exige adicionar entradas BibTeX para `knowles2000memetic`, `talbi2002taxonomy`, `blum2011hybrid` e `Lu2025`.

### Experimental Setup
**Destino:** `main.tex`, linhas `124–134`  
**Ação:** substituir o bloco inteiro da seção experimental por uma versão mais precisa

```latex
All experiments were conducted in MATLAB~\texttt{[release]} using PlatEMO version~\texttt{[PlatEMO version]}. We considered 51 synthetic benchmark instances: 28 bi-objective instances from ZDT~\cite{zitzler2000zdt}, DTLZ~\cite{deb2005dtlz}, WFG~\cite{huband2006wfg}, and MaF~\cite{cheng2017maf}; and 23 tri-objective instances from DTLZ, WFG, and MaF. This yields 28 instances with $M=2$ and 23 instances with $M=3$. Each configuration was executed for 30 runs with population size $N=100$ and stopping criterion $\mathrm{maxFE}=100{,}000$.

\paragraph{Budget accounting.}
The comparison is evaluation-normalized rather than runtime-normalized. In all three host-specific IVF realizations, evaluations spent inside IVF are debited against the host descendants of the same generation: the IVF phase is capped at at most $N$ internal evaluations in an activated generation, and the remaining host variation budget is reduced to $N-\mathrm{FE}_{\mathrm{IVF,gen}}$. Consequently, the nominal generation budget remains fixed at $N$, although wall-clock overhead still differs across hosts because the IVF realizations use different internal selection, continuation, and offspring-generation routines. For trajectory plots, small checkpoint drifts are handled by interpolation on a common FE grid when exact checkpoint alignment is unavailable.

\paragraph{Metrics and references.}
Final IGD~\cite{zitzler1999igd} and HV~\cite{zitzler2003hv} were used as endpoint metrics. For the synthetic benchmarks, both were taken from PlatEMO's built-in metric outputs. Each problem instance constructs a problem-specific reference set through \texttt{Problem.GetOptimum(10000)} before optimization. IGD is then computed as the mean distance from this 10{,}000-point reference-front sample to the final nondominated approximation, whereas HV uses the same problem-specific optimum set to determine the normalization bounds in PlatEMO's standard HV implementation, after which the reference point is the all-ones vector in normalized objective space. The runs were executed on \texttt{[CPU / RAM / OS]}, and the processed CSV files, raw metric traces, and analysis scripts used to generate the reported tables and figures are archived at \url{[artifact URL or DOI]}.

\paragraph{Pairing and endpoint inference.}
The three host comparisons do not share the same pairing status. IVF/NSGA-II versus NSGA-II and IVF/NSGA-III versus NSGA-III use strict run-ID pairing because each IVF track shares the same run range as its baseline track (4001--4030 and 5001--5030, respectively). IVF/SPEA2 versus SPEA2 does not share absolute run IDs (3001--3030 versus 1--30); for this block we therefore report the deterministic matched-order analysis used in the original version together with an unpaired robustness analysis in the supplementary artifact. Endpoint comparisons use the Wilcoxon signed-rank test on strictly paired blocks and an unpaired robustness analysis on the order-aligned block; Vargha--Delaney $A_{12}$ is reported throughout as effect size.

\paragraph{Multiplicity control.}
We use Benjamini--Hochberg false-discovery-rate control rather than a family-wise procedure such as Bonferroni--Holm because the goal is to characterize broad comparative patterns across many benchmark instances without the severe power loss that arises under dozens of simultaneous tests. For endpoint analyses, BH is applied separately within each \emph{(host comparison, metric)} family across the 51 instance-level hypotheses. For dynamic per-run trajectory summaries, BH is applied separately within each summary metric across the 18 host-instance hypotheses in the dynamic block. For ECDF differences, BH is applied across the 18 host-instance Kolmogorov--Smirnov tests in the ECDF block.

\paragraph{Parameter provenance.}
No additional instance-wise retuning was performed for this host-comparison study. Each pipeline used the fixed parameter setting of its cited canonical implementation throughout the 51-instance evaluation: IVF/SPEA2 v2 used $C=0.12$, $R=0.225$, $M_{\mathrm{mut}}=0.3$, $V=0.1$, and \textit{Cycles}=2; IVF/NSGA-II used $R=0.5$, $C=0.07$, and \textit{Cycles}=5; and IVF/NSGA-III used \textit{ivf\_rate}=0.10, $C=0.10$, and \textit{Cycles}=5.

\paragraph{Dynamic block.}
To complement the 51-instance endpoint analysis with trajectory-level evidence, we also analyze a smaller dynamic block defined by a deterministic six-instance protocol: DTLZ5 ($M=2$), MaF1 ($M=2$), WFG8 ($M=2$), ZDT4 ($M=2$), DTLZ5 ($M=3$), and WFG2 ($M=2$). These configurations were rerun with 100 saved checkpoints. The dynamic block is intended as mechanism-oriented diagnostic evidence rather than as a second confirmatory benchmark of the same scope as the 51-instance endpoint analysis.
```

- Endereça: FE accounting; BH desambiguado; HV/IGD/normalização; seeds/versão/hardware; tuning provenance; pairing status.

**Nota operacional:**  
Se o estudo `hosts` realmente usou a mesma snapshot congelada do companion paper, preencher `\texttt{[PlatEMO version]}` com `24.2.0.2923080`.  
Se houve qualquer retuning neste estudo, substituir o parágrafo `Parameter provenance` pela descrição exata do protocolo e da separação tuning/teste.  
Se o artifact do PPSN precisar ficar cego, usar `\url{[anonymous artifact URL]}` no corpo e migrar DOI/Zenodo para a versão camera-ready.

### Results
**Destino 1:** `main.tex`, linhas `160–161`  
**Ação:** inserir após o parágrafo que termina em `Table~\ref{tab:a12_summary} confirms the same pattern through oriented effect sizes.`

```latex
To complement wins/ties/losses and oriented effect sizes with a direct view of dispersion, Table~\ref{tab:rep_endpoint_medians} reports median/IQR endpoint values for a deterministic representative set of gain, tie, and adverse cases across the three hosts. The full per-instance median/IQR tables remain in the archived supplementary artifact.
```

- Endereça: promoção de medianas/IQR ao corpo principal.

**Destino 2:** `main.tex`, linhas `176–179`  
**Ação:** substituir a abertura da subseção dinâmica

```latex
\subsection{Dynamic Evidence}
\label{sec:results_dynamic}

To complement the 51-instance endpoint analysis with temporal evidence, we use a smaller dynamic block as diagnostic support about search trajectory rather than as a second confirmatory benchmark of equal scope. The six instances were selected by a deterministic protocol for mechanism-oriented visualization, so the curves and ECDFs below should be interpreted as case studies that help explain the endpoint pattern, not as an independent sample of the full suite.
```

- Endereça: rebaixar corretamente a análise dinâmica atual para papel diagnóstico.

### Discussion
**Destino:** `main.tex`, linhas `207–214`  
**Ação:** substituir o corpo atual da discussão

```latex
Figures~\ref{fig:a12_strip}--\ref{fig:ecdf} support Hypothesis~H at the pipeline level studied here, but they do not by themselves demonstrate that directional feedback is the sole causal mechanism. The common IVF core is shared across hosts, yet the published host-specific realizations also differ in father selection, reproduction, continuation, and activation policy. The present evidence therefore supports a comparative reading: among the canonical pipelines considered here, IVF/SPEA2 couples most effectively to its host, IVF/NSGA-III remains conditionally beneficial, and IVF/NSGA-II is largely neutral.

A plausible interpretation is that hosts offering more explicit directional information in objective space make it easier for the IVF core to convert local intensification into offspring that survive environmental selection. This interpretation is consistent with the observed ranking, but it should still be read as a mechanistic account supported by the current evidence rather than as a mechanism already isolated experimentally. Its most useful implication is predictive: if the interpretation is correct, the strength of IVF should vary not only with the host but also with Pareto-front geometry. Regular convex, concave, or weakly degenerate fronts should offer more stable opportunities for useful directional reinforcement, whereas disconnected or strongly irregular fronts should weaken or destabilize the gain.

Three threats to validity remain material. First, the comparison is evaluation-normalized only if the documented FE accounting is accepted; wall-clock overhead still differs across hosts. Second, the inference is strongest for strict run-ID pairing and weaker for the order-aligned IVF/SPEA2 versus SPEA2 block, which is why the robustness analysis should be reported separately. Third, any parameter adjustment performed on the reported benchmark suite would blur the distinction between host compatibility and problem-specific calibration. These limitations do not erase the pipeline-level result, but they do bound the strength of the causal interpretation that can be attached to it.
```

- Endereça: `directional feedback` como interpretação plausível; ameaças à validade explícitas; previsão por geometria.

### Conclusions
**Destino:** `main.tex`, linhas `219–221`  
**Ação:** substituir o parágrafo conclusivo atual

```latex
This paper compared three canonical IVF pipelines rather than a single identical IVF implementation transplanted across hosts. Under that scope, the evidence is consistent and practically useful: IVF/SPEA2 shows the strongest and most stable gains, IVF/NSGA-III is a conditional second host, and IVF/NSGA-II is largely neutral. The results therefore support the conclusion that published IVF couplings are not interchangeable across hosts.

A broader claim about operator-host compatibility as a mechanism remains plausible but provisional. It is supported by the observed pipeline ordering, by the dynamic case studies, and by the geometry-dependent patterns, but it is not yet isolated from differences among the host-specific IVF realizations themselves. Future work should therefore separate mechanism from implementation more cleanly through cross-host transplant experiments, broader geometry-stratified analyses, and higher-dimensional benchmarks.
```

- Endereça: centralizar o enquadramento pipeline-level sem “diminuir” a contribuição.

### Supplementary Material
**Destino:** `main.tex`, linha `237`  
**Ação:** substituir a frase atual sobre supplementary material

```latex
The full per-instance median/IQR tables for all 51 instances (IGD and HV, by host and $M$), the complete endpoint robustness analyses, the geometry labels and geometry-stratified summaries, the FE-accounting audit, the full paired dynamic-test tables, and the dynamic-selection diagnostics are archived in an auditable artifact at \url{[artifact URL or DOI]}. The main text reports only compact summaries; all machine-readable CSV files and figure-generation scripts required to reproduce those summaries are included in the same artifact.
```

- Endereça: acesso permanente auditável ao suplemento.

## 3. Especificações de análises adicionais

- **A1. FE accounting audit.** Input: `IVFSPEA2V2.m`, `IVF_V2.m`, `IVFNSGAII.m`, `IVF_NSGAII.m`, `IVFNSGAIII.m`, `IVF_NSGAIII.m`; se disponível, `hosts_convergence.csv` e/ou extração de `FE` dos `.mat`. Método: auditoria estática do código para provar que `IVF_Gen_FE` é debitado do orçamento do host em todas as três variantes; auditoria empírica com `fe_max`, número de checkpoints, overshoot e drift por algoritmo/instância/run. Output: `results/tables/hosts_fe_audit.csv` + `hosts_fe_audit.tex` no suplemento; uma frase quantitativa no `Experimental Setup`. Conexão: responde à crítica central sobre comparabilidade causal em FEs, não só reprodutibilidade.

- **A2. Seed-paired vs order-aligned robustness.** Input: `data/processed/hosts_paper.csv` com colunas `algo, problem, M, run, IGD, HV`; mapa de tracks. Método: para `IVFNSGAII vs NSGAII` e `IVFNSGAIII vs NSGAIII`, usar Wilcoxon pareado por `run`; para `IVFSPEA2 vs SPEA2`, usar como análise principal um teste não pareado por instância e métrica (`Mann-Whitney` + `A12`, ou teste permutacional sobre diferença de medianas) e manter o Wilcoxon order-aligned como robustez/sensibilidade. Aplicar BH nas mesmas famílias declaradas no texto. Output: `results/tables/hosts_pairing_robustness.csv` + tabela curta no suplemento com W/T/L por host e métrica sob análise principal e sensibilidade; uma frase-resumo no corpo. Conexão: corrige a fragilidade do pareamento artificial.

- **A3. Harmonização de multiplicidade no ECDF.** Input: `results/tables/ecdf_significance.csv` atual ou reexecução a partir de `data/processed/hosts_convergence.csv`. Método: aplicar BH aos 18 testes KS do bloco ECDF e adicionar coluna `p_adj`; opcionalmente reportar também `significant_bh`. Output: atualizar `ecdf_significance.csv` e a anotação/caption da figura ECDF. Conexão: resolve a ambiguidade de “BH” e elimina a inconsistência atual entre endpoint/dinâmica.

- **A4. Auditoria de proveniência dos hiperparâmetros.** Input: defaults nas classes MATLAB, papers fonte, experiment runners e documentação local. Método: construir uma tabela de proveniência com colunas `pipeline`, `parameters`, `source_type` (`published default`, `in-house tuned`, `retained from prior paper`), `tuning_split` e `notes`. Output: `results/tables/hosts_parameter_provenance.tex` no suplemento; uma sentença fechando o risco de leakage no `Experimental Setup`. Conexão: transforma a crítica de tuning leakage em item auditável.

- **A5. Rotulagem por geometria e análise estratificada.** Input: `hosts_paper.csv`; novo arquivo manual `config/hosts_front_geometry.csv` com colunas mínimas `problem, M, geometry_primary, geometry_secondary, source_note`. Método: rotular as 51 instâncias por geometria primária; recomputar ou juntar `A12_ivf`, sinal e W/T/L por `host × metric × geometry`; testar interação com um modelo por permutação do tipo `A12_ivf ~ host * geometry + M`, separado para IGD e HV; como sensibilidade, colapsar geometrias esparsas em `regular` vs `disconnected/irregular`. Output: uma figura ou tabela principal `hosts_geometry_summary` entre `Per-Host Compatibility` e `Dimensional Asymmetry`; `results/tables/hosts_geometry_interaction.csv` no suplemento. Conexão: torna a narrativa de `directional feedback` previsiva por geometria, não apenas plausível.

- **A6. Tabela compacta de medianas/IQR no corpo.** Input: `results/tables/hosts_ivfspea2_*_stats.csv`, `hosts_ivfnsgaii_*_stats.csv`, `hosts_ivfnsgaiii_*_stats.csv`. Método: seleção determinística de três casos por host para IGD: maior ganho, caso mais neutro e pior caso; se o host não tiver perda, usar o menor `A12_ivf` disponível. Gerar uma única tabela compacta com 9 linhas, contendo medianas e IQR de IVF e base. Output: `results/tables/hosts_rep_endpoint_igd.tex` para o corpo principal; manter as tabelas completas no artefato. Conexão: adiciona distribuição sem estourar página.

- **A7. Sumarização dinâmica alternativa para toda a suíte.** Input: raw `.mat` dos cohorts padrão (`IVFSPEA2 3001–3030`, `SPEA2 1–30`, `IVFNSGAII/NSGAII 4001–4030`, `IVFNSGAIII/NSGAIII 5001–5030`); é preciso primeiro verificar se esses `.mat` preservam vetores `metric.IGD/HV` e checkpoints `result`, e não apenas o último valor. Método: se a verificação for positiva, generalizar `build_hosts_convergence_csv.py` para extrair `FE, IGD, HV` de todas as 51 instâncias; definir por instância um `IGD_best_final` e `HV_best_final`; construir gaps normalizados `g_IGD(t)` e `g_HV(t)` por run; calcular, ao longo de `FE/maxFE`, a fração de runs ou instâncias que atinge `g \le \tau` para limiares fixos (`\tau \in \{0.5, 0.25, 0.1\}`), com IC bootstrap. Resumir diferenças IVF-base por host usando AUC da curva de fração-resolvida por instância. Output: uma nova figura agregada para o corpo principal, idealmente substituindo a ECDF atual, e uma tabela suplementar de diferenças por host, `M` e geometria. Conexão: remove a dependência interpretativa do subconjunto de 6 instâncias. Se a verificação inicial mostrar que os cohorts padrão guardam só endpoint, esta análise reclassifica para E.

## 4. Itens E — avaliar viabilidade

| Item experimental | Viável no mesmo PPSN? | Recomendação |
|---|---|---|
| Ablação cruzada com núcleo IVF compartilhado entre hosts | Não | Mover para versão estendida |
| Extensão para `M>=4` nos três hosts atuais | Não | Mover para versão estendida |
| Novo host com IVF, p.ex. MOEA/D | Não | Mover para versão estendida |
| Outras famílias de intensificação/local search | Não | Mover para versão estendida |
| Validação adicional em aplicações reais | Não | Mover para versão estendida |

**Parágrafo curto para shared-core ablation.**
A clean cross-host transplant of a shared IVF core would be the definitive causal follow-up to this paper, because it would hold the intensification mechanics fixed while varying only the host environment. We do not present that experiment here because it requires new host-specific engineering and a fresh benchmark campaign under tightly matched budgets. The present manuscript should therefore be read as a comparison among canonical published pipelines, with mechanism-isolation reserved for a subsequent extended version.

**Parágrafo curto para `M>=4` e MOEA/D.**
The current evidence intentionally targets moderate objective counts ($M=2$ and $M=3$), where all three canonical host-specific IVF pipelines are already available and directly comparable. Extending the study to many-objective settings and to decomposition-based hosts such as MOEA/D would strengthen external validity, but it requires new runs and, in the MOEA/D case, a new IVF coupling. We therefore position that extension as follow-up work rather than as a page-limited PPSN revision.

**Parágrafo curto para outras famílias de intensificação.**
Testing whether the same compatibility pattern survives beyond the IVF family is scientifically attractive, but it changes the scope from a focused pipeline-comparison paper to a broader component-benchmarking study. Given the PPSN page limit, the revision should keep the contribution centred on IVF and treat cross-family transfer as a natural next step for an extended journal article.

**Parágrafo curto para aplicações reais.**
Additional real-world validation would improve external validity, but it belongs to a broader version with space for domain formulation, problem-specific metric handling, and application-level interpretation. In the PPSN paper, the stronger move is to delimit scope explicitly and to present real-world transfer as the next validation stage rather than to dilute the current contribution.

## 5. Restrição de página LNCS

- **Texto novo que deve substituir, não somar.** O novo enquadramento da introdução deve substituir as linhas `46–59`, não ser adicionado acima delas. O novo `Experimental Setup` substitui `124–134`. A nova `Discussion` substitui `207–214`. As novas `Conclusions` substituem `219–221`.
- **Onde cortar sem perder núcleo científico.** O `Background` atual (`64–79`) pode ser comprimido em aproximadamente metade, porque a Tabela~1 já carrega as diferenças operacionais entre as variantes. O parágrafo `Table~\ref{tab:adaptations} shows...` (`119`) pode virar uma única frase. A repetição de contagens de wins/ties/losses no texto de `Results` pode ser encurtada quando a tabela representativa e o resumo geométrico entrarem.
- **Mover para suplemento, não para o corpo.** As tabelas completas por instância já estão prontas e devem continuar fora do corpo principal. O `appendix` atual (`227–237`) deve sair do PDF principal do PPSN e virar material suplementar/artifact; caso contrário, ele compete diretamente com páginas do corpo.
- **Trade-off principal se entrar uma nova figura dinâmica agregada.** Se a sumarização dinâmica sobre as 51 instâncias entrar no corpo, mova a ECDF de seis instâncias para o suplemento primeiro. Se ainda faltar espaço, mova também a Fig.~3 (`m2_vs_m3`) para o suplemento e mantenha no corpo apenas a evidência geométrica estratificada e a figura dinâmica agregada.
- **Trade-off principal se entrar uma nova tabela de medianas/IQR.** A tabela precisa ser compacta, uma só, com cerca de 9 linhas. Não promova tabelas completas `M=2/M=3` por host ao corpo principal.
- **Risco de estouro.** O plano cabe em 16 páginas LNCS se: a) o apêndice sair do PDF principal; b) entrar no máximo uma nova tabela curta e uma nova figura principal; c) o bloco `Background` for comprimido. Sem esses cortes, o plano tende a estourar.

## 6. Sequência executável

1. **Fechar enquadramento e fatos-base.** Pré-requisitos: decidir o claim pipeline-level, confirmar se houve ou não retuning, confirmar `PlatEMO version`, MATLAB release, hardware e artifact URL. Entregável: mini-brief editorial com esses fatos congelados + rascunhos aprovados de abstract/intro/conclusions. Feito quando o manuscrito deixa de prometer isolamento causal do host.
2. **Documentar o protocolo experimental.** Pré-requisitos: acesso às classes MATLAB e aos scripts Python atuais. Entregável: texto final de `Experimental Setup` com FE accounting, famílias BH, HV/IGD, seeds, versão, hardware e proveniência dos parâmetros. Feito quando cada detalhe metodológico criticado no parecer aponta para uma fonte verificável no repositório.
3. **Rodar as análises de robustez de endpoint.** Pré-requisitos: `hosts_paper.csv` e scripts de tabela atuais. Entregável: `hosts_pairing_robustness.*`, `hosts_fe_audit.*`, `hosts_parameter_provenance.*`, `ecdf_significance` com `p_adj`. Feito quando há um bloco seed-paired limpo, um bloco order-aligned tratado separadamente e uma política BH coerente em todos os outputs.
4. **Construir a camada geométrica.** Pré-requisitos: arquivo manual `hosts_front_geometry.csv` preenchido para as 51 instâncias. Entregável: tabela/figura `hosts_geometry_summary` + CSV de teste de interação. Feito quando toda instância tem rótulo e existe pelo menos um resultado principal que diferencia host por geometria.
5. **Produzir a tabela compacta de medianas/IQR.** Pré-requisitos: stats CSVs de endpoint prontos. Entregável: `hosts_rep_endpoint_igd.tex` + sentença de amarração em `Results`. Feito quando o corpo principal mostra distribuição sem depender só de W/T/L e `A12`.
6. **Executar a verificação-gate da dinâmica all-suite.** Pré-requisitos: acesso aos `.mat` dos cohorts padrão. Entregável: decisão binária “traces completos existem / não existem”. Feito quando não houver mais incerteza se a alternativa dinâmica é A ou E.
7. **Se o gate for positivo, gerar a dinâmica agregada; se for negativo, manter o bloco atual e só rebaixar sua força inferencial.** Pré-requisitos: passo 6. Entregável: ou uma nova figura dinâmica agregada para o corpo + tabela suplementar, ou uma versão textual que assume explicitamente o papel diagnóstico das 6 instâncias. Feito quando a narrativa dinâmica deixa de depender implicitamente de uma seleção ad hoc.
8. **Reescrever `Results`.** Pré-requisitos: passos 3–7 concluídos. Entregável: `Results` com nova hierarquia interpretativa, referência à tabela compacta, referência ao estrato geométrico e bloco dinâmico compatível com o que foi efetivamente obtido. Feito quando o texto não promete mais do que as novas análises entregam.
9. **Reescrever `Discussion` e `Conclusions`.** Pré-requisitos: `Results` final. Entregável: seções finais com `directional feedback` tratado como interpretação plausível, não mecanismo provado. Feito quando o fechamento está integralmente consistente com o escopo pipeline-level.
10. **Passagem final de budget LNCS.** Pré-requisitos: manuscrito completo. Entregável: lista de cortes finais, apêndice removido do PDF principal, artefato suplementar fechado. Feito quando o PDF principal fica dentro do limite e todos os detalhes volumosos migram para o suplemento.

## 7. Autocrítica antes de entregar

- **Cobertura do mínimo viável.** Todos os 5 itens do `Mínimo viável` viraram ações concretas: enquadramento pipeline-level, FE accounting, tuning/proveniência + pairing robustness, BH/HV/IGD/reprodutibilidade, geometria/variabilidade/dinâmica.
- **Tom e terminologia.** Os rascunhos preservam a nomenclatura do manuscrito: `IVF/SPEA2`, `IVF/NSGA-II`, `IVF/NSGA-III`, `IGD`, `HV`, `directional feedback`, `pipeline`, `host-specific realization`.
- **Assunções de dados.** Nenhuma análise proposta depende de novos experimentos, exceto a dinâmica all-suite se os `.mat` padrão não preservarem trilhas temporais; por isso o plano inclui um gate explícito que reclassifica esse item para E se necessário.
- **Dependências.** Não há circularidade: o enquadramento vem antes da documentação experimental; a documentação vem antes das reanálises; as reanálises vêm antes da reescrita de `Results`; `Discussion` e `Conclusions` ficam por último.
- **Limite LNCS.** O plano só cabe de forma realista se o apêndice sair do PDF principal e se houver disciplina de substituição, não acumulação. O maior risco de estouro é tentar manter todas as figuras atuais e ainda adicionar uma nova figura dinâmica agregada e uma nova tabela no corpo.