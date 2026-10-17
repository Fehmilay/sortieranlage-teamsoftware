"""Fügt Anhang 10 (Arbeitsaufträge M2) + 4 Arbeitsblätter (2.1–2.4) per XML in die Leistungsnachweis-Excel ein.
Aufruf: python anhang10.py <xlsx> <backup> <vorlagen-ordner>
"""
import csv, math, os, re, shutil, sys, zipfile
from xml.sax.saxutils import escape

SRC, BAK, VORL = sys.argv[1], sys.argv[2], sys.argv[3]
TITLE, SUB, SEC, HEAD, ROW, ROW2, NOTE, VOR, BES, OFF, LBL, FILL = 478, 479, 480, 481, 484, 485, 486, 487, 488, 494, 496, 43
STATUS = {"VORSCHLAG": VOR, "BESTÄTIGT": BES, "OFFEN": OFF}


def col(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


class Blatt:
    def __init__(self, breiten):
        self.breiten = breiten
        self.n = len(breiten)
        self.rows, self.merges, self.r = [], [], 0

    def _hoehe(self, zellen):
        zeilen = 1
        for i, (txt, _, span) in enumerate(zellen):
            if not txt:
                continue
            w = sum(self.breiten[i:i + span]) * 1.05
            z = sum(max(1, math.ceil(len(teil) / max(w, 1))) for teil in str(txt).split("\n"))
            zeilen = max(zeilen, z)
        return max(18, 14.5 * zeilen + 4)

    def zeile(self, zellen, hoehe=None):
        """zellen: Liste (text, style, span)."""
        self.r += 1
        r = self.r
        xml, i = [], 0
        for txt, st, span in zellen:
            ref = f"{col(i)}{r}"
            if txt in (None, ""):
                xml.append(f'<c r="{ref}" s="{st}"/>')
            else:
                t = escape(str(txt))
                xml.append(f'<c r="{ref}" s="{st}" t="inlineStr"><is><t xml:space="preserve">{t}</t></is></c>')
            for k in range(1, span):
                xml.append(f'<c r="{col(i + k)}{r}" s="{st}"/>')
            if span > 1:
                self.merges.append(f"{col(i)}{r}:{col(i + span - 1)}{r}")
            i += span
        h = hoehe or self._hoehe(zellen)
        self.rows.append(f'<row r="{r}" ht="{h:.1f}" customHeight="1">{"".join(xml)}</row>')

    def leer(self):
        self.r += 1

    def titel(self, t):
        self.zeile([(t, TITLE, self.n)], 28)

    def unter(self, t):
        self.zeile([(t, SUB, self.n)])

    def abschnitt(self, t):
        self.leer()
        self.zeile([(t, SEC, self.n)], 22)

    def kopf(self, werte, spans=None):
        spans = spans or [1] * len(werte)
        self.zeile([(w, HEAD, s) for w, s in zip(werte, spans)])

    def daten(self, werte, nr, spans=None, status_spalte=None):
        spans = spans or [1] * len(werte)
        st = ROW if nr % 2 else ROW2
        zellen = []
        for j, (w, s) in enumerate(zip(werte, spans)):
            zellen.append((w, STATUS.get(w, st) if j == status_spalte else st, s))
        self.zeile(zellen)

    def label(self, lab, text):
        self.zeile([(lab, LBL, 1), (text, ROW, self.n - 1)])

    def notiz(self, t):
        self.zeile([(t, NOTE, self.n)])

    def xml(self, fit=True):
        cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(self.breiten))
        merges = (f'<mergeCells count="{len(self.merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in self.merges)
                  + "</mergeCells>") if self.merges else ""
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheetPr><tabColor rgb="FFC55A11"/><pageSetUpPr fitToPage="1"/></sheetPr>'
                f'<dimension ref="A1:{col(self.n - 1)}{max(self.r, 1)}"/>'
                '<sheetViews><sheetView showGridLines="0" workbookViewId="0"><selection activeCell="A1" sqref="A1"/></sheetView></sheetViews>'
                '<sheetFormatPr defaultRowHeight="15"/>'
                f'<cols>{cols}</cols><sheetData>{"".join(self.rows)}</sheetData>{merges}'
                '<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>'
                '<pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>')


# ---------------------------------------------------------------- Anhang 10
a = Blatt([16, 64, 12, 34, 16, 16])
a.titel("Anhang 10 – Arbeitsaufträge M2 und Pflichtaufgaben Richtung Pre-Production (Stand 15.10.2026)")
a.notiz("Neu hier? Zuerst das Blatt „LIES MICH - Einfach erklaert“ lesen – dort steht alles in einfachen Worten, inklusive Ablauf für nächste Woche.")
a.unter("To-Dos 2.1–2.4 aus Anhang 4, verteilt auf P1–P4 am 13.10.2026; Pflichtaufgaben J1–J14 und Messaufgaben T1–T10 ergänzt am 15.10.2026. Für Einsteiger geschrieben. Die Arbeitsblätter "
        "„M2 2.1 …“ bis „M2 2.4 …“ in dieser Mappe sind vorbefüllt: gefüllte Zellen = Vorschlag zum Prüfen, leere Zellen = eure Aufgabe. "
        "Status: BESTÄTIGT = belegt · VORSCHLAG = Team-Entwurf · OFFEN = unbekannt.")
