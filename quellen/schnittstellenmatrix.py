"""Schnittstellenmatrix (Stand 03.11.2026) – EINE Quelle für HTML/PDF und CSV (Google-Tabelle im Drive).
Aufruf (im Projektordner):  python quellen\\schnittstellenmatrix.py
Reihenfolge = chronologisch: A Inbetriebnahme (einmalig) → B Sortierzyklus (je Klotz, wie process.py) → C Anzeige (je Klotz).
IDs passen zum Datenflussplan V4 und Netzwerkplan V2.
"""
import csv, html, os

STAND = "03.11.2026"
KOPF = ["ID", "Quelle → Ziel", "Signal / Protokoll", "Daten / Format", "Zweck"]
GRUPPEN = [
    ("A · Inbetriebnahme – einmalig, bevor die Anlage läuft", [
        ["S01", "9-V-Netzteil → Platinen + Aktoren · 5-V-Netzteil → Pi", "Spannungsversorgung (Kabel, WAGO-Klemmen)",
         "9 V DC · 5 V / 3 A", "Strom für Motor, Ventile, Kompressor und Raspberry Pi"],
        ["S02", "Laptop Team Software → Raspberry Pi", "SSH / SCP, TCP 22 (SSH-Schlüssel)",
         "Befehle, Python-Dateien, Einrichtungs-Skripte, Berichte", "Programm einspielen, einrichten, warten"],
        ["S03", "MQTT-Broker (Pi) → Laptop Peakboard Designer", "MQTT (abonnieren), TCP 1883, mit Login",
         "wie S13 – Testdaten aus der Simulation", "Board mit Live-Testdaten bauen und prüfen"],
        ["S04", "Laptop Peakboard Designer → Peakboard Box", "Peakboard-Upload über LAN / WLAN (Port noch offen)",
         "Board-Projekt (Dashboard)", "fertiges Dashboard auf die Box laden"],
    ]),
    ("B · Sortierzyklus – Reihenfolge, in der ein Klotz durchläuft", [
        ["S05", "I1 Lichtschranke Farbsensor → Automation HAT Mini Input 1 → Pi GPIO 26", "digital (Kabel, GPIO)",
         "1 = Lichtstrahl frei, 0 = unterbrochen; Abfrage alle 10 ms", "1. Klotz kommt an → Zyklus startet"],
        ["S06", "Pi → Motor Driver HAT (PCA9685, Kanal A) → Bandmotor M1", "I2C-Bus 1, Adresse 0x40; PWM; 9 V (max. 650 mA)",
         "Kanal 0 = Geschwindigkeit, Kanal 1/2 = Richtung; an / aus", "2. Band starten (und nach dem Zählen wieder stoppen)"],
        ["S07", "I2 Farbsensor → Automation HAT Mini Analog 1 (ADC ADS1015) → Pi", "analog; I2C-Bus 1, Adresse 0x48",
         "0–9 V → Messwert 0–1, kleinster Wert zählt; weiß < 0,116 ≤ rot < 0,150 ≤ blau", "3. Farbe messen, während der Klotz vorbeifährt"],
        ["S08", "C1 Impulstaster → Automation HAT Mini Input 3 → Pi GPIO 21", "digital, Impulse (Kabel, GPIO)",
         "Impulse des Zahnrads, entprellt (beide Flanken)", "4. Band überwachen (kein Impuls 2 s = blockiert), später Weg zählen"],
        ["S09", "I3 Lichtschranke Auswurf → Automation HAT Mini Input 2 → Pi GPIO 20", "digital (Kabel, GPIO)",
         "1 / 0; Abfrage alle 10 ms", "5. Klotz am Auswurf → Farbe steht fest; am Ende: Ausgang wieder frei?"],
        ["S10", "Pi GPIO 16 → Automation HAT Mini Relais → Kompressor O8", "Relais, 9 V (max. 200 mA)",
         "ein / aus, mind. 1 s vor dem Ventil", "6. Druckluft aufbauen, während der Klotz zum Ventil fährt (5 / 15 / 26 Impulse)"],
        ["S11", "Pi GPIO 5 / 12 / 6 → Automation HAT Mini Output 1–3 → Ventile O5 / O6 / O7", "digital, 9 V geschaltet",
         "ein / aus, Stoß 0,5 s", "7. Klotz in die Rutsche seiner Farbe schieben"],
    ]),
    ("C · Anzeige – nach jedem Klotz und bei jeder Änderung", [
        ["S12", "Steuerungsprogramm (mqtt_client.py) → MQTT-Broker Mosquitto auf dem Pi", "MQTT 3.1.1, TCP 1883 (localhost), mit Benutzer + Passwort",
         "Text-Werte sortieranlage/wert/* (retain) + JSON-Ereignis sortieranlage/event {event, color, cycle_count, timestamp}", "8. Ergebnis und Zustand veröffentlichen"],
        ["S13", "MQTT-Broker (Pi) → Peakboard Box", "MQTT (abonnieren), TCP 1883, mit Login; LAN / WLAN",
         "Format A (Text): zustand, zyklen, farbe_letzte, anzahl_weiss / _rot / _blau, fehler_aktiv, fehler_text, modus", "9. Dashboard mit Live-Daten versorgen"],
        ["S14", "Peakboard Box → Bildschirm", "HDMI", "Bildsignal", "10. Anzeige an der Anlage"],
    ]),
]
ZEILEN = [z for _, g in GRUPPEN for z in g]

HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)


def html_seite():
    teile = []
    for titel, zeilen in GRUPPEN:
        teile.append(f'<tr class="g"><td colspan="5">{html.escape(titel)}</td></tr>')
        teile += ["<tr>" + "".join(f"<td>{html.escape(z)}</td>" for z in r) + "</tr>" for r in zeilen]
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Schnittstellenmatrix</title><style>
@page {{ size: A4 landscape; margin: 11mm; }}
body {{ font-family: "Segoe UI", Arial, sans-serif; color: #1a1a1a; margin: 0; }}
h1 {{ background: #1f4e79; color: #fff; font-size: 19px; padding: 9px 14px; border-radius: 8px; margin: 0 0 6px; }}
p {{ font-size: 11px; margin: 0 0 7px; color: #333; }}
table {{ border-collapse: collapse; width: 100%; font-size: 10.6px; }}
th {{ background: #1f4e79; color: #fff; text-align: left; padding: 5px 6px; }}
td {{ border: 1px solid #bfbfbf; padding: 3.5px 6px; vertical-align: top; }}
tr.g td {{ background: #deebf7 !important; font-weight: 700; color: #1f4e79; font-size: 11.5px; }}
td:first-child {{ font-weight: 700; white-space: nowrap; }}
.fuss {{ font-size: 9.5px; color: #666; margin-top: 5px; }}
</style></head><body>
<h1>Schnittstellenmatrix – Sortieranlage (Team Software, Stand {STAND})</h1>
<p>Eine Zeile = eine Übergabe zwischen zwei Teilen, in zeitlicher Reihenfolge: erst die einmalige Inbetriebnahme, dann der Weg eines Klotzes (wie im Programm), dann die Anzeige.
IDs wie im Datenflussplan V4 und Netzwerkplan V2. Pin-Belegung laut Team Hardware (20.10.2026). Offen: Ventilstrom, gemeinsame Masse, Schutz Motortreiber (Team Hardware) ·
IP der Peakboard Box, Upload-Port (Team Netzwerk) · Farbwörter deutsch/englisch, Topic-Anfang (alle Teams).</p>
<table><tr>{"".join(f"<th>{html.escape(k)}</th>" for k in KOPF)}</tr>{"".join(teile)}</table>
<div class="fuss">Projektmanagement (IoT und Digitalisierung) WS 26/27 · Hochschule Niederrhein · Modernisierung fischertechnik-Sortieranlage</div>
</body></html>"""


if __name__ == "__main__":
    with open(os.path.join(HIER, "Schnittstellenmatrix.html"), "w", encoding="utf-8") as f:
        f.write(html_seite())
    with open(os.path.join(PROJ, f"Schnittstellenmatrix_{STAND.replace('.', '-')}.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(KOPF); w.writerows(ZEILEN)
    print("ok", len(ZEILEN), "Zeilen")
