#!/usr/bin/env python3
"""Check a BibTeX database offline and, on request, against Crossref/doi.org.

Offline (default): duplicate keys, required fields by entry type, DOI and year
shape, keys cited in the build (.aux) but missing from the .bib, entries never
cited. Online (--online): for entries with a DOI, fetch the Crossref record (or
doi.org CSL-JSON for DataCite DOIs such as arXiv and Zenodo) and compare title,
year and first author, and report retractions/corrections (Crossref `updated-by`,
fed by Retraction Watch). Entries without a DOI get the best Crossref title match
as a *candidate*, never as a correction.

Only bibliographic metadata leaves the machine; manuscript text never does. The
tool reports; it never edits the .bib.

    python3 scripts/science/bib_check.py
    python3 scripts/science/bib_check.py --keys deb2002fast,holm1979simple --online
    python3 scripts/science/bib_check.py --online --json > .omp/runs/bib.json
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_BIB = Path("thesis/masters/bib/modelo-tese.bib")
DEFAULT_AUX = Path("thesis/masters/build/main.aux")
USER_AGENT = "ivfspea2-bib-check/1.0 (+https://github.com/pedsanches/ivfspea2-content)"
# Crossref "polite pool" (mailto): falls back to the caller's git identity; the
# service is merely told who is calling. Leave MAILTO empty to bypass it.
MAILTO = os.environ.get("OMP_BIB_CHECK_MAILTO", "pedrosanches@discente.ufg.br")

REQUIRED = {
    "article": [("author",), ("title",), ("journal",), ("year",)],
    "book": [("author", "editor"), ("title",), ("publisher",), ("year",)],
    "inproceedings": [("author",), ("title",), ("booktitle",), ("year",)],
    "conference": [("author",), ("title",), ("booktitle",), ("year",)],
    "incollection": [("author",), ("title",), ("booktitle",), ("publisher",), ("year",)],
    "techreport": [("author",), ("title",), ("institution",), ("year",)],
    "phdthesis": [("author",), ("title",), ("school",), ("year",)],
    "mastersthesis": [("author",), ("title",), ("school",), ("year",)],
    "misc": [("title",)],
}
DOI_SHAPE = re.compile(r"^10\.\d{4,9}/\S+$")


@dataclass
class Entry:
    key: str
    kind: str
    fields: dict[str, str]
    line: int


@dataclass
class Result:
    key: str
    kind: str
    status: str
    issues: list[str] = field(default_factory=list)
    doi: str = ""
    remote: dict[str, object] = field(default_factory=dict)


def parse_bib(text: str) -> list[Entry]:
    """Small BibTeX parser: braces, quotes and bare values; @string/@comment skipped."""
    entries: list[Entry] = []
    for match in re.finditer(r"@(\w+)\s*\{", text):
        kind = match.group(1).lower()
        if kind in {"comment", "preamble", "string"}:
            continue
        pos = match.end()
        key_match = re.match(r"\s*([^,\s]+)\s*,", text[pos:])
        if not key_match:
            continue
        key = key_match.group(1)
        pos += key_match.end()
        fields: dict[str, str] = {}
        while pos < len(text):
            field_match = re.match(r"\s*([\w-]+)\s*=\s*", text[pos:])
            if not field_match:
                break
            name = field_match.group(1).lower()
            pos += field_match.end()
            value, pos = read_value(text, pos)
            fields[name] = re.sub(r"\s+", " ", value).strip()
            tail = re.match(r"\s*,?", text[pos:])
            pos += tail.end() if tail else 0
            if re.match(r"\s*\}", text[pos:]):
                break
        entries.append(Entry(key, kind, fields, text.count("\n", 0, match.start()) + 1))
    return entries


def read_value(text: str, pos: int) -> tuple[str, int]:
    parts: list[str] = []
    while pos < len(text):
        char = text[pos]
        if char == "{":
            depth, start = 0, pos
            while pos < len(text):
                if text[pos] == "{":
                    depth += 1
                elif text[pos] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                pos += 1
            parts.append(text[start + 1 : pos])
            pos += 1
        elif char == '"':
            end = pos + 1
            while end < len(text) and not (text[end] == '"' and text[end - 1] != "\\"):
                end += 1
            parts.append(text[pos + 1 : end])
            pos = end + 1
        else:
            bare = re.match(r"[^,#}\s]+", text[pos:])
            if bare:
                parts.append(bare.group(0))
                pos += bare.end()
        concat = re.match(r"\s*#\s*", text[pos:])
        if not concat:
            break
        pos += concat.end()
    return "".join(parts), pos


ACCENTS = {
    "\\'s": "š",
    "\\'z": "ž",
    "\\'c": "ć",
    "\\'e": "é",
    "\\'a": "á",
    "\\'i": "í",
    "\\'o": "ó",
    "\\'u": "ú",
    "\\'y": "ý",
    "\\'n": "ń",
    "\\'l": "ĺ",
    "\\`e": "è",
    "\\`a": "à",
    "\\`i": "ì",
    "\\`o": "ò",
    "\\`u": "ù",
    "\\^o": "ô",
    "\\^e": "ê",
    "\\^a": "â",
    "\\^i": "î",
    "\\^u": "û",
    '\\"o': "ö",
    '\\"e': "ë",
    '\\"u': "ü",
    '\\"a': "ä",
    '\\"i': "ï",
    "\\~n": "ñ",
    "\\~a": "ã",
    "\\~o": "õ",
}


def plain(text: str) -> str:
    """Comparable form: accents from LaTeX macros resolved, punctuation gone, lower case."""
    for macro, letter in ACCENTS.items():
        text = text.replace(macro, letter)
    text = re.sub(r"\\[cv]\{([a-z])\}", r"\1", text)  # \c{s}, \v{z}
    text = re.sub(r"\\[A-Za-z]+\s*", " ", text)
    text = re.sub(r"\\.", "", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s]", " ", text.replace("{", "").replace("}", ""))
    return re.sub(r"\s+", " ", text).strip().lower()


def author_families(authors: str) -> list[str]:
    """Family names in BibTeX order; "others" is kept as a marker for et al."""
    families = []
    for person in re.split(r"\s+and\s+", authors.strip()):
        if not person:
            continue
        family = person.split(",")[0] if "," in person else (person.split() or [""])[-1]
        families.append(plain(family))
    return families


def first_author_family(authors: str) -> str:
    families = author_families(authors)
    return families[0] if families else ""


def normalize_doi(raw: str) -> str:
    doi = raw.strip()
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi, flags=re.I)
    return doi


def offline_checks(entries: list[Entry], cited: set[str] | None) -> dict[str, Result]:
    results: dict[str, Result] = {}
    counts = Counter(e.key for e in entries)
    lower = Counter(e.key.lower() for e in entries)
    for entry in entries:
        result = results.setdefault(entry.key, Result(entry.key, entry.kind, "ok"))
        if counts[entry.key] > 1:
            result.issues.append(f"chave duplicada ({counts[entry.key]}x)")
        elif lower[entry.key.lower()] > 1:
            result.issues.append("chave difere de outra só por maiúsculas")
        for alternatives in REQUIRED.get(entry.kind, [("title",)]):
            if not any(entry.fields.get(name) for name in alternatives):
                result.issues.append(f"campo obrigatório ausente: {'/'.join(alternatives)}")
        doi = normalize_doi(entry.fields.get("doi", ""))
        if doi:
            result.doi = doi
            if not DOI_SHAPE.match(doi):
                result.issues.append(f"DOI malformado: {doi}")
        year = entry.fields.get("year", "")
        if year and not re.fullmatch(r"(19|20)\d{2}[a-z]?", year):
            result.issues.append(f"ano fora do padrão: {year}")
        if cited is not None and entry.key not in cited:
            result.issues.append("nunca citada no documento")
    if cited is not None:
        defined = {e.key for e in entries}
        for key in sorted(cited - defined):
            results[key] = Result(key, "?", "missing", ["citada no documento sem entrada no .bib"])
    for result in results.values():
        if result.status == "ok" and result.issues:
            only_unused = all(i == "nunca citada no documento" for i in result.issues)
            result.status = "unused" if only_unused else "warn"
    return results


def http_json(url: str, accept: str = "application/json", timeout: float = 20.0) -> dict:
    """GET JSON, retrying politely on 429/503 (Retry-After or exponential backoff)."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code not in {429, 503} or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After", "")
            time.sleep(float(retry_after) if retry_after.isdigit() else 2.0 * 2**attempt)
    raise RuntimeError("unreachable")


