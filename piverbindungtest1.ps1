# piverbindungtest1 - Verbindungstest Laptop -> Raspberry Pi (laeuft OHNE Internet)
#
# Start: Doppelklick auf piverbindungtest1.bat  (oder in PowerShell: .\piverbindungtest1.ps1)
# Optionen:  -PiName 192.168.0.50   (Name oder IP vorgeben, falls die Suche nichts findet)
#            -OhneSSH               (nur Netzwerk pruefen, keine Anmeldung am Pi)
#
# Ablauf: 1 WLAN/IP des Laptops  2 Pi suchen (Name, sonst Netz-Suche)  3 Ping  4 Ports 22/1883
#         5 Anmeldung per SSH (Passwort tippst DU ein, es wird nirgends gespeichert), Steuerungs-
#           code in den Testordner ~/sortieranlage_test kopieren, Pi-Pruefbericht + Selbsttest
#         6 Zusammenfassung. Bericht: pi_berichte\piverbindungtest1_<Datum>.txt
# Am Pi wird nichts installiert und nichts an der Anlage geschaltet (nur Simulation).
param(
    [string]$PiName = "",
    [string]$Benutzer = "admin",
    [switch]$OhneSSH
)
$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$root = $PSScriptRoot
$berichtDir = Join-Path $root "pi_berichte"
if (-not (Test-Path $berichtDir)) { New-Item -ItemType Directory $berichtDir | Out-Null }
$bericht = Join-Path $berichtDir ("piverbindungtest1_{0}.txt" -f (Get-Date -Format "yyyy-MM-dd_HHmm"))
$erg = New-Object System.Collections.ArrayList

function Log($text, $farbe = "Gray") {
    Write-Host $text -ForegroundColor $farbe
    Add-Content -Path $bericht -Value $text -Encoding UTF8
}
function Teil($text) { Log ""; Log "=== $text" "Cyan" }
function Ergebnis($nr, $ok, $text, $hilfe = "") {
    [void]$erg.Add([pscustomobject]@{ Nr = $nr; OK = $ok; Text = $text; Hilfe = $hilfe })
    if ($ok) { Log "  [OK]     $text" "Green" } else { Log "  [FEHLER] $text" "Red"; if ($hilfe) { Log "           -> $hilfe" "Yellow" } }
}
function Port-Offen($ip, $port, $ms = 1500) {
    $c = New-Object Net.Sockets.TcpClient
    try { $a = $c.BeginConnect($ip, $port, $null, $null); $ok = $a.AsyncWaitHandle.WaitOne($ms) -and $c.Connected } catch { $ok = $false }
    $c.Close(); return $ok
}

Log "piverbindungtest1 - $(Get-Date -Format 'dd.MM.yyyy HH:mm:ss') - Laptop: $env:COMPUTERNAME"

# ---------------------------------------------------------------- 1 Laptop-Netz
Teil "1/6 Netzwerk des Laptops"
$ipcfg = Get-NetIPConfiguration | Where-Object { $_.NetAdapter.Status -eq "Up" -and $_.IPv4Address } |
    Where-Object { $_.IPv4Address.IPAddress -notlike "127.*" }
$eigeneIP = $null; $prefix = 24
foreach ($c in $ipcfg) {
    $ip = $c.IPv4Address | Select-Object -First 1
    $gw = if ($c.IPv4DefaultGateway) { $c.IPv4DefaultGateway.NextHop } else { "-" }
    Log ("  Adapter '{0}': IP {1}/{2}  Gateway {3}" -f $c.InterfaceAlias, $ip.IPAddress, $ip.PrefixLength, $gw)
    if (-not $eigeneIP -and $c.InterfaceAlias -match "WLAN|Wi-?Fi|Wireless") { $eigeneIP = $ip.IPAddress; $prefix = $ip.PrefixLength }
}
if (-not $eigeneIP -and $ipcfg) { $ip = ($ipcfg | Select-Object -First 1).IPv4Address | Select-Object -First 1; $eigeneIP = $ip.IPAddress; $prefix = $ip.PrefixLength }
if (-not $eigeneIP) {
    Ergebnis 1 $false "Laptop hat keine Netzwerkverbindung" "Mit dem WLAN der Anlage verbinden (Taskleiste rechts unten), dann Test neu starten."
} elseif ($eigeneIP -like "169.254.*") {
    Ergebnis 1 $false "Laptop hat nur eine Notfall-IP ($eigeneIP) - keine Adresse vom Router/Pi bekommen" "WLAN trennen und neu verbinden; pruefen, ob Router/Pi eingeschaltet ist."
} else {
    Ergebnis 1 $true "Laptop ist im Netz: $eigeneIP/$prefix"
}

