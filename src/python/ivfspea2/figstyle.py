"""One matplotlib style for the project, applied by importing this module.

Two problems this replaces.

**The backend dance.** 36 scripts open with::

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt      # E402: module import not at top of file

The ``use()`` call has to precede the pyplot import, so the pyplot import cannot
be at the top, so every one of those files carries a lint error that can only be
silenced. Importing this module *is* a top-of-file import and does the same job::

    from ivfspea2 import figstyle        # sets the backend as a side effect
    import matplotlib.pyplot as plt

**Seventeen drifted rcParams blocks.** They disagreed on the things that decide
whether figures look like one paper: ``font.family`` was serif in 13 and
sans-serif in 3; ``font.size`` was 8 in 12 and 9 or 10 elsewhere;
``axes.labelsize`` was 9 in seven and 8 in five; five different ``sns.set_*``
calls. ``PAPER_RC`` settles each by majority, except ``pdf.fonttype``.

``pdf.fonttype: 42`` embeds TrueType rather than Type-3 fonts. Only 2 of the 17
blocks set it, so most committed figures carry Type-3, which several publishers
reject outright. That is a real defect, but fixing it rewrites the bytes of
camera-ready figures for an accepted paper — so this module makes the correct
setting available without applying it to anything retroactively. Adopt it when
regenerating a figure deliberately, with a fresh checksum pass.
"""

from __future__ import annotations

import os

import matplotlib

# force=False leaves an already-chosen backend alone, so importing this module
# cannot break an interactive session or a notebook.
matplotlib.use(os.environ.get("IVFSPEA2_MPL_BACKEND", "Agg"), force=False)

PAPER_RC: dict[str, object] = {
    "font.family": "serif",
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "axes.grid": True,
    "grid.linestyle": ":",
    "grid.alpha": 0.4,
}

SLIDE_RC: dict[str, object] = {
    **PAPER_RC,
    "font.family": "sans-serif",
    "font.size": 12,
    "axes.labelsize": 13,
    "axes.titlesize": 14,
    "legend.fontsize": 11,
}

_CONTEXTS = {"paper": PAPER_RC, "slide": SLIDE_RC}


def apply_paper_style(context: str = "paper") -> None:
    """Apply the project rcParams and the single canonical seaborn theme."""
    try:
        rc = _CONTEXTS[context]
    except KeyError:
        raise ValueError(
            f"unknown context {context!r}; expected one of {sorted(_CONTEXTS)}"
        ) from None

    try:
        import seaborn as sns
    except ImportError:
        pass
    else:
        sns.set_theme(style="whitegrid", rc={})

    matplotlib.pyplot.rcParams.update(rc)


__all__ = ["PAPER_RC", "SLIDE_RC", "apply_paper_style"]
