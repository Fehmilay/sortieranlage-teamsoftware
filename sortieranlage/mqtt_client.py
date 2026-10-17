"""MQTT-Veröffentlichung der Prozessdaten für die Peakboard Box.

Eigene Minimal-Implementierung (MQTT 3.1.1, QoS 0, retain) nur mit der Python-Standardbibliothek,
damit auf dem Pi im lokalen Netz OHNE Internet nichts per pip installiert werden muss.
Gesendet wird in einem Hintergrund-Thread: Die Steuerschleife legt Nachrichten nur in eine
Warteschlange und wird von Verbindungsproblemen nie aufgehalten (Steuerung und Visualisierung getrennt).
"""
import json
import logging
import queue
import select
import socket
import struct
import threading
import time
from datetime import datetime, timezone

import config

log = logging.getLogger("mqtt")


def _str(s):
    b = s.encode("utf-8")
    return struct.pack("!H", len(b)) + b


def _paket(kopf, inhalt):
    laenge, n = b"", len(inhalt)
    while True:
        byte, n = n % 128, n // 128
        laenge += bytes([byte | (0x80 if n else 0)])
        if not n:
            return bytes([kopf]) + laenge + inhalt


def _connect(client_id, keepalive, benutzer=None, passwort=None):
    """CONNECT-Paket (MQTT 3.1.1, Clean Session, optional mit Benutzer/Passwort)."""
    flags, nutz = 0x02, _str(client_id)
    if benutzer:
        flags |= 0x80
        nutz += _str(benutzer)
        if passwort is not None:
            flags |= 0x40
            nutz += _str(passwort)
    return _paket(0x10, _str("MQTT") + bytes([4, flags]) + struct.pack("!H", keepalive) + nutz)


class MqttPublisher:
    def __init__(self, host=config.MQTT_HOST, port=config.MQTT_PORT, client_id=config.MQTT_CLIENT_ID,
                 keepalive=30, aktiv=True, benutzer=None, passwort=None):
        self.host, self.port, self.client_id, self.keepalive = host, port, client_id, keepalive
        if benutzer is None:
            benutzer, passwort = config.mqtt_zugang()
        self.benutzer, self.passwort = benutzer, passwort
        self.aktiv = aktiv
        self.sock = None
        self.t_gesendet = 0.0
        self.gesendet = 0
        self.verworfen = 0
        self._schlange = queue.Queue(maxsize=config.MQTT_PUFFER)
        self._stopp = threading.Event()
        self._thread = None
        if aktiv:
            self._thread = threading.Thread(target=self._lauf, name="mqtt", daemon=True)
            self._thread.start()

    # --- Aufrufe aus der Steuerschleife (blockieren nie) ---
    def senden(self, topic, daten, retain=True):
        """daten: dict -> JSON (mit Zeitstempel), str -> Text unverändert.
        Gibt True zurück, wenn die Nachricht zum Senden eingereiht wurde."""
        if isinstance(daten, str):
            nutz = daten.encode("utf-8")
        else:
            nutz = json.dumps(dict(daten, zeit=datetime.now().isoformat(timespec="seconds")),
                              ensure_ascii=False).encode("utf-8")
        log.debug("PUB %s %s", topic, nutz.decode("utf-8"))
        if not self.aktiv:
            return False
        try:
            self._schlange.put_nowait((topic, nutz, retain))
            return True
        except queue.Full:
            self.verworfen += 1
            if self.verworfen % 100 == 1:
                log.warning("MQTT-Warteschlange voll – Nachrichten werden verworfen (%d)", self.verworfen)
            return False

    def am_leben_halten(self):
        """Nur noch aus Kompatibilität: Keepalive erledigt der Hintergrund-Thread."""

    def trennen(self, warten_s=2.0):
        """Restliche Nachrichten noch bis zu warten_s senden, dann sauber trennen."""
        if self._thread:
            self._stopp.set()
            self._thread.join(warten_s)

    # --- Hintergrund-Thread ---
    def _verbinden(self):
        try:
            s = socket.create_connection((self.host, self.port), timeout=2)
            s.sendall(_connect(self.client_id, self.keepalive, self.benutzer, self.passwort))
            antwort = s.recv(4)
            if len(antwort) < 4 or antwort[0] != 0x20 or antwort[3] != 0:
                s.close()
                raise ConnectionError("CONNACK abgelehnt: %r (Code 4 = Benutzer/Passwort falsch, Code 5 = Login nötig)" % antwort)
            self.sock = s
            self.t_gesendet = time.monotonic()
            log.info("MQTT verbunden mit %s:%d (%s)", self.host, self.port,
                     "Benutzer " + self.benutzer if self.benutzer else "anonym")
            return True
        except OSError as e:
            log.warning("MQTT nicht erreichbar (%s:%d): %s – neuer Versuch in 5 s", self.host, self.port, e)
            self.sock = None
            return False

    def _socket_zu(self, abmelden=False):
        if self.sock:
            try:
                if abmelden:
                    self.sock.sendall(b"\xe0\x00")      # DISCONNECT
                self.sock.close()
            except OSError:
                pass
        self.sock = None

    def _pflegen(self):
        """Eingehende Bytes (PINGRESP) verwerfen, Keepalive senden, Abbruch erkennen."""
        try:
            while select.select([self.sock], [], [], 0)[0]:
                if not self.sock.recv(1024):
                    raise ConnectionError("Broker hat die Verbindung geschlossen")
            if time.monotonic() - self.t_gesendet > self.keepalive / 2:
                self.sock.sendall(b"\xc0\x00")          # PINGREQ
                self.t_gesendet = time.monotonic()
        except OSError as e:
            log.warning("MQTT-Verbindung verloren: %s", e)
            self._socket_zu()

    def _lauf(self):
        while True:
            if self.sock is None:
                if self._stopp.is_set():
                    break
                if not self._verbinden():
                    self._stopp.wait(5)
                    continue
            try:
                topic, nutz, retain = self._schlange.get(timeout=0.5)
            except queue.Empty:
                if self._stopp.is_set():
                    break
                self._pflegen()
                continue
            try:
                self.sock.sendall(_paket(0x30 | (1 if retain else 0), _str(topic) + nutz))
                self.t_gesendet = time.monotonic()
                self.gesendet += 1
            except OSError as e:
                log.warning("MQTT Senden fehlgeschlagen: %s", e)
                self._socket_zu()
                try:
                    self._schlange.put_nowait((topic, nutz, retain))   # nach Neuverbindung erneut
                except queue.Full:
                    self.verworfen += 1
        self._socket_zu(abmelden=True)


