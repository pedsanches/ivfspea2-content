# Registro de assistência por inteligência artificial

Este registro preserva a transparência sobre o uso de ferramentas de
inteligência artificial no desenvolvimento e na redação da dissertação. Ele é
um documento de trabalho: não substitui a declaração final exigida pela UFG,
pelo PPGCC, pelo CNPq, por uma editora ou por um evento.

Fontes de controle:

- Guia de Integridade Acadêmica da UFG, edição de 2024;
- Portaria CNPq nº 2.664, de 6 de março de 2026, quando aplicável;
- políticas vigentes do programa, da editora e do veículo de publicação;
- orientações documentadas do autor e do orientador.

## Como registrar

Criar uma entrada por sessão ou lote material de trabalho. Não é necessário
registrar cada correção de vírgula separadamente, mas o registro deve permitir
identificar:

- data;
- ferramenta, fornecedor e versão/modelo, se informados pela interface;
- fase da pesquisa;
- finalidade;
- arquivos, seções ou artefatos afetados;
- natureza das entradas fornecidas à ferramenta e sua classificação de
  confidencialidade;
- conteúdo ou ação produzido;
- verificação humana e fontes usadas;
- limitações, correções e decisões pendentes;
- regra de declaração aplicável e destino previsto da declaração.

Não inserir neste log dados pessoais sensíveis, credenciais, conteúdo sigiloso
ou informação que amplie indevidamente a exposição de material inédito.

## Entradas

### 2026-07-26 — governança da escrita científica

- **Ferramenta:** Codex, da OpenAI. O modelo/versão exato deve ser confirmado na
  interface antes de uma declaração formal.
- **Fase:** organização do projeto e preparação editorial.
- **Finalidade:** estruturar o ambiente versionado da dissertação; criar uma
  skill reutilizável de escrita científica; definir regras de português,
  integridade, evidência e relato estatístico; auditar o texto histórico.
- **Arquivos afetados:** `AGENTS.md`, `thesis/masters/README.md`,
  `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md` e este registro. A skill foi
  instalada fora do repositório em
  `~/.codex/skills/write-scientific-manuscripts/`.
- **Texto científico inserido:** nenhum capítulo, resumo, resultado ou conclusão
  da dissertação foi reescrito nesta sessão.
- **Entradas inspecionadas:** arquivos locais do repositório e fontes públicas
  oficiais. Antes de usar a ferramenta com material confidencial ou inédito,
  devem-se confirmar as condições institucionais e de privacidade aplicáveis.
- **Verificação humana/técnica:** fontes oficiais da UFG, PPGCC, CNPq, ABL,
  COPE, Springer Nature, IEEE, ACM e ASA foram consultadas; a skill passou no
  validador estrutural; o auditor foi testado com exemplos controlados e com o
  manuscrito histórico.
- **Limitações e pendências:** o autor e o orientador devem acordar o protocolo
  de uso de IA; confirmar a aplicabilidade da Portaria CNPq nº 2.664/2026; e
  definir a forma e o local da declaração final antes do depósito ou de cada
  submissão.

### 2026-08-13 — especificação da reescrita (rodada R1)

- **Ferramenta:** Claude Code, da Anthropic, modelo Opus 5
  (`claude-opus-5`).
- **Fase:** diagnóstico de evidência e planejamento editorial da reescrita.
- **Finalidade:** mapear o que o texto importado tem de desatualizado em relação
  aos manuscritos; verificar, contra os artefatos do repositório, quais famílias
  de evidência são reconstruíveis neste checkout; e fixar a fonte da verdade da
  reescrita capítulo a capítulo.
- **Arquivos afetados:** `thesis/masters/REWRITE_SPEC.md` (criado),
  `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md` (§4, §5, §6 e §7 emendadas),
  `thesis/masters/REVISION_PLAN.md` (§2 e §3 emendadas) e este registro.
- **Texto científico inserido:** nenhum. Nenhum arquivo em `tex/` ou `pre/` foi
  tocado; nenhum capítulo, resumo, resultado ou conclusão foi reescrito.
