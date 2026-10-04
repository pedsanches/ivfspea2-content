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

### 2026-09-20 — figuras de resultado, Capítulo 3 e limpeza bibliográfica

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** rodada R7, decidida pelo autor após a auditoria de estado.
- **Finalidade:** dar à dissertação figuras de resultado espelhando as dos três
  manuscritos-fonte, aprofundar o Capítulo 3 e remover uma entrada
  bibliográfica com autoria não verificada.
- **Arquivos afetados:** `src/python/thesis/build_fig_resultados.py` e
  `build_fig_complementares.py` (novos), `src/python/thesis/build_all.py`,
  `thesis/masters/Makefile`, `data-sources.toml`, `main.tex`, `tex/cap_III.tex`,
  `tex/cap_VI.tex`, `tex/cap_VII_complementares.tex`,
  `bib/modelo-tese.bib` e este registro. Sete PDFs novos em
  `results/thesis/figures/`. O PDF em `build/main.pdf` foi regenerado.
- **Texto científico inserido:** o Capítulo 3 foi reescrito de 812 para 1.672
  palavras, mantendo as 15 obras já citadas e incorporando `li2015many` e
  `coello2007evolutionary`, que estavam definidas no `.bib` e nunca citadas.
  Cada obra passou a ter método, resultado e relação com a proposta, em vez de
  uma frase de atribuição. A antiga seção "Decidir quando aplicar um operador"
  foi dividida em duas — paisagem de aptidão aplicada a algoritmos
  multiobjetivo, e controle adaptativo de operadores — porque misturava
  linhagens distintas. Três obras (`talbi2009metaheuristics`,
  `zhou2011multiobjective`, `wolpert1997no`) **não foram aprofundadas**: nenhum
  dos três manuscritos-fonte as cita, e caracterizá-las além do que o texto
  original já dizia exigiria afirmar o que não foi verificado. Os capítulos 6 e
  7 ganharam uma frase de introdução por figura; nenhum número foi alterado.
- **Entradas inspecionadas:** as figuras dos três manuscritos-fonte e os seus
  scripts produtores em `src/python/analysis/`, `figures/` e `fla/`;
  `results/tables/`, `results/tuning_ivfspea2v2/`, `results/engineering_suite/`,
  `data/processed/dynamic_signal_test.csv` e o CSV consolidado.
- **Verificação humana/técnica:** as sete figuras foram geradas sob
  `.venv/bin/python` com matplotlib 3.10.8, o que preserva os PDFs versionados
  do repositório, e `apply_paper_style()` fixa `pdf.fonttype = 42` — nenhuma
  delas usa fonte Type 3, e o PDF final também não. Cada figura foi renderizada
  e **inspecionada visualmente página a página**: três reprovaram na primeira
  tentativa e foram refeitas. A distribuição de IGD estava ilegível e com as 51
  instâncias espremidas numa faixa; passou a boxplots horizontais, uma linha por
  instância, em página própria. O posto médio e os perfis de engenharia traziam
  título interno duplicando a legenda LaTeX; foi removido. Nos perfis de
  engenharia, o rótulo do eixo de HV ficava cortado na borda direita e os
  rótulos `n=` colidiam com os marcadores; ambos corrigidos, com o `n=18` do
  RWMOP8 preservado. `make thesis-tables-check` confirma que tabelas e figuras
  são byte-estáveis; `make thesis-doctor` valida as oito fontes e os 116
  caminhos declarados; `make verify-release` aprova; `make test` passa nos 40
  testes; e `make thesis` compila 87 páginas com zero referências indefinidas,
  zero citações indefinidas, zero avisos do LaTeX e zero linhas *overfull*.
- **Limitações e pendências:** a entrada `Chen2021` foi removida do `.bib` por
  carregar nota interna de autoria não verificada; quatro entradas legítimas
  seguem sem citação. A declaração de formato monográfico exigida pela Resolução
  INF nº 02/2023/PPGCC **continua ausente por decisão do autor**, que optou por
  confirmar a redação com a secretaria antes de inseri-la; a pendência está
  registrada em `REVISION_PLAN.md`. Permanecem a data de defesa, a folha da
  banca, o `\publica` e a divergência da ficha catalográfica, agora com 87
  páginas contra as 72 folhas que a ficha registra.

### 2026-09-20 — contagens por suíte trocadas e ancoragem das ameaças

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** fechamento da R7, a partir das lacunas que a própria auditoria
  havia registrado como não resolvidas.
- **Finalidade:** eliminar o último número sem lastro do Capítulo 6 e dar
  ancoragem bibliográfica ao capítulo de ameaças à validade.
- **Arquivos afetados:** `tex/cap_VI.tex`, `tex/cap_VIII.tex`,
  `bib/modelo-tese.bib` e este registro. O PDF foi regenerado.
- **Texto científico inserido:** três intervenções.
  (i) O parágrafo de contagens por suíte tinha **empates e derrotas trocados
  nas quatro linhas não triviais**: o texto dizia WFG $M{=}2$ igual a 4/3/2 e
  DTLZ, WFG e MaF em $M{=}3$ iguais a 6/0/1, 6/1/2 e 6/0/1, enquanto
  `claims_summary_instance_details.csv` dá 4/2/3, 6/1/0, 6/2/1 e 6/1/0. É a
  armadilha de convenção que o `REWRITE_SPEC.md` §3.1 adverte — os manuscritos
  ordenam vitórias/derrotas/empates e a dissertação declara
  vitórias/empates/derrotas em `cap_VI.tex:6`. O erro contradizia o próprio
  capítulo, que afirma três derrotas em WFG com $M{=}2$ e uma única derrota
  remanescente em $M{=}3$. Corrigido, e o parágrafo passou a declarar que as
  linhas somam 23/2/3 e 18/4/1, reconciliando com as linhas não corrigidas da
  Tabela 6.1.
  (ii) O mesmo parágrafo estava na seção de posicionamento exploratório, que se
  anuncia como comparação contra sete comparadores de contexto, mas reportava o
  par IVF/SPEA2 — o mesmo da seção confirmatória. Foi movido para a seção de
  resultados por instância, onde a concentração das derrotas já é discutida.
  (iii) O capítulo de ameaças à validade não tinha nenhuma citação. Três
  afirmações passaram a apontar a literatura que já as sustenta no Capítulo 2:
  a incompatibilidade de qualquer indicador isolado com a dominância
  (`zitzler2004performance`), a distinção entre Holm e Benjamini--Hochberg
  (`holm1979simple`, `benjamini1995controlling`) e o limite de generalização
  entre classes de problemas (`li2015many`, `wolpert1997no`). Nenhuma
  referência nova foi introduzida.
- **Entradas inspecionadas:** `results/tables/claims_summary_instance_details.csv`
  (102 linhas), `results/tables/claims_summary_audit.csv` e as entradas do `.bib`
  citadas acima.
- **Verificação humana/técnica:** as contagens por suíte foram recomputadas a
  partir do artefato por instância e conferem com as linhas não corrigidas do
  resumo de auditoria nos dois valores de $M$. O parágrafo corrigido foi lido no
  PDF compilado. A bibliografia ficou **balanceada em 47 entradas definidas e 47
  citadas**, sem entrada morta, após remover `Cremene2016` e `Lopez2005`, que
  nunca foram citadas. `make thesis-tables-check`, `make thesis-doctor`,
  `make verify-release` e `make test` passam; `make thesis` compila 88 páginas
  com zero referências indefinidas, zero citações indefinidas, zero avisos do
  LaTeX e zero linhas *overfull*.
- **Limitações e pendências:** as pendências institucionais seguem inalteradas
  e dependem do autor — data de defesa, folha da banca, `\publica`, ficha
  catalográfica e a declaração de formato monográfico da Resolução INF
  nº 02/2023/PPGCC. Três obras do Capítulo 3 permanecem sem aprofundamento por
  falta de fonte verificável. Nenhum dado bruto da campanha do Memetic Computing
  está nesta máquina: `data/raw/` contém apenas a campanha de dinâmica, não há
  nenhum `.mat` do projeto e `src/matlab/lib/PlatEMO/Data` não existe.

### 2026-09-20 — a leitura geométrica não se sustentava na família confirmatória

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** auditoria de consistência de argumentação, a pedido do autor.
- **Finalidade:** procurar contradição entre capítulos, promessa não cumprida e
  conclusão além da evidência. Não eram defeitos mecânicos: o documento já
  compilava limpo.
- **Arquivos afetados:** `tex/cap_VI.tex`, `tex/cap_VII.tex`, `tex/cap_IV.tex`,
  `tex/cap_V.tex`, `pre/pre_resumo.tex`, `pre/pre_abstract.tex` e este registro.
