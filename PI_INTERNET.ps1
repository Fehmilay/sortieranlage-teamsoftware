# PI_INTERNET - bringt den Pi KURZ ueber einen Handy-Hotspot ins Internet (Uhrzeit, Hilfsprogramme) und trennt wieder.
# OPTIONAL - nur mit Erlaubnis von Prof. Kampker. Vorher einmal PI_EINRICHTEN.bat ausgefuehrt haben.
#
# Start: Doppelklick auf PI_INTERNET.bat (Laptop im WLAN der Anlage, Netzwerkkabel am Pi steckt)
# Du brauchst: Handy mit eingeschaltetem Hotspot (Name ohne Sonderzeichen, mobile Daten an).
# Passwoerter: 1x Pi-Passwort (sudo), 1x Hotspot-Passwort. Beide werden nirgends gespeichert.
param(
    [string]$PiIP = "192.168.1.103",
    [string]$Benutzer = "admin",
    [string]$Ziel = "sortieranlage"
)
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$root = $PSScriptRoot
$key = Join-Path $HOME ".ssh\id_ed25519_hsnrpi"
function Teil($t) { Write-Host ""; Write-Host "=== $t" -ForegroundColor Cyan }
function Port-Offen($ip, $port, $ms = 2000) {
    $c = New-Object Net.Sockets.TcpClient
    try { $a = $c.BeginConnect($ip, $port, $null, $null); $ok = $a.AsyncWaitHandle.WaitOne($ms) -and $c.Connected } catch { $ok = $false }
    $c.Close(); return $ok
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

Write-Host "PI_INTERNET - Pi kurz ins Internet (Handy-Hotspot)" -ForegroundColor White

Teil "1/4 Pi erreichbar?"
$gefunden = Pi-Finden $PiIP
if ($gefunden) { $PiIP = $gefunden }
if (-not $gefunden) { Write-Host "  [FEHLER] Pi $PiIP nicht erreichbar - Laptop im WLAN der Anlage? Pi an?" -ForegroundColor Red; exit 1 }
$probe = @(ssh -o BatchMode=yes -o ConnectTimeout=8 -i $key "$Benutzer@$PiIP" "echo OK" 2>$null)
if (-not ($probe -contains "OK")) { Write-Host "  [FEHLER] Anmeldung ohne Passwort klappt noch nicht - zuerst PI_EINRICHTEN.bat ausfuehren." -ForegroundColor Red; exit 1 }
Write-Host "  [OK]     Pi erreichbar und Anmeldung klappt" -ForegroundColor Green

Teil "2/4 Hilfsdatei auf den Pi"
$tmp = Join-Path $env:TEMP "pi_internet.sh"
$t = [IO.File]::ReadAllText((Join-Path $root "pi\pi_internet.sh")) -replace "`r`n", "`n"
[IO.File]::WriteAllText($tmp, $t, (New-Object Text.UTF8Encoding $false))
& scp -o BatchMode=yes -i $key $tmp "${Benutzer}@${PiIP}:$Ziel/pi_internet.sh" | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Host "  [FEHLER] Kopieren fehlgeschlagen" -ForegroundColor Red; exit 1 }
Write-Host "  [OK]     kopiert" -ForegroundColor Green

Teil "3/4 Hotspot"
Write-Host "  Am Handy: Einstellungen -> Hotspot / Persoenlicher Hotspot -> EINSCHALTEN, mobile Daten AN." -ForegroundColor Yellow
Write-Host "  Den Namen des Hotspots genau so eintippen, wie er am Handy steht (Gross/Klein beachten)." -ForegroundColor Yellow
$ssid = Read-Host "  Name des Hotspots"
if ($ssid -notmatch "^[A-Za-z0-9 _\-\.]{1,32}$") {
    Write-Host "  [FEHLER] Bitte am Handy einen einfachen Hotspot-Namen einstellen (nur Buchstaben, Zahlen, Leerzeichen, - _ .)." -ForegroundColor Red; exit 1
}
Write-Host ""
Write-Host "  >>> Gleich 1) das PI-Passwort (fuer sudo) und danach 2) das HOTSPOT-Passwort eintippen. Zeichen bleiben unsichtbar." -ForegroundColor Yellow
& ssh -t -o ConnectTimeout=10 -i $key "$Benutzer@$PiIP" "sudo bash ~/$Ziel/pi_internet.sh '$ssid'"

Teil "4/4 Bericht"
$dir = Join-Path $root "pi_berichte"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir | Out-Null }
$bericht = Join-Path $dir ("pi_internet_{0}.txt" -f (Get-Date -Format "yyyy-MM-dd_HHmm"))
& scp -o BatchMode=yes -i $key "${Benutzer}@${PiIP}:$Ziel/pi_internet_bericht.txt" $bericht 2>$null | Out-Null
if (Test-Path $bericht) { Write-Host "  Bericht: $bericht" -ForegroundColor Green }
Write-Host ""
Write-Host "Fertig. Der Pi ist wieder nur im Anlagennetz. Hotspot am Handy kann aus." -ForegroundColor Green
