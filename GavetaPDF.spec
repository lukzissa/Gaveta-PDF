# -*- mode: python ; coding: utf-8 -*-
# Gera dist\GavetaPDF\GavetaPDF.exe  (modo pasta: abre mais rápido e gera menos alarmes de antivírus)
import os
import re

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
)

block_cipher = None

# Versão lida de gavetapdf/__init__.py (único lugar onde ela é definida)
with open(os.path.join("gavetapdf", "__init__.py"), encoding="utf-8") as fh:
    VERSION = re.search(r'__version__ = "([^"]+)"', fh.read()).group(1)
numbers = tuple(int(n) for n in VERSION.split("."))
numbers = (numbers + (0, 0, 0, 0))[:4]
version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=numbers, prodvers=numbers, mask=0x3F, flags=0x0, OS=0x40004,
                      fileType=0x1, subtype=0x0, date=(0, 0)),
    kids=[
        StringFileInfo([StringTable("041604B0", [
            StringStruct("CompanyName", "Gaveta PDF"),
            StringStruct("FileDescription", "Gaveta PDF - ferramentas de PDF offline"),
            StringStruct("FileVersion", VERSION),
            StringStruct("InternalName", "GavetaPDF"),
            StringStruct("LegalCopyright", "Lucas Issa - AGPL-3.0"),
            StringStruct("OriginalFilename", "GavetaPDF.exe"),
            StringStruct("ProductName", "Gaveta PDF"),
            StringStruct("ProductVersion", VERSION),
        ])]),
        VarFileInfo([VarStruct("Translation", [0x0416, 1200])]),
    ],
)
os.makedirs("build", exist_ok=True)
with open(os.path.join("build", "version_info.txt"), "w", encoding="utf-8") as fh:
    fh.write(str(version_info))

tessdata = [(os.path.join("tessdata", f), "tessdata")
            for f in os.listdir("tessdata") if f.endswith(".traineddata")]

a = Analysis(
    ["GavetaPDF.py"],
    pathex=[],
    binaries=[],
    datas=tessdata + [("assets/icon.png", "assets")],
    hiddenimports=["PySide6.QtSvg"],
    excludes=[
        # integrações opcionais que puxariam bibliotecas enormes
        # (numpy, lxml e fontTools ficam: o PDF → Word precisa deles)
        "scipy", "pandas", "matplotlib", "PIL", "IPython", "fire",
        "tkinter", "unittest", "pydoc", "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
        "PySide6.QtQml", "PySide6.QtQuick", "PySide6.Qt3DCore", "PySide6.QtMultimedia",
        "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtPdf",
    ],
    noarchive=False,
)
# DLLs que o programa não usa: vídeo do OpenCV e OpenGL por software do Qt (~50 MB)
UNUSED_DLLS = ("opencv_videoio_ffmpeg", "opengl32sw")
a.binaries = [b for b in a.binaries if not os.path.basename(b[0]).lower().startswith(UNUSED_DLLS)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GavetaPDF",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon="assets/icon.ico",
    version=os.path.join("build", "version_info.txt"),
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="GavetaPDF")
