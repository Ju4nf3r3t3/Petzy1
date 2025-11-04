"""Currency helpers for formatting monetary values."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


_DECIMAL_QUANTIZE = Decimal("0.01")
_FALSEY_STRINGS = {"0", "false", "no", "off"}


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        return Decimal(str(value))

    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            raise InvalidOperation
        normalised = candidate.replace(",", ".")
        return Decimal(normalised)

    return Decimal(value)


def format_cop(value: Any, *, with_symbol: bool = True) -> str:
    """Return a human-readable representation in Colombian pesos.

    Numbers are formatted with a period as thousands separator and a comma as
    decimal separator (e.g. ``$ 12.345,67``). Trailing decimal zeros are
    omitted.
    """

    if value in (None, ""):
        return ""

    try:
        amount = _to_decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return str(value)

    quantized = amount.quantize(_DECIMAL_QUANTIZE, rounding=ROUND_HALF_UP)
    sign = "-" if quantized < 0 else ""
    absolute = quantized.copy_abs()

    integer_part, fractional_part = f"{absolute:.2f}".split(".")
    integer_number = int(integer_part)
    integer_with_sep = f"{integer_number:,}".replace(",", ".")

    if fractional_part == "00":
        formatted = integer_with_sep
    else:
        formatted = f"{integer_with_sep},{fractional_part}"

    result = f"{sign}{formatted}"
    if with_symbol:
        return f"$ {result}"
    return result


def should_include_symbol(flag: Any) -> bool:
    """Utility to coerce template arguments into booleans."""

    if isinstance(flag, str):
        return flag.strip().lower() not in _FALSEY_STRINGS
    return bool(flag)
