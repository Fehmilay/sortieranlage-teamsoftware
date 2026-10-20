"""To-do-Liste fürs Team (bis zum nächsten Regelmeeting) – EINE Datenquelle für
  a) den Block unten auf Seite 1 der Excel (Leistungsnachweis, ab Zeile 27, außerhalb des Druckbereichs) und
  b) eine kleine xlsx, die als Google-Tabelle in den Drive-Ordner kommt (dort hakt das Team ab).

Aufruf (im Ordner werkzeuge\\excel):
  python todo_team.py excel <xlsx> <backup.xlsx>
  python todo_team.py drive <ziel.xlsx> [<drive_links.json>]
Live-Pflege: Aufgaben/Status/Rückmeldungen unten in TODOS und STAND ändern, dann beide Befehle erneut ausführen.
"""
import json, os, re, shutil, sys, zipfile
from xml.sax.saxutils import escape

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

KOPF = ["Wer", "Bis", "Was tun (einfach erklärt) – Anleitung steht in der genannten Karte", "Öffnen (klicken)",
        "Status (Pfeil)", "Erledigt am", "Deine Rückmeldung / Frage an Claude (hier reinschreiben)"]
STATUS_LISTE = '"offen,in Arbeit,erledigt,Frage/Problem"'
ANLEITUNG = ("So geht's: 1) Such deinen Namen in Spalte A. 2) Klick in Spalte D auf den Link – dann öffnet sich genau das Blatt bzw. die Datei. "
             "3) Die Schritte stehen in der genannten Arbeitskarte. 4) In Spalte E den Status wählen (Zelle anklicken → Pfeil). "
             "5) Gelbe Felder: Datum und Rückmeldung bzw. Frage eintragen. Rushit (Leitung) hat diese Woche keine eigenen Aufgaben "
             "und hält den Draht zu Claude: Fragen aus Spalte G werden beantwortet und hier aktualisiert.")


# ---- Daten der laufenden Woche kommen aus woche.py (überschreibt die Werte oben) ----
from woche import WOCHE, STAND_DATUM, BIS, ZIEL, TODOS, STAND, WER_KURZ, KOPF, ANLEITUNG, REITER
import woche as _w
TODO_SHEET_URL = _w.TODO_SHEET_URL   # Link der Wochen-Tabelle (leer bis zum Upload)
for _r in [r[0] for r in REITER] + ["TO-DO"]:
    ZIELE["R:" + _r] = (TODO_SHEET_URL, "→ Reiter „" + _r + "“")


def _str(f, t):
    return escape(f'"{t}"') if f else escape(t)


def zeilen_daten(links):
    """Liefert Liste von ('abschnitt', text) bzw. ('todo', [werte], (ziel, anzeige))."""
    aus = []
    for person, todos in TODOS:
        aus.append(("abschnitt", person))
        for nr, bis, text, ziel in todos:
            st, am, rm = STAND.get(nr, ("offen", "", ""))
            wer = WER_KURZ.get(person[:2], person.split(" (")[0])
            aus.append(("todo", [f"{nr} {wer}", bis, text, None, st, am, rm], links(ziel)))
    return aus


def cell(ref, s, text=None, formel=None, wert=None):
    if formel:
        return f'<c r="{ref}" s="{s}" t="str"><f>{escape(formel)}</f><v>{escape(wert or "")}</v></c>'
    if text in (None, ""):
        return f'<c r="{ref}" s="{s}"/>'
    return f'<c r="{ref}" s="{s}" t="inlineStr"><is><t xml:space="preserve">{escape(str(text))}</t></is></c>'


def link_formel(ziel, anzeige):
    if ziel.startswith("http"):
        return f'HYPERLINK("{ziel}","{anzeige}")'
    return f"HYPERLINK(\"#'{ziel}'!A1\",\"{anzeige}\")"


def hoehe(text, breite):
    import math
    return max(30, 15 * sum(max(1, math.ceil(len(t) / (breite * 1.1))) for t in str(text).split("\n")) + 6)


