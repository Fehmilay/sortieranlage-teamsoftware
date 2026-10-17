"""MQTT-Test vom Laptop aus – prüft den Broker auf dem Pi so, wie ihn später die Peakboard Box sieht.

Aufruf: python mqtt_test_laptop.py [host] [port]
Anmeldung: Umgebungsvariablen SORTIER_MQTT_USER / SORTIER_MQTT_PASS (setzen die .bat-Skripte nach Eingabe).
Verbindet sich, abonniert sortieranlage/#, sendet sortieranlage/test und wartet, ob die Nachricht zurückkommt.
Nur Python-Standardbibliothek (kein Internet, kein pip). Exitcode 0 = Broker vom Netz aus voll nutzbar.
"""
import json
import os
import socket
import struct
import sys
import time

HOST = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.103"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1883
BENUTZER = os.environ.get("SORTIER_MQTT_USER") or None
PASSWORT = os.environ.get("SORTIER_MQTT_PASS")
FILTER = "sortieranlage/#"
TEST_TOPIC = "sortieranlage/test"


def s(text):
    b = text.encode("utf-8")
    return struct.pack("!H", len(b)) + b


def paket(kopf, inhalt):
    laenge, n = b"", len(inhalt)
    while True:
        byte, n = n % 128, n // 128
        laenge += bytes([byte | (0x80 if n else 0)])
        if not n:
            return bytes([kopf]) + laenge + inhalt


def lese_paket(sock):
    kopf = sock.recv(1)
    if not kopf:
        raise ConnectionError("Verbindung vom Broker geschlossen")
    mult, laenge = 1, 0
    while True:
        b = sock.recv(1)[0]
        laenge += (b & 127) * mult
        mult *= 128
        if not b & 128:
            break
    daten = b""
    while len(daten) < laenge:
        teil = sock.recv(laenge - len(daten))
        if not teil:
            raise ConnectionError("Paket unvollständig")
        daten += teil
    return kopf[0], daten


def main():
    print(f"MQTT-Test gegen {HOST}:{PORT}")
    try:
        sock = socket.create_connection((HOST, PORT), timeout=5)
    except OSError as e:
        print(f"[FEHLER] Keine TCP-Verbindung zu {HOST}:{PORT}: {e}")
        print("         -> Broker läuft nicht oder lauscht nur auf localhost (siehe Zusammenfassung).")
        return 2
    flags, nutz = 0x02, s(f"laptop-test-{int(time.time())}")
    if BENUTZER:
        flags, nutz = flags | 0x80 | 0x40, nutz + s(BENUTZER) + s(PASSWORT or "")
    sock.sendall(paket(0x10, s("MQTT") + bytes([4, flags]) + struct.pack("!H", 30) + nutz))
    typ, daten = lese_paket(sock)
    if typ != 0x20 or len(daten) < 2 or daten[1] != 0:
        code = daten[1] if len(daten) > 1 else "?"
        print(f"[FEHLER] Broker lehnt die Verbindung ab (CONNACK-Code {code}).")
        print("         -> Code 4 = Benutzer/Passwort falsch. Code 5 = nicht autorisiert: Anmeldung nötig oder Benutzer gesperrt.")
        return 3
    print(f"[OK]     Verbindung angenommen ({'Benutzer ' + BENUTZER if BENUTZER else 'anonym'})")
    sock.sendall(paket(0x82, struct.pack("!H", 1) + s(FILTER) + b"\x00"))
    typ, daten = lese_paket(sock)
    print("[OK]     Abonniert:", FILTER if typ == 0x90 else f"unerwartete Antwort {typ:#x}")
    marke = f"hallo-{int(time.time())}"
    sock.sendall(paket(0x30, s(TEST_TOPIC) + json.dumps({"wert": marke}).encode()))
    print(f"[OK]     Testnachricht gesendet: {TEST_TOPIC}")
    zurueck, ende = False, time.time() + 5
    sock.settimeout(1)
    while time.time() < ende:
        try:
            typ, daten = lese_paket(sock)
        except socket.timeout:
            continue
        if typ & 0xF0 == 0x30:
            tl = struct.unpack("!H", daten[:2])[0]
            topic = daten[2:2 + tl].decode("utf-8", "replace")
            nutz = daten[2 + tl:].decode("utf-8", "replace")
            print(f"         empfangen {topic}: {nutz[:120]}")
            if topic == TEST_TOPIC and marke in nutz:
                zurueck = True
    sock.sendall(b"\xe0\x00")
    sock.close()
    if zurueck:
        print("[OK]     Testnachricht kam zurück -> Broker vom Netz aus voll nutzbar (Peakboard kann sich verbinden).")
        return 0
    print("[FEHLER] Testnachricht kam nicht zurück -> Broker-Rechte (ACL) prüfen.")
    return 4


if __name__ == "__main__":
    sys.exit(main())
