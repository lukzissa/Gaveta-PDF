"""Testes da atualização automática (sem internet: o "download" vem de um arquivo local)."""
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gavetapdf import paths, updater  # noqa: E402
from gavetapdf.core.common import PdfError  # noqa: E402


def test_version_has_two_numbers():
    from gavetapdf import __version__

    assert re.fullmatch(r"\d+\.\d+", __version__), "a versão deve ter 2 números, ex.: 1.0, 1.1, 2.0"


def test_versions():
    assert updater.is_newer("1.1", "1.0")
    assert updater.is_newer("v1.10", "1.9")  # 1.10 vem depois de 1.9
    assert updater.is_newer("2.0", "1.12")
    assert not updater.is_newer("v1.0", "1.0")
    assert not updater.is_newer("0.9", "1.0")


def test_parse_release():
    data = {
        "tag_name": "v1.1", "body": "Novidades", "html_url": "https://github.com/x/y/releases/tag/v1.1",
        "assets": [
            {"name": "GavetaPDF-1.1-setup.exe", "browser_download_url": "https://x/setup.exe", "size": 1},
            {"name": "GavetaPDF-1.1-portatil.zip", "browser_download_url": "https://x/p.zip", "size": 10,
             "digest": "sha256:ABC"},
        ],
    }
    r = updater.parse_release(data)
    assert (r.version, r.zip_url, r.size, r.sha256) == ("1.1", "https://x/p.zip", 10, "abc")
    assert updater.parse_release({**data, "prerelease": True}) is None
    assert updater.parse_release({**data, "assets": []}).zip_url is None


def _fake_install(root: pathlib.Path) -> pathlib.Path:
    app = root / "GavetaPDF"
    (app / "_internal").mkdir(parents=True)
    (app / "GavetaPDF.exe").write_text("versao antiga")
    (app / "_internal" / "velho.dll").write_text("x")
    (app / "GavetaPDF.ini").write_text("[General]\ntheme=dark\n")
    (app / "dados").mkdir()
    (app / "dados" / "gavetapdf.log").write_text("log")
    return app


def _release_zip(root: pathlib.Path) -> tuple[pathlib.Path, str]:
    z = root / "GavetaPDF-9.9-portatil.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("GavetaPDF/GavetaPDF.exe", "versao nova")
        zf.writestr("GavetaPDF/_internal/novo.dll", "y")
    return z, hashlib.sha256(z.read_bytes()).hexdigest()


def test_download_prepare_and_apply(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        app = _fake_install(root)
        monkeypatch.setattr(paths, "app_dir", lambda: str(app))
        monkeypatch.setattr(paths, "_can_write", None)
        zip_path, sha = _release_zip(root)
        release = updater.Release("9.9", "", "", zip_path.as_uri(), zip_path.name, zip_path.stat().st_size, sha)

        # soma de verificação errada: recusa o arquivo
        bad = updater.Release(**{**release.__dict__, "sha256": "0" * 64})
        try:
            updater.download(bad)
        except PdfError as exc:
            assert "corrompido" in str(exc)
        else:
            raise AssertionError("deveria recusar o arquivo")

        new_dir = updater.prepare(updater.download(release))
        assert pathlib.Path(new_dir, "GavetaPDF.exe").read_text() == "versao nova"

        finished = subprocess.Popen(["cmd", "/c", "exit"])
        finished.wait()  # processo que já terminou: o script não precisa esperar
        # um "processo auxiliar" que ficou rodando dentro da pasta do programa
        helper = app / "_internal" / "auxiliar.exe"
        shutil.copy(os.path.join(os.environ["WINDIR"], "System32", "PING.EXE"), helper)
        leftover = subprocess.Popen([str(helper), "-n", "600", "127.0.0.1"], stdout=subprocess.DEVNULL)
        script = updater.write_script(new_dir, str(app), finished.pid)
        subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script],
                       check=True, timeout=120)
        assert leftover.poll() is not None, "o processo que sobrou precisa ser encerrado antes da troca"

        assert (app / "GavetaPDF.exe").read_text() == "versao nova"
        assert (app / "_internal" / "novo.dll").exists()
        assert not (app / "_internal" / "velho.dll").exists()  # arquivos que saíram da versão nova somem
        assert (app / "GavetaPDF.ini").read_text().startswith("[General]")  # configurações mantidas
        assert (app / "dados" / "gavetapdf.log").exists()
        assert not (app / "dados" / "update").exists()  # o script limpa o que baixou


def test_zip_cannot_write_outside(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        z = pathlib.Path(d) / "mau.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr("../../fora.txt", "x")
        try:
            updater.prepare(str(z))
        except PdfError:
            pass
        else:
            raise AssertionError("deveria recusar caminhos fora da pasta")
