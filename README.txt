README – Sortieranlage Team Software (Stand 13.10.2026)
=========================================================
Zweck: Alles ist so vorbereitet, dass bei der EINMALIGEN Laptop-Anbindung an den Raspberry Pi
(Laptop im WLAN der Anlage) Claude Code die Schritte im Terminal selbst ausführen kann.
Danach läuft der Pi ohne Laptop (systemd-Autostart). Siehe Datenflussplan_V2_13-10-2026.png/.pdf.

Status-Konvention: BESTÄTIGT (belegt) · VORSCHLAG (Team-Entwurf) · OFFEN (unbekannt)
Zielkonto für Ablage/Versand: das Team-Drive (Konto kubilayff).


1. ORDNER
---------
sortieranlage\        Python-Steuerung (läuft auf dem Pi, nur Standardbibliothek, kein pip nötig)
   config.py          I/O-Zuordnung, Schwellwerte, Timeouts, MQTT, Aktorik-Sperre
   inputs.py          Sensoren (Simulation / Automation HAT)
   outputs.py         Aktoren  (Simulation / Automation HAT, gesperrt bis Freigabe)
   process.py         Zustandslogik BEREIT → FOERDERN → ZAEHLEN → AUSSCHLEUSEN → PRUEFEN, FEHLER
   mqtt_client.py     MQTT-Publisher für Peakboard (eigene Minimal-Implementierung, MQTT 3.1.1)
   simulation.py      simulierte Anlage inkl. Fehlerfälle
   main.py            Start (python3 main.py --help)
   selbsttest.py      4 Abnahmeszenarien in der Simulation (lokal BESTANDEN am 13.10.2026)
pi\                   Dateien, die zusätzlich auf den Pi kommen
   pi_setup.sh        Prüfbericht, optional Mosquitto + Autostart, Selbsttest
   sortieranlage.service       systemd-Dienst (startet Dauer-Simulation, später Hardware)
   mosquitto_sortieranlage.conf Broker lauscht im Anlagennetz auf 1883 (VORSCHLAG)
laptop\
   01_ssh_schluessel_einrichten.ps1  EINMAL VOM MENSCHEN (Passworteingabe)
   02_einspielen.ps1                 danach von Claude: kopieren, einrichten, testen, Bericht holen
peakboard\            MQTT_Schnittstelle.md (Topics, JSON, Designer-Schritte), beispiel_nachrichten.json
pi_berichte\          entsteht beim Einspielen: Bericht vom Pi (IP-Adressen, Broker, I2C/HAT)
quellen\              HTML-Quelle des Datenflussplans V2


2. ABLAUF BEI DER LAPTOP-ANBINDUNG (Terminal-Block)
---------------------------------------------------
NEU (15.10.2026) – EINFACHSTER WEG: Laptop ins WLAN der Anlage, Doppelklick auf PI_EINRICHTEN.bat,
zweimal das Pi-Passwort eintippen. Das erledigt die Schritte b–f unten automatisch (Programm kopieren,
SSH-Schlüssel, Uhrzeit, I2C, Mosquitto-Netzfreigabe, Tests, Abschlusstest) – ohne Internet.
Vorher Prof. Kampker Bescheid geben (ändert Einstellungen am Pi). Einfach erklärt: Excel-Blatt „LIES MICH“.
Die Einzelschritte unten bleiben als Rückfallweg.

Vorher (zu Hause, ohne Pi) – optional, Claude kann das jederzeit:
    cd C:\Users\apc-fehmikubi\Desktop\projektmanagement\sortieranlage
    python selbsttest.py

