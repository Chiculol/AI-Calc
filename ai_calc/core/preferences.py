"""Preferências do usuário (tema, DEG/RAD e última aba), salvas em JSON."""

from __future__ import annotations

from pathlib import Path

from .storage import load_or_quarantine, write_json_atomic

FORMAT_VERSION = 1
THEMES = ("claro", "escuro")
ANGLE_MODES = ("DEG", "RAD")
TABS = ("comum", "cientifica")


def _validate(data: object) -> dict:
    if not isinstance(data, dict) or data.get("versao") != FORMAT_VERSION:
        raise ValueError("formato desconhecido")
    return data


class Preferences:
    """Valores desconhecidos no arquivo são ignorados (vale o padrão)."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.theme: str | None = None     # None = seguir o tema do Windows
        self.angle_mode = "DEG"
        self.last_tab = "comum"
        data = load_or_quarantine(path, _validate) if path is not None else None
        if data:
            if data.get("tema") in THEMES:
                self.theme = data["tema"]
            if data.get("modo_angulo") in ANGLE_MODES:
                self.angle_mode = data["modo_angulo"]
            if data.get("ultima_aba") in TABS:
                self.last_tab = data["ultima_aba"]

    def update(self, **changes) -> None:
        """Muda e salva. Ex.: update(theme="escuro")."""
        for key, value in changes.items():
            if not hasattr(self, key) or key == "path":
                raise AttributeError(key)
            setattr(self, key, value)
        self.save()

    def save(self) -> None:
        if self.path is None:
            return
        write_json_atomic(
            self.path,
            {
                "versao": FORMAT_VERSION,
                "tema": self.theme,
                "modo_angulo": self.angle_mode,
                "ultima_aba": self.last_tab,
            },
        )
