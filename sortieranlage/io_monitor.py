"""Eingangs-Monitor für den Testtag: zeigt ALLE Eingänge des Automation HAT live an. Schaltet NICHTS.

Auf dem Pi:   python3 io_monitor.py                 # Anzeige, Beenden mit Strg+C
              python3 io_monitor.py --csv messung.csv --dauer 60
Ohne HAT:     python3 io_monitor.py --demo          # nur zum Ausprobieren am Laptop

Wofür (Arbeitsaufträge „nach dem Testing“):
- Welcher Draht hängt an welcher Klemme?  -> Lichtschranke abdecken und schauen, welcher Eingang wechselt.
- Pegel frei / unterbrochen               -> config.LS_INVERTIERT
- Farbsensor: Wert leeres Band, weiß, rot, blau (min/max je Durchlauf) -> config.FARB_BEREICHE, FARB_MESSUNG, ANALOG_MAX_V
- Impulstaster: Flanken pro Sekunde bei laufendem Band   -> Entprellung / IMPULS_ZAEHLT
"""
import argparse
import csv
import random
import sys
import time

KANAELE_DIGITAL = ("one", "two", "three")
KANAELE_ANALOG = ("one", "two", "three")


class DemoHat:
    """Ersatz ohne Hardware: wackelnde Werte, damit die Anzeige getestet werden kann."""

    class _K:
        def __init__(self, f):
            self.read = f

    def __init__(self):
        t0 = time.monotonic()
        takt = lambda p: int((time.monotonic() - t0) / p) % 2
        self.input = type("I", (), {k: self._K(lambda p=p: takt(p)) for k, p in zip(KANAELE_DIGITAL, (2.0, 3.0, 0.1))})()
        self.analog = type("A", (), {k: self._K(lambda: round(random.uniform(1.0, 8.0), 2)) for k in KANAELE_ANALOG})()


def main():
    p = argparse.ArgumentParser(description="Eingangs-Monitor (nur lesen)")
    p.add_argument("--demo", action="store_true", help="ohne HAT mit Zufallswerten")
    p.add_argument("--csv", help="Messwerte zusätzlich in diese CSV-Datei schreiben")
    p.add_argument("--dauer", type=float, default=0, help="nach so vielen Sekunden beenden (0 = endlos)")
    p.add_argument("--takt", type=float, default=0.005, help="Abtastzeit in s (Standard 5 ms)")
    a = p.parse_args()

    if a.demo:
        hat = DemoHat()
    else:
        try:
            from hat_mini import lade_hat   # Pimoroni-Bibliothek oder eingebauter Treiber
            hat = lade_hat()
        except Exception as e:
            print("HAT nicht ansprechbar:", e)
            print("-> Ist der HAT aufgesteckt und I2C eingeschaltet? (PI_EINRICHTEN.bat ausführen)")
            return 2

    dig = {f"IN{i}": getattr(hat.input, k) for i, k in enumerate(KANAELE_DIGITAL, 1)}
    ana = {f"A{i}": getattr(hat.analog, k) for i, k in enumerate(KANAELE_ANALOG, 1)}
    alt = {n: k.read() for n, k in dig.items()}
    flanken = {n: 0 for n in dig}
    mini = {n: 99.0 for n in ana}
    maxi = {n: -99.0 for n in ana}
    schreiber = None
    if a.csv:
        datei = open(a.csv, "w", newline="", encoding="utf-8")
        schreiber = csv.writer(datei, delimiter=";")
        schreiber.writerow(["zeit_s"] + list(dig) + list(ana))

    print("Eingangs-Monitor – schaltet nichts. Strg+C beendet. (IN = digital 0/1, A = Spannung in V)")
    t0 = t_anzeige = time.monotonic()
    try:
        while not a.dauer or time.monotonic() - t0 < a.dauer:
            werte_d = {n: k.read() for n, k in dig.items()}
            for n, w in werte_d.items():
                if w != alt[n]:
                    flanken[n] += 1
                    alt[n] = w
            jetzt = time.monotonic()
            if jetzt - t_anzeige >= 0.25:
                werte_a = {n: k.read() for n, k in ana.items()}
                for n, w in werte_a.items():
                    mini[n], maxi[n] = min(mini[n], w), max(maxi[n], w)
                dt = jetzt - t_anzeige
                zeile = "  ".join(f"{n}={w}" for n, w in werte_d.items())
                zeile += "  |  " + "  ".join(f"{n}={w:5.2f}V ({mini[n]:.2f}..{maxi[n]:.2f})" for n, w in werte_a.items())
                zeile += "  |  Flanken/s " + " ".join(f"{n}:{flanken[n] / dt:4.1f}" for n in dig)
                print("\r" + zeile, end="", flush=True)
                if schreiber:
                    schreiber.writerow([f"{jetzt - t0:.2f}"] + list(werte_d.values()) + [f"{w:.3f}" for w in werte_a.values()])
                flanken = {n: 0 for n in dig}
                t_anzeige = jetzt
            time.sleep(a.takt)
    except KeyboardInterrupt:
        pass
    print("\nMin/Max der Analogeingänge:", {n: (round(mini[n], 2), round(maxi[n], 2)) for n in ana})
    if schreiber:
        datei.close()
        print("CSV gespeichert:", a.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
