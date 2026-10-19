@echo off
chcp 65001 >nul
title Nap Code RCWL-1601 vao ESP32
echo ==================================================
echo   TU DONG NAP CODE RCWL-1601 VAO ESP32
echo ==================================================
python "%~dp0run_terminal.py" --upload
echo.
pause
