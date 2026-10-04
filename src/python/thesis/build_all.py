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
    "build_tab_posicionamento.py",
    "build_tab_geometria_confirmatoria.py",
    "build_tab_magnitude_confirmatoria.py",
    "build_tab_ativacao_robustez.py",
    "build_tab_wfg_exploratoria.py",
    "build_fig_resultados.py",
    "build_fig_complementares.py",
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
    """Copy generated tables and figures into the thesis build directory."""
    ensure_dir(THESIS_GENERATED)
    count = 0
    for source in sorted(RESULTS_THESIS.glob("*.tex")):
        shutil.copyfile(source, THESIS_GENERATED / source.name)
        count += 1
    figures = RESULTS_THESIS / "figures"
    if figures.is_dir():
        target = ensure_dir(THESIS_GENERATED / "figures")
        for source in sorted(figures.glob("*.pdf")):
            shutil.copyfile(source, target / source.name)
            count += 1
    print(f"espelhados {count} arquivos em thesis/masters/generated/")
    return count


def _snapshot() -> dict[str, bytes]:
    """Bytes of every canonical artifact, tables and figures alike."""
    snapshot = {p.name: p.read_bytes() for p in RESULTS_THESIS.glob("*.tex")}
    for path in (RESULTS_THESIS / "figures").glob("*.pdf"):
        snapshot[f"figures/{path.name}"] = path.read_bytes()
    return snapshot


def check_drift() -> int:
    """Rebuild and report any artifact whose bytes changed. Returns exit code."""
    before = _snapshot()
    failed = run_builders()
    if failed:
        print(f"\nERRO: construtores falharam: {', '.join(failed)}", file=sys.stderr)
        return 1

    after = _snapshot()
    drifted = sorted(
        name for name in set(before) | set(after) if before.get(name) != after.get(name)
    )
    if drifted:
        print("\nERRO: artefatos fora de sincronia com os dados:", file=sys.stderr)
        for name in drifted:
            print(f"  {name}", file=sys.stderr)
        print("Rode: make thesis-tables", file=sys.stderr)
        return 1
    print("\nOK: tabelas e figuras estão sincronizadas com os artefatos.")
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