a.label("Ziel der Woche", "Am 20.10. wissen wir für jedes Bauteil der Sortierstrecke, welches Signal es liefert bzw. was es tun soll, "
        "in welcher Reihenfolge die Anlage arbeitet und welche Daten später auf dem Peakboard-Bildschirm erscheinen. Grundlage für M3 (Programmierung).")

a.abschnitt("Wer macht was?")
a.kopf(["To-Do", "Aufgabe", "Wer", "Name / Ergebnis-Blatt", "Entwurf teilen bis", "Fertig bis"])
for i, z in enumerate([
        ["2.1", "Input-Liste: Welcher Sensor liefert welches Signal und wann?", "P2", "Name: ____ · Blatt „M2 2.1 Input-Liste (P2)“", "Do 15.10.", "Sa 17.10."],
        ["2.2", "Output-Liste: Welcher Aktor soll wann wie angesteuert werden?", "P3", "Name: ____ · Blatt „M2 2.2 Output-Liste (P3)“", "Do 15.10.", "Sa 17.10."],
        ["2.3", "Ablauf-/Logikmodell: Input → Verarbeitung → Output", "P1", "Name: ____ · Blatt „M2 2.3 Ablaufmodell (P1)“ + Skizze", "Fr 16.10.", "So 18.10."],
        ["2.4", "Datenpunkte für Zustand, Zykluszahl, Farbe, Fehler (Topics für Peakboard)", "P4", "Name: ____ · Blatt „M2 2.4 Datenpunkte (P4)“ + Bildschirm-Skizze", "Fr 16.10.", "Mo 19.10."],
        ["2.5", "I/O- und Logikmodell gegen Anforderungen prüfen (danach)", "P5", "P5 bzw. Softwareleitung, ab Mo 19.10.", "–", "Di 20.10."]], 1):
    a.daten(z, i)
a.notiz("Abhängigkeiten laut Anhang 4: 2.3 braucht 2.1 + 2.2, 2.4 braucht 2.3. Damit das in einer Woche klappt, starten alle sofort mit dem "
        "vorbefüllten Entwurf und stimmen sich früh ab – deshalb die festen Übergabetermine.")

a.abschnitt("PFLICHT JETZT – damit wir Richtung Pre-Production (erster Test an der echten Anlage) kommen  ·  Stand 15.10.2026")
a.notiz("Nur Aufgaben, ohne die der erste Hardwaretest nicht möglich oder nicht sicher ist. Jede Zeile ist so geschrieben, dass man sie "
        "ohne Vorwissen erledigen kann. Erledigt? Status auf „Erledigt + Datum“ setzen und kurz in die Gruppe schreiben.")
