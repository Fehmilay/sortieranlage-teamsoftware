"""Schlanke Kopie des Leistungsnachweises für Google Drive: nur Blatt „Leistungsnachweis (Abgabe)“ (sheet20.xml),
ohne Bilder/Zeichnungen/andere Blätter – klein genug für den Drive-Connector (Upload als base64).
Aufruf:  python ln_schlank.py <gesamt.xlsx> <ziel.xlsx>
"""
import re
import sys
import zipfile

QUELLE, ZIEL = sys.argv[1], sys.argv[2]
BLATT = "xl/worksheets/sheet20.xml"
zin = zipfile.ZipFile(QUELLE)
namen = set(zin.namelist())
blatt = zin.read(BLATT).decode("utf-8")
blatt = re.sub(r"<drawing [^>]*/>|<legacyDrawing [^>]*/>|<picture [^>]*/>", "", blatt)   # keine Bilder
blatt = re.sub(r"<hyperlinks>.*?</hyperlinks>", "", blatt, flags=re.S)
blatt = re.sub(r' r:id="[^"]*"', "", blatt)                                   # keine Verweise auf entfernte Teile
blatt = re.sub(r"<tableParts.*?</tableParts>|<tableParts[^>]*/>", "", blatt, flags=re.S)

ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
      '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
      '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
      + ('<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
         if "xl/sharedStrings.xml" in namen else "")
      + ('<Override PartName="/xl/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
         if "xl/theme/theme1.xml" in namen else "")
      + "</Types>")
wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
      '<sheet name="Leistungsnachweis" sheetId="1" r:id="rId1"/></sheets>'
      '<definedNames><definedName name="_xlnm.Print_Area" localSheetId="0">Leistungsnachweis!$A$1:$F$26</definedName></definedNames></workbook>')
rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>',
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
if "xl/sharedStrings.xml" in namen:
    rels.append('<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>')
if "xl/theme/theme1.xml" in namen:
    rels.append('<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>')
with zipfile.ZipFile(ZIEL, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                              '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    z.writestr("xl/workbook.xml", wb)
    z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               + "".join(rels) + "</Relationships>")
    z.writestr("xl/worksheets/sheet1.xml", blatt)
    for n in ("xl/styles.xml", "xl/sharedStrings.xml", "xl/theme/theme1.xml"):
        if n in namen:
            z.writestr(n, zin.read(n))
print("ok", ZIEL)
