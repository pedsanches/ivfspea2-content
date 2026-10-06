# Especificação da reescrita da dissertação IVF/SPEA2

Fonte da verdade da reescrita. Para cada capítulo novo, fixa qual afirmação entra,
de qual artefato ela vem, quem a produz, sob qual coorte e qual correção.

Não é um inventário de defeitos do texto importado. O texto importado descreve uma
formulação anterior cuja coorte (`2001–2100`) **não existe neste checkout** — foi
verificado: o CSV consolidado não contém nenhum identificador nessa faixa, para
nenhum algoritmo. Aquelas tabelas não são atualizáveis linha a linha; são
substituídas.

Complementa `REVISION_PLAN.md`, que continua sendo o índice estratégico, e obedece
a `SCIENTIFIC_WRITING_PROFILE.md`. Onde este documento e o perfil divergirem, vale
a §1 abaixo — decisão documentada do autor precede o perfil, conforme o próprio
perfil §1.

Estado do checkout na redação: commit `39ddf27`, árvore limpa, `make thesis-doctor`
aprovando 7 fontes e 58 caminhos.

---

## 1. Decisões e vocabulário

### 1.1 Decisões do autor

1. **Formato monográfico.**
2. **Não versionar.** Não existe "v1" nem "v2" no texto da dissertação. Existe **um**
   IVF/SPEA2: o acoplamento proposto no manuscrito da Springer Nature.
3. **Reescrita quase integral**, tomando os manuscritos como verdade.
4. **Fontes:** `paper/springer-nature/`, `paper/ppsn2026-ivf-hosts/` (aceito, PPSN 2026)
   e `paper/clei2026/`. O `paper/ppsn2026/` fica fora: é a mesma família de evidência
   do CLEI em outra saída editorial, e é a versão cujo número de turnover em WFG não
   reproduz do artefato (`OQ-01`).
5. **Ordem:** esta especificação primeiro, reescrita capítulo a capítulo depois.
6. **Sem re-execução (2026-09-22).** A dissertação é montada apenas com os artefatos
   existentes. Análises novas são admitidas quando recalculam a partir de artefatos
   versionados, por um gerador em `src/python/thesis/` coberto pelo portão de deriva. O que
   só uma nova campanha responderia — a ablação na configuração promovida (`OQ-14`) — é
   declarado como limite e vai para os trabalhos futuros.
7. **Artefato precede leitura.** Os números vêm dos manuscritos; quando a *leitura* que um
   manuscrito faz deles não sobrevive ao artefato que a sustenta, o texto segue o artefato
   e a divergência vira questão aberta, para decisão sobre errata. Precedentes: `OQ-01`,
   `OQ-13`, `OQ-16`, `OQ-17`.

### 1.2 A proibição de versionamento, na prática

| Recusado no texto | Aceito |
|---|---|
| "o IVF/SPEA2 v2 propõe" | "o IVF/SPEA2 propõe" |
| "diferentemente da v1" | "diferentemente dos acoplamentos anteriores do IVF a algoritmos hospedeiros" |
| "a versão anterior usava critério individual" | "as formulações anteriores do IVF condicionavam a continuação do ciclo a um único descendente" |
| "parâmetros da v1 (`c=10%`, `r=10%`)" | "a configuração inicial não ajustada, herdada da literatura de IVF" |
| "a v2 empata com a v1" | "a ablação não distingue o acoplamento completo da variante sem as duas decisões" |

**Escopo da proibição.** Vale para `tex/**` e `pre/**` — a prosa da dissertação. Não
vale para este documento, para `REVISION_PLAN.md`, para `data-sources.toml` nem para
nomes de diretório (`results/ablation_v2/`), que são registro interno de posicionamento.

**Identificadores de artefato.** `IVFSPEA2V2` é nome de classe MATLAB, não afirmação de
versão. Pode aparecer, em fonte monoespaçada, **apenas** no Apêndice A e na declaração
de disponibilidade de código.

Verificação ao fim de cada rodada de prosa:

```bash
grep -rniE "\bv1\b|\bv2\b|vers(ão|ao) (1|2|anterior do (nosso|presente))" thesis/masters/tex thesis/masters/pre
```

### 1.3 Reenquadramento que a decisão 2 força

Duas evidências do Springer comparam contra a formulação anterior. Sem linguagem de
versão, elas se reenquadram pelo que factualmente são — e o enquadramento novo é o
mais preciso, porque nomeia o mecanismo em vez do rótulo:

| Evidência | Enquadramento a evitar | Enquadramento correto |
|---|---|---|
| Ablação, `phase3_summary.json`: 0/50/1 contra `IVFSPEA2` | "empata com a v1" | ablação **contra a variante sem seleção de pai dissimilar e sem continuação coletiva**; mede a contribuição das decisões de acoplamento |
| Ablação, 25/25/1 (IGD) e 28/21/2 (HV) contra `SPEA2` | — | inalterado: acoplamento completo × SPEA2 canônico |
| Tuning: C26 × linha de base pré-ajuste (`c=0.11, r=0.10, AR, ℓ=3`) | "configuração da v1" | **configuração inicial não ajustada**, herdada da literatura de IVF |

No Cap. VIII, IVF/NSGA-II e IVF/NSGA-III **continuam sendo acoplamentos distintos**:
são pipelines publicados por outros autores, em outros hospedeiros. A proibição
recai sobre apresentar *a proposta desta dissertação* em múltiplas versões, não sobre
a comparação entre hospedeiros.

### 1.4 Emendas obrigatórias a documentos de governo

Aplicadas nesta mesma rodada, porque toda a reescrita se apoia neles:

- `SCIENTIFIC_WRITING_PROFILE.md` §4 (linhas 119–121) e §5 (linhas 163–164) — hoje
  fixam "IVF/SPEA2 v2" e "IVF/SPEA2 v1" como vocabulário canônico.
- `REVISION_PLAN.md` §2 — hoje manda separar `IVFSPEA2` (v1) de `IVFSPEA2V2` e
  preservar parâmetros da v1.

### 1.5 Questões de pesquisa (R8; QP2 e QP3 reformuladas na R14, ver §1.6)

A dissertação responde a cinco questões (R17); só a QP1 é respondida pela avaliação comparativa
principal (§1.7; até a R14b, "confirmatória"). Numeração de capítulo
conforme o PDF compilado (o Cap. VII é `cap_VII_complementares.tex`; o Cap. VIII é
`cap_VII.tex`).

| QP | Pergunta | Onde | Família | Afirmações |
|---|---|---|---|---|
| QP1 | O IVF/SPEA2 supera o SPEA2 sob orçamento idêntico, e com que magnitude? | Cap. VI; §7.1 | `CONF`; `ENG` | `C-CONF-*`, `C-MAG-*`; `C-ENG-04` |
| QP2 | Que diferenças de desempenho são observadas entre as configurações e as variantes de acoplamento avaliadas nos estudos de calibração e ablação do IVF/SPEA2? | §7.2 | `SUP` | `C-TUN-01`, `C-ABL-*` |
| QP3 | Como varia o desempenho relativo dos acoplamentos IVF/SPEA2, IVF/NSGA-II e IVF/NSGA-III diante de seus respectivos hospedeiros? | §7.3 | `HOST` | `C-HOST-*` |
| QP4 | É possível decidir cedo quando usar o operador, e isso compensa? (R14b: objetivo geral e OE5 cobrem informação anterior à execução e da dinâmica inicial; o comparador do benefício do controle é o IVF/SPEA2 sempre ativo; o controlador decide só pela renovação inicial do arquivo, `IVFSPEA2V2CTRLTRACE.m`, `controller_feature = mean_turnover`) | §7.4 | `DEC` | `C-FLA-*`, `C-DYN-*`, `C-CTRL-*` |
| QP5 | Como o IVF/SPEA2 se posiciona, em IGD e HV, diante dos sete algoritmos comparados, e em que medida o posicionamento varia com o número de objetivos? (R17: pergunta **comparativa**, formulada depois de calculadas as contagens, não hipótese prévia; correção de Holm por comparador, por número de objetivos e por métrica) | §7.5; §8.5 | `CONF` (mesma coorte, papel contextual) | `C-POS-*`, `tab:posicionamento` |

Cada questão é **respondida num único lugar**, a seção correspondente do Cap. VIII; os
demais capítulos remetem a ela. Os quatro defeitos de argumentação das auditorias de 20/09
tinham a mesma forma — um trecho reenunciava o resultado de outro e o alterava —, e esta
regra existe para impedi-los.

### 1.6 Reenquadramento de QP2 e QP3 (R14, 2026-10-01)

Decisão do autor. Os quatro eixos de pesquisa ficam — eficácia, configuração e decisões
de acoplamento, variação entre acoplamentos, ativação —, mas a QP2 e a QP3 passam a ser
perguntas **comparativas sobre os estudos realizados**, para aproximar pergunta, desenho e
resposta. A QP1 e a QP4 não mudam.

| QP | Formulação R8 (histórico) | Formulação R14 (vigente) |
|---|---|---|
| QP2 | "Atribuição." O ganho decorre das duas decisões de acoplamento ou da configuração do operador? Objetivo: verificar se o ganho se deve às duas decisões ou à configuração. | "Configuração e decisões de acoplamento." Que diferenças de desempenho são observadas entre as configurações e as variantes de acoplamento avaliadas nos estudos de calibração e ablação do IVF/SPEA2? Objetivo: comparar o desempenho das configurações e das variantes de acoplamento avaliadas nesses estudos. |
| QP3 | "Dependência do hospedeiro." O benefício do operador IVF depende do algoritmo que o hospeda? Objetivo: verificar se o benefício depende do algoritmo que o hospeda. | "Variação entre acoplamentos." Como varia o desempenho relativo dos acoplamentos IVF/SPEA2, IVF/NSGA-II e IVF/NSGA-III diante de seus respectivos hospedeiros? Objetivo: comparar os perfis de desempenho desses acoplamentos em relação aos respectivos hospedeiros. |

Regras que acompanham a decisão:

1. **Não são hipóteses prévias.** As formulações novas foram fixadas depois dos estudos e
   não podem ser apresentadas como hipóteses declaradas antes deles. A QP1 continua sendo a
   única confirmatória; a força de `SUP` e de `HOST` não muda.
2. **Resposta pela comparação.** A resposta da QP2 e da QP3 abre pelo resultado comparativo
   observado e segue a ordem resultado → interpretação sustentada → alcance → questão
   aberta. Uma resposta composta só por "não foi possível atribuir" ou "o efeito causal não
   foi identificado" não responde à pergunta nova; esses limites continuam no ponto
   pertinente (alcance e questão aberta).
3. **A atribuição continua aberta.** A atribuição do ganho às duas decisões, à configuração
   ou ao recálculo de aptidão (`OQ-14`, `OQ-24`) e o efeito isolado do hospedeiro (`OQ-25`)
   permanecem problemas **não isolados**; nenhuma formulação nova os converte em achado.
4. **QP3: dois níveis de inferência.** Os testes de cada acoplamento contra o seu
   hospedeiro (Wilcoxon, BH por acoplamento e métrica) são distintos da ordenação entre
   pipelines, que é **descritiva**: nenhum teste compara diretamente o desempenho dos
   acoplamentos entre si (o único teste que envolve os três, a interação entre hospedeiro e
   geometria, não atingiu significância e responde a outra pergunta).
5. **QP2: o contraste histórico de calibração** (C26 e A43 × `IVFSPEA2v1`) muda a
   formulação (o braço histórico é `IVFSPEA2`, sem as duas decisões:
   `head_to_head_c26_a43_v1_summary.json`, `inputs.baseline_algorithm`; as configurações
   calibradas rodaram `IVFSPEA2V2`, `scripts/experiments/run_ivfspea2v2_tuning.m:220`) e os
   parâmetros, além das diferenças já declaradas de execuções (60 × 30) e de orçamento
   (não registrado no artefato).
6. **Sem mudança de evidência.** Nenhum número, parâmetro, coorte, teste ou correção muda;
   não há campanha nem análise numérica nova; "hospedeiro" não é substituído globalmente
   por "pipeline"; o rótulo "confirmatória" não é reclassificado nesta rodada.

Respostas sustentadas antes da R14, transcritas de `REVISION_PLAN.md` §2 (estado R13), como
registro:

