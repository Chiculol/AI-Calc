"""Motor de cálculo do AI Calc (sem nenhuma dependência de interface)."""

from .calculator import CalcResult, calculate
from .errors import (
    CalcError,
    DivisionByZeroError,
    DomainError,
    FactorialDomainError,
    FactorialLimitError,
    IncompleteExpressionError,
    IndeterminateError,
    InvalidExpressionError,
    OverflowCalcError,
    ParenthesesError,
    UndefinedError,
    UnexpectedError,
)
from .formatting import format_number
from .trig import TrigCircleState, TrigSigns

__all__ = [
    "CalcError",
    "CalcResult",
    "DivisionByZeroError",
    "DomainError",
    "FactorialDomainError",
    "FactorialLimitError",
    "IncompleteExpressionError",
    "IndeterminateError",
    "InvalidExpressionError",
    "OverflowCalcError",
    "ParenthesesError",
    "TrigCircleState",
    "TrigSigns",
    "UndefinedError",
    "UnexpectedError",
    "calculate",
    "format_number",
]
