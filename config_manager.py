import json
import os
import sys
from getpass import getpass

def printException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("Error:")
    print(exc_type, fname, exc_tb.tb_lineno)

# Dateipfade für die Konfiguration
botfile = "config/ani.json"
botfolder = "config/"

def loadconfig():
    try:
        os.makedirs(os.path.dirname(botfolder), exist_ok=True)
        with open(botfile, "r") as infile:
            data = json.load(infile)
    except Exception as e:
        printException(e)
        print("ani.json nicht gefunden oder fehlerhaft.")
        return False, False, False, False, False, False, False, False, False
    
    try:
        value = data["settings"]
        return (
            value['jdhost'], value['hoster'], value['browserengine'],
            value['browserlocation'], value['pushbullet_apikey'], value['timedelay'],
            value['myjd_user'], value['myjd_pw'], value['myjd_device']
        )
    except Exception as e:
        printException(e)
        print("Fehlerhafte ani.json Konfiguration")
        return False, False, False, False, False, False, False, False, False

def editconfig():
    print("Konfiguration bearbeiten...")
    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pw, myjd_device = loadconfig()
    
    # Hoster ändern
    hoster_map = {"uploaded": 0, "ddownload": 1, "rapidgator": 2}
    hoster_reverse_map = {0: "uploaded", 1: "ddownload", 2: "rapidgator"}
    print(f"Aktueller Hoster: {hoster_reverse_map.get(hoster, 'unbekannt')}")
    if input("Möchtest du den Hoster ändern? (J/N): ").lower() in ["j", "ja", "yes", "y"]:
        while True:
            hoster_input = input("Neuer Hoster (uploaded/rapidgator/ddownload): ")
            if hoster_input in hoster_map:
                hoster = hoster_map[hoster_input]
                break
            print("Ungültige Eingabe! Bitte erneut versuchen.")
    
    # JDownloader Host ändern
    print(f"Aktueller JDownloader Host: {jdhost}")
    if input("Möchtest du den JDownloader Host ändern? (J/N): ").lower() in ["j", "ja", "yes", "y"]:
        jdhost = input("Neuer JDownloader Host: ") or "127.0.0.1"
    
    # Browser ändern
    browser_map = {"Firefox": 0, "Chrome": 1}
    browser_reverse_map = {0: "Firefox", 1: "Chrome"}
    print(f"Aktueller Browser: {browser_reverse_map.get(browser, 'unbekannt')}")
    if input("Möchtest du den Browser ändern? (J/N): ").lower() in ["j", "ja", "yes", "y"]:
        while True:
            browser_input = input("Neuer Browser (Chrome/Firefox): ")
            if browser_input in browser_map:
                browser = browser_map[browser_input]
                break
            print("Ungültige Eingabe! Bitte erneut versuchen.")
    
    # Pushbullet Key ändern
    print(f"Aktueller Pushbullet API-Key: {pushkey}")
    if input("Möchtest du den Pushbullet API-Key ändern? (J/N): ").lower() in ["j", "ja", "yes", "y"]:
        pushkey = input("Neuer Pushbullet API-Key (leer lassen für keinen): ") or ""
    
    # Zeitverzögerung ändern
    print(f"Aktuelle Zeitverzögerung: {timedelay} Sekunden")
    if input("Möchtest du die Zeitverzögerung ändern? (J/N): ").lower() in ["j", "ja", "yes", "y"]:
        while True:
            try:
                timedelay = int(input("Neue Zeitverzögerung in Sekunden: "))
                break
            except ValueError:
                print("Bitte eine gültige Zahl eingeben!")
    
    # MyJDownloader Login-Daten ändern
    if myjd_user:
        print(f"Aktueller MyJDownloader Benutzer: {myjd_user}")
    if input("Möchtest du MyJDownloader-Daten ändern? (J/N): ").lower() in ["j", "ja", "yes", "y"]:
        myjd_user = input("Neuer MyJDownloader Nutzername: ") or ""
        myjd_pw = getpass("Neues MyJDownloader Passwort (leer lassen für kein Login): ") or ""
        myjd_device = input("Neues MyJDownloader Gerät: ") or ""
    
    # Speichern der neuen Konfiguration
    settingsdata = {
        "jdhost": jdhost,
        "hoster": hoster,
        "browserengine": browser,
        "browserlocation": browserlocation,
        "pushbullet_apikey": pushkey,
        "timedelay": timedelay,
        "myjd_user": myjd_user,
        "myjd_pw": myjd_pw,
        "myjd_device": myjd_device
    }
    
    os.makedirs(os.path.dirname(botfolder), exist_ok=True)
    with open(botfile, "w") as jfile:
        json.dump({"settings": settingsdata}, jfile, indent=4, sort_keys=True)
    
    print("Einstellungen gespeichert.")

if __name__ == "__main__":
    print("Teste Konfigurationsmodul...")
    print("Lade aktuelle Konfiguration:")
    print(loadconfig())
    print("Starte Edit-Modus...")
    editconfig()