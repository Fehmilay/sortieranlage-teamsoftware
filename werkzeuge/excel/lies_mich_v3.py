"""Blatt „LIES MICH - Einfach erklaert“ einfügen (vor Anhang 10) + Anhang 7 / KI-Kontext / Seite 1 (Bestellliste, Plan KW 43).
Aufruf: python lies_mich.py <xlsx> <backup>
"""
import os, re, shutil, sys, zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blatt import Blatt, ROW, LBL, NOTE  # noqa: E402

SRC, BAK = sys.argv[1], sys.argv[2]
NAME = "LIES MICH - Einfach erklaert"

b = Blatt([24, 62, 30, 46])
b.titel("LIES MICH – Einfach erklärt: Was wir bauen und was nächste Woche passiert")
b.unter("Für alle ohne Technik-Vorwissen. Wenn du nur ein Blatt liest, dann dieses. Stand 15.10.2026. "
        "Die Aufgaben mit allen Schritten stehen in Anhang 10 (J = jetzt erledigen, T = erst beim Testen messbar).")

b.abschnitt("1. Worum geht es? (in 4 Sätzen)")
for lab, txt in [
        ("Die Anlage", "Eine kleine Modell-Fabrik von fischertechnik sortiert Bauklötze nach Farbe: weiß, rot und blau."),
        ("Was wir ändern", "Bisher steuert ein alter Steuer-Computer (TXT) die Anlage. Wir ersetzen ihn durch einen Raspberry Pi – einen kleinen Computer – mit unserem eigenen Programm."),
        ("Was man sieht", "Der Pi meldet laufend an einen Bildschirm (Peakboard), was die Anlage gerade tut: läuft / Fehler, wie viele Teile, welche Farbe."),
        ("Unser Ziel", "Bei der Abnahme sortiert die Anlage mehrere Teile richtig, der Bildschirm zeigt alles an, und wir führen mindestens einen Fehlerfall vor.")]:
    b.label(lab, txt)

b.abschnitt("2. So läuft ein Sortiervorgang ab")
b.kopf(["Schritt", "Was passiert", "Welches Teil arbeitet", "Was der Bildschirm zeigt"])
for i, z in enumerate([
        ["1", "Ein Bauklotz wird aufs Band gelegt. Die erste Lichtschranke merkt das, das Band startet.", "Lichtschranke I1, Bandmotor M1", "„FOERDERN“"],
        ["2", "Beim Vorbeifahren misst der Farbsensor, wie hell der Klotz ist (weiß = hell, blau = dunkel).", "Farbsensor I2", "–"],
        ["3", "Die zweite Lichtschranke merkt den Klotz. Ab jetzt zählt der Impulstaster mit, wie weit das Band fährt – wie ein Kilometerzähler.", "Lichtschranke I3, Impulstaster C1", "„ZAEHLEN“"],
        ["4", "Der Klotz steht vor dem Auswerfer seiner Farbe: Band stoppt, der Kompressor macht Druckluft.", "Bandmotor M1, Kompressor O8", "„AUSSCHLEUSEN“"],
        ["5", "Das Ventil öffnet kurz, Druckluft schiebt den Klotz in die Rutsche seiner Farbe.", "Ventil O5 / O6 / O7", "–"],
        ["6", "Zähler +1, die Anlage ist bereit für den nächsten Klotz.", "–", "Zykluszahl, letzte Farbe, „BEREIT“"],
        ["!", "Dauert etwas zu lange oder ist die Farbe unklar: alles stoppt sofort.", "–", "rote Fehlermeldung"]], 1):
    b.daten(z, i)

