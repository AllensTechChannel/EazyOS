@echo off
title EazyOS Python Environment Setup
echo ====================================================
echo Checking Python installation...
echo ====================================================
echo.
cd /d "%~dp0"
start song.vbs
COLOR 1F

:: --- Check if Python exists ---
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading and installing Python...
    echo.

    :: --- Set download URL and temporary installer path ---
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"

    :: --- Download Python installer using PowerShell ---
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"

    :: --- Install Python silently for all users, add to PATH ---
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 InstallLauncherAllUsers=1

    :: --- Remove installer safely ---
    if exist "%PYTHON_INSTALLER%" del "%PYTHON_INSTALLER%"

    echo Python installed successfully!

    :: --- Detect actual Python install path ---
    for /f "delims=" %%i in ('where python') do set "PYTHON_PATH=%%~dpi"
    set "PYTHON_SCRIPTS=%PYTHON_PATH%Scripts\"

    :: --- Add Python to current session PATH ---
    set "PATH=%PYTHON_PATH%;%PYTHON_SCRIPTS%;%PATH%"
) else (
    echo Python is already installed.
)

echo.
echo Upgrading pip and installing required packages...
echo.

:: --- Upgrade pip safely ---
py -m ensurepip --upgrade
py -m pip install --upgrade pip

:: --- Install required packages ---
py -m pip install Pillow pygame tk psutil py-cpuinfo

echo.
echo ====================================================
echo Updates
echo Lanching Updates.txt
echo ====================================================
cd /d "%~dp0"
cls
:: --- Show updates.txt (if intended) ---
if exist updates.txt type updates.txt
echo.
echo.
pause
echo Ending process "wscript.exe" 
taskkill /f /im wscript.exe >nul 2>&1
echo.
echo ====================================================
echo All packages installed successfully!
echo Launching boot.py...
echo ====================================================
:: --- Run your Python program ---
py boot.py

pause
