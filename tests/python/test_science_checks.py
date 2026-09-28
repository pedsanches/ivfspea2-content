"""Deterministic checks of the scientific-writing environment (scripts/science/).

These scripts guard the manuscript against silent changes: a missed undefined
citation, a number swapped during an edit, or an invented DOI would reach the
defense unnoticed if their parsing drifted. No network access here; the online
paths of bib_check.py are exercised by the environment test suite.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "science"


def load(name: str):
    spec = importlib.util.spec_from_file_location(f"science_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


latex_check = load("latex_check")
bib_check = load("bib_check")
claims = load("claims")
prose_audit = load("prose_audit")


# --- latex_check -----------------------------------------------------------------

CITED_KEY = "zitzler2001spea2improvingstrength"
MESSAGE = f"LaTeX Warning: Citation `{CITED_KEY}' on page 12 undefined on input line 34."
# TeX hard-wraps log lines at 79 characters; with this key the break falls inside
# "undefined", so the warning is only recognizable after unwrapping.
WRAPPED_CITATION = MESSAGE[:79] + "\n" + MESSAGE[79:] + "\n"


def build_files(tmp_path: Path, log: str, cited: list[str], bib_keys: list[str]) -> list[str]:
    (tmp_path / "main.log").write_text(log, encoding="utf-8")
    (tmp_path / "main.blg").write_text("This is BibTeX, Version 0.99d\n", encoding="utf-8")
    aux = "".join(f"\\citation{{{key}}}\n" for key in cited)
    (tmp_path / "main.aux").write_text(aux, encoding="utf-8")
    bib = "".join(f"@misc{{{key}, title={{T}}}}\n" for key in bib_keys)
    (tmp_path / "refs.bib").write_text(bib, encoding="utf-8")
    return [
        "--log",
        str(tmp_path / "main.log"),
        "--blg",
        str(tmp_path / "main.blg"),
        "--aux",
        str(tmp_path / "main.aux"),
        "--bib",
        str(tmp_path / "refs.bib"),
        "--baseline",
        str(tmp_path / "baseline.json"),
    ]


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / f"{name}.py"), *args], capture_output=True, text=True
    )


def test_wrapped_warning_is_read_as_one_message(tmp_path: Path) -> None:
    log = tmp_path / "main.log"
    log.write_text(WRAPPED_CITATION, encoding="utf-8")
    items = latex_check.parse_log(log)
    assert "undefined" not in WRAPPED_CITATION.splitlines()[0]
    assert [(i.category, i.key) for i in items] == [("undefined_citation", CITED_KEY)]


def test_box_warnings_are_attributed_to_the_file_tex_had_open(tmp_path: Path) -> None:
    log = tmp_path / "main.log"
    log.write_text(
        "(./tex/cap_IX [80]\n] [82]) [83] (main.bbl\n"
        "Underfull \\hbox (badness 1769) in paragraph at lines 222--227\n"
        "(generated/apendice_fontes\n"
        "Overfull \\hbox (3.2pt too wide) in paragraph at lines 4--5\n",
        encoding="utf-8",
    )
    keys = [(i.category, i.key) for i in latex_check.parse_log(log)]
    assert keys == [("underfull", "main.bbl:222"), ("overfull", "generated/apendice_fontes:4")]


def test_compare_fails_only_on_blocking_items_absent_from_baseline(tmp_path: Path) -> None:
    old_log = "LaTeX Warning: Reference `sec:x' on page 3 undefined on input line 9.\n"
    args = build_files(tmp_path, old_log, ["a"], ["a"])
    assert run_script("latex_check", *args, "--save-baseline").returncode == 0

    same = run_script("latex_check", *args, "--compare")
    assert same.returncode == 0, same.stdout
    assert "[preexistente] BLOQUEANTE undefined_reference sec:x" in same.stdout

    new_log = old_log + "Underfull \\hbox (badness 10000) in paragraph at lines 3--3\n"
    args = build_files(tmp_path, new_log, ["a", "ghost"], ["a"])
    worse = run_script("latex_check", *args, "--compare")
    assert worse.returncode == 1
    assert "[novo] BLOQUEANTE cited_not_in_bib ghost" in worse.stdout
    assert "[novo] aviso underfull" in worse.stdout


# --- bib_check -------------------------------------------------------------------

BIB = r"""
@string{tec = "IEEE TEC"}
@article{deb2002fast,
  author = {Deb, K. and Pratap, A.},
  title = {A Fast and Elitist {Multiobjective} Genetic Algorithm: {NSGA-II}},
  journal = tec # " 6",
  year = 2002,
  doi = {https://doi.org/10.1109/4235.996017}
}
@inproceedings{nobook,
  author = "Silva, Ana",
  title = "Sem booktitle",
  year = {2020}
}
@misc{deb2002fast, title = {duplicada}}
"""


def test_bib_parser_reads_nested_braces_quotes_and_concatenation() -> None:
    entries = bib_check.parse_bib(BIB)
    first = entries[0]
    assert first.key == "deb2002fast"
    assert first.fields["title"].startswith("A Fast and Elitist {Multiobjective}")
    assert first.fields["journal"] == "tec 6"
    assert first.fields["year"] == "2002"
    assert entries[1].fields["author"] == "Silva, Ana"


def test_offline_checks_flag_duplicates_missing_fields_and_citation_gaps() -> None:
    entries = bib_check.parse_bib(BIB)
    results = bib_check.offline_checks(entries, cited={"deb2002fast", "ghost"})
    assert results["deb2002fast"].doi == "10.1109/4235.996017"
    assert any("duplicada" in issue for issue in results["deb2002fast"].issues)
    assert "campo obrigatório ausente: booktitle" in results["nobook"].issues
    assert results["nobook"].status == "warn"
    assert results["ghost"].status == "missing"


def test_retraction_outranks_matching_metadata() -> None:
    entry = bib_check.parse_bib(BIB)[0]
    result = bib_check.Result(entry.key, entry.kind, "ok", doi="10.1109/4235.996017")
    summary = {
        "title": "A fast and elitist multiobjective genetic algorithm: NSGA-II",
        "year": 2002,
        "first_author": "deb",
        "authors": ["deb", "pratap", "agarwal", "meyarivan"],
        "container": "IEEE TEC",
        "type": "journal-article",
        "updated_by": [{"type": "retraction", "source": "retraction-watch", "doi": "x"}],
    }
    bib_check.compare(entry, result, summary)
    assert result.status == "retracted"
    assert result.issues == []


def test_metadata_divergence_is_a_mismatch() -> None:
    entry = bib_check.parse_bib(BIB)[0]
    result = bib_check.Result(entry.key, entry.kind, "ok", doi="10.1109/4235.996017")
    summary = {
        "title": "Something else entirely",
        "year": 2003,
        "first_author": "zitzler",
        "authors": ["zitzler"],
        "container": "",
        "type": "journal-article",
        "updated_by": [],
    }
    bib_check.compare(entry, result, summary)
    assert result.status == "mismatch"
    joined = " | ".join(result.issues)
    for fragment in ("título diverge", "ano 2002 no .bib, 2003", "primeiro autor 'deb'"):
        assert fragment in joined


def test_chimeric_author_list_is_a_mismatch() -> None:
    """Right DOI and first author, wrong co-author: the pattern of a stitched reference."""
    entry = bib_check.parse_bib(BIB)[0]
    entry.fields["author"] = "Deb, K. and Zitzler, E."
    result = bib_check.Result(entry.key, entry.kind, "ok", doi="10.1109/4235.996017")
    summary = {
        "title": "A fast and elitist multiobjective genetic algorithm: NSGA-II",
        "year": 2002,
        "first_author": "deb",
        "authors": ["deb", "pratap", "agarwal", "meyarivan"],
        "container": "IEEE TEC",
        "type": "journal-article",
        "updated_by": [],
    }
    bib_check.compare(entry, result, summary)
    assert result.status == "mismatch"
    assert result.issues == ["autores do .bib ausentes no registro: ['zitzler']"]


# --- claims ----------------------------------------------------------------------


def test_numbers_are_read_as_the_reader_sees_them() -> None:
    line = (
        r"Nas 37 vitórias, $A_{12}$ mediano de $0{,}804$ e piora de $6{,}41\%$ "
        r"(execuções 3001--3060; 22/3/3; São quatro) \label{sec:9} \ref{tab:2}"
        r"~\cite{deb2002fast}"
    )
    assert claims.numbers_in(line) == ["37", "0,804", "6,41%", "3001–3060", "22/3/3", "quatro"]


def test_inventory_skips_comments_and_keeps_line_numbers(tmp_path: Path) -> None:
    tex = tmp_path / "cap.tex"
    tex.write_text(
        "% 99 comentário\nTexto sem número.\nObteve 12 vitórias~\\cite{a,b}.\n",
        encoding="utf-8",
    )
    found = claims.sentences(tex)
    assert [(s.line, s.numbers, s.cites) for s in found] == [(3, ["12"], ["a", "b"])]


def test_guard_reports_number_citation_and_strength_changes() -> None:
    before = r"Os resultados sugerem 22 vitórias~\cite{a}."
    after = r"Os resultados comprovam 24 vitórias~\cite{b}."
    old, new = claims.tokens(before), claims.tokens(after)
    guard = {kind: claims.delta(old[kind], new[kind]) for kind in old}
    assert guard["numbers"] == {"added": ["24"], "removed": ["22"]}
    assert guard["cites"] == {"added": ["b"], "removed": ["a"]}
    assert guard["strength"] == {"added": ["+comprova"], "removed": ["~sugere"]}


def test_diff_strict_exits_3_only_when_claim_tokens_change(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    tex = tmp_path / "sec.tex"
    tex.write_text("Obteve 22 vitórias em IGD.\n", encoding="utf-8")

    def run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "claims.py"), *args],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

    assert run("snapshot", "sec.tex").returncode == 0
    tex.write_text("Obteve 22 vitórias na IGD.\n", encoding="utf-8")
    assert run("diff", "--strict", "sec.tex").returncode == 0
    tex.write_text("Obteve 23 vitórias na IGD.\n", encoding="utf-8")
    changed = run("diff", "--strict", "--json", "sec.tex")
    assert changed.returncode == 3
    assert json.loads(changed.stdout)[0]["guard"]["numbers"]["added"] == ["23"]


# --- prose_audit -----------------------------------------------------------------


def audit(tmp_path: Path, text: str, **kwargs) -> list[tuple[str, str]]:
    tex = tmp_path / "t.tex"
    tex.write_text(text, encoding="utf-8")
    findings = prose_audit.audit_file(
        tex, max_sentence_words=55, repeated_opener_threshold=3, **kwargs
    )
    return [(f.severity, f.rule) for f in findings]


@pytest.mark.parametrize(
    ("text", "flagged"),
    [
        ("para todo $j$ vale a relação.\n", False),
        ("TODO: conferir o valor.\n", True),
        ("Valor [NÃO VERIFICADO: fonte] aqui.\n", True),
    ],
)
def test_placeholder_is_case_sensitive_for_todo(tmp_path: Path, text: str, flagged: bool) -> None:
    assert (("high", "placeholder") in audit(tmp_path, text)) is flagged


def test_latex_accents_are_resolved_for_author_comparison() -> None:
    assert bib_check.plain("Koro\\v{s}ec, Peter") == "korosec peter"
    entry = bib_check.Entry(
        "k",
        "article",
        {
            "author": "Koro\\v{s}ec, Peter",
            "title": "Adaptive Estimation of the Number of Algorithm Runs "
            "in Stochastic Optimization",
        },
        1,
    )
    result = bib_check.Result("k", "article", "ok")
    bib_check.compare(
        entry,
        result,
        {
            "title": "Adaptive Estimation of the Number of Algorithm Runs "
            "in Stochastic Optimization",
            "year": 2025,
            "authors": ["Korošec"],
            "updated_by": [],
        },
    )
    assert result.issues == []


def test_negation_correction_targets_copular_contrast_only(tmp_path: Path) -> None:
    assert ("advisory", "negation-correction") in audit(
        tmp_path, "Comparar em 51 instâncias não é uma decisão, mas 51 decisões.\n"
    )
    assert ("advisory", "negation-correction") not in audit(
        tmp_path, "O dado bruto não está disponível, mas o processado está.\n"
    )


def test_dash_density_threshold(tmp_path: Path) -> None:
    words = " ".join(["palavra"] * 300)
    dense = f"{words} --- aparte --- {words} --- outro --- fim.\n"
    assert ("advisory", "dash-density") in audit(tmp_path, dense, max_dashes_per_1k=3.0)
    assert ("advisory", "dash-density") not in audit(tmp_path, dense, max_dashes_per_1k=10.0)
