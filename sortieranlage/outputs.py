"""Aktoren schalten. Einheitliche Schnittstelle: setze(name, an), alle_aus().

9-V-Aktoren werden NIE direkt an GPIOs geschaltet, sondern nur über HAT-Relais/-Ausgänge bzw.
den Motor Driver HAT.
"""
import logging

import config

log = logging.getLogger("outputs")
NAMEN = {1: "one", 2: "two", 3: "three"}     # Kanalnamen der automationhat-Bibliothek


class SimAusgaenge:
    def __init__(self, anlage):
        self.anlage = anlage
        self.zustand = {n: False for n in config.AUSGAENGE}

    def setze(self, name, an):
        if self.zustand[name] != an:
            log.debug("SIM %s (%s) -> %s", name, config.AUSGAENGE[name]["ft"], "AN" if an else "AUS")
        self.zustand[name] = an
        self.anlage.setze(name, an)

    def alle_aus(self):
        for n in self.zustand:
            self.setze(n, False)


class HatAusgaenge:
    """Automation HAT (Mini) für Ventile/Kompressor, Waveshare Motor Driver HAT für das Band."""

    def __init__(self):
        if not config.HARDWARE_FREIGEGEBEN:
            raise RuntimeError("Aktorik gesperrt: config.HARDWARE_FREIGEGEBEN = False "
                               "(erst I/O-Liste und Verdrahtung bestätigen).")
        probleme = config.anschluss_pruefen()
        if probleme:
            raise RuntimeError("I/O-Zuordnung fehlerhaft: " + "; ".join(probleme))
        self.zustand = {n: False for n in config.AUSGAENGE}
        self.hat, self.motoren = None, {}
        for name, e in config.AUSGAENGE.items():
            art, nr = e["kanal"]
            if art == "motor":
                from motor_hat import MotorHat
                self.motoren[name] = MotorHat(nr)
            elif self.hat is None:
                from hat_mini import lade_hat   # Pimoroni-Bibliothek oder eingebauter Treiber
                self.hat = lade_hat()
        self.alle_aus()

    def setze(self, name, an):
        art, nr = config.AUSGAENGE[name]["kanal"]
        if art == "motor":
            m = self.motoren[name]
            m.an() if an else m.stopp()
        else:
            k = getattr({"relay": self.hat.relay, "output": self.hat.output}[art], NAMEN[nr])
            k.on() if an else k.off()
        if self.zustand.get(name) != an:
            log.info("HW %s (%s) -> %s", name, config.AUSGAENGE[name]["ft"], "AN" if an else "AUS")
        self.zustand[name] = an

    def alle_aus(self):
        for n in config.AUSGAENGE:
            try:
                self.setze(n, False)
            except Exception:  # beim Not-Aus nie abbrechen
                log.exception("Abschalten von %s fehlgeschlagen", n)
