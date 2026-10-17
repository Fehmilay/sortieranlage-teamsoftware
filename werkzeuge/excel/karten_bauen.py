"""Erzeugt aus karten_daten.py: Druck-HTML (für PDF), einfaches HTML (für Google Drive) und das Excel-Blatt ARBEITSKARTEN.
Aufruf: python karten_bauen.py <druck.html> <drive.html> [<xlsx> <backup>]
"""
import os, re, shutil, sys, zipfile
from html import escape as h

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karten_daten as K  # noqa: E402
import karten_peakboard  # noqa: E402
karten_peakboard.anwenden()
import karten_team  # noqa: E402
karten_team.umverteilen()

DRUCK, DRIVE_HTML = sys.argv[1], sys.argv[2]

CSS = """
@page { size: A4; margin: 13mm 13mm 15mm 13mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.4; color: #1a1a1a; margin: 0; }
h1 { background: #1f4e79; color: #fff; font-size: 17pt; padding: 9px 13px; border-radius: 6px; margin: 0 0 6px; }
h2 { background: #2e7d32; color: #fff; font-size: 14pt; padding: 6px 11px; border-radius: 5px; margin: 0 0 8px; page-break-before: always; }
h2.v { background: #c55a11; }
.karte { border: 2px solid #b7c4d3; border-radius: 8px; padding: 7px 11px; margin: 0 0 10px; page-break-inside: avoid; }
.kt { font-size: 12pt; font-weight: 700; color: #1f3d5c; }
.meta { color: #444; font-size: 9.5pt; margin: 2px 0 5px; }
ol { margin: 3px 0 5px; padding-left: 22px; } ol li { margin-bottom: 3px; }
ol li::marker { font-weight: 700; }
.zeile { margin: 2px 0; } .ok { color: #2e7d32; } .warn { color: #b26a00; } .nein { color: #c00000; }
.box { border: 1px solid #b7c4d3; background: #f6f9fc; padding: 6px 10px; border-radius: 5px; }
.vorlage { border: 1px dashed #888; padding: 7px 11px; margin: 0 0 10px; page-break-inside: avoid; }
.vorlage p { margin: 3px 0; }
.schild { page-break-before: always; text-align: center; padding-top: 70mm; }
.schild .gross { font-size: 34pt; font-weight: 800; color: #c00000; line-height: 1.2; }
.schild .mittel { font-size: 20pt; margin-top: 12mm; }
.uebersicht td, .uebersicht th { border: 1px solid #b7c4d3; padding: 3px 6px; font-size: 9.5pt; vertical-align: top; }
.uebersicht { border-collapse: collapse; width: 100%; } .uebersicht th { background: #dbe9f6; text-align: left; }
"""


def karte_html(k, einfach=False):
    nr, titel, bis, dauer, brauchst, schritte, fertig, problem, nicht = k
    s = "".join(f"<li>{h(x)}</li>" for x in schritte)
    if einfach:
        return (f"<h3>{h(nr)} – {h(titel)}</h3><p><i>Bis: {h(bis)} · Dauer: {h(dauer)} · Du brauchst: {h(brauchst)}</i></p><ol>{s}</ol>"
                f"<p>✅ <b>Fertig, wenn:</b> {h(fertig)}</p><p>⚠️ <b>Wenn etwas nicht klappt:</b> {h(problem)}</p>"
                + (f"<p>⛔ <b>Nicht tun:</b> {h(nicht)}</p>" if nicht != "–" else ""))
    return (f'<div class="karte"><div class="kt">☐ {h(nr)} – {h(titel)}</div>'
            f'<div class="meta">Bis: <b>{h(bis)}</b> · Dauer: {h(dauer)} · Du brauchst: {h(brauchst)}</div><ol>{s}</ol>'
            f'<div class="zeile ok">✅ <b>Fertig, wenn:</b> {h(fertig)}</div>'
            f'<div class="zeile warn">⚠️ <b>Wenn etwas nicht klappt:</b> {h(problem)}</div>'
            + (f'<div class="zeile nein">⛔ <b>Nicht tun:</b> {h(nicht)}</div>' if nicht != "–" else "") + "</div>")


