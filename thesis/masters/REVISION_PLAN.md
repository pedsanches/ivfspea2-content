# Plano de revisão da dissertação

Índice estratégico. A especificação detalhada — afirmações, artefatos, questões abertas
(`OQ-*`) e rodadas — está em `REWRITE_SPEC.md`; o perfil editorial, em
`SCIENTIFIC_WRITING_PROFILE.md`. Este plano substitui a versão de julho, cujos itens de
identidade do algoritmo e de sincronização de evidência foram cumpridos nas rodadas R1–R6.
Numeração de capítulos e seções conforme o PDF compilado.

## 1. Escopo: sem re-execução

Decisão do autor em 2026-09-22 (`REWRITE_SPEC.md` §1.1, decisão 6). A dissertação usa
apenas os artefatos existentes. Uma análise nova entra quando recalcula a partir de
artefatos versionados, por gerador em `src/python/thesis/` coberto por
`make thesis-tables-check`; nenhum número de tabela é digitado à mão.

A decisão tem uma única consequência sobre as conclusões: a QP2 recebe uma resposta mais
estreita que a pergunta. A ablação rodou na configuração inicial não ajustada, contra
execuções de outra campanha (`OQ-14`), e na configuração promovida a contribuição das
duas decisões de acoplamento não foi isolada. O texto declara o limite, e o experimento
que o fecharia — a ablação em C26, com braços pareados por semente — fica em trabalhos
futuros (§10.1).

## 2. Pergunta geral e questões de pesquisa

Objetivo geral (R12): avaliar se o acoplamento do IVF ao SPEA2 melhora o hospedeiro sob
orçamento fixo de avaliações, com que magnitude e em que instâncias, e investigar a que o
benefício pode ser atribuído, se ele depende do algoritmo hospedeiro e se é possível
decidir, durante a execução, quando usar o operador. A formulação anterior, "determinar se,
por que e em que condições", prometia uma identificação causal que os desenhos não fazem.