- **Texto científico inserido:** a correção principal desfaz a afirmação
  interpretativa central do Capítulo 6. O texto dizia que as instâncias em que o
  acoplamento perde "envolvem fronteiras desconectadas ou irregulares", e a
  Discussão chamava a distribuição do ganho de achado mais informativo da
  dissertação, dizendo que a comparação entre hospedeiros "reforça essa
  associação". O cruzamento das quatro derrotas com
  `config/hosts_front_geometry.csv`, que é a classificação geométrica adotada
  pelo próprio projeto, mostra o contrário: **duas das quatro ocorrem em
  fronteiras classificadas como regulares** --- WFG3 com $M{=}2$, linear, e WFG9
  com $M{=}2$, côncava --- e o acoplamento **vence em 8 das 11 instâncias
  irregulares**, incluindo ZDT3, DTLZ7 e MaF7, desconectadas, e DTLZ5, DTLZ6 e
  MaF6, degeneradas. Sob correção de Holm as taxas de vitória dos dois grupos
  são praticamente iguais, 29 de 40 contra 8 de 11: na família confirmatória a
  geometria **não separa nada**. O que as quatro derrotas compartilham é a
  suíte, não a forma da fronteira. A família de hospedeiros, por outro lado,
  mostra gradiente real --- 28/11/1 contra 5/4/2, com $A_{12}$ mediano caindo de
  0,781 para 0,642. As duas famílias discordam, e o texto passou a **reportar a
  divergência em vez de harmonizá-la**, como a regra da própria dissertação já
  exigia. A conclusão de destaque, o resumo e o abstract deixaram de afirmar
  dependência da geometria e passaram a dizer que o fator discriminante
  permanece em aberto.
  Três correções menores acompanham: o parágrafo de contagens por suíte usava
  valores não corrigidos logo abaixo de tabelas corrigidas por Holm, e passou a
  usar Holm (WFG com $M{=}2$ é 3/3/3, não 4/2/3), somando 22/3/3 e 15/7/1; a
  Discussão afirmava vitória em **todas** as instâncias de ZDT, DTLZ e MaF, o
  que é falso com $M{=}3$, onde há empates, e passou a afirmar ausência de
  derrota fora da WFG; e o Capítulo 5 não dizia como o $A_{12}$ é orientado para
  o HV, onde maior é melhor.
- **Entradas inspecionadas:** `results/tables/claims_summary_instance_details.csv`,
  `claims_summary_audit.csv`, `results/tables/hosts_geometry_summary.csv`,
  `config/hosts_front_geometry.csv` e as tabelas geradas por instância.
- **Verificação humana/técnica:** o cruzamento entre resultado e geometria foi
  computado das duas formas, com e sem correção de multiplicidade, e a
  conclusão não muda. Confirmou-se que as tabelas por instância publicam
  p-valores corrigidos por Holm, e não brutos, o que determinou qual conjunto de
  contagens o texto deve citar. O abstract precisou voltar a caber na caixa da
  classe: a versão corrigida estourava o quadro em 1,7pt e empurrava as
  palavras-chave, e foi enxugada de 368 para 350 palavras. O arranjo dos
  pré-textuais foi comparado com o do último commit e é idêntico.
  `make thesis-tables-check`, `make thesis-doctor`, `make verify-release` e
  `make test` passam; `make thesis` compila 89 páginas com zero referências
  indefinidas, zero citações indefinidas, zero avisos e zero linhas *overfull*.
- **Limitações e pendências:** o fator que discrimina as instâncias favoráveis
  passa a ser uma questão explicitamente em aberto no texto, e não uma
  conclusão. As pendências institucionais seguem inalteradas.

### 2026-09-20 — a sobrecorreção da leitura geométrica, desfeita e tabulada

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** segunda passagem da auditoria de argumentação, revisando a
  correção feita na passagem anterior.
- **Finalidade:** verificar se o gradiente por geometria da família de
  hospedeiros sobrevive ao mesmo escrutínio que derrubou a leitura geométrica
  do Capítulo 6, e corrigir o texto conforme o resultado.
- **Arquivos afetados:** `src/python/thesis/build_tab_geometria_confirmatoria.py`
  (novo), `build_all.py`, `data-sources.toml`, `tex/cap_VI.tex`,
  `tex/cap_VII.tex` e este registro. Nova tabela em
  `results/thesis/tab_geometria_confirmatoria.tex`.
- **Texto científico inserido:** a entrada anterior deste registro afirmava que
  as duas famílias **divergiam** quanto à associação entre geometria e
  benefício. **Isso estava errado, e a correção anterior foi excessiva.** O
  $A_{12}$ mediano por grupo de geometria foi recalculado na coorte
  confirmatória completa, com as 60 execuções, e comparado ao da família de
  hospedeiros: $0{,}775$ contra $0{,}664$ na primeira, $0{,}781$ contra
  $0{,}642$ na segunda. A direção e a magnitude da queda são praticamente
  idênticas, e em nenhuma das duas a diferença atinge significância
  ($p = 0{,}092$ e $p = 0{,}065$, Mann--Whitney). As famílias **concordam** no
  efeito. O que difere é a decisão binária do teste: com 60 execuções e Holm a
  taxa de vitória satura nos dois grupos, 29 de 40 contra 8 de 11, e a diferença
  de magnitude não vira diferença de contagem; com 30 execuções e
  Benjamini--Hochberg a detecção cai mais no grupo de efeito menor, produzindo
  28/11/1 contra 5/4/2. A aparente discordância é diferença de poder
  estatístico sobre o mesmo fenômeno. O texto passou a dizer isso, em vez de
  declarar divergência entre famílias.
  O que permanece da correção anterior: a leitura de que as derrotas ocorrem em
  fronteiras irregulares continua falsa --- duas das quatro são em fronteiras
  regulares --- e o fator discriminante continua em aberto. O gradiente existe,
  é modesto, é consistente e não é significativo; ele não explica as derrotas.
- **Entradas inspecionadas:** `results/tables/hosts_ivfspea2_igd_stats.csv`,
  `hosts_geometry_summary.csv`, `claims_summary_instance_details.csv`,
  `config/hosts_front_geometry.csv` e a coorte confirmatória do CSV
  consolidado, lida através de `filter_submission_synthetic_cohort`.
- **Verificação humana/técnica:** a análise deixou de ser cálculo de sessão e
  virou artefato. O novo gerador produz a Tabela 6.4 a partir das quatro fontes
  declaradas e entra no portão de deriva, de modo que a afirmação mais
  contestável da dissertação passa a ter produtor executável. Dois defeitos
  foram encontrados e corrigidos no próprio gerador antes do uso: a coluna
  `median_a12_ivf` do resumo de hospedeiros **já vem orientada**, e aplicar a
  inversão publicava $0{,}219$ e $0{,}358$ ao lado de $0{,}775$ e $0{,}664$, ou
  seja duas convenções na mesma tabela; e uma edição na lista de construtores
  chegou a remover `build_apendice_fontes.py` e duplicar `build_tab_hosts.py`,
  o que foi detectado e desfeito antes de qualquer execução. A tabela foi
  renderizada e inspecionada. Um rebuild limpo, com `make thesis-clean`,
  confirmou que o *overfull* da rodada anterior estava de fato resolvido e não
  era artefato de cache. `make thesis-tables-check`, `make thesis-doctor`,
  `make verify-release` e `make test` passam; `make thesis` compila 89 páginas,
  17 tabelas e 10 figuras, com zero referências indefinidas, zero citações
  indefinidas, zero avisos e zero linhas *overfull*.
- **Limitações e pendências:** o gradiente por geometria é descritivo nas duas
  famílias e não sustenta afirmação causal. As pendências institucionais seguem
  inalteradas.

### 2026-09-20 — a maior queda não é a do acoplamento que mais ganha

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** terceira passagem da auditoria de argumentação, varrendo o que a
  correção da cadeia geométrica deixou para trás.
- **Finalidade:** fechar as duas pontas soltas da seção de hospedeiros e um
  defeito latente no gerador criado na passagem anterior.
- **Arquivos afetados:** `tex/cap_VII_complementares.tex`,
  `src/python/thesis/build_tab_geometria_confirmatoria.py` e este registro.
- **Texto científico inserido:** duas correções na seção de compatibilidade
  entre hospedeiros. A primeira é factual: o texto afirmava que a diferença
  entre geometrias "é maior justamente no acoplamento que mais ganha", e
  `results/tables/hosts_geometry_summary.csv` diz o contrário. A maior queda de
  $A_{12}$ é a do IVF/NSGA-III --- $0{,}687$ para $0{,}529$ em IGD, e $0{,}676$
  para $0{,}501$ em HV --- e não a do IVF/SPEA2, cujas quedas são $0{,}139$ e
  $0{,}148$ contra $0{,}158$ e $0{,}175$. O IVF/SPEA2 é de fato o que mais
  ganha, mas não é o que mais perde com a irregularidade da fronteira. A
  segunda é de coerência: a seção abria dizendo que "o padrão observado no
  Capítulo 6 reaparece aqui", quando o Capítulo 6 passou a reportar que na
  família confirmatória a geometria **não** separa vitórias de derrotas. A
  passagem agora declara o que as duas famílias de fato compartilham, o
  gradiente de magnitude, e o que as separa, a decisão binária do teste.
- **Entradas inspecionadas:** `results/tables/hosts_geometry_summary.csv`, com
  as seis linhas de grupo de geometria dos três acoplamentos nos dois
  indicadores.
- **Verificação humana/técnica:** o gerador criado na passagem anterior tinha
  um **defeito latente** que o teste bem-sucedido não revelou: a reordenação de
  importações removera `import sys`, usado apenas nos dois caminhos de erro, que
  não disparam quando todos os artefatos existem. O script teria falhado com
  `NameError` exatamente quando precisasse reportar artefato ausente. As
  importações foram restauradas e **os dois caminhos foram exercitados**: o
  feliz escreve a tabela, e o de erro imprime a mensagem e retorna código 1.
  Confirmou-se também que o novo gerador e a nova tabela estão declarados em
  `data-sources.toml`, nas listas de scripts e de artefatos, e não apenas
  presentes no disco --- `make thesis-doctor` valida caminhos declarados, e não
  detectaria a omissão. Os quatro portões passam e `make thesis` compila 89
  páginas com zero referências indefinidas, zero citações indefinidas, zero
  avisos e zero linhas *overfull*.
