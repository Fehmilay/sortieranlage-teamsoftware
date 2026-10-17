"""Zustandslogik der Sortierstrecke (ohne direkten Hardwarezugriff).

Ablauf (BESTÄTIGT, 9V-Handbuch): Werkstück unterbricht Lichtschranke I1 -> Band startet ->
Farbsensor misst -> Farbe über Schwellwert -> ab Lichtschranke I3 zählt Impulstaster C1 bis
zur Zielposition -> Ventil der Farbe schiebt Werkstück auf die Rutsche.
"""
import logging

import config

log = logging.getLogger("process")

BEREIT, FOERDERN, ZAEHLEN, AUSSCHLEUSEN, PRUEFEN, FEHLER = (
    "BEREIT", "FOERDERN", "ZAEHLEN", "AUSSCHLEUSEN", "PRUEFEN", "FEHLER")


def farbe_aus_wert(wert):
    for farbe, (von, bis) in config.FARB_BEREICHE.items():
        if von <= wert < bis:
            return farbe
    return None


class Sortierprozess:
    def __init__(self, ein, aus, melde=lambda art, daten: None):
        self.ein, self.aus, self.melde = ein, aus, melde
        self.zustand = None
        self.zyklen = 0
        self.anzahl = {f: 0 for f in config.FARBEN}
        self.letzte_farbe = None
        self.fehler_anzahl = 0
        self.letzter_fehler = None
        self._wechsel(BEREIT, 0.0)

    # --- Hilfen ---
    def _wechsel(self, neu, jetzt):
        if neu != self.zustand:
            log.info("Zustand %s -> %s", self.zustand, neu)
            self.zustand = neu
            self.t_zustand = jetzt
            self.melde("status", self.snapshot())

    def _fehler(self, code, text, jetzt):
        self.aus.alle_aus()
        self.fehler_anzahl += 1
        self.letzter_fehler = {"code": code, "text": text, "zustand": self.zustand,
                               "zyklus": self.zyklen + 1}
        log.error("FEHLER %s: %s", code, text)
        self._wechsel(FEHLER, jetzt)
        self.melde("fehler", dict(self.letzter_fehler, anzahl=self.fehler_anzahl))

    def snapshot(self):
        return {"zustand": self.zustand, "zyklen": self.zyklen, "farbe_letzte": self.letzte_farbe,
                "anzahl": dict(self.anzahl), "fehler_anzahl": self.fehler_anzahl,
                "modus": config.MODUS}

    def quittieren(self, jetzt):
        """Fehler zurücksetzen (Werkstück wurde vom Bediener entnommen)."""
        if self.zustand == FEHLER:
            self.aus.alle_aus()
            self._wechsel(BEREIT, jetzt)
            self.melde("fehler", {"code": None, "text": "quittiert", "anzahl": self.fehler_anzahl})

    def _impuls_flanke(self, jetzt):
        """True, wenn ein (entprellter) Impuls am Taster C1 gezählt werden soll."""
        i = self.ein.lese("IMPULS")
        if i == self.impuls_alt:
            self.impuls_kandidat = 0
            return False
        self.impuls_kandidat += 1                      # neuer Pegel muss stabil anliegen
        if self.impuls_kandidat < config.IMPULS_STABIL_ABTASTUNGEN:
            return False
        self.impuls_kandidat = 0
        self.impuls_alt = i
        self.t_impuls = jetzt                          # Band bewegt sich (Wächter "band_blockiert")
        return config.IMPULS_ZAEHLT == "beide" or bool(i)

    # --- Hauptschritt, zyklisch aufrufen ---
    def schritt(self, jetzt):
        z = self.zustand
        if z == BEREIT:
            if self.ein.lese("LS_FARBE"):
                self.messwert = None
                self.impuls_alt = self.ein.lese("IMPULS")
                self.impuls_kandidat = 0
                self.t_impuls = jetzt
                self.aus.setze("BAND", True)
                self._wechsel(FOERDERN, jetzt)

        elif z == FOERDERN:
            wert = self.ein.lese("FARBSENSOR")
            if self.messwert is None:
                self.messwert = wert
            else:
                self.messwert = (min if config.FARB_MESSUNG == "min" else max)(self.messwert, wert)
            self._impuls_flanke(jetzt)
            if self.ein.lese("LS_AUSWURF"):
                farbe = farbe_aus_wert(self.messwert)
                if farbe is None:
                    return self._fehler("unbekannte_farbe",
                                        "Farbe nicht erkannt (Messwert %.2f)" % self.messwert, jetzt)
                self.farbe = farbe
                self.impulse = 0
                # Ein Pegelwechsel, der gerade noch entprellt wird, gehört zur Ankunft an I3 -> nicht zählen
                self.ignoriere_flanke = self.impuls_kandidat > 0
                log.info("Farbe %s (Messwert %.2f)", farbe, self.messwert)
                self.aus.setze("KOMPRESSOR", True)   # Druckaufbau während der Restfahrt
                self.t_kompressor = jetzt
                self._wechsel(ZAEHLEN, jetzt)
            elif jetzt - self.t_impuls > config.TIMEOUT_IMPULS_S:
                self._fehler("band_blockiert", "Kein Impuls am Taster C1 trotz laufendem Band", jetzt)
            elif jetzt - self.t_zustand > config.TIMEOUT_BIS_AUSWURF_S:
                self._fehler("timeout_auswurf", "Lichtschranke Auswurf nicht erreicht", jetzt)

        elif z == ZAEHLEN:
            if self._impuls_flanke(jetzt):
                if self.ignoriere_flanke:
                    self.ignoriere_flanke = False
                else:
                    self.impulse += 1
            if self.impulse >= config.IMPULSE_BIS_VENTIL[self.farbe]:
                self.aus.setze("BAND", False)
                self._wechsel(AUSSCHLEUSEN, jetzt)
            elif jetzt - self.t_impuls > config.TIMEOUT_IMPULS_S:
                self._fehler("band_blockiert", "Kein Impuls am Taster C1 trotz laufendem Band", jetzt)

        elif z == AUSSCHLEUSEN:
            ventil = config.VENTIL_JE_FARBE[self.farbe]
            if jetzt - self.t_kompressor < config.KOMPRESSOR_VORLAUF_S:
                return
            if not self.aus.zustand[ventil]:
                self.aus.setze(ventil, True)
                self.t_ventil = jetzt
            elif jetzt - self.t_ventil >= config.VENTIL_PULS_S:
                self.aus.setze(ventil, False)
                self.aus.setze("KOMPRESSOR", False)
                self._wechsel(PRUEFEN, jetzt)

        elif z == PRUEFEN:
            # Werkstück-Ausgang prüfen: Auswurf-Lichtschranke muss frei sein.
            # (Lagerstellen I6–I8 laut Auftrag zunächst nicht im Umfang.)
            if self.ein.lese("LS_AUSWURF"):
                if jetzt - self.t_zustand > 1.0:
                    self._fehler("auswurf_nicht_frei", "Werkstück nach dem Ausschleusen noch erkannt", jetzt)
                return
            self.zyklen += 1
            self.anzahl[self.farbe] += 1
            self.letzte_farbe = self.farbe
            log.info("Zyklus %d fertig: %s", self.zyklen, self.farbe)
            self.melde("zyklus", self.snapshot())
            self._wechsel(BEREIT, jetzt)
