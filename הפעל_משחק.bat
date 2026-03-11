@echo off
chcp 65001 >nul
title 🌍 משחק ערי בירה
echo.
echo  ╔══════════════════════════════════════╗
echo  ║     🌍 משחק ערי הבירה של המשפחה     ║
echo  ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: Find local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
    set "LOCAL_IP=%%a"
)
set "LOCAL_IP=%LOCAL_IP: =%"

echo  📱 כל אחד מהמשפחה יכול להיכנס מהטלפון:
echo.
echo     http://%LOCAL_IP%:8505
echo.
echo  💻 מהמחשב הזה:
echo     http://localhost:8505
echo.
echo  ─────────────────────────────────────
echo  ❌ לסגירת השרת: סגרו את החלון הזה
echo  ─────────────────────────────────────
echo.

.venv\Scripts\python.exe -m streamlit run app.py --server.port 8505 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
pause
