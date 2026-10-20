# Projekt: Modernisierung fischertechnik-Sortieranlage (Team Software)

Dieser Ordner ist der Arbeitsordner für den Kurs "Projektmanagement (IoT und Digitalisierung) WS 26/27", Hochschule Niederrhein. Sprache: Deutsch. Nutzer: Rushit Vlasi (Softwareleitung, Team Software). Auftraggeber/Berater: Prof. Kampker.

## Auftrag (Quelle: Projektauftrag HSNR V2)
- Sortierstrecke der fischertechnik Fabrik Simulation 9V: TXT-Controller durch Raspberry Pi ersetzen. Software in Python, Entwicklung mit VS Code.
- Farbe erkennen, Förderband steuern, pneumatisch ausschleusen, Werkstück-Ausgang prüfen.
- Daten (Zustand, Zykluszahl, Farbe, Fehler) per MQTT an die Peakboard Box, Anzeige auf Bildschirm.
- Lokales Netz: TP-Link-Router (kein Internet nötig). Budget max. 250 €. Laufzeit 29.09.2026–02.02.2027. Wöchentliches Regelmeeting.
- Keine eigene Elektronik/Lötarbeit. 9-V-Aktoren NIE direkt an Raspberry-Pi-GPIOs. Geprüfte Bauteile: Pimoroni Automation HAT PIM213, Waveshare Motor Driver HAT SKU 15364.
- Abnahme: mehrere Sortierzyklen mit verschiedenen Farben, Peakboard-Anzeige, mindestens ein Fehlerfall; Dokumentation muss ein anderes Team zum Starten befähigen.

## I/O Sortierstrecke (Quelle: 9V-Handbuch, Belegungsplan)
Eingänge: I1 Fototransistor Farbsensor, I2 Farbsensor (analog), I3 Fototransistor Auswurf, I6/I7/I8 Lagerstellen weiß/rot/blau (zunächst nicht im Umfang), C1 Impulstaster.
Ausgänge: M1 Förderband, O5/O6/O7 Ventile Auswurf weiß/rot/blau, O8 Kompressor.

## Raspberry Pi Zugriff
- Host `hsnrpi1.local`, Benutzer `admin` (laut Anhang 6). Passwort/SSID/IPs NICHT erfunden und nicht gespeichert – kommen von Prof. Kampker.
- Siehe `Pi_SSH_SCP_Kurzanleitung.md` und `pi_deploy.ps1`.

## Vorgeschlagene Python-Struktur
`inputs.py` (Sensoren), `outputs.py` (Aktoren), `process.py` (Zustandslogik), `mqtt_client.py` (MQTT), `config.py` (I/O-Zuordnung, Timeouts), `main.py` (Start). Hardwarezugriff und Prozesslogik trennen; Timeouts und Fehlerzustände vorsehen.

## MQTT-Topics (Vorschlag, noch abzustimmen)
`sortieranlage/status`, `sortieranlage/zyklen`, `sortieranlage/farbe/letzte`, `sortieranlage/farbe/anzahl`, `sortieranlage/fehler` (JSON-Payload).

## Dateien in diesem Ordner
- `Leistungsnachweis_gesamt_bis_13-10-2026_aktualisiert.xlsx` – Leistungsnachweis + Anhänge 1–9 + Blatt "KI-Kontext" (Gesamtüberblick, offene Punkte).
- `Datenflussplan_13-10-2026.pdf/.png` – Abgabe vom 13.10.2026.
- `Netzwerkplan_13-10-2026.png`.
- `Pi_SSH_SCP_Kurzanleitung.md`, `pi_deploy.ps1`, `Mail_Entwurf_Kampker.md`.
- `Datenflussplan_V2_13-10-2026.png/.pdf` (Quelle `quellen/Datenflussplan_V2.html`, gerendert mit Chrome headless) – einmalige Laptop-Anbindung → autonomer Pi-Betrieb.
- `README.txt` – Ablauf der Laptop-Anbindung (wer macht was), NEEDTODO-Liste, Peakboard-Vorgehen. Zuerst lesen.
- `sortieranlage/` Python-Steuerung (Standardbibliothek, Simulation Standard, `selbsttest.py`), `pi/` (pi_setup.sh, systemd, Mosquitto-Conf), `laptop/` (01 SSH-Schlüssel: Mensch; 02 einspielen: Claude, BatchMode über ssh-Alias `hsnrpi`), `peakboard/` (MQTT-Schnittstelle).

