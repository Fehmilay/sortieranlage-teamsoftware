"""Sensoren lesen. Einheitliche Schnittstelle: lese(name) -> bool bzw. float (0..1 für FARBSENSOR)."""
import config


class SimEingaenge:
    def __init__(self, anlage):
        self.anlage = anlage

    def lese(self, name):
        return self.anlage.lese(name)


class HatEingaenge:
    """Pimoroni Automation HAT (Mini). Bibliothek: automationhat."""

    NAMEN = {1: "one", 2: "two", 3: "three"}

    def __init__(self):
        probleme = [p for p in config.anschluss_pruefen()
                    if p.split(":")[0] in config.EINGAENGE]
        if probleme:
            raise RuntimeError("I/O-Zuordnung der Eingänge fehlerhaft: " + "; ".join(probleme))
        from hat_mini import lade_hat   # Pimoroni-Bibliothek oder eingebauter Treiber
        self.hat = lade_hat()

    def _kanal(self, name):
        art, nr = config.EINGAENGE[name]["kanal"]
        gruppe = {"input": self.hat.input, "analog": self.hat.analog}[art]
        return art, getattr(gruppe, self.NAMEN[nr])

    def lese(self, name):
        art, k = self._kanal(name)
        if art == "analog":
            return min(1.0, max(0.0, k.read() / config.ANALOG_MAX_V))
        wert = bool(k.read())
        if name.startswith("LS_") and config.LS_INVERTIERT:
            wert = not wert
        return wert