def uebersicht():
    z = "".join(f"<tr><td>{h(p)}</td><td>{h(k[0])}</td><td>{h(k[1])}</td><td>{h(k[2])}</td></tr>"
                for p, karten in K.PERSONEN for k in karten)
    return f'<table class="uebersicht"><tr><th>Wer</th><th>Karte</th><th>Aufgabe</th><th>Bis</th></tr>{z}</table>'


def peakboard_html(einfach=False):
    erkl = "".join(f"<p>{h(x)}</p>" for x in K.PEAKBOARD_ERKLAERUNG)
    z = "".join(f"<tr><td>{h(a)}</td><td>{h(b)}</td><td>{h(c)}</td><td>{h(d)}</td></tr>" for a, b, c, d in K.PEAKBOARD_PLAN)
    tab = f'<table class="uebersicht" border="1" cellpadding="4"><tr><th>Schritt</th><th>Karte</th><th>Wer</th><th>Was</th></tr>{z}</table>'
    kopf = "<h2>So kriegen wir Peakboard fertig</h2>" if einfach else '<h2 class="v">So kriegen wir Peakboard fertig – Reihenfolge</h2>'
    return kopf + (erkl if einfach else f'<div class="box">{erkl}</div>') + tab


def druck():
    teile = [f"<h1>Arbeitskarten Schritt für Schritt – Sortieranlage (Stand {K.STAND})</h1>",
             '<div class="box">' + "".join(f"<p>{h(x)}</p>" for x in K.EINLEITUNG) + f"<p>Drive-Ordner: {h(K.DRIVE)}</p></div>",
             "<h3>Übersicht – wer macht was bis wann</h3>", uebersicht(), peakboard_html()]
    for person, karten in K.PERSONEN:
        teile.append(f"<h2>{h(person)}</h2>")
        teile += [karte_html(k) for k in karten]
    teile.append('<h2 class="v">VORLAGEN A–I zum Kopieren und Ausdrucken</h2>')
    for b, titel, zeilen in K.VORLAGEN:
        if b == "G":
            continue
        teile.append(f'<div class="vorlage"><b>Vorlage {b} – {h(titel)}</b>' + "".join(f"<p>{h(x)}</p>" for x in zeilen) + "</div>")
    g = [v for v in K.VORLAGEN if v[0] == "G"][0][2]
    teile.append(f'<div class="schild"><div class="gross">{h(g[0])}</div><div class="mittel">{h(g[1])}</div><div class="mittel">{h(g[2])}</div></div>')
    return f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Arbeitskarten</title><style>{CSS}</style></head><body>{"".join(teile)}</body></html>'


def drive():
    teile = [f"<h1>Arbeitskarten Schritt für Schritt – Sortieranlage (Stand {K.STAND})</h1>"]
    teile += [f"<p>{h(x)}</p>" for x in K.EINLEITUNG]
    teile.append("<h2>Übersicht</h2>" + uebersicht().replace('class="uebersicht"', 'border="1" cellpadding="4"'))
    teile.append(peakboard_html(einfach=True).replace('class="uebersicht" ', ''))
    for person, karten in K.PERSONEN:
        teile.append(f"<h2>{h(person)}</h2>")
        teile += [karte_html(k, einfach=True) for k in karten]
    teile.append("<h2>VORLAGEN zum Kopieren</h2>")
    for b, titel, zeilen in K.VORLAGEN:
        teile.append(f"<h3>Vorlage {b} – {h(titel)}</h3>" + "".join(f"<p>{h(x)}</p>" for x in zeilen))
    return f'<html><head><meta charset="utf-8"></head><body>{"".join(teile)}</body></html>'


open(DRUCK, "w", encoding="utf-8").write(druck())
open(DRIVE_HTML, "w", encoding="utf-8").write(drive())
print("HTML ok", len(druck()), len(drive()))

