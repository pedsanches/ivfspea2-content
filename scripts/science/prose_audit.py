#!/usr/bin/env python3
"""Conservative editorial audit for Portuguese scientific prose.

This tool reports review signals such as placeholders, inflated claims,
formulaic transitions, very long sentences, negation-correction ("não é X, mas
Y") and em-dash density. It is not an AI detector, does not determine
authorship, and does not verify citations or statistical correctness. It never
rewrites text automatically.

Provenance: vendored from the author's personal Codex skill
``write-scientific-manuscripts/scripts/audit_scientific_text.py`` (sha256
948b134e…9aa5, 2026-09-24) so that the check is versioned with the thesis. The
two added signals follow docs/ai-scientific-writing/research.md §4 and the
stylometry in .omp/skills/scientific-writing-ptbr/references/voz.md.

    python3 scripts/science/prose_audit.py thesis/masters/tex/cap_IV.tex
    python3 scripts/science/prose_audit.py thesis/masters/tex --format json
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

TEXT_EXTENSIONS = {".tex", ".md", ".txt", ".rst"}
SKIP_DIRS = {
    ".git",
    ".venv",
    "build",
    "dist",
    "node_modules",
    "__pycache__",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    severity: str
    rule: str
    excerpt: str
    message: str


LINE_RULES: tuple[tuple[str, str, str, re.Pattern[str]], ...] = (
    (
        "high",
        "placeholder",
        "Resolve the explicit placeholder before submission.",
        re.compile(
            r"(?ix)"
            # Uppercase only: Portuguese "todo" ("para todo j", "como um todo") is not a marker.
            r"(?-i:\b(?:TODO|FIXME|XXX)\b)|"
            r"\[(?:FONTE|CITA[CÇ][AÃ]O|REFER[ÊE]NCIA|N[AÃ]O\s+VERIFICADO)[^\]]*\]|"
            r"\\cite\{(?:todo|placeholder|citation[-_]?needed|fonte)[^}]*\}"
        ),
    ),
    (
        "high",
        "nocite-all",
        r"Remove \nocite{*}; cite only sources actually used.",
        re.compile(r"\\nocite\s*\{\s*\*\s*\}"),
    ),
    (
        "high",
        "impossible-p-value",
        "A p-value should not be reported as exactly zero; use an exact value or justified bound.",
        re.compile(r"(?i)\bp\s*[=]\s*0[,.]0{2,}\b"),
    ),
    (
        "medium",
        "absolute-claim",
        "Check whether the design supports this absolute or proof-like wording.",
        re.compile(
            r"(?ix)\b(?:"
            r"comprova(?:d[oa]mente)?|prova\s+definitivamente|"
            r"sempre\s+supera|superioridade\s+universal|"
            r"em\s+todos\s+os\s+cen[aá]rios|sem\s+qualquer\s+limita[cç][aã]o"
            r")\b"
        ),
    ),
    (
        "advisory",
        "empty-emphasis",
        "Delete or replace empty emphasis with the claim itself.",
        re.compile(
            r"(?ix)\b(?:"
            r"[ée]\s+importante\s+(?:destacar|ressaltar|salientar)(?:\s+que)?|"
            r"vale\s+(?:destacar|ressaltar|salientar)(?:\s+que)?|"
            r"cabe\s+(?:destacar|mencionar|ressaltar)(?:\s+que)?|"
            r"[ée]\s+v[aá]lido\s+(?:observar|destacar)(?:\s+que)?"
            r")\b"
        ),
    ),
    (
        "advisory",
        "formulaic-connector",
        "Verify that this formal connector expresses a necessary relation; remove it if it "
        "only decorates the transition.",
        re.compile(r"(?i)\bademais\b"),
    ),
    (
        "advisory",
        "vague-evaluation",
        "Operationalize or support the evaluative term; do not treat it as self-evident.",
        re.compile(
            r"(?ix)\b(?:"
            r"abrangente|consider[aá]vel|eficaz|eficiente|inovador[ao]?|"
            r"not[aá]vel|promissor[ao]?|robust[oa]|sofisticad[oa]|"
            r"superior(?:es)?|significativ[oa]s?"
            r")\b"
        ),
    ),
    (
        "advisory",
        "english-calque",
        "Check for an avoidable English calque and prefer natural Brazilian Portuguese.",
        re.compile(
            r"(?ix)\b(?:"
            r"endere[cç]ar\s+(?:o|a|um|uma)\s+(?:problema|quest[aã]o)|"
            r"performar|perform[aá]tico|"
            r"atrav[eé]s\s+de\s+(?:um|uma|o|a)\s+(?:m[eé]todo|algoritmo|an[aá]lise)"
            r")\b"
        ),
    ),
    (
        "advisory",
        "negation-correction",
        "Negation-correction ('não é X, mas Y'): keep it only if X is a reading that the text "
        "or the literature actually holds; otherwise state Y directly.",
        re.compile(
            r"(?i)\bn[aã]o\s+(?:[eé]|s[aã]o|se\s+trata\s+de|apenas|s[oó]|somente)\b"
            r"[^.!?;]{1,160}?"
            r"(?:,\s*(?:mas|e\s+sim|sen[aã]o)\b|;\s*(?:[eé]|s[aã]o)\b|---\s*(?:[eé]|s[aã]o)\b)"
        ),
    ),
)


OPENERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("neste contexto", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*neste contexto\b")),
    ("além disso", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*al[eé]m disso\b")),
    ("ademais", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*ademais\b")),
    ("dessa forma", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*dessa forma\b")),
    ("nesse sentido", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*nesse sentido\b")),
    ("por fim", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*por fim\b")),
    ("em suma", re.compile(r"(?i)^\s*(?:\\\w+\{[^}]*\}\s*)*em suma\b")),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report conservative editorial signals in scientific text. This is not an AI detector."
        )
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to audit")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on",
        choices=("never", "high", "medium", "advisory"),
        default="never",
        help="Return exit status 2 when this severity or a higher one is found",
    )
    parser.add_argument(
        "--max-sentence-words",
        type=int,
        default=55,
        help="Advisory sentence-length threshold (default: 55)",
    )
    parser.add_argument(
        "--repeated-opener-threshold",
        type=int,
        default=3,
        help="File-level opener repetition threshold (default: 3)",
    )
    parser.add_argument(
        "--max-dashes-per-1k",
        type=float,
        default=3.0,
        help="Advisory em-dash density threshold per 1,000 prose words (default: 3.0)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help=(
            "Exclude a path or filename glob; repeat as needed "
            "(for example: --exclude 'SCIENTIFIC_WRITING_PROFILE.md')"
        ),
    )
    return parser.parse_args()


def is_excluded(path: Path, patterns: Iterable[str]) -> bool:
    path_text = path.as_posix()
    return any(
        fnmatch.fnmatch(path_text, pattern) or fnmatch.fnmatch(path.name, pattern)
        for pattern in patterns
    )


def iter_files(paths: Iterable[Path], exclude_patterns: Iterable[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    for raw_path in paths:
        path = raw_path.resolve()
        if path.is_file():
            candidates = (path,)
        elif path.is_dir():
            candidates = (
                item
                for item in path.rglob("*")
                if item.is_file()
                and item.suffix.lower() in TEXT_EXTENSIONS
                and not any(part in SKIP_DIRS for part in item.parts)
            )
        else:
            raise FileNotFoundError(f"Path does not exist: {raw_path}")

        for candidate in candidates:
            if candidate.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            resolved = candidate.resolve()
            if resolved not in seen and not is_excluded(resolved, exclude_patterns):
                seen.add(resolved)
                yield resolved


def strip_tex_comment(line: str) -> str:
    """Strip a LaTeX comment introduced by an unescaped percent sign."""
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


def normalize_for_sentence_scan(text: str) -> str:
    text = re.sub(r"\\(?:cite|ref|eqref|label|url|href)\*?(?:\[[^\]]*\])?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\$[^$]*\$", " EQUATION ", text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(text: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


EM_DASH = re.compile(r"(?<!-)---(?!-)|—")


def audit_file(
    path: Path,
    max_sentence_words: int,
    repeated_opener_threshold: int,
    max_dashes_per_1k: float = 3.0,
) -> list[Finding]:
    findings: list[Finding] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    opener_lines: dict[str, list[int]] = defaultdict(list)
    in_markdown_fence = False
    dash_lines: list[int] = []
    prose_words = 0

    for line_number, raw_line in enumerate(lines, start=1):
        if path.suffix.lower() == ".md" and re.match(r"^\s*(?:```|~~~)", raw_line):
            in_markdown_fence = not in_markdown_fence
            continue
        if in_markdown_fence:
            continue

        line = strip_tex_comment(raw_line) if path.suffix.lower() == ".tex" else raw_line
        if not line.strip():
            continue

        for severity, rule, message, pattern in LINE_RULES:
            for match in pattern.finditer(line):
                if rule == "absolute-claim":
                    prefix = line[max(0, match.start() - 60) : match.start()]
                    if re.search(
                        r"(?i)(?:"
                        r"\bn[aã]o(?:\s+\w+){0,2}|"
                        r"\bnem|"
                        r"\bsem(?:\s+\w+){0,2}|"
                        r"\bem\s+vez\s+de(?:\s+\w+){0,2}|"
                        r"\bevitar(?:\s+\w+){0,2}"
                        r")\s*$",
                        prefix,
                    ):
                        continue
                findings.append(
                    Finding(
                        path=str(path),
                        line=line_number,
                        severity=severity,
                        rule=rule,
                        excerpt=excerpt(match.group(0)),
                        message=message,
                    )
                )

        for name, pattern in OPENERS:
            if pattern.search(line):
                opener_lines[name].append(line_number)
        normalized = normalize_for_sentence_scan(line)
        dash_count = len(EM_DASH.findall(line))
        dash_lines.extend([line_number] * dash_count)
        prose_words += len(re.findall(r"\b[\wÀ-ÿ'-]+\b", normalized, flags=re.UNICODE))
        for sentence in re.split(r"(?<=[.!?])\s+", normalized):
            words = re.findall(r"\b[\wÀ-ÿ'-]+\b", sentence, flags=re.UNICODE)
            if len(words) > max_sentence_words:
                findings.append(
                    Finding(
                        path=str(path),
                        line=line_number,
                        severity="advisory",
                        rule="long-sentence",
                        excerpt=excerpt(sentence),
                        message=(
                            f"Sentence has approximately {len(words)} words; "
                            "check whether the main clause and qualifications remain clear."
                        ),
                    )
                )

    for name, line_numbers in opener_lines.items():
        if len(line_numbers) >= repeated_opener_threshold:
            findings.append(
                Finding(
                    path=str(path),
                    line=line_numbers[0],
                    severity="advisory",
                    rule="repeated-opener",
                    excerpt=f"{name}: lines {', '.join(map(str, line_numbers[:8]))}",
                    message=(
                        f"The opener appears {len(line_numbers)} times in this file; "
                        "verify that each occurrence expresses a necessary logical relation."
                    ),
                )
            )

    if prose_words >= 200 and dash_lines:
        density = 1000 * len(dash_lines) / prose_words
        if density > max_dashes_per_1k:
            findings.append(
                Finding(
                    path=str(path),
                    line=dash_lines[0],
                    severity="advisory",
                    rule="dash-density",
                    excerpt=f"lines {', '.join(map(str, sorted(set(dash_lines))[:12]))}",
                    message=(
                        f"{len(dash_lines)} em-dashes in about {prose_words} words "
                        f"({density:.1f} per 1,000); keep a dash where it isolates an "
                        "internal enumeration, otherwise prefer a comma, parentheses or a "
                        "new sentence."
                    ),
                )
            )

    return findings


def severity_rank(severity: str) -> int:
    return {"high": 3, "medium": 2, "advisory": 1}[severity]


def print_text(findings: list[Finding], files_checked: int) -> None:
    print("Scientific text advisory audit (not an AI detector)")
    print(
        "Scope: editorial signals only; citations, statistics, and authorship require "
        "separate verification"
    )
    print(f"Files checked: {files_checked}")
    if not findings:
        print("No configured review signals found.")
        return

    for finding in findings:
        print(
            f"{finding.path}:{finding.line}: "
            f"{finding.severity.upper()} [{finding.rule}] {finding.message}"
        )
        print(f"  {finding.excerpt}")

    counts = Counter(item.severity for item in findings)
    print(
        f"Summary: {counts['high']} high, {counts['medium']} medium, {counts['advisory']} advisory"
    )


def main() -> int:
    args = parse_args()
    try:
        files = sorted(iter_files(args.paths, args.exclude))
    except (FileNotFoundError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    if not files:
        print(
            "No supported text files were found after applying extensions and exclusions.",
            file=sys.stderr,
        )
        return 1

    findings: list[Finding] = []
    try:
        for path in files:
            findings.extend(
                audit_file(
                    path,
                    max_sentence_words=args.max_sentence_words,
                    repeated_opener_threshold=args.repeated_opener_threshold,
                    max_dashes_per_1k=args.max_dashes_per_1k,
                )
            )
    except (OSError, UnicodeError) as error:
        print(f"Could not audit file: {error}", file=sys.stderr)
        return 1

    findings.sort(
        key=lambda item: (
            item.path,
            item.line,
            -severity_rank(item.severity),
            item.rule,
        )
    )

    if args.output_format == "json":
        print(
            json.dumps(
                {
                    "tool": "scientific-text-advisory-audit",
                    "is_ai_detector": False,
                    "files_checked": len(files),
                    "findings": [asdict(item) for item in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(findings, len(files))

    if args.fail_on == "never":
        return 0

    threshold = severity_rank(args.fail_on)
    return 2 if any(severity_rank(item.severity) >= threshold for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
