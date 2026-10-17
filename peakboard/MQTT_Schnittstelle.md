# MQTT-Schnittstelle Raspberry Pi → Peakboard Box und Board-Bau (Stand 15.10.2026, VORSCHLAG)

## So hängt es zusammen (einfach)
Unser Programm auf dem Pi schickt Nachrichten an das **Postamt** (MQTT-Broker Mosquitto auf dem Pi, Port 1883).
Die **Peakboard Box** holt sie dort ab (abonniert) und zeigt sie auf dem Bildschirm. Pi und Box sprechen nie direkt
miteinander (Kursfolien „HSNR MQTT Raspberry Peakboard“, Moodle).

- Broker-Adresse an der Anlage: **IP des Pi** (13.10.: 192.168.1.103 – kann sich ändern, wenn der TP-Link an einen anderen Router
  angeschlossen wird → `piverbindungtest1.bat` zeigt die aktuelle IP).
- Port 1883, QoS 0. **Mit Anmeldung** (BESTÄTIGT 16.10.2026, Prof. Kampker): Mosquitto verlangt Benutzer/Passwort. Der Zugang steht
  bewusst NICHT in den Unterlagen – bei Rushit erfragen. Die Steuerung liest ihn auf dem Pi aus `~/.sortieranlage_mqtt`
  (legt `PI_EINRICHTEN.bat` nach Eingabe an), die Laptop-Skripte fragen ihn beim Start ab.
- Für das Hochladen des Boards auf die **Peakboard Box** gibt es eigene Box-Zugangsdaten (ebenfalls von Prof. Kampker, bei Rushit).

## Die Nachrichten
### A) Einfache Einzelwerte – EMPFOHLEN für Peakboard (kein JSON nötig)
Jeder Wert hat ein eigenes Topic, die Nachricht ist nur der Text bzw. die Zahl (retain → Peakboard bekommt sofort den letzten Stand).

| Topic | Beispiel | Bedeutung |
|---|---|---|
| `sortieranlage/wert/zustand` | `FOERDERN` | BEREIT, FOERDERN, ZAEHLEN, AUSSCHLEUSEN, PRUEFEN, FEHLER, AUS |
| `sortieranlage/wert/zyklen` | `12` | fertig sortierte Klötze |
| `sortieranlage/wert/farbe_letzte` | `rot` | weiss, rot, blau (– = noch keiner) |
| `sortieranlage/wert/anzahl_weiss` / `_rot` / `_blau` | `4` | Anzahl je Farbe |
| `sortieranlage/wert/fehler_aktiv` | `1` | 1 = Störung, 0 = keine |
| `sortieranlage/wert/fehler_text` | `Kein Impuls am Taster C1 …` | Klartext der Störung |
| `sortieranlage/wert/fehler_anzahl` | `2` | Störungen seit Start |
| `sortieranlage/wert/modus` | `sim` | sim = Testbetrieb, hardware = Echtbetrieb |

### B) Ereignis wie in den Kursfolien
`sortieranlage/event` (kein retain), JSON: `{"event": "sorted", "color": "red", "cycle_count": 42, "timestamp": "2026-10-15T08:23:40Z"}`
bzw. bei Störung `{"event": "error", "code": "band_blockiert", "text": "…", "cycle_count": 2, "timestamp": "…"}`.
Im Designer mit „Use data paths“ (z. B. `color`, `cycle_count`) auslesbar.

### C) JSON-Zusammenfassungen (Anhang 7 / Code-Variante)
`sortieranlage/status` `{"zustand","modus","zeit"}` · `sortieranlage/zyklen` `{"wert","zeit"}` · `sortieranlage/farbe/letzte` `{"wert","zeit"}` ·
`sortieranlage/farbe/anzahl` `{"weiss","rot","blau","zeit"}` · `sortieranlage/fehler` `{"aktiv","code","text","anzahl","zeit"}`.

Entscheidung im Team (J12): welches Format das Board nutzt. Empfehlung: **A** (am einfachsten). Der Topic-Anfang lässt sich mit
einer Einstellung ändern, z. B. auf `hsnr/sortieranlage` wie in den Kursfolien (`main.py --topic-basis hsnr/sortieranlage`).

## Testdaten ohne Anlage
`PEAKBOARD_TESTDATEN.bat` (Laptop mit Python): 1 = an der Anlage (Postamt auf dem Pi), 2 = zuhause (öffentliches Test-Postamt
test.mosquitto.org bzw. broker.hivemq.com, Topic-Anfang `hsnr-sortieranlage-teamsoftware`, nur erfundene Daten). Alle paar Sekunden
ein Klotz, bei jedem 8. Klotz eine Störung. Das Fenster zeigt, was im Designer einzutragen ist.

## Peakboard Designer – Schritte (laut Kursfolie 7, Bezeichnungen je nach Version leicht anders)
1. **Data → Add data source → MQTT**.
2. Broker: IP des Pi (bzw. Test-Postamt), Port 1883, keine Anmeldung.
3. Subscriptions: die Topics aus Tabelle A eintragen, QoS 0, Message type: Text.
4. **Enable listener** → prüfen, dass Werte ankommen (Vorschau).
5. Anzeigeelemente auf die Werte binden (siehe Bildschirm-Entwurf).
6. Board auf die Peakboard Box hochladen (Box im selben Netz, Zugangsdaten der Box von Prof. Kampker).

## Bildschirm-Entwurf (1920 × 1080) – VORSCHLAG
| Bereich | Inhalt | Daten | Darstellung |
|---|---|---|---|
| Kopfzeile | „Sortieranlage – Team Software HSNR“ + Uhrzeit | – | dunkelblau |
| Kachel groß links | Zustand | `wert/zustand` | Text übersetzt (siehe unten), Farbe je Zustand |
| Kachel Mitte | „Sortierte Klötze“ | `wert/zyklen` | sehr große Zahl |
| Kachel rechts | „Letzte Farbe“ | `wert/farbe_letzte` | Kachel färbt sich weiß/rot/blau |
| Zeile darunter | 3 Zähler weiß · rot · blau | `wert/anzahl_*` | Zahlen oder Balkendiagramm |
| Banner unten | Störungsmeldung | `wert/fehler_aktiv`, `wert/fehler_text` | nur sichtbar, wenn fehler_aktiv = 1; rot |
| Fußzeile | Betriebsart, Störungen gesamt | `wert/modus`, `wert/fehler_anzahl` | klein |

Zustandstexte: BEREIT → „Bereit – Klotz auflegen“ (grau) · FOERDERN → „Fördert“ (grün) · ZAEHLEN → „Fährt zum Auswerfer“ (grün) ·
AUSSCHLEUSEN → „Sortiert aus“ (grün) · PRUEFEN → „Prüft“ (grün) · FEHLER → „STÖRUNG“ (rot) · AUS → „Aus“ (dunkelgrau).
Betriebsart: sim → „Testbetrieb (Simulation)“, hardware → „Echtbetrieb“.

## Abnahmetest Peakboard (Kursfolie 8)
1. Broker erreichbar? 2. `mosquitto_sub` empfängt Testnachricht? 3. Peakboard-Listener empfängt? 4. Felder korrekt ausgelesen?
5. Dashboard aktualisiert sich? 6. Neustart / WLAN-Unterbrechung geprüft? 7. Doppelte Ereignisse / Zähler geprüft?

## Testbefehle (auf dem Pi)
```
mosquitto_sub -h localhost -t 'sortieranlage/#' -v
python3 main.py --farben weiss,rot,blau --fehler band_blockiert
```