- **Entradas inspecionadas:** arquivos locais do repositório — fontes dos quatro
  manuscritos, documentos de evidência em `docs/`, e os CSVs e artefatos
  declarados em `data-sources.toml`. Nenhum material foi enviado a serviço
  externo além da própria ferramenta.
- **Verificação humana/técnica:** todos os números da especificação foram
  conferidos por leitura direta dos artefatos, não copiados dos manuscritos —
  `claims_summary_audit.csv` (contagens com correção de Holm),
  `hosts_summary.tex`, `phase3_summary.json`,
  `engineering_suite_pairwise_main.csv`,
  `controller_wtl_oos_20260326_221909.csv` e `dynamic_signal_test.csv`. Três
  divergências entre manuscrito e artefato foram identificadas e registradas
  como questões abertas (`OQ-01`, `OQ-02`, `OQ-03`) em vez de resolvidas no
  texto. `make thesis-doctor` foi executado e aprovou as 7 fontes declaradas.
- **Limitações e pendências:** a decisão do autor de não versionar o algoritmo
  contradizia o perfil e o plano de revisão anteriores, que foram emendados
  nesta rodada; as questões `OQ-02`, `OQ-03`, `OQ-04`, `OQ-09` e `OQ-10`
  dependem de decisão do autor e do orientador antes que as afirmações
  correspondentes entrem no texto; a verificação final de cada número
  permanece responsabilidade humana.

### 2026-08-13 — camada de artefatos das tabelas (rodada R2)

- **Ferramenta:** Claude Code, da Anthropic, modelo Opus 5
  (`claude-opus-5`).
- **Fase:** engenharia de reprodutibilidade, anterior à redação dos capítulos.
- **Finalidade:** eliminar a digitação manual de números na dissertação,
  criando geradores que produzem cada tabela diretamente do artefato canônico
  correspondente.
- **Arquivos afetados:** criados `src/python/thesis/{ptbr_format,latex_table,
  build_all}.py` e oito construtores `build_tab_*.py` / `build_apendice_fontes.py`;
  criadas 15 tabelas em `results/thesis/`; `src/python/ivfspea2/paths.py`,
  `Makefile`, `.gitignore` e `thesis/masters/data-sources.toml` estendidos;
  `REWRITE_SPEC.md` atualizado. Nenhum arquivo em `tex/` ou `pre/` foi tocado.
- **Texto científico inserido:** nenhum capítulo foi redigido. As legendas e
  notas de tabela são texto novo, redigido nesta rodada e sujeito a revisão do
  autor; elas declaram coorte, correção e direção da métrica conforme o perfil §8.
- **Entradas inspecionadas:** apenas artefatos locais do repositório.
- **Verificação humana/técnica:** cada número impresso foi conferido contra o
  artefato de origem e contra o manuscrito correspondente — contagens com
  correção de Holm, contagens por hospedeiro, ablação, engenharia, calibração,
  regra de limiar e controlador, todas coincidentes. As 15 tabelas foram
  compiladas em documento-sonda isolado, com zero avisos de `Overfull` e
  `Underfull`. `make thesis-tables-check` confirma que a regeneração é estável
  byte a byte. `make thesis-doctor` valida 8 fontes e 101 caminhos.
- **Limitações e pendências:** foi identificada uma divergência nova, registrada
  como `OQ-13`: `data/processed/classifier_comparison.csv` rotula como validação
  cruzada um ajuste feito dentro da amostra, e o valor inflado inverte a
  ordenação que o manuscrito do CLEI argumenta. O manuscrito está correto; o CSV
  não. Como esse CSV alimenta uma figura do CLEI, cabe ao autor verificar a
  figura publicada. Também foi corrigido um defeito de ambiente: o pacote
  `ivfspea2` instalado no `.venv` apontava para um worktree antigo em vez deste
  checkout.

### 2026-08-14 — reescrita dos capítulos da proposta, do protocolo e dos resultados (rodada R3)

- **Ferramenta:** Claude Code, da Anthropic, modelo Opus 5
  (`claude-opus-5`).
