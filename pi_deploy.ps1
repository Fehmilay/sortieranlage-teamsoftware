# Kopiert einen Projektordner auf den Raspberry Pi und startet das Programm.
# Aufruf (PowerShell): .\pi_deploy.ps1 -Quelle .\sortieranlage -Start main.py
# Das Passwort wird von ssh/scp abgefragt und NICHT in dieser Datei gespeichert.
# Ungetestet: vor dem ersten Einsatz Host/Benutzer/Zielordner mit Prof. Kampker abstimmen.
param(
    [string]$Quelle = ".\sortieranlage",
    [string]$Start = "main.py",
    [string]$PiHost = "hsnrpi1.local",
    [string]$Benutzer = "admin",
    [string]$Ziel = "/home/admin/"
)
$ordner = Split-Path -Leaf (Resolve-Path $Quelle)
Write-Host "1/3 Erreichbarkeit pruefen: $PiHost"
ping $PiHost -n 2
Write-Host "2/3 Kopiere $Quelle nach ${Benutzer}@${PiHost}:$Ziel"
scp -r $Quelle "${Benutzer}@${PiHost}:$Ziel"
if ($LASTEXITCODE -ne 0) { Write-Error "scp fehlgeschlagen"; exit 1 }
Write-Host "3/3 Starte python3 $Start (Beenden mit Strg+C)"
ssh -t "${Benutzer}@${PiHost}" "cd $Ziel$ordner && python3 $Start"