def handle_exists(doi: str) -> bool | None:
    """Ask the DOI handle system whether the DOI is registered at all."""
    quoted = urllib.parse.quote(doi, safe="/()")
    try:
        code = http_json(f"https://doi.org/api/handles/{quoted}").get("responseCode")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False
        raise
    return {1: True, 100: False}.get(code)


def remote_record(doi: str) -> dict | None:
    quoted = urllib.parse.quote(doi, safe="/()")
    try:
        return http_json(f"https://api.crossref.org/works/{quoted}")["message"]
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    try:  # DataCite and other agencies: CSL-JSON through doi.org content negotiation
        return http_json(
            f"https://doi.org/{quoted}", accept="application/vnd.citationstyles.csl+json"
        )
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def record_summary(record: dict) -> dict[str, object]:
    title = record.get("title")
    title = title[0] if isinstance(title, list) and title else (title or "")
    issued = record.get("issued") or record.get("published") or {}
    parts = issued.get("date-parts") or [[None]]
    authors = record.get("author") or []
    families = [plain(str(a.get("family", ""))) for a in authors if a.get("family")]
    family = families[0] if families else ""
    container = record.get("container-title")
    container = container[0] if isinstance(container, list) and container else (container or "")
    updates = [
        {"type": u.get("type"), "source": u.get("source"), "doi": u.get("DOI")}
        for u in record.get("updated-by") or []
    ]
    return {
        "title": title,
        "year": parts[0][0] if parts and parts[0] else None,
        "first_author": family,
        "authors": families,
        "container": container,
        "type": record.get("type"),
        "updated_by": updates,
    }