- **QP2 (R13):** "Configurações C26 e A43 usam 30 execuções, a histórica 60 e orçamento não
  verificado no contraste; não é teste isolado dos parâmetros. A calibração usou 50.000
  avaliações e a avaliação 100.000; a estabilidade da escolha entre orçamentos não foi estudada
  (§9.1). A ablação inicial registra 0/50/1 diante da ausência das duas decisões em cada
  métrica, sem equivalência; Friedman fatorial p = 0,485 não prova igualdade. Na configuração
  promovida não há ablação; o recálculo de aptidão antes do torneio também não foi isolado. A
  hipótese de densidade permanece justificativa de projeto." Natureza: "apoio; atribuição
  indeterminada".
- **QP3 (R13):** "Dois níveis. (a) Os resultados diferem entre os pipelines avaliados: em
  IGD, 33 de 51 instâncias no SPEA2, 22 no NSGA-III e 1 no NSGA-II (30 execuções, Wilcoxon,
  BH). (b) O efeito causal do hospedeiro não foi identificado: hospedeiro, realização do
  módulo, recombinação, ativação, configuração e procedimento de ajuste variam juntos; só o
  IVF/SPEA2 tem calibração documentada nesta suíte, e os pipelines NSGA usam configurações
  fixas dos runners, sem registro de ajuste equivalente (`OQ-25`)." Natureza: "comparativa".

### 1.7 Nomenclatura da avaliação principal (R15, 2026-10-01)

Decisão do autor, opção (c) de `OQ-26`. A comparação IVF/SPEA2 × SPEA2 na suíte sintética
(família `CONF`) passa a ser chamada, na prosa da dissertação, **avaliação comparativa
principal** ou **comparação principal**, conforme a função da frase; a família, "família da
comparação principal", e a sua coorte, "coorte da comparação principal".

- "Principal" descreve o **papel** da avaliação na dissertação. Não afirma
  pré-especificação (a anterioridade continua não verificada, `OQ-26`) nem cria categoria
  nova de força estatística. A IGD continua desfecho primário e o HV, secundário obrigatório;
  testes, correções, coortes e contagens não mudam.
- As demais famílias mantêm o papel e a inferência que tinham (apoio, comparativa,
  diagnóstica); nada passa a "exploratório" por efeito desta decisão.
- Ficam como estão os identificadores técnicos: `CONF`, `C-CONF-*`, o id de fonte
  `memetic-computing-v2-confirmatory`, nomes de arquivo e de função
  (`tab_confirmatorio_wtl`, `build_tab_*_confirmatoria.py`, `_a12_confirmatorio`), rótulos
  (`sec:confirmatorio`, `tab:*confirmatori*`). No manifesto, o papel da fonte passou de
  `confirmatory` a `primary`, traduzido como "principal" no Apêndice A.
- Registros históricos (rodadas R1–R14b, verificações de `OQ-*` já fechadas, alvo original
  da §6.1) mantêm a palavra da época. Declarações literais dos manuscritos de origem
  ("pre-specified", "confirmatory") não são reescritas.

---

## 2. Estado verificado do checkout

### 2.1 Viabilidade por família

| Família | Veredito | Fato determinante |
|---|---|---|
| Confirmatória (Springer) | **REGENERÁVEL** | `todas_metricas_consolidado_with_modern.csv`, 30 660 linhas, com `3001–3060` e `1–60` completos |
| Formulação anterior | **BLOQUEADA / irrelevante** | faixa `2001–2100` ausente para todos os algoritmos; nada dela entra no texto |
| Tuning, ablação, engenharia | **SÓ ARTEFATO CONGELADO** | artefatos presentes e conferidos; `data/ablation_v2/`, `data/tuning_ivfspea2v2/` e `data/engineering/` **ausentes**, e `analyze_ablation_v2_phase3.py:39` ainda aponta para `/home/pedro/desenvolvimento/ivfspea2` |
| Hospedeiros | **PARCIAL** | endpoint regenerável; convergência bloqueada — `src/matlab/lib/PlatEMO/Data` não existe |
| Paisagem, dinâmica, controlador | **PARCIAL** | CSVs presentes; raw em `data/raw/ppsn_dynamics/` existe **só nesta máquina** (`.gitignore:37`); raw do controlador ausente |
| `results/thesis/`, `src/python/thesis/`, `experiments/thesis/` | **VAZIOS** | um `README.md` cada; nenhuma tabela da dissertação tem produtor |

### 2.2 Armadilha de coorte

No CSV consolidado, o rótulo `Algoritmo = IVFSPEA2` carrega **120 identificadores**:
`1–60` **e** `3001–3060`. Nenhuma análise pode ler esse CSV direto; `cohort_filter.py`
é obrigatório. Todos os demais algoritmos têm apenas `1–60`.

### 2.3 Comandos de reconstrução

```bash
.venv/bin/python src/python/analysis/compute_claims_summary.py      # comparação principal
.venv/bin/python src/python/analysis/generate_per_instance_tables.py
make -C paper ppsn-hosts-assets                                     # hospedeiros (endpoint)
.venv/bin/python src/python/fla/test_dynamic_signal.py              # dinâmica (só nesta máquina)
make thesis-tables                                                  # tabelas da dissertação
make thesis-tables-check                                            # falha se houver deriva
```

**Armadilha de ambiente, encontrada na R2.** O install editável do pacote `ivfspea2` no
`.venv` apontava para um worktree antigo em `.claude/worktrees/`, e não para este
checkout: qualquer script com `from ivfspea2...` importava código de outro branch.
Corrigido com `.venv/bin/pip install -e . --no-deps`, que reescreve só o registro de
caminho e não toca em dependência alguma — importante, porque o matplotlib está fixado
em 3.10.8 e reinstalá-lo reescreveria todos os PDFs versionados. Confirmar
`.venv/bin/python -c "import ivfspea2; print(ivfspea2.__file__)"` antes de suspeitar dos
dados.

Sem comando de reconstrução: tuning, ablação, engenharia e o controlador. O Cap. VII
e a seção do controlador no Cap. IX devem declarar essa condição, e o Apêndice B deve
dizer de qual depósito o bruto se recupera.

---

## 3. Fonte da verdade por capítulo

### 3.0 Protocolo por família

As linhas de afirmação abaixo referenciam esta tabela em vez de repetir o protocolo.

| Família | Coorte | n | Correção | Métricas | Ambiente registrado (`OQ-15`) | `id_fonte` |
|---|---|---|---|---|---|---|
| `CONF` comparação principal | IVF `3001–3060` × SPEA2 `1–60`, 51 instâncias, FE = 100 000, N = 100 | 60 | Holm, por `M` e por métrica | IGD primária (menor melhor), HV secundária obrigatória (maior melhor) | Springer: "24.2.0.2923080", formato de versão do MATLAB (R2024b) | `memetic-computing-v2-confirmatory` |
| `SUP` tuning e ablação | subconjunto de 12 problemas, FE = 50 000 (tuning); 51 instâncias, FE = 100 000, na **configuração inicial não ajustada** (ablação, fase final; `OQ-14`) | 30 / 60 | Mann–Whitney + Holm | IGD, HV | Springer: idem | `memetic-computing-tuning-ablation` |
| `ENG` engenharia | RWMOP9, RWMOP21, RWMOP8 | 60 | — | IGD, HV | Springer: idem | `memetic-computing-engineering` |
| `HOST` hospedeiros | IVF/SPEA2 `3001–3030` × SPEA2 `1–30`; IVF/NSGA-II `4001–4030`; IVF/NSGA-III `5001–5030`; 51 instâncias | 30 | Benjamini–Hochberg | IGD, HV | PPSN: MATLAB R2025b + PlatEMO 4.6, incompatível com `CONF` nas execuções `3001–3030` (`OV-01`) | `ppsn-operator-host-compatibility` |
| `DEC` decisão de ativação | 60 execuções para rótulos; 30 pareadas por semente para dinâmica e controlador | 60 / 30 | BH | IGD para rótulos; **HV primária para o controlador** | CLEI: não registrado | `ppsn-clei-landscape-dynamics-controller` |

Divergências de protocolo entre famílias são **reportadas, não harmonizadas**
(`OQ-06`, `OQ-07`, `OQ-08`).

### 3.1 Capítulo VI — Resultados da comparação principal

Artefato: `results/tables/claims_summary_audit.csv`. Produtor:
`src/python/analysis/compute_claims_summary.py`. Família `CONF`.

**Convenção de ordem.** Este documento e as tabelas geradas usam
**vitórias/empates/derrotas (V/E/D)**. Os manuscritos usam vitórias/derrotas/empates.
A mesma linha aparece como `15/7/1` aqui e como `15/1/7` no artigo da Springer. Não é
divergência de evidência; ao transpor um número de manuscrito, reordenar.

| `claim_id` | Enunciado | Valor verificado (V/E/D) |
|---|---|---|
| `C-CONF-01` | IGD, Holm, suíte completa | M=2 **22/3/3** (n=28); M=3 **15/7/1** (n=23) |
| `C-CONF-02` | IGD, Holm, fora do ajuste | M=2 **19/3/2** (n=24); M=3 **12/3/0** (n=15) |
| `C-CONF-03` | HV, Holm, suíte completa | M=2 **22/3/3**; M=3 **17/5/1** |
| `C-CONF-04` | HV, Holm, fora do ajuste | M=2 **19/3/2**; M=3 **11/4/0** |
| `C-MAG-01` | Magnitude em IGD por desfecho corrigido (R13) | todas n=51, sem seleção por significância: Â₁₂ mediano **0,756**, Δ mediano **+1,15%**; vitórias n=37: Â₁₂ mediano **0,804**, 29 com Â₁₂ ≥ 0,71, Δ mediano **+1,27%** (+0,28% a +10,23%); derrotas n=4: Â₁₂ mediano **0,265** (0,101 no WFG2/M3 a 0,344 no WFG9/M2), Δ **−2,21% a −6,41%** (mediana −4,01%). Leitura permitida: as derrotas deslocam a mediana mais que a vitória típica, mas a mediana do seu Â₁₂ fica mais perto de 0,5 que a das vitórias (não cada derrota: WFG2/M3 é mais unilateral que a vitória típica); os resumos condicionados descrevem as instâncias em que a diferença foi detectada. Leitura **proibida**: "custam mais", saldo líquido entre problemas, relevância prática, probabilidade de benefício em problema novo |
| `C-MAG-02` | Magnitude em HV | vitórias n=39: Â₁₂ mediano 0,863, Δ mediano **+0,06%**; derrotas n=4: Δ −0,11% a −0,33% |

Fora do ajuste = 24 + 15 = **39 instâncias**; ajuste = 4 + 8 = **12**; total 51.
Discriminador por instância: coluna `is_full12` de `claims_summary_instance_details.csv`
(102 linhas = 2 métricas × 51 instâncias).

Produtor de `C-MAG-*`: `src/python/thesis/build_tab_magnitude_confirmatoria.py` →
`results/thesis/tab_magnitude_confirmatoria.tex` (Seção `sec:magnitude`). Agrupa as
instâncias pelo `indicator_holm` da auditoria canônica e lê a coorte só por
`filter_submission_synthetic_cohort`.

Limite de generalização em todas as quatro: escopo sintético declarado, mesmo
orçamento, comparação contra SPEA2 canônico. Posicionamento multibaseline entra no
mesmo capítulo em seção **explicitamente rotulada como exploratória**.

### 3.2 Capítulo VII — Configuração, ablação e transferência

| `claim_id` | Enunciado | Valor verificado | Artefato |
|---|---|---|---|
| `C-TUN-01` | O ajuste em três fases promove C26 (`C=0.12, R=0.225, M=0.3, V=0.1, Cycles=2`) | C26 × A43 = 0/12/0 | `results/tuning_ivfspea2v2/` |
| `C-ABL-01` | Na configuração inicial não ajustada, a variante com as duas decisões supera o SPEA2 canônico | IGD **25/25/1**; HV **28/21/2** | `results/ablation_v2/phase3/phase3_summary.json` |
| `C-ABL-02` | Na configuração inicial não ajustada, a variante com as duas decisões não se distingue da formulação sem elas | IGD e HV **0/50/1** | idem |
| `C-ABL-03` | Na fase fatorial, as 16 combinações não se distinguem entre si | Friedman p = **0,485**; a variante com as duas decisões tem o melhor posto médio | `results/ablation_v2/phase2/phase2_summary.json` |
| `C-ENG-01` | RWMOP9 | IGD **8/0/0**; HV **5/0/3** | `results/engineering_suite/engineering_suite_pairwise_main.csv` |
| `C-ENG-02` | RWMOP21 | IGD e HV **3/2/3** | idem |
| `C-ENG-03` | RWMOP8 | IGD e HV **1/1/5** | idem |
| `C-ENG-04` | IVF/SPEA2 × SPEA2 (hospedeiro), por problema | RWMOP9: vitória em IGD (p = 0,0018; Holm 0,005; Δ +1,17%) e em HV (p = 0,0035; Holm 0,010; Δ +0,01%); RWMOP21 e RWMOP8: empate nos dois | `results/engineering_suite/engineering_suite_summary_main.csv` |

