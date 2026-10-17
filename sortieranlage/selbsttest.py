"""Selbsttest ohne Hardware und ohne Broker: python3 selbsttest.py  (Exitcode 0 = alles OK)

Prüft die Abnahmeszenarien in der Simulation: mehrere Zyklen mit verschiedenen Farben und
definierte Fehlerfälle.
"""
import logging
import sys

import config
config.LOGDATEI = "selbsttest_log.txt"

import main  # noqa: E402

FAELLE = [
    ("3 Farben",            "weiss,rot,blau",       None,               3, 0),
    ("6 gemischt",          "blau,blau,rot,weiss,rot,weiss", None,      6, 0),
    ("Fehler Band blockiert", "weiss,rot,blau",     "band_blockiert",   2, 1),
    ("Fehler unbek. Farbe", "weiss,rot,blau",       "unbekannte_farbe", 2, 1),
    ("Taster prellt",       "weiss,rot,blau,blau",  "prellen",          4, 0),
]


def pruefen():
    ok = True
    for name, farben, fehler, soll_zyklen, soll_fehler in FAELLE:
        argv = ["--kein-mqtt", "--farben", farben]
        if fehler == "prellen":
            argv.append("--prellen")
        elif fehler:
            argv += ["--fehler", fehler]
        prozess, anlage, _ = main.lauf(main.argumente(argv))
        s = prozess.snapshot()
        erfolg = (s["zyklen"] == soll_zyklen and s["fehler_anzahl"] == soll_fehler
                  and not anlage.falsch and len(anlage.ausgeschleust) == soll_zyklen)
        ok &= erfolg
        print("%-24s %s  Zyklen=%d Fehler=%d Anzahl=%s falsch=%s" % (
            name, "OK  " if erfolg else "FEHL", s["zyklen"], s["fehler_anzahl"], s["anzahl"], anlage.falsch))
    return ok


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s %(message)s")
    ergebnis = pruefen()
    print("SELBSTTEST", "BESTANDEN" if ergebnis else "NICHT BESTANDEN")
    sys.exit(0 if ergebnis else 1)