| QP | Pergunta | Onde | Resposta que a evidência sustenta | Natureza |
|---|---|---|---|---|
| QP1 | O IVF/SPEA2 supera o SPEA2, e com que magnitude? | Cap. 6; §7.1; §8.1 | Sim, delimitado, para a implementação completa (que também recalcula a aptidão antes do torneio, `OQ-24`). IGD com Holm: 22/3/3 (M=2) e 15/7/1 (M=3); fora do ajuste, 19/3/2 e 12/3/0 (11/3/0 sem MaF7/M3). Magnitude: nas 51 instâncias, sem seleção por significância, Â₁₂ mediano 0,756 e Δ mediano +1,15%; condicionado às 37 vitórias, 0,804 e +1,27%; às 4 derrotas, 0,265 e −4,01%; Δ mediano das vitórias em HV +0,06%. Â₁₂ e Δ medem coisas diferentes e ordenam vitórias e derrotas de modo diferente; nenhum é custo, e não há limiar de relevância prática. Nas vitórias fora do ajuste, Δ mediano +1,27% (M=2) e +1,39% (M=3); ICs bootstrap em quatro instâncias são sensibilidade local. Engenharia: vitória detectável em 1/3 e ausência de diferença detectável em 2/3, sem inferir ausência de prejuízo. Posicionamento exploratório (Apêndice C): 2.º posto médio com M=2 e 1.º com M=3, sem superioridade par a par. | confirmatória na suíte sintética; apoio em engenharia |
| QP2 | O ganho vem das duas decisões ou da configuração? | §7.2; §8.2 | Configurações C26 e A43 usam 30 execuções, a histórica 60 e orçamento não verificado no contraste; não é teste isolado dos parâmetros. A calibração usou 50.000 avaliações e a avaliação 100.000; a estabilidade da escolha entre orçamentos não foi estudada (§9.1). A ablação inicial registra 0/50/1 diante da ausência das duas decisões em cada métrica, sem equivalência; Friedman fatorial p = 0,485 não prova igualdade. Na configuração promovida não há ablação; o recálculo de aptidão antes do torneio também não foi isolado. A hipótese de densidade permanece justificativa de projeto. A retenção dos descendentes do módulo foi registrada numa variante instrumentada, em outra coorte (`IVF_V2_TRACE.m`; `results/ivf_trace/representative_cycles.csv`, `selection_rate`), mas essa análise não integra a evidência de atribuição da dissertação; não escrever que a retenção "não foi medida". | apoio; atribuição indeterminada |
| QP3 | O benefício depende do hospedeiro? | §7.3; §8.3 | Dois níveis. (a) Os resultados diferem entre os pipelines avaliados: em IGD, 33 de 51 instâncias no SPEA2, 22 no NSGA-III e 1 no NSGA-II (30 execuções, Wilcoxon, BH). (b) O efeito causal do hospedeiro não foi identificado: hospedeiro, realização do módulo, recombinação, ativação, configuração e procedimento de ajuste variam juntos; só o IVF/SPEA2 tem calibração documentada nesta suíte, e os pipelines NSGA usam configurações fixas dos runners, sem registro de ajuste equivalente (`OQ-25`). Não abrir com "Sim". IVF/NSGA-III 22/29/0 em IGD: zero derrotas detectadas não é segurança nem equivalência. Os estudos de origem (IVF/NSGA-II 2017; tese IVF/NSGA-III 2024) usam outros orçamentos, configurações e testes; as divergências e semelhanças não são replicação. Por suíte (descritivo): a WFG é a de menor taxa de vitória em IGD no IVF/SPEA2 (9/6/3) e no IVF/NSGA-III (3/15/0); o IVF/NSGA-II não segue o padrão. | comparativa |
| QP4 | Dá para antecipar o benefício, e usar essa informação compensa? | §7.4; §8.4 | Veredito: sinal diagnóstico limitado nesta amostra; nenhuma regra de controle vantajosa diante do sempre ativo. Estático: reanálise com resposta transformada no treino, DTLZ+MaF retidas juntas e escala original, r_s = 0,150; a diferença para o original não é atribuída a um fator isolado. Resumos por instância: BA = 0,754 ao reter suíte ou agrupar DTLZ+MaF, com sinal e janela escolhidos antes; decisões coincidem com WFG/demais em 49/51; a partição pós-hoc WFG/demais, sobre os mesmos rótulos, dá BA 0,778 (discordâncias: DTLZ6 M=2 e M=3). Execução: controlador em HV 34/14/3 contra o SPEA2 e 2/40/9 contra o sempre ativo, sem utilidade líquida; faltam registros de decisão por execução. BA não é utilidade; custos assimétricos são hipótese. | diagnóstica |

Síntese (§8.6, R13): no escopo avaliado (51 instâncias sintéticas, M = 2 e 3, 100.000
avaliações, desfecho final), a implementação completa do IVF/SPEA2 melhora o SPEA2 com
frequência, por deslocamento mediano pequeno (Â₁₂ mediano 0,756; Δ mediano +1,15% nas 51
instâncias); as quatro derrotas detectáveis, todas na WFG, deslocam a mediana mais que a
vitória típica, mas a mediana do seu Â₁₂ fica mais perto de 0,5 que a das vitórias (por
instância, varia de 0,101 no WFG2/M3 a 0,344 no WFG9/M2), e nenhuma dessas medidas é custo ou
relevância prática. A atribuição não foi identificada (decisões, configuração, recálculo de
aptidão, `OQ-24`); os resultados diferem entre pipelines sem isolar o hospedeiro; a
renovação inicial carrega sinal diagnóstico indistinguível da suíte, e o controlador não
superou o sempre ativo. A frase anterior "perde raramente e por mais" foi retirada por
confundir deslocamento com custo. As Conclusões remetem ao Cap. 9 e não introduzem
contribuição ausente do Cap. 1.

