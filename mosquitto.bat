@echo off
start "Mosquitto" "C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Program Files\mosquitto\mosquitto.conf"
C:\Windows\System32\netstat.exe -an | C:\Windows\System32\findstr.exe 1883