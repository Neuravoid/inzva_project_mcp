@echo off
echo Chatbot Backend Server baslatiliyor...
echo.

REM Ana proje dizinine git
cd /d "%~dp0..\"

REM Python environment'i aktif et (eger varsa)
if exist "project_env\Scripts\activate.bat" (
    echo Python environment aktif ediliyor...
    call project_env\Scripts\activate.bat
) else (
    echo Python environment bulunamadi, system Python kullaniliyor...
)

REM Backend dizinine git
cd chatbot-backend

REM Gerekli paketleri yukle
echo Gerekli paketler kontrol ediliyor...
pip install -r requirements.txt

echo.
echo Backend server http://localhost:8080 adresinde baslatiliyor...
echo Frontend ile test etmek icin http://localhost:5173 adresini kullanin
echo.
echo Server'i durdurmak icin Ctrl+C basin
echo.

REM FastAPI server'i baslat
python main.py

pause