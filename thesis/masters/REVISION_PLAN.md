# Plano de revisão da dissertação

Índice estratégico. A especificação detalhada — afirmações, artefatos, questões abertas
(`OQ-*`) e rodadas — está em `REWRITE_SPEC.md`; o perfil editorial, em
`SCIENTIFIC_WRITING_PROFILE.md`. Este plano substitui a versão de julho, cujos itens de
identidade do algoritmo e de sincronização de evidência foram cumpridos nas rodadas R1–R6.
Numeração de capítulos e seções conforme o PDF compilado.

**Numeração desde a R19 (2026-10-10).** A dissertação passou a ter nove capítulos: os
antigos Caps. 5 (Experimentos) e 6 (Resultados) formam o Cap. 5, Experimentação, e os
seguintes recuam um número. Os blocos datados anteriores à R19 neste plano e em
`REWRITE_SPEC.md` mantêm a numeração da época; para lê-los, use a correspondência abaixo.
As referências das §2, §4 e §8 deste plano também usam a numeração anterior quando não
indicam o contrário.

| Até a R18 | Desde a R19 |
|---|---|
| §1.2 Questões de pesquisa | §5.1 (`sec:questoes`) |
| §1.3 Contribuições; §1.4 Publicações derivadas; §1.5 Organização | §1.2; §7.8 (`sec:publicacoes`); §1.3 |
| §5.1–§5.5 (plataforma, suítes, métricas, estatística, calibração) | §5.2.1–§5.2.5 |
| §5.6 Famílias de evidência | §5.1.1 (`sec:familias`) |
| Cap. 6 Resultados; §6.1–§6.4 | §5.3 (`sec:results`); §5.3.1–§5.3.4 |
| Cap. 7 e §7.1–§7.5 (estudos complementares) | Cap. 6 e §6.1–§6.5 |
| Cap. 8 e §8.1–§8.7 (discussão, conclusões) | Cap. 7 e §7.1–§7.7; §7.8 nova |
| Cap. 9 (ameaças) e Cap. 10 (trabalhos futuros) | Cap. 8 e Cap. 9 |

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

Na R14, a QP2 passou a perguntar pelas diferenças observadas entre configurações e
variantes nos estudos realizados (§2); a consequência acima recai agora sobre a atribuição,
que a resposta da QP2 declara como problema não isolado, e não sobre a pergunta.

## 2. Pergunta geral e questões de pesquisa

Objetivo geral vigente (R19, 2026-10-10; reformulação feita nesta rodada em resposta ao
comentário A033 do revisor externo, **pendente de aprovação do autor**): "propor um
acoplamento do método IVF ao SPEA2 e avaliar se ele melhora o desempenho do hospedeiro sem
aumentar o orçamento de avaliações, delimitando o alcance desse resultado". A decomposição
operacional passou aos objetivos específicos 2 a 6, que correspondem à QP1–QP5, e as QPs
passaram à §5.1 por decisão do autor. Histórico (R17, abaixo): a formulação anterior
enumerava as cinco questões no próprio objetivo geral.

Objetivo geral (R17, 2026-10-03; ordem alinhada às QPs no fechamento da R17): avaliar se o
acoplamento do IVF ao SPEA2 melhora o hospedeiro sob orçamento fixo de avaliações, com que
magnitude e em que instâncias; comparar o desempenho das configurações e das variantes de
acoplamento avaliadas na calibração e na ablação; comparar como varia o desempenho relativo
dos acoplamentos do IVF ao SPEA2, ao NSGA-II e ao NSGA-III diante dos respectivos
hospedeiros; investigar se informação disponível antes da execução ou colhida na sua
dinâmica inicial permite antecipar quando o operador ajuda, e se uma regra de controle
construída sobre a dinâmica inicial produz ganho diante do IVF/SPEA2 sempre ativo; e
posicionar o acoplamento diante dos sete comparadores de contexto da avaliação.

Histórico. R14 (mesma data, antes do complemento): a última oração era "e investigar se é
possível decidir, durante a execução, quando usar o operador", que não cobria os descritores
estáticos, anteriores à execução, nem nomeava o comparador do controle.

Histórico. R12: "avaliar se o acoplamento do IVF ao SPEA2 melhora o hospedeiro sob orçamento
fixo de avaliações, com que magnitude e em que instâncias, e investigar a que o benefício pode
ser atribuído, se ele depende do algoritmo hospedeiro e se é possível decidir, durante a
execução, quando usar o operador". A formulação anterior a ela, "determinar se, por que e em
que condições", prometia uma identificação causal que os desenhos não fazem. A R14 manteve os
quatro eixos e reformulou a QP2 e a QP3 como perguntas comparativas sobre os estudos
realizados (`REWRITE_SPEC.md` §1.6): as formulações novas foram fixadas depois dos estudos e
não são hipóteses prévias, e a atribuição às decisões, à configuração e ao hospedeiro continua
não isolada. As formulações R8 da QP2 ("o ganho vem das duas decisões ou da configuração?") e
da QP3 ("o benefício depende do hospedeiro?") ficam registradas na §1.6 da especificação.

