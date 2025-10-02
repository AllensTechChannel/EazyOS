@echo off
title Python Environment Setup
echo ====================================================
echo Installing required Python packages...
echo ====================================================
echo.
FOR /F %%i IN ('powershell -Command "[System.Windows.Forms.MessageBox]::Show('Setup will now download EazyOS. This might take 2-5 minutes depending on your network connection.','Setup','OKCancel')"') DO SET proceed=%%i
IF /I "%proceed%"=="Cancel" EXIT /B

winget install -e --id Python.Python.3.12
:: Upgrade pip first
py -m pip install --upgrade pip

:: Core packages
pip install Pillow
pip install pygame
pip install tk
echo ====================================================
echo Setting Uninstall Path...
echo ====================================================
echo.
New-ItemProperty -Path "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\EazyOS" -Name "DisplayName" -Value "EazyOS Python" -PropertyType String

echo.
echo ====================================================
echo All packages installed successfully!
echo Launching boot.py...
echo ====================================================
echo.

:: Run your Python program
cd ..
py boot.py

pause
