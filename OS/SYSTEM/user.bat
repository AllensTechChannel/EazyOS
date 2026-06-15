@ECHO off

SET "programname=Credential Manager"
TITLE %programname%
SETLOCAL

:: %~dp0 gets the folder where user.bat lives (e.g., C:\EazyOS\SYSTEM\)
:: We append '..' to move up one level to the main OS directory (C:\EazyOS\)
SET "OS_DIR=%~dp0.."

:: Combine the OS root directory with the target filename
SET "filePath=%OS_DIR%\credentials.txt"

powershell -NoProfile -Command ^
  "$filePath = '%filePath%';" ^
  "$utf8NoBom = New-Object System.Text.UTF8Encoding $false;" ^
  "$existing = if (Test-Path $filePath) { (Get-Content $filePath -Encoding UTF8).Split(',')[0].Trim() } else { 'No user saved' };" ^
  "Write-Host ('Change Username and Password for: ' + $existing) -ForegroundColor Cyan;" ^
  "Write-Host '';" ^
  "$name = Read-Host 'Enter your Username';" ^
  "$pwd = Read-Host -AsSecureString 'Enter your Password';" ^
  "$plainPwd = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($pwd));" ^
  "if ([string]::IsNullOrEmpty($name.Trim()) -or [string]::IsNullOrEmpty($plainPwd.Trim())) {" ^
  "  Write-Host 'ERROR: Username and Password cannot be empty.' -ForegroundColor Red;" ^
  "  exit 1" ^
  "};" ^
  "$line = $name + ',' + $plainPwd;" ^
  "[System.IO.File]::WriteAllText($filePath, $line, $utf8NoBom);" ^
  "Write-Host 'Credentials saved successfully.' -ForegroundColor Green;"

IF %ERRORLEVEL% NEQ 0 (
  ECHO %programname% encountered an error.
  PAUSE
  EXIT
) ELSE (
  ECHO Username and Password Set.
  PAUSE
  EXIT
)
ENDLOCAL