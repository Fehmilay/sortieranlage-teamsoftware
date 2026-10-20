"""Wochen-Tabelle für Google Drive: Reiter 1 = ★ TO-DO (abhaken), danach je Aufgabe ein Reiter zum Ausfüllen (aus woche.py).
Aufruf (im Ordner werkzeuge\\excel):  python woche_drive.py <ziel.xlsx>
Nach dem Hochladen: Google wandelt die xlsx in eine Google-Tabelle mit Reitern um (Auswahllisten + Farben bleiben).
Einsammeln: download_file_content mit exportMimeType xlsx → Reiter auslesen → in Excel/Gantt/Code übernehmen.
"""
import re, sys, zipfile
from xml.sax.saxutils import escape

import todo_team as T
from woche import REITER, WOCHE

ST = {"title": 1, "sub": 2, "sec": 3, "head": 4, "row": 5, "input": 6, "link": 7}


def spalte(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def blatt_xml(rows, merges, breiten, extra="", fix=4):
    cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(breiten))
    mc = (f'<mergeCells count="{len(merges)}">' + "".join(f'<mergeCell ref="{x}"/>' for x in merges) + "</mergeCells>") if merges else ""
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheetViews><sheetView workbookViewId="0">'
            f'<pane ySplit="{fix}" topLeftCell="A{fix + 1}" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>{cols}</cols>'
            f'<sheetData>{"".join(rows)}</sheetData>{mc}{extra}</worksheet>')


def reiter_xml(titel, hinweis, kopf, zeilen, breiten, eingabe):
    n = len(kopf)
    letzte = spalte(n - 1)
    rows, merges, r = [], [], 1
    def zeile(xml, h):
        rows.append(f'<row r="{r}" ht="{h:.0f}" customHeight="1">{xml}</row>')
    zeile(T.cell(f"A{r}", ST["title"], titel) + "".join(T.cell(f"{spalte(i)}{r}", ST["title"]) for i in range(1, n)), 28); merges.append(f"A{r}:{letzte}{r}"); r += 1
    zeile(T.cell(f"A{r}", ST["sub"], hinweis) + "".join(T.cell(f"{spalte(i)}{r}", ST["sub"]) for i in range(1, n)), 44); merges.append(f"A{r}:{letzte}{r}"); r += 1
    zeile(T.cell(f"A{r}", ST["sec"], "Gelbe Spalten ausfüllen – Claude liest sie aus und arbeitet damit weiter.")
          + "".join(T.cell(f"{spalte(i)}{r}", ST["sec"]) for i in range(1, n)), 20); merges.append(f"A{r}:{letzte}{r}"); r += 1
    zeile("".join(T.cell(f"{spalte(i)}{r}", ST["head"], k) for i, k in enumerate(kopf)), 32); r += 1
    for z in zeilen:
        h = max(T.hoehe(str(v), breiten[i]) for i, v in enumerate(z))
        zeile("".join(T.cell(f"{spalte(i)}{r}", ST["input"] if i in eingabe else ST["row"], v) for i, v in enumerate(z)), h); r += 1
    for _ in range(2):   # Reservezeilen
        zeile("".join(T.cell(f"{spalte(i)}{r}", ST["input"] if i in eingabe else ST["row"]) for i in range(n)), 24); r += 1
    return blatt_xml(rows, merges, breiten)


def main(ziel):
    def links(z):
        if z.startswith("R:"):
            return "", "→ Reiter „" + z[2:] + "“"
        url = T.DRIVE.get(z) or T.ZIELE[z][0]
        return url, T.ZIELE[z][1]
    breiten = [20, 11, 62, 26, 16, 12, 50]
    rows, merges, erste, letzte = T.block_xml(1, ST, links, breiten)
    cf, dv = T.cf_dv(erste, letzte, {"erledigt": 0, "frage": 1, "arbeit": 2})
    blaetter = [("★ TO-DO " + WOCHE, blatt_xml(rows, merges, breiten, cf + dv, fix=5))]
    for name, titel, hinweis, kopf, zeilen, br, eingabe in REITER:
        blaetter.append((name, reiter_xml(titel, hinweis, kopf, zeilen, br, eingabe)))
    # Stile aus todo_team.drive() übernehmen (gleiche Optik)
    import io, tempfile, os
    tmp = os.path.join(tempfile.gettempdir(), "_todo_stil.xlsx")
    T.drive(tmp)
    styles = zipfile.ZipFile(tmp).read("xl/styles.xml")
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
          + "".join(f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                    for i in range(len(blaetter))) + "</Types>")
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
          + "".join(f'<sheet name="{escape(n)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, (n, _) in enumerate(blaetter)) + "</sheets></workbook>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i + 1}.xml"/>'
                      for i in range(len(blaetter)))
            + f'<Relationship Id="rId{len(blaetter) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        z.writestr("xl/styles.xml", styles)
        for i, (_, xml) in enumerate(blaetter):
            z.writestr(f"xl/worksheets/sheet{i + 1}.xml", xml)
    print("Wochen-Tabelle ok:", ziel, len(blaetter), "Reiter", os.path.getsize(ziel), "Bytes")


if __name__ == "__main__":
    main(sys.argv[1])
