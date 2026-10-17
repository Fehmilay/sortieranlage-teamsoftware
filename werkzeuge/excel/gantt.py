"""Gantt-Plan ab 15.10.2026 mit kritischem Pfad (Netzplan in Arbeitstagen).
Erzeugt: Excel-Blatt (selbst aktualisierend), Druck-HTML (Wochenansicht) und Drive-HTML.
Aufruf: python gantt.py <druck.html> <drive.html> [<xlsx> <backup>]
"""
import datetime as dt
import math
import re
import shutil
import sys
import zipfile
from html import escape as h
from xml.sax.saxutils import escape as x

D = dt.date
START, ENDE = D(2026, 10, 12), D(2027, 2, 7)
PAUSE = (D(2026, 12, 21), D(2027, 1, 1))                 # Weihnachtspause: keine Arbeit eingeplant
DEADLINE = D(2027, 2, 2)


def arbeitstag(t):
    return t.weekday() < 5 and not (PAUSE[0] <= t <= PAUSE[1])


TAGE = [START + dt.timedelta(n) for n in range((ENDE - START).days + 1)]
AT = [t for t in TAGE if arbeitstag(t)]
IDX = {t: i for i, t in enumerate(AT)}


def erster_at(t):
    while not arbeitstag(t):
        t += dt.timedelta(1)
    return IDX[t]


