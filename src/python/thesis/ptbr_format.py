"""Brazilian-Portuguese number formatting for dissertation tables.

Every number in the imported manuscript was typed by hand. That is the root
cause of the two defects the rewrite inherits: Table 6.3 used decimal commas
while Table 6.4 used periods, and two SPEA2 entries in Table 6.4 lost an order
of magnitude (``2.1642e-3`` for what the data say is ``2.1642e-1``).

A single formatter removes both failure modes at the source. Anything a
dissertation table prints goes through here, so the decimal separator cannot
drift between tables and no magnitude is ever retyped.

Math-mode note: in LaTeX math, a bare comma is punctuation and picks up a
trailing thin space, so ``3,14`` renders as ``3, 14``. Every function below
emits ``{,}`` instead, which is why the strings look odd in source.
"""

from __future__ import annotations

import math

__all__ = [
    "decimal",
    "integer",
    "median_iqr",
    "percent",
    "pvalue",
    "sci",
    "signed",
    "smart",
    "wtl",
]

# Below this magnitude (and at/above 1e4) fixed-point notation stops being
# readable in a table cell, so `smart` switches to scientific.
_SCI_LOW = 1e-2
_SCI_HIGH = 1e4


def _comma(text: str) -> str:
    """Swap the decimal point for a LaTeX-math-safe comma."""
    return text.replace(".", "{,}")


def decimal(value: float, places: int = 3) -> str:
    """Fixed-point in pt-BR, wrapped for math mode: ``0,754``."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    return f"${_comma(f'{value:.{places}f}')}$"


def integer(value: int) -> str:
    """Integer with pt-BR thousands separator (period): ``100.000``."""
    if value is None:
        return "---"
    return f"{int(value):,}".replace(",", ".")


def sci(value: float, sig: int = 3) -> str:
    r"""Scientific notation: ``$1{,}23 \times 10^{-3}$``."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    if value == 0:
        return "$0$"

    exponent = math.floor(math.log10(abs(value)))
    mantissa = value / (10.0**exponent)

    # Rounding can carry the mantissa to 10.0 (e.g. 9.999 at sig=3).
    rounded = round(mantissa, sig - 1)
    if abs(rounded) >= 10.0:
        rounded /= 10.0
        exponent += 1

    body = _comma(f"{rounded:.{sig - 1}f}")
    return rf"${body} \times 10^{{{exponent}}}$"


def smart(value: float, sig: int = 3, places: int = 3) -> str:
    """Scientific for very small/large magnitudes, fixed-point otherwise."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    if value != 0 and (abs(value) < _SCI_LOW or abs(value) >= _SCI_HIGH):
        return sci(value, sig=sig)
    return decimal(value, places=places)


def median_iqr(median: float, iqr: float, sig: int = 3) -> str:
    r"""Median with its IQR in parentheses, sharing one exponent.

    ``3,88(0,09) \times 10^{-3}``. Sharing the exponent is what makes a column
    of these comparable at a glance; formatting the IQR independently would
    print two different powers of ten in the same cell.
    """
    nan = (median is None or (isinstance(median, float) and math.isnan(median)))
    if nan:
        return "---"
    if median == 0:
        return f"$0({_comma(f'{iqr:.{sig - 1}f}')})$"

    exponent = math.floor(math.log10(abs(median)))
    m = median / (10.0**exponent)
    q = (iqr or 0.0) / (10.0**exponent)

    rounded = round(m, sig - 1)
    if abs(rounded) >= 10.0:
        rounded /= 10.0
        q /= 10.0
        exponent += 1

    body = _comma(f"{rounded:.{sig - 1}f}")
    spread = _comma(f"{q:.{sig - 1}f}")
    return rf"${body}({spread}) \times 10^{{{exponent}}}$"


def percent(value: float, places: int = 1) -> str:
    """Percentage, pt-BR: ``12,3\\%``."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    return f"${_comma(f'{value:.{places}f}')}$\\%"


def pvalue(p: float, threshold: float = 1e-3) -> str:
    """p-value, collapsing anything below ``threshold``."""
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return "---"
    if p < threshold:
        return f"$<{_comma(f'{threshold:g}')}$"
    if p < 0.01:
        return sci(p, sig=2)
    return decimal(p, places=3)


def signed(value: float, places: int = 3) -> str:
    """Fixed-point carrying an explicit sign, for deltas."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    sign = "+" if value >= 0 else "-"
    return f"${sign}{_comma(f'{abs(value):.{places}f}')}$"


def wtl(wins: int, ties: int, losses: int) -> str:
    """Win/tie/loss triple in the fixed order used throughout the text."""
    return f"{int(wins)}/{int(ties)}/{int(losses)}"
