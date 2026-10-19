@echo off
chcp 65001 >nul
title Phan Tich Du Lieu Do RCWL-1601
python "%~dp0data_analysis.py"
echo.
pause
