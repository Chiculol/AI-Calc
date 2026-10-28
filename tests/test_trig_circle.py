"""Testes da Etapa 2: círculo trigonométrico (ponto 3 da especificação)."""

import math

import pytest

from ai_calc.core import DomainError, TrigCircleState, format_number
from ai_calc.core.trig import (
    LEFT,
    ON_AXIS,
    RIGHT,
    UNDEFINED,
    angles_from_sin,
    circle_values,
    normalize_degrees,
    periodicity_text,
    quadrant,
    quadrant_label,
    radians_text,
    side_of,
    signs,
)


# --- Normalização para [0°, 360°) --------------------------------------------
@pytest.mark.parametrize(
    "angulo, esperado",
    [
        (450, 90),
        (-30, 330),
        (360, 0),
        (720, 0),
        (-360, 0),
        (0, 0),
        (359.5, 359.5),
        (-1e-15, 0),            # não pode virar 360
        (30.000000000000004, 30),
        (-450, 270),
    ],
)
def test_normaliza_angulo(angulo, esperado):
    assert normalize_degrees(angulo) == esperado


def test_normaliza_nunca_devolve_menos_zero():
    assert math.copysign(1, normalize_degrees(-0.0)) == 1


@pytest.mark.parametrize("angulo", [math.inf, -math.inf, math.nan])
def test_normaliza_rejeita_infinito(angulo):
    with pytest.raises(DomainError):
        normalize_degrees(angulo)


# --- Quadrante ---------------------------------------------------------------
@pytest.mark.parametrize(
    "angulo, esperado",
    [(45, 1), (135, 2), (225, 3), (315, 4), (-30, 4), (450.5, 2)],
)
def test_quadrante(angulo, esperado):
    assert quadrant(angulo) == esperado
    assert quadrant_label(angulo) == f"{esperado}º quadrante"


@pytest.mark.parametrize("angulo", [0, 90, 180, 270, 360, 450, -90])
def test_sobre_o_eixo(angulo):
    assert quadrant(angulo) is None
    assert quadrant_label(angulo) == ON_AXIS


# --- Valores e sinais --------------------------------------------------------
def test_45_graus():
    seno, cosseno, tangente = circle_values(45)
    assert seno == pytest.approx(0.7071, abs=1e-4)
    assert cosseno == pytest.approx(0.7071, abs=1e-4)
    assert tangente == pytest.approx(1)
    assert format_number(seno) == "0,707106781187"
    assert format_number(tangente) == "1"


@pytest.mark.parametrize(
    "angulo, esperado",
    [
        (45, ("+", "+", "+")),
        (135, ("+", "-", "-")),
        (225, ("-", "-", "+")),
        (315, ("-", "+", "-")),
        (0, ("0", "+", "0")),
        (90, ("+", "0", UNDEFINED)),
        (180, ("0", "-", "0")),
        (270, ("-", "0", UNDEFINED)),
    ],
)
def test_sinais(angulo, esperado):
    assert tuple(signs(angulo)) == esperado


@pytest.mark.parametrize("angulo", [90, 270, 450, -90])
def test_tangente_indefinida(angulo):
    assert circle_values(angulo)[2] is None


def test_zero_sem_sinal_negativo():
    # sin(180°) e tan(180°) são exatamente 0, sem "-0"
    seno, _, tangente = circle_values(180)
    assert math.copysign(1, seno) == 1
    assert math.copysign(1, tangente) == 1


# --- Lado do círculo ---------------------------------------------------------
@pytest.mark.parametrize(
    "angulo, esperado",
    [(0, RIGHT), (60, RIGHT), (90, RIGHT), (300, RIGHT), (120, LEFT), (180, LEFT), (240, LEFT)],
)
def test_lado(angulo, esperado):
    assert side_of(angulo) == esperado


# --- Ângulo a partir do seno -------------------------------------------------
@pytest.mark.parametrize(
    "seno, esperado",
    [
        (0.5, (30, 150)),
        (-0.5, (330, 210)),
        (0, (0, 180)),
        (1, (90,)),
        (-1, (270,)),
    ],
)
def test_angulos_pelo_seno(seno, esperado):
    assert angles_from_sin(seno) == pytest.approx(esperado)


@pytest.mark.parametrize("seno", [2, -1.5, 1.001])
def test_seno_fora_do_dominio(seno):
    with pytest.raises(DomainError):
        angles_from_sin(seno)


# --- Texto "Também vale" -----------------------------------------------------
def test_texto_periodicidade_graus():
    assert periodicity_text(30) == "Também vale: 30° + 360° × k"
    assert periodicity_text(450) == "Também vale: 90° + 360° × k"


