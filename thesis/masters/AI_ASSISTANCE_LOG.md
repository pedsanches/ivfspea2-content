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
