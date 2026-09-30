"""Roda operações pesadas de PDF num processo auxiliar, para a janela não congelar.

O MuPDF (PyMuPDF) segura o interpretador Python durante cada chamada. Numa operação
grande (salvar um PDF de 80 MB, comprimir imagens, desenhar páginas em alta resolução)
isso congela a janela por segundos: a barra de progresso para e o Windows mostra
"não está respondendo". Aqui a operação roda num processo separado, criado uma vez e
reaproveitado; os avisos de progresso voltam por uma fila e o cancelamento encerra o
processo na hora. Arquivos pequenos rodam direto, sem esse custo.
"""
from __future__ import annotations

import atexit
import multiprocessing
import os
import queue
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import Callable

from .common import Cancelled, Context

SMALL = 8 * 1024 * 1024  # abaixo disso (soma dos arquivos de entrada) roda direto

_pool: ProcessPoolExecutor | None = None
_progress = None  # fila de avisos de progresso (processo auxiliar → programa)
_cancel = None  # sinal de cancelamento (programa → processo auxiliar)


# ------------------------------------------------------------------ lado do processo auxiliar
def _init(progress, cancel) -> None:
    global _progress, _cancel
    _progress, _cancel = progress, cancel


class _ChildContext(Context):
    def check(self) -> None:
        if _cancel is not None and _cancel.is_set():
            raise Cancelled()

    def progress(self, done: int, total: int, message: str = "") -> None:
        self.check()
        _progress.put((done, max(total, 1), message))


def _call(func: Callable, args: tuple, kwargs: dict):
    return func(*args, ctx=_ChildContext(), **kwargs)


# ------------------------------------------------------------------ lado do programa
def _get_pool() -> ProcessPoolExecutor:
    global _pool, _progress, _cancel
    if _pool is None:
        mp = multiprocessing.get_context("spawn")
        _progress, _cancel = mp.Queue(), mp.Event()
        _pool = ProcessPoolExecutor(max_workers=1, mp_context=mp, initializer=_init,
                                    initargs=(_progress, _cancel))
    return _pool


def _kill_pool() -> None:
    """Encerra o processo auxiliar na hora (cancelamento ou saída do programa)."""
    global _pool
    if _pool is None:
        return
    pool, _pool = _pool, None
    pool.shutdown(wait=False, cancel_futures=True)
    for proc in list((getattr(pool, "_processes", None) or {}).values()):  # sem API pública para isso
        try:
            proc.terminate()
        except Exception:  # noqa: BLE001
            pass


atexit.register(_kill_pool)


def total_size(paths) -> int:
    size = 0
    for p in paths:
        try:
            size += os.path.getsize(p)
        except OSError:
            pass
    return size


def run(func: Callable, *args, ctx: Context, inputs: list[str] = (), **kwargs):
    """Chama `func(*args, ctx=..., **kwargs)`; num processo auxiliar se os arquivos forem grandes.

    `func` precisa ser uma função de módulo (não lambda). Erros (PdfError etc.) e o
    cancelamento chegam aqui como se a função tivesse rodado neste processo.
    """
    if total_size(inputs) < SMALL:
        return func(*args, ctx=ctx, **kwargs)
    pool = _get_pool()
    _cancel.clear()
    while True:  # descarta avisos que sobraram de uma operação anterior
        try:
            _progress.get_nowait()
        except queue.Empty:
            break
    future = pool.submit(_call, func, args, kwargs)
    try:
        while True:
            try:
                done, total, message = _progress.get(timeout=0.1)
                ctx.progress(done, total, message)
                continue
            except queue.Empty:
                pass
            if future.done():
                while True:  # repassa os últimos avisos antes do resultado
                    try:
                        ctx.progress(*_progress.get_nowait())
                    except queue.Empty:
                        break
                return future.result()
            ctx.check()
    except Cancelled:
        _cancel.set()
        _kill_pool()
        raise
    except BrokenProcessPool:  # o processo auxiliar morreu (ex.: falta de memória): recria na próxima
        _kill_pool()
        raise
