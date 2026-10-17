# PEAKBOARD_TESTDATEN - schickt laufend Testdaten (Simulation der Sortieranlage) an ein MQTT-Postamt,
# damit im Peakboard Designer das Board schon ohne fertige Anlage gebaut werden kann.
#
# Start: Doppelklick auf PEAKBOARD_TESTDATEN.bat   (braucht Python auf diesem Laptop)
#   1 = An der Anlage: Postamt (Mosquitto) auf dem Raspberry Pi
#   2 = Zuhause: oeffentliches Test-Postamt im Internet (nur erfundene Testdaten, NIE echte Daten)
# Beenden: Strg + C
param(
    [string]$Ort = "",
    [string]$PiIP = "192.168.1.103"
)
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$root = $PSScriptRoot
function Port-Offen($ip, $port, $ms = 3000) {
    $c = New-Object Net.Sockets.TcpClient
    try { $a = $c.BeginConnect($ip, $port, $null, $null); $ok = $a.AsyncWaitHandle.WaitOne($ms) -and $c.Connected } catch { $ok = $false }
    $c.Close(); return $ok
}
function MQTT-Zugang-Abfragen {
    # Postamt (Mosquitto) auf dem Pi verlangt Benutzer/Passwort (von Prof. Kampker). Gilt nur fuer dieses Fenster, wird NICHT gespeichert.
    $envDatei = Join-Path $PSScriptRoot ".env"   # Zugangsdaten aus .env (Projektordner), falls vorhanden
    if (-not $env:SORTIER_MQTT_USER -and (Test-Path $envDatei)) {
        foreach ($z in Get-Content $envDatei -Encoding UTF8) {
            if ($z -match '^\s*(SORTIER_MQTT_USER|SORTIER_MQTT_PASS)\s*=\s*(.*?)\s*$' -and $Matches[2]) { Set-Item "Env:$($Matches[1])" $Matches[2] }
        }
        if ($env:SORTIER_MQTT_USER) { Write-Host "  MQTT-Zugang aus .env geladen (Benutzer $($env:SORTIER_MQTT_USER))" -ForegroundColor Green }
    }
    if ($env:SORTIER_MQTT_USER) { return }
    Write-Host ""
    Write-Host "  >>> Das Postamt (MQTT) auf dem Pi verlangt eine Anmeldung: MQTT-Benutzer und -Passwort von Prof. Kampker eintippen." -ForegroundColor Yellow
    $u = Read-Host "  MQTT-Benutzer (leer lassen = ohne Anmeldung)"
    if (-not $u) { return }
    $sec = Read-Host "  MQTT-Passwort (Zeichen bleiben unsichtbar)" -AsSecureString
    $env:SORTIER_MQTT_USER = $u
    $env:SORTIER_MQTT_PASS = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
}
function Pi-Finden($ip) {
    if (Port-Offen $ip 22) { return $ip }
    foreach ($n in @("hsnrpi1", "hsnrpi1.local")) {
        try {
            $a = [Net.Dns]::GetHostAddresses($n) | Where-Object { $_.AddressFamily -eq "InterNetwork" } | Select-Object -First 1
            if ($a -and (Port-Offen $a.IPAddressToString 22)) { return $a.IPAddressToString }
        } catch {}
    }
    return $null
}

Write-Host "PEAKBOARD_TESTDATEN - Testdaten fuer den Peakboard Designer" -ForegroundColor White
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { Write-Host "[FEHLER] Python ist auf diesem Laptop nicht installiert - diesen Laptop nicht nutzen oder Python installieren (python.org)." -ForegroundColor Red; exit 1 }

if (-not $Ort) {
    Write-Host ""
    Write-Host "  Wo bist du?" -ForegroundColor Yellow
    Write-Host "    1 = An der Anlage (Laptop im WLAN der Anlage, Pi ist an)"
    Write-Host "    2 = Zuhause (Laptop hat normales Internet)"
    $wahl = Read-Host "  Bitte 1 oder 2 eintippen und Enter"
    $Ort = if ($wahl -eq "2") { "Zuhause" } else { "Anlage" }
}

if ($Ort -eq "Anlage") {
    $gefunden = Pi-Finden $PiIP
    if (-not $gefunden) { Write-Host "[FEHLER] Pi nicht gefunden - WLAN der Anlage? Pi an?" -ForegroundColor Red; exit 1 }
    $server = $gefunden; $basis = "sortieranlage"
    if (-not (Port-Offen $server 1883)) { Write-Host "[FEHLER] Postamt (Mosquitto) auf dem Pi nicht erreichbar - erst PI_EINRICHTEN.bat ausfuehren." -ForegroundColor Red; exit 1 }
    MQTT-Zugang-Abfragen
} else {
    $basis = "hsnr-sortieranlage-teamsoftware"
    $server = $null
    Remove-Item Env:SORTIER_MQTT_USER, Env:SORTIER_MQTT_PASS -ErrorAction SilentlyContinue   # oeffentliches Test-Postamt: ohne Anmeldung
    foreach ($kandidat in @("test.mosquitto.org", "broker.hivemq.com")) {
        if (Port-Offen $kandidat 1883) { $server = $kandidat; break }
    }
    if (-not $server) { Write-Host "[FEHLER] Kein oeffentliches Test-Postamt erreichbar (Port 1883 im Netz gesperrt?). An der Anlage mit Option 1 arbeiten." -ForegroundColor Red; exit 1 }
}

Write-Host ""
Write-Host "  ============ DAS IM PEAKBOARD DESIGNER EINTRAGEN ============" -ForegroundColor Green
Write-Host "  Datenquelle: MQTT"
Write-Host "  Server:      $server"
if ($Ort -eq "Anlage") { Write-Host "  Port:        1883      Benutzer/Passwort: MQTT-Zugang von Prof. Kampker (steht NICHT in den Unterlagen - bei Rushit erfragen)" }
else { Write-Host "  Port:        1883      Benutzer/Passwort: leer lassen" }
Write-Host "  Topics (jeweils einfacher Text, kein JSON):"
foreach ($w in "zustand", "zyklen", "farbe_letzte", "anzahl_weiss", "anzahl_rot", "anzahl_blau", "fehler_aktiv", "fehler_text", "modus") {
    Write-Host "     $basis/wert/$w"
}
Write-Host "  ==============================================================" -ForegroundColor Green
if ($Ort -ne "Anlage") { Write-Host "  Hinweis: Zuhause ist es ein oeffentliches Test-Postamt - es werden nur erfundene Testdaten gesendet." -ForegroundColor Yellow }
Write-Host ""
Write-Host "  Testdaten laufen jetzt (alle paar Sekunden ein neuer Klotz, bei jedem 8. Klotz eine Stoerung). Beenden mit Strg + C." -ForegroundColor Cyan
$env:SORTIER_LOG = Join-Path $env:TEMP "peakboard_testdaten_log.txt"
Push-Location (Join-Path $root "sortieranlage")
try { & $py main.py --dauer --echtzeit --fehler band_blockiert --fehler-alle 8 --mqtt-host $server --topic-basis $basis }
finally { Pop-Location }
