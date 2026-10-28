"""Ponto de entrada do motor de cálculo."""

from __future__ import annotations

import logging
from dataclasses import dataclass, fields

from .ast_nodes import Func
from .errors import CalcError, InvalidExpressionError, UnexpectedError
from .evaluator import evaluate
from .formatting import format_number
from .limits import MAX_EXPRESSION_LENGTH
from .parser import parse
from .render import contains_implicit, to_text
from .tokenizer import tokenize

logger = logging.getLogger(__name__)

TRIG_FUNCTIONS = frozenset({"sin", "cos", "tan", "asin", "acos", "atan"})


@dataclass(frozen=True)
class CalcResult:
    value: float            # valor numérico calculado
    text: str               # valor formatado para exibição (pt-BR)
    interpreted: str | None  # expressão com os "×" inseridos; None se não houve nenhum
    expression: str         # expressão original
    uses_trig: bool = False  # True se a conta usou seno, cosseno ou tangente (ou inversas)


def uses_trig(node) -> bool:
    """True se a árvore tem alguma função trigonométrica (o modo DEG/RAD importa)."""
    if isinstance(node, Func) and node.name in TRIG_FUNCTIONS:
        return True
    if isinstance(node, tuple):
        return any(uses_trig(item) for item in node)
    if hasattr(node, "__dataclass_fields__"):
        return any(uses_trig(getattr(node, f.name)) for f in fields(node))
    return False


def calculate(expression: str, angle_mode: str = "DEG") -> CalcResult:
    """Calcula uma expressão.

    Levanta apenas CalcError (com mensagem amigável em português); qualquer
    falha inesperada é convertida em UnexpectedError.
    """
    try:
        if len(expression) > MAX_EXPRESSION_LENGTH:
            raise InvalidExpressionError("Expressão longa demais")
        tree = parse(tokenize(expression))
        value = evaluate(tree, angle_mode)
        text = format_number(value)
        interpreted = to_text(tree) if contains_implicit(tree) else None
        return CalcResult(value, text, interpreted, expression, uses_trig(tree))
    except CalcError:
        raise
    except RecursionError:
        raise InvalidExpressionError() from None
    except ValueError:
        # modo angular inválido é erro de programação, não do usuário
        raise
    except Exception:  # rede de segurança: o app nunca deve fechar por causa de uma conta
        logger.exception("Erro inesperado ao calcular %r", expression)
        raise UnexpectedError() from None