An der Anlage:
 [MENSCH] a) Pi + TP-Link-Router einschalten, Laptop ins Anlagen-WLAN verbinden
             (SSID/Passwort von Prof. Kampker – NICHT an Claude geben, nicht notieren).
 [MENSCH] b) PowerShell im Ordner projektmanagement öffnen und EINMAL ausführen:
                 .\laptop\01_ssh_schluessel_einrichten.ps1
             (falls hsnrpi1.local nicht gefunden wird: -PiHost <IP aus der Router-Clientliste>)
             Pi-Passwort einmal eintippen. Am Ende muss "SSH-OK: hsnrpi1" erscheinen.
             Falls PowerShell Skripte blockiert:  powershell -ExecutionPolicy Bypass -File .\laptop\01_ssh_schluessel_einrichten.ps1
 [MENSCH] c) Claude schreiben: "Pi ist verbunden".
 [CLAUDE] d) .\laptop\02_einspielen.ps1 -Schritt Pruefen
             .\laptop\02_einspielen.ps1                    (kopieren, Bericht, Selbsttest auf dem Pi)
             -> Claude wertet pi_berichte\pi_bericht_*.txt aus (IP, OS, Broker, sudo, I2C).
 [CLAUDE] e) nach Freigabe (siehe Punkt 3.5):
             .\laptop\02_einspielen.ps1 -Installieren -Autostart
             .\laptop\02_einspielen.ps1 -Schritt MqttTest
 [CLAUDE] f) Netzwerkplan/Excel mit den echten IPs aktualisieren, Leistungsnachweis Seite 1 nachtragen.
 [MENSCH] g) Laptop trennen. Pi läuft ab jetzt allein (Dauer-Simulation sendet an Peakboard).


3. NEEDTODO – was Claude von euch braucht
-----------------------------------------
 1. WLAN-Verbindung des Laptops herstellen (macht ihr selbst, Zugangsdaten bleiben bei euch).
 2. Pi-Passwort: nur einmal selbst in Schritt 2b eintippen. Claude tippt keine Passwörter.
 3. Falls hsnrpi1.local nicht aufgelöst wird: IP des Pi (Router-Clientliste) – OFFEN.
 4. Projektordner auf dem Pi (offener Punkt 4, Prof. Kampker). Standard bis dahin: ~/sortieranlage
    (anderer Ordner: 02_einspielen.ps1 -Ziel <ordner>).
 5. FREIGABE von Prof. Kampker für Änderungen am Pi: Mosquitto installieren + Konfiguration
    (nur falls Mosquitto noch keine eigene Einstellung hat – Prof. Kampker hat ihn mit Benutzer/Passwort eingerichtet, das bleibt unverändert) und systemd-Autostart. Ohne Freigabe nur Schritt 2d.
 6. Internet für den Pi? Mosquitto kommt per apt. Optionen, wenn kein Internet:
    a) prüfen, ob Mosquitto schon installiert ist (steht im Pi-Bericht),
    b) Pi kurz per LAN an einen Router mit Internet,
    c) .deb-Pakete passend zur Pi-OS-Version (steht im Bericht) vorab herunterladen und in
       projektmanagement\pi_debs\ ablegen – 02_einspielen.ps1 nimmt sie automatisch mit
       (Claude kann das nach eurer Zustimmung vorbereiten).
 7. sudo ohne Passwort am Pi? (steht im Bericht). Falls NEIN: ihr führt am Pi selbst aus:
       cd ~/sortieranlage && sudo bash pi_setup.sh --installieren --autostart
 8. I/O-Kanäle am Automation HAT vom Hardware-Team → in sortieranlage\config.py eintragen
    (EINGAENGE/AUSGAENGE "kanal"), danach HARDWARE_FREIGEGEBEN = True – erst nach Prüfung
    der Verdrahtung, dann Einzeltests. Kapazität PIM213: 3 digitale Eingänge, 3 Analog-
    eingänge, 3 Relais, 3 Ausgänge. Bedarf: 3 digital (I1, I3, C1) + 1 analog (I2),
    Lasten M1 + O5–O7 + O8 (M1 ggf. über Motor Driver HAT) – Pegel/Spannungen OFFEN
    (offener Punkt 1).
 9. Farb-Schwellwerte und Impulse bis Ventil an der realen Anlage messen (offener Punkt 5).
    Bis dahin Platzhalter in config.py (FARB_SCHWELLEN, IMPULSE_BIS_VENTIL, ANALOG_MAX_V).
