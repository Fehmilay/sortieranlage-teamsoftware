"""Baut das Peakboard-Board der Sortieranlage als .pbmx (VORSCHLAG, im Designer noch nicht geöffnet).

Aufruf:  python werkzeuge/peakboard/board_bauen.py <vorlage.pbmx> [ziel.pbmx]
         python werkzeuge/peakboard/board_bauen.py --heimtest <vorlage.pbmx>   # → Sortieranlage_Board_Heimtest.pbmx

<vorlage.pbmx> = offizielle, öffentliche Peakboard-Vorlage „Intralogistik-Bestellungen-Empfangen-ueber-MQTT.pbmx“
(github.com/Peakboard/peakboard-templates.github.io, Ordner _templates/Intralogistics-Receive-Orders-via-MQTT).
Aus ihr kommen Theme, Schriftstile, die Peakboard-Hilfsdateien in Resources\\ und der Aufbau der Elemente.
Alles Fachliche (Datenquelle, Topics, Layout, Texte, Farben) steht unten und folgt peakboard/MQTT_Schnittstelle.md.

Eine .pbmx ist ein ZIP: Manifest.xml, Connections.pbcx (MQTT-Verbindung), Peakboard.xml (Laufzeit-Definition mit
XAML-Bildschirm) und Peakboard.json (gleiches Board für den Designer). Beide Fassungen werden hier aus EINER
Layout-Liste erzeugt, damit sie zusammenpassen. Zugangsdaten stehen NICHT in der Datei – Benutzer und Passwort
trägt Marie im Designer ein (Data → Verbindung „Postamt Pi“).
"""
import base64, copy, html, json, os, sys, uuid, zipfile
from xml.sax.saxutils import escape, quoteattr

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ZIEL = os.path.join(WURZEL, "peakboard", "Sortieranlage_Board.pbmx")

BROKER = "192.168.1.180"          # Pi im TP-Link-WLAN (BESTÄTIGT 20.10.2026)
PORT = 1883
TOPIC = "sortieranlage/wert/"      # Tabelle A in MQTT_Schnittstelle.md
VERBINDUNG = "Postamt Pi (Mosquitto)"
# --heimtest: öffentliches Test-Postamt ohne Anmeldung, Daten von PEAKBOARD_TESTDATEN.bat Option 2
HEIMTEST = dict(BROKER="broker.hivemq.com", TOPIC="hsnr-sortieranlage-teamsoftware/wert/",
                VERBINDUNG="Test-Postamt Internet (broker.hivemq.com)",
                ZIEL=os.path.join(WURZEL, "peakboard", "Sortieranlage_Board_Heimtest.pbmx"))
WERTE = ["zustand", "zyklen", "farbe_letzte", "anzahl_weiss", "anzahl_rot", "anzahl_blau",
         "fehler_aktiv", "fehler_text", "fehler_anzahl", "modus"]
MQTT = "SortierMQTT"               # Name der Datenquelle im Board
ANZEIGE = "Anzeige"                # Liste mit den übersetzten Texten (füllt das Skript)
ANZEIGE_START = {"ZustandText": "Warte auf Daten …", "FarbeText": "–", "FehlerText": "Keine Störung", "ModusText": "–"}
ZAHLEN = ["ZustandNr", "FarbeNr", "FehlerNr"]   # Variablen für die Farbregeln

