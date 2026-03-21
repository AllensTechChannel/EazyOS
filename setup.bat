@echo off
title EazyOS Installer
color 1F
setlocal enabledelayedexpansion
if exist song.vbs start song.vbs

echo ====================================================
echo Checking Python installation...
echo ====================================================

:: Check if Python is in the PATH
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Initiating Auto-Install...
    
    set "PY_VER= 3.14.3"
    set "PY_EXE=python-installer.exe"
    
    echo Downloading Python !PY_VER!...
	

    winget install -e --id Python.Python.3.13 --silent --accept-package-agreements --scope machine


   

    echo Installing Python... Please wait...
    :: Install silently, add to PATH, and install pip for all users
    start /wait !PY_EXE! /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    del !PY_EXE!
    echo Python installed successfully. 
    echo Please RESTART this script to refresh system environment variables.
    pause
    exit /b 0
)

echo Python is already installed.
echo.
cd /d "%~dp0"
:: Start background audio if it exists

COLOR 1F

echo Installing/Updating required packages...
echo.

:: Ensure pip is ready
py -m ensurepip --upgrade
py -m pip install --upgrade pip

:: List of packages to install
set "PACKAGES=Pillow pygame-ce psutil py-cpuinfo"

for %%p in (%PACKAGES%) do (
    echo Installing %%p...
    py -m pip install %%p
	cls
    if !errorlevel! neq 0 (
        echo WARNING: Failed to install %%p
    )
)

echo.
echo ====================================================
echo Verifying installations...
echo ====================================================

echo.
echo Attempting to install PIL
echo.
py -c "import PIL; print('v Pillow')"
cls

echo.
echo Installing Pygame CE
echo.
py -c "import pygame_ce; print('v pygame-ce')" 2>nul || py -c "import pygame; print('v pygame')"
cls
echo.
echo Installing Packageing
echo.
py -m pip install packaging
echo.
echo Installing Psutil
echo.
py -c "import psutil; print('v psutil')"
cls

echo.
echo Installing cpuinfo
echo.
py -c "import cpuinfo; print('v py-cpuinfo')"

echo.
echo Installing PyQt5
echo.
cls
py -m pip install PyQt5

echo.
echo PyQtWebEngine
echo.

py -m pip install PyQtWebEngine

echo.
echo Installing ttkbootstrap
echo.
py -m pip install ttkbootstrap

echo.
echo Attempting to install requests
echo.
py -m pip install requests
cls

echo.
echo ====================================================
echo Environment Ready!
echo ====================================================

if exist updates.txt (
    type updates.txt
    echo.
)

:: Clean up background tasks
taskkill /f /im wscript.exe >nul 2>&1

echo Launching boot.py...
cd ..
py boot.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: boot.py encountered an error!
    pause
)
pause