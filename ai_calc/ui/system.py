"""Preferências do sistema operacional lidas pela interface."""

from __future__ import annotations

import sys

# SystemParametersInfo: "Efeitos de animação" (Configurações › Acessibilidade › Efeitos visuais).
_SPI_GETCLIENTAREAANIMATION = 0x1042


def reduce_motion() -> bool:
    """True quando o usuário desligou as animações no Windows."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        enabled = ctypes.c_int(1)
        ok = ctypes.windll.user32.SystemParametersInfoW(
            _SPI_GETCLIENTAREAANIMATION, 0, ctypes.byref(enabled), 0
        )
        return bool(ok) and not enabled.value
    except Exception:  # sem acesso à API: segue com animações
        return False
