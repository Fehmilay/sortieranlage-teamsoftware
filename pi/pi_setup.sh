#!/usr/bin/env bash
# Einrichtung/Bestandsaufnahme auf dem Raspberry Pi (hsnrpi1). Läuft im Projektordner.
# Aufruf:  bash pi_setup.sh [--installieren] [--autostart]
#   ohne Optionen : nur prüfen und Bericht pi_bericht.txt schreiben (ändert nichts)
#   --installieren: Mosquitto-Broker installieren/konfigurieren (braucht sudo ohne Passwort;
#                   apt braucht Internet ODER vorher kopierte .deb-Pakete in ./debs/)
#   --autostart   : systemd-Dienst "sortieranlage" einrichten (startet Simulation im Dauerbetrieb,
#                   bis HARDWARE_FREIGEGEBEN in config.py gesetzt ist)
# Keine Zugangsdaten in dieser Datei.
set -u
cd "$(dirname "$0")"
DIR="$(pwd)"
BERICHT="$DIR/pi_bericht.txt"
INSTALL=0; AUTOSTART=0
for a in "$@"; do
  case "$a" in
    --installieren) INSTALL=1 ;;
    --autostart) AUTOSTART=1 ;;
  esac
done

exec > >(tee "$BERICHT") 2>&1
abschnitt() { echo; echo "== $1"; }
ok() { echo "[OK]    $1"; }
warn() { echo "[OFFEN] $1"; }

echo "Pi-Bericht Sortieranlage – $(date '+%Y-%m-%d %H:%M:%S') (Uhrzeit des Pi, ohne Internet ggf. falsch)"
abschnitt "System"
echo "Host: $(hostname)  Benutzer: $(whoami)  Ordner: $DIR"
grep -E '^(PRETTY_NAME|VERSION_CODENAME)=' /etc/os-release 2>/dev/null
echo "Architektur: $(uname -m)  Kernel: $(uname -r)"
tr -d '\0' 2>/dev/null < /proc/device-tree/model; echo
python3 --version
df -h "$DIR" | tail -1

abschnitt "Netzwerk (IP-Adressen fuer Netzwerkplan/Peakboard)"
ip -br addr 2>/dev/null | grep -v '^lo'
echo "Gateway: $(ip route 2>/dev/null | awk '/default/ {print $3; exit}')"
if ping -c1 -W2 1.1.1.1 >/dev/null 2>&1; then INTERNET=1; ok "Internet erreichbar"; else INTERNET=0; warn "kein Internet (erwartet im Anlagennetz)"; fi
command -v nmcli >/dev/null && nmcli -t -f NAME,TYPE,DEVICE con show --active 2>/dev/null | sed 's/^[^:]*:/<Verbindung>:/'

abschnitt "Rechte"
if sudo -n true 2>/dev/null; then SUDO=1; ok "sudo ohne Passwort moeglich"; else SUDO=0; warn "sudo verlangt Passwort -> Installationen manuell (siehe README)"; fi

abschnitt "Automation HAT / I2C"
echo "I2C-Geraete: $(ls /dev/i2c-* 2>/dev/null | tr '\n' ' ')"
# Der Automation HAT haengt am GPIO-I2C-Bus 1; i2c-20/21 sind beim Pi 4 nur die HDMI-Busse.
if [ -e /dev/i2c-1 ]; then ok "GPIO-I2C (Bus 1) aktiv"; else warn "GPIO-I2C (Bus 1) nicht aktiv -> raspi-config -> Interface Options -> I2C (fuer Automation HAT noetig)"; fi
if command -v i2cdetect >/dev/null; then i2cdetect -y 1 2>/dev/null; echo "(Automation HAT erwartet u. a. 0x48 ADC, 0x54 LED-Treiber)"; else warn "i2c-tools nicht installiert"; fi
if python3 -c "import automationhat" 2>/dev/null; then ok "Python-Modul automationhat vorhanden"; else warn "Python-Modul automationhat fehlt (nur fuer Hardware-Modus noetig)"; fi

abschnitt "MQTT-Broker (Mosquitto)"
if command -v mosquitto >/dev/null; then ok "mosquitto installiert: $(mosquitto -h 2>/dev/null | head -1)"; HAT_BROKER=1; else warn "mosquitto nicht installiert"; HAT_BROKER=0; fi
systemctl is-active mosquitto 2>/dev/null | sed 's/^/Dienst mosquitto: /'
ss -ltn 2>/dev/null | grep -E ':1883\b' || warn "Port 1883 lauscht nicht"

if [ "$INSTALL" = 1 ]; then
  abschnitt "Installation Mosquitto"
  if [ "$SUDO" != 1 ]; then
    warn "uebersprungen: sudo braucht Passwort"
  else
    if [ "$HAT_BROKER" = 0 ]; then
      if ls ./debs/*.deb >/dev/null 2>&1; then
        sudo -n apt-get install -y ./debs/*.deb && HAT_BROKER=1
      elif [ "$INTERNET" = 1 ]; then
        sudo -n apt-get update && sudo -n apt-get install -y mosquitto mosquitto-clients && HAT_BROKER=1
      else
        warn "weder Internet noch ./debs/*.deb -> siehe README Abschnitt Broker"
      fi
    fi
    if [ "$HAT_BROKER" = 1 ]; then
      # VORSCHLAG: im geschlossenen Anlagennetz anonyme Verbindungen auf Port 1883 erlauben,
      # damit die Peakboard Box abonnieren kann (Mosquitto 2.x erlaubt sonst nur localhost).
      sudo -n cp "$DIR/mosquitto_sortieranlage.conf" /etc/mosquitto/conf.d/sortieranlage.conf
      sudo -n systemctl enable mosquitto && sudo -n systemctl restart mosquitto
      sleep 1
      ss -ltn | grep -E ':1883\b' && ok "Broker lauscht auf 1883"
    fi
  fi
fi

if [ "$AUTOSTART" = 1 ]; then
  abschnitt "Autostart (systemd)"
  if [ "$SUDO" = 1 ]; then
    sed -e "s#__DIR__#$DIR#g" -e "s#__USER__#$(whoami)#g" "$DIR/sortieranlage.service" \
      | sudo -n tee /etc/systemd/system/sortieranlage.service >/dev/null
    sudo -n systemctl daemon-reload && sudo -n systemctl enable --now sortieranlage
    sleep 2; systemctl --no-pager status sortieranlage | head -5
  else
    warn "uebersprungen: sudo braucht Passwort"
  fi
fi

abschnitt "Selbsttest Steuerung (Simulation, ohne Hardware)"
python3 selbsttest.py
abschnitt "Ersatztest Hardware-Code (ohne Hardware)"
[ -f hardware_ersatztest.py ] && python3 hardware_ersatztest.py
abschnitt "Ende"
echo "Bericht: $BERICHT"