- **Fase:** redação científica.
- **Finalidade:** substituir integralmente os capítulos da proposta, dos
  experimentos e dos resultados, tomando como fonte o manuscrito submetido à
  Memetic Computing e os artefatos do repositório.
- **Arquivos afetados:** `tex/cap_IV.tex`, `tex/cap_V.tex` e `tex/cap_VI.tex`
  reescritos; `main.tex` (pacotes de pseudocódigo e tradução das palavras-chave);
  `Makefile` da dissertação; `bib/modelo-tese.bib` (dez entradas acrescentadas);
  `SCIENTIFIC_WRITING_PROFILE.md` §5 e `REWRITE_SPEC.md` emendados.
- **Texto científico inserido:** sim, e é o produto principal desta rodada. Os
  três capítulos são texto novo em português, redigido a partir do manuscrito e
  dos artefatos, não traduzido literalmente. Toda afirmação comparativa declara
  métrica, direção, coorte, número de execuções, orçamento e correção de
  multiplicidade. As contagens não foram digitadas: vêm por `\input` das tabelas
  geradas na rodada anterior.
- **Entradas inspecionadas:** `paper/springer-nature/src/sn-article.tex`, os
  capítulos importados, o perfil de escrita, o manifesto de evidência e as
  tabelas geradas. Nenhum material foi enviado a serviço externo além da própria
  ferramenta.
- **Verificação humana/técnica:** as dez entradas bibliográficas acrescentadas
  foram copiadas literalmente do `.bib` do manuscrito, cuja auditoria por chave
  está em `paper/springer-nature/citation_review.md`; nenhum metadado foi
  completado por plausibilidade. `make thesis` compila com zero referência
  indefinida, zero citação indefinida e zero `Overfull`. `make thesis-render`
  foi executado e as páginas dos capítulos novos foram inspecionadas.
  `make thesis-doctor` e `make thesis-tables-check` passam. A auditoria
  editorial da skill foi executada nos três arquivos: as duas ocorrências
  materiais foram corrigidas e o único aviso remanescente é falso positivo
  --- a palavra portuguesa em "para todo o texto".
- **Limitações e pendências:** a figura `fig/fluxo_ivfspea2_pt.pdf` é anterior às
  duas decisões de acoplamento e não as ilustra; a legenda foi escrita para o que
  a figura de fato mostra, e a regeneração fica para a rodada de figuras. O
  Capítulo 6 ainda não tem figuras, porque as importadas derivam da formulação
  anterior e foram aposentadas. A notação dos parâmetros divergiu da letra do
  perfil por colisão com o símbolo do número de objetivos; a decisão está
  registrada no perfil e em `OQ-05`. A revisão final do texto permanece
  responsabilidade do autor e do orientador.

### 2026-08-14 — capítulo de estudos complementares (rodada R4)

- **Ferramenta:** Claude Code, da Anthropic, modelo Opus 5
  (`claude-opus-5`).
- **Fase:** redação científica.
- **Finalidade:** absorver as quatro famílias de evidência de apoio num capítulo
  único, consumindo as tabelas que a rodada R2 gerou e que ainda estavam ociosas.
- **Arquivos afetados:** criado `tex/cap_VII_complementares.tex`; `main.tex`
  (inclusão do capítulo e geração da Lista de Algoritmos); quatro construtores em
  `src/python/thesis/` passaram a ajustar a largura das suas tabelas;
  `REWRITE_SPEC.md` atualizado.
- **Texto científico inserido:** sim. O capítulo é texto novo em português,
  redigido a partir dos manuscritos e dos artefatos. Cada seção declara a
  sobreposição de coorte aplicável antes de apresentar números.
- **Entradas inspecionadas:** as nove tabelas geradas e os manuscritos de origem.
- **Verificação humana/técnica:** todos os valores citados no texto foram
  conferidos contra o corpo das tabelas geradas. `make thesis` compila com zero
  referência indefinida e zero `Overfull`; `make thesis-render` executado e as
  páginas do capítulo inspecionadas. A auditoria editorial da skill acusou dois
  termos avaliativos sem operacionalização, ambos corrigidos, e passou a não
  reportar sinal algum.