Hipótese (§8.5, não conclusão): a WFG concentra os resultados menos favoráveis, já na
família confirmatória; a recorrência nas outras famílias é, para o IVF/SPEA2, reutilização
(`OV-01`, `OV-02`); das duas colunas com execuções novas, só a do IVF/NSGA-III repete o
padrão, e o IVF/NSGA-II concentra na WFG diferenças nos dois sentidos. A tabulação
exploratória (`C-WFG-01`) restringe a hipótese: o contraste com as demais suítes depende da
configuração (WFG 3/3/3 com M=2 e 5/3/1 com M=3, contra 19/0/0 e 10/4/0 nas demais; a única
derrota com M=3 continua na WFG; K e D mudam com M), duas derrotas estão em instâncias da calibração,
e as derrotas caem nas funções não separáveis (separáveis 6/2/0, não separáveis 2/4/4 em
IGD), sem isolar a propriedade. A WFG também reúne 8 vitórias corrigidas em 18
configurações: não é "marcador das instâncias desfavoráveis". O teste proposto é o desenho
fatorial da §10.1, com M e K/L controlados.

Regra de redação: cada QP é respondida num único lugar, a seção correspondente do Cap. 8.
Os outros capítulos remetem a ela e não reenunciam o resultado.

## 3. Estado em 2026-09-24

Rodadas R1–R12 concluídas (`REWRITE_SPEC.md` §6.2). O PDF compila com 98 páginas, sem
aviso LaTeX, sem linha *overfull* e sem página de texto só com *floats*;
`thesis-tables-check`, `thesis-doctor`, `verify-release` e `make test` passam. Resumo e
abstract cabem, cada um com as suas palavras-chave, numa página. A R10 corrigiu os defeitos
apontados pela avaliação de 2026-09-23: fatos (versão de plataforma, uso da MaF, duplicata
MaF7/DTLZ7, observáveis testados, regra dos rótulos, custo de relógio), contradições
internas, definições de Pareto, §3.5, citações de métodos, os três manuscritos derivados
(§1.4) e a forma das figuras. A R11 conferiu essas correções uma a uma e fechou o que
restava: generalizações ao IVF/GDE3 sem fonte (Caps. 1 e 3), o posto médio chamado de "sem
correção de multiplicidade" quando não há teste (§5.4, Cap. 6, Apêndice C), frases que
afirmavam mais do que a evidência (§1.4, §3.4, §6.3, §8.1.1, §9.1, §9.4, §10.2), a entrada
bibliográfica de Maturana et al., o rótulo cortado da Figura 7.3 e trechos de
metacomentário. A R12 calibrou a linha argumentativa --- objetivo geral, motivação por
densidade como hipótese de projeto, Conclusões organizadas em eficácia, atribuição e decisão
de uso --- e corrigiu dois fatos do Cap. 4 contra o código: o gatilho não concentra a
intensificação no início (`OQ-23`), e o IVF/SPEA2 recalcula a aptidão antes do torneio, o
que o SPEA2 da plataforma não faz (`OQ-24`). Não resta pendência de conteúdo que dependa de
dados. O que falta está nas §4 e §5.

Complemento sobre artefatos versionados, sem novas campanhas (§1): foram gerados os
recortes de magnitude fora do ajuste, quatro intervalos bootstrap exploratórios de IGD
e a reanálise estática/dinâmica de ativação (Tabelas do Cap. 6 e §7.4). O contraste
histórico da calibração e a triagem de engenharia foram qualificados pelos registros
efetivamente distribuídos; as decisões por instância não foram confundidas com
desativações por execução do controlador. As afirmações do estado R12 acima são um
registro histórico e não substituem essas ressalvas.

Verificação bibliográfica deste complemento: o registro Crossref
`10.1016/j.swevo.2021.100961` inclui Qizhang Luo; as entradas .bib da
dissertação e do Springer foram corrigidas. O DOI anteriormente associado a
Holm (1979), `10.2307/4615733`, retorna 404 em doi.org e foi removido das
duas entradas; não se substituiu pelo candidato automático sem conferência.
O texto primário integral de Vargha--Delaney e Holm não ficou acessível nesta
revisão: a categoria convencional de efeito pelo corte $A_{12}=0,71$ foi
substituída por um corte explicitamente descritivo e operacional, sem
atribuição bibliográfica de categorias; a demonstração original do
procedimento de Holm permanece sem conferência direta do PDF.

