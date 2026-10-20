"""Ergänzt karten_daten.py um Peakboard-Plan, Internet über Router, neue Karten und Vorlagen H/I (15.10.2026, nachmittags)."""
import karten_daten as K

S9 = ("S9", "Internet für die Anlage über den Router von Kleutges", "vor der Peakboard-Arbeit an der Anlage", "15 min",
      "1 LAN-Kabel, Erlaubnis von Kleutges (Besitzer des Routers mit Internet)",
      ["Kleutges fragen, ob wir einen freien LAN-Anschluss an seinem Router benutzen dürfen.",
       "LAN-Kabel: ein Ende in eine freie LAN-Buchse am Router von Kleutges (meist gelb, nummeriert 1–4).",
       "Anderes Ende in die WAN- bzw. Internet-Buchse an UNSEREM TP-Link-Router (meist blau, einzeln, „WAN“ oder Weltkugel).",
       "1–2 Minuten warten. Am TP-Link leuchtet dann das Internet- bzw. Weltkugel-Lämpchen.",
       "Laptop ins WLAN der Anlage (unser TP-Link) → im Browser eine Webseite öffnen. Lädt sie, ist Internet da.",
       "Doppelklick auf piverbindungtest1.bat: unten steht die aktuelle IP des Pi. Ist sie NICHT mehr 192.168.1.103, die neue Zahl in die Gruppe schreiben "
       "(unsere Programme finden den Pi trotzdem über seinen Namen).",
       "Danach PI_EINRICHTEN.bat ausführen (Karte S2) – mit Internet stellt es auch die Uhr und installiert Hilfsprogramme."],
      "Webseite lädt im Anlagen-WLAN und PI_EINRICHTEN meldet „Internet vorhanden“.",
      "Kein Internet-Lämpchen → Kabel in der richtigen Buchse? Hat der Router von Kleutges selbst Internet? Notfalls Karte S3 (Handy-Hotspot).",
      "An einem der beiden Router Einstellungen ändern.")
S10 = ("S10", "Testdaten für Peakboard laufen lassen", "sobald P4 im Designer arbeitet", "5 min, dann laufen lassen",
       "Laptop mit dem Ordner „projektmanagement“ (dort ist Python installiert)",
       ["Doppelklick auf „PEAKBOARD_TESTDATEN.bat“.",
        "Frage „Wo bist du?“: 1 = an der Anlage, 2 = zuhause → Zahl eintippen, Enter.",
        "Im Fenster erscheint ein grüner Kasten „DAS IM PEAKBOARD DESIGNER EINTRAGEN“ → Foto davon an P4 schicken.",
        "Fenster offen lassen, solange P4 baut (alle paar Sekunden ein neuer Klotz, jeder 8. ist eine Störung).",
        "Zum Beenden: Strg + C drücken, dann Fenster schließen."],
       "P4 sieht im Designer wechselnde Werte.",
       "„Python ist nicht installiert“ → den Laptop mit den Projektdateien nehmen. „Postamt nicht erreichbar“ an der Anlage → erst Karte S2.",
       "–")
P1_5 = ("P1-5", "Texte und Farben für den Bildschirm: Vorschlag kurz bewerten + Marie beim Designer helfen", "Mo 19.10.", "15 min + gemeinsamer Termin", "Vorlage H (ganz hinten in den Arbeitskarten)",
        ["Vorlage H lesen – das ist schon der fertige Vorschlag (Claude), welcher Zustand mit welchem Text und welcher Farbe angezeigt wird. Den nehmen wir.",
         "Kurz bewerten: „passt“ – oder 1–2 Sätze, was du ändern würdest. In die gelbe Spalte der To-do-Tabelle schreiben.",
         "Mit Marie einen Termin ausmachen und ZUSAMMEN den Peakboard Designer startklar machen (Karte P4-5): Konto klären, installieren, leeres Projekt anlegen."],
        "Bewertung steht in der To-do-Tabelle, Designer ist mit Marie eingerichtet.", "–", "Nicht alles neu erfinden – der Vorschlag gilt.")
P2_2 = ("P2-2", "ROBO-Pro-Programm – ERLEDIGT durch Claude (15.10.)", "–", "0 min", "–",
        ["Nichts mehr zu tun: Claude hat das Programm „Sorting Line“ direkt aus Moodle ausgelesen. Ergebnis: weiß < 1160 ≤ rot < 1500 ≤ blau, "
         "Impulse bis Ventil 5 / 15 / 26, Ventil 0,5 s – schon im Programm eingetragen."],
        "erledigt", "–", "–")
