"""Hält alle Ausgänge des Automation HAT Mini sicher AUS, solange das Programm läuft (Standard 3 Stunden).

Wofür: Beim Messen der Eingänge muss das 9-V-Netzteil an sein (die Sensoren brauchen Strom). Ohne Programm sind
die GPIO-Pins nicht festgelegt – GPIO 5 und 6 haben beim Pi ab Werk einen Pull-up und könnten ein Ventil leicht
ansteuern. Dieses Programm legt Ventile (GPIO 5/12/6) und Relais/Kompressor (GPIO 16) fest auf AUS.
Der Motor Driver HAT (PCA9685) startet von sich aus mit allen Kanälen AUS.

Auf dem Pi:  python3 ausgaenge_aus.py [Sekunden]      Beenden: Strg+C bzw. pkill -f ausgaenge_aus
"""
import sys
import time

from gpiozero import DigitalOutputDevice

PINS = {"Ventil weiß (Output 1)": 5, "Ventil rot (Output 2)": 12, "Ventil blau (Output 3)": 6, "Kompressor (Relais)": 16}

aus = {name: DigitalOutputDevice(pin, initial_value=False) for name, pin in PINS.items()}
print("Ausgänge fest AUS:", ", ".join(f"{n} = GPIO {p}" for n, p in PINS.items()), flush=True)
try:
    time.sleep(float(sys.argv[1]) if len(sys.argv) > 1 else 3 * 3600)
except KeyboardInterrupt:
    pass
for d in aus.values():
    d.off()
