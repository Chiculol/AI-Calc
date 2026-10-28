"""Testes de cálculo: T01 a T04 e as regras dos pontos 1, 2 e 7."""

import math

import pytest

from ai_calc.core import (
    FactorialDomainError,
    FactorialLimitError,
    InvalidExpressionError,
    calculate,
)


def texto(expressao, modo="DEG"):
    return calculate(expressao, modo).text


# --- T01: precedência e parênteses -------------------------------------------
@pytest.mark.parametrize(
    "expressao, esperado",
    [
        ("2 + 3 * 4", "14"),
        ("(2 + 3) * 4", "20"),
        ("2 + 3 × 4", "14"),
        ("10 - 4 - 3", "3"),          # esquerda para a direita
        ("100 / 10 / 2", "5"),
        ("2 + 3 * 4 ^ 2", "50"),
        ("((1 + 2) * (3 + 4))", "21"),
        ("+5", "5"),
        ("5 + + 3", "8"),
        ("2 * -3", "-6"),
        ("7 ÷ 2", "3,5"),
        ("0.5 + 0.25", "0,75"),       # ponto também vale como decimal
        ("0,5 + 0,25", "0,75"),
    ],
)
def test_precedencia_e_parenteses(expressao, esperado):
    assert texto(expressao) == esperado


# --- T03: constantes, potências, fatorial e logaritmo ------------------------------
def test_pi_e_euler():
    assert math.isclose(calculate("pi * 2").value, 2 * math.pi, rel_tol=1e-12)
    assert texto("pi * 2") == "6,28318530718"
    assert texto("e^1") == "2,71828182846"
    assert texto("π") == "3,14159265359"


def test_fatorial_e_logaritmos():
    assert texto("5!") == "120"
    assert texto("log(100)") == "2"
    assert texto("log(1000)") == "3"
    assert texto("ln(e)") == "1"
    assert texto("ln(1)") == "0"


# --- T04: graus x radianos -----------------------------------------------------
def test_seno_de_30_em_graus_e_radianos():
    assert texto("sin(30)", "DEG") == "0,5"
    assert math.isclose(calculate("sin(30)", "RAD").value, -0.9880316240928618)
    assert texto("sin(30)", "RAD") == "-0,988031624093"


@pytest.mark.parametrize(
    "expressao, modo, esperado",
    [
        ("sin(180)", "DEG", "0"),
        ("sin(pi)", "RAD", "0"),
        ("cos(90)", "DEG", "0"),
        ("cos(pi/2)", "RAD", "0"),
        ("cos(60)", "DEG", "0,5"),
        ("cos(0)", "DEG", "1"),
        ("sin(90)", "DEG", "1"),
        ("sin(270)", "DEG", "-1"),
        ("tan(45)", "DEG", "1"),
        ("tan(0)", "DEG", "0"),
        ("tan(180)", "DEG", "0"),
        ("asin(0,5)", "DEG", "30"),
        ("acos(0)", "DEG", "90"),
        ("acos(-1)", "DEG", "180"),
        ("atan(1)", "DEG", "45"),
        ("atan(1)", "RAD", "0,785398163397"),
    ],
)
def test_trigonometria_sem_sujeira_numerica(expressao, modo, esperado):
    assert texto(expressao, modo) == esperado


def test_modo_angular_invalido_e_erro_de_programacao():
    with pytest.raises(ValueError):
        calculate("sin(30)", "GRAD")


# --- arredondamento -------------------------------------------------------------
def test_arredondamento_de_exibicao():
    assert texto("0,1 + 0,2") == "0,3"
    assert texto("1/3") == "0,333333333333"


# --- Ponto 1: porcentagem ---------------------------------------------------------
@pytest.mark.parametrize(
    "expressao, esperado",
    [
        ("200 + 10%", "220"),
        ("200 - 10%", "180"),
        ("200 * 10%", "20"),
        ("200 / 10%", "2000"),
        ("50%", "0,5"),
        ("100 + 20 + 10%", "132"),    # base = tudo que já foi somado
        ("(2 + 3)%", "0,05"),
        ("200 + 10% * 3", "200,3"),   # o % não é o termo inteiro: vale 0,1
        ("200 + (10%)", "200,1"),     # parênteses desligam a regra especial
        ("50% * 200", "100"),
    ],
)
def test_porcentagem(expressao, esperado):
    assert texto(expressao) == esperado


# --- Ponto 2: fatorial --------------------------------------------------------------
@pytest.mark.parametrize(
    "expressao, esperado",
    [
        ("0!", "1"),
        ("1!", "1"),
        ("5!", "120"),
        ("170!", "7,25741561531e+306"),
        ("(10 / 2)!", "120"),
        ("(0,1 * 30)!", "6"),          # tolerância para inteiros
        ("2^3!", "64"),                # ! vem antes de ^
        ("-3!", "-6"),
    ],
)
def test_fatorial_valido(expressao, esperado):
    assert texto(expressao) == esperado


def test_fatorial_acima_do_limite():
    with pytest.raises(FactorialLimitError) as erro:
        calculate("171!")
    assert erro.value.message == "Fatorial limitado a 170"


@pytest.mark.parametrize("expressao", ["5,5!", "(-3)!", "(1/3)!"])
def test_fatorial_fora_do_dominio(expressao):
    with pytest.raises(FactorialDomainError) as erro:
        calculate(expressao)
    assert erro.value.message == "Fatorial só vale para inteiros não negativos"


def test_fatorial_duplo_pede_parenteses():
    with pytest.raises(InvalidExpressionError) as erro:
        calculate("5!!")
    assert erro.value.message == "Use parênteses: (5!)!"
    assert texto("(5!)!") == "6,68950291345e+198"


# --- Ponto 7: precedência ---------------------------------------------------------------
@pytest.mark.parametrize(
    "expressao, esperado",
    [
        ("2^3^2", "512"),   # direita para a esquerda
        ("-2^2", "-4"),
        ("2^-2", "0,25"),
        ("(-2)^2", "4"),
        ("(-2)^3", "-8"),
        ("2^0,5 * 2^0,5", "2"),
    ],
)
def test_precedencia_da_potencia_e_do_menos_unario(expressao, esperado):
    assert texto(expressao) == esperado


# --- funções diversas -----------------------------------------------------------------
@pytest.mark.parametrize(
    "expressao, esperado",
    [
        ("sqrt(16)", "4"),
        ("√9", "3"),
        ("√(2 + 7)", "3"),
        ("abs(-5)", "5"),
        ("abs(5)", "5"),
        ("raiz(3; 8)", "2"),
        ("raiz(2; 9)", "3"),
        ("raiz(3; -8)", "-2"),
        ("raiz(2; 0)", "0"),
        ("1/(1/4)", "4"),
        ("SIN(30)", "0,5"),            # maiúsculas funcionam
    ],
)
def test_funcoes(expressao, esperado):
    assert texto(expressao) == esperado