- **Limitações e pendências:** as pendências institucionais seguem inalteradas.
  Registre-se, para a revisão do autor, que os três defeitos de argumentação
  encontrados nesta e nas duas passagens anteriores estavam todos na mesma
  cadeia interpretativa --- a que liga geometria da fronteira a desempenho ---
  e nenhum deles era detectável por compilação ou por conferência de número
  isolado. Todos exigiram confrontar a prosa com o artefato.

### 2026-09-20 — mecanismo atribuído a um capítulo que não o formula

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** quarta passagem da auditoria de argumentação, dirigida ao padrão
  que produziu todos os defeitos anteriores.
- **Finalidade:** varrer as remissões entre capítulos e auditar a família de
  ativação do operador, que era a menos conferida.
- **Arquivos afetados:** `tex/cap_VII.tex`, `tex/cap_VII_complementares.tex`,
  `tex/cap_IX.tex` e este registro.
- **Texto científico inserido:** três intervenções.
  (i) A Discussão atribuía ao Capítulo 4 uma interpretação mecanicista
  diferenciada por geometria --- descendentes retidos em fronteiras regulares,
  adensamento penalizado em fronteiras desconectadas. O Capítulo 4 **não
  menciona geometria de fronteira em nenhuma linha**; ele argumenta apenas que
  descendentes de um progenitor comum se penalizam pela componente de
  densidade. A conjectura foi construída na Discussão e atribuída
  retroativamente à Proposta. O texto agora a apresenta como conjectura da
  própria Discussão, derivada do argumento de densidade, e diz que o capítulo
  de origem não a formula.
  (ii) A seção de paisagem afirmava que, sob validação deixa-uma-família,
  "três" classificadores exibiam coeficiente de Matthews negativo. São
  **quatro**, e são todos os que a tabela apresenta: $-0{,}070$, $-0{,}163$,
  $-0{,}070$ e $-0{,}070$. A afirmação errava por defeito, enfraquecendo um
  resultado negativo que é mais forte do que o texto dizia.
  (iii) A correção da cadeia geométrica deixou uma lacuna: a Discussão passou a
  declarar o fator discriminante como questão em aberto, mas os Trabalhos
  Futuros só propunham testar a geometria. Foi acrescentado o item que a
  evidência de fato sugere --- as quatro derrotas estão todas na WFG, cujas
  transformações são não separabilidade, multimodalidade, engano e assimetria,
  manipuláveis de forma independente nos geradores da suíte, o que admite
  desenho fatorial.
- **Entradas inspecionadas:** as 54 remissões entre capítulos; `tex/cap_IV.tex`
  integralmente, para confirmar a ausência de qualquer menção a geometria;
  `results/tables/fla_model_comparison.csv`,
  `dynamic_signal_{main_tests,loocv,lofo}.csv` e
  `controller_wtl_oos_20260326_221909.csv`.
- **Verificação humana/técnica:** das 54 remissões, 53 conferem. A família de
  ativação foi conferida número a número contra os cinco artefatos que a
  sustentam e só o erro de contagem do MCC apareceu; a aritmética do
  controlador fecha nas quatro afirmações que o texto encadeia
  ($10 + 32 = 42$ e $41 - 32 = 9$), e não há uso de IGD como evidência de
  sucesso do controlador, o que preservaria a circularidade que a seção declara
  evitar. `make thesis-tables-check`, `make thesis-doctor`,
  `make verify-release` e `make test` passam; `make thesis` compila 90 páginas
  com zero referências indefinidas, zero citações indefinidas, zero avisos e
  zero linhas *overfull*.
- **Limitações e pendências:** os quatro defeitos de argumentação encontrados
  nas quatro passagens têm a mesma forma --- um trecho afirma que outro
  capítulo, tabela ou família "mostra", "confirma" ou "reforça" algo, e o alvo
  não diz aquilo. Três estavam na cadeia da geometria e o quarto na atribuição
  do mecanismo. Nenhum era detectável por compilação. Recomenda-se que a
  revisão do autor priorize exatamente essas construções. As pendências
  institucionais seguem inalteradas.

### 2026-09-22 — a dissertação organizada por questões de pesquisa, sem re-execução

- **Ferramenta:** Claude, da Anthropic. O modelo/versão exato deve ser
  confirmado na interface antes de uma declaração formal.
- **Fase:** reestruturação argumentativa (rodada R8 de `REWRITE_SPEC.md`), sob a
  decisão do autor de não reexecutar experimentos.
- **Finalidade:** organizar a dissertação em torno de quatro questões de
  pesquisa e conferir cada resposta contra o artefato que a sustenta, usando
  apenas artefatos versionados.
- **Arquivos afetados:** `tex/cap_I.tex`, `cap_V.tex`, `cap_VI.tex`,
  `cap_VII_complementares.tex`, `cap_VII.tex`, `cap_VIII.tex`, `cap_IX.tex`;
  `pre/pre_resumo.tex` e `pre/pre_abstract.tex`;
  `src/python/thesis/build_tab_magnitude_confirmatoria.py` (novo),
  `build_tab_engenharia.py`, `build_tab_controlador.py`,
  `build_tab_fla_dinamica.py`, `build_tab_tuning_ablacao.py` e `build_all.py`;
  `data-sources.toml`; `REWRITE_SPEC.md`; `REVISION_PLAN.md`, reescrito; e este
  registro. Tabelas regeneradas em `results/thesis/`.
- **Texto científico inserido:** objetivos, quatro questões de pesquisa e
  contribuições reescritas a partir das respostas (Cap. 1); uma seção de
  magnitude (Cap. 6); uma seção por questão no Cap. 7 e uma resposta por
  questão no Cap. 8; resumo e abstract derivados das respostas. Quatro leituras
  foram corrigidas contra os artefatos. (i) A ablação rodou na configuração
  inicial não ajustada, e não na promovida, e o braço sem as duas decisões veio
  de outra campanha; o texto chamava a variante de "acoplamento completo" sem
  dizer isso (`OQ-14`). (ii) A transferência para engenharia é 1/2/0 contra o
  hospedeiro, com a vitória do RWMOP9 sobrevivendo a Holm; os "resultados
  mistos" eram o posicionamento contra oito comparadores (`OQ-17`). (iii) A
  validação deixa-uma-família ajusta o limiar sem a família retida; o texto
  dizia que a regra pressupunha conhecer a família (`OQ-16`). (iv) O
  controlador perde para o operador sempre ativo (HV 2/40/9); a Discussão dizia
  que ele "elimina as perdas", sem o qualificador, e nas quatro instâncias em
  que o operador prejudica ele ainda perde para o SPEA2 em três. Além disso, a
  afirmação de que as duas famílias "divergem" quanto à geometria, que restava
  nas Conclusões e no resumo, foi removida, porque contradizia a Discussão
  corrigida em 20/09.
- **Entradas inspecionadas:** `claims_summary_instance_details.csv`; o CSV
  consolidado, lido por `filter_submission_synthetic_cohort`;
  `engineering_suite_summary_main.csv` e `engineering_suite_pairwise_main.csv`;
  `ppsn_controller_comparison_oos_20260326_221909.csv`; `fla_response.csv`;
  `dynamic_signal_test.csv`; `dynamic_signal_lofo.csv`; `phase2_summary.json` e
  `phase3_summary.json`; os roteiros `run_ablation_v2_phase3_batch_common.m`,
  `analyze_ablation_v2_phase3.py`, `test_dynamic_signal.py`,
  `launch_ppsn_controller_oos_lofo_parallel.sh`, `run_ppsn_controller.m` e
  `process_engineering_suite.m`; `sn-article.tex` (linhas 285 e 566); o CLEI
  (linhas 548--550, 613--626 e 673--683); o regulamento CEPEC nº 1622/2018 e as
  perguntas frequentes do PPGCC. São artefatos do próprio repositório e
  documentos públicos; nenhum dado pessoal foi fornecido à ferramenta.
- **Verificação humana/técnica:** os números novos vêm de geradores cobertos
  pelo portão de deriva, e não de cálculo de sessão. O gerador do controlador
  recalcula a decomposição em três classes e **falha** se não reproduzir as três
  linhas do artefato congelado com a regra do produtor original (valor-$p$
  ajustado abaixo de 0,05 e $A_{12}$ fora de $[0{,}44;\,0{,}56]$); reproduziu
  todas. O gerador de engenharia confere o símbolo do artefato contra o valor-$p$
  e as medianas. O limiar aplicado pelo controlador (0,216 e 0,248, e não o
  padrão 0,232437 da classe) foi confirmado pela cadeia de proveniência dos
  lançadores (`OQ-18`), e não por reexecução. A inspeção visual das páginas
  alteradas achou um defeito anterior a esta rodada: o resumo e o abstract ficam
  numa `minipage` que não quebra página, e os textos de HEAD transbordavam ---
  o corpo do resumo caía na página seguinte, e as palavras-chave do abstract
  também. Os dois textos foram reduzidos e cabem numa página cada. Os portões
  `make thesis-tables-check`, `make thesis-doctor`, `make verify-release` e
  `make test` (40 testes) passam; `make thesis` compila 92 páginas sem aviso
  LaTeX e sem linha *overfull*, e as quatro linhas *underfull* que restam
  existem também na compilação anterior.