b.abschnitt("3. Die Teile – wer ist wer?")
b.kopf(["Teil", "Was es macht", "Status", "Erkennungszeichen"])
for i, z in enumerate([
        ["Raspberry Pi", "Kleiner Computer, auf dem unser Programm läuft.", "vorhanden, getestet 13.10.", "Platine im Gehäuse, Name „hsnrpi1“"],
        ["Automation HAT Mini", "Aufsteck-Platine: liest die Sensoren und schaltet Ventile und Kompressor.", "bestellt (Bestellliste)", "Platine mit Schraubklemmen und kleinem Display"],
        ["Motor Driver HAT", "Aufsteck-Platine nur für den Bandmotor.", "bestellt (Bestellliste)", "Platine mit Motor-Klemmen"],
        ["GPIO-Multiplexer", "Verteiler, damit beide Platinen gleichzeitig am Pi angeschlossen werden können.", "bestellt (Bestellliste)", "–"],
        ["Lichtschranke", "Merkt, ob ein Klotz vorbeikommt (Lampe gegenüber einem Lichtsensor).", "an der Anlage", "kleine Lampe + Sensor am Band"],
        ["Farbsensor", "Misst die Helligkeit des Klotzes.", "an der Anlage", "Sensor über dem Band"],
        ["Impulstaster", "Wird vom laufenden Band immer wieder gedrückt – so weiß der Pi, wie weit das Band gefahren ist.", "an der Anlage", "kleiner Taster am Bandantrieb"],
        ["Ventile + Kompressor", "Der Kompressor macht Druckluft, die Ventile lassen sie kurz zu den Auswerfern.", "an der Anlage", "Schläuche, kleine Zylinder"],
        ["MQTT-Broker (Mosquitto)", "„Postamt“ auf dem Pi: verteilt die Meldungen des Programms an den Bildschirm.", "laut Prof. Kampker installiert", "Programm auf dem Pi"],
        ["Peakboard Box", "Kleiner Kasten, der die Meldungen schön auf dem Bildschirm anzeigt.", "vorhanden (Lizenz)", "per HDMI am Bildschirm"]], 1):
    b.daten(z, i)

b.abschnitt("4. Nächste Woche: Code einspielen – genau in dieser Reihenfolge")
b.notiz("Wichtig: Zuerst muss das Team Hardware alles anschließen (Schritt 1). Vorher können wir nur Netzwerk und Programm prüfen, aber nichts an der Anlage testen. "
        "Stopp-Regel für alle Schritte: Ist etwas komisch (Geruch, Klotz klemmt, Motor brummt) → 9-V-Netzteil ziehen, erst fragen, dann weitermachen.")
b.kopf(["Schritt / Wer", "Was passiert (einfach erklärt)", "Bewegt sich etwas?", "Woran erkenne ich, dass es geklappt hat?"])
for i, z in enumerate([
        ["0 · Hardware-Team + P3", "Prüfen, ob alle bestellten Teile da sind. Klären, welches 9-V-Netzteil wir nehmen (steht nicht auf der Bestellliste).", "nein", "Alle Teile liegen auf dem Tisch."],
        ["1 · Team Hardware", "Strom aus. Beide Platinen über den Verteiler an den Pi stecken, Kabel nach dem Anschlussplan (Abschnitt 5) an die Klemmen.", "nein", "Foto vom Aufbau + Anschlussplan abgehakt in der Gruppe."],
        ["2 · Dogukan (P6)", "Doppelklick auf PI_EINRICHTEN.bat (Laptop im WLAN der Anlage, vorher Prof. Kampker kurz Bescheid geben). Das Programm macht alles allein: "
                                "unser Programm auf den Pi kopieren, Uhrzeit stellen, I2C einschalten, das Postamt (Mosquitto) für den Bildschirm freigeben, Tests. "
                                "Du tippst nur zweimal das Pi-Passwort.", "nein", "Am Ende „EINRICHTUNG OK“ und im Abschlusstest „ALLES GRÜN“. Startet der Pi neu: ca. 2 Minuten warten."],
        ["3 · P2 + Team Hardware", "Eingangs-Monitor starten. Jede Lichtschranke kurz abdecken, Taster drücken, Klötze unter den Farbsensor legen und Zahlen aufschreiben (T1–T4).", "nein – der Monitor schaltet nichts", "Zu jedem Sensor ändert sich genau eine Zahl. Werte stehen auf dem Zettel."],
        ["4 · Dogukan (P6) mit Claude", "Die gemessenen Werte ins Programm eintragen.", "nein", "Programm startet ohne Fehlermeldung."],
        ["5 · Alle – NUR mit Freigabe von Prof. Kampker", "Jeden Ausgang einzeln kurz einschalten: Band, jedes Ventil, Kompressor (T5, T6).", "JA – einzeln und kurz", "Band läuft in die richtige Richtung, jedes Ventil klickt hörbar."],
        ["6 · Alle", "Erster Sortiervorgang mit EINEM Klotz, danach mehrere Farben nacheinander.", "JA", "Klotz landet in der richtigen Rutsche, Bildschirm zeigt Zyklus 1."]], 1):
    b.daten(z, i)