`C-ABL-*` é a linha que a §1.3 reenquadra: escrever pelo mecanismo ausente, nunca por
rótulo de versão — e declarar a configuração em que a ablação rodou (`OQ-14`).
`C-ENG-01..03` são **posicionamento** entre nove algoritmos, de resultados mistos;
`C-ENG-04` é a comparação com o hospedeiro, a única que responde à QP1 fora da suíte
sintética (`OQ-17`). O `RWMOP8` tem cobertura heterogênea de execuções válidas
(SPEA2+SDE 18/60, MOEA/D 0/60), e por isso a sua contagem soma sete comparadores.

Nenhuma dessas linhas tem produtor executável neste checkout. O capítulo declara isso.

### 3.3 Capítulo VIII — Compatibilidade operador–hospedeiro

Artefato: `results/tables/hosts_summary.tex` (+ `hosts_a12_summary.tex`,
`hosts_geometry_summary.tex`, `hosts_rep_endpoint_igd.tex`). Família `HOST`.

| `claim_id` | Enunciado | Valor verificado |
|---|---|---|
| `C-HOST-01` | IVF/SPEA2 × SPEA2 | IGD 21/5/2 (M=2) + 12/10/1 (M=3) = **33/15/3**; HV 21/4/3 + 16/6/1 = **37/10/4** |
| `C-HOST-02` | IVF/NSGA-III × NSGA-III | IGD 18/10/0 + 4/19/0 = **22/29/0**; HV 15/12/1 + 6/16/1 = **21/28/2** |
| `C-HOST-03` | IVF/NSGA-II × NSGA-II | IGD 1/25/2 + 0/23/0 = **1/48/2**; HV 4/21/3 + 1/22/0 = **5/43/3** |
| `C-HOST-04` | Estratificação por geometria da fronteira | regular n = 40, irregular n = 11, de `config/hosts_front_geometry.csv` |
| `C-HOST-05` | Estratificação por suíte (R9; descritiva, sem teste de interação) | IGD: IVF/SPEA2 WFG **9/6/3** × demais 24/9/0, Â₁₂ mediano 0,644 × 0,769; IVF/NSGA-III WFG **3/15/0** × demais 19/14/0, Â₁₂ 0,537 × 0,687. HV: todas as derrotas dos dois acoplamentos na WFG (4 e 2); menor taxa de vitória do IVF/NSGA-III em HV é a da ZDT (1/4/0), WFG em seguida (5/11/2), Â₁₂ WFG 0,439. IVF/NSGA-II **não segue o padrão**: única vitória em IGD e 4 das 5 vitórias em HV na WFG. Produtor: `build_tab_hosts.py` → `results/thesis/tab_hosts_suite.tex`, que falha se as somas por suíte divergirem de `C-HOST-01..03` ou se a orientação do Â₁₂ não reproduzir `median_a12_ivf` de `hosts_geometry_summary.csv` |
| `C-HOST-06` | Pareamento da família (R9) | Os pares NSGA compartilham a faixa com o hospedeiro e são pareados por execução: os quatro `hosts_ivfnsga*_{igd,hv}_stats.csv` reproduzem o Wilcoxon por identificador, com 30 pares por instância. O par IVF/SPEA2 (`3001–3030` × `1–30`) é **alinhado por ordem**, como declara o PPSN (`paper/ppsn2026-ivf-hosts/main.tex:142-143`). Sem pareamento (Mann–Whitney + BH): IGD **33/15/3**, igual; HV **38/9/4**, uma mudança (DTLZ4, M = 3, empate → vitória); por suíte, só a DTLZ em HV muda, e a WFG fica em 9/6/3 e 10/4/4. As 408 decisões recomputadas de `data/processed/hosts_paper.csv` coincidem com o depósito congelado `artifact/ppsn2026-ivf-hosts-rev1/tables/hosts_pairing_robustness.csv`. Produtor: `build_tab_hosts.py`, que chama `compute_hosts_pairing_robustness.build_rows` e falha se a recomputação não reproduzir os CSVs que as tabelas contam |
| `C-HOST-07` | Configuração e ajuste dos pipelines (R13) | IVF/SPEA2: C26, calibrada em 12 das 51 instâncias com 50.000 avaliações. IVF/NSGA-II: `R=0.5, C=0.07, Cycles=5`; IVF/NSGA-III: `ivf_rate=0.10, C=0.10, Cycles=5` (`experiments/run_ivfnsgaii_submission.m`, `run_ivfnsgaiii_submission.m`), fixos, sem registro de ajuste nesta suíte. Os valores do NSGA-II pertencem à grade de Sampaio e Camilo-Junior (2017), mas não são as configurações vencedoras relatadas; os cinco ciclos do NSGA-III divergem dos três (sem *steady state*) do experimento ampliado da tese de 2024. Leitura permitida: o esforço de ajuste não foi demonstrado como simétrico. Leitura **proibida**: "configuração canônica publicada", "nenhum pipeline NSGA foi calibrado" (as publicações de origem exploraram parâmetros) | runners e classes MATLAB; `results/tuning_ivfspea2v2/`; `references/ivfnsga2.pdf`; tese de Sampaio (2024), §4.7 |

O capítulo **abre** declarando `OV-01`. A subseção de convergência reporta **apenas** o
que o artefato de 10 checkpoints sustenta, e declara `OQ-02`, `OQ-03` e `OQ-04` como
limitação explícita.

### 3.4 Capítulo IX — Quando ativar o operador

Família `DEC`. Fonte editorial: `paper/clei2026/`.

| `claim_id` | Enunciado | Valor verificado | Artefato |
|---|---|---|---|
| `C-FLA-01` | Descritores estáticos de paisagem ordenam o ganho esperado com sinal moderado | r_s = 0,374 (p = 0,0068), R² = 0,160; deixa-uma-família 0,380 | `results/tables/fla_model_comparison.csv` |
| `C-FLA-02` | A classificação binária não generaliza entre famílias de problemas | LOOCV: floresta 0,527, logística 0,728, SVC 0,690; deixa-uma-família cai a 0,439–0,488 | idem |
| `C-DYN-01` | A renovação média do arquivo nos primeiros 20% das gerações separa as classes | q_BH = 0,013; Â₁₂ = 0,849; medianas 0,250 e 0,209 | `results/tables/dynamic_signal_main_tests.csv` |
| `C-DYN-02` | Regra de limiar único; em cada dobra da deixa-uma-família o limiar é ajustado **sem** a família retida | LOOCV BA 0,691 / MCC 0,311; deixa-uma-família BA **0,754** / MCC 0,413; limiares por dobra 0,216 (DTLZ, MaF ou ZDT retida) e 0,248 (WFG retida) | `results/tables/dynamic_signal_{loocv,lofo}.csv` |
| `C-CTRL-01` | O controlador contra o SPEA2, em HV | **34/14/3** em 51 casos | `results/tables/controller_wtl_oos_20260326_221909.csv` |
| `C-CTRL-02` | O controlador contra o IVF/SPEA2 sempre ativo, em HV | **2/40/9** (iguala ou supera em 42/51): saldo desfavorável | idem |
| `C-CTRL-03` | Decomposição pelo rótulo de três classes, em HV | contra o sempre ativo: ajuda 0/32/9, neutro 0/6/0, prejudica 2/2/0; contra o SPEA2, nas quatro em que o operador prejudica: 0/1/3 | `results/thesis/tab_controlador_wtl.tex`, recalculado de `ppsn_controller_comparison_oos_20260326_221909.csv` e `fla_response.csv`; o gerador falha se não reproduzir as três linhas congeladas |
| `C-CTRL-04` | Onde o limiar age | todas as diferenças em HV contra o sempre ativo estão na WFG (2/7/9; fora dela 0/33/0); a renovação inicial mediana fica abaixo do limiar aplicado nas 18 instâncias WFG e, fora delas, só em DTLZ6 (M = 2 e 3); mediana por suíte 0,215 na WFG contra 0,244–0,342 nas demais | `data/processed/dynamic_signal_test.csv`, `results/tables/dynamic_signal_lofo.csv` |
| `C-DYN-03` | A regra de limiar aberta por suíte (R9; descritiva) | 8 dos 10 `NOT_HELPS` são WFG; a WFG tem a menor renovação inicial mediana nas execuções do IVF/SPEA2 (0,215) e do SPEA2 (0,222); os limiares deixa-uma-família desligam o operador nas 18 instâncias WFG e, fora dela, só em DTLZ6 (M = 2 e 3, ambos `HELPS`); decisões da regra = partição "desligar na WFG e só nela" em **49/51**; toda decisão correta da regra é também correta na partição. Leitura permitida: a amostra não separa renovação de suíte, e BA 0,754 não mede discriminação dentro de uma suíte. Leitura **proibida**: "a renovação é só um marcador de suíte" | `results/thesis/tab_dinamica_suite.tex`, produzida por `build_tab_fla_dinamica.py` a partir de `dynamic_signal_test.csv` e `dynamic_signal_lofo.csv`; o gerador falha se tp/tn/fp/fn não reproduzirem o artefato LOFO (29/8/2/12) ou se alguma decisão correta da regra não for correta na partição. Passa a ser também o produtor de `C-CTRL-04` |
| `C-DYN-04` | Partição WFG/demais como referência retrospectiva (R13) | aplicada aos 51 rótulos, sem ajuste: BA **0,778**, MCC **0,462** (tp 31, tn 8, fp 2, fn 10), contra BA 0,754 da regra de renovação; as duas discordâncias são DTLZ6 M = 2 e M = 3. Formulada depois de observada a concentração dos `NOT_HELPS` na WFG. Leitura permitida: nesta amostra, a regra de renovação não discrimina melhor que a identidade da suíte. Leitura **proibida**: partição como controlador validado ou superior fora da amostra | `results/thesis/tab_ativacao_robustez.tex`, produzida por `build_tab_ativacao_robustez.py` (`wfg_partition_posthoc`) a partir de `dynamic_signal_test.csv` |
| `C-WFG-01` | Exploração descritiva da WFG (R13; pós-hoc) | Holm da família completa, sem recorreção: IGD WFG **3/3/3** com M = 2 e **5/3/1** com M = 3; WFG3 e WFG9 passam de derrota (M = 2, D = 11, K = 1) a vitória (M = 3, D = 12, K = 2), L = 10 nos dois; WFG9/M2 e WFG2/M3 são instâncias da calibração. Por separabilidade (Huband et al., 2006, tabela de propriedades): separáveis WFG1, 4, 5, 7 com IGD 3/1/0 e 3/1/0; não separáveis WFG2, 3, 6, 8, 9 com 0/2/3 e 2/2/1. Leitura permitida: restringe a hipótese; vitórias em funções multimodal (WFG4), enganosa (WFG5) e com viés dependente de parâmetro (WFG7) excluem explicações deterministas simples por essas propriedades isoladas. Leitura **proibida**: "a não separabilidade é a candidata que sobra", 18 configurações como 18 funções independentes, reversão atribuída só a M | `results/thesis/tab_wfg_exploratoria.tex`, produzida por `build_tab_wfg_exploratoria.py` a partir de `claims_summary_instance_details.csv`, `igd_per_instance_M{2,3}.csv` e `config/wfg_properties.csv`; o gerador falha se D divergir de 11/12 ou se L diferir entre as configurações |
| `C-SYN-01` | Concentração de resultados menos favoráveis na WFG (Cap. VIII, `sec:padrao_familias`) | **Hipótese, não conclusão.** A WFG já concentra as derrotas corrigidas na família da comparação principal (`C-CONF-01`); a recorrência como suíte de menor taxa de vitória em IGD do IVF/SPEA2 e do IVF/NSGA-III (`C-HOST-05`) e em 8 dos 10 `NOT_HELPS` (`C-DYN-03`) não é replicação: para o IVF/SPEA2 as famílias leem a mesma coorte (`OV-01`, `OV-02`). Das duas colunas com execuções novas, só a do IVF/NSGA-III repete o padrão, e compara pipelines; o IVF/NSGA-II é contraexemplo declarado e concentra na WFG diferenças nos dois sentidos (1 das 2 derrotas em IGD, 2 das 3 em HV). `C-WFG-01` restringe a hipótese. A WFG também reúne 8 vitórias corrigidas em 18 configurações. Leitura **proibida** (R13): "regularidade que nenhuma família formula sozinha", "marcador das instâncias desfavoráveis", "todas as derrotas em IGD" do IVF/NSGA-III (não há nenhuma), "só o IVF/NSGA-III acrescenta execuções". Teste proposto: desenho fatorial sobre as transformações da WFG com M e K/L controlados (`sec:fw_isolar`) | composição de `C-CONF-01`, `C-HOST-05`, `C-DYN-03`, `C-WFG-01` |