class PeakboardMelder:
    """Übersetzt Prozessereignisse in die MQTT-Topics (Schema siehe peakboard/MQTT_Schnittstelle.md)."""

    def __init__(self, pub):
        self.pub = pub
        self.fehler_aktiv = False

    FARBE_EN = {"weiss": "white", "rot": "red", "blau": "blue"}

    def _event(self, daten):
        """Ereignis im Format der Kursfolien: event, color, cycle_count, timestamp (UTC)."""
        zeit = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        self.pub.senden(config.TOPICS["event"], dict(daten, timestamp=zeit), retain=False)

    def _wert(self, name, wert):
        """Einzelwert als einfacher Text (für Peakboard ohne JSON-Auswertung)."""
        self.pub.senden(config.TOPICS["wert"] + name, "" if wert is None else str(wert))

    def __call__(self, art, d):
        t = config.TOPICS
        if art == "status":
            self.pub.senden(t["status"], {"zustand": d["zustand"], "modus": d["modus"]})
            self._wert("zustand", d["zustand"])
            self._wert("modus", d["modus"])
            if d["zustand"] != "FEHLER" and self.fehler_aktiv:
                self.fehler_aktiv = False
        elif art == "zyklus":
            self.pub.senden(t["zyklen"], {"wert": d["zyklen"]})
            self.pub.senden(t["farbe_letzte"], {"wert": d["farbe_letzte"]})
            self.pub.senden(t["farbe_anzahl"], dict(d["anzahl"]))
            self._wert("zyklen", d["zyklen"])
            self._wert("farbe_letzte", d["farbe_letzte"] or "–")
            for farbe, n in d["anzahl"].items():
                self._wert("anzahl_" + farbe, n)
            if d["zyklen"] > 0:
                self._event({"event": "sorted", "color": self.FARBE_EN.get(d["farbe_letzte"], d["farbe_letzte"]),
                             "cycle_count": d["zyklen"]})
        elif art == "fehler":
            if d.get("code") is not None:
                self._event({"event": "error", "code": d.get("code"), "text": d.get("text"), "cycle_count": d.get("zyklus")})
            self.fehler_aktiv = d.get("code") is not None
            self.pub.senden(t["fehler"], {"aktiv": self.fehler_aktiv, "code": d.get("code"),
                                          "text": d.get("text"), "anzahl": d.get("anzahl", 0)})
            self._wert("fehler_aktiv", 1 if self.fehler_aktiv else 0)
            self._wert("fehler_text", d.get("text") or "")
            self._wert("fehler_anzahl", d.get("anzahl", 0))

    def startwerte(self, snap):
        """Beim Start alle Topics einmal setzen, damit Peakboard sofort Werte hat."""
        self("status", snap)
        self("zyklus", snap)
        self("fehler", {"code": None, "text": "kein Fehler", "anzahl": snap["fehler_anzahl"]})
