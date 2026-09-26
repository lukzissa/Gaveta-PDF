"""Compressão de PDFs: recompacta imagens, remove objetos inúteis e subconjunta fontes."""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass

from .common import NULL_CONTEXT, Context, open_pdf
from ..i18n import tr


@dataclass(frozen=True)
class Level:
    label: str
    description: str
    dpi_target: int
    quality: int


LEVELS: dict[str, Level] = {
    "leve": Level(tr("Leve"), tr("Qualidade quase igual, redução menor"), 200, 85),
    "recomendada": Level(tr("Recomendada"), tr("Bom equilíbrio para enviar por e-mail"), 144, 70),
    "forte": Level(tr("Forte"), tr("Menor tamanho possível, imagens mais simples"), 96, 50),
}


@dataclass
class CompressResult:
    out: str
    before: int
    after: int
    kept_original: bool = False

    @property
    def saved_percent(self) -> float:
        if self.before == 0:
            return 0.0
        return max(0.0, (1 - self.after / self.before) * 100)


def compress(
    path: str,
    out: str,
    level: str = "recomendada",
    grayscale: bool = False,
    ctx: Context = NULL_CONTEXT,
) -> CompressResult:
    cfg = LEVELS[level]
    before = os.path.getsize(path)
    ctx.progress(0, 4, tr("Abrindo arquivo…"))
    doc = open_pdf(path)
    try:
        ctx.progress(1, 4, tr("Recomprimindo imagens…"))
        doc.rewrite_images(
            dpi_threshold=cfg.dpi_target + 20,
            dpi_target=cfg.dpi_target,
            quality=cfg.quality,
            lossy=True,
            lossless=True,
            bitonal=True,
            color=True,
            gray=True,
            set_to_gray=grayscale,
        )
        ctx.progress(2, 4, tr("Otimizando fontes…"))
        try:
            doc.subset_fonts()
        except Exception:  # noqa: BLE001 - fontes incomuns não devem impedir a compressão
            pass
        ctx.progress(3, 4, tr("Salvando…"))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        tmp = out + ".tmp"
        doc.save(tmp, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True,
                 clean=True, use_objstms=1)
    finally:
        doc.close()

    after = os.path.getsize(tmp)
    kept_original = False
    if after >= before:
        # Nada a ganhar: entrega uma cópia do original em vez de um arquivo maior.
        os.remove(tmp)
        if os.path.abspath(path) != os.path.abspath(out):
            shutil.copyfile(path, out)
        after = before
        kept_original = True
    else:
        os.replace(tmp, out)
    ctx.progress(4, 4, tr("Concluído"))
    return CompressResult(out, before, after, kept_original)