**Fonte proibida para este capítulo:** `data/processed/classifier_comparison.csv`.
A linha da regra de limiar sob `LOOCV` ali é um ajuste dentro da amostra, não uma
estimativa validada — ver `OQ-13`. Os artefatos acima são os que se sustentam.

Rótulos: **41 HELPS / 10 NOT_HELPS**. O capítulo **abre** declarando `OV-02`: os rótulos
derivam da comparação em IGD da coorte da comparação principal **sem correção de multiplicidade**
(`src/python/fla/compute_response.py:16`: Mann–Whitney p < 0,05 e Â₁₂ > 0,56), o que põe
entre os HELPS quatro empates de Holm (WFG1 M = 2; DTLZ4, DTLZ7 e WFG8 M = 3), e não
constituem desfecho independente — por isso o desfecho primário declarado do controlador é
HV, não IGD.

`C-DYN-01` é a linha atingida por `OQ-01`; usar os valores do CLEI, que reproduzem.

`C-CTRL-02` mudou de enquadramento na R8: a contagem 42/51 continua certa, mas o texto a
lê pelo saldo contra o operador sempre ativo (2/40/9), e não pela proteção nas instâncias
`NOT_HELPS`. A Discussão anterior dizia que o controlador "elimina as perdas" sem o
qualificador "contra o IVF sempre ativo"; nas quatro instâncias em que o operador
prejudica, o controlador continua a perder para o SPEA2 em três.

### 3.5 Afirmações bloqueadas

| `claim_id` | Enunciado pretendido | Bloqueio |
|---|---|---|
| `C-CONV-01` | Trajetórias em 100 checkpoints, 6 instâncias | `OQ-02` — o artefato tem 10 checkpoints |
| `C-CONV-02` | 64 de 108 testes pareados significativos após BH | `OQ-03`, `OQ-04` — o par IVF/SPEA2 × SPEA2 não existe no artefato |

Não entram no texto enquanto a questão correspondente estiver aberta.

---

## 4. Questões abertas

**Regra:** nenhuma afirmação vai ao texto final enquanto depender de uma questão
`ABERTA` ou `BLOQUEADA`. Estas não se resolvem por decisão editorial.

