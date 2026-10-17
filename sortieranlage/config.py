"""Zentrale Konfiguration der Sortierstrecke (I/O-Zuordnung, Schwellwerte, Timeouts, MQTT).

Status-Konvention: BESTÄTIGT (belegt) · VORSCHLAG (Team-Entwurf) · OFFEN (unbekannt).
Keine Zugangsdaten in dieser Datei.
"""
import os

# --- Betriebsart --------------------------------------------------------------
# "sim"      = Simulation ohne Hardware (Standard, immer gefahrlos)
# "hardware" = echte Ein-/Ausgänge über Pimoroni Automation HAT
MODUS = os.environ.get("SORTIER_MODUS", "sim")

# Sperre für Aktorik: erst auf True setzen, wenn I/O-Liste und Verdrahtung vom
# Hardware-Team bestätigt und die Kanäle unten eingetragen sind (CLAUDE.md-Regel).
HARDWARE_FREIGEGEBEN = False

# --- Hardware (laut Bestellliste 15.10.2026) -------------------------------------
# Pimoroni Automation HAT MINI: 3 digitale Eingänge, 3 Analogeingänge (0–24 V), 3 Schaltausgänge
# (sinking, bis 500 mA), 1 Relais. Förderband-Motor über Waveshare Motor Driver HAT (I2C).
HAT_TYP = "mini"              # "mini" = 1 Relais, "voll" = Automation HAT PIM213 mit 3 Relais
# Eingebauter Treiber (hat_mini.py), falls die Pimoroni-Bibliothek fehlt. BCM-Pins laut Pimoroni-Bibliothek:
# VORSCHLAG – am Testtag mit io_monitor.py prüfen (T1).
HAT_PINS = {"input": (26, 20, 21), "output": (5, 12, 6), "relay": (16,)}
ADS1015_ADRESSE = 0x48        # Analog-Digital-Wandler auf dem HAT
ANALOG_EINGANG_MAX_V = 25.85  # Messbereich der Analogeingänge (Spannungsteiler auf dem HAT)

# --- I/O-Zuordnung ------------------------------------------------------------
# Signale der Sortierstrecke: BESTÄTIGT (9V-Handbuch, Belegungsplan).
# Klemme am HAT: VORSCHLAG (Anschlussplan 15.10.2026, Excel-Blatt „LIES MICH“) – das Hardware-Team
# bestätigt oder ändert ihn beim Anschließen; Kontrolle am Testtag mit io_monitor.py (Aufgabe T1).
# Mögliche Werte: ("input", 1..3), ("analog", 1..3), ("output", 1..3), ("relay", 1 bzw. 1..3), ("motor", "A")
EINGAENGE = {
    "LS_FARBE":   {"ft": "I1", "text": "Fototransistor vor Farbsensor", "kanal": ("input", 1)},
    "LS_AUSWURF": {"ft": "I3", "text": "Fototransistor Auswurf",        "kanal": ("input", 2)},
    "IMPULS":     {"ft": "C1", "text": "Impulstaster Förderweg",        "kanal": ("input", 3)},
    "FARBSENSOR": {"ft": "I2", "text": "Farbsensor (analog)",           "kanal": ("analog", 1)},
}
AUSGAENGE = {
    "BAND":         {"ft": "M1", "text": "Förderband-Motor",    "kanal": ("motor", "A")},
    "VENTIL_WEISS": {"ft": "O5", "text": "Ventil Auswurf weiß", "kanal": ("output", 1)},
    "VENTIL_ROT":   {"ft": "O6", "text": "Ventil Auswurf rot",  "kanal": ("output", 2)},
    "VENTIL_BLAU":  {"ft": "O7", "text": "Ventil Auswurf blau", "kanal": ("output", 3)},
    "KOMPRESSOR":   {"ft": "O8", "text": "Kompressor",          "kanal": ("relay", 1)},  # Relais: höherer Strom
}

