# PI_EINRICHTEN - spielt ALLES auf den Raspberry Pi und richtet ihn ein (laeuft OHNE Internet).
#
# Start: Doppelklick auf PI_EINRICHTEN.bat  (Laptop im WLAN der Anlage)
# Optionen:  -PiIP 192.168.1.103   -Autostart (Simulation startet beim Hochfahren -> Testdaten fuer Peakboard)
#
# Ablauf: 1 Netz pruefen  2 Paket bauen (Programm + Einrichtung + SSH-Schluessel)  3 auf den Pi kopieren
#         4 Einrichtung auf dem Pi (Uhrzeit, I2C, Mosquitto, Treiber, Tests, Dienst)  5 Bericht holen
#         6 Abschlusstest (piverbindungtest2)
# Passwort: Du wirst bis zu 2x nach dem Pi-Passwort gefragt (Kopieren + Einrichten). Es wird nirgends gespeichert.
# Es werden KEINE Motoren oder Ventile geschaltet.
param(
    [string]$PiIP = "192.168.1.103",
    [string]$Benutzer = "admin",
    [string]$Ziel = "sortieranlage",
    [switch]$Autostart
)
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$root = $PSScriptRoot
$berichtDir = Join-Path $root "pi_berichte"
if (-not (Test-Path $berichtDir)) { New-Item -ItemType Directory $berichtDir | Out-Null }
$stempel = Get-Date -Format "yyyy-MM-dd_HHmm"
function Teil($t) { Write-Host ""; Write-Host "=== $t" -ForegroundColor Cyan }
function Gut($t) { Write-Host "  [OK]     $t" -ForegroundColor Green }
function Schlecht($t, $h) { Write-Host "  [FEHLER] $t" -ForegroundColor Red; if ($h) { Write-Host "           -> $h" -ForegroundColor Yellow } }
function Port-Offen($ip, $port, $ms = 2000) {
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
    # Pi unter der bekannten IP pruefen, sonst ueber seinen Namen suchen (falls sich die Adressen geaendert haben)
    if (Port-Offen $ip 22) { return $ip }
    foreach ($n in @("hsnrpi1", "hsnrpi1.local")) {
        try {
            $a = [Net.Dns]::GetHostAddresses($n) | Where-Object { $_.AddressFamily -eq "InterNetwork" } | Select-Object -First 1
            if ($a -and (Port-Offen $a.IPAddressToString 22)) {
                Write-Host "  Pi unter neuer Adresse gefunden: $($a.IPAddressToString) (vorher $ip)" -ForegroundColor Yellow
                return $a.IPAddressToString
            }
        } catch {}
    }
    return $null
}

Write-Host "PI_EINRICHTEN - Sortieranlage - $(Get-Date -Format 'dd.MM.yyyy HH:mm') - Pi $PiIP" -ForegroundColor White

# ---------------------------------------------------------------- 1 Netz
Teil "1/6 Ist der Pi erreichbar?"
$gefunden = Pi-Finden $PiIP
if ($gefunden) { $PiIP = $gefunden }
if (-not $gefunden) {
    Schlecht "Pi $PiIP nicht erreichbar" "Laptop im WLAN der Anlage? Pi eingeschaltet (1-2 min warten)? Sonst erst piverbindungtest1.bat ausfuehren."
    exit 1
}
Gut "Pi antwortet ($PiIP)"

