"""Testes do ponto 6: erros amigáveis (a calculadora nunca quebra)."""

import random

import pytest

from ai_calc.core import (
    CalcError,
    DivisionByZeroError,
    DomainError,
    IncompleteExpressionError,
    IndeterminateError,
    InvalidExpressionError,
    OverflowCalcError,
    ParenthesesError,
    UndefinedError,
    UnexpectedError,
    calculate,
)
import ai_calc.core.calculator as modulo_calculadora


@pytest.mark.parametrize(
    "expressao, modo, classe, mensagem",
    [
        # T02 e divisão por zero
        ("5 / 0", "DEG", DivisionByZeroError, "Divisão por zero inválida"),
        ("1/(0)", "DEG", DivisionByZeroError, "Divisão por zero inválida"),
        ("0^(-1)", "DEG", DivisionByZeroError, "Divisão por zero inválida"),
        ("raiz(-1; 0)", "DEG", DivisionByZeroError, "Divisão por zero inválida"),
        ("raiz(0; 8)", "DEG", DomainError, "Valor fora do domínio"),
        # indeterminações
        ("0 / 0", "DEG", IndeterminateError, "Indeterminação"),
        ("0^0", "DEG", IndeterminateError, "Indeterminação"),
        # domínio
        ("sqrt(-4)", "DEG", DomainError, "Valor fora do domínio"),
        ("√(-4)", "DEG", DomainError, "Valor fora do domínio"),
        ("ln(0)", "DEG", DomainError, "Valor fora do domínio"),
        ("ln(-1)", "DEG", DomainError, "Valor fora do domínio"),
        ("log(0)", "DEG", DomainError, "Valor fora do domínio"),
        ("asin(2)", "DEG", DomainError, "Valor fora do domínio"),
        ("acos(-1,5)", "DEG", DomainError, "Valor fora do domínio"),
        ("(-8)^(1/3)", "DEG", DomainError, "Valor fora do domínio"),
        ("raiz(2; -4)", "DEG", DomainError, "Valor fora do domínio"),
        # tangente indefinida
        ("tan(90)", "DEG", UndefinedError, "Indefinida"),
        ("tan(270)", "DEG", UndefinedError, "Indefinida"),
        ("tan(-90)", "DEG", UndefinedError, "Indefinida"),
        ("tan(450)", "DEG", UndefinedError, "Indefinida"),
        ("tan(90 + 360 * 1000000)", "DEG", UndefinedError, "Indefinida"),
        ("tan(pi/2)", "RAD", UndefinedError, "Indefinida"),
        ("tan(3 * pi / 2)", "RAD", UndefinedError, "Indefinida"),
        # estouro
        ("10^400", "DEG", OverflowCalcError, "Resultado grande demais"),
        ("10^308 * 10", "DEG", OverflowCalcError, "Resultado grande demais"),
        ("1e999", "DEG", OverflowCalcError, "Resultado grande demais"),
        # sintaxe
        ("2 +", "DEG", IncompleteExpressionError, "Expressão incompleta"),
        ("2 *", "DEG", IncompleteExpressionError, "Expressão incompleta"),
        ("", "DEG", IncompleteExpressionError, "Expressão incompleta"),
        ("   ", "DEG", IncompleteExpressionError, "Expressão incompleta"),
        ("sin(", "DEG", IncompleteExpressionError, "Expressão incompleta"),
        ("(2 + 3", "DEG", ParenthesesError, "Parênteses incorretos"),
        ("2 + 3)", "DEG", ParenthesesError, "Parênteses incorretos"),
        ("()", "DEG", ParenthesesError, "Parênteses incorretos"),
        ("sin(30", "DEG", ParenthesesError, "Parênteses incorretos"),
        ("abc", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("2 $ 3", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("2 +* 3", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("*3", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("1.2.3", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("sin(1; 2)", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("raiz(3)", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("(2; 3)", "DEG", InvalidExpressionError, "Expressão inválida"),
        ("a" * 501, "DEG", InvalidExpressionError, "Expressão longa demais"),
    ],
)
def test_mensagens_de_erro(expressao, modo, classe, mensagem):
    with pytest.raises(classe) as erro:
        calculate(expressao, modo)
    assert erro.value.message == mensagem


def test_erro_inesperado_vira_mensagem_amigavel(monkeypatch):
    def quebrado(*args, **kwargs):
        raise RuntimeError("falha interna")

    monkeypatch.setattr(modulo_calculadora, "evaluate", quebrado)
    with pytest.raises(UnexpectedError) as erro:
        calculate("1 + 1")
    assert erro.value.message == "Algo deu errado nesta conta"


def test_parenteses_muito_aninhados_nao_quebram():
    expressao = "(" * 200 + "1" + ")" * 200
    try:
        calculate(expressao)
    except CalcError:
        pass  # erro amigável também é aceitável; o que não pode é estourar


def test_robustez_com_entradas_aleatorias():
    """Nenhuma entrada pode levantar algo que não seja CalcError."""
    sorteio = random.Random(42)
    alfabeto = list("0123456789+-*/^()!%;., ") + ["pi", "e", "sin", "cos", "tan",
        "ln", "log", "sqrt", "raiz", "abs", "asin", "√", "×", "÷", "−", "π", "x", "@"]
    for _ in range(4000):
        tamanho = sorteio.randint(0, 14)
        expressao = "".join(sorteio.choice(alfabeto) for _ in range(tamanho))
        for modo in ("DEG", "RAD"):
            try:
                calculate(expressao, modo)
            except CalcError:
                pass
