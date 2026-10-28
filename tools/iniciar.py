"""Ponto de entrada do executável (o PyInstaller precisa de um arquivo, não de "-m ai_calc")."""

import sys

from ai_calc.ui.app import main

if __name__ == "__main__":
    sys.exit(main())
