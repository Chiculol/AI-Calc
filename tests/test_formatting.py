"""Testes do ponto 5: formatação e notação científica."""

import pytest

from ai_calc.core import OverflowCalcError, calculate, format_number


@pytest.mark.parametrize(
    "valor, esperado",
    [
        (0.1 + 0.2, "0,3"),
        (1 / 3, "0,333333333333"),
        (0.5, "0,5"),
        (120.0, "120"),
        (-1.5, "-1,5"),
        (0.0, "0"),
        (-0.0, "0"),
        (999999999999.0, "999999999999"),
        (1e12, "1e+12"),
        (1.5e20, "1,5e+20"),
        (123456789012345.0, "1,23456789012e+14"),
        (999999999999.9, "1e+12"),      # arredonda para cima e muda de faixa
        (0.000001, "0,000001"),
        (1e-7, "1e-7"),
        (2.5e-9, "2,5e-9"),
        (9.9999999999999e-7, "0,000001"),
        (1e-300, "1e-300"),
        (-2.5e-9, "-2,5e-9"),
        (7.257415615307994e306, "7,25741561531e+306"),
        (1234567.891, "1234567,891"),   # sem separador de milhar
    ],
)
def test_formatar_numero(valor, esperado):
    assert format_number(valor) == esperado


@pytest.mark.parametrize("valor", [float("inf"), float("-inf"), float("nan")])
def test_formatar_valor_invalido_vira_erro_amigavel(valor):
    with pytest.raises(OverflowCalcError):
        format_number(valor)


def test_notacao_cientifica_pode_voltar_para_a_conta():
    # o histórico insere o número do resultado; ele precisa ser lido de volta
    assert calculate("1,5e+20").text == "1,5e+20"
    assert calculate("2,5e-9 * 2").text == "5e-9"
    assert calculate("1e12 + 1e12").text == "2e+12"


def test_resultados_nas_bordas_da_formatacao():
    assert calculate("999999999999").text == "999999999999"
    assert calculate("1000000000000").text == "1e+12"
    assert calculate("0,0000001").text == "1e-7"
