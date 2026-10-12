# Terminologia

Fonte canônica: `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md` §4 (vocabulário) e §4.1
(proibição de versionamento). Esta tabela **completa** aquela com o uso efetivo do texto em
2026-09-24 (contagens em `tex/*.tex`); não a substitui. Em conflito, vale o perfil.

**Ratificação do autor (2026-10-11).** Todas as decisões terminológicas da R19 (G-2,
`RELATORIO_INTERVENCAO_ALTINO.md` §G) foram ratificadas sem exceção: orçamento de avaliações
distinto de consumo acumulado e de cota da geração; métrica primária/secundária no lugar de
"desfecho"; acoplamento no lugar de *pipeline*; algoritmos comparados; suíte; instância distinta
de configuração e de variante de acoplamento; "IVF/SPEA2 sempre ativo". "Paisagem de aptidão"
(G-3) mantida — ver linha abaixo.

## Regra de decisão para termo novo

1. Existe forma portuguesa usada na literatura brasileira da área que preserva o referente?
   Usar a forma portuguesa.
2. A tradução cria ambiguidade ou é incomum na área? Manter o termo inglês em itálico, definir
   na primeira ocorrência e não alternar depois.
3. Registrar a decisão aqui (com a data) antes de usar o termo em mais de um capítulo.

Não trocar termo técnico por sinônimo para evitar repetição. Não "corrigir" para purismo uma forma
já consolidada no texto sem decisão do autor.

## Formas em uso

