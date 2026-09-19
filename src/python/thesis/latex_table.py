"""LaTeX table emission for the dissertation.

Deliberately limited to what ``inf-ufg-tectonic.cls`` already loads. The class
does **not** require ``booktabs`` or ``siunitx``, and the imported chapters use
``|l|c|`` column specs with ``\\hline``, so every table here does the same.
Emitting booktabs rules would compile only after a preamble change, which
belongs to a chapter round, not to the artifact layer.

``graphicx`` *is* loaded by the class, so ``\\resizebox`` is available for the
wide per-instance tables.

Output is byte-stable: no timestamps, no host paths, no run counters. A
regenerated table is identical unless its data changed, so ``git diff`` over
``results/thesis/`` shows evidence drift and nothing else.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ivfspea2.paths import PROJECT_ROOT, ensure_dir

__all__ = ["Rule", "render", "write"]

# Sentinel row: emits a horizontal rule instead of cells. Lets a caller express
# grouped tables ("IVF/SPEA2 block, then IVF/NSGA-II block") without the
# renderer needing to know anything about grouping.
Rule = object()


def _relative(path: Path | str) -> str:
    """Repo-relative path, so provenance comments are machine-independent."""
    try:
        return str(Path(path).resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def render(
    *,
    header: Sequence[str],
    rows: Sequence[Sequence[str] | object],
    colspec: str,
    caption: str,
    label: str,
    producer: Path | str,
    sources: Sequence[Path | str],
    note: str | None = None,
    resize: bool = False,
    placement: str = "!htb",
) -> str:
    """Render one ``table`` float as a string.

    ``header`` cells are bolded. ``rows`` may contain ``Rule`` to break groups.
    ``note`` renders under the tabular in small type, for the scope and
    correction statements the writing profile requires next to every count.
    """
    ncols = len(header)
    for row in rows:
        if row is Rule:
            continue
        if len(row) != ncols:  # type: ignore[arg-type]
            raise ValueError(
                f"row has {len(row)} cells but header has {ncols}: {row!r}"  # type: ignore[arg-type]
            )

    lines: list[str] = [
        f"% Gerado por {_relative(producer)} -- nao editar a mao.",
        "% Regenerar com: make thesis-tables",
    ]
    lines += [f"% Fonte: {_relative(s)}" for s in sources]
    lines += [
        f"\\begin{{table}}[{placement}]",
        "    \\centering",
        f"    \\caption{{{caption}}}",
        f"    \\label{{{label}}}",
    ]

    if resize:
        lines.append("    \\resizebox{\\textwidth}{!}{%")

    lines += [
        f"    \\begin{{tabular}}{{{colspec}}}",
        "        \\hline",
        "        " + " & ".join(f"\\textbf{{{c}}}" for c in header) + " \\\\",
        "        \\hline",
    ]

    for row in rows:
        if row is Rule:
            lines.append("        \\hline")
            continue
        lines.append("        " + " & ".join(row) + " \\\\")  # type: ignore[arg-type]

    lines.append("        \\hline")
    lines.append("    \\end{tabular}")

    if resize:
        lines.append("    }")

    if note:
        # A bare `{\footnotesize ...}` would inherit the float's \centering and
        # render the note as centred prose. Boxing it restores justified text
        # while the box itself stays centred under the table.
        lines += [
            "    \\par\\smallskip",
            "    \\parbox{0.95\\textwidth}{\\footnotesize",
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