def block_xml(start, st, links, breiten):
    """st: dict mit Stil-Indizes title, sub, sec, head, row, input, link. Gibt (rows, merges, erste, letzte Datenzeile)."""
    rows, merges, r = [], [], start
    def zeile(xml, h):
        rows.append(f'<row r="{r}" ht="{h:.0f}" customHeight="1">{xml}</row>')
    zeile(cell(f"A{r}", st["title"], f"TO-DO FÜR DAS TEAM BIS {BIS.upper()} – Stand {STAND_DATUM}, wird von Claude laufend aktualisiert")
          + "".join(cell(f"{c}{r}", st["title"]) for c in "BCDEFG"), 30); merges.append(f"A{r}:G{r}"); r += 1
    zeile(cell(f"A{r}", st["sec"], ZIEL) + "".join(cell(f"{c}{r}", st["sec"]) for c in "BCDEFG"), 34); merges.append(f"A{r}:G{r}"); r += 1
    zeile(cell(f"A{r}", st["sub"], ANLEITUNG) + "".join(cell(f"{c}{r}", st["sub"]) for c in "BCDEFG"), 62); merges.append(f"A{r}:G{r}"); r += 1
    hinweis = ("Alle Dateien immer aktuell auf GitHub (Startseite = Erklärung)." +
               (f" Gemeinsame Wochen-Tabelle im Drive: „★ {WOCHE} – Aufgaben + Ergebnisse“ (jede Aufgabe hat dort einen eigenen Reiter)." if TODO_SHEET_URL else ""))
    zeile(cell(f"A{r}", st["link"], formel=link_formel(GH_START, "→ GitHub öffnen"), wert="→ GitHub öffnen")
          + (cell(f"B{r}", st["link"], formel=link_formel(TODO_SHEET_URL, "→ Abhak-Liste (Drive)"), wert="→ Abhak-Liste (Drive)") if TODO_SHEET_URL else cell(f"B{r}", st["sub"]))
          + cell(f"C{r}", st["sub"], hinweis) + "".join(cell(f"{c}{r}", st["sub"]) for c in "DEFG"), 30); merges.append(f"C{r}:G{r}"); r += 1
    zeile("".join(cell(f"{c}{r}", st["head"], k) for c, k in zip("ABCDEFG", KOPF)), 34); r += 1
    erste = r
    for art, *rest in zeilen_daten(links):
        if art == "abschnitt":
            zeile(cell(f"A{r}", st["sec"], rest[0]) + "".join(cell(f"{c}{r}", st["sec"]) for c in "BCDEFG"), 22)
            merges.append(f"A{r}:G{r}"); r += 1
            continue
        w, (ziel, anzeige) = rest
        xml = (cell(f"A{r}", st["row"], w[0]) + cell(f"B{r}", st["row"], w[1]) + cell(f"C{r}", st["row"], w[2])
               + (cell(f"D{r}", st["link"], formel=link_formel(ziel, anzeige), wert=anzeige) if ziel else cell(f"D{r}", st["row"], anzeige.replace("→ ", "")))
               + cell(f"E{r}", st["input"], w[4]) + cell(f"F{r}", st["input"], w[5]) + cell(f"G{r}", st["input"], w[6]))
        zeile(xml, max(hoehe(w[2], breiten[2]), hoehe(w[6], breiten[6]))); r += 1
    return rows, merges, erste, r - 1


def cf_dv(erste, letzte, dxf):
    """Bedingte Formatierung (ganze Zeile nach Status) + Auswahlliste in Spalte E."""
    cf = (f'<conditionalFormatting sqref="A{erste}:G{letzte}">'
          f'<cfRule type="expression" dxfId="{dxf["erledigt"]}" priority="1"><formula>$E{erste}="erledigt"</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{dxf["frage"]}" priority="2"><formula>$E{erste}="Frage/Problem"</formula></cfRule>'
          f'<cfRule type="expression" dxfId="{dxf["arbeit"]}" priority="3"><formula>$E{erste}="in Arbeit"</formula></cfRule>'
          f'</conditionalFormatting>')
    dv = (f'<dataValidations count="1"><dataValidation type="list" allowBlank="1" showDropDown="0" showInputMessage="1" '
          f'promptTitle="Status" prompt="offen / in Arbeit / erledigt / Frage/Problem" sqref="E{erste}:E{letzte}">'
          f'<formula1>{escape(STATUS_LISTE)}</formula1></dataValidation></dataValidations>')
    return cf, dv


DXF_XML = {"erledigt": '<dxf><font><color rgb="FF006100"/></font><fill><patternFill><bgColor rgb="FFC6EFCE"/></patternFill></fill></dxf>',
           "frage": '<dxf><font><color rgb="FF9C0006"/></font><fill><patternFill><bgColor rgb="FFFFC7CE"/></patternFill></fill></dxf>',
           "arbeit": '<dxf><font><color rgb="FF9C5700"/></font><fill><patternFill><bgColor rgb="FFFFEB9C"/></patternFill></fill></dxf>'}


