"""Funções de apoio usadas por vários testes de janela."""

from PySide6.QtGui import QColor


def distancia(cor: QColor, hex_cor: str) -> int:
    """Quão longe uma cor da tela está de uma cor da paleta (soma das diferenças em R, G e B)."""
    alvo = int(hex_cor[1:3], 16), int(hex_cor[3:5], 16), int(hex_cor[5:7], 16)
    return sum(abs(a - b) for a, b in zip((cor.red(), cor.green(), cor.blue()), alvo))