a.kopf(["Nr", "Aufgabe – so geht's (für Einsteiger)", "Wer", "Warum wichtig / fertig, wenn …", "Bis", "Status"])
for i, z in enumerate([
        ["J1", "MQTT-Broker (Postamt für Peakboard): wird von PI_EINRICHTEN.bat automatisch fürs Netz freigegeben und geprüft – siehe J3.",
         "Softwareleitung", "Mosquitto ist laut Prof. Kampker installiert. Fertig, wenn PI_EINRICHTEN im Abschlusstest „ALLES GRÜN“ zeigt.", "mit J3", "in J3 enthalten"],
        ["J2", "SSH-Schlüssel: wird von PI_EINRICHTEN.bat automatisch hinterlegt – siehe J3. Danach geht alles ohne Passwort.",
         "Softwareleitung", "Claude kann danach Einspielen und Tests selbst im Terminal erledigen.", "mit J3", "in J3 enthalten"],
        ["J3", "Pi einrichten mit EINEM Doppelklick: 1) Prof. Kampker kurz Bescheid geben (es ändert Einstellungen am Pi). 2) Laptop ins WLAN der Anlage. "
               "3) Doppelklick auf PI_EINRICHTEN.bat im Projektordner. 4) Zweimal das Pi-Passwort eintippen (Zeichen bleiben unsichtbar). "
               "Das Programm erledigt allein: Programm kopieren, SSH-Schlüssel, Uhrzeit, I2C einschalten, Mosquitto fürs Netz freigeben, Tests, Abschlusstest. "
               "Startet der Pi neu: einfach warten (ca. 2 Minuten).",
         "Softwareleitung", "Kein Internet nötig – ein eigener Treiber ersetzt die fehlende Bibliothek für den Automation HAT Mini. Fertig, wenn „EINRICHTUNG OK“ "
                            "und im Abschlusstest „ALLES GRÜN“ steht (Platinen werden erst nach J15 erkannt).", "nächster Anlagentermin (geht schon vor dem Anschluss)", "Offen"],
        ["J4", "Bauteile: Die Bestellliste des Hardware-Teams liegt vor (92,50 €, Datei quellen/Bestellliste_Sortieranlage.pdf): Waveshare Motor Driver HAT, "
               "Automation HAT MINI, GPIO-Multiplexer (Verteiler), GPIO-Kabel, WAGO-Klemmen, Jumper-Kabel. Noch klären: 1) Ist bestellt? 2) Wann kommt es? "
               "3) Ein 9-V-Netzteil steht NICHT auf der Liste – reicht das vorhandene fischertechnik-Netzteil?",
         "P3 + Softwareleitung", "Ohne Bauteile kein Einspieltag. Fertig, wenn alles da ist (Foto in die Gruppe).", "Fr 16.10.", "Teilweise erledigt 15.10."],
        ["J5", "Entscheidung Motor: erledigt durch die Bestellung – das Band läuft über den Waveshare Motor Driver HAT (Motor A). "
               "Der Programmteil dafür ist fertig (motor_hat.py, mit Ersatztest geprüft, an echter Hardware noch ungetestet).",
         "P3", "Drehrichtung und Geschwindigkeit werden am Testtag eingestellt (T5).", "–", "Erledigt 15.10."],
        ["J6", "Anschluss-Frage an das Hardware-Team: Können Lichtschranken (Fototransistoren), Impulstaster und Farbsensor OHNE Zusatzbauteile "
               "an die Eingänge des Automation HAT MINI? Welche Spannung liefern sie? Passt unser Anschlussplan-Vorschlag (Blatt „LIES MICH“)?",
         "P2 + Hardware-Team", "Projektauftrag: keine eigene Elektronik/Lötarbeit. Passt es nicht, braucht es ein anderes Bauteil – das muss vor dem Test klar sein.",
         "Di 20.10.", "Offen"],
        ["J7", "Entscheidung: Wie geht es nach einem Fehler weiter? Im Meeting eine Variante wählen: A) Knopf auf dem Peakboard-Bildschirm, "
               "B) Taster an der Anlage (braucht freien Eingang), C) automatisch, wenn das Werkstück entnommen ist und alle Lichtschranken 5 s frei sind.",
         "P1", "Sonst bleibt die echte Anlage nach einem Fehler stehen, bis das Programm neu gestartet wird (nur die Simulation quittiert automatisch).",
         "Di 20.10.", "Offen"],
        ["J8", "Entscheidung mit Prof. Kampker: Wie prüfen wir den „Werkstück-Ausgang“? Die Lichtschranke I3 hat das Werkstück schon hinter sich, "
               "wenn das Ventil schaltet. Möglich: Lichtschranken der Lagerstellen I6–I8 doch nutzen (braucht 3 weitere Eingänge) oder "
               "„Ventil hat geschaltet und kein Fehler“ als Prüfung akzeptieren.",
         "P1 + Softwareleitung", "Der Projektauftrag verlangt „Werkstück-Ausgang prüfen“; der jetzige Code prüft das nur eingeschränkt.", "Di 20.10.", "Offen"],
        ["J9", "Bedienregel festlegen und an der Anlage aushängen: Immer nur EIN Werkstück auflegen und warten, bis es aussortiert ist. "
               "Mitentscheiden: Soll die Software ein zweites Werkstück als Fehler melden?",
         "P1", "Ein zweites Werkstück fährt ungemessen mit und landet in der falschen Rutsche.", "Di 20.10.", "Offen"],
        ["J10", "Altes Programm besorgen: Im Moodle-Kurs das ROBO-Pro-Projekt der Sortierstrecke (XML-Datei) herunterladen und in den "
                "Projektordner bzw. Drive-Ordner legen. Nichts daran ändern.",
         "P2 (erledigt durch Claude)", "Aus Moodle (Sorting_Line.rpp) ausgelesen: weiß < 1160 ≤ rot < 1500 ≤ blau (Rohwert TXT), Impulse 5/15/26, Ventil 0,5 s, kleinster Messwert zählt – ins Programm übernommen. Auffällig: Original schaltet zusätzlich Motor M2 für 3 s (Zweck klären).", "–", "Erledigt 15.10."],
        ["J11", "Peakboard vorbereiten: 1) IP-Adresse der Peakboard Box herausfinden (Geräteliste im TP-Link-Router oder Prof. Kampker). "
                "2) Klären, wer den Peakboard Designer auf dem Laptop hat. 3) Im Designer Datenquelle MQTT anlegen: Server 192.168.1.103, Port 1883 "
                "(Anleitung: peakboard/MQTT_Schnittstelle.md).",
         "P4", "Dann kann das Dashboard schon mit Simulationsdaten gebaut werden (piverbindungtest2.bat -SimStarten).", "Di 20.10.", "Offen"],
        ["J12", "Nachrichtenformat festlegen: Im Meeting zwischen Anhang 7 (Abschnitt A2) und dem Code (peakboard/MQTT_Schnittstelle.md) entscheiden. "
                "Empfehlung: Code-Variante, weil sie schon getestet ist.",
         "P4", "Peakboard und Steuerung müssen dieselben Namen und Felder verwenden.", "Di 20.10.", "Offen"],
        ["J13", "Ablauf für den ersten Hardwaretest aufschreiben: 1) nur Eingänge lesen (Eingangs-Monitor, schaltet nichts), 2) jeden Ausgang einzeln "
                "mit Freigabe von Prof. Kampker, 3) erst dann ganze Sortierzyklen. Vorher klären: Wer darf schalten? Wie wird sofort abgeschaltet (9-V-Netzteil ziehen)?",
         "P5 bzw. Softwareleitung", "Sicherheit: Aktoren erst nach bestätigter Verdrahtung (Projektauftrag).", "Di 20.10.", "Offen"],
        ["J14", "Code erneut geprüft und verbessert: MQTT-Versand bremst die Steuerung nicht mehr, Impulstaster wird entprellt, Messrichtung des "
                "Farbsensors einstellbar, Eingangs-Monitor für den Testtag (sortieranlage/io_monitor.py), Selbsttest um „Taster prellt“ erweitert (5/5 bestanden). "
                "Ebenfalls 15.10.: an die bestellte Hardware angepasst (Automation HAT Mini, Motor Driver HAT, Anschluss-Vorschlag, Ersatztest bestanden), eingebauter Treiber für den HAT Mini und Einrichtungsprogramm PI_EINRICHTEN.bat (ein Doppelklick, kein Internet). "
                "Offen: Code für J7, J8, J9 – sobald entschieden.",
         "Softwareleitung (mit Claude)", "Steuerung ist für den ersten Test vorbereitet; Rest hängt an den Entscheidungen.", "laufend", "Teilweise erledigt 15.10."],
        ["J15", "Hardware anschließen (Team Hardware): Strom aus, beide Platinen über den Verteiler an den Pi, Kabel nach dem Anschlussplan-Vorschlag "
                "(Blatt „LIES MICH“) an die Klemmen. Abweichungen in den Plan schreiben. Danach Foto vom Aufbau in die Gruppe.",
         "Team Hardware (Ansprechpartner: Softwareleitung)", "Ohne angeschlossene Hardware kann der Code nicht eingespielt und getestet werden. Fertig: Foto + abgehakter Plan.",
         "vor dem Einspieltag (KW 43)", "Offen"],
        ["J16", "Code einspielen (Woche ab 19.10.): genau nach Ablauf im Blatt „LIES MICH“, Schritte 0–6 – erst prüfen und messen, dann mit Freigabe schalten.",
         "Softwareleitung + alle", "Ziel: erster echter Sortiervorgang mit einem Werkstück. Voraussetzung: J3, J4, J6, J15.", "KW 43 (nach J15)", "Geplant"]], 1):
    a.daten(z, i)

