"""Verteilt die Arbeitskarten auf P2–P6 (Leitung ohne Gantt-Aufgaben), Stand 15.10.2026 nachmittags."""
import re

import karten_daten as K

TEAM = {
    "P1": "Rushit Vlasi (Leitung)",
    "P2": "Jan",
    "P3": "Marie",
    "P4": "Alhasane",
    "P5": "Hassan",
    "P6": "Dogukan",
}
UMBENENNEN = {   # alte Karte -> neue Karte
    "S1": "P6-1", "S9": "P6-2", "S2": "P6-3", "S3": "P6-4", "S10": "P6-5", "S8": "P6-6",
    "P1-1": "P5-4", "P1-2": "P5-5", "P1-3": "P5-6", "P1-4": "P4-9", "P1-5": "P2-6",
    "S4": "L-1", "S5": "L-2", "S6": "L-3", "S7": "L-4",
}
TEXTE = [  # gezielte Textanpassungen in Karten-Schritten
    ("Die Softwareleitung startet den Eingangs-Monitor", "Dogukan (P6) startet mit Claude den Eingangs-Monitor"),
    ("Einspieltag mit der Softwareleitung absprechen", "Einspieltag mit Dogukan (P6) absprechen"),
    ("Strom erst wieder einstecken, wenn die Softwareleitung dabei ist.", "Strom erst wieder einstecken, wenn Dogukan (P6) dabei ist."),
    ("mit Softwareleitung und P4 durchgehen", "mit Dogukan (P6) und P4 durchgehen"),
    ("Board gestalten (zusammen mit P1)", "Board gestalten (Texte und Farben kommen von P2)"),
    ("Ergebnis an P4 (für das Board) und in die Gruppe.", "Ergebnis an P4 (für das Board) und in die Gruppe."),
    ("SOFORT der Softwareleitung schreiben", "SOFORT Rushit (Leitung) schreiben"),
    ("dann Softwareleitung informieren (die spricht Prof. Kampker an).", "dann Rushit (Leitung) informieren – Rushit spricht dann Prof. Kampker an."),
    ("„M2 2.3 Ablaufmodell (P1)“", "„M2 2.3 Ablaufmodell (P1)“ (alter Dateiname – ist jetzt Hassans Liste)"),
    ("PI_EINRICHTEN (Softwareleitung)", "PI_EINRICHTEN (Dogukan, P6)"),
    ("E-Mail-Adressen von P1–P4", "E-Mail-Adressen von P2–P6 (inkl. Hassan und Dogukan)"),
    ("Namen von P1–P4 an Claude schicken – Claude trägt sie in Excel (Anhang 10, „Wer macht was?“) ein",
     "Namen von P2–P4 an Claude schicken – Claude trägt sie im Gantt-Blatt (Team-Tabelle) ein"),
    ("„Python ist nicht installiert“ → den Laptop mit den Projektdateien nehmen.",
     "„Python ist nicht installiert“ → Python von python.org installieren (beim Installieren den Haken „Add Python to PATH“ setzen)."),
]
ORDNER_SCHRITT = ("Einmalig vorher: den Ordner „projektmanagement“ von Rushit bekommen (USB-Stick oder ZIP) und auf den eigenen Desktop kopieren – "
                  "alle .bat-Dateien liegen darin.")


def _neu_id(t):
    for alt, neu in sorted(UMBENENNEN.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"(?<![\w-]){re.escape(alt)}(?![\w-])", neu, t)
    return t


def _text(t):
    for a, b in TEXTE:
        t = t.replace(a, b)
    return _neu_id(t)


def umverteilen():
    alle = {}
    for person, karten in K.PERSONEN:
        for k in karten:
            alle[k[0]] = k
    def karte(alt):
        nr, titel, bis, dauer, brauchst, schritte, fertig, problem, nicht = alle[alt]
        neu = UMBENENNEN.get(nr, nr)
        schritte = [_text(s) for s in schritte]
        if neu.startswith("P6-") and neu in ("P6-3", "P6-4", "P6-5", "P6-2"):
            schritte = [ORDNER_SCHRITT] + schritte
        return (neu, _text(titel), _text(bis), dauer, _text(brauchst), schritte, _text(fertig), _text(problem), _text(nicht))
    T = TEAM
    K.PERSONEN = [
        (f"P2 – {T['P2']} – Sensoren / Eingänge", [karte(n) for n in ["P2-1", "P2-2", "P2-3", "P2-4", "P2-5", "P1-5"]]),
        (f"P3 – {T['P3']} – Aktoren / Ausgänge + Draht zu Team Hardware", [karte(n) for n in ["P3-0", "P3-1", "P3-2", "P3-3", "P3-4"]]),
        (f"P4 – {T['P4']} – Daten / Peakboard", [karte(n) for n in ["P4-1", "P4-2", "P4-3", "P4-4", "P4-5", "P4-6", "P4-7", "P4-8", "P1-4"]]),
        (f"P5 – {T['P5']} – Testen, Doku, Abläufe", [karte(n) for n in ["P5-1", "P5-2", "P5-3", "P1-1", "P1-2", "P1-3"]]),
        (f"P6 – {T['P6']} – Pi, Netzwerk, Organisation", [karte(n) for n in ["S1", "S9", "S2", "S3", "S10", "S8"]]),
        ("Team Hardware (P3 hält Kontakt)", [karte("H-1")]),
        (f"Leitung – {T['P1']} – nur Verwaltung der eigenen Unterlagen, keine Gantt-Aufgaben", [karte(n) for n in ["S4", "S5", "S6", "S7"]]),
    ]
    wer_neu = {"Softwareleitung": "P6 Dogukan", "P1": "P5 Hassan", "P4 + P1": "P4", "P5 bzw. Softwareleitung": "P5 Hassan"}
    kurz = {"P2": "P2", "P3": "P3", "P4": "P4", "P5": "P5 Hassan", "P6": "P6 Dogukan"}
    K.PEAKBOARD_PLAN = [(a, _neu_id(b), kurz.get(_neu_id(b)[:2], wer_neu.get(c, c)), _text(d)) for a, b, c, d in K.PEAKBOARD_PLAN]
    K.PEAKBOARD_ERKLAERUNG = [_text(x) for x in K.PEAKBOARD_ERKLAERUNG]
    K.VORLAGEN = [(b, _text(t), [_text(z) for z in zeilen]) for b, t, zeilen in K.VORLAGEN]
    K.EINLEITUNG = [
        "Jede Person hat eigene Karten. Eine Karte = eine Aufgabe. Einfach Schritt für Schritt abarbeiten und abhaken.",
        "Team: P1 Rushit (Leitung, koordiniert – keine eigenen Gantt-Aufgaben) · P2 Jan · P3 Marie · P4 Alhasane · P5 Hassan · P6 Dogukan.",
        "Unklar? NICHT raten – Frage in die Gruppe oder an Rushit. Fertig? „Erledigt + Datum“ in die Gruppe schreiben und im Gantt den Status auf „fertig“ setzen.",
        "Alles, was Programm, Excel und Drive-Dateien betrifft, erledigt Claude (KI-Assistent der Leitung). Hier steht nur, was Menschen tun müssen.",
        "Texte zum Kopieren (Nachrichten, Testplan, Messprotokoll, Bildschirm-Texte, Checkliste, Schild) stehen am Ende unter VORLAGEN A–I.",
    ]
