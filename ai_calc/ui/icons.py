"""Ícones desenhados à mão (sol e lua), na cor e opacidade pedidas."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen


def paint_sun(painter: QPainter, rect: QRectF, color: QColor) -> None:
    center = rect.center()
    unit = min(rect.width(), rect.height()) / 64
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)
    painter.drawEllipse(center, 12 * unit, 12 * unit)
    painter.setPen(QPen(color, 5 * unit, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    for step in range(8):
        angle = step * math.pi / 4
        dx, dy = math.cos(angle), math.sin(angle)
        painter.drawLine(
            center + QPointF(dx * 19 * unit, dy * 19 * unit),
            center + QPointF(dx * 27 * unit, dy * 27 * unit),
        )


def paint_moon(painter: QPainter, rect: QRectF, color: QColor) -> None:
    unit = min(rect.width(), rect.height()) / 64
    left, top = rect.center().x() - 32 * unit, rect.center().y() - 32 * unit
    full = QPainterPath()
    full.addEllipse(QRectF(left + 10 * unit, top + 10 * unit, 44 * unit, 44 * unit))
    bite = QPainterPath()
    bite.addEllipse(QRectF(left + 24 * unit, top + 2 * unit, 40 * unit, 40 * unit))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)
    painter.drawPath(full.subtracted(bite))


def paint_clock(painter: QPainter, rect: QRectF, color: QColor) -> None:
    """Relógio (ícone do histórico)."""
    unit = min(rect.width(), rect.height()) / 64
    center = rect.center()
    pen = QPen(color, 5 * unit, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, 25 * unit, 25 * unit)
    painter.drawLine(center, center + QPointF(0, -15 * unit))
    painter.drawLine(center, center + QPointF(11 * unit, 7 * unit))
