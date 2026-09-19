#!/usr/bin/env python3
"""Run every dissertation table builder, then mirror into the build directory.

Canonical outputs live in ``results/thesis/`` and are committed. Tectonic runs
with its working directory at ``thesis/masters/``, so the compile-time copies
go to ``thesis/masters/generated/``, which the thesis README reserves for
exactly this and which Git ignores. Chapters then ``\\input{generated/<name>}``
with no parent-directory traversal.

Usage:
    .venv/bin/python src/python/thesis/build_all.py           # build + mirror
    .venv/bin/python src/python/thesis/build_all.py --check   # fail on drift
"""

from __future__ import annotations

import argparse
import runpy
import shutil
import sys
from pathlib import Path

from ivfspea2.paths import RESULTS_THESIS, THESIS_GENERATED, ensure_dir

BUILDERS = [
    "build_tab_confirmatorio.py",
    "build_tab_por_instancia.py",
    "build_tab_hosts.py",
    "build_tab_engenharia.py",
    "build_tab_tuning_ablacao.py",
    "build_tab_fla_dinamica.py",
    "build_tab_controlador.py",
    "build_apendice_fontes.py",
]

HERE = Path(__file__).resolve().parent


def run_builders() -> list[str]:
    """Run each builder in-process. Returns the names that failed."""
    failed: list[str] = []
    for builder in BUILDERS:
        print(f"[{builder}]")
        try:
            runpy.run_path(str(HERE / builder), run_name="__main__")
        except SystemExit as exit_signal:
            if exit_signal.code:
                failed.append(builder)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"  FALHOU: {exc}", file=sys.stderr)
            failed.append(builder)
    return failed


def mirror() -> int:
    """Copy generated tables into the thesis build directory."""
    ensure_dir(THESIS_GENERATED)
    count = 0
    for source in sorted(RESULTS_THESIS.glob("*.tex")):
        shutil.copyfile(source, THESIS_GENERATED / source.name)
        count += 1
    print(f"espelhados {count} arquivos em thesis/masters/generated/")
    return count


def check_drift() -> int:
    """Rebuild and report any table whose bytes changed. Returns exit code."""
    before = {p.name: p.read_bytes() for p in RESULTS_THESIS.glob("*.tex")}
    failed = run_builders()
    if failed:
        print(f"\nERRO: construtores falharam: {', '.join(failed)}", file=sys.stderr)
        return 1

    after = {p.name: p.read_bytes() for p in RESULTS_THESIS.glob("*.tex")}
    drifted = sorted(
        name for name in set(before) | set(after) if before.get(name) != after.get(name)
    )
    if drifted:
        print("\nERRO: tabelas fora de sincronia com os artefatos:", file=sys.stderr)
        for name in drifted:
            print(f"  {name}", file=sys.stderr)
        print("Rode: make thesis-tables", file=sys.stderr)
        return 1
    print("\nOK: todas as tabelas estão sincronizadas com os artefatos.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="rebuild and fail if any committed table would change",
    )
    args = parser.parse_args()

    if args.check:
        return check_drift()

    failed = run_builders()
    mirror()
    if failed:
        print(f"\nERRO: construtores falharam: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("\nOK: todas as tabelas foram geradas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
