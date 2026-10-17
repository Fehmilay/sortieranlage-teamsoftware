import csv, math, os, re, shutil, sys, zipfile
from xml.sax.saxutils import escape

TITLE, SUB, SEC, HEAD, ROW, ROW2, NOTE, VOR, BES, OFF, LBL, FILL = 478, 479, 480, 481, 484, 485, 486, 487, 488, 494, 496, 43
STATUS = {"VORSCHLAG": VOR, "BESTÄTIGT": BES, "OFFEN": OFF}


def col(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


class Blatt:
    def __init__(self, breiten):
        self.breiten = breiten
        self.n = len(breiten)
        self.rows, self.merges, self.r = [], [], 0

    def _hoehe(self, zellen):
        zeilen = 1
        for i, (txt, _, span) in enumerate(zellen):
            if not txt:
                continue
            w = sum(self.breiten[i:i + span]) * 1.05
            z = sum(max(1, math.ceil(len(teil) / max(w, 1))) for teil in str(txt).split("\n"))
            zeilen = max(zeilen, z)
        return max(18, 14.5 * zeilen + 4)

    def zeile(self, zellen, hoehe=None):
        """zellen: Liste (text, style, span)."""
        self.r += 1
        r = self.r
        xml, i = [], 0
        for txt, st, span in zellen:
            ref = f"{col(i)}{r}"
            if txt in (None, ""):
                xml.append(f'<c r="{ref}" s="{st}"/>')
            else:
                t = escape(str(txt))
                xml.append(f'<c r="{ref}" s="{st}" t="inlineStr"><is><t xml:space="preserve">{t}</t></is></c>')
            for k in range(1, span):
                xml.append(f'<c r="{col(i + k)}{r}" s="{st}"/>')
            if span > 1:
                self.merges.append(f"{col(i)}{r}:{col(i + span - 1)}{r}")
            i += span
        h = hoehe or self._hoehe(zellen)
        self.rows.append(f'<row r="{r}" ht="{h:.1f}" customHeight="1">{"".join(xml)}</row>')

    def leer(self):
        self.r += 1

    def titel(self, t):
        self.zeile([(t, TITLE, self.n)], 28)

    def unter(self, t):
        self.zeile([(t, SUB, self.n)])

    def abschnitt(self, t):
        self.leer()
        self.zeile([(t, SEC, self.n)], 22)

    def kopf(self, werte, spans=None):
        spans = spans or [1] * len(werte)
        self.zeile([(w, HEAD, s) for w, s in zip(werte, spans)])

    def daten(self, werte, nr, spans=None, status_spalte=None):
        spans = spans or [1] * len(werte)
        st = ROW if nr % 2 else ROW2
        zellen = []
        for j, (w, s) in enumerate(zip(werte, spans)):
            zellen.append((w, STATUS.get(w, st) if j == status_spalte else st, s))
        self.zeile(zellen)

    def label(self, lab, text):
        self.zeile([(lab, LBL, 1), (text, ROW, self.n - 1)])

    def notiz(self, t):
        self.zeile([(t, NOTE, self.n)])

    def xml(self, fit=True):
        cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(self.breiten))
        merges = (f'<mergeCells count="{len(self.merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in self.merges)
                  + "</mergeCells>") if self.merges else ""
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '<sheetPr><tabColor rgb="FFC55A11"/><pageSetUpPr fitToPage="1"/></sheetPr>'
                f'<dimension ref="A1:{col(self.n - 1)}{max(self.r, 1)}"/>'
                '<sheetViews><sheetView showGridLines="0" workbookViewId="0"><selection activeCell="A1" sqref="A1"/></sheetView></sheetViews>'
                '<sheetFormatPr defaultRowHeight="15"/>'
                f'<cols>{cols}</cols><sheetData>{"".join(self.rows)}</sheetData>{merges}'
                '<pageMargins left="0.5" right="0.5" top="0.6" bottom="0.6" header="0.3" footer="0.3"/>'
                '<pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>')


