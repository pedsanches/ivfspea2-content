# Revision Changelog

Registro histórico da revisão do manuscrito *IVF hosts* (PPSN 2026), encerrada
com o camera-ready na tag `ppsn2026` (2026-06-12). Descreve o que foi feito na
época, não o estado atual do repositório.

> **Tabelas citadas abaixo que não estão mais em `results/tables/`.** O commit
> `39d3c31` removeu `hosts_fe_audit.*`, `hosts_pairing_robustness.*`,
> `hosts_parameter_provenance.*` e `hosts_dynamic_aggregate_*` de `results/`.
> Elas continuam no artefato depositado
> (`artifact/ppsn2026-ivf-hosts-rev1/tables/`), que é o que o manuscrito
> referencia. Os geradores seguem vivos: `make analysis-hosts-audits` os
> reconstrói.

## Passo 1-2

- Reenquadrado o manuscrito no nível de comparação entre pipelines `host + host-specific IVF realization`.
- Expandido o related work com âncoras concretas em memetic MOEAs, taxonomias de híbridos e mating guiado por estrutura.
- Reescrita a seção experimental para explicitar FE accounting, famílias de testes com Benjamini–Hochberg, métricas/referências e proveniência de parâmetros.
- Requalificado o bloco dinâmico como evidência diagnóstica no escopo atual.
- Atualizadas a discussão, as conclusões e a nota de material suplementar para alinhar o texto com o escopo pipeline-level.
- Adicionadas as entradas BibTeX `knowles2000memetic`, `talbi2002taxonomy`, `blum2011hybrid` e `Lu2025`.

### Arquivos modificados

- `paper/ppsn2026-ivf-hosts/main.tex`
- `paper/ppsn2026-ivf-hosts/references.bib`
- `REVISION_CHANGELOG.md`

## Passo 3

- Implementada a auditoria de FE accounting, combinando leitura estática das classes MATLAB com diagnóstico empírico dos checkpoints dinâmicos.
- Implementada a auditoria de proveniência de parâmetros, comparando os defaults em código com os valores declarados no manuscrito.
- Recomputada a análise de robustez de pareamento: Wilcoxon estrito para os tracks NSGA, Mann–Whitney no bloco não pareado IVF/SPEA2 e Wilcoxon por alinhamento de ordem como sensibilidade.
- Aplicada correção de Benjamini–Hochberg ao bloco ECDF e atualizada a caption da figura correspondente no manuscrito.

### Arquivos modificados

- `paper/ppsn2026-ivf-hosts/main.tex`
- `src/python/analysis/audit_hosts_fe_accounting.py`
- `src/python/analysis/build_hosts_parameter_provenance.py`
- `src/python/analysis/compute_hosts_pairing_robustness.py`
- `src/python/analysis/adjust_ecdf_bh.py`
- `results/tables/hosts_fe_audit.csv`
- `results/tables/hosts_fe_audit.tex`
- `results/tables/hosts_parameter_provenance.csv`
- `results/tables/hosts_parameter_provenance.tex`
- `results/tables/hosts_pairing_robustness.csv`
- `results/tables/hosts_pairing_robustness.tex`
- `results/tables/ecdf_significance.csv`
- `results/tables/ecdf_significance_bh.tex`

## Passo 4

- Promovido o arquivo `config/hosts_front_geometry.csv` como fonte explícita de rótulos geométricos para as 51 instâncias do estudo.
- Executada a análise estratificada por geometria com sumarização W/T/L e mediana de $A_{12}^{\mathrm{IVF}}$ por host, métrica e estrato geométrico.
- Executados testes de interação por permutação para `host × geometry` em IGD e HV, tanto para `geometry_primary` quanto para o colapso `regular` vs `irregular`.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `config/hosts_front_geometry.csv`
- `src/python/analysis/compute_hosts_geometry_stratified.py`
- `results/tables/hosts_geometry_summary.csv`
- `results/tables/hosts_geometry_summary.tex`
- `results/tables/hosts_geometry_interaction.csv`

## Passo 5-7

- Gerada a tabela compacta de endpoint `hosts_rep_endpoint_igd.tex` com seleção determinística de casos representativos (gain, tie e adverse/weakest) para os três hosts.
- Inserido o `\input` dessa tabela no manuscrito para resolver `tab:rep_endpoint_medians` antes da reescrita final de `Results`.
- Confirmado o gate dinâmico positivo com traces all-suite disponíveis para os três pares de host, incluindo os reruns com trace de `IVFSPEA2V2` e `SPEA2`.
- Executada a análise dinâmica agregada sobre as 51 instâncias usando gap normalizado em IGD/HV, curvas de fração resolvida com bootstrap e resumo por `host × M × geometria`.
- Gerada a nova figura `hosts_v2_fig5_dynamic_aggregate.pdf` para substituição/integração posterior no corpo principal.
- Gerado também o artefato intermediário `results/tables/hosts_dynamic_normalized_traces.csv`; por ser um derivado pesado (174 MB) e totalmente reproduzível a partir do script e dos traces-fonte, ele foi deixado fora do commit.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `paper/ppsn2026-ivf-hosts/main.tex`

## Passo 10

- Aplicados cortes de budget LNCS no manuscrito principal.
- `Background` foi condensado de dois blocos descritivos longos para dois parágrafos curtos, preservando apenas o contraste funcional relevante entre SPEA2, NSGA-II e NSGA-III e o núcleo comum da família IVF.
- A nota após a Tabela~1 foi reduzida a uma frase curta explicitando o nível de inferência em pipeline.
- O apêndice `Supplementary Summary Tables` foi removido do PDF principal; as tabelas-resumo e o material auxiliar passaram a existir apenas no artifact/suplemento.
- O parágrafo de assimetria em dimensionalidade foi encurtado para evitar repetição de contagens W/T/L já visíveis na figura.
- Resultado final: o PDF principal caiu de 16 para 14 páginas LNCS, sem necessidade de mover figuras adicionais para o suplemento.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `paper/ppsn2026-ivf-hosts/main.tex`
- `src/python/analysis/build_hosts_rep_endpoint_table.py`
- `src/python/analysis/compute_hosts_dynamic_aggregate.py`
- `results/tables/hosts_rep_endpoint_igd.csv`
- `results/tables/hosts_rep_endpoint_igd.tex`
- `results/tables/hosts_dynamic_aggregate_curves.csv`
- `results/tables/hosts_dynamic_aggregate_summary.csv`
- `results/tables/hosts_dynamic_aggregate_tau10.tex`
- `results/figures/hosts_v2_fig5_dynamic_aggregate.pdf`
- `paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig5_dynamic_aggregate.pdf`

## Passo 8-9

- Reescrita a seção `Results` para integrar explicitamente: (i) a tabela compacta de dispersão por medianas/IQR, (ii) a estratificação por geometria, e (iii) a nova evidência dinâmica agregada all-suite.
- Mantida a distinção entre evidência confirmatória (agregado all-suite) e evidência diagnóstica (bloco de seis instâncias), removendo a dependência interpretativa da antiga figura ECDF como principal suporte dinâmico.
- Ajustadas `Discussion` e `Conclusions` para refletir com mais precisão que: (i) a geometria fornece padrões estratificados sugestivos, mas sem interação significativa por permutação; e (ii) `IVF/NSGA-II` continua sendo o host mais fraco no agregado, embora não totalmente inerte nas curvas dinâmicas em estratos regulares.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `paper/ppsn2026-ivf-hosts/main.tex`