a.abschnitt("ERST NACH DEM TESTING – das können wir nur an der echten Anlage messen (nicht raten!)")
a.notiz("Hilfsmittel: Eingangs-Monitor (auf dem Pi: python3 io_monitor.py) – zeigt alle Eingänge live und schaltet nichts. "
        "Die Ergebnisse trägt die Softwareleitung in sortieranlage/config.py ein (Wert in Klammern).")
a.kopf(["Nr", "Was wir messen – so geht's", "Wer", "Ergebnis geht in … (config.py)", "Wann", "Status"])
for i, z in enumerate([
        ["T1", "Welcher Draht an welcher Klemme? Mit dem Eingangs-Monitor jede Lichtschranke kurz abdecken und den Taster drücken – notieren, "
               "welcher Eingang (IN1–IN3, A1–A3) reagiert.", "P2 / P3", "Kanalbelegung (EINGAENGE, AUSGAENGE)", "1. Testtag (nur lesen)", "Offen"],
        ["T2", "Zeigt eine Lichtschranke 1 oder 0, wenn sie FREI ist? Einmal frei, einmal abgedeckt im Monitor ablesen.", "P2",
         "Pegel der Lichtschranken (LS_INVERTIERT)", "1. Testtag (nur lesen)", "Offen"],
        ["T3", "Farbsensor: Wert bei leerem Band notieren. Dann je Farbe 10 Werkstücke langsam unter dem Sensor durchschieben und kleinsten/größten Wert notieren.",
         "P2", "Farbbereiche, Messrichtung, Spannungsbereich (FARB_BEREICHE, FARB_MESSUNG, ANALOG_MAX_V)", "1. Testtag (nur lesen)", "Offen"],
        ["T4", "Impulstaster: von Hand langsam drücken – zählt ein Druck als 1 oder 2 Wechsel? Später bei laufendem Band Flanken pro Sekunde ablesen.",
         "P2", "Welche Flanken zählen, Entprellung (IMPULS_ZAEHLT, IMPULS_STABIL_ABTASTUNGEN)", "1. Testtag / nach Freigabe Band", "Offen"],
        ["T5", "Impulse bis zu jedem Ventil: Werkstück an der Lichtschranke I3 anlegen, Band in kleinen Schritten fahren, Impulse bis vor Ventil weiß/rot/blau zählen "
               "(mit den Werten aus dem ROBO-Pro-Programm vergleichen). Dabei prüfen: läuft das Band in die richtige Richtung?", "P3", "Impulse bis Ventil, Drehrichtung (IMPULSE_BIS_VENTIL, MOTOR_VORWAERTS)", "nach Freigabe Band", "Offen"],
        ["T6", "Druckluft: Nach wie vielen Sekunden Kompressor reicht der Druck? Wie lange muss ein Ventil offen sein, damit das Werkstück sicher in der Rutsche landet?",
         "P3", "Vorlaufzeit Kompressor, Ventilzeit (KOMPRESSOR_VORLAUF_S, VENTIL_PULS_S)", "nach Freigabe Aktoren", "Offen"],
        ["T7", "Zeiten messen (Stoppuhr oder Logdatei): Wie lange fährt ein Werkstück vom Farbsensor bis I3? Wie lange dauert es höchstens zwischen zwei Impulsen?",
         "P1", "Zeitlimits für Fehler (TIMEOUT_BIS_AUSWURF_S, TIMEOUT_IMPULS_S)", "nach Freigabe Band", "Offen"],
        ["T8", "Erster Start der Steuerung mit echter Hardware – zuerst nur Eingänge. Läuft die HAT-Bibliothek mit unserem Code? Fehlermeldungen an die Softwareleitung.",
         "Softwareleitung", "Code-Anpassung falls nötig (inputs.py / outputs.py)", "nach J3", "Offen"],
        ["T9", "Fehlerfall für die Abnahme vorführen (z. B. Band festhalten → Meldung „band_blockiert“ auf dem Peakboard).", "P5",
         "Abnahme-Nachweis (Testprotokoll)", "nach erstem vollständigen Zyklus", "Offen"],
        ["T10", "Peakboard mit echten Werten prüfen: stimmen Zustand, Zykluszahl, Farbe und Fehler mit der Anlage überein? (To-Do 6.4)", "P4",
         "Dashboard-Freigabe", "nach erstem vollständigen Zyklus", "Offen"]], 1):
    a.daten(z, i)