Rodada R13 (2026-09-28), revisão da Discussão sem novas campanhas: o Cap. 8 passou a
responder às QP com títulos que reproduzem o objeto das perguntas do Cap. 1, a separar resumo não condicionado de resumos
condicionados ao desfecho, a responder à QP3 em dois níveis, a dar veredito explícito à
QP4 e a dialogar com a linhagem IVF, com a seleção adaptativa de operadores e com a
análise de paisagem, conferidas nas fontes primárias. Dois cálculos novos, ambos por
gerador: a partição pós-hoc WFG/demais (`tab_ativacao_robustez`) e a tabulação da WFG
por propriedade e configuração (`tab_wfg_exploratoria`, com `config/wfg_properties.csv`).
O Cap. 9 ganhou a diferença de orçamento entre calibração e avaliação, a assimetria de
ajuste entre pipelines e as análises formuladas depois dos resultados; os Caps. 3, 4, 6, 7
e 10 foram ajustados apenas para coerência. Registro em `REWRITE_SPEC.md` §6.2.

## 4. Decisões do autor e do orientador

Bloqueiam o depósito:

- [ ] **`OQ-10` — autoria e reúso.** Declaração de contribuição e permissões de texto,
  figuras e tabelas dos manuscritos. A §1.4 já cita os três manuscritos e a sua situação
  editorial (preprint, aceito no PPSN 2026, submetido ao CLEI 2026); falta a declaração.
- [ ] **`OQ-09` — identidade de release.** No congelamento, criar um release próprio da
  dissertação no Zenodo e citar o DOI de versão junto com o DOI de conceito
  (`10.5281/zenodo.19071253`).

Não bloqueiam o depósito, mas têm prazo próprio:

- [ ] **`OQ-15` — ambiente de execução.** O texto deixou de afirmar versão de campanha na
  R10 (§5.1, nota da Tabela 5.1, §9.4): a §9.4 expõe os três registros dos manuscritos e a
  incompatibilidade entre o Springer e o PPSN nas execuções `3001–3030`. Resta, fora da
  dissertação, localizar os logs dos runners, se existirem, e decidir errata do Springer
  (legenda da tabela de parâmetros) e do PPSN (ambiente da coluna IVF/SPEA2). Se os logs
  aparecerem, a §9.4 pode passar a afirmar as versões.
- [ ] **`OQ-21`** — o Springer diz que a MaF entra só com três objetivos e não registra
  que o MaF7 repete o DTLZ7, nem que o MaF7 com M = 3, fora do ajuste, é a função do
  DTLZ7 da calibração. Decidir errata.
- [ ] **`OQ-22`** — o resumo e a discussão do Springer associam o ganho às fronteiras
  regulares; a família confirmatória não sustenta essa leitura para a frequência das
  vitórias nem para as derrotas (§6.3). Decidir errata.
- [ ] **Seleção RWMOP no Springer.** O texto do artigo descreve uma sondagem de uma
  execução (compatível com o registro histórico), mas a sondagem V2 disponível tem
  cinco por candidata. As contagens `0/8/0` das quatro excluídas não têm saída
  pareada distribuída, e `0/3/5` para RWMOP8 diverge do `1/1/5` registrado na
  triagem; a cobertura principal de RWMOP8 inclui 18/60 SPEA2+SDE e 0/60 MOEA/D.
  Não há carimbo temporal que verifique pré-seleção nem critério operacional
  documentado para a cobertura mínima dos comparadores. A dissertação declara
  essas limitações (§7.1); decidir eventual errata do artigo contra os registros
  de cada versão, sem inventar empates a partir de métricas ausentes.
- [ ] **`OQ-23`** — o Springer (`sn-article.tex:252`) afirma que o gatilho fica mais difícil
  de satisfazer ao longo da execução e deduz dele um custo amortizado estritamente menor; a
  regra implementada limita a fração acumulada e fica mais fácil de satisfazer depois de uma
  geração sem ativação. A dissertação segue o código e declara a divergência (§4.1). Decidir
  errata.