| id | Questão | Árbitro | Situação |
|---|---|---|---|
| `OQ-01` | Turnover em WFG: CLEI (0,218 / 0,196) × PPSN-dinâmica (0,225 / 0,237) | `dynamic_signal_test.csv`, `early_frac = 0.2`, subconjunto WFG (n = 18) | **Verificado:** HELPS n = 10 média **0,2180**; NOT_HELPS n = 8 média **0,1960**. Reproduz o CLEI exatamente. O par do PPSN não reproduz em nenhum `early_frac` e inverte a ordenação. Mitigado pela escolha de fontes; risco de errata em manuscrito submetido → **ESCALAR** |
| `OQ-02` | 100 × 10 checkpoints | `hosts_convergence.csv` | **Verificado:** 91 800 linhas = 6 algoritmos × 51 instâncias × 30 execuções × **10** checkpoints; todas as 9 180 execuções têm exatamente 10. `docs/PLAN_CONVERGENCE_RIGOR.md:12` e `docs/MERGE_DIAGNOSTIC_REPORT.md:7` ainda descrevem a coorte aposentada → **BLOQUEADA** |
| `OQ-03` | Par IVF/SPEA2 × SPEA2 ausente das estatísticas de convergência | `test_convergence_significance.py` | **Verificado:** o teste pareia por identificador; IVF/SPEA2 é `3001–3030` e SPEA2 é `1–30`, interseção vazia, par descartado **sem aviso**. `convergence_significance.csv` tem 612 linhas = 51 × **2** pares × 6 métricas, só NSGA-II e NSGA-III. Os pares NSGA funcionam porque hospedeiro e variante compartilham a faixa → **ABERTA, decisão do autor** |
| `OQ-04` | "64/108" e "30 de 540 run-pairs" do Springer | `merge_diagnostic.csv` | Não reprodutíveis neste checkout → **BLOQUEADA** |
| `OQ-05` | Deriva de símbolos: `c,r,ℓ,m,v` (Springer) × `C,R,Cycles,M,V` (canônico) | perfil §5 | **RESOLVIDA na R3, contra a letra do perfil.** O canônico usa `M` para a fração de mães mutadas, mas `M` é o número de objetivos em toda tabela da dissertação — a colisão é ambígua. O texto adota os símbolos em minúscula ($c$, $r$, $\ell$, $m$, $v$) e a Tabela 4.1 publica a correspondência com os identificadores de implementação. Perfil §5 emendado |
| `OQ-06` | Execuções 60 (`CONF`) × 30 (`HOST`) × 60 e 30 (`DEC`) | §3.0 | **RESOLVIDA:** reportar por família, nunca agrupar |
| `OQ-07` | PlatEMO 24.2.0.2923080 × 4.6 | §3.0 | **RESOLVIDA:** declarar por família |
| `OQ-08` | Holm (`CONF`, `SUP`) × BH (`HOST`, `DEC`) | §3.0 | **RESOLVIDA:** declarar por capítulo; não harmonizar retroativamente |
| `OQ-09` | Identidade de release: a tag `submission-snapshot-2026-03` nunca foi criada; `bib/modelo-tese.bib#ivfspea2github` aponta para `pedsanches/IVF-SPEA2`, remoto errado, com autoria divergente de `main.tex:21` | `docs/RELEASE_IDENTITY.md` | **ABERTA:** a dissertação deve citar o DOI Zenodo `10.5281/zenodo.20672828` |
| `OQ-10` | Autoria: manuscritos com 5, 4 e 3 autores; dissertação individual | perfil §10 | **ABERTA, decisão do autor e do orientador:** declaração de contribuição e permissões de reúso de texto e figuras |
| `OQ-12` | `rwmop9_m2` é o 52º caso de `dynamic_signal_test.csv` e não tem `response_label` | `dynamic_signal_test.csv` | **Verificado e RESOLVIDA:** todas as contagens são sobre 51 casos rotulados; documentar a exclusão |
| `OQ-13` | A linha `Early-turnover threshold / LOOCV` de `data/processed/classifier_comparison.csv` reporta BA 0,791 e MCC 0,467, onde o CLEI (`main.tex:530`) reporta 0,691 e 0,311 | `dynamic_signal_loocv.csv` × `compute_classifier_comparison.py:164` | **Verificado. O manuscrito está certo; o CSV está mal rotulado.** `compute_classifier_comparison.py` chama `fit_best_threshold` sobre o quadro inteiro e grava o resultado como se fosse validação cruzada: é um ajuste dentro da amostra. O valor inflado inverte a ordenação que o CLEI argumenta em `main.tex:548-549` (deixa-uma-família acima de deixa-uma-instância). `dynamic_signal_loocv.csv` traz a estimativa genuína, 0,691/0,311, idêntica ao manuscrito. Esse CSV alimenta `fig7_classifier_comparison.pdf`, figura do CLEI → **ESCALAR:** verificar se a figura publicada exibe o valor inflado |
| `OQ-14` | A ablação não testa a configuração promovida | `scripts/experiments/run_ablation_v2_phase3_batch_common.m:81,94-98`; `src/python/analysis/analyze_ablation_v2_phase3.py:47-50`; `sn-article.tex:566` | **Verificado.** A fase final rodou com `c=0.11, r=0.10, m=0, v=0, ℓ=3` (a configuração inicial não ajustada), 60 execuções `300001–300060`. O braço "sem as duas decisões" são as execuções históricas `IVFSPEA2` `1–60` da base consolidada: outra campanha, sem pareamento por semente, com configuração não registrada no artefato. A dissertação chamava a variante de "acoplamento completo" e não declarava a configuração; o Springer declara (o vencedor fatorial foi o ponto de partida da calibração), logo **não há risco de errata no artigo**. **Texto RESOLVIDO na R8** (nota da Tabela de ablação; Caps. I, VII, VIII, IX e X). **Lacuna de evidência ABERTA**: fechá-la exige nova campanha, recusada pela decisão 6 |
| `OQ-15` | Versão da plataforma | `sn-article.tex:285`; `src/matlab/lib/PlatEMO/VENDOR.md:9`; `paper/ppsn2026-ivf-hosts/main.tex:134`; `docs/REPRODUCIBILITY_ENVIRONMENT.md:128`; logs MATLAB (ausentes) | **Texto da dissertação corrigido na R10; ABERTA quanto aos manuscritos.** "24.2.0.2923080" tem o formato do número de versão do **MATLAB** (24.2 = R2024b), e não do PlatEMO. A cópia vendorizada do PlatEMO é identificada como 4.6 em `VENDOR.md:9`, por inferência a partir do README e sem SHA; a versão executada em cada campanha **permanece por confirmar**, porque os logs não estão no checkout. O PPSN registra MATLAB R2025b e PlatEMO 4.6 para a família `HOST`, o que é incompatível com o registro do Springer nas execuções `3001–3030` e `1–30` (`OV-01`); o CLEI não registra versão. A dissertação deixou de afirmar qualquer versão de campanha: a §5.1 diz o que a cópia distribuída é, a nota da Tabela 5.1 remete à §9.4, e a §9.4 ("O ambiente de execução não é verificável") expõe os três registros e a incompatibilidade. Pendente, sem afirmação falsa no texto: localizar os logs dos runners, que imprimem `version`, e decidir errata do Springer (legenda da tabela de parâmetros) e do PPSN (ambiente da coluna IVF/SPEA2) |
| `OQ-16` | Leitura da validação deixa-uma-família | `src/python/fla/test_dynamic_signal.py:739-750`; `dynamic_signal_lofo.csv`; CLEI `main.tex:548-550, 620-624` | **Verificado.** Cada dobra ajusta o limiar **sem** a família retida, de modo que 0,754 é uma estimativa fora da família, e o ajuste não depende de conhecer a família da instância. A dissertação afirmava o contrário ("pressupõe conhecer a família"), herdando o CLEI, que também atribui a vantagem sobre a LOOCV ao reajuste por família. **Texto RESOLVIDO na R8**: a ordem entre as duas validações deixou de ser interpretada (10 negativos em 51). Na R10, a divergência passou a ser **declarada** no texto (§7.4, com citação do CLEI). Números inalterados; a divergência é de **leitura** com o CLEI → decisão do autor sobre revisar o manuscrito, se ainda houver oportunidade |
| `OQ-17` | "Transferência mista" confundia hospedeiro e posicionamento | `engineering_suite_summary_main.csv` | **Verificado e RESOLVIDA na R8.** Os "resultados mistos" são o posicionamento contra oito comparadores; contra o SPEA2 o registro é 1/2/0, e a vitória do RWMOP9 sobrevive a Holm entre os três problemas. O Springer não afirma o contrário; a confusão estava na dissertação |
| `OQ-18` | Limiar do controlador congelado | `IVFSPEA2V2CTRLTRACE.m:7,21`; `experiments/run_ppsn_controller.m:47`; `experiments/launch_ppsn_controller_oos_lofo_parallel.sh:24-25,101-103` | **Verificado por cadeia de proveniência.** O padrão `TurnoverThreshold = 0.232437` da classe **não** produziu o artefato OOS: os lançadores passam 0,2158 (lotes A e B) e 0,2479 (lote C, WFG) por `CTRL_TURNOVER_THRESHOLD`, e a raiz de saída `controller_oos_lofo_parallel_20260326_221909` coincide com o nome do artefato congelado. Logs e bruto do controlador não estão no checkout: a verificação é de proveniência, não de reexecução. O padrão da classe é resíduo de uma rodada anterior e pode confundir quem ler o código |
| `OQ-19` | Leitura do sinal de renovação como regra de decisão binária | `results/thesis/tab_dinamica_suite.tex` (`C-DYN-03`); CLEI `main.tex:42-53`, `572-581`, `710-714` | **Verificado na R9.** Os números do CLEI se mantêm (BA 0,754 deixa-uma-família). O CLEI já reconhece que o sinal depende da família e que, na WFG, a separação é mais fraca (`main.tex:577-581`: Â₁₂ 0,775, p = 0,055), mas não registra que as decisões da regra coincidem com a partição "desligar na WFG e só nela" em 49 das 51 instâncias, nem que toda decisão correta da regra é também correta nessa partição; o resumo e a conclusão apresentam a dinâmica inicial como mais acionável para a decisão binária. A dissertação passou a ler o 0,754 como separação entre a WFG e as demais suítes, e não como capacidade de distinguir instâncias de uma mesma suíte (Caps. VII, VIII e IX); na R10, a divergência passou a ser declarada no texto (§7.4). Divergência de **leitura**, não de número → decisão do autor sobre revisar o manuscrito, como em `OQ-16` |
| `OQ-20` | "Wilcoxon pareado" descrevia mal o par IVF/SPEA2 na família de hospedeiros | `src/python/analysis/compute_hosts_tables.py:142-165`; `compute_hosts_pairing_robustness.py`; PPSN `main.tex:142-143`; `data-sources.toml` (fonte de hospedeiros, `notes`) | **Verificado e RESOLVIDA na R9.** `compute_hosts_tables.py` alinha as execuções pela ordem dos identificadores. Nos pares NSGA isso coincide com o pareamento por semente; no par IVF/SPEA2 as faixas não se intersectam e o alinhamento é arbitrário. O artigo declara o tratamento; a nota das tabelas da dissertação dizia apenas "Wilcoxon pareado". As notas agora declaram o pareamento por par e a sensibilidade sem pareamento (`C-HOST-06`), e a §7.3 ganhou a terceira ressalva. Nenhum número muda. Sem risco de errata no artigo |
| `OQ-21` | MaF: uso e duplicata do DTLZ7 | `src/matlab/lib/PlatEMO/Problems/Multi-objective optimization/MaF/MaF7.m`; `.../DTLZ/DTLZ7.m`; `sn-article.tex:345`; `results/tables/claims_summary_instance_details.csv` | **Verificado na R10.** (i) A MaF entra com M = 2 **e** M = 3 (MaF1–MaF7 nos dois); o Springer (`sn-article.tex:345`) e a dissertação diziam "configurações tri-objetivo". (ii) Na plataforma, `MaF7` tem `CalObj`, `GetOptimum` e padrões idênticos aos do `DTLZ7`: as 51 instâncias são 49 funções, e as execuções dos dois são réplicas independentes (valores diferentes execução a execução). (iii) O DTLZ7 com M = 3 integra a calibração e o MaF7 com M = 3 está no recorte fora do ajuste: sem ele, o recorte com M = 3 fica em IGD 11/3/0 e HV 10/4/0 (Holm). (iv) Com M = 3, os vereditos dos dois divergem (DTLZ7 empate, MaF7 vitória), o que ilustra a sensibilidade de instâncias próximas do limiar. **Texto RESOLVIDO na R10** (§5.2, §5.5, §6.1, §6.3, §8.1, §9.1, notas das Tabelas 6.1 e 6.5). Errata do Springer quanto a (i) e à declaração de (ii) e (iii) → decisão do autor |
| `OQ-22` | Leitura geométrica do manuscrito de origem | preprint `10.21203/rs.3.rs-9431034/v1` (resumo); `sn-article.tex:575` | **Verificado na R10.** O resumo e a discussão do Springer associam o ganho às fronteiras regulares e tomam a compatibilidade geométrica como principal moderador. Na família confirmatória, as taxas de vitória são iguais nos dois grupos (29/40 e 8/11), duas das quatro derrotas são em fronteiras regulares e as duas irregulares são o mesmo problema (WFG2); só a magnitude (Â₁₂ 0,775 contra 0,664) segue a geometria, sem significância. A dissertação declara a divergência (§6.3) e lê a concentração como de suíte. Divergência de **leitura** → decisão do autor sobre errata |
| `OQ-23` | Propriedade do gatilho de ativação | `src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/IVF-SPEA2-V2/IVF_V2.m:27`; `IVFSPEA2V2.m:39-56`; `sn-article.tex:252` | **Verificado na R12.** A regra implementada salta o módulo quando `IVF_Total_FE > ivf_rate * Problem.FE`: o gatilho limita a fração acumulada das avaliações do módulo e fica **mais fácil** de satisfazer depois de uma geração sem ativação; ao fim de cada geração, `FE_IVF` excede `r·FE` no máximo pelo consumo de uma ativação. Simulação exata da regra (N = 100, r = 0,225, 999 gerações): com 12 avaliações por ativação o módulo nunca é suspenso (fração final 0,120); com 24 em toda ativação é suspenso em 62 gerações, uma a cada 16 a partir da 17ª, 31 em cada metade da execução (fração final 0,225). O Springer afirma que o gatilho "becomes harder to satisfy as the run progresses" e deduz custo amortizado "strictly smaller than ℓ times the baseline"; a dissertação herdara a leitura (§2.3.2, §4.1, §4.5) e acrescentava que a intensificação se concentrava na fase inicial. **Texto corrigido na R12**, com a divergência declarada na §4.1. Divergência de **leitura** → decisão do autor sobre errata |
| `OQ-24` | O laço do hospedeiro do IVF/SPEA2 não é o do SPEA2 da plataforma | `IVF-SPEA2-V2/IVFSPEA2V2.m:46-52`; `SPEA2/SPEA2.m:23-29`; `IVF-SPEA2/IVFSPEA2.m:51-54`; `IVFSPEA2-P2-COMBINED/IVFSPEA2_P2.m:71-75`; `sn-article.tex:206,247` | **Verificado na R12.** Antes do torneio de reprodução, o IVF/SPEA2 recalcula `CalFitness` sobre a população corrente (k = 10 com N = 100); o `SPEA2.m` da plataforma, inalterado desde o commit inicial, usa a aptidão devolvida pela seleção ambiental anterior, calculada sobre a união (k = 14 com 200 indivíduos). As funções de aptidão e de seleção ambiental das duas classes são equivalentes: o `diff` mostra apenas vetorização da dominância, saídas auxiliares e uma invalidação de linhas sem efeito na truncagem. A diferença está no laço, e existe também em gerações sem ativação, o que contradiz "the generation is identical to canonical SPEA2" (`sn-article.tex:247`) e a frase correspondente da dissertação. O pseudocódigo do Springer (`sn-article.tex:206`) calcula a aptidão sobre `P_t` no início da geração, mas o módulo usa a da última seleção ambiental, e é dela que sai `F̄_antes`. A variante da ablação e a implementação versionada da formulação anterior recalculam da mesma forma: a ablação não separa a diferença, nem a comparação confirmatória. Efeito não medido. **Texto declara na R12** (§4.1, Algoritmo 4.1, §4.2.2, §8.2, §8.6, §9.1, §10.1, resumo e abstract). O controle que a fecharia, o SPEA2 com o mesmo recálculo, exige campanha nova (decisão 6) → decisão do autor sobre errata e sobre a campanha |
| `OQ-25` | Configuração dos pipelines NSGA na família `HOST` | `paper/ppsn2026-ivf-hosts/main.tex:148-149`; `experiments/run_ivfnsgaii_submission.m`; `experiments/run_ivfnsgaiii_submission.m`; `references/ivfnsga2.pdf`; tese de Sampaio (2024), §4.7 | **Verificado na R13.** O PPSN afirma que cada pipeline usou "the fixed parameter setting of its cited canonical implementation". Os runners fixam `R=0.5, C=0.07, Cycles=5` (IVF/NSGA-II) e `ivf_rate=0.10, C=0.10, Cycles=5` (IVF/NSGA-III): valores da grade de 2017 que não são as configurações vencedoras relatadas, e cinco ciclos contra três (sem *steady state*) no experimento ampliado de 2024. Não há registro de ajuste nesta suíte equivalente ao do IVF/SPEA2. A dissertação declara a assimetria (`C-HOST-07`; §7.3, §8.3, §9.2) sem alterar números. Divergência de **leitura** com o PPSN → decisão do autor sobre errata |
| `OQ-26` | Anterioridade do protocolo da comparação principal (chamada "confirmatória" até a R14b): escolha da IGD como desfecho primário e delimitação das famílias de Holm (por `M` e por métrica) | `paper/springer-nature/src/sn-article.tex:379,383`; `docs/IVFSPEA2_EVIDENCE_MODEL.md:25-27`; `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_report.md` (Notes); histórico Git; `docs/RELEASE_IDENTITY.md:18` | **Examinada na R14b; anterioridade NÃO VERIFICADA para os dois itens.** (i) IGD: o Springer a declara "the pre-specified primary performance indicator" (`:379`), e o modelo de evidência a fixa como desfecho primário; são declarações dos autores, sem carimbo temporal independente anterior aos resultados. O relatório da calibração prioriza a IGD na promoção da configuração (campo interno `generated_at` 2026-02-28), mas trata da calibração, não da análise confirmatória, e data interna de arquivo não demonstra pré-especificação. (ii) Famílias: o Springer descreve Holm "separately for each objective count" (`:383`), sem declarar anterioridade nem a separação por métrica; nenhum documento fixa a delimitação por `M` e por métrica antes dos resultados. O histórico Git começa em 2026-03-17 (`a07ca76`, "Init Commit", com todo o conteúdo), data posterior à inscrita na etiqueta da campanha `SUB20260228_V2`, e o primeiro depósito Zenodo é da mesma data. **Texto corrigido na R14b**: §5.3 deixou de afirmar a IGD "fixada antes da análise", §9.1 deixou de dizer família "declarada antes da análise", e o Apêndice C, idem; a §5.4 já declarava a ausência de data. A ausência de registro não é evidência de escolha pós-hoc. **Nomenclatura DECIDIDA na R15** (opção c, §1.7): "avaliação comparativa principal"; a decisão trata do nome e do papel, não da cronologia. **Anterioridade: continua NÃO VERIFICADA**; a busca da R14b não foi repetida, e a ausência de registro não indica escolha posterior aos resultados. |

---

## 5. Sobreposição e não independência

| id | Relação | Consequência para o texto |
|---|---|---|
| `OV-01` | Hospedeiros `3001–3030` e `1–30` ⊂ coorte da comparação principal `3001–3060` e `1–60` | a coluna IVF/SPEA2 do Cap. VIII **não replica** o Cap. VI; só `4001–4030` e `5001–5030` acrescentam execuções novas |
| `OV-02` | Coorte de rótulos do Cap. IX ≡ coorte de desfecho do Cap. VI | os rótulos HELPS/NOT_HELPS são **derivados** da comparação principal em IGD, **sem correção** (41 HELPS contra 37 vitórias de Holm), não desfecho independente |
| `OV-03` | `paper/clei2026/` e `paper/ppsn2026/` são uma família em duas saídas editoriais | citar como uma; a dissertação adota o CLEI (`OQ-01`) |
| `OV-04` | 12 problemas de ajuste ⊂ 51 instâncias | só as linhas `Holm_OOS` sustentam contagem fora do ajuste |
| `OV-05` | Controlador e dinâmica compartilham as 30 sementes | HV é o desfecho primário declarado do controlador |
| `OV-06` | RWMOP e as 51 sintéticas | nunca somar; escopos disjuntos |

**Três proibições.** (i) Não somar vitórias, empates e derrotas entre famílias.
(ii) Não descrever os manuscritos como validações independentes. (iii) Toda contagem
declara família, coorte, faixa de execuções, n, correção e direção da métrica
(perfil §8).

---

## 6. Arquitetura-alvo e sequenciamento

### 6.1 Capítulos