def compare(entry: Entry, result: Result, summary: dict[str, object]) -> None:
    result.remote = summary
    title_ratio = difflib.SequenceMatcher(
        a=plain(entry.fields.get("title", "")), b=plain(str(summary["title"]))
    ).ratio()
    result.remote["title_similarity"] = round(title_ratio, 3)
    if title_ratio < 0.85:
        result.issues.append(f"título diverge do registro (similaridade {title_ratio:.2f})")
    year = entry.fields.get("year", "")[:4]
    if summary["year"] and year and str(summary["year"]) != year:
        result.issues.append(f"ano {year} no .bib, {summary['year']} no registro")
    local = author_families(entry.fields.get("author", entry.fields.get("editor", "")))
    remote = [plain(str(a)) for a in (summary.get("authors") or [])]  # type: ignore[arg-type]
    # Records vary between "Zhang, Qingfu" and family-only names; match by family token.
    last = [n.split()[-1] for n in local if n]
    rast = [n.split()[-1] for n in remote if n]
    if last and rast and last[0] != rast[0]:
        result.issues.append(f"primeiro autor {last[0]!r} no .bib, {rast[0]!r} no registro")
    extra = sorted({t for t in last if t != "others"} - set(rast))
    if rast and extra:
        result.issues.append(f"autores do .bib ausentes no registro: {extra}")
    kinds = {str(u["type"]).lower() for u in summary["updated_by"]}  # type: ignore[union-attr]
    if "retraction" in kinds:
        result.status = "retracted"
    elif result.issues:
        result.status = "mismatch"
    elif kinds:
        result.status = "updated"
    else:
        result.status = "verified"


