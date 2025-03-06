import os
import json
from utils import compare

def settings():
    """Lädt und speichert die Einstellungen für den Downloader."""
    settingsfile = "config/settings.json"
    settingsfolder = "config/"
    
    try:
        os.makedirs(os.path.dirname(settingsfolder), exist_ok=True)
        with open(settingsfile, "r") as file:
            jdata = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        jdata = {}
    
    jdhost = jdata.get("jdhost", "")
    mode = jdata.get("mode", "")
    hoster = jdata.get("hoster", "")
    browserengine = jdata.get("browserengine", "")
    browserlocation = jdata.get("browserlocation", "")
    jd_user = jdata.get("myjd_user", "")
    jd_pass = jdata.get("myjd_pw", "")
    jd_device = jdata.get("myjd_device", "")
    
    # Falls ein Hoster bereits gesetzt ist, nachfragen, ob geändert werden soll
    hoster_map = {0: "uploaded", 1: "ddownload", 2: "rapidgator"}
    if hoster in hoster_map:
        print(f"Dein gewählter Hoster: {hoster_map[hoster]}")
        if not compare(input("Möchtest du den Hoster wechseln? [J/N]: "), {"j", "ja", "yes", "y"}):
            return
    
    while True:
        host = input("Welchen Hoster bevorzugst du? (uploaded/rapidgator/ddownload): ")
        if host in ["uploaded", "ddownload", "rapidgator"]:
            hoster = [k for k, v in hoster_map.items() if v == host][0]
            break
        print("Bitte gib entweder 'uploaded', 'rapidgator' oder 'ddownload' ein.")
    
    # Browser-Einstellungen
    browser_map = {"Firefox": 0, "Chrome": 1}
    if browserengine in browser_map.values():
        current_browser = [k for k, v in browser_map.items() if v == browserengine][0]
        print(f"Dein gewählter Browser: {current_browser}")
        if not compare(input("Möchtest du den Browser wechseln? [J/N]: "), {"j", "ja", "yes", "y"}):
            return
    
    while True:
        browser = input("Welchen Browser möchtest du nutzen? (Chrome/Firefox): ")
        if browser in browser_map:
            browserengine = browser_map[browser]
            break
        print("Fehlerhafte Eingabe, bitte 'Chrome' oder 'Firefox' wählen.")
    
    if compare(input("Ist dein Browser an einem anderen Ort installiert? [J/N]: "), {"j", "ja", "yes", "y"}):
        browserlocation = input("Dann gib jetzt den Pfad an: ")
    
    # Speichern der Einstellungen
    data = {
        "hoster": hoster,
        "mode": mode,
        "browserengine": browserengine,
        "browserlocation": browserlocation,
        "jdhost": jdhost,
        "myjd_user": jd_user,
        "myjd_pw": jd_pass,
        "myjd_device": jd_device
    }
    
    with open(settingsfile, "w") as file:
        json.dump(data, file, indent=4)
    
    print("Einstellungen gespeichert.")

def loadSettings():
    """Lädt gespeicherte Einstellungen."""
    settingsfile = "config/settings.json"
    
    try:
        with open(settingsfile, "r") as file:
            jdata = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Keine gültige Konfigurationsdatei gefunden.")
        return None
    
    return (
        jdata.get("jdhost", ""),
        jdata.get("mode", ""),
        jdata.get("hoster", ""),
        jdata.get("browserengine", ""),
        jdata.get("browserlocation", ""),
        jdata.get("myjd_user", ""),
        jdata.get("myjd_pw", ""),
        jdata.get("myjd_device", "")
    )

if __name__ == "__main__":
    print("Teste Settings-Manager...")
    settings()
    print(loadSettings())