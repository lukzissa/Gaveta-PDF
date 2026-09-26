@echo off
REM Roda o Gaveta PDF direto do codigo (sem gerar o .exe)
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python GavetaPDF.py %*