b.abschnitt("5. Anschlussplan-Vorschlag für das Team Hardware (so ist das Programm eingestellt)")
b.kopf(["Teil der Anlage", "Neuer Anschluss (Vorschlag)", "Alter Anschluss am TXT", "Hinweis"])
for i, z in enumerate([
        ["Lichtschranke vor dem Farbsensor", "Automation HAT Mini – Eingang 1", "I1", "Digital (an/aus)"],
        ["Lichtschranke vor den Auswerfern", "Automation HAT Mini – Eingang 2", "I3", "Digital (an/aus)"],
        ["Impulstaster", "Automation HAT Mini – Eingang 3", "C1", "Digital, zählt die Wegstrecke"],
        ["Farbsensor", "Automation HAT Mini – Analog 1", "I2", "Liefert eine Spannung (Zahl)"],
        ["Ventil weiß", "Automation HAT Mini – Ausgang 1", "O5", "Ausgänge schalten nach Minus („sinking“) – Hardware-Team prüft die Verdrahtung"],
        ["Ventil rot", "Automation HAT Mini – Ausgang 2", "O6", "wie Ventil weiß"],
        ["Ventil blau", "Automation HAT Mini – Ausgang 3", "O7", "wie Ventil weiß"],
        ["Kompressor", "Automation HAT Mini – Relais (einziges)", "O8", "Relais, weil der Kompressor mehr Strom braucht"],
        ["Förderband-Motor", "Motor Driver HAT – Motor A", "M1", "Drehrichtung wird am Testtag eingestellt"],
        ["Lichtschranken der Lagerstellen", "nicht anschließen", "I6–I8", "laut Auftrag zunächst nicht im Umfang"]], 1):
    b.daten(z, i)
b.notiz("VORSCHLAG – das Team Hardware entscheidet. Wird etwas anders angeschlossen: einfach hier eintragen, das Programm wird angepasst (eine Zeile in config.py). "
        "Damit sind alle Klemmen des Mini belegt (3 Eingänge, 1 Analog von 3, 3 Ausgänge, 1 Relais). Offene Frage J6: Gehen Lichtschranken und Taster ohne Zusatzbauteile an die Eingänge?")

b.abschnitt("6. Welche Datei / welches Blatt ist wofür?")
b.kopf(["Datei / Blatt", "Wofür", "Brauche ich das?", "Wo"])
for i, z in enumerate([
        ["LIES MICH (dieses Blatt)", "Überblick in einfachen Worten, Ablauf nächste Woche, Anschlussplan", "Ja – zuerst lesen", "Excel"],
        ["GANTT (roter Reiter)", "Der Zeitplan: wer macht was bis wann (danach arbeiten wir) – mit Team-Tabelle und Namen", "Ja – deine Zeilen", "Excel + Drive"],
        ["ARBEITSKARTEN (grüner Reiter)", "Zu jeder Gantt-Aufgabe die Schritt-für-Schritt-Anleitung", "Ja – deine Karten", "Excel + Drive + PDF"],
        ["Anhang 10", "Alle Aufgaben mit Schritten: J = jetzt erledigen, T = beim Testen messen", "Ja – deine Zeilen", "Excel + Drive"],
        ["M2 2.1 – 2.4", "Je eine Liste zum Ausfüllen für Jan (P2), Marie (P3), Hassan (P5), Alhasane (P4)", "Ja – deine Liste", "Excel + Drive"],
        ["Leistungsnachweis (Blatt 1)", "Unsere Arbeitszeiten für Prof. Kampker", "Nur Rushit (Leitung)", "Excel"],
        ["Anhang 7", "Technik-Details: Netzwerk, Anschlüsse, Verbindungstest", "Nur bei Bedarf", "Excel"],
        ["Anhang 1 – 9, KI-Kontext", "Frühere Termine, Notizen, Kursmaterial, Zusammenfassung für KI-Assistenten", "Nein", "Excel"],
        ["PI_EINRICHTEN.bat", "Ein Doppelklick spielt alles auf den Pi und richtet ihn ein (kein Internet nötig)", "Dogukan (P6)", "Projektordner"],
        ["piverbindungtest1.bat / piverbindungtest2.bat", "Tests per Doppelklick: Pi erreichbar? Postamt (MQTT) und Platinen in Ordnung?", "Dogukan (P6)", "Projektordner"],
        ["Drive-Ordner", "Dieselben Aufgaben online zum gemeinsamen Bearbeiten", "Ja", "drive.google.com/drive/folders/1Y78I7ZrLTqD7yeOHkOy1qJUV80fm9HNn"]], 1):
    b.daten(z, i)

