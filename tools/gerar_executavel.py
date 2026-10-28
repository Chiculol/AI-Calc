"""Gera dist/AI Calc.exe (um arquivo só, sem janela de console) com o PyInstaller.

Uso (da raiz do projeto):
    .venv\\Scripts\\python -m pip install -r requirements-build.txt
    .venv\\Scripts\\python tools\\gerar_executavel.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "AI Calc"
ICON = ROOT / "assets" / "ai_calc.ico"

# Partes do Qt que o app não usa: deixá-las de fora diminui o executável.
EXCLUDED = [
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets", "PySide6.QtMultimedia", "PySide6.QtPdf", "PySide6.Qt3DCore",
    "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtSql", "PySide6.QtTest",
    "tkinter", "unittest", "pytest", "pytestqt", "PIL",
]


def main() -> int:
    if not ICON.exists():
        subprocess.run([sys.executable, str(ROOT / "tools" / "gerar_icone.py")], check=True)
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile", "--windowed",
        "--name", NAME,
        "--icon", str(ICON),
        "--paths", str(ROOT),
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT / "build"),
    ]
    for module in EXCLUDED:
        command += ["--exclude-module", module]
    command.append(str(ROOT / "tools" / "iniciar.py"))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode == 0:
        exe = ROOT / "dist" / f"{NAME}.exe"
        print(f"\nPronto: {exe.relative_to(ROOT)} ({exe.stat().st_size / 1_048_576:.1f} MB)")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
