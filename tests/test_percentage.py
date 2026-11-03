"""Testes unitários do motor de porcentagem (Etapa 6A)."""

import math

import pytest

from ai_calc.core.errors import CalcError, DivisionByZeroError, DomainError, OverflowCalcError
from ai_calc.core.percentage import (
    original_before_discount,
    part_of_total,
    percentage_change,
)


# --- part_of_total -----------------------------------------------------------
def test_part_of_total_casos_basicos():
    assert part_of_total(36, 240) == pytest.approx(0.15)
    assert part_of_total(120, 100) == pytest.approx(1.2)
    assert part_of_total(0, 100) == 0.0
    assert part_of_total(-25, 100) == pytest.approx(-0.25)
    assert part_of_total(25, -100) == pytest.approx(-0.25)
    assert isinstance(part_of_total(36, 240), float)


def test_part_of_total_denominador_zero():
    with pytest.raises(CalcError):
        part_of_total(50, 0)

    with pytest.raises(DivisionByZeroError) as erro:
        part_of_total(36, 0)
    assert erro.value.message == "Divisão por zero inválida"

    with pytest.raises(DivisionByZeroError):
        part_of_total(0, 0)


@pytest.mark.parametrize(
    "parte, total",
    [
        (float("nan"), 100),
        (100, float("nan")),
        (float("inf"), 100),
        (-float("inf"), 100),
        (100, float("inf")),
        (100, -float("inf")),
    ],
)
def test_part_of_total_nao_finito(parte, total):
    with pytest.raises(CalcError):
        part_of_total(parte, total)


# --- percentage_change -------------------------------------------------------
def test_percentage_change_casos_basicos():
    assert percentage_change(240, 204) == pytest.approx(-0.15)
    assert percentage_change(100, 0) == -1.0
    assert percentage_change(100, 150) == pytest.approx(0.5)
    assert percentage_change(100, 100) == 0.0
    assert percentage_change(50, 150) == pytest.approx(2.0)
    assert isinstance(percentage_change(240, 204), float)


def test_percentage_change_preserva_sinal_da_base():
    # Base inicial negativa preserva seu sinal na fórmula (final - initial) / initial
    assert percentage_change(-100, -50) == pytest.approx(-0.5)
    assert percentage_change(-100, -150) == pytest.approx(0.5)
    assert percentage_change(-100, 100) == pytest.approx(-2.0)


def test_percentage_change_denominador_zero():
    with pytest.raises(CalcError):
        percentage_change(0, 100)

    with pytest.raises(DivisionByZeroError) as erro:
        percentage_change(0, 50)
    assert erro.value.message == "Divisão por zero inválida"

    with pytest.raises(DivisionByZeroError):
        percentage_change(0, 0)


@pytest.mark.parametrize(
    "inicial, final",
    [
        (float("nan"), 100),
        (100, float("nan")),
        (float("inf"), 100),
        (-float("inf"), 100),
        (100, float("inf")),
        (100, -float("inf")),
    ],
)
def test_percentage_change_nao_finito(inicial, final):
    with pytest.raises(CalcError):
        percentage_change(inicial, final)


# --- original_before_discount ------------------------------------------------
def test_original_before_discount_casos_basicos():
    assert original_before_discount(150, 0.25) == pytest.approx(200.0)
    assert original_before_discount(150, 0) == 150.0
    assert original_before_discount(80, 0.2) == pytest.approx(100.0)
    assert original_before_discount(50, 0.5) == pytest.approx(100.0)
    assert isinstance(original_before_discount(150, 0.25), float)


@pytest.mark.parametrize("taxa", [-0.01, -0.5, -1.0])
def test_original_before_discount_desconto_negativo(taxa):
    with pytest.raises(CalcError):
        original_before_discount(100, taxa)

    with pytest.raises(DomainError) as erro:
        original_before_discount(100, taxa)
    assert erro.value.message == "Valor fora do domínio"


@pytest.mark.parametrize("taxa", [1.0, 1.05, 2.0])
def test_original_before_discount_desconto_100_ou_mais(taxa):
    with pytest.raises(CalcError):
        original_before_discount(100, taxa)

    with pytest.raises(DomainError) as erro:
        original_before_discount(100, taxa)
    assert erro.value.message == "Valor fora do domínio"


@pytest.mark.parametrize(
    "final, taxa",
    [
        (float("nan"), 0.2),
        (100, float("nan")),
        (float("inf"), 0.2),
        (-float("inf"), 0.2),
        (100, float("inf")),
        (100, -float("inf")),
    ],
)
def test_original_before_discount_nao_finito(final, taxa):
    with pytest.raises(CalcError):
        original_before_discount(final, taxa)