- `M2_Arbeitsauftraege/` – Arbeitsaufträge To-Do 2.1–2.4 (P1–P4) bis Regelmeeting 20.10.2026 als PDF (Quelle `quellen/Arbeitsauftraege_M2.html`) + vorbefüllte CSV-Vorlagen. Achtung: MQTT-Schema in Excel Anhang 7 A2 weicht vom Code/`peakboard/` ab – P4 entscheidet.

- `piverbindungtest1.ps1/.bat` – erster Verbindungstest ohne Internet (Pi suchen, Ping, Port 22/1883, SSH mit Passworteingabe durch den Nutzer, Code nach `~/sortieranlage_test`, pi_setup.sh-Bericht + Selbsttest). Bericht in `pi_berichte/`.
- Verbindungstest 13.10.2026 BESTÄTIGT (pi_berichte/piverbindungtest1_2026-10-13_1740.txt): Hostname `hsnrpi1` (nicht hsnrrp1), Raspberry Pi 4 Model B, Debian 13 trixie, Python 3.13.5. Netz 192.168.1.0/24, Gateway 192.168.1.1, Pi eth0 192.168.1.103 + wlan0 192.168.1.180, Laptop per WLAN 192.168.1.187. Kein Internet, Pi-Uhr falsch, sudo verlangt Passwort, Mosquitto/i2c-tools/automationhat fehlen, GPIO-I2C (/dev/i2c-1) nicht aktiv (nur i2c-20/21 = HDMI). Selbsttest auf dem Pi bestanden; Testcode in ~/sortieranlage_test.
- Excel Anhang 10 + Blätter „M2 2.1–2.4“ (Arbeitsaufträge, orange Reiter; Abschnitt „Weitere Aufgaben W1–W7“). Überlappende Zellverbindungen in Anhang 3/4 behoben (Excel meldete „Repaired“).
- Bestellliste Team Hardware (quellen/Bestellliste_Sortieranlage.pdf, 92,50 €): **Automation HAT Mini** (1 Relais, 3 Ein-/3 Analog-/3 Ausgänge), Waveshare Motor Driver HAT, GPIO-Multiplexer, Kabel, WAGO-Klemmen; kein 9-V-Netzteil. Code angepasst: `config.HAT_TYP="mini"`, Anschluss-VORSCHLAG in EINGAENGE/AUSGAENGE (I1→input1, I3→input2, C1→input3, I2→analog1, O5–O7→output1–3, O8→relay1, M1→Motor A), `config.anschluss_pruefen()`, `motor_hat.py` (PCA9685 per /dev/i2c-1, nur stdlib, ungetestet), `hardware_ersatztest.py` (12/12). piverbindungtest2 prüft auch Python-Module und I2C-Geräte 0x48/0x40.
- `PI_EINRICHTEN.bat/.ps1` (Laptop, Doppelklick, offline): tar|ssh nach ~/sortieranlage + SSH-Key, dann `ssh -t … sudo bash pi_installieren.sh <unixzeit> [--autostart]` (Uhrzeit, I2C via raspi-config, Mosquitto-Netzfreigabe nur ohne vorhandene listener-Konfig mit Rollback, Treiberprüfung, Tests, Dienst, Platinen 0x48/0x40, ggf. `shutdown -r +1`), Bericht → pi_berichte, dann piverbindungtest2. `hat_mini.py` = eingebauter Treiber (gpiozero + ADS1015 per I2C; BCM-Pins 26/20/21 Ein, 5/12/6 Aus, 16 Relais – VORSCHLAG), `lade_hat()` nimmt automationhat falls vorhanden.
- Arbeitskarten (alle Aufgaben, die Menschen erledigen müssen, je Person S1–S8, P1-1…P5-2, H-1, mit Schritten/Fertig/Problem/Nicht-tun + Vorlagen A–G): Excel-Blatt „ARBEITSKARTEN“ (Blattnamen max. 31 Zeichen!), PDF `Arbeitskarten/…pdf` (Quelle `quellen/Arbeitskarten.html`), Google Doc im Drive. `PI_INTERNET.bat` (optional, nur mit Prof-OK): Pi kurz per Handy-Hotspot ins Internet über `pi/pi_internet.sh` (bricht ohne eth0 ab, trap trennt automatisch).
- 15.10. nachmittags: Moodle-Kurs id=13093 (im eingebauten Browser angemeldet). Aus `Sorting_Line.rpp` übernommen: FARB_MESSUNG min, Grenzen 1160/1500 (→ 0,116/0,150 bei ANALOG_MAX_V 10), IMPULSE 5/15/26 (beide Flanken), VENTIL_PULS_S 0,5; Original schaltet zusätzlich M2 3 s (unklar). Kursfolien „HSNR MQTT Raspberry Peakboard“: Topic-Beispiel hsnr/sortieranlage/event {event,color,cycle_count,timestamp} → zusätzlich `<basis>/event`; Einzelwerte `<basis>/wert/*` (Text, retain) für Peakboard; `--topic-basis`, `--fehler-alle`. `PEAKBOARD_TESTDATEN.bat` (Laptop: an der Anlage → Pi-Broker, zuhause → test.mosquitto.org/broker.hivemq.com mit Basis hsnr-sortieranlage-teamsoftware). Skripte finden den Pi per Name, falls sich die IP ändert (Internet via Router-Kaskade „Kleutges“). pi_installieren.sh installiert Hilfsprogramme + NTP, wenn Internet da ist.
- **Gantt = Arbeitsgrundlage ab 15.10.2026**: Excel-Blatt „GANTT ab 15.10 (krit. Pfad)“ (bedingte Formatierung, Balken folgen Start/Ende/Status), PDF `Gantt/…pdf`, Google Doc im Drive. Kritischer Pfad H4→H5→H6→H7→E1→E3→E4→T1→T2→A1→A2→A3→A4. P3 = Draht zu Team Hardware (HW1–HW10, Karte P3-0). Generatoren in `werkzeuge/excel/` (siehe LIESMICH_werkzeuge.txt) – nach jedem Regelmeeting Status pflegen und Pfad neu rechnen.
- Plan: Code-Einspielung KW 43 (ab 19.10.), erst nachdem Team Hardware angeschlossen hat. Ablauf Schritt 0–8 im Excel-Blatt „LIES MICH - Einfach erklaert“ (grüner Reiter, für Laien) und als Google Doc im Drive-Ordner. Nutzer ist Laie → alles einfach erklären.
- Stand 15.10.2026 (später): Mosquitto laut Prof. Kampker auf dem Pi installiert (ungeprüft → `piverbindungtest2.bat`, prüft Dienst, Netz-Listener, anonymen Zugriff vom Laptop via `laptop/mqtt_test_laptop.py`; `-SimStarten` startet Dauer-Simulation). Anhang 10 enthält jetzt „PFLICHT JETZT“ J1–J14 und „ERST NACH DEM TESTING“ T1–T10 (auch als Google Doc im Drive-Ordner). Code: MQTT im Hintergrund-Thread, Entprellung C1, FARB_BEREICHE/FARB_MESSUNG statt FARB_SCHWELLEN, `io_monitor.py` (nur lesen), Selbsttest 5 Fälle. Offene Code-Entscheidungen: Motor (J5), Quittierung (J7), Ausgangsprüfung (J8), Zweitwerkstück (J9). Leistungsnachweis Zeile 11 = 15.10. (0,5 h, Ort „Remote“ – vom Nutzer nicht genannt).
- Stand 15.10.2026: Anhang 7 mit gemessenen IPs (C1, S3, B3 Nr. 2), neuem Abschnitt D Verbindungstest und E Datenflussplan V2 (Bild image5.png); KI-Kontext aktualisiert; Seite 1 Zeile 13.10. konsolidiert (Arbeitszeit E10 weiter 2 h – vom Nutzer zu bestätigen).
- Google Drive (Konto kubilayff@gmail.com): Team-Ordner https://drive.google.com/drive/folders/1Y78I7ZrLTqD7yeOHkOy1qJUV80fm9HNn mit Google Doc „M2 Arbeitsaufträge …“ und 4 Google Sheets „M2 2.x …“. Nur Drive-Connector vorhanden → Dateien können nicht in place bearbeitet werden (Google Sheets/Docs-Connector fehlt).