- **Limitações e pendências:** por decisão do autor, a análise de convergência
  ficou fora da dissertação; `OQ-02` e `OQ-04` continuam registrados como
  problemas dos manuscritos, não do texto. O capítulo reporta explicitamente um
  resultado negativo que não pode ser suavizado: na suíte completa, a ablação não
  distingue o acoplamento completo da variante sem as duas decisões, e o texto
  declara que a justificativa dessas decisões é mecanicista, não estatística.

### 2026-08-14 — embasamento teórico e trabalhos relacionados (rodada R5)

- **Ferramenta:** Claude Code, da Anthropic, modelo Opus 5
  (`claude-opus-5`).
- **Fase:** redação científica.
- **Finalidade:** eliminar as contradições entre o embasamento e o capítulo da
  proposta, acrescentar o embasamento que os capítulos de protocolo e resultados
  já usavam sem definir, e reescrever os trabalhos relacionados.
- **Arquivos afetados:** `tex/cap_II.tex` (seis correções de conteúdo, cinco
  correções editoriais e três seções novas), `tex/cap_III.tex` (reescrito),
  `tex/cap_IV.tex` (notação de $k$ unificada), `bib/modelo-tese.bib` (quatro
  entradas) e `REWRITE_SPEC.md`.
- **Texto científico inserido:** sim. As seções sobre indicadores, inferência e
  paisagem de aptidão são texto novo; o capítulo de trabalhos relacionados foi
  reescrito integralmente.
- **Entradas inspecionadas:** os capítulos já reescritos, os manuscritos e as
  bibliografias dos artigos.
- **Verificação humana/técnica:** as quatro entradas bibliográficas foram
  copiadas literalmente das bibliografias dos manuscritos, sem completar
  metadados. `make thesis` compila com zero referência indefinida, zero citação
  indefinida e zero `Overfull`; `make thesis-doctor` valida 8 fontes.
  A auditoria editorial não acusa achado algum nas seções novas.
- **Limitações e pendências:** as contradições do Capítulo 2 foram resolvidas por
  enquadramento --- a Seção 2.3 passa a declarar-se como a formulação original do
  método, e não como descrição do que esta dissertação implementa. Essa é uma
  decisão interpretativa e merece conferência do autor. Onze sinais editoriais
  permanecem em trechos antigos do Capítulo 2 que não estavam no escopo desta
  rodada; foram inspecionados um a um e correspondem a usos legítimos da metáfora
  biológica do método ("material genético promissor", "geneticamente superiores")
  ou a definições operacionais explícitas, e por isso não foram alterados.

### 2026-08-14 — introdução, discussão, ameaças, trabalhos futuros, pré-textuais e apêndices (rodada R6)

- **Ferramenta:** Claude Code, da Anthropic, modelo Opus 5
  (`claude-opus-5`).
- **Fase:** redação científica e higiene bibliográfica.
- **Finalidade:** reescrever os capítulos que ainda descreviam a evidência
  antiga, escrever os apêndices e sanear a bibliografia.
- **Arquivos afetados:** `tex/cap_I.tex`, `tex/cap_VII.tex`, `tex/cap_VIII.tex` e
  `tex/cap_IX.tex` reescritos; `pre/pre_resumo.tex` e `pre/pre_abstract.tex`
  reescritos; `pos/apend_I.tex` e `pos/apend_II.tex` escritos e habilitados em
  `main.tex`; `bib/modelo-tese.bib` saneada; `src/python/thesis/build_apendice_fontes.py`
  passou a emitir português.
- **Texto científico inserido:** sim, incluindo o resumo e o abstract, que
  passam a declarar o número de instâncias, o número de execuções, os dois
  indicadores e a correção de multiplicidade, e que substituem a alegação de
  superação consistente por conclusão delimitada.
- **Entradas inspecionadas:** os capítulos já reescritos, as tabelas geradas, o
  manifesto de evidência e `docs/RELEASE_IDENTITY.md`.
