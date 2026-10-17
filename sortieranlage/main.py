"""Start der Sortierstrecken-Steuerung.

Beispiele:
  python3 main.py                                  # Simulation: weiß, rot, blau (schnell)
  python3 main.py --farben weiss,rot,blau,rot --fehler band_blockiert
  python3 main.py --dauer --echtzeit               # Dauer-Simulation für den Peakboard-Aufbau
  python3 main.py --kein-mqtt                      # ohne Broker
  python3 main.py --modus hardware                 # nur nach Freigabe in config.py
"""
import argparse
import logging
import random
import signal
import sys
import time
from logging.handlers import RotatingFileHandler

import config

log = logging.getLogger("main")


def argumente(argv=None):
    p = argparse.ArgumentParser(description="Steuerung fischertechnik-Sortierstrecke (Raspberry Pi)")
    p.add_argument("--modus", choices=["sim", "hardware"], default=config.MODUS)
    p.add_argument("--farben", default="weiss,rot,blau", help="Simulation: Werkstückfolge")
    p.add_argument("--fehler", choices=["band_blockiert", "unbekannte_farbe"],
                   help="Simulation: Fehlerfall beim 2. Werkstück einbauen")
    p.add_argument("--prellen", action="store_true", help="Simulation: Impulstaster prellt (Test der Entprellung)")
    p.add_argument("--dauer", action="store_true", help="Simulation: endlos zufällige Werkstücke")
    p.add_argument("--fehler-alle", type=int, help="Simulation: Fehler bei jedem n-ten Werkstück (mit --fehler)")
    p.add_argument("--echtzeit", action="store_true", help="Simulation in Echtzeit statt im Zeitraffer")
    p.add_argument("--mqtt-host", default=config.MQTT_HOST)
    p.add_argument("--mqtt-port", type=int, default=config.MQTT_PORT)
    p.add_argument("--kein-mqtt", action="store_true")
    p.add_argument("--topic-basis", default=config.TOPIC_BASIS,
                   help="Anfang aller Topics (Standard: sortieranlage; für öffentliche Test-Broker eindeutig wählen)")
    p.add_argument("--debug", action="store_true")
    return p.parse_args(argv)


def logging_einrichten(debug):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)-8s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout),
                                  RotatingFileHandler(config.LOGDATEI, maxBytes=2_000_000,
                                                      backupCount=3, encoding="utf-8")])


def starten(a):
    """Baut Prozess, Ein-/Ausgänge und MQTT auf. Gibt (prozess, anlage|None, pub, aus) zurück."""
    from mqtt_client import MqttPublisher, PeakboardMelder
    from process import Sortierprozess

    config.MODUS = a.modus
    config.topics_setzen(a.topic_basis)
    pub = MqttPublisher(a.mqtt_host, a.mqtt_port, aktiv=not a.kein_mqtt)
    melder = PeakboardMelder(pub)

    if a.modus == "sim":
        from inputs import SimEingaenge
        from outputs import SimAusgaenge
        from simulation import SimAnlage
        farben = [f.strip() for f in a.farben.split(",") if f.strip()]
        anlage = SimAnlage(farben, fehler=a.fehler, prellen=a.prellen, fehler_alle=a.fehler_alle)
        ein, aus = SimEingaenge(anlage), SimAusgaenge(anlage)
    else:
        from inputs import HatEingaenge
        from outputs import HatAusgaenge
        anlage = None
        ein, aus = HatEingaenge(), HatAusgaenge()

    prozess = Sortierprozess(ein, aus, melde=melder)
    melder.startwerte(prozess.snapshot())
    return prozess, anlage, pub, aus


def lauf(a):
    prozess, anlage, pub, aus = starten(a)
    stopp = {"ja": False}

    def beenden(*_):
        stopp["ja"] = True
    signal.signal(signal.SIGTERM, beenden)

    jetzt, t_fehler = 0.0, None
    rng = random.Random()
    try:
        while not stopp["ja"]:
            if anlage is not None:
                jetzt += config.TAKT_S
                anlage.schritt(config.TAKT_S)
                if prozess.zustand == "FEHLER":       # Sim: Bediener entnimmt Werkstück nach 3 s
                    t_fehler = jetzt if t_fehler is None else t_fehler
                    if jetzt - t_fehler > 3.0:
                        anlage.werkstueck = None
                        prozess.quittieren(jetzt)
                        t_fehler = None
                fertig = (not anlage.warteschlange and anlage.werkstueck is None
                          and prozess.zustand == "BEREIT")
                if fertig and a.dauer:
                    anlage.warteschlange.append(rng.choice(config.FARBEN))
                elif fertig or jetzt > 600:
                    break
                if a.echtzeit:
                    time.sleep(config.TAKT_S)
            else:
                jetzt = time.monotonic()
                time.sleep(config.TAKT_S)
            prozess.schritt(jetzt)
            pub.am_leben_halten()
    except KeyboardInterrupt:
        pass
    finally:
        aus.alle_aus()
        prozess.melde("status", dict(prozess.snapshot(), zustand="AUS"))
        pub.trennen()
    return prozess, anlage, pub


def main(argv=None):
    a = argumente(argv)
    logging_einrichten(a.debug)
    log.info("Start Modus=%s MQTT=%s", a.modus, "aus" if a.kein_mqtt else "%s:%d" % (a.mqtt_host, a.mqtt_port))
    try:
        prozess, anlage, pub = lauf(a)
    except RuntimeError as e:
        log.error("%s", e)
        return 2
    log.info("Ende: %s", prozess.snapshot())
    if anlage is not None:
        log.info("Sim: richtig ausgeschleust=%s falsch=%s", anlage.ausgeschleust, anlage.falsch)
    log.info("MQTT-Nachrichten gesendet: %d", pub.gesendet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
