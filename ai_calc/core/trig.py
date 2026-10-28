"""Funções trigonométricas com tratamento exato de ângulos notáveis.

A primeira parte é usada pelo avaliador. A segunda (Etapa 2) é a lógica do
círculo trigonométrico: normalização do ângulo, quadrante, sinais, as duas
soluções do seno e a memória do último lado. O círculo guarda o ângulo sempre
em graus; radianos só aparecem na hora de mostrar.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import NamedTuple

from .errors import DomainError, UndefinedError
from .formatting import format_number
from .limits import (
    ANGLE_SNAP_TOLERANCE,
    COS_UNDEFINED_THRESHOLD,
    GRAPH_LIMIT,
    NOTABLE_SNAP_DEGREES,
    TRIG_TOLERANCE,
)

_SIN_AT = (0.0, 1.0, 0.0, -1.0)
_COS_AT = (1.0, 0.0, -1.0, 0.0)


def _quarter_turns(x: float, mode: str) -> int | None:
    """Se x é (quase) um múltiplo não nulo de um quarto de volta, devolve o múltiplo."""
    quarter = 90.0 if mode == "DEG" else math.pi / 2
    k = x / quarter
    n = round(k)
    if n != 0 and abs(k - n) < TRIG_TOLERANCE:
        return n
    return None


def _to_radians(x: float, mode: str) -> float:
    return math.radians(x) if mode == "DEG" else x


def _from_radians(x: float, mode: str) -> float:
    return math.degrees(x) if mode == "DEG" else x


def sin(x: float, mode: str) -> float:
    n = _quarter_turns(x, mode)
    if n is not None:
        return _SIN_AT[n % 4]
    return math.sin(_to_radians(x, mode))


def cos(x: float, mode: str) -> float:
    n = _quarter_turns(x, mode)
    if n is not None:
        return _COS_AT[n % 4]
    return math.cos(_to_radians(x, mode))


def tan(x: float, mode: str) -> float:
    n = _quarter_turns(x, mode)
    if n is not None:
        if n % 2 != 0:
            raise UndefinedError()
        return 0.0
    radians = _to_radians(x, mode)
    if abs(math.cos(radians)) < COS_UNDEFINED_THRESHOLD:
        raise UndefinedError()
    return math.tan(radians)


def asin(x: float, mode: str) -> float:
    if x > 1 + 1e-12 or x < -1 - 1e-12:
        raise DomainError()
    return _from_radians(math.asin(max(-1.0, min(1.0, x))), mode)


def acos(x: float, mode: str) -> float:
    if x > 1 + 1e-12 or x < -1 - 1e-12:
        raise DomainError()
    return _from_radians(math.acos(max(-1.0, min(1.0, x))), mode)


def atan(x: float, mode: str) -> float:
    return _from_radians(math.atan(x), mode)


# --- Etapa 2: círculo trigonométrico ------------------------------------------

RIGHT = "direita"     # cosseno >= 0
LEFT = "esquerda"     # cosseno < 0
ON_AXIS = "Sobre o eixo"
UNDEFINED = "indefinida"

# Ângulos notáveis (em graus) escritos como fração de π no modo RAD.
NOTABLE_ANGLES = frozenset(
    (0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330)
)


class TrigSigns(NamedTuple):
    """Sinal de cada função: "+", "-", "0" ou "indefinida"."""

    sin: str
    cos: str
    tan: str


def to_degrees(angle: float, mode: str) -> float:
    """Converte para graus um ângulo digitado no modo DEG ou RAD."""
    return math.degrees(angle) if mode == "RAD" else angle


def normalize_degrees(angle: float) -> float:
    """Leva o ângulo para o intervalo [0°, 360°): 450° vira 90°, -30° vira 330°."""
    if math.isnan(angle) or math.isinf(angle):
        raise DomainError()
    result = angle % 360.0
    nearest = round(result)
    if abs(result - nearest) < ANGLE_SNAP_TOLERANCE:
        result = float(nearest)
    if result >= 360.0:
        result = 0.0
    return result + 0.0  # troca -0,0 por 0,0


def quadrant(angle: float) -> int | None:
    """Quadrante de 1 a 4, ou None quando o ângulo está sobre um eixo."""
    theta = normalize_degrees(angle)
    if theta % 90.0 == 0.0:
        return None
    return int(theta // 90.0) + 1


def quadrant_label(angle: float) -> str:
    number = quadrant(angle)
    return ON_AXIS if number is None else f"{number}º quadrante"


def circle_values(angle: float) -> tuple[float, float, float | None]:
    """Seno, cosseno e tangente do ângulo em graus (tangente None se indefinida)."""
    theta = normalize_degrees(angle)
    try:
        tangent: float | None = tan(theta, "DEG") + 0.0
    except UndefinedError:
        tangent = None
    return sin(theta, "DEG") + 0.0, cos(theta, "DEG") + 0.0, tangent


def _sign(value: float | None) -> str:
    if value is None:
        return UNDEFINED
    if value == 0:
        return "0"
    return "+" if value > 0 else "-"


def signs(angle: float) -> TrigSigns:
    return TrigSigns(*(_sign(value) for value in circle_values(angle)))


def side_of(angle: float) -> str:
    """Lado do círculo: direita quando cosseno >= 0, esquerda quando < 0."""
    return RIGHT if circle_values(angle)[1] >= 0 else LEFT


def angles_from_sin(value: float) -> tuple[float, ...]:
    """Ângulos (em graus) com esse seno: (lado direito, lado esquerdo).

    θ e 180° - θ; em seno 1 ou -1 só existe uma solução.
    """
    right = normalize_degrees(asin(value, "DEG"))
    left = normalize_degrees(180.0 - right)
    if left == right:
        return (right,)
    return (right, left)


def radians_text(angle: float) -> str:
    """Ângulo em radianos para exibição: fração de π nos notáveis ("π/6",
    "3π/4", "π"), senão decimal com 4 casas ("0,1745")."""
    theta = normalize_degrees(angle)
    if theta in NOTABLE_ANGLES:
        fraction = Fraction(int(theta), 180)
        if fraction == 0:
            return "0"
        numerator = "π" if fraction.numerator == 1 else f"{fraction.numerator}π"
        return numerator if fraction.denominator == 1 else f"{numerator}/{fraction.denominator}"
    return f"{math.radians(theta):.4f}".replace(".", ",")


def periodicity_text(angle: float, mode: str = "DEG") -> str:
    """Texto discreto: "Também vale: 30° + 360° × k" (ou "π/6 + 2π × k" em RAD)."""
    theta = normalize_degrees(angle)
    if mode == "RAD":
        return f"Também vale: {radians_text(theta)} + 2π × k"
    return f"Também vale: {format_number(theta)}° + 360° × k"


def nearest_notable(angle: float, tolerance: float = NOTABLE_SNAP_DEGREES) -> float:
    """Encaixa no ângulo notável mais próximo, se estiver a menos de "tolerance" graus."""
    theta = normalize_degrees(angle)
    for notable in (*NOTABLE_ANGLES, 360):
        if abs(theta - notable) < tolerance:
            return normalize_degrees(notable)
    return theta


def angle_from_point(x: float, y: float) -> float | None:
    """Ângulo (graus) do ponto (x, y) visto do centro do círculo, com y para cima.

    None no centro exato, onde não há direção.
    """
    if x == 0 and y == 0:
        return None
    return normalize_degrees(math.degrees(math.atan2(y, x)))


def angle_text(angle: float, mode: str = "DEG") -> str:
    """Ângulo para mostrar: "30°" em DEG, "π/6" (ou "0,1745") em RAD."""
    if mode == "RAD":
        return radians_text(angle)
    return f"{format_number(normalize_degrees(angle))}°"


TRIG_FUNCTIONS = ("sin", "cos", "tan")


def toggle_visible(visible: frozenset[str], name: str) -> frozenset[str]:
    """Liga ou desliga uma função no círculo e nos gráficos.

    A última função visível não pode ser desligada (devolve o conjunto sem mudar).
    """
    if name not in TRIG_FUNCTIONS:
        raise ValueError(f"Função desconhecida: {name}")
    if name in visible:
        return visible if len(visible) == 1 else visible - {name}
    return visible | {name}


GraphSegment = list[tuple[float, float]]


def graph_points(function: str, step: float = 1.0, limit: float = GRAPH_LIMIT) -> list[GraphSegment]:
    """Pontos (graus, valor) de 0° a 360° para desenhar a curva, em trechos contínuos.

    A tangente é interrompida nas assíntotas (90° e 270°) e cortada em ±limit: o trecho
    termina (ou começa) exatamente na borda, para não desenhar linhas falsas.
    """
    functions = {"sin": sin, "cos": cos, "tan": tan}
    if function not in functions:
        raise ValueError(f"Função desconhecida: {function}")
    segments: list[GraphSegment] = []
    current: GraphSegment = []
    outside: tuple[float, float] | None = None   # último ponto além da borda
    steps = int(round(360 / step))
    for index in range(steps + 1):
        degrees = index * step
        try:
            value = functions[function](degrees, "DEG")
        except UndefinedError:
            if current:
                segments.append(current)
            current, outside = [], None
            continue
        if abs(value) > limit:
            edge = (degrees, math.copysign(limit, value))
            if current:
                current.append(edge)
                segments.append(current)
                current = []
            outside = edge
            continue
        if not current and outside is not None:
            current.append(outside)
        outside = None
        current.append((degrees, value))
    if current:
        segments.append(current)
    return segments


class TrigCircleState:
    """Estado do círculo para a interface: ângulo atual e o último lado usado.

    O ângulo fica sempre em graus, entre 0° e 360°. O lado começa na direita e
    só muda quando o ângulo sai do eixo vertical (em 90° e 270° ele é mantido).
    """

    def __init__(self, angle: float = 0.0, mode: str = "DEG") -> None:
        self._angle = 0.0
        self._side = RIGHT
        self.set_angle(angle, mode)

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def side(self) -> str:
        return self._side

    @property
    def can_toggle(self) -> bool:
        """Falso em seno 1 ou -1, onde só existe uma solução."""
        return abs(sin(self._angle, "DEG")) != 1.0

    def angle_in(self, mode: str) -> float:
        return math.radians(self._angle) if mode == "RAD" else self._angle

    def set_angle(self, angle: float, mode: str = "DEG") -> float:
        self._angle = normalize_degrees(to_degrees(angle, mode))
        cosine = circle_values(self._angle)[1]
        if cosine != 0:
            self._side = RIGHT if cosine > 0 else LEFT
        return self._angle

    def set_sin(self, value: float) -> float:
        """Escolhe o ângulo com esse seno, respeitando o último lado."""
        solutions = angles_from_sin(value)
        if len(solutions) == 1 or self._side == RIGHT:
            self._angle = solutions[0]
        else:
            self._angle = solutions[1]
        return self._angle

    def toggle(self) -> float:
        """Troca θ por 180° - θ (não faz nada quando há uma solução só)."""
        if self.can_toggle:
            self.set_angle(180.0 - self._angle)
        return self._angle

    @property
    def quadrant_label(self) -> str:
        return quadrant_label(self._angle)

    @property
    def values(self) -> tuple[float, float, float | None]:
        return circle_values(self._angle)

    @property
    def signs(self) -> TrigSigns:
        return signs(self._angle)

    def periodicity_text(self, mode: str = "DEG") -> str:
        return periodicity_text(self._angle, mode)
