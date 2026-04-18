# Revision Changelog

## Passo 1-2

- Reenquadrado o manuscrito no n\'ivel de compara\c{c}\~ao entre pipelines `host + host-specific IVF realization`.
- Expandido o related work com \^ancoras concretas em memetic MOEAs, taxonomias de h\'ibridos e mating guiado por estrutura.
- Reescrita a se\c{c}\~ao experimental para explicitar FE accounting, fam\'ilias de testes com Benjamini--Hochberg, m\'etricas/refer\^encias e proveni\^encia de par\^ametros.
- Requalificado o bloco din\^amico como evid\^encia diagn\'ostica no escopo atual.
- Atualizadas a discuss\~ao, as conclus\~oes e a nota de material suplementar para alinhar o texto com o escopo pipeline-level.
- Adicionadas as entradas BibTeX `knowles2000memetic`, `talbi2002taxonomy`, `blum2011hybrid` e `Lu2025`.

### Arquivos modificados

- `paper/ppsn2026-ivf-hosts/main.tex`
- `paper/ppsn2026-ivf-hosts/references.bib`
- `REVISION_CHANGELOG.md`

## Passo 3

- Implementada a auditoria de FE accounting, combinando leitura est\'atica das classes MATLAB com diagn\'ostico emp\'irico dos checkpoints din\^amicos.
- Implementada a auditoria de proveni\^encia de par\^ametros, comparando os defaults em c\'odigo com os valores declarados no manuscrito.
- Recomputada a an\'alise de robustez de pareamento: Wilcoxon estrito para os tracks NSGA, Mann--Whitney no bloco n\~ao pareado IVF/SPEA2 e Wilcoxon por alinhamento de ordem como sensibilidade.
- Aplicada corre\c{c}\~ao de Benjamini--Hochberg ao bloco ECDF e atualizada a caption da figura correspondente no manuscrito.

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

- Promovido o arquivo `config/hosts_front_geometry.csv` como fonte expl\'icita de r\'otulos geom\'etricos para as 51 inst\^ancias do estudo.
- Executada a an\'alise estratificada por geometria com sumariza\c{c}\~ao W/T/L e mediana de $A_{12}^{\mathrm{IVF}}$ por host, m\'etrica e estrato geom\'etrico.
- Executados testes de intera\c{c}\~ao por permuta\c{c}\~ao para `host \times geometry` em IGD e HV, tanto para `geometry_primary` quanto para o colapso `regular` vs `irregular`.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `config/hosts_front_geometry.csv`
- `src/python/analysis/compute_hosts_geometry_stratified.py`
- `results/tables/hosts_geometry_summary.csv`
- `results/tables/hosts_geometry_summary.tex`
- `results/tables/hosts_geometry_interaction.csv`

## Passo 5-7

- Gerada a tabela compacta de endpoint `hosts_rep_endpoint_igd.tex` com sele\c{c}\~ao determin\'istica de casos representativos (gain, tie e adverse/weakest) para os tr\^es hosts.
- Inserido o `\input` dessa tabela no manuscrito para resolver `tab:rep_endpoint_medians` antes da reescrita final de `Results`.
- Confirmado o gate din\^amico positivo com traces all-suite dispon\'iveis para os tr\^es pares de host, incluindo os reruns com trace de `IVFSPEA2V2` e `SPEA2`.
- Executada a an\'alise din\^amica agregada sobre as 51 inst\^ancias usando gap normalizado em IGD/HV, curvas de fra\c{c}\~ao resolvida com bootstrap e resumo por `host \times M \times geometria`.
- Gerada a nova figura `hosts_v2_fig5_dynamic_aggregate.pdf` para substitui\c{c}\~ao/integra\c{c}\~ao posterior no corpo principal.
- Gerado tamb\'em o artefato intermedi\'ario `results/tables/hosts_dynamic_normalized_traces.csv`; por ser um derivado pesado (174 MB) e totalmente reproduz\'ivel a partir do script e dos traces-fonte, ele foi deixado fora do commit.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `paper/ppsn2026-ivf-hosts/main.tex`

## Passo 10

- Aplicados cortes de budget LNCS no manuscrito principal.
- `Background` foi condensado de dois blocos descritivos longos para dois par\'agrafos curtos, preservando apenas o contraste funcional relevante entre SPEA2, NSGA-II e NSGA-III e o n\'ucleo comum da fam\'ilia IVF.
- A nota ap\'os a Tabela~1 foi reduzida a uma frase curta explicitando o n\'ivel de infer\^encia em pipeline.
- O ap\^endice `Supplementary Summary Tables` foi removido do PDF principal; as tabelas-resumo e o material auxiliar passaram a existir apenas no artifact/suplemento.
- O par\'agrafo de assimetria em dimensionalidade foi encurtado para evitar repetição de contagens W/T/L j\'a vis\'iveis na figura.
- Resultado final: o PDF principal caiu de 16 para 14 p\'aginas LNCS, sem necessidade de mover figuras adicionais para o suplemento.

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

- Reescrita a se\c{c}\~ao `Results` para integrar explicitamente: (i) a tabela compacta de dispers\~ao por medianas/IQR, (ii) a estratifica\c{c}\~ao por geometria, e (iii) a nova evid\^encia din\^amica agregada all-suite.
- Mantida a distin\c{c}\~ao entre evid\^encia confirmat\'oria (agregado all-suite) e evid\^encia diagn\'ostica (bloco de seis inst\^ancias), removendo a depend\^encia interpretativa da antiga figura ECDF como principal suporte din\^amico.
- Ajustadas `Discussion` e `Conclusions` para refletir com mais precis\~ao que: (i) a geometria fornece padr\~oes estratificados sugestivos, mas sem intera\c{c}\~ao significativa por permuta\c{c}\~ao; e (ii) `IVF/NSGA-II` continua sendo o host mais fraco no agregado, embora n\~ao totalmente inerte nas curvas din\^amicas em estratos regulares.

### Arquivos modificados

- `REVISION_CHANGELOG.md`
- `paper/ppsn2026-ivf-hosts/main.tex`
