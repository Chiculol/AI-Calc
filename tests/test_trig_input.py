"""Testes da Etapa 4 no motor: encaixe, ponto do mouse, campos, resumo falado e gráficos."""

import math

import pytest

from ai_calc.core import DomainError, IncompleteExpressionError, InvalidExpressionError
from ai_calc.core.trig import (
    TrigCircleState,
    angle_from_point,
    angle_text,
    graph_points,
    nearest_notable,
)
from ai_calc.core.trig_input import angle_from_text, describe, sine_from_text


# --- encaixe nos notáveis ----------------------------------------------------
@pytest.mark.parametrize(
    "angulo, esperado",
    [
        (29.4, 30),
        (31.9, 30),
        (32.1, 32.1),         # longe demais: fica onde está
        (44.0, 45),
        (89.0, 90),
        (359.2, 0),           # perto de 360 encaixa em 0
        (0.8, 0),
        (-1.0, 0),
        (17.0, 17.0),
        (330.5, 330),
    ],
)
def test_encaixe_nos_notaveis(angulo, esperado):
    assert nearest_notable(angulo) == pytest.approx(esperado)


def test_encaixe_com_tolerancia_zero_nao_muda():
    assert nearest_notable(29.4, tolerance=0) == pytest.approx(29.4)


# --- ponto do mouse -> ângulo --------------------------------------------------
@pytest.mark.parametrize(
    "x, y, esperado",
    [
        (1, 0, 0),
        (0, 1, 90),
        (-1, 0, 180),
        (0, -1, 270),
        (1, 1, 45),
        (-1, -1, 225),
        (math.sqrt(3), 1, 30),
        (5, -5, 315),
    ],
)
def test_angulo_a_partir_do_ponto(x, y, esperado):
    assert angle_from_point(x, y) == pytest.approx(esperado)


def test_ponto_no_centro_nao_tem_angulo():
    assert angle_from_point(0, 0) is None


# --- texto do ângulo ---------------------------------------------------------
@pytest.mark.parametrize(
    "angulo, modo, esperado",
    [(30, "DEG", "30°"), (450, "DEG", "90°"), (22.5, "DEG", "22,5°"),
     (30, "RAD", "π/6"), (10, "RAD", "0,1745"), (0, "RAD", "0")],
)
def test_texto_do_angulo(angulo, modo, esperado):
    assert angle_text(angulo, modo) == esperado


# --- campo "Ângulo" ----------------------------------------------------------
@pytest.mark.parametrize(
    "texto, modo, esperado",
    [
        ("30", "DEG", 30),
        ("450", "DEG", 90),
        ("-30", "DEG", 330),
        ("−30", "DEG", 330),
        ("22,5", "DEG", 22.5),
        ("45+45", "DEG", 90),
        ("π/6", "RAD", 30),
        ("2π/3", "RAD", 120),
        ("pi", "RAD", 180),
        ("0,1745", "RAD", math.degrees(0.1745)),
    ],
)
def test_campo_angulo(texto, modo, esperado):
    assert angle_from_text(texto, modo) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "texto, erro",
    [("", IncompleteExpressionError), ("   ", IncompleteExpressionError),
     ("abc", InvalidExpressionError), ("30+", IncompleteExpressionError)],
)
def test_campo_angulo_invalido(texto, erro):
    with pytest.raises(erro):
        angle_from_text(texto, "DEG")


# --- campo "Seno" ------------------------------------------------------------
@pytest.mark.parametrize(
    "texto, esperado",
    [("0,5", 0.5), ("0.5", 0.5), ("1/2", 0.5), ("√3/2", math.sqrt(3) / 2), ("-1", -1), ("0", 0)],
)
def test_campo_seno(texto, esperado):
    assert sine_from_text(texto) == pytest.approx(esperado)


@pytest.mark.parametrize("texto", ["2", "-1,5", "1,0001"])
def test_campo_seno_fora_do_dominio(texto):
    with pytest.raises(DomainError):
        sine_from_text(texto)


def test_campo_seno_vazio():
    with pytest.raises(IncompleteExpressionError):
        sine_from_text("")


# --- resumo para leitor de tela ------------------------------------------------
def test_resumo_em_graus():
    estado = TrigCircleState(30)
    assert describe(estado) == (
        "Ângulo 30 graus, 1º quadrante, seno 0,5, cosseno 0,866025403784, tangente 0,57735026919"
    )


def test_resumo_sobre_o_eixo_com_tangente_indefinida():
    texto = describe(TrigCircleState(90))
    assert "sobre o eixo" in texto
    assert texto.endswith("tangente indefinida")


def test_resumo_em_radianos():
    assert describe(TrigCircleState(180), "RAD").startswith("Ângulo 3,14159265359 radianos")


# --- pontos dos gráficos (Etapa 4B) ------------------------------------------------


@pytest.mark.parametrize("funcao", ["sin", "cos"])
def test_seno_e_cosseno_sao_um_trecho_so(funcao):
    trechos = graph_points(funcao)
    assert len(trechos) == 1
    assert trechos[0][0][0] == 0 and trechos[0][-1][0] == 360
    assert len(trechos[0]) == 361


def test_valores_exatos_nos_eixos():
    pontos = dict(graph_points("sin")[0])
    assert pontos[90] == 1 and pontos[180] == 0 and pontos[270] == -1
    assert pontos[30] == pytest.approx(0.5)


def test_tangente_quebra_nas_assintotas_e_respeita_o_limite():
    trechos = graph_points("tan", limit=2.0)
    assert len(trechos) == 3
    for trecho in trechos:
        assert all(abs(valor) <= 2.0 for _, valor in trecho)
        graus = [g for g, _ in trecho]
        assert not any(g in (90, 270) for g in graus)
    primeiro, meio, ultimo = trechos
    assert primeiro[0] == (0, 0) and primeiro[-1][1] == 2.0      # sobe até a borda de cima
    assert meio[0][1] == -2.0 and meio[-1][1] == 2.0            # vem de baixo e sobe de novo
    assert ultimo[0][1] == -2.0 and ultimo[-1] == (360, 0)
    assert dict(primeiro)[45] == pytest.approx(1)


def test_passo_menor_da_mais_pontos():
    assert len(graph_points("sin", step=0.5)[0]) == 721


def test_funcao_desconhecida():
    with pytest.raises(ValueError):
        graph_points("sec")