# Läuft bei jeder neuen MQTT-Nachricht. ZustandNr: 0 bereit, 1 läuft, 2 Störung, 3 aus.
SKRIPT = """local m = data.SortierMQTT[0]
local a = data.Anzeige[0]
local z = m.zustand
local texte = {BEREIT = 'Bereit – Klotz auflegen', FOERDERN = 'Fördert', ZAEHLEN = 'Fährt zum Auswerfer',
	AUSSCHLEUSEN = 'Sortiert aus', PRUEFEN = 'Prüft', FEHLER = 'STÖRUNG', AUS = 'Aus'}

if z == 'FEHLER' then
	data.ZustandNr = 2
elseif z == 'AUS' then
	data.ZustandNr = 3
elseif z == 'BEREIT' or z == '' then
	data.ZustandNr = 0
else
	data.ZustandNr = 1
end
a.ZustandText = texte[z] or z

local f = m.farbe_letzte
if f == 'weiss' then
	data.FarbeNr = 1
	a.FarbeText = 'Weiß'
elseif f == 'rot' then
	data.FarbeNr = 2
	a.FarbeText = 'Rot'
elseif f == 'blau' then
	data.FarbeNr = 3
	a.FarbeText = 'Blau'
else
	data.FarbeNr = 0
	a.FarbeText = 'noch keiner'
end

if m.fehler_aktiv == '1' then
	data.FehlerNr = 1
	a.FehlerText = 'STÖRUNG: ' .. m.fehler_text
else
	data.FehlerNr = 0
	a.FehlerText = 'Keine Störung'
end

if m.modus == 'hardware' then
	a.ModusText = 'Echtbetrieb'
elseif m.modus == 'sim' then
	a.ModusText = 'Testbetrieb (Simulation)'
else
	a.ModusText = m.modus
end""".replace("\n", "\r\n")

SEITE = "#FF0B1A33"
KACHEL = "#FF14284B"
STILE = [  # zusätzlich zu den Stilen der Vorlage
    ("kachel_titel", "#FFB0BEC5", 36, "Normal"),
    ("wert_gross", "#FFFFFFFF", 72, "Bold"),
    ("zahl_gross", "#FFFFFFFF", 90, "Bold"),
    ("zahl_riesig", "#FFFFFFFF", 200, "Bold"),
    ("banner", "#FFFFFFFF", 48, "Bold"),
]


def r(x, y, w, h, bg, radius=20, regeln=None):
    return dict(art="rect", x=x, y=y, w=w, h=h, bg=bg, radius=radius, regeln=regeln or [])


def t(x, y, w, h, text, schrift, rechts=False, fmt=""):
    return dict(art="text", x=x, y=y, w=w, h=h, text=text, schrift=schrift, rechts=rechts, fmt=fmt)


def wert(name):
    return "{%s[0].%s}" % (MQTT, name)


def anzeige(name):
    return "{%s[0].%s}" % (ANZEIGE, name)


# Reihenfolge = Zeichenreihenfolge (erstes Element liegt ganz unten). 1920 × 1080.
LAYOUT = [
    r(20, 20, 1880, 120, KACHEL),
    t(50, 38, 1400, 90, "Sortieranlage – Team Software HSNR", "header2"),
    t(1600, 38, 270, 90, "{Time}", "header2", rechts=True, fmt="D|TIMEC3|en-US;de-DE;pb-SAP-DT|en-US=HH:mm|N/A"),
    # Zustand: grau = bereit, grün = läuft, rot = Störung, dunkel = aus
    r(20, 160, 1000, 420, "#FF546E7A", regeln=[("Laeuft", "ZustandNr", "1", "#FF2E7D32"),
                                               ("Stoerung", "ZustandNr", "2", "#FFC62828"),
                                               ("Aus", "ZustandNr", "3", "#FF37474F")]),
    t(50, 185, 940, 60, "Zustand", "kachel_titel"),
    t(50, 290, 940, 250, anzeige("ZustandText"), "wert_gross"),
    r(1040, 160, 420, 420, KACHEL),
    t(1070, 185, 360, 60, "Sortierte Klötze", "kachel_titel"),
    t(1070, 260, 360, 280, wert("zyklen"), "zahl_riesig"),
    r(1480, 160, 420, 420, KACHEL),
    t(1510, 185, 360, 60, "Letzte Farbe", "kachel_titel"),
    r(1510, 255, 360, 190, "#FF37474F", regeln=[("Weiss", "FarbeNr", "1", "#FFF5F5F5"),
                                                ("Rot", "FarbeNr", "2", "#FFE53935"),
                                                ("Blau", "FarbeNr", "3", "#FF1E88E5")]),
    t(1510, 465, 360, 80, anzeige("FarbeText"), "header2"),
]
for i, (farbe, name, feld) in enumerate([("#FFF5F5F5", "Weiß", "anzahl_weiss"), ("#FFE53935", "Rot", "anzahl_rot"),
                                         ("#FF1E88E5", "Blau", "anzahl_blau")]):
    x = 20 + i * 633
    LAYOUT += [r(x, 600, 613, 200, KACHEL), r(x + 30, 640, 120, 120, farbe),
               t(x + 180, 625, 400, 60, name, "kachel_titel"), t(x + 180, 680, 400, 110, wert(feld), "zahl_gross")]
