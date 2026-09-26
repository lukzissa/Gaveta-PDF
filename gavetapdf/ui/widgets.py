"""Componentes reutilizáveis: lista de arquivos com arrastar e soltar, pasta de saída etc."""
from __future__ import annotations

import os

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from .. import paths
from ..core.common import IMAGE_EXTENSIONS, human_size
from . import theme
from ..i18n import tr

PDF_EXT = {".pdf"}
PDF_FILTER = tr("Arquivos PDF (*.pdf)")
IMAGE_FILTER = tr("Imagens (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)")
PDF_IMAGE_FILTER = tr("PDFs e imagens (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)")


def settings() -> QSettings:
    """Configurações num .ini ao lado do programa (nada no registro do Windows)."""
    return QSettings(paths.ini_path(), QSettings.IniFormat)


def last_dir() -> str:
    d = settings().value("lastDir", "")
    return d if d and os.path.isdir(d) else os.path.expanduser("~")


def remember_dir(path: str) -> None:
    d = path if os.path.isdir(path) else os.path.dirname(path)
    if d:
        settings().setValue("lastDir", d)


def save_file_dialog(parent: QWidget, title: str, suggested: str, filt: str = PDF_FILTER) -> str:
    start = suggested if os.path.isabs(suggested) else os.path.join(last_dir(), suggested)
    path, _ = QFileDialog.getSaveFileName(parent, title, start, filt)
    if path:
        remember_dir(path)
    return path


def choose_dir_dialog(parent: QWidget, title: str, start: str = "") -> str:
    path = QFileDialog.getExistingDirectory(parent, title, start or last_dir())
    if path:
        remember_dir(path)
    return path


def collect_files(paths: list[str], extensions: set[str]) -> list[str]:
    """Aceita arquivos e pastas (inclui os arquivos compatíveis da pasta)."""
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p), key=str.lower):
                full = os.path.join(p, name)
                if os.path.isfile(full) and os.path.splitext(name)[1].lower() in extensions:
                    out.append(full)
        elif os.path.splitext(p)[1].lower() in extensions:
            out.append(p)
    return out


