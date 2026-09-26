"""Janela principal: barra lateral de ferramentas, área de conteúdo e barra de tarefas."""
from __future__ import annotations

import os
import subprocess
import sys

from PySide6.QtCore import QObject, QPoint, QProcess, QRunnable, QSize, Qt, QThreadPool, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .. import APP_NAME, AUTHOR, DONATE_URL, __version__, i18n, paths, updater
from ..core.common import IMAGE_EXTENSIONS
from . import theme, worker
from .organizer import OrganizerPage
from .pages import CompressPage, ConvertPage, MergePage, OcrPage, Outcome, SplitPage
from .signer import SignPage
from .widgets import settings
from ..i18n import tr

TOOLS = [
    ("merge", tr("Juntar PDFs"), MergePage),
    ("split", tr("Dividir e extrair"), SplitPage),
    ("organize", tr("Organizar páginas"), OrganizerPage),
    ("sign", tr("Assinar PDF"), SignPage),
    ("compress", tr("Comprimir"), CompressPage),
    ("convert", tr("Converter"), ConvertPage),
    ("ocr", tr("OCR (pesquisável)"), OcrPage),
]


def open_path(path: str) -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def reveal_in_explorer(path: str) -> None:
    """Abre a pasta com o arquivo já selecionado (Windows)."""
    if sys.platform == "win32" and os.path.isfile(path):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    else:
        open_path(path if os.path.isdir(path) else os.path.dirname(path))


def paypal_button() -> QPushButton:
    """Botão amarelo no estilo do PayPal que abre a página de doação no navegador."""
    btn = QPushButton()
    btn.setObjectName("paypal")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setToolTip(tr("Abre a página de doação do PayPal no navegador"))
    btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DONATE_URL)))
    label = QLabel(f'<span style="color:#003087;">{tr("Doar com")} </span>'
                   '<b><i><span style="color:#003087;">Pay</span><span style="color:#009CDE;">Pal</span></i></b>')
    label.setObjectName("paypalLabel")
    label.setAttribute(Qt.WA_TransparentForMouseEvents)
    lay = QHBoxLayout(btn)
    lay.setContentsMargins(18, 0, 18, 0)
    lay.addWidget(label, 0, Qt.AlignCenter)
    btn.setFixedHeight(34)
    btn.setMinimumWidth(label.sizeHint().width() + 36)
    return btn


class _ReleaseSignal(QObject):
    found = Signal(object)


class _UpdateCheck(QRunnable):
    """Consulta a última versão no GitHub numa thread separada."""

    def __init__(self) -> None:
        super().__init__()
        self.signals = _ReleaseSignal()

    def run(self) -> None:
        self.signals.found.emit(updater.latest_release())