b.abschnitt("7. Wer macht was – Team und Rollen (Stand 17.10.2026)")
for lab, txt in [
        ("P1 – Rushit", "Leitung: koordiniert, beantwortet Fragen, spricht mit Prof. Kampker – hat bewusst KEINE eigenen Aufgaben im Gantt."),
        ("P2 – Jan", "Sensoren: Liste 2.1, Fragen ans Hardware-Team, am Einspieltag Sensoren messen, Peakboard-Texte/-Farben und Board prüfen."),
        ("P3 – Marie", "Aktoren + Draht zu Team Hardware: fragt Montag und Donnerstag nach (Liste HW1–HW10), Ausgänge testen, Peakboard Box aufbauen."),
        ("P4 – Alhasane", "Daten/Peakboard: Liste 2.4, Designer, Datenquelle, Board bauen und auf die Box laden, Abstimmung am Freitag."),
        ("P5 – Hassan", "Testen und Doku: Ablaufmodell 2.3, Entscheidungen J7–J9 vorstellen, Testplan, Dauertest, Doku, Probeabnahme, Peakboard-Abnahmetest."),
        ("P6 – Dogukan", "Pi, Netzwerk, Organisation: Freigaben bei Prof. Kampker, Internet, PI_EINRICHTEN, Testdaten, Einspieltag leiten, Feinschliff, Nacharbeiten."),
        ("Team Hardware", "Bestellung, Netzteil, Anschlussfragen, Anschluss nach Plan – P3 hält den Kontakt."),
        ("Claude (KI)", "Programm, Excel, Drive-Dateien, Auswertung der Berichte – über Rushit.")]:
    b.label(lab, txt)

b.abschnitt("8. Mini-Wörterbuch")
for lab, txt in [
        ("Sensor / Eingang", "Teil, das etwas MERKT und es dem Pi meldet (Lichtschranke, Farbsensor, Taster)."),
        ("Aktor / Ausgang", "Teil, das etwas TUT, wenn der Pi es einschaltet (Motor, Ventil, Kompressor)."),
        ("HAT", "Aufsteck-Platine für den Raspberry Pi („Hut“). Sie schützt den Pi, weil die Anlage mit 9 Volt läuft."),
        ("I2C", "Interne Leitung, über die der Pi mit den Platinen spricht (Farbsensor-Messung, Motor). Ab Werk aus – PI_EINRICHTEN schaltet sie ein."),
        ("Impuls", "Ein kurzes An-Aus-Signal. Viele Impulse zählen = Weg messen."),
        ("MQTT / Mosquitto", "Nachrichtensystem: unser Programm „schickt Briefe“ („Band läuft“, „Zyklus 5“, „Fehler“), Mosquitto auf dem Pi ist das Postamt, die Peakboard Box holt sie ab und zeigt sie an."),
        ("SSH", "Fernzugriff vom Laptop auf den Pi über das WLAN."),
        ("Simulation", "Das Programm tut so, als gäbe es die Anlage – zum gefahrlosen Testen ohne Hardware."),
        ("Freigabe", "Erlaubnis von Prof. Kampker, bevor sich zum ersten Mal etwas bewegt."),
        ("Zyklus", "Ein kompletter Sortiervorgang für einen Klotz.")]:
    b.label(lab, txt)

blatt_xml = b.xml().replace("FFC55A11", "FF2E7D32")      # grüner Reiter


def zelle(ref, text, st):
    return f'<c r="{ref}" s="{st}" t="inlineStr"><is><t xml:space="preserve">{escape(text)}</t></is></c>'


def setze(t, ref, text, st=None):
    m = re.search(rf'<c r="{ref}"( s="(\d+)")?[^>]*?(?:/>|>.*?</c>)', t, re.S)
    assert m, ref
    return t[:m.start()] + zelle(ref, text, st or m.group(2)) + t[m.end():]


def hoehe(t, r, h):
    return re.sub(rf'<row r="{r}"( ht="[\d.]+")?( customHeight="1")?', f'<row r="{r}" ht="{h}" customHeight="1"', t, count=1)


def anhang7(t):
    for ref, txt in [("E100", "Automation HAT Mini – Eingang 1 (VORSCHLAG)"), ("E101", "Automation HAT Mini – Analog 1 (VORSCHLAG)"),
                     ("E102", "Automation HAT Mini – Eingang 2 (VORSCHLAG)"), ("E106", "Automation HAT Mini – Eingang 3, Impulse zählen (VORSCHLAG)"),
                     ("E107", "Waveshare Motor Driver HAT – Motor A (bestellt)"), ("E108", "Automation HAT Mini – Ausgang 1 (VORSCHLAG)"),
                     ("E109", "Automation HAT Mini – Ausgang 2 (VORSCHLAG)"), ("E110", "Automation HAT Mini – Ausgang 3 (VORSCHLAG)"),
                     ("E111", "Automation HAT Mini – Relais 1 (VORSCHLAG)"),
                     ("H111", "Bestellliste 15.10.: Automation HAT Mini hat 1 Relais + 3 Ausgänge = 4 Lasten → passt genau, keine Reserve"),
                     ("D117", "Bestellliste 15.10.2026: Automation HAT Mini (3 digital, 3 analog, 3 Ausgänge, 1 Relais) + Waveshare Motor Driver HAT "
                              "+ GPIO-Multiplexer → Bedarf gedeckt, keine Reserve. Offen: Spannungen / Anschluss ohne Zusatzbauteile (Anhang 10, J6); 9-V-Netzteil.")]:
        t = setze(t, ref, txt)
    t = setze(t, "G111", "VORSCHLAG", 487)
    return hoehe(hoehe(t, "111", 45), "117", 90)


