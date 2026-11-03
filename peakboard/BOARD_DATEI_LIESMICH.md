# Fertige Board-Datei für den Peakboard Designer (Stand 03.11.2026, VORSCHLAG)

**Datei:** `peakboard/Sortieranlage_Board.pbmx` · **So sieht sie aus:** `peakboard/Sortieranlage_Board_Vorschau.png` (mit Beispielwerten)

Das Board wurde von Claude gebaut, nicht im Designer. **Es wurde noch nie im Peakboard Designer geöffnet** – bitte genau
das als Erstes testen (Marie, P4). Klappt es nicht, Board von Hand nach `MQTT_Schnittstelle.md` bauen (Weg A, ca. 45 min)
und die Fehlermeldung als Screenshot in „03 Bilder + Skizzen“ legen.

## So testen (Marie, Windows-Laptop mit Peakboard Designer)
1. `Sortieranlage_Board.pbmx` von GitHub herunterladen (Datei anklicken → „Download raw file“) und im Designer öffnen.
2. Links unter **Data** die Verbindung **„Postamt Pi (Mosquitto)“** öffnen: Server `192.168.1.180`, Port `1883`.
   **Benutzer und Passwort selbst eintragen** (bekommt ihr persönlich von Rushit – stehen absichtlich nicht in der Datei).
3. Laptop ins WLAN der Anlage (TP-Link), Testdaten starten (`PEAKBOARD_TESTDATEN.bat`, Option 1 = an der Anlage).
4. Vorschau/Start im Designer: Zahlen und Zustand müssen sich ändern, bei jedem 8. Klotz wird das Banner unten rot.
5. Ergebnis in die Wochen-Tabelle, Reiter **Peakboard-Stand** („öffnet: ja/nein“, „Werte kommen: ja/nein“, Fehlermeldung).
6. Wenn alles passt: Board auf die Peakboard Box hochladen (Zugang der Box ebenfalls bei Rushit).

## Heimtest – ohne Anlage, von zu Hause (Stand 03.11.2026)
`peakboard/Sortieranlage_Board_Heimtest.pbmx` ist dasselbe Board, hört aber auf das öffentliche Test-Postamt
**broker.hivemq.com** (Port 1883, **keine Anmeldung** – Authentifizierung „Keine“ lassen) unter dem Topic-Anfang
`hsnr-sortieranlage-teamsoftware/wert/…`. Oben im Titel steht „(HEIMTEST)“. (test.mosquitto.org war am 03.11. nicht erreichbar.)
1. Testdaten starten: `PEAKBOARD_TESTDATEN.bat` → Option **2 (zuhause)**. Das Fenster zeigt, welcher Server benutzt wird –
   steht dort `test.mosquitto.org`, im Designer bei der Datenquelle `SortierMQTT` den MQTT Broker entsprechend ändern.
2. Heimtest-Datei im Designer öffnen → `SortierMQTT` → „Empfänger starten“ → Werte müssen im MQTT Tester erscheinen → OK → Vorschau.
3. Prüfen: Zustandstext + Farbe der Kachel, Zahlen, Farbfeld „Letzte Farbe“, bei jedem 8. Klotz rotes Störungsbanner.
Nur erfundene Daten, jeder im Internet kann mitlesen – deshalb ohne Passwort und nie mit echten Anlagendaten.

## Was drin ist
| Teil | Inhalt |
|---|---|
| Datenquelle `SortierMQTT` | MQTT, abonniert die 10 Einzelwerte `sortieranlage/wert/…` (zustand, zyklen, farbe_letzte, anzahl_weiss/_rot/_blau, fehler_aktiv, fehler_text, fehler_anzahl, modus) |
| Skript bei jeder Nachricht | übersetzt den Zustand („FOERDERN“ → „Fördert“ …), Farbe, Störungstext und Betriebsart in die Liste `Anzeige`, setzt die Variablen `ZustandNr`, `FarbeNr`, `FehlerNr` |
| Farbregeln | Zustand-Kachel grau (bereit) / grün (läuft) / rot (Störung) / dunkel (aus); Farbfeld „Letzte Farbe“ weiß/rot/blau; Banner unten rot bei Störung |
| Bildschirm 1920 × 1080 | Kopfzeile mit Uhrzeit, Zustand, sortierte Klötze, letzte Farbe, Zähler je Farbe, Störungsbanner, Betriebsart + Störungen seit Start |

## Neu bauen (nach Änderungen)
```
python werkzeuge/peakboard/board_bauen.py --vorschau vorschau.html   # Vorschau-HTML (dann z. B. mit Chrome als PNG speichern)
python werkzeuge/peakboard/board_bauen.py <vorlage.pbmx>             # schreibt peakboard/Sortieranlage_Board.pbmx
```
`<vorlage.pbmx>` = offizielle Peakboard-Vorlage „Intralogistik-Bestellungen-Empfangen-ueber-MQTT.pbmx“ aus
github.com/Peakboard/peakboard-templates.github.io (`_templates/Intralogistics-Receive-Orders-via-MQTT/`). Aus ihr
stammen nur Theme, Schriftstile und Peakboard-Hilfsdateien; Topics, Layout, Texte und Farben stehen im Skript.

## Was noch unsicher ist (OFFEN)
- Ob der aktuelle Designer die Datei öffnet (Vorlage stammt aus Designer 3.3.1).
- Ob jede Abo-Zeile wirklich eine eigene Spalte in `SortierMQTT[0]` füllt (so in der Vorlage, mit mehreren Topics ungetestet).
- Farbregeln: „ist gleich“ = Operator 2 – aus den offiziellen Vorlagen abgelesen, nicht dokumentiert.
