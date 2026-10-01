"""Aparência: temas claro e escuro, folha de estilos e ícones vetoriais desenhados em SVG.

As cores ficam no dicionário `C`, trocado por `apply()`. Tudo que é desenhado à mão
(ícones, prévias, miniaturas) lê `C` na hora de pintar, então a troca de tema vale
na hora, sem reiniciar o programa.
"""
from __future__ import annotations

from PySide6.QtCore import QByteArray, QPoint, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QIconEngine, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

LIGHT = {
    "accent": "#D6423A",
    "accent_hover": "#BF352E",
    "accent_soft": "#FBECEB",     # fundo de item selecionado
    "accent_strong": "#F7D3D0",   # miniatura selecionada no organizador
    "on_accent": "#FFFFFF",
    "primary_disabled": "#EBA7A3",
    "text": "#1F2328",
    "muted": "#667085",
    "disabled": "#A0A7B4",
    "bg": "#F5F6F8",              # fundo da área de conteúdo
    "sidebar": "#FFFFFF",
    "surface": "#FFFFFF",         # cartões, campos, botões
    "hover": "#F9FAFB",
    "pressed": "#F2F4F7",
    "border": "#E3E6EA",
    "control_border": "#D0D5DD",
    "control_border_hover": "#B8BFCA",
    "dashed": "#C9CED6",
    "canvas": "#EEF0F3",          # fundo atrás das páginas
    "scroll": "#CDD2DA",
    "tooltip_bg": "#1F2328",
    "tooltip_text": "#FFFFFF",
}

# Modo escuro, com o mesmo vermelho do tema claro como destaque.
DARK = {
    "accent": "#D6423A",
    "accent_hover": "#E0564E",
    "accent_soft": "#3A1F1D",
    "accent_strong": "#52302C",
    "on_accent": "#FFFFFF",
    "primary_disabled": "#5A2A27",
    "text": "#F0EFEC",
    "muted": "#9C9A92",
    "disabled": "#5F5E5A",
    "bg": "#151515",
    "sidebar": "#111111",
    "surface": "#20201F",
    "hover": "#2A2A28",
    "pressed": "#323230",
    "border": "#2A2A28",
    "control_border": "#3E3E3B",
    "control_border_hover": "#56564F",
    "dashed": "#3E3E3B",
    "canvas": "#1B1B1A",
    "scroll": "#3E3E3B",
    "tooltip_bg": "#F0EFEC",
    "tooltip_text": "#151515",
}

THEMES = {"light": LIGHT, "dark": DARK}
C: dict[str, str] = dict(LIGHT)
current = "light"


def color(role: str) -> QColor:
    return QColor(C[role])