def search_candidate(entry: Entry) -> dict[str, object] | None:
    query = " ".join(
        part
        for part in (
            entry.fields.get("title", ""),
            first_author_family(entry.fields.get("author", "")),
        )
        if part
    )
    if not query:
        return None
    params = urllib.parse.urlencode(
        {"query.bibliographic": plain(query), "rows": 3, "select": "DOI,title,author,issued,type"}
    )
    if MAILTO:
        url = f"https://api.crossref.org/works?{params}&mailto={MAILTO}"
    else:
        url = f"https://api.crossref.org/works?{params}"
    items = http_json(url)["message"]["items"]
    best, best_ratio = None, 0.0
    for item in items:
        ratio = difflib.SequenceMatcher(
            a=plain(entry.fields.get("title", "")),
            b=plain((item.get("title") or [""])[0]),
        ).ratio()
        if ratio > best_ratio:
            best, best_ratio = item, ratio
    if not best:
        return None
    return {"doi": best.get("DOI"), "similarity": round(best_ratio, 3)} | record_summary(best)


def online_checks(entries: list[Entry], results: dict[str, Result], delay: float) -> None:
    for entry in entries:
        result = results[entry.key]
        try:
            if result.doi:
                record = remote_record(result.doi)
                if record is None:
                    registered = handle_exists(result.doi)
                    result.status = "not_found" if registered is False else "no_metadata"
                    result.issues.append(
                        f"DOI {result.doi} não está registrado no sistema DOI"
                        if registered is False
                        else f"DOI {result.doi} existe, mas sem metadados em Crossref/doi.org"
                    )
                else:
                    compare(entry, result, record_summary(record))
            else:
                candidate = search_candidate(entry)
                result.status = "no_doi"
                if candidate:
                    result.remote = {"candidate": candidate}
                    result.issues.append(
                        f"sem DOI; melhor candidato Crossref {candidate['doi']} (similaridade "
                        f"de título {candidate['similarity']}) — conferir antes de usar"
                    )
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
            result.status = "error"
            result.issues.append(f"consulta falhou: {error}")
        time.sleep(delay)


def cited_keys(aux: Path) -> set[str] | None:
    if not aux.is_file():
        return None
    keys: set[str] = set()
    for match in re.finditer(r"\\citation\{([^}]*)\}", aux.read_text(encoding="utf-8")):
        keys.update(k.strip() for k in match.group(1).split(",") if k.strip())
    keys.discard("*")
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB)
    parser.add_argument("--aux", type=Path, default=DEFAULT_AUX, help="build .aux for cited keys")
    parser.add_argument("--keys", default="", help="comma-separated keys to check (default: all)")
    parser.add_argument("--online", action="store_true", help="query Crossref/doi.org (network)")
    parser.add_argument("--delay", type=float, default=0.2, help="seconds between requests")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.bib.is_file():
        print(f"not found: {args.bib}", file=sys.stderr)
        return 1
    entries = parse_bib(args.bib.read_text(encoding="utf-8"))
    results = offline_checks(entries, cited_keys(args.aux))
    wanted = {k.strip() for k in args.keys.split(",") if k.strip()}
    if wanted:
        unknown = wanted - set(results)
        for key in sorted(unknown):
            results[key] = Result(key, "?", "missing", ["chave pedida não existe no .bib"])
        results = {k: v for k, v in results.items() if k in wanted}
        entries = [e for e in entries if e.key in wanted]
    unique = {e.key: e for e in entries}
    if args.online:
        online_checks(list(unique.values()), results, args.delay)

    ordered = sorted(
        results.values(), key=lambda r: (r.status in {"ok", "verified", "unused"}, r.key)
    )
    if args.json:
        print(json.dumps([asdict(r) for r in ordered], ensure_ascii=False, indent=2))
    else:
        for result in ordered:
            print(
                f"{result.status:10} {result.key}" + (f"  doi:{result.doi}" if result.doi else "")
            )
            for issue in result.issues:
                print(f"           - {issue}")
        tally = Counter(r.status for r in ordered)
        print("resumo: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    bad = {"missing", "not_found", "retracted", "mismatch"}
    return 1 if any(r.status in bad for r in ordered) else 0


if __name__ == "__main__":
    raise SystemExit(main())
