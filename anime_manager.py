import os
import json
from config_manager import loadconfig
from logger import log
from utils import compare
from error_handler import printException
import animeloads

def addAnime():
    """ Fügt einen neuen Anime zur Liste hinzu. """
    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
    
    while jdhost is False:
        print("Noch keine oder fehlerhafte Konfiguration, leite weiter zu Einstellungen...")
        from config_manager import editconfig
        editconfig()
        jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
    
    al = animeloads.Animeloads(browser=browser, browserloc=browserlocation)
    exit = False
    search = False
    
    while not exit:
        print("Gib eine URL zu einem Anime oder einen Suchbegriff ein.")
        aniquery = input("URL/Anime (oder 'exit' zum Beenden): ")
        if aniquery.lower() == "exit":
            break
        
        if "https://www.anime-loads.org/media/" in aniquery:
            anime = al.getAnime(aniquery)
        else:
            results = al.search(aniquery)
            if not results:
                print("Keine Ergebnisse gefunden.")
                continue
            
            print("Suchergebnisse:")
            for idx, result in enumerate(results, start=1):
                print(f"[{idx}] {result.tostring()}")
            
            while True:
                choice = input("Wähle einen Anime (Nummer eingeben): ")
                try:
                    anime = results[int(choice) - 1].getAnime()
                    break
                except (ValueError, IndexError):
                    print("Ungültige Eingabe, bitte erneut versuchen.")
        
        releases = anime.getReleases()
        print("Verfügbare Releases:")
        for idx, rel in enumerate(releases, start=1):
            print(f"[{idx}] {rel.tostring()}")
        
        while True:
            relchoice = input("Wähle eine Release ID: ")
            try:
                relchoice = int(relchoice)
                if 1 <= relchoice <= len(releases):
                    release = releases[relchoice - 1]
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Ungültige Eingabe, bitte erneut versuchen.")
        
        print(f"Du hast {release.tostring()} gewählt.")
        curEpisodes = release.getEpisodeCount()
        existingEpisodes = input("Wieviele Episoden hast du bereits heruntergeladen? (Leerlassen für alle neuen): ")
        existingEpisodes = int(existingEpisodes) if existingEpisodes.isdigit() else curEpisodes
        
        customPackage = input("Möchtest du einen individuellen Paketnamen vergeben? (Leer lassen für Standard): ")
        
        animedata = {
            "name": anime.getName(),
            "missing": [],
            "releaseID": relchoice,
            "episodes": existingEpisodes,
            "url": anime.getURL(),
            "customPackage": customPackage
        }
        
        os.makedirs("config", exist_ok=True)
        try:
            with open("config/ani.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
             data = {}
           
        if "anime" not in data:
            data["anime"] = []

        if any(a["url"] == anime.getURL() and a["releaseID"] == relchoice for a in data["anime"]):
            print("Dieser Anime ist bereits in der Liste.")
            continue
        
        data["anime"].append(animedata)
        with open("config/ani.json", "w") as f:
            json.dump(data, f, indent=4)
        
        print("Anime erfolgreich hinzugefügt!")
        break

def removeAnime():
    """ Entfernt einen Anime aus der Liste. """
    data = loadconfig("anime")
    
    #Dodo direkt Fragen ob man ANime suchen will
    if not data:
        print("Die Anime-Liste ist leer.")
        print("Füge zuerst einen Anime hinzu in dem du python anibot.py -add eingibts")
        return
    
    print("Deine Anime-Liste:")
    for idx, animeentry in enumerate(data, start=1):
        print(f"[{idx}] {animeentry['name']} mit Release {animeentry['releaseID']}")
    
    while True:
        selection = input("Welchen Anime möchtest du löschen? (Nummer eingeben, 'exit' zum Beenden): ")
        if selection.lower() == "exit":
            print("Abbruch.")
            return
        
        try:
            sel_int = int(selection) - 1
            if 0 <= sel_int < len(data):
                removed_anime = data.pop(sel_int)

                # **Lade die komplette JSON-Datei, um die Änderungen zu speichern**
                try:
                    with open("config/ani.json", "r") as f:
                        full_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    full_data = {}  # Falls Datei nicht existiert oder defekt ist

                full_data["anime"] = data  # **Neue Anime-Liste setzen**

                # **Jetzt die komplette JSON mit allen Einstellungen speichern**
                with open("config/ani.json", "w") as f:
                    json.dump(full_data, f, indent=4)

                print(f"Anime '{removed_anime['name']}' wurde entfernt.")
                return
            else:
                print("Ungültige Auswahl, bitte erneut versuchen.")
        except ValueError:
            print("Bitte eine gültige Nummer eingeben.")

if __name__ == "__main__":
    print("Teste Anime-Manager...")
    addAnime()
    removeAnime()