- **Limitações e pendências:** a QP2 continua sem resposta na configuração
  promovida, por decisão de não reexecutar. A versão da plataforma (`OQ-15`) não
  foi alterada no texto e bloqueia o depósito até decisão do autor e do
  orientador. A divergência de leitura com o CLEI (`OQ-16`) é decisão do autor.
  As pendências institucionais estão em `REVISION_PLAN.md` §5, inclusive a data
  provisória de defesa, que cai num domingo.

### 2026-09-23 — a regularidade da WFG como hipótese e a revisão da linha narrativa (rodada R9)

- **Ferramenta:** Claude Code, da Anthropic, com subagentes de edição e de revisão;
  a interface informa o modelo `claude-opus-5-5`, o que deve ser confirmado antes de
  uma declaração formal.
- **Fase:** revisão argumentativa e editorial, a pedido do autor, depois de uma
  avaliação da espinha dorsal da dissertação.
- **Finalidade:** tornar visível, como hipótese descritiva, a regularidade que três
  famílias de evidência compartilham (a suíte WFG concentra os casos em que o operador
  não rende), corrigir leituras que os artefatos não sustentam e melhorar a qualidade
  do texto.
- **Arquivos afetados:** `tex/cap_I.tex`, `cap_II.tex`, `cap_III.tex`, `cap_IV.tex`,
  `cap_V.tex`, `cap_VI.tex`, `cap_VII_complementares.tex`, `cap_VII.tex`,
  `cap_VIII.tex`, `cap_IX.tex`; `pos/apend_III.tex` (novo); `main.tex`;
  `pre/pre_resumo.tex` e `pre/pre_abstract.tex`; `bib/modelo-tese.bib`;
  `src/python/thesis/build_tab_hosts.py` e `build_tab_fla_dinamica.py`;
  `data-sources.toml`; `REWRITE_SPEC.md`; `REVISION_PLAN.md`; `README.md`; e este
  registro. Tabelas novas `results/thesis/tab_hosts_suite.tex` e
  `tab_dinamica_suite.tex`; notas regeneradas em `tab_hosts_wtl.tex` e
  `tab_hosts_geometria.tex`.
- **Texto científico inserido:** (i) a §8.5 formula a concentração na WFG como
  hipótese, com quatro ressalvas: para o IVF/SPEA2, as três famílias leem a mesma
  coorte; o IVF/NSGA-II não segue o padrão; renovação e suíte não se separam nesta
  amostra; e as propriedades da WFG não foram separadas. (ii) A leitura da regra de
  renovação mudou: as suas decisões coincidem com a partição WFG/demais em 49 das 51
  instâncias, de modo que a acurácia balanceada de 0,754 não mede discriminação
  dentro de uma suíte (`OQ-19`). (iii) As tabelas da família de hospedeiros diziam
  "Wilcoxon pareado", mas o par IVF/SPEA2 é alinhado por ordem, porque as faixas de
  execução não coincidem; as notas passaram a declarar o pareamento por par e a
  sensibilidade sem pareamento, que muda uma única contagem, em HV (`OQ-20`). (iv) O
  Cap. 2 descrevia o SPEA2 com o arquivo inicial de tamanho $N$, remoção de
  duplicatas, preenchimento a partir do arquivo anterior e aptidão calculada depois da
  seleção ambiental; o texto foi corrigido contra Zitzler et al. (2001) e contra a
  implementação da plataforma. A descrição da distância de aglomeração do NSGA-II era
  imprecisa, e não errada: falava em densidade entre os dois vizinhos mais próximos no
  espaço de objetivos, e não na soma, por objetivo, das distâncias normalizadas entre
  os vizinhos adjacentes na frente ordenada. (v) Os argumentos que motivam
  as duas decisões de acoplamento passaram a ser apresentados como argumentos de
  projeto, e não como fatos, porque a ablação não os confirma. (vi) O posicionamento
  exploratório foi para o Apêndice C, e o Cap. 6 ficou só confirmatório.
- **Entradas inspecionadas:** `data/processed/dynamic_signal_test.csv`,
  `data/processed/hosts_paper.csv`, `results/tables/hosts_*_stats.csv`,
  `results/tables/dynamic_signal_{main_tests,lofo}.csv`,
  `results/tables/hosts_geometry_summary.csv`, `config/hosts_front_geometry.csv`,
  `artifact/ppsn2026-ivf-hosts-rev1/tables/hosts_pairing_robustness.csv`,
  `src/python/analysis/compute_hosts_tables.py`,
  `compute_hosts_pairing_robustness.py`, os arquivos `SPEA2.m`,
  `EnvironmentalSelection.m` e `CalFitness.m` da plataforma vendorizada, os
  fluxogramas de `fig/`, e os manuscritos Springer, PPSN-hospedeiros e CLEI. São
  artefatos do próprio repositório; nenhum dado pessoal foi fornecido à ferramenta.
- **Verificação humana/técnica:** os números novos vêm de geradores cobertos pelo
  portão de deriva. O gerador da tabela de renovação falha se não reproduzir
  tp/tn/fp/fn do artefato deixa-uma-família; o de hospedeiros falha se as somas por
  suíte divergirem dos totais, se a orientação do $A_{12}$ não reproduzir o resumo por
  geometria, ou se a recomputação do pareamento não reproduzir os CSVs que as tabelas
  contam. Os caminhos de erro dos três controles foram exercitados. Uma nota gerada
  chegou a inverter o sentido da divergência em DTLZ6 (dizia que a regra mantinha o
  operador ligado, quando o desliga); o gerador passou a derivar o sentido dos dados.
  Três revisões independentes, uma por grupo de capítulos, conferiram remissões,
  números e calibração; os achados foram aplicados. `make thesis-tables-check`,
  `make thesis-doctor`, `make verify-release` e `make test` (40 testes) passam;
  `make thesis` compila 96 páginas sem aviso LaTeX e sem linha *overfull*, e as quatro
  linhas *underfull* são as da rodada anterior. Resumo, abstract e as páginas das
  tabelas novas foram inspecionados renderizados. Uma última passagem qualificou com
  "em 49 de 51 instâncias" as menções curtas à coincidência entre a regra e a partição
  WFG/demais (resumo, abstract, contribuição 5, §8.4 e a ameaça correspondente), que a
  apresentavam como igualdade e apagavam as duas exceções em DTLZ6.
- **Limitações e pendências:** a regularidade da WFG é hipótese; o teste proposto é o
  desenho fatorial da §10.1, que exige nova campanha. A leitura da regra de renovação
  vai além da do CLEI, que reconhece a dependência da família, mas não a coincidência
  de 49 em 51 decisões com a partição WFG/demais (`OQ-19`); revisar o manuscrito é
  decisão do autor. `OQ-15` continua bloqueando o
  depósito. O fluxograma do SPEA2 (`fig/fluxo_spea2_pt.pdf`) ainda diz que o arquivo é
  completado com dominados do arquivo anterior; o texto registra a formulação correta,
  e a figura, sem fonte editável no repositório, precisa ser redesenhada pelo autor.

### 2026-09-23 — correções de fato, coerência e fundamentação após a avaliação (rodada R10)

- **Ferramenta:** Claude Code, da Anthropic; a interface informa o modelo
  `claude-opus-5-5`, o que deve ser confirmado antes de uma declaração formal. A skill
  `$write-scientific-manuscripts` não está disponível neste ambiente; o perfil
  `SCIENTIFIC_WRITING_PROFILE.md` foi aplicado diretamente.
- **Fase:** avaliação da dissertação (nota 8,0/10, com vinte defeitos listados) e, a
  pedido do autor, correção desses defeitos com prioridade para a coerência entre
  capítulos, tabelas, figuras e fontes.
- **Finalidade:** eliminar afirmações que os artefatos, o código ou os manuscritos
  desmentem; alinhar descrições divergentes entre capítulos; completar a fundamentação
  (definições de Pareto, literatura de controle de operadores, citações de métodos e dos
  manuscritos derivados); corrigir legendas e figuras.
- **Arquivos afetados:** `tex/cap_I.tex` a `cap_IX.tex` e `cap_VII_complementares.tex`;
  `pos/apend_II.tex` e `apend_III.tex`; `bib/modelo-tese.bib`; os geradores
  `src/python/thesis/build_fig_resultados.py`, `build_fig_complementares.py`,
  `build_tab_geometria_confirmatoria.py`, `build_tab_fla_dinamica.py`,
  `build_tab_controlador.py`, `build_tab_hosts.py`, `build_tab_engenharia.py`,
  `build_tab_confirmatorio.py` e `ptbr_format.py`; tabelas e figuras regeneradas em
  `results/thesis/`; `REWRITE_SPEC.md`, `REVISION_PLAN.md`, `README.md` e este registro.
