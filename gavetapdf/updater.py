"""Atualização automática pelo GitHub Releases.

Fluxo: ao abrir, o programa consulta a última release do repositório (GITHUB_REPO).
Se a versão for mais nova, o usuário confirma, o .zip portátil é baixado para
dados/update, conferido (SHA-256 publicado pelo GitHub) e extraído. Um pequeno script
do PowerShell espera o programa fechar, copia os arquivos novos por cima (sem tocar
no GavetaPDF.ini nem na pasta "dados") e abre a versão nova.

Para publicar uma versão: crie uma release com a tag "vX.Y" e anexe o
GavetaPDF-X.Y-portatil.zip gerado pelo build.bat.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from dataclasses import dataclass

from . import GITHUB_REPO, __version__, paths
from .core.common import NULL_CONTEXT, Cancelled, Context, PdfError
from .i18n import tr

API_URL = "https://api.github.com/repos/{repo}/releases/latest"
EXE_NAME = "GavetaPDF.exe"
PRESERVE = ("GavetaPDF.ini", "dados")  # nunca sobrescritos nem apagados
TIMEOUT = 8  # segundos


@dataclass
class Release:
    version: str
    notes: str
    page_url: str
    zip_url: str | None
    zip_name: str
    size: int
    sha256: str | None


def version_tuple(text: str) -> tuple[int, ...]:
    """"v1.10" → (1, 10). Partes não numéricas (ex.: "-beta") são ignoradas."""
    return tuple(int(n) for n in re.findall(r"\d+", text.split("-")[0])[:4]) or (0,)


def is_newer(remote: str, local: str = __version__) -> bool:
    return version_tuple(remote) > version_tuple(local)


def is_enabled() -> bool:
    """Só o programa gerado (.exe) se atualiza; rodando pelo código não faz sentido."""
    return bool(GITHUB_REPO) and getattr(sys, "frozen", False)


def _request(url: str):
    req = urllib.request.Request(url, headers={
        "User-Agent": f"GavetaPDF/{__version__}",
        "Accept": "application/vnd.github+json",
    })
    return urllib.request.urlopen(req, timeout=TIMEOUT)  # noqa: S310 - URL fixa do GitHub (https)


def parse_release(data: dict) -> Release | None:
    """Extrai da resposta da API a versão e o .zip portátil (None se for rascunho/pré-lançamento)."""
    if data.get("draft") or data.get("prerelease") or not data.get("tag_name"):
        return None
    asset = next((a for a in data.get("assets", [])
                  if a.get("name", "").lower().endswith("portatil.zip")), None)
    digest = (asset or {}).get("digest") or ""
    return Release(
        version=data["tag_name"].lstrip("vV"),
        notes=(data.get("body") or "").strip(),
        page_url=data.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases/latest",
        zip_url=asset.get("browser_download_url") if asset else None,
        zip_name=asset.get("name", "") if asset else "",
        size=int(asset.get("size") or 0) if asset else 0,
        sha256=digest.split(":", 1)[1].lower() if digest.startswith("sha256:") else None,
    )


def latest_release() -> Release | None:
    """Última release publicada, ou None se não houver ou sem internet."""
    try:
        with _request(API_URL.format(repo=GITHUB_REPO)) as resp:
            return parse_release(json.load(resp))
    except Exception:  # noqa: BLE001 - sem internet, repositório sem releases etc.: segue a vida
        return None


def update_dir() -> str | None:
    d = paths.data_dir()
    return os.path.join(d, "update") if d else None


def download(release: Release, ctx: Context = NULL_CONTEXT) -> str:
    """Baixa o .zip da release para dados/update e confere o SHA-256."""
    folder = update_dir()
    if folder is None:
        raise PdfError(tr("A pasta do programa não permite gravação, então não dá para atualizar automaticamente.\n"
                          "Baixe a versão nova pelo site."))
    if not release.zip_url:
        raise PdfError(tr("A versão nova ainda não tem o arquivo para atualização automática.\n"
                          "Baixe pelo site."))
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, release.zip_name or "update.zip")
    sha = hashlib.sha256()
    try:
        with _request(release.zip_url) as resp, open(target, "wb") as fh:
            total = release.size or int(resp.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = resp.read(256 * 1024)
                if not chunk:
                    break
                fh.write(chunk)
                sha.update(chunk)
                done += len(chunk)
                mb = done / 1024 / 1024
                ctx.progress(done, total or done + 1, tr("Baixando atualização… {0:.1f} MB", mb))
    except (PdfError, Cancelled):
        raise
    except Exception as exc:  # noqa: BLE001 - rede, disco cheio etc.
        raise PdfError(tr("Não foi possível baixar a atualização.\nVerifique a internet e tente de novo.\n\n{0}", exc)) from exc
    if release.sha256 and sha.hexdigest() != release.sha256:
        os.remove(target)
        raise PdfError(tr("O arquivo baixado está corrompido (a verificação de segurança falhou).\nTente de novo mais tarde."))
    return target


def prepare(zip_path: str) -> str:
    """Extrai a atualização e devolve a pasta que contém o GavetaPDF.exe novo."""
    dest = os.path.join(os.path.dirname(zip_path), "novo")
    shutil.rmtree(dest, ignore_errors=True)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            root = os.path.realpath(dest)
            for name in zf.namelist():  # não deixa o .zip gravar fora da pasta
                if not os.path.realpath(os.path.join(dest, name)).startswith(root + os.sep):
                    raise PdfError(tr("O arquivo de atualização é inválido."))
            zf.extractall(dest)
    except zipfile.BadZipFile as exc:
        raise PdfError(tr("O arquivo de atualização é inválido.")) from exc
    for folder, _, files in os.walk(dest):
        if EXE_NAME in files:
            return folder
    raise PdfError(tr("O arquivo de atualização é inválido."))


def _ps(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def write_script(new_dir: str, app_dir: str, pid: int) -> str:
    """Script do PowerShell que troca os arquivos depois que o programa fecha e o reabre."""
    folder = update_dir()
    assert folder, "download() já garantiu que a pasta de dados existe"
    script = os.path.join(folder, "aplicar.ps1")
    exclude_files = " ".join(_ps(n) for n in PRESERVE)
    body = f"""$ErrorActionPreference = 'SilentlyContinue'
