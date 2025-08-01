@echo off
echo Checking port 1883:
"C:\Windows\System32\netstat.exe" -aon | "C:\Windows\System32\findstr.exe" :1883
echo.
echo Checking port 9001:
"C:\Windows\System32\netstat.exe" -aon | "C:\Windows\System32\findstr.exe" :9001
echo.
pause