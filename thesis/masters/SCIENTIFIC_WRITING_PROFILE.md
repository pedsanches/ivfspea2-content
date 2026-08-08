# Perfil científico e editorial da dissertação IVF/SPEA2

Este arquivo especializa a skill pessoal `$write-scientific-manuscripts` para a
dissertação de mestrado em Ciência da Computação do PPGCC/UFG. Ele é obrigatório
em toda criação, revisão, tradução, síntese ou reorganização de texto da
dissertação.

## 1. Autoridades e precedência

Aplicar as regras nesta ordem:

1. normas vigentes da UFG e do PPGCC aplicáveis ao discente;
2. decisões documentadas do autor e do orientador;
3. este perfil, `AGENTS.md` e o modelo de evidências do repositório;
4. instruções gerais de `$write-scientific-manuscripts`;
5. preferências editoriais genéricas.

Em caso de conflito, não decidir silenciosamente. Registrar a divergência,
identificar a autoridade aplicável e solicitar a decisão do autor/orientador
quando ela puder alterar o produto acadêmico.

Fontes institucionais verificadas em 26 de julho de 2026:

- [Legislação e normativas do PPGCC/UFG](https://ppgcc.inf.ufg.br/p/35372-legislacao-e-normativas);
- [Resolução INF nº 02/2023/PPGCC — formatos de dissertações e teses](https://files.cercomp.ufg.br/weby/up/1289/o/Resolucao_PPGCC_n_02_2023_Formato_de_dissertacoes_teses.pdf);
- [Orientações do SIBI/UFG para normalização](https://bc.ufg.br/n/35519-orientacoes-para-normalizacao-de-trabalhos-academicos);
- [Procedimentos de depósito na BDTD/UFG](https://bc.ufg.br/n/33055-procedimentos-para-envio-das-teses-e-dissertacoes-para-publicacao-na-bdtd).

A página do PPGCC distingue regulamentos conforme data de ingresso ou migração.
Confirmar a situação acadêmica do autor antes de declarar qual resolução geral
se aplica.

Também consultar:

- [Guia de Integridade Acadêmica da UFG, edição de 2024](https://files.cercomp.ufg.br/weby/up/680/o/Guia_de_integridade_acade%CC%82mica_-_2024_-_com_alterac%CC%A7o%CC%83es.pdf);
- [Política de Integridade na Atividade Científica do CNPq](https://www.gov.br/cnpq/pt-br/composicao/comissao-de-integridade/documentos),
  quando aplicável.

## 2. Formato acadêmico

A Resolução INF nº 02/2023/PPGCC admite:

- modelo tradicional ou monográfico; e
- modelo alternativo ou escandinavo.

A fonte importada está organizada como monografia. Portanto, o estado
operacional desta árvore é **monográfico** até que autor e orientador
documentem outra decisão. Não converter o texto em coletânea de artigos por
inferência.

Antes do depósito, confirmar formalmente o modelo com o orientador e inserir no
documento a declaração do formato no local exigido pela resolução e pelo
modelo institucional vigente. A árvore atual ainda não contém essa declaração;
o estado operacional deste perfil não a substitui.

Se o modelo escandinavo for escolhido, replanejar formalmente a arquitetura.
Para mestrado, a resolução exige pelo menos dois artigos complementares, o
discente como autor principal, o orientador como coautor, introdução geral,
integração explícita entre os artigos, conclusão geral e os demais elementos e
comprovantes previstos na norma. A simples concatenação dos artigos não atende a
essa função integradora.

Nesse caso, conferir literalmente antes do depósito: complementaridade e
quantidade dos artigos; autoria; situação editorial, veículo, métricas de
qualidade e idioma; descrição da relação entre os artigos; conteúdo integral em
formatação autorizada; capítulos adicionais quando o detalhamento for
insuficiente; síntese e conclusão gerais; elementos pré/pós-textuais; referências
e anexos; comprovantes de submissão/aceite; menção ao vínculo e aos
financiamentos; permissões de reuso de texto, figuras e tabelas.

Mesmo no modelo monográfico, os artigos são fontes de conhecimento e evidência,
não blocos para copiar. Reescrever o conteúdo de acordo com a pergunta global da
dissertação, declarar sobreposições e preservar direitos de reutilização.

## 3. Idioma e voz

- Idioma principal: português brasileiro formal e natural.
- Resumo em português e abstract em inglês devem comunicar a mesma evidência,
  sem tradução literal.
- A voz deve ser autoral, precisa e sóbria. Formalidade não implica frases
  longas, passivas ou impessoais.
- Primeira pessoa do plural é permitida quando identifica uma ação dos autores
  e permanece compatível com a orientação institucional. Não alternar
  arbitrariamente entre “avaliamos”, “avaliou-se” e “foi avaliado”.
- Preferir sujeitos e operações explícitos: “O IVF/SPEA2 seleciona...”, “A
  análise compara...”, “Os experimentos usam...”.
- Conservar termos técnicos quando necessários, mas explicar o conceito na
  primeira ocorrência e usar a mesma forma ao longo do documento.
- Não introduzir erros, coloquialismos artificiais ou variação aleatória para
  parecer humano. A autoria se manifesta em decisões científicas específicas,
  não em imperfeições fabricadas.

### Transparência sobre inteligência artificial

- Acordar com o orientador se, onde e como ferramentas de IA podem ser usadas.
- Tratar a ferramenta como apoio, nunca como autora ou fonte científica.
- Verificar criticamente toda saída e todas as fontes; a responsabilidade é
  humana.
- Não fornecer a serviço não aprovado dados sigilosos, pareceres, pedidos de
  patente ou material inédito cuja exposição possa comprometer direitos ou
  publicação.
- Registrar cada lote material de uso em `AI_ASSISTANCE_LOG.md`, com ferramenta,
  finalidade, partes afetadas, verificação e limitações.
- Antes do depósito ou de uma submissão, confirmar a declaração exigida pela
  UFG, pelo PPGCC, pelo CNPq e pelo veículo. A Portaria CNPq nº 2.664/2026,
  quando aplicável, exige declaração do uso de IA generativa, da ferramenta e da
  finalidade em qualquer fase da pesquisa.

## 4. Vocabulário canônico

Usar estas formas, salvo decisão explícita em contrário:

| Conceito | Forma preferida | Observação |
|---|---|---|
| problema | problema de otimização multiobjetivo | Evitar alternância com “multi-objetivo”. |
| área | otimização multiobjetivo | Forma aglutinada. |
| algoritmo | algoritmo evolutivo multiobjetivo | Definir MOEA na primeira ocorrência quando a sigla for útil. |
| IVF | método de fertilização *in vitro* (IVF) | Usar IVF sem itálico depois da definição; preservar IVF/SPEA2 como rótulo. |
| proposta atual | IVF/SPEA2 v2 | No texto de apresentação, pode-se usar IVF/SPEA2 após deixar claro que se trata da v2. |
| implementação | `IVFSPEA2V2` | Nome de classe em fonte monoespaçada. |
| versão histórica | IVF/SPEA2 v1 ou `IVFSPEA2` | Nunca fundir resultados ou parâmetros com a v2. |
| conjuntos de teste | suítes de problemas de teste | Usar *benchmark* apenas quando necessário; não alternar por elegância. |
| busca | exploração e intensificação | Definir a correspondência com *exploration*/*exploitation* se ela for discutida. |
| relação conflitante | equilíbrio ou compromisso entre X e Y | Reservar *trade-off* para casos em que o termo técnico acrescente precisão. |
| Pareto | fronteira de Pareto; dominância de Pareto | Manter maiúscula no nome próprio. |
| métricas | IGD e HV | Definir nome, direção e interpretação na primeira ocorrência metodológica. |

Não trocar um termo técnico preciso por sinônimo apenas para evitar repetição.
A repetição controlada preserva o referente.

## 5. Identidade científica atual

O texto importado em 2025 é um registro histórico, não a fonte científica
vigente. Toda afirmação sobre método, parâmetros ou resultados deve ser
sincronizada com:

- `docs/IVFSPEA2_EVIDENCE_MODEL.md`;
- `results/SUBMISSION_EVIDENCE_MAP.md`;
- `thesis/masters/data-sources.toml`;
- artefatos e scripts declarados nesses documentos.

Este perfil organiza e restringe o uso das fontes, mas não é a fonte primária
dos números. Antes de inserir ou atualizar um valor, conferir o artefato
canônico e seu produtor. Valores resumidos aqui servem para detectar
inconsistências, não para substituir essa verificação.

Identidade canônica:

- implementação principal: `IVFSPEA2V2`;
- rótulo de apresentação: IVF/SPEA2;
- configuração promovida: C26;
- parâmetros: `C=0.12`, `R=0.225`, `M=0.3`, `V=0.1`,
  `Cycles=2`;
- H1: seleção de pai dissimilar;
- H2: critério coletivo de continuação dos ciclos;
- escopo sintético principal: 51 instâncias ZDT, DTLZ, WFG e MaF;
- coorte IVF/SPEA2 v2: execuções `3001–3060`;
- coorte dos baselines: execuções `1–60`;
- orçamento sintético comum: 100.000 avaliações de função;
- IGD: desfecho primário, menor é melhor;
- HV: desfecho secundário obrigatório, maior é melhor.

A v1 deve aparecer apenas em contexto histórico, reprodução da submissão
original ou comparação explicitamente rotulada.

## 6. Famílias de evidência dos artigos

Quatro manuscritos representam três famílias de evidência:

| Família | Manuscrito(s) | Papel na dissertação |
|---|---|---|
| validação IVF/SPEA2 v2 | `paper/springer-nature/` | Evidência confirmatória principal contra SPEA2; posicionamento multibaseline, engenharia, tuning e ablação têm papéis auxiliares distintos. |
| decisão de uso do operador | `paper/ppsn2026/` e `paper/clei2026/` | Uma única família sobre FLA, dinâmica inicial e controlador; as duas versões editoriais não são réplicas independentes. |
| compatibilidade operador–host | `paper/ppsn2026-ivf-hosts/` | Comparação dos pipelines IVF/SPEA2, IVF/NSGA-II e IVF/NSGA-III; não isola causalmente apenas o efeito do host. |

O manifesto `data-sources.toml` apresenta quatro famílias no total porque
registra também `ivfspea2-v1-history`, a família histórica da dissertação
importada. As três famílias da tabela acima correspondem aos quatro manuscritos
atuais que serão absorvidos.

Regras:

- não contar PPSN e CLEI como duas validações;
- não contar os runs `3001–3030` e `1–30` reutilizados no artigo Hosts como
  nova replicação da evidência principal;
- não combinar evidências apenas porque algoritmo, problema ou métrica têm o
  mesmo nome;
- manter como chave conceitual ao menos família de evidência, coorte, versão do
  algoritmo, problema, número de objetivos, execução e métrica;
- declarar sobreposição, pareamento e proveniência;
- reconciliar a afirmação de 100 checkpoints do manuscrito Hosts com o
  `hosts_convergence.csv` atual, que contém dez checkpoints, antes de citá-la;
- tratar `ppsn_trajectories.csv` como parcial/legado, não como fonte da suíte
  completa;
- usar o controlador OOS congelado indicado em `data-sources.toml`, não um CSV
  genérico anterior.

## 7. Hierarquia inferencial

### Confirmação principal

Pergunta: sob orçamento fixo, o IVF/SPEA2 v2 melhora o SPEA2 canônico na suíte
sintética declarada?

- comparação principal: IVF/SPEA2 v2 × SPEA2;
- 60 execuções por algoritmo;
- 51 instâncias sintéticas, sem RWMOP;
- 39 instâncias fora do ajuste e 12 usadas no tuning devem permanecer
  identificáveis;
- IGD primário;
- HV secundário;
- correção de Holm para a família confirmatória definida.

Protocolo canônico para as contagens inferenciais do resumo e da conclusão:

- teste bicaudal de Mann–Whitney U, também denominado Wilcoxon rank-sum, para
  as coortes de execuções independentes;
- `alpha=0,05`;
- correção de Holm aplicada separadamente às comparações IVF/SPEA2 × SPEA2 de
  todas as instâncias de cada número de objetivos (`M`) e de cada métrica;
- o recorte fora do ajuste é obtido após a correção da família completa;
- fonte geradora: `src/python/analysis/compute_claims_summary.py`;
- auditoria persistida: `results/tables/claims_summary_audit.csv`;
- índice humano: `results/SUBMISSION_EVIDENCE_MAP.md`.

Somente esses artefatos podem sustentar linguagem de contagem
“Holm-corrigida”. Os indicadores de
`generate_per_instance_tables.py` e
`generate_ivf_benchmark_five_figures.py` usam testes não corrigidos e devem ser
rotulados como descritivos/exploratórios; não podem substituir a fonte
confirmatória. Antes de atualizar o texto final, confirmar que a auditoria
canônica foi regenerada e contém `p_raw`, `p_holm`, família, direção e cobertura.
Relatar, além do teste, resumo descritivo e magnitude de efeito quando
aplicáveis.

### Suporte

- multibaseline: posicionamento exploratório;
- engenharia: transferência externa de força inferior e resultados mistos;
- tuning e ablação: justificativa da implementação/configuração;
- FLA e dinâmica: interpretação e decisão de ativação;
- controlador: avaliação OOS com seu próprio desfecho primário declarado;
- hosts: compatibilidade entre pipelines, não prova causal isolada do host.

Não promover uma análise de suporte a “prova principal” para fortalecer a
narrativa.

## 8. Linguagem de resultados

Cada afirmação comparativa deve conter ou tornar recuperáveis:

- algoritmo e versão;
- comparador;
- métrica e direção;
- instâncias/coorte;
- número de execuções;
- orçamento;
- magnitude e resumo descritivo, quando aplicáveis;
- teste, pareamento e multiplicidade, quando houver;
- limite da generalização.

Formulações compatíveis:

- “No escopo sintético avaliado e sob o mesmo orçamento, o IVF/SPEA2 v2
  apresentou melhora delimitada em relação ao SPEA2.”
- “O HV fornece suporte secundário ao padrão observado no IGD.”
- “A comparação com os demais baselines tem caráter exploratório.”
- “A transferência para problemas de engenharia produziu resultados mistos.”
- “O padrão é consistente com a interpretação de..., mas não isola o mecanismo.”

Formulações incompatíveis sem nova evidência:

- “é o melhor algoritmo em geral”;
- “supera todos os algoritmos do estado da arte”;
- “comprova superioridade universal”;
- “garante convergência e diversidade superiores”;
- “o mecanismo foi definitivamente validado”;
- “os quatro artigos oferecem quatro confirmações independentes”.

Evitar “estatisticamente significativo” sem teste e família definidos. Não
interpretar `p > 0,05` como igualdade nem significância estatística como
importância prática.

## 9. Regras contra prosa formulaica

Na revisão desta dissertação, buscar especificamente:

- aberturas repetidas por “Neste contexto”, “Além disso”, “Ademais”, “Dessa
  forma” e “Nesse sentido”;
- ênfases vazias como “é importante destacar”, “vale ressaltar” e “cabe
  mencionar”;
- adjetivos sem operação ou evidência: “abrangente”, “considerável”, “eficaz”,
  “inovador”, “promissor”, “robusto”, “sofisticado”, “superior”;
- parágrafos que terminam sempre com uma afirmação genérica de relevância;
- sequências uniformes de quatro ou cinco frases com a mesma cadência;
- traduções literais do inglês, especialmente “endereçar o problema”,
  “performar”, “através do método” e substantivos empilhados;
- construções passivas em série: “foi realizada”, “foi efetuada”, “foi
  conduzida”;
- demonstrativos sem referente: “isso”, “esse resultado”, “tal abordagem”;
- substituição ornamental de termos técnicos por sinônimos;
- introduções genéricas que poderiam pertencer a qualquer trabalho de
  otimização.

Corrigir pela função da frase, não por substituição automática. O objetivo é
recuperar a escolha científica concreta: o que foi feito, em qual evidência se
baseia, o que significa e até onde se pode concluir.

## 10. Citações e absorção dos artigos

- Verificar cada referência antes de incluí-la; não completar metadados por
  plausibilidade.
- Uma citação deve sustentar a proposição imediatamente associada.
- Não reutilizar listas bibliográficas dos artigos sem confirmar cada fonte
  pertinente à dissertação.
- Sintetizar texto previamente publicado; não produzir paráfrases por troca de
  sinônimos.
- Identificar publicação, submissão, coautoria e contribuição conforme a norma
  aplicável.
- Conferir licenças e permissões antes de reutilizar figuras, tabelas ou texto
  formatado por editoras.
- Se uma fonte ou número não puder ser verificado, usar marcador explícito e
  registrar a pendência; nunca inventar.

## 11. Procedimento obrigatório por edição

Antes:

1. invocar `$write-scientific-manuscripts`;
2. ler este perfil e o contexto do capítulo;
3. localizar a afirmação no modelo/manifesto de evidências;
4. escolher o modo de edição: revisão, edição de linha, substantiva ou
   desenvolvimental.

Durante:

1. preservar comandos, rótulos e chaves LaTeX válidos;
2. manter um propósito argumentativo por parágrafo;
3. separar descrição, inferência e interpretação;
4. marcar qualquer lacuna de fonte ou decisão;
5. não atualizar números manualmente quando houver gerador canônico.

Depois:

1. executar a auditoria editorial da skill nos arquivos `.tex` alterados, não
   no diretório de guias que contém exemplos deliberadamente inadequados;
2. conferir citações, referências cruzadas e consistência terminológica;
3. atualizar `AI_ASSISTANCE_LOG.md` quando houver participação material de IA;
4. executar `make thesis-doctor`;
5. compilar com `make thesis`;
6. quando a alteração afetar layout, executar `make thesis-render` e inspecionar
   o PDF;
7. relatar mudanças de força inferencial, fontes consultadas e pendências.

## 12. Critério de aceitação

Um trecho está pronto somente quando:

- sua função no argumento é clara;
- afirmações materiais são rastreáveis;
- escopo e certeza correspondem à evidência;
- português, terminologia e voz estão consistentes;
- não há fórmulas vazias nem ornamento promocional;
- texto, tabela, figura e fonte canônica concordam;
- o documento continua compilável e visualmente íntegro.

Antes do depósito, o modelo monográfico ou escandinavo deve estar confirmado e
declarado no próprio documento, com todos os elementos correspondentes
verificados.

Este perfil não substitui a leitura do autor e do orientador. A versão final
continua sob responsabilidade humana integral.
