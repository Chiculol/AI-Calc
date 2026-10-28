"""Desenho do "vidro líquido" simulado: degradê, translucidez, borda, brilho e sombra.

Sem blur real: a superfície é semitransparente sobre um fundo colorido, com
um brilho na metade de cima e uma borda clara no alto.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from .theme import (
    GLOW_ALPHA,
    HOVER_ALPHA,
    RIM_ALPHA,
    SHADOW_ALPHA,
    SHEEN_ALPHA,
    TOP_TINT,
    ThemeManager,
    mix,
)


def with_alpha(color: QColor | str, alpha: float) -> QColor:
    result = QColor(color)
    result.setAlphaF(max(0.0, min(1.0, alpha)))
    return result


def paint_glass(
    painter: QPainter,
    rect: QRectF,
    radius: float,
    theme: ThemeManager,
    fill: str,
    alpha: float,
    hover: float = 0.0,
) -> None:
    """Pinta uma superfície de vidro com a cor "fill" (hex) e a opacidade dada."""
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)

    # Sombra suave logo abaixo.
    shadow = QPainterPath()
    shadow.addRoundedRect(rect.translated(0, 1.5), radius, radius)
    painter.fillPath(shadow, with_alpha(theme.hex("shadow"), SHADOW_ALPHA))

    # Corpo: degradê do topo (mais claro) para baixo, semitransparente.
    rim = theme.hex("glass_rim")
    body = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    body.setColorAt(0.0, with_alpha(mix(fill, rim, TOP_TINT), alpha))
    body.setColorAt(1.0, with_alpha(fill, alpha))
    painter.fillPath(path, QBrush(body))

    if hover > 0:
        painter.fillPath(path, with_alpha(rim, HOVER_ALPHA * hover))

    # Brilho na metade de cima.
    sheen = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.top() + rect.height() * 0.55))
    sheen.setColorAt(0.0, with_alpha(rim, SHEEN_ALPHA))
    sheen.setColorAt(1.0, with_alpha(rim, 0.0))
    painter.fillPath(path, QBrush(sheen))

    # Borda: clara no alto, discreta embaixo.
    edge = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    edge.setColorAt(0.0, with_alpha(rim, RIM_ALPHA))
    edge.setColorAt(1.0, with_alpha(theme.hex("glass_edge"), 0.6))
    painter.setPen(QPen(QBrush(edge), 1.0))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)


def paint_focus_ring(painter: QPainter, rect: QRectF, radius: float, color: QColor) -> None:
    painter.setPen(QPen(color, 2.5))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    inner = rect.adjusted(1.5, 1.5, -1.5, -1.5)
    painter.drawRoundedRect(inner, max(0.0, radius - 1.5), max(0.0, radius - 1.5))


class Backdrop(QWidget):
    """Fundo da janela: degradê com duas manchas de cor que aparecem através do vidro."""

    def __init__(self, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme

    def paintEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        theme = self._theme

        base = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        base.setColorAt(0.0, theme.color("window_top"))
        base.setColorAt(1.0, theme.color("window_bottom"))
        painter.fillRect(rect, QBrush(base))

        size = max(rect.width(), rect.height())
        for key, cx, cy in (("glow_a", 0.12, 0.30), ("glow_b", 0.95, 0.80)):
            center = QPointF(rect.width() * cx, rect.height() * cy)
            glow = QRadialGradient(center, size * 0.55)
            glow.setColorAt(0.0, with_alpha(theme.hex(key), GLOW_ALPHA))
            glow.setColorAt(1.0, with_alpha(theme.hex(key), 0.0))
            painter.fillRect(rect, QBrush(glow))


def set_text_color(widget: QWidget, color: QColor) -> None:
    """Cor do texto de um QLabel (sem folha de estilo, para acompanhar a transição)."""
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.WindowText, color)
    widget.setPalette(palette)
