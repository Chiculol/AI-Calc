"""Erros amigáveis do motor de cálculo, todos com mensagens em português."""

from __future__ import annotations


class CalcError(Exception):
    """Erro de cálculo com mensagem pronta para ser mostrada ao usuário."""

    default_message = "Erro de cálculo"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class DivisionByZeroError(CalcError):
    default_message = "Divisão por zero inválida"


class IndeterminateError(CalcError):
    default_message = "Indeterminação"


class DomainError(CalcError):
    default_message = "Valor fora do domínio"


class UndefinedError(CalcError):
    default_message = "Indefinida"


class OverflowCalcError(CalcError):
    default_message = "Resultado grande demais"


class FactorialLimitError(CalcError):
    default_message = "Fatorial limitado a 170"


class FactorialDomainError(CalcError):
    default_message = "Fatorial só vale para inteiros não negativos"


class IncompleteExpressionError(CalcError):
    default_message = "Expressão incompleta"


class ParenthesesError(CalcError):
    default_message = "Parênteses incorretos"


class InvalidExpressionError(CalcError):
    default_message = "Expressão inválida"


class UnexpectedError(CalcError):
    default_message = "Algo deu errado nesta conta"