## MQTT-Anmeldung (16.10.2026)
Prof. Kampker hat Mosquitto MIT Benutzer/Passwort eingerichtet und Zugangsdaten für MQTT und die Peakboard Box geschickt. Auf Wunsch des Nutzers (16.10., „nur Testmodul“) stehen ALLE bekannten Zugangsdaten (Pi, MQTT, Peakboard Box; WLAN offen) in `.env` im Projektordner – NUR dort, nie in Excel/Drive/PDF/Doku. Laptop-Skripte und `config.py` lesen die MQTT-Werte daraus automatisch. Steuerung: `config.mqtt_zugang()` (Env `SORTIER_MQTT_USER`/`SORTIER_MQTT_PASS` oder `~/.sortieranlage_mqtt` auf dem Pi, legt PI_EINRICHTEN nach Eingabe durch den Menschen an). Laptop-Skripte fragen den Zugang ab. pi_installieren.sh legt keine anonyme Freigabe an, wenn Mosquitto schon eigene Einstellungen hat. Getestet nur mit Probe-Broker – am echten Pi noch OFFEN.

## Team (Stand 15.10.2026)
P1 Rushit Vlasi = Leitung (koordiniert, KEINE eigenen Gantt-Aufgaben) · P2 Jan (Sensoren + Peakboard-Texte) · P3 Alhasane (Aktoren + Draht zu Team Hardware) · P4 Marie (Daten/Peakboard-Board) · P5 Hassan = Testen, Doku, Ablaufmodell 2.3, Abnahme · P6 Dogukan = Pi, Netzwerk, Organisation, leitet den Einspieltag. P3/P4 hat das Team am 18.10. selbst getauscht (Alhasane = P3, Marie = P4) – übernommen 20.10.; Jan = P2 laut Rushit. Drive-Ordner freigegeben (Stand 17.10.) für Marie, Jan, hziyani1 (= Hassan) und Alhassbarry94 (= Alhasane). Dogukan hat (noch) keinen Drive-Zugang und bekommt seine Aufgaben von Rushit manuell – seine To-dos trotzdem in der Liste führen, Status ggf. über Rushit nachtragen. Arbeitsgrundlage ist das Blatt „GANTT ab 15.10 (krit. Pfad)“; Generatoren in `werkzeuge/excel/` (siehe LIESMICH_werkzeuge.txt).

