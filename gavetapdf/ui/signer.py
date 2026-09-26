"""Assinar PDF: criar a assinatura (desenhar, digitar ou importar) e posicioná-la nas páginas."""
from __future__ import annotations

import math
import os

import pymupdf
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QImage,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APP_NAME
from ..core import sign
from ..core.common import PdfError, open_pdf, stem, unique_path
from . import theme
from .pages import BasePage, Outcome, _two_columns
from .widgets import IMAGE_FILTER, PDF_FILTER, card, hint, last_dir, remember_dir, save_file_dialog, section, settings
from ..i18n import tr

INK_COLORS = [(tr("Azul"), "#1B3A8C"), (tr("Preto"), "#1A1A1A")]
HANDWRITING_FONTS = ["Segoe Script", "Lucida Handwriting", "Ink Free", "Segoe Print",
                     "Brush Script MT", "Freestyle Script", "Mistral"]
DEFAULT_WIDTH = 150.0  # pontos (≈ 5,3 cm) — largura inicial da assinatura na página
MIN_WIDTH = 24.0
HANDLE = 10  # px
PAPER_BORDER = "#D0D5DD"  # a área da assinatura é sempre "papel branco", nos dois temas
PAPER_HINT = "#667085"


def image_to_png(img: QImage) -> bytes:
    buf = QBuffer()
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return bytes(buf.data())