# Waveshare Motor Driver HAT (PCA9685 + TB6612FNG). Kanäle laut Waveshare-Beispielcode: VORSCHLAG,
# Drehrichtung und Geschwindigkeit OFFEN (am Testtag prüfen, Aufgabe T5).
MOTOR_I2C_BUS = 1
MOTOR_I2C_ADRESSE = 0x40
MOTOR_KANAELE = {"A": {"pwm": 0, "in1": 1, "in2": 2}, "B": {"pwm": 5, "in1": 3, "in2": 4}}
MOTOR_VORWAERTS = True        # falls das Band falsch herum läuft: False
MOTOR_GESCHWINDIGKEIT = 100   # Prozent
# Lichtschranke aktiv = unterbrochen. Pegel am HAT: OFFEN (True = Pegel 0 bedeutet unterbrochen).
LS_INVERTIERT = True

# --- Farberkennung -------------------------------------------------------------
# Startwerte aus dem Original-ROBO-Pro-Programm „Farbsortierer“ (Moodle: Sorting_Line.rpp, 15.10.2026):
# kleinster Wert der Durchfahrt; weiß < 1160 <= rot < 1500 <= blau (TXT-Rohwert, vermutlich Millivolt).
# Hier normiert: Messwert = Spannung / ANALOG_MAX_V (10 V) -> Grenzen 0,116 und 0,150.
# VORSCHLAG – am Testtag mit dem Eingangs-Monitor prüfen (Aufgabe T3).
# Messwert außerhalb aller Bereiche = keine Farbe erkannt -> Fehler "unbekannte_farbe".
FARB_BEREICHE = {
    "weiss": (0.000, 0.116),
    "rot":   (0.116, 0.150),
    "blau":  (0.150, 0.950),
}
# Messrichtung: "min" = kleinster Wert der Durchfahrt zählt (so macht es auch das Original-Programm).
FARB_MESSUNG = "min"
FARBEN = ["weiss", "rot", "blau"]
# Normierung Analogeingang: Messwert = Spannung / ANALOG_MAX_V (Messbereich des TXT: 0–10 V).
ANALOG_MAX_V = 10.0
VENTIL_JE_FARBE = {"weiss": "VENTIL_WEISS", "rot": "VENTIL_ROT", "blau": "VENTIL_BLAU"}

# Impulse ab Lichtschranke Auswurf bis Ventil – aus dem Original-ROBO-Pro-Programm (Zähler C1,
# Drücken UND Loslassen zählen). VORSCHLAG – am Testtag prüfen (Aufgabe T5).
IMPULSE_BIS_VENTIL = {"weiss": 5, "rot": 15, "blau": 26}

# Impulstaster C1 (mechanisch): Entprellung – ein neuer Pegel zählt erst, wenn er so oft
# hintereinander gelesen wurde (2 x TAKT_S = 20 ms). Welche Flanken zählen: OFFEN (nach dem Testing):
# "beide" = jedes Drücken UND Loslassen zählt, "steigend" = nur Drücken zählt.
IMPULS_STABIL_ABTASTUNGEN = 2
IMPULS_ZAEHLT = "beide"

# --- Zeiten / Timeouts (VORSCHLAG) ----------------------------------------------
TAKT_S = 0.01                 # Abtastzeit der Hauptschleife
KOMPRESSOR_VORLAUF_S = 1.0    # Druckaufbau vor dem Ausschleusen
VENTIL_PULS_S = 0.5           # Ventil-Öffnungszeit (wie im Original-ROBO-Pro-Programm)
TIMEOUT_BIS_AUSWURF_S = 10.0  # Farbsensor -> Lichtschranke Auswurf
TIMEOUT_IMPULS_S = 2.0        # kein Impuls trotz laufendem Band = Band blockiert
TIMEOUT_LEERLAUF_S = 30.0     # nach so langer Zeit ohne Werkstück: Status "bereit"