| QP | Pergunta | Onde | Resposta que a evidência sustenta | Natureza |
|---|---|---|---|---|
| QP1 | O IVF/SPEA2 supera o SPEA2, e com que magnitude? | Cap. 6; §7.1; §8.1 | Sim, delimitado, para a implementação completa (que também recalcula a aptidão antes do torneio, `OQ-24`). IGD com Holm: 22/3/3 (M=2) e 15/7/1 (M=3); fora do ajuste, 19/3/2 e 12/3/0 (11/3/0 sem MaF7/M3). Magnitude: nas 51 instâncias, sem seleção por significância, Â₁₂ mediano 0,756 e Δ mediano +1,15%; condicionado às 37 vitórias, 0,804 e +1,27%; às 4 derrotas, 0,265 e −4,01%; Δ mediano das vitórias em HV +0,06%. Â₁₂ e Δ medem coisas diferentes e ordenam vitórias e derrotas de modo diferente; nenhum é custo, e não há limiar de relevância prática. Nas vitórias fora do ajuste, Δ mediano +1,27% (M=2) e +1,39% (M=3); ICs bootstrap em quatro instâncias são sensibilidade local. Engenharia: vitória detectável em 1/3 e ausência de diferença detectável em 2/3, sem inferir ausência de prejuízo. A comparação com os sete algoritmos, inclusive o posto médio, é resposta da QP5 (§8.5; desde a R19, §7.5) e saiu da §7.1 em 2026-10-11. | avaliação comparativa principal na suíte sintética (R15; antes "confirmatória"); apoio em engenharia |
| QP2 | Que diferenças de desempenho são observadas entre as configurações e as variantes de acoplamento avaliadas nos estudos de calibração e ablação do IVF/SPEA2? | §7.2; §8.2 | Resultado comparativo primeiro (desde a R20, na ordem em que os estudos ocorreram). Ablação na configuração inicial (51 instâncias, 60 execuções, Holm): variante com as duas decisões × SPEA2 25/25/1 (IGD) e 28/21/2 (HV); × acoplamento sem as duas decisões 0/50/1 nos dois; Friedman fatorial p = 0,485 entre 16 combinações, todas na configuração inicial. Calibração (12 instâncias, Holm): configuração padrão (C26) × melhor da fase A, IGD 0/12/0 e HV 1/11/0. Os contrastes contra a configuração inicial na calibração saíram do texto na R20 (D2; resposta pronta na §8). Interpretação: as decisões foram mantidas pelo posto médio e pela hipótese de projeto, não por diferença detectada; na configuração inicial, não produziram diferença detectável, o que não as torna irrelevantes; a configuração padrão não se distingue da melhor da fase A (sem equivalência), e a escolha se apoia no posto médio. Alcance: ablação anterior à calibração, fora da configuração padrão, contra braço de outra campanha sem configuração nem orçamento registrados (`OQ-14`); calibração com 50.000 avaliações (§9.1); recálculo de aptidão não separado (`OQ-24`). Questão aberta: atribuição do ganho às decisões, à configuração ou ao recálculo, não isolada. A hipótese de densidade permanece justificativa de projeto. A retenção dos descendentes do módulo foi registrada numa variante instrumentada, em outra coorte (`IVF_V2_TRACE.m`; `results/ivf_trace/representative_cycles.csv`, `selection_rate`), mas essa análise não integra a evidência da dissertação; não escrever que a retenção "não foi medida". | apoio; comparativa; atribuição não isolada |
| QP3 | Como varia o desempenho relativo dos acoplamentos IVF/SPEA2, IVF/NSGA-II e IVF/NSGA-III diante de seus respectivos hospedeiros? | §7.3; §8.3 | Resultado comparativo primeiro, em dois níveis de inferência. (a) Testes de cada acoplamento contra o seu hospedeiro (30 execuções, Wilcoxon, BH por acoplamento e métrica): IVF/SPEA2 IGD 33/15/3, HV 37/10/4; IVF/NSGA-III 22/29/0 e 21/28/2; IVF/NSGA-II 1/48/2 e 5/43/3. (b) Ordenação entre pipelines (SPEA2 > NSGA-III > NSGA-II nos dois indicadores): **descritiva**, sem teste que compare os acoplamentos entre si. Interpretação: os acoplamentos existentes, tal como configurados, não têm o mesmo perfil diante dos seus hospedeiros. Zero derrotas do IVF/NSGA-III e 48 empates do IVF/NSGA-II não são segurança nem equivalência. Alcance: hospedeiro, realização do módulo, recombinação, ativação, configuração e procedimento de ajuste variam juntos; só o IVF/SPEA2 tem calibração documentada nesta suíte (`OQ-25`); a coluna IVF/SPEA2 reutiliza a coorte da comparação principal (`OV-01`). Os estudos de origem (IVF/NSGA-II 2017; tese IVF/NSGA-III 2024) usam outros orçamentos, configurações e testes; divergências e semelhanças não são replicação. Por suíte (descritivo): a WFG é a de menor taxa de vitória em IGD no IVF/SPEA2 (9/6/3) e no IVF/NSGA-III (3/15/0); o IVF/NSGA-II não segue o padrão. Questão aberta: efeito isolado do hospedeiro. Não abrir com "Sim". | comparativa |
| QP4 | Dá para antecipar o benefício, e usar essa informação compensa? | §7.4; §8.4 | Veredito: sinal diagnóstico limitado nesta amostra; o controlador avaliado teve saldo desfavorável em HV diante do sempre ativo (formulação de 2026-10-11; antes, "nenhuma regra de controle vantajosa diante do sempre ativo"). Estático: reanálise com resposta transformada no treino, DTLZ+MaF retidas juntas e escala original, r_s = 0,150; a diferença para o original não é atribuída a um fator isolado. Resumos por instância: BA = 0,754 ao reter suíte ou agrupar DTLZ+MaF, com sinal e janela escolhidos sobre as mesmas 51 instâncias, fora das dobras; decisões coincidem com WFG/demais em 49/51; a partição pós-hoc WFG/demais, sobre os mesmos rótulos, dá BA 0,778 (discordâncias: DTLZ6 M=2 e M=3). Execução: controlador em HV 34/14/3 contra o SPEA2 e 2/40/9 contra o sempre ativo, sem utilidade líquida; faltam registros de decisão por execução. BA não é utilidade; custos assimétricos são hipótese. | diagnóstica |
| QP5 | Como o IVF/SPEA2 se posiciona, em IGD e HV, diante dos sete comparadores de contexto, e em que medida o posicionamento varia com o número de objetivos? | §7.5; §8.5 | Comparação, não superioridade. Mesma coorte da comparação principal (IVF/SPEA2 3001--3060 × comparadores 1--60, 60 execuções), Mann--Whitney bicaudal por instância, Holm por comparador, por M e por métrica, IGD primária e HV secundária; todos os algoritmos na configuração padrão. Vocabulário: **derrota** = instância com diferença corrigida desfavorável; **saldo desfavorável** = contraste (comparador × M × métrica) com mais derrotas que vitórias. 28 contrastes; saldo desfavorável em quatro: NSGA-III (9/2/17) e AR-MOEA (9/5/14) em IGD M=2; SPEA2+SDE (8/1/14) e AGE-MOEA-II (6/1/16) em HV M=3. Saldo favorável: IGD M=2 em 5 de 7; IGD M=3 em 7 de 7 (estreito contra o AGE-MOEA-II, 9/6/8); HV M=2 em 7 de 7; HV M=3 em 5 de 7. Contrastes de saldo favorável também têm derrotas (ex.: NSGA-III e AR-MOEA em HV M=3, 13/0/10; MOEA/D em IGD M=2, 19/1/8); só 3 dos 28 não têm derrota. Complementos descritivos da R20, fixados antes de calculados: $A_{12}$ mediano abaixo de 0,5 nos quatro desfavoráveis (0,143; 0,342; 0,363; 0,134) e no estreito com o AGE-MOEA-II (0,455), 0,728--1,000 nos demais 23; fora do ajuste (39 instâncias), os mesmos quatro contrastes desfavoráveis e os outros 24 favoráveis, o mais estreito AGE-MOEA-II em IGD M=3 (7/3/5); mapas de $A_{12}$ por instância; posto médio de IGD (2º com M=2 atrás do NSGA-III, 1º com M=3) e de HV (1º com M=2, 2º com M=3 atrás do AGE-MOEA-II) — descritivo, divergente da contagem em dois contrastes (AR-MOEA em IGD M=2; SPEA2+SDE em HV M=3). A discordância entre IGD e HV muda de direção entre M=2 e M=3, e o desenho não isola a causa; nenhuma leitura de mecanismo. A expectativa informal do autor de que esses dois comparadores fossem preferíveis não é afirmada no texto. | Posicionamento comparativo; formulada depois das contagens |

