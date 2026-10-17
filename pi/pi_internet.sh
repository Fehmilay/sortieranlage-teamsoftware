#!/usr/bin/env bash
# Verbindet den Pi KURZ über einen Handy-Hotspot mit dem Internet, stellt die Uhr, installiert Hilfsprogramme
# und trennt danach automatisch wieder. Wird von PI_INTERNET.bat (Laptop) gestartet.
# Aufruf auf dem Pi:  sudo bash pi_internet.sh "<Hotspot-Name>"
# Sicherheit: Läuft nur, wenn der Pi per Netzwerkkabel (eth0) im Anlagennetz hängt – so bleibt er immer erreichbar.
# Es wird nichts aktualisiert außer den genannten Hilfsprogrammen (kein Systemupdate).
set -u
if [ "$(id -u)" != 0 ]; then echo "[FEHLER] bitte mit sudo starten"; exit 1; fi
SSID="${1:-}"
if [ -z "$SSID" ]; then echo "[FEHLER] Hotspot-Name fehlt"; exit 1; fi
cd "$(dirname "$0")"
BERICHT="$(pwd)/pi_internet_bericht.txt"
exec > >(tee "$BERICHT") 2>&1
ok()     { echo "[OK]     $1"; }
fehler() { echo "[FEHLER] $1"; }
info()   { echo "[INFO]   $1"; }

if ! command -v nmcli >/dev/null; then fehler "NetworkManager (nmcli) fehlt – abgebrochen"; exit 1; fi
ETH_IP=$(ip -4 -o addr show eth0 2>/dev/null | awk '{print $4}' | cut -d/ -f1)
if [ -z "$ETH_IP" ]; then
  fehler "Netzwerkkabel (eth0) ohne Verbindung – abgebrochen. Sonst wäre der Pi nach dem Umschalten nicht mehr erreichbar."
  exit 1
fi
ok "Pi bleibt per Kabel im Anlagennetz erreichbar ($ETH_IP)"
ALT=$(nmcli -t -f NAME,DEVICE con show --active | awk -F: '$2=="wlan0"{print $1}')
info "Bisheriges WLAN des Pi: ${ALT:-keins}"

zurueck() {
  echo
  echo "== Zurück ins Anlagennetz"
  nmcli con down sortier-hotspot >/dev/null 2>&1
  nmcli con delete sortier-hotspot >/dev/null 2>&1
  if [ -n "$ALT" ] && nmcli con up "$ALT" >/dev/null 2>&1; then
    ok "WLAN des Pi wieder mit dem Anlagennetz verbunden – Internet getrennt"
  else
    info "Internet getrennt. WLAN der Anlage nicht automatisch verbunden (Kabel reicht, nach Neustart wieder normal)"
  fi
}
trap zurueck EXIT

echo
echo "== Mit dem Hotspot „$SSID“ verbinden – gleich das HOTSPOT-Passwort (vom Handy) eintippen"
nmcli con delete sortier-hotspot >/dev/null 2>&1
if ! nmcli --ask dev wifi connect "$SSID" ifname wlan0 name sortier-hotspot; then
  fehler "Verbindung zum Hotspot fehlgeschlagen – Name/Passwort richtig? Hotspot an? Am Handy „2,4 GHz“ bzw. „Kompatibilität maximieren“ einschalten."
  exit 1
fi
nmcli con modify sortier-hotspot ipv4.route-metric 10 ipv6.route-metric 10 connection.autoconnect no >/dev/null 2>&1
nmcli con up sortier-hotspot >/dev/null 2>&1
sleep 3
if ping -c2 -W3 1.1.1.1 >/dev/null 2>&1 && getent hosts deb.debian.org >/dev/null 2>&1; then
  ok "Internet erreichbar"
else
  fehler "Kein Internet über den Hotspot (mobile Daten am Handy an?)"
  exit 1
fi

echo
echo "== Uhrzeit aus dem Internet"
timedatectl set-ntp true >/dev/null 2>&1
sleep 8
ok "Uhrzeit jetzt: $(date '+%d.%m.%Y %H:%M')"

echo
echo "== Hilfsprogramme installieren (dauert 1–3 Minuten)"
if apt-get update -qq >/dev/null 2>&1; then ok "Paketliste geladen"; else fehler "Paketliste konnte nicht geladen werden"; exit 1; fi
for p in mosquitto-clients i2c-tools python3-gpiozero python3-lgpio; do
  if dpkg -s "$p" >/dev/null 2>&1; then
    ok "$p schon vorhanden"
  elif DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$p" >/dev/null 2>&1; then
    ok "$p installiert"
  else
    info "$p nicht installiert (nicht schlimm)"
  fi
done
echo
echo "ERGEBNIS: INTERNET-SCHRITT OK – Pi wird jetzt wieder vom Internet getrennt"
exit 0