a.notiz("Nicht entscheidend für die Pre-Production (trotzdem erledigen): Fotos vom 06.10. in Anhang 5 neu einfügen; E-Mail-Adresse von Prof. Kampker erfragen. "
        "Erledigt: gemessene IP-Adressen in Anhang 7 (15.10.); Teammitglieder informiert und Drive-Ordner aktualisiert (15.10.).")

a.abschnitt("Zeitplan")
a.kopf(["Tag", "Was passiert", "", "", "", ""], [1, 5, 0, 0, 0, 0][:2])
for i, (tag, was) in enumerate([
        ("Di 13.10.", "Aufgaben verteilt. Jeder liest seinen Auftrag und öffnet sein Arbeitsblatt (30 min)."),
        ("Mi 14.10.", "P2/P3: Handbuch und Fotos auswerten, Liste ausfüllen. P1/P4: Vorschlag lesen, Fragen notieren."),
        ("Do 15.10.", "P2 und P3 teilen ihren Entwurf in der Gruppe – auch mit Lücken (Lücke = OFFEN)."),
        ("Fr 16.10.", "Abstimmung 20 min online (alle 4): Passen Inputs, Outputs, Ablauf und Datenpunkte zusammen? Fragen-Liste ergänzen."),
        ("Sa 17.10.", "P2/P3 fertig. P1 stellt das Ablaufmodell fertig."),
        ("So 18.10.", "P1 fertig → an P4. P4 prüft, ob jeder Zustand einen Datenpunkt hat."),
        ("Mo 19.10.", "P4 fertig. Alles liegt in dieser Mappe / im Gruppenordner. Ab hier Prüfung 2.5."),
        ("Di 20.10.", "Regelmeeting: jeder stellt sein Ergebnis in 3–5 min vor, offene Fragen an Prof. Kampker.")], 1):
    a.daten([tag, was], i, [1, 5])

a.abschnitt("Regeln für alle")
for lab, txt in [
        ("Nichts raten", "Was ihr nicht sicher wisst, steht als OFFEN in der Tabelle und kommt auf die Fragen-Liste (Gruppenchat: Frage – wer fragt – an wen)."),
        ("Anlage", "Nichts umstecken oder verkabeln, keine Motoren/Ventile selbst schalten. 9-V-Teile nie direkt an den Raspberry Pi. Beobachten und fotografieren ist erlaubt."),
        ("Quelle", "Immer angeben, woher eine Angabe stammt (9V-Handbuch Seite …, Foto vom 06.10., beobachtet am …)."),
        ("Arbeitsblatt", "Jeder arbeitet nur in seinem Blatt „M2 2.x …“. Gefüllte Zellen prüfen, leere Zellen ausfüllen, Status-Spalte pflegen.")]:
    a.label(lab, txt)

a.abschnitt("Wo finde ich was?")
a.kopf(["Quelle", "Wo", "Wofür"], [1, 2, 3])
for i, z in enumerate([
        ["9V-Handbuch (Belegungsplan)", "Moodle-Kurs; Zusammenfassung Blatt „Anhang 9 - Kursmaterial“", "welche Anschlüsse (I1, M1 …) es gibt"],
        ["I/O-Zuordnung", "Blatt „Anhang 7 - Datenfluss+Netz“, Tabelle B2 (ab Zeile 98)", "Startpunkt für 2.1 und 2.2"],
        ["Ablauf der Sortierung", "Blatt „KI-Kontext“, Zeile „ABLAUF SORTIERUNG“", "Startpunkt für 2.3"],
        ["Datenflussplan V2", "Datei Datenflussplan_V2_13-10-2026.pdf", "Gesamtbild"],
        ["MQTT-Vorschlag", "Blatt „Anhang 7“, Abschnitt A2 und Datei peakboard/MQTT_Schnittstelle.md", "Startpunkt für 2.4"],
        ["Fotos der Anlage", "Blätter „Anhang“ / „Anhang 5“, eure Handys (06.10.)", "Bauteile erkennen"]], 1):
    a.daten(z, i, [1, 2, 3])

