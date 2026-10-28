"""Transforma o texto digitado em uma lista de tokens."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .errors import InvalidExpressionError, OverflowCalcError

NUMBER = "NUMBER"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
POW = "POW"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
FACT = "FACT"
PERCENT = "PERCENT"
NAME = "NAME"
SQRT = "SQRT"
SEMI = "SEMI"


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    value: float | None = None


# Número com separador decimal "." ou "," e expoente opcional (1,5e+20).
# O expoente só vale se o "e" vier colado ao número e seguido de dígitos;
# caso contrário, o "e" é a constante de Euler (ex.: "2e" = 2 * e).
_NUMBER_RE = re.compile(r"(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?")
_NAME_RE = re.compile(r"[^\W\d_]+")

_SYMBOLS = {
    "+": PLUS,
    "-": MINUS,
    "−": MINUS,  # −
    "–": MINUS,  # –
    "*": MUL,
    "×": MUL,    # ×
    "·": MUL,    # ·
    "/": DIV,
    "÷": DIV,    # ÷
    "^": POW,
    "(": LPAREN,
    ")": RPAREN,
    "!": FACT,
    "%": PERCENT,
    "√": SQRT,   # √
    ";": SEMI,
}


def tokenize(expression: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(expression)
    while i < n:
        ch = expression[i]
        if ch.isspace():
            i += 1
            continue

        match = _NUMBER_RE.match(expression, i)
        if match:
            text = match.group()
            value = float(text.replace(",", "."))
            if math.isinf(value):
                raise OverflowCalcError()
            tokens.append(Token(NUMBER, text, value))
            i = match.end()
            continue

        if ch in _SYMBOLS:
            tokens.append(Token(_SYMBOLS[ch], ch))
            i += 1
            continue

        match = _NAME_RE.match(expression, i)
        if match:
            tokens.append(Token(NAME, match.group().lower()))
            i = match.end()
            continue

        raise InvalidExpressionError()
    return tokens
