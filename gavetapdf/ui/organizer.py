"""Organizador visual: miniaturas de páginas para reordenar, girar, excluir e combinar."""
from __future__ import annotations

import os
import queue

import pymupdf
from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QColor, QIcon, QImage, QKeySequence, QPainter, QPixmap, QShortcut, QTransform
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QSlider

from .. import APP_NAME
from ..core import organize
from ..core.common import IMAGE_EXTENSIONS, PdfError, open_pdf, stem, unique_path
from . import theme
from .pages import BasePage, Outcome
from .widgets import PDF_EXT, PDF_IMAGE_FILTER, DropList, last_dir, remember_dir, save_file_dialog
from ..i18n import tr

ROLE_REF = Qt.UserRole
ROLE_IMAGE = Qt.UserRole + 1
ROLE_KEY = Qt.UserRole + 2
THUMB_RENDER_WIDTH = 260  # px — renderizado uma vez, depois só redimensionado


class ThumbLoader(QThread):
    """Renderiza miniaturas numa thread separada, na ordem em que foram pedidas."""

    loaded = Signal(int, QImage)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.jobs: queue.Queue = queue.Queue()
        self._docs: dict[str, pymupdf.Document] = {}

    def request(self, key: int, path: str, index: int) -> None:
        self.jobs.put((key, path, index))

    def stop(self) -> None:
        self.jobs.put(None)
        self.wait(3000)

    def run(self) -> None:
        while True:
            job = self.jobs.get()
            if job is None:
                break
            key, path, index = job
            try:
                doc = self._docs.get(path)
                if doc is None:
                    doc = self._docs[path] = open_pdf(path)
                page = doc[index]
                zoom = THUMB_RENDER_WIDTH / max(page.rect.width, page.rect.height) * 1.0
                pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888).copy()
                self.loaded.emit(key, img)
            except Exception:  # noqa: BLE001 - miniatura com falha fica com o quadro vazio
                continue
        for d in self._docs.values():
            d.close()


class PageGrid(DropList):
    def __init__(self, parent=None):
        super().__init__(tr("Arraste PDFs ou imagens para cá\n\n"
                         "Depois arraste as miniaturas para mudar a ordem,\n"
                         "use os botões para girar ou excluir páginas."),
                         PDF_EXT | IMAGE_EXTENSIONS, parent)
        self.setObjectName("pageGrid")
        self.setViewMode(QListWidget.IconMode)
        self.setFlow(QListWidget.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Snap)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setUniformItemSizes(True)
        self.setSpacing(10)


