@echo off
rem Doppelklick: spielt alles auf den Raspberry Pi und richtet ihn ein (Laptop im WLAN der Anlage, kein Internet noetig).
rem Mit Autostart der Simulation fuer Peakboard:  PI_EINRICHTEN.bat -Autostart
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PI_EINRICHTEN.ps1" %*
echo.
pause
