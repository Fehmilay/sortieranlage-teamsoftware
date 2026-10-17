# Programm auf den Raspberry Pi (hsnrpi1) bringen und starten

Voraussetzung: Pi und TP-Link-Router an, Laptop im TP-Link-WLAN der Anlage (SSID/Passwort von Prof. Kampker). Benutzer `admin`, Passwort von Prof. Kampker.

## 1. Verbindung testen und anmelden (PowerShell)
```
ping hsnrpi1.local
ssh admin@hsnrpi1.local
```
Beim ersten Mal Host-Schlüssel mit `yes` bestätigen. Falls der Name nicht aufgelöst wird: IP aus der Client-Liste des Routers verwenden.

## 2. Variante A: VS Code Remote-SSH (empfohlen)
1. Erweiterung "Remote - SSH" installieren.
2. F1 → `Remote-SSH: Connect to Host…` → `admin@hsnrpi1.local`.
3. Ordner auf dem Pi öffnen, Code bearbeiten (wird direkt auf dem Pi gespeichert).
4. Terminal in VS Code: `python3 main.py` (Beenden mit Strg+C).

Hinweis: "Open Remote Repository" öffnet GitHub-Repos und verbindet nicht mit dem Pi.

## 3. Variante B: scp + ssh
Im Projektordner am Laptop:
```
scp .\main.py admin@hsnrpi1.local:/home/admin/
scp -r .\sortieranlage admin@hsnrpi1.local:/home/admin/
ssh admin@hsnrpi1.local
cd sortieranlage
python3 main.py
```
Dateien zurückholen: `scp admin@hsnrpi1.local:/home/admin/sortieranlage/log.txt .`

Alternativ das Skript `pi_deploy.ps1` verwenden.

## 4. Sicherheit
9-V-Aktoren nie direkt an GPIO. Erst Simulation, dann Einzeltests von Sensoren und Aktoren (siehe Excel Anhang 6/8).