# (nr, phase, aufgabe, wer, dauer_AT, vorgaenger, nicht_vor, status, karte)
AUFGABEN = [
    ("F0", "0 Erledigt", "Software vorbereitet: Programm, Tests, Einrichtungsprogramm, Arbeitskarten (Claude + Softwareleitung)", "Softwareleitung", 3, [], D(2026, 10, 13), "fertig", "–"),
    ("V1", "1 Vorbereitung", "Freigaben bei Prof. Kampker holen (Mail mit 5 Fragen)", "Softwareleitung", 4, [], D(2026, 10, 15), "läuft", "S1"),
    ("V2", "1 Vorbereitung", "M2-Listen 2.1–2.4 fertig machen + Abstimmung am Freitag", "P1–P4", 5, [], D(2026, 10, 13), "läuft", "P1-3, P2-3, P3-2, P4-4"),
    ("V3", "1 Vorbereitung", "Regelmeeting: Entscheidungen J7–J9 und Nachrichtenformat", "alle", 1, ["V2"], D(2026, 10, 20), "offen", "P1-1, P4-3"),
    ("H1", "2 Team Hardware (P3 fragt nach)", "Bestellung auslösen (Bestellliste 92,50 €)", "Team Hardware", 1, [], D(2026, 10, 16), "offen", "P3-1"),
    ("H2", "2 Team Hardware (P3 fragt nach)", "Lieferung der Teile abwarten", "Lieferant", 2, ["H1"], None, "offen", "P3-1"),
    ("H3", "2 Team Hardware (P3 fragt nach)", "9-V-Netzteil klären und bereitlegen", "Team Hardware", 3, [], D(2026, 10, 16), "offen", "P3-1"),
    ("H4", "2 Team Hardware (P3 fragt nach)", "Anschlussfragen beantworten (Spannungen, geht es ohne Zusatzbauteile?)", "Team Hardware", 3, [], D(2026, 10, 16), "offen", "P2-1"),
    ("H5", "2 Team Hardware (P3 fragt nach)", "Anschlussplan bestätigen oder ändern (Vorlage F)", "Team Hardware + P3", 1, ["H4"], None, "offen", "H-1"),
    ("H6", "2 Team Hardware (P3 fragt nach)", "Hardware anschließen: Platinen auf den Pi, Kabel an die Klemmen", "Team Hardware", 1, ["H2", "H3", "H5"], None, "offen", "H-1"),
    ("H7", "2 Team Hardware (P3 fragt nach)", "Sichtprüfung, Foto, Übergabe an Team Software", "Team Hardware + P3", 1, ["H6"], None, "offen", "H-1"),
    ("N1", "3 Pi und Netzwerk", "Internet für die Anlage über den Router von Kleutges", "Softwareleitung", 1, [], D(2026, 10, 19), "offen", "S9"),
    ("N2", "3 Pi und Netzwerk", "Pi einrichten mit PI_EINRICHTEN (ein Doppelklick)", "Softwareleitung", 1, ["V1", "N1"], None, "offen", "S2"),
    ("E1", "4 Einspielen auf echter Hardware", "Eingänge prüfen und messen – nichts bewegt sich (T1–T4), Werte ins Programm", "P2 + Team Hardware", 1, ["H7", "N2"], None, "offen", "P2-4"),
    ("E2", "4 Einspielen auf echter Hardware", "Programmteile für die Entscheidungen J7–J9 (Claude)", "Softwareleitung", 4, ["V3"], None, "offen", "J14"),
    ("E3", "4 Einspielen auf echter Hardware", "Ausgänge einzeln testen – NUR mit Freigabe (T5, T6)", "P3 + Prof. Kampker", 1, ["E1"], None, "offen", "P3-3"),
    ("E4", "4 Einspielen auf echter Hardware", "Erster Sortiervorgang, dann mehrere Farben und ein Fehlerfall", "alle", 2, ["E3", "E2"], None, "offen", "S8"),
    ("B1", "5 Peakboard (parallel)", "Peakboard Designer startklar machen", "P4", 2, [], D(2026, 10, 16), "offen", "P4-5"),
    ("B2", "5 Peakboard (parallel)", "Board mit Testdaten bauen (Datenquelle, Kacheln, Farben)", "P4 + P1", 4, ["B1"], None, "offen", "P4-6, P4-7, P1-5"),
    ("B3", "5 Peakboard (parallel)", "Board mit Testdaten prüfen", "P2", 1, ["B2"], None, "offen", "P2-5"),
    ("B4", "5 Peakboard (parallel)", "Peakboard Box und Bildschirm aufbauen", "P3", 1, [], D(2026, 10, 21), "offen", "P3-4"),
    ("B5", "5 Peakboard (parallel)", "Board auf die Peakboard Box laden", "P4", 1, ["B3", "B4", "N2"], None, "offen", "P4-8"),
    ("B6", "5 Peakboard (parallel)", "Peakboard-Abnahmetest (7 Punkte)", "P5 bzw. Softwareleitung", 2, ["B5", "E4"], None, "offen", "P5-3"),
    ("T1", "6 Testen und Verbessern", "Dauertest: viele Klötze, alle Farben, alle Fehlerfälle (To-Dos 6.1–6.4)", "P1–P4", 15, ["E4"], None, "offen", "–"),
    ("T2", "6 Testen und Verbessern", "Feinschliff: Werte nachstellen, Neustart/Netzausfall testen, Autostart im Echtbetrieb", "Softwareleitung + P5", 10, ["T1"], None, "offen", "–"),
    ("A1", "7 Doku und Abnahme", "Doku für ein anderes Team: Starten, Bedienen, Fehler beheben", "P5 + alle", 11, ["T2"], None, "offen", "–"),
    ("A2", "7 Doku und Abnahme", "Probeabnahme intern (alles einmal wie bei der echten Abnahme)", "alle", 3, ["A1", "B6"], D(2027, 1, 4), "offen", "–"),
    ("A3", "7 Doku und Abnahme", "Nacharbeiten + Puffer (Fehler aus der Probeabnahme beheben)", "alle", None, ["A2"], None, "offen", "–"),
    ("A4", "7 Doku und Abnahme", "ABNAHME beim Auftraggeber (Prof. Kampker)", "alle", 1, ["A3"], DEADLINE, "offen", "–"),
]

# ---------------------------------------------------------------- Netzplan (kritischer Pfad)
A = {a[0]: dict(nr=a[0], phase=a[1], text=a[2], wer=a[3], dauer=a[4], vor=a[5], nichtvor=a[6], status=a[7], karte=a[8]) for a in AUFGABEN}
for nr in A:                                           # Vorwärtsrechnung
    a = A[nr]
    es = erster_at(a["nichtvor"]) if a["nichtvor"] else 0
    for v in a["vor"]:
        es = max(es, A[v]["ef"] + 1)
    a["es"] = es
    if a["dauer"] is None:                             # Puffer-Aufgabe füllt bis zum Tag vor der Abnahme
        a["dauer"] = IDX[DEADLINE] - es
    a["ef"] = es + a["dauer"] - 1
nach = {nr: [m for m in A if nr in A[m]["vor"]] for nr in A}
for nr in reversed(list(A)):                           # Rückwärtsrechnung
    a = A[nr]
    a["lf"] = min((A[m]["ls"] - 1 for m in nach[nr]), default=IDX[DEADLINE])
    a["ls"] = a["lf"] - a["dauer"] + 1
    a["puffer"] = a["ls"] - a["es"]
