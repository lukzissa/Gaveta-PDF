"""Utilidades compartilhadas pelo núcleo de processamento."""
from __future__ import annotations

import math
import os
import re
import threading
import time
from contextlib import contextmanager
from typing import Callable, Optional

import pymupdf

from ..i18n import decimal_separator, tr


class Cancelled(Exception):
    """Operação cancelada pelo usuário."""


class PdfError(Exception):
    """Erro com mensagem amigável para exibir ao usuário."""


class Context:
    """Canal de progresso e cancelamento entre o núcleo e a interface."""

    def __init__(
        self,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> None:
        self._on_progress = on_progress
        self._is_cancelled = is_cancelled

    def check(self) -> None:
        if self._is_cancelled and self._is_cancelled():
            raise Cancelled()

    def progress(self, done: int, total: int, message: str = "") -> None:
        self.check()
        if self._on_progress:
            self._on_progress(done, max(total, 1), message)


NULL_CONTEXT = Context()


@contextmanager
def ticking(ctx: Context, start: int, span: int, total: int, seconds: float, message: str):
    """Avança a barra de `start` até perto de `start + span` durante uma etapa longa sem avisos.

    Usado em passos únicos e demorados (ex.: a análise inicial do PDF → Word). O avanço
    segue o tempo esperado (`seconds`) e desacelera perto do fim, sem ultrapassá-lo.
    Cancelar durante a etapa é respeitado assim que ela termina.
    """
    stop = threading.Event()
    cancelled: list[bool] = []

    def tick() -> None:
        began = time.monotonic()
        while not stop.wait(0.2):
            share = 1 - math.exp(-(time.monotonic() - began) / max(seconds, 0.5))
            try:
                ctx.progress(start + int(span * 0.95 * share), total, message)
            except Cancelled:
                cancelled.append(True)
                return

    thread = threading.Thread(target=tick, daemon=True)
    ctx.progress(start, total, message)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join()
    if cancelled:
        raise Cancelled()


def sub_context(ctx: Context, index: int, count: int, prefix: str = "") -> Context:
    """Contexto para o item `index` de um lote de `count` itens (progresso proporcional)."""
    scale = 1000

    def on_progress(done: int, total: int, message: str) -> None:
        overall = index * scale + int(done * scale / max(total, 1))
        label = f"{prefix} — {message}" if prefix and message else (prefix or message)
        ctx.progress(overall, count * scale, label)

    def is_cancelled() -> bool:
        try:
            ctx.check()
        except Cancelled:
            return True
        return False

    return Context(on_progress, is_cancelled)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif", ".webp"}


def open_pdf(path: str) -> pymupdf.Document:
    """Abre um PDF com mensagens de erro em português."""
    if not os.path.isfile(path):
        raise PdfError(tr("Arquivo não encontrado:\n{0}", path))
    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # noqa: BLE001
        raise PdfError(tr("Não foi possível abrir o arquivo:\n{0}\n\n{1}", os.path.basename(path), exc)) from exc
    if doc.needs_pass:
        doc.close()
        raise PdfError(
            tr("O arquivo “{0}” está protegido por senha.\nRemova a senha antes de usar este arquivo.", os.path.basename(path))
        )
    if not doc.is_pdf:
        # Aceita imagens e outros formatos suportados convertendo para PDF em memória.
        pdf_bytes = doc.convert_to_pdf()
        doc.close()
        doc = pymupdf.open("pdf", pdf_bytes)
    return doc


def page_count(path: str) -> int:
    with open_pdf(path) as doc:
        return doc.page_count


def parse_ranges(text: str, total: int) -> list[list[int]]:
    """Converte "1-3, 5, 8-" em grupos de índices (base 0).

    Cada item separado por vírgula ou ponto e vírgula vira um grupo.
    "8-" vai até o fim; "-3" começa na página 1.
    """
    groups: list[list[int]] = []
    parts = [p.strip() for p in re.split(r"[;,]", text) if p.strip()]
    if not parts:
        raise PdfError(tr("Informe ao menos uma página ou intervalo (ex.: 1-3, 5, 8-)."))
    for part in parts:
        m = re.fullmatch(r"(\d*)\s*-\s*(\d*)", part)
        if m:
            start = int(m.group(1)) if m.group(1) else 1
            end = int(m.group(2)) if m.group(2) else total
        elif part.isdigit():
            start = end = int(part)
        else:
            raise PdfError(tr("Intervalo inválido: “{0}”. Use o formato 1-3, 5, 8-.", part))
        if start < 1 or end > total or start > end:
            raise PdfError(
                tr("O intervalo “{0}” está fora do documento, que tem {1} página(s).", part, total)
            )
        groups.append(list(range(start - 1, end)))
    return groups


def unique_path(path: str) -> str:
    """Evita sobrescrever arquivos existentes acrescentando (2), (3)..."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f"{base} ({n}){ext}"):
        n += 1
    return f"{base} ({n}){ext}"


def stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def human_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024 or unit == "GB":
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}".replace(".", decimal_separator())
        num /= 1024
    return f"{num:.1f} GB".replace(".", decimal_separator())


def save_pdf(doc: pymupdf.Document, out: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    doc.save(out, garbage=3, deflate=True)
