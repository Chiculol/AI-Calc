"""Animações discretas de entrada (esmaecer), desligadas com "reduzir movimento"."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from .theme import ThemeManager

FADE_MS = 150


def fade_in(widget: QWidget, theme: ThemeManager, ms: int = FADE_MS) -> QPropertyAnimation | None:
    """Faz o widget aparecer esmaecendo (0 → 1). Sem animação se o movimento estiver reduzido."""
    previous = getattr(widget, "_fade_animation", None)
    if previous is not None:
        previous.stop()
        widget.setGraphicsEffect(None)
        widget._fade_animation = None
    if theme.reduce_motion() or not widget.isVisible():
        return None

    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(ms)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def finished() -> None:
        # Tira o efeito no fim: desenhar com ele custa mais e não é mais preciso.
        if getattr(widget, "_fade_animation", None) is animation:
            widget.setGraphicsEffect(None)
            widget._fade_animation = None

    animation.finished.connect(finished)
    widget._fade_animation = animation
    animation.start()
    return animation