class TaskBar(QFrame):
    """Mostra progresso, botão cancelar e, ao terminar, atalhos para abrir o resultado."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("taskBar")
        self.setFixedHeight(58)
        self.label = QLabel(tr("Pronto. Seus arquivos nunca saem do seu computador."))
        self.label.setObjectName("hint")
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(220)
        self.progress.hide()
        self.b_cancel = QPushButton(tr("Cancelar"))
        self.b_cancel.hide()
        self.b_open = QPushButton(theme.icon("file"), tr(" Abrir arquivo"))
        self.b_open.hide()
        self.b_folder = QPushButton(theme.icon("folder"), tr(" Abrir pasta"))
        self.b_folder.hide()
        self._outcome: Outcome | None = None
        self.b_open.clicked.connect(lambda: self._outcome and open_path(self._outcome.files[0]))
        self.b_folder.clicked.connect(self._open_folder)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(10)
        lay.addWidget(self.label, 1)
        lay.addWidget(self.progress)
        lay.addWidget(self.b_cancel)
        lay.addWidget(self.b_open)
        lay.addWidget(self.b_folder)

    def _open_folder(self):
        o = self._outcome
        if not o:
            return
        if o.files and (len(o.files) == 1 or not o.folder):
            reveal_in_explorer(o.files[0])
        elif o.folder:
            open_path(o.folder)

    def busy(self, text: str) -> None:
        self._outcome = None
        self.label.setText(text)
        self.progress.setValue(0)
        self.progress.setMaximum(0)  # indeterminado até o primeiro aviso de progresso
        for w in (self.b_open, self.b_folder):
            w.hide()
        self.progress.show()
        self.b_cancel.setEnabled(True)
        self.b_cancel.show()

    def update_progress(self, done: int, total: int, msg: str) -> None:
        self.progress.setMaximum(total)
        self.progress.setValue(done)
        if msg:
            self.label.setText(msg)

    def finish(self, text: str, outcome: Outcome | None = None) -> None:
        self.progress.hide()
        self.b_cancel.hide()
        self.label.setText(text)
        self._outcome = outcome
        if outcome and outcome.files:
            self.b_open.setVisible(len(outcome.files) == 1)
            self.b_folder.show()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(theme.app_icon())
        self.resize(1120, 740)
        self.setMinimumSize(900, 660)
        self._worker: worker.Worker | None = None

        # barra lateral
        side = QWidget()
        side.setObjectName("sidebarPanel")
        side.setAttribute(Qt.WA_StyledBackground)
        side.setFixedWidth(232)
        side_lay = QVBoxLayout(side)
        side_lay.setContentsMargins(0, 0, 1, 0)  # 1 px para a borda direita aparecer
        side_lay.setSpacing(0)
        brand = QLabel(APP_NAME)
        brand.setObjectName("brand")
        sub = QLabel(tr("Ferramentas de PDF grátis\ne 100% offline"))
        sub.setObjectName("brandSub")
        self.nav = QListWidget()
        self.nav.setObjectName("sidebar")
        self.nav.setIconSize(QSize(20, 20))
        self.nav.setFocusPolicy(Qt.NoFocus)
        self.nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        footer = QFrame()
        footer.setObjectName("sidebarFooter")
        f_lay = QVBoxLayout(footer)
        f_lay.setContentsMargins(14, 6, 14, 12)
        about = QPushButton(theme.icon("info", "accent"), tr(" Sobre o {0}", APP_NAME))
        about.setObjectName("link")
        about.setCursor(Qt.PointingHandCursor)
        about.clicked.connect(self.about)
        version = QLabel(tr("v{0} · Desenvolvido por {1}", __version__, AUTHOR))
        version.setObjectName("hint")
        version.setToolTip(tr("Versão {0}", __version__))
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("subtle")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self._update_theme_button()
        theme_row = QHBoxLayout()
        theme_row.setContentsMargins(16, 4, 16, 0)
        theme_row.addWidget(self.theme_btn)
        theme_row.addStretch(1)
        self.lang_btn = QPushButton(theme.icon("globe", "muted"), " " + i18n.LANGUAGES[i18n.current])
        self.lang_btn.setObjectName("subtle")
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.setToolTip(tr("Idioma"))
        lang_menu = QMenu(self.lang_btn)
        for code, name in i18n.LANGUAGES.items():
            action = lang_menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(code == i18n.current)
            action.triggered.connect(lambda _=False, c=code: self.change_language(c))
        # menu aberto pelo clique (com setMenu o Qt desloca o ícone e desalinha com o botão do tema)
        self.lang_btn.clicked.connect(
            lambda: lang_menu.exec(self.lang_btn.mapToGlobal(QPoint(0, self.lang_btn.height()))))
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(16, 0, 16, 0)
        lang_row.addWidget(self.lang_btn)
        lang_row.addStretch(1)
        donate_text = QLabel(tr("O {0} é grátis e sem anúncios. Se ele te ajudou, considere uma doação.", APP_NAME))
        donate_text.setObjectName("hint")
        donate_text.setWordWrap(True)
        donate_text.setAlignment(Qt.AlignHCenter)
        # altura exata para o texto quebrado em linhas (em alguns idiomas são 4 linhas)
        donate_text.setFixedHeight(donate_text.heightForWidth(side.width() - 28))
        f_lay.addWidget(donate_text)
        f_lay.addWidget(paypal_button(), 0, Qt.AlignHCenter)
        f_lay.addSpacing(10)
        f_lay.addWidget(about, 0, Qt.AlignHCenter)
        f_lay.addWidget(version, 0, Qt.AlignHCenter)
        side_lay.addWidget(brand)
        side_lay.addWidget(sub)
        side_lay.addWidget(self.nav)
        side_lay.addLayout(theme_row)
        side_lay.addLayout(lang_row)
        side_lay.addStretch(1)
        side_lay.addWidget(footer)

        # páginas
        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        self.pages = []
        for key, label, cls in TOOLS:
            QListWidgetItem(theme.nav_icon(key), f"  {label}", self.nav)
            page = cls(self)
            self.pages.append(page)
            self.stack.addWidget(page)
        self._fit_nav()
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.currentRowChanged.connect(lambda r: settings().setValue("lastTool", r))

        self.taskbar = TaskBar()
        self.taskbar.b_cancel.clicked.connect(self.cancel)

        right = QWidget()
        right.setObjectName("content")
        r_lay = QVBoxLayout(right)
        r_lay.setContentsMargins(0, 0, 0, 0)
        r_lay.setSpacing(0)
        r_lay.addWidget(self.stack, 1)
        r_lay.addWidget(self.taskbar)

        central = QWidget()
        lay = QHBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(side)
        lay.addWidget(right, 1)
        self.setCentralWidget(central)

        last = settings().value("lastTool", 0)
        try:
            last = int(last)
        except (TypeError, ValueError):
            last = 0
        self.nav.setCurrentRow(last if 0 <= last < len(TOOLS) else 0)

        if updater.is_enabled():  # confere se há versão nova, sem atrasar a abertura
            QTimer.singleShot(2500, self._check_updates)

    # ------------------------------------------------------------ tarefas
    def run(self, fn, on_done, label: str) -> None:
        if self._worker is not None:
            QMessageBox.information(self, APP_NAME, tr("Aguarde a tarefa atual terminar."))
            return
        w = worker.Worker(fn)
        w.signals.progress.connect(self.taskbar.update_progress)
        w.signals.done.connect(lambda result: self._done(on_done, result))
        w.signals.failed.connect(self._failed)
        w.signals.cancelled.connect(self._cancelled)
        self._worker = w
        self._set_busy(True)
        self.taskbar.busy(label)
        worker.start(w)

    def cancel(self) -> None:
        if self._worker:
            self._worker.cancel()
            self.taskbar.b_cancel.setEnabled(False)
            self.taskbar.label.setText(tr("Cancelando…"))

    def _set_busy(self, busy: bool) -> None:
        self.stack.setEnabled(not busy)
        self.nav.setEnabled(not busy)

    def _release(self) -> None:
        self._worker = None
        self._set_busy(False)

    def _done(self, on_done, result) -> None:
        self._release()
        try:
            outcome = on_done(result)
        except Exception as exc:  # noqa: BLE001
            self.taskbar.finish(tr("Concluído, mas houve um problema ao exibir o resultado: {0}", exc))
            return
        self.taskbar.finish("✔  " + outcome.message, outcome)

    def _failed(self, message: str) -> None:
        self._release()
        self.taskbar.finish(tr("Não foi possível concluir a tarefa."))
        QMessageBox.warning(self, APP_NAME, message)

    def _cancelled(self) -> None:
        self._release()
        self.taskbar.finish(tr("Tarefa cancelada. Arquivos parciais podem ter sido criados."))

    # ------------------------------------------------------------ outros
    def open_files(self, paths: list[str]) -> None:
        """Arquivos recebidos pela linha de comando ("Abrir com" / arrastar sobre o .exe)."""
        paths = [p for p in paths if os.path.isfile(p)]
        if not paths:
            return
        only_images = all(os.path.splitext(p)[1].lower() in IMAGE_EXTENSIONS for p in paths)
        if only_images:
            key = "convert"  # Imagem para PDF
        elif len(paths) > 1:
            key = "merge"
        else:
            key = "organize"
        row = [k for k, _, _ in TOOLS].index(key)
        self.nav.setCurrentRow(row)
        self.pages[row].add_files(paths)

    def _fit_nav(self) -> None:
        """Altura do menu exatamente para todas as ferramentas (sem rolagem nem cortes)."""
        self.nav.ensurePolished()
        self.nav.doItemsLayout()
        last = self.nav.visualItemRect(self.nav.item(self.nav.count() - 1))
        top = self.nav.viewport().geometry().top()
        self.nav.setFixedHeight(top + last.bottom() + 1 + top)  # mesmo respiro em cima e embaixo

    def toggle_theme(self) -> None:
        theme.apply("light" if theme.current == "dark" else "dark")
        settings().setValue("theme", theme.current)
        self._update_theme_button()

    # ------------------------------------------------------------ atualização
    def _check_updates(self) -> None:
        self._update_check = _UpdateCheck()  # mantém referência enquanto a thread roda
        self._update_check.signals.found.connect(self._on_release)
        QThreadPool.globalInstance().start(self._update_check)

    def _on_release(self, release) -> None:
        if release is None or not updater.is_newer(release.version) or self._worker is not None:
            return
        box = QMessageBox(self)
        box.setWindowTitle(tr("Atualização disponível"))
        box.setIconPixmap(theme.app_pixmap(56))
        box.setText(tr("<b>O {0} {1} está disponível.</b><br>Você está usando a versão {2}.",
                       APP_NAME, release.version, __version__))
        notes = release.notes if len(release.notes) <= 700 else release.notes[:700].rsplit(" ", 1)[0] + "…"
        automatic = bool(release.zip_url) and paths.can_write()
        info = tr("O programa vai baixar a versão nova, fechar e abrir de novo já atualizado. "
                  "Suas configurações e a assinatura salva são mantidas.") if automatic else \
            tr("Baixe a versão nova pela página de download.")
        box.setInformativeText((tr("Novidades:") + "\n" + notes + "\n\n" if notes else "") + info)
        update = box.addButton(tr("Atualizar agora") if automatic else tr("Abrir página de download"),
                               QMessageBox.AcceptRole)
        update.setObjectName("primary")
        box.addButton(tr("Depois"), QMessageBox.RejectRole)
        box.setDefaultButton(update)
        box.exec()
        if box.clickedButton() is not update:
            return
        if not automatic:
            QDesktopServices.openUrl(QUrl(release.page_url))
            return

        def install(new_dir: str) -> Outcome:
            updater.launch(updater.write_script(new_dir, paths.app_dir(), os.getpid()))
            QTimer.singleShot(300, self.close)
            return Outcome(tr("Instalando a atualização…"))

        self.run(lambda ctx: updater.prepare(updater.download(release, ctx)), install,
                 tr("Baixando atualização…"))

    def change_language(self, code: str) -> None:
        """Salva o idioma e reinicia o programa (os textos são montados ao abrir)."""
        if code == i18n.current:
            return
        if self._worker is not None:
            QMessageBox.information(self, APP_NAME, tr("Aguarde a tarefa atual terminar."))
            return
        settings().setValue("language", code)
        settings().sync()
        self._restarting = True
        if self.close():
            if getattr(sys, "frozen", False):
                QProcess.startDetached(sys.executable, [])
            else:
                QProcess.startDetached(sys.executable, [os.path.abspath(sys.argv[0])])

    def _update_theme_button(self) -> None:
        if theme.current == "dark":
            self.theme_btn.setIcon(theme.icon("sun", "muted"))
            self.theme_btn.setText(tr(" Modo claro"))
        else:
            self.theme_btn.setIcon(theme.icon("moon", "muted"))
            self.theme_btn.setText(tr(" Modo escuro"))

    def about(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(tr("Sobre o {0}", APP_NAME))
        box.setIconPixmap(theme.app_pixmap(64))
        box.setText(f"<b>{APP_NAME} {__version__}</b>")
        box.setInformativeText(
            tr("Ferramentas de PDF gratuitas que funcionam 100% offline.<br>Nenhum arquivo é enviado para a internet.<br><br>Desenvolvido por <b>{0}</b>.<br><br>Feito com PyMuPDF, Tesseract OCR e Qt (PySide6).<br>Distribuído sob a licença AGPL-3.0.", AUTHOR)
        )
        box.exec()

    def closeEvent(self, e) -> None:
        if self._worker is not None:
            r = QMessageBox.question(self, APP_NAME, tr("Há uma tarefa em andamento. Deseja cancelar e sair?"))
            if r != QMessageBox.Yes:
                e.ignore()
                return
            self._worker.cancel()
        for p in self.pages:
            if hasattr(p, "shutdown"):
                p.shutdown()
        super().closeEvent(e)
