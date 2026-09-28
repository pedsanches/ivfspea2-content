"""Brazilian-Portuguese number formatting for dissertation tables and figures.

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
    "axis_formatter",
    "decimal",
    "exponent",
    "integer",
    "percent",
    "plain",
    "power_of_ten",
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


def exponent(*values: float, sig: int = 4) -> int:
    """Power of ten that puts the largest ``|value|`` in ``[1, 10)`` at ``sig`` digits.

    A per-instance row prints both algorithms' medians and spreads against one
    power of ten, so the row is read in one scale. The power is taken from the
    largest value, after rounding, so a mantissa never prints as ``10,000``.
    """
    largest = max(abs(value) for value in values)
    if largest == 0:
        return 0
    power = math.floor(math.log10(largest))
    if round(largest / 10.0**power, sig - 1) >= 10.0:
        power += 1
    return power


def power_of_ten(power: int) -> str:
    """``$10^{-3}$``: the scale printed beside a row of mantissas."""
    return rf"$10^{{{power}}}$"


def percent(value: float, places: int = 1) -> str:
    """Percentage, pt-BR: ``12,3\\%``."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    return f"${_comma(f'{value:.{places}f}')}$\\%"


def pvalue(p: float, threshold: float = 1e-3, places: int = 3) -> str:
    """p-value in fixed point, three decimals by default, floored at ``threshold``.

    One notation per column: the scientific form this used below 0,01 put
    ``2,0 \\times 10^{-3}`` between ``< 0,001`` and ``0,042`` in the same column,
    so the decimal commas no longer lined up. Three decimals resolve every
    decision at 0,05; a table that also prints adjusted values from the same
    p-values asks for four, so the adjustment can be followed digit by digit.
    Anything below ``threshold`` prints as ``< 0,001``.
    """
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return "---"
    if p < threshold:
        return f"$<{_comma(f'{threshold:g}')}$"
    return decimal(p, places=places)


def signed(value: float, places: int = 3) -> str:
    """Fixed-point carrying an explicit sign, for deltas.

    A value that rounds to zero prints unsigned: ``+0,00`` or ``-0,00`` would
    claim a direction the printed digits do not show.
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "---"
    digits = f"{abs(value):.{places}f}"
    if float(digits) == 0:
        return f"${_comma(digits)}$"
    sign = "+" if value > 0 else "-"
    return f"${sign}{_comma(digits)}$"


def wtl(wins: int, ties: int, losses: int) -> str:
    """Win/tie/loss triple in the fixed order used throughout the text."""
    return f"{int(wins)}/{int(ties)}/{int(losses)}"


def plain(value: float, places: int = 2) -> str:
    """Fixed-point text for figure labels, outside math mode: ``0,216``."""
    return f"{value:.{places}f}".replace(".", ",")


def axis_formatter():
    """Matplotlib tick formatter that prints the pt-BR decimal comma.

    It keeps ``ScalarFormatter``'s choice of ticks and decimals and only swaps
    the separator, so every figure axis agrees with the tables and the text.
    Matplotlib is imported lazily: the table builders share this module and
    never need it.
    """
    from matplotlib.ticker import ScalarFormatter

    class _CommaFormatter(ScalarFormatter):
        def __call__(self, x, pos=None):
            return super().__call__(x, pos).replace(".", ",")

    return _CommaFormatter()
