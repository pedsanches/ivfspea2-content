#!/usr/bin/env python3
"""Classify the warnings of a LaTeX build and tell new problems from old ones.

Reads the TeX log, the BibTeX log and the .aux of a finished build (Tectonic keeps
all three with --keep-logs --keep-intermediates) and sorts every signal into a
category. Blocking categories fail the check; layout categories are reported.

    python3 scripts/science/latex_check.py                  # state of the last build
    python3 scripts/science/latex_check.py --save-baseline  # before an edit
    python3 scripts/science/latex_check.py --compare        # after rebuilding

Defaults point at the dissertation (thesis/masters/build/main.*). With --compare,
only blocking items absent from the baseline fail (exit 1); a warning that already
existed is reported as pre-existing, not as a regression. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

BUILD = Path("thesis/masters/build")
DEFAULT_BASELINE = Path(".omp/runs/latex-baseline.json")
WRAP = 79  # TeX's default max_print_line; longer logical lines continue on the next line.

BLOCKING = {
    "error",
    "undefined_reference",
    "undefined_citation",
    "multiply_defined",
    "missing_file",
    "cited_not_in_bib",
    "bibtex_error",
}

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("error", re.compile(r"^! (.+)")),
    ("undefined_reference", re.compile(r"Reference [`'](.+?)' on page .* undefined")),
    ("undefined_citation", re.compile(r"Citation [`'](.+?)' on page .* undefined")),
    ("multiply_defined", re.compile(r"Label [`'](.+?)' multiply defined")),
    ("missing_file", re.compile(r"(?:File|file) [`'](.+?)' not found")),
    ("overfull", re.compile(r"^Overfull \\[hv]box \((.+?)\)")),
    ("underfull", re.compile(r"^Underfull \\[hv]box \((.+?)\)")),
    ("float_only_page", re.compile(r"Text page (\d+) contains only floats")),
    ("rerun", re.compile(r"(Label\(s\) may have changed|There were undefined references)")),
    ("font", re.compile(r"^LaTeX Font Warning: (.+)")),
    ("hyperref", re.compile(r"^Package hyperref Warning: (.+)")),
    ("other_warning", re.compile(r"^(?:LaTeX|Package \w+|Class \w+) Warning: (.+)")),
]
FILE_OPEN = re.compile(r"\(([^\s()\[\]]+)")
SOURCE_SUFFIX = re.compile(r"\.(?:tex|bbl|toc|aux|lof|lot|loa|out|cls|sty|def|cfg|clo|fd)$")


def opened_files(line: str) -> list[str]:
    """Paths TeX reports opening on this line: "(./tex/cap_IX", "(main.bbl", ..."""
    return [
        token.removeprefix("./")
        for token in FILE_OPEN.findall(line)
        if "/" in token or SOURCE_SUFFIX.search(token)
    ]


@dataclass(frozen=True)
class Item:
    category: str
    key: str
    source: str
    line: int
    text: str


def logical_lines(text: str) -> list[tuple[int, str]]:
    """Undo TeX's hard wrap so that one message is one line."""
    out: list[tuple[int, str]] = []
    buffer, start = "", 0
    for number, line in enumerate(text.splitlines(), start=1):
        if not buffer:
            start = number
        buffer += line
        if len(line) < WRAP and len(line.encode("utf-8")) < WRAP:
            out.append((start, buffer))
            buffer = ""
    if buffer:
        out.append((start, buffer))
    return out


def parse_log(path: Path) -> list[Item]:
    items: list[Item] = []
    current = "?"
    for number, line in logical_lines(path.read_text(encoding="utf-8", errors="replace")):
        opened = opened_files(line)
        if opened:
            current = opened[-1]
        for category, pattern in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            if category in {"overfull", "underfull"}:
                where = re.search(r"at lines (\d+)--(\d+)", line)
                key = f"{current}:{where.group(1)}" if where else current
            elif category == "float_only_page":
                key = "page"
            else:
                key = match.group(1)
                if "#" in key:  # TeX help text quoting a macro ("File `#1.#2' not found")
                    break
            items.append(Item(category, key, current, number, line.strip()[:240]))
            break
    return items