class OrganizerPage(BasePage):
    title = tr("Organizar páginas")
    subtitle = (tr("Monte um novo PDF escolhendo páginas de um ou vários arquivos. "
                "Arraste para reordenar; selecione várias com Ctrl ou Shift."))

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self._next_key = 0
        self._items: dict[int, QListWidgetItem] = {}
        self.thumb_size = 150

        self.loader = ThumbLoader(self)
        self.loader.loaded.connect(self._on_thumb)
        self.loader.start()

        self.grid = PageGrid()
        self.grid.filesDropped.connect(self.add_files)
        self.grid.model().rowsMoved.connect(lambda *a: self._renumber())
        self.grid.itemSelectionChanged.connect(self._update_buttons)

        def btn(ic, text, tip, slot):
            b = QPushButton(theme.icon(ic), text)
            b.setToolTip(tip)
            b.clicked.connect(slot)
            return b

        self.b_add = btn("add", tr(" Adicionar PDF"), tr("Adicionar PDFs ou imagens"), self._browse)
        self.b_left = btn("rotl", "", tr("Girar para a esquerda (Ctrl+L)"), lambda: self._rotate(-90))
        self.b_right = btn("rotr", "", tr("Girar para a direita (Ctrl+R)"), lambda: self._rotate(90))
        self.b_del = btn("clear", tr(" Excluir"), tr("Excluir páginas selecionadas (Delete)"), self._delete)
        self.b_clear = btn("remove", tr(" Limpar tudo"), tr("Remover todas as páginas"), self._clear)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(90, 240)
        self.slider.setValue(self.thumb_size)
        self.slider.setFixedWidth(120)
        self.slider.setToolTip(tr("Tamanho das miniaturas"))
        self.slider.valueChanged.connect(self._set_size)
        self.count = QLabel("")
        self.count.setObjectName("hint")

        bar = QHBoxLayout()
        bar.setSpacing(6)
        for w in (self.b_add, self.b_left, self.b_right, self.b_del, self.b_clear):
            bar.addWidget(w)
        bar.addStretch(1)
        bar.addWidget(self.count)
        bar.addSpacing(12)
        zoom = QLabel(tr("Zoom"))
        zoom.setObjectName("hint")
        bar.addWidget(zoom)
        bar.addWidget(self.slider)
        self.body.addLayout(bar)
        self.body.addWidget(self.grid, 1)

        QShortcut(QKeySequence.Delete, self.grid, activated=self._delete)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: self._rotate(-90))
        QShortcut(QKeySequence("Ctrl+R"), self, activated=lambda: self._rotate(90))
        self._set_size(self.thumb_size)
        self._update_buttons()

    def action_text(self):
        return tr("Salvar PDF")

    def shutdown(self):
        self.loader.stop()

    # ---------------------------------------------------------- páginas
    def _browse(self):
        from PySide6.QtWidgets import QFileDialog

        paths, _ = QFileDialog.getOpenFileNames(self, tr("Adicionar arquivos"), last_dir(), PDF_IMAGE_FILTER)
        if paths:
            self.add_files(paths)

    def add_files(self, paths: list[str]) -> None:
        errors = []
        for path in paths:
            try:
                with open_pdf(path) as doc:
                    n = doc.page_count
            except PdfError as exc:
                errors.append(str(exc))
                continue
            remember_dir(path)
            for i in range(n):
                self._add_page(path, i)
        self._renumber()
        if errors:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, APP_NAME, "\n\n".join(errors))

    def _placeholder(self) -> QIcon:
        pm = QPixmap(self.thumb_size, int(self.thumb_size * 1.414))
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setPen(theme.color("border"))
        p.setBrush(QColor("#FFFFFF"))
        w = int(self.thumb_size / 1.414)
        p.drawRect((self.thumb_size - w) // 2, 0, w - 1, pm.height() - 1)
        p.end()
        return QIcon(pm)

    def _add_page(self, path: str, index: int) -> None:
        key = self._next_key
        self._next_key += 1
        item = QListWidgetItem(self._placeholder(), "")
        item.setData(ROLE_REF, organize.PageRef(path, index, 0))
        item.setData(ROLE_KEY, key)
        item.setToolTip(tr("{0} — página {1}", os.path.basename(path), index + 1))
        item.setTextAlignment(Qt.AlignHCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)
        self.grid.addItem(item)
        self._items[key] = item
        self.loader.request(key, path, index)

    def _on_thumb(self, key: int, img: QImage) -> None:
        item = self._items.get(key)
        if item is None:
            return
        item.setData(ROLE_IMAGE, img)
        self._refresh_icon(item)

    def _refresh_icon(self, item: QListWidgetItem) -> None:
        img: QImage | None = item.data(ROLE_IMAGE)
        if img is None:
            item.setIcon(self._placeholder())
            return
        ref: organize.PageRef = item.data(ROLE_REF)
        if ref.rotation % 360:
            img = img.transformed(QTransform().rotate(ref.rotation), Qt.SmoothTransformation)
        box = QSize(self.thumb_size, int(self.thumb_size * 1.414))
        scaled = img.scaled(box, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # centraliza numa tela fixa para todas as células terem o mesmo tamanho
        canvas = QPixmap(box)
        canvas.fill(Qt.transparent)
        p = QPainter(canvas)
        x = (box.width() - scaled.width()) // 2
        y = (box.height() - scaled.height()) // 2
        p.fillRect(x + 2, y + 2, scaled.width(), scaled.height(), QColor(0, 0, 0, 30))  # sombra
        p.drawImage(x, y, scaled)
        p.setPen(theme.color("border"))
        p.drawRect(x, y, scaled.width() - 1, scaled.height() - 1)
        p.end()
        item.setIcon(QIcon(canvas))

    def _renumber(self) -> None:
        multi = len({self.grid.item(i).data(ROLE_REF).path for i in range(self.grid.count())}) > 1
        for i in range(self.grid.count()):
            item = self.grid.item(i)
            ref: organize.PageRef = item.data(ROLE_REF)
            label = f"{i + 1}"
            if multi:
                name = stem(ref.path)
                label += tr("\n{0} p.{1}", name[:18] + '…' if len(name) > 19 else name, ref.index + 1)
            item.setText(label)
        n = self.grid.count()
        self.count.setText(tr("{0} página(s)", n) if n else "")
        self._update_buttons()

    def _rotate(self, degrees: int) -> None:
        for item in self.grid.selectedItems():
            ref: organize.PageRef = item.data(ROLE_REF)
            ref = organize.PageRef(ref.path, ref.index, (ref.rotation + degrees) % 360)
            item.setData(ROLE_REF, ref)
            self._refresh_icon(item)

    def _delete(self) -> None:
        for item in self.grid.selectedItems():
            self._items.pop(item.data(ROLE_KEY), None)
            self.grid.takeItem(self.grid.row(item))
        self._renumber()

    def _clear(self) -> None:
        self.grid.clear()
        self._items.clear()
        self._renumber()

    def _set_size(self, size: int) -> None:
        self.thumb_size = size
        self.grid.setIconSize(QSize(size, int(size * 1.414)))
        self.grid.setGridSize(QSize(size + 24, int(size * 1.414) + 58))
        for i in range(self.grid.count()):
            self._refresh_icon(self.grid.item(i))

    def _update_buttons(self) -> None:
        has_sel = bool(self.grid.selectedItems())
        for b in (self.b_left, self.b_right, self.b_del):
            b.setEnabled(has_sel)
        self.b_clear.setEnabled(self.grid.count() > 0)
        self.action.setEnabled(self.grid.count() > 0)

    # ---------------------------------------------------------- salvar
    def execute(self):
        refs = [self.grid.item(i).data(ROLE_REF) for i in range(self.grid.count())]
        if not refs:
            raise PdfError(tr("Adicione páginas antes de salvar."))
        first = refs[0].path
        suggested = unique_path(os.path.join(os.path.dirname(first), tr("{0} (organizado).pdf", stem(first))))
        out = save_file_dialog(self, tr("Salvar PDF organizado"), suggested)
        if not out:
            return
        self.run(lambda ctx: organize.build_from_pages(refs, out, ctx),
                 lambda r: Outcome(tr("PDF salvo com {0} página(s).", len(refs)), [out]),
                 tr("Salvando PDF…"))
