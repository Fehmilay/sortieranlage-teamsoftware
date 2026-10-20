"""Archiv: Aufgaben KW 42 (bis Di 20.10.2026) mit Stand der Rückmeldungen vom 20.10."""
STAND_DATUM = "Di 20.10.2026"
BIS = "Dienstag 20.10.2026 (Regelmeeting)"
# Zweizeiler (max. 2 Zeilen): Was haben wir erreicht, wenn alle die Ziele dieser Woche schaffen? Steht unten auf Blatt 2 (Abgabe) und im To-do-Block.
ZIEL = ("Ziel bis Di 20.10.2026 – wenn alle ihre Aufgaben schaffen: Listen 2.1–2.4 fertig, Freigaben von Prof. Kampker und Antworten von Team Hardware liegen vor, "
        "Peakboard läuft mit Testdaten – damit kann Team Hardware ab 21.10. anschließen und wir ab 26.10. auf der echten Anlage testen.")
GH = "https://github.com/Fehmilay/sortieranlage-teamsoftware/blob/main/"
GH_START = "https://github.com/Fehmilay/sortieranlage-teamsoftware"
TODO_SHEET_URL = "https://docs.google.com/spreadsheets/d/1MI7Egtn5bykn7BOq3XI69zSVreS4dCe1AguFCColf-I"   # Abhak-Liste im Drive (17.10.)

# Ziel -> (Excel-Blatt bzw. URL, Anzeigetext)
ZIELE = {
    "KARTEN": ("ARBEITSKARTEN", "→ Karten"),
    "GANTT": ("GANTT ab 15.10 (krit. Pfad)", "→ GANTT"),
    "LIESMICH": ("LIES MICH - Einfach erklaert", "→ LIES MICH"),
    "A10": ("Anhang 10 - Auftraege M2", "→ Anhang 10"),
    "M21": ("M2 2.1 Input-Liste (P2)", "→ Liste 2.1"),
    "M22": ("M2 2.2 Output-Liste (P3)", "→ Liste 2.2"),
    "M23": ("M2 2.3 Ablaufmodell (Hassan)", "→ Liste 2.3"),
    "M24": ("M2 2.4 Datenpunkte (P4)", "→ Liste 2.4"),
    "GH": (GH_START, "→ GitHub"),
    "GH_PB": (GH + "peakboard/MQTT_Schnittstelle.md", "→ GitHub: Peakboard"),
    "GH_TD": (GH + "PEAKBOARD_TESTDATEN.ps1", "→ GitHub: Testdaten"),
}
# Drive-Fassung: Google-Dateien statt Excel-Blätter (IDs der M2-Tabellen vom 13.10.)
DRIVE = {
    "M21": "https://docs.google.com/spreadsheets/d/1q92NFAx_uGRmlY2XTzdVFWz8aC2DhSuJ8EVyvWZ8ouA",
    "M22": "https://docs.google.com/spreadsheets/d/1tKzMXjdTDKlp0g0ragU7pb0srB4rPkYWy0mnweGGo5k",
    "M23": "https://docs.google.com/spreadsheets/d/1zO7ygc6XWWHZVU45HBLI9078lFZZ4RExi0XJrcu7XSs",
    "M24": "https://docs.google.com/spreadsheets/d/17C2LRRfTtDszVhvl3QhIWhoc7F6n0rwVwuxH1X5XtpY",
    "A10": "https://docs.google.com/document/d/1-5F8SC5UActX2wZ9pChN4gzXffhrMuJimg8n9YQHCmA",
    "LIESMICH": "https://docs.google.com/document/d/1i2OrFtgO_htB23cnSGMUsUedySec6s13XYgyj92SBBk",
    "GANTT_DOC": "https://docs.google.com/document/d/1Pi6jj2J9udxW2zTxtTb2pkYBHdnaFa-hsEqna9pGLF0",
    "KARTEN": GH + "Arbeitskarten/Arbeitskarten_Schritt_fuer_Schritt_Stand_15-10-2026.pdf",
    "GANTT": GH + "Gantt/Gantt_Plan_ab_15-10-2026_mit_kritischem_Pfad.pdf",
}

