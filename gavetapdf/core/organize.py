"""Juntar, dividir, extrair e reorganizar páginas."""
from __future__ import annotations

import os
from dataclasses import dataclass

import pymupdf

from .common import NULL_CONTEXT, Context, PdfError, open_pdf, parse_ranges, save_pdf, stem, unique_path
from ..i18n import tr


def merge(files: list[str], out: str, ctx: Context = NULL_CONTEXT) -> str:
    """Une vários PDFs (ou imagens) em um único arquivo, na ordem dada."""
    if len(files) < 1:
        raise PdfError(tr("Adicione ao menos um arquivo."))
    result = pymupdf.open()
    for i, path in enumerate(files):
        ctx.progress(i, len(files), tr("Adicionando {0}", os.path.basename(path)))
        with open_pdf(path) as src:
            result.insert_pdf(src)
    ctx.progress(len(files), len(files), tr("Salvando…"))
    save_pdf(result, out)
    result.close()
    return out


def _write_pages(src: pymupdf.Document, pages: list[int], out: str) -> str:
    part = pymupdf.open()
    for p in pages:
        part.insert_pdf(src, from_page=p, to_page=p)
    out = unique_path(out)
    save_pdf(part, out)
    part.close()
    return out


def split_ranges(path: str, ranges_text: str, out_dir: str, ctx: Context = NULL_CONTEXT) -> list[str]:
    """Cria um arquivo para cada intervalo informado (ex.: "1-3, 4-6, 7-")."""
    outputs: list[str] = []
    with open_pdf(path) as src:
        groups = parse_ranges(ranges_text, src.page_count)
        for i, pages in enumerate(groups):
            ctx.progress(i, len(groups), tr("Criando parte {0} de {1}", i + 1, len(groups)))
            label = f"{pages[0] + 1}" if len(pages) == 1 else f"{pages[0] + 1}-{pages[-1] + 1}"
            name = tr("{0} - páginas {1}.pdf", stem(path), label)
            outputs.append(_write_pages(src, pages, os.path.join(out_dir, name)))
    ctx.progress(1, 1, tr("Concluído"))
    return outputs


def split_every(path: str, every: int, out_dir: str, ctx: Context = NULL_CONTEXT) -> list[str]:
    """Divide a cada N páginas (N=1 gera um arquivo por página)."""
    if every < 1:
        raise PdfError(tr("O número de páginas por arquivo deve ser 1 ou mais."))
    outputs: list[str] = []
    with open_pdf(path) as src:
        total = src.page_count
        starts = list(range(0, total, every))
        for i, start in enumerate(starts):
            ctx.progress(i, len(starts), tr("Criando parte {0} de {1}", i + 1, len(starts)))
            pages = list(range(start, min(start + every, total)))
            label = f"{pages[0] + 1}" if len(pages) == 1 else f"{pages[0] + 1}-{pages[-1] + 1}"
            name = tr("{0} - páginas {1}.pdf", stem(path), label)
            outputs.append(_write_pages(src, pages, os.path.join(out_dir, name)))
    ctx.progress(1, 1, tr("Concluído"))
    return outputs


def extract(path: str, ranges_text: str, out: str, ctx: Context = NULL_CONTEXT) -> str:
    """Junta as páginas selecionadas em um único arquivo novo."""
    with open_pdf(path) as src:
        groups = parse_ranges(ranges_text, src.page_count)
        pages = [p for g in groups for p in g]
        ctx.progress(0, 1, tr("Extraindo páginas…"))
        part = pymupdf.open()
        for p in pages:
            part.insert_pdf(src, from_page=p, to_page=p)
        save_pdf(part, out)
        part.close()
    ctx.progress(1, 1, tr("Concluído"))
    return out


@dataclass
class PageRef:
    """Uma página no editor: arquivo de origem, índice e rotação extra (graus)."""

    path: str
    index: int
    rotation: int = 0


def build_from_pages(pages: list[PageRef], out: str, ctx: Context = NULL_CONTEXT) -> str:
    """Monta um PDF a partir de páginas de um ou vários arquivos, em qualquer ordem."""
    if not pages:
        raise PdfError(tr("Não há páginas para salvar."))
    cache: dict[str, pymupdf.Document] = {}
    result = pymupdf.open()
    try:
        for i, ref in enumerate(pages):
            ctx.progress(i, len(pages), tr("Página {0} de {1}", i + 1, len(pages)))
            if ref.path not in cache:
                cache[ref.path] = open_pdf(ref.path)
            src = cache[ref.path]
            result.insert_pdf(src, from_page=ref.index, to_page=ref.index)
            if ref.rotation % 360:
                page = result[-1]
                page.set_rotation((page.rotation + ref.rotation) % 360)
        # As páginas já foram copiadas: fecha as origens antes de salvar,
        # assim é possível salvar por cima de um dos arquivos originais.
        for d in cache.values():
            d.close()
        cache.clear()
        ctx.progress(len(pages), len(pages), tr("Salvando…"))
        save_pdf(result, out)
    finally:
        result.close()
        for d in cache.values():
            d.close()
    return out
