# Normas do PPGCC/UFG, depósito e declaração de IA

Conferido em 2026-09-24 (detalhes e demais fontes: `docs/ai-scientific-writing/research.md`
§3). Norma muda: antes de afirmar exigência ao autor, reabrir a fonte primária.

## Formato e produção

- **Resolução INF nº 02/2023/PPGCC** (vigente; lista em
  <https://ppgcc.inf.ufg.br/p/35372-legislacao-e-normativas>, atualizada em 28/05/2026).
  Art. 2º: modelo tradicional (monográfico) ou alternativo (escandinavo). Art. 3º: a opção
  "deverá constar na contra capa do documento". A dissertação é monográfica; a declaração do
  formato ainda falta (`REVISION_PLAN.md` §5). Escandinavo exigiria ≥ 2 artigos com o discente
  como autor principal e o orientador como coautor (Art. 7º) — mudar de formato é decisão do
  autor e do orientador, nunca inferência.
- **Resolução INF nº 002/2024/PPGCC**: mestrado com 1ª matrícula a partir de 2023/2 precisa de
  um aceite definitivo de trabalho completo (periódico com percentil Scopus/WoS > 0 ou
  conferência nacional com H5 ≥ 1) antes de pedir a defesa.
- Regulamento específico por coorte: CEPEC 1983/2026 (ingresso ≥ 2026/1) ou 1622/2018 (demais);
  Regulamento Geral CEPEC 1847/2023. A coorte do autor não é pública: perguntar.

## Classe LaTeX

`inf-ufg.cls` deriva da classe do INF mantida pelo Prof. Humberto Longo
(<https://ww2.inf.ufg.br/~longo/classe-inf/classe-inf.html>), template de fato do instituto, sem
declaração formal de "oficial" pelo PPGCC. O projeto preserva o original e compila com o
derivado `inf-ufg-tectonic.cls` (Tectonic/XeTeX).

## Depósito (SIBI/UFG)

- TECA e comprovante via SEI; PDF final e Formulário de Metadados por e-mail à biblioteca;
  retorno em até 8 dias úteis; Resolução CEPEC 832 (BDTD) em atualização.
  <https://bc.ufg.br/n/33055-procedimentos-para-envio-das-teses-e-dissertacoes-para-publicacao-na-bdtd>
- Ficha catalográfica só pelo gerador oficial (<https://bc.ufg.br/p/3397-ficha-catalografica>);
  agentes nunca redigem nem editam o texto da ficha. Mudar o título exige novo TECA.

## Uso de IA

- **Portaria CNPq nº 2.664/2026**, Art. 9º, I: "c) declarar o uso de ferramentas de
  Inteligência Artificial Generativa - IAG, de qualquer espécie e em qualquer fase do
  desenvolvimento da pesquisa (concepção, redação, análise de dados, submissão) especificando
  nos respectivos textos e exposições eletrônicas, a ferramenta utilizada e a finalidade"; "d)
  é vedada a submissão de conteúdo gerado por IAG como se fosse de autoria humana". Aplicação
  a discente sem bolsa CNPq é indireta; confirmar com o orientador.
- **Guia de Integridade Acadêmica UFG 2024**, cap. 9 (orientativo): verificação humana,
  transparência, IA não é autora.
- CAPES: nenhum documento primário localizado; não citar como norma.
- Registro de trabalho: `thesis/masters/AI_ASSISTANCE_LOG.md` (uma entrada por sessão ou lote
  material). A declaração final é redigida a partir dele, no local que o PPGCC indicar.
- Artigos: IEEE e ACM → *Acknowledgments*; Springer Nature → *Methods* (imagem gerada por IA
  proibida); arXiv → declarar uso significativo. IA nunca é autora.

## ABNT (edições por fontes secundárias, `[INFERÊNCIA]`)

NBR 14724:2024 (trabalhos acadêmicos), 10520:2023 (citações: sobrenome só com inicial maiúscula;
"et al." a partir de 4 autores), 6023 (referências; 2018 + errata; 3ª edição de 2025), 6028:2021
(resumo: terceira pessoa; voz ativa deixou de ser exigida). O texto das normas não foi lido; o
estilo de citação é o do `.bst` do projeto. Divergência entre o `.bst` e a NBR 10520:2023 é
decisão do autor, registrada, nunca correção silenciosa.
