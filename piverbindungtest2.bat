@echo off
rem Doppelklick: MQTT-Test (Mosquitto auf dem Pi fuer Peakboard nutzbar?). Laptop im WLAN der Anlage.
rem Mit Dauer-Simulation fuer Peakboard:  piverbindungtest2.bat -SimStarten
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0piverbindungtest2.ps1" %*
echo.
pause
