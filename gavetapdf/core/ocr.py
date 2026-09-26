"""OCR: transforma PDFs escaneados e imagens em PDFs pesquisáveis.

Usa o Tesseract embutido no MuPDF — não é preciso instalar nada além dos
arquivos de idioma (*.traineddata) na pasta "tessdata".
"""
from __future__ import annotations

import os
import sys

import pymupdf

from .common import IMAGE_EXTENSIONS, NULL_CONTEXT, Context, PdfError, open_pdf, save_pdf
from ..i18n import tr

LANGUAGE_NAMES = {
    "por": tr("Português"),
    "eng": tr("Inglês"),
    "spa": tr("Espanhol"),
    "rus": tr("Russo"),
    "fra": tr("Francês"),
    "deu": tr("Alemão"),
    "ita": tr("Italiano"),
}


def _candidate_dirs() -> list[str]:
    dirs: list[str] = []
    if getattr(sys, "frozen", False):
        dirs.append(os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)), "tessdata"))
        dirs.append(os.path.join(os.path.dirname(sys.executable), "tessdata"))
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dirs.append(os.path.join(root, "tessdata"))
    if os.environ.get("TESSDATA_PREFIX"):
        dirs.append(os.environ["TESSDATA_PREFIX"])
    return dirs


def find_tessdata() -> str | None:
    for d in _candidate_dirs():
        if os.path.isdir(d) and any(f.endswith(".traineddata") for f in os.listdir(d)):
            return d
    try:  # Tesseract instalado no sistema
        return pymupdf.get_tessdata()
    except Exception:  # noqa: BLE001
        return None


def available_languages(tessdata: str | None = None) -> list[str]:
    tessdata = tessdata or find_tessdata()
    if not tessdata or not os.path.isdir(tessdata):
        return []
    langs = sorted(f[:-12] for f in os.listdir(tessdata) if f.endswith(".traineddata") and f != "osd.traineddata")
    # Português primeiro
    return sorted(langs, key=lambda l: (l != "por", l != "eng", l))


def page_has_text(page: pymupdf.Page) -> bool:
    return len(page.get_text("text").strip()) > 20


def ocr_file(
    path: str,
    out: str,
    languages: list[str] | None = None,
    dpi: int = 300,
    skip_text_pages: bool = True,
    ctx: Context = NULL_CONTEXT,
) -> dict:
    """Gera um PDF pesquisável. Retorna estatísticas simples."""
    tessdata = find_tessdata()
    if not tessdata:
        raise PdfError(
            tr("Os arquivos de idioma do OCR não foram encontrados.\n"
            "Coloque os arquivos .traineddata na pasta “tessdata” ao lado do programa.")
        )
    langs = languages or ["por"]
    missing = [l for l in langs if not os.path.isfile(os.path.join(tessdata, f"{l}.traineddata"))]
    if missing:
        raise PdfError(tr("Idioma de OCR não instalado: {0}", ', '.join(missing)))
    lang = "+".join(langs)

    is_image = os.path.splitext(path)[1].lower() in IMAGE_EXTENSIONS
    src = open_pdf(path)
    result = pymupdf.open()
    total = src.page_count
    stats = {"pages": total, "ocr_pages": 0, "skipped": 0}
    try:
        for i, page in enumerate(src):
            ctx.progress(i, total, tr("Reconhecendo texto — página {0} de {1}", i + 1, total))
            if skip_text_pages and not is_image and page_has_text(page):
                result.insert_pdf(src, from_page=i, to_page=i)
                stats["skipped"] += 1
                continue
            pix = page.get_pixmap(dpi=dpi, alpha=False)
            pix.set_dpi(dpi, dpi)  # mantém o tamanho físico original da página
            try:
                data = pix.pdfocr_tobytes(compress=True, language=lang, tessdata=tessdata)
            except Exception as exc:  # noqa: BLE001
                raise PdfError(tr("Falha no OCR da página {0}:\n{1}", i + 1, exc)) from exc
            with pymupdf.open("pdf", data) as ocr_page:
                result.insert_pdf(ocr_page)
            stats["ocr_pages"] += 1
        src.close()
        ctx.progress(total, total, tr("Salvando…"))
        save_pdf(result, out)
    finally:
        if not src.is_closed:
            src.close()
        result.close()
    return stats