AUFTRAEGE = [
    ("P2 · To-Do 2.1 – Input-Liste (Sensoren)",
     "Welcher Sensor meldet was, wann und wie sieht das Signal aus, wenn nichts los ist bzw. wenn ein Werkstück kommt?",
     "Lichtschranke = Lampe + Fototransistor, meldet frei/unterbrochen (digital). Farbsensor = misst reflektiertes rotes Licht, liefert eine Zahl (analog; weiß viel, blau wenig). "
     "Impulstaster = wird vom laufenden Band immer wieder gedrückt, jeder Druck = 1 Impuls; gezählt ergibt das den Weg.",
     ["Blatt „M2 2.1 Input-Liste (P2)“ öffnen – die 7 Eingänge I1, I2, I3, C1, I6–I8 stehen schon drin.",
      "Blatt „Anhang 7“, Tabelle B2 lesen und mit deinem Blatt vergleichen (Anschluss, Bauteil, Signalart). Abweichungen notieren.",
      "Im 9V-Handbuch den Belegungsplan der Sortierstrecke suchen, Seite als Quelle eintragen; was dort steht → BESTÄTIGT.",
      "Auf Fotos/Handbuch-Bild jeden Sensor an der Anlage finden und beschreiben, wo er sitzt.",
      "„Ruhezustand“ und „Aktiv, wenn …“ ausfüllen. Spannung unbekannt → OFFEN.",
      "„Wann im Ablauf?“: Reihenfolge, in der ein Werkstück vorbeikommt (I1 → I2 → I3, C1 während das Band läuft). Band mit Sensoren auf Papier skizzieren, Foto beilegen.",
      "„Wie oft / wie schnell?“: bei C1 Impulse pro Sekunde schätzen (beim nächsten Anlagentermin per Handy-Video zählen, bis dahin OFFEN).",
      "I6–I8 nur prüfen – laut Auftrag zunächst nicht im Umfang.",
      "Fragen in die Gruppenliste (Spannung der Fototransistoren? Wertebereich Farbsensor?).",
      "Do 15.10. Entwurf teilen, Fr Abstimmung, Sa 17.10. fertig."],
     "alle 7 Eingänge ohne leere Zelle (unbekannt = OFFEN) · jeder Eingang hat eine Bedeutung für die Software · Reihenfolge + Skizze vorhanden · Fragen stehen auf der Liste"),
    ("P3 · To-Do 2.2 – Output-Liste (Aktoren)",
     "Welches Teil soll sich wann bewegen, wie lange, unter welcher Voraussetzung – und was darf nie passieren?",
     "M1 = Motor des Förderbands. O5/O6/O7 = Magnetventile: öffnen kurz die Druckluft, ein Zylinder schiebt das Werkstück in die Rutsche seiner Farbe. "
     "O8 = Kompressor, erzeugt die Druckluft. Aktoren laufen mit 9 V und werden nur über Relais/Treiber geschaltet.",
     ["Blatt „M2 2.2 Output-Liste (P3)“ öffnen – M1, O5, O6, O7, O8 stehen schon drin.",
      "Mit Blatt „Anhang 7“, Tabelle B2 (Nr. 8–12) vergleichen; Quelle 9V-Handbuch eintragen.",
      "Auf Fotos/Handbuch jeden Aktor finden; Reihenfolge der Ventile weiß/rot/blau entlang des Bandes notieren (wichtig fürs Impulse-Zählen).",
      "„Was passiert sichtbar?“ in einfachen Worten ausfüllen.",
      "„Wann EIN?“ / „Wann AUS / wie lange?“ prüfen und ergänzen. Unbekannte Zeiten (z. B. Ventil-Öffnungszeit) → OFFEN.",
      "„Voraussetzung“: z. B. Ventil nur, wenn Kompressor Druck hat und Band steht.",
      "„Darf nie passieren“: Sicherheits-/Logikregeln (zwei Ventile gleichzeitig, Band läuft endlos …).",
      "Entscheidungsvorlage: Kompressor dauerhaft an oder nur beim Ausschleusen? (4 Lasten, aber 3 Relais am Automation HAT) – beide Varianten mit Vor-/Nachteilen.",
      "Motor-Fragen notieren: nur eine Drehrichtung? feste Geschwindigkeit?",
      "Do 15.10. Entwurf teilen, Fr Abstimmung, Sa 17.10. fertig."],
     "alle 5 Ausgänge mit wann ein/aus/Voraussetzung · Reihenfolge der Ventile fest · „Darf nie passieren“ ausgefüllt · Kompressor-Entscheidungsvorlage liegt vor"),
    ("P1 · To-Do 2.3 – Ablauf-/Logikmodell",
     "In welchen Schritten (Zuständen) arbeitet die Anlage, welcher Sensor löst den nächsten Schritt aus, welche Aktoren laufen dabei – und was passiert bei einem Fehler?",
     "Zustand = was die Anlage gerade tut (immer genau einer). Übergang = „wenn Sensor X meldet, dann Zustand Y und Aktor Z“. "
     "Timeout = passiert etwas zu lange nicht, ist das ein Fehler. Der Vorschlag mit 6 Zuständen entspricht dem Python-Grundgerüst (sortieranlage/process.py).",
     ["Blatt „M2 2.3 Ablaufmodell (P1)“ öffnen – 6 Zustände als Vorschlag eingetragen.",
      "Blatt „KI-Kontext“, Zeile „ABLAUF SORTIERUNG“ lesen und mit den Zuständen vergleichen: fehlt ein Schritt, ist einer überflüssig?",
      "Ablauf als Bild zeichnen (Papier, PowerPoint oder draw.io): Kästen = Zustände, Pfeile = Übergänge mit auslösendem Sensor, ein Fehler-Kasten.",
      "Ab Do (Entwürfe P2/P3): für jeden Übergang prüfen, ob der Sensor in 2.1 und jeder Aktor in 2.2 steht. Fehlt etwas → Frage an P2/P3.",
      "Fehlerfälle festlegen (Abnahme braucht mindestens einen): woran erkannt, was macht die Anlage (alles aus), was sieht der Bediener.",
      "Klären, wie ein Fehler quittiert wird (Werkstück entnehmen + Neustart? Taste? Knopf im Peakboard?) → Frage fürs Meeting.",
      "Zeitlimits als VORSCHLAG lassen (2 s ohne Impuls, 10 s bis Auswurf-Lichtschranke) – echte Werte werden an der Anlage gemessen.",
      "Fr 16.10. Abstimmung leiten (20 min, alle 4).",
      "Optional: Simulation ansehen – PowerShell im Ordner sortieranlage: python main.py (zeigt die Zustandswechsel).",
      "So 18.10. fertig → an P4."],
     "jeder Zustand hat Auslöser, Aktionen und Folgezustand · mindestens ein Fehlerfall vollständig · Ablaufskizze vorhanden · passt zu 2.1 und 2.2"),
    ("P4 · To-Do 2.4 – Datenpunkte für Peakboard",
     "Welche Informationen zeigt der Peakboard-Bildschirm, wie heißen sie (Topic), wie sehen die Werte aus und wann werden sie geschickt?",
     "MQTT = Nachrichten-Briefkasten: der Raspberry Pi schickt Nachrichten unter einem Topic (Adresse, z. B. sortieranlage/zyklen), die Peakboard Box hat es abonniert. "
     "JSON = Schreibweise der Nachricht, z. B. {\"wert\": 12}.",
     ["Blatt „M2 2.4 Datenpunkte (P4)“ öffnen – die 5 Pflicht-Datenpunkte stehen drin.",
      "Zwei Vorschläge vergleichen: Blatt „Anhang 7“, Abschnitt A2 („zustand“: idle|running|fehler, „gesamt“, „ts“) und Datei peakboard/MQTT_Schnittstelle.md („zustand“: FOERDERN, „wert“, „zeit“). Unterschiede auflisten, einen empfehlen (das Python-Grundgerüst nutzt den zweiten).",
      "Namensregeln festlegen: Kleinbuchstaben, keine Umlaute/Leerzeichen, alles beginnt mit sortieranlage/.",
      "Je Datenpunkt Wertebereich, Sendezeitpunkt und eine Beispielnachricht festlegen.",
      "Ab So 18.10. (Ablaufmodell P1): kommt jeder Zustand im Status vor, ist jeder Fehlerfall ein Fehlercode?",
      "Bildschirm skizzieren (Papier/PowerPoint): Kacheln, Anordnung, Farben (Fehler rot, läuft grün).",
      "Kann-Daten sammeln (Zykluszeit, Farbsensor-Messwert für Kalibrierung …) und als „Kann“ markieren.",
      "Fragen fürs Meeting: IP der Peakboard Box? Broker auf dem Pi? Wer hat den Peakboard Designer?",
      "Mo 19.10. fertig; im Meeting die Topics zur Abstimmung vorlegen (bereitet To-Do 4.3 vor)."],
     "5 Pflicht-Datenpunkte mit Topic, Beispiel-JSON, Wertebereich, Sendezeitpunkt · Empfehlung A oder B mit Begründung · jeder Zustand/Fehler aus 2.3 abgedeckt · Bildschirm-Skizze"),
]
for kopf, frage, erklaert, schritte, fertig in AUFTRAEGE:
    a.abschnitt(kopf)
    a.label("Deine Frage", frage)
    a.label("Kurz erklärt", erklaert)
    a.kopf(["Schritt", "Was tun?", "Erledigt", "", "", ""], [1, 1, 4])
    for i, s in enumerate(schritte, 1):
        a.daten([str(i), s, "☐"], i, [1, 1, 4])
    a.label("Fertig, wenn …", fertig)

