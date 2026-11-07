# Eingangstest an der echten Anlage – 03.11.2026 (Befund)

**Aufbau:** Raspberry Pi „hsnrpi1“ über WLAN 192.168.1.180, Automation HAT Mini (I2C 0x48) und Motor Driver HAT (I2C 0x40, zusätzlich 0x70) **erkannt**. Strom Pi in Ordnung (`throttled=0x0`).
Test mit `io_monitor.py --takt 0.01 --csv messung_eingaenge_2026-11-03.csv` (nur lesen, Ausgänge dabei fest AUS). Messdatei liegt auf dem Pi in `~/sortieranlage/` (ca. 11 min) – beim nächsten Termin auf den Laptop holen.

| Sensor | Eingang | Ergebnis |
|---|---|---|
| C1 Impulstaster | IN3 (GPIO 21) | ✅ saubere Impulse, wenn das Band von Hand bewegt wird |
| I1 Lichtschranke Farbsensor | IN1 (GPIO 26) | ❌ immer 0, keine Reaktion |
| I3 Lichtschranke Auswurf | IN2 (GPIO 20) | ❌ flackert ständig von allein (ca. 7 Wechsel / 5 s, anfangs ~95 Flanken/s = Netzbrummen → offener Eingang) |
| I2 Farbsensor | A1 (ADS1015) | ❌ kein Farbsignal (0,03 V); zeitweise springen A1, A2, A3 gleichzeitig zwischen −1,9 V und +5 V (Rauschen) |

**Vermutete Ursachen (Team Hardware prüft mit Multimeter):**
1. Lampen der Lichtschranken ohne 9 V (9-V-Netzteil eingesteckt? Lampe leuchtet?).
2. Gemeinsame Masse fehlt: GND des 9-V-Netzteils nicht mit GND der Automation-HAT-Platine verbunden (typisch: Flackern, negative Spannungen).
3. Fototransistoren falsch gepolt bzw. ohne Pull-up: Der TXT-Controller hatte einen eingebauten Pull-up nach +, der Automation HAT Mini nicht. Ggf. wie den Taster (funktioniert) beschalten – Lösung mit Team Hardware klären (keine eigene Löterei).
4. Farbsensor: 9-V-Versorgung und Signaldraht an Analog 1 prüfen.

**Nächster Termin (Di 10.11.):** erst Punkte 1–4 durch Team Hardware, dann Eingangstest wiederholen (gezielt: 10 s nichts, Hand je 5 s in beide Lichtschranken, weiß/rot/blau je 5 s unter den Farbsensor), danach Farbgrenzen einstellen. Ausgänge erst nach bestandenem Eingangstest und mit Freigabe von Prof. Kampker.