# ---------------------------------------------------------------- 2 Pi finden
Teil "2/6 Raspberry Pi suchen"
$kandidaten = @($PiName, "hsnrrp1", "hsnrrp1.local", "hsnrpi1", "hsnrpi1.local") | Where-Object { $_ } | Select-Object -Unique
$PiIP = $null; $PiHost = $null
foreach ($n in $kandidaten) {
    if ($n -match '^\d+\.\d+\.\d+\.\d+$') { $PiIP = $n; $PiHost = $n; Log "  IP vorgegeben: $n"; break }
    try {
        $a = [Net.Dns]::GetHostAddresses($n) | Where-Object { $_.AddressFamily -eq "InterNetwork" } | Select-Object -First 1
        if ($a) { $PiIP = $a.IPAddressToString; $PiHost = $n; Log "  Name '$n' gefunden -> $PiIP" "Green"; break }
    } catch { Log "  Name '$n' nicht gefunden" }
}
if (-not $PiIP -and $eigeneIP -and $eigeneIP -notlike "169.254.*") {
    $netz = ($eigeneIP -split '\.')[0..2] -join '.'
    Log "  Kein Name gefunden - suche im Netz $netz.1-254 nach Geraeten mit SSH (Port 22), ca. 5 s ..."
    $offen = @{}
    foreach ($i in 1..254) {
        $ip = "$netz.$i"; if ($ip -eq $eigeneIP) { continue }
        $c = New-Object Net.Sockets.TcpClient
        try { $offen[$ip] = @($c, $c.BeginConnect($ip, 22, $null, $null)) } catch { $c.Close() }
    }
    Start-Sleep -Seconds 4
    $treffer = @()
    foreach ($ip in $offen.Keys) { $c = $offen[$ip][0]; if ($c.Connected) { $treffer += $ip }; $c.Close() }
    # Raspberry-Pi-Herstellerkennungen (MAC-Anfang) aus der ARP-Tabelle
    $piMac = "b8-27-eb|dc-a6-32|e4-5f-01|d8-3a-dd|2c-cf-67|28-cd-c1"
    $arpPi = @(arp -a | Select-String -Pattern $piMac | ForEach-Object { ($_.Line.Trim() -split '\s+')[0] })
    foreach ($ip in $arpPi) { Log "  Raspberry-Pi-Hardware erkannt (MAC) unter $ip" "Green" }
    foreach ($ip in $treffer) { Log "  SSH offen bei $ip" }
    $bevorzugt = @($treffer | Where-Object { $arpPi -contains $_ })
    if ($bevorzugt.Count -ge 1) { $PiIP = $bevorzugt[0] }
    elseif ($treffer.Count -eq 1) { $PiIP = $treffer[0] }
    elseif ($arpPi.Count -ge 1) { $PiIP = $arpPi[0] }
    elseif ($treffer.Count -gt 1) { Log "  Mehrere Geraete mit SSH - bitte Test mit -PiName <IP> wiederholen: $($treffer -join ', ')" "Yellow" }
    $PiHost = $PiIP
}
if ($PiIP) {
    Ergebnis 2 $true "Pi gefunden: $PiHost ($PiIP)"
} else {
    Ergebnis 2 $false "Pi nicht gefunden" "Pi eingeschaltet? Nach dem Einschalten 1-2 min warten. Laptop im selben WLAN wie der Pi? IP aus der Geraeteliste des Routers ablesen und Test mit -PiName <IP> starten."
}

# ---------------------------------------------------------------- 3 Ping
Teil "3/6 Ping"
if ($PiIP) {
    $ping = Test-Connection -ComputerName $PiIP -Count 3 -ErrorAction SilentlyContinue
    if ($ping) {
        $ms = [math]::Round(($ping | Measure-Object -Property ResponseTime -Average).Average)
        Ergebnis 3 $true "Pi antwortet auf Ping (Mittel $ms ms, $(@($ping).Count)/3 Antworten)"
    } else {
        Ergebnis 3 $false "Pi antwortet nicht auf Ping" "Kann bei manchen Netzen gesperrt sein - entscheidend ist Schritt 4 (Port 22)."
    }
} else { Log "  uebersprungen (kein Pi gefunden)" }

# ---------------------------------------------------------------- 4 Ports
Teil "4/6 Dienste am Pi (Ports)"
$ssh22 = $false
if ($PiIP) {
    $ssh22 = Port-Offen $PiIP 22
    Ergebnis 4 $ssh22 "SSH-Dienst (Port 22) $(if($ssh22){'erreichbar'}else{'NICHT erreichbar'})" "SSH ist am Pi aus (raspi-config -> Interface Options -> SSH) oder falsches Geraet."
    $mq = Port-Offen $PiIP 1883
    Log ("  [INFO]   MQTT-Broker (Port 1883): {0}" -f $(if ($mq) { "laeuft bereits" } else { "laeuft noch nicht (wird spaeter eingerichtet, kein Fehler)" }))
} else { Log "  uebersprungen" }

