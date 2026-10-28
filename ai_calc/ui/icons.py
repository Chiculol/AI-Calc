"""Ícones desenhados à mão: sol, lua, relógio e o ícone do app."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap


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


def paint_app_icon(painter: QPainter, size: int) -> None:
    """Ícone do AI Calc: quadrado arredondado em degradê com o círculo trigonométrico."""
    s = float(size)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    gradient = QLinearGradient(0, 0, s, s)
    gradient.setColorAt(0.0, QColor("#4B3F99"))
    gradient.setColorAt(1.0, QColor("#1FA89B"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawRoundedRect(QRectF(0, 0, s, s), s * 0.22, s * 0.22)

    center = QPointF(s / 2, s / 2)
    radius = s * 0.30
    white = QColor("#FFFFFF")
    faint = QColor(255, 255, 255, 110)
    painter.setPen(QPen(faint, max(1.0, s * 0.03)))
    painter.drawLine(QPointF(s * 0.12, center.y()), QPointF(s * 0.88, center.y()))
    painter.drawLine(QPointF(center.x(), s * 0.12), QPointF(center.x(), s * 0.88))
    painter.setPen(QPen(white, max(1.0, s * 0.06)))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, radius, radius)

    angle = math.radians(40)
    tip = QPointF(center.x() + radius * math.cos(angle), center.y() - radius * math.sin(angle))
    painter.setPen(QPen(white, max(1.0, s * 0.05), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.drawLine(center, tip)
    painter.setPen(QPen(QColor("#FFD166"), max(1.0, s * 0.05), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.drawLine(QPointF(tip.x(), center.y()), tip)          # o seno
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#FFD166"))
    painter.drawEllipse(tip, s * 0.065, s * 0.065)


ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def app_icon() -> QIcon:
    """QIcon com o ícone desenhado em vários tamanhos (barra de tarefas, janela, Alt+Tab)."""
    icon = QIcon()
    for size in ICON_SIZES:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        paint_app_icon(painter, size)
        painter.end()
        icon.addPixmap(pixmap)
    return icon