Síntese (§8.7, R13; número corrigido na R17): no escopo avaliado (51 instâncias sintéticas, M = 2 e 3, 100.000
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

Atualização de 2026-10-11 (intervenção no Cap. 7; ver §3): as Conclusões (§7.7 na numeração
atual) abrem pelo resultado principal, com escopo e limites, descrevem o controlador pelo saldo
desfavorável em HV diante do sempre ativo, deixam a comparação entre as medianas de Â₁₂ de
derrotas e vitórias só na §7.1 e terminam na contribuição principal: melhora frequente do SPEA2
canônico na suíte avaliada, pequena em deslocamento percentual.

Hipótese (§8.6, não conclusão; era §8.5 até a R17): a WFG concentra os resultados menos favoráveis, já na
família da comparação principal; a recorrência nas outras famílias é, para o IVF/SPEA2, reutilização
(`OV-01`, `OV-02`); das duas colunas com execuções novas, só a do IVF/NSGA-III repete o
padrão, e o IVF/NSGA-II concentra na WFG diferenças nos dois sentidos. A tabulação
exploratória (`C-WFG-01`) restringe a hipótese: o contraste com as demais suítes depende da
configuração (WFG 3/3/3 com M=2 e 5/3/1 com M=3, contra 19/0/0 e 10/4/0 nas demais; a única
derrota com M=3 continua na WFG; K e D mudam com M), duas derrotas estão em instâncias da calibração,
e as derrotas caem nas funções não separáveis (separáveis 6/2/0, não separáveis 2/4/4 em
IGD), sem isolar a propriedade. A WFG também reúne 8 vitórias corrigidas em 18
configurações: não é "marcador das instâncias desfavoráveis". O teste proposto é o desenho
fatorial da §10.1, com M e K/L controlados.

Atualização de 2026-10-11: a §7.6 (numeração atual) formula a hipótese pós-hoc direcional que
esse desenho testaria — a não separabilidade reduz o benefício do IVF/SPEA2 diante do SPEA2, em
interação com M e K —, declara que M, K e D variaram juntos, que a interação não foi identificada
e que outras propriedades das transformações continuam candidatas; a leitura vetada em
`C-WFG-01` ("a candidata que sobra") continua fora do texto.

Regra de redação: cada QP é respondida num único lugar, a seção correspondente do Cap. 7
(Cap. 8 até a R18).
Os outros capítulos remetem a ela e não reenunciam o resultado.

## 3. Estado em 2026-10-11

Rodada R20 (`REWRITE_SPEC.md` §6.2) — revisão do Cap. 6 a partir das anotações do autor.
Decisões do autor: D2, retirar da calibração os contrastes contra a configuração inicial
(braço de outra campanha, sem orçamento nem configuração registrados); D3, "configuração
padrão" para a C26 em todo o texto, apresentada na §6.2; D4, implementações dos acoplamentos
NSGA descritas pelo que a verificação contra as publicações mostrou (IVF/NSGA-III conforme o
artigo do CEC 2023, nova entrada `sampaio2023ivf`); D5, pareamento do par IVF/SPEA2 no Cap. 8;
D6, regressão de paisagem só no procedimento estrito, com os valores do CLEI na §7.8; D7,
cinco complementos descritivos na §6.5, fixados antes de calculados; D8, notas de tabela como
instrução de leitura (perfil §9). Também por decisão do autor saíram do texto a frase sobre
fidelidade não verificada, a frase sobre o histórico do repositório e a frase sobre os
protocolos de origem das configurações NSGA. Estrutura: Tabelas 6.2 e 6.3 fundidas
(`tab:ablacao`; `tab:tuning_c26` aposentado), tabela de robustez eliminada
(`tab:ativacao_robustez`; gerador `build_tab_ativacao_robustez.py` removido, funções levadas a
`build_tab_fla_dinamica.py`), tabela e duas figuras novas na §6.5. Nenhum número das famílias
existentes mudou; os números novos são os da §6.5 ($A_{12}$ mediano, recorte fora do ajuste).
**D1 (fechada em 2026-10-11, decisão do autor):** as divergências de leitura com os artigos
(gatilho, geometria e procedimento da regressão do CLEI) ficam declaradas só na §7.8
(`sec:publicacoes`), com uma frase cada e remissão ao ponto do texto (`eq:gatilho_ivf`,
`sec:resposta_qp1`, `tab:fla_modelos`). Saíram: o rodapé da §4.1, a oração "e o situa diante da
leitura do manuscrito de origem" da §5.3.3, a abertura "O manuscrito de origem associa o ganho às
geometrias regulares" da §7.1.1 e a citação do CLEI na §3.4 (substituída por remissão à §6.4).
`zambrano2026ivfspea2` continua citado na §5.2.3 (protocolo de IGD/HV na engenharia) e na §7.8;
`zambrano2026clei` e `zambrano2026hosts`, só na §7.8.

Intervenção no Cap. 7 (2026-10-11, posterior à R20; candidato à revisão do autor, sem número de
rodada). Hierarquia das respostas: cada QP abre pelo resultado, e as repetições de resultados e
de limites passaram a remissões ao lugar canônico (critério: o limite fica junto da afirmação
quando a sua retirada permitiria leitura errada). Mudanças de força: o controlador passou a
"saldo desfavorável em HV diante do IVF/SPEA2 sempre ativo" (antes, "não superou") no Cap. 7, no
resumo e no abstract; a hipótese da §7.6 ficou direcional e pós-hoc; o abstract passou de
*weakly associated* a *limited predictive performance*; a lógica das duas derrotas em instâncias
da calibração (§7.6) deixou de depender do orçamento. Por instrução do autor nesta data, o título
da §7.5 nomeia os sete algoritmos comparados e a variação com o número de objetivos
(`terminologia.md`). O Cap. 1 (roteiro) passou a "concentração de resultados menos favoráveis na
suíte WFG". Bibliografia: `zambrano2026hosts` descreve o capítulo publicado (LNCS 16986,
p. 284–298, DOI 10.1007/978-3-032-36223-0_18; ano editorial 2027, publicação on-line em
23/08/2026, evento em 2026). **CLEI (fechado em 2026-10-11, informação do autor):** aceito e em
processo de publicação. `zambrano2026clei` descreve a versão final de edição (título "Static
Landscape Features or Early Population Dynamics? Deciding When to Keep an Intensification
Operator in SPEA2", quatro autores, 52nd Latin American Computing Conference, Intelligent Systems
Track, IEEE), sem DOI nem páginas; a §7.8 diz "aceita para publicação". Atualizar DOI e páginas
quando os anais saírem.
Rastreio: `.omp/runs/cap7_intervencao/` (linha de base, diff e verificação).
Complemento (2026-10-11, decisão do autor): a §7.8 passou a listar só os três manuscritos, o
seu status e a parte das famílias que cada um cobre (QP1/QP2/QP5, QP3, QP4), com a frase de que
relatam as mesmas execuções. A enumeração das divergências de leitura (gatilho, `OQ-23`;
geometria regular, `OQ-22`; procedimento da regressão FLA e os valores 0,374/0,380) saiu; como a
D1 já havia retirado essas declarações da §4.1, da §5.3.3, da §7.1.1 e da §3.4, a dissertação não
declara mais as divergências em lugar nenhum — elas ficam só neste plano (§4) e nas erratas por
decidir. Na mesma data, a Tabela 7.1 (`tab:wfg_exploratoria`) perdeu as colunas Modalidade e Viés
e a nota longa; modalidade, viés, protocolo e a leitura das linhas de resumo passaram à prosa da
§7.6 (`build_tab_wfg_exploratoria.py`).