def _stylesheet(c: dict[str, str]) -> str:
    return f"""
* {{ font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif; font-size: 10pt; color: {c['text']}; }}
QMainWindow, #content {{ background: {c['bg']}; }}
QDialog, QMessageBox {{ background: {c['bg']}; }}

#sidebar {{ background: {c['sidebar']}; border: none; outline: 0; padding: 8px 8px; }}
#sidebar::item {{ padding: 10px 12px; border-radius: 8px; margin: 2px 0; }}
#sidebar::item:hover {{ background: {c['pressed']}; }}
#sidebar::item:selected {{ background: {c['accent_soft']}; color: {c['accent']}; font-weight: 600; }}
#sidebarPanel {{ background: {c['sidebar']}; border-right: 1px solid {c['border']}; }}
#brandRow {{ background: {c['sidebar']}; }}
#brand {{ font-size: 15pt; font-weight: 700; background: transparent; }}
#brandSub {{ color: {c['muted']}; font-size: 9pt; padding: 2px 16px 12px 16px; background: {c['sidebar']}; }}
#sidebarFooter {{ background: {c['sidebar']}; }}

#pageTitle {{ font-size: 17pt; font-weight: 700; }}
#pageSubtitle {{ color: {c['muted']}; font-size: 10pt; }}
#sectionLabel {{ font-weight: 600; margin-top: 6px; }}
#hint {{ color: {c['muted']}; font-size: 9pt; }}

#card {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 10px; }}

QPushButton {{ background: {c['surface']}; border: 1px solid {c['control_border']}; border-radius: 7px; padding: 7px 14px; }}
QPushButton:hover {{ background: {c['hover']}; border-color: {c['control_border_hover']}; }}
QPushButton:pressed {{ background: {c['pressed']}; }}
QPushButton:disabled {{ color: {c['disabled']}; background: {c['hover']}; }}
QPushButton#primary {{ background: {c['accent']}; color: {c['on_accent']}; border: 1px solid {c['accent']}; font-weight: 600; padding: 9px 22px; }}
QPushButton#primary:hover {{ background: {c['accent_hover']}; border-color: {c['accent_hover']}; }}
QPushButton#primary:disabled {{ background: {c['primary_disabled']}; border-color: {c['primary_disabled']}; color: {c['on_accent']}; }}
QPushButton#link {{ border: none; background: transparent; color: {c['accent']}; padding: 4px 6px; text-align: left; }}
QPushButton#link:hover {{ text-decoration: underline; }}
QPushButton#paypal {{ background: #FFC439; border: none; border-radius: 17px; padding: 0; }}
QPushButton#paypal:hover {{ background: #F2BA36; }}
QPushButton#paypal:pressed {{ background: #E6AE2E; }}
#paypalLabel {{ background: transparent; font-size: 10pt; }}
QPushButton#subtle {{ border: none; background: transparent; color: {c['muted']}; padding: 4px 6px; text-align: left; }}
QPushButton#subtle:hover {{ color: {c['text']}; }}
QPushButton#subtle::menu-indicator {{ image: none; width: 0; }}
QMenu {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 4px; }}
QMenu::item {{ padding: 6px 22px 6px 26px; border-radius: 5px; }}
QMenu::item:selected {{ background: {c['accent_soft']}; color: {c['text']}; }}
QMenu::indicator {{ width: 14px; height: 14px; left: 6px; }}

QListWidget#dropList {{ background: {c['surface']}; border: 1.5px dashed {c['dashed']}; border-radius: 10px; padding: 6px; outline: 0; }}
QListWidget#dropList[dragging="true"] {{ border-color: {c['accent']}; background: {c['accent_soft']}; }}
QListWidget#dropList::item {{ padding: 6px 8px; border-radius: 6px; }}
QListWidget#dropList::item:selected {{ background: {c['accent_soft']}; color: {c['text']}; }}
QListWidget#pageGrid {{ background: {c['canvas']}; border: 1.5px dashed {c['dashed']}; border-radius: 10px; outline: 0; }}
QListWidget#pageGrid[dragging="true"] {{ border-color: {c['accent']}; }}
QListWidget#pageGrid::item {{ border-radius: 8px; padding: 6px; color: {c['muted']}; }}
QListWidget#pageGrid::item:selected {{ background: {c['accent_strong']}; color: {c['text']}; }}

QLineEdit, QSpinBox, QComboBox {{ background: {c['surface']}; border: 1px solid {c['control_border']}; border-radius: 7px; padding: 6px 8px; min-height: 18px; }}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{ border-color: {c['accent']}; }}
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{ color: {c['disabled']}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{ background: {c['surface']}; border: 1px solid {c['border']}; selection-background-color: {c['accent_soft']}; selection-color: {c['text']}; }}

QRadioButton, QCheckBox {{ spacing: 8px; padding: 3px 0; }}
QRadioButton::indicator, QCheckBox::indicator {{ width: 16px; height: 16px; }}

QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; padding: 8px 16px; margin-right: 4px; border-bottom: 2px solid transparent; color: {c['muted']}; }}
QTabBar::tab:selected {{ color: {c['accent']}; border-bottom: 2px solid {c['accent']}; font-weight: 600; }}
QTabBar::tab:hover {{ color: {c['text']}; }}

#taskBar {{ background: {c['surface']}; border-top: 1px solid {c['border']}; }}
QProgressBar {{ background: {c['canvas']}; border: none; border-radius: 4px; height: 8px; max-height: 8px; text-align: center; }}
QProgressBar::chunk {{ background: {c['accent']}; border-radius: 4px; }}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {c['scroll']}; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QSlider::groove:horizontal {{ height: 4px; background: {c['control_border']}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {c['accent']}; width: 14px; margin: -6px 0; border-radius: 7px; }}
QToolTip {{ background: {c['tooltip_bg']}; color: {c['tooltip_text']}; border: none; padding: 5px 8px; border-radius: 4px; }}
"""


