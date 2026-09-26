"""Confere se todo texto passado para tr() tem tradução nos quatro idiomas."""
import ast
import glob
import os
import re
import string
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from gavetapdf import i18n  # noqa: E402
from gavetapdf.translations import TRANSLATIONS  # noqa: E402


def source_texts() -> dict[str, str]:
    """Frases usadas em tr("...") no código → onde aparecem."""
    found = {}
    files = glob.glob(os.path.join(ROOT, "gavetapdf", "**", "*.py"), recursive=True)
    for path in files + [os.path.join(ROOT, "GavetaPDF.py")]:
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "tr" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found.setdefault(arg.value.strip(), f"{os.path.relpath(path, ROOT)}:{node.lineno}")
    return found


def fields(text: str) -> list[str]:
    return sorted(name for _, name, _, _ in string.Formatter().parse(text) if name is not None)


def test_every_text_has_translation():
    missing = [f"{where}: {text!r}" for text, where in source_texts().items() if text not in TRANSLATIONS]
    assert not missing, "Textos sem tradução em gavetapdf/translations.py:\n" + "\n".join(missing)


def test_translations_are_complete_and_consistent():
    for pt, values in TRANSLATIONS.items():
        assert len(values) == 3 and all(v.strip() for v in values), pt
        for v in values:
            assert fields(v) == fields(pt), f"marcadores diferentes em {pt!r} → {v!r}"
            assert v.count("<br>") == pt.count("<br>") and v.count("\n") == pt.count("\n"), f"quebras em {v!r}"


def test_no_unused_translations():
    used = set(source_texts())
    unused = [k for k in TRANSLATIONS if k not in used]
    assert not unused, "Traduções que não são mais usadas:\n" + "\n".join(map(repr, unused))


def test_tr_keeps_spaces_and_fills_values():
    try:
        i18n.set_language("en")
        assert i18n.tr(" Abrir pasta") == " Open folder"
        assert i18n.tr("Página {0} de {1}", 2, 5) == "Page 2 of 5"
        assert i18n.tr("Texto que não existe") == "Texto que não existe"
        i18n.set_language("ru")
        assert re.search("[а-я]", i18n.tr("Salvando…"))
    finally:
        i18n.set_language("pt")
    assert i18n.tr("Página {0} de {1}", 2, 5) == "Página 2 de 5"
