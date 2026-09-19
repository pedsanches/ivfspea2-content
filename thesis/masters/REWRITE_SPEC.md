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
.venv/bin/python src/python/analysis/compute_claims_summary.py      # confirmatória
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

| Família | Coorte | n | Correção | Métricas | PlatEMO | `id_fonte` |
|---|---|---|---|---|---|---|
| `CONF` confirmatória | IVF `3001–3060` × SPEA2 `1–60`, 51 instâncias, FE = 100 000, N = 100 | 60 | Holm, por `M` e por métrica | IGD primária (menor melhor), HV secundária obrigatória (maior melhor) | 24.2.0.2923080 | `memetic-computing-v2-confirmatory` |
| `SUP` tuning e ablação | subconjunto de 12 problemas, FE = 50 000 (tuning); 51 instâncias (ablação) | 30 | Mann–Whitney + Holm | IGD, HV | 24.2.0.2923080 | `memetic-computing-tuning-ablation` |
| `ENG` engenharia | RWMOP9, RWMOP21, RWMOP8 | 60 | — | IGD, HV | 24.2.0.2923080 | `memetic-computing-engineering` |
| `HOST` hospedeiros | IVF/SPEA2 `3001–3030` × SPEA2 `1–30`; IVF/NSGA-II `4001–4030`; IVF/NSGA-III `5001–5030`; 51 instâncias | 30 | Benjamini–Hochberg | IGD, HV | 4.6 (MATLAB R2025b) | `ppsn-operator-host-compatibility` |
| `DEC` decisão de ativação | 60 execuções para rótulos; 30 pareadas por semente para dinâmica e controlador | 60 / 30 | BH | IGD para rótulos; **HV primária para o controlador** | 24.2.0.2923080 | `ppsn-clei-landscape-dynamics-controller` |

Divergências de protocolo entre famílias são **reportadas, não harmonizadas**
(`OQ-06`, `OQ-07`, `OQ-08`).

### 3.1 Capítulo VI — Resultados confirmatórios

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

Fora do ajuste = 24 + 15 = **39 instâncias**; ajuste = 4 + 8 = **12**; total 51.
Discriminador por instância: coluna `is_full12` de `claims_summary_instance_details.csv`
(102 linhas = 2 métricas × 51 instâncias).

Limite de generalização em todas as quatro: escopo sintético declarado, mesmo
orçamento, comparação contra SPEA2 canônico. Posicionamento multibaseline entra no
mesmo capítulo em seção **explicitamente rotulada como exploratória**.

### 3.2 Capítulo VII — Configuração, ablação e transferência

| `claim_id` | Enunciado | Valor verificado | Artefato |
|---|---|---|---|
| `C-TUN-01` | O ajuste em três fases promove C26 (`C=0.12, R=0.225, M=0.3, V=0.1, Cycles=2`) | C26 × A43 = 0/12/0 | `results/tuning_ivfspea2v2/` |
| `C-ABL-01` | O acoplamento completo supera o SPEA2 canônico | IGD **25/25/1**; HV **28/21/2** | `results/ablation_v2/phase3/phase3_summary.json` |
| `C-ABL-02` | A ablação não distingue o acoplamento completo da variante sem as duas decisões | IGD e HV **0/50/1** | idem |
| `C-ENG-01` | RWMOP9 | IGD **8/0/0**; HV **5/0/3** | `results/engineering_suite/engineering_suite_pairwise_main.csv` |
| `C-ENG-02` | RWMOP21 | IGD e HV **3/2/3** | idem |
| `C-ENG-03` | RWMOP8 | IGD e HV **1/1/5** | idem |

`C-ABL-02` é a linha que a §1.3 reenquadra: escrever pelo mecanismo ausente, nunca
por rótulo de versão. `C-ENG-*` tem peso probatório menor (transferência externa,
resultados mistos) e `RWMOP8` tem cobertura heterogênea de execuções válidas.

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
| `C-DYN-02` | Regra de limiar único | LOOCV BA 0,691 / MCC 0,311; deixa-uma-família BA **0,754** / MCC 0,413, limiar 0,216 | `results/tables/dynamic_signal_{loocv,lofo}.csv` |
| `C-CTRL-01` | O controlador contra o SPEA2, em HV | **34/14/3** em 51 casos | `results/tables/controller_wtl_oos_20260326_221909.csv` |
| `C-CTRL-02` | O controlador iguala ou supera o IVF sempre ativo, em HV | **42/51** | idem |

**Fonte proibida para este capítulo:** `data/processed/classifier_comparison.csv`.
A linha da regra de limiar sob `LOOCV` ali é um ajuste dentro da amostra, não uma
estimativa validada — ver `OQ-13`. Os artefatos acima são os que se sustentam.

Rótulos: **41 HELPS / 10 NOT_HELPS**. O capítulo **abre** declarando `OV-02`: os rótulos
derivam do desfecho confirmatório e não constituem desfecho independente — por isso o
desfecho primário declarado do controlador é HV, não IGD.

`C-DYN-01` é a linha atingida por `OQ-01`; usar os valores do CLEI, que reproduzem.

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

---

## 5. Sobreposição e não independência

| id | Relação | Consequência para o texto |
|---|---|---|
| `OV-01` | Hospedeiros `3001–3030` e `1–30` ⊂ coorte confirmatória `3001–3060` e `1–60` | a coluna IVF/SPEA2 do Cap. VIII **não replica** o Cap. VI; só `4001–4030` e `5001–5030` acrescentam execuções novas |
| `OV-02` | Coorte de rótulos do Cap. IX ≡ coorte de desfecho do Cap. VI | os rótulos HELPS/NOT_HELPS são **derivados** do desfecho confirmatório, não desfecho independente |
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

Portões por rodada: `make thesis-doctor` → `make thesis` → `make thesis-render` quando
houver mudança de layout. Por perfil §11: invocar `$write-scientific-manuscripts` antes
de editar prosa, auditoria editorial nos `.tex` alterados depois, e entrada em
`AI_ASSISTANCE_LOG.md` a cada lote.

### 6.3 Decisões que exigem autor ou orientador

`OQ-02` e `OQ-04` — recuperar o conjunto `.mat` arquivado e reexecutar, ou escrever
para a realidade de 10 checkpoints declarando as afirmações dos manuscritos como não
verificadas em árvore · `OQ-03` — corrigir o pareamento em
`test_convergence_significance.py`, o que altera artefato por trás de artigo aceito, ou
documentar a exclusão · `OQ-09` · `OQ-10` · data de defesa, banca, `\publica`, campos de
coorientador e a declaração de formato exigida pela Resolução INF nº 02/2023/PPGCC ·
confirmar com o programa se 13 capítulos e 2 apêndices são aceitáveis, ou se VII–IX
devem formar um único capítulo de estudos complementares.
