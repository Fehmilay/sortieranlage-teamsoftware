"""Eingebauter Treiber für den Pimoroni Automation HAT Mini.

Wird benutzt, wenn die Pimoroni-Bibliothek „automationhat“ fehlt (Pi ohne Internet). Bietet dieselbe
Schnittstelle: hat.input.one.read(), hat.analog.one.read(), hat.output.one.on()/off(), hat.relay.one.on()/off().
Digitale Ein-/Ausgänge über gpiozero (auf Raspberry Pi OS vorinstalliert), Analogeingänge über den
ADC ADS1015 per /dev/i2c-1 (nur Python-Standardbibliothek).
Pins/Adresse laut Pimoroni-Bibliothek – VORSCHLAG, am Testtag prüfen (Anhang 10, T1). An echter Hardware UNGETESTET.
"""
import os
import time
import types

import config

I2C_SLAVE = 0x0703


def lade_hat():
    """Pimoroni-Bibliothek, falls installiert – sonst der eingebaute Treiber."""
    try:
        import automationhat
        return automationhat
    except ImportError:
        return HatMini()


class I2C:
    def __init__(self, bus, adresse):
        import fcntl              # nur unter Linux vorhanden
        self.fd = os.open(f"/dev/i2c-{bus}", os.O_RDWR)
        fcntl.ioctl(self.fd, I2C_SLAVE, adresse)

    def schreibe(self, daten):
        os.write(self.fd, bytes(daten))

    def lese(self, anzahl):
        return os.read(self.fd, anzahl)


class ADS1015:
    """12-Bit-ADC, Einzelmessung, Messbereich ±4,096 V, 1600 Messungen/s."""

    def __init__(self, i2c):
        self.i2c = i2c

    @staticmethod
    def konfig(kanal):
        # Start | Eingang AINx gegen Masse | ±4,096 V | Einzelmessung | 1600 SPS | Komparator aus
        return 0x8000 | ((4 + kanal) << 12) | (1 << 9) | (1 << 8) | (4 << 5) | 0x0003

    def spannung(self, kanal):
        k = self.konfig(kanal)
        self.i2c.schreibe([0x01, k >> 8, k & 0xFF])
        time.sleep(0.002)
        self.i2c.schreibe([0x00])
        hi, lo = self.i2c.lese(2)
        roh = ((hi << 8) | lo) >> 4
        if roh > 0x7FF:
            roh -= 0x1000
        return roh * 4.096 / 2048


class _Eingang:
    def __init__(self, pin):
        from gpiozero import DigitalInputDevice
        self.d = DigitalInputDevice(pin, pull_up=None, active_state=True)

    def read(self):
        return int(self.d.value)


class _Ausgang:
    def __init__(self, pin):
        from gpiozero import DigitalOutputDevice
        self.d = DigitalOutputDevice(pin, initial_value=False)

    def on(self):
        self.d.on()

    def off(self):
        self.d.off()

    def read(self):
        return int(self.d.value)


class _Analog:
    def __init__(self, adc, kanal):
        self.adc, self.kanal = adc, kanal

    def read(self):
        # Spannungsteiler auf dem HAT: ANALOG_EINGANG_MAX_V am Eingang = 3,3 V am ADC
        return round(self.adc.spannung(self.kanal) * config.ANALOG_EINGANG_MAX_V / 3.3, 2)


class HatMini:
    def __init__(self, i2c=None):
        p = config.HAT_PINS
        ns = types.SimpleNamespace
        namen = ("one", "two", "three")
        self.input = ns(**{n: _Eingang(pin) for n, pin in zip(namen, p["input"])})
        self.output = ns(**{n: _Ausgang(pin) for n, pin in zip(namen, p["output"])})
        self.relay = ns(**{n: _Ausgang(pin) for n, pin in zip(namen, p["relay"])})
        adc = ADS1015(i2c or I2C(1, config.ADS1015_ADRESSE))
        self.analog = ns(**{n: _Analog(adc, k) for k, n in enumerate(namen)})
