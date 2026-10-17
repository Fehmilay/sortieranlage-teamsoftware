"""Ersatztest für den Hardware-Code OHNE Hardware: python3 hardware_ersatztest.py (Exitcode 0 = OK)

Ersetzt die automationhat-Bibliothek und den I2C-Bus durch Attrappen und prüft:
Anschluss-Zuordnung, Eingänge lesen, Aktorik-Sperre, Schalten der Ausgänge, Register des Motor Driver HAT.
"""
import sys
import types

import config

fehler = []


def pruefe(bedingung, text):
    print(("OK    " if bedingung else "FEHL  ") + text)
    if not bedingung:
        fehler.append(text)


class Kanal:
    def __init__(self, wert=0):
        self.wert, self.an = wert, False

    def read(self):
        return self.wert

    def on(self):
        self.an = True

    def off(self):
        self.an = False


def attrappe_automationhat():
    m = types.ModuleType("automationhat")
    gruppe = lambda **k: types.SimpleNamespace(**k)
    m.input = gruppe(one=Kanal(1), two=Kanal(0), three=Kanal(0))
    m.analog = gruppe(one=Kanal(4.5), two=Kanal(0), three=Kanal(0))
    m.output = gruppe(one=Kanal(), two=Kanal(), three=Kanal())
    m.relay = gruppe(one=Kanal())
    sys.modules["automationhat"] = m
    return m


class I2CAttrappe:
    def __init__(self):
        self.reg = {0x00: 0x00}

    def schreibe(self, r, w):
        self.reg[r] = w

    def lese(self, r):
        return self.reg.get(r, 0)


def pwm_aus(i2c, kanal):
    r = 0x06 + 4 * kanal
    return i2c.reg.get(r + 2, 0) | (i2c.reg.get(r + 3, 0) << 8)


def eingebauter_treiber():
    """hat_mini.HatMini ohne Pimoroni-Bibliothek: gpiozero und ADS1015 werden nachgebildet."""
    sys.modules.pop("automationhat", None)
    pins = {}

    class Geraet:
        def __init__(self, pin, **k):
            self.pin, self.value = pin, 0
            pins[pin] = self

        def on(self):
            self.value = 1

        def off(self):
            self.value = 0

    gz = types.ModuleType("gpiozero")
    gz.DigitalInputDevice = gz.DigitalOutputDevice = Geraet
    sys.modules["gpiozero"] = gz

    class AdsAttrappe:
        def __init__(self):
            self.geschrieben = []

        def schreibe(self, d):
            self.geschrieben.append(list(d))

        def lese(self, n):
            return bytes([0x33, 0x90])        # Rohwert 825 = 1,65 V am ADC

    import hat_mini
    ads = AdsAttrappe()
    hat = hat_mini.HatMini(i2c=ads)
    pruefe(hat_mini.ADS1015.konfig(0) == 0xC383, "ADS1015-Konfiguration Kanal 1 = 0xC383 (Einzelmessung, ±4,096 V)")
    pruefe(abs(hat.analog.one.read() - 12.92) < 0.02, "Analog: 1,65 V am ADC -> 12,9 V am Eingang (Teiler 25,85/3,3)")
    pruefe(ads.geschrieben[0] == [0x01, 0xC3, 0x83], "Messung wird über Register 0x01 gestartet")
    pins[26].value = 1
    pruefe(hat.input.one.read() == 1 and hat.input.two.read() == 0, "Digitaleingang 1 = BCM 26 wird gelesen")
    hat.relay.one.on()
    hat.output.three.on()
    pruefe(pins[16].value == 1 and pins[6].value == 1 and pins[5].value == 0, "Relais = BCM 16, Ausgang 3 = BCM 6 schalten")
    sys.modules.pop("gpiozero", None)


def main():
    pruefe(config.anschluss_pruefen() == [], "Anschluss-Vorschlag ist gültig (Mini: 3 Eingänge, 3 Analog, 3 Ausgänge, 1 Relais)")
    alt = config.AUSGAENGE["KOMPRESSOR"]["kanal"]
    config.AUSGAENGE["KOMPRESSOR"]["kanal"] = ("relay", 2)
    pruefe(any("relay 2" in p for p in config.anschluss_pruefen()), "Relais 2 wird beim Mini als Fehler erkannt")
    config.AUSGAENGE["KOMPRESSOR"]["kanal"] = ("output", 1)
    pruefe(any("schon belegt" in p for p in config.anschluss_pruefen()), "Doppelbelegung wird erkannt")
    config.AUSGAENGE["KOMPRESSOR"]["kanal"] = alt

    hat = attrappe_automationhat()
    from inputs import HatEingaenge
    ein = HatEingaenge()
    pruefe(ein.lese("LS_FARBE") is False, "Lichtschranke: Pegel 1 = frei (LS_INVERTIERT) -> nicht unterbrochen")
    hat.input.one.wert = 0
    pruefe(ein.lese("LS_FARBE") is True, "Lichtschranke: Pegel 0 -> unterbrochen")
    erwartet = 4.5 / config.ANALOG_MAX_V
    pruefe(abs(ein.lese("FARBSENSOR") - erwartet) < 1e-9, f"Farbsensor 4,5 V / ANALOG_MAX_V {config.ANALOG_MAX_V:g} V -> {erwartet:.2f}")

    import motor_hat
    i2c = I2CAttrappe()
    motor_hat.I2CGeraet = lambda bus, adresse: i2c       # kein echter Bus
    from outputs import HatAusgaenge
    try:
        HatAusgaenge()
        pruefe(False, "Aktorik-Sperre greift")
    except RuntimeError:
        pruefe(True, "Aktorik-Sperre greift (HARDWARE_FREIGEGEBEN = False)")

    config.HARDWARE_FREIGEGEBEN = True
    try:
        aus = HatAusgaenge()
        pruefe(i2c.reg.get(0xFE) == 121, "PCA9685 auf 50 Hz eingestellt (Teiler 121)")
        pruefe(pwm_aus(i2c, 0) == 0, "Motor beim Start aus")
        aus.setze("BAND", True)
        pruefe(pwm_aus(i2c, 0) == 4095 and pwm_aus(i2c, 1) == 0 and pwm_aus(i2c, 2) == 4095,
               "Band an: PWM 100 %, IN1 = 0, IN2 = 1 (Waveshare 'forward')")
        aus.setze("KOMPRESSOR", True)
        aus.setze("VENTIL_ROT", True)
        pruefe(hat.relay.one.an and hat.output.two.an and not hat.output.one.an, "Kompressor = Relais 1, Ventil rot = Ausgang 2")
        aus.alle_aus()
        pruefe(pwm_aus(i2c, 0) == 0 and not hat.relay.one.an and not hat.output.two.an, "Alles aus schaltet Motor, Relais und Ausgänge ab")
    finally:
        config.HARDWARE_FREIGEGEBEN = False

    eingebauter_treiber()
    print("HARDWARE-ERSATZTEST", "BESTANDEN" if not fehler else "NICHT BESTANDEN")
    return 0 if not fehler else 1


if __name__ == "__main__":
    sys.exit(main())