- **Texto científico inserido:** definições de dominância, conjunto e fronteira de Pareto
  (Cap. I), com `M` para o número de objetivos, como no restante do texto; §1.4 com os
  três manuscritos derivados e a sua situação editorial; parágrafo da §3.5 sobre controle
  de parâmetros, seleção adaptativa de operadores e seleção de algoritmos; descrição da
  referência da IGD nos RWMOP (§5.3); declaração da duplicata MaF7/DTLZ7 e do seu efeito
  sobre o recorte fora do ajuste (§5.2, §5.5, §6.1, §8.1, §9.1); regra dos rótulos de
  ativação e a diferença 41 × 37 (§7.4, §8.5, §9.3); ameaça "O ambiente de execução não é
  verificável" (§9.4) no lugar da afirmação de versões; divergências de leitura com os
  manuscritos declaradas onde ocorrem (§6.3, §7.4). Correções de coerência: critério de
  continuação dos acoplamentos anteriores (Caps. III e IV), protocolo de seleção dos
  RWMOP, Apêndice C × §5.4, conclusão sobre a especificidade da vantagem, legenda da
  Tabela 6.5, amplitude do DTLZ4, custo de relógio, lista de propriedades da WFG.
- **Entradas inspecionadas:** `MaF7.m`, `DTLZ7.m` e `MaF6.m` da plataforma;
  `IVF_NSGAII.m`, `IVF_NSGAIII.m` e `IVF.m` (acoplamentos anteriores);
  `experiments/process_engineering_suite.m`; `src/python/fla/compute_response.py`;
  `src/python/fla/test_dynamic_signal.py`; `results/tables/dynamic_signal_main_tests.csv`;
  `claims_summary_instance_details.csv`; `fla_response.csv`; o CSV consolidado, pelo filtro
  de coorte; `config/hosts_front_geometry.csv`; `sn-article.tex`, o PPSN-hospedeiros e o
  CLEI; `docs/RELEASE_IDENTITY.md`, `docs/REPRODUCIBILITY_ENVIRONMENT.md` e `VENDOR.md`.
  Metadados bibliográficos novos conferidos no Crossref pelo DOI (Eiben et al. 1999,
  Friedman 1937, Rice 1976, Deb e Deb 2014 e o preprint); as demais entradas novas foram
  copiadas das bibliografias dos manuscritos. O Crossref registra um coautor do preprint
  como "Sávio Menezes"; a entrada usa o nome do manuscrito, Sávio Menezes Sampaio. São
  artefatos do repositório e metadados públicos; nenhum dado pessoal foi fornecido.
- **Verificação humana/técnica:** os números novos do texto foram recalculados a partir
  dos artefatos (recorte com M = 3 sem o MaF7: IGD 11/3/0 e HV 10/4/0; os quatro empates
  de Holm rotulados como "ajuda"; 18 observáveis testados; amplitudes do DTLZ4 e do MaF5).
  Os geradores ganharam verificações que falham se as notas deixarem de valer (observáveis
  exibidos = os de menor valor-p; derrotas irregulares = um único problema). A identidade
  MaF7/DTLZ7 foi conferida no código, e a independência das execuções, valor a valor.
  `make thesis-tables-check`, `make thesis-doctor`, `make verify-release` e `make test`
  (40 testes) passam; `make thesis` compila 98 páginas sem aviso LaTeX, sem *overfull* e
  sem página de texto só com *floats*; as sete figuras regeneradas e as páginas alteradas
  foram inspecionadas renderizadas; o PDF não tem fonte Type 3.
- **Limitações e pendências:** a correção da avaliação anterior quanto ao MaF7 e ao
  DTLZ7: as medianas arredondadas coincidem com M = 2, mas as execuções não são idênticas
  (réplicas independentes da mesma função). `OQ-15` deixou de bloquear o texto, que não
  afirma mais versão, mas os registros de execução continuam ausentes e a errata dos
  manuscritos é decisão do autor, como em `OQ-21` e `OQ-22`. A declaração de contribuição
  (`OQ-10`) não foi redigida. O fluxograma do SPEA2 continua pendente de redesenho.

### 2026-09-24 — conferência da R10 e correções residuais (rodada R11)

- **Ferramenta:** Claude Code, da Anthropic; a interface informa o modelo
  `claude-opus-5-5`, o que deve ser confirmado antes de uma declaração formal. A skill
  `$write-scientific-manuscripts` foi localizada em
  `~/.codex/skills/write-scientific-manuscripts/` e aplicada (instruções, referências de
  estilo em português e de integridade de citações, script de auditoria editorial); a
  entrada da R10 a registrava como indisponível.
- **Fase:** revisão de linha e correção de fatos, a pedido do autor, com a instrução de
  que o texto fosse contido, direto e restrito ao seu objetivo.
- **Finalidade:** conferir, um a um, os vinte defeitos da avaliação de 2026-09-23 contra o
  estado deixado pela R10 e corrigir o que restava, sem ampliar o escopo.
- **Arquivos afetados:** `tex/cap_I.tex`, `cap_III.tex`, `cap_IV.tex`, `cap_V.tex`,
  `cap_VI.tex`, `cap_VII.tex`, `cap_VII_complementares.tex`, `cap_VIII.tex`,
  `cap_IX.tex`; `pos/apend_II.tex` e `apend_III.tex`; `bib/modelo-tese.bib`;
  `src/python/thesis/build_fig_complementares.py` (rótulo do eixo da Figura 7.3) e
  `build_fig_resultados.py` (docstring); `results/thesis/figures/fig_hospedeiros_a12.pdf`,
  regenerada; `REWRITE_SPEC.md`, `REVISION_PLAN.md` e este registro.
- **Texto científico alterado:** nenhuma afirmação nova de resultado. Escopo: o pai
  compartilhado e o critério individual de continuação passaram a ser atribuídos à
  formulação original e aos acoplamentos ao NSGA-II e ao NSGA-III, os únicos cujo critério
  o texto descreve com fonte; o IVF/GDE3 saiu da generalização (Caps. 1 e 3). Categoria: o
  posto médio do Apêndice C é descritivo e não envolve teste, e deixou de ser dito "sem
  correção de multiplicidade" (§5.4, Cap. 6, Apêndice C). Calibração: "reflete
  variabilidade, e não equivalência" passou a "não indica equivalência" (§6.3); "é diferença
  de poder", a "é compatível com diferença de poder" (§8.1.1); "é contraproducente", a
  "tende a ser contraproducente" (§4.2.1), como no Cap. 2; a §3.4 deixou de afirmar lacuna
  na literatura; a §9.1 e a §9.4 ficaram coerentes com a indeterminação do ambiente; a
  §10.2 ("Problemas caros") deixou de afirmar a troca como favorável; a §1.4 diz "gera" em
  vez de "recalcula". Cortes: frases de metacomentário (§7.2, §8.2, Apêndice B) e o
  quantificador "em ordens de grandeza" do Apêndice B, não verificável.
- **Entradas inspecionadas:** os capítulos, apêndices e tabelas geradas no estado da R10;
  `experiments/process_engineering_suite.m` (IGD dos RWMOP contra a fronteira empírica
  viável das execuções comuns; HV com `GetOptimum`); `src/python/thesis/build_fig_resultados.py`
  (posto médio sobre as medianas por instância); `paper/springer-nature/src/sn-article.tex:165`
  (sem descrição do critério do IVF/GDE3); `docs/RELEASE_IDENTITY.md` e o histórico de
  `paper/clei2026/` (situação editorial); registros Crossref de
  `10.1007/978-3-642-21434-9_7`, `10.1214/aoms/1177730491`, `10.1007/978-3-540-87700-4_18`
  e `10.1162/evco_a_00236`, e a página do periódico Complex Systems para Deb e Agrawal
  (1995), sem DOI. São artefatos do repositório e metadados públicos; nenhum dado pessoal
  foi fornecido.
- **Verificação humana/técnica:** a regeneração completa (`make thesis-tables`) alterou
  apenas `fig_hospedeiros_a12.pdf`, conferido por checksum antes e depois; o rótulo do eixo,
  antes cortado na borda superior, cabe na figura renderizada. `make thesis-tables-check`,
  `make thesis-doctor`, `make verify-release` e `make test` (40 testes) passam; `make
  thesis` compila 98 páginas sem aviso LaTeX, sem *overfull*, sem referência indefinida e
  sem página só com *floats*; as quatro linhas *underfull* são as das rodadas anteriores. A
  primeira compilação da rodada foi interrompida por um `head` no *pipe*; a conferência
  final usa o PDF recompilado, e as páginas alteradas foram inspecionadas renderizadas. A
  auditoria editorial acusou três "placeholders" que são a palavra "todo" do português e
  frases longas já existentes; nenhuma alteração decorreu dela.
- **Limitações e pendências:** o critério de continuação do IVF/GDE3 continua sem
  descrição, por falta de fonte examinada. A entrada `maturana2009adaptive` segue errada nos
  manuscritos CLEI e PPSN-dinâmica (`REVISION_PLAN.md` §4). As decisões de autor e
  orientador (`OQ-09`, `OQ-10`, `OQ-15`, `OQ-21`, `OQ-22`) não mudaram.

### 2026-09-24 — calibração da linha argumentativa e dois fatos da proposta (rodada R12)

- **Ferramenta:** Claude Code, da Anthropic; a interface informa o modelo
  `claude-opus-5-5`, o que deve ser confirmado antes de uma declaração formal. A skill
  `$write-scientific-manuscripts` foi aplicada: instruções, referências de estilo em
  português, argumentação, relato quantitativo, arquitetura e integridade, e script de
  auditoria editorial.
- **Fase:** revisão substantiva, a pedido do autor, depois de uma avaliação da linha
  argumentativa que apontou objetivo geral mais amplo do que a evidência responde,
  mecanismos de projeto afirmados como fatos, ressalvas repetidas entre capítulos e
  Conclusões que terminavam no que falta.