# ---------------------------------------------------------------- 5 SSH + Selbsttest
Teil "5/6 Anmeldung am Pi + Pruefbericht + Selbsttest"
$sshOk = $false; $selbsttest = $false; $offenPunkte = @()
if ($OhneSSH) { Log "  uebersprungen (-OhneSSH)" }
elseif (-not $ssh22) { Log "  uebersprungen (Port 22 nicht erreichbar)" }
else {
    $stage = Join-Path $env:TEMP "piverbindungtest1_stage"
    if (Test-Path $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    New-Item -ItemType Directory $stage | Out-Null
    Copy-Item (Join-Path $root "sortieranlage\*.py") $stage
    Copy-Item (Join-Path $root "pi\pi_setup.sh") $stage
    Get-ChildItem $stage -File | ForEach-Object {   # Linux-Zeilenenden
        $t = [IO.File]::ReadAllText($_.FullName) -replace "`r`n", "`n"
        [IO.File]::WriteAllText($_.FullName, $t, (New-Object Text.UTF8Encoding $false))
    }
    $batch = Join-Path $env:TEMP "piverbindungtest1.cmd"
    $remote = "mkdir -p ~/sortieranlage_test && tar -xf - -C ~/sortieranlage_test && cd ~/sortieranlage_test && bash pi_setup.sh"
    $zeilen = @("@echo off",
        "tar -cf - -C `"$stage`" . | ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 $Benutzer@$PiIP `"$remote`"")
    [IO.File]::WriteAllLines($batch, $zeilen, (New-Object Text.ASCIIEncoding))
    Log ""
    Log "  >>> Jetzt fragt ssh nach dem PASSWORT fuer $Benutzer@$PiIP." "Yellow"
    Log "  >>> Passwort eintippen und Enter druecken. Beim Tippen erscheinen KEINE Zeichen - das ist normal." "Yellow"
    Log ""
    $ausgabe = & cmd /c $batch
    $code = $LASTEXITCODE
    $ausgabe | ForEach-Object { Log "  | $_" }
    Remove-Item -LiteralPath $batch, $stage -Recurse -Force -ErrorAction SilentlyContinue
    $text = ($ausgabe -join "`n")
    $sshOk = ($text -match "Pi-Bericht Sortieranlage")
    if ($sshOk) {
        Ergebnis 5 $true "Anmeldung am Pi erfolgreich, Code nach ~/sortieranlage_test kopiert"
    } else {
        Ergebnis 5 $false "Anmeldung/Kopieren fehlgeschlagen (Code $code)" "Passwort falsch ('Permission denied')? Neu starten und genau tippen. Meldung 'HOST IDENTIFICATION HAS CHANGED': einmal  ssh-keygen -R $PiIP  ausfuehren."
    }
    if ($sshOk) {
        $selbsttest = ($text -match "SELBSTTEST BESTANDEN")
        Ergebnis 6 $selbsttest "Selbsttest der Steuerung auf dem Pi (Simulation): $(if($selbsttest){'BESTANDEN'}else{'nicht bestanden'})" "Python 3 auf dem Pi fehlt oder Fehler im Code - Bericht an Claude geben."
        $offenPunkte = @($ausgabe | Where-Object { $_ -match "\[OFFEN\]" } | ForEach-Object { ($_ -replace '^\s*\[OFFEN\]\s*', '').Trim() })
    }
}

# ---------------------------------------------------------------- 6 Zusammenfassung
Teil "6/6 ZUSAMMENFASSUNG"
foreach ($e in $erg) { Log ("  {0} Schritt {1}: {2}" -f $(if ($e.OK) { "[OK]    " } else { "[FEHLER]" }), $e.Nr, $e.Text) $(if ($e.OK) { "Green" } else { "Red" }) }
if ($offenPunkte.Count) {
    Log ""; Log "  Hinweise vom Pi (kein Fehler des Tests, sondern noch einzurichten):" "Yellow"
    $offenPunkte | ForEach-Object { Log "   - $_" "Yellow" }
}
Log ""
$fehler = @($erg | Where-Object { -not $_.OK -and $_.Nr -ne 3 })
if ($selbsttest) {
    Log "  ERGEBNIS: ALLES GRUEN - Verbindung steht, Steuerung laeuft auf dem Pi (Simulation)." "Green"
    Log "  Naechster Schritt: einmal  .\laptop\01_ssh_schluessel_einrichten.ps1 -PiHost $PiIP  (dann kann Claude ohne Passwort weitermachen)." "Green"
} elseif ($sshOk -or ($ssh22 -and $OhneSSH)) {
    Log "  ERGEBNIS: Verbindung steht, aber nicht alles gruen - Bericht an Claude geben." "Yellow"
} elseif ($fehler.Count) {
    Log "  ERGEBNIS: Verbindung NICHT hergestellt. Ersten roten Schritt oben ansehen und den Hinweis (->) befolgen." "Red"
}
Log "  Bericht gespeichert: $bericht"
Log "  Pi-IP fuer die Doku (Netzwerkplan): $(if($PiIP){$PiIP}else{'unbekannt'})"