| Conceito (inglês) | Forma no texto | Uso | Observação |
|---|---|---|---|
| fitness | aptidão | 57 | *fitness* só em rótulos LaTeX. |
| fitness landscape / landscape analysis | paisagem de aptidão; análise de paisagem (FLA) | 22 | Sigla FLA definida uma vez. **Decisão do autor (2026-10-11, G-3):** mantido "paisagem" contra a sugestão do revisor (A011, A016, "superfície de aptidão"). Justificativa registrada: a tripla espaço–vizinhança–função de Liefooghe et al. (§2.5) não é uma superfície em espaços discretos. |
| host (algorithm) | hospedeiro | 128 | — |
| coupling | acoplamento | 80 | Distingue formulações; nunca "versão" (§4.1). |
| run | execução | 107 | "execuções `3001–3060`" identifica coorte. |
| seed | semente | 7 | — |
| benchmark suite | suíte (de problemas de teste) | 60 | *benchmark* só quando necessário (perfil §4). |
| tuning | calibração (as três fases); ajuste | 40 / 11 | "fora do ajuste" = as 39 instâncias não usadas na calibração. |
| turnover (dinâmica) | renovação | 25 | *turnover* só em rótulo de figura. |
| exploration / exploitation | exploração e intensificação | — | Correspondência declarada em itálico no Cap. 2. |
| IGD | distância geracional invertida (IGD) | — | Métrica primária (R19: "desfecho primário" saiu da prosa); menor é melhor. |
| HV | hipervolume (HV) | 7 | Métrica secundária obrigatória; maior é melhor. |
| Vargha–Delaney A12 | estatística $A_{12}$ de Vargha e Delaney; "$A_{12}$ orientado" | 29 (texto + tabelas) | Mesma notação $A_{12}$ em prosa e tabelas geradas. Definida genericamente (duas amostras) antes da aplicação a execuções (Cap. 2, R19). |
| baseline | comparador principal (SPEA2); algoritmos comparados (os sete) | — | "linha de base" não é usado. R19: "comparadores de contexto", "demais comparadores" e "comparadores modernos" saíram; "comparador" só para o braço de um teste par a par. **Decisão do autor (2026-10-10, versão final, substitui a regra de "estado da arte" da mesma data):** a taxonomia é a do manuscrito de origem (`sn-article.tex:280`): três famílias complementares relevantes para a questão do acoplamento ao hospedeiro, **variantes do SPEA2** (MFO-SPEA2, SPEA2+SDE; "host-centered SPEA2 variants"), **métodos canônicos** de dominância de Pareto e de decomposição (NSGA-II, NSGA-III, MOEA/D) e **abordagens modernas** de adaptação de geometria e de pontos de referência (AGE-MOEA-II, AR-MOEA). Não usar "estado da arte" para os sete (o artigo não usa); não adotar do artigo a justificativa "often competitive" (enfraquecida na R19, N20). Definição canônica na §5.2.1. |
| leave-one-family-out validation | validação deixa-uma-família (nome do esquema), definida como retenção de uma suíte por vez; "fora das suítes de treino" | — | Leitura da dissertação difere da do CLEI (`OQ-16`). R19: "família" sozinha designa família de evidência; família estatística é "família de hipóteses"; conjunto de problemas é "suíte". |
| many-objective | *many-objective* (itálico) | 2 | Sem tradução consolidada. |
| preprint | *preprint* (itálico) | 1 | — |
| pipeline | acoplamento, "tal como implementado e configurado" | 0 (R19) | **Decisão da R19 (instrução do autor na tarefa da rodada):** o termo saiu de `tex/` e `pre/`; a §6.3 define acoplamento como hospedeiro + realização do módulo + configuração. Permanece em notas internas e no Apêndice A oculto (`build_apendice_fontes.py`). |
| positioning (QP5) | comparação com os sete algoritmos comparados; família "Algoritmos comparados" (Tabela 5.1); título da §6.5 nomeia as três famílias; o da §7.5 nomeia os sete algoritmos comparados e a variação com o número de objetivos | 0 (2026-10-10) | **Decisão do autor (2026-10-10):** "posicionamento" e "se posiciona" saíram do texto visível, da legenda gerada (`build_tab_posicionamento.py`) e do Apêndice A oculto, embora o artigo use "positioning" (comentário A051 do revisor). Rótulos `sec:posicionamento`, `tab:posicionamento`, o id `context-comparator-positioning` e nomes de arquivo ficam (invariante). "Posicionamento" no sentido de situar a proposta na literatura (Cap. 3) não é afetado. **Instrução do autor (2026-10-11, intervenção no Cap. 7):** o título da §7.5 deixou de referir "três famílias de algoritmos", porque o corpo da seção restringe a leitura aos sete algoritmos, e não às famílias de métodos que eles representam; a taxonomia das três famílias continua definida na §5.2.1 e usada no corpo das §6.5 e §7.5. |
| unfavourable balance | *saldo desfavorável* = contraste com mais derrotas do que vitórias, sendo *derrota* a instância com diferença corrigida desfavorável ao IVF/SPEA2 (definição da §6.5); *saldo favorável*, o inverso | — | **R17** (vocabulário da QP5). **Instrução do autor (2026-10-11, intervenção no Cap. 7):** o termo vale também para o controlador diante do IVF/SPEA2 sempre ativo em HV (2/40/9), na §7.4, nas Conclusões e no resumo; o abstract usa *recorded more losses than wins*. Descreve contagem de instâncias, e não prejuízo médio, utilidade líquida negativa ou inferioridade geral. |
| budget | orçamento de avaliações = número máximo de avaliações por execução; condição de comparação: "com a mesma quantidade de avaliações das funções objetivo" | — | **R19.** Distinguir de consumo acumulado ($FE$, $FE_{\text{IVF}}$) e cota da geração ($N$ avaliações). Não usar "orçamento" para número de execuções nem "operador orçado". **Decisão do autor (2026-10-11):** toda frase que declara a igualdade de orçamento entre algoritmos usa "com a mesma quantidade de avaliações das funções objetivo" (variações de regência: "dispõem da", "usa a ... que o hospedeiro"); saíram "com o mesmo orçamento de avaliações", "sob o mesmo orçamento", "o orçamento é o mesmo" e "com o mesmo número de avaliações das funções objetivo" (resumo e objetivo geral). "Orçamento" continua como termo técnico definido no Cap. 1 e na §4.1 ($FE_{\max}$, valores como 100.000 ou 50.000 avaliações, frações como "20\% do orçamento"). Abstract: *under the same number of objective-function evaluations*. |
| endpoint / test outcome | métrica primária/secundária; resultado (corrigido) do teste; qualidade da aproximação final | — | **R19.** "Desfecho" tinha três sentidos e saiu da prosa e das notas das tabelas visíveis. |
| configuration / instance | configuração = valores dos parâmetros do módulo; instância = problema × número de objetivos; variante de acoplamento = presença ou ausência de decisões | — | **R19.** "Configuração problema–objetivo" e "configuração" no sentido de $M$ saíram. |
| always-on | IVF/SPEA2 sempre ativo | — | **R19.** Sem controlador que desligue o módulo; o gatilho de avaliações continua a valer (§6.4). |
| primary donor / secondary donor (father / mother) | doador primário / doador secundário; conjunto de candidatos a doador primário | — | **Decisão do autor, 2026-10-03.** Substitui "pai"/"mãe" em `tex/` e `pre/` (Algoritmo 4.1: $\mathbf{s}_i$, $\mathbf{p}_i$; rótulos "Secundários" e "Candidatos"). A decisão H1 chama-se "seleção de doador primário dissimilar"; o rótulo `sec:pai_dissimilar` fica. "Progenitor(es)" só como termo genérico para qualquer dos dois. O abstract usa *primary donor* e *secondary donor*. |
| default configuration | configuração padrão (do IVF/SPEA2, a C26; dos demais algoritmos, a publicada na plataforma ou a da implementação) | — | **Decisão do autor (2026-10-11, D3):** substitui "configuração promovida" e "configuração calibrada" em `tex/`; apresentada na §6.2, onde a calibração a fixa. Nomes fixos das demais: "configuração inicial" ($c=0{,}11$, $r=0{,}10$, $m=0$, $v=0$, $\ell=3$; sem "não ajustada"), "melhor configuração da fase A", "acoplamento sem as duas decisões" (o braço da ablação; saíram "formulação anterior", "braço histórico" e "comparador histórico"). Toda comparação de desempenho é padrão × padrão; a ablação e a calibração, por definição, não. |

## Nomes próprios e rótulos

- IVF/SPEA2, IVF/NSGA-II, IVF/NSGA-III, IVF/GDE3 com barra; SPEA2, NSGA-II, NSGA-III, MOEA/D.
- Suítes: ZDT, DTLZ, WFG, MaF, RWMOP.
- Plataforma: PlatEMO. Classe da implementação: `IVFSPEA2V2`, só no apêndice (perfil §4).
- QP1–QP5 para as questões de pesquisa (apresentadas na §5.1 desde a R19; a Introdução não usa os códigos); C26 para a configuração padrão do IVF/SPEA2 (até 2026-10-11, "configuração promovida").

## Artigos em inglês

Os artigos (`paper/*`) usam os termos ingleses equivalentes (fitness, host, coupling, run,
turnover, benchmark). A disciplina de evidência é a mesma; a tabela acima vale só para a
dissertação.
