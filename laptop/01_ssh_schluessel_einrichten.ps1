# EINMALIG vom Menschen auszufuehren (nicht von Claude): richtet die passwortlose
# SSH-Anmeldung Laptop -> Pi ein. Danach kann Claude alle weiteren Schritte im Terminal
# ohne Passworteingabe ausfuehren (02_einspielen.ps1).
#
# Aufruf (PowerShell im Ordner projektmanagement):
#   .\laptop\01_ssh_schluessel_einrichten.ps1
#   .\laptop\01_ssh_schluessel_einrichten.ps1 -PiHost 192.168.0.50     # falls hsnrpi1.local nicht aufloest
#
# Das Pi-Passwort wird nur von ssh abgefragt und NIRGENDS gespeichert.
param(
    [string]$PiHost = "hsnrpi1.local",
    [string]$Benutzer = "admin",
    [string]$Alias = "hsnrpi"
)
$ErrorActionPreference = "Stop"
$sshDir = Join-Path $HOME ".ssh"
$key = Join-Path $sshDir "id_ed25519_hsnrpi"
$cfg = Join-Path $sshDir "config"
if (-not (Test-Path $sshDir)) { New-Item -ItemType Directory $sshDir | Out-Null }

Write-Host "1/4 Schluessel $key"
if (-not (Test-Path $key)) {
    ssh-keygen -t ed25519 -N '""' -C "laptop-sortieranlage" -f $key
} else { Write-Host "    vorhanden" }

Write-Host "2/4 Eintrag '$Alias' in $cfg"
$block = @"

Host $Alias
    HostName $PiHost
    User $Benutzer
    IdentityFile $key
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
    ConnectTimeout 8
"@
$vorhanden = (Test-Path $cfg) -and (Select-String -Path $cfg -Pattern "^Host $Alias\s*$" -Quiet)
if ($vorhanden) {
    Write-Host "    Eintrag existiert bereits - HostName ggf. von Hand in $cfg anpassen"
} else {
    Add-Content -Path $cfg -Value $block -Encoding ascii
}

Write-Host "3/4 Oeffentlichen Schluessel auf den Pi kopieren (jetzt einmal das Pi-Passwort eingeben)"
Get-Content "$key.pub" | ssh $Alias "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
if ($LASTEXITCODE -ne 0) { Write-Error "Kopieren fehlgeschlagen (Netz/Passwort pruefen)" }

Write-Host "4/4 Test ohne Passwort"
ssh -o BatchMode=yes $Alias "echo SSH-OK: `$(hostname)"
if ($LASTEXITCODE -eq 0) {
    Write-Host "FERTIG. Jetzt Claude sagen: 'Pi ist verbunden' -> Claude fuehrt .\laptop\02_einspielen.ps1 aus." -ForegroundColor Green
} else {
    Write-Host "Test fehlgeschlagen - siehe README.txt, Abschnitt Fehlerbehebung." -ForegroundColor Red
}