# ------------------------------------------------------------------ a) Excel, Seite 1
def excel(src, bak):
    START = 27
    BREITEN = [16, 17, 95, 15, 14, 14, 60]
    shutil.copy2(src, bak)
    zin = zipfile.ZipFile(bak)
    styles = zin.read("xl/styles.xml").decode("utf-8")
    # neue Formate: Eingabefeld (gelb), Link (blau unterstrichen) – Klone des Zeilenstils 484
    m = re.search(r"<cellXfs count=\"(\d+)\">(.*?)</cellXfs>", styles, re.S)
    xfs = re.findall(r"<xf [^>]*?(?:/>|>.*?</xf>)", m.group(2), re.S)
    basis = xfs[484]
    fonts = re.search(r"<fonts count=\"(\d+)\"[^>]*>(.*?)</fonts>", styles, re.S)
    font_alt = re.findall(r"<font>.*?</font>|<font/>", fonts.group(2), re.S)[int(re.search(r'fontId="(\d+)"', basis).group(1))]
    sz = re.search(r'<sz val="([\d.]+)"/>', font_alt)
    name = re.search(r'<name val="([^"]+)"/>', font_alt)
    font_link = (f'<font><u/><sz val="{sz.group(1) if sz else 10}"/><color rgb="FF0563C1"/>'
                 f'<name val="{name.group(1) if name else "Arial"}"/></font>')   # Reihenfolge laut Schema: u, sz, color, name
    n_font = int(fonts.group(1))
    styles = styles.replace(fonts.group(0), fonts.group(0).replace(f'<fonts count="{n_font}"', f'<fonts count="{n_font + 1}"').replace("</fonts>", font_link + "</fonts>"))
    fills = re.search(r"<fills count=\"(\d+)\">(.*?)</fills>", styles, re.S)
    n_fill = int(fills.group(1))
    styles = styles.replace(fills.group(0), fills.group(0).replace(f'<fills count="{n_fill}"', f'<fills count="{n_fill + 1}"')
                            .replace("</fills>", '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill></fills>'))
    x_input = re.sub(r'fillId="\d+"', f'fillId="{n_fill}"', basis).replace("<xf ", '<xf applyFill="1" ', 1) if 'applyFill' not in basis else re.sub(r'fillId="\d+"', f'fillId="{n_fill}"', basis)
    x_link = re.sub(r'fontId="\d+"', f'fontId="{n_font}"', basis)
    m = re.search(r"<cellXfs count=\"(\d+)\">(.*?)</cellXfs>", styles, re.S)
    n_xf = int(m.group(1))
    styles = styles.replace(m.group(0), f'<cellXfs count="{n_xf + 2}">' + m.group(2) + x_input + x_link + "</cellXfs>")
    dm = re.search(r'<dxfs count="(\d+)">(.*?)</dxfs>', styles, re.S)
    n_dxf = int(dm.group(1))
    styles = styles.replace(dm.group(0), f'<dxfs count="{n_dxf + 3}">' + dm.group(2) + "".join(DXF_XML.values()) + "</dxfs>")
    dxf = {k: n_dxf + i for i, k in enumerate(DXF_XML)}
    st = {"title": 478, "sub": 479, "sec": 480, "head": 481, "row": 484, "input": n_xf, "link": n_xf + 1}

    def links(ziel):
        z, anzeige = ZIELE[ziel]
        return z, anzeige

    rows, merges, erste, letzte = block_xml(START, st, links, BREITEN)
    s1 = zin.read("xl/worksheets/sheet1.xml").decode("utf-8")
    # alten To-do-Block entfernen (Zeilen ab START, Formate/Listen/Verbindungen von früheren Läufen)
    s1 = re.sub(r'<row r="(\d+)"[^>]*?(?:/>|>.*?</row>)', lambda mm: "" if int(mm.group(1)) >= START else mm.group(0), s1, flags=re.S)
    s1 = re.sub(r"<mergeCells.*?</mergeCells>|<conditionalFormatting.*?</conditionalFormatting>|<dataValidations.*?</dataValidations>", "", s1, flags=re.S)
    s1 = re.sub(r'<row r="1"([^>]*)>', r'<row r="1"\1>', s1)
    # Hinweis ganz oben rechts (außerhalb des Druckbereichs)
    hin = cell("H1", st["sec"], formel=f'HYPERLINK("#A{START}","↓ TO-DOs fürs Team: hier klicken (ab Zeile {START})")', wert=f"↓ TO-DOs fürs Team: hier klicken (ab Zeile {START})")
    s1 = re.sub(r'(<row r="1"[^>]*>)(.*?)(</row>)', lambda mm: mm.group(1) + re.sub(r'<c r="H1"[^>]*?(?:/>|>.*?</c>)', "", mm.group(2), flags=re.S) + hin + mm.group(3), s1, count=1, flags=re.S)
    s1 = s1.replace("</sheetData>", "".join(rows) + "</sheetData>")
    cf, dv = cf_dv(erste, letzte, dxf)
    s1 = s1.replace("</sheetData>", "</sheetData>" + f'<mergeCells count="{len(merges)}">' + "".join(f'<mergeCell ref="{x}"/>' for x in merges) + "</mergeCells>" + cf + dv, 1)
    s1 = re.sub(r'<dimension ref="[^"]*"/>', f'<dimension ref="A1:H{letzte}"/>', s1)
    s1 = re.sub(r'<col width="11.4609375" customWidth="1" style="224" min="7" max="256"/>',
                '<col width="60" customWidth="1" style="224" min="7" max="7"/><col width="48" customWidth="1" style="224" min="8" max="8"/>'
                '<col width="11.4609375" customWidth="1" style="224" min="9" max="256"/>', s1)
    wb = zin.read("xl/workbook.xml").decode("utf-8")
    if "_xlnm.Print_Area" not in wb:   # Ausdruck = nur der Leistungsnachweis (ohne To-dos)
        dn = '<definedName name="_xlnm.Print_Area" localSheetId="0">Leistungsnachweis!$A$1:$F$24</definedName>'
        if "<definedNames/>" in wb:
            wb = wb.replace("<definedNames/>", f"<definedNames>{dn}</definedNames>", 1)
        elif "<definedNames>" in wb:
            wb = wb.replace("<definedNames>", "<definedNames>" + dn, 1)
        else:
            wb = wb.replace("</sheets>", f"</sheets><definedNames>{dn}</definedNames>", 1)
    zout = zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        d = zin.read(it.filename)
        if it.filename == "xl/worksheets/sheet1.xml":
            d = s1.encode("utf-8")
        elif it.filename == "xl/styles.xml":
            d = styles.encode("utf-8")
        elif it.filename == "xl/workbook.xml":
            d = wb.encode("utf-8")
        zout.writestr(zipfile.ZipInfo(it.filename, it.date_time), d, zipfile.ZIP_DEFLATED)
    zout.close()
    print("Excel ok: To-do-Block Zeilen", START, "bis", letzte)