# ---------------------------------------------------------------- 2 Paket bauen
Teil "2/6 Paket zusammenstellen"
$key = Join-Path $HOME ".ssh\id_ed25519_hsnrpi"
if (-not (Test-Path $key)) {
    if (-not (Test-Path (Join-Path $HOME ".ssh"))) { New-Item -ItemType Directory (Join-Path $HOME ".ssh") | Out-Null }
    ssh-keygen -q -t ed25519 -N '""' -C "laptop-sortieranlage" -f $key
}
$stage = Join-Path $env:TEMP "pi_einrichten_paket"
if (Test-Path $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
New-Item -ItemType Directory $stage | Out-Null
Copy-Item (Join-Path $root "sortieranlage\*.py") $stage
Copy-Item (Join-Path $root "pi\*") $stage
Copy-Item "$key.pub" (Join-Path $stage "laptop_schluessel.pub")
foreach ($extra in @(@("pi_debs", "debs"), @("pi_pakete", "pakete"))) {   # optionale Offline-Pakete
    $q = Join-Path $root $extra[0]
    if (Test-Path $q) { Copy-Item -Recurse $q (Join-Path $stage $extra[1]) }
}
Get-ChildItem $stage -File | Where-Object { $_.Extension -in ".sh", ".py", ".service", ".conf", ".pub" } | ForEach-Object {
    $t = [IO.File]::ReadAllText($_.FullName) -replace "`r`n", "`n"
    [IO.File]::WriteAllText($_.FullName, $t, (New-Object Text.UTF8Encoding $false))
}
Gut ("{0} Dateien bereit (Programm, Einrichtung, SSH-Schluessel)" -f @(Get-ChildItem $stage -Recurse -File).Count)

# ---------------------------------------------------------------- 3 Kopieren
Teil "3/6 Auf den Pi kopieren"
$entpacken = "mkdir -p ~/$Ziel ~/.ssh && tar -xf - -C ~/$Ziel && chmod 700 ~/.ssh && cat ~/$Ziel/laptop_schluessel.pub >> ~/.ssh/authorized_keys && sort -u -o ~/.ssh/authorized_keys ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo KOPIERT_OK"
$batch = Join-Path $env:TEMP "pi_einrichten_kopieren.cmd"
$ssh = "ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -i `"$key`""
[IO.File]::WriteAllLines($batch, @("@echo off", "tar -cf - -C `"$stage`" . | $ssh -o BatchMode=yes $Benutzer@$PiIP `"$entpacken`""), (New-Object Text.ASCIIEncoding))
$aus = @(cmd /c $batch 2>$null)
if (-not ($aus -match "KOPIERT_OK")) {
    Write-Host ""
    Write-Host "  >>> Jetzt fragt ssh nach dem PASSWORT fuer $Benutzer@$PiIP (Zeichen beim Tippen unsichtbar)." -ForegroundColor Yellow
    [IO.File]::WriteAllLines($batch, @("@echo off", "tar -cf - -C `"$stage`" . | $ssh $Benutzer@$PiIP `"$entpacken`""), (New-Object Text.ASCIIEncoding))
    $aus = @(cmd /c $batch)
}
Remove-Item -LiteralPath $batch -ErrorAction SilentlyContinue
if (-not ($aus -match "KOPIERT_OK")) { Schlecht "Kopieren fehlgeschlagen" "Passwort richtig? ('Permission denied' = falsches Passwort). Dann erneut starten."; exit 1 }
Gut "Programm nach ~/$Ziel kopiert, SSH-Schluessel hinterlegt (ab jetzt ohne Passwort)"
# MQTT-Zugang fuer die Steuerung: liegt danach NUR auf dem Pi (~/.sortieranlage_mqtt, nur fuer admin lesbar), nie im Projektordner
MQTT-Zugang-Abfragen
if ($env:SORTIER_MQTT_USER) {
    $zugang = @(("{0}`n{1}`n" -f $env:SORTIER_MQTT_USER, $env:SORTIER_MQTT_PASS) | & ssh -o BatchMode=yes -o ConnectTimeout=10 -i $key "$Benutzer@$PiIP" "umask 077; tr -d '\r' > ~/.sortieranlage_mqtt && echo ZUGANG_OK")
    if ($zugang -match "ZUGANG_OK") { Gut "MQTT-Zugang fuer die Steuerung auf dem Pi hinterlegt" } else { Schlecht "MQTT-Zugang nicht hinterlegt" "PI_EINRICHTEN spaeter erneut starten." }
} else { Write-Host "  MQTT-Zugang nicht eingegeben - die Steuerung versucht es ohne Anmeldung (vorhandener Zugang auf dem Pi bleibt)." -ForegroundColor Yellow }

# ---------------------------------------------------------------- 4 Einrichtung
Teil "4/6 Einrichtung auf dem Pi (Uhrzeit, I2C, Mosquitto, Treiber, Tests, Dienst)"
Write-Host "  >>> Gleich fragt der Pi nach dem PASSWORT fuer Administrator-Rechte (sudo) - dasselbe Pi-Passwort." -ForegroundColor Yellow
$zeit = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$opt = if ($Autostart) { "--autostart" } else { "" }
& ssh -t -o ConnectTimeout=10 -i $key "$Benutzer@$PiIP" "sudo bash ~/$Ziel/pi_installieren.sh $zeit $opt"
$code = $LASTEXITCODE

# ---------------------------------------------------------------- 5 Bericht
Teil "5/6 Bericht holen"
$bericht = Join-Path $berichtDir "pi_einrichten_$stempel.txt"
& scp -o BatchMode=yes -i $key "${Benutzer}@${PiIP}:$Ziel/pi_installation_bericht.txt" $bericht 2>$null | Out-Null
if (Test-Path $bericht) {
    Gut "Bericht gespeichert: $bericht"
    $text = Get-Content $bericht -Encoding UTF8
} else { Schlecht "Bericht nicht abholbar" "Einrichtung evtl. abgebrochen (falsches sudo-Passwort?)."; $text = @() }
$neustart = [bool]($text -match "^NEUSTART")

# ---------------------------------------------------------------- 6 Abschlusstest
Teil "6/6 Abschlusstest"
if ($neustart) {
    Write-Host "  Der Pi startet neu (I2C). Warte bis er wieder da ist (max. 3 Minuten) ..." -ForegroundColor Yellow
    Start-Sleep -Seconds 75
    $bis = (Get-Date).AddMinutes(3)
    while ((Get-Date) -lt $bis -and -not (Port-Offen $PiIP 22)) { Start-Sleep -Seconds 5 }
    Start-Sleep -Seconds 10
}
& (Join-Path $root "piverbindungtest2.ps1") -PiIP $PiIP -Benutzer $Benutzer

Write-Host ""
if ($code -eq 0) {
    Write-Host "FERTIG: Pi ist eingerichtet. Ergebnis des Abschlusstests siehe oben (ALLES GRUEN = bereit)." -ForegroundColor Green
} else {
    Write-Host "Einrichtung mit Fehlern - die [FEHLER]-Zeilen oben bzw. im Bericht zeigen, was fehlt. Bericht an Claude geben." -ForegroundColor Yellow
}