# (Person, [(Nr, Bis, Was tun, Ziel)])
TODOS = [
    ("P6 – Dogukan (Pi, Netzwerk, Organisation)", [
        ("T1", "Mo 19.10.", "Mail an Prof. Kampker (Vorlage A, Karte P6-1). MQTT- und Box-Zugang haben wir schon (bei Rushit). Nur noch fragen: "
                            "Freigabe für den Ausgänge-Test am Di 27.10.? WLAN-Passwort der Anlage? IP-Adresse der Peakboard Box? Wer hat den Peakboard Designer?", "KARTEN"),
        ("T2", "Di 20.10.", "„Wie spielen wir den Code auf den Pi?“ – LIES MICH (Abschnitt 4) und Karte P6-3 (PI_EINRICHTEN) durchlesen. "
                            "Rückmeldung: Ist der Ablauf klar? Was fehlt dir noch?", "LIESMICH"),
        ("T3", "Mo 19.10.", "Internet für die Anlage über den Router von Kleutges einrichten (Karte P6-2) – nur an der Anlage möglich.", "KARTEN"),
        ("T4", "Di 20.10.", "Testdaten für Peakboard laufen lassen: PEAKBOARD_TESTDATEN.bat (Karte P6-5) – geht auch zuhause. Ordner vorher von Rushit holen.", "GH_TD"),
    ]),
    ("P5 – Hassan (Testen, Doku, Abläufe)", [
        ("T5", "Di 20.10.", "Liste 2.3 Ablaufmodell lesen (15–20 min): Tabelle ist schon ausgefüllt, 6 Zeilen = 6 Schritte eines Klotzes. Nur die Spalten „Zustand“, „Was passiert hier?“ und „Nächster Zustand“ lesen – wie eine Geschichte. Kürzel (I1, M1 …) muss man nicht verstehen. Letzte Spalte: „passt“ oder Frage. Gemeinsam anschauen im Regelmeeting (Karte P5-6).", "M23"),
        ("T6", "Di 20.10.", "Im Regelmeeting die 3 Entscheidungen J7–J9 vorstellen (Vorlage B, Karte P5-4).", "A10"),
        ("T7", "Di 20.10.", "GitHub-Seite öffnen und die Startseite (README) lesen – nur lesen, nichts ändern. "
                            "Rückmeldung: Was ist unklar? Wie sollen wir weitermachen?", "GH"),
    ]),
    ("P2 – Jan (Sensoren / Eingänge + Bildschirm-Texte)", [
        ("T8", "Mo 19.10.", "Liste 2.1 Sensoren fertig machen (Karte P2-3).", "M21"),
        ("T9", "Mo 19.10.", "Vorschlag für Texte und Farben auf dem Bildschirm (Vorlage H, ganz hinten in den Arbeitskarten) kurz bewerten: „passt“ oder 1–2 Änderungen. Danach mit Marie zusammen den Peakboard Designer startklar machen (Karte P2-6 + P4-5).", "KARTEN"),
        ("T10", "Di 20.10.", "LIES MICH und deine Arbeitskarten (P2-…) durchlesen. Rückmeldung: Was verstehst du nicht?", "LIESMICH"),
    ]),
    ("P3 – Alhasane (Aktoren / Ausgänge + Draht zu Team Hardware)", [
        ("T11", "Mo 19.10.", "WICHTIG (roter Pfad im Gantt): Team Hardware anschreiben (Vorlage J, Karte P3-0): Bestellung raus? Liefertermin? "
                             "Welches 9-V-Netzteil? Anschlussfragen bis Di 20.10. beantworten? Am Do 22.10. nochmal nachfragen. Antworten rechts eintragen.", "KARTEN"),
        ("T12", "Mo 19.10.", "Liste 2.2 Aktoren fertig machen (Karte P3-2).", "M22"),
        ("T13", "Di 20.10.", "Gantt durchsehen (rote Zeilen = kritischer Pfad). Rückmeldung: Sind die Termine von Team Hardware realistisch?", "GANTT"),
    ]),
    ("P4 – Marie (Daten / Peakboard)", [
        ("T14", "Mo 19.10.", "Liste 2.4 Datenpunkte fertig machen (Karte P4-4).", "M24"),
        ("T15", "sofort", "Abstimmung vom Fr 16.10. (Karte P4-9): Hat sie stattgefunden? Wenn nein: bis Mo 19.10. nachholen (20 min online). Ergebnis rechts eintragen.", "KARTEN"),
        ("T16", "Mo 19.10.", "ZUSAMMEN MIT JAN den Peakboard Designer startklar machen (Karte P4-5): Prof. Kampker fragen, mit welchem Konto wir uns anmelden; Designer installieren (Windows-Laptop); leeres Projekt „Sortieranlage Team Software“ anlegen. Den MQTT-Zugang bekommst du von Rushit.", "KARTEN"),
        ("T17", "Di 20.10.", "Peakboard-Beschreibung auf GitHub lesen. Rückmeldung: Welches Nachrichten-Format (A, B oder C) nehmen wir fürs Board?", "GH_PB"),
    ]),
    ("ALLE (außer Rushit)", [
        ("T18", "Di 20.10.", "Vor dem Regelmeeting: eigene Zeilen auf „erledigt“ setzen, Fragen rechts eintragen. Rushit gibt sie an Claude weiter – "
                             "die Antwort steht danach hier.", "GANTT"),
    ]),
]
WER_KURZ = {"P2": "Jan (P2)", "P3": "Alhasane (P3)", "P4": "Marie (P4)", "P5": "Hassan (P5)", "P6": "Dogukan (P6)", "AL": "ALLE"}
# Stand der Rückmeldungen (Claude überträgt hier, was im Drive eingetragen wurde): Nr -> (Status, Erledigt am, Rückmeldung)
STAND = {   # übertragen aus der Drive-Tabelle am 20.10.2026
    "T1": ("offen", "", "Dogukan hat keinen Drive-Zugang – bekommt die Aufgabe direkt von Rushit."),
    "T2": ("offen", "", "Dogukan bekommt die Aufgabe direkt von Rushit."),
    "T3": ("offen", "", "Dogukan bekommt die Aufgabe direkt von Rushit."),
    "T4": ("offen", "", "Dogukan bekommt die Aufgabe direkt von Rushit."),
    "T5": ("erledigt", "19.10.", "Ablaufmodell gelesen – gemeinsame Durchsicht im Regelmeeting 20.10."),
    "T6": ("in Arbeit", "", ""),
    "T7": ("erledigt", "18.10.", ""),
    "T8": ("erledigt", "", ""),
    "T9": ("offen", "", "Vorschlag aus Vorlage H gilt – Jan bewertet nur kurz und richtet mit Marie den Peakboard Designer ein (20.10. in der VL)."),
    "T10": ("erledigt", "", ""),
    "T11": ("erledigt", "17.10.", "Team Hardware ist angeschrieben. Bitte die ANTWORTEN von Team Hardware hier eintragen (Bestellung, Netzteil, Anschlussfragen)."),
    "T12": ("erledigt", "18.10.", ""),
    "T13": ("offen", "", ""),
    "T14": ("erledigt", "18.10.", "Bildschirmskizze von Marie liegt im Drive (Bildschirmskizze.png)."),
    "T15": ("offen", "", ""),
    "T16": ("Frage/Problem", "", "Marie: Designer läuft auf dem HSNR-Laptop, geht erst am 20.10. in der VL. – Claude: Passt. Am 20.10. in der VL zusammen mit Jan "
                                "einrichten und das leere Projekt anlegen."),
    "T17": ("erledigt", "19.10.", "Marie: A ist einfacher, aber nicht so umfangreich wie C – A versuchen, sonst C. – Claude: Einverstanden (Entscheidung J12 = A). "
                                  "Der Pi schickt A, B und C gleichzeitig, Umstellen geht also jederzeit ohne Programmänderung."),
}

