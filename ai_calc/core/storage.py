"""Arquivos JSON do app: gravação segura e tratamento de arquivo corrompido."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CorruptFileError(Exception):
    """O arquivo existe, mas não dá para ler (JSON inválido ou formato errado)."""


def write_json_atomic(path: Path, data: object) -> bool:
    """Grava num arquivo temporário na mesma pasta e só então troca pelo definitivo.

    Assim, se o app fechar no meio da gravação, o arquivo antigo continua inteiro.
    Devolve False (e registra no log) se não deu para gravar; o app segue funcionando.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, path)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise
        return True
    except OSError:
        logger.exception("Não foi possível gravar %s", path)
        return False


def read_json(path: Path) -> object | None:
    """Lê o JSON. None se o arquivo não existe; CorruptFileError se está estragado."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        raise CorruptFileError(str(error)) from error
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise CorruptFileError(str(error)) from error


def quarantine(path: Path, now: datetime | None = None) -> Path | None:
    """Renomeia o arquivo estragado (ex.: historico.corrompido-20261028-153000.json)."""
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    target = path.with_name(f"{path.stem}.corrompido-{stamp}{path.suffix}")
    counter = 1
    while target.exists():
        counter += 1
        target = path.with_name(f"{path.stem}.corrompido-{stamp}-{counter}{path.suffix}")
    try:
        path.rename(target)
    except OSError:
        logger.exception("Não foi possível renomear o arquivo corrompido %s", path)
        return None
    logger.warning("Arquivo corrompido renomeado para %s", target)
    return target


def load_or_quarantine(path: Path, validate) -> object | None:
    """Lê e valida o arquivo. Se estiver estragado, renomeia e devolve None (começa do zero)."""
    try:
        data = read_json(path)
        if data is None:
            return None
        return validate(data)
    except (CorruptFileError, ValueError, TypeError, KeyError):
        quarantine(path)
        return None
