"""Gera assets/ai_calc.ico a partir do ícone desenhado em ai_calc/ui/icons.py.

Uso (da raiz do projeto): .venv\\Scripts\\python tools\\gerar_icone.py
Precisa do Pillow (requirements-build.txt) para juntar os tamanhos num só .ico.
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402
from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from ai_calc.ui.icons import ICON_SIZES, paint_app_icon  # noqa: E402

ICON_FILE = ROOT / "assets" / "ai_calc.ico"


def render(size: int) -> Image.Image:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    paint_app_icon(painter, size)
    painter.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return Image.open(io.BytesIO(bytes(buffer.data()))).convert("RGBA")


def main() -> None:
    app = QApplication.instance() or QApplication([])  # noqa: F841 (o Qt precisa dele para desenhar)
    images = {size: render(size) for size in ICON_SIZES}
    ICON_FILE.parent.mkdir(parents=True, exist_ok=True)
    largest = images[max(ICON_SIZES)]
    # Cada tamanho é desenhado separadamente (os pequenos têm menos teclas).
    largest.save(ICON_FILE, format="ICO", sizes=[(s, s) for s in ICON_SIZES],
                 append_images=[images[s] for s in ICON_SIZES if s != max(ICON_SIZES)])
    print(f"Ícone gravado em {ICON_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
