"""Test-suite path setup.

The scripts under ``src/python/analysis/`` are run as files
(``python src/python/analysis/X.py``), which puts their own directory on
``sys.path``. Importing them from a test needs the same directory available, so
each test module used to open with its own four-line preamble:

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "python", "analysis"))

Doing it once here removes that duplication, and with it the E402 the preamble
forced on every import below it.

``ivfspea2`` itself needs nothing: ``pip install -e .`` puts it on the path.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = PROJECT_ROOT / "src" / "python" / "analysis"

if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