| Cap. | Conteúdo | Fonte |
|---|---|---|
| I | Introdução; contribuições reescritas; roteiro cobrindo todos os capítulos | todas |
| II | Embasamento; acrescentar HV com ponto de referência, correção de multiplicidade, A₁₂ com convenção de orientação (hoje usado e nunca definido), conceitos de análise de paisagem, turnover de arquivo | todas |
| III | Trabalhos relacionados; hoje 12 linhas e 6 obras — expandir para linhagem do IVF, portabilidade operador–hospedeiro, paisagem para MOEAs, controle adaptativo de operadores | `HOST`, `DEC` |
| IV | Proposta: **um** IVF/SPEA2 — seleção de pai dissimilar, continuação coletiva, portão de orçamento, C26, contabilidade de avaliações; tabela de correspondência de símbolos (`OQ-05`) | `CONF` |
| V | Experimentos; protocolo por família conforme §3.0 | todas |
| VI | Resultados confirmatórios; `C-CONF-01..04`; tudo por `\input` de `results/thesis/` | `CONF` |
| VII | Configuração, ablação e transferência; `C-TUN-01`, `C-ABL-01..02`, `C-ENG-01..03` | `SUP`, `ENG` |
| VIII | Compatibilidade operador–hospedeiro; `C-HOST-01..04`; abre com `OV-01` | `HOST` |
| IX | Quando ativar o operador; `C-FLA-01..02`, `C-DYN-01..02`, `C-CTRL-01..02`; abre com `OV-02` | `DEC` |
| X / XI | Discussão / Conclusões; sem agregar famílias | síntese |
| XII | Ameaças à validade; voz de dissertação; **remover** transferência entre hospedeiros das limitações — virou o Cap. VIII — e pôr no lugar a limitação real: a comparação avalia pipelines publicados e não isola causalmente o hospedeiro. Acrescentar `OQ-02`, `OQ-03`, bruto não reprodutível em árvore, execução em máquina única, deriva de versão do PlatEMO | todas |
| XIII | Trabalhos futuros; podar o que já foi feito | — |
| Ap. A | Fontes de evidência e reprodutibilidade; quita `REVISION_PLAN.md` §5 | `data-sources.toml` + §3 |
| Ap. B | Recuperação dos dados brutos ignorados | `docs/RELEASE_IDENTITY.md` |

Toda `\ref{}` precisa de reauditoria depois da renumeração.

**Arquitetura efetiva (R4–R9).** Dez capítulos e três apêndices: I Introdução · II
Embasamento · III Trabalhos relacionados · IV Proposta · V Experimentos · VI Resultados
(QP1, só confirmatório desde a R9) · VII Estudos complementares, uma seção por questão
(QP1 em engenharia, QP2, QP3, QP4) · VIII Discussão e Conclusões, uma resposta por
questão, mais a seção de regularidade entre famílias (`C-SYN-01`, R9) · IX Ameaças · X
Trabalhos futuros · Ap. A, B e C (posicionamento exploratório, retirado do Cap. VI na R9).
A tabela acima é o alvo original, anterior à consolidação da R4.

### 6.2 Rodadas

- **R1 (concluída)** — esta especificação e as emendas da §1.4. Nenhum `.tex` tocado.
- **R2 (concluída) — camada de artefatos.** `ptbr_format.py` e `latex_table.py` mais oito
  geradores em `src/python/thesis/`, produzindo 15 tabelas em `results/thesis/` e
  espelhadas em `thesis/masters/generated/`. A causa-raiz dos erros das tabelas
  importadas era que **nenhum** número do texto vinha de `\input`: todos foram digitados
  à mão. Alvos `make thesis-tables` e `make thesis-tables-check`; a fonte
  `[[source]] thesis-derived-tables` foi declarada por último, porque
  `scripts/validate_data_sources.py` falha se um caminho declarado ainda não existir.
  As tabelas foram compiladas em documento-sonda: zero *overfull* e zero *underfull*.
- **R3 (concluída)** — Caps. IV, V e VI reescritos do zero. As Tabelas 6.1--6.4 importadas
  foram aposentadas; o Cap. VI agora só faz `\input` de `generated/`. O Cap. IV ganhou
  pseudocódigo (`algorithm` e `algpseudocode` acrescentados ao preâmbulo, com palavras-chave
  traduzidas) e a tabela de correspondência de símbolos. O Cap. V passou de 14 para
  ~70 linhas e declara o protocolo das cinco famílias. Dez chaves de citação faltavam no
  `.bib` da dissertação e foram copiadas literalmente do `.bib` do Springer, cuja auditoria
  por chave está em `paper/springer-nature/citation_review.md`. Compilação com zero
  *overfull*, zero referência indefinida e zero citação indefinida.
- **R4 (concluída)** — As três famílias complementares foram consolidadas em **um único**
  capítulo, "Estudos Complementares" (decisão do autor), e não em três. O documento tem
  agora 10 capítulos. O capítulo consome nove das dez tabelas ociosas e declara `OV-01` e
  `OV-02` na abertura das seções correspondentes. A fonte
  `thesis-convergence-reconciliation` **não foi criada**: a análise de convergência foi
  retirada da dissertação por decisão do autor, o que torna `OQ-02` e `OQ-04` inertes para
  o texto. O preâmbulo passou a gerar a Lista de Algoritmos — a classe monta a lista com
  `\listalgorithmcfname`, macro do `algorithm2e`, que precisou ser definida porque o
  documento usa `algorithm`/`algpseudocode`.
- **R5 (concluída)** — Cap. II: as seis contradições com o Cap. IV foram resolvidas por
  enquadramento, e não por deleção. A Seção 2.3 passa a declarar-se explicitamente como a
  **formulação original** do IVF, o que torna legível o contraste do Cap. IV; a taxa de
  execução é apresentada nas duas operacionalizações publicadas (probabilística no
  acoplamento ao NSGA-II, orçamento acumulado nesta dissertação), e o mesmo vale para o
  tamanho da coleta e para o EAR-PA. A colisão do símbolo `F` foi eliminada. Três seções
  novas acrescentam o embasamento que os Caps. V e VI usavam sem definir: indicadores com
  direção e ponto de referência, inferência com Holm × BH e orientação de $A_{12}$, e
  paisagem de aptidão com renovação de arquivo. Cap. III reescrito de 13 para 32 linhas,
  em quatro seções, citando `Sampaio2024` pela primeira vez. Quatro entradas
  bibliográficas acrescentadas.
- **R6 (concluída)** — Caps. I, VIII (Discussão e Conclusões), IX (Ameaças) e X (Trabalhos
  Futuros) reescritos; pré-textuais reescritos por último. Os dois apêndices foram
  escritos e habilitados: o A consome o `apendice_fontes.tex` gerado, e o B documenta a
  distinção entre evidência regenerável e evidência apenas verificável. Bibliografia
  limpa: oito entradas mortas removidas (as triplicatas de Huband, a duplicata de Cheng
  com artefato de prompt no campo `note`, `reference1` duplicando o relatório do SPEA2,
  `reference2`, `pymoo` e duas chaves de template já sem citação), quatro chaves de
  template renomeadas para autor--ano com os seus pontos de citação atualizados, e a
  entrada do repositório corrigida para o remoto real com o DOI de conceito que
  `docs/RELEASE_IDENTITY.md` manda citar por padrão. O gerador do apêndice passou a
  emitir português: os campos de prosa do manifesto estavam sendo impressos em inglês, e
  o identificador da fonte histórica expunha "v1" como título de seção. O gerador agora
  falha se uma fonte declarada não tiver tradução.
- **R7** — figuras e validação final. Regenerar as cinco figuras com fontes Type 3 usando
  `pdf.fonttype = 42` **dentro do `.venv`, com matplotlib 3.10.8**; qualquer outra versão
  reescreve todos os PDFs versionados do repositório.
  **Situação (R8): resolvido por obsolescência.** Nenhum capítulo inclui mais as cinco
  figuras estatísticas legadas: `fig/` só é usado pelos três fluxogramas, que já embutem
  TrueType, e `pdffonts build/main.pdf` não lista fonte Type 3. As cinco figuras continuam
  em `fig/` sem uso; removê-las é limpeza opcional, a critério do autor.
- **R8 (concluída) — questões de pesquisa, sem re-execução.** Decisões 6 e 7 da §1.1 e
  §1.5. O Cap. I ganhou objetivos, questões e contribuições reescritas a partir das
  respostas; o Cap. VI, a seção de magnitude (`C-MAG-*`); o Cap. VII passou a ter uma
  seção por questão, na ordem QP1–QP4; o Cap. VIII responde a uma questão por seção; os
  Caps. IX e X foram sincronizados; resumo e abstract foram derivados das respostas. Um
  gerador novo (`build_tab_magnitude_confirmatoria.py`) e quatro estendidos: engenharia
  com a comparação contra o hospedeiro; controlador com a decomposição em três classes e
  conferência contra o artefato congelado; limiar com os valores por dobra; ablação com a
  configuração e o Friedman da fase fatorial. Leituras corrigidas: `OQ-14`, `OQ-16`,
  `OQ-17`; a afirmação de que as famílias "divergem" quanto à geometria (Conclusões e
  resumo) foi removida, porque contradizia a própria Discussão. Portões
  `thesis-tables-check`, `thesis-doctor`, `verify-release` e `make test` aprovados;
  `make thesis` compila 92 páginas sem aviso LaTeX e sem *overfull*. A inspeção visual
  achou um defeito anterior à R8: o resumo e o abstract ficam numa `minipage` que não
  quebra página, e os textos de HEAD transbordavam — o corpo do resumo caía na página
  seguinte, e as palavras-chave do abstract também. Os dois textos foram reduzidos a
  cerca de 21 linhas e cabem, com as palavras-chave, numa página cada.
- **R9 (concluída) — a regularidade da WFG entre famílias, como hipótese.** Motivada por
  uma auditoria da linha narrativa: a abertura pelo argumento de densidade não sustenta
  conclusão alguma, e a concentração dos casos desfavoráveis na WFG aparecia em três
  famílias sem que o texto a juntasse. Geradores estendidos (`build_tab_hosts.py`,
  `build_tab_fla_dinamica.py`), com duas tabelas novas, `tab_hosts_suite` (`C-HOST-05`) e
  `tab_dinamica_suite` (`C-DYN-03`), ambas com autoverificação contra artefatos;
  `build_tab_hosts.py` também declara e recomputa o pareamento (`C-HOST-06`, `OQ-20`). O
  Cap. VIII ganhou a §8.5, `sec:padrao_familias` (`C-SYN-01`), que formula a regularidade
  como **hipótese**, com quatro ressalvas (sobreposição de coortes, contraexemplo do
  IVF/NSGA-II, renovação e suíte não separáveis nesta amostra, propriedades da WFG não
  separadas); a §8.1.1 foi condensada, e a QP4 e as Conclusões, recalibradas. A leitura da
  regra de renovação mudou (`OQ-19`): as suas decisões coincidem com a partição WFG/demais
  em 49 das 51 instâncias, e o 0,754 não mede discriminação dentro de uma suíte. O
  posicionamento exploratório saiu do Cap. VI para o Apêndice C (`apend:exploratorio`). O
  Cap. II foi corrigido contra Zitzler et al. (2001) e contra `SPEA2.m` e
  `EnvironmentalSelection.m` da plataforma: o texto dizia que o arquivo começa com tamanho
  $N$, que duplicatas são removidas e que o arquivo é completado com dominados do arquivo
  anterior, e calculava a aptidão depois da seleção ambiental; a §2.1.5 passou a contrastar
  a ordenação dos três hospedeiros; a §2.3 deixou de chamar de paralelo um arranjo que a
  §2.2 classifica como integrativo. Os argumentos de projeto das duas decisões passaram a
  ser apresentados como argumentos, e não como fatos (Caps. I, II e IV). Seis entradas
  bibliográficas sem citação foram removidas. Resumo e abstract foram reescritos, e o
  abstract, composto em inglês, e não traduzido. Portões `thesis-tables-check`,
  `thesis-doctor`, `verify-release` e `make test` aprovados; `make thesis` compila 96
  páginas sem aviso LaTeX e sem *overfull*, e as quatro linhas *underfull* são as da R8.