for a in A.values():
    a["kritisch"] = a["puffer"] == 0 and a["status"] != "fertig"
    a["start"], a["ende"] = AT[a["es"]], AT[a["ef"]]
KRIT = [a["nr"] for a in A.values() if a["kritisch"]]

ERKLAERUNG = [
    ("Was ist das?", "Ein Kalender für unser Projekt. Links steht die Aufgabe, rechts zeigt ein farbiger Balken, von wann bis wann sie läuft. "
                     "Ganz rechts ist die Abnahme am 02.02.2027 – da müssen wir fertig sein."),
    ("Farben", "ROT = kritischer Pfad (siehe unten). BLAU = normale Aufgabe. GRÜN = fertig. GELB = heute. GRAU = Wochenende bzw. Weihnachtspause. "
               "ORANGE (Zeile R) = Regelmeeting jeden Dienstag."),
    ("Kritischer Pfad", "Die Kette von Aufgaben, die direkt hintereinander hängen und KEINEN Puffer haben: Ist eine rote Aufgabe auch nur einen Tag zu spät, "
                        "wird ALLES danach zu spät – bis zur Abnahme. Bei uns: Team Hardware beantwortet die Anschlussfragen → bestätigt den Plan → schließt an "
                        "→ wir messen → testen die Ausgänge → erster Sortiervorgang → Dauertest → Feinschliff → Doku → Probeabnahme → Abnahme."),
    ("Puffer", "So viele Arbeitstage darf sich eine BLAUE Aufgabe verspäten, ohne dass etwas Schlimmes passiert. Rote Aufgaben haben 0 Tage Puffer."),
    ("Wichtigste Erkenntnis", "Am Anfang hängt alles an Team Hardware. Deshalb fragt P3 als „Draht zu Team Hardware“ zweimal pro Woche nach "
                              "(Liste „Was wir von Team Hardware brauchen“ weiter unten) und trägt den Stand hier ein."),
    ("So arbeitest du damit", "1) Montags schaut jeder auf seine Zeilen (Spalte „Wer“). 2) Spalte „Status“ setzen: offen / läuft / fertig / verspätet "
                              "(Zelle anklicken, Pfeil, auswählen). 3) Wird etwas später fertig: das Ende-Datum ändern – der Balken wandert von selbst. "
                              "4) Ist eine ROTE Aufgabe in Gefahr: SOFORT der Softwareleitung schreiben. 5) Jeden Dienstag im Regelmeeting gehen wir das Diagramm "
                              "gemeinsam durch; Claude rechnet den kritischen Pfad danach neu."),
    ("Karte", "Die Spalte „Karte“ sagt, auf welcher Arbeitskarte (Blatt ARBEITSKARTEN) die Schritt-für-Schritt-Anleitung steht."),
]

HW = [  # was wir von Team Hardware brauchen (P3 fragt nach)
    ("HW1", "Bestätigung: Bestellung ist raus + Liefertermin", "ohne Teile kein Anschluss", "Fr 16.10."),
    ("HW2", "Welches 9-V-Netzteil nehmen wir? (steht nicht auf der Bestellliste)", "ohne Strom läuft nichts", "Di 20.10."),
    ("HW3", "Antworten auf die Anschlussfragen (Vorlage E): Spannungen, geht es ohne Zusatzbauteile?", "ROT – davon hängt der Anschluss ab", "Di 20.10."),
    ("HW4", "Anschlussplan bestätigt oder geändert (Vorlage F)", "ROT – danach wird verkabelt", "Mi 21.10."),
    ("HW5", "Hardware angeschlossen + Foto + Sichtprüfung", "ROT – danach können wir messen", "Fr 23.10."),
    ("HW6", "Zusage: jemand von Team Hardware ist am Mo 26.10. (Messen) und Di 27.10. (Ausgänge testen) dabei", "Fehler an Kabeln findet nur Team Hardware", "Fr 23.10."),
    ("HW7", "Was ist Motor M2? (das alte Programm schaltet ihn 3 Sekunden)", "sonst fehlt evtl. ein Teil der Anlage", "Fr 23.10."),
    ("HW8", "Pneumatik in Ordnung? Kompressor, Schläuche dicht, Ventile gehen", "sonst klemmt das Ausschleusen", "Fr 23.10."),
    ("HW9", "Hilfe bei Fehlersuche an Kabeln während der Testphase", "Dauertest braucht stabile Verkabelung", "19.11. (laufend)"),
    ("HW10", "Verdrahtungsplan als Foto/Skizze für die Doku (To-Do 5.3)", "die Doku muss ein anderes Team befähigen", "Fr 20.11."),
]
NACHRICHT_P3 = [
    "Hallo Team Hardware, ich (P3) bin ab jetzt euer Ansprechpartner aus Team Software. Unser Zeitplan hängt am Anfang komplett an euch – "
    "deshalb hier alles, was wir brauchen, mit Termin:",
] + [f"{n}) {w} – bis {b}" for n, (_, w, _, b) in enumerate(HW, 1)] + [
    "Ich frage jeden Montag und Donnerstag kurz nach. Wenn ein Termin nicht klappt, sagt bitte sofort Bescheid – dann planen wir um. Danke!"]