## Wochenrhythmus (ab 20.10.2026)
Team jetzt 7 Ausführende: P2 Jan, P3 Alhasane, P4 Marie, P5 Hassan, P6 Dogukan, P7 Melih (Schnittstellen + Abstimmung Team Netzwerk), P8 Hamza (Peakboard Box + Bildschirm). Rushit koordiniert nur. Jede Woche: `werkzeuge/excel/woche.py` neu schreiben (alte als woche_kwNN.py aufheben) → `python woche_drive.py <xlsx>` → als Google-Tabelle in den Team-Ordner hochladen (Reiter 1 = ★ TO-DO, je Aufgabe ein Reiter zum Eintragen) → alte Wochen-Tabelle nach 99 ALT → TODO_SHEET_URL in woche.py eintragen → `todo_team.py excel` + `abgabe_blatt.py`. KW 43: Tabelle 1DuZ2UUs9cQRFxrFO-DPKGI-sL-6l2aLFfs1L8jQXP_E. Einsammeln: download_file_content (CSV nur Reiter 1; für alle Reiter exportMimeType xlsx). Nicht per Klick im Browser in Google Sheets schreiben (fehleranfällig).
Hardware: Team Hardware hat am 20.10. die GPIO-Belegung geliefert (quellen/GPIO-Schnittstellen_TeamHardware_2026-10-20.pdf) – identisch mit config.py, dort als BESTÄTIGT markiert. Teile sind am 20.10. eingetroffen, 9-V-Netzteil vorhanden. Code liegt auf Rushits Laptop (PI_EINRICHTEN von dort ausführen).