- **R10 (concluída) — correções de fato, de coerência e de fundamentação.** Motivada por
  uma avaliação da dissertação (nota 8,0/10) que listou vinte defeitos verificados contra
  código, artefatos e manuscritos. Fato: a versão de plataforma deixou de ser afirmada
  (`OQ-15`); a MaF passou a constar com M = 2 e 3, e a duplicata MaF7/DTLZ7, com o seu efeito
  sobre o recorte fora do ajuste, foi declarada (`OQ-21`); a Tabela 7.8 passou a dizer que
  exibe 5 dos 18 observáveis testados, e o gerador falha se deixarem de ser os de menor
  valor-p; a regra dos rótulos (sem correção) e a diferença 41 × 37 foram explicitadas
  (`OV-02`); a amplitude do DTLZ4 foi medida (quase nove vezes a mediana); o custo de relógio
  deixou de ser dito "quantificado". Coerência: o critério de continuação dos acoplamentos
  anteriores foi alinhado ao código do IVF/NSGA-II e do IVF/NSGA-III; o protocolo de seleção
  dos RWMOP, ao do Springer (critérios fixados antes, RWMOP8 mantido apesar de adverso); o
  Apêndice C e a §5.4 passaram a dizer a mesma coisa; a conclusão deixou de chamar a vantagem
  de "específica" do SPEA2; a legenda da Tabela 6.5 deixou de negar a concentração de
  derrotas irregulares, que agora é explicada (um único problema). Fundamentação: definições
  de dominância, conjunto e fronteira de Pareto (Cap. I, com `M` para o número de objetivos);
  §3.5 ampliada com controle de parâmetros, seleção adaptativa de operadores e seleção de
  algoritmos; citações de SBX, mutação polinomial, Mann–Whitney e Friedman; §1.4 com os três
  manuscritos derivados, citados onde o texto os invoca, e divergências de leitura
  declaradas no ponto em que ocorrem (§6.3, §7.4; `OQ-22`); referência da IGD nos RWMOP
  descrita (§5.3). Forma: códigos internos (CONF, ENG, SUP, HOST, DEC, HELPS, C26) fora das
  legendas; legendas curtas na Lista de Figuras; vírgula decimal em todas as figuras;
  Figura 6.1 refeita, relativa à mediana do SPEA2 e com vereditos de Holm; contraste do texto
  na Figura 7.2 corrigido. Portões `thesis-tables-check`, `thesis-doctor`, `verify-release`
  e `make test` aprovados; `make thesis` compila 98 páginas sem aviso LaTeX, sem *overfull* e
  sem página de texto só com *floats*.
- **R11 (concluída) — conferência da R10 e correções residuais.** Os vinte defeitos da
  avaliação foram conferidos no texto, nas tabelas e nas figuras regeneradas: catorze
  estavam resolvidos e seis tinham resto. A generalização do critério de continuação
  estendia ao IVF/GDE3, sem fonte, o que só vale para o IVF/NSGA-II e o IVF/NSGA-III (Caps.
  1 e 3). A §5.4, o Cap. 6 e o Apêndice C diziam "sem correção de multiplicidade" de um posto
  médio que não envolve teste. A §9.1 atribuía a execução a "uma versão específica da
  plataforma", que a §9.4 declara não verificável, e a §9.4 dizia que nenhuma contagem
  "depende da versão". A entrada `maturana2009adaptive`, copiada do PPSN-dinâmica, trazia ano
  e autoria errados (Crossref: 2011, seis autores). A §1.4 dizia que a dissertação
  "recalcula" as tabelas, o que só vale para a família confirmatória, e a §3.4 afirmava
  lacuna na literatura sem levantamento. A §6.3 lia "reflete variabilidade, e não
  equivalência", onde o teste só permite "não indica equivalência". Além dos vinte: a
  discordância entre famílias passou a "compatível com" diferença de poder (§8.1.1);
  "Problemas caros" (§10.2) deixou de afirmar a troca como favorável; frases de
  metacomentário foram cortadas (§7.2, §8.2, Apêndice B); o rótulo do eixo da Figura 7.3,
  cortado no PDF, foi encurtado no gerador, e só essa figura mudou na regeneração. Portões
  `thesis-tables-check`, `thesis-doctor`, `verify-release` e `make test` aprovados; `make
  thesis` compila 98 páginas sem aviso LaTeX, sem *overfull* e sem página só com *floats*.
- **R12 (concluída) — calibração da linha argumentativa e dois fatos da proposta.** A pedido do
  autor, depois de uma avaliação que apontou objetivo mais amplo do que a evidência responde,
  mecanismos de projeto afirmados como fatos, ressalvas repetidas e Conclusões que terminavam
  no que falta. Objetivo: "determinar se, por que e em que condições" passou a avaliar
  eficácia, magnitude e instâncias e a investigar atribuição, dependência do hospedeiro e
  decisão de uso (Cap. 1, resumo, abstract, `REVISION_PLAN.md` §2). Fato, contra o código: o
  gatilho limita a fração acumulada e não concentra a intensificação no início (`OQ-23`;
  §2.3.2, §4.1, §4.5); o IVF/SPEA2 recalcula a aptidão antes do torneio, o que o SPEA2 da
  plataforma não faz (`OQ-24`; nova ameaça na §9.1, candidato de atribuição na §8.2, controle
  na §10.1); o critério coletivo passou a definir as duas médias pelo contexto em que são
  calculadas, a declarar que um ciclo sem melhora não é desfeito e a delimitar o que a média
  de F registra; "pai distinto" passou a pai escolhido para cada mãe, com K = min(3, n_c) e
  sorteio de dois candidatos; o Algoritmo 4.1 foi alinhado a `IVF_V2.m`. Calibração: a
  motivação por densidade passou a hipótese de projeto (Caps. 1 e 4); "o ganho não é
  atribuível" passou a "a evidência disponível não permite atribuir"; a WFG passou a marcador
  empírico (§8.5); saíram a afirmação "autolimitante" do critério coletivo, não medida, e a
  conjectura mecanicista da §8.1.1. Desenvolvimento: as Conclusões distinguem eficácia,
  atribuição e decisão de uso e terminam na contribuição; a §8.4 trata o controlador como
  problema de decisão sob custos assimétricos. Enxugamento: os Caps. 6 e 7 deixaram de
  reenunciar respostas às QP (§1.5), e as ressalvas de reprodutibilidade, sobreposição,
  ablação e renovação–suíte ficaram num lugar canônico, com remissão. Nenhum número de
  resultado mudou. Portões `thesis-tables-check`, `thesis-doctor`, `verify-release` e `make
  test` aprovados; `make thesis` compila 98 páginas sem aviso LaTeX, sem *overfull* e sem
  página só com *floats*; resumo e abstract cabem numa página cada.
- **R13 (concluída) — revisão científica da Discussão, sem novas campanhas.** A pedido do
  autor, a partir de um diagnóstico da Discussão (C1–C8, A1–A7), usado como lista de
  problemas e não como fonte. Cap. VIII: títulos das QP alinhados ao Cap. I; QP1 com resumo
  não condicionado (`C-MAG-01`), Â₁₂ e Δ distinguidos e sem leitura de custo; QP2 com o
  orçamento de calibração e a hipótese de densidade como justificativa de projeto; QP3 em
  dois níveis, sem "Sim", com a assimetria de ajuste (`C-HOST-07`, `OQ-25`) e o contraste com
  os estudos de origem conferido nas fontes primárias; QP4 com veredito, três níveis e a
  partição pós-hoc WFG/demais (`C-DYN-04`); §8.5 reescrita como concentração de resultados
  menos favoráveis, restringida por `C-WFG-01`; Conclusões com escopo e remissão ao Cap. IX.
  Dois cálculos novos por gerador (`build_tab_ativacao_robustez.py`, estendido;
  `build_tab_wfg_exploratoria.py`, novo, com `config/wfg_properties.csv` transcrito da tabela
  de propriedades de Huband et al., 2006). Coerência nos Caps. III (linhagem IVF, Zhou,
  Liefooghe), IV (custo), VI (geometria, síntese), VII (hospedeiros, reanálise estática,
  partição, controlador), IX (orçamento de calibração, assimetria de ajuste, tempo,
  protocolos, análises pós-hoc, convergência) e X (hospedeiro, WFG, decisão reversível),
  resumo e abstract (magnitude não condicionada). Nenhum número de resultado preexistente
  mudou. Auditorias independentes quantitativa, científica e fonte→afirmação; achados
  aceitos incorporados. Portões `thesis-tables-check`, `thesis-doctor`, `verify-release` e
  `make test` aprovados; `make thesis` compila 108 páginas sem aviso LaTeX novo, sem
  *overfull*, com as quatro linhas *underfull* da linha de base.
- **R14 (concluída, 2026-10-01) — reenquadramento de QP2 e QP3, sem novas campanhas.**
  Decisão do autor registrada na §1.6. Cap. I: objetivo geral, objetivos específicos 3 e 4,
  QP2 ("Configuração e decisões de acoplamento") e QP3 ("Variação entre acoplamentos") com as
  formulações comparativas, aviso de que não são hipóteses prévias, contribuições 3 e 4
  reescritas pelas comparações registradas. Cap. VII: apresentações da QP2 e da QP3; o
  contraste histórico de calibração passou a declarar que muda formulação e parâmetros
  (texto e nota da Tabela 7.2, pelo gerador `build_tab_tuning_ablacao.py`, que agora falha se
  o braço histórico do artefato não for `IVFSPEA2`); a ordenação entre pipelines passou a
  descritiva; "próximo da neutralidade" do IVF/NSGA-II, no parágrafo sincronizado, deu lugar
  à contagem 1/48/2. Cap. VIII: §8.2 e §8.3 reescritas na ordem resultado → interpretação →
  alcance → questão aberta, com títulos novos e rótulos preservados; Conclusões
  sincronizadas. Caps. IX e X, resumo e abstract: só sincronização. Nenhum número,
  parâmetro, coorte, teste ou correção mudou. Auditorias independentes quantitativa (sem
  divergência numérica) e científica; os dois achados aceitos (síntese da ablação que
  apagava a derrota; "neutralidade") foram incorporados. Portões `thesis-tables-check`,
  `thesis-doctor`, `verify-release` e `make test` aprovados; `make thesis` compila 110
  páginas sem item bloqueante novo, sem *overfull*, com as quatro linhas *underfull* da
  linha de base.
- **R14b (concluída, 2026-10-01) — continuidade após a R14, sem novas campanhas.** (1)
  Conclusões: a frase "As demais questões recebem respostas mais estreitas" deu lugar a
  "A QP2 e a QP3 são comparativas, e as suas respostas têm esse alcance", com os limites de
  atribuição preservados; "perfis observados distintos" no §8.3, nas Conclusões e na
  contribuição 4; as duas ocorrências restantes de "próximo da neutralidade" (§7.3 por suíte,
  §8.5) trocadas por contagens; a Seção 7.3 passou a "Comparação dos acoplamentos com seus
  hospedeiros", com o rótulo `sec:hospedeiros` preservado. (2) QP4: objetivo geral, OE5 e
  enunciado da QP4 passaram a cobrir informação anterior à execução e da dinâmica inicial e a
  nomear o IVF/SPEA2 sempre ativo como comparador; §7.4.3 declara que o controlador usa só a
  renovação inicial do arquivo; resumo e abstract delimitam a conclusão à regra de controle
  avaliada. (3) Cronologia do protocolo examinada (`OQ-26`): sem registro temporal
  independente, o texto descreve o protocolo sem afirmar anterioridade. O rótulo
  "confirmatória" não foi reclassificado. Nenhum número, parâmetro, coorte, teste, correção,
  citação ou rótulo mudou. `make thesis` compila 111 páginas (110 antes; o Cap. 1 cresceu
  uma página) sem item bloqueante novo, sem *overfull*, com as quatro *underfull* da linha
  de base; resumo e abstract cabem numa página cada depois de dois ajustes de extensão.
- **R15 (concluída, 2026-10-01) — nomenclatura da avaliação principal.** Decisão da §1.7
  (opção c de `OQ-26`). Prosa: as ocorrências de "confirmatória", "confirmatório" e
  "confirmatoriamente" nos Caps. 1, 5, 6, 7, 8 e 9, no resumo, no abstract e nos Apêndices B e
  C foram revistas uma a uma e trocadas por "comparação principal", "avaliação comparativa
  principal", "família/coorte da comparação principal" ou "evidência principal"; a Tabela 5.1
  passou a "Comparação principal", papel "Principal". Manifesto: papel `primary`, descrições
  vigentes sincronizadas. Geradores: rótulo de papel e título da fonte no Apêndice A, célula da
  Tabela 6.7 e notas das tabelas de ativação, controlador, dinâmica, geometria, hospedeiros,
  magnitude e WFG, além das docstrings que definem a avaliação. Nenhum número, coorte, teste,
  correção, parâmetro, rótulo, id de fonte ou nome de arquivo mudou; os manuscritos e os
  artefatos congelados não foram tocados.
