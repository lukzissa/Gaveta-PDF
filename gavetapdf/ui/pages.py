"""Telas de cada ferramenta (exceto o organizador de páginas, em organizer.py)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APP_NAME, i18n
from ..core import compress, convert, ocr, organize
from ..core.common import (
    IMAGE_EXTENSIONS,
    PdfError,
    human_size,
    page_count,
    parse_ranges,
    stem,
    sub_context,
    unique_path,
)
from ..i18n import tr
from .widgets import (
    IMAGE_FILTER,
    PDF_EXT,
    PDF_IMAGE_FILTER,
    FileList,
    OutputDir,
    card,
    choose_dir_dialog,
    hint,
    save_file_dialog,
    section,
)


@dataclass
class Outcome:
    message: str
    files: list[str] = field(default_factory=list)
    folder: str | None = None


class BasePage(QWidget):
    title = ""
    subtitle = ""

    def __init__(self, runner, parent=None) -> None:
        super().__init__(parent)
        self.runner = runner
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 26, 32, 20)
        outer.setSpacing(14)
        t = QLabel(self.title)
        t.setObjectName("pageTitle")
        s = QLabel(self.subtitle)
        s.setObjectName("pageSubtitle")
        s.setWordWrap(True)
        head = QVBoxLayout()
        head.setSpacing(2)
        head.addWidget(t)
        head.addWidget(s)
        outer.addLayout(head)
        self.body = QVBoxLayout()
        self.body.setSpacing(12)
        outer.addLayout(self.body, 1)
        self.action = QPushButton(self.action_text())
        self.action.setObjectName("primary")
        self.action.setCursor(Qt.PointingHandCursor)
        self.action.clicked.connect(self._on_action)
        foot = QHBoxLayout()
        foot.addStretch(1)
        foot.addWidget(self.action)
        outer.addLayout(foot)

    def action_text(self) -> str:
        return tr("Executar")

    def _on_action(self) -> None:
        try:
            self.execute()
        except PdfError as exc:
            QMessageBox.warning(self, APP_NAME, str(exc))

    def execute(self) -> None:  # implementado nas subclasses
        raise NotImplementedError

    def run(self, fn: Callable, done: Callable[[object], Outcome], label: str) -> None:
        self.runner.run(fn, done, label)

    def add_files(self, paths: list[str]) -> None:
        """Recebe arquivos abertos pela linha de comando / 'Abrir com'."""
        fl = getattr(self, "files", None)
        if isinstance(fl, FileList):
            fl.add_files(paths)


def _two_columns(left: QWidget, right: QWidget, right_width: int = 340) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(14)
    row.addWidget(left, 1)
    right.setFixedWidth(right_width)
    row.addWidget(right, 0, Qt.AlignTop)
    return row


# ---------------------------------------------------------------- Juntar
class MergePage(BasePage):
    title = tr("Juntar PDFs")
    subtitle = tr("Una vários PDFs (e imagens) em um único arquivo. Arraste para mudar a ordem.")

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self.files = FileList(PDF_EXT | IMAGE_EXTENSIONS, PDF_IMAGE_FILTER,
                              tr("Arraste PDFs ou imagens para cá\na ordem da lista é a ordem do arquivo final"))
        self.body.addWidget(self.files, 1)
        self.body.addWidget(hint(tr("Dica: para escolher páginas específicas de cada arquivo, use “Organizar páginas”.")))

    def action_text(self):
        return tr("Juntar PDFs")

    def execute(self):
        files = self.files.files()
        if len(files) < 2:
            raise PdfError(tr("Adicione pelo menos dois arquivos para juntar."))
        suggested = os.path.join(os.path.dirname(files[0]), tr("{0} (unido).pdf", stem(files[0])))
        out = save_file_dialog(self, tr("Salvar PDF unido"), unique_path(suggested))
        if not out:
            return
        if os.path.abspath(out) in map(os.path.abspath, files):
            raise PdfError(tr("Escolha um nome diferente dos arquivos de origem."))
        self.run(lambda ctx: organize.merge(files, out, ctx),
                 lambda r: Outcome(tr("{0} arquivos unidos em “{1}”.", len(files), os.path.basename(out)), [out]),
                 tr("Juntando arquivos…"))


# ---------------------------------------------------------------- Dividir
class SplitPage(BasePage):
    title = tr("Dividir e extrair")
    subtitle = tr("Separe um PDF em vários arquivos ou tire dele só as páginas que interessam.")

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self.files = FileList(PDF_EXT, tr("Arquivos PDF (*.pdf)"), tr("Arraste um PDF para cá"), single=True)
        self.files.changed.connect(self._update_count)
        self.count_label = hint("")

        self.rb_each = QRadioButton(tr("Um arquivo para cada página"))
        self.rb_every = QRadioButton(tr("Um arquivo a cada"))
        self.spin_every = QSpinBox()
        self.spin_every.setRange(1, 9999)
        self.spin_every.setValue(2)
        self.spin_every.setSuffix(tr(" páginas"))
        self.spin_every.setButtonSymbols(QSpinBox.UpDownArrows)
        self.spin_every.setFixedWidth(140)
        self.rb_ranges = QRadioButton(tr("Um arquivo para cada intervalo:"))
        self.ed_ranges = QLineEdit()
        self.ed_ranges.setPlaceholderText(tr("ex.: 1-3, 4-10, 11-"))
        self.rb_extract = QRadioButton(tr("Extrair páginas para um só arquivo:"))
        self.ed_extract = QLineEdit()
        self.ed_extract.setPlaceholderText(tr("ex.: 1, 3, 5-7"))
        self.rb_each.setChecked(True)
        grp = QButtonGroup(self)
        for rb in (self.rb_each, self.rb_every, self.rb_ranges, self.rb_extract):
            grp.addButton(rb)
        self.ed_ranges.textEdited.connect(lambda: self.rb_ranges.setChecked(True))
        self.ed_extract.textEdited.connect(lambda: self.rb_extract.setChecked(True))
        self.spin_every.valueChanged.connect(lambda: self.rb_every.setChecked(True))

        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.addWidget(self.rb_each, 0, 0, 1, 2)
        grid.addWidget(self.rb_every, 1, 0)
        grid.addWidget(self.spin_every, 1, 1, Qt.AlignLeft)
        grid.addWidget(self.rb_ranges, 2, 0)
        grid.addWidget(self.ed_ranges, 2, 1)
        grid.addWidget(self.rb_extract, 3, 0)
        grid.addWidget(self.ed_extract, 3, 1)
        grid.setColumnStretch(1, 1)

        self.body.addWidget(card(section(tr("Arquivo")), self.files, self.count_label))
        self.body.addWidget(card(section(tr("Como dividir")), grid,
                                 hint(tr("Intervalos: separe por vírgula. “8-” vai da página 8 até o fim."))))
        self.body.addStretch(1)

    def action_text(self):
        return tr("Dividir PDF")

    def _update_count(self):
        f = self.files.files()
        if not f:
            self.count_label.setText("")
            return
        try:
            self.count_label.setText(tr("{0} página(s)", page_count(f[0])))
        except PdfError as exc:
            self.count_label.setText(str(exc).split("\n")[0])

    def execute(self):
        f = self.files.files()
        if not f:
            raise PdfError(tr("Escolha um arquivo PDF."))
        path = f[0]
        if self.rb_extract.isChecked():
            text = self.ed_extract.text()
            parse_ranges(text, page_count(path))  # valida antes de abrir a janela de salvar
            out = save_file_dialog(self, tr("Salvar páginas extraídas"),
                                   unique_path(os.path.join(os.path.dirname(path), tr("{0} (extraído).pdf", stem(path)))))
            if not out:
                return
            if os.path.abspath(out) == os.path.abspath(path):
                raise PdfError(tr("Escolha um nome diferente do arquivo original."))
            self.run(lambda ctx: organize.extract(path, text, out, ctx),
                     lambda r: Outcome(tr("Páginas extraídas para “{0}”.", os.path.basename(out)), [out]),
                     tr("Extraindo páginas…"))
            return

        if self.rb_ranges.isChecked():
            text = self.ed_ranges.text()
            parse_ranges(text, page_count(path))  # valida antes de pedir a pasta
        out_dir = choose_dir_dialog(self, tr("Escolha a pasta para salvar as partes"), os.path.dirname(path))
        if not out_dir:
            return
        if self.rb_each.isChecked():
            fn = lambda ctx: organize.split_every(path, 1, out_dir, ctx)  # noqa: E731
        elif self.rb_every.isChecked():
            n = self.spin_every.value()
            fn = lambda ctx: organize.split_every(path, n, out_dir, ctx)  # noqa: E731
        else:
            fn = lambda ctx: organize.split_ranges(path, text, out_dir, ctx)  # noqa: E731
        self.run(fn, lambda r: Outcome(tr("PDF dividido em {0} arquivo(s).", len(r)), r, out_dir), tr("Dividindo…"))


# ---------------------------------------------------------------- Comprimir
class CompressPage(BasePage):
    title = tr("Comprimir PDF")
    subtitle = tr("Diminua o tamanho dos arquivos para enviar por e-mail, WhatsApp ou sistemas com limite de upload.")

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self.files = FileList(PDF_EXT, tr("Arquivos PDF (*.pdf)"), tr("Arraste um ou vários PDFs para cá"), reorder=False)
        self.level_group = QButtonGroup(self)
        levels = QVBoxLayout()
        levels.setSpacing(6)
        for key, lvl in compress.LEVELS.items():
            rb = QRadioButton(lvl.label)
            rb.setProperty("level", key)
            self.level_group.addButton(rb)
            levels.addWidget(rb)
            desc = hint(lvl.description)
            desc.setContentsMargins(26, 0, 0, 4)
            levels.addWidget(desc)
            if key == "recomendada":
                rb.setChecked(True)
        self.cb_gray = QCheckBox(tr("Imagens em tons de cinza (reduz mais)"))
        self.output = OutputDir()

        options = card(section(tr("Nível de compressão")), levels, self.cb_gray,
                       section(tr("Salvar")), self.output,
                       hint(tr("O original nunca é alterado. O novo arquivo recebe “(comprimido)” no nome.")))
        self.body.addLayout(_two_columns(self.files, options, 380), 1)

    def action_text(self):
        return tr("Comprimir")

    def execute(self):
        files = self.files.files()
        if not files:
            raise PdfError(tr("Adicione ao menos um PDF."))
        if self.output.resolve(files[0]) is None:
            raise PdfError(tr("Escolha a pasta onde os arquivos serão salvos."))
        level = self.level_group.checkedButton().property("level")
        gray = self.cb_gray.isChecked()
        jobs = [(f, unique_path(os.path.join(self.output.resolve(f), tr("{0} (comprimido).pdf", stem(f))))) for f in files]

        def fn(ctx):
            results = []
            for i, (src, out) in enumerate(jobs):
                sub = sub_context(ctx, i, len(jobs), os.path.basename(src))
                results.append(compress.compress(src, out, level, gray, sub))
            return results

        def done(results):
            before = sum(r.before for r in results)
            after = sum(r.after for r in results)
            pct = max(0, (1 - after / before) * 100) if before else 0
            msg = f"{human_size(before)} → {human_size(after)}  (−{pct:.0f}%)"
            if len(results) == 1 and results[0].kept_original:
                msg = tr("Este PDF já estava otimizado; não foi possível reduzir mais.")
            elif len(results) > 1:
                msg = tr("{0} arquivos comprimidos: {1}", len(results), msg)
            else:
                msg = tr("Arquivo comprimido: {0}", msg)
            return Outcome(msg, [r.out for r in results], os.path.dirname(results[0].out))

        self.run(fn, done, tr("Comprimindo…"))


# ---------------------------------------------------------------- Converter
class ConvertPage(BasePage):
    title = tr("Converter")
    subtitle = tr("Transforme PDF em Word, Excel, imagens ou texto, e fotos ou digitalizações em PDF.")

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        # (aba, título, texto do botão, ação)
        self._modes = [
            (self._tab_pdf_to_word(), tr("PDF → Word"), tr("Converter para Word"), self._run_word),
            (self._tab_pdf_to_excel(), tr("PDF → Excel"), tr("Converter para Excel"), self._run_excel),
            (self._tab_pdf_to_img(), tr("PDF → Imagem"), tr("Converter em imagens"), self._run_images),
            (self._tab_img_to_pdf(), tr("Imagem → PDF"), tr("Criar PDF"), self._run_img_to_pdf),
            (self._tab_pdf_to_txt(), tr("PDF → Texto"), tr("Extrair texto"), self._run_text),
        ]
        for tab, label, _, _ in self._modes:
            self.tabs.addTab(tab, label)
        self.tabs.currentChanged.connect(self._update_action)
        self._update_action()
        self.body.addWidget(self.tabs, 1)

    def action_text(self):
        return tr("Converter")

    def _update_action(self):
        self.action.setText(self._modes[self.tabs.currentIndex()][2])

    def add_files(self, paths):
        imgs = [p for p in paths if os.path.splitext(p)[1].lower() in IMAGE_EXTENSIONS]
        if imgs and len(imgs) == len(paths):
            self.tabs.setCurrentIndex(3)
            self.img_files.add_files(imgs)
        else:
            if self.tabs.currentIndex() == 3:  # aba de imagens: vai para PDF → Word
                self.tabs.setCurrentIndex(0)
            pdf_lists = [self.word_files, self.xls_files, self.p2i_files, None, self.txt_files]
            pdf_lists[self.tabs.currentIndex()].add_files(paths)

    # PDF → Word
    def _tab_pdf_to_word(self):
        w = QWidget()
        self.word_files = FileList(PDF_EXT, tr("Arquivos PDF (*.pdf)"), tr("Arraste PDFs para cá"), reorder=False)
        self.word_out = OutputDir()
        opts = card(section(tr("Salvar")), self.word_out,
                    hint(tr("Cria um arquivo .docx editável, mantendo parágrafos, tabelas e imagens.")),
                    hint(tr("Funciona melhor com PDFs gerados no computador. Documentos escaneados "
                         "precisam passar pelo OCR antes.")),
                    hint(tr("Layouts muito elaborados podem precisar de pequenos ajustes no Word.")))
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addLayout(_two_columns(self.word_files, opts, 360), 1)
        return w

    # PDF → Excel
    def _tab_pdf_to_excel(self):
        w = QWidget()
        self.xls_files = FileList(PDF_EXT, tr("Arquivos PDF (*.pdf)"), tr("Arraste PDFs com tabelas para cá"), reorder=False)
        self.cmb_sheets = QComboBox()
        self.cmb_sheets.addItem(tr("Uma aba para cada página"), False)
        self.cmb_sheets.addItem(tr("Todas as tabelas em uma aba"), True)
        self.cb_numbers = QCheckBox(tr("Transformar números em valores do Excel"))
        self.cb_numbers.setToolTip(tr("“R$ 1.234,56”, “12,5” e “15%” viram números, "
                                   "prontos para somar e fazer contas."))
        self.cb_numbers.setChecked(True)
        self.xls_out = OutputDir()
        opts = card(section(tr("Organização")), self.cmb_sheets, self.cb_numbers,
                    section(tr("Salvar")), self.xls_out,
                    hint(tr("Encontra as tabelas do PDF (extratos, relatórios, notas) e cria um arquivo .xlsx. "
                         "Códigos com zero à esquerda, CPF e datas continuam como texto.")))
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addLayout(_two_columns(self.xls_files, opts, 360), 1)
        return w

    # PDF → imagem
    def _tab_pdf_to_img(self):
        w = QWidget()
        self.p2i_files = FileList(PDF_EXT, tr("Arquivos PDF (*.pdf)"), tr("Arraste PDFs para cá"), reorder=False)
        self.cmb_fmt = QComboBox()
        self.cmb_fmt.addItem(tr("PNG (sem perda, ideal para texto)"), "png")
        self.cmb_fmt.addItem(tr("JPG (menor, ideal para fotos)"), "jpg")
        self.cmb_dpi = QComboBox()
        for label, dpi in [(tr("Baixa — 96 DPI (tela)"), 96), (tr("Média — 150 DPI"), 150),
                           (tr("Alta — 300 DPI (impressão)"), 300), (tr("Máxima — 600 DPI"), 600)]:
            self.cmb_dpi.addItem(label, dpi)
        self.cmb_dpi.setCurrentIndex(1)
        self.ed_pages = QLineEdit()
        self.ed_pages.setPlaceholderText(tr("Todas as páginas (ou ex.: 1-3, 7)"))
        self.p2i_out = OutputDir()
        opts = card(section(tr("Formato")), self.cmb_fmt, section(tr("Qualidade")), self.cmb_dpi,
                    section(tr("Páginas")), self.ed_pages, section(tr("Salvar")), self.p2i_out,
                    hint(tr("Cada PDF gera uma pasta com uma imagem por página.")))
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addLayout(_two_columns(self.p2i_files, opts, 360), 1)
        return w

    # imagem → PDF
    def _tab_img_to_pdf(self):
        w = QWidget()
        self.img_files = FileList(IMAGE_EXTENSIONS, IMAGE_FILTER,
                                  tr("Arraste imagens (JPG, PNG, TIFF…) para cá\ncada imagem vira uma página"))
        self.cmb_size = QComboBox()
        self.cmb_size.addItem(tr("A4 (ajusta a imagem na folha)"), "a4")
        self.cmb_size.addItem(tr("Tamanho original da imagem"), "original")
        self.cmb_margin = QComboBox()
        for label, mm in [(tr("Sem margem"), 0), (tr("Pequena (5 mm)"), 5), (tr("Normal (10 mm)"), 10), (tr("Grande (20 mm)"), 20)]:
            self.cmb_margin.addItem(label, mm)
        self.cmb_margin.setCurrentIndex(2)
        opts = card(section(tr("Tamanho da página")), self.cmb_size, section(tr("Margem")), self.cmb_margin,
                    hint(tr("Dica: depois de criar o PDF, use o OCR para tornar o texto pesquisável.")))
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addLayout(_two_columns(self.img_files, opts, 360), 1)
        return w

    # PDF → texto
    def _tab_pdf_to_txt(self):
        w = QWidget()
        self.txt_files = FileList(PDF_EXT, tr("Arquivos PDF (*.pdf)"), tr("Arraste PDFs para cá"), reorder=False)
        self.txt_out = OutputDir()
        opts = card(section(tr("Salvar")), self.txt_out,
                    hint(tr("Gera um arquivo .txt com o texto de cada página. "
                         "PDFs escaneados precisam passar pelo OCR antes.")))
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.addLayout(_two_columns(self.txt_files, opts, 360), 1)
        return w

    def execute(self):
        self._modes[self.tabs.currentIndex()][3]()

    def _jobs(self, files_widget: FileList, out_widget: OutputDir, ext: str, missing_dir: str):
        files = files_widget.files()
        if not files:
            raise PdfError(tr("Adicione ao menos um PDF."))
        if out_widget.resolve(files[0]) is None:
            raise PdfError(missing_dir)
        return [(f, unique_path(os.path.join(out_widget.resolve(f), f"{stem(f)}{ext}"))) for f in files]

    def _run_word(self):
        jobs = self._jobs(self.word_files, self.word_out, ".docx",
                          tr("Escolha a pasta onde os documentos serão salvos."))

        def fn(ctx):
            return [convert.pdf_to_word(s, o, sub_context(ctx, i, len(jobs), os.path.basename(s)))
                    for i, (s, o) in enumerate(jobs)]

        self.run(fn, lambda r: Outcome(tr("{0} arquivo(s) convertido(s) para Word.", len(r)), r,
                                       os.path.dirname(r[0])), tr("Convertendo para Word…"))

    def _run_excel(self):
        jobs = self._jobs(self.xls_files, self.xls_out, ".xlsx",
                          tr("Escolha a pasta onde as planilhas serão salvas."))
        one_sheet, numbers = self.cmb_sheets.currentData(), self.cb_numbers.isChecked()

        def fn(ctx):
            return [convert.pdf_to_excel(s, o, one_sheet, numbers,
                                         sub_context(ctx, i, len(jobs), os.path.basename(s)))
                    for i, (s, o) in enumerate(jobs)]

        outs = [o for _, o in jobs]
        self.run(fn, lambda r: Outcome(tr("{0} tabela(s) exportada(s) para {1} planilha(s).", sum(r), len(r)), outs,
                                       os.path.dirname(outs[0])), tr("Convertendo para Excel…"))

    def _run_images(self):
        files = self.p2i_files.files()
        if not files:
            raise PdfError(tr("Adicione ao menos um PDF."))
        if self.p2i_out.resolve(files[0]) is None:
            raise PdfError(tr("Escolha a pasta onde as imagens serão salvas."))
        fmt, dpi, pages = self.cmb_fmt.currentData(), self.cmb_dpi.currentData(), self.ed_pages.text()
        if pages.strip():
            for f in files:
                parse_ranges(pages, page_count(f))
        jobs = [(f, os.path.join(self.p2i_out.resolve(f), tr("{0} - imagens", stem(f)))) for f in files]

        def fn(ctx):
            out = []
            for i, (src, d) in enumerate(jobs):
                out += convert.pdf_to_images(src, d, fmt, dpi, pages,
                                             sub_context(ctx, i, len(jobs), os.path.basename(src)))
            return out

        folder = jobs[0][1]
        self.run(fn, lambda r: Outcome(tr("{0} imagem(ns) criada(s).", len(r)), r, folder), tr("Convertendo…"))

    def _run_img_to_pdf(self):
        imgs = self.img_files.files()
        if not imgs:
            raise PdfError(tr("Adicione ao menos uma imagem."))
        out = save_file_dialog(self, tr("Salvar PDF"),
                               unique_path(os.path.join(os.path.dirname(imgs[0]), f"{stem(imgs[0])}.pdf")))
        if not out:
            return
        size, margin = self.cmb_size.currentData(), self.cmb_margin.currentData()
        self.run(lambda ctx: convert.images_to_pdf(imgs, out, size, margin, ctx),
                 lambda r: Outcome(tr("PDF criado com {0} imagem(ns).", len(imgs)), [out]), tr("Criando PDF…"))

    def _run_text(self):
        jobs = self._jobs(self.txt_files, self.txt_out, ".txt",
                          tr("Escolha a pasta onde os textos serão salvos."))

        def fn(ctx):
            return [convert.pdf_to_text(s, o, sub_context(ctx, i, len(jobs), os.path.basename(s)))
                    for i, (s, o) in enumerate(jobs)]

        self.run(fn, lambda r: Outcome(tr("Texto extraído de {0} arquivo(s).", len(r)), r,
                                       os.path.dirname(r[0])), tr("Extraindo texto…"))


# ---------------------------------------------------------------- OCR
class OcrPage(BasePage):
    title = tr("OCR — tornar pesquisável")
    subtitle = (tr("Reconhece o texto de PDFs escaneados e fotos de documentos. "
                "Depois você pode buscar (Ctrl+F), selecionar e copiar o texto. Tudo acontece no seu computador."))

    def __init__(self, runner, parent=None):
        super().__init__(runner, parent)
        self.files = FileList(PDF_EXT | IMAGE_EXTENSIONS, PDF_IMAGE_FILTER,
                              tr("Arraste PDFs escaneados ou fotos de documentos para cá"), reorder=False)
        self.lang_boxes: list[QCheckBox] = []
        langs_lay = QVBoxLayout()
        langs_lay.setSpacing(2)
        available = ocr.available_languages()
        # já vem marcado o idioma da interface (ou o primeiro instalado)
        preferred = i18n.OCR_LANGUAGE.get(i18n.current, "eng")
        if preferred not in available and available:
            preferred = available[0]
        for code in available:
            cb = QCheckBox(ocr.LANGUAGE_NAMES.get(code, code))
            cb.setProperty("code", code)
            cb.setChecked(code == preferred)
            self.lang_boxes.append(cb)
            langs_lay.addWidget(cb)
        if not available:
            langs_lay.addWidget(hint(tr("Nenhum idioma instalado. Coloque arquivos .traineddata na pasta “tessdata”.")))
        self.cmb_quality = QComboBox()
        self.cmb_quality.addItem(tr("Rápido (200 DPI)"), 200)
        self.cmb_quality.addItem(tr("Recomendado (300 DPI)"), 300)
        self.cmb_quality.addItem(tr("Máxima precisão (400 DPI)"), 400)
        self.cmb_quality.setCurrentIndex(1)
        self.cb_skip = QCheckBox(tr("Pular páginas que já têm texto"))
        self.cb_skip.setChecked(True)
        self.output = OutputDir()
        opts = card(section(tr("Idioma do documento")), langs_lay, section(tr("Qualidade")), self.cmb_quality,
                    self.cb_skip, section(tr("Salvar")), self.output,
                    hint(tr("O novo arquivo recebe “(pesquisável)” no nome. Para reduzir o tamanho depois, use Comprimir.")))
        self.body.addLayout(_two_columns(self.files, opts, 380), 1)

    def action_text(self):
        return tr("Reconhecer texto")

    def execute(self):
        files = self.files.files()
        if not files:
            raise PdfError(tr("Adicione ao menos um arquivo."))
        langs = [cb.property("code") for cb in self.lang_boxes if cb.isChecked()]
        if not langs:
            raise PdfError(tr("Marque ao menos um idioma."))
        if self.output.resolve(files[0]) is None:
            raise PdfError(tr("Escolha a pasta onde os arquivos serão salvos."))
        dpi, skip = self.cmb_quality.currentData(), self.cb_skip.isChecked()
        jobs = [(f, unique_path(os.path.join(self.output.resolve(f), tr("{0} (pesquisável).pdf", stem(f))))) for f in files]

        def fn(ctx):
            stats = []
            for i, (src, out) in enumerate(jobs):
                stats.append(ocr.ocr_file(src, out, langs, dpi, skip,
                                          sub_context(ctx, i, len(jobs), os.path.basename(src))))
            return stats

        def done(stats):
            ocr_pages = sum(s["ocr_pages"] for s in stats)
            skipped = sum(s["skipped"] for s in stats)
            msg = tr("Texto reconhecido em {0} página(s).", ocr_pages)
            if skipped:
                msg += tr(" {0} já tinham texto e foram mantidas.", skipped)
            outs = [o for _, o in jobs]
            return Outcome(msg, outs, os.path.dirname(outs[0]))

        self.run(fn, done, tr("Reconhecendo texto…"))
