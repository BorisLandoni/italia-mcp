@echo off
cd /d "%~dp0"
title Panda Italia
echo ==================================================
echo   Panda Italia - servizi italiani per xiaozhi
echo   Lascia questa finestra APERTA.
echo   Per fermare: chiudi la finestra oppure Ctrl+C
echo ==================================================
echo.
".venv\Scripts\python.exe" -m italia_mcp.bridge %*
echo.
echo Il collegamento si e' interrotto.
pause