# ---------------------------------------------------------------- Excel-Blatt
if len(sys.argv) > 4:
    from blatt import Blatt, ROW, ROW2, LBL, NOTE, HEAD  # noqa: E402
    SRC, BAK = sys.argv[3], sys.argv[4]
    NAME = "ARBEITSKARTEN"  # Excel: max. 31 Zeichen
    b = Blatt([12, 92, 26, 30])
    b.titel(f"ARBEITSKARTEN – Schritt für Schritt, damit nichts schiefgehen kann (Stand {K.STAND})")
    b.unter(" ".join(K.EINLEITUNG) + " Druckversion mit Schild und Messprotokoll: Ordner „Arbeitskarten“ (PDF).")
    b.abschnitt("Übersicht – wer macht was bis wann")
    b.kopf(["Karte", "Aufgabe", "Wer", "Bis"])
    i = 0
    for person, karten in K.PERSONEN:
        for k in karten:
            i += 1
            b.daten([k[0], k[1], person, k[2]], i)
    b.abschnitt("So kriegen wir Peakboard fertig – Reihenfolge")
    for x in K.PEAKBOARD_ERKLAERUNG:
        b.zeile([("", ROW, 1), (x, ROW, 3)])
    b.kopf(["Schritt", "Was", "Karte", "Wer"])
    for j, (nr, karte, wer, was) in enumerate(K.PEAKBOARD_PLAN, 1):
        b.daten([nr, was, karte, wer], j)
    for person, karten in K.PERSONEN:
        b.abschnitt(person)
        for nr, titel, bis, dauer, brauchst, schritte, fertig, problem, nicht in karten:
            b.zeile([(f"☐ {nr}", HEAD, 1), (titel, HEAD, 1), (f"Bis: {bis}", HEAD, 1), (f"Dauer: {dauer}", HEAD, 1)])
            b.label("Du brauchst", brauchst)
            for j, s in enumerate(schritte, 1):
                b.zeile([(f"Schritt {j}", ROW2 if j % 2 == 0 else ROW, 1), (s, ROW2 if j % 2 == 0 else ROW, 3)])
            b.label("✅ Fertig, wenn", fertig)
            b.label("⚠️ Wenn etwas nicht klappt", problem)
            if nicht != "–":
                b.label("⛔ Nicht tun", nicht)
            b.leer()
    b.abschnitt("VORLAGEN A–I zum Kopieren (Strg + C)")
    for bst, titel, zeilen in K.VORLAGEN:
        b.zeile([(f"Vorlage {bst}", HEAD, 1), (titel, HEAD, 3)])
        for z in zeilen:
            b.zeile([("", ROW, 1), (z, ROW, 3)])
        b.leer()
    blatt_xml = b.xml().replace("FFC55A11", "FF2E7D32")

    shutil.copy2(SRC, BAK)
    zin = zipfile.ZipFile(BAK)
    wb = zin.read("xl/workbook.xml").decode("utf-8")
    rels = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    ct = zin.read("[Content_Types].xml").decode("utf-8")
    ersatz = None
    if f'name="{NAME}"' in wb:          # schon vorhanden -> ersetzen
        rid = re.search(rf'name="{NAME}"[^>]*r:id="(rId\d+)"', wb).group(1)
        ersatz = re.search(rf'Target="/?(xl/worksheets/sheet\d+\.xml)" Id="{rid}"', rels).group(1)
    else:
        nr = max(int(re.search(r"sheet(\d+)\.xml", n).group(1)) for n in zin.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)) + 1
        rid = max(int(x) for x in re.findall(r'Id="rId(\d+)"', rels)) + 1
        sid = max(int(x) for x in re.findall(r'sheetId="(\d+)"', wb)) + 1
        rels = rels.replace("</Relationships>", f'<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                                                f'Target="/xl/worksheets/sheet{nr}.xml" Id="rId{rid}"/></Relationships>')
        m = re.search(r'<sheet [^>]*name="Anhang 10 - Auftraege M2"', wb)
        wb = wb[:m.start()] + (f'<sheet xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" name="{NAME}" '
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
        elif it.filename == ersatz: d = blatt_xml.encode()
        zout.writestr(zipfile.ZipInfo(it.filename, it.date_time), d, zipfile.ZIP_DEFLATED)
    if ersatz is None:
        zout.writestr(zipfile.ZipInfo(neu_teil, (2026, 10, 15, 0, 0, 0)), blatt_xml.encode(), zipfile.ZIP_DEFLATED)
    zout.close()
    print("Excel ok:", ersatz or neu_teil)