# Ícones em traço, 24x24.
_ICONS = {
    "merge": '<rect x="3" y="3" width="9" height="12" rx="1.5"/><rect x="12" y="9" width="9" height="12" rx="1.5"/><path d="M7 19h2M17 5h-2"/>',
    "split": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M2 12h3M8 12h3M13 12h3M19 12h3"/>',
    "organize": '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="9" rx="1.5"/><rect x="3" y="15" width="7" height="6" rx="1.5"/><rect x="14" y="15" width="7" height="6" rx="1.5"/>',
    "compress": '<path d="M4 14h6v6"/><path d="M20 10h-6V4"/><path d="M14 10l7-7"/><path d="M3 21l7-7"/>',
    "convert": '<path d="M4 8h13l-3-3"/><path d="M20 16H7l3 3"/>',
    "ocr": '<path d="M3 7V4h3M21 7V4h-3M3 17v3h3M21 17v3h-3"/><path d="M8 9h8M8 12h8M8 15h5"/>',
    "sign": '<path d="M3 16c2-3 3.5-8 5.5-8S8 16 10 16s2.5-4 4-4 1 3 2.5 3 2-1.5 4-1.5"/><path d="M3 20h18"/>',
    "add": '<path d="M12 5v14M5 12h14"/>',
    "remove": '<path d="M5 12h14"/>',
    "up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "down": '<path d="M12 5v14M6 13l6 6 6-6"/>',
    "clear": '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    "rotl": '<path d="M4 4v5h5"/><path d="M4.5 9A8 8 0 1 1 6 17"/>',
    "rotr": '<path d="M20 4v5h-5"/><path d="M19.5 9A8 8 0 1 0 18 17"/>',
    "folder": '<path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "file": '<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9s1.3-6.3 3.8-9z"/>',
    "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
}

# O ícone do programa não muda com o tema: é a marca. Gaveta aberta com uma folha de PDF saindo (vermelho da marca).
APP_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E4574E"/><stop offset="1" stop-color="#B8342D"/></linearGradient></defs>
<rect x="3" y="3" width="58" height="58" rx="14" fill="url(#bg)"/>
<rect x="9" y="33" width="46" height="12" rx="3" fill="#8E2621"/>
<g transform="rotate(-8 32 30)">
  <path d="M19 9h18l8 8v27H19z" fill="#FFFFFF"/>
  <path d="M37 9v8h8z" fill="#F7D3D0"/>
  <rect x="22" y="22" width="20" height="9" rx="2" fill="#D6423A"/>
  <text x="32" y="29.2" font-family="Segoe UI, Arial" font-weight="800" font-size="7.4" fill="#FFFFFF" text-anchor="middle">PDF</text>
  <path d="M23 35h18M23 38.5h12" stroke="#E7C9C6" stroke-width="1.6" stroke-linecap="round"/>
