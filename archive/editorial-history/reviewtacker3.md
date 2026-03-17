# reviewtacker3 - Revisao R3.1 (integridade + escopo)

## Contexto

Este documento e uma versao revisada do planejamento R3, com foco em:

1. corrigir referencias internas desatualizadas (secoes/figuras);
2. ajustar escopo para o estado real do repositorio;
3. reduzir risco metodologico (especialmente na suite de engenharia).

Base comparativa mantida:

- Cao et al. (2024), *Advances in Engineering Software*
- Yang et al. (2024), *Swarm and Evolutionary Computation*

Principio mantido: enriquecer evidencia visual e analitica sem alterar claims centrais.

---

## Ajustes de integridade aplicados

1. **V1 nao e lacuna total**: ja existe figura de fronts representativos em `paper/figures/pareto_fronts.pdf` e pipeline em `src/python/analysis/generate_paper_figures.py`.
2. **Secao de engenharia**: no manuscrito atual, engenharia esta em `paper/src/sn-article.tex` na subsecao iniciada em `:537` (nao em "Sec. 5.3" antiga).
3. **Ablacao H1xH2**: efeitos e interacoes ja foram calculados em `results/ablation_v2/phase2/phase2_summary.json` (interacao H1xH2 = +1.042), com figuras prontas no mesmo diretorio.
4. **RWMOP8 exige cautela**: cobertura de runs validos e heterogenea (ex.: MOEAD 0/60; SPEA2+SDE 18/60) em `results/engineering_suite/engineering_suite_summary_main.csv`.
5. **V4 (GD/Spread) precisa reescopo**: no consolidado, IGD/HV tem cobertura completa, mas Spread/IGDp/Spacing tem cobertura parcial e concentrada em subconjuntos.

---

## Status geral revisado

| ID | Item | Prioridade | Esforco | Status | Nota de integridade |
|----|------|------------|---------|--------|---------------------|
| V5 | Plot de interacao H1xH2 (ablation) | Alta | Baixo | Em progresso | Integrado no texto; figura referenciada |
| V3 | Ranking medio (Friedman-style) | Alta | Baixo | Em progresso | Figura e estatisticas geradas |
| V2 | Engenharia expandida (RWMOP) | Alta | Medio | Em progresso | Figura de perfil IGD/HV com `n` valido integrada |
| V1 | Fronts side-by-side por algoritmo | Media-Alta | Medio | Em progresso | Painel de engenharia expandido com RWMOP8 |
| V6 | Visual mecanistico DTLZ4 bimodal | Media | Baixo | Em progresso | Criterio objetivo + RunIDs integrados no texto |
| V4 | Indicador adicional (GD/Spread) | Media | Medio-Alto | Pendente (reescopo) | Pairwise IVF/SPEA2 sem cobertura valida no consolidado atual |
| V7 | Boxplot isolado de estabilidade IVF | Baixa | Baixo | Opcional | Melhor em suplemento |

---

## Detalhamento revisado por item

### V1 - Fronts side-by-side por algoritmo (expansao)

**Estado atual:** parcialmente coberto (figura existente com DTLZ2, WFG2, RWMOP9).

**Ajuste:** reposicionar como *expansao* da figura atual, nao como item inexistente.

**Entrega recomendada:**

- manter os 3 casos representativos (sucesso, falha, engenharia);
- incluir mais algoritmos nos paineis sinteticos (hoje o script enfatiza IVF nos sinteticos);
- manter criterio de run mediana IGD por algoritmo para consistencia metodologica.

**Arquivos relevantes:**

- `paper/figures/pareto_fronts.pdf`
- `src/python/analysis/generate_paper_figures.py`

---

### V2 - Engenharia expandida (RWMOP)

**Racional:** alto impacto para leitores aplicados.

**Escopo recomendado:**

1. pequeno contexto fisico de cada problema reportado;
2. fronts comparativos para pelo menos RWMOP9 e RWMOP8;
3. barras de IGD/HV com mediana + dispersao, sempre com anotacao de `n` valido.

**Regra de integridade obrigatoria:**

- em RWMOP8, explicitar cobertura desigual (MOEAD sem runs validos; SPEA2+SDE com baixa cobertura) para evitar inferencia injusta.

**Arquivos relevantes:**

- `results/engineering_suite/engineering_suite_summary_main.csv`
- `results/engineering_suite/engineering_suite_raw_main.csv`

---

### V3 - Ranking medio (Friedman-style)

**Racional:** quick win de leitura global.

**Regra de uso:** visual de navegacao, nao claim primario (claim primario continua pairwise IVF vs SPEA2).

**Entrega recomendada:**

- 2 paineis: M2 e M3 separados (evita mascara de comportamento);
- opcional terceiro painel agregado (M2+M3) apenas como apoio;
- barras ordenadas (menor rank = melhor) com valores numericos.

**Fonte de dados sugerida:**

- `results/tables/igd_per_instance_M2.csv`
- `results/tables/igd_per_instance_M3.csv`

---

### V4 - Indicador adicional (GD/Spread) (reescopo)

**Risco identificado:** cobertura atual de metricas adicionais e incompleta para parte dos cenarios/algoritmos.