def ki(t):
    t = t.replace("Waveshare Motor Driver HAT SKU 15364. BESTÄTIGT",
                  "Waveshare Motor Driver HAT SKU 15364. BESTELLT laut Bestellliste 15.10.2026 (92,50 €): Automation HAT MINI (statt PIM213: 1 Relais), "
                  "Waveshare Motor Driver HAT, GPIO-Multiplexer, GPIO-Kabel, WAGO-Klemmen, Jumper-Kabel; kein 9-V-Netzteil auf der Liste. BESTÄTIGT")
    assert "BESTELLT laut Bestellliste" in t
    t = t.replace("(J1–J14)", "(J1–J16)")
    letzte = max(int(x) for x in re.findall(r'<row r="(\d+)"', t))
    zus = [("PLAN KW 43", "Code-Einspielung in der Woche ab 19.10.2026, sobald Team Hardware angeschlossen hat (Anhang 10 J15/J16). Ablauf Schritt 0–8 im Blatt "
                          "„LIES MICH - Einfach erklaert“ (erst prüfen und messen, dann mit Freigabe schalten)."),
           ("SHEET: LIES MICH", "Einfache Erklärung für Laien: Projekt in 4 Sätzen, Ablauf eines Zyklus, Teile, Ablauf Einspieltag, Anschlussplan-Vorschlag "
                                "(= Voreinstellung in config.py), Datei-Wegweiser, Aufgaben je Person, Wörterbuch.")]
    xml = ""
    for i, (l, v) in enumerate(zus, 1):
        r = letzte + i
        xml += f'<row r="{r}" ht="60" customHeight="1">{zelle(f"A{r}", l, LBL)}{zelle(f"B{r}", v, ROW)}</row>'
    t = t.replace("</sheetData>", xml + "</sheetData>")
    t = re.sub(r'<dimension ref="A1:B\d+"/>', f'<dimension ref="A1:B{letzte + len(zus)}"/>', t)
    return hoehe(t, "8", 120)


ZUSATZ11 = (" Bestellliste des Hardware-Teams ausgewertet (Automation HAT Mini, Waveshare Motor Driver HAT, GPIO-Verteiler, Kabel, Klemmen; "
            "9-V-Netzteil fehlt) und das Programm an die bestellte Hardware angepasst (Anschlussvorschlag, Ansteuerung des Motor Driver HAT, "
            "Ersatztest ohne Hardware bestanden). Code-Einspielung für die nächste Woche geplant – abhängig vom Anschluss durch Team Hardware. "
            "Einfache Erklärung für Einsteiger (Blatt „LIES MICH“) mit Ablauf des Einspieltags und Anschlussplan-Vorschlag erstellt.")


def seite1(t):
    m = re.search(r'(<c r="C11"[^>]*><is><t[^>]*>)(.*?)(</t>)', t, re.S)
    assert m and "Bestellliste" not in m.group(2)
    t = t[:m.end(2)] + escape(ZUSATZ11) + t[m.end(2):]
    return hoehe(t, "11", 215)


shutil.copy2(SRC, BAK)
zin = zipfile.ZipFile(BAK)
wb = zin.read("xl/workbook.xml").decode("utf-8")
rels = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
rid = re.search(rf'name="{NAME}"[^>]*r:id="(rId\d+)"', wb).group(1)
ziel = re.search(rf'Target="/?(xl/worksheets/sheet\d+\.xml)" Id="{rid}"', rels).group(1)
zout = zipfile.ZipFile(SRC, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d = zin.read(it.filename)
    if it.filename == ziel:
        d = blatt_xml.encode("utf-8")
    zout.writestr(zipfile.ZipInfo(it.filename, it.date_time), d, zipfile.ZIP_DEFLATED)
zout.close()
print("ok: ersetzt", ziel)
