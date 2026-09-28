#!/usr/bin/env python3
"""Claim-bearing tokens of LaTeX prose: inventory, snapshot and guarded diff.

Numbers, citation keys, cross-references, labels and claim-strength markers are
the parts of a scientific sentence that an edit must not change silently. This
tool makes them visible:

    claims.py inventory FILE[:START-END] ... [--json]
        every sentence that carries a number or a citation, with its line
    claims.py snapshot FILE ...
        copy FILE to .omp/runs/snapshots/<path> before an edit
    claims.py diff FILE ... [--json] [--strict]
        word-level diff against the snapshot, then the tokens that appeared or
        disappeared; --strict exits 3 when numbers, citations, refs or labels changed

Standard library only. It reports; it never edits the manuscript.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

SNAPSHOT_DIR = Path(".omp/runs/snapshots")

CITE = re.compile(
    r"\\(?:cite|citeonline|citeauthor|citeyear|citet|citep)\*?(?:\[[^\]]*\])*\{([^}]*)\}"
)
REF = re.compile(r"\\(?:ref|eqref|autoref|pageref|cref|Cref)\*?\{([^}]*)\}")
LABEL = re.compile(r"\\label\{([^}]*)\}")
# Arguments that hold names, paths or lengths rather than claims.
NON_CLAIM_ARGS = re.compile(
    r"\\(?:label|ref|eqref|autoref|pageref|cref|Cref|input|include|includegraphics|"
    r"cite\w*|url|href|begin|end|hspace|vspace|setlength|addtolength|setcounter|"
    r"renewcommand|newcommand|providecommand|captionsetup|usepackage|documentclass)"
    r"\*?(?:\[[^\]]*\])*(?:\{[^{}]*\})*"
)
NUMBER = re.compile(
    r"(?<![\w.,])[-−+]?\d+(?:[.,]\d+)*"
    r"(?:\s*[–-]\s*\d+(?:[.,]\d+)*)?"
    r"(?:/\d+(?:/\d+)?)?"
    r"(?:\s*%)?"
    r"(?![\w])"
)
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\\(])")
# Spelled-out quantities are claims too ("São quatro", "três vezes maior"). "um/uma" are
# left out: as articles they would drown the signal.
NUMBER_WORDS = re.compile(
    r"(?i)\b(?:dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|treze|"
    r"quatorze|catorze|quinze|dezesseis|dezessete|dezoito|dezenove|vinte|trinta|quarenta|"
    r"cinquenta|sessenta|setenta|oitenta|noventa|cem|cento|mil|metade|dobro|triplo|"
    r"qu[aá]druplo)\b"
)
# Words whose appearance or disappearance changes how strongly a sentence claims.
BOOSTERS = (
    "comprova",
    "prova",
    "demonstra",
    "garante",
    "confirma",
    "estabelece",
    "sempre",
    "nunca",
    "universal",
    "claramente",
    "evidentemente",
    "inequivoc",
    "definitiv",
    "significativ",
    "robust",
    "superior",
    "causa",
    "decorre",
    "deve-se",
    "devido a",
    "resulta de",
    "leva a",
    "determina",
)
HEDGES = (
    "sugere",
    "indica",
    "pode",
    "podem",
    "parece",
    "possivelmente",
    "provavelmente",
    "consistente com",
    "hipótese",
    "aparentemente",
    "em parte",
    "nesta amostra",
    "neste escopo",
    "delimitad",
    "não permite",
    "não isola",
)


@dataclass
class Sentence:
    path: str
    line: int
    text: str
    numbers: list[str] = field(default_factory=list)
    cites: list[str] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        )
        return Path(out.stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd()


def strip_comment(line: str) -> str:
    """Drop a LaTeX comment introduced by an unescaped percent sign."""
    for index, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def normalize(text: str) -> str:
    """Plain-ish text in which numbers read as the reader sees them."""
    text = NON_CLAIM_ARGS.sub(" ", text)
    text = text.replace("{,}", ",").replace("\\,", " ").replace("\\%", "%").replace("~", " ")
    text = text.replace("---", "—").replace("--", "–")
    text = re.sub(r"\\[A-Za-z@]+\*?", " ", text)
    text = text.replace("$", " ").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", text).strip()


def split_keys(matches: list[str]) -> list[str]:
    return [key.strip() for group in matches for key in group.split(",") if key.strip()]


def numbers_in(text: str) -> list[str]:
    plain = normalize(text)
    digits = [m.group(0).replace(" ", "") for m in NUMBER.finditer(plain)]
    words = [m.group(0).lower() for m in NUMBER_WORDS.finditer(plain)]
    return digits + words


def parse_target(spec: str) -> tuple[Path, int | None, int | None]:
    match = re.fullmatch(r"(.+?):(\d+)(?:-(\d+))?", spec)
    if match and not Path(spec).exists():
        start = int(match.group(2))
        end = int(match.group(3) or start)
        return Path(match.group(1)), start, end
    return Path(spec), None, None


def expand(specs: list[str]) -> list[tuple[Path, int | None, int | None]]:
    targets: list[tuple[Path, int | None, int | None]] = []
    for spec in specs:
        path, start, end = parse_target(spec)
        if path.is_dir():
            targets.extend((p, None, None) for p in sorted(path.rglob("*.tex")))
        elif path.is_file():
            targets.append((path, start, end))
        else:
            raise FileNotFoundError(f"not found: {spec}")
    return targets


def sentences(path: Path, start: int | None = None, end: int | None = None) -> list[Sentence]:
    found: list[Sentence] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if start is not None and not (start <= number <= (end or start)):
            continue
        line = strip_comment(raw)
        if not line.strip():
            continue
        for chunk in SENTENCE_END.split(line):
            cites = split_keys(CITE.findall(chunk))
            refs = split_keys(REF.findall(chunk))
            nums = numbers_in(chunk)
            if nums or cites:
                text = normalize(chunk)
                found.append(
                    Sentence(
                        path=str(path),
                        line=number,
                        text=text if len(text) <= 400 else text[:399] + "…",
                        numbers=nums,
                        cites=cites,
                        refs=refs,
                    )
                )
    return found


def markers(text: str) -> Counter[str]:
    low = normalize(text).lower()
    counts: Counter[str] = Counter()
    for word in BOOSTERS:
        counts[f"+{word}"] = len(re.findall(r"\b" + re.escape(word), low))
    for word in HEDGES:
        counts[f"~{word}"] = len(re.findall(r"\b" + re.escape(word), low))
    return +counts


def tokens(text: str) -> dict[str, Counter[str]]:
    body = "\n".join(strip_comment(line) for line in text.splitlines())
    return {
        "numbers": Counter(numbers_in(body)),
        "cites": Counter(split_keys(CITE.findall(body))),
        "refs": Counter(split_keys(REF.findall(body))),
        "labels": Counter(LABEL.findall(body)),
        "strength": markers(body),
    }


def delta(before: Counter[str], after: Counter[str]) -> dict[str, list[str]]:
    added = after - before
    removed = before - after
    return {
        "added": sorted(added.elements()),
        "removed": sorted(removed.elements()),
    }


def word_diff(old: str, new: str) -> str:
    old_words, new_words = old.split(), new.split()
    out: list[str] = []
    matcher = difflib.SequenceMatcher(a=old_words, b=new_words, autojunk=False)
    for op, a1, a2, b1, b2 in matcher.get_opcodes():
        if op == "equal":
            out.extend(old_words[a1:a2])
            continue
        if a2 > a1:
            out.append("[-" + " ".join(old_words[a1:a2]) + "-]")
        if b2 > b1:
            out.append("{+" + " ".join(new_words[b1:b2]) + "+}")
    return " ".join(out)


def text_diff(old: str, new: str) -> list[str]:
    old_lines, new_lines = old.splitlines(), new.splitlines()
    lines: list[str] = []
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    for op, a1, a2, b1, b2 in matcher.get_opcodes():
        if op == "equal":
            continue
        lines.append(f"@@ linha {b1 + 1} (antes {a1 + 1}) @@")
        if op == "replace" and a2 - a1 == b2 - b1:
            for i in range(a2 - a1):
                lines.append(word_diff(old_lines[a1 + i], new_lines[b1 + i]))
            continue
        lines.extend(f"- {line}" for line in old_lines[a1:a2])
        lines.extend(f"+ {line}" for line in new_lines[b1:b2])
    return lines


def snapshot_path(path: Path, root: Path) -> Path:
    try:
        relative = path.resolve().relative_to(root)
    except ValueError:
        relative = Path(*path.resolve().parts[1:])
    return root / SNAPSHOT_DIR / relative


def cmd_inventory(args: argparse.Namespace) -> int:
    found: list[Sentence] = []
    for path, start, end in expand(args.targets):
        found.extend(sentences(path, start, end))
    if args.json:
        payload = {
            "sentences": [asdict(item) for item in found],
            "totals": {
                "sentences": len(found),
                "numbers": sum(len(item.numbers) for item in found),
                "cite_keys": sorted({key for item in found for key in item.cites}),
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    for item in found:
        tags = []
        if item.numbers:
            tags.append("números: " + ", ".join(item.numbers))
        if item.cites:
            tags.append("citações: " + ", ".join(item.cites))
        print(f"{item.path}:{item.line}: {' | '.join(tags)}")
        print(f"  {item.text}")
    print(f"{len(found)} frases; {sum(len(i.numbers) for i in found)} números")
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    root = repo_root()
    for spec in args.files:
        path = parse_target(spec)[0]
        if not path.is_file():
            print(f"not found: {spec}", file=sys.stderr)
            return 1
        target = snapshot_path(path, root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        print(f"snapshot: {target.relative_to(root)}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    root = repo_root()
    report: list[dict[str, object]] = []
    changed_hard = False
    for spec in args.files:
        path = parse_target(spec)[0]
        snap = snapshot_path(path, root)
        if not snap.is_file():
            print(f"no snapshot for {spec}; run: claims.py snapshot {spec}", file=sys.stderr)
            return 1
        old = snap.read_text(encoding="utf-8")
        new = path.read_text(encoding="utf-8")
        old_tokens, new_tokens = tokens(old), tokens(new)
        guard = {kind: delta(old_tokens[kind], new_tokens[kind]) for kind in old_tokens}
        if any(
            guard[k]["added"] or guard[k]["removed"] for k in ("numbers", "cites", "refs", "labels")
        ):
            changed_hard = True
        report.append({"path": str(path), "diff": text_diff(old, new), "guard": guard})

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for entry in report:
            print(f"== {entry['path']}")
            diff_lines = entry["diff"]
            print("\n".join(diff_lines) if diff_lines else "(sem alteração)")
            print("-- guarda")
            names = {
                "numbers": "números",
                "cites": "citações",
                "refs": "referências cruzadas",
                "labels": "rótulos",
                "strength": "marcadores de força (+ reforço, ~ ressalva)",
            }
            for kind, label in names.items():
                change = entry["guard"][kind]
                if change["added"] or change["removed"]:
                    print(f"  {label}: +{change['added']} -{change['removed']}")
            if not any(entry["guard"][k]["added"] or entry["guard"][k]["removed"] for k in names):
                print("  nenhuma mudança em números, citações, rótulos ou força")
    return 3 if args.strict and changed_hard else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory", help="sentences with numbers or citations")
    inventory.add_argument("targets", nargs="+", help="file, file:START-END or directory")
    inventory.add_argument("--json", action="store_true")
    inventory.set_defaults(func=cmd_inventory)

    snapshot = sub.add_parser("snapshot", help="save a copy before editing")
    snapshot.add_argument("files", nargs="+")
    snapshot.set_defaults(func=cmd_snapshot)

    diff = sub.add_parser("diff", help="compare against the snapshot")
    diff.add_argument("files", nargs="+")
    diff.add_argument("--json", action="store_true")
    diff.add_argument("--strict", action="store_true", help="exit 3 if claim tokens changed")
    diff.set_defaults(func=cmd_diff)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (FileNotFoundError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
