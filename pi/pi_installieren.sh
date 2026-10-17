#!/usr/bin/env bash
# Richtet den Raspberry Pi für die Sortieranlage ein – wird von PI_EINRICHTEN.bat (Laptop) gestartet.
# Aufruf auf dem Pi:  sudo bash pi_installieren.sh <unixzeit-vom-laptop> [--autostart]
# Braucht KEIN Internet. Macht:
#   1 Uhrzeit vom Laptop übernehmen   2 I2C einschalten (Platinen)   3 Mosquitto fürs Netz freigeben (Peakboard)
#   4 Python-Treiber prüfen           5 Programm-Tests              6 Autostart-Dienst (nur mit --autostart einschalten)
#   7 angeschlossene Platinen erkennen
# Schaltet KEINE Motoren/Ventile. Bericht: pi_installation_bericht.txt
set -u
if [ "$(id -u)" != 0 ]; then echo "[FEHLER] bitte mit sudo starten"; exit 1; fi
cd "$(dirname "$0")"
DIR="$(pwd)"
NUTZER="${SUDO_USER:-admin}"
BERICHT="$DIR/pi_installation_bericht.txt"
ZEIT="${1:-}"
AUTOSTART=0; [ "${2:-}" = "--autostart" ] && AUTOSTART=1
FEHLER=0; NEUSTART=0
exec > >(tee "$BERICHT") 2>&1
ok()     { echo "[OK]     $1"; }
fehler() { echo "[FEHLER] $1"; FEHLER=1; }
info()   { echo "[INFO]   $1"; }
als_nutzer() { sudo -u "$NUTZER" bash -c "cd '$DIR' && $1"; }

echo "Pi-Einrichtung Sortieranlage – $(hostname) – Benutzer $NUTZER – Ordner $DIR"