**Recomendacao de escopo:**

- **Plano A (baixo risco):** usar diagnostico apenas IVF/SPEA2 vs SPEA2 nas instancias com cobertura valida, como analise suplementar;
- **Plano B (alto custo):** recomputar metricas desde os `.mat` para cobertura total e comparavel.

**Decisao sugerida:** manter V4 fora do caminho critico do corpo principal; entrar como suplemento se houver tempo.

---

### V5 - Plot de interacao H1xH2 (ablation)

**Estado atual:** dados ja prontos e consistentes com narrativa do manuscrito.

**Entrega recomendada (imediata):**

- inserir interaction plot 2x2 (H1 off/on x H2 off/on) com eixo de rank medio;
- destacar que H1 e H2 isolados sao fracos/negativos e a combinacao e sinergica;
- citar valor observado de interacao H1xH2 (+1.042).

**Arquivos relevantes:**

- `results/ablation_v2/phase2/phase2_summary.json`
- `results/ablation_v2/phase2/phase2_interactions.pdf`
- `results/ablation_v2/phase2/phase2_factor_effects.pdf`

---

### V6 - Visual mecanistico DTLZ4 (bimodalidade)

**Racional:** fortalece secao mecanistica com evidencia visual do regime bom vs ruim.

**Regra metodologica para evitar cherry-picking:**

- definir a priori:
  - good run: IGD <= Q1;
  - bad run: IGD >= Q3 e IGD > 0.1;
- reportar os RunIDs selecionados no caption/appendix.

**Formato:** parallel coordinates (ou scatter 3D, se mais legivel para M=3).

---

### V7 - Boxplots de estabilidade isolada do IVF/SPEA2

**Racional:** util para robustez, mas redundante com parte da evidencia atual.

**Decisao:** manter como suplemento (baixa prioridade para corpo principal).

---

## Plano de execucao revisado (ordem recomendada)

1. **V5** - integrar interacao H1xH2 (quick win com evidencia pronta)
2. **V3** - ranking medio M2/M3 (quick win visual)
3. **V2** - reforco de engenharia com regra de cobertura valida
4. **V1** - expandir fronts side-by-side existentes
5. **V6** - visual mecanistico DTLZ4 com criterio objetivo
6. **V4** - apenas se viavel sem comprometer cronograma
7. **V7** - suplemento

---

## Criterios de aceite (checklist curto)

- [ ] Nenhuma nova figura contradiz claims primarios (pairwise IVF vs SPEA2).
- [ ] Itens de engenharia exibem `n` valido quando houver cobertura desigual.
- [ ] Ranking medio e apresentado como apoio exploratorio.
- [ ] Qualquer analise V4 informa explicitamente limitacoes de cobertura.
- [ ] DTLZ4 good/bad run segue criterio predefinido, com RunIDs reportados.

---

## Log

### Sessao de revisao R3.1

- Documento revisado para integridade metodologica e alinhamento com o estado atual do repositorio.
- Priorizacao recalibrada para impacto/risco.
- Nome do arquivo definido conforme solicitado: `reviewtacker3.md`.

### Sessao de progresso R3.1

- V5 iniciado: figura de interacao H1xH2 adicionada ao manuscrito com referencia explicita ao efeito +1.04.
- V3 implementado em modo exploratorio: figura M2/M3, tabelas de rank medio e estatisticas Friedman/Kendall geradas.
- Integracao no manuscrito concluida com ressalva metodologica de que ranking nao substitui claim pairwise.
- V2 iniciado: figura de perfis de engenharia (IGD/HV) com mediana+IQR e anotacao de `n` valido por algoritmo/problema adicionada ao manuscrito.
- Contexto fisico curto dos tres RWMOPs adicionado na subsecao de engenharia (truss, crash energy, side impact).
- V1 iniciado: extracao de fronts medianos para RWMOP8 (alem de RWMOP9) e nova figura side-by-side de engenharia integrada ao manuscrito.
- Proximo passo sugerido: avaliar se vale ampliar os paineis sinteticos com mais algoritmos (DTLZ2/WFG2), mantendo legibilidade e criterio de run mediana.

### Sessao de progresso R3.1 (continuidade)

- V1 avancou: paineis sinteticos de fronts (DTLZ2/WFG2) expandidos para quatro algoritmos (IVF/SPEA2, SPEA2, NSGA-III, MOEA/D), mantendo criterio de run mediana por IGD.
- V6 avancou: criterio predefinido formalizado no pipeline (`good: IGD <= Q1`; `bad: IGD >= Q3 e IGD > 0.1`) com persistencia de metadados de selecao (RunID/IGD).
- V6 integrado ao manuscrito: figura DTLZ4 good vs bad adicionada com referencia explicita a Q1/Q3, RunIDs selecionados e proporcao de runs nos dois regimes.
- Figura `pareto_fronts.pdf` regenerada com os paineis sinteticos expandidos e legenda/caption alinhadas no manuscrito.
- V4 (Plano A) executado em modo diagnostico: tabelas suplementares geradas para Spread/IGDp/Spacing, confirmando ausencia de cobertura pareada valida para inferencia IVF/SPEA2 vs SPEA2 no coorte sintetico atual.
