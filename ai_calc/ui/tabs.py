"""Barra de abas de vidro (Comum, Científica, Trigonometria)."""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QTabBar, QWidget

from .glass import paint_focus_ring, paint_glass
from .theme import ROLE_COLORS, ThemeManager

TAB_PADDING = 9
TAB_HEIGHT = 34
TAB_RADIUS = 10


class GlassTabBar(QTabBar):
    def __init__(self, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self.setExpanding(True)
        self.setDrawBase(False)
        self.setUsesScrollButtons(False)
        font = QFont(self.font())
        font.setPointSize(10)
        self.setFont(font)

    def tabSizeHint(self, index: int) -> QSize:  # noqa: N802 (nome do Qt)
        width = QFontMetrics(self.font()).horizontalAdvance(self.tabText(index))
        return QSize(width + 2 * TAB_PADDING, TAB_HEIGHT)

    def minimumTabSizeHint(self, index: int) -> QSize:  # noqa: N802 (nome do Qt)
        return self.tabSizeHint(index)

    def paintEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font())
        theme = self._theme
        for index in range(self.count()):
            if not self.isTabEnabled(index):
                role = "tab_disabled"
            elif index == self.currentIndex():
                role = "tab_selected"
            else:
                role = "tab"
            fill_key, _, text_key, alpha, focus_key = ROLE_COLORS[role]
            rect = QRectF(self.tabRect(index)).adjusted(1.5, 1.5, -2.5, -3.0)
            paint_glass(painter, rect, TAB_RADIUS, theme, theme.hex(fill_key), alpha)
            painter.setPen(theme.color(text_key))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.tabText(index))
            if self.hasFocus() and index == self.currentIndex():
                paint_focus_ring(painter, rect, TAB_RADIUS, theme.color(focus_key))
