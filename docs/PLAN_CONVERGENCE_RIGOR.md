# Plano: Reforço Metodológico da Análise de Convergência

> Objetivo: elevar Fig 4 (trajetória temporal) e Fig 5 (ECDF) ao padrão
> "suficiente para artigo forte", endereçando todas as lacunas críticas.

---

## Diagnóstico do Estado Atual

| Componente | Status | Observação |
|---|---|---|
| Dados IGD por FE | ✅ Pronto | `data/processed/hosts_convergence.csv` (6 algos × 6 instâncias × 30 runs × 100 checkpoints) |
| Dados HV por FE | ⚠️ Parcial | MATLAB salva `metric.HV` mas `build_hosts_convergence_csv.py` só extrai IGD |
| Seleção de instâncias | ⚠️ Frágil | `select_convergence_instances.py` usa A12 mas sem protocolo estatístico formal |
| Fig 4 (razão IGD) | ⚠️ Limitada | Suavização ad hoc (window=5), descarta 1° checkpoint, sem IC |
| Fig 5 (ECDF) | ⚠️ Limitada | Sem bandas de incerteza, sem teste de diferença entre métodos |
| Testes inferenciais | ❌ Ausente | Nenhum teste estatístico por host nem correção múltipla |
| Métricas resumidas | ⚠️ Parcial | `explore_convergence_visuals.py` tem AUC mas não por-run com IC |

---

## Requisitos a Satisfazer

### R1 — Protocolo de seleção de instâncias
**Problema:** 6 instâncias em `hosts_convergence_instances.csv` foram escolhidas
por critérios heurísticos ("representativas") sem protocolo estatístico.

**Solução proposta (duas opções):**

| Opção | Descrição | Esforço |
|---|---|---|
| **R1-A: Sumário completo** | Gerar Fig 4/5 para **todas as 51 instâncias** em painel resumido (median + IC por grupo: DTLZ, ZDT, WFG, MaF). As 6 instâncias ficam como "casos de estudo" em apêndice. | Médio |
| **R1-B: Pré-registro formal** | Documentar o critério de seleção atual como protocolo: as 6 instâncias são selecionadas por (a) maior efeito A12 orientado dentro do grupo, (b) sem sobreposição de (problem, M). Adicionar teste de sensibilidade: repetir análise com as 6 "segunda melhor escolha" e comparar结论. | Baixo |

**Recomendação:** R1-B primeiro (mais rápido), com compromisso de R1-A se reviewers pedirem.

**Artefatos:**
- `docs/CONVERGENCE_SELECTION_PROTOCOL.md` — protocolo documentado
- `src/python/analysis/select_convergence_sensitivity.py` — seleção alternativa (2ª escolha por grupo) + comparação

---

### R2 — HV dinâmico
**Problema:** só IGD ao longo do tempo. Artigos fortes exigem convergência consistente em múltiplos indicadores.

**Solução:**
1. Modificar `build_hosts_convergence_csv.py` para extrair **também HV** dos `.mat` files (coluna adicional `metric` → `HV`).
2. Gerar figura análoga à Fig 4 com **razão HV_IVF / HV_base** (agora > 1 = IVF melhor, invertido do IGD).
3. ECDF Fig 5 com eixo duplo ou painel separado para HV.

**Artefatos:**
- `build_hosts_convergence_csv.py` — adicionar extração de HV
- `plot_hosts_convergence_hv.py` — Fig 4 HV (estrutura idêntica à Fig 4 IGD)
- Output: `data/processed/hosts_convergence_hv.csv` (ou coluna extra no CSV atual)

**Nota:** O MATLAB já salva HV (`'metName', {'IGD', 'HV'}` no `run_hosts_convergence.m`). Só precisa extrair.

---

### R3 — Métricas resumidas por run + IC 95% bootstrap
**Problema:** sem métrica consolidada por run para teste inferencial.

**Solução:** Para cada `(algo, problema, M, run)` computar:

