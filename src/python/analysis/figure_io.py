"""Deprecated shim — import from :mod:`ivfspea2.figio` instead.

The implementation moved into the installable package. Eight scripts import this
module bare (``from figure_io import save_figure``), which works because they are
run as ``python src/python/analysis/X.py`` and so get this directory on
``sys.path[0]``. Keeping the shim meant none of them had to change.

New code should import ``ivfspea2.figio`` directly.
"""

from ivfspea2.figio import DETERMINISTIC_PDF_METADATA, save_figure  # noqa: F401

__all__ = ["DETERMINISTIC_PDF_METADATA", "save_figure"]