- [ ] **`OQ-24`** — o IVF/SPEA2 recalcula a aptidão sobre a população antes do torneio; o
  SPEA2 da plataforma usa a da seleção ambiental anterior. O Springer diz que uma geração
  sem ativação "is identical to canonical SPEA2" (`sn-article.tex:247`). A dissertação
  declara a diferença (§4.1, §9.1) e o controle que a fecharia (§10.1). Decidir errata e se
  a campanha de controle, o SPEA2 com o mesmo recálculo, entra antes da defesa, o que
  exigiria rever a decisão da §1.
- [ ] **`OQ-16`** — a dissertação passou a ler a validação deixa-uma-família como
  estimativa fora da família, contra a leitura do CLEI (`main.tex:548-550, 620-624`).
  Revisar o CLEI, se ainda houver oportunidade.
- [ ] **`OQ-13`** — conferir se a figura 7 do CLEI exibe o valor inflado de
  `classifier_comparison.csv`.
- [ ] **`OQ-01`** — o turnover em WFG do manuscrito PPSN-dinâmica não reproduz.
- [ ] **`OQ-19`** — a dissertação passou a ler o 0,754 da regra de renovação como
  separação entre a WFG e as demais suítes (decisões coincidentes em 49 de 51 instâncias),
  leitura que o resumo e a conclusão do CLEI não registram. Revisar o CLEI, se ainda houver
  oportunidade.
- [ ] **Entrada `maturana2009adaptive` do CLEI** (`paper/clei2026/references.bib:214`):
  ano 2009 e cinco autores, contra 2011 e seis autores no registro Crossref do capítulo
  (DOI `10.1007/978-3-642-21434-9_7`). A dissertação já usa a entrada corrigida. Corrigir
  no CLEI, se ainda houver oportunidade.
- [ ] **Fluxograma do SPEA2** (`fig/fluxo_spea2_pt.pdf`, sem fonte editável no
  repositório): a caixa "Preenche ND com soluções dominadas do Conjunto Arquivo" deveria
  dizer "da união da população com o arquivo", como a §2.1.4 e Zitzler et al. (2001). O
  texto já está correto e declara que a figura representa a implementação, em que
  população e arquivo coincidem. Redesenhar a caixa ou manter.
- [ ] Cinco figuras legadas com fontes Type 3 continuam em `thesis/masters/fig/` sem
  nenhum uso. Remover ou manter.
- [ ] **`OQ-25` — configuração dos pipelines NSGA no PPSN.** O artigo de hospedeiros
  (`paper/ppsn2026-ivf-hosts/main.tex:148-149`) diz que cada pipeline usou "the fixed
  parameter setting of its cited canonical implementation". Os runners fixam (R, C,
  Cycles) = (0,5; 0,07; 5) no IVF/NSGA-II e (0,10; 0,10; 5) no IVF/NSGA-III; esses valores
  pertencem à grade do estudo de 2017 mas não são as configurações vencedoras relatadas, e o
  limite de cinco ciclos diverge dos três (sem *steady state*) do experimento ampliado da tese
  de 2024. Não há registro de ajuste equivalente ao do IVF/SPEA2 nesta suíte. A dissertação
  declara a assimetria (§7.3, §8.3, §9.2). Decidir errata do PPSN.
- [ ] **Referências da linhagem IVF/NSGA-III.** A implementação local segue o artigo CEC
  2023 (DOI `10.1109/CEC53210.2023.10254062`, pp. 1--8), que não está no `.bib`; a
  dissertação cita a tese de 2024. O comentário de cabeçalho de
  `IVF-NSGA-III/IVFNSGAIII.m` atribui ao artigo as páginas 2066--2073, que são do IVF/GDE3.
  Decidir se o artigo de 2023 entra no `.bib` e corrigir o comentário fora desta rodada.
