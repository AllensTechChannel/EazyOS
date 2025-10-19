@echo off
title Python Environment Setup
echo ====================================================
echo Installing required Python packages...
echo ====================================================
echo.

:: === Show confirmation dialog ===
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $result=[System.Windows.Forms.MessageBox]::Show('Setup will now download Python. This might take a few minutes depending on your network connection.','Setup','OKCancel'); if ($result -eq 'Cancel') { exit 1 }"
if %errorlevel% neq 0 (
    echo Installation cancelled by user.
    exit /b
)

:: === Install Python ===
winget install -e --id Python.Python.3.12

:: === Upgrade pip ===
py -m pip install --upgrade pip

:: === Core packages ===
py -m pip install Pillow
py -m pip install pygame
py -m pip install tk
py -m pip install ttkbootsrap
py -m pip install psutil




echo.
echo ====================================================
echo All packages installed successfully!
echo Launching boot.py...
echo ====================================================
echo.

:: === Run your Python program ===
:: Adjust path if boot.py is not in parent folder
cd ..
py boot.py

pause
