# Protocolo de Seleção de Instâncias para Análise de Convergência

**Data:** 2026-04-15
**Versão:** 1.0
**Status:** Pré-registrado

## Objetivo

Selecionar 6 instâncias (problema × número de objetivos) representativas dos 51 hosts
avaliados, para exibição de curvas de convergência temporal (Fig 4) e ECDF (Fig 5).

## Dados de Entrada

Três arquivos de estatísticas Vargha-Delaney A12 orientados:
- `results/tables/hosts_ivfspea2_igd_stats.csv`
- `results/tables/hosts_ivfnsgaii_igd_stats.csv`
- `results/tables/hosts_ivfnsgaiii_igd_stats.csv`

Cada arquivo contém: `problem`, `M`, `group`, `A12`, `sign` (onde `sign ∈ {+, =, -}`).

O A12 é definido como P(IVF > base) + 0.5·P(IVF = base) para IGD, onde valores
menores indicam que IVF é melhor (IGD menor). Para análise, orientamos como:
`A12_ivf = 1 - A12`, de modo que **A12_ivf > 0.5 indica vantagem do IVF**.

## Critérios de Seleção

São selecionadas 6 instâncias, uma por "papel" (role), sem sobreposição de
`(problem, M)`:

| Slot | Papel | Critério | Grupo |
|---|---|---|---|
| 1 | `strong_both_dtlz` | Maior A12_ivf combinado (IVFSPEA2 + IVFNSGAIII) | DTLZ, M=2 |
| 2 | `strong_both_maf` | Maior A12_ivf combinado (IVFSPEA2 + IVFNSGAIII) | MaF, M=2 |
| 3 | `difficult_wfg` | Mais empates (`sign = "="`) + menor A12 combinado | WFG, M=2 |
| 4 | `spea2_wins_zdt` | SPEA2 tem vantagem (+) + NSGA-II neutro (A12 ≈ 0.5) | ZDT, M=2 |
| 5 | `nsgaiii_drops_m3` | NSGA-III perde mais ao ir de M=2 para M=3 | DTLZ, M=3 |
| 6 | `spea2_loss_wfg` | Pior A12_ivf do SPEA2 em WFG (ou menor se sem perdas) | WFG, M=2 |

### Regras de Desempate

1. **Sem sobreposição**: uma instância `(problem, M)` só pode ser selecionada uma vez.
2. **Preferência por sinal forte**: quando disponível, filtra-se por `sign = "+"` antes
   de ordenar pela magnitude.
3. **Determinismo**: ordenação é estritamente por colunas numéricas; não há aleatoriedade.

## Script de Seleção

```
src/python/analysis/select_convergence_instances.py
```

O script é determinístico e re-executável. Qualquer alteração no critério deve ser
documentada neste arquivo e no git log.

## Instâncias Selecionadas

| Slot | Problema | M | Papel |
|---|---|---|---|
| 1 | DTLZ5 | 2 | strong_both_dtlz |
| 2 | MaF1 | 2 | strong_both_maf |
| 3 | WFG8 | 2 | difficult_wfg |
| 4 | ZDT4 | 2 | spea2_wins_zdt |
| 5 | DTLZ5 | 3 | nsgaiii_drops_m3 |
| 6 | WFG2 | 2 | spea2_loss_wfg |

## Análise de Sensibilidade

Para avaliar robustez da seleção, um script alternativo (`select_convergence_sensitivity.py`)
seleciona a **segunda melhor escolha** por grupo e compara as conclusões qualitativas
(direção do efeito IVF vs base) das figuras resultantes. Se as conclusões forem consistentes,
a seleção principal é considerada robusta.

## Limitações Reconhecidas

1. As 6 instâncias não cobrem todo o espaço de problemas (51 hosts).
2. A seleção é orientada por efeitos observados (A12), não por randomização.
3. Fig 4 e Fig 5 no paper mostram apenas estas 6 instâncias; o sumário agregado
   completo (todas as 51 instâncias) está disponível nos resultados supplementares.

## Histórico de Revisões

| Data | Versão | Mudança |
|---|---|---|
| 2026-04-15 | 1.0 | Pré-registro inicial |
