"""Operações de porcentagem para o painel de porcentagem (Etapa 6A).

Fornece funções numéricas puras independentes da sintaxe da calculadora:
- part_of_total: fração que a parte representa do total (part / total)
- percentage_change: taxa de variação relativa ((final - initial) / initial)
- original_before_discount: valor original antes do desconto (final / (1 - discount_rate))
"""

from __future__ import annotations

import math

from .errors import CalcError, DivisionByZeroError, DomainError, OverflowCalcError


def _ensure_finite(value: float) -> float:
    """Valida se o valor é numérico e finito.

    Levanta OverflowCalcError se for infinito ou NaN.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise OverflowCalcError()
    return float(value)


def part_of_total(part: float, total: float) -> float:
    """Calcula a taxa em fração decimal que a parte representa do total (part / total).

    Exemplos:
        part_of_total(36, 240) -> 0.15 (15%)
        part_of_total(120, 100) -> 1.2 (120%)
    """
    _part = _ensure_finite(part)
    _total = _ensure_finite(total)

    if _total == 0.0:
        raise DivisionByZeroError()

    try:
        result = _part / _total
    except OverflowError:
        raise OverflowCalcError() from None

    if not math.isfinite(result):
        raise OverflowCalcError()

    return float(result)


def percentage_change(initial: float, final: float) -> float:
    """Calcula a variação percentual relativa (final - initial) / initial.

    Exemplos:
        percentage_change(240, 204) -> -0.15 (-15%)
        percentage_change(100, 0) -> -1.0 (-100%)
    """
    _initial = _ensure_finite(initial)
    _final = _ensure_finite(final)

    if _initial == 0.0:
        raise DivisionByZeroError()

    try:
        result = (_final - _initial) / _initial
    except OverflowError:
        raise OverflowCalcError() from None

    if not math.isfinite(result):
        raise OverflowCalcError()

    return float(result)


def original_before_discount(final: float, discount_rate: float) -> float:
    """Calcula o valor original antes do desconto (final / (1 - discount_rate)).

    A taxa discount_rate deve estar no intervalo [0, 1) em fração decimal
    (ex.: 0.25 para 25%).

    Exemplos:
        original_before_discount(150, 0.25) -> 200.0
        original_before_discount(150, 0) -> 150.0
    """
    _final = _ensure_finite(final)
    _rate = _ensure_finite(discount_rate)

    if not (0.0 <= _rate < 1.0):
        raise DomainError()

    try:
        denom = 1.0 - _rate
        if denom == 0.0:
            raise OverflowCalcError()
        result = _final / denom
    except OverflowError:
        raise OverflowCalcError() from None

    if not math.isfinite(result):
        raise OverflowCalcError()

    return float(result)


__all__ = [
    "original_before_discount",
    "part_of_total",
    "percentage_change",
]