- **Finalidade:** executar esses pontos com precisão, sem ampliar alegações nem acrescentar
  resultados.
- **Arquivos afetados:** `tex/cap_I.tex`, `cap_II.tex`, `cap_IV.tex`, `cap_VI.tex`,
  `cap_VII.tex`, `cap_VII_complementares.tex`, `cap_VIII.tex` e `cap_IX.tex`;
  `pre/pre_resumo.tex` e `pre_abstract.tex`; `REWRITE_SPEC.md`, `REVISION_PLAN.md`,
  `README.md` e este registro. Nenhum gerador, tabela, figura ou código MATLAB foi alterado.
- **Texto científico alterado:** (i) objetivo geral, contribuições, resumo e abstract:
  "determinar se, por que e em que condições" passou a avaliar eficácia, magnitude e
  instâncias e a investigar atribuição, dependência do hospedeiro e decisão de uso. (ii)
  Gatilho (§2.3.2, §4.1, §4.5): o texto dizia, como o Springer, que a condição fica mais
  difícil de satisfazer e que a intensificação se concentra no início; a regra implementada
  limita a fração acumulada e fica mais fácil de satisfazer depois de uma geração sem
  ativação (`OQ-23`). (iii) Laço do hospedeiro (§4.1, Algoritmo 4.1, §8.2, §8.6, §9.1, §10.1,
  resumo e abstract): o texto dizia que uma geração sem ativação é idêntica à do SPEA2
  canônico; o IVF/SPEA2 recalcula a aptidão antes do torneio, e o SPEA2 da plataforma não
  (`OQ-24`), diferença que nem a comparação confirmatória nem a ablação separam. (iv)
  Critério coletivo (§4.2.2): as duas médias passaram a ser definidas pelo contexto em que
  são calculadas; o texto declara que um ciclo sem melhora não é desfeito, o que a média de
  F registra e as duas propriedades que limitam essa leitura; a afirmação "autolimitante",
  não medida, saiu. (v) Pai dissimilar (§4.2.1, resumo): "pai distinto" passou a pai
  escolhido para cada mãe, com a exclusão da própria mãe, K = min(3, n_c), o sorteio de dois
  candidatos e o vetor de objetivos anterior à perturbação; a motivação passou a hipótese
  explícita. (vi) Discussão e Conclusões: a QP2 delimita o alcance do resultado nulo; a QP4
  distingue separar ajuda de não ajuda de detectar prejuízo; a §8.5 trata a WFG como
  marcador empírico; a conjectura mecanicista da §8.1.1 saiu; as Conclusões distinguem
  eficácia, atribuição e decisão de uso e terminam na contribuição. (vii) Enxugamento: as
  respostas às QP saíram dos Caps. 6 e 7, pela regra do `REVISION_PLAN.md` §2, e as
  ressalvas de reprodutibilidade, sobreposição, ablação e renovação–suíte ficaram num lugar
  canônico, com remissão.
- **Entradas inspecionadas:** `IVFSPEA2V2.m`, `IVF_V2.m`, `CalFitness.m` e
  `EnvironmentalSelection.m` do acoplamento; `SPEA2.m`, `CalFitness.m` e
  `EnvironmentalSelection.m` da plataforma; `IVFSPEA2.m` da formulação anterior;
  `IVFSPEA2_P2.m` e `scripts/experiments/run_ablation_v2_phase3_batch_common.m` da ablação;
  `sn-article.tex:190-254`; a descrição do gatilho nos manuscritos PPSN-hospedeiros e CLEI;
  `docs/IVFSPEA2_EVIDENCE_MODEL.md`. São artefatos do repositório; nenhum dado pessoal foi
  fornecido.
- **Verificação humana/técnica:** a propriedade do gatilho foi verificada por simulação
  exata da regra de `IVF_V2.m:27` (N = 100, r = 0,225, 999 gerações): nenhuma suspensão com
  12 avaliações por ativação; 62 suspensões com 24, uma a cada 16 gerações, 31 em cada
  metade. O recálculo de aptidão foi conferido nas quatro classes, e a equivalência das
  funções de aptidão e de seleção, por `diff`. Nenhum número de resultado mudou; os números
  citados vêm das tabelas geradas. `make thesis-tables-check`, `make thesis-doctor`, `make
  verify-release` e `make test` (40 testes) passam; `make thesis` compila 98 páginas, sem
  aviso LaTeX e sem *overfull*, com as quatro linhas *underfull* das rodadas anteriores. A
  paginação foi comparada capítulo a capítulo com uma compilação da versão anterior, e as
  páginas do resumo, do abstract, do Algoritmo 4.1 e dos Caps. 4 e 6 a 10 foram
  inspecionadas renderizadas; um deslocamento de *floats* no Cap. 6 e uma página com duas
  linhas no Cap. 9 foram corrigidos pelo texto. A auditoria editorial acusou frases longas;
  as que a rodada introduziu foram divididas, e o único item alto é a palavra "todo" da
  definição de dominância.
- **Limitações e pendências:** o efeito do recálculo de aptidão sobre a vantagem medida não
  é conhecido, e a campanha de controle depende de decisão do autor (`OQ-24`). A errata do
  Springer quanto ao gatilho e ao laço do hospedeiro é decisão do autor (`OQ-23`, `OQ-24`).
  O comentário de `IVFSPEA2V2.m` que descreve `R` como "fraction of total FE budget" continua
  impreciso: a rodada não alterou código.

### 2026-09-27 — revisão científica e reanálise da dissertação

- **Ferramenta:** OMP/Codex, da OpenAI; a interface informa o modelo
  `openai-codex/gpt-6-sol`, a confirmar antes da declaração formal. Revisores
  auxiliares configurados examinaram separadamente ciência, números e fontes;
  seus modelos não foram informados.
- **Fase:** revisão científica e reanálise de resultados já produzidos.
- **Finalidade:** executar o plano de revisão sem novas campanhas experimentais,
  distinguindo evidência confirmatória, análise exploratória e limites de
  validação e de atribuição.
- **Arquivos afetados:** `tex/cap_I.tex`, `cap_II.tex`, `cap_V.tex`, `cap_VI.tex`,
  `cap_VII.tex`, `cap_VII_complementares.tex`, `cap_VIII.tex`,
  `pre/pre_resumo.tex` e `pre/pre_abstract.tex`; geradores em
  `src/python/thesis/` e tabelas geradas em `results/thesis/`;
  `data-sources.toml`, `REVISION_PLAN.md`, `bib/modelo-tese.bib`,
  `paper/springer-nature/bib/sn-bibliography.bib` e
  `paper/springer-nature/Makefile`. Nenhum dado bruto, artefato congelado ou
  código MATLAB foi alterado.
- **Texto científico alterado:** métodos, resultados, discussão, conclusões,
  resumo e abstract passaram a delimitar o alcance da correção de Holm, das
  magnitudes e do bootstrap, da calibração histórica, da ablação, da suíte de
  engenharia e da validação da regra de ativação. As tabelas novas descrevem
  magnitude fora do ajuste, sensibilidade exploratória e robustez por grupos;
  a validação após escolha de sinal e janela não foi apresentada como
  prospectiva. Metadados bibliográficos foram corrigidos sem criar fonte nova.
- **Entradas inspecionadas:** manuscritos e artefatos locais versionados,
  geradores, tabelas, scripts e documentos de evidência do repositório;
  consultas externas limitaram-se a metadados bibliográficos públicos.
  O material da dissertação pode ser inédito; sua classificação de
  confidencialidade deve ser confirmada pelo autor. Não foram fornecidos
  dados pessoais sensíveis ao registro nem enviados trechos do manuscrito
  a serviços externos além dos modelos configurados.
- **Verificação humana/técnica:** houve auditorias independentes de números,
  argumentos e referências, com correção dos achados aceitos. Passaram
  `make thesis-tables-check`, `make thesis-doctor`, `make thesis`,
  `make paper`, `make verify-release` e `make test` (58 testes Python);
  a comparação de avisos LaTeX não apontou novos bloqueios e as páginas
  afetadas foram inspecionadas renderizadas. A conferência e aprovação
  humana do conteúdo ainda cabem ao autor e ao orientador.
- **Limitações e pendências:** não houve campanha nova nem validação
  prospectiva da regra selecionada. O texto integral da fonte primária de
  Holm não foi conferido; o DOI inválido foi removido sem substituição.
  Divergências de triagem e proveniência da suíte de engenharia no artigo
  Springer exigem decisão editorial do autor. A declaração de uso de IA
  deve especificar ferramenta e finalidade no texto e na exposição
  eletrônica pertinentes, no local exigido pela UFG, pelo PPGCC e pelo
  veículo, após definição do autor e do orientador.

### 2026-09-28 — revisão científica da Discussão (rodada R13)

- **Ferramenta:** omp; a interface desta sessão informa o modelo
  `anthropic/claude-opus-5-5`, a confirmar antes da declaração formal. A entrada de
  2026-09-27 registra outro modelo (`openai-codex/gpt-6-sol`); o autor deve conferir
  na interface qual modelo produziu cada sessão. Revisores auxiliares configurados
  (quantitativo, científico e de fontes) atuaram separadamente; seus modelos não foram
  informados. Foram aplicadas as skills de argumentação científica, escrita em
  português, auditoria quantitativa, verificação de evidência, estrutura da tese e
  qualidade LaTeX.
