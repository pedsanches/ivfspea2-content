# Revisao tecnica do paper (sn-article.tex)

Date: 2026-02-28
Status: Major revision recomendada antes de submissao
Escopo revisado: `paper/src/sn-article.tex` (revisao completa), coerencia com implementacao MATLAB e qualidade cientifica geral

## 1) Veredito executivo

O manuscrito esta promissor e bem estruturado, mas ainda tem bloqueios cientificos e de coerencia metodo-implementacao que precisam ser resolvidos antes da submissao.

Classificacao atual: **major revision**.

## 2) Pontos fortes atuais

- Protocolo experimental amplo (ZDT, DTLZ, WFG, MaF e RWMOP) com `n=60` por configuracao.
- Discussao nao triunfalista (reconhece limites e dependencia de paisagem).
- Existe controle de multiplicidade para o claim principal (Holm-Bonferroni).
- Ha secao explicita de ameacas a validade.

## 3) Problemas cientificos criticos (alta prioridade)

### 3.1 Inconsistencia entre metodo descrito e implementacao canonica v2

No texto do paper, o metodo esta descrito como:

- pai unico sorteado no intervalo top-`2c`;
- continuacao do ciclo com criterio `F(x*) < F(father)`.

Referencias no paper:

- `paper/src/sn-article.tex:185`
- `paper/src/sn-article.tex:199`

Na implementacao canonica v2, o comportamento e outro:

- pai dissimilar por mae (distancia em espaco de objetivos + torneio);
- continuacao por melhora coletiva da media de fitness da populacao.

Referencias no codigo:

- `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/IVF_V2.m:35`
- `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/IVF_V2.m:168`

Impacto: risco de invalidar interpretacao dos resultados por desalinhamento metodo-resultados.

### 3.2 Variante do algoritmo nao explicitada de forma inequvoca

O manuscrito menciona V2 apenas pontualmente, sem cravar claramente classe/versao usada no pipeline inteiro.

Referencia:

- `paper/src/sn-article.tex:396`

Impacto: reprodutibilidade e atribuicao causal comprometidas.

### 3.3 Possivel vies de tuning (leakage treino-teste)

O texto reporta tuning no subconjunto FULL12 e resultados no benchmark amplo, mas sem separar com rigor o que e tuning e o que e avaliacao confirmatoria fora do conjunto usado para promocao.

Referencia:

- `paper/src/sn-article.tex:641`

Impacto: pode inflar desempenho reportado.

### 3.4 Inferencia fragil em problemas de engenharia com baixa factibilidade

No RWMOP8, ha algoritmos com baixa/zero validade de run para metricas, mas ainda com comparacoes estatisticas no mesmo bloco narrativo.

Referencias:

- `paper/src/sn-article.tex:526`
- `paper/src/sn-article.tex:544`

Impacto: comparabilidade desigual e risco de conclusao enviesada.

### 3.5 Ablacao top-2c nao totalmente alinhada ao default promovido

A ablacao do top-`2c` foi feita com configuracao AR antiga (`c=0.11`, `r=0.10`, `l=3`), enquanto o default promovido principal e C26/EAR-P.

Referencia:

- `paper/src/sn-article.tex:515`

Impacto: evidencia parcial para justificar o default final.


## 6) Problemas tecnicos de LaTeX observados na compilacao

Compilacao executada com `make` em `paper/`.

Principais avisos:

- Float muito grande na pagina (algorithm/table).
  - `paper/src/sn-article.tex:247`
  - `paper/src/sn-article.tex:371`
- Overfull hbox na tabela de ablacao.
  - `results/ablation/ablation_table.tex:1`
- Warning de nivel de bookmark (estrutura de secoes).
  - `paper/src/sn-article.tex:668`

## 7) Plano de acao recomendado (para progresso)

### Fase A - Bloqueios cientificos (obrigatorio)

- [x] Atualizar para suporte oficial ao algoritmo otimizado v2. Tratar sempre como IVF/SPEA2 apenas. Os dados serão do IVF/SPEA2 v2
- [x] Alinhar Secao de Metodo, pseudocodigo, ablacoes e claims com a variante escolhida acima.
- [x] Adicionar identificadores reprodutiveis (classe, script, versao/commit, run ranges).

### Fase B - Robustez estatistica

- [x] Separar claramente analise de tuning e avaliacao confirmatoria.

### Fase C - Cobertura de metricas e engenharia

- [ ] Em RWMOP resolver todos os algoritmos com inviabilidade para que tenham 60 runs viáveis (requer re-execução MATLAB — fora do escopo desta revisão textual)

### Fase D - Pronto para submissao

- [x] Remover linguagem de bastidor de revisao e ajustar estrutura para compliance do journal.
- [x] Corrigir warnings principais de LaTeX (floats, overfull, bookmarks). Warnings residuais são inerentes ao template Springer (float da tabela de 9 algoritmos + bookmark levels no backmatter).

## 8) Criterio de saida (Definition of Done)

Este review sera considerado resolvido quando:

1. Metodo no paper e metodo no codigo canonico estiverem 1:1 consistentes.
2. Claims principais forem sustentados por analise estatistica robusta e claramente delimitada.
3. IGD/HV e viabilidade estiverem reportados com cobertura e limites transparentes.
4. Manuscrito compilar limpo (sem warnings estruturais relevantes) e pronto para submissao formal.