- **R17 (concluída, 2026-10-03) — ocultação dos apêndices e promoção do posicionamento a
  QP5.** Decisões do autor: (a) apêndices A, B e C ocultados por enquanto, com os arquivos
  versionados em `pos/`; (b) QP5 comparativa, não afirmação de superioridade; (c) correção
  de Holm por comparador, por número de objetivos e por métrica; (d) defesa da escolha do
  hospedeiro limitada às fontes já citadas; (e) restauração dos apêndices só a pedido do
  autor. `main.tex` comenta `\apendices` e os três `\input`, com bloco de comentário que
  registra motivo, permanência dos arquivos e comando de restauração; nada foi renomeado,
  movido ou apagado, e `build_apendice_fontes.py`, `data-sources.toml` e o manifesto seguem
  produzindo normalmente. Remissões: `cap_III.tex:25`, `cap_V.tex:49`, `cap_VI.tex:4` e
  `cap_VII.tex:15` passaram a `Seção~\ref{sec:posicionamento}`; os parênteses de
  `(Apêndice~\ref{apend:recuperacao})` saíram de `cap_VII_complementares.tex:6` e
  `cap_VIII.tex:61`; a ORGANIZAÇÃO (`cap_I.tex:85`) deixou de anunciar os apêndices. Nova
  família de evidência na Tabela 5.1, com a sobreposição de coorte e o intervalo de anos dos
  comparadores (2002--2023) declarados na nota. Gerador novo
  `src/python/thesis/build_tab_posicionamento.py`, registrado em `build_all.py`, que reprocessa
  `todas_metricas_consolidado_with_modern.csv` pelo filtro de coorte e proíbe o reuso de
  `pairwise_ivf_vs_all.csv`, `pairwise_ivf_vs_all_hv.csv` e
  `pairwise_vs_spea2_with_modern*.csv` (rótulo misto do IVF/SPEA2, sem correção de
  multiplicidade); o pipeline foi validado por reprodução exata das contagens canônicas da
  Tabela 6.1. Texto: QP5 no Cap. 1 (objetivo geral, objetivo específico 6, "cinco questões",
  contribuição 6, roteiro, aviso de formulação posterior aos estudos), §7.5 no Cap. 7
  (figura `fig:posto_medio` migrada do Apêndice C), §8.5 no Cap. 8 (WFG passa a §8.6,
  Conclusões a §8.7), §5.1 e §5.4 no Cap. 5, justificativa do hospedeiro em `cap_I.tex:28`,
  §3.3 do Cap. 3, item de ameaça no Cap. 9 e §10.2, resumo e abstract. Nenhum rótulo, citação
  ou chave de bibliografia mudou.

  **Fechamento da R17 (2026-10-03), lote corretivo.** (A1) Vocabulário único: *derrota* é a
  instância com diferença corrigida desfavorável; *saldo desfavorável* é o contraste
  (comparador × M × métrica) com mais derrotas que vitórias. São quatro em 28: NSGA-III e
  AR-MOEA em IGD com M = 2; SPEA2+SDE e AGE-MOEA-II em HV com M = 3. §7.5 define os dois
  termos; §8.5, Conclusões, contribuição 6, item de ameaça da §9.4, §10.2 e
  `REVISION_PLAN.md` §2 os usam; §8.5 declara as derrotas dentro de contrastes de saldo
  favorável (13/0/10 contra NSGA-III e AR-MOEA em HV com M = 3; 19/1/8 contra MOEA/D em IGD
  com M = 2; só três dos 28 contrastes sem derrota). (A2) Saiu a leitura de mecanismo
  ("intensificação que aproxima e não expande a cobertura"): a discordância IGD × HV muda de
  direção entre M = 2 e M = 3 e o desenho não isola a causa; "proximidade e cobertura" deu
  lugar a "IGD e HV" nos trechos novos. (A3) O bloco de `main.tex` e a pendência do
  `REVISION_PLAN.md` §4 passaram a restaurar só os Apêndices A e B; a restauração não desfaz a
  QP5, e `pos/apend_III` não volta como está (`fig:posto_medio` ficaria duplicado); destino do
  Apêndice C a decidir pelo autor. O motivo registrado é só a decisão do autor. (A4)
  `cap_I.tex:28`: "hipótese de projeto", decisões definidas no Capítulo `sec:Proposal`;
  objetivo geral e objetivos específicos na ordem das QPs (ativação antes de posicionamento).
  (A5) `cap_VIII.tex:65`: rederivação restrita aos acoplamentos ao NSGA-II e ao NSGA-III
  (§3.1). (B1) "Outros hospedeiros". (B2) saldo favorável em IGD com M = 3 declarado estreito
  contra o AGE-MOEA-II (9/6/8). (B3) a leitura sobre AGE-MOEA-II e AR-MOEA é restrita aos dois
  algoritmos nas configurações padrão diante do IVF/SPEA2 calibrado, sem estender à classe.
  (B4) a nota da tabela remete a `tab:confirmatorio_wtl`; só a nota mudou, por
  `make thesis-tables`. (B5) nenhuma das duas opções do lote coube: o texto anterior à R17
  ocupa exatamente uma página em cada língua, e qualquer oração sobre a QP5 levava as
  palavras-chave à página seguinte. O autor autorizou refatorar os dois textos "mantendo
  qualidade e completude em relação ao texto"; resumo e abstract foram reescritos a partir
  do texto anterior à R17, cada um numa página com as palavras-chave, com a oração "diante de
  sete comparadores de contexto, o saldo é desfavorável em 4 dos 28 contrastes". Uma revisão
  independente da refatoração apontou três precisões perdidas (seleção do sinal e da janela
  antes das dobras; "diferença relativa mediana entre medianas"; "reanálise da regressão
  estática", com Spearman), todas restauradas, e quatro ambiguidades herdadas do texto
  anterior à R17, registradas como pendência na §6.3. (B6) `cap_VI.tex:4` remete o protocolo à `sec:estatistica` e o relato à
  `sec:posicionamento`. Também foi restaurada, nas Conclusões, a formulação anterior "o que
  distingue as instâncias em que o operador rende menos", que a R17 alterara sem fonte.
  Nenhum número, coorte, teste, correção, parâmetro ou chave bibliográfica preexistente
  mudou; a R17 introduziu 28 contagens novas por gerador e os rótulos `sec:posicionamento`,
  `sec:resposta_qp5` e `tab:posicionamento`, e o fechamento não alterou nenhuma delas.
  Revisões independentes deste lote (científica, A1–A5 e B2–B3; quantitativa, todas as
  contagens citadas, com recomputação das 28 células) sem achado.

  **Achados da R17 não adotados (C1).** `Q7`: não existe. A auditoria quantitativa da R17
  produziu cinco achados, `Q1`–`Q5`, todos adotados; a lista "Q1–Q6, Q8–Q14" do relatório da
  R17 foi erro de redação, e não há justificativa de rejeição a reconstituir. `S7` (Jiao et
  al. não sustenta, no trecho acessível, "o cálculo da aptidão segue sob exame"): na prática
  foi adotado — a §3.3 deixou de atribuir a Jiao et al. o exame do cálculo da aptidão e passou
  a descrevê-lo como tratamento multiforme de problemas com restrições —, mas o relatório da
  R17 o omitiu da lista de adotados. A razão dessa omissão não pode ser reconstituída a
  partir dos registros da sessão. A atribuição a `li2015many`, que o achado também
  apontava como não conferida (HTTP 403), saiu do parágrafo na mesma reescrita.

- **R18 (concluída, 2026-10-03) — atenuação da autocrítica (nível 2).** Decisão do autor:
  reduzir a repetição de ressalvas, neutralizar o tom e retirar do corpo do texto um conjunto
  fechado de ressalvas de bastidor, que passam a ser respostas prontas para a banca
  (`REVISION_PLAN.md` §8). Nenhum número, coorte, teste, correção, `\cite`, `\ref` ou
  `\label` mudou, e nenhum veredito de QP foi alterado; a verificação por arquivo usou
  `claims.py diff` e `prose_audit.py`. Reescrita do Cap. 9 como ameaça → mitigação → risco
  residual, de 6 para 3 páginas, e remoções do corpo do texto: exposição das versões de
  MATLAB e PlatEMO dos manuscritos (§5.1 guarda só a identificação da cópia distribuída como
  4.6), histórico dos registros de sondagem da seleção RWMOP, momento de formulação da QP5,
  análise de convergência omitida (a §5.3 declara o escopo do desfecho final e a §10.2 propõe
  a análise), tempo de relógio (fica uma frase na §4.5), magnitudes como intervalos
  (§5.4 as delimita), pré-processamento pré-dobra do modelo estático (a §7.4 descreve a
  reanálise como validação mais estrita) e dados brutos (lugar canônico: Apêndice B, oculto).
  Enquadramentos reescritos: Holm e Benjamini–Hochberg por família (§5.6) e política de
  tamanho de população (§5.1) passam a descrição de desenho; a divergência com o manuscrito
  de origem sobre o gatilho passa a nota de rodapé na §4.1; a divergência sobre geometria fica
  uma vez, na §8.1. Cap. 10: §10.1 "Separar os efeitos combinados", §10.4 extinta, item de
  velocidade de convergência na §10.2. Conclusões do Cap. 8 terminam na síntese das
  contribuições. Nenhuma ressalva que sustenta afirmação mantida foi removida: permanecem
  calibração em 12/51, diferença de implementação fora do módulo, ablação fora da
  configuração promovida, escopo, sobreposição de coortes, rótulos da análise de ativação e
  análises formuladas após os resultados. `make thesis` sem item bloqueante novo e sem
  *overfull*; 103 páginas (eram 106). Fica registrada a reversão, no resumo e no abstract, da
  precisão "sinal e janela escolhidos antes das dobras" que o fechamento da R17 havia
  restaurado: a decisão da R18 é mantê-la apenas na §7.4, por economia de resumo.

Portões por rodada: `make thesis-doctor` → `make thesis` → `make thesis-render` quando
houver mudança de layout. Por perfil §11: invocar `$write-scientific-manuscripts` antes
de editar prosa, auditoria editorial nos `.tex` alterados depois, e entrada em
`AI_ASSISTANCE_LOG.md` a cada lote.

### 6.3 Decisões que exigem autor ou orientador

`OQ-02` e `OQ-04` — recuperar o conjunto `.mat` arquivado e reexecutar, ou escrever
para a realidade de 10 checkpoints declarando as afirmações dos manuscritos como não
verificadas em árvore · `OQ-03` — corrigir o pareamento em
`test_convergence_significance.py`, o que altera artefato por trás de artigo aceito, ou
documentar a exclusão · `OQ-09` · `OQ-10` · `OQ-15` (texto corrigido na R10; restam os logs
e a errata dos manuscritos) · `OQ-16`, `OQ-19`, `OQ-21`, `OQ-22` e `OQ-23` (errata ou revisão dos
manuscritos, se ainda houver oportunidade) · `OQ-24` (errata e campanha de controle) · `OQ-25` (errata do PPSN quanto à configuração dos pipelines NSGA) · data de defesa — a provisória, 08/11/2026, cai num **domingo** —,
banca, `\publica`, campos de coorientador e a declaração de formato exigida pela
Resolução INF nº 02/2023/PPGCC. A estrutura em dez capítulos e três apêndices (o terceiro desde a R9) resulta da
decisão da R4, que consolidou os estudos complementares num único capítulo.

Pendentes desde o fechamento da R18 (2026-10-03): **autorizar** a entrada da rodada em
`AI_ASSISTANCE_LOG.md` e os commits; **revisar** as respostas da §8 acrescentadas na R18
(convergência, tempo de relógio, versões de ambiente, QP5, seleção RWMOP, vazamento entre
dobras, dados brutos); decidir se a precisão "sinal e janela escolhidos antes das dobras"
volta ao resumo e ao abstract; revisar as remissões ao Cap. 9 no texto (a R18 as manteve só
para itens que ele ainda contém).

Pendentes desde o fechamento da R17 (2026-10-03): **Apêndice C** — aposentar ou
reaproveitar como detalhamento por instância, sem a figura. **Ferramenta e modelo** do
registro de IA e **autorização** do registro e dos commits. **Ambiguidades herdadas do
resumo e do abstract** (já presentes antes da R17; não corrigidas no lote fechado): as
contagens contra o SPEA2 não dizem que são de IGD; o recorte de 39 instâncias não menciona a
duplicata funcional MaF7/DTLZ7 com M = 3; a frase dos hospedeiros não sinaliza a mudança de
protocolo (30 execuções, Benjamini--Hochberg); a ablação não diz que roda na configuração
inicial nem nomeia as duas decisões. Cada correção custa espaço numa página que está cheia.
**Remanescentes fora do lote:** `cap_VII_complementares.tex:26` (engenharia) ainda diz
"proximidade e cobertura" para IGD e HV; `cap_VIII.tex:67` chama de "comparação
exploratória" o contraste com NSGA-III e MOEA/D, que a QP5 agora testa com Holm.
