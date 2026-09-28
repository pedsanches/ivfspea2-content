# Invariantes científicos deste repositório

Valem para toda sessão e todo subagente, em qualquer tarefa.

1. Nunca inventar referência, DOI, autor, ano, citação literal, resultado, número, tamanho de
   amostra, teste ou valor-p. Sem fonte verificável: `[NÃO VERIFICADO]` e aviso ao autor.
2. Nunca alterar número, métrica, coorte, instância ou parâmetro sem apontar a fonte (artefato,
   gerador ou código executado).
3. Nunca fortalecer afirmação em silêncio: associação não é causalidade; resultado nesta suíte
   não é generalidade; melhor métrica não é superioridade geral; `p > 0,05` não é equivalência;
   ausência de evidência não é evidência de ausência.
4. Separar observação, interpretação e hipótese. Não remover nem esconder limitação sem decisão
   do autor.
5. A existência de uma referência não prova que ela sustenta a afirmação; conferir as duas coisas.
6. Não editar dados brutos nem artefatos congelados (`data/raw/`, `artifact/`). Tabelas e
   figuras geradas mudam só pelo gerador (`src/python/thesis/`, `make thesis-tables`).
7. Preservar terminologia canônica, `\label`, `\ref`, chaves `\cite` e comandos LaTeX.
8. Toda alteração de texto precisa ser revisável por diff. Não sobrescrever, reverter nem
   descartar alterações preexistentes do autor.
9. Um modelo de linguagem não é fonte científica. O autor humano responde pelo texto; uso
   material de IA na dissertação é registrado em `thesis/masters/AI_ASSISTANCE_LOG.md`.
10. Não enviar trechos do manuscrito a serviços externos além dos modelos configurados;
    consultas externas levam só metadados bibliográficos.