LAYOUT += [
    # Störungsbanner: wird rot, sobald fehler_aktiv = 1
    r(20, 820, 1880, 140, KACHEL, regeln=[("Stoerung", "FehlerNr", "1", "#FFC62828")]),
    t(50, 848, 1820, 90, anzeige("FehlerText"), "banner"),
    t(30, 985, 250, 60, "Betriebsart:", "kachel_titel"),
    t(280, 985, 700, 60, anzeige("ModusText"), "kachel_titel"),
    t(1100, 985, 420, 60, "Störungen seit Start:", "kachel_titel"),
    t(1530, 985, 340, 60, wert("fehler_anzahl"), "kachel_titel"),
]


def regeln_text(regeln):
    """Bedingte Formatierung im Peakboard-Format: o = 2 heißt „ist gleich“ (aus den offiziellen Vorlagen abgelesen)."""
    if not regeln:
        return ""
    r_ = [{"t": titel, "ab": [{"o": 2, "l": {"il": False, "ip": True, "d": var, "ri": -1, "rv": "{%s}" % var},
                               "r": {"il": False, "ip": False, "ri": -1, "rv": wert_}}],
           "ob": [], "tb": [{"p": "Background", "v": farbe}]} for titel, var, wert_, farbe in regeln]
    return json.dumps({"r": r_, "t": False}, separators=(",", ":"), ensure_ascii=False)[1:-1]


def bindung_xml(text):
    if text == "{Time}":
        return "{Binding Time}"
    if text.startswith("{"):
        return "{Binding Path='%s'}" % text[1:-1]
    return text


def stil_xml(name, setters):
    s = "".join('\n            <Setter Property="%s" Value="%s" />' % (p, v) for p, v in setters)
    return '\n          <Style x:Key="%s" TargetType="TextBlock">%s\n          </Style>' % (name, s)


def stil_setter(farbe, groesse, gewicht):
    return [("Foreground", farbe), ("FontSize", str(groesse)), ("FontFamily", "Segoe UI"), ("FontStyle", "Normal"),
            ("FontWeight", gewicht), ("TextDecorations", "None")]


def control_json(e, vorlage_text, vorlage_rect):
    c = copy.deepcopy(vorlage_text if e["art"] == "text" else vorlage_rect)
    c.update(Width=float(e["w"]), Height=float(e["h"]), Top=float(e["y"]), Left=float(e["x"]),
             Margin={"Left": float(e["x"]), "Top": float(e["y"]), "Right": 0.0, "Bottom": 0.0})
    if e["art"] == "text":
        c.update(Text=e["text"], Font=e["schrift"], Align=1 if e["rechts"] else 0, VAlign=0, Format=e["fmt"],
                 ConditionalFormatting="")
    else:
        c.update(Background=e["bg"], CornerRadius=e["radius"], ConditionalFormatting=regeln_text(e["regeln"]))
    return c


