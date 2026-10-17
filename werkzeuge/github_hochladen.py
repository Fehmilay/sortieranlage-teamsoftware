"""Lädt den Projektordner als einen Commit nach GitHub (ohne git, nur mit der GitHub-CLI „gh“).

Aufruf (im Projektordner):  python werkzeuge\\github_hochladen.py "Commit-Nachricht"
Der Stand im Repository wird danach genau der lokale Ordner (gelöschte Dateien verschwinden auch dort).
Ausgeschlossen: alles aus AUSSCHLUSS – vor allem .env (Zugangsdaten).
"""
import base64, fnmatch, json, os, subprocess, sys, tempfile

REPO = "Fehmilay/sortieranlage-teamsoftware"
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUSSCHLUSS = [".env", "*.env", "__pycache__", "*.pyc", "~$*", ".git", ".claude"]


def gh(pfad, daten=None, methode=None):
    befehl = ["gh", "api", pfad]
    datei = None
    if daten is not None:
        datei = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(daten, datei); datei.close()
        befehl += ["--method", methode or "POST", "--input", datei.name]
    r = subprocess.run(befehl, capture_output=True, text=True, encoding="utf-8")
    if datei:
        os.unlink(datei.name)
    if r.returncode:
        raise SystemExit(f"gh api {pfad} fehlgeschlagen: {r.stderr or r.stdout}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def dateien():
    for wurzel, ordner, namen in os.walk(WURZEL):
        ordner[:] = [o for o in ordner if not any(fnmatch.fnmatch(o, m) for m in AUSSCHLUSS)]
        for n in namen:
            if any(fnmatch.fnmatch(n, m) for m in AUSSCHLUSS):
                continue
            voll = os.path.join(wurzel, n)
            yield os.path.relpath(voll, WURZEL).replace("\\", "/"), voll


def main():
    nachricht = sys.argv[1] if len(sys.argv) > 1 else "Aktualisierung"
    liste = sorted(dateien())
    assert not any(p.endswith(".env") for p, _ in liste), "Zugangsdaten würden hochgeladen!"
    ref = gh(f"repos/{REPO}/git/ref/heads/main")
    eltern = ref["object"]["sha"]
    baum = []
    for pfad, voll in liste:
        with open(voll, "rb") as f:
            inhalt = base64.b64encode(f.read()).decode("ascii")
        blob = gh(f"repos/{REPO}/git/blobs", {"content": inhalt, "encoding": "base64"})
        modus = "100755" if pfad.endswith((".sh",)) else "100644"
        baum.append({"path": pfad, "mode": modus, "type": "blob", "sha": blob["sha"]})
        print("  +", pfad)
    tree = gh(f"repos/{REPO}/git/trees", {"tree": baum})
    commit = gh(f"repos/{REPO}/git/commits", {"message": nachricht, "tree": tree["sha"], "parents": [eltern]})
    gh(f"repos/{REPO}/git/refs/heads/main", {"sha": commit["sha"]}, "PATCH")
    print(f"Fertig: {len(baum)} Dateien, Commit {commit['sha'][:7]} → https://github.com/{REPO}")


if __name__ == "__main__":
    main()
