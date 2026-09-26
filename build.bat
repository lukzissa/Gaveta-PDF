@echo off
REM ===== Gera o executavel do Gaveta PDF =====
REM Requisito: Python 3.10+ instalado (marque "Add python.exe to PATH").
setlocal
cd /d "%~dp0"

if not exist .venv (
    echo Criando ambiente virtual...
    python -m venv .venv || goto :erro
)
call .venv\Scripts\activate.bat

echo Instalando dependencias...
python -m pip install --upgrade pip >nul
pip install -r requirements-dev.txt || goto :erro

REM Idiomas do OCR (versao "fast": menores e rapidos)
if not exist tessdata mkdir tessdata
for %%L in (por eng spa rus) do (
    if not exist tessdata\%%L.traineddata (
        echo Baixando idioma de OCR: %%L
        powershell -NoProfile -Command "Invoke-WebRequest -Uri https://github.com/tesseract-ocr/tessdata_fast/raw/main/%%L.traineddata -OutFile tessdata\%%L.traineddata" || goto :erro
    )
)

echo Rodando testes...
python -m pytest -q tests || goto :erro

echo Gerando executavel...
pyinstaller --noconfirm --clean GavetaPDF.spec || goto :erro

echo Gerando versao portatil (.zip)...
for /f %%v in ('python -c "import gavetapdf; print(gavetapdf.__version__)"') do set VERSAO=%%v
set ZIP=dist\GavetaPDF-%VERSAO%-portatil.zip
if exist "%ZIP%" del "%ZIP%"
powershell -NoProfile -Command "Compress-Archive -Path 'dist\GavetaPDF' -DestinationPath '%ZIP%'" || goto :erro

echo.
echo Pronto!
echo   Executavel: dist\GavetaPDF\GavetaPDF.exe
echo   Portatil:   %ZIP%  (extraia e abra o GavetaPDF.exe, sem instalar)
echo Para criar o instalador, abra installer.iss no Inno Setup e clique em Compile.
goto :eof

:erro
echo.
echo *** Ocorreu um erro. Veja as mensagens acima. ***
exit /b 1
