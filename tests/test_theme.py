"""Tema ao abrir: o do Windows na primeira vez; depois, o que o usuário escolher."""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gavetapdf.ui import theme  # noqa: E402


def _fake_winreg(value):
    class Key:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def query(key, name):
        assert name == "AppsUseLightTheme"
        if value is None:
            raise FileNotFoundError(name)
        return value, 4

    return types.SimpleNamespace(HKEY_CURRENT_USER=0, OpenKey=lambda *a: Key(), QueryValueEx=query)


def test_follows_windows_theme(monkeypatch):
    monkeypatch.setitem(sys.modules, "winreg", _fake_winreg(1))
    assert theme.system_theme() == "light"
    monkeypatch.setitem(sys.modules, "winreg", _fake_winreg(0))
    assert theme.system_theme() == "dark"
    # Windows sem essa opção: não quebra (usa o que o Qt informar, claro por padrão)
    monkeypatch.setitem(sys.modules, "winreg", _fake_winreg(None))
    assert theme.system_theme() in ("light", "dark")


def test_first_time_follows_windows_then_user_choice(monkeypatch):
    monkeypatch.setitem(sys.modules, "winreg", _fake_winreg(0))  # Windows escuro
    assert theme.startup_theme(None) == "dark"  # primeira vez: nada salvo
    assert theme.startup_theme("light") == "light"  # usuário escolheu claro: mantém
    monkeypatch.setitem(sys.modules, "winreg", _fake_winreg(1))  # Windows claro
    assert theme.startup_theme(None) == "light"
    assert theme.startup_theme("dark") == "dark"
    assert theme.startup_theme("valor estranho") == "light"  # .ini corrompido: volta ao Windows
