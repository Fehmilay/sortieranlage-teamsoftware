"""Simulierte Sortierstrecke: liefert Sensorwerte passend zu den Aktorbefehlen.

Damit lässt sich die komplette Prozesslogik inkl. MQTT/Peakboard ohne Anlage testen.
Modell (vereinfacht): Werkstück liegt am Bandanfang; läuft das Band, wandert es
in Schritten (= Impulse am Taster C1) Richtung Auswurf.
"""
import random

import config

POS_LS_FARBE = 0        # Werkstück eingelegt = Lichtschranke vor Farbsensor unterbrochen
POS_SENSOR = (2, 4)     # Bereich unter dem Farbsensor
POS_LS_AUSWURF = 8      # Lichtschranke vor dem ersten Auswurf
SCHRITT_S = 0.15        # Zeit je Impuls bei laufendem Band (simuliert)

# normierte Messwerte je Farbe (liegen mittig in config.FARB_BEREICHE; Rauschen ± RAUSCHEN)
FARBWERT = {"weiss": 0.09, "rot": 0.133, "blau": 0.20}
RAUSCHEN = 0.008


class SimAnlage:
    def __init__(self, farben, fehler=None, seed=1, prellen=False, fehler_alle=None):
        self.warteschlange = list(farben)   # noch einzulegende Werkstücke
        self.fehler = fehler                # None | "band_blockiert" | "unbekannte_farbe"
        self.prellen = prellen              # Impulstaster prellt: kurzer Rücksprung nach jedem Wechsel
        self.fehler_alle = fehler_alle      # Fehler bei jedem n-ten Werkstück statt nur beim 2. (Testdaten für Peakboard)
        self.prell = 0
        self.rng = random.Random(seed)
        self.werkstueck = None              # {"farbe", "pos"}
        self.zeit_im_schritt = 0.0
        self.impuls = False
        self.ausgaenge = {n: False for n in config.AUSGAENGE}
        self.ausgeschleust = []             # Farben, die im richtigen Fach gelandet sind
        self.falsch = []
        self._naechstes_einlegen()

    def _naechstes_einlegen(self):
        if self.warteschlange and self.werkstueck is None:
            self.werkstueck = {"farbe": self.warteschlange.pop(0), "pos": POS_LS_FARBE}
            self.nr = getattr(self, "nr", 0) + 1

    def _fehler_dran(self):
        return self.nr % self.fehler_alle == 0 if self.fehler_alle else self.nr == 2

    # --- Schnittstelle für outputs.SimAusgaenge ---
    def setze(self, name, wert):
        if wert and not self.ausgaenge[name] and name.startswith("VENTIL"):
            self._ventil_auf(name)
        self.ausgaenge[name] = wert

    def _ventil_auf(self, name):
        w = self.werkstueck
        if w is None or not self.ausgaenge["KOMPRESSOR"]:
            return
        ziel = config.VENTIL_JE_FARBE.get(w["farbe"])
        soll_pos = POS_LS_AUSWURF + config.IMPULSE_BIS_VENTIL.get(w["farbe"], -99)
        if name == ziel and w["pos"] == soll_pos:
            self.ausgeschleust.append(w["farbe"])
        else:
            self.falsch.append((w["farbe"], name, w["pos"]))
        self.werkstueck = None

    # --- Zeitfortschritt ---
    def schritt(self, dt):
        w = self.werkstueck
        if w is None:
            self._naechstes_einlegen()
            return
        blockiert = self.fehler == "band_blockiert" and self._fehler_dran() and w["pos"] >= 5
        if self.ausgaenge["BAND"] and not blockiert:
            self.zeit_im_schritt += dt
            if self.zeit_im_schritt >= SCHRITT_S:
                self.zeit_im_schritt = 0.0
                w["pos"] += 1
                self.impuls = not self.impuls
                self.prell = 2 if self.prellen else 0
                if w["pos"] > POS_LS_AUSWURF + 40:   # vom Band gefallen
                    self.falsch.append((w["farbe"], "bandende", w["pos"]))
                    self.werkstueck = None

    # --- Schnittstelle für inputs.SimEingaenge ---
    def lese(self, name):
        w = self.werkstueck
        if name == "LS_FARBE":
            return w is not None and w["pos"] == POS_LS_FARBE
        if name == "LS_AUSWURF":
            return w is not None and w["pos"] == POS_LS_AUSWURF
        if name == "IMPULS":
            if self.prell:                  # Lesefolge nach Wechsel: neu, alt (Prellen), neu ...
                self.prell -= 1
                return self.impuls if self.prell else not self.impuls
            return self.impuls
        if name == "FARBSENSOR":
            if w is not None and POS_SENSOR[0] <= w["pos"] <= POS_SENSOR[1]:
                if self.fehler == "unbekannte_farbe" and self._fehler_dran():
                    return 0.97
                return FARBWERT[w["farbe"]] + self.rng.uniform(-RAUSCHEN, RAUSCHEN)
            return 1.0   # kein Werkstück = keine Reflexion
        raise KeyError(name)