a.abschnitt("Danach: 2.5 Prüfung (P5) und Regelmeeting 20.10.")
a.label("2.5 Prüffragen", "Hat jeder Sensor eine Aufgabe im Ablauf? Wird jeder Aktor irgendwo geschaltet? Gibt es mindestens einen Fehlerfall? "
        "Werden Zustand, Zykluszahl, Farbe und Fehler übertragen (Abnahmekriterien)? Ist P5 nicht besetzt, prüft die Softwareleitung.")
a.kopf(["Minuten", "Punkt im Regelmeeting", "Wer", "", "", ""], [1, 1, 4])
for i, z in enumerate([["5", "Input-Liste", "P2"], ["5", "Output-Liste + Entscheidungsvorlage Kompressor", "P3"],
                       ["5", "Ablaufmodell + Fehlerfälle (Skizze)", "P1"], ["5", "Datenpunkte/Topics + Bildschirm-Skizze, Abstimmung", "P4"],
                       ["10", "Offene Fragen an Prof. Kampker (HAT-Kapazität, Spannungen, IPs, Broker-Ort, Projektordner auf dem Pi)", "alle"]], 1):
    a.daten(z, i, [1, 1, 4])

a.abschnitt("Mini-Glossar")
for lab, txt in [("Input / Eingang", "Signal, das in die Steuerung hineinkommt (von einem Sensor)."),
                 ("Output / Ausgang", "Befehl, den die Steuerung herausgibt (an einen Aktor)."),
                 ("digital / analog", "digital = nur an/aus · analog = Zahlenwert (z. B. Helligkeit)."),
                 ("Impuls", "kurzes An-Aus-Signal; viele Impulse zählen = Weg messen."),
                 ("Zustand / Timeout", "aktueller Arbeitsschritt der Anlage / Zeitlimit, dessen Überschreitung als Fehler gilt."),
                 ("Relais", "elektrischer Schalter, mit dem der Raspberry Pi sicher 9-V-Teile schaltet."),
                 ("MQTT / Topic", "Nachrichtensystem / „Adresse“ einer Nachricht für Peakboard."),
                 ("TXT", "alter fischertechnik-Controller, den der Raspberry Pi ersetzt (I1, M1 … sind seine Anschlussnamen).")]:
    a.label(lab, txt)