- **Verificação humana/técnica:** as contagens do resumo e da discussão foram
  conferidas contra as tabelas geradas. `make thesis` compila com zero
  referência indefinida, zero citação indefinida e zero `Overfull`; o registro do
  BibTeX está limpo; `make thesis-doctor` e `make thesis-tables-check` passam. A
  auditoria editorial não acusa achado nos capítulos novos.
- **Limitações e pendências:** a entrada bibliográfica do repositório passou a
  citar o DOI de conceito, que é o que `docs/RELEASE_IDENTITY.md` determina como
  padrão; se o autor preferir a versão específica, a decisão continua registrada
  em `OQ-09`. A autoria dessa entrada lista cinco pessoas enquanto a dissertação
  é individual, o que permanece pendente em `OQ-10`. Cinco entradas
  bibliográficas legítimas seguem sem citação; como `\nocite{*}` está desativado,
  elas não são impressas.

### 2026-09-10 — incorporação do TECA e da ficha catalográfica

- **Ferramenta:** Codex, da OpenAI. O modelo/versão exato deve ser confirmado na
  interface antes de uma declaração formal.
- **Fase:** preparação dos elementos pré-textuais para depósito.
- **Finalidade:** incorporar ao PDF da dissertação o TECA e a ficha catalográfica
  fornecidos pelo autor, nas posições indicadas pelo tutorial do PPGCC/UFG.
- **Arquivos afetados:** `main.tex`; cópias byte a byte dos documentos recebidos
  em `pre/teca.pdf` e `pre/ficha-catalografica.pdf`.
- **Texto científico inserido:** nenhum. A primeira página material do TECA foi
  inserida depois da capa e a ficha catalográfica depois da folha de rosto. A
  segunda página do TECA, que contém apenas o rodapé de versão do formulário,
  não integra a dissertação.
- **Entradas inspecionadas:** apenas os dois PDFs fornecidos pelo autor, o
  tutorial de depósito e os elementos pré-textuais locais da dissertação.
- **Verificação humana/técnica:** os hashes das cópias locais coincidem com os
  arquivos recebidos; a dissertação foi recompilada e as páginas iniciais foram
  renderizadas para conferir conteúdo, escala e ordem.
- **Limitações e pendências:** o TECA recebido registra `08/09/2026`, enquanto a
  data provisória da defesa na dissertação é `08/11/2026`, e ainda não contém as
  assinaturas exigidas. A ficha recebida registra 72 folhas, cinco pessoas como
  autores, dois orientadores e palavras-chave diferentes das adotadas na
  dissertação. Esses dados precisam ser corrigidos pelo autor no sistema
  institucional antes do depósito. A folha da banca continua ausente.

### 2026-09-10 — adequação da capa e da folha de rosto

- **Ferramenta:** Codex, da OpenAI. O modelo/versão exato deve ser confirmado na
  interface antes de uma declaração formal.
- **Fase:** preparação dos elementos pré-textuais para depósito.
- **Finalidade:** executar as correções solicitadas pelo programa após a defesa:
  identificar o PPGCC na capa; corrigir área de concentração e linha de pesquisa;
  registrar Ronaldo Martins da Costa como orientador; e registrar Celso Gonçalves
  Camilo Junior como coorientador.
- **Arquivos afetados:** `main.tex`, `inf-ufg-tectonic.cls` e este registro. O
  PDF compilado em `build/main.pdf` foi regenerado.
- **Texto científico inserido:** nenhum. As alterações se restringem a metadados
  acadêmicos, ao texto de natureza do trabalho e à apresentação dos elementos
  pré-textuais.
- **Entradas inspecionadas:** solicitação do autor, PDF de orientações de capa e
  folha de rosto fornecido pelo autor e TECA local já incorporado à dissertação.
- **Verificação humana/técnica:** `make thesis-doctor` validou as oito fontes e
  os 101 caminhos declarados; a auditoria editorial não encontrou sinais nos
  campos alterados; o Tectonic compilou o documento; e capa, TECA, folha de rosto
  e ficha catalográfica foram renderizados e inspecionados visualmente.