class DropList(QListWidget):
    """QListWidget que aceita arquivos arrastados do Explorer e mostra um texto quando vazio."""

    filesDropped = Signal(list)

    def __init__(self, placeholder: str, extensions: set[str], parent=None) -> None:
        super().__init__(parent)
        self.placeholder = placeholder
        self.extensions = extensions
        self.setAcceptDrops(True)
        self.setObjectName("dropList")

    def _set_dragging(self, on: bool) -> None:
        self.setProperty("dragging", "true" if on else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            self._set_dragging(True)
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dragLeaveEvent(self, e):
        self._set_dragging(False)
        super().dragLeaveEvent(e)

    def dropEvent(self, e):
        self._set_dragging(False)
        if e.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
            files = collect_files(paths, self.extensions)
            if files:
                self.filesDropped.emit(files)
            e.acceptProposedAction()
        else:
            super().dropEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.count() == 0:
            p = QPainter(self.viewport())
            p.setPen(theme.color("muted"))
            p.drawText(self.viewport().rect().adjusted(20, 20, -20, -20),
                       Qt.AlignCenter | Qt.TextWordWrap, self.placeholder)
            p.end()


class FileList(QWidget):
    """Lista de arquivos com botões Adicionar/Remover/Subir/Descer e arrastar e soltar."""

    changed = Signal()

    def __init__(
        self,
        extensions: set[str] = PDF_EXT,
        file_filter: str = PDF_FILTER,
        placeholder: str = tr("Arraste arquivos PDF para cá\nou clique em “Adicionar”"),
        single: bool = False,
        reorder: bool = True,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.extensions = extensions
        self.file_filter = file_filter
        self.single = single

        self.list = DropList(placeholder, extensions)
        self.list.setSelectionMode(QListWidget.ExtendedSelection)
        if reorder and not single:
            self.list.setDragDropMode(QListWidget.InternalMove)
            self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.filesDropped.connect(self.add_files)
        self.list.model().rowsMoved.connect(lambda *a: self.changed.emit())
        if single:
            self.list.setMaximumHeight(90)

        self.btn_add = QPushButton(theme.icon("add"), tr(" Escolher arquivo") if single else tr(" Adicionar"))
        self.btn_add.clicked.connect(self.browse)
        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        buttons.addWidget(self.btn_add)
        self.btn_remove = QPushButton(theme.icon("remove"), tr(" Remover"))
        self.btn_remove.clicked.connect(self.remove_selected)
        buttons.addWidget(self.btn_remove)
        if not single:
            if reorder:
                self.btn_up = QPushButton(theme.icon("up"), "")
                self.btn_up.setToolTip(tr("Mover para cima"))
                self.btn_up.clicked.connect(lambda: self.move(-1))
                self.btn_down = QPushButton(theme.icon("down"), "")
                self.btn_down.setToolTip(tr("Mover para baixo"))
                self.btn_down.clicked.connect(lambda: self.move(1))
                buttons.addWidget(self.btn_up)
                buttons.addWidget(self.btn_down)
            self.btn_clear = QPushButton(theme.icon("clear"), tr(" Limpar"))
            self.btn_clear.clicked.connect(self.clear)
            buttons.addWidget(self.btn_clear)
        buttons.addStretch(1)
        self.info = QLabel("")
        self.info.setObjectName("hint")
        buttons.addWidget(self.info)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(self.list, 1)
        lay.addLayout(buttons)
        self.changed.connect(self._update_info)
        self._update_info()

    # --- API
    def files(self) -> list[str]:
        return [self.list.item(i).data(Qt.UserRole) for i in range(self.list.count())]

    def add_files(self, paths: list[str]) -> None:
        paths = collect_files(paths, self.extensions)
        if not paths:
            return
        if self.single:
            self.list.clear()
            paths = paths[:1]
        existing = set(self.files())
        for p in paths:
            if p in existing:
                continue
            try:
                size = human_size(os.path.getsize(p))
            except OSError:
                size = ""
            item = QListWidgetItem(theme.icon("file", "muted"), f"{os.path.basename(p)}   ·   {size}")
            item.setData(Qt.UserRole, p)
            item.setToolTip(p)
            self.list.addItem(item)
        remember_dir(paths[0])
        self.changed.emit()

    def browse(self) -> None:
        if self.single:
            path, _ = QFileDialog.getOpenFileName(self, tr("Escolher arquivo"), last_dir(), self.file_filter)
            paths = [path] if path else []
        else:
            paths, _ = QFileDialog.getOpenFileNames(self, tr("Adicionar arquivos"), last_dir(), self.file_filter)
        if paths:
            self.add_files(paths)

    def remove_selected(self) -> None:
        for item in self.list.selectedItems() or ([self.list.item(0)] if self.single and self.list.count() else []):
            self.list.takeItem(self.list.row(item))
        self.changed.emit()

    def clear(self) -> None:
        self.list.clear()
        self.changed.emit()

    def move(self, delta: int) -> None:
        rows = sorted({self.list.row(i) for i in self.list.selectedItems()}, reverse=delta > 0)
        if not rows:
            return
        if (delta < 0 and rows[0] == 0) or (delta > 0 and rows[0] == self.list.count() - 1):
            return
        for r in rows:
            item = self.list.takeItem(r)
            self.list.insertItem(r + delta, item)
            item.setSelected(True)
        self.changed.emit()

    def _update_info(self) -> None:
        n = self.list.count()
        self.info.setText("" if self.single or n == 0 else tr("{0} arquivo(s)", n))


class OutputDir(QWidget):
    """Escolha entre salvar ao lado do original ou numa pasta específica."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rb_same = QRadioButton(tr("Na mesma pasta do arquivo original"))
        self.rb_custom = QRadioButton(tr("Em outra pasta:"))
        self.rb_same.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.rb_same)
        grp.addButton(self.rb_custom)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(tr("Escolha uma pasta…"))
        self.edit.setEnabled(False)
        self.btn = QPushButton(theme.icon("folder"), "")
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self._browse)
        self.rb_custom.toggled.connect(self.edit.setEnabled)
        self.rb_custom.toggled.connect(self.btn.setEnabled)

        row = QHBoxLayout()
        row.addWidget(self.rb_custom)
        row.addWidget(self.edit, 1)
        row.addWidget(self.btn)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        lay.addWidget(self.rb_same)
        lay.addLayout(row)

    def _browse(self) -> None:
        d = choose_dir_dialog(self, tr("Salvar em…"), self.edit.text())
        if d:
            self.edit.setText(d)

    def resolve(self, source: str) -> str | None:
        """Pasta de saída para `source`; None se o usuário ainda não escolheu uma."""
        if self.rb_same.isChecked():
            return os.path.dirname(os.path.abspath(source))
        d = self.edit.text().strip()
        return d or None


def card(*widgets: QWidget, spacing: int = 10) -> QFrame:
    f = QFrame()
    f.setObjectName("card")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(spacing)
    for w in widgets:
        if isinstance(w, QWidget):
            lay.addWidget(w)
        else:
            lay.addLayout(w)
    return f


def section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("sectionLabel")
    return lbl


def hint(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("hint")
    lbl.setWordWrap(True)
    return lbl