# ================================================================ criação da assinatura
class DrawPad(QWidget):
    """Área para desenhar a assinatura com o mouse, caneta ou dedo."""

    changed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.strokes: list[list[QPointF]] = []
        self.color = QColor(INK_COLORS[0][1])
        self.setMinimumSize(560, 220)
        self.setCursor(Qt.CrossCursor)
        self.setAttribute(Qt.WA_AcceptTouchEvents, False)

    def set_color(self, color: str) -> None:
        self.color = QColor(color)
        self.update()

    def clear(self) -> None:
        self.strokes.clear()
        self.update()
        self.changed.emit()

    def undo(self) -> None:
        if self.strokes:
            self.strokes.pop()
            self.update()
            self.changed.emit()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.strokes.append([e.position()])
            self.update()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self.strokes:
            self.strokes[-1].append(e.position())
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.changed.emit()

    def _path(self) -> QPainterPath:
        path = QPainterPath()
        for pts in self.strokes:
            path.moveTo(pts[0])
            if len(pts) == 1:
                path.lineTo(pts[0] + QPointF(0.5, 0.5))
                continue
            # curva suave passando pelos pontos médios
            for a, b in zip(pts[:-1], pts[1:]):
                path.quadTo(a, (a + b) / 2)
            path.lineTo(pts[-1])
        return path

    def _pen(self) -> QPen:
        return QPen(self.color, 2.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QColor(PAPER_BORDER))
        p.setBrush(QColor("#FFFFFF"))
        p.drawRoundedRect(r, 10, 10)
        base_y = self.height() * 0.72
        p.setPen(QPen(QColor("#C9CED6"), 1, Qt.DashLine))
        p.drawLine(QPointF(30, base_y), QPointF(self.width() - 30, base_y))
        if not self.strokes:
            p.setPen(QColor(PAPER_HINT))
            p.drawText(QRectF(0, 0, self.width(), base_y - 8), Qt.AlignCenter,
                       tr("Assine aqui com o mouse, a caneta ou o dedo"))
        p.setPen(self._pen())
        p.setBrush(Qt.NoBrush)
        p.drawPath(self._path())
        p.end()

    def to_image(self) -> QImage | None:
        if not self.strokes:
            return None
        path = self._path()
        r = path.boundingRect().adjusted(-4, -4, 4, 4)
        scale = 3  # renderiza em alta resolução para ficar nítida na impressão
        img = QImage(max(1, math.ceil(r.width() * scale)), max(1, math.ceil(r.height() * scale)),
                     QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(scale, scale)
        p.translate(-r.topLeft())
        p.setPen(self._pen())
        p.drawPath(path)
        p.end()
        return img


def available_handwriting_fonts() -> list[str]:
    families = set(QFontDatabase.families())
    return [f for f in HANDWRITING_FONTS if f in families]


def text_image(text: str, family: str, color: str) -> QImage | None:
    text = text.strip()
    if not text:
        return None
    font = QFont(family)
    font.setPixelSize(140)
    if family not in QFontDatabase.families():
        font.setItalic(True)
    fm = QFontMetricsF(font)
    # Fontes cursivas costumam "vazar" da caixa normal do texto: une as duas medidas.
    br = fm.boundingRect(text).united(fm.tightBoundingRect(text)).adjusted(-16, -12, 16, 12)
    img = QImage(math.ceil(br.width()), math.ceil(br.height()), QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    p.setFont(font)
    p.setPen(QColor(color))
    p.drawText(QPointF(-br.left(), -br.top()), text)
    p.end()
    return img


class SignatureView(QLabel):
    """Mostra a assinatura atual sobre fundo branco."""

    def __init__(self, empty_text: str, height: int = 96, parent=None) -> None:
        super().__init__(parent)
        self.empty_text = empty_text
        self.image: QImage | None = None
        self.setMinimumHeight(height)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"background: #FFFFFF; color: {PAPER_HINT}; border: 1px solid {PAPER_BORDER}; "
                           "border-radius: 8px;")
        self.set_image(None)

    def set_image(self, img: QImage | None) -> None:
        self.image = img
        self.setText("" if img else self.empty_text)
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.image is None or self.image.isNull():
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        area = QRectF(self.rect()).adjusted(12, 10, -12, -10)
        size = self.image.size().toSizeF().scaled(area.size(), Qt.KeepAspectRatio)
        target = QRectF(area.center().x() - size.width() / 2, area.center().y() - size.height() / 2,
                        size.width(), size.height())
        p.drawImage(target, self.image)
        p.end()


class SignatureDialog(QDialog):
    """Três formas de criar a assinatura: desenhar, digitar o nome ou importar uma imagem."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Criar assinatura"))
        self.setMinimumWidth(640)
        self.result_png: bytes | None = None
        self._imported: bytes | None = None

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._tab_draw(), tr("Desenhar"))
        self.tabs.addTab(self._tab_type(), tr("Digitar"))
        self.tabs.addTab(self._tab_import(), tr("Importar imagem"))
        self.tabs.currentChanged.connect(self._update_ok)

        self.cmb_color = QComboBox()
        for name, value in INK_COLORS:
            self.cmb_color.addItem(name, value)
        self.cmb_color.currentIndexChanged.connect(self._color_changed)
        self.cb_remember = QCheckBox(tr("Lembrar esta assinatura neste computador"))
        self.cb_remember.setChecked(True)
        self.cb_remember.setToolTip(tr("Fica salva só neste computador, para reutilizar na próxima vez."))

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText(tr("Usar assinatura"))
        self.buttons.button(QDialogButtonBox.Ok).setObjectName("primary")
        self.buttons.button(QDialogButtonBox.Cancel).setText(tr("Cancelar"))
        self.buttons.accepted.connect(self._accept)
        self.buttons.rejected.connect(self.reject)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel(tr("Cor da tinta:")))
        color_row.addWidget(self.cmb_color)
        color_row.addStretch(1)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)
        lay.addWidget(self.tabs, 1)
        lay.addLayout(color_row)
        lay.addWidget(self.cb_remember)
        lay.addWidget(self.buttons)
        self._update_ok()

    # --- abas
    def _tab_draw(self) -> QWidget:
        w = QWidget()
        self.pad = DrawPad()
        self.pad.changed.connect(self._update_ok)
        b_undo = QPushButton(theme.icon("rotl"), tr(" Desfazer"))
        b_undo.clicked.connect(self.pad.undo)
        b_clear = QPushButton(theme.icon("clear"), tr(" Limpar"))
        b_clear.clicked.connect(self.pad.clear)
        row = QHBoxLayout()
        row.addWidget(b_undo)
        row.addWidget(b_clear)
        row.addStretch(1)
        QShortcut(QKeySequence.Undo, w, activated=self.pad.undo)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addWidget(self.pad, 1)
        lay.addLayout(row)
        return w

    def _tab_type(self) -> QWidget:
        w = QWidget()
        self.ed_name = QLineEdit()
        self.ed_name.setPlaceholderText(tr("Digite seu nome"))
        self.cmb_font = QComboBox()
        fonts = available_handwriting_fonts()
        for f in fonts or [self.font().family()]:
            self.cmb_font.addItem(f, f)
        self.type_view = SignatureView(tr("A prévia aparece aqui"), 150)
        self.ed_name.textChanged.connect(self._update_typed)
        self.cmb_font.currentIndexChanged.connect(self._update_typed)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addWidget(section(tr("Nome")))
        lay.addWidget(self.ed_name)
        lay.addWidget(section(tr("Estilo")))
        lay.addWidget(self.cmb_font)
        lay.addWidget(self.type_view, 1)
        return w

    def _tab_import(self) -> QWidget:
        w = QWidget()
        b_open = QPushButton(theme.icon("folder"), tr(" Escolher imagem…"))
        b_open.clicked.connect(self._browse_image)
        self.cb_clean = QCheckBox(tr("Remover o fundo branco e recortar as bordas"))
        self.cb_clean.setChecked(True)
        self.cb_clean.toggled.connect(self._update_imported)
        self.import_view = SignatureView(tr("Escolha uma foto ou digitalização da sua assinatura\n"
                                         "(de preferência em papel branco, com caneta escura)"), 150)
        self._import_raw: bytes | None = None
        row = QHBoxLayout()
        row.addWidget(b_open)
        row.addStretch(1)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addLayout(row)
        lay.addWidget(self.cb_clean)
        lay.addWidget(self.import_view, 1)
        return w

    # --- eventos
    def _color_changed(self):
        self.pad.set_color(self.cmb_color.currentData())
        self._update_typed()

    def _update_typed(self):
        self.type_view.set_image(text_image(self.ed_name.text(), self.cmb_font.currentData(),
                                            self.cmb_color.currentData()))
        self._update_ok()

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Imagem da assinatura"), last_dir(), IMAGE_FILTER)
        if not path:
            return
        remember_dir(path)
        try:
            with open(path, "rb") as fh:
                self._import_raw = fh.read()
        except OSError as exc:
            QMessageBox.warning(self, APP_NAME, tr("Não foi possível abrir a imagem.\n\n{0}", exc))
            return
        self._update_imported()

    def _update_imported(self):
        self._imported = None
        if self._import_raw:
            try:
                data = sign.clean_signature_image(self._import_raw) if self.cb_clean.isChecked() else self._import_raw
            except PdfError as exc:
                QMessageBox.warning(self, APP_NAME, str(exc))
                data = None
            img = QImage.fromData(data) if data else QImage()
            if data and not img.isNull():
                self._imported = image_to_png(img)
                self.import_view.set_image(img)
            else:
                self.import_view.set_image(None)
        self._update_ok()

    def _current_png(self) -> bytes | None:
        idx = self.tabs.currentIndex()
        if idx == 0:
            img = self.pad.to_image()
            return image_to_png(img) if img else None
        if idx == 1:
            img = self.type_view.image
            return image_to_png(img) if img else None
        return self._imported

    def _update_ok(self):
        idx = self.tabs.currentIndex()
        ready = [bool(self.pad.strokes), bool(self.ed_name.text().strip()), self._imported is not None][idx]
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(ready)
        self.cmb_color.setEnabled(idx != 2)

    def _accept(self):
        self.result_png = self._current_png()
        if self.result_png:
            self.accept()


# ================================================================ pré-visualização da página
class PagePreview(QWidget):
    """Mostra uma página do PDF; clique para posicionar a assinatura, arraste para mover."""

    changed = Signal()
    needSignature = Signal()
    fileDropped = Signal(str)
    pageStep = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.doc: pymupdf.Document | None = None
        self.page_index = 0
        self.placements: dict[int, list[QRectF]] = {}  # em pontos, coordenadas da página exibida
        self.signature: QImage | None = None
        self.selected: int | None = None
        self._cache: tuple[tuple, QPixmap] | None = None
        self._drag: tuple[str, QPointF, QRectF] | None = None  # (modo, ponto inicial, retângulo inicial)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(360, 360)

    # --- estado
    def set_document(self, doc: pymupdf.Document | None) -> None:
        self.doc = doc
        self.page_index = 0
        self.placements.clear()
        self.selected = None
        self._cache = None
        self.update()
        self.changed.emit()

    def set_page(self, index: int) -> None:
        if self.doc is not None and 0 <= index < self.doc.page_count and index != self.page_index:
            self.page_index = index
            self.selected = None
            self.update()
            self.changed.emit()

    def set_signature(self, img: QImage | None) -> None:
        """Troca a imagem mantendo a largura e o centro das assinaturas já posicionadas."""
        self.signature = img
        if img:
            for rects in self.placements.values():
                for i, r in enumerate(rects):
                    c = r.center()
                    h = r.width() * self.aspect()
                    rects[i] = QRectF(r.left(), c.y() - h / 2, r.width(), h)
        self.update()
        self.changed.emit()

    def aspect(self) -> float:
        s = self.signature
        return s.height() / s.width() if s and s.width() else 0.35

    def rects(self) -> list[QRectF]:
        return self.placements.setdefault(self.page_index, [])

    def total(self) -> int:
        return sum(len(v) for v in self.placements.values())

    def page_size(self, index: int | None = None) -> tuple[float, float]:
        r = self.doc[self.page_index if index is None else index].rect
        return r.width, r.height

    def remove_selected(self) -> None:
        if self.selected is not None:
            self.rects().pop(self.selected)
            self.selected = None
            self.update()
            self.changed.emit()

    def clear_page(self) -> None:
        self.placements.pop(self.page_index, None)
        self.selected = None
        self.update()
        self.changed.emit()

    def clear_all(self) -> None:
        self.placements.clear()
        self.selected = None
        self.update()
        self.changed.emit()

    def repeat_on_all_pages(self) -> int:
        """Copia a assinatura selecionada (ou a última da página) para as demais páginas."""
        rects = self.rects()
        if self.doc is None or not rects:
            return 0
        src = rects[self.selected if self.selected is not None else -1]
        pw, ph = self.page_size()
        added = 0
        for i in range(self.doc.page_count):
            if i == self.page_index:
                continue
            w2, h2 = self.page_size(i)
            # mesma posição relativa (ex.: canto inferior direito continua no canto)
            cx = src.center().x() / pw * w2
            cy = src.center().y() / ph * h2
            r = QRectF(0, 0, src.width(), src.height())
            r.moveCenter(QPointF(cx, cy))
            self.placements.setdefault(i, []).append(self._clamp(r, w2, h2))
            added += 1
        self.changed.emit()
        return added

    def all_placements(self) -> list[sign.Placement]:
        out = []
        for page, rects in sorted(self.placements.items()):
            for r in rects:
                out.append(sign.Placement(page, (r.left(), r.top(), r.right(), r.bottom())))
        return out

    # --- geometria
    def _layout(self) -> tuple[float, QPointF]:
        """Escala (px por ponto) e origem da página no widget."""
        pw, ph = self.page_size()
        pad = 16
        s = min((self.width() - 2 * pad) / pw, (self.height() - 2 * pad) / ph)
        s = max(s, 0.05)
        return s, QPointF((self.width() - pw * s) / 2, (self.height() - ph * s) / 2)

    def _to_widget(self, r: QRectF) -> QRectF:
        s, o = self._layout()
        return QRectF(o.x() + r.left() * s, o.y() + r.top() * s, r.width() * s, r.height() * s)

    def _to_page(self, pt: QPointF) -> QPointF:
        s, o = self._layout()
        return QPointF((pt.x() - o.x()) / s, (pt.y() - o.y()) / s)

    @staticmethod
    def _clamp(r: QRectF, pw: float, ph: float) -> QRectF:
        r = QRectF(r)
        if r.width() > pw:
            r.setWidth(pw)
        if r.height() > ph:
            r.setHeight(ph)
        r.moveLeft(min(max(r.left(), 0), pw - r.width()))
        r.moveTop(min(max(r.top(), 0), ph - r.height()))
        return r

    def _hit(self, pos: QPointF) -> tuple[str, int] | None:
        rects = self.rects()
        for i in reversed(range(len(rects))):
            w = self._to_widget(rects[i])
            if i == self.selected:
                if QRectF(w.right() - HANDLE, w.top() - HANDLE, HANDLE * 2, HANDLE * 2).contains(pos):
                    return "delete", i
                if QRectF(w.right() - HANDLE, w.bottom() - HANDLE, HANDLE * 2, HANDLE * 2).contains(pos):
                    return "resize", i
            if w.contains(pos):
                return "move", i
        return None

    # --- mouse e teclado
    def mousePressEvent(self, e):
        if self.doc is None or e.button() != Qt.LeftButton:
            return
        self.setFocus()
        pos = e.position()
        hit = self._hit(pos)
        if hit and hit[0] == "delete":
            self.selected = hit[1]
            self.remove_selected()
            return
        if hit:
            self.selected = hit[1]
            self._drag = (hit[0], pos, QRectF(self.rects()[hit[1]]))
            self.update()
            self.changed.emit()
            return
        pw, ph = self.page_size()
        p = self._to_page(pos)
        if not (0 <= p.x() <= pw and 0 <= p.y() <= ph):
            self.selected = None
            self.update()
            self.changed.emit()
            return
        if self.signature is None:
            self.needSignature.emit()
            return
        w = min(DEFAULT_WIDTH, pw * 0.45)
        r = QRectF(0, 0, w, w * self.aspect())
        r.moveCenter(p)
        self.rects().append(self._clamp(r, pw, ph))
        self.selected = len(self.rects()) - 1
        self._drag = ("move", pos, QRectF(self.rects()[-1]))
        self.update()
        self.changed.emit()

    def mouseMoveEvent(self, e):
        pos = e.position()
        if self._drag and self.selected is not None:
            mode, start, orig = self._drag
            s, _ = self._layout()
            dx, dy = (pos.x() - start.x()) / s, (pos.y() - start.y()) / s
            pw, ph = self.page_size()
            if mode == "move":
                r = orig.translated(dx, dy)
            else:
                w = max(MIN_WIDTH, orig.width() + dx)
                w = min(w, pw - orig.left(), (ph - orig.top()) / self.aspect())
                r = QRectF(orig.left(), orig.top(), w, w * self.aspect())
            self.rects()[self.selected] = self._clamp(r, pw, ph)
            self.update()
            return
        hit = self._hit(pos) if self.doc is not None else None
        cursor = {"move": Qt.SizeAllCursor, "resize": Qt.SizeFDiagCursor,
                  "delete": Qt.PointingHandCursor}.get(hit[0] if hit else "", Qt.ArrowCursor)
        if not hit and self.doc is not None and self.signature is not None:
            p = self._to_page(pos)
            pw, ph = self.page_size()
            if 0 <= p.x() <= pw and 0 <= p.y() <= ph:
                cursor = Qt.CrossCursor
        self.setCursor(cursor)

    def mouseReleaseEvent(self, e):
        if self._drag:
            self._drag = None
            self.changed.emit()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.remove_selected()
        elif e.key() in (Qt.Key_PageDown, Qt.Key_Right):
            self.pageStep.emit(1)
        elif e.key() in (Qt.Key_PageUp, Qt.Key_Left):
            self.pageStep.emit(-1)
        else:
            super().keyPressEvent(e)

    def wheelEvent(self, e):
        if self.doc is not None:
            self.pageStep.emit(1 if e.angleDelta().y() < 0 else -1)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            if u.isLocalFile() and u.toLocalFile().lower().endswith(".pdf"):
                self.fileDropped.emit(u.toLocalFile())
                e.acceptProposedAction()
                return

    # --- desenho
    def _page_pixmap(self, scale: float) -> QPixmap:
        dpr = self.devicePixelRatioF()
        key = (id(self.doc), self.page_index, round(scale * dpr, 3))
        if self._cache and self._cache[0] == key:
            return self._cache[1]
        z = scale * dpr
        pix = self.doc[self.page_index].get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888).copy()
        pm = QPixmap.fromImage(img)
        pm.setDevicePixelRatio(dpr)
        self._cache = (key, pm)
        return pm

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.fillRect(self.rect(), theme.color("canvas"))
        if self.doc is None:
            p.setPen(QPen(theme.color("dashed"), 1.5, Qt.DashLine))
            p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 10, 10)
            p.setPen(theme.color("muted"))
            p.drawText(self.rect(), Qt.AlignCenter, tr("Arraste um PDF para cá\nou clique em “Abrir PDF”"))
            p.end()
            return
        s, o = self._layout()
        pw, ph = self.page_size()
        page_rect = QRectF(o.x(), o.y(), pw * s, ph * s)
        p.fillRect(page_rect.translated(3, 3), QColor(0, 0, 0, 30))
        try:
            p.drawPixmap(page_rect.topLeft(), self._page_pixmap(s))
        except Exception:  # noqa: BLE001 - página corrompida: mostra só o quadro em branco
            p.fillRect(page_rect, QColor("#FFFFFF"))
        p.setPen(theme.color("border"))
        p.drawRect(page_rect)

        for i, r in enumerate(self.rects()):
            w = self._to_widget(r)
            if self.signature is not None:
                p.drawImage(w, self.signature)
            sel = i == self.selected
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(theme.color("accent" if sel else "muted"), 1.2, Qt.DashLine))
            p.drawRect(w)
            if sel:
                p.setPen(Qt.NoPen)
                p.setBrush(theme.color("accent"))
                p.drawRect(QRectF(w.right() - 5, w.bottom() - 5, 10, 10))  # redimensionar
                p.drawEllipse(QPointF(w.right(), w.top()), 9, 9)  # excluir
                p.setPen(QPen(QColor("#FFFFFF"), 1.8, Qt.SolidLine, Qt.RoundCap))
                c = QPointF(w.right(), w.top())
                p.drawLine(c + QPointF(-3.5, -3.5), c + QPointF(3.5, 3.5))
                p.drawLine(c + QPointF(-3.5, 3.5), c + QPointF(3.5, -3.5))
        p.end()


# ================================================================ tela
class SignPage(BasePage):
    title = tr("Assinar PDF")
    subtitle = (tr("Crie sua assinatura e clique no documento onde ela deve aparecer. "
                "Arraste para mover e use o canto para mudar o tamanho."))

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self.path: str | None = None
        self.png: bytes | None = None

        self.preview = PagePreview()
        self.preview.changed.connect(self._refresh)
        self.preview.needSignature.connect(self._need_signature)
        self.preview.fileDropped.connect(self.load)
        self.preview.pageStep.connect(lambda d: self.spin_page.setValue(self.spin_page.value() + d))

        self.b_open = QPushButton(theme.icon("file"), tr(" Abrir PDF"))
        self.b_open.clicked.connect(self._browse)
        self.file_label = QLabel("")
        self.file_label.setObjectName("hint")
        self.b_prev = QPushButton(theme.icon("up"), "")
        self.b_prev.setToolTip(tr("Página anterior (Page Up)"))
        self.b_prev.clicked.connect(lambda: self.spin_page.setValue(self.spin_page.value() - 1))
        self.spin_page = QSpinBox()
        self.spin_page.setRange(1, 1)
        self.spin_page.setFixedWidth(80)
        self.spin_page.valueChanged.connect(lambda v: self.preview.set_page(v - 1))
        self.of_label = QLabel("")
        self.of_label.setObjectName("hint")
        self.b_next = QPushButton(theme.icon("down"), "")
        self.b_next.setToolTip(tr("Próxima página (Page Down)"))
        self.b_next.clicked.connect(lambda: self.spin_page.setValue(self.spin_page.value() + 1))
        top = QHBoxLayout()
        top.setSpacing(6)
        top.addWidget(self.b_open)
        top.addWidget(self.file_label, 1)
        for w in (self.b_prev, self.spin_page, self.of_label, self.b_next):
            top.addWidget(w)

        left = QWidget()
        l_lay = QVBoxLayout(left)
        l_lay.setContentsMargins(0, 0, 0, 0)
        l_lay.setSpacing(8)
        l_lay.addLayout(top)
        l_lay.addWidget(self.preview, 1)

        # painel da direita
        self.sig_view = SignatureView(tr("Nenhuma assinatura criada"))
        self.b_create = QPushButton(theme.icon("sign"), tr(" Criar assinatura"))
        self.b_create.clicked.connect(self._create_signature)
        self.b_repeat = QPushButton(tr(" Repetir em todas as páginas"))
        self.b_repeat.setToolTip(tr("Coloca a assinatura selecionada na mesma posição em todas as páginas "
                                 "(útil para rubricar)"))
        self.b_repeat.clicked.connect(self._repeat)
        self.b_remove = QPushButton(theme.icon("remove"), tr(" Remover selecionada"))
        self.b_remove.setToolTip(tr("Remover a assinatura selecionada (Delete)"))
        self.b_remove.clicked.connect(self.preview.remove_selected)
        self.b_clear = QPushButton(theme.icon("clear"), tr(" Remover todas"))
        self.b_clear.clicked.connect(self.preview.clear_all)
        self.count_label = hint("")

        opts = card(section(tr("Sua assinatura")), self.sig_view, self.b_create,
                    section(tr("Posicionar")),
                    hint(tr("Clique na página para colocar a assinatura. Selecione e aperte Delete para remover.")),
                    self.b_repeat, self.b_remove, self.b_clear, self.count_label,
                    hint(tr("Esta é uma assinatura visual (imagem). Ela não substitui a assinatura digital "
                         "com certificado (ICP-Brasil ou gov.br) quando esta for exigida.")))
        self.body.addLayout(_two_columns(left, opts, 300), 1)

        saved = settings().value("signaturePng")
        if isinstance(saved, (bytes, QByteArray)) and len(saved):
            self._set_signature(bytes(saved))
        self._refresh()

    def action_text(self):
        return tr("Salvar PDF assinado")

    def shutdown(self):
        if self.preview.doc is not None:
            self.preview.doc.close()
            self.preview.doc = None

    # --- arquivo
    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Abrir PDF"), last_dir(), PDF_FILTER)
        if path:
            self.load(path)

    def add_files(self, paths: list[str]) -> None:
        pdfs = [p for p in paths if p.lower().endswith(".pdf")]
        if pdfs:
            self.load(pdfs[0])

    def load(self, path: str) -> None:
        try:
            doc = open_pdf(path)
        except PdfError as exc:
            QMessageBox.warning(self, APP_NAME, str(exc))
            return
        remember_dir(path)
        old = self.preview.doc
        self.path = path
        self.preview.set_document(doc)
        if old is not None:
            old.close()
        self.spin_page.blockSignals(True)
        self.spin_page.setRange(1, doc.page_count)
        self.spin_page.setValue(1)
        self.spin_page.blockSignals(False)
        self.file_label.setText(os.path.basename(path))
        self.file_label.setToolTip(path)
        self._refresh()

    # --- assinatura
    def _set_signature(self, png: bytes) -> None:
        img = QImage.fromData(png)
        if img.isNull():
            return
        self.png = png
        self.sig_view.set_image(img)
        self.preview.set_signature(img)

    def _create_signature(self) -> bool:
        dlg = SignatureDialog(self)
        if dlg.exec() != QDialog.Accepted or not dlg.result_png:
            return False
        self._set_signature(dlg.result_png)
        if dlg.cb_remember.isChecked():
            settings().setValue("signaturePng", QByteArray(dlg.result_png))
        else:
            settings().remove("signaturePng")
        return True

    def _need_signature(self):
        self._create_signature()

    def _repeat(self):
        n = self.preview.repeat_on_all_pages()
        if n:
            self.runner.taskbar.finish(tr("Assinatura repetida em mais {0} página(s).", n))

    # --- estado da tela
    def _refresh(self):
        has_doc = self.preview.doc is not None
        n_pages = self.preview.doc.page_count if has_doc else 0
        for w in (self.b_prev, self.spin_page, self.b_next):
            w.setEnabled(n_pages > 1)
        self.of_label.setText(tr("de {0}", n_pages) if has_doc else "")
        on_page = has_doc and bool(self.preview.rects())
        self.b_repeat.setEnabled(on_page and n_pages > 1)
        self.b_remove.setEnabled(self.preview.selected is not None)
        total = self.preview.total() if has_doc else 0
        self.b_clear.setEnabled(total > 0)
        self.b_create.setText(tr(" Trocar assinatura") if self.png else tr(" Criar assinatura"))
        if total:
            pages = sum(1 for v in self.preview.placements.values() if v)
            self.count_label.setText(tr("{0} assinatura(s) em {1} página(s)", total, pages))
        else:
            self.count_label.setText("")
        self.action.setEnabled(total > 0 and self.png is not None)

    # --- salvar
    def execute(self):
        if not self.path or self.preview.doc is None:
            raise PdfError(tr("Abra um PDF para assinar."))
        if not self.png:
            raise PdfError(tr("Crie sua assinatura antes de salvar."))
        placements = self.preview.all_placements()
        if not placements:
            raise PdfError(tr("Clique na página para posicionar a assinatura."))
        if sign.has_digital_signature(self.preview.doc):
            r = QMessageBox.question(
                self, APP_NAME,
                tr("Este PDF já tem uma assinatura digital. Qualquer alteração faz essa assinatura "
                "aparecer como inválida.\n\nDeseja continuar mesmo assim?"))
            if r != QMessageBox.Yes:
                return
        path = self.path
        out = save_file_dialog(self, tr("Salvar PDF assinado"),
                               unique_path(os.path.join(os.path.dirname(path), tr("{0} (assinado).pdf", stem(path)))))
        if not out:
            return
        if os.path.abspath(out) == os.path.abspath(path):
            raise PdfError(tr("Escolha um nome diferente do arquivo original."))
        png = self.png
        self.run(lambda ctx: sign.sign(path, png, placements, out, ctx),
                 lambda r: Outcome(tr("PDF assinado ({0} assinatura(s)) salvo como “{1}”.", len(placements), os.path.basename(out)), [out]),
                 tr("Assinando…"))