- **Fase:** revisão científica substantiva, sem novas campanhas experimentais.
- **Finalidade:** corrigir inferências, respostas às QP, diálogo com a literatura e
  fechamento do Cap. 8, a partir de um diagnóstico anterior (C1–C8, A1–A7) usado como
  lista de problemas, e não como fonte, segundo decisões editoriais do autor para a
  rodada.
- **Arquivos afetados:** `tex/cap_VII.tex` (Cap. 8, reescrito); `tex/cap_III.tex`,
  `cap_IV.tex`, `cap_VI.tex`, `cap_VII_complementares.tex`, `cap_VIII.tex`,
  `cap_IX.tex`, `pre/pre_resumo.tex` e `pre/pre_abstract.tex` (coerência);
  `src/python/thesis/build_tab_wfg_exploratoria.py` (novo),
  `build_tab_ativacao_robustez.py`, `build_all.py`, `build_apendice_fontes.py` e a
  documentação de `build_tab_geometria_confirmatoria.py`; `config/wfg_properties.csv`
  (novo); tabelas geradas `tab_wfg_exploratoria`, `tab_ativacao_robustez` e
  `apendice_fontes`; `REVISION_PLAN.md`, `REWRITE_SPEC.md`, `data-sources.toml` e este
  registro. Nenhum dado bruto, artefato congelado, parâmetro experimental, protocolo
  estatístico ou artigo de origem foi alterado; nenhum número de resultado preexistente
  mudou.
- **Texto científico alterado:** (i) QP1: títulos das QP alinhados ao Cap. 1; eficácia
  atribuída à implementação completa, que também recalcula a aptidão; magnitude sem
  seleção pelo teste ($A_{12}$ mediano 0,756, $\Delta$ +1,15%) separada dos resumos de
  vitórias e derrotas; $A_{12}$ e $\Delta$ tratados como medidas distintas, sem leitura
  de custo, saldo ou relevância prática; saíram "custam mais" e a generalização a
  operadores de intensificação. (ii) QP2: orçamento de calibração (50.000 contra
  100.000 avaliações); hipótese de densidade como justificativa de projeto; a retenção
  de descendentes registrada numa variante instrumentada, em outra coorte, foi descrita
  como fora da evidência de atribuição, e não como não medida. (iii) QP3 em dois níveis,
  sem "Sim", com a assimetria de ajuste entre pipelines (`OQ-25`) e contraste com os
  estudos de origem do IVF/NSGA-II e do IVF/NSGA-III sem tratá-los como replicação.
  (iv) QP4 com veredito explícito, três níveis de evidência e a partição WFG/demais
  rotulada como pós-hoc. (v) §8.5 reescrita como concentração de resultados menos
  favoráveis, restringida por tabulação descritiva por função, configuração e
  separabilidade. (vi) Conclusões com escopo e remissão ao Cap. 9. (vii) Cap. 9 com
  novas ameaças: orçamento de calibração, assimetria de ajuste e análises formuladas
  depois dos resultados; linguagem de custo computacional uniformizada nos Caps. 4, 8,
  9 e 10; resumo e abstract com a magnitude não condicionada.
- **Entradas inspecionadas:** artefatos, código MATLAB e Python, tabelas geradas e
  manuscritos do repositório; fontes bibliográficas públicas: `references/ivfnsga2.pdf`
  (IVF/NSGA-II, 2017), PDF público da tese de Sampaio (UFG, 2024), Zhou et al. (2011),
  Liefooghe et al. (versão HAL), Kerschke e Trautmann (arXiv), cópia de Huband et al.
  (2006) no Academia.edu, resumos de Fialho et al. e de Maturana et al., e registros
  Crossref. As consultas externas levaram apenas metadados bibliográficos; nenhum trecho
  do manuscrito foi enviado a serviço externo além dos modelos configurados, e nenhum
  dado pessoal foi fornecido.
- **Verificação humana/técnica:** cálculos novos produzidos por gerador e conferidos por
  código; `make thesis-tables-check`, `make thesis-doctor` (8 fontes, 141 caminhos),
  `make verify-release` e `make test` (58 testes) aprovados; `make thesis` compila 108
  páginas sem item bloqueante novo em relação à linha de base, sem *overfull*, com as
  quatro linhas *underfull* preexistentes; páginas afetadas, sumário, lista de tabelas e
  bibliografia inspecionados renderizados. Auditorias independentes quantitativa (sem
  divergência), científica e fonte→afirmação; os achados aceitos foram incorporados. A
  conferência e a aprovação humanas do conteúdo cabem ao autor e ao orientador.
- **Limitações e pendências:** a tabela de propriedades de Huband et al. foi conferida
  em cópia não editorial; Fialho et al. e Maturana et al. só pelos resumos; a frase do
  Cap. 3 sobre o IVF/GDE3 não foi conferida na fonte primária. Os ajustes feitos depois
  das auditorias não foram reauditados de forma independente. Ficam com o autor:
  `OQ-24`, `OQ-25` (errata do PPSN), `OQ-03` (eventual análise descritiva de
  convergência), inclusão do artigo CEC 2023 no `.bib` e normalização de metadados
  bibliográficos. A declaração de uso de IA deve especificar ferramenta e finalidade no
  local exigido pela UFG, pelo PPGCC e pelo veículo.

### 2026-10-02 — fechamento científico: disponibilidade dos brutos, formulações, fluxograma e bibliografia (rodada R16)

- **Ferramenta:** Claude Code, da Anthropic, em ambiente omp, com subagentes de revisão
  (científica e de evidência externa); o ambiente informa o modelo
  `anthropic/claude-opus-5-5`, o que deve ser confirmado antes de uma declaração formal.
- **Fase:** fechamento de pendências delimitadas e leitura integrada.
- **Finalidade:** alinhar Apêndices A e B, manifesto e gerador sobre os dados brutos;
  examinar três formulações candidatas (Caps. 1, 3 e 4); corrigir o fluxograma do SPEA2;
  fechar as pendências bibliográficas registradas; verificar a continuidade QP↔respostas.
- **Arquivos afetados:** `tex/cap_I.tex`, `cap_III.tex`, `cap_IV.tex`; `pos/apend_II.tex`;
  `bib/modelo-tese.bib`; `data-sources.toml`; `src/python/thesis/build_apendice_fontes.py`
  e `results/thesis/apendice_fontes.tex` (regenerado); `fig/src/fluxo_spea2_pt.tex` (novo)
  e `fig/fluxo_spea2_pt.pdf`; `REVISION_PLAN.md` §4.
- **Texto científico alterado:** generalização sobre velocidade de convergência
  recalibrada (Cap. 1); hipótese de projeto deixou de ser afirmada como inadequação
  (Cap. 3); frase do IVF/GDE3 delimitada ao resumo oficial; remissão do Cap. 4 alinhada à
  QP2 comparativa; §4.5 reescrita sem fator multiplicativo de custo, com truncagem e
  recálculo de aptidão; estado dos brutos corrigido nos Apêndices A e B. Nenhum número de
  resultado, teste, correção ou coorte mudou.
- **Entradas inspecionadas:** código MATLAB do IVF/SPEA2 e do SPEA2 da plataforma;
  manifestos de release e `docs/RELEASE_IDENTITY.md`; listas de arquivos das três versões
  publicadas do registro Zenodo; registros Crossref; página e PDF público do capítulo de
  Camilo-Junior e Yamanaka (IntechOpen); resumo do IVF/GDE3 e do IVF/NSGA-III no IEEE
  Xplore; PDF público da tese de Sampaio (2024). As consultas externas levaram apenas
  identificadores e metadados.
- **Verificação humana/técnica:** `make thesis-tables-check` e `make thesis-doctor`
  aprovados; `bib_check.py` ok=53; `make thesis` sem bloqueante novo nem overfull, com as
  quatro linhas underfull preexistentes; fluxograma, §4.5, bibliografia e Apêndices A e B
  inspecionados renderizados. A conferência e a aprovação humanas cabem ao autor e ao
  orientador.
- **Limitações e pendências:** textos integrais do IVF/GDE3 e do artigo CEC 2023 não
  acessados; redação final não reauditada de forma independente; comentário de cabeçalho
  de `IVFNSGAIII.m` e erratas dos artigos ficam fora desta rodada.

### 2026-10-03 — coluna $M$, recorte sem MaF7 e centralização vertical dos rótulos de grupo

- **Ferramenta:** opencode omp, com subagentes de edição em paralelo; o ambiente reporta
  o modelo `opencode-go/deepseek-v4.1-flash`, que deve ser confirmado antes de uma
  declaração formal.
- **Fase:** apresentação e legibilidade das tabelas geradas, e decisão editorial do autor
  sobre o que a Tabela 6.3 torna visível; sem reanálise estatística e sem nova campanha.
- **Finalidade:** (i) remover o prefixo `M` do valor da coluna cujo cabeçalho já é `$M$`;
  (ii) retirar da Tabela 6.3 a linha descritiva "Todas, sem MaF7" e a sentença de nota que
  a explicava, espelhando a decisão na prosa dos Capítulos 5, 6, 7 e 8; (iii) centralizar
  no eixo vertical, com `\multirow`, todos os rótulos que agrupam várias linhas nas
  tabelas geradas.