P2_5 = ("P2-5", "Board mit Testdaten prüfen", "So 18.10.", "20 min", "Videoanruf mit P4 (Bildschirm teilen) oder Screenshots",
        ["P4 zeigt die Vorschau des Boards (Bildschirm teilen).",
         "Prüfen: Steht „rot“ als letzte Farbe, ist die Kachel rot? Dasselbe für weiß und blau.",
         "Prüfen: Steigt „Sortierte Klötze“ jedes Mal um genau 1?",
         "Prüfen: Kommt bei der Störung das rote Banner – und verschwindet es danach wieder?",
         "Gefundene Fehler in die Gruppe schreiben."],
        "Alle Prüfungen stimmen.", "–", "–")
P3_4 = ("P3-4", "Peakboard Box und Bildschirm aufbauen", "vor P4-8", "20 min", "Peakboard Box mit Netzteil, Bildschirm, HDMI-Kabel, LAN-Kabel",
        ["Bildschirm aufstellen und einschalten.",
         "HDMI-Kabel von der Peakboard Box zum Bildschirm stecken.",
         "LAN-Kabel von der Box in eine freie LAN-Buchse unseres TP-Link-Routers.",
         "Netzteil an die Box. Nach 1–2 Minuten zeigt der Bildschirm ein Startbild der Box.",
         "Foto in die Gruppe. Steht auf dem Startbild eine IP-Adresse: notieren und an P4 schicken."],
        "Der Bildschirm zeigt das Startbild der Peakboard Box.", "Schwarzer Bildschirm → am Bildschirm den richtigen HDMI-Eingang wählen.",
        "Die Box aufschrauben.")
P4_5 = ("P4-5", "Peakboard Designer startklar machen", "Fr 16.10.", "30 min", "Windows-Laptop, Peakboard-Zugang von Prof. Kampker",
        ["Prof. Kampker fragen: „Mit welchem Peakboard-Konto melden wir uns im Designer an?“ (Lizenz der Hochschule).",
         "Peakboard Designer von peakboard.com herunterladen und installieren – oder den Laptop nehmen, auf dem er schon installiert ist.",
         "Designer starten und mit dem Konto anmelden.",
         "Neues Projekt anlegen: Name „Sortieranlage Team Software“, Bildschirmgröße 1920 × 1080."],
        "Das leere Projekt ist offen.", "Anmeldung klappt nicht → Prof. Kampker fragen oder help.peakboard.com.", "–")
P4_6 = ("P4-6", "Datenquelle MQTT anlegen", "Sa 17.10.", "30 min", "Foto mit den Einstellungen aus S10 (Testdaten laufen)",
        ["Im Designer: Data → Add data source → MQTT.",
         "Server wie im grünen Kasten (an der Anlage: IP des Pi; zuhause: test.mosquitto.org bzw. broker.hivemq.com). Port 1883. Benutzer und Passwort: an der Anlage den MQTT-Zugang von Prof. Kampker eintragen (steht aus Sicherheitsgründen NICHT in den Unterlagen – bei Rushit erfragen); zuhause beim öffentlichen Test-Postamt leer lassen.",
         "Subscriptions: jedes Topic aus dem grünen Kasten einzeln hinzufügen (…/wert/zustand, …/wert/zyklen usw.). QoS 0, Message type: Text.",
         "„Enable listener“ einschalten und auf Vorschau/Aktualisieren klicken: die Werte müssen sich alle paar Sekunden ändern.",
         "Datenquelle speichern."],
        "In der Vorschau ändern sich Zustand und Zykluszahl.",
        "Keine Werte → laufen die Testdaten (S10) noch? Server und Topics genau abgetippt (Groß-/Kleinschreibung)?",
        "Topics aus dem Kopf tippen – immer vom Foto abschreiben.")
P4_7 = ("P4-7", "Board gestalten (zusammen mit P1)", "So 18.10.", "1–2 Stunden", "Vorlage H, Bildschirm-Skizze aus P4-4",
        ["Kopfzeile: Text „Sortieranlage – Team Software HSNR“ und ein Uhrzeit-Element.",
         "Große Kachel „Zustand“: Textfeld mit …/wert/zustand verbinden.",
         "Bedingte Formatierung dieser Kachel: FEHLER → rot, BEREIT → grau, alles andere → grün; Texte laut Vorlage H.",
         "Kachel „Sortierte Klötze“: große Zahl mit …/wert/zyklen verbinden.",
         "Kachel „Letzte Farbe“ mit …/wert/farbe_letzte verbinden; bedingte Formatierung: weiss → weiß, rot → rot, blau → blau.",
         "Drei Zähler (oder ein Balkendiagramm) mit …/wert/anzahl_weiss, …/wert/anzahl_rot, …/wert/anzahl_blau verbinden.",
         "Rotes Banner unten mit …/wert/fehler_text – nur sichtbar, wenn …/wert/fehler_aktiv = 1.",
         "Fußzeile mit …/wert/modus und …/wert/fehler_anzahl.",
         "Vorschau starten und 5 Minuten zusehen: wechseln die Werte? Kommt bei jedem 8. Klotz das rote Banner?",
         "Screenshot in den Drive-Ordner."],
        "Die Vorschau zeigt alle Kacheln mit wechselnden Werten und das Störungsbanner.",
        "Bedingte Formatierung unklar → help.peakboard.com oder Screenshot an Claude.", "–")
