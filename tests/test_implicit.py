"""Testes do ponto 7: multiplicação implícita e linha 'Interpretado como'."""

import math

import pytest

from ai_calc.core import InvalidExpressionError, calculate


@pytest.mark.parametrize(
    "expressao, esperado, interpretado",
    [
        ("2pi", "6,28318530718", "2 × π"),
        ("2π", "6,28318530718", "2 × π"),
        ("3(4+5)", "27", "3 × (4 + 5)"),
        ("(1+2)(3+4)", "21", "(1 + 2) × (3 + 4)"),
        ("2sin(30)", "1", "2 × sin(30)"),
        ("1/2pi", "1,57079632679", "1 ÷ 2 × π"),   # (1/2) * pi
        ("2pi^2", "19,7392088022", "2 × π^2"),
        ("2√9", "6", "2 × √9"),
        ("√4pi", "6,28318530718", "√4 × π"),        # (√4) * pi
        ("2e", "5,43656365692", "2 × e"),
        ("50%(2)", "1", "50% × (2)"),
        ("5!(2)", "240", "5! × (2)"),
        ("2(3)(4)", "24", "2 × (3) × (4)"),
    ],
)
def test_multiplicacao_implicita(expressao, esperado, interpretado):
    resultado = calculate(expressao)
    assert resultado.text == esperado
    assert resultado.interpreted == interpretado


@pytest.mark.parametrize(
    "expressao",
    ["2*3", "2 + 3", "-2^2", "2e3", "sqrt(4)", "(1+2)*3", "5!"],
)
def test_sem_linha_interpretada_quando_nao_ha_multiplicacao_implicita(expressao):
    assert calculate(expressao).interpreted is None


def test_expoente_colado_ao_numero_e_literal():
    assert calculate("2e3").text == "2000"
    assert calculate("2e+3").text == "2000"
    assert calculate("2e-3").text == "0,002"
    assert calculate("1,5e2").text == "150"
    assert math.isclose(calculate("2e").value, 2 * math.e)


@pytest.mark.parametrize("expressao", ["2 3", "(1+2)3", "pi 2", "e3", "3 4 5"])
def test_dois_numeros_seguidos_sao_invalidos(expressao):
    with pytest.raises(InvalidExpressionError) as erro:
        calculate(expressao)
    assert erro.value.message == "Expressão inválida"


@pytest.mark.parametrize(
    "expressao, mensagem",
    [
        ("sin 30", "Use parênteses: sin(30)"),
        ("cos 60", "Use parênteses: cos(60)"),
        ("ln e", "Use parênteses: ln(...)"),
        ("sin -30", "Use parênteses: sin(...)"),
    ],
)
def test_funcoes_exigem_parenteses(expressao, mensagem):
    with pytest.raises(InvalidExpressionError) as erro:
        calculate(expressao)
    assert erro.value.message == mensagem