- **Arquivos afetados:** `src/python/thesis/latex_table.py` (novo tipo de célula
  `Multirow`, que emite `\multirow{n}{*}{...}`); nove construtores
  `src/python/thesis/build_tab_*.py` (`magnitude_confirmatoria`, `ativacao_robustez`,
  `confirmatorio`, `controlador`, `engenharia`, `fla_dinamica`,
  `geometria_confirmatoria`, `hosts`, `posicionamento`); `thesis/masters/main.tex`
  (`\usepackage{multirow}`); `thesis/masters/tex/{cap_V,cap_VI,cap_VII,cap_VIII}.tex`;
  regeneradas 11 tabelas em `results/thesis/`, com 40 células `\multirow`, espelhadas em
  `thesis/masters/generated/`.
- **Texto científico alterado:** removidos o recorte quantificado sem MaF7 (IGD 11 vitórias
  em 14 instâncias, Δ mediano $+1{,}15\%$; HV 10/14, $+0{,}50\%$) e as duas afirmações de
  que o Capítulo 6 reporta esse recorte com e sem a instância duplicada; removida a menção
  "11 sem o MaF7" da resposta à QP1. Preservadas a declaração da duplicata funcional
  MaF7/DTLZ7 e todas as contagens, correções e coortes; nenhum número, teste ou família de
  Holm mudou. Nas tabelas, mudaram apenas células de rótulo: nenhum valor.
- **Entradas inspecionadas:** apenas artefatos locais do repositório
  (`results/tables/claims_summary_instance_details.csv`,
  `data/processed/todas_metricas_consolidado_with_modern.csv`, as tabelas de
  `results/thesis/`, a prosa de `tex/` e `REWRITE_SPEC.md` OQ-21). Nenhuma consulta externa
  e nenhum conteúdo inédito enviado a terceiros.
- **Verificação humana/técnica:** varredura mecânica das 24 tabelas — zero rótulo de grupo
  sem `\multirow` e corpo normalizado idêntico ao da versão anterior, o que confirma que só
  o invólucro do rótulo mudou; `make thesis-tables-check` aprovado; `make thesis` sem
  bloqueante novo (`latex_check.py --compare`: zero novos, três linhas *underfull*
  preexistentes) e zero *overfull*; páginas 53, 55, 57, 65, 73, 75, 77 e 79 rasterizadas e
  inspecionadas. Três defeitos introduzidos pelos subagentes de edição (rótulo repetido em
  `controlador_wtl` e `engenharia_wtl`; duplicação do rótulo de métrica e deriva de
  espaçamento em `posicionamento`) foram detectados pela varredura e corrigidos antes da
  entrega. A conferência e a aprovação humanas cabem ao autor e ao orientador.
- **Limitações e pendências:** a convenção `2`/`3` na coluna `$M$`, a remoção do recorte e a
  centralização foram decisões do autor nesta sessão; `REWRITE_SPEC.md` OQ-21 (iii) ainda
  descreve o recorte removido e não foi emendado;
  `paper/springer-nature/src/sn-article.tex` mantém 13 grupos de rótulos no mesmo estado
  anterior e ficou fora do escopo. Esta sessão é posterior à R17 (2026-10-03, ainda sem
  entrada neste log) e não recebeu número de rodada em `REWRITE_SPEC.md` §6.2.

### 2026-10-03 — ilustrações esquemáticas do Capítulo 2 e legendas concisas

- **Ferramenta:** Claude Code, da Anthropic, em ambiente omp, sem subagentes; o ambiente
  reporta o modelo `anthropic/claude-opus-5-5`, que deve ser confirmado antes de uma
  declaração formal.
- **Fase:** ilustração esquemática e edição de legendas e da prosa que as cita; sem
  reanálise estatística e sem nova campanha.
- **Finalidade:** (i) acrescentar ao Capítulo 2 três figuras esquemáticas: a atribuição de
  aptidão e a truncagem do SPEA2 (Figura 2.1) e o cálculo da IGD e do HV (Figuras 2.4 e
  2.5); (ii) aplicar a decisão do autor de manter legendas concisas às três legendas novas
  e a nove legendas preexistentes (Figuras 4.1, 4.2, 6.1, 6.2, 7.1 a 7.5), levando para o
  parágrafo que cita cada figura a leitura dos elementos gráficos, a coorte e as
  ressalvas; (iii) registrar a regra em `SCIENTIFIC_WRITING_PROFILE.md` §9.
- **Arquivos afetados:** `thesis/masters/fig/src/{spea2_aptidao_pt,igd_ilustracao_pt,hv_ilustracao_pt}.tex`
  (novos) e os PDFs correspondentes em `thesis/masters/fig/`;
  `thesis/masters/fig/src/fluxo_spea2_pt.tex` e `thesis/masters/fig/fluxo_spea2_pt.pdf`
  (Figura 2.2, revisão na mesma sessão);
  `thesis/masters/tex/{cap_II,cap_IV,cap_VI,cap_VII_complementares}.tex`;
  `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md`; `thesis/masters/README.md` (nota sobre
  desenhos estáticos em `fig/`).
- **Texto científico alterado:** no Capítulo 2, um parágrafo de leitura da Figura 2.1 e
  frases de leitura das Figuras 2.4 e 2.5; o texto do Capítulo 2 não antecipa o argumento
  do Capítulo 4. No Capítulo 4, um parágrafo novo cita a Figura 4.1, antes não citada,
  descreve os traços do desenho e declara que o $F$ da figura é $n_{\text{ivf}}$, e não a
  aptidão; a frase sobre o doador primário da formulação original passou a nomeá-lo (o
  melhor indivíduo coletado, como no Capítulo 2) e a remeter à Figura 4.2a. Nos Capítulos 6
  e 7, parágrafos de leitura receberam das legendas a coorte, o $n$, a descrição dos
  elementos gráficos e as ressalvas, sem alteração de texto. Removidos sem transferência:
  na legenda da Figura 7.2, "evidenciando uma região ampla de bom desempenho, e não um ponto
  ótimo isolado", mais forte que o texto já existente, que registra postos próximos sem
  demonstrar equivalência; na legenda da Figura 4.1, "setas bidirecionais" e "fluxo
  condicional", sem correspondência no desenho, substituídos pela leitura do desenho
  (contínuo: fluxo de controle; tracejado: conjuntos de soluções); direções "menor é
  melhor"/"maior é melhor" e remissões a equações já presentes no texto. Nenhum número de
  resultado, teste, coorte, família ou correção mudou. Os números novos (14 soluções,
  $k = 3$, $R = 6$, nove não dominadas e sete vagas, e as IGD e os HV usados para conferir
  os rótulos qualitativos) pertencem aos exemplos ilustrativos, foram calculados por
  script com a regra de `CalFitness.m` e `EnvironmentalSelection.m` do SPEA2 no PlatEMO e
  estão tabelados nos cabeçalhos das fontes TikZ.
- **Entradas inspecionadas:** apenas artefatos locais do repositório
  (`src/matlab/lib/PlatEMO/Algorithms/Multi-objective optimization/SPEA2/`,
  `src/python/thesis/build_fig_resultados.py`, as figuras de `generated/figures/` e de
  `fig/`, a prosa de `tex/`). Nenhuma consulta externa e nenhum conteúdo inédito enviado a
  terceiros.
- **Verificação humana/técnica:** `claims.py diff` nos quatro capítulos, com cada número,
  referência e marcador de força removido conferido no texto que permanece;
  `prose_audit.py` sem achado alto ou médio; `make thesis` sem bloqueante novo
  (`latex_check.py --compare`: zero novos, três linhas *underfull* preexistentes) e zero
  *overfull*; páginas 22, 23, 29, 30, 41, 43, 57, 58, 62, 66, 67, 68, 71, 77 e 81
  rasterizadas e inspecionadas. A conferência e a aprovação humanas cabem ao autor e ao
  orientador.
- **Limitações e pendências:** a Figura 4.1 (`fig/fluxo_ivfspea2_pt.pdf`) não tem fonte
  editável no repositório, e a colisão de $F$ foi tratada no texto, não no desenho; os
  títulos dos painéis da Figura 6.2, gerados por `build_fig_resultados.py`, chamam as
  execuções de "Regime de convergência" e "Regime de estagnação", rótulos interpretativos
  que o texto não sustenta e que só mudam pelo gerador; a legenda da figura de
  `pos/apend_III.tex`, fora da compilação, não foi tratada; a figura do Capítulo 4 que
  retoma a nuvem da Figura 2.1 não foi feita; não houve revisão independente (`/gate`).
- **Revisão na mesma sessão:** a pedido do autor, a legenda interna da Figura 2.1 passou a
  ter um símbolo por significado: as dominadas usam o mesmo círculo vazado nos três
  painéis (antes, um segundo círculo esmaecido em (b) e (c)); a removida pela truncagem é
  só um "×" (antes, círculo vazado com "×"); o significado dos números de (a) saiu da
  legenda e foi para uma nota dentro do painel; o rótulo "maior $F$" ganhou linha de
  chamada. A pedido do autor, a Figura 2.2 (`fig/src/fluxo_spea2_pt.tex`) perdeu a caixa
  "F = 0", herdada do fluxograma do IVF/SPEA2 e sem função no SPEA2, e o seu "na ordem de
  F" passou a "na ordem de $F(i)$", de modo que $F$ denota só a aptidão. Nenhuma
  coordenada, valor ou texto da dissertação mudou; página 23 conferida após
  `make thesis`.
