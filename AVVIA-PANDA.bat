@echo off
cd /d "%~dp0"
title italia-mcp -> Panda
echo ==================================================
echo   italia-mcp collegato al Panda
echo   Lascia questa finestra APERTA.
echo   Per fermare: chiudi la finestra oppure Ctrl+C
echo ==================================================
echo.
".venv\Scripts\python.exe" mcp_pipe.py "xiaozhi\italia_server.py"
echo.
echo Il collegamento si e' interrotto.
pause