def parse_blg(path: Path) -> list[Item]:
    items: list[Item] = []
    for number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if line.startswith("Warning--"):
            missing = re.search(r"didn't find a database entry for \"(.+?)\"", line)
            category = "cited_not_in_bib" if missing else "bibtex_warning"
            key = missing.group(1) if missing else line[9:].strip()
            items.append(Item(category, key, path.name, number, line.strip()))
        elif re.search(r"I couldn't open|---line \d+ of file|I was expecting", line):
            items.append(Item("bibtex_error", line.strip(), path.name, number, line.strip()))
    return items


def aux_citations(path: Path) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(
        r"\\citation\{([^}]*)\}", path.read_text(encoding="utf-8", errors="replace")
    ):
        keys.update(k.strip() for k in match.group(1).split(",") if k.strip())
    keys.discard("*")
    return keys


def aux_bibdata(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\bibdata\{([^}]*)\}", text)
    if not match:
        return []
    base = path.parent.parent  # build/ lives next to the .bib directory of the document
    files = []
    for name in match.group(1).split(","):
        candidate = (base / name.strip()).with_suffix(".bib")
        files.append(candidate)
    return files


def bib_keys(paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    for path in paths:
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            keys.update(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", text))
    return keys


def collect(log: Path, blg: Path, aux: Path, bibs: list[Path]) -> list[Item]:
    items: list[Item] = []
    if log.is_file():
        items.extend(parse_log(log))
    else:
        items.append(Item("missing_file", str(log), "build", 0, "log not found: build first"))
    if blg.is_file():
        items.extend(parse_blg(blg))
    if aux.is_file():
        bib_paths = bibs or aux_bibdata(aux)
        defined = bib_keys(bib_paths)
        if defined:
            reported = {i.key for i in items if i.category == "cited_not_in_bib"}
            for key in sorted(aux_citations(aux) - defined - reported):
                items.append(Item("cited_not_in_bib", key, aux.name, 0, f"\\citation{{{key}}}"))
    return items


def summarize(items: list[Item]) -> dict[str, int]:
    return dict(sorted(Counter(i.category for i in items).items()))


def fingerprint(item: Item) -> str:
    return f"{item.category}|{item.key}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--log", type=Path, default=BUILD / "main.log")
    parser.add_argument("--blg", type=Path, default=BUILD / "main.blg")
    parser.add_argument("--aux", type=Path, default=BUILD / "main.aux")
    parser.add_argument("--bib", type=Path, action="append", default=[], help="override \\bibdata")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--save-baseline", action="store_true")
    group.add_argument("--compare", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    items = collect(args.log, args.blg, args.aux, args.bib)

    if args.save_baseline:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"baseline: {args.baseline} ({len(items)} itens: {summarize(items)})")
        return 0

    baseline: list[Item] | None = None
    if args.compare:
        if not args.baseline.is_file():
            print(
                f"sem linha de base em {args.baseline}; rode --save-baseline antes", file=sys.stderr
            )
            return 2
        baseline = [Item(**raw) for raw in json.loads(args.baseline.read_text(encoding="utf-8"))]

    old = Counter(fingerprint(i) for i in baseline) if baseline is not None else Counter()
    seen: Counter[str] = Counter()
    rows = []
    for item in items:
        seen[fingerprint(item)] += 1
        status = "preexistente" if seen[fingerprint(item)] <= old[fingerprint(item)] else "novo"
        if baseline is None:
            status = "atual"
        rows.append((item, status))
    new_blocking = [i for i, s in rows if s != "preexistente" and i.category in BLOCKING]
    resolved = old - Counter(fingerprint(i) for i in items) if baseline is not None else Counter()

    if args.json:
        print(
            json.dumps(
                {
                    "summary": summarize(items),
                    "items": [asdict(i) | {"status": s} for i, s in rows],
                    "new_blocking": len(new_blocking),
                    "resolved": sorted(resolved.elements()),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"resumo: {summarize(items) or 'nenhum aviso classificado'}")
        for item, status in rows:
            flag = "BLOQUEANTE" if item.category in BLOCKING else "aviso"
            print(f"[{status}] {flag} {item.category} {item.key} ({item.source}, log:{item.line})")
        if baseline is not None:
            print(f"resolvidos desde a linha de base: {sorted(resolved.elements()) or 'nenhum'}")
        print(f"bloqueantes {'novos' if baseline is not None else 'atuais'}: {len(new_blocking)}")
    return 1 if new_blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
