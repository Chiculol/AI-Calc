"""Nós da árvore de expressão."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Number:
    value: float
    text: str


@dataclass(frozen=True)
class Const:
    name: str  # "pi" ou "e"


@dataclass(frozen=True)
class Group:
    expr: "Node"


@dataclass(frozen=True)
class Unary:
    op: str  # "+" ou "-"
    operand: "Node"


@dataclass(frozen=True)
class Binary:
    op: str  # "+", "-", "*", "/", "^"
    left: "Node"
    right: "Node"
    implicit: bool = False  # multiplicação inserida pelo app


@dataclass(frozen=True)
class Postfix:
    op: str  # "!" ou "%"
    operand: "Node"


@dataclass(frozen=True)
class Func:
    name: str
    args: tuple


@dataclass(frozen=True)
class Sqrt:
    operand: "Node"


Node = Union[Number, Const, Group, Unary, Binary, Postfix, Func, Sqrt]
