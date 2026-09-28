---
name: thesis-structure
description: Função de cada capítulo da dissertação IVF/SPEA2, continuidade objetivos→métodos→resultados→discussão→conclusões, consistência entre capítulos, resumo e abstract, e requisitos do PPGCC/UFG (formato, depósito, declaração de uso de IA). Use em auditoria de capítulo, passagem final e dúvidas de normalização institucional.
---

# Estrutura da dissertação

## Mapa (ordem do PDF ≠ nome do arquivo)

| Cap. | Arquivo | Função |
|---|---|---|
| 1 | `tex/cap_I.tex` | Problema, lacuna, objetivo geral, QP1–QP4, contribuições, publicações derivadas, roteiro. |
| 2 | `tex/cap_II.tex` | SPEA2, hibridização, IVF original, indicadores (IGD, HV), estatística. |
| 3 | `tex/cap_III.tex` | Posicionamento: linhagem IVF, memética, variantes do SPEA2, FLA, controle de operadores. |
| 4 | `tex/cap_IV.tex` | Proposta: acoplamento, gatilho e orçamento, pai dissimilar, critério coletivo, parâmetros. |
| 5 | `tex/cap_V.tex` | Protocolo: plataforma, suítes, referências e métricas, estatística, partição 12 × 39. |
| 6 | `tex/cap_VI.tex` | Resultado confirmatório QP1 (contagens, magnitude, por instância). |
| 7 | `tex/cap_VII_complementares.tex` | Famílias de apoio: engenharia, calibração/ablação, hospedeiros, ativação. |
| 8 | `tex/cap_VII.tex` | Discussão e conclusões: **único lugar** que responde QP1–QP4. |
| 9 | `tex/cap_VIII.tex` | Ameaças à validade (lugar canônico das ressalvas). |
| 10 | `tex/cap_IX.tex` | Trabalhos futuros. |
| A–C | `pos/apend_I–III.tex` | Fontes e reprodutibilidade; disponibilidade de dados; posicionamento exploratório. |

Pré-textuais: `pre/pre_resumo.tex`, `pre/pre_abstract.tex`. Bibliografia: `bib/modelo-tese.bib`.

## Regras de continuidade

- Cada QP é respondida só no Cap. 8; os demais capítulos remetem (`REVISION_PLAN.md` §2).
- Ressalva tem lugar canônico (Cap. 9 ou a seção indicada no plano) e é remetida, não repetida.
- Objetivos específicos (Cap. 1) ↔ QPs ↔ protocolo (Cap. 5) ↔ respostas (Cap. 8) ↔
  conclusões ↔ resumo/abstract: mesma pergunta, mesmo escopo, mesmos números.
- Resumo e abstract: mesma evidência, sem tradução literal; cada um cabe numa página com as
  palavras-chave.
- Métodos no Cap. 5 descrevem o que os resultados usam; resultado sem protocolo é achado.
- Proibição de versionamento em `tex/` e `pre/` (perfil §4.1).

## Procedimento de auditoria de capítulo

1. Ler o capítulo inteiro e as seções que ele remete ou que o remetem (`grep -n "ref{<label>}"`).
2. Conferir a função do capítulo na tabela acima; conteúdo fora da função é achado
   (`consistency`).
3. Conferir as regras de continuidade contra o Cap. 1, o Cap. 8, o resumo e o abstract.
4. Conferir termos e siglas contra `scientific-writing-ptbr/references/terminologia.md`.
5. Força das afirmações: skill `scientific-argumentation`; números: `quantitative-audit`.

## Normas institucionais

Fatos verificados, fontes e datas: `skill://thesis-structure/references/normas-ppgcc-ufg.md`
(carregar para qualquer questão de formato, depósito, ABNT ou declaração de IA).

Hierarquia: resoluções do PPGCC > classe `inf-ufg` (template de fato do INF) > decisões
documentadas do projeto > ABNT > prática genérica. Nunca "corrigir para ABNT" o que a classe
ou o programa determinam de outro modo. `inf-ufg.cls` não é editado; ajustes vão em
`inf-ufg-tectonic.cls` ou em `main.tex`.
