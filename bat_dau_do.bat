@echo off
chcp 65001 >nul
title Do Khoang Cach RCWL-1601 (ESP32)
echo ==================================================
echo   CHE DO DO KHOANG CACH RCWL-1601 (ESP32)
echo ==================================================
python "%~dp0run_terminal.py" --measure
echo.
pause
