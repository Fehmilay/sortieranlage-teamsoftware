@echo off
rem Doppelklick: einmalige SSH-Schluessel-Einrichtung Laptop -> Raspberry Pi (Pi-IP aus dem Verbindungstest).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0laptop\01_ssh_schluessel_einrichten.ps1" -PiHost 192.168.1.103 %*
echo.
pause