$new = {_ps(new_dir)}
$app = {_ps(app_dir)}
Wait-Process -Id {pid} -Timeout 60
# processos auxiliares (OCR, operações pesadas) também são o GavetaPDF.exe desta pasta:
# espera todos terminarem para nenhum arquivo ficar preso; o que sobrar é encerrado
$prefix = (Join-Path $app '')
$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline -and (Get-Process | Where-Object {{ $_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) }})) {{
    Start-Sleep -Milliseconds 300
}}
Get-Process | Where-Object {{ $_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) }} | Stop-Process -Force
Start-Sleep -Milliseconds 500
# _internal é espelhada (remove arquivos que não existem mais); o resto é copiado por cima
robocopy (Join-Path $new '_internal') (Join-Path $app '_internal') /MIR /R:5 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
robocopy $new $app /E /XD (Join-Path $new '_internal') /XF {exclude_files} /XD {exclude_files} /R:5 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
Start-Process -FilePath (Join-Path $app {_ps(EXE_NAME)}) -WorkingDirectory $app
Start-Sleep -Seconds 2
Remove-Item -LiteralPath {_ps(folder)} -Recurse -Force
"""
    with open(script, "w", encoding="utf-8-sig") as fh:  # BOM: o PowerShell 5 lê acentos corretamente
        fh.write(body)
    return script


def launch(script: str) -> None:
    """Roda o script escondido e independente do programa (que deve fechar em seguida)."""
    # Console oculto (CREATE_NO_WINDOW) em vez de DETACHED_PROCESS: sem console o
    # PowerShell nem inicia. Novo grupo de processos e, se o Windows permitir, fora do
    # "job" do programa, para o script continuar vivo depois que ele fechar.
    no_window, new_group, breakaway = 0x08000000, 0x00000200, 0x01000000
    command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", script]
    try:
        subprocess.Popen(command, creationflags=no_window | new_group | breakaway, close_fds=True)
    except OSError:  # job que não permite sair: roda dentro dele mesmo
        subprocess.Popen(command, creationflags=no_window | new_group, close_fds=True)
