"""Botões de vidro: teclas da calculadora e o botão de tema (sol/lua)."""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import QPushButton, QSizePolicy, QWidget

from .glass import paint_focus_ring, paint_glass, with_alpha
from .icons import paint_clock, paint_moon, paint_sun
from .theme import ROLE_COLORS, ThemeManager, mix

KEY_RADIUS = 12
PRESS_IN_MS = 70
PRESS_OUT_MS = 180
HOVER_MS = 140
PRESS_SCALE = 0.04     # a tecla encolhe 4% quando apertada


class GlassButton(QPushButton):
    """Tecla de vidro com animações discretas de passar o mouse e de clique."""

    def __init__(
        self,
        text: str,
        theme: ThemeManager,
        role: str = "digit",
        small: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self._theme = theme
        self._role = role
        self._press = 0.0
        self._hover = 0.0
        self._was_down = False
        self.setProperty("role", role)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        font = QFont(self.font())
        font.setPointSize(11 if small else 15)
        font.setBold(role == "equals")
        self.setFont(font)

        self._press_animation = QVariantAnimation(self)
        self._press_animation.valueChanged.connect(self._set_press)
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.valueChanged.connect(self._set_hover)

    @property
    def role(self) -> str:
        return self._role

    # --- animações ---
    def _set_press(self, value: float) -> None:
        self._press = float(value)
        self.update()

    def _set_hover(self, value: float) -> None:
        self._hover = float(value)
        self.update()

    def _animate(self, animation: QVariantAnimation, current: float, target: float, ms: int) -> None:
        animation.stop()
        if self._theme.reduce_motion():
            setter = self._set_press if animation is self._press_animation else self._set_hover
            setter(target)
            return
        animation.setStartValue(current)
        animation.setEndValue(target)
        animation.setDuration(ms)
        animation.start()

    def enterEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        super().enterEvent(event)
        self._animate(self._hover_animation, self._hover, 1.0, HOVER_MS)

    def leaveEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        super().leaveEvent(event)
        self._animate(self._hover_animation, self._hover, 0.0, HOVER_MS)

    # --- desenho ---
    def paintEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        # isDown() muda por mouse, Espaço ou teclado físico (flash); anima a partir daqui.
        down = self.isDown()
        if down != self._was_down:
            self._was_down = down
            if down:
                self._animate(self._press_animation, self._press, 1.0, PRESS_IN_MS)
            else:
                self._animate(self._press_animation, self._press, 0.0, PRESS_OUT_MS)

        fill_key, pressed_key, text_key, alpha, focus_key = ROLE_COLORS[self._role]
        theme = self._theme
        fill = mix(theme.hex(fill_key), theme.hex(pressed_key), self._press)
        hover = self._hover
        if self._role == "equals":
            fill = mix(fill, theme.hex("equals_hover"), hover * (1 - self._press))
            hover = 0.0

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -3.0)
        scale = 1.0 - PRESS_SCALE * self._press
        center = rect.center()
        painter.translate(center)
        painter.scale(scale, scale)
        painter.translate(-center)

        paint_glass(painter, rect, KEY_RADIUS, theme, fill, alpha, hover)
        self.paint_content(painter, rect, theme.color(text_key))
        if self.hasFocus():
            paint_focus_ring(painter, rect, KEY_RADIUS, theme.color(focus_key))

    def paint_content(self, painter: QPainter, rect: QRectF, color) -> None:
        painter.setPen(color)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class ThemeToggleButton(GlassButton):
    """Botão de tema: lua no claro, sol no escuro, trocando suavemente junto com o tema."""

    def __init__(self, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__("", theme, role="theme", parent=parent)
        self.setObjectName("themeButton")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(QSize(36, 34))

    def paint_content(self, painter: QPainter, rect: QRectF, color) -> None:
        progress = self._theme.progress         # 0 = claro (lua), 1 = escuro (sol)
        icon_rect = QRectF(0, 0, 20, 20)
        icon_rect.moveCenter(rect.center())
        if progress < 1:
            paint_moon(painter, icon_rect, with_alpha(color, 1 - progress))
        if progress > 0:
            paint_sun(painter, icon_rect, with_alpha(color, progress))


class HistoryToggleButton(GlassButton):
    """Botão que mostra/esconde o histórico quando a janela está estreita."""

    def __init__(self, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__("", theme, role="theme", parent=parent)
        self.setObjectName("historyButton")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(QSize(36, 34))

    def paint_content(self, painter: QPainter, rect: QRectF, color) -> None:
        icon_rect = QRectF(0, 0, 20, 20)
        icon_rect.moveCenter(rect.center())
        paint_clock(painter, icon_rect, color)
