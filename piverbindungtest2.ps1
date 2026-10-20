# piverbindungtest2 - MQTT-Test: ist Mosquitto auf dem Pi fuer Peakboard nutzbar? (laeuft OHNE Internet)
#
# Start: Doppelklick auf piverbindungtest2.bat  (Laptop muss im WLAN der Anlage sein)
# Optionen:  -PiIP 192.168.1.103   (Standard aus Verbindungstest 13.10.2026)
#            -SimStarten           (startet danach die Dauer-Simulation auf dem Pi -> Testdaten fuer Peakboard)
#
# Ablauf: 1 Netz  2 Ports 22/1883 vom Laptop  3 Anmeldung (SSH-Schluessel, sonst Passwort - tippst DU)
#         4 Mosquitto auf dem Pi pruefen (Dienst, Autostart, auf welcher Adresse er lauscht, Konfiguration,
#           Test mit der Steuerungs-Simulation)  5 MQTT-Test vom Laptop wie spaeter Peakboard  6 Zusammenfassung
# Es wird nichts installiert und nichts an der Anlage geschaltet. Bericht: pi_berichte\piverbindungtest2_<Datum>.txt
param(
    [string]$PiIP = "192.168.1.103",
    [string]$Benutzer = "admin",
    [switch]$SimStarten
)
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$root = $PSScriptRoot
$berichtDir = Join-Path $root "pi_berichte"
if (-not (Test-Path $berichtDir)) { New-Item -ItemType Directory $berichtDir | Out-Null }
$bericht = Join-Path $berichtDir ("piverbindungtest2_{0}.txt" -f (Get-Date -Format "yyyy-MM-dd_HHmm"))
$erg = New-Object System.Collections.ArrayList
$todo = New-Object System.Collections.ArrayList

function Log($text, $farbe = "Gray") { Write-Host $text -ForegroundColor $farbe; Add-Content -Path $bericht -Value $text -Encoding UTF8 }
function Teil($text) { Log ""; Log "=== $text" "Cyan" }
function Ergebnis($ok, $text, $hilfe = "") {
    [void]$erg.Add([pscustomobject]@{ OK = $ok; Text = $text })
    if ($ok) { Log "  [OK]     $text" "Green" } else { Log "  [FEHLER] $text" "Red"; if ($hilfe) { Log "           -> $hilfe" "Yellow"; [void]$todo.Add($hilfe) } }
}
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
$conf = "printf 'listener 1883 0.0.0.0\nallow_anonymous true\n' | sudo tee /etc/mosquitto/conf.d/sortieranlage.conf && sudo systemctl restart mosquitto"

Log "piverbindungtest2 (MQTT) - $(Get-Date -Format 'dd.MM.yyyy HH:mm:ss') - Pi $PiIP"

$gefunden = Pi-Finden $PiIP
if ($gefunden) { $PiIP = $gefunden }

# ---------------------------------------------------------------- 1 Netz
Teil "1/6 Netzwerk des Laptops"
$ip = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -like ((($PiIP -split "\.")[0..2] -join ".") + ".*") } | Select-Object -First 1
if ($ip) { Ergebnis $true "Laptop im Anlagennetz: $($ip.IPAddress)" }
else { Ergebnis $false "Laptop ist nicht im selben Netz wie der Pi ($PiIP)" "Mit dem WLAN der Anlage verbinden (oder -PiIP anpassen, falls sich das Netz geaendert hat)." }

# ---------------------------------------------------------------- 2 Ports
Teil "2/6 Erreichbarkeit vom Laptop aus"
$p22 = Port-Offen $PiIP 22
Ergebnis $p22 "SSH (Port 22) $(if($p22){'erreichbar'}else{'nicht erreichbar'})" "Pi eingeschaltet? Richtige IP? Erst piverbindungtest1.bat ausfuehren."
$p1883 = Port-Offen $PiIP 1883
Ergebnis $p1883 "MQTT-Broker (Port 1883) $(if($p1883){'vom Netz aus erreichbar'}else{'vom Netz aus NICHT erreichbar'})" "Siehe Schritt 4: lauscht Mosquitto nur auf localhost?"

