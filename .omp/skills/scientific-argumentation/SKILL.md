---
name: scientific-argumentation
description: Avaliar ou calibrar a relação afirmação→evidência em texto científico do projeto — escopo, força (observado, comparação, suporte, sugestão, causalidade), overclaiming, estatística, explicações concorrentes, limitações e coerência entre métodos e resultados. Use em revisão adversarial e ao redigir resultados, discussão e conclusões.
---

# Argumentação científica

## Escala de força

Toda afirmação ocupa um degrau. Subir de degrau exige a evidência do degrau.

| Degrau | Forma típica | Exige |
|---|---|---|
| OBSERVADO | "o IVF/SPEA2 obteve IGD mediana ⟨valor⟩ em ⟨instância⟩ (M = ⟨m⟩)" | Valor rastreável ao artefato. |
| COMPARAÇÃO | "…menor que a do SPEA2 em ⟨k⟩ das ⟨n⟩ instâncias com M = ⟨m⟩, pelo teste de Mann–Whitney com correção de Holm" | Comparador, métrica e direção, instâncias, execuções, orçamento, teste, família de correção. |
| SUPORTE | "os resultados sustentam a hipótese de que…" | Hipótese declarada antes e desenho que poderia refutá-la. |
| SUGESTÃO | "o padrão sugere / é consistente com…" | Explicação plausível nomeada como interpretação; alternativas consideradas. |
| CAUSALIDADE | "X causa Y", "o ganho decorre de…" | Manipulação controlada que isola X (ablação pareada, controle). Sem isso, não usar. |

Conversões proibidas sem nova evidência:

- correlação → causalidade;
- resultado nesta suíte/coorte → generalidade ("em problemas multiobjetivo");
- melhor métrica numa família → superioridade geral (NFL; Wolpert & Macready, 1997);
- resultado de benchmark → mecanismo ("porque a seleção de pai dissimilar preserva diversidade");
- `p > 0,05` → equivalência ou "não afeta" (exige teste de equivalência com margem; Lakens);
- ausência de evidência → evidência de ausência;
- evidência de apoio (engenharia, multibaseline, ablação, FLA) → prova principal
  (`SCIENTIFIC_WRITING_PROFILE.md` §7);
- manuscritos que reutilizam as mesmas execuções → replicações independentes (perfil §6).

## Fontes do projeto que delimitam afirmações

- `docs/IVFSPEA2_EVIDENCE_MODEL.md` — hierarquia e *wording guardrails*.
- `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md` §6–§8 — famílias, hierarquia inferencial,
  protocolo confirmatório (Mann–Whitney bicaudal, α = 0,05, Holm por M e métrica).
- `thesis/masters/REWRITE_SPEC.md` §3.5 (afirmações bloqueadas), §4 (questões abertas `OQ-*`),
  §5 (sobreposição e não independência).
- `thesis/masters/REVISION_PLAN.md` §2 — o que cada QP pode responder; cada QP é respondida só
  no Cap. 8.

## Procedimento de revisão

Para cada parágrafo com afirmação material:

1. Transcrever a afirmação exata e classificá-la na escala.
2. Localizar a evidência que o texto oferece ou deveria oferecer (tabela, figura, seção,
   artefato). Não aceitar a própria prosa como evidência.
3. Conferir o escopo: suíte, M, coorte (execuções `3001–3060` × `1–60`), métrica e direção,
   recorte fora do ajuste (39 instâncias; MaF7 com M = 3 repete o DTLZ7 da calibração).
4. Conferir a estatística: teste adequado ao pareamento, família de correção declarada,
   tamanho de efeito junto do p-valor, contagem corrigida × não corrigida.
5. Perguntar pela explicação concorrente (configuração × decisões de acoplamento; recálculo de
   aptidão antes do torneio, `OQ-24`; identidade de suíte × sinal de renovação, `OQ-19`).
6. Conferir a limitação: está declarada no lugar canônico e remetida, sem ser apagada nem
   repetida em cada capítulo?
7. Conferir coerência métodos ↔ resultados ↔ conclusões (mesmos números, mesmo protocolo).

Checklist de benchmarking e ML/FLA com fontes:
`skill://scientific-argumentation/references/checklist-emo.md` (carregar em revisão de
métodos, resultados ou discussão).

## Achados

Um achado aponta: a afirmação exata (citação literal), o local (`arquivo:linha`), o degrau
atual e o degrau que a evidência sustenta, a evidência conferida, o problema e a ação mínima
(reformulação mais fraca, ressalva, remissão, citação, ou decisão do autor). Achado sem
evidência conferida é suspeita: `confidence: baixa`.

`confidence` é indicação operacional, não probabilidade:

- `alta` — conferido por leitura direta do artefato ou cálculo;
- `media` — indício forte, conferência parcial;
- `baixa` — suspeita que precisa de verificação.
