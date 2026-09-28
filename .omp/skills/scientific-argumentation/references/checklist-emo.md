# Checklist de revisão — benchmarking de MOEAs e ML/FLA

Fontes lidas em 2026-09-24 (ver `docs/ai-scientific-writing/research.md` §5). Cada item é uma
pergunta; "não" gera achado quando o texto afirma algo que depende dela.

## Desenho

1. O orçamento de avaliações é idêntico entre os algoritmos comparados, ou a exceção de política
   de população (NSGA-III, MOEA/D) está declarada? — Bartz-Beielstein et al. 2020.
2. O comparador canônico simples (SPEA2) está presente e é o alvo da afirmação confirmatória? —
   Bartz-Beielstein et al. 2020.
3. Instâncias usadas na calibração estão separadas das usadas para generalizar (12 × 39), e o
   texto não trata o recorte fora do ajuste como independente onde ele não é (MaF7/DTLZ7)? —
   Eiben & Smit 2011; Eggensperger, Hutter et al. (armadilha 6, *over-tuning*).
4. O número de execuções e de instâncias está declarado e o texto não o apresenta como garantia
   de potência que não foi calculada? — Campelo & Takahashi 2019.
5. Execuções reutilizadas entre famílias de evidência (Springer, Hosts, CLEI/PPSN) não são
   contadas como replicação independente? — López-Ibáñez, Branke, Paquete 2021; perfil §6.

## Métricas

6. IGD e HV aparecem juntos, com direção (menor/maior é melhor) e o aspecto que cada um mede? —
   Li & Yao 2019; Audet et al. 2021.
7. Ponto de referência do HV e conjunto de referência da IGD estão declarados e são comuns por
   problema? — Ishibuchi et al. 2018.
8. Para problemas sem fronteira analítica (RWMOP), o conjunto de referência empírico está
   descrito e congelado? — COCO bbob-biobj (Brockhoff, Tušar et al. 2016).
9. Comparação de HV entre problemas de escalas diferentes usa objetivos normalizados? — COCO.

## Estatística

10. O teste corresponde ao pareamento real: Mann–Whitney para coortes independentes
    (`3001–3060` × `1–60`); teste pareado só quando as execuções são pareadas por semente? —
    Derrac et al. 2011.
11. A família de correção está declarada antes da correção (por M e por métrica, no protocolo
    confirmatório), e Holm × Benjamini–Hochberg não são misturados sem justificativa? — Derrac
    et al. 2011; perfil §7.
12. Contagens "corrigidas" vêm de `results/tables/claims_summary_audit.csv`; contagens de
    geradores descritivos não são chamadas de confirmatórias? — perfil §7.
13. Todo p-valor usado como apoio vem com tamanho de efeito ($A_{12}$) e resumo descritivo? —
    Arcuri & Briand 2014.
14. Nenhuma afirmação de "equivalência", "empate real" ou "não afeta" se apoia só em
    `p > 0,05`? — Lakens 2017; Lakens, Scheel, Isager 2018.
15. Posto médio entre vários algoritmos não sustenta afirmação par a par (depende do conjunto
    de algoritmos)? — Benavoli, Corani, Mangili 2016.
16. Limiares de magnitude de $A_{12}$ são tratados como convenção aproximada, não corte exato?
    — Vargha & Delaney 2000 (via fonte secundária).

## Generalização

17. Nenhuma linguagem de superioridade geral, universal ou "em problemas multiobjetivo" sem
    escopo? — Wolpert & Macready 1997.
18. Toda afirmação comparativa carrega suíte, M, métrica e coorte? — Bartz-Beielstein et al.
    2020; `IVFSPEA2_EVIDENCE_MODEL.md`.
19. Evidência de apoio (engenharia, multibaseline, ablação, FLA, controlador) não é promovida a
    prova principal? — perfil §7.
20. Mecanismo de projeto aparece como hipótese, não como fato medido, quando o desenho não o
    isola (ablação na configuração não ajustada; recálculo de aptidão, `OQ-24`)? —
    `REVISION_PLAN.md` §2.

## Reprodutibilidade

21. Versões de plataforma, seeds e ambiente são afirmadas só quando o artefato as registra
    (`OQ-15`)? — López-Ibáñez et al. 2021; ACM Artifact Review and Badging.
22. O texto distingue repetibilidade, reprodutibilidade e replicabilidade ao descrever o que
    os artefatos permitem? — López-Ibáñez et al. 2021.
23. Tabelas e figuras vêm de geradores versionados (`src/python/thesis/`, `make
    thesis-tables-check`)? — política do projeto.

## ML/FLA e controlador

24. Instâncias da mesma família não aparecem em treino e teste do classificador; a validação
    deixa-uma-família é lida pelo que mede (a coincidência com a partição WFG/demais,
    `OQ-19`)? — Kapoor & Narayanan 2023 (vazamento); aplicação a FLA é `[INFERÊNCIA]`.
25. Métricas do classificador e do controlador vêm com incerteza entre dobras/sementes e com a
    unidade de análise declarada? — REFORMS 2024.