10. Peakboard: IP der Peakboard Box, Peakboard Designer auf dem Laptop, Box im selben Netz.
11. MQTT-Topics im Team abstimmen (To-Do 4.3) – Vorschlag: peakboard\MQTT_Schnittstelle.md.
12. Leistungsnachweis 13.10.: Arbeitszeit in E10 steht weiter auf 2 h – bitte ggf. anpassen.
13. Ablage/Versand an kubilayff@gmail.com: wie gewünscht? (Upload in dessen Drive oder Mail
    mit Anhang) – Claude versendet nichts ohne ausdrückliche Bestätigung im Chat.
14. Fotos in Anhang 5 (06.10.) neu einfügen; E-Mail-Adresse Prof. Kampker (offene Punkte 6/7).


4. PEAKBOARD-ANBINDUNG – VORGEHEN
---------------------------------
Ziel: Pi (Publisher) → Mosquitto auf dem Pi (Broker, :1883) → Peakboard Box (Subscriber) → HDMI.
Schritt 1  Broker läuft (02_einspielen.ps1 -Installieren, dann -Schritt MqttTest zeigt die sortieranlage/...-Nachrichten).
Schritt 2  IP des Pi aus pi_berichte\ notieren; im TP-Link-Router feste DHCP-Reservierung
           für Pi und Peakboard Box anlegen (sonst ändert sich die Broker-Adresse).
Schritt 3  Testdaten ohne Anlage: Autostart-Dienst sendet Dauer-Simulation, oder am Laptop:
               python sortieranlage\main.py --dauer --echtzeit --mqtt-host <IP des Pi>
Schritt 4  Peakboard Designer: Datenquelle MQTT (Server = IP Pi, Port 1883, ohne Login),
           5 Topics abonnieren (Liste + JSON-Felder in peakboard\MQTT_Schnittstelle.md).
Schritt 5  Dashboard: Zustand · Zykluszahl · letzte Farbe · Anzahl je Farbe · Fehler (rot wenn aktiv).
Schritt 6  Fehlerfall vorführen: python3 main.py --farben weiss,rot,blau --fehler band_blockiert
           → Fehler-Kachel wird rot, nach Quittierung wieder grün.
Schritt 7  Board auf die Peakboard Box übertragen, Anzeige am HDMI-Bildschirm prüfen.
Schritt 8  Später: Simulation durch Hardware-Modus ersetzen (Topics bleiben gleich → Dashboard bleibt).
Ausbaustufe (VORSCHLAG): Quittier-Taste im Dashboard → Topic sortieranlage/befehl (noch nicht umgesetzt).


5. FEHLERBEHEBUNG
-----------------
- ping hsnrpi1.local scheitert → IP aus Router-Clientliste, 01-Skript mit -PiHost <IP> neu starten
  (oder HostName in %USERPROFILE%\.ssh\config unter "Host hsnrpi" ändern).
- "Permission denied (publickey)" → 01-Skript erneut ausführen.
- "REMOTE HOST IDENTIFICATION HAS CHANGED" (Pi neu aufgesetzt) → ssh-keygen -R hsnrpi1.local
- Peakboard bekommt nichts → Pi-Bericht: lauscht 1883 auf 0.0.0.0? Box im selben Netz?
- Logs auf dem Pi: ~/sortieranlage/log.txt  ·  journalctl -u sortieranlage -n 50


6. SICHERHEIT
-------------
9-V-Aktoren nie direkt an GPIO. Aktorik bleibt per Software gesperrt (HARDWARE_FREIGEGEBEN = False),
bis I/O-Liste und Verdrahtung bestätigt sind. Erst Simulation, dann Einzeltests. Keine Zugangsdaten in Dateien.