## 3a. Estado em 2026-10-10

Rodada R19 (`REWRITE_SPEC.md` §6.2; relatório rastreável em `RELATORIO_INTERVENCAO_ALTINO.md`)
— resposta aos 64 comentários do revisor externo (A001–A064). Decisões do autor aplicadas:
título preservado (A001 fora da rodada); "Publicações derivadas" no fechamento do Cap. 7
(§7.8); Experimentos e Resultados reunidos no Cap. 5, Experimentação; QP1–QP5 transferidas
da Introdução para a §5.1; Estudos Complementares continua capítulo próprio; respostas às QPs
continuam no capítulo de discussão; apêndices continuam ocultos. Decisões terminológicas
desta rodada (registradas em `skill://scientific-writing-ptbr/references/terminologia.md`):
orçamento × consumo acumulado × cota da geração; métrica primária/secundária no lugar de
"desfecho"; "acoplamento, tal como implementado e configurado" no lugar de "pipeline";
"algoritmos comparados" para os sete; "suíte" no lugar de "família" no sentido de conjunto
de problemas; "instância" no lugar de "configuração problema–objetivo". Nenhum número,
coorte, teste, correção ou veredito de QP mudou; os geradores de 14 tabelas e de uma figura
tiveram só texto alterado (números conferidos idênticos). Pendências e decisões que cabem
ao autor estão no relatório (§G, e §I.9 para o fechamento da mesma data, que corrigiu a
descrição do IVF original, a relação entre indicadores e dominância, a justificativa das 60
execuções, a distinção entre o IVF/NSGA-III publicado e o implementado e os desenhos de
trabalhos futuros).

Decisões do autor na mesma data, posteriores ao fechamento (relatório, §J e §K): os sete
algoritmos comparados são apresentados pela taxonomia do manuscrito de origem, em três famílias
complementares, variantes do SPEA2 (MFO-SPEA2, SPEA2+SDE), métodos canônicos de dominância de
Pareto e de decomposição (NSGA-II, NSGA-III, MOEA/D) e abordagens modernas de adaptação de
geometria e de pontos de referência (AGE-MOEA-II, AR-MOEA). "Posicionamento" saiu do texto
visível, da Tabela 5.1 e da legenda gerada; rótulos, ids e nomes de arquivo ficaram. A família
da Tabela 5.1 chama-se "Algoritmos comparados" e mantém o papel contextual; a regra está em
`terminologia.md`.

## 3b. Estado em 2026-10-03

Rodada R18 concluída (`REWRITE_SPEC.md` §6.2) — atenuação da autocrítica, nível 2, por
decisão do autor. O Cap. 9 passou de 6 para 3 páginas, com cada ameaça reescrita em três
movimentos (ameaça, mitigação, risco residual), e o texto perdeu a repetição das ressalvas
transversais: cada uma aparece completa uma vez, no lugar canônico indicado no contrato da
rodada, e as demais ocorrências remetem. Saíram do corpo do texto, passando a respostas
prontas da §8: versões de MATLAB e PlatEMO dos manuscritos, histórico dos registros de
sondagem da seleção RWMOP, momento de formulação da QP5, análise de convergência omitida,
tempo de relógio, magnitudes como intervalos, pré-processamento pré-dobra do modelo estático
e dados brutos (que ficam no Apêndice B, oculto). Nenhum número, coorte, teste, correção,
citação, remissão ou rótulo mudou, e nenhum veredito de QP foi alterado; `claims.py diff` e
`prose_audit.py` foram rodados por arquivo. O PDF compila com 103 páginas, sem item
bloqueante novo, sem *overfull* e com as três linhas *underfull* da linha de base; resumo e
abstract continuam em uma página cada, e as palavras-chave ficaram nelas. Fica registrada a
reversão, no resumo e no abstract, da precisão "sinal e janela escolhidos antes das dobras"
que o fechamento da R17 havia restaurado: por decisão da R18, ela permanece apenas na §7.4.

Rodada R17 concluída (`REWRITE_SPEC.md` §6.2). Os três apêndices estão ocultados em
`main.tex` por decisão do autor, e os arquivos continuam versionados em `pos/`; a
declaração de disponibilidade de dados fica oculta junto com o Apêndice B e não foi movida
para o corpo. O posicionamento contra os sete comparadores de contexto passou a ser a QP5,
com contagens corrigidas por comparador, por número de objetivos e por métrica, e recebeu
§7.5 no Cap. 7 e §8.5 no Cap. 8; a WFG passou a §8.6 e as Conclusões a §8.7. A Tabela de
famílias tem uma linha a mais, e a nota declara a sobreposição de coorte com a comparação
principal e o intervalo de anos dos comparadores. A tabela nova é gerada por
`src/python/thesis/build_tab_posicionamento.py`, coberto por `make thesis-tables-check`. O
PDF compila sem item bloqueante novo e sem linha *overfull*, e as linhas *underfull* caíram
de quatro para três, com o desaparecimento da linha do apêndice de fontes.

Fechamento da R17 (mesma data, `REWRITE_SPEC.md` §6.2): vocabulário único de *derrota*
(instância) e *saldo desfavorável* (contraste; quatro em 28), sem leitura de mecanismo para a
discordância IGD × HV, restauração limitada aos Apêndices A e B, objetivos na ordem das QPs e
restrição da rederivação aos acoplamentos ao NSGA-II e ao NSGA-III. Nenhum número mudou; só
a nota de `tab_posicionamento.tex` foi regenerada, e os checksums foram reescritos. Resumo e
abstract foram refatorados com autorização do autor e cabem, cada um com as suas
palavras-chave, numa página. O PDF tem 106 páginas, sem item bloqueante novo e sem
*overfull*, com as três linhas *underfull* da linha de base. Pendências do fechamento:
`REWRITE_SPEC.md` §6.3.

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