- [ ] **Metadados incompletos no `.bib` (R13, verificados no Crossref).** Faltam DOIs
  conferidos: `liefooghe2018landscape` `10.1109/TEVC.2019.2940828` (ano 2020 correto; título
  publicado grafa "Multiobjective"), `zhou2011multiobjective` `10.1016/j.swevo.2011.03.001`,
  `kerschke2019automated` `10.1162/evco_a_00236`, `fialho2008adaptive`
  `10.1007/978-3-540-87700-4_18` e `sampaio2017ivf` `10.1109/LA-CCI.2017.8285710`.
  `camilo-junior2011` traz `pages = {1--14}`, contagem do PDF avulso, sem DOI
  (`10.5772/16074`) nem editor; o intervalo no volume não foi conferido. Normalizar, se o
  autor quiser. A frase do Cap. 3 sobre o IVF/GDE3 (`sampaio2019ivf`) segue sem conferência
  na fonte primária, de acesso pago.

## 5. Pendências institucionais

Confirmar com o orientador e a secretaria do PPGCC:

- [ ] **Data de defesa.** A provisória, 08/11/2026 (`main.tex:77-79`), cai num domingo.
- [ ] **Regulamento aplicável.** CEPEC 1622/2018 (30 dias para a versão final) ou
  1983/2026 (60 dias), conforme o ingresso.
- [ ] **Prazo entre depósito e defesa.** Não consta do regulamento 1622/2018 nem do FAQ
  do programa; confirmar com a secretaria.
- [ ] **Banca** (art. 46 da 1622/2018): três examinadores doutores, ao menos um externo ao
  programa ou à UFG; suplentes interno e externo; aprovação da CPG. O coorientador, se
  participar, não conta para o mínimo.
- [ ] Folha de aprovação (`pre/pre_aprovacao.tex`) e `\publica`, depois de fixada a data.
- [ ] Declaração do formato monográfico, exigida pela Resolução INF nº 02/2023/PPGCC.
- [ ] Referência ao projeto de pesquisa cadastrado na UFG ao qual a dissertação se
  vincula (art. 40, §1º, da 1622/2018).
- [ ] Agradecimento a financiamento ou bolsa, se houver (os agradecimentos estão
  desativados em `main.tex`).
- [ ] Declaração de uso de IA exigida pela UFG e, se aplicável, pela Portaria CNPq nº
  2.664/2026, redigida a partir de `AI_ASSISTANCE_LOG.md`.
- [ ] O TECA assinado em 08/09/2026 traz o título atual; mudar o título exige novo termo.
- [ ] Opção `nocolorlinks` na versão impressa, se o programa exigir.

## 6. Validação a cada lote e antes do envio

```bash
make thesis-tables-check   # tabelas e figuras batem com os artefatos
make thesis-doctor         # data-sources.toml válido
make verify-release        # manifesto, checksums e DOIs
make test                  # suíte Python
make thesis                # compilação; conferir zero aviso LaTeX e zero overfull
make thesis-render         # rasterizar e inspecionar as páginas alteradas
grep -rniE "\bv1\b|\bv2\b|vers(ão|ao) (1|2|anterior do (nosso|presente))" \
  thesis/masters/tex thesis/masters/pre
```

O grep de versionamento não acusa ocorrência nos `.tex` desde a R10 (os acertos restantes são
bytes do PDF binário `pre/teca.pdf`; restrinja o grep a `*.tex`).
Antes do envio, conferir ainda citações e referências, metadados do PDF, a numeração das
páginas e a ausência de fontes Type 3 (`pdffonts build/main.pdf`).

## 7. Cronograma relativo à data de defesa (D)

| Quando | Entrega |
|---|---|
| Agora | Leitura do orientador sobre a versão R8; decisões da §4, em especial `OQ-15` |
| até D − 5 semanas | Correções da leitura; itens institucionais da §5 |
| até D − 4 semanas | Congelamento: tag e release Zenodo; processo SEI com a versão digital; envio à banca — antecipar se a secretaria exigir prazo maior |
| D − 3 a D − 1 semana | Apresentação em quatro blocos, um por QP; dois ensaios |
| D + 30 ou 60 dias | Versão final com as correções da banca e depósito na BDTD, conforme o regulamento aplicável |

## 8. Perguntas previsíveis da banca

