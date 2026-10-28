"""Leitura dos campos da aba Trigonometria e o resumo falado do círculo.

Fica separado de trig.py porque usa o motor de cálculo (que por sua vez usa trig.py).
"""

from __future__ import annotations

from .calculator import calculate
from .errors import DomainError, IncompleteExpressionError
from .formatting import format_number
from .trig import TrigCircleState, normalize_degrees, to_degrees

MODE_NAMES = {"DEG": "graus", "RAD": "radianos"}


def angle_from_text(text: str, mode: str = "DEG") -> float:
    """Ângulo digitado (aceita contas: 450, -30, π/6...) convertido para graus em [0°, 360°).

    O número vale no modo atual: em RAD, "π/6" é 30°. Levanta CalcError se a conta
    for inválida.
    """
    if not text.strip():
        raise IncompleteExpressionError()
    value = calculate(text, mode).value
    return normalize_degrees(to_degrees(value, mode))


def sine_from_text(text: str, mode: str = "DEG") -> float:
    """Valor do seno digitado (aceita contas como 1/2 ou √3/2). Fora de [-1, 1]: DomainError."""
    if not text.strip():
        raise IncompleteExpressionError()
    value = calculate(text, mode).value
    if not -1 - 1e-12 <= value <= 1 + 1e-12:
        raise DomainError()
    return max(-1.0, min(1.0, value))


def describe(state: TrigCircleState, mode: str = "DEG") -> str:
    """Resumo para leitor de tela: "Ângulo 30 graus, 1º quadrante, seno 0,5, ..."."""
    sine, cosine, tangent = state.values
    angle = format_number(state.angle_in(mode))
    tangent_text = "indefinida" if tangent is None else format_number(tangent)
    place = state.quadrant_label
    place = place[0].lower() + place[1:]          # "Sobre o eixo" no meio da frase
    return (
        f"Ângulo {angle} {MODE_NAMES[mode]}, {place}, "
        f"seno {format_number(sine)}, cosseno {format_number(cosine)}, tangente {tangent_text}"
    )