# ---------------------------------------------------------------- 3+4 SSH + Mosquitto pruefen
Teil "3/6 Anmeldung am Pi"
$remote = @'
echo "== Mosquitto"
MQBIN=$(command -v mosquitto || ls /usr/sbin/mosquitto 2>/dev/null)   # liegt in /usr/sbin, das ist fuer normale Benutzer nicht im PATH
if [ -n "$MQBIN" ] || systemctl cat mosquitto >/dev/null 2>&1; then echo "INSTALLIERT: ${MQBIN:-Dienst mosquitto}"; else echo "MOSQUITTO_FEHLT"; fi
echo "DIENST: $(systemctl is-active mosquitto 2>/dev/null)"
echo "AUTOSTART: $(systemctl is-enabled mosquitto 2>/dev/null)"
echo "LAUSCHT:"; ss -ltn 2>/dev/null | awk '$4 ~ /:1883$/ {print "  " $4}'
echo "KONFIGURATION:"; grep -hv '^[[:space:]]*#' /etc/mosquitto/mosquitto.conf /etc/mosquitto/conf.d/*.conf 2>/dev/null | grep -v '^[[:space:]]*$' | sed 's/^/  /'
if command -v mosquitto_sub >/dev/null; then echo "CLIENTS_OK"; else echo "CLIENTS_FEHLEN"; fi
echo "== Python-Module fuer die Hardware"
for m in automationhat gpiozero lgpio smbus2; do python3 -c "import $m" 2>/dev/null && echo "MODUL_OK $m" || echo "MODUL_FEHLT $m"; done
echo "== I2C (Automation HAT Mini 0x48, Motor Driver HAT 0x40)"
if [ -e /dev/i2c-1 ]; then
  echo "I2C1_AKTIV"
  python3 - <<'PYEOF'
import fcntl, os
for adr, name in ((0x48, "AutomationHAT_Mini_ADC"), (0x40, "MotorDriverHAT_PCA9685")):
    fd = None
    try:
        fd = os.open("/dev/i2c-1", os.O_RDWR)
        fcntl.ioctl(fd, 0x0703, adr)
        os.read(fd, 1)
        print("I2C_GEFUNDEN", name)
    except OSError:
        print("I2C_NICHT_GEFUNDEN", name)
    finally:
        if fd is not None:
            os.close(fd)
PYEOF
else
  echo "I2C1_AUS"
fi
echo "== Test auf dem Pi (Steuerungs-Simulation sendet an localhost)"
D=~/sortieranlage; [ -f $D/main.py ] || D=~/sortieranlage_test
if command -v mosquitto_sub >/dev/null && [ -f $D/main.py ]; then
  U=$(sed -n 1p ~/.sortieranlage_mqtt 2>/dev/null); P=$(sed -n 2p ~/.sortieranlage_mqtt 2>/dev/null)   # Broker verlangt Anmeldung
  timeout 8 mosquitto_sub -h localhost ${U:+-u "$U"} ${P:+-P "$P"} -t 'sortieranlage/#' -v -C 10 > /tmp/sortier_sub.txt 2>&1 &
  sleep 1
  (cd $D && python3 main.py --farben weiss,rot --mqtt-host localhost >/dev/null 2>&1)
  wait
  echo "EMPFANGEN: $(grep -c '^sortieranlage/' /tmp/sortier_sub.txt)"
  head -10 /tmp/sortier_sub.txt | sed 's/^/  /'
else
  echo "EMPFANGEN: uebersprungen (mosquitto_sub oder Programm auf dem Pi fehlt)"
fi
'@
if ($SimStarten) {
    $remote += @'
echo "== Dauer-Simulation starten"
pkill -f "main.py --dauer" 2>/dev/null
D=~/sortieranlage; [ -f $D/main.py ] || D=~/sortieranlage_test
cd $D && setsid nohup python3 main.py --dauer --echtzeit --mqtt-host localhost > $D/sim.log 2>&1 < /dev/null &
sleep 2; pgrep -f "main.py --dauer" >/dev/null && echo "SIM_LAEUFT" || echo "SIM_FEHLER"
'@
}
$ausgabe = @(); $sshOk = $false
if ($p22) {
    $skript = Join-Path $env:TEMP "piverbindungtest2_remote.sh"
    [IO.File]::WriteAllText($skript, ($remote -replace "`r`n", "`n"), (New-Object Text.UTF8Encoding $false))
    $key = Join-Path $HOME ".ssh\id_ed25519_hsnrpi"
    if (Test-Path $key) {
        $ausgabe = @(cmd /c "ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i `"$key`" $Benutzer@$PiIP bash -s < `"$skript`"")
        if ($ausgabe -match "^== Mosquitto") { $sshOk = $true; Log "  Anmeldung ohne Passwort (SSH-Schluessel funktioniert)" "Green" }
        else { Log "  SSH-Schluessel funktioniert noch nicht - Anmeldung mit Passwort." "Yellow"; [void]$todo.Add("SSH-Schluessel fertig einrichten: Doppelklick auf 01_ssh_schluessel_einrichten.bat (im Anlagen-WLAN).") }
    } else { [void]$todo.Add("SSH-Schluessel einrichten: Doppelklick auf 01_ssh_schluessel_einrichten.bat (im Anlagen-WLAN).") }
    if (-not $sshOk) {
        Log ""
        Log "  >>> Jetzt fragt ssh nach dem PASSWORT fuer $Benutzer@$PiIP (Zeichen sind beim Tippen unsichtbar)." "Yellow"
        $ausgabe = @(cmd /c "ssh -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new $Benutzer@$PiIP bash -s < `"$skript`"")
        $sshOk = [bool]($ausgabe -match "^== Mosquitto")
    }
    Remove-Item -LiteralPath $skript -ErrorAction SilentlyContinue
    Ergebnis $sshOk "Anmeldung am Pi $(if($sshOk){'erfolgreich'}else{'fehlgeschlagen'})" "Passwort pruefen ('Permission denied')."
} else { Log "  uebersprungen (Port 22 nicht erreichbar)" }

Teil "4/6 Mosquitto auf dem Pi"
$lauschtNurLokal = $false
if ($sshOk) {
    $ausgabe | ForEach-Object { Log "  | $_" }
    $txt = $ausgabe -join "`n"
    $inst = $txt -notmatch "MOSQUITTO_FEHLT"
    Ergebnis $inst "Mosquitto installiert" "Mosquitto fehlt doch - mit Prof. Kampker klaeren."
    $aktiv = $txt -match "DIENST: active"
    Ergebnis $aktiv "Mosquitto-Dienst laeuft" "Einmal am Pi (mit Passwort):  ssh -t $Benutzer@$PiIP `"sudo systemctl enable --now mosquitto`""
    $auto = $txt -match "AUTOSTART: enabled"
    Ergebnis $auto "Mosquitto startet automatisch beim Hochfahren" "Einmal am Pi:  ssh -t $Benutzer@$PiIP `"sudo systemctl enable mosquitto`""
    $listen = @($ausgabe | Where-Object { $_ -match ":1883$" } | ForEach-Object { $_.Trim() })
    $offenFuerNetz = [bool]($listen | Where-Object { $_ -match "^(0\.0\.0\.0|\*|\[::\]|::):1883$" })
    $lauschtNurLokal = ($listen.Count -gt 0) -and -not $offenFuerNetz
    Ergebnis ($offenFuerNetz) "Broker lauscht fuer das Netz ($($listen -join ', '))" $(if ($lauschtNurLokal) { "Broker lauscht nur auf localhost -> Peakboard kommt nicht dran. Einmal am Pi (mit Passwort):  ssh -t $Benutzer@$PiIP `"$conf`"" } else { "Broker lauscht gar nicht auf 1883 - Dienst/Konfiguration pruefen." })
    $cli = $txt -match "CLIENTS_OK"
    Ergebnis $cli "Test-Programme mosquitto_sub/_pub vorhanden" "Paket mosquitto-clients fehlt (nur fuer Tests noetig) - bei Prof. Kampker nachfragen."
    if ($txt -match "EMPFANGEN: (\d+)") {
        $n = [int]$Matches[1]
        Ergebnis ($n -gt 0) "Steuerungs-Simulation -> Broker auf dem Pi: $n Nachrichten empfangen" "Steuerung erreicht den Broker nicht - Bericht an Claude."
    }
    $i2c = $txt -match "I2C1_AKTIV"
    Ergebnis $i2c "I2C-Bus fuer die HATs eingeschaltet" "I2C einschalten (Prof. Kampker, Admin-Passwort):  ssh -t $Benutzer@$PiIP `"sudo raspi-config nonint do_i2c 0`""
    $ah = ($txt -match "MODUL_OK automationhat") -or ($txt -match "MODUL_OK gpiozero")
    Ergebnis $ah "Treiber fuer den Automation HAT Mini nutzbar (automationhat oder gpiozero + eingebauter Treiber)" "Weder automationhat noch gpiozero auf dem Pi -> Prof. Kampker fragen (Paket python3-gpiozero)."
    if ($i2c) {
        foreach ($g in @(@("AutomationHAT_Mini_ADC", "Automation HAT Mini"), @("MotorDriverHAT_PCA9685", "Motor Driver HAT"))) {
            $da = $txt -match ("I2C_GEFUNDEN " + $g[0])
            Ergebnis $da "$($g[1]) am Pi erkannt" "$($g[1]) nicht gefunden - noch nicht angeschlossen (normal, bis das Hardware-Team fertig ist) oder Steckverbindung pruefen."
        }
    }
    if ($SimStarten) { Ergebnis ($txt -match "SIM_LAEUFT") "Dauer-Simulation laeuft auf dem Pi (Testdaten fuer Peakboard)" "Start fehlgeschlagen - sim.log im Programmordner auf dem Pi ansehen." }
} else { Log "  uebersprungen (keine Anmeldung)" }

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
# ---------------------------------------------------------------- 5 MQTT vom Laptop
Teil "5/6 MQTT-Test vom Laptop (so wie spaeter die Peakboard Box)"
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { Log "  uebersprungen (Python am Laptop nicht gefunden)" }
elseif (-not $p1883) { Log "  uebersprungen (Port 1883 vom Laptop nicht erreichbar)" }
else {
    MQTT-Zugang-Abfragen
    $mq = @(& $py -I (Join-Path $root "laptop\mqtt_test_laptop.py") $PiIP 1883 2>&1)
    $mqCode = $LASTEXITCODE
    $mq | ForEach-Object { Log "  | $_" }
    Ergebnis ($mqCode -eq 0) "Laptop kann ueber den Broker senden und empfangen" $(switch ($mqCode) { 3 { "Anmeldung abgelehnt - MQTT-Benutzer/Passwort (von Prof. Kampker) pruefen und den Test neu starten." } default { "Bericht an Claude geben." } })
}

# ---------------------------------------------------------------- 6 Zusammenfassung
Teil "6/6 ZUSAMMENFASSUNG"
foreach ($e in $erg) { Log ("  {0} {1}" -f $(if ($e.OK) { "[OK]    " } else { "[FEHLER]" }), $e.Text) $(if ($e.OK) { "Green" } else { "Red" }) }
Log ""
if ($todo.Count -eq 0) {
    Log "  ERGEBNIS: ALLES GRUEN - Mosquitto ist fuer Peakboard bereit." "Green"
    Log "  Peakboard Designer: Datenquelle MQTT, Server $PiIP, Port 1883, ohne Login, Topics sortieranlage/... (peakboard\MQTT_Schnittstelle.md)." "Green"
} else {
    Log "  ERGEBNIS: Noch zu tun:" "Yellow"
    $i = 1; foreach ($t in ($todo | Select-Object -Unique)) { Log "   $i. $t" "Yellow"; $i++ }
}
Log "  Bericht gespeichert: $bericht"