| Pergunta | Onde está a resposta |
|---|---|
| Se a ablação não separa as decisões, qual é a contribuição? | §8.2 e §8.6: a eficácia é da implementação completa, e a atribuição é outra pergunta; contribuições 1 e 3 do §1.3; `OQ-14` |
| O ganho vem do módulo IVF ou de outra diferença entre as implementações? | §4.1, §8.2 e §9.1: o IVF/SPEA2 recalcula a aptidão antes do torneio, e nenhuma comparação separa essa diferença; o controle está em §10.1 (`OQ-24`) |
| O gatilho concentra a intensificação no início da execução? | §4.1: não; limita a fração acumulada e, mesmo com dois ciclos em toda ativação, suspende o módulo em uma de cada 16 gerações, distribuídas ao longo da execução (`OQ-23`) |
| Por que a ablação não foi repetida na configuração promovida? | §7.2 e §10.1: limite declarado, sem nova campanha |
| O ganho importa na prática? | §6.2 e §8.1: nas 51 instâncias, Â₁₂ mediano 0,756 e Δ mediano +1,15% em IGD; não se definiu limiar de relevância prática, e Â₁₂ e Δ medem aspectos diferentes; não há intervalo global de generalização. |
| Por que o NSGA-II quase não se beneficia? | §7.3, §8.3 e §9.2: comparação entre pipelines que diferem em realização do módulo, configuração e procedimento de ajuste; só o IVF/SPEA2 foi calibrado nesta suíte (`OQ-25`); o estudo de origem usou outro orçamento e a melhor configuração por problema. |
| O controlador vale a pena? | §7.4 e §8.4: HV 34/14/3 contra o SPEA2 e 2/40/9 diante do sempre ativo, sem utilidade líquida nem equivalência nos 40 empates; classificação e decisão sob custos assimétricos são perguntas distintas. |
| O limiar exige conhecer a família do problema? | §7.4: cada dobra ajusta limiar sem a família retida; o observável e a janela foram escolhidos antes dessas dobras na mesma linha de evidência, sem validação aninhada. |
| O sinal de renovação é mais que a identidade da suíte? | §7.4, §8.4 e §9.3: nesta amostra, não se distingue dela; 49/51 decisões em resumos de instância coincidem com WFG/demais, e a própria partição, pós-hoc, atinge BA 0,778 contra 0,754; não equivalem a desativações por execução. |
| Se a geometria não separa e as decisões não foram isoladas, o que distingue as instâncias desfavoráveis? | §8.5: hipótese, restringida pela Tabela 8.1 (dependência de M, D e K; derrotas só em funções não separáveis; duas derrotas em instâncias da calibração); teste fatorial em §10.1 |
| Por que o Cap. 6 não traz o posicionamento contra os outros algoritmos? | Apêndice C: é exploratório, um posto médio descritivo, sem teste de hipótese, e nenhuma QP depende dele |
| As execuções do IVF/SPEA2 e do SPEA2 foram pareadas na comparação entre hospedeiros? | §7.3, terceira ressalva, e nota da Tabela 7.4: os pares NSGA são pareados por execução; o do IVF/SPEA2 é alinhado por ordem, e sem pareamento só uma contagem muda, em HV (`OQ-20`) |
| Por que Holm numa família e Benjamini–Hochberg noutra? | §9.4 |
| Dá para reexecutar? | Apêndice B |
| O recorte fora do ajuste é independente da calibração? | §5.5 e §6.1: não inteiramente; o MaF7 com M = 3 repete o DTLZ7 da calibração, e sem ele o recorte com M = 3 fica em 11/3/0 (`OQ-21`) |
| Por que 41 instâncias em que o operador "ajuda", se as vitórias corrigidas são 37? | §7.4: o rótulo usa o teste sem correção; quatro empates de Holm entram como "ajuda" (`OV-02`) |
| Em que versões do MATLAB e do PlatEMO as campanhas rodaram? | §9.4: não é verificável; os registros dos manuscritos divergem (`OQ-15`) |
| O artigo diz que a geometria da fronteira modera o ganho. Por que a dissertação não? | §6.3: a divergência é declarada; a frequência das vitórias não muda com a geometria, e as derrotas irregulares são um único problema (`OQ-22`) |
