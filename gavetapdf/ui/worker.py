"""Execução de tarefas em segundo plano, sem travar a janela."""
from __future__ import annotations

import logging
import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from ..core.common import Cancelled, Context, PdfError
from ..i18n import tr

log = logging.getLogger("gavetapdf")


class _Signals(QObject):
    progress = Signal(int, int, str)
    done = Signal(object)
    failed = Signal(str)
    cancelled = Signal()


class Worker(QRunnable):
    """Roda `fn(ctx)` numa thread do pool e avisa a interface por sinais."""

    def __init__(self, fn: Callable[[Context], Any]) -> None:
        super().__init__()
        self.fn = fn
        self.signals = _Signals()
        self._cancel = False
        self.setAutoDelete(False)

    def cancel(self) -> None:
        self._cancel = True

    def run(self) -> None:  # executa fora da thread da interface
        ctx = Context(
            on_progress=lambda d, t, m: self.signals.progress.emit(d, t, m),
            is_cancelled=lambda: self._cancel,
        )
        try:
            result = self.fn(ctx)
        except Cancelled:
            self.signals.cancelled.emit()
        except PdfError as exc:
            self.signals.failed.emit(str(exc))
        except Exception as exc:  # noqa: BLE001
            log.error("Erro inesperado\n%s", traceback.format_exc())
            self.signals.failed.emit(tr("Ocorreu um erro inesperado:\n{0}", exc))
        else:
            self.signals.done.emit(result)


def start(worker: Worker) -> None:
    QThreadPool.globalInstance().start(worker)
