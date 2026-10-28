"""Histórico das contas: últimas 20, mais nova primeiro, salvo em JSON."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .storage import load_or_quarantine, write_json_atomic

MAX_HISTORY = 20
FORMAT_VERSION = 1
ANGLE_MODES = ("DEG", "RAD")


@dataclass(frozen=True)
class HistoryEntry:
    expression: str
    result: str                  # já arredondado e com vírgula, como no visor
    angle_mode: str | None = None  # "DEG"/"RAD" só se a conta usou trigonometria

    def to_json(self) -> dict:
        return {"expressao": self.expression, "resultado": self.result, "modo": self.angle_mode}

    @classmethod
    def from_json(cls, data: dict) -> HistoryEntry:
        expression, result, mode = data["expressao"], data["resultado"], data.get("modo")
        if not isinstance(expression, str) or not isinstance(result, str) or not result:
            raise ValueError("item inválido")
        if mode is not None and mode not in ANGLE_MODES:
            raise ValueError("modo inválido")
        return cls(expression, result, mode)


def _validate(data: object) -> list[HistoryEntry]:
    if not isinstance(data, dict) or data.get("versao") != FORMAT_VERSION:
        raise ValueError("formato desconhecido")
    items = data["itens"]
    if not isinstance(items, list):
        raise ValueError("itens inválidos")
    return [HistoryEntry.from_json(item) for item in items][:MAX_HISTORY]


class History:
    """Lista de contas feitas. Sem caminho (path=None), fica só na memória."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._entries: list[HistoryEntry] = []
        if path is not None:
            self._entries = load_or_quarantine(path, _validate) or []

    @property
    def entries(self) -> list[HistoryEntry]:
        return list(self._entries)

    def add(self, expression: str, result: str, angle_mode: str | None = None) -> bool:
        """Guarda uma conta que deu certo. Conta com erro (sem resultado) não entra."""
        if not expression.strip() or not result:
            return False
        self._entries.insert(0, HistoryEntry(expression, result, angle_mode))
        del self._entries[MAX_HISTORY:]
        self._save()
        return True

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def _save(self) -> None:
        if self.path is not None:
            data = {"versao": FORMAT_VERSION, "itens": [e.to_json() for e in self._entries]}
            write_json_atomic(self.path, data)
