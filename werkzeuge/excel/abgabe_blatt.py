"""Blatt 2 „Leistungsnachweis (Abgabe)“ = saubere Kopie von Seite 1 (nur Zeilen 1–24, ohne To-do-Block und Hinweise)
+ ganz unten ein Zweizeiler: Was haben wir erreicht, wenn alle die Ziele dieser Woche schaffen (ZIEL aus todo_team.py).

Aufruf (im Ordner werkzeuge\\excel):  python abgabe_blatt.py <xlsx> <backup.xlsx>
Nach JEDER Änderung an Seite 1 erneut ausführen (Seite 1 bleibt unverändert die Arbeitsfassung).
"""
import re, shutil, sys, zipfile
from xml.sax.saxutils import escape

from todo_team import ZIEL

NAME = "Leistungsnachweis (Abgabe)"
LETZTE = 24          # letzte Zeile des eigentlichen Leistungsnachweises (Unterschrift Kunde)


def abgabe_xml(s1):
    t = re.sub(r'<row r="(\d+)"[^>]*?(?:/>|>.*?</row>)', lambda m: "" if int(m.group(1)) > LETZTE else m.group(0), s1, flags=re.S)
    t = re.sub(r'<c r="[G-Z]\d+"[^>]*?(?:/>|>.*?</c>)', "", t, flags=re.S)          # nur Spalten A–F
    t = re.sub(r"<mergeCells.*?</mergeCells>|<conditionalFormatting.*?</conditionalFormatting>|<dataValidations.*?</dataValidations>", "", t, flags=re.S)
    t = re.sub(r'<col width="60"[^>]*min="7" max="7"/><col width="48"[^>]*min="8" max="8"/><col width="11.4609375" customWidth="1" style="224" min="9" max="256"/>',
               '<col width="11.4609375" customWidth="1" style="224" min="7" max="256"/>', t)
    r = LETZTE + 2
    ziel = (f'<row r="{r}" ht="34" customHeight="1"><c r="A{r}" s="440" t="inlineStr"><is><t xml:space="preserve">{escape(ZIEL)}</t></is></c>'
            + "".join(f'<c r="{c}{r}" s="440"/>' for c in "BCDEF") + "</row>")
    t = t.replace("</sheetData>", ziel + "</sheetData>")
    t = t.replace("</sheetData>", f'</sheetData><mergeCells count="1"><mergeCell ref="A{r}:F{r}"/></mergeCells>', 1)
    t = re.sub(r'<dimension ref="[^"]*"/>', f'<dimension ref="A1:F{r}"/>', t)
    return t.replace('<sheetView showGridLines="0" workbookViewId="0">', '<sheetView showGridLines="0" workbookViewId="0" tabSelected="0">', 1)


def main(src, bak):
    shutil.copy2(src, bak)
    zin = zipfile.ZipFile(bak)
    wb = zin.read("xl/workbook.xml").decode("utf-8")
    rels = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    ct = zin.read("[Content_Types].xml").decode("utf-8")
    neu = {}
    blatt = abgabe_xml(zin.read("xl/worksheets/sheet1.xml").decode("utf-8")).encode("utf-8")
    m = re.search(rf'name="{re.escape(escape(NAME))}"[^>]*r:id="(rId\d+)"', wb)
    if m:                                   # schon vorhanden → nur Inhalt ersetzen
        ziel = re.search(rf'Target="/?(xl/worksheets/sheet\d+\.xml)" Id="{m.group(1)}"', rels).group(1)
    else:                                   # neu anlegen, direkt hinter Seite 1
        nr = max(int(x) for x in re.findall(r"xl/worksheets/sheet(\d+)\.xml", rels)) + 1
        ziel = f"xl/worksheets/sheet{nr}.xml"
        rid = "rId" + str(max(int(x) for x in re.findall(r'Id="rId(\d+)"', rels)) + 1)
        sid = max(int(x) for x in re.findall(r'sheetId="(\d+)"', wb)) + 1
        rels = rels.replace("</Relationships>", f'<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="/{ziel}" Id="{rid}"/></Relationships>')
        ct = ct.replace("</Types>", f'<Override PartName="/{ziel}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        erstes = re.search(r"<sheet [^>]*?/>", wb).group(0)
        eintrag = re.sub(r'name="[^"]*"', f'name="{escape(NAME)}"', erstes)
        eintrag = re.sub(r'sheetId="\d+"', f'sheetId="{sid}"', eintrag)
        eintrag = re.sub(r'r:id="rId\d+"', f'r:id="{rid}"', eintrag)
        wb = wb.replace(erstes, erstes + eintrag, 1)
        wb = re.sub(r'localSheetId="(\d+)"', lambda mm: f'localSheetId="{int(mm.group(1)) + (1 if int(mm.group(1)) >= 1 else 0)}"', wb)
        wb = wb.replace("</definedNames>", f"<definedName name=\"_xlnm.Print_Area\" localSheetId=\"1\">'{escape(NAME)}'!$A$1:$F${LETZTE + 2}</definedName></definedNames>", 1)
    neu[ziel] = blatt
    neu["xl/workbook.xml"] = wb.encode("utf-8")
    neu["xl/_rels/workbook.xml.rels"] = rels.encode("utf-8")
    neu["[Content_Types].xml"] = ct.encode("utf-8")
    zout = zipfile.ZipFile(src, "w", zipfile.ZIP_DEFLATED)
    namen = set()
    for it in zin.infolist():
        namen.add(it.filename)
        zout.writestr(zipfile.ZipInfo(it.filename, it.date_time), neu.get(it.filename, zin.read(it.filename)), zipfile.ZIP_DEFLATED)
    for n, d in neu.items():
        if n not in namen:
            zout.writestr(zipfile.ZipInfo(n, zin.infolist()[0].date_time), d, zipfile.ZIP_DEFLATED)
    zout.close()
    print("Abgabe-Blatt ok:", ziel)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
