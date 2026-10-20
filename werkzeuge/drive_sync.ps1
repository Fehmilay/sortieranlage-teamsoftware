# Kopiert die aktuelle Excel-Gesamtdatei und den Leistungsnachweis (PDF) in den Drive-Ordner
# "04 Excel + PDFs" – über "Google Drive für Desktop" (Konto kubilayff@gmail.com).
# Einmalig nötig: Google Drive für Desktop installieren und mit kubilayff anmelden (legt Laufwerk G: o. Ä. an).
# Aufruf: powershell -NoProfile -ExecutionPolicy Bypass -File werkzeuge\drive_sync.ps1
$ErrorActionPreference = "Stop"
$projekt = Split-Path $PSScriptRoot -Parent

# Google-Drive-Laufwerk suchen ("Meine Ablage" bzw. "My Drive")
$ablage = $null
foreach ($lw in Get-PSDrive -PSProvider FileSystem) {
    foreach ($n in "Meine Ablage", "My Drive") {
        $p = Join-Path $lw.Root $n
        if (Test-Path $p) { $ablage = $p; break }
    }
    if ($ablage) { break }
}
if (-not $ablage) {
    Write-Host "FEHLER: Google Drive für Desktop nicht gefunden (kein Laufwerk mit 'Meine Ablage')." -ForegroundColor Red
    Write-Host "Einmalig installieren: https://www.google.com/drive/download/ und mit kubilayff@gmail.com anmelden."
    exit 1
}
$team = Get-ChildItem $ablage -Directory | Where-Object Name -like "Sortieranlage*Team Software*" | Select-Object -First 1
if (-not $team) { Write-Host "FEHLER: Team-Ordner 'Sortieranlage – Team Software …' nicht in $ablage." -ForegroundColor Red; exit 1 }
$ziel = Get-ChildItem $team.FullName -Directory | Where-Object Name -like "04 Excel*" | Select-Object -First 1
if (-not $ziel) { Write-Host "FEHLER: Unterordner '04 Excel + PDFs' fehlt." -ForegroundColor Red; exit 1 }

$dateien = @(
    @{ von = "Leistungsnachweis_gesamt_bis_13-10-2026_aktualisiert.xlsx"; nach = "Leistungsnachweis_gesamt_bis_13-10-2026_aktualisiert.xlsx" }
)
$pdf = Get-ChildItem (Join-Path $projekt "abgabe") -Filter "Leistungsnachweis_Rushit_Vlasi_Stand_*.pdf" -ErrorAction SilentlyContinue |
       Sort-Object LastWriteTime | Select-Object -Last 1
if ($pdf) { $dateien += @{ von = "abgabe\$($pdf.Name)"; nach = $pdf.Name } }

foreach ($d in $dateien) {
    $quelle = Join-Path $projekt $d.von
    Copy-Item $quelle (Join-Path $ziel.FullName $d.nach) -Force   # gleicher Name -> Drive legt eine neue Version an
    Write-Host "OK  $($d.nach) -> $($ziel.FullName)"
}
Write-Host "Fertig. Google Drive lädt die Dateien jetzt im Hintergrund hoch."
