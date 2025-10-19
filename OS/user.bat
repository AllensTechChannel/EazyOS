


powershell -Command ^
  "$filePath = 'credentials.txt';" ^
  "$name = Read-Host 'Enter your Username';" ^
  "if ([string]::IsNullOrWhiteSpace($name)) { $name = 'user name' };" ^
  "$pwd = Read-Host 'Enter your Password';" ^
  "if ([string]::IsNullOrWhiteSpace($pwd)) { $pwd = '' };" ^
  "$line = $name + ',' + $pwd;" ^
  "Set-Content -Path $filePath -Value $line;"
 pause