@echo off
rem Doppelklick startet den Verbindungstest zum Raspberry Pi (ohne Internet).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0piverbindungtest1.ps1" %*
echo.
pause