# --- MQTT (Topics VORSCHLAG, noch im Team abzustimmen) ----------------------------
MQTT_HOST = os.environ.get("SORTIER_MQTT_HOST", "localhost")  # Broker auf dem Pi (VORSCHLAG)
MQTT_PORT = int(os.environ.get("SORTIER_MQTT_PORT", "1883"))
MQTT_CLIENT_ID = "sortieranlage-pi"
MQTT_PUFFER = 1000            # max. wartende Nachrichten, wenn der Broker nicht erreichbar ist
TOPIC_BASIS = os.environ.get("SORTIER_TOPIC_BASIS", "sortieranlage")
# Broker-Anmeldung (Mosquitto auf dem Pi verlangt Benutzer/Passwort, BESTÄTIGT 16.10.2026).
# Zugangsdaten stehen NIE im Projektordner: Umgebungsvariablen SORTIER_MQTT_USER / SORTIER_MQTT_PASS
# oder Datei auf dem Pi (Zeile 1 Benutzer, Zeile 2 Passwort, nur für den Besitzer lesbar; legt PI_EINRICHTEN an).
MQTT_ZUGANG_DATEI = os.environ.get("SORTIER_MQTT_ZUGANG", os.path.expanduser("~/.sortieranlage_mqtt"))


def mqtt_zugang():
    """(benutzer, passwort) oder (None, None) für anonyme Verbindung."""
    benutzer, passwort = os.environ.get("SORTIER_MQTT_USER"), os.environ.get("SORTIER_MQTT_PASS")
    if not benutzer:
        try:
            with open(MQTT_ZUGANG_DATEI, encoding="utf-8") as f:
                zeilen = [z.strip() for z in f.read().splitlines() if z.strip()]
            benutzer = zeilen[0] if zeilen else None
            passwort = zeilen[1] if len(zeilen) > 1 else None
        except OSError:
            pass
    if not benutzer:                     # Laptop: .env im Projektordner (Testaufbau, siehe .env)
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, ".env"), encoding="utf-8") as f:
                werte = dict(z.split("=", 1) for z in (z.strip() for z in f) if "=" in z and not z.startswith("#"))
            benutzer, passwort = werte.get("SORTIER_MQTT_USER", "").strip(), werte.get("SORTIER_MQTT_PASS", "").strip()
        except OSError:
            pass
    return (benutzer or None), (passwort if benutzer else None)


def topics_setzen(basis):
    """JSON-Topics (VORSCHLAG Anhang 7 / peakboard/MQTT_Schnittstelle.md) + einfache Einzelwerte für Peakboard."""
    global TOPIC_BASIS, TOPICS
    TOPIC_BASIS = basis
    TOPICS = {
        "status":       basis + "/status",
        "zyklen":       basis + "/zyklen",
        "farbe_letzte": basis + "/farbe/letzte",
        "farbe_anzahl": basis + "/farbe/anzahl",
        "fehler":       basis + "/fehler",
        "wert":         basis + "/wert/",      # + Name, z. B. sortieranlage/wert/zyklen = "12" (ohne JSON)
        "event":        basis + "/event",      # Ereignis wie im Kursbeispiel (Moodle-Folien „HSNR MQTT Raspberry Peakboard“)
    }


topics_setzen(TOPIC_BASIS)

LOGDATEI = os.environ.get("SORTIER_LOG", "log.txt")


def fehlende_kanaele():
    """Liste der Signale ohne eingetragenen HAT-Kanal."""
    return [n for n, e in {**EINGAENGE, **AUSGAENGE}.items() if e["kanal"] is None]


def anschluss_pruefen():
    """Liste von Problemen in der I/O-Zuordnung (leer = in Ordnung)."""
    probleme = [f"{n}: Kanal fehlt" for n in fehlende_kanaele()]
    grenzen = {"input": 3, "analog": 3, "output": 3, "relay": 1 if HAT_TYP == "mini" else 3}
    belegt = {}
    for n, e in {**EINGAENGE, **AUSGAENGE}.items():
        k = e["kanal"]
        if k is None:
            continue
        art, nr = k
        if art == "motor":
            if nr not in MOTOR_KANAELE:
                probleme.append(f"{n}: Motorkanal {nr} unbekannt")
        elif art not in grenzen or not 1 <= nr <= grenzen[art]:
            probleme.append(f"{n}: {art} {nr} gibt es am HAT ({HAT_TYP}) nicht")
        if k in belegt:
            probleme.append(f"{n}: {art} {nr} schon belegt durch {belegt[k]}")
        belegt[k] = n
    return probleme
