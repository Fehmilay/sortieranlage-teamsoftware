"""Waveshare Motor Driver HAT (PCA9685 + TB6612FNG) – Förderband-Motor M1.

Nur Python-Standardbibliothek (I2C über /dev/i2c-1), damit auf dem Pi ohne Internet nichts
installiert werden muss. Register und Kanäle wie im Waveshare-Beispielcode (VORSCHLAG).
UNGETESTET an echter Hardware – erster Einsatz nur mit Freigabe (Anhang 10, J13/T5).
"""
import os
import time

import config

I2C_SLAVE = 0x0703            # ioctl-Befehl: Zieladresse auf dem I2C-Bus setzen


class I2CGeraet:
    def __init__(self, bus, adresse):
        import fcntl          # nur unter Linux vorhanden
        self.fd = os.open(f"/dev/i2c-{bus}", os.O_RDWR)
        fcntl.ioctl(self.fd, I2C_SLAVE, adresse)

    def schreibe(self, register, wert):
        os.write(self.fd, bytes([register, wert & 0xFF]))

    def lese(self, register):
        os.write(self.fd, bytes([register]))
        return os.read(self.fd, 1)[0]


class PCA9685:
    MODE1, PRESCALE, LED0_ON_L = 0x00, 0xFE, 0x06

    def __init__(self, geraet):
        self.g = geraet
        self.g.schreibe(self.MODE1, 0x00)

    def frequenz(self, hz):
        teiler = int(round(25_000_000 / 4096 / hz - 1))
        alt = self.g.lese(self.MODE1)
        self.g.schreibe(self.MODE1, (alt & 0x7F) | 0x10)   # Schlafmodus, nur dann darf der Teiler gesetzt werden
        self.g.schreibe(self.PRESCALE, teiler)
        self.g.schreibe(self.MODE1, alt)
        time.sleep(0.005)
        self.g.schreibe(self.MODE1, alt | 0x80)            # Neustart

    def pwm(self, kanal, an, aus):
        r = self.LED0_ON_L + 4 * kanal
        for i, wert in enumerate((an & 0xFF, an >> 8, aus & 0xFF, aus >> 8)):
            self.g.schreibe(r + i, wert)

    def tastgrad(self, kanal, prozent):
        self.pwm(kanal, 0, int(max(0, min(100, prozent)) * 4095 / 100))

    def pegel(self, kanal, hoch):
        self.pwm(kanal, 0, 4095 if hoch else 0)


class MotorHat:
    """Ein Motorausgang (A oder B) des Motor Driver HAT."""

    def __init__(self, motor="A", geraet=None):
        self.k = config.MOTOR_KANAELE[motor]
        self.chip = PCA9685(geraet or I2CGeraet(config.MOTOR_I2C_BUS, config.MOTOR_I2C_ADRESSE))
        self.chip.frequenz(50)
        self.stopp()

    def an(self):
        vorwaerts = config.MOTOR_VORWAERTS
        self.chip.tastgrad(self.k["pwm"], config.MOTOR_GESCHWINDIGKEIT)
        self.chip.pegel(self.k["in1"], not vorwaerts)       # Waveshare-Beispiel "forward": IN1=0, IN2=1
        self.chip.pegel(self.k["in2"], vorwaerts)

    def stopp(self):
        self.chip.tastgrad(self.k["pwm"], 0)
        self.chip.pegel(self.k["in1"], False)
        self.chip.pegel(self.k["in2"], False)
