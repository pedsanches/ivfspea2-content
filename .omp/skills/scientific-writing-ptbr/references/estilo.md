# Estilo científico em português brasileiro

Adaptado da skill do autor `write-scientific-manuscripts` (`portuguese-scientific-style.md`) e da
pesquisa registrada em `docs/ai-scientific-writing/research.md` §4. Normalização (ABNT,
tipografia) não é tratada aqui: ver `thesis-structure`.

Critério único: **uma palavra entra quando transmite informação.** Nenhuma expressão abaixo é
proibida; todas exigem uma função.

Números nos exemplos ilustram a forma; não são fonte. Todo número vem do artefato.

## 1. Sentido antes do polimento

Antes de mexer numa frase, identificar: sujeito e ação; proposição principal; evidência ou
fonte; relação com a frase anterior; ressalva necessária. Se algo disso não está claro, não
disfarçar com prosa lisa: manter o trecho e perguntar ao autor.

## 2. Frase

- **Posição (Gopen & Swan, 1990).** Sujeito perto do verbo. Início da frase retoma o que já foi
  dito; fim da frase traz a informação nova. Frase longa não é defeito; frase com mais candidatos
  a ênfase do que posições de ênfase é.
- **Uma proposição por frase quando o estatuto muda.** Separar dado medido de interpretação
  (Cervo, Bervian e Silva). Juntar frases curtas quando a fragmentação esconde a relação.
- **Verbo finito antes de nominalização.** Teste de Sword: a frase ainda diz quem fez o quê?
  "Foi realizada a execução da avaliação" → "O experimento avaliou". Nominalização que nomeia
  conceito do domínio (convergência, dominância, aptidão) é legítima.
- **Passiva em série apaga o agente** ("foi realizada", "foi conduzida", "foi efetuada"). Nomear
  o agente ou a operação quando isso esclarece responsabilidade.
- Condição perto do que ela limita. Paralelismo sintático entre itens comparáveis. Nada de
  vírgula entre sujeito e predicado.

## 3. Conectivos

Manter o conectivo só quando nomeia a relação real:

| Relação | Formas naturais |
|---|---|
| contraste | "No entanto", "Em contrapartida", "Embora…" |
| causa | "porque", "uma vez que" |
| consequência | "por isso", "logo", "o que resulta em…" |
| especificação | "isto é", "em particular" |
| progressão | nenhum: a ordem das frases basta |

Sinais de conectivo decorativo: "Neste/Nesse contexto", "Além disso", "Ademais", "Dessa forma",
"Nesse sentido", "Em suma", "Por fim" abrindo parágrafos seguidos; "É importante destacar que",
"Vale ressaltar que", "Cabe mencionar que". Correção: apagar a moldura e afirmar o conteúdo.
"É importante destacar que o método usa duas métricas" → "A avaliação usa duas métricas."

## 4. Avaliação e força

- Adjetivo avaliativo precisa de operação, comparação ou evidência: abrangente, adequado,
  avançado, considerável, eficaz, eficiente, inovador, notável, promissor, relevante, robusto,
  significativo, sofisticado, superior. "Uma avaliação abrangente e robusta" → "uma avaliação em
  51 instâncias, com 60 execuções por algoritmo e dois indicadores".
- "Significativo" nunca sem dizer qual sentido: estatístico (teste, família, correção),
  magnitude (efeito) ou importância prática.
- *Hedge* e *booster* por seção (Hyland): Métodos quase sem ressalva; Resultados com ressalva só
  onde o valor medido vira interpretação; Discussão com mais ressalvas. Não apagar ressalva para
  "fluir melhor" nem acrescentar ressalva que o autor não pôs sem apontar o motivo.
- Verbos de relação real: métodos (define, seleciona, calcula, compara, estima); resultados
  (apresenta, obtém, difere, aumenta); interpretação (indica, sugere, sustenta, é consistente
  com); limites (restringe, confunde, não permite concluir). Tabela "apresenta", figura
  "ilustra"; quem sustenta inferência é a análise, não o objeto.

## 5. Padrões de prosa genérica

Catálogo de padrões estruturais (Wikipedia, *Signs of AI writing*; Kobak et al. 2025). A lista em
PT-BR é convenção editorial por analogia `[INFERÊNCIA]`: não há estudo quantitativo equivalente
para o português. Nunca usar como detector de autoria.

| Padrão | Pergunta de revisão |
|---|---|
| Fecho de parágrafo sobre "importância"/"relevância" | O parágrafo termina numa afirmação que o próprio parágrafo sustenta? |
| Negação-correção ("não é X, mas Y") | Alguém de fato afirmou X? Se não, dizer Y. |
| Tríades ("clareza, precisão e rigor") | Os três itens foram todos verificados, ou o terceiro completa o ritmo? |
| Travessão como parêntese em série | Vírgula, parênteses ou nova frase não servem melhor? |
| Oração em "-ndo" de análise vaga no fim ("…, evidenciando a relevância do método") | Qual relação o gerúndio afirma, e quem a verificou? |
| Atribuição vaga ("a literatura aponta", "estudos mostram") | Qual referência, sobre qual resultado? |
| Parágrafos com a mesma cadência (4–5 frases do mesmo tamanho) | A estrutura segue o argumento ou um molde? |
| Introdução que serviria a qualquer dissertação de otimização | O que é específico desta pesquisa? |

## 6. Português brasileiro natural

- Traduzir a função, não a palavra. "Endereçar um problema" → "tratar/abordar"; "performar" →
  "executar"; "através de" para instrumento → "por meio de"; "onde" não espacial → "em que", "no
  qual".
- "Evidência" (massa) em geral é melhor que "evidências" contáveis; às vezes "indícios",
  "resultados", "base empírica".
- Estrangeirismo só quando o termo técnico não tem equivalente sem ambiguidade (USP/SIBiUSP
  §2.1); então itálico e definição na primeira ocorrência. Ver `terminologia.md`.
- Sigla definida na primeira ocorrência de cada texto autônomo (resumo, abstract, capítulo de
  abertura), não redefinida a cada capítulo.
- Concordância com porcentagens e sujeitos pospostos; regência e crase; antecedente de
  pronomes e demonstrativos ("isso", "esse resultado", "tal abordagem") sempre recuperável.

## 7. Parágrafo e coesão

- Um propósito argumentativo por parágrafo; a primeira frase anuncia esse propósito.
- Repetição lexical preserva o referente técnico; sinônimo "elegante" cria falsa distinção.
- Consecutivos não abrem com o mesmo conectivo ou demonstrativo.
- Tamanho segue a função; nada de simetria forçada.

## 8. Sequência de revisão

1. Restaurar afirmação exata e escopo.
2. Consertar lógica do parágrafo e referentes.
3. Trocar avaliação vaga por evidência.
4. Cortar fórmulas vazias e redundância.
5. Simplificar a sintaxe sem apagar ressalva necessária.
6. Gramática, pontuação, ortografia, tipografia.
7. Ler devagar procurando ambiguidade.
8. Comparar com o original: o significado científico mudou? Se sim, desfazer ou registrar.

Se um parágrafo pudesse ser colado numa dissertação qualquer, está genérico demais.
