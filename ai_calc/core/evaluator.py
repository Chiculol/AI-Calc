"""Calcula o valor de uma árvore de expressão."""

from __future__ import annotations

import math

from . import trig
from .ast_nodes import Binary, Const, Func, Group, Node, Number, Postfix, Sqrt, Unary
from .errors import (
    DivisionByZeroError,
    DomainError,
    FactorialDomainError,
    FactorialLimitError,
    IndeterminateError,
    OverflowCalcError,
)
from .limits import ANGLE_MODES, INTEGER_TOLERANCE, MAX_FACTORIAL


def evaluate(node: Node, angle_mode: str = "DEG") -> float:
    if angle_mode not in ANGLE_MODES:
        raise ValueError(f"Modo angular inválido: {angle_mode!r}")
    return _eval(node, angle_mode)


# --- utilidades -----------------------------------------------------------
def _finite(value: float) -> float:
    if math.isinf(value) or math.isnan(value):
        raise OverflowCalcError()
    return value


def _is_integer(x: float) -> bool:
    return abs(x - round(x)) < INTEGER_TOLERANCE


def _divide(left: float, right: float) -> float:
    if right == 0:
        if left == 0:
            raise IndeterminateError()
        raise DivisionByZeroError()
    return _finite(left / right)


def _power(base: float, exponent: float) -> float:
    if base == 0:
        if exponent == 0:
            raise IndeterminateError()
        if exponent < 0:
            raise DivisionByZeroError()
        return 0.0
    if base < 0:
        if not _is_integer(exponent):
            raise DomainError()
        exponent = float(round(exponent))
    try:
        return _finite(math.pow(base, exponent))
    except OverflowError:
        raise OverflowCalcError() from None
    except ValueError:
        raise DomainError() from None


def _factorial(x: float) -> float:
    if not _is_integer(x):
        raise FactorialDomainError()
    n = round(x)
    if n < 0:
        raise FactorialDomainError()
    if n > MAX_FACTORIAL:
        raise FactorialLimitError()
    return float(math.factorial(n))


def _nth_root(index: float, radicand: float) -> float:
    if index == 0:
        raise DomainError()
    if radicand < 0:
        # raiz real de número negativo só existe com índice inteiro ímpar
        if _is_integer(index) and round(index) % 2 != 0:
            return -_power(-radicand, 1.0 / round(index))
        raise DomainError()
    return _power(radicand, 1.0 / index)


def _call(name: str, args: list[float], mode: str) -> float:
    if name == "raiz":
        return _nth_root(args[0], args[1])

    x = args[0]
    if name == "sin":
        return trig.sin(x, mode)
    if name == "cos":
        return trig.cos(x, mode)
    if name == "tan":
        return trig.tan(x, mode)
    if name == "asin":
        return trig.asin(x, mode)
    if name == "acos":
        return trig.acos(x, mode)
    if name == "atan":
        return trig.atan(x, mode)
    if name == "ln":
        if x <= 0:
            raise DomainError()
        return math.log(x)
    if name == "log":
        if x <= 0:
            raise DomainError()
        return math.log10(x)
    if name == "sqrt":
        if x < 0:
            raise DomainError()
        return math.sqrt(x)
    if name == "abs":
        return abs(x)
    raise DomainError()


# --- avaliação ------------------------------------------------------------
def _eval(node: Node, mode: str) -> float:
    if isinstance(node, Number):
        return node.value

    if isinstance(node, Const):
        return math.pi if node.name == "pi" else math.e

    if isinstance(node, Group):
        return _eval(node.expr, mode)

    if isinstance(node, Unary):
        value = _eval(node.operand, mode)
        return -value if node.op == "-" else value

    if isinstance(node, Postfix):
        value = _eval(node.operand, mode)
        if node.op == "!":
            return _factorial(value)
        return value / 100.0

    if isinstance(node, Sqrt):
        value = _eval(node.operand, mode)
        if value < 0:
            raise DomainError()
        return math.sqrt(value)

    if isinstance(node, Func):
        args = [_eval(arg, mode) for arg in node.args]
        return _finite(_call(node.name, args, mode))

    if isinstance(node, Binary):
        return _eval_binary(node, mode)

    raise TypeError(f"Nó desconhecido: {node!r}")


def _eval_binary(node: Binary, mode: str) -> float:
    op = node.op

    # Regra da porcentagem: em A + B% e A - B%, o B% é uma fração de A.
    # Só vale quando o "%" é o termo inteiro à direita (sem parênteses).
    if op in ("+", "-") and isinstance(node.right, Postfix) and node.right.op == "%":
        base = _eval(node.left, mode)
        percent = _eval(node.right.operand, mode)
        delta = base * percent / 100.0
        return _finite(base + delta if op == "+" else base - delta)

    left = _eval(node.left, mode)
    right = _eval(node.right, mode)

    if op == "+":
        return _finite(left + right)
    if op == "-":
        return _finite(left - right)
    if op == "*":
        return _finite(left * right)
    if op == "/":
        return _divide(left, right)
    if op == "^":
        return _power(left, right)
    raise TypeError(f"Operador desconhecido: {op!r}")