| Métrica | Fórmula | Interpretação |
|---|---|---|
| **AUC_IGD** | ∫ IGD(FE) dFE (trapz) | Desempenho acumulado |
| **AUC_ratio** | AUC_base / AUC_IVF | Efeito agregado (>1 = IVF melhor) |
| **Time-to-target** | FE* tal que IGD(FE*) ≤ τ | Velocidade de convergência |
| **Final_IGD** | IGD no último FE | Qualidade final |

**Targets τ:** usar os mesmos 10 multiplicadores da ECDF (100× até 1.0× do melhor IGD).

**Bootstrap:** Para cada métrica por host, gerar IC 95% com 10.000 reamostragens (com reposição) dos 30 runs.

**Artefatos:**
- `src/python/analysis/compute_convergence_summaries.py` — calcula AUC, time-to-target, final IGD/HV
- `src/python/analysis/bootstrap_ci.py` — módulo utilitário para IC bootstrap
- Output: `results/tables/convergence_summaries.csv` (métricas por run)
- Output: `results/tables/convergence_summaries_bootstrap_ci.csv` (median + IC 95%)

---

### R4 — Testes inferenciais IVF vs base + correção BH
**Problema:** nenhuma comparação formal entre IVF e base por host.

**Solução:** Para cada instância (problema, M) e cada par (IVF, base):

1. **Teste pareado**: Wilcoxon signed-rank nas métricas resumidas (AUC_ratio, time-to-target, final_IGD) dos 30 runs pareados.
2. **Efeito**: Cliff's delta ou Vargha-Delaney A12 (já usado no projeto).
3. **Correção múltipla**: Benjamini-Hochberg (FDR) sobre todos os testes por métrica.

**Artefatos:**
- `src/python/analysis/test_convergence_significance.py` — Wilcoxon pareado + A12 + BH
- Output: `results/tables/convergence_significance.csv` (p-value, p_adj, efeito por host)

**Pseudocódigo:**
```python
for each (problem, M):
    for each pair (ivf_algo, base_algo):
        # AUC ratio
        ivf_aucs = summaries[ivf_algo][problem][M]['AUC_IGD']
        base_aucs = summaries[base_algo][problem][M]['AUC_IGD']
        ratio = ivf_aucs / base_aucs  # ou comparar direto
        p = wilcoxon(ivf_aucs, base_aucs)  # pareado
        a12 = vargha_delaney(ivf_aucs, base_aucs)
        # ... acumular para BH
p_adj = multipletests(p_raw, method='fdr_bh')
```

---

### R5 — ECDF com bandas de incerteza + teste de diferença
**Problema:** Fig 5 atual é pontual, sem incerteza nem teste.

**Solução:**

**5a. Bandas de incerteza por bootstrap:**
- Para cada algoritmo, bootstrap dos 30 runs (com reposição) → recalcular ECDF 1000×.
- Banda = percentil 2.5–97.5 em cada ponto da grade FE.
- Plotar como faixa semi-transparente ao redor da curva.

**5b. Teste de diferença global:**
- **Teste de Permutação Pareado**: para cada par (IVF, base), contar quantos
  (target, run) são resolvidos mais cedo pelo IVF. Estatístico = diferença média
  de "tempo de resolução". p-value via permutação (10.000).
- Alternativa mais simples: teste de Kolmogorov-Smirnov 2 amostras nas
  distribuições de time-to-target agregadas (menos poderoso, mas padrão).

**Artefatos:**
- Modificar `plot_hosts_convergence.py` → função `fig5_ecdf` para adicionar bandas
- `src/python/analysis/test_ecdf_difference.py` — teste de permutação ou KS
- Output: `results/tables/ecdf_significance.csv`

---

### R6 — Análise de sensibilidade
**Problema:** suavização e descarte de checkpoints podem mascarar efeitos.

**Solução — 3 análises:**

| Variante | O que muda | O que comparar |
|---|---|---|
| **Sem suavização** | Remover rolling median(window=5) | Mediana e IQR mudam? Conclusão muda? |
| **Com 1° checkpoint** | Incluir primeiro FE (~1000) | Transiente é informativo ou ruído? |
| **Merge por FE** | Quantificar linhas perdidas no merge `(run, FE)` entre IVF e base | % de dados perdidos por algoritmo |