## Drive-Struktur (ab 20.10.2026)
Team-Ordner 1Y78I7ZrLTqD7yeOHkOy1qJUV80fm9HNn: oben „00 ★ START HIER“ (Doc 1q35OVnJ6rBrDMVL3lsK2jSYI6nNlX4rFv2J0_eYYn9M) + ★ TO-DO-Tabelle der laufenden Woche. Unterordner: 01 Zeitplan + Anleitungen (1zSHBd05tWyQX_1Gkh3jEx_l_p7A8fqYc; Gantt-Doc 1zenI3GuRR2WrM3DhngxhVIC9K-pMcFad8Xn2S1a1euc), 02 Listen 2.1–2.4 (1XBEUpPK6_s3zuco96inFVdwVJJm7HRzS), 03 Bilder + Skizzen (1OKrHUu9QyIRD-joQysAJ4uNNR9Nmvg4b), 04 Excel-Gesamtdatei (1jnn_ZnMIJR3Po7XsgvxGtrpSGON5EE9n – Excel lädt Rushit von Hand hoch, der Connector schafft 4 MB nicht), 99 ALT (1MAbnFlxqyXYJvD-QQyI5hCKuQKnQm7bz). Veraltetes immer nach 99 ALT verschieben, nie löschen. Ordner 04 heißt seit 20.10. „04 Excel + PDFs“ (Excel + alle PDFs; Upload nur von Hand durch Rushit – der eingebaute Browser öffnet keinen Dateidialog, API-Umwege sind gesperrt). Moodle (Kurs 13093, Abschnitt „Teilprojekt SW“): Link zum Drive-Ordner + Verzeichnis „Team Software – Unterlagen (Stand 20.10.2026)“ mit 6 Dateien – hochgeladen über Claude in Chrome (file_upload ins Moodle-Formular); bei neuen Ständen dort Dateien ersetzen. Dateien anderer Besitzer (z. B. Maries Bildschirmskizze) kann Claude nicht verschieben.

## Stand Pi-Einrichtung (20.10.2026, vor Ort)
- Pi diesmal nur per WLAN erreichbar: 192.168.1.180 (MAC dc-a6-32-cc-d2-00), Laptop Rushit im WLAN „TP-Link_25F4“ = 192.168.1.187 (TP-Link hatte Internet über Router-Kaskade). Unbekanntes Gerät 192.168.1.81 (evtl. Peakboard Box). LAN-Kabel Laptop→Router bekam keine DHCP-Adresse (Kabel/Buchse prüfen).
- SSH-Schlüssel funktioniert (BatchMode). PI_EINRICHTEN: Schritte 1–3 OK (~/sortieranlage kopiert, ~/.sortieranlage_mqtt mit MQTT-Zugang angelegt). Schritt 4 (sudo pi_installieren.sh: I2C, Dienst, Uhrzeit) NICHT gelaufen – erster Versuch Verbindung beim Passwort abgerissen, zweiter vom Nutzer auf später verschoben. → Nächstes Mal: PI_EINRICHTEN -PiIP 192.168.1.180 im Terminal starten, Nutzer tippt sudo-Passwort. Dritter Versuch 20.10. ~17:50: wieder „client_loop: send disconnect: Connection reset“ genau beim sudo-Prompt, danach Pi gar nicht mehr erreichbar (SSH-Timeout) → Verdacht: Pi-WLAN instabil oder Pi startet neu (Stromversorgung mit aufgesteckten HATs?). Nächstes Mal: Pi per LAN-Kabel an gelbe TP-Link-Buchse, offizielles 5-V/3-A-Netzteil, vorher `uptime`/`vcgencmd get_throttled` prüfen.
- MQTT BESTÄTIGT: Broker auf dem Pi (allow_anonymous false, password_file), Laptop-Test mit Benutzer aus .env OK, Steuerungs-Simulation auf dem Pi hat mit Login retained Werte gesendet.
- Fehlalarme in piverbindungtest2 beheben: „MOSQUITTO_FEHLT“ (Prüfung findet /usr/sbin/mosquitto nicht) und „Steuerungs-Simulation 0 Nachrichten“ (mosquitto_sub auf dem Pi ohne -u/-P → not authorised).