@pytest.mark.parametrize(
    "angulo, esperado",
    [
        (0, "0"),
        (30, "π/6"),
        (45, "π/4"),
        (60, "π/3"),
        (90, "π/2"),
        (120, "2π/3"),
        (135, "3π/4"),
        (150, "5π/6"),
        (180, "π"),
        (210, "7π/6"),
        (225, "5π/4"),
        (240, "4π/3"),
        (270, "3π/2"),
        (300, "5π/3"),
        (315, "7π/4"),
        (330, "11π/6"),
        (360, "0"),                     # normalizado antes
        (390, "π/6"),
        (-30, "11π/6"),
        (30.000000000000004, "π/6"),    # erro de arredondamento não atrapalha
    ],
)
def test_radianos_notaveis_em_fracao_de_pi(angulo, esperado):
    assert radians_text(angulo) == esperado


@pytest.mark.parametrize(
    "angulo, esperado",
    [
        (10, "0,1745"),
        (1, "0,0175"),
        (100, "1,7453"),
        (200, "3,4907"),
        (359.5, "6,2745"),
        (15, "0,2618"),                 # 15° não está na lista de notáveis
    ],
)
def test_radianos_demais_com_4_casas(angulo, esperado):
    assert radians_text(angulo) == esperado


def test_texto_periodicidade_radianos():
    assert periodicity_text(30, "RAD") == "Também vale: π/6 + 2π × k"
    assert periodicity_text(180, "RAD") == "Também vale: π + 2π × k"
    assert periodicity_text(0, "RAD") == "Também vale: 0 + 2π × k"
    assert periodicity_text(10, "RAD") == "Também vale: 0,1745 + 2π × k"


def test_estado_texto_em_radianos():
    estado = TrigCircleState()
    estado.set_sin(0.5)
    estado.toggle()
    assert estado.periodicity_text("RAD") == "Também vale: 5π/6 + 2π × k"


# --- Estado do círculo (o que a interface vai usar) --------------------------
def test_estado_comeca_na_direita():
    estado = TrigCircleState()
    assert estado.angle == 0
    assert estado.side == RIGHT


def test_seno_meio_e_alternancia():
    estado = TrigCircleState()
    assert estado.set_sin(0.5) == pytest.approx(30)
    assert estado.can_toggle
    assert estado.toggle() == pytest.approx(150)
    assert estado.side == LEFT
    assert estado.toggle() == pytest.approx(30)
    assert estado.side == RIGHT


def test_seno_um_desativa_alternancia():
    estado = TrigCircleState()
    assert estado.set_sin(1) == 90
    assert not estado.can_toggle
    assert estado.toggle() == 90       # o botão desativado não muda nada


def test_seno_menos_um_desativa_alternancia():
    estado = TrigCircleState()
    assert estado.set_sin(-1) == 270
    assert not estado.can_toggle


def test_memoria_do_lado_ao_mexer_no_seno():
    estado = TrigCircleState(150)
    assert estado.side == LEFT
    assert estado.set_sin(0.8) == pytest.approx(180 - math.degrees(math.asin(0.8)))
    assert estado.set_sin(-0.3) > 180    # continua na esquerda (3º quadrante)
    assert estado.side == LEFT


def test_memoria_mantida_em_seno_um():
    # passar por 90° não apaga o lado: ao sair do seno 1, volta para a esquerda
    estado = TrigCircleState(120)
    estado.set_sin(1)
    assert estado.side == LEFT
    assert estado.set_sin(0.5) == pytest.approx(150)


def test_arrastar_pelo_eixo_vertical_mantem_lado():
    estado = TrigCircleState(100)
    estado.set_angle(90)
    assert estado.side == LEFT
    estado.set_angle(80)
    assert estado.side == RIGHT


def test_estado_normaliza_e_aceita_radianos():
    estado = TrigCircleState(450)
    assert estado.angle == 90
    estado.set_angle(-30)
    assert estado.angle == 330
    estado.set_angle(math.pi, "RAD")
    assert estado.angle == 180
    assert estado.angle_in("RAD") == pytest.approx(math.pi)


def test_estado_resumo_para_interface():
    estado = TrigCircleState(225)
    assert estado.quadrant_label == "3º quadrante"
    assert tuple(estado.signs) == ("-", "-", "+")
    assert estado.values[2] == pytest.approx(1)
    assert estado.periodicity_text() == "Também vale: 225° + 360° × k"


def test_seno_invalido_nao_muda_estado():
    estado = TrigCircleState(60)
    with pytest.raises(DomainError):
        estado.set_sin(2)
    assert estado.angle == 60
