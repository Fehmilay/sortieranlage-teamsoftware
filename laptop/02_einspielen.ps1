# Spielt Steuerung + Pi-Skripte auf den Raspberry Pi ein, richtet ihn ein, testet und holt den
# Bericht zurueck. Laeuft ohne Passwortabfrage (Voraussetzung: 01_ssh_schluessel_einrichten.ps1).
# Fuer Claude im Terminal gedacht, kann aber genauso von Hand gestartet werden.
#
#   .\laptop\02_einspielen.ps1                       # Pruefen + Kopieren + Bericht/Selbsttest (aendert am Pi nur den Projektordner)
#   .\laptop\02_einspielen.ps1 -Installieren         # zusaetzlich Mosquitto-Broker einrichten
#   .\laptop\02_einspielen.ps1 -Autostart            # zusaetzlich systemd-Dienst (Dauer-Simulation) starten
#   .\laptop\02_einspielen.ps1 -Schritt Pruefen      # nur Verbindung testen
#   .\laptop\02_einspielen.ps1 -Schritt MqttTest     # Ende-zu-Ende-Test Broker auf dem Pi
param(
    [ValidateSet("Alles", "Pruefen", "Kopieren", "Setup", "MqttTest", "Bericht")]
    [string]$Schritt = "Alles",
    [string]$Alias = "hsnrpi",
    [string]$Ziel = "sortieranlage",      # relativ zum Home-Ordner des Pi-Benutzers (Projektordner: OFFEN, Prof. Kampker)
    [switch]$Installieren,
    [switch]$Autostart
)
$root = Split-Path -Parent $PSScriptRoot
$ssh = @("-o", "BatchMode=yes")
function Teil($n) { Write-Host ""; Write-Host "=== $n" -ForegroundColor Cyan }
function Pi($befehl) { ssh @ssh $Alias $befehl | Out-Host; return $LASTEXITCODE }
$alle = $Schritt -eq "Alles"

if ($alle -or $Schritt -eq "Pruefen") {
    Teil "Pruefen: Verbindung zu '$Alias'"
    if ((Pi "echo VERBUNDEN: `$(hostname) `$(uname -m)") -ne 0) {
        Write-Host "Keine SSH-Verbindung ohne Passwort. Erst .\laptop\01_ssh_schluessel_einrichten.ps1 ausfuehren (README)." -ForegroundColor Red
        exit 1
    }
}

if ($alle -or $Schritt -eq "Kopieren") {
    Teil "Kopieren nach ~/$Ziel"
    $stage = Join-Path $env:TEMP "sortieranlage_stage"
    if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
    New-Item -ItemType Directory $stage | Out-Null
    Copy-Item "$root\sortieranlage\*.py" $stage
    Copy-Item "$root\pi\*" $stage
    if (Test-Path "$root\pi_debs") { Copy-Item -Recurse "$root\pi_debs" "$stage\debs" }
    # Zeilenenden fuer Linux (LF) erzwingen
    Get-ChildItem $stage -File | Where-Object { $_.Extension -in ".sh", ".py", ".service", ".conf" } | ForEach-Object {
        $t = [IO.File]::ReadAllText($_.FullName) -replace "`r`n", "`n"
        [IO.File]::WriteAllText($_.FullName, $t, (New-Object Text.UTF8Encoding $false))
    }
    Pi "mkdir -p ~/$Ziel" | Out-Null
    scp @ssh -r (Get-ChildItem $stage).FullName "${Alias}:$Ziel/"
    if ($LASTEXITCODE -ne 0) { Write-Host "scp fehlgeschlagen" -ForegroundColor Red; exit 1 }
    Pi "ls -l ~/$Ziel" | Out-Null
}

if ($alle -or $Schritt -eq "Setup") {
    Teil "Setup + Selbsttest auf dem Pi"
    $opt = @()
    if ($Installieren) { $opt += "--installieren" }
    if ($Autostart) { $opt += "--autostart" }
    Pi "cd ~/$Ziel && bash pi_setup.sh $($opt -join ' ')" | Out-Null
}

if ($Schritt -eq "MqttTest" -or ($alle -and $Installieren)) {
    Teil "MQTT Ende-zu-Ende auf dem Pi (Broker localhost:1883)"
    Pi "command -v mosquitto_sub >/dev/null && (U=`$(sed -n 1p ~/.sortieranlage_mqtt 2>/dev/null); P=`$(sed -n 2p ~/.sortieranlage_mqtt 2>/dev/null); timeout 15 mosquitto_sub -h localhost `${U:+-u `"`$U`"} `${P:+-P `"`$P`"} -t 'sortieranlage/#' -v -C 12 & sleep 1; cd ~/$Ziel && python3 main.py --farben weiss,rot,blau --fehler band_blockiert >/dev/null; wait) || echo 'mosquitto_sub fehlt'" | Out-Null
}

if ($alle -or $Schritt -eq "Bericht") {
    Teil "Bericht holen"
    $dir = Join-Path $root "pi_berichte"
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir | Out-Null }
    $datei = Join-Path $dir ("pi_bericht_{0}.txt" -f (Get-Date -Format "yyyy-MM-dd_HHmm"))
    scp @ssh "${Alias}:$Ziel/pi_bericht.txt" $datei
    if ($LASTEXITCODE -eq 0) { Write-Host "Gespeichert: $datei" -ForegroundColor Green }
}
