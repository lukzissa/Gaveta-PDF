"""Idiomas da interface: português (Brasil), inglês, espanhol e russo.

Os textos ficam escritos em português no código e passam por `tr()`, que devolve a
tradução do idioma atual (tabela em `translations.py`). O idioma é definido uma vez,
ao iniciar, a partir do GavetaPDF.ini ou, na primeira execução, do idioma do Windows.
Trocar de idioma reinicia o programa.
"""
from __future__ import annotations

import locale

from . import paths

LANGUAGES = {
    "pt": "Português (Brasil)",
    "en": "English",
    "es": "Español",
    "ru": "Русский",
}
DEFAULT = "en"

# Idioma do OCR sugerido para cada idioma da interface
OCR_LANGUAGE = {"pt": "por", "en": "eng", "es": "spa", "ru": "rus"}


def _saved_language() -> str | None:
    try:
        from PySide6.QtCore import QSettings

        value = QSettings(paths.ini_path(), QSettings.IniFormat).value("language")
    except Exception:  # noqa: BLE001
        return None
    return value if value in LANGUAGES else None


def _system_language() -> str:
    try:
        from PySide6.QtCore import QLocale

        code = QLocale.system().name()  # ex.: "pt_BR"
    except Exception:  # noqa: BLE001
        code = locale.getlocale()[0] or ""
    code = code[:2].lower()
    return code if code in LANGUAGES else DEFAULT


current = _saved_language() or _system_language()
_table: dict[str, str] = {}


def set_language(code: str) -> None:
    """Define o idioma. Só tem efeito completo antes de criar as telas (ou após reiniciar)."""
    global current, _table
    current = code if code in LANGUAGES else DEFAULT
    if current == "pt":
        _table = {}
    else:
        from .translations import TRANSLATIONS

        column = ("en", "es", "ru").index(current)
        _table = {pt: values[column] for pt, values in TRANSLATIONS.items()}


def tr(text: str, *args) -> str:
    """Traduz `text` (escrito em português) e preenche {0}, {1}… com `args`.

    Espaços no começo e no fim (usados ao lado de ícones) são mantidos.
    """
    core = text.strip()
    translated = _table.get(core, core)
    if core != text:
        start = text[:len(text) - len(text.lstrip())]
        end = text[len(text.rstrip()):]
        translated = f"{start}{translated}{end}"
    return translated.format(*args) if args else translated


def decimal_separator() -> str:
    return "." if current == "en" else ","


set_language(current)