echo; echo "== 1/7 Uhrzeit"
if [[ "$ZEIT" =~ ^[0-9]+$ ]]; then
  ABW=$(( $(date +%s) - ZEIT )); ABW=${ABW#-}
  if [ "$ABW" -gt 120 ]; then
    date -s "@$ZEIT" >/dev/null && ok "Uhrzeit vom Laptop übernommen: $(date '+%d.%m.%Y %H:%M')"
  else
    ok "Uhrzeit stimmt ($(date '+%d.%m.%Y %H:%M'))"
  fi
else
  info "keine Laptop-Zeit übergeben – Uhrzeit unverändert"
fi

echo; echo "== 2/7 I2C (Leitung zu den Platinen)"
if command -v raspi-config >/dev/null; then
  raspi-config nonint do_i2c 0 && ok "I2C in der Pi-Konfiguration eingeschaltet"
else
  CFG=/boot/firmware/config.txt; [ -f "$CFG" ] || CFG=/boot/config.txt
  grep -q '^dtparam=i2c_arm=on' "$CFG" || echo 'dtparam=i2c_arm=on' >> "$CFG"
  info "I2C in $CFG eingetragen"
fi
modprobe i2c-dev 2>/dev/null
grep -qx 'i2c-dev' /etc/modules 2>/dev/null || echo 'i2c-dev' >> /etc/modules
if [ -e /dev/i2c-1 ]; then ok "I2C-Bus 1 aktiv"; else info "I2C wird nach einem Neustart aktiv"; NEUSTART=1; fi
for g in i2c gpio; do getent group "$g" >/dev/null && usermod -aG "$g" "$NUTZER"; done
ok "Benutzer $NUTZER darf I2C und GPIO benutzen"

echo; echo "== 3/7 Mosquitto (Postamt für die Peakboard-Nachrichten)"
if ! command -v mosquitto >/dev/null && ls "$DIR"/debs/*.deb >/dev/null 2>&1; then
  apt-get install -y "$DIR"/debs/*.deb >/dev/null && ok "Mosquitto aus mitgebrachten Paketen installiert"
fi
if command -v mosquitto >/dev/null; then
  ok "Mosquitto installiert"
  ANDERE=$(ls /etc/mosquitto/conf.d/*.conf 2>/dev/null | grep -v '/sortieranlage.conf$')
  if grep -qsE '^[[:space:]]*(listener|password_file|allow_anonymous)' /etc/mosquitto/mosquitto.conf $ANDERE; then
    # Prof. Kampker hat Mosquitto mit Benutzer/Passwort eingerichtet (16.10.2026) -> NIE eine anonyme Freigabe dazulegen
    rm -f /etc/mosquitto/conf.d/sortieranlage.conf
    info "Mosquitto hat schon eine eigene Einstellung mit Anmeldung (von Prof. Kampker) – nicht verändert"
  else
    cp "$DIR/mosquitto_sortieranlage.conf" /etc/mosquitto/conf.d/sortieranlage.conf
    ok "Netz-Freigabe für Peakboard eingetragen (Port 1883, nur im Anlagennetz)"
  fi
  systemctl enable mosquitto >/dev/null 2>&1
  systemctl restart mosquitto; sleep 2
  if systemctl is-active --quiet mosquitto; then
    ok "Mosquitto läuft und startet automatisch beim Hochfahren"
  else
    fehler "Mosquitto startet mit der neuen Einstellung nicht – Änderung wird zurückgenommen"
    rm -f /etc/mosquitto/conf.d/sortieranlage.conf; systemctl restart mosquitto
  fi
  if ss -ltn 2>/dev/null | awk '$4 ~ /^(0\.0\.0\.0|\*|\[::\]):1883$/' | grep -q .; then
    ok "Mosquitto ist im Netz erreichbar (Peakboard kann sich verbinden)"
  else
    fehler "Mosquitto lauscht nur auf dem Pi selbst – Peakboard käme nicht dran"
  fi
else
  fehler "Mosquitto ist nicht installiert (Pi ohne Internet) – Prof. Kampker fragen"
fi

if ping -c1 -W3 1.1.1.1 >/dev/null 2>&1 && getent hosts deb.debian.org >/dev/null 2>&1; then
  echo; echo "== Internet vorhanden: Uhrzeit-Abgleich und Hilfsprogramme (dauert 1–3 Minuten)"
  timedatectl set-ntp true >/dev/null 2>&1 && ok "automatischer Uhrzeit-Abgleich eingeschaltet"
  if apt-get update -qq >/dev/null 2>&1; then
    for p in mosquitto-clients i2c-tools python3-gpiozero python3-lgpio; do
      if dpkg -s "$p" >/dev/null 2>&1; then ok "$p schon vorhanden"
      elif DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$p" >/dev/null 2>&1; then ok "$p installiert"
      else info "$p nicht installiert (nicht schlimm)"; fi
    done
  else
    info "Paketliste nicht ladbar – Hilfsprogramme übersprungen"
  fi
else
  info "Kein Internet – Hilfsprogramme übersprungen (nicht nötig)"
fi

echo; echo "== 4/7 Python-Treiber für die Platinen"
if ls "$DIR"/pakete/*.whl >/dev/null 2>&1 && ! als_nutzer "python3 -c 'import automationhat'" 2>/dev/null; then
  pip3 install --no-index --find-links "$DIR/pakete" --break-system-packages automationhat >/dev/null 2>&1 \
    && ok "automationhat aus mitgebrachten Paketen installiert" || info "automationhat konnte nicht installiert werden"
fi
if als_nutzer "python3 -c 'import automationhat'" 2>/dev/null; then
  ok "Pimoroni-Bibliothek automationhat vorhanden"
elif als_nutzer "python3 -c 'import gpiozero'" 2>/dev/null; then
  ok "gpiozero vorhanden – unser eingebauter Treiber für den Automation HAT Mini wird benutzt (keine Installation nötig)"
else
  fehler "Weder automationhat noch gpiozero vorhanden – Prof. Kampker fragen (Paket python3-gpiozero)"
fi
ok "Motor Driver HAT braucht keine Bibliothek (eigener Treiber motor_hat.py)"

echo; echo "== 5/7 Programm-Tests (ohne Hardware, nichts bewegt sich)"
chown -R "$NUTZER": "$DIR"
if als_nutzer "python3 selbsttest.py" 2>&1 | grep -qx "SELBSTTEST BESTANDEN"; then ok "Selbsttest Steuerung bestanden"; else fehler "Selbsttest Steuerung NICHT bestanden"; fi
if als_nutzer "python3 hardware_ersatztest.py" 2>&1 | grep -qx "HARDWARE-ERSATZTEST BESTANDEN"; then ok "Ersatztest Hardware-Code bestanden"; else fehler "Ersatztest Hardware-Code NICHT bestanden"; fi

echo; echo "== 6/7 Autostart-Dienst"
sed -e "s#__DIR__#$DIR#g" -e "s#__USER__#$NUTZER#g" "$DIR/sortieranlage.service" > /etc/systemd/system/sortieranlage.service
systemctl daemon-reload
if [ "$AUTOSTART" = 1 ]; then
  systemctl enable --now sortieranlage >/dev/null 2>&1 && ok "Autostart eingeschaltet (Simulation sendet Testdaten an Peakboard)"
else
  systemctl disable --now sortieranlage >/dev/null 2>&1
  ok "Autostart-Dienst eingerichtet, aber AUS (einschalten: PI_EINRICHTEN.bat -Autostart)"
fi

echo; echo "== 7/7 Angeschlossene Platinen"
if [ -e /dev/i2c-1 ]; then
  python3 - <<'PYEOF'
import fcntl, os
for adr, name in ((0x48, "Automation HAT Mini"), (0x40, "Motor Driver HAT")):
    fd = None
    try:
        fd = os.open("/dev/i2c-1", os.O_RDWR)
        fcntl.ioctl(fd, 0x0703, adr)
        os.read(fd, 1)
        print("[OK]     " + name + " erkannt")
    except OSError:
        print("[INFO]   " + name + " nicht gefunden – noch nicht angeschlossen? (normal, bis Team Hardware fertig ist)")
    finally:
        if fd is not None:
            os.close(fd)
PYEOF
else
  info "Platinen-Erkennung nach dem Neustart (piverbindungtest2.bat)"
fi

echo
if [ "$FEHLER" = 0 ]; then echo "ERGEBNIS: EINRICHTUNG OK"; else echo "ERGEBNIS: EINRICHTUNG MIT FEHLERN – Bericht ansehen"; fi
chown "$NUTZER": "$BERICHT" 2>/dev/null
if [ "$NEUSTART" = 1 ]; then
  echo "NEUSTART: Der Pi startet in 1 Minute neu, damit I2C aktiv wird."
  shutdown -r +1 "Neustart fuer I2C (Sortieranlage)" >/dev/null 2>&1
fi
exit $FEHLER