</g>
<rect x="7" y="40" width="50" height="17" rx="4" fill="#FFFFFF"/>
<rect x="7" y="40" width="50" height="3" rx="1.5" fill="#F1E3E2"/>
<rect x="25" y="46.5" width="14" height="4.5" rx="2.25" fill="#D6423A"/>
</svg>"""


def _svg(name: str, stroke: str, width: float = 1.8) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'{_ICONS[name]}</svg>')


def _render(svg: str, size: int) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    renderer.render(p, QRectF(0, 0, size, size))
    p.end()
    return pm


class _ThemedIconEngine(QIconEngine):
    """Desenha o ícone com a cor do tema atual toda vez que ele é pintado."""

    def __init__(self, name: str, role: str, selected_role: str | None = None) -> None:
        super().__init__()
        self.name = name
        self.role = role
        self.selected_role = selected_role

    def _stroke(self, mode) -> str:
        if mode == QIcon.Disabled:
            return C["disabled"]
        if mode == QIcon.Selected and self.selected_role:
            return C[self.selected_role]
        return C[self.role]

    def paint(self, painter, rect, mode, state):
        QSvgRenderer(QByteArray(_svg(self.name, self._stroke(mode)).encode())).render(painter, QRectF(rect))

    def pixmap(self, size, mode, state):
        pm = QPixmap(size)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        self.paint(p, QRect(QPoint(0, 0), size), mode, state)
        p.end()
        return pm

    def clone(self):
        return _ThemedIconEngine(self.name, self.role, self.selected_role)


def icon(name: str, role: str = "text") -> QIcon:
    """Ícone de traço na cor `role` do tema (ex.: "text", "muted", "accent")."""
    return QIcon(_ThemedIconEngine(name, role))


def nav_icon(name: str) -> QIcon:
    """Ícone da barra lateral: cinza normal, cor de destaque quando selecionado."""
    return QIcon(_ThemedIconEngine(name, "muted", "accent"))


def app_icon() -> QIcon:
    ic = QIcon()
    for s in (16, 24, 32, 48, 64, 128, 256):
        ic.addPixmap(_render(APP_ICON_SVG, s))
    return ic


def app_pixmap(size: int) -> QPixmap:
    return _render(APP_ICON_SVG, size)


def palette() -> QPalette:
    """Paleta do tema atual, independente do tema (claro/escuro) do Windows."""
    pal = QPalette()
    colors = {
        QPalette.Window: C["bg"],
        QPalette.WindowText: C["text"],
        QPalette.Base: C["surface"],
        QPalette.AlternateBase: C["bg"],
        QPalette.Text: C["text"],
        QPalette.Button: C["surface"],
        QPalette.ButtonText: C["text"],
        QPalette.BrightText: C["on_accent"],
        QPalette.ToolTipBase: C["tooltip_bg"],
        QPalette.ToolTipText: C["tooltip_text"],
        QPalette.PlaceholderText: C["muted"],
        QPalette.Highlight: C["accent"],
        QPalette.HighlightedText: C["on_accent"],
        QPalette.Link: C["accent"],
        QPalette.Light: C["hover"],
        QPalette.Midlight: C["border"],
        QPalette.Mid: C["control_border"],
        QPalette.Dark: C["control_border_hover"],
        QPalette.Shadow: "#000000",
    }
    for role, value in colors.items():
        pal.setColor(QPalette.All, role, QColor(value))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        pal.setColor(QPalette.Disabled, role, QColor(C["disabled"]))
    return pal


ICON_SIZE = QSize(20, 20)


def build_stylesheet() -> str:
    """Folha de estilos do tema atual.

    As setas do QSpinBox precisam de imagens em arquivo quando o widget é estilizado,
    então elas são geradas na pasta de dados do programa (uma por tema).
    """
    import os

    from .. import paths

    folder = paths.ui_cache_dir()
    arrows = {"up": "M6 15l6-6 6 6", "down": "M6 9l6 6 6-6"}
    files = {}
    for name, d in arrows.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{C["muted"]}" '
               f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></svg>')
        path = os.path.join(folder, f"arrow-{name}-{current}.png")
        _render(svg, 24).save(path)
        files[name] = path.replace("\\", "/")
    extra = f"""
QSpinBox {{ padding-right: 22px; }}
QSpinBox::up-button, QSpinBox::down-button {{ subcontrol-origin: border; width: 20px; border: none; background: transparent; }}
QSpinBox::up-button {{ subcontrol-position: top right; margin-top: 3px; }}
QSpinBox::down-button {{ subcontrol-position: bottom right; margin-bottom: 3px; }}
QSpinBox::up-arrow {{ image: url("{files['up']}"); width: 11px; height: 11px; }}
QSpinBox::down-arrow {{ image: url("{files['down']}"); width: 11px; height: 11px; }}
"""
    return _stylesheet(C) + extra


def startup_theme(saved) -> str:
    """Tema ao abrir: a escolha que o usuário salvou pelo botão; sem escolha, o do Windows."""
    return saved if saved in THEMES else system_theme()


def system_theme() -> str:
    """Tema do Windows ("light" ou "dark"), lido de Configurações → Personalização → Cores."""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            light, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "light" if light else "dark"
    except (ImportError, OSError):  # outro sistema ou Windows sem essa opção: pergunta ao Qt
        app = QApplication.instance()
        try:
            if app is not None and app.styleHints().colorScheme() == Qt.ColorScheme.Dark:
                return "dark"
        except AttributeError:  # Qt < 6.5
            pass
        return "light"


def apply(name: str) -> None:
    """Troca o tema ("light" ou "dark") de todo o programa, na hora."""
    global current
    current = name if name in THEMES else "light"
    C.clear()
    C.update(THEMES[current])
    app = QApplication.instance()
    if app is None:
        return
    try:  # impede o Windows de misturar o tema dele com o nosso (Qt 6.8+)
        app.styleHints().setColorScheme(Qt.ColorScheme.Dark if current == "dark" else Qt.ColorScheme.Light)
    except AttributeError:
        pass
    app.setPalette(palette())
    app.setStyleSheet(build_stylesheet())
    for w in app.allWidgets():
        w.update()