Rodada R14 (2026-10-01), reenquadramento de QP2 e QP3 sem novas campanhas: as duas questões
passaram a perguntas comparativas sobre os estudos realizados (§2; `REWRITE_SPEC.md` §1.6),
com objetivo geral, objetivos específicos, contribuições, apresentações do Cap. 7, respostas
do Cap. 8, Conclusões, Caps. 9 e 10, resumo e abstract sincronizados. A atribuição às
decisões, à configuração e ao hospedeiro continua não isolada. Registro em
`REWRITE_SPEC.md` §6.2.

Complemento R14b (2026-10-01), continuidade sem novas campanhas: as Conclusões deixaram de
chamar de "mais estreitas" as respostas da QP2 e da QP3; "perfis observados distintos" entre
pipelines; as duas ocorrências restantes de "próximo da neutralidade" viraram contagens; a
Seção 7.3 passou a "Comparação dos acoplamentos com seus hospedeiros"; objetivo geral, OE5 e
QP4 alinhados (informação anterior à execução e da dinâmica inicial; IVF/SPEA2 sempre ativo
como comparador; controlador só pela renovação); resumo e abstract delimitados à regra de
controle avaliada; a anterioridade da IGD e das famílias de Holm deixou de ser afirmada
(`OQ-26`). Registro em `REWRITE_SPEC.md` §6.2.

Rodada R15 (2026-10-01), nomenclatura: a comparação IVF/SPEA2 × SPEA2 na suíte sintética passou a
"avaliação comparativa principal" (opção c de `OQ-26`), em revisão ocorrência a ocorrência da
prosa, do manifesto (papel `primary`) e dos geradores; IGD primária e HV secundário obrigatório
inalterados, e nenhum número, teste, correção ou identificador técnico mudou. Registro em
`REWRITE_SPEC.md` §1.7 e §6.2.

## 4. Decisões do autor e do orientador

Bloqueiam o depósito:

- [x] **`OQ-10` — autoria e reúso (decidido em 2026-10-11).** Decisão do autor: a declaração de
  contribuição e as permissões não são necessárias; a §7.8 mantém só a lista das publicações.
- [x] **`OQ-09` — identidade de release (decidido em 2026-10-11).** Decisão do autor: a
  dissertação cita o DOI de conceito (`10.5281/zenodo.19071253`), conforme
  `docs/RELEASE_IDENTITY.md`; não haverá release próprio da dissertação. Risco aceito: o DOI de
  conceito passa a apontar para versões posteriores à dissertação.
- [x] **Apêndices A, B e C (decidido em 2026-10-11).** Decisão do autor: os Apêndices A e B
  permanecem fora do PDF; o Apêndice C foi aposentado. Registro em
  `RELATORIO_INTERVENCAO_ALTINO.md` §L. `pos/apend_III.tex` foi removido da árvore de trabalho
  (o histórico do git preserva a última versão, cujo comentário de advertência registrava que o
  arquivo contradizia a QP5 e definia `fig:posto_medio`, também definido na §7.5). Se os
  Apêndices A e B voltarem, o procedimento de restauração é:

  A restauração **não desfaz a QP5**: a §7.5 (`sec:posicionamento`) e a §8.5
  (`sec:resposta_qp5`) são o lugar canônico do posicionamento, e as remissões de
  `cap_III.tex:25`, `cap_V.tex:49`, `cap_VI.tex:4`, `cap_VII.tex:15`, o item de ameaça da §9.2
  ("Escolha do hospedeiro", na §9.4 até a R17) e a §10.2 permanecem como estão. Procedimento:
  - `main.tex` — descomentar `\apendices` e os `\input` de `pos/apend_I` e `pos/apend_II`;
    **não** descomentar `pos/apend_III` (define `fig:posto_medio`, também definido na §7.5:
    rótulo duplicado);
  - `tex/cap_VII_complementares.tex` (abertura do capítulo) — o parêntese
    `(Apêndice~\ref{apend:recuperacao})` volta. Desde a R18 o Cap. 9 não tem item sobre dados
    brutos: o Apêndice B é o lugar canônico dessa ressalva;
  - `tex/cap_I.tex` (Organização do texto) — volta a menção aos Apêndices A e B (fontes de
    evidência e disponibilidade dos dados), sem o posicionamento.

  Os rótulos dos Apêndices A e B (`apend:fontes`, `apend:recuperacao`, `sec:disponibilidade`)
  não colidem com nenhum rótulo do corpo, e o Apêndice B só remete a rótulos que existem.
  **Apêndice C:** aposentado em 2026-10-11; `pos/apend_III.tex` foi removido da árvore de
  trabalho e o histórico do git preserva a última versão. A declaração de disponibilidade de
  dados segue oculta com o Apêndice B, de modo que o repositório público e o DOI de conceito
  ficam sem menção no corpo do texto — consequência aceita pelo autor nesta data.

Não bloqueiam o depósito, mas têm prazo próprio:

- [x] **`OQ-26` — rótulo "confirmatória" sem registro temporal do protocolo (nomenclatura decidida na R15).** Fundamento:
  nenhum registro com data independente mostra que a IGD como desfecho primário e as
  famílias de Holm (por `M` e por métrica) foram fixadas antes de os resultados serem
  conhecidos; o Springer declara a IGD "pre-specified", sem carimbo, e o histórico Git e o
  primeiro depósito Zenodo começam em 2026-03-17. A R14b retirou do texto as afirmações de
  anterioridade e manteve o rótulo. Opções e consequências: (a) manter "confirmatória" como
  o papel que o protocolo atribui à QP1, com a ausência de data declarada (§5.3, §5.4) —
  nada muda além do que já está no texto; (b) qualificar o rótulo uma vez, na §5.4 e na
  §9.4, como confirmatória pelo protocolo declarado nos manuscritos, sem pré-registro
  datado; (c) reclassificar como "principal" ou "primária" — exige revisar o termo em todo o
  texto, inclusive Caps. 1, 5, 6, 8, Apêndices e resumo/abstract, e a tabela de famílias.
  Se aparecer registro datado (mensagens, plano submetido, versão anterior do manuscrito),
  a anterioridade pode voltar a ser afirmada com a fonte. **Decisão (R15, 2026-10-01):
  opção (c)**, com o termo "avaliação comparativa principal" (`REWRITE_SPEC.md` §1.7). A
  decisão resolve o nome e o papel da avaliação; a anterioridade continua não verificada.