def control_xml(e):
    pos = 'Width="%d" Height="%d" Margin="%d,%d,0,0" VerticalAlignment="Top" HorizontalAlignment="Left"' % (
        e["w"], e["h"], e["x"], e["y"])
    anim = 'controls:PeakboardXaml.Animation="None" controls:PeakboardXaml.AnimationLoopType="RunOnce"'
    if e["art"] == "text":
        fmt = ' Format=%s' % quoteattr(e["fmt"]) if e["fmt"] else ""
        return ('<controls:PeakboardTextBlock %s Background="#00FFFFFF" %s%s Font="%s" VAlign="Top" Align="%s" Text=%s />'
                % (pos, anim, fmt, e["schrift"], "Right" if e["rechts"] else "Left", quoteattr(bindung_xml(e["text"]))))
    cf = regeln_text(e["regeln"])
    cf = ' controls:PeakboardXaml.ConditionalFormatting=%s' % quoteattr(cf) if cf else ""
    return ('<controls:PeakboardRectangle %s Background="%s" %s StrokeThickness="0" BorderBrush="#00000000" '
            'CornerRadius="%d"%s />' % (pos, e["bg"], anim, e["radius"], cf))


def zeichenkette(name, wert_):
    return {"Name": name, "Value": wert_, "Events": [], "TypeName": "System.String", "ElementTypeName": "StringElementInfo"}


