"""Onde o programa grava seus arquivos: sempre na própria pasta (modo portátil).

    GavetaPDF.exe
    GavetaPDF.ini        configurações (última pasta, ferramenta, assinatura salva…)
    dados\\gavetapdf.log  registro de erros
    dados\\ui\\          imagens geradas para a interface

Nada vai para o registro do Windows, %APPDATA%, %LOCALAPPDATA% ou %TEMP%.
Se a pasta do programa não permitir gravação (pendrive protegido, Arquivos de Programas),
o programa funciona normalmente, só não guarda configurações nem log entre uma execução e outra.
"""
from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile

INI_NAME = "GavetaPDF.ini"
DATA_DIR_NAME = "dados"


def app_dir() -> str:
    """Pasta do GavetaPDF.exe (ou a raiz do projeto quando roda pelo código)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _writable(folder: str) -> bool:
    try:
        os.makedirs(folder, exist_ok=True)
        probe = os.path.join(folder, ".teste-gravacao")
        with open(probe, "w", encoding="ascii") as fh:
            fh.write("ok")
        os.remove(probe)
        return True
    except OSError:
        return False


_can_write: bool | None = None


def can_write() -> bool:
    """Indica se a pasta do programa aceita gravação (calculado uma vez)."""
    global _can_write
    if _can_write is None:
        _can_write = _writable(app_dir())
    return _can_write


def ini_path() -> str:
    return os.path.join(app_dir(), INI_NAME)


def data_dir() -> str | None:
    """Pasta `dados` ao lado do programa; None se não for possível gravar nela."""
    if not can_write():
        return None
    d = os.path.join(app_dir(), DATA_DIR_NAME)
    return d if _writable(d) else None


def log_path() -> str | None:
    d = data_dir()
    return os.path.join(d, "gavetapdf.log") if d else None


_scratch: str | None = None


def ui_cache_dir() -> str:
    """Pasta para as imagens da interface.

    Em último caso (pasta do programa somente leitura) usa uma pasta temporária
    que é apagada ao fechar o programa, para não deixar rastro.
    """
    global _scratch
    d = data_dir()
    if d:
        ui = os.path.join(d, "ui")
        if _writable(ui):
            return ui
    if _scratch is None:
        _scratch = tempfile.mkdtemp(prefix="gavetapdf-")
        atexit.register(shutil.rmtree, _scratch, True)
    return _scratch