- [ ] **`OQ-15` — ambiente de execução.** O texto deixou de afirmar versão de campanha na
  R10. Na R18, por decisão do autor, saiu do texto a exposição dos três registros dos
  manuscritos e da incompatibilidade entre o Springer e o PPSN nas execuções `3001–3030`
  (antes na §5.1, na nota da Tabela 5.1 e na §9.4): a §5.1 diz só que a cópia distribuída se
  identifica como a versão 4.6, e a resposta completa está na §8. Resta, fora da
  dissertação, localizar os logs dos runners, se existirem, e decidir errata do Springer
  (legenda da tabela de parâmetros) e do PPSN (ambiente da coluna IVF/SPEA2). Se os logs
  aparecerem, a §5.1 pode passar a afirmar as versões.
  **Decisão do autor (2026-10-11, D2):** a dissertação (§5.2.1, `sec:plataforma`) passa a
  declarar a versão da PlatEMO como "24.2.0.2923080", o identificador do artigo da Memetic
  Computing (`paper/springer-nature/src/sn-article.tex:285`), e a frase sobre o README da
  cópia depositada (4.6) saiu do texto. O autor adotou o identificador sabendo que ele tem
  formato de versão do MATLAB e não coincide com o PPSN nem com o README; a divergência fica
  registrada só aqui e na resposta da §8 ("Em que versões do MATLAB e do PlatEMO…"), sem
  ressalva no texto da dissertação.
- [ ] **`OQ-21`** — o Springer diz que a MaF entra só com três objetivos e não registra
  que o MaF7 repete o DTLZ7, nem que o MaF7 com M = 3, fora do ajuste, é a função do
  DTLZ7 da calibração. Decidir errata.
  **Decisão do autor (2026-10-11, D3):** na dissertação, a repetição MaF7/DTLZ7 e as suas
  consequências (49 pares de função e número de objetivos, nove pares entre as 11
  instâncias irregulares, o MaF7 com M = 3 no recorte fora do ajuste, o agrupamento de DTLZ
  e MaF na reanálise de `tab:ativacao_robustez`) passam a constar só do Cap. 8
  (`sec:validade_interna`, item "Função repetida na suíte"). Saíram do corpo do texto, do
  resumo, do abstract e das notas das tabelas geradas; a §5.2.5 remete a
  `sec:validade_interna`. A errata do Springer continua por decidir.
- [ ] **`OQ-22`** — o resumo e a discussão do Springer associam o ganho às fronteiras
  regulares; a família da comparação principal não sustenta essa leitura para a frequência das
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
- [x] **Fluxograma do SPEA2** (`fig/fluxo_spea2_pt.pdf`). Resolvido em 2026-10-02: a
  figura passou a ter fonte editável (`fig/src/fluxo_spea2_pt.tex`), que reproduz o fluxo
  original; a caixa de preenchimento diz "com as soluções dominadas da união, na ordem de
  F", como a §2.1.4, e saiu o tracejado que a ligava só ao Conjunto Arquivo.
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
- [x] **Referências da linhagem IVF/NSGA-III** (2026-10-02). O artigo CEC 2023 (DOI
  `10.1109/CEC53210.2023.10254062`, metadados conferidos no Crossref; texto integral não
  acessado) não entrou no `.bib`: a tese de 2024, aberta, sustenta cada mecanismo do
  IVF/NSGA-III descrito no Cap. 3, e a dissertação não afirma que a implementação local
  siga um texto específico. Continua fora desta rodada corrigir o comentário de
  `IVF-NSGA-III/IVFNSGAIII.m`, que atribui ao artigo as páginas 2066--2073, do IVF/GDE3.
- [x] **Metadados do `.bib`** (2026-10-02, Crossref). DOIs acrescentados a
  `liefooghe2018landscape` (título corrigido para "Multiobjective"), `zhou2011multiobjective`,
  `kerschke2019automated`, `fialho2008adaptive`, `sampaio2017ivf`, `sampaio2019ivf` e
  `camilo-junior2011`; neste, editor (Eisuke Kita, página da IntechOpen) e páginas 57--68,
  lidas nos cabeçalhos do PDF do capítulo, no lugar de 1--14. A forma "Camilo, Celso G." do
  registro de `sampaio2017ivf` não foi adotada: o nome segue normalizado como Camilo-Junior.
  A frase do Cap. 3 sobre o IVF/GDE3 foi delimitada ao resumo oficial (IEEE Xplore): proposta
  do acoplamento ao GDE3 e desempenho superior ao GDE3 na maioria dos problemas avaliados;
  operador, suíte e hipervolume saíram por não terem conferência primária.

## 5. Pendências institucionais

Confirmar com o orientador e a secretaria do PPGCC:

- [x] **Data de defesa.** 27/10/2026, terça-feira, 14h30, no INF, com participação remota
  dos membros externos (`main.tex:99-101`), definida pelo autor em 2026-10-11. Substitui a
  provisória de 08/11/2026, que caía num domingo. `\publica` é gerada com essa data.
- [ ] **Regulamento aplicável.** CEPEC 1622/2018 (30 dias para a versão final) ou
  1983/2026 (60 dias), conforme o ingresso.
- [ ] **Prazo entre depósito e defesa.** Não consta do regulamento 1622/2018 nem do FAQ
  do programa; confirmar com a secretaria.
- [ ] **Banca** (art. 46 da 1622/2018): três examinadores doutores, ao menos um externo ao
  programa ou à UFG; suplentes interno e externo; aprovação da CPG. O coorientador, se
  participar, não conta para o mínimo. **Solicitada em 2026-10-11** (formulário de
  nomeação, a assinar no SEI pelo orientador e pelo estudante): titulares Ronaldo Martins da
  Costa (presidente, INF/UFG, interno), Hugo Alexandre Dantas do Nascimento (INF/UFG,
  interno) e Karla Tereza Figueiredo Leite (DC/UERJ, externa); suplentes Thierson Couto
  Rosa (INF/UFG) e Maria Bernardes Rebuzzi Vellasco (PUC-Rio); coorientador Celso Gonçalves
  Camilo Junior (INF/UFG) como membro. Falta a nomeação formal.
- [x] Folha de aprovação (`pre/pre_aprovacao.tex`) ativada com essa banca. Falta confirmar o
  nome por extenso da unidade "DC" da UERJ.
- [ ] Declaração do formato monográfico, exigida pela Resolução INF nº 02/2023/PPGCC.
- [ ] Referência ao projeto de pesquisa cadastrado na UFG ao qual a dissertação se
  vincula (art. 40, §1º, da 1622/2018).
- [x] Agradecimento a financiamento ou bolsa: não houve bolsa (informação do autor,
  2026-10-11); dedicatória, agradecimentos e epígrafe ativados em `main.tex`.
- [ ] Conferir a epígrafe (Guimarães Rosa, *Grande Sertão: Veredas*) no exemplar: o texto foi
  conferido só em fontes secundárias concordantes (Rosa, 1994, Nova Aguilar, p. 86).
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

## 7. Cronograma relativo à data de defesa (D = 27/10/2026)

