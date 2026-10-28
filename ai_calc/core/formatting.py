"""Formata números para exibição (pt-BR, 12 dígitos significativos)."""

from __future__ import annotations

import math
from decimal import Decimal

from .errors import OverflowCalcError
from .limits import (
    SCIENTIFIC_LOWER_EXPONENT,
    SCIENTIFIC_UPPER_EXPONENT,
    SIGNIFICANT_DIGITS,
)


def _trim(text: str) -> str:
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_number(value: float) -> str:
    """Devolve o número arredondado, com vírgula decimal.

    Entre 10^-6 e 10^12 usa notação comum; fora disso, notação científica
    (ex.: 1e+12, 1,5e+20, 2,5e-9).
    """
    if math.isnan(value) or math.isinf(value):
        raise OverflowCalcError()
    if value == 0:
        return "0"

    sign = "-" if value < 0 else ""
    mantissa, exponent_text = f"{abs(value):.{SIGNIFICANT_DIGITS - 1}e}".split("e")
    exponent = int(exponent_text)

    if SCIENTIFIC_LOWER_EXPONENT <= exponent < SCIENTIFIC_UPPER_EXPONENT:
        body = _trim(format(Decimal(mantissa).scaleb(exponent), "f"))
    else:
        body = f"{_trim(mantissa)}e{'+' if exponent >= 0 else '-'}{abs(exponent)}"

    return sign + body.replace(".", ",")
