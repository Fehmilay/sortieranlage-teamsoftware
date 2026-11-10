# Regelmeeting Di 10.11.2026, 16–18 Uhr – Zettel für Dogukan (vertritt Rushit)

## Das sagst du (ca. 1 Minute)

> „Ich vertrete heute Rushit. Stand Team Software: Der Raspberry Pi ist fertig eingerichtet, das Postamt (MQTT) läuft, und die Peakboard-Anzeige ist gebaut – Rushit und Marie haben einen Live-Test vorbereitet, den zeigen wir gleich: Peakboard zeigt die Daten vom Pi live.
> Beim Eingangstest letzte Woche hat der Pi beide Platinen erkannt und der Zähltaster funktioniert. Die zwei Lichtschranken und der Farbsensor liefern noch keine richtigen Werte. Wahrscheinliche Ursachen: 9 V an den Lampen, gemeinsame Masse zwischen 9-V-Netzteil und Platine, Beschaltung der Lichtschranken. Das muss Team Hardware heute prüfen – danach messen wir sofort noch einmal.
> Zeitplan: heute Verkabelung fertig, 17.11. Übergabe, 24.11. Einspielen, 01.12. erster Sortierlauf, Abnahme 02.02. Wir brauchen heute: Team Hardware für die Fehlersuche, von Herrn Kampker die Freigabe für den Ausgänge-Test am 24.11., und die Info, ob wir die Peakboard Box nutzen oder Peakboard im Browser.“

## Ablauf heute

| Uhrzeit | Was | Wer |
|---|---|---|
| 16:00 | Stand vortragen (Text oben), Live-Test Peakboard zeigen | Dogukan, Marie |
| 16:15 | Team Hardware prüft mit Multimeter: 9 V an den Lampen der Lichtschranken? Gemeinsame Masse (GND 9-V-Netzteil ↔ GND Automation HAT)? Lichtschranken richtig gepolt / brauchen sie einen Pull-up? Farbsensor: 9 V + Signal an Analog 1? | Team Hardware, Alhasane |
| danach | Eingangstest wiederholen (nur lesen, nichts bewegt sich): Laptop im WLAN „TP-Link_25F4“, Eingangs-Monitor starten. 10 s nichts tun · Hand je 5 s in beide Lichtschranken · Band von Hand drehen · weiß / rot / blau je 5 s unter den Farbsensor. Werte ins Messprotokoll. | Dogukan (Terminal), Jan (Werte) |
| 17:30 | Ergebnis + Termine festhalten, Aufgaben bis 17.11. verteilen | alle |

## Live-Test Peakboard

1. Laptop ins WLAN „TP-Link_25F4“.
2. Damit Daten fließen: Doppelklick auf `PEAKBOARD_TESTDATEN.bat` (an der Anlage → sendet an den Pi 192.168.1.180).
3. Peakboard Designer öffnen, Board von Marie starten (Vorschau) – Zustand, Stückzahl, Farbe und Störung müssen sich bewegen.

## Wichtig / Sicherheit

- Platinen nur bei **ausgeschaltetem** Pi auf- oder abstecken.
- **Keine Ausgänge** einschalten (Band, Ventile, Kompressor) – erst am 24.11. mit Freigabe von Prof. Kampker.
- Reihenfolge beim Aufhören: erst 9 V aus, dann den Eingangs-Monitor beenden.
- Messdatei vom 03.11. liegt noch auf dem Pi (`~/sortieranlage/messung_eingaenge_2026-11-03.csv`) – mit auf den Laptop holen.
- Passwörter nie in die Gruppe oder ins Drive.

## Fragen, die heute beantwortet werden müssen

- **Team Hardware:** Woran lag es (9 V, Masse, Beschaltung)? Ist am 17.11. alles fertig? Wie viel Strom ziehen die Ventile? Wer ist am 24.11. dabei?
- **Prof. Kampker (Hamza):** Freigabe Ausgänge-Test 24.11.? Peakboard Box oder Browser (Peakboard LINK)? Dürfen wir auch an anderen Tagen an die Anlage?
- **Team QM (Melih):** Schnittstellenmatrix abgestimmt?

## Aufgaben bis Di 17.11.

| Wer | Aufgabe |
|---|---|
| Alhasane | Mit Team Hardware Fehlerursachen klären, Übergabe 17.11. festmachen, Fotos ins Drive |
| Dogukan | Eingangstest heute + am 17.11. wiederholen, Messdateien auf den Laptop holen |
| Jan | Messprotokoll ausfüllen (Werte für weiß/rot/blau) |
| Marie | Board fertig machen, Screenshot ins Drive |
| Hassan | Testkonzept + Doku-Gliederung |
| Melih | Schnittstellenmatrix mit Team QM abschließen |
| Hamza | Fragen an Prof. Kampker, Risikoliste |
| alle | Ergebnisse in die Drive-Tabellen eintragen (seit 03.11. ist dort nichts angekommen) |
