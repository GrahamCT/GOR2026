@echo off
echo Running GOR Reporting...
call "%~dp0.venv\Scripts\activate.bat"
python "%~dp0gor_reporting.py"
if %errorlevel% neq 0 ( echo. & echo ERROR: Script failed & pause & exit /b 1 )
pause
