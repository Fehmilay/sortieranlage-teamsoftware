# ★ PEAKBOARD – LIES MICH ZUERST (Marie + Jan)

**Stand 03.11.2026.** Hier steht alles, was ihr für das Peakboard braucht. Dasselbe Dokument liegt als Google Doc im Drive
(Ordner „05 Peakboard (Marie + Jan)“): https://docs.google.com/document/d/1qmOIfqN57xvzhgJGufYyh8RXb5hjy0S5mbmNttcGpOM
Quelle: `quellen/Peakboard_LIES_MICH.html`. Wer etwas ändert, ändert es bitte im Drive und hier.

## 1. Worum geht es?
Unser Programm läuft auf dem Raspberry Pi und schickt seine Werte an das **Postamt**. Das Postamt ist der MQTT-Broker auf dem Pi.
Das Peakboard holt die Werte dort ab und zeigt sie an: Zustand, Stückzahl, Farbe und Störung. Pi und Peakboard sprechen nie direkt
miteinander, immer nur über das Postamt.

## 2. Stand jetzt
- **Die Verbindung steht.** Auf dem Pi laufen gerade **2 Stunden lang Testdaten**. Der Pi spielt eine sortierende Anlage vor.
  Es bewegt sich nichts, alles ist nur Simulation.
- Die Daten kommen am Postamt an, das ist geprüft. Zustand und Stückzahl ändern sich laufend.
- **Das Peakboard kann ab sofort mit echten Pi-Daten verbunden werden.**

## 3. Was ihr braucht
| Was | Wert |
|---|---|
| Laptop | Windows-Laptop mit **Peakboard Designer** |
| WLAN | **TP-Link_25F4** (WLAN der Anlage) |
| Datenquelle | **MQTT** |
| Server | **192.168.1.180** |
| Port | **1883** (QoS 0, Message type: Text) |
| Benutzer + Passwort | **bekommt ihr persönlich von Kubilay**. Sie stehen absichtlich nirgends im Drive, in GitHub oder in ChatGPT. |

## 4. Diese Topics abonnieren
Jeder Wert hat ein eigenes Topic. Die Nachricht ist nur der Text oder die Zahl, kein JSON. Gesendet wird mit „retain“, das Peakboard
bekommt also sofort den letzten Stand.

| Topic | Beispiel | Bedeutung |
|---|---|---|
| `sortieranlage/wert/zustand` | `FOERDERN` | BEREIT, FOERDERN, ZAEHLEN, AUSSCHLEUSEN, PRUEFEN, FEHLER, AUS |
| `sortieranlage/wert/zyklen` | `12` | fertig sortierte Klötze |
| `sortieranlage/wert/farbe_letzte` | `rot` | weiss, rot, blau („–“ = noch keiner) |
| `sortieranlage/wert/anzahl_weiss` | `4` | Anzahl weiße Klötze |
| `sortieranlage/wert/anzahl_rot` | `5` | Anzahl rote Klötze |
| `sortieranlage/wert/anzahl_blau` | `3` | Anzahl blaue Klötze |
| `sortieranlage/wert/fehler_aktiv` | `1` | 1 = Störung, 0 = keine |
| `sortieranlage/wert/fehler_text` | `Kein Impuls am Taster C1 …` | Klartext der Störung |
| *optional:* `sortieranlage/wert/fehler_anzahl` | `2` | Störungen seit Start |
| *optional:* `sortieranlage/wert/modus` | `sim` | sim = Testbetrieb, hardware = Echtbetrieb |

## 5. So geht es: zwei Wege
**Weg A (schnell): die fertige Board-Datei** `Sortieranlage_Board.pbmx` (in diesem Ordner). Sie wurde **noch nie im Designer
geöffnet**, genau das bitte zuerst testen.
1. Datei anklicken → „Download raw file“ → im Peakboard Designer öffnen.
2. Links unter **Data** die Verbindung „Postamt Pi (Mosquitto)“ öffnen: Server 192.168.1.180, Port 1883, **Benutzer und Passwort selbst eintragen**.
3. Vorschau bzw. Start: Die Werte müssen sich ändern. So soll es aussehen: `Sortieranlage_Board_Vorschau.png`.

**Weg B (falls A nicht klappt), ca. 45 min:**
1. **Data → Add data source → MQTT**, Server 192.168.1.180, Port 1883, Benutzer und Passwort von Kubilay.
2. Unter Subscriptions die Topics aus Abschnitt 4 eintragen, QoS 0, Message type: Text.
3. **Enable listener**, dann in der Vorschau prüfen, ob Werte ankommen.
4. Kacheln anlegen und binden (Abschnitt 9).

Kommt bei Weg A eine Fehlermeldung, bitte einen Screenshot davon in „03 Bilder + Skizzen vom Team“ legen.

## 6. Ziel für heute
- Die Werte ändern sich im Designer.
- **Ungefähr bei jedem 8. Klotz kommt eine Störung** (fehler_aktiv = 1). Das ist Absicht, so wird der Fehlerfall getestet.
- **Screenshot** in den Drive-Ordner „03 Bilder + Skizzen vom Team“.

## 7. Peakboard Box
Im Netz hängt ein Gerät mit der Adresse **192.168.1.81**. Bitte am Bildschirm der Box nachschauen, ob das ihre Adresse ist.
Das Board kommt erst auf die Box, wenn es im Designer läuft. Den Zugang zur Box gibt es ebenfalls bei Kubilay.

## 8. Vor dem Gehen
- Ergebnisse in die ★ KW-45-Tabelle im Drive eintragen: Öffnet die Datei (ja/nein)? Kommen Werte an (ja/nein)? Gab es eine
  Fehlermeldung? Was zeigt die Box als Adresse?
- **Den Pi nicht einfach ausstecken**, das kann die Speicherkarte beschädigen. Kubilay Bescheid geben („Pi aus“). Dann wird er
  sauber heruntergefahren, und nach 30 Sekunden darf der Stecker raus.

## 9. Bildschirm-Entwurf (1920 × 1080, VORSCHLAG)
| Bereich | Inhalt | Topic |
|---|---|---|
| Kopfzeile | „Sortieranlage – Team Software HSNR“ + Uhrzeit | – |
| Kachel links (groß) | Zustand (übersetzt, farbig) | `wert/zustand` |
| Kachel Mitte | Sortierte Klötze (große Zahl) | `wert/zyklen` |
| Kachel rechts | Letzte Farbe (färbt sich weiß/rot/blau) | `wert/farbe_letzte` |
| Zeile darunter | Zähler weiß · rot · blau | `wert/anzahl_*` |
| Banner unten | Störung, rot, nur bei fehler_aktiv = 1 | `wert/fehler_aktiv`, `wert/fehler_text` |

Zustandstexte: BEREIT → „Bereit – Klotz auflegen“ (grau) · FOERDERN → „Fördert“ (grün) · ZAEHLEN → „Fährt zum Auswerfer“ (grün) ·
AUSSCHLEUSEN → „Sortiert aus“ (grün) · PRUEFEN → „Prüft“ (grün) · FEHLER → „STÖRUNG“ (rot) · AUS → „Aus“ (dunkelgrau).

## 10. Mehr Details
`MQTT_Schnittstelle.md` (ganze Schnittstelle) · `BOARD_DATEI_LIESMICH.md` (Board-Datei, was noch unsicher ist).
Frage? Den Link https://github.com/Fehmilay/sortieranlage-teamsoftware in ChatGPT/Claude einfügen und die Frage dazuschreiben,
oder Hamza bzw. Kubilay fragen.