def bauen(vorlage, ziel):
    with zipfile.ZipFile(vorlage) as z:
        dateien = {n: z.read(n) for n in z.namelist()}
    vj = json.loads(dateien["Peakboard.json"].decode("utf-8"))
    vx = dateien["Peakboard.xml"].decode("utf-8")
    elemente = {e["ElementTypeName"]: e for e in vj["Data"]["Elements"]}
    texte = [c for c in vj["Screens"][0]["Controls"] if c["ControlTypeName"] == "TextBlockInfo"]
    rechtecke = [c for c in vj["Screens"][0]["Controls"] if c["ControlTypeName"] == "RectangleInfo"]
    verbindung_id = base64.b64encode(os.urandom(20)).decode()

    # --- Connections.pbcx: Postamt (Mosquitto) auf dem Pi, ohne Zugangsdaten
    alt = next(iter(json.loads(dateien["Connections.pbcx"].decode("utf-8")).values()))
    verbindung = dict(alt, Server=BROKER, Port=PORT, UserName="", Password="", Name=VERBINDUNG,
                      ClientID="#{-- Auto generated. Remove this comment on editing.\r\n"
                               "return runtime.network.hostname .. 'SortierMQTT'}#")

    # --- Daten (JSON)
    zeit = elemente["TimeElementInfo"]
    zahlen = [{"Save": False, "Path": "", "Name": n, "Value": 0.0, "CanPush": False, "Events": [],
               "TypeName": "System.Double", "ElementTypeName": "PeakboardNumberElementInfo"} for n in ZAHLEN]
    liste = copy.deepcopy(elemente["PeakboardListElementInfo"])
    liste.update(Name=ANZEIGE, Columns=[{"Name": k, "ElementName": k, "DataType": "String"} for k in ANZEIGE_START],
                 Value=[{"Value": [zeichenkette(k, v) for k, v in ANZEIGE_START.items()], "Events": [],
                         "TypeName": "Peakboard.Designer.DataModels.DataElementInfoCollection",
                         "ElementTypeName": "ObjectElementInfo"}])
    mqtt = copy.deepcopy(elemente["MqttListElementInfo"])
    mqtt.update(Name=MQTT, ConnectionId=verbindung_id,
                Subscriptions=[{"Title": w, "TopicFilter": TOPIC + w, "QosLevel": 0, "Datapath": ""} for w in WERTE],
                Columns=[{"Name": w, "ElementName": w, "DataType": "String"} for w in WERTE],
                Value=[dict(mqtt["Value"][0], Value=[zeichenkette(w, "") for w in WERTE])],
                Events=[{"Name": "Refreshed", "Script": SKRIPT}])
    stile = vj["Styles"] + [{"Name": n, "Setters": [{"Property": p, "Value": v} for p, v in stil_setter(f, g, w)]}
                            for n, f, g, w in STILE]
    leer_hub = {"HubUrl": "", "UserGroupKey": "", "MQTTServer": "", "MQTTServerPort": 1883, "IsMQTTSecureChannel": False}
    bj = dict(vj, Styles=stile, PeakboardHubInfo=leer_hub)
    bj["Data"] = {"Elements": [zeit] + zahlen + [liste, mqtt], "ReloadFlows": []}
    bj["Screens"] = [dict(vj["Screens"][0], Background=SEITE,
                          Controls=[control_json(e, texte[0], rechtecke[0]) for e in reversed(LAYOUT)])]

    # --- Daten (XML)
    zeit_xml = vx[vx.index("<Time "):vx.index("</Time>") + len("</Time>")]
    browser_xml = vx[vx.index("<Browser>"):vx.index("</Browser>") + len("</Browser>")]
    stile_alt = vx[vx.index("<controls:PeakboardGrid.Resources>") + len("<controls:PeakboardGrid.Resources>"):
                   vx.index("</controls:PeakboardGrid.Resources>")].rstrip()
    stile_neu = "".join(stil_xml(n, stil_setter(f, g, w)) for n, f, g, w in STILE)
    spalten = lambda namen: "".join("\n        <Column>%s</Column>" % n for n in namen)
    zeilen = "".join('\n          <String Name="%s">%s</String>' % (k, escape(v)) for k, v in ANZEIGE_START.items())
    themen = "".join('\n        <Topic QosLevel="AtMostOnce" Title="%s" Datapath="">%s%s</Topic>' % (w, TOPIC, w)
                     for w in WERTE)
    controls = "".join("\n        " + control_xml(e) for e in LAYOUT)
    xml = f"""<Peakboard xmlns="http://schemas.theobald-software.com/pbmx/2015">
  <Data>
    {zeit_xml}{"".join(f'''
    <PeakboardNumber Name="{n}">0</PeakboardNumber>''' for n in ZAHLEN)}
    <PeakboardList Name="{ANZEIGE}" TriggerRefreshScriptOnLoad="False">
      <TriggerReloadFlowOnDataChange>True</TriggerReloadFlowOnDataChange>
      <Columns>{spalten(ANZEIGE_START)}
      </Columns>
      <Items>
        <Object>{zeilen}
        </Object>
      </Items>
    </PeakboardList>
    <MqttList Name="{MQTT}" TriggerRefreshScriptOnLoad="False">
      <QueueSize>15</QueueSize>
      <MessageType>Simple</MessageType>
      <TriggerReloadFlowOnDataChange>True</TriggerReloadFlowOnDataChange>
      <Columns>{spalten(WERTE)}
      </Columns>
      <ConnectionId>{verbindung_id}</ConnectionId>
      <Subscriptions>{themen}
      </Subscriptions>
      <Events>
        <Event Name="Refreshed" Script={quoteattr(SKRIPT)} />
      </Events>
    </MqttList>
    <ReloadFlowSettingsCollection />
  </Data>
  {browser_xml}
  <PeakboardHubInfo>
    <HubUrl></HubUrl>
    <UserGroupKey></UserGroupKey>
    <MQTTServer></MQTTServer>
    <MQTTServerPort>1883</MQTTServerPort>
    <IsMQTTSecureChannel>False</IsMQTTSecureChannel>
  </PeakboardHubInfo>
  <Screen Title="Screen1" Duration="00:00:00" Transition="FadeOver" ControlAnimation="Default">
    <View>
      <controls:PeakboardGrid xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns:controls="using:Peakboard.Runtime.Controls" BackgroundImageStretch="Fill" Background="{SEITE}" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
        <controls:PeakboardGrid.Resources>{stile_alt}{stile_neu}
        </controls:PeakboardGrid.Resources>{controls}
      </controls:PeakboardGrid>
    </View>
  </Screen>
</Peakboard>"""

    manifest = dateien["Manifest.xml"].decode("utf-8")
    alt_id = manifest[manifest.index("<ID>") + 4:manifest.index("</ID>")]
    alt_titel = manifest[manifest.index("<Title>"):manifest.index("</Title>") + 8]
    alt_beschr = manifest[manifest.index("<Description>"):manifest.index("</Description>") + 14]
    manifest = (manifest.replace(alt_id, str(uuid.uuid4()))
                .replace(alt_titel, "<Title>%s</Title>" % os.path.basename(ziel))
                .replace(alt_beschr, "<Description>Sortieranlage Team Software HSNR – Anzeige über MQTT vom "
                                     "Raspberry Pi</Description>"))

    crlf = lambda s: s.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    neu = {
        "Connections.pbcx": crlf(json.dumps({verbindung_id: verbindung}, indent=2, ensure_ascii=False)),
        "Manifest.xml": crlf(manifest),
        "Peakboard.json": crlf(json.dumps(bj, indent=2, ensure_ascii=False)),
        "Peakboard.xml": crlf(xml),
    }
    vorschau = os.path.join(os.path.dirname(ziel), "Sortieranlage_Board_Vorschau.png")
    if os.path.exists(vorschau):
        neu["thumb.png"] = open(vorschau, "rb").read()
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for name, inhalt in dateien.items():   # Reihenfolge und Resources\ der Vorlage beibehalten
            z.writestr(name, neu.get(name, inhalt))
    print("geschrieben:", ziel)


