"""Leistungsnachweis (Blatt „Leistungsnachweis (Abgabe)“) als HTML-Tabelle – für ein Google-Doc im Drive (Upload als Text, kein base64).
Aufruf:  python ln_html.py <gesamt.xlsx> <ziel.html>
"""
import re
import sys
import zipfile
from html import escape, unescape

QUELLE, ZIEL = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(QUELLE)
shared = []
if "xl/sharedStrings.xml" in z.namelist():
    for si in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), re.S):
        shared.append("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S)))
blatt = z.read("xl/worksheets/sheet20.xml").decode("utf-8")


def wert(zelle):
    t = re.search(r' t="(\w+)"', zelle)
    if t and t.group(1) == "inlineStr":
        return "".join(re.findall(r"<t[^>]*>(.*?)</t>", zelle, re.S))
    v = re.search(r"<v>(.*?)</v>", zelle, re.S)
    if not v:
        return ""
    if t and t.group(1) == "s":
        return shared[int(v.group(1))]
    return v.group(1)


def unxml(s):
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")


zeilen = {}
for r, inhalt in re.findall(r'<row r="(\d+)"[^>]*>(.*?)</row>', blatt, re.S):
    for ref, zelle in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?/>|[^>]*>.*?</c>)', inhalt, re.S):
        w = unescape(unescape(wert(zelle))).strip()
        if w:
            zeilen.setdefault(int(r), {})[ref] = w

kopf = [zeilen.get(i, {}) for i in (3, 4, 5)]
eintraege, summe, ziel = [], "", ""
for r in sorted(zeilen):
    z_ = zeilen[r]
    if re.match(r"\d\d\.\d\d\.\d{4}$", z_.get("A", "")):
        eintraege.append(z_)
    if z_.get("A", "").startswith("Summe"):
        summe = z_.get("E", "")
    if z_.get("A", "").startswith("Ziel"):
        ziel = z_["A"]
if not summe:                                          # Summe ist eine Formel ohne gespeicherten Wert -> selbst rechnen
    summe = str(round(sum(float(z_.get("E", "0") or 0) for z_ in eintraege), 2)).rstrip("0").rstrip(".")
zahl = lambda s: s.replace(".", ",") if re.match(r"^\d+(\.\d+)?$", s) else s
html = ['<html><head><meta charset="utf-8"></head><body>',
        "<h1>Leistungsnachweis Hochschule Niederrhein</h1>"]
for z_ in kopf:
    if z_:
        html.append("<p>" + " ".join(f"<b>{escape(v)}</b>" if k == "A" else escape(v) for k, v in sorted(z_.items())) + "</p>")
html.append('<table border="1" cellpadding="5" style="border-collapse:collapse">'
            "<tr><th>Datum</th><th>Arbeitsort</th><th>Kurzbeschrieb der Tätigkeit</th><th>Arbeitszeit (h)</th><th>Reisezeit (h)</th></tr>")
for z_ in eintraege:
    html.append(f"<tr><td>{escape(z_.get('A',''))}</td><td>{escape(z_.get('B',''))}</td><td>{escape(z_.get('C',''))}</td>"
                f"<td>{escape(zahl(z_.get('E','')))}</td><td>{escape(zahl(z_.get('F','')))}</td></tr>")
html.append(f"<tr><td colspan=\"3\"><b>Summe</b></td><td><b>{escape(zahl(summe))}</b></td><td></td></tr></table>")
if ziel:
    html.append(f"<p><i>{escape(ziel)}</i></p>")
html.append("</body></html>")
open(ZIEL, "w", encoding="utf-8").write("\n".join(html))
print("ok", len(eintraege), "Einträge, Summe", summe)
