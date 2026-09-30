"""OCR: transforma PDFs escaneados e imagens em PDFs pesquisáveis.

Usa o Tesseract embutido no MuPDF — não é preciso instalar nada além dos
arquivos de idioma (*.traineddata) na pasta "tessdata".
"""
from __future__ import annotations

import math
import os
import sys
import time

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


STEPS = 100  # unidades de progresso por página
FIRST_ESTIMATE = 0.6  # segundos por megapixel, até medir as primeiras páginas
STARTUP = 1.5  # segundos para abrir cada processo auxiliar


def _ocr_job(path: str, index: int, dpi: int, lang: str, tessdata: str) -> bytes:
    """Roda num processo auxiliar: desenha a página e reconhece o texto.

    O Tesseract embutido no MuPDF segura o interpretador Python enquanto trabalha, então
    se rodasse no próprio programa a janela congelaria (sem barra de progresso nem como
    cancelar). Em processos separados a janela fica livre, e várias páginas são
    reconhecidas ao mesmo tempo.
    """
    with open_pdf(path) as doc:
        pix = doc[index].get_pixmap(dpi=dpi, alpha=False)
    pix.set_dpi(dpi, dpi)  # mantém o tamanho físico original da página
    return pix.pdfocr_tobytes(compress=True, language=lang, tessdata=tessdata)


def _stop(executor) -> None:
    """Encerra os processos auxiliares na hora (ex.: o usuário cancelou)."""
    executor.shutdown(wait=False, cancel_futures=True)
    for proc in list((getattr(executor, "_processes", None) or {}).values()):  # sem API pública para isso
        try:
            proc.terminate()
        except Exception:  # noqa: BLE001
            pass


def ocr_file(
    path: str,
    out: str,
    languages: list[str] | None = None,
    dpi: int = 300,
    skip_text_pages: bool = True,
    ctx: Context = NULL_CONTEXT,
) -> dict:
    """Gera um PDF pesquisável. Retorna estatísticas simples."""
    import multiprocessing
    from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait

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
    ctx.progress(0, total * STEPS, tr("Reconhecendo texto — página {0} de {1}", 1, total))
    todo = [i for i, page in enumerate(src) if is_image or not skip_text_pages or not page_has_text(page)]
    megapixels = {i: src[i].rect.width * src[i].rect.height * (dpi / 72) ** 2 / 1e6 for i in todo}

    executor = None
    try:
        results: dict[int, bytes] = {}
        if todo:
            workers = max(1, min(len(todo), (os.cpu_count() or 2) - 1, 4))
            executor = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
            futures = {executor.submit(_ocr_job, path, i, dpi, lang, tessdata): i for i in todo}
            pending = set(futures)
            began: dict = {}  # quando cada página começou a ser reconhecida
            rates: list[float] = []  # segundos por megapixel das páginas já prontas
            done_pages = total - len(todo)
            while pending:
                finished, pending = wait(pending, timeout=0.2, return_when=FIRST_COMPLETED)
                now = time.monotonic()
                for fut in finished:
                    i = futures[fut]
                    try:
                        results[i] = fut.result()
                    except Exception as exc:  # noqa: BLE001
                        raise PdfError(tr("Falha no OCR da página {0}:\n{1}", i + 1, exc)) from exc
                    if fut in began:
                        rates.append((now - began[fut]) / max(megapixels[i], 0.1))
                    done_pages += 1
                # páginas em andamento avançam pelo tempo esperado, sem passar do fim
                rate = sum(rates) / len(rates) if rates else FIRST_ESTIMATE
                partial = 0.0
                for fut in pending:
                    if fut.running():
                        began.setdefault(fut, now)
                        expected = rate * megapixels[futures[fut]] + (0 if rates else STARTUP)
                        partial += 0.95 * (1 - math.exp(-(now - began[fut]) / max(expected, 0.5)))
                current = min(done_pages + 1, total)
                ctx.progress(int((done_pages + partial) * STEPS), total * STEPS,
                             tr("Reconhecendo texto — página {0} de {1}", current, total))
            executor.shutdown()
            executor = None

        for i in range(total):
            if i in results:
                with pymupdf.open("pdf", results[i]) as ocr_page:
                    result.insert_pdf(ocr_page)
                stats["ocr_pages"] += 1
            else:
                result.insert_pdf(src, from_page=i, to_page=i)
                stats["skipped"] += 1
        src.close()
        ctx.progress(total * STEPS, total * STEPS, tr("Salvando…"))
        save_pdf(result, out)
    finally:
        if executor is not None:
            _stop(executor)
        if not src.is_closed:
            src.close()
        result.close()
    return stats
