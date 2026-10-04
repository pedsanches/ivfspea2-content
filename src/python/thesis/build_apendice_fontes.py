#!/usr/bin/env python3
"""Reproducibility appendix, generated from the evidence manifest.

Discharges `REVISION_PLAN.md` §5: every claim family traceable to a dataset, a
producing script, a cohort, a run range and a multiplicity correction.

Rendered as itemised blocks rather than a table: the manifest fields are long
prose (cohort descriptions, overlap statements, known gaps) and would be
unreadable in a tabular. Uses only `enumitem`, which the class already loads.

Version identifiers in the manifest are internal positioning and are mapped to
coupling-based prose on the way out, per REWRITE_SPEC.md §1.2. Class names are
allowed here — this is the one place the dissertation names implementations.

Writes: results/thesis/apendice_fontes.tex
"""

from __future__ import annotations

import sys
import tomllib

from ivfspea2.paths import PROJECT_ROOT, RESULTS_THESIS, THESIS

import latex_table as lt

MANIFEST = THESIS / "data-sources.toml"
OUT = RESULTS_THESIS / "apendice_fontes.tex"

# Manifest `algorithm_version` -> prose. Never a version number in the output.
ALGORITHM_LABEL = {
    "IVFSPEA2 v1": "formulação anterior do operador (registro histórico)",
    "IVFSPEA2V2 / C26": "\\texttt{IVFSPEA2V2}, configuração C26",
    "IVFSPEA2V2 variants": "\\texttt{IVFSPEA2V2} e suas variantes de ablação",
    "IVFSPEA2V2 and warmup controller": "\\texttt{IVFSPEA2V2} e o controlador de aquecimento",
    "IVFSPEA2V2 trajectory subset": "\\texttt{IVFSPEA2V2}, subconjunto de trajetórias",
    "Published IVF/SPEA2, IVF/NSGA-II, and IVF/NSGA-III host pipelines":
        "pipelines publicados IVF/SPEA2, IVF/NSGA-II e IVF/NSGA-III",
}

ROLE_LABEL = {
    "primary": "principal",
    "supportive": "de apoio",
    "external-support": "de apoio externo",
    "diagnostic": "diagnóstica",
    "comparative": "comparativa",
    "historical": "histórica",
}

FAMILY_LABEL = {
    "ivfspea2-v1-history": "registro histórico da formulação anterior",
    "ivfspea2-v2-validation": "validação do IVF/SPEA2",
    "keep-drop-decision": "decisão de ativação do operador",
    "operator-host-compatibility": "compatibilidade operador--hospedeiro",
}

# Sources that do not feed the rewritten text; listed for completeness with an
# explicit statement of why.
NOT_IN_TEXT = {"legacy-v1-dissertation"}