**Artefatos:**
- `src/python/analysis/sensitivity_smoothing.py` — Fig 4 com/sem suavização + 1° checkpoint
- `src/python/analysis/diagnose_merge.py` — relatório de perdas no merge
- Output: `results/tables/merge_diagnostic.csv`
- Output: `results/figures/sensitivity_smoothing.pdf`

---

## Ordem de Execução Sugerida

```
Fase 1 (dados — baixa fricção)
  ├── T1: Extrair HV dos .mat files existentes        [R2]
  └── T2: Diagnóstico de merge                        [R6]

Fase 2 (métricas resumidas — base para testes)
  ├── T3: Calcular AUC, time-to-target, final IGD/HV  [R3]
  └── T4: Bootstrap IC 95%                            [R3]

Fase 3 (inferência — rigor estatístico)
  ├── T5: Wilcoxon pareado + A12 + BH                 [R4]
  └── T6: Teste de diferença ECDF                     [R5b]

Fase 4 (visualizações — figuras finais)
  ├── T7: Fig 4 IGD com bandas IC (bootstrap)         [R5a]
  ├── T8: Fig 4 HV (nova figura)                      [R2]
  ├── T9: Fig 5 ECDF com bandas + teste               [R5]
  └── T10: Figuras de sensibilidade                   [R6]

Fase 5 (documentação — blindagem)
  ├── T11: Protocolo de seleção documentado            [R1-B]
  └── T12: Seleção alternativa (2ª escolha)            [R1-B]
```

---

## Checklist de Validação Final

- [x] HV dinâmico disponível e consistente com IGD (mesma direção de efeito)? → **SIM** — 108.000 valores HV extraídos. Fig 4 HV gerada (`hosts_v2_fig4_hv_ratio.pdf`)
- [x] IC 95% reportado para todas as métricas resumidas? → **SIM** — `convergence_summaries_bootstrap_ci.csv` (576 rows)
- [x] p-values ajustados (BH) para todos os testes por host? → **SIM** — `convergence_significance.csv` (108 testes, 59.3% significativos)
- [x] ECDF com bandas visíveis em pelo menos um painel? → **SIM** — Fig 5 v2 com bootstrap CI (500 replicates)
- [x] Análise de sensibilidade não inverte conclusão principal? → **SIM** — suavização tem impacto ≤0.25; 1° checkpoint tem impacto maior (≤0.48), justificando descarte
- [x] Protocolo de seleção documentado e replicável? → **SIM** — `docs/CONVERGENCE_SELECTION_PROTOCOL.md`
- [x] Todos os scripts rodam de um target Make sem intervenção manual? → **SIM** — novo alvo `make analysis-convergence` (com subalvos `-build`, `-summaries`, `-tests`, `-plots`) no Makefile raiz, encadeado por dependências.

---

## Notas Técnicas

### Dependências Python adicionais necessárias
- `scipy.stats.wilcoxon` — já disponível (scipy)
- `scipy.stats.kstest` — já disponível
- Bootstrap manual — já implementável com numpy
- `statsmodels.stats.multitest.multipletests` — verificar se está em `requirements.txt`

### Dados existentes reutilizáveis
- `.mat` files em `src/matlab/lib/PlatEMO/Data/*/` (run 7001–7030) já contêm HV
- `explore_convergence_visuals.py` já tem esqueleto de AUC — estender
- `explore_convergence_advanced.py` já tem delta ECDF — usar como base

### Riscos
- **Re-executar MATLAB**: se HV não foi salvo em algum run, precisa re-rodar (30 runs × 6 algos × 6 instâncias = 1080 runs, ~horas).
- **Tempo de bootstrap**: 10.000 iterações × 6 algoritmos × 6 instâncias pode ser lento; paralelizável.
- **Memória**: ECDF com bootstrap 1000× pode exigir ~100MB RAM por algoritmo; tranquilo.
