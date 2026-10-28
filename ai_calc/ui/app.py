"""Cria o aplicativo, carrega histórico e preferências e abre a janela."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ..core.history import History
from ..core.preferences import Preferences
from .main_window import MainWindow
from .theme import ThemeManager

logger = logging.getLogger(__name__)

FONT_FAMILIES = ["Segoe UI Variable", "Segoe UI"]
FONT_POINT_SIZE = 11
HISTORY_FILE = "historico.json"
PREFERENCES_FILE = "preferencias.json"


def create_app(argv: list[str] | None = None) -> QApplication:
    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName("AI Calc")
    # Fusion respeita a paleta do tema em todos os elementos padrão do Qt.
    app.setStyle("Fusion")
    font = QFont()
    font.setFamilies(FONT_FAMILIES)
    font.setPointSize(FONT_POINT_SIZE)
    app.setFont(font)
    return app


def data_folder() -> Path:
    """Pasta de dados do app (no Windows: %APPDATA%/AI Calc)."""
    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    return Path(location)


def _log_unexpected(exc_type, exc, traceback) -> None:
    # Rede de segurança: registra o erro e mantém o app aberto.
    logger.error("Erro inesperado na interface", exc_info=(exc_type, exc, traceback))


def build_window(folder: Path, **theme_options) -> MainWindow:
    """Janela com histórico e preferências guardados em "folder"."""
    preferences = Preferences(folder / PREFERENCES_FILE)
    history = History(folder / HISTORY_FILE)
    # Tema salvo pelo botão vale sobre o do Windows; sem escolha salva, segue o Windows.
    theme = ThemeManager(preferences.theme, **theme_options)
    return MainWindow(theme, history, preferences)


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    sys.excepthook = _log_unexpected
    app = create_app()
    window = build_window(data_folder())
    window.show()
    return app.exec()