# Portuguese presentation for each declared source. The manifest is an internal
# record written in English; printing its prose verbatim would put English into
# a Portuguese dissertation, and its ids carry version labels the text must not
# use. Every declared source must appear here — the builder fails otherwise, so
# a new source cannot silently reach the appendix untranslated.
SOURCE_PT = {
    "legacy-v1-dissertation": {
        "titulo": "Registro histórico da formulação anterior",
        "coorte": "Coorte do manuscrito de 2025; os identificadores de execução estão misturados e exigiriam reconciliação antes de qualquer reúso.",
        "bruto": "O protocolo isolado usa as execuções 2001--2100, faixa que não está presente na base consolidada atual.",
        "lacunas": "As afirmações do manuscrito histórico precisariam ser reconciliadas contra esse protocolo antes de serem reutilizadas.",
    },
    "memetic-computing-v2-confirmatory": {
        "titulo": "Avaliação comparativa principal: IVF/SPEA2 contra SPEA2",
        "coorte": "51 instâncias sintéticas; IVF/SPEA2 nas execuções 3001--3060 contra SPEA2 nas execuções 1--60; orçamento fixo de 100.000 avaliações.",
        "bruto": "As saídas brutas da plataforma não são versionadas e não constam de nenhuma das três versões publicadas do registro no Zenodo; a sua recuperação a partir de outra fonte não foi demonstrada. As análises desta família regeneram-se da base processada por execução, que é versionada.",
        "lacunas": "A base consolidada é mista e precisa sempre ser lida através do filtro de coorte.",
    },
    "memetic-computing-tuning-ablation": {
        "titulo": "Calibração de parâmetros e ablação fatorial",
        "coorte": "Coortes da calibração em três fases e da ablação fatorial, mantidas separadas da comparação principal.",
        "bruto": "Os artefatos processados estão congelados; a disponibilidade do bruto varia por fase.",
        "lacunas": "As instâncias de calibração pertencem à suíte de 51, mas são excluídas das contagens fora do ajuste.",
    },
    "memetic-computing-engineering": {
        "titulo": "Transferência para problemas de engenharia",
        "coorte": "RWMOP9, RWMOP21 e RWMOP8, com processamento estrito de execuções comuns.",
        "bruto": "As saídas brutas da plataforma não são versionadas nem constam das versões publicadas do registro no Zenodo, e a sua recuperação não foi demonstrada; as tabelas processadas por execução estão versionadas.",
        "lacunas": "O RWMOP8 tem cobertura heterogênea de execuções válidas e força probatória menor.",
    },
    "ppsn-clei-landscape-dynamics-controller": {
        "titulo": "Paisagem de aptidão, dinâmica inicial e controlador",
        "coorte": "Coorte de 60 execuções independentes para os rótulos, mais 30 execuções pareadas por semente para a dinâmica e o controlador.",
        "bruto": "Os arquivos brutos de dinâmica estão numa cópia local, fora do repositório e das versões publicadas do registro no Zenodo; o bruto do controlador está ausente, e o seu processado congelado está presente.",
        "lacunas": "Os rótulos derivados em IGD não constituem desfecho independente para o controlador, cujo desfecho primário declarado é o hipervolume.",
    },
    "ppsn-clei-partial-legacy-trajectories": {
        "titulo": "Trajetórias parciais (registro histórico)",
        "coorte": "Apenas cinco casos selecionados; não é a fonte da suíte completa de dinâmica.",
        "bruto": "Processado parcial disponível.",
        "lacunas": "Contém somente cinco casos e não substitui a fonte principal de dinâmica.",
    },
    "ppsn-operator-host-compatibility": {
        "titulo": "Compatibilidade entre o operador e o hospedeiro",
        "coorte": "51 instâncias sintéticas com 30 execuções por configuração; a situação de pareamento difere conforme o hospedeiro.",
        "bruto": "Os processados de desfecho estão presentes; as saídas brutas não são versionadas.",
        "lacunas": "A comparação avalia pipelines publicados e não isola causalmente a escolha do hospedeiro das diferenças de implementação e de configuração que a acompanham; só o IVF/SPEA2 tem calibração documentada nesta suíte, e os pipelines NSGA usam configurações fixas sem registro de ajuste equivalente.",
    },
    "thesis-derived-tables": {
        "titulo": "Tabelas desta dissertação",
        "coorte": "Não há execuções novas. Esta fonte apenas converte os artefatos congelados das demais famílias em tabelas, preservando a coorte e a correção de cada uma.",
        "bruto": "Não se aplica: todas as entradas são artefatos processados e versionados.",
        "lacunas": "Não há tabela para a família de convergência, cuja análise foi omitida da dissertação. A partição WFG/demais e a tabulação por propriedades da WFG são análises pós-hoc sobre a mesma amostra, não validações independentes.",
    },
    "context-comparator-positioning": {
        "titulo": "Posicionamento frente aos algoritmos comparados",
        "coorte": "Idêntica à da comparação principal: IVF/SPEA2 nas execuções 3001--3060 contra cada comparador nas execuções 1--60, 51 instâncias sintéticas, 60 execuções por algoritmo e instância, orçamento de 100.000 avaliações; sem linhas de RWMOP.",
        "bruto": "Não se aplica: a única entrada é o consolidado por execução, lido pelo filtro de coorte.",
        "lacunas": "O posicionamento é uma comparação, não afirmação de superioridade, e o posto médio é descritivo. A coluna do IVF/SPEA2 usa a configuração promovida pela calibração e os comparadores usam as configurações publicadas padrão. Reaproveitar a coorte da comparação principal significa que estas contagens não são replicação independente da família da QP1. Os arquivos pairwise_ivf_vs_all.csv e afins são proibidos como entrada: foram calculados sobre o rótulo misto do IVF/SPEA2 e sem correção de multiplicidade.",
    },
}