| Quando | Data | Entrega |
|---|---|---|
| D − 5 semanas | 22/09/2026 (passada) | Leitura do orientador; decisões da §4, em especial `OQ-15`; correções da leitura; itens institucionais da §5 |
| D − 4 semanas | 29/09/2026 (passada) | Congelamento: tag e release Zenodo; processo SEI com a versão digital; envio à banca. A tag `dissertacao-R20` foi criada em 2026-10-11, 12 dias depois desta data; os demais itens dependem de secretaria e orientador |
| D − 3 a D − 1 semana | 06/10 a 20/10/2026 | Apresentação em quatro blocos, um por QP; dois ensaios |
| D + 30 dias | 26/11/2026 | Versão final com as correções da banca e depósito na BDTD, se vale a CEPEC 1622/2018 |
| D + 60 dias | 26/12/2026 | Idem, se vale a CEPEC 1983/2026 |

## 8. Perguntas previsíveis da banca

| Pergunta | Onde está a resposta |
|---|---|
| Se a ablação não separa as decisões, qual é a contribuição? | §8.2 e §8.6: a eficácia é da implementação completa, e a atribuição é outra pergunta; contribuições 1 e 3 do §1.3; `OQ-14` |
| O ganho vem do módulo IVF ou de outra diferença entre as implementações? | §4.1, §8.2 e §9.1: o IVF/SPEA2 recalcula a aptidão antes do torneio, e nenhuma comparação separa essa diferença; o controle está em §10.1 (`OQ-24`) |
| O gatilho concentra a intensificação no início da execução? | §4.1 e §4.4: não; limita a fração acumulada e, mesmo com dois ciclos em toda ativação, suspende o módulo em uma de cada 16 gerações, distribuídas ao longo da execução (`OQ-23`). A divergência com o Springer está em nota de rodapé da §4.1 desde a R18 |
| Por que a ablação não foi repetida na configuração promovida? | §7.2 e §10.1: limite declarado, sem nova campanha |
| O ganho importa na prática? | §6.2 e §8.1: nas 51 instâncias, Â₁₂ mediano 0,756 e Δ mediano +1,15% em IGD; não se definiu limiar de relevância prática, e Â₁₂ e Δ medem aspectos diferentes; não há intervalo global de generalização. |
| Por que o NSGA-II quase não se beneficia? | §7.3, §8.3 e §9.2: comparação entre pipelines que diferem em realização do módulo, configuração e procedimento de ajuste; só o IVF/SPEA2 foi calibrado nesta suíte (`OQ-25`); o estudo de origem usou outro orçamento e a melhor configuração por problema. |
| O controlador vale a pena? | §7.4 e §8.4: HV 34/14/3 contra o SPEA2 e 2/40/9 diante do sempre ativo, sem utilidade líquida nem equivalência nos 40 empates; classificação e decisão sob custos assimétricos são perguntas distintas. |
| O limiar exige conhecer a família do problema? | §7.4: cada dobra ajusta limiar sem a família retida; o observável e a janela foram escolhidos antes dessas dobras na mesma linha de evidência, sem validação aninhada. |
| O sinal de renovação é mais que a identidade da suíte? | §7.4, §8.4 e §9.3: nesta amostra, não se distingue dela; 49/51 decisões em resumos de instância coincidem com WFG/demais, e a própria partição, pós-hoc, atinge BA 0,778 contra 0,754; não equivalem a desativações por execução. |
| Se a geometria não separa e as decisões não foram isoladas, o que distingue as instâncias desfavoráveis? | §8.6: hipótese pós-hoc (desde 2026-10-11, direcional: a não separabilidade reduz o benefício do IVF/SPEA2 diante do SPEA2, em interação com M e K), restringida pela Tabela 8.1 (dependência de M, D e K; derrotas só em funções não separáveis; duas derrotas em instâncias da calibração); teste fatorial em §10.1 |
| Por que o Cap. 6 não traz o posicionamento contra os outros algoritmos? | §7.5 e §8.5: o posicionamento é a QP5, com protocolo próprio (Holm por comparador, por número de objetivos e por métrica); o Cap. 6 trata só da avaliação comparativa principal |
| As execuções do IVF/SPEA2 e do SPEA2 foram pareadas na comparação entre hospedeiros? | Cap. 8, item "Pareamento na comparação entre hospedeiros" (desde a R20; antes, §6.3 e nota da Tabela 6.4): os pares NSGA são pareados por execução; o do IVF/SPEA2 é alinhado por ordem, e sem pareamento só uma contagem muda, em HV, de 37/10/4 para 38/9/4 (`OQ-20`) |
| Por que Holm numa família e Benjamini–Hochberg noutra? | §2.5 e §5.6: cada família conserva a correção da análise em que foi originalmente relatada; Holm controla a taxa de erro por família, e BH, a taxa de falsas descobertas; reaplicar outra correção mudaria as contagens sem que os dados mudassem; contagens de famílias diferentes não são somadas, e, onde aparecem lado a lado (tabela de geometria, cuja nota declara os protocolos distintos; o parágrafo da §8.1 que repetia essa nota saiu em 2026-10-11), a diferença não é atribuída a um fator, porque execuções, teste, pareamento e correção mudam juntos |
| Por que "avaliação comparativa principal" e não "confirmatória"? | §5.4: o protocolo é declarado, mas os artefatos não registram quando a IGD e as famílias de Holm foram fixadas em relação aos resultados; "principal" nomeia o papel da avaliação, sem afirmar pré-especificação nem escolha posterior (`OQ-26`) |
| Dá para reexecutar? Os dados brutos estão disponíveis? | Apêndice B (oculto; restaurar antes do depósito). Fora do corpo do texto desde a R18. Resposta: a família principal é regenerável a partir dos dados processados versionados; as de calibração, ablação, engenharia e do controlador são verificáveis contra os artefatos congelados, mas os produtores não executam a partir de uma cópia recém-obtida do repositório, porque os dados brutos não estão versionados; refazer a cadeia anterior aos artefatos exige reexecutar a campanha |
| O recorte fora do ajuste é independente da calibração? | §5.5 e §6.1: não inteiramente; o MaF7 com M = 3 repete o DTLZ7 da calibração, e sem ele o recorte com M = 3 fica em 11/3/0 (`OQ-21`). Desde 2026-10-11 (decisão do autor D3), a repetição consta só do Cap. 8 (`sec:validade_interna`, item "Função repetida na suíte"); a §5.2.5 remete a essa seção, e o corpo do texto, o resumo, o abstract e as notas das tabelas geradas deixaram de mencioná-la |
| Por que 41 instâncias em que o operador "ajuda", se as vitórias corrigidas são 37? | §7.4: o rótulo usa o teste sem correção; quatro empates de Holm entram como "ajuda" (`OV-02`) |
| Em que versões do MATLAB e do PlatEMO as campanhas rodaram? | Fora do texto desde a R18 (§5.1 diz só que a cópia distribuída se identifica como 4.6). Resposta: não é verificável, porque os registros de execução do MATLAB não estão no repositório. O Springer registra como versão do PlatEMO o identificador 24.2.0.2923080, que tem o formato do número de versão do MATLAB (24.2 corresponde ao R2024b); o PPSN registra MATLAB R2025b com PlatEMO 4.6; o CLEI não registra versão. Como a coluna IVF/SPEA2 da comparação entre hospedeiros reutiliza execuções da coorte principal, os dois primeiros registros não podem estar ambos certos. Nenhuma contagem depende disso: todas são calculadas a partir dos artefatos (`OQ-15`). Desde 2026-10-11 (decisão do autor D2), a §5.2.1 declara a versão 24.2.0.2923080, como o Springer, e a frase sobre o README (4.6) saiu do texto; a divergência com o PPSN e com o README continua registrada só aqui e em `OQ-15`, sem ressalva na dissertação |
| O artigo diz que a geometria da fronteira modera o ganho. Por que a dissertação não? | §8.1, com as contagens da §6.3: a divergência é declarada uma vez; a frequência das vitórias não muda com a geometria, e as derrotas irregulares são um único problema (`OQ-22`) |
| Por que não há análise de convergência, se os manuscritos de origem a reportam? | Fora do texto desde a R18; a §5.3 declara o escopo (aproximação final) e a §10.2 propõe a análise. Resposta: os manuscritos reportam trajetória com 100 pontos de verificação por execução; o artefato disponível no repositório tem dez pontos por execução, e o par IVF/SPEA2 × SPEA2 está ausente das estatísticas de convergência porque o teste pareia execuções por identificador e as faixas 3001–3060 e 1–60 não se intersectam (`OQ-02`, `OQ-03`, `OQ-04`). Em vez de reportar uma análise que os artefatos não sustentam, a dissertação se restringe ao desfecho final; qualidade final e velocidade de convergência são propriedades distintas, e o desfecho final não mostra que o operador acelere a busca |
| Por que não há comparação de tempo de execução? | §4.5 (uma frase) desde a R18. Resposta: a base consolidada registra tempos, mas os ambientes das campanhas não são verificáveis, os resumos de tempo disponíveis usam formas de agregação distintas e não foram reconciliados quanto a coortes e filtros, e não houve comparação controlada do custo do módulo; a comparação é normalizada por avaliações, e a §4.5 dá a análise assintótica, que não substitui uma medida comparável de sobrecarga |
| Quando a QP5 foi formulada? | Fora do texto desde a R18 (§1.2 diz que QP2, QP3 e QP5 são perguntas comparativas, sem hipótese fixada antes dos estudos). Resposta: na R17, depois de calculadas as contagens que a respondem; por isso o posicionamento é comparação, não teste de superioridade, e o posto médio é descritivo |
| Como os três problemas de engenharia foram escolhidos? | §7.1 traz os critérios e as exclusões; o histórico dos registros saiu do texto na R18. Resposta: o Springer relata como critérios dois ou três objetivos, o mesmo orçamento da suíte sintética, soluções viáveis não dominadas para o IVF/SPEA2 e IGD e HV com cobertura de execuções comuns, e descreve uma sondagem com uma execução por candidato; há um registro anterior dessa sondagem para a formulação inicial, distinto do registro de cinco execuções por candidato do IVF/SPEA2 avaliado. Nesse registro, RWMOP13, RWMOP20, RWMOP24 e RWMOP29 não produziram solução viável em nenhuma das cinco execuções. A saída da triagem completa com todos os algoritmos não está disponível para esses quatro candidatos, nem há registro contemporâneo que comprove a fixação dos critérios antes da campanha. O RWMOP9 foi mantido como problema de continuidade; o RWMOP8, desfavorável na triagem disponível, também foi mantido, com cobertura parcial ou nula em dois comparadores, o que impede verificar a aplicação integral do critério de disponibilidade de métricas. A retenção de um caso adverso limita a seleção só de resultados favoráveis, mas não elimina o viés de seleção |
| O modelo estático do estudo de ativação tinha vazamento entre treino e teste? | Desde a R20, a Tabela 6.6 traz só o procedimento estrito, e a §7.8 registra o do artigo. Resposta: no artigo do CLEI, os postos da resposta foram calculados nas 51 instâncias antes da separação entre treino e teste, e a validação por suíte deixava o par funcional MaF7/DTLZ7 atravessar treino e teste ($r_s$ 0,374 ao reter uma instância e 0,380 ao reter uma suíte; a §7.8 separa os dois valores desde 2026-10-11). Com a transformação da resposta ajustada no treino e DTLZ e MaF retidas juntas, $r_s$ = 0,286 ao reter uma instância e 0,150 ao reter uma suíte; o procedimento muda também a escala do alvo e não quantifica separadamente quanto cada fator alterou os números publicados (`OQ-13`, `OQ-16`). Os classificadores continuam com uma suíte por dobra (Cap. 8, "Função repetida na suíte") |
| As implementações do IVF/NSGA-II e do IVF/NSGA-III são fiéis às publicações? | §3.1 e Cap. 8 (desde a R20). Resposta, pela conferência de 2026-10-11 contra `references/ivfnsga2.pdf`, `references/ivfnsga3.pdf` e o código: o IVF/NSGA-II segue os mecanismos de 2017 (coleta por posto e aglomeração, doador inicial, SBX, continuação por objetivo designado, ativação probabilística), na variante AR, com escolhas que o artigo não especifica (um descendente por par, probabilidade de recombinação 1 contra 0,9 do artigo, teto de $N$ avaliações por chamada, desconto das avaliações do módulo no hospedeiro); o IVF/NSGA-III segue o critério de substituição do CEC 2023 (melhora estrita da distância ao nicho-alvo, sem a condição de não dominância que a tese de 2024 acrescenta) e faz uma única coleta local, pelos mais próximos do doador primário, sem a alternativa por proximidade aos próprios nichos |
| O código do IVF/NSGA-III é o que gerou as execuções 5001--5030? | Fora do texto desde a R20, por decisão do autor. Resposta: o histórico do repositório começa num commit único de 2026-04-17, posterior às execuções, e não permite reconstituir o código da campanha; o autor responde pela correspondência |
| A configuração padrão supera a configuração inicial? | Fora do texto desde a R20 (D2). Resposta: nas 12 instâncias da calibração, a C26 registra 4/8/0 em IGD e 4/7/1 em HV contra as execuções 1--60 do rótulo `IVFSPEA2` (a melhor da fase A, 4/8/0 e 3/8/1), mas esse braço muda também a formulação (sem as duas decisões), tem 60 execuções contra 30 e não tem orçamento nem configuração registrados; nenhum fator se isola. Os runners do repositório com 60 execuções usam 100.000 avaliações, e o tempo mediano desse braço é 1,25--1,31 vez o do SPEA2 com 100.000, o que é compatível com 100.000 e não com 50.000 [inferência: campanhas e máquinas podem diferir] |