# ------------------------------------------------------------------ b) eigenständige xlsx für Google Drive
def drive(ziel, links_json=None):
    extra = json.load(open(links_json, encoding="utf-8")) if links_json else {}
    def links(z):
        url = extra.get(z) or (DRIVE["GANTT_DOC"] if z == "GANTT" else None) or DRIVE.get(z) or ZIELE[z][0]
        return url, ZIELE[z][1]
    st = {"title": 1, "sub": 2, "sec": 3, "head": 4, "row": 5, "input": 6, "link": 7}
    BREITEN = [20, 11, 70, 20, 16, 12, 55]
    rows, merges, erste, letzte = block_xml(1, st, links, BREITEN)
    cf, dv = cf_dv(erste, letzte, {"erledigt": 0, "frage": 1, "arbeit": 2})
    cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(BREITEN))
    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
             'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheetViews><sheetView workbookViewId="0">'
             f'<pane ySplit="4" topLeftCell="A5" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>{cols}</cols><sheetData>{"".join(rows)}</sheetData>'
             f'<mergeCells count="{len(merges)}">' + "".join(f'<mergeCell ref="{x}"/>' for x in merges) + f"</mergeCells>{cf}{dv}</worksheet>")
    rand = '<border><left style="thin"><color rgb="FFBFBFBF"/></left><right style="thin"><color rgb="FFBFBFBF"/></right><top style="thin"><color rgb="FFBFBFBF"/></top><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border>'
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<fonts count="5"><font><sz val="10"/><name val="Arial"/></font><font><b/><sz val="14"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>'
              '<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font><font><b/><sz val="11"/><color rgb="FF1F4E79"/><name val="Arial"/></font>'
              '<font><u/><sz val="10"/><color rgb="FF0563C1"/><name val="Arial"/></font></fonts>'
              '<fills count="6"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
              '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E79"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFDDEBF7"/></patternFill></fill>'
              '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF2E75B6"/></patternFill></fill></fills>'
              f'<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>{rand}</borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="8">'
              '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
              '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="3" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="2" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="4" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
              '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
              f'<dxfs count="3">{"".join(DXF_XML.values())}</dxfs></styleSheet>')
    teile = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                               '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                               '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                               '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                               '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="TO-DO bis Di 20.10." sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                      '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                                      '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": sheet,
        "xl/styles.xml": styles,
    }
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for n, d in teile.items():
            z.writestr(n, d)
    print("Drive-xlsx ok:", ziel, os.path.getsize(ziel), "Bytes")


if __name__ == "__main__":
    if sys.argv[1] == "excel":
        excel(sys.argv[2], sys.argv[3])
    else:
        drive(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