def _escape(text: str) -> str:
    """Escape the LaTeX specials that appear in manifest prose."""
    for old, new in (("\\", "\\textbackslash{}"), ("_", "\\_"), ("%", "\\%"),
                     ("&", "\\&"), ("#", "\\#"), ("$", "\\$")):
        text = text.replace(old, new)
    return text


def _breakable(path: str) -> str:
    r"""Escape a path and let TeX break it at separators.

    Repository paths are long and monospaced, and TeX will not hyphenate them,
    so a plain ``\texttt{}`` runs past the margin. Offering a break after each
    ``/`` and each escaped underscore keeps them inside the text block.
    """
    escaped = _escape(path)
    return escaped.replace("/", "/\\allowbreak{}").replace("\\_", "\\_\\allowbreak{}")


def _path_list(paths: list[str]) -> str:
    if not paths:
        return "---"
    return ", ".join(f"\\texttt{{{_breakable(p)}}}" for p in paths)


def _prose_list(items: list[str]) -> str:
    if not items:
        return "---"
    return " ".join(_escape(i) for i in items)


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERRO: manifesto ausente: {MANIFEST}", file=sys.stderr)
        return 1

    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = manifest.get("source", [])
    if not sources:
        print("ERRO: manifesto sem entradas [[source]]", file=sys.stderr)
        return 1

    lines = [
        f"% Gerado por {MANIFEST.name} via src/python/thesis/build_apendice_fontes.py",
        "% Regenerar com: make thesis-tables -- nao editar a mao.",
        "",
        "Cada família de evidência desta dissertação é declarada no manifesto "
        "\\texttt{thesis/masters/data-sources.toml}, que fixa o conjunto de dados, o "
        "script produtor, a coorte de execuções e as lacunas conhecidas de cada uma. "
        "As entradas abaixo são geradas diretamente desse manifesto, de modo que o "
        "apêndice não pode divergir do que o repositório declara.",
        "",
    ]

    for source in sources:
        source_id = source.get("id", "?")
        pt = SOURCE_PT.get(source_id)
        if pt is None:
            print(f"ERRO: fonte sem tradução em SOURCE_PT: {source_id}", file=sys.stderr)
            return 1
        lines.append(f"\\subsection*{{{_escape(pt['titulo'])}}}")
        # Ragged right: these items are mostly repository paths, which TeX
        # cannot hyphenate. The break points `_breakable` inserts carry no
        # stretchable glue, so a justified line still overflows; letting the
        # right margin float is what actually keeps them inside the block, and
        # is the conventional setting for a reference appendix.
        lines.append("\\begin{itemize}[nosep]\\raggedright")

        family = FAMILY_LABEL.get(source.get("evidence_family", ""), source.get("evidence_family", "---"))
        role = ROLE_LABEL.get(source.get("role", ""), source.get("role", "---"))
        algorithm = ALGORITHM_LABEL.get(
            source.get("algorithm_version", ""), _escape(source.get("algorithm_version", "---"))
        )

        lines.append(f"    \\item \\textbf{{Família:}} {family}.")
        lines.append(f"    \\item \\textbf{{Papel:}} {role}.")
        lines.append(f"    \\item \\textbf{{Implementação:}} {algorithm}.")
        lines.append(f"    \\item \\textbf{{Coorte:}} {_escape(pt['coorte'])}")
        lines.append(f"    \\item \\textbf{{Métricas:}} {', '.join(source.get('metrics', [])) or '---'}.")
        lines.append(f"    \\item \\textbf{{Dados:}} {_path_list(source.get('datasets', []))}")
        lines.append(f"    \\item \\textbf{{Scripts:}} {_path_list(source.get('scripts', []))}")
        lines.append(f"    \\item \\textbf{{Artefatos:}} {_path_list(source.get('artifacts', []))}")

        if source.get("raw_status"):
            lines.append(f"    \\item \\textbf{{Dados brutos:}} {_escape(pt['bruto'])}")
        if source.get("known_gaps"):
            lines.append(f"    \\item \\textbf{{Lacunas conhecidas:}} {_escape(pt['lacunas'])}")
        if source_id in NOT_IN_TEXT:
            lines.append(
                "    \\item \\textbf{Uso nesta dissertação:} nenhum. A coorte "
                "correspondente não está presente no repositório e nenhuma afirmação do "
                "texto se apoia nela."
            )

        lines.append("\\end{itemize}")
        lines.append("")

    content = "\n".join(lines)
    lt.write(OUT, content)
    print(f"  {len(sources)} fontes declaradas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
