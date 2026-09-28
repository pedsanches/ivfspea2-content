# Terminologia

Fonte canônica: `thesis/masters/SCIENTIFIC_WRITING_PROFILE.md` §4 (vocabulário) e §4.1
(proibição de versionamento). Esta tabela **completa** aquela com o uso efetivo do texto em
2026-09-24 (contagens em `tex/*.tex`); não a substitui. Em conflito, vale o perfil.

## Regra de decisão para termo novo

1. Existe forma portuguesa usada na literatura brasileira da área que preserva o referente?
   Usar a forma portuguesa.
2. A tradução cria ambiguidade ou é incomum na área? Manter o termo inglês em itálico, definir
   na primeira ocorrência e não alternar depois.
3. Registrar a decisão aqui (com a data) antes de usar o termo em mais de um capítulo.

Não trocar termo técnico por sinônimo para evitar repetição. Não "corrigir" para purismo uma forma
já consolidada no texto sem decisão do autor.

## Formas em uso

| Conceito (inglês) | Forma no texto | Uso | Observação |
|---|---|---|---|
| fitness | aptidão | 57 | *fitness* só em rótulos LaTeX. |
| fitness landscape / landscape analysis | paisagem de aptidão; análise de paisagem (FLA) | 22 | Sigla FLA definida uma vez. |
| host (algorithm) | hospedeiro | 128 | — |
| coupling | acoplamento | 80 | Distingue formulações; nunca "versão" (§4.1). |
| run | execução | 107 | "execuções `3001–3060`" identifica coorte. |
| seed | semente | 7 | — |
| benchmark suite | suíte (de problemas de teste) | 60 | *benchmark* só quando necessário (perfil §4). |
| tuning | calibração (as três fases); ajuste | 40 / 11 | "fora do ajuste" = as 39 instâncias não usadas na calibração. |
| turnover (dinâmica) | renovação | 25 | *turnover* só em rótulo de figura. |
| exploration / exploitation | exploração e intensificação | — | Correspondência declarada em itálico no Cap. 2. |
| IGD | distância geracional invertida (IGD) | — | Desfecho primário; menor é melhor. |
| HV | hipervolume (HV) | 7 | Desfecho secundário obrigatório; maior é melhor. |
| Vargha–Delaney A12 | estatística $A_{12}$ de Vargha e Delaney; "$A_{12}$ orientado" | 29 (texto + tabelas) | Mesma notação $A_{12}$ em prosa e tabelas geradas. |
| baseline | comparador principal (SPEA2); comparadores de contexto | — | "linha de base" não é usado. |
| leave-one-family-out validation | validação deixa-uma-família; "fora da família de treino" | — | Leitura da dissertação difere da do CLEI (`OQ-16`). |
| many-objective | *many-objective* (itálico) | 2 | Sem tradução consolidada. |
| preprint | *preprint* (itálico) | 1 | — |
| pipeline | pipeline (sem itálico) | 11 | **Pendente de decisão do autor**: estrangeirismo sem itálico nem definição; não alterar sem decisão. |

## Nomes próprios e rótulos

- IVF/SPEA2, IVF/NSGA-II, IVF/NSGA-III, IVF/GDE3 com barra; SPEA2, NSGA-II, NSGA-III, MOEA/D.
- Suítes: ZDT, DTLZ, WFG, MaF, RWMOP.
- Plataforma: PlatEMO. Classe da implementação: `IVFSPEA2V2`, só no apêndice (perfil §4).
- QP1–QP4 para as questões de pesquisa; C26 para a configuração promovida.

## Artigos em inglês

Os artigos (`paper/*`) usam os termos ingleses equivalentes (fitness, host, coupling, run,
turnover, benchmark). A disciplina de evidência é a mesma; a tabela acima vale só para a
dissertação.
