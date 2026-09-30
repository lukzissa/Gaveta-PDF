"""Ponto de entrada do Gaveta PDF.  Uso:  python GavetaPDF.py [arquivos...]"""
import multiprocessing

if __name__ == "__main__":
    # O OCR usa processos auxiliares; no .exe eles são o próprio GavetaPDF.exe aberto em
    # modo especial. Isto os desvia para o trabalho antes de carregar a interface.
    multiprocessing.freeze_support()

import logging  # noqa: E402
import sys  # noqa: E402

from PySide6.QtCore import QLibraryInfo, Qt, QTranslator  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from gavetapdf import APP_NAME, i18n, paths  # noqa: E402
from gavetapdf.ui import theme  # noqa: E402
from gavetapdf.ui.main_window import MainWindow  # noqa: E402
from gavetapdf.ui.widgets import settings  # noqa: E402


def setup_logging() -> None:
    """Log em dados/gavetapdf.log ao lado do programa (modo portátil)."""
    path = paths.log_path()
    if path is None:  # pasta somente leitura: sem log em arquivo, para não gravar em outro lugar
        logging.getLogger().addHandler(logging.NullHandler())
        return
    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


QT_TRANSLATIONS = {"pt": "qtbase_pt_BR", "es": "qtbase_es", "ru": "qtbase_ru"}


def install_qt_translation(app: QApplication) -> None:
    """Traduz os botões padrão do Qt (OK, Cancelar, Sim, Não…) para o idioma escolhido."""
    name = QT_TRANSLATIONS.get(i18n.current)
    if not name:
        return
    translator = QTranslator(app)
    if translator.load(name, QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)


def main() -> int:
    setup_logging()
    if sys.platform == "win32":
        # Ícone próprio na barra de tarefas do Windows (em vez do ícone do Python)
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GavetaPDF.App")
        except Exception:  # noqa: BLE001
            pass
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    install_qt_translation(app)
    app.setStyle("Fusion")
    # Tema escolhido pelo usuário (claro por padrão), independente do tema do Windows.
    # Na primeira vez segue o tema do Windows; depois, a escolha feita no botão da barra lateral
    theme.apply(theme.startup_theme(settings().value("theme")))
    app.setWindowIcon(theme.app_icon())
    win = MainWindow()
    win.show()
    win.open_files(sys.argv[1:])
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