- **Limitações e pendências:** o TECA continua sem assinaturas. O acesso ao
  Assinador GOV.BR foi preparado, mas CPF, autenticação e ato de assinatura
  dependem de ação pessoal do autor. A solicitação ao orientador deve usar
  Ronaldo Martins da Costa e somente pode ser enviada depois de obtido o TECA
  assinado pelo autor. O nome abreviado do autor existente na capa e na folha de
  rosto não foi alterado, pois essa correção não integrou a solicitação atual.

### 2026-09-10 — siglas institucionais e nome civil completo

- **Ferramenta:** Codex, da OpenAI. O modelo/versão exato deve ser confirmado na
  interface antes de uma declaração formal.
- **Fase:** preparação dos elementos pré-textuais para depósito.
- **Finalidade:** apresentar `Universidade Federal de Goiás (UFG)` e `Instituto
  de Informática (INF)` na capa e na folha de rosto, além de substituir o nome
  abreviado do autor por `Pedro Henrique Sanches Pelegrino Zambrano` nos
  elementos pré-textuais gerados pela classe.
- **Arquivos afetados:** `main.tex`, `inf-ufg-tectonic.cls` e este registro. O
  PDF compilado em `build/main.pdf` foi regenerado.
- **Texto científico inserido:** nenhum. A edição alterou somente identificação
  institucional, autoria e metadados do documento.
- **Entradas inspecionadas:** solicitação do autor e os quatro primeiros
  elementos pré-textuais do PDF compilado.
- **Verificação humana/técnica:** `make thesis-doctor` validou as oito fontes e
  os 101 caminhos declarados; a auditoria editorial não encontrou sinais em
  `main.tex`; o Tectonic compilou o documento; e capa, TECA, folha de rosto e
  ficha catalográfica foram renderizados e inspecionados visualmente.
- **Limitações e pendências:** o TECA e a ficha catalográfica são PDFs externos.
  Ambos já contêm o nome civil completo e, por isso, não precisaram ser
  alterados nesta rodada. O TECA permanece sem assinaturas.

### 2026-09-10 — TECA assinado e titulação do orientador e do coorientador

- **Ferramenta:** Codex, da OpenAI. O modelo/versão exato deve ser confirmado na
  interface antes de uma declaração formal.
- **Fase:** preparação dos elementos pré-textuais para depósito.
- **Finalidade:** substituir o TECA anterior pelo documento assinado pelo autor e
  pelo orientador e apresentar Ronaldo Martins da Costa e Celso Gonçalves Camilo
  Junior como Professor Doutor na folha de rosto.
- **Arquivos afetados:** `pre/teca.pdf`, `pre/teca-inclusao.pdf`, `main.tex`,
  `inf-ufg-tectonic.cls`, `Makefile` e este registro. O PDF compilado em
  `build/main.pdf` foi regenerado.
- **Texto científico inserido:** nenhum. As alterações se restringem ao TECA e
  à identificação acadêmica do orientador e do coorientador.
- **Entradas inspecionadas:** TECA assinado fornecido pelo autor e as três
  primeiras páginas da dissertação recompilada.
- **Verificação humana/técnica:** a cópia local do TECA tem o mesmo SHA-256 do
  arquivo recebido; as assinaturas de Pedro Henrique Sanches Pelegrino Zambrano
  e Ronaldo Martins da Costa foram reconhecidas com integridade válida, e a
  segunda assinatura cobre o documento completo. A auditoria editorial não
  encontrou sinais em `main.tex`; `make thesis-doctor` validou as oito fontes e
  os 101 caminhos declarados; e capa, TECA e folha de rosto foram renderizados e
  inspecionados visualmente.