## Wenn der Laptop mit dem Pi verbunden ist
README.txt Abschnitt 2 folgen: erst `.\laptop\02_einspielen.ps1 -Schritt Pruefen`. Claude tippt keine Passwörter; ohne Schlüssel (Schritt 01) den Nutzer bitten. `-Installieren`/`-Autostart` nur nach Freigabe. Danach Bericht in `pi_berichte/` auswerten und Excel/Netzwerkplan aktualisieren.

## Leistungsnachweis
Sicherungen: Jedes Skript legt vor jeder Änderung eine Kopie im Scratchpad (Temp) an. Zusätzlich am Ende jeder Sitzung den Tagesstand nach `sicherungen\Leistungsnachweis_JJJJ-MM-TT.xlsx` kopieren (Ordner ist von GitHub ausgeschlossen).
Blatt 2 „Leistungsnachweis (Abgabe)“ (sheet20.xml) = saubere Kopie von Blatt 1 Zeilen 1–24 + Zweizeiler-Wochenziel (ZIEL in todo_team.py) – nach JEDER Änderung an Blatt 1 `python werkzeuge\excel\abgabe_blatt.py <xlsx> <backup>` ausführen. Blatt 1 bleibt die Arbeitsfassung mit To-do-Block. Zeiten: Regelmeeting 2 h/Woche, jede Claude-Sitzung eigene Zeile, min. 0,5 h, realistisch.
Alles, was wir tun, laufend auf Blatt 1 ("Leistungsnachweis") in der Zeile des heutigen Datums ergänzen (XML direkt im xlsx bearbeiten, openpyxl ist nicht installiert und würde Bilder gefährden).
Ablage/Versand: Team-Drive (Konto kubilayff).

## GitHub + To-do (ab 17.10.2026)
- Öffentliches Repository https://github.com/Fehmilay/sortieranlage-teamsoftware (Konto Fehmilay, kein git installiert → Upload per `gh api`, Skript `werkzeuge/github_hochladen.py`). `.env` NIE hochladen (steht in .gitignore).
- To-do-Liste fürs Team bis zum nächsten Regelmeeting: EINE Quelle `werkzeuge/excel/todo_team.py` → Block unten auf Seite 1 der Excel (ab Zeile 27, außerhalb des Druckbereichs) + Google-Tabelle im Drive (ID 1MI7Egtn5bykn7BOq3XI69zSVreS4dCe1AguFCColf-I; Gantt-Doc mit Namen 1Pi6jj2J9udxW2zTxtTb2pkYBHdnaFa-hsEqna9pGLF0), in der das Team abhakt. Bei jeder Sitzung: Google-Tabelle als CSV lesen, Status/Rückmeldungen in STAND übernehmen, Fragen beantworten, Excel neu erzeugen, GitHub aktualisieren. Rushit hat keine eigenen To-dos (hält den Draht zu Claude).

## Offene Punkte (13.10.2026)
1. Automation-HAT-Kapazität (Eingänge/Relais) gegen Bedarf prüfen (3 digitale + 1 analoger Eingang, 4 Lasten).
2. Verbindungsart und IPs von Pi und Peakboard Box im TP-Link-Netz.
3. Ort des MQTT-Brokers (Vorschlag: auf dem Pi).
4. Projektordner auf dem Pi von Prof. Kampker.
5. Farb-Schwellwerte kalibrieren.
6. Fotos in Anhang 5 (06.10.) der Excel neu einfügen (waren in der hochgeladenen Datei leer).
7. E-Mail-Adresse von Prof. Kampker für den Versand des Leistungsnachweises.

## Arbeitsregeln für Claude Code
- Zugangsdaten nur in `.env` (vom Nutzer erlaubt), sonst in keine Datei. Claude tippt trotzdem keine Passwörter in ssh/Login-Masken (SSH-Schlüssel nutzen). Keine Aktorik-Befehle ohne bestätigte I/O-Liste und Verdrahtung; erst Simulation, dann Einzeltests.
- Status-Konvention in Dokumenten: BESTÄTIGT (belegt), VORSCHLAG (Team-Entwurf), OFFEN (unbekannt).