P4_8 = ("P4-8", "Board auf die Peakboard Box laden", "wenn S2 erledigt ist und die Box steht (P3-4)", "30 min",
        "IP der Box (P4-1), Zugangsdaten der Box (Prof. Kampker)",
        ["An der Anlage: Laptop ins WLAN der Anlage.",
         "In der Datenquelle MQTT als Server die IP des Pi eintragen (NICHT das Test-Postamt von zuhause).",
         "Im Designer die Box hinzufügen (IP der Box + Box-Benutzer/-Passwort von Prof. Kampker – bei Rushit erfragen, NICHT aufschreiben oder in die Gruppe posten).",
         "Board auf die Box hochladen.",
         "Am Bildschirm prüfen: Das Board erscheint und zeigt Werte (an der Anlage Testdaten aus S10 oder echte Werte)."],
        "Das Board läuft auf dem Bildschirm an der Anlage.", "Box nicht gefunden → im selben Netz? IP richtig (P4-1)?",
        "An der Box Einstellungen ändern, die nicht abgesprochen sind.")
P5_3 = ("P5-3", "Peakboard-Abnahmetest (Kursfolie 8)", "wenn das Board auf der Box läuft", "30 min", "Vorlage I ausgedruckt",
        ["Vorlage I ausdrucken.",
         "Jede der 7 Fragen mit Softwareleitung und P4 durchgehen und ankreuzen.",
         "Für Frage 6: Pi kurz neu starten bzw. das Netzwerkkabel der Box kurz ziehen – kommt das Board von allein wieder?",
         "Foto der Checkliste und Screenshot in den Drive-Ordner."],
        "Alle 7 Punkte abgehakt.", "Ein Punkt klappt nicht → Foto an Claude.", "–")

P3_0 = ("P3-0", "Draht zu Team Hardware (ab jetzt, jeden Montag und Donnerstag)", "laufend bis 20.11.", "10 min pro Termin",
        "Excel-Blatt „GANTT ab 15.10 (krit. Pfad)“, Liste „Was wir von Team Hardware brauchen“, Vorlage J",
        ["Heute: Vorlage J (unten im Gantt-Blatt) kopieren und an Team Hardware schicken – damit wissen sie alle Termine.",
         "Jeden Montag und Donnerstag: kurz bei Team Hardware nachfragen „Wie weit seid ihr mit HW…?“ (die nächsten offenen Punkte der Liste).",
         "Antwort in die Liste eintragen (Spalten „gefragt am“ und „Antwort / Stand“) – oder an Claude schicken, Claude trägt ein.",
         "Ist eine Hardware-Aufgabe fertig: im Gantt bei H1–H7 den Status auf „fertig“ setzen (Zelle anklicken → Pfeil → „fertig“).",
         "Wird ein ROTER Termin (HW3, HW4, HW5) nicht geschafft: SOFORT der Softwareleitung schreiben – dann planen wir um.",
         "Im Regelmeeting am Dienstag kurz berichten: Was ist fertig? Was hakt?"],
        "Alle HW-Punkte haben eine Antwort, H1–H7 stehen auf „fertig“.",
        "Team Hardware antwortet nicht → nach 1 Tag nochmal fragen, dann Softwareleitung informieren (die spricht Prof. Kampker an).",
        "Selbst Kabel umstecken oder Hardware-Aufgaben übernehmen, ohne Absprache.")
H = ("H", "Texte und Farben für den Bildschirm (für P1-5 und P4-7) – VORSCHLAG", [
    "BEREIT → „Bereit – Klotz auflegen“ (grau)",
    "FOERDERN → „Fördert“ (grün)   ·   ZAEHLEN → „Fährt zum Auswerfer“ (grün)   ·   AUSSCHLEUSEN → „Sortiert aus“ (grün)   ·   PRUEFEN → „Prüft“ (grün)",
    "FEHLER → „STÖRUNG“ (rot)   ·   AUS → „Aus“ (dunkelgrau)",
    "Letzte Farbe: weiss → weiße Kachel, rot → rote Kachel, blau → blaue Kachel, – → grau",
    "Betriebsart: sim → „Testbetrieb (Simulation)“, hardware → „Echtbetrieb“",
    "Störungsbanner: rot, weiße Schrift, Text aus …/wert/fehler_text, nur sichtbar bei …/wert/fehler_aktiv = 1",
    "Aufteilung 1920 × 1080: Kopfzeile · Zustand (groß, links) · Sortierte Klötze (Mitte) · Letzte Farbe (rechts) · 3 Zähler · Störungsbanner · Fußzeile"])