# ---------------------------------------------------------------- HTML (Wochenansicht)
def wochen():
    w, t = [], START
    while t <= ENDE:
        w.append(t)
        t += dt.timedelta(7)
    return w


def html(einfach=False):
    ws = wochen()
    kopf = "".join(f"<th>KW{w.isocalendar()[1]}<br>{w:%d.%m.}</th>" for w in ws)
    zeilen, phase = [], None
    for a in A.values():
        if a["phase"] != phase:
            phase = a["phase"]
            zeilen.append(f'<tr><td colspan="{6 + len(ws)}" bgcolor="#1f4e79" style="background-color:#1f4e79;color:#fff"><b>{h(phase)}</b></td></tr>')
        zellen = ""
        for w in ws:
            an = a["start"] <= w + dt.timedelta(6) and a["ende"] >= w
            farbe = ("#70ad47" if a["status"] == "fertig" else "#c00000" if a["kritisch"] else "#4472c4") if an else ("#e7e6e6" if PAUSE[0] <= w <= PAUSE[1] else "#ffffff")
            zellen += f'<td bgcolor="{farbe}" style="background-color:{farbe}">&nbsp;</td>'
        krit = "<b>JA</b>" if a["kritisch"] else "nein"
        zeilen.append(f"<tr><td>{a['nr']}</td><td>{h(a['text'])}</td><td>{h(a['wer'])}</td><td>{a['start']:%d.%m.}–{a['ende']:%d.%m.}</td>"
                      f"<td>{a['puffer']}</td><td>{krit}</td>{zellen}</tr>")
    tab = (f'<table border="1" cellpadding="3" style="border-collapse:collapse;font-size:9pt"><tr><th>Nr</th><th>Aufgabe</th><th>Wer</th>'
           f'<th>von–bis</th><th>Puffer (AT)</th><th>Kritisch</th>{kopf}</tr>{"".join(zeilen)}</table>')
    erkl = "".join(f"<p><b>{h(k)}:</b> {h(v)}</p>" for k, v in ERKLAERUNG)
    hw = ('<table border="1" cellpadding="4" style="border-collapse:collapse"><tr><th>Nr</th><th>Was wir von Team Hardware brauchen</th><th>Warum</th><th>bis</th><th>gefragt am</th><th>Antwort / Stand</th></tr>'
          + "".join(f"<tr><td>{n}</td><td>{h(w)}</td><td>{h(g)}</td><td>{h(b)}</td><td>&nbsp;</td><td>&nbsp;</td></tr>" for n, w, g, b in HW) + "</table>")
    msg = "".join(f"<p>{h(z)}</p>" for z in NACHRICHT_P3)
    css = ("" if einfach else "<style>@page{size:A3 landscape;margin:10mm} body{font-family:'Segoe UI',Arial,sans-serif;font-size:10pt} "
           "h1{background:#1f4e79;color:#fff;padding:8px 12px;border-radius:5px;font-size:16pt} h2{color:#1f4e79;margin-top:14px} "
           "td,th{vertical-align:top} th{background:#dbe9f6} .neu{page-break-before:always}</style>")
    teile = [f"<h1>Gantt-Plan Sortieranlage ab 15.10.2026 – mit kritischem Pfad (ab jetzt arbeiten wir danach)</h1>",
             f"<p><b>Kritischer Pfad (rot):</b> {' → '.join(KRIT)}. Die Abnahme ist am 02.02.2027. Weihnachtspause 21.12.–01.01. ist nicht eingeplant. AT = Arbeitstage.</p>",
             tab, '<h2 class="neu">Erklärung für alle (ganz einfach)</h2>', erkl,
             "<h2>Was wir von Team Hardware brauchen – P3 fragt nach (Montag + Donnerstag)</h2>", hw,
             "<h2>Vorlage J – Nachricht von P3 an Team Hardware (kopieren)</h2>", msg]
    return f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Gantt</title>{css}</head><body>{"".join(teile)}</body></html>'


