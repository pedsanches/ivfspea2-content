"""LaTeX table emission for the dissertation.

Every generated table goes through ``render``, so the house style lives here
and nowhere else:

* **Rules.** booktabs only (``\\toprule``, ``\\midrule``, ``\\cmidrule``,
  ``\\bottomrule``) and no vertical rule: the table is open at the sides, as in
  the IBGE tabular norm that ABNT adopts. A ``|`` in a colspec is an error.
* **Type size.** The body is ``\\small`` and the note ``\\footnotesize`` in
  every table. Nothing is scaled: the ``\\resizebox`` this module used to emit
  gave each wide table a type size of its own, from about 7 to 13 points.
* **Width.** Every table spans ``\\textwidth`` with flush outer edges, and its
  note spans the same width, so table, note and text share both margins. A
  colspec with a flexible column (``X``, or the ragged-right ``L`` that
  ``main.tex`` defines) is set with ``tabularx``; any other with ``tabular*``,
  which spreads the free width evenly between the columns.
* **Headers.** Header cells are bold. A header may have several rows; a
  :class:`Span` with text that covers several columns gets a ``\\cmidrule``
  under it, which shows the reader which columns it groups.

``main.tex`` loads ``booktabs`` and ``tabularx`` and defines ``L``. The two
tables typed into Chapters 4 and 5 follow the same rules by hand.

Output is byte-stable: no timestamps, no host paths, no run counters. A
regenerated table is identical unless its data changed, so ``git diff`` over
``results/thesis/`` shows evidence drift and nothing else.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from ivfspea2.paths import PROJECT_ROOT, ensure_dir

__all__ = ["Gap", "Multirow", "Rule", "Span", "render", "write"]

# Sentinel rows. ``Rule`` separates row groups with a \midrule (the IVF/SPEA2
# block, then the IVF/NSGA-III block); ``Gap`` separates subgroups with space
# only (the suites inside a per-instance table). The renderer needs to know
# nothing else about grouping.
Rule = object()
Gap = object()


@dataclass(frozen=True)
class Span:
    """A cell covering ``width`` columns, set with ``\\multicolumn``.

    In a header, a span with text is ruled underneath when it groups several
    columns; ``rule=True`` rules a one-column group too, so that two groups
    side by side look alike.
    """

    text: str
    width: int = 1
    align: str = "c"
    rule: bool = False


@dataclass(frozen=True)
class Multirow:
    """A cell covering ``rows`` rows, centred on the vertical axis.

    A label that groups a contiguous block (a metric, a number of objectives)
    otherwise sits on the block's first line, reading as a property of that
    line alone. ``\\multirow`` centres it over the whole block instead.
    """

    text: str
    rows: int


Cell = str | Span | Multirow

# Column types that take one column each. ``p``, ``m`` and ``b`` also take a
# width argument; ``@``, ``!``, ``>`` and ``<`` insert material and take none.
_FLEXIBLE = frozenset("XL")
_PLAIN = frozenset("lcr") | _FLEXIBLE
_SIZED = frozenset("pmb")
_INSERTS = frozenset("@!><")


def _relative(path: Path | str) -> str:
    """Repo-relative path, so provenance comments are machine-independent."""
    try:
        return str(Path(path).resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _skip_group(spec: str, start: int) -> int:
    """Index just past the brace group opening at ``spec[start]``."""
    if start >= len(spec) or spec[start] != "{":
        raise ValueError(f"expected '{{' at position {start} of {spec!r}")
    depth = 0
    for index in range(start, len(spec)):
        if spec[index] == "{":
            depth += 1
        elif spec[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError(f"unbalanced braces in {spec!r}")


def _columns(colspec: str) -> int:
    """Number of columns a tabular preamble declares."""
    count = 0
    index = 0
    while index < len(colspec):
        char = colspec[index]
        if char in _INSERTS or char in _SIZED:
            count += char in _SIZED
            index = _skip_group(colspec, index + 1)
            continue
        if char in _PLAIN:
            count += 1
        elif char == "|":
            raise ValueError(f"vertical rule in {colspec!r}: the house style has none")
        elif not char.isspace():
            raise ValueError(f"unsupported column type {char!r} in {colspec!r}")
        index += 1
    return count


def _bold(text: str) -> str:
    return f"\\textbf{{{text}}}" if text else ""


def _header_rows(header: Sequence[Cell] | Sequence[Sequence[Cell]]) -> list[Sequence[Cell]]:
    """Accept one header row or several."""
    if header and isinstance(header[0], (list, tuple)):
        return list(header)  # type: ignore[arg-type]
    return [header]  # type: ignore[list-item]


def _row(cells: Sequence[Cell], ncols: int, *, header: bool) -> tuple[str, str]:
    """One row of cells, and the ``\\cmidrule`` line its header spans call for."""
    parts: list[str] = []
    rules: list[str] = []
    column = 1
    for cell in cells:
        if isinstance(cell, Multirow):
            text = _bold(cell.text) if header else cell.text
            parts.append(f"\\multirow{{{cell.rows}}}{{*}}{{{text}}}" if cell.rows > 1 else text)
            column += 1
            continue
        if not isinstance(cell, Span):
            parts.append(_bold(cell) if header else cell)
            column += 1
            continue
        last = column + cell.width - 1
        # A \multicolumn replaces the preamble of the columns it covers, so
        # a span at either edge restates the flush @{} of that edge.
        align = ("@{}" if column == 1 else "") + cell.align + ("@{}" if last == ncols else "")
        text = _bold(cell.text) if header else cell.text
        parts.append(f"\\multicolumn{{{cell.width}}}{{{align}}}{{{text}}}")
        if header and cell.text and (cell.width > 1 or cell.rule):
            # Trim the rule where it meets a neighbouring group, not at the
            # table edge, so it ends where the top rule ends.
            trim = ("l" if column > 1 else "") + ("r" if last < ncols else "")
            option = f"({trim})" if trim else ""
            rules.append(f"\\cmidrule{option}{{{column}-{last}}}")
        column = last + 1
    if column - 1 != ncols:
        raise ValueError(f"row covers {column - 1} columns but the colspec has {ncols}: {cells!r}")
    return " & ".join(parts) + " \\\\", "".join(rules)


def render(
    *,
    header: Sequence[Cell] | Sequence[Sequence[Cell]],
    rows: Sequence[Sequence[Cell] | object],
    colspec: str,
    caption: str,
    label: str,
    producer: Path | str,
    sources: Sequence[Path | str],
    note: str | None = None,
    short_caption: str | None = None,
    tabcolsep: str | None = None,
    placement: str = "!htb",
) -> str:
    """Render one ``table`` float as a string.

    ``colspec`` lists the columns only; the renderer adds the flush outer
    edges. ``header`` is one row of cells or a list of rows; header cells are
    bolded. ``rows`` may contain ``Rule`` and ``Gap`` to separate groups.
    ``note`` renders under the table in small type, for the scope and
    correction statements the writing profile requires next to every count.
    ``short_caption`` is the List of Tables entry, for a caption too long to
    set there cleanly. ``tabcolsep`` narrows the minimum gap between columns
    of a table that would otherwise overrun the text block: the type size is
    never the variable.
    """
    ncols = _columns(colspec)
    flexible = any(char in _FLEXIBLE for char in colspec)

    lines: list[str] = [
        f"% Gerado por {_relative(producer)} -- nao editar a mao.",
        "% Regenerar com: make thesis-tables",
    ]
    lines += [f"% Fonte: {_relative(s)}" for s in sources]
    entry = f"[{short_caption}]" if short_caption else ""
    lines += [
        f"\\begin{{table}}[{placement}]",
        "    \\centering",
        "    \\small",
    ]
    if tabcolsep:
        lines.append(f"    \\setlength{{\\tabcolsep}}{{{tabcolsep}}}")
    lines += [
        f"    \\caption{entry}{{{caption}}}",
        f"    \\label{{{label}}}",
    ]

    if flexible:
        environment = "tabularx"
        preamble = f"@{{}}{colspec}@{{}}"
    else:
        environment = "tabular*"
        preamble = f"@{{\\extracolsep{{\\fill}}}}{colspec}@{{}}"
    lines += [
        f"    \\begin{{{environment}}}{{\\textwidth}}{{{preamble}}}",
        "        \\toprule",
    ]

    for cells in _header_rows(header):
        text, rules = _row(cells, ncols, header=True)
        lines.append(f"        {text}")
        if rules:
            lines.append(f"        {rules}")
    lines.append("        \\midrule")

    for row in rows:
        if row is Rule:
            lines.append("        \\midrule")
            continue
        if row is Gap:
            lines.append("        \\addlinespace")
            continue
        text, _ = _row(row, ncols, header=False)  # type: ignore[arg-type]
        lines.append(f"        {text}")

    lines += [
        "        \\bottomrule",
        f"    \\end{{{environment}}}",
    ]

    if note:
        # A bare `{\footnotesize ...}` would inherit the float's \centering and
        # render the note as centred prose. The box restores justified text,
        # and at \textwidth its edges are the table's edges.
        lines += [
            "    \\par\\smallskip",
            "    \\parbox{\\textwidth}{\\footnotesize",
            f"    {note}",
            "    }",
        ]

    lines.append("\\end{table}")
    return "\n".join(lines) + "\n"


def write(path: Path, content: str) -> Path:
    """Write ``content`` to ``path``, creating parents. Returns the path."""
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    print(f"  escrito: {_relative(path)}")
    return path
