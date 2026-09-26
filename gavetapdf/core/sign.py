"""Assinatura visual: insere a imagem de uma assinatura em posições escolhidas do PDF."""
from __future__ import annotations

from dataclasses import dataclass

import pymupdf

from .common import NULL_CONTEXT, Context, PdfError, open_pdf, save_pdf
from ..i18n import tr


@dataclass
class Placement:
    """Onde carimbar a assinatura.

    `rect` é (x0, y0, x1, y1) em pontos, nas coordenadas da página como ela aparece
    na tela (já considerando a rotação), com origem no canto superior esquerdo.
    """

    page: int
    rect: tuple[float, float, float, float]


def clean_signature_image(data: bytes, threshold: int = 215) -> bytes:
    """Remove o fundo claro de uma foto ou digitalização da assinatura.

    Pixels mais claros que `threshold` ficam transparentes; os demais mantêm a cor,
    com a transparência proporcional à intensidade do traço (bordas suaves).
    Também recorta as margens vazias. Retorna um PNG com canal alfa.
    """
    try:
        src = pymupdf.Pixmap(data)
    except Exception as exc:  # noqa: BLE001
        raise PdfError(tr("Não foi possível abrir a imagem da assinatura.\n\n{0}", exc)) from exc
    if src.alpha:
        src = pymupdf.Pixmap(src, 0)
    if src.colorspace is None or src.colorspace.n != 3:
        src = pymupdf.Pixmap(pymupdf.csRGB, src)
    gray = pymupdf.Pixmap(pymupdf.csGRAY, src)

    # Tabela de tons de cinza → opacidade: claro some, escuro fica opaco.
    table = bytes(0 if v >= threshold else min(255, int((threshold - v) * 255 / max(threshold - 60, 1)))
                  for v in range(256))
    alpha = gray.samples.translate(table)
    out = pymupdf.Pixmap(src, 1)
    out.set_alpha(alpha, premultiply=False)

    box = _opaque_bbox(alpha, out.width, out.height)
    if box is None:
        raise PdfError(tr("A imagem parece estar em branco: nenhum traço de assinatura foi encontrado."))
    if box != (0, 0, out.width, out.height):
        out = _crop(out, box)
    return out.tobytes("png")


def _opaque_bbox(alpha: bytes, w: int, h: int, margin: int = 6) -> tuple[int, int, int, int] | None:
    rows = [y for y in range(h) if alpha[y * w:(y + 1) * w].strip(b"\x00")]
    if not rows:
        return None
    y0, y1 = rows[0], rows[-1] + 1
    x0, x1 = w, 0
    for y in range(y0, y1):
        line = alpha[y * w:(y + 1) * w]
        stripped_left = len(line) - len(line.lstrip(b"\x00"))
        stripped_right = len(line.rstrip(b"\x00"))
        if stripped_right:
            x0 = min(x0, stripped_left)
            x1 = max(x1, stripped_right)
    return (max(0, x0 - margin), max(0, y0 - margin), min(w, x1 + margin), min(h, y1 + margin))


def _crop(pix: pymupdf.Pixmap, box: tuple[int, int, int, int]) -> pymupdf.Pixmap:
    x0, y0, x1, y1 = box
    n = pix.n
    stride = pix.stride
    data = pix.samples
    rows = [data[y * stride + x0 * n:y * stride + x1 * n] for y in range(y0, y1)]
    return pymupdf.Pixmap(pix.colorspace, x1 - x0, y1 - y0, b"".join(rows), 1)


def has_digital_signature(doc: pymupdf.Document) -> bool:
    """Indica se o PDF já tem assinaturas digitais (que seriam invalidadas por alterações)."""
    try:
        return bool(doc.get_sigflags() > 0)
    except Exception:  # noqa: BLE001
        return False


def sign(path: str, image: bytes, placements: list[Placement], out: str, ctx: Context = NULL_CONTEXT) -> str:
    """Insere a imagem `image` (PNG/JPG) em cada posição de `placements` e salva em `out`."""
    if not placements:
        raise PdfError(tr("Clique na página para posicionar a assinatura antes de salvar."))
    with open_pdf(path) as doc:
        xref = 0
        for i, pl in enumerate(placements):
            ctx.progress(i, len(placements), tr("Assinando página {0}", pl.page + 1))
            if not 0 <= pl.page < doc.page_count:
                raise PdfError(tr("A página {0} não existe neste documento.", pl.page + 1))
            page = doc[pl.page]
            rect = pymupdf.Rect(pl.rect) * page.derotation_matrix
            if rect.is_empty:
                continue
            # A mesma imagem é gravada uma única vez e reaproveitada nas outras posições.
            xref = page.insert_image(rect, stream=image if not xref else None, xref=xref,
                                     rotate=page.rotation, keep_proportion=False, overlay=True)
        ctx.progress(len(placements), len(placements), tr("Salvando…"))
        save_pdf(doc, out)
    return out
