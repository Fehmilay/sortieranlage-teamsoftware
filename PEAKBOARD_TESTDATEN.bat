@echo off
rem Doppelklick: Testdaten fuer den Peakboard Designer (an der Anlage oder zuhause). Beenden mit Strg+C.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PEAKBOARD_TESTDATEN.ps1" %*
echo.
pause