def vorschau_html(ziel_html):
    """HTML-Vorschau desselben Layouts (mit Beispielwerten) – für Doku und thumb.png."""
    beispiel = {wert("zyklen"): "12", wert("anzahl_weiss"): "4", wert("anzahl_rot"): "5", wert("anzahl_blau"): "3",
                wert("fehler_anzahl"): "1", anzeige("ZustandText"): "Fährt zum Auswerfer", anzeige("FarbeText"): "Rot",
                anzeige("FehlerText"): "Keine Störung", anzeige("ModusText"): "Testbetrieb (Simulation)",
                "{Time}": "16:42"}
    aktiv = {"ZustandNr": "1", "FarbeNr": "2", "FehlerNr": "0"}
    groesse = {"header2": (50, 700), "kachel_titel": (36, 400), "wert_gross": (72, 700), "zahl_gross": (90, 700),
               "zahl_riesig": (200, 700), "banner": (48, 700)}
    farbe_hex = lambda f: "#" + f[3:]
    teile = []
    for e in LAYOUT:
        stil = "left:%dpx;top:%dpx;width:%dpx;height:%dpx;" % (e["x"], e["y"], e["w"], e["h"])
        if e["art"] == "rect":
            bg = e["bg"]
            for _, var, w, f in e["regeln"]:
                if aktiv[var] == w:
                    bg = f
            teile.append('<div style="%sbackground:%s;border-radius:%dpx"></div>' % (stil, farbe_hex(bg), e["radius"]))
        else:
            g, gew = groesse[e["schrift"]]
            farbe = "#B0BEC5" if e["schrift"] == "kachel_titel" else "#FFFFFF"
            teile.append('<div style="%sfont-size:%dpx;font-weight:%d;color:%s;text-align:%s;line-height:1.15">%s</div>'
                         % (stil, g, gew, farbe, "right" if e["rechts"] else "left",
                            html.escape(beispiel.get(e["text"], e["text"]))))
    with open(ziel_html, "w", encoding="utf-8") as f:
        f.write('<!doctype html><meta charset="utf-8"><style>body{margin:0}div{position:absolute;'
                'font-family:"Segoe UI",Helvetica,Arial,sans-serif;overflow:hidden}</style>'
                '<div style="left:0;top:0;width:1920px;height:1080px;background:%s">%s</div>'
                % (farbe_hex(SEITE), "".join(teile)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if sys.argv[1] == "--vorschau":
        vorschau_html(sys.argv[2])
    elif sys.argv[1] == "--heimtest":
        globals().update(HEIMTEST)
        LAYOUT[1]["text"] += " (HEIMTEST)"
        bauen(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ZIEL)
    else:
        bauen(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ZIEL)
