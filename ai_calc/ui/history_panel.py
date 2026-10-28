"""Painel de vidro do histórico: lista de contas, barra de rolagem e botão Limpar."""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
    QStyle,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)

from ..core.history import HistoryEntry
from .glass import paint_glass, set_text_color, with_alpha
from .glass_button import GlassButton
from .theme import DIALOG_ALPHA, DISPLAY_ALPHA, ThemeManager

PANEL_RADIUS = 16
ITEM_HEIGHT = 58
MODE_NAMES = {"DEG": "graus", "RAD": "radianos"}


class HistoryItemButton(GlassButton):
    """Um item do histórico: conta em cima (discreta), resultado embaixo e etiqueta DEG/RAD."""

    def __init__(self, entry: HistoryEntry, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(entry.result, theme, role="history", small=True, parent=parent)
        self.entry = entry
        self.setFixedHeight(ITEM_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mode = f", {MODE_NAMES[entry.angle_mode]}" if entry.angle_mode else ""
        name = f"{entry.expression} igual a {entry.result}{mode}"
        self.setAccessibleName(name)
        self.setAccessibleDescription("Insere o resultado na conta atual")
        self.setToolTip(f"{entry.expression} = {entry.result}\nClique para inserir {entry.result}")

    def paint_content(self, painter: QPainter, rect: QRectF, color) -> None:
        inner = rect.adjusted(12, 6, -12, -6)
        theme = self._theme

        small = QFont(self.font())
        small.setPointSize(9)
        painter.setFont(small)
        painter.setPen(theme.color("text_muted"))
        top = QRectF(inner.left(), inner.top(), inner.width(), inner.height() / 2)
        expression = QFontMetrics(small).elidedText(
            self.entry.expression, Qt.TextElideMode.ElideLeft, int(top.width())
        )
        painter.drawText(top, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, expression)
        bottom = QRectF(inner.left(), inner.center().y(), inner.width(), inner.height() / 2)
        if self.entry.angle_mode:
            painter.drawText(bottom, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             self.entry.angle_mode)

        big = QFont(self.font())
        big.setPointSize(13)
        big.setBold(True)
        painter.setFont(big)
        painter.setPen(color)
        result = QFontMetrics(big).elidedText(
            self.entry.result, Qt.TextElideMode.ElideLeft, int(bottom.width() - 40)
        )
        painter.drawText(bottom, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, result)


class GlassScrollBar(QScrollBar):
    """Barra de rolagem fina, desenhada com as cores do tema."""

    def __init__(self, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(Qt.Orientation.Vertical, parent)
        self._theme = theme
        self.setFixedWidth(10)

    def paintEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        track = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        painter.setBrush(with_alpha(self._theme.hex("glass_rim"), 0.18))
        painter.drawRoundedRect(track, 3, 3)

        option = QStyleOptionSlider()
        self.initStyleOption(option)
        handle = self.style().subControlRect(
            QStyle.ComplexControl.CC_ScrollBar, option, QStyle.SubControl.SC_ScrollBarSlider, self
        )
        painter.setBrush(self._theme.color("scroll_handle"))
        painter.drawRoundedRect(QRectF(handle).adjusted(2, 1, -2, -1), 3, 3)


class HistoryPanel(QFrame):
    value_chosen = Signal(str)      # número do resultado escolhido
    clear_requested = Signal()
    close_requested = Signal()

    def __init__(self, theme: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("historyPanel")
        self.setAccessibleName("Histórico")
        self._theme = theme
        self._entries: list[HistoryEntry] = []
        self._alpha = DISPLAY_ALPHA

        self.title = QLabel("Histórico", self)
        title_font = QFont(self.title.font())
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title.setFont(title_font)

        self.clear_button = GlassButton("Limpar", theme, role="action", small=True, parent=self)
        self.clear_button.setAccessibleName("Limpar histórico")
        self.clear_button.setToolTip("Limpar histórico")
        self.clear_button.setFixedSize(QSize(76, 34))
        self.clear_button.clicked.connect(self.clear_requested)

        self.close_button = GlassButton("✕", theme, role="theme", small=True, parent=self)
        self.close_button.setAccessibleName("Fechar histórico")
        self.close_button.setToolTip("Fechar histórico")
        self.close_button.setFixedSize(QSize(36, 34))
        self.close_button.clicked.connect(self.close_requested)
        self.close_button.hide()

        self.empty_label = QLabel("Nenhuma conta ainda.\nAs contas feitas aparecem aqui.", self)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)

        self._list = QWidget()
        self._list_layout = QVBoxLayout(self._list)
        self._list_layout.setContentsMargins(0, 0, 4, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch(1)

        self.scroll = QScrollArea(self)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBar(GlassScrollBar(theme))
        self.scroll.setWidget(self._list)
        self.scroll.setAccessibleName("Lista de contas")
        self.scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)   # o Tab vai direto aos itens
        # Fundo transparente: o vidro do painel aparece por trás da lista.
        self.scroll.viewport().setAutoFillBackground(False)
        self._list.setAutoFillBackground(False)

        header = QHBoxLayout()
        header.setSpacing(6)
        header.addWidget(self.title, 1)
        header.addWidget(self.clear_button)
        header.addWidget(self.close_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 8, 12)
        layout.setSpacing(10)
        layout.addLayout(header)
        layout.addWidget(self.empty_label, 1)
        layout.addWidget(self.scroll, 1)

        theme.changed.connect(self.apply_colors)
        self.apply_colors()
        self.show_entries([])

    @property
    def items(self) -> list[HistoryItemButton]:
        return self._list.findChildren(HistoryItemButton)

    def set_drawer_mode(self, drawer: bool) -> None:
        # Como gaveta, o painel fica sobre o teclado: vidro mais opaco para não misturar textos.
        self.close_button.setVisible(drawer)
        self._alpha = DIALOG_ALPHA if drawer else DISPLAY_ALPHA
        self.update()

    def show_entries(self, entries: list[HistoryEntry]) -> None:
        self._entries = list(entries)
        for item in self.items:
            item.setParent(None)
            item.deleteLater()
        for index, entry in enumerate(self._entries):
            item = HistoryItemButton(entry, self._theme, self._list)
            item.clicked.connect(lambda _=False, r=entry.result: self.value_chosen.emit(r))
            self._list_layout.insertWidget(index, item)
            item.show()   # visível já, para entrar na conta da altura logo abaixo
        # Altura mínima da lista = soma dos itens; assim a rolagem aparece em vez de apertar.
        self._list_layout.activate()
        self._list.setMinimumHeight(self._list_layout.minimumSize().height())
        empty = not self._entries
        self.empty_label.setVisible(empty)
        self.scroll.setVisible(not empty)
        self.clear_button.setEnabled(not empty)

    def apply_colors(self) -> None:
        set_text_color(self.title, self._theme.color("text"))
        set_text_color(self.empty_label, self._theme.color("text_muted"))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (nome do Qt)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -3)
        theme = self._theme
        paint_glass(painter, rect, PANEL_RADIUS, theme, theme.hex("display_bg"), self._alpha)