- **Limitações e pendências:** as marcas GOV.BR são anotações do PDF assinado e
  não são incorporadas diretamente pelo LaTeX. Por isso, `pre/teca.pdf` preserva
  o original verificável, enquanto `pre/teca-inclusao.pdf` é uma cópia estática
  de sua primeira página para exibir as assinaturas na dissertação. A data do
  TECA permanece `08/09/2026`, enquanto a data provisória da defesa no documento
  é `08/11/2026`; essa divergência ainda requer confirmação antes do depósito.

### 2026-09-19 — auditoria de estado e correção de quatro defeitos verificados

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** auditoria do estado da escrita após a R6 e saneamento dos defeitos
  que a auditoria confirmou contra os artefatos.
- **Finalidade:** levantar o estado de acabamento capítulo a capítulo e corrigir
  apenas o que foi verificado diretamente contra dado ou fonte, sem reescrita de
  prosa.
- **Arquivos afetados:** `tex/cap_VI.tex`, `tex/cap_V.tex`,
  `tex/cap_VII_complementares.tex`, `pos/apend_II.tex` e este registro. O PDF em
  `build/main.pdf` foi regenerado.
- **Texto científico inserido:** quatro intervenções pontuais. (i) Em
  `cap_VI.tex:17`, a frase afirmava que sete instâncias passavam a empate sob
  correção de Holm com $M = 3$; `results/tables/claims_summary_audit.csv` registra
  18 vitórias e 4 empates sem correção contra 15 e 7 com correção, isto é, três
  instâncias, e a frase foi corrigida para três, explicitando a passagem de
  quatro para sete empates. (ii) Em `cap_VII_complementares.tex`, a seção de
  engenharia recebeu a ressalva de produtor não executável que a seção de
  calibração já trazia e que o `REWRITE_SPEC.md` §3.2 exige para as linhas
  `C-ENG-*`. (iii) Em `cap_V.tex`, a nota da Tabela 5.1 passou a declarar a
  versão da plataforma de todas as famílias, e não apenas da confirmatória, da
  calibração e da comparação entre hospedeiros. (iv) Em `pos/apend_II.tex`, a
  Seção B.2 remetia a uma declaração de disponibilidade de dados e código que não
  existia no documento; a declaração foi escrita como Seção B.4, citando o DOI de
  conceito `10.5281/zenodo.19071253` conforme `docs/RELEASE_IDENTITY.md`, e a
  remissão passou a apontar para ela.
- **Entradas inspecionadas:** `REWRITE_SPEC.md`, `REVISION_PLAN.md`,
  `SCIENTIFIC_WRITING_PROFILE.md`, os dez capítulos, os dois apêndices, os
  pré-textuais, `bib/modelo-tese.bib`, `data-sources.toml`, os geradores em
  `src/python/thesis/`, `results/tables/claims_summary_audit.csv` e
  `docs/RELEASE_IDENTITY.md`.
- **Verificação humana/técnica:** as contagens da prosa dos Capítulos 6 e 7 foram
  conferidas linha a linha contra as tabelas do `REWRITE_SPEC.md` §3 e contra os
  artefatos, e a única divergência encontrada foi a do item (i). `make
  thesis-doctor` validou as oito fontes e os 101 caminhos; `make
  thesis-tables-check` não acusou deriva; `make verify-release` aprovou o DOI
  acrescentado; e `make thesis` compilou com zero referências indefinidas, zero
  citações indefinidas, zero avisos do LaTeX e zero linhas *overfull*.
- **Limitações e pendências:** a dissertação não contém nenhuma figura de
  resultado --- as três figuras são diagramas conceituais, e as cinco figuras
  estatísticas de `fig/` não são incluídas por nenhum capítulo; a R7 precisa
  decidir se elas entram antes de tratar de fontes Type 3. O Capítulo 3 tem 812
  palavras para 15 obras, cerca de uma frase por trabalho. Cinco entradas
  bibliográficas seguem sem citação, e `Chen2021` ainda carrega nota interna de
  autoria não verificada. Permanecem as pendências institucionais já registradas:
  data de defesa, folha da banca, `\publica`, divergência da ficha catalográfica
  e a declaração de formato monográfico exigida pela Resolução INF nº 02/2023/PPGCC,
  que não existe no documento.