# ---------------------------------------------------------------- Arbeitsblätter 2.1–2.4
def arbeitsblatt(csvdatei, titel, hinweis, breiten):
    with open(os.path.join(VORL, csvdatei), encoding="utf-8-sig", newline="") as f:
        daten = list(csv.reader(f, delimiter=";"))
    kopf, zeilen = daten[0], daten[1:]
    b = Blatt(breiten)
    b.titel(titel)
    b.unter(hinweis)
    b.leer()
    b.kopf(kopf)
    st = kopf.index("Status") if "Status" in kopf else None
    for i, z in enumerate(zeilen, 1):
        b.daten(z, i, status_spalte=st)
    for _ in range(3):                      # Reserve-Zeilen zum Ergänzen
        b.daten([""] * len(kopf), len(zeilen) + 1)
    b.leer()
    b.notiz("Status: BESTÄTIGT = in Quelle belegt · VORSCHLAG = Team-Entwurf, prüfen · OFFEN = unbekannt, auf Fragen-Liste. "
            "Gefüllte Zellen sind ein Vorschlag (13.10.2026), leere Zellen sind eure Aufgabe. Auftrag und Schritte: Blatt „Anhang 10 - Auftraege M2“.")
    return b


H = "Arbeitsblatt zu Anhang 10. Fertig bis {}. Verantwortlich: {} (Name: ____)."
blaetter = [
    ("Anhang 10 - Auftraege M2", a),
    ("M2 2.1 Input-Liste (P2)", arbeitsblatt("2.1_Input-Liste_P2.csv", "M2 · To-Do 2.1 – Input-Liste (Sensoren)", H.format("Sa 17.10.2026", "P2"),
                                             [5, 10, 26, 18, 14, 18, 22, 20, 16, 26, 12, 14, 22, 13, 24])),
    ("M2 2.2 Output-Liste (P3)", arbeitsblatt("2.2_Output-Liste_P3.csv", "M2 · To-Do 2.2 – Output-Liste (Aktoren)", H.format("Sa 17.10.2026", "P3"),
                                              [5, 10, 22, 14, 22, 24, 24, 18, 11, 22, 9, 22, 13, 28])),
    ("M2 2.3 Ablaufmodell (P1)", arbeitsblatt("2.3_Ablaufmodell_P1.csv", "M2 · To-Do 2.3 – Ablauf-/Logikmodell", H.format("So 18.10.2026", "P1"),
                                              [5, 15, 34, 24, 16, 16, 18, 40, 24, 13])),
    ("M2 2.4 Datenpunkte (P4)", arbeitsblatt("2.4_Datenpunkte_P4.csv", "M2 · To-Do 2.4 – Datenpunkte für Peakboard", H.format("Mo 19.10.2026", "P4"),
                                             [5, 18, 24, 24, 40, 28, 18, 18, 18, 10, 13])),
]

# ---------------------------------------------------------------- vorhandene Blätter ersetzen
shutil.copy2(SRC, BAK)
zin = zipfile.ZipFile(BAK)
wb = zin.read("xl/workbook.xml").decode("utf-8")
rels = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
ersatz = {}
for name, blatt in blaetter:
    rid = re.search(rf'name="{re.escape(escape(name))}"[^>]*r:id="(rId\d+)"', wb).group(1)
    ziel = re.search(rf'Target="/?(xl/worksheets/sheet\d+\.xml)" Id="{rid}"', rels).group(1)
    ersatz[ziel] = blatt.xml().encode("utf-8")
zout = zipfile.ZipFile(SRC, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)
    if it.filename in ersatz:
        d = ersatz[it.filename]
    elif it.filename == "xl/worksheets/sheet4.xml":          # Anhang 4: To-Dos 2.1–2.4 sind verteilt
        t = d.decode("utf-8")
        for zelle in ("F22", "F23", "F24", "F25"):
            t = re.sub(rf'(<c r="{zelle}"[^>]*><is><t>)Offen(</t>)', r"\1In Arbeit\2", t)
        d = t.encode("utf-8")
    zout.writestr(zipfile.ZipInfo(it.filename, it.date_time), d, zipfile.ZIP_DEFLATED)
zout.close()
print("ersetzt:", sorted(ersatz))