"""Shared figure-writing helper for the analysis scripts.

Figures under ``paper/*/figures/`` are tracked in git, so a rebuild that only
changes the embedded timestamp shows up as a diff and dirties the working tree.
Passing ``CreationDate: None`` drops the key from the PDF info dictionary
altogether (the pdf backend filters ``None`` entries), which makes repeated runs
byte-identical as long as the data and the matplotlib version are unchanged.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from matplotlib.figure import Figure


# Note that ``Creator`` and ``Producer`` still carry the matplotlib version, so
# upgrading matplotlib does rewrite every figure once.
DETERMINISTIC_PDF_METADATA = {"CreationDate": None}


def save_figure(
    fig: "Figure",
    name: str,
    out_dirs: Iterable[str | os.PathLike[str]],
    *,
    dpi: float | None = 300,
    log_prefix: str = "",
) -> None:
    """Write ``fig`` as ``name`` into every directory in ``out_dirs``.

    ``dpi=None`` defers to ``savefig.dpi`` exactly as omitting the argument does.
    """
    for out_dir in out_dirs:
        directory = Path(out_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        fig.savefig(
            path,
            bbox_inches="tight",
            dpi=dpi,
            metadata=DETERMINISTIC_PDF_METADATA,
        )
        print(f"{log_prefix}Wrote {path}")
