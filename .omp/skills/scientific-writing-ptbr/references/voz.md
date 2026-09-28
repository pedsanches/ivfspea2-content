# Perfil de voz da dissertação

Referência para reescrever prosa da dissertação sem convertê-la em prosa acadêmica genérica.
Não é modelo para imitar frase a frase: descreve o registro que o autor aprovou e os vícios
que não devem voltar.

Os exemplos citam o texto de 2026-09-24 para ilustrar o registro; não são fonte de números.

## Proveniência — o que este perfil pode e não pode afirmar

Nenhum corpus do repositório é, com certeza, escrita exclusiva do autor. O perfil foi construído
separando três fontes:

| Corpus | Onde | Autoria | Uso aqui |
|---|---|---|---|
| A. Texto de 2025 | `git show 39ddf27:thesis/masters/tex/cap_*.tex` (9 capítulos, ~9,4 mil palavras) | Autor; vários trechos parecem tradução do artigo em inglês. Uso de IA na época não é registrado. | Hábitos estruturais do autor. Vícios a não repetir. |
| B. Texto atual (R1–R12) | `thesis/masters/tex/` (~17,9 mil palavras) | Redigido com IA (Claude, conforme `AI_ASSISTANCE_LOG.md`) sob decisões do autor e por ele aceito. | Registro-alvo aprovado. **Não** é evidência da voz do autor. |
| C. Decisões documentadas | `SCIENTIFIC_WRITING_PROFILE.md` §3–§4.1, `REWRITE_SPEC.md` §1.1, `REVISION_PLAN.md` §2 e §4 | Autor. | Evidência mais forte das preferências do autor. |

Medidas de 2026-09-24 (script descartável sobre o texto sem comandos LaTeX, parágrafos com 25+
palavras):

| Medida | A (2025) | B (atual) |
|---|---|---|
| Palavras por frase, mediana (média) | 27 (30,1) | 24 (26,3) |
| Frases com até 15 palavras | 5% | 28% |
| Frases com mais de 40 palavras | 15% | 15% |
| Palavras por parágrafo, mediana | 63 | 70 |
| Travessões (`---`) por mil palavras | 0,0 | 4,9 |
| "não é / não apenas / não se trata" por mil palavras | 0,2 | 2,0 |
| Adjetivos avaliativos (superior, significativo, promissor, abrangente, robusto) por mil palavras | 10,0 | 0,1 |
| Primeira pessoa do plural | quase nula | nula |

## Registro a preservar

1. **Impessoal com agente explícito.** "O IVF/SPEA2 seleciona", "A análise compara", "A
   dissertação investiga". O texto não usa "nós"; não introduzir primeira pessoa sem decisão do
   autor (o perfil a permite, mas pede consistência).
2. **Número com escopo.** Todo resultado traz contagem, métrica, família e recorte: "nas 37
   vitórias corrigidas em IGD, o valor mediano é $0{,}804$". Nunca "melhora significativa" sem o
   número e o teste.
3. **Medida definida pela pergunta que responde.** "o $A_{12}$ orientado estima com que
   frequência…; a diferença relativa entre as medianas estima quanto o resultado típico se
   desloca." Definir antes de interpretar.
4. **Frases curtas para o fato, longas só para a relação.** O fato medido vem numa frase
   curta ("As derrotas têm o perfil oposto. São quatro, …"); a frase longa carrega uma relação
   lógica explícita (causa, contraste, condição).
5. **Definição formal seguida de leitura.** Hábito do autor já no texto de 2025: equação, depois
   o que cada símbolo significa e por que importa.
6. **Enumeração quando a estrutura é enumerável.** Objetivos, contribuições e QPs em lista;
   argumento em prosa.
7. **Remissão em vez de repetição.** Cada QP é respondida só no Cap. 8 (`REVISION_PLAN.md` §2);
   ressalvas têm lugar canônico e os outros capítulos remetem a ele.
8. **Divergência declarada no ponto em que ocorre.** Quando o artefato contradiz um manuscrito,
   o texto segue o artefato e diz isso ali, com o identificador (`OQ-*` fica fora do texto).

## Vícios a não reproduzir

Do corpus A (2025):

- adjetivo avaliativo sem operação: "desempenho superior", "abordagem promissora", "avaliação
  abrangente", "estrutura robusta";
- decalque do inglês: "abordar desafios", "Algoritmo Evolutivo de Pareto de Força";
- abertura por fórmula: "Neste contexto, …";
- prioridade não verificada: "pela primeira vez", "inédito", sem busca documentada.

Do corpus B (atual), padrões aceitos mas frequentes demais — tratar como sinal, não proibição:

- **travessão como parêntese** (4,9 por mil palavras). Preferir vírgula, parênteses ou nova
  frase; manter quando isola uma enumeração interna ("três estágios --- coleta, manipulação e
  transferência ---").
- **negação-correção** ("não é X, mas Y"; "A lacuna não é apenas de cobertura."). Manter só
  quando X é uma leitura que o próprio texto ou a literatura sustentaram e que agora se corrige.
  Caso contrário, afirmar Y diretamente.
- **fecho aforístico** ao fim de parágrafo ("O acoplamento vence o hospedeiro com regularidade,
  por margem estreita."). Um por seção pode resumir; em série vira cadência de LLM.

## Convenções formais do texto

- Vírgula decimal; em modo matemático, `{,}` (`$0{,}12$`). Milhar com ponto na prosa
  ("100.000 avaliações"). Números de tabela vêm de `src/python/thesis/ptbr_format.py`.
- Parâmetros em minúscula no texto ($c$, $r$, $\ell$, $m$, $v$): `M` é o número de objetivos.
- `IVFSPEA2V2` em fonte monoespaçada só no apêndice de reprodutibilidade.
- `Capítulo~\ref{…}`, `Seção~\ref{…}`, `Tabela~\ref{…}` com espaço inseparável.
