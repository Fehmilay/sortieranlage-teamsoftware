# Sortieranlage – Team Software

Hochschule Niederrhein · Projektmanagement (IoT und Digitalisierung) WS 26/27 · Auftraggeber: Prof. Kampker

**Worum geht es?** Die Sortierstrecke der fischertechnik-Fabrik bekommt ein neues „Gehirn“: Ein **Raspberry Pi** mit einem
**Python-Programm** ersetzt den alten Controller. Er erkennt die Farbe der Klötze (weiß / rot / blau), steuert das Förderband,
pustet die Klötze mit Druckluft in die richtige Rutsche und schickt alles per **MQTT** an die **Peakboard Box**, die es auf einem
Bildschirm anzeigt. Abnahme: **02.02.2027**.

---

> ### 💬 Fragen zum Projekt? So bekommst du sofort eine Antwort
> 1. Diesen Link kopieren: **https://github.com/Fehmilay/sortieranlage-teamsoftware**
> 2. ChatGPT (oder Claude, Gemini …) öffnen, den Link einfügen und deine Frage dazuschreiben, z. B.
>    *„Hier ist unser Projekt: <Link>. Was genau muss ich bei Aufgabe W7 tun?“*
> 3. Die KI liest die Dateien hier und antwortet. Passt etwas nicht, Frage in die To-do-Tabelle (Spalte G) schreiben.
>
> Dieses Repository wird nach jeder Änderung aktualisiert – hier liegt immer der neueste Stand.

## ▶ START HIER – was muss ich tun?

| Schritt | Was | Wo |
|---|---|---|
| 1 | **Deine Aufgaben bis zum nächsten Regelmeeting** (mit Links, Status zum Abhaken, Feld für Rückmeldung) | Google-Tabelle **„★ KW 43 – Aufgaben bis Di 27.10.“** im Team-Drive-Ordner (ein Reiter pro Aufgabe zum Eintragen) – oder Excel, Blatt 1 ganz unten (ab Zeile 27) |
| 2 | **Schritt-für-Schritt-Anleitungen** zu jeder Aufgabe (Karte P2-3, P6-1 …) | [Arbeitskarten (PDF)](Arbeitskarten/Arbeitskarten_Schritt_fuer_Schritt_Stand_15-10-2026.pdf) |
| 3 | **Zeitplan** – wer macht was bis wann, rot = darf sich nicht verspäten | [Gantt-Plan (PDF)](Gantt/Gantt_Plan_ab_15-10-2026_mit_kritischem_Pfad.pdf) |
| 4 | **Alles in einer Datei** (Leistungsnachweis, Gantt, Arbeitskarten, LIES MICH, Listen 2.1–2.4) | [Excel herunterladen](Leistungsnachweis_gesamt_bis_13-10-2026_aktualisiert.xlsx) → Datei öffnen → oben rechts „TO-DOs fürs Team“ anklicken |
| 5 | **Fragen?** Erst den GitHub-Link mit deiner Frage in ChatGPT einfügen (Kasten oben). Sonst in die gelbe Spalte G der To-do-Tabelle oder an Hamza – er sammelt die Fragen für Rushit. | |

**Team:** Rushit (P1, Leitung – koordiniert, hält den Draht zu Claude) · Jan (P2) Sensoren · Alhasane (P3) Aktoren + Draht zu Team Hardware ·
Marie (P4) Daten/Peakboard · Hassan (P5) Testen/Doku · Dogukan (P6) **alles im Terminal + Datenübertragung zum Pi** ·
Melih (P7) Schnittstellen + Abstimmung mit Team Netzwerk/QM · Hamza (P8) **rechte Hand der Leitung: Kommunikation** + Risiken.

**Ganzen Ordner herunterladen:** oben auf den grünen Knopf **„Code“** → **„Download ZIP“** → ZIP entpacken (Rechtsklick → „Alle extrahieren“).

**Zugangsdaten** (Pi, MQTT, Peakboard Box) stehen absichtlich **nicht** hier – die Datei `.env` bekommst du von Rushit.
Nie Passwörter in die Gruppe, ins Drive oder hier hochladen.

---

## Was liegt wo?

| Ordner / Datei | Inhalt | Für wen |
|---|---|---|
| `sortieranlage/` | Das Python-Programm (Steuerung, Simulation, Selbsttest) | Claude, Dogukan |
| `PI_EINRICHTEN.bat` | **Ein Doppelklick** spielt das Programm auf den Pi und richtet ihn ein (ohne Internet) | Dogukan (Karte P6-3) |
| `piverbindungtest1.bat`, `piverbindungtest2.bat` | Tests: Ist der Pi erreichbar? Läuft das Postamt (MQTT)? | Dogukan |
| `PEAKBOARD_TESTDATEN.bat` | Schickt Testdaten, damit das Peakboard-Board schon ohne Anlage gebaut werden kann | Dogukan, Marie |
| `PI_INTERNET.bat` | Pi kurz übers Handy ins Internet (nur mit OK von Prof. Kampker) | Dogukan |
| `peakboard/MQTT_Schnittstelle.md` | Welche Daten der Pi an das Peakboard schickt | Marie (P4) |
| `Arbeitskarten/`, `Gantt/` | PDFs zum Lesen und Ausdrucken | alle |
| `M2_Arbeitsauftraege/` | Listen 2.1–2.4 (Vorlagen) | Jan, Alhasane, Marie, Hassan |
| `Datenflussplan_*`, `Netzwerkplan_*` | Bilder: wie die Daten fließen, wie das Netz aussieht | alle |
| `README.txt` | Ablauf der Laptop-Anbindung an den Pi (ausführlich) | Dogukan |
| `pi/`, `laptop/` | Hilfsdateien für die Einrichtung (werden von den .bat-Dateien benutzt) | – |
| `pi_berichte/` | Ergebnisse der Tests am echten Pi | Claude |
| `werkzeuge/` | Werkzeuge, mit denen Claude Excel, Gantt und Karten erzeugt | Claude |
| `CLAUDE.md` | Projektwissen für den KI-Assistenten | Claude |

## Sicherheit (wichtig)

- 9-V-Motoren und Ventile **nie** direkt an den Pi anschließen – nur über die Platinen (Automation HAT Mini, Motor Driver HAT).
- Motoren/Ventile erst schalten, wenn die Verkabelung geprüft ist und Prof. Kampker es freigegeben hat (Karte P3-3).
- Ohne Freigabe läuft alles in der **Simulation** – da bewegt sich nichts.

## Für Technik-Interessierte

```
cd sortieranlage
python selbsttest.py          # 5 Simulationsfälle inkl. Fehlerfälle – muss "SELBSTTEST BESTANDEN" melden
python main.py --kein-mqtt    # Simulation ohne Postamt
```

Nur Python-Standardbibliothek (läuft auf dem Pi ohne Internet). Status in den Dokumenten: **BESTÄTIGT** = belegt,
**VORSCHLAG** = Team-Entwurf, **OFFEN** = noch unbekannt.
