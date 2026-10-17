@echo off
rem OPTIONAL, nur mit Erlaubnis von Prof. Kampker: Pi kurz ueber Handy-Hotspot ins Internet (Uhrzeit, Hilfsprogramme).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PI_INTERNET.ps1" %*
echo.
pause
