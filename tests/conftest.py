"""Configuração comum dos testes: a janela roda em modo offscreen (sem aparecer na tela)."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# No Windows, o modo offscreen não acha as fontes do sistema sozinho.
_windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
if _windows_fonts.is_dir():
    os.environ.setdefault("QT_QPA_FONTDIR", str(_windows_fonts))