open(sys.argv[1], "w", encoding="utf-8").write(html())
open(sys.argv[2], "w", encoding="utf-8").write(html(einfach=True))
print("Kritischer Pfad:", " -> ".join(KRIT))
for a in A.values():
    print(f"{a['nr']:3} {a['start']:%a %d.%m.}–{a['ende']:%a %d.%m.%y}  Puffer {a['puffer']:3}  {'KRIT' if a['kritisch'] else ''}  {a['text'][:55]}")

# ---------------------------------------------------------------- Excel-Blatt
if len(sys.argv) > 4:
    SRC, BAK = sys.argv[3], sys.argv[4]
    NAME = "GANTT ab 15.10 (krit. Pfad)"
    TITLE, SUB, SEC, HEAD, ROW, ROW2, NOTE, LBL = 478, 479, 480, 481, 484, 485, 486, 496

    def col(i):
        s, i = "", i + 1
        while i:
            i, r = divmod(i - 1, 26)
            s = chr(65 + r) + s
        return s

    def serial(t):
        return (t - D(1899, 12, 30)).days

    zin = zipfile.ZipFile(SRC)
    styles = zin.read("xl/styles.xml").decode("utf-8")
    # neue Zahlenformate, Zellformate und bedingte Formate
    styles = styles.replace('<numFmt numFmtId="166" formatCode=";;;"/></numFmts>',
                            '<numFmt numFmtId="166" formatCode=";;;"/><numFmt numFmtId="167" formatCode="d"/></numFmts>').replace('<numFmts count="3">', '<numFmts count="4">')
    n_xf = int(re.search(r'<cellXfs count="(\d+)"', styles).group(1))
    neue_xf = [
        '<xf numFmtId="165" fontId="3" fillId="0" borderId="65" applyNumberFormat="1" applyAlignment="1" xfId="0"><alignment horizontal="center" vertical="top"/></xf>',  # Datum
        '<xf numFmtId="167" fontId="1" fillId="36" borderId="65" applyNumberFormat="1" applyAlignment="1" xfId="0"><alignment horizontal="center" vertical="center"/></xf>',  # Tag
        '<xf numFmtId="0" fontId="3" fillId="0" borderId="65" applyAlignment="1" xfId="0"><alignment horizontal="center" vertical="center"/></xf>',  # Zelle zentriert
        '<xf numFmtId="0" fontId="1" fillId="36" borderId="65" applyAlignment="1" xfId="0"><alignment horizontal="center" vertical="center"/></xf>',  # Kopf zentriert
    ]
    X_DATUM, X_TAG, X_MITTE, X_KOPFM = range(n_xf, n_xf + 4)
    styles = re.sub(r'(<cellXfs count=")\d+(">.*?)(</cellXfs>)', lambda m: f'{m.group(1)}{n_xf + 4}{m.group(2)}{"".join(neue_xf)}{m.group(3)}', styles, flags=re.S)
    n_dxf = int(re.search(r'<dxfs count="(\d+)"', styles).group(1))
    farben = ["FF70AD47", "FFC00000", "FF4472C4", "FFED7D31", "FFFFE699", "FFE7E6E6"]
    dxf = "".join(f'<dxf><fill><patternFill><bgColor rgb="{f}"/></patternFill></fill></dxf>' for f in farben)
    styles = re.sub(r'(<dxfs count=")\d+(">.*?)(</dxfs>)', lambda m: f'{m.group(1)}{n_dxf + len(farben)}{m.group(2)}{dxf}{m.group(3)}', styles, flags=re.S)
    DX_GRUEN, DX_ROT, DX_BLAU, DX_ORANGE, DX_GELB, DX_GRAU = range(n_dxf, n_dxf + 6)

    K0 = 11                                   # erste Tagesspalte (L) – Spalten A..K = 11 Spalten
    breiten = [6, 48, 18, 10, 9, 9, 6, 7, 8, 10, 17]
    N = len(TAGE)
    rows, merges = [], []

    def c(ref, wert, st, art="s"):
        if wert is None or wert == "":
            return f'<c r="{ref}" s="{st}"/>'
        if art == "n":
            return f'<c r="{ref}" s="{st}"><v>{wert}</v></c>'
        if art == "f":
            return f'<c r="{ref}" s="{st}"><f>{x(wert)}</f></c>'
        return f'<c r="{ref}" s="{st}" t="inlineStr"><is><t xml:space="preserve">{x(str(wert))}</t></is></c>'

    def zeile(r, zellen, ht=None):
        rows.append(f'<row r="{r}"' + (f' ht="{ht}" customHeight="1"' if ht else "") + f'>{"".join(zellen)}</row>')

    letzte_spalte = col(K0 + N - 1)
    zeile(1, [c("A1", "GANTT-Plan Sortieranlage ab 15.10.2026 – mit kritischem Pfad (ab jetzt arbeiten wir danach)", TITLE)], 28)
    merges.append("A1:K1")
    zeile(2, [c("A2", "ROT = kritischer Pfad (kein Puffer – jede Verspätung verschiebt die Abnahme) · BLAU = Aufgabe mit Puffer · GRÜN = fertig · "
                      "GELB = heute · GRAU = Wochenende/Pause · ORANGE = Regelmeeting. Erklärung für alle: unter der Tabelle.", SUB)], 32)
    merges.append("A2:K2")
    # Kopf: KW / Tag / Wochentag
    kw, tag, wt = [c(f"{col(i)}3", "", X_KOPFM) for i in range(K0)], [], []
    for i, t in enumerate(TAGE):
        ref = col(K0 + i)
        if t.weekday() == 0 or i == 0:
            kw.append(c(f"{ref}3", f"KW {t.isocalendar()[1]}", X_KOPFM))
            ende = min(i + (6 - t.weekday()), N - 1)
            if ende > i:
                merges.append(f"{ref}3:{col(K0 + ende)}3")
        else:
            kw.append(c(f"{ref}3", "", X_KOPFM))
        tag.append(c(f"{ref}4", serial(t), X_TAG, "n"))
        wt.append(c(f"{ref}5", "MDMDFSS"[t.weekday()], X_KOPFM))
    kopf = ["Nr", "Aufgabe (einfach erklärt)", "Wer", "Vorgänger", "Start", "Ende", "Arb.-tage", "Puffer (AT)", "Kritisch?", "Status", "Karte"]
    zeile(3, kw, 18)
    zeile(4, [c(f"{col(i)}4", kopf[i], HEAD) for i in range(K0)] + tag, 30)
    zeile(5, [c(f"{col(i)}5", "", X_KOPFM) for i in range(K0)] + wt, 16)
    for i in range(K0):
        merges.append(f"{col(i)}4:{col(i)}5")
    r, phase, erste = 6, None, 6
    leer_tage = lambda r: [c(f"{col(K0 + i)}{r}", "", X_MITTE) for i in range(N)]
    for a in A.values():
        if a["phase"] != phase:
            phase = a["phase"]
            zeile(r, [c(f"A{r}", phase, SEC)] + [c(f"{col(i)}{r}", "", SEC) for i in range(1, K0)] + leer_tage(r), 20)
            r += 1
        st = ROW
        zellen = [c(f"A{r}", a["nr"], X_MITTE), c(f"B{r}", a["text"], st), c(f"C{r}", a["wer"], st), c(f"D{r}", ", ".join(a["vor"]) or "–", X_MITTE),
                  c(f"E{r}", serial(a["start"]), X_DATUM, "n"), c(f"F{r}", serial(a["ende"]), X_DATUM, "n"),
                  c(f"G{r}", f"NETWORKDAYS(E{r},F{r})", X_MITTE, "f"), c(f"H{r}", a["puffer"], X_MITTE, "n"),
                  c(f"I{r}", "JA" if a["kritisch"] else "nein", X_MITTE), c(f"J{r}", a["status"], X_MITTE), c(f"K{r}", a["karte"], ROW)]
        zeile(r, zellen + leer_tage(r), 30)
        r += 1
    zeile(r, [c(f"A{r}", "R", X_MITTE), c(f"B{r}", "Regelmeeting (jeden Dienstag) – Gantt gemeinsam durchgehen", ROW), c(f"C{r}", "alle", ROW)]
          + [c(f"{col(i)}{r}", "", X_MITTE) for i in range(3, K0)] + leer_tage(r), 32)
    letzte = r
    bereich = f"{col(K0)}{erste}:{letzte_spalte}{letzte}"
    L, Z = col(K0), erste
    cf = (f'<conditionalFormatting sqref="{bereich}">'
          f'<cfRule type="expression" dxfId="{DX_GRAU}" priority="1" stopIfTrue="1"><formula>OR(WEEKDAY({L}$4,2)&gt;5,AND({L}$4&gt;={serial(PAUSE[0])},{L}$4&lt;={serial(PAUSE[1])}))</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{DX_GRUEN}" priority="2" stopIfTrue="1"><formula>AND({L}$4&gt;=$E{Z},{L}$4&lt;=$F{Z},$J{Z}="fertig")</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{DX_ROT}" priority="3" stopIfTrue="1"><formula>AND({L}$4&gt;=$E{Z},{L}$4&lt;=$F{Z},$I{Z}="JA")</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{DX_BLAU}" priority="4" stopIfTrue="1"><formula>AND($E{Z}&gt;0,{L}$4&gt;=$E{Z},{L}$4&lt;=$F{Z})</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{DX_ORANGE}" priority="5" stopIfTrue="1"><formula>AND($A{Z}="R",WEEKDAY({L}$4,2)=2)</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{DX_GELB}" priority="6" stopIfTrue="1"><formula>{L}$4=TODAY()</formula></cfRule>'
          f'</conditionalFormatting>'
          f'<conditionalFormatting sqref="{col(K0)}3:{letzte_spalte}5"><cfRule type="expression" dxfId="{DX_GELB}" priority="7"><formula>{L}$4=TODAY()</formula></cfRule></conditionalFormatting>')
    dv = (f'<dataValidations count="1"><dataValidation type="list" allowBlank="1" showErrorMessage="1" sqref="J{erste}:J{letzte}">'
          f'<formula1>"offen,läuft,fertig,verspätet"</formula1></dataValidation></dataValidations>')
    # Erklärung, Hardware-Liste, Nachricht
    r = letzte + 2
    zeile(r, [c(f"A{r}", "ERKLÄRUNG FÜR ALLE (ganz einfach)", SEC)] + [c(f"{col(i)}{r}", "", SEC) for i in range(1, K0)], 22); merges.append(f"A{r}:K{r}"); r += 1
    for k, v in ERKLAERUNG:
        zeile(r, [c(f"A{r}", k, LBL), c(f"B{r}", "", LBL), c(f"C{r}", v, ROW)] + [c(f"{col(i)}{r}", "", ROW) for i in range(3, K0)], max(32, math.ceil(len(v) / 120) * 15 + 8))
        merges += [f"A{r}:B{r}", f"C{r}:K{r}"]; r += 1
    r += 1
    zeile(r, [c(f"A{r}", "WAS WIR VON TEAM HARDWARE BRAUCHEN – P3 fragt nach (jeden Montag und Donnerstag) und trägt die Antwort ein", SEC)]
          + [c(f"{col(i)}{r}", "", SEC) for i in range(1, K0)], 22); merges.append(f"A{r}:K{r}"); r += 1
    zeile(r, [c(f"A{r}", "Nr", HEAD), c(f"B{r}", "Was wir brauchen", HEAD), c(f"C{r}", "Warum", HEAD), c(f"D{r}", "", HEAD), c(f"E{r}", "bis", HEAD),
              c(f"F{r}", "", HEAD), c(f"G{r}", "gefragt am", HEAD), c(f"H{r}", "", HEAD), c(f"I{r}", "Antwort / Stand", HEAD), c(f"J{r}", "", HEAD), c(f"K{r}", "", HEAD)], 20)
    merges += [f"C{r}:D{r}", f"E{r}:F{r}", f"G{r}:H{r}", f"I{r}:K{r}"]; r += 1
    for j, (n, w, g, b) in enumerate(HW):
        st = ROW if j % 2 == 0 else ROW2
        zeile(r, [c(f"A{r}", n, st), c(f"B{r}", w, st), c(f"C{r}", g, st), c(f"D{r}", "", st), c(f"E{r}", b, st), c(f"F{r}", "", st),
                  c(f"G{r}", "", st), c(f"H{r}", "", st), c(f"I{r}", "", st), c(f"J{r}", "", st), c(f"K{r}", "", st)], 32)
        merges += [f"C{r}:D{r}", f"E{r}:F{r}", f"G{r}:H{r}", f"I{r}:K{r}"]; r += 1
    r += 1
    zeile(r, [c(f"A{r}", "VORLAGE J – Nachricht von P3 an Team Hardware (kopieren)", SEC)] + [c(f"{col(i)}{r}", "", SEC) for i in range(1, K0)], 22)
    merges.append(f"A{r}:K{r}"); r += 1
    for z in NACHRICHT_P3:
        zeile(r, [c(f"A{r}", z, ROW)] + [c(f"{col(i)}{r}", "", ROW) for i in range(1, K0)], 30 if len(z) > 120 else 18)
        merges.append(f"A{r}:K{r}"); r += 1

    colsxml = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(breiten))
    colsxml += f'<col min="{K0 + 1}" max="{K0 + N}" width="3.3" customWidth="1"/>'
    heute = TAGE.index(D(2026, 10, 15)) if D(2026, 10, 15) in TAGE else 0
    blatt = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<sheetPr><tabColor rgb="FFC00000"/><pageSetUpPr fitToPage="1"/></sheetPr>'
             f'<dimension ref="A1:{letzte_spalte}{r}"/>'
             '<sheetViews><sheetView showGridLines="0" workbookViewId="0">'
             f'<pane xSplit="{K0}" ySplit="5" topLeftCell="{col(K0 + max(0, heute - 3))}6" activePane="bottomRight" state="frozen"/>'
             '<selection pane="topRight"/><selection pane="bottomLeft"/>'
             f'<selection pane="bottomRight" activeCell="{col(K0)}6" sqref="{col(K0)}6"/></sheetView></sheetViews>'
             f'<sheetFormatPr defaultRowHeight="15"/><cols>{colsxml}</cols><sheetData>{"".join(rows)}</sheetData>'
             f'<mergeCells count="{len(merges)}">{"".join(f"<mergeCell ref=\"{m}\"/>" for m in merges)}</mergeCells>'
             f'{cf}{dv}<pageMargins left="0.3" right="0.3" top="0.4" bottom="0.4" header="0.2" footer="0.2"/>'
             '<pageSetup paperSize="8" orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>')

    shutil.copy2(SRC, BAK)
    zin = zipfile.ZipFile(BAK)
    wb = zin.read("xl/workbook.xml").decode()
    rels = zin.read("xl/_rels/workbook.xml.rels").decode()
    ct = zin.read("[Content_Types].xml").decode()
    ersatz = None
    if f'name="{NAME}"' in wb:
        rid = re.search(rf'name="{re.escape(NAME)}"[^>]*r:id="(rId\d+)"', wb).group(1)
        ersatz = re.search(rf'Target="/?(xl/worksheets/sheet\d+\.xml)" Id="{rid}"', rels).group(1)
    else:
        nr = max(int(re.search(r"sheet(\d+)\.xml", n).group(1)) for n in zin.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)) + 1
        rid = max(int(v) for v in re.findall(r'Id="rId(\d+)"', rels)) + 1
        sid = max(int(v) for v in re.findall(r'sheetId="(\d+)"', wb)) + 1
        rels = rels.replace("</Relationships>", f'<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                                                f'Target="/xl/worksheets/sheet{nr}.xml" Id="rId{rid}"/></Relationships>')
        m = re.search(r'<sheet [^>]*name="ARBEITSKARTEN"', wb)
        wb = wb[:m.start()] + (f'<sheet xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" name="{x(NAME)}" '
                               f'sheetId="{sid}" state="visible" r:id="rId{rid}"/>') + wb[m.start():]
        ct = ct.replace("</Types>", f'<Override PartName="/xl/worksheets/sheet{nr}.xml" '
                                    f'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        neu_teil = f"xl/worksheets/sheet{nr}.xml"
    zout = zipfile.ZipFile(SRC, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        d = zin.read(it.filename)
        if it.filename == "xl/workbook.xml": d = wb.encode()
        elif it.filename == "xl/_rels/workbook.xml.rels": d = rels.encode()
        elif it.filename == "[Content_Types].xml": d = ct.encode()
        elif it.filename == "xl/styles.xml": d = styles.encode()
        elif it.filename == ersatz: d = blatt.encode()
        zout.writestr(zipfile.ZipInfo(it.filename, it.date_time), d, zipfile.ZIP_DEFLATED)
    if ersatz is None:
        zout.writestr(zipfile.ZipInfo(neu_teil, (2026, 10, 15, 0, 0, 0)), blatt.encode(), zipfile.ZIP_DEFLATED)
    zout.close()
    print("Excel ok:", ersatz or neu_teil, "| Zeilen bis", r, "| Tagesspalten", N)