I = ("I", "Abnahme-Checkliste Peakboard (für P5-3, nach Kursfolie 8)", [
    "☐ 1. Broker (Postamt) erreichbar? (piverbindungtest2 „ALLES GRÜN“)",
    "☐ 2. Testnachricht kommt beim Postamt an? (piverbindungtest2, Schritt „Test auf dem Pi“)",
    "☐ 3. Peakboard empfängt Nachrichten?",
    "☐ 4. Werte werden richtig angezeigt (Zustand, Zahl, Farbe, Störung)?",
    "☐ 5. Bildschirm aktualisiert sich von selbst?",
    "☐ 6. Nach Neustart des Pi bzw. kurzer Netzunterbrechung läuft alles von allein weiter?",
    "☐ 7. Keine doppelten Zählungen (Zahl steigt pro Klotz um genau 1)?",
    "Geprüft am: ________   von: ______________________"])

PEAKBOARD_PLAN = [
    ("1", "S9", "Softwareleitung", "Internet für die Anlage über den Router von Kleutges"),
    ("2", "S2", "Softwareleitung", "Pi einrichten (PI_EINRICHTEN) – Postamt wird fürs Netz freigegeben"),
    ("3", "P4-5", "P4", "Peakboard Designer startklar machen"),
    ("4", "S10", "Softwareleitung", "Testdaten laufen lassen (geht auch zuhause)"),
    ("5", "P4-6", "P4", "Datenquelle MQTT im Designer anlegen"),
    ("6", "P1-5", "P1", "Texte und Farben festlegen"),
    ("7", "P4-7", "P4 + P1", "Board gestalten"),
    ("8", "P2-5", "P2", "Board mit Testdaten prüfen"),
    ("9", "P3-4", "P3", "Peakboard Box und Bildschirm aufbauen"),
    ("10", "P4-1", "P4", "IP-Adresse der Box herausfinden"),
    ("11", "P4-8", "P4", "Board auf die Box laden"),
    ("12", "P5-3", "P5 bzw. Softwareleitung", "Abnahmetest Peakboard"),
    ("13", "–", "alle", "Später: echte Daten statt Simulation (nach dem Hardware-Einspieltag, Board bleibt gleich)"),
]
PEAKBOARD_ERKLAERUNG = [
    "Teil 1 – Daten senden: FERTIG. Unser Programm auf dem Pi schickt Zustand, Zykluszahl, Farbe und Störungen als Nachrichten.",
    "Teil 2 – Postamt (Mosquitto auf dem Pi): installiert; PI_EINRICHTEN gibt es fürs Netz frei.",
    "Teil 3 – Board bauen im Peakboard Designer: kann SOFORT beginnen – mit Testdaten, auch zuhause.",
    "Teil 4 – Board auf die Box laden, Bildschirm per HDMI: sobald Box und Pi im selben Netz sind.",
    "Wenn später die echte Anlage läuft, bleibt das Board gleich – es kommen nur echte statt Test-Werte.",
]


def anwenden():
    p = dict(K.PERSONEN)
    sl = p["Softwareleitung (Rushit)"]
    i = [k[0] for k in sl].index("S3")
    sl[i] = (sl[i][0], "OPTIONAL: Pi kurz über Handy-Hotspot ins Internet (nur falls S9 nicht geht und Prof. Kampker Ja sagt)") + sl[i][2:]
    sl.insert(i, S9)
    sl.append(S10)
    p["P1 – Prozesslogik"].append(P1_5)
    p2 = p["P2 – Sensoren / Eingänge"]
    p2[[k[0] for k in p2].index("P2-2")] = P2_2
    p2.append(P2_5)
    p["P3 – Aktoren / Ausgänge"].insert(0, P3_0)
    p["P3 – Aktoren / Ausgänge"].append(P3_4)
    p["P4 – Daten / Peakboard"].extend([P4_5, P4_6, P4_7, P4_8])
    p["P5 – Testen / Doku (falls niemand P5 ist: Softwareleitung)"].append(P5_3)
    K.VORLAGEN.insert(len(K.VORLAGEN) - 1, H)
    K.VORLAGEN.insert(len(K.VORLAGEN) - 1, I)
    K.PEAKBOARD_PLAN = PEAKBOARD_PLAN
    K.PEAKBOARD_ERKLAERUNG = PEAKBOARD_ERKLAERUNG
    K.EINLEITUNG[3] = "Texte zum Kopieren (Nachrichten, Testplan, Messprotokoll, Bildschirm-Texte, Checkliste, Schild) stehen am Ende unter VORLAGEN A–I."
