import subprocess, sys, json, time, os, re
from config_manager import loadconfig, editconfig
from logger import log
from error_handler import printException



from getpass import getpass

from datetime import datetime

from pushbullet import Pushbullet

import animeloads

from animeloads import animeloads

arglen = len(sys.argv)

import myjdapi

pb = ""

botfile = "config/ani.json"
botfolder = "config/"

def is_docker():
  if not os.path.isfile("/proc/" + str(os.getpid()) + "/cgroup"): return False
  with open("/proc/" + str(os.getpid()) + "/cgroup") as f:
    for line in f:
      if re.match("\d+:[\w=]+:/docker(-[ce]e)?/\w+", line):
        return True
    return False

def compare(inputstring, validlist):
    for v in validlist:
        if(v.lower() in inputstring.lower()):
            return True
    return False

def addAnime():
    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
 
    while(jdhost == False):
        print("Noch keine oder Fehlerhafte konfiguration, leite weiter zu Einstellungen")
        editconfig()
        jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()

    al = animeloads(browser=browser, browserloc=browserlocation)
    exit = False
    search = False

    while(exit == False):
        search = False
        print("Gib nun entweder eine URL zu einem Anime-Eintrag oder einen Namen, nach dem du suchen willst ein")
        aniquery = input("URL/Anime (Du kannst jederzeit \"suche\" eingeben, um zurück zur Suche zu kommen oder \"exit\", um das Programm zu beenden): ")
        if(aniquery == "exit"):
            break
        if("https://www.anime-loads.org/media/" in aniquery):
            print("Hole Anime von URL: " + aniquery)
            anime = al.getAnime(aniquery)

            releases = anime.getReleases()
        
            print("\n\nReleases:\n")
        
            for rel in releases:
                print(rel.tostring())
    
            print("\n")
            relchoice = ""
            while(True):
                relchoice = input("Wähle eine Release ID: ")
                if(relchoice == "exit"):
                    exit = True
                    break
                elif(relchoice == "suche"):
                    search = True
                    break
                try:
                    relchoice = int(relchoice)
                    if(relchoice <= len(releases)):
                        break
                    else:
                        raise Exception()
                except:
                    print("Fehlerhafte Eingabe, versuche erneut")
    
            if(search or exit):
                continue

            release = releases[relchoice-1]
            print("Du hast folgendes Release gewählt: " + str(release.tostring()))
    
            print("\n")

            print("Das Release hat " + str(release.getEpisodeCount()) + " Episode(n)")
            curEpisodes = -1
            while(curEpisodes == -1):
                epi_in = input("Wieviel Episoden hast du bereits runtergeladen? Die restlichen verfügbaren werden dann automatisch heruntergeladen (Leerlassen, wenn nur neue Episoden runterladen willst): ")
                if(epi_in == "exit"):
                    exit = True
                    break
                elif(epi_in == "suche"):
                    search = True
                    break
                try:
                    if(epi_in == ""):
                        curEpisodes = release.getEpisodeCount()
                    else:
                        epi_in_int = int(epi_in)
                        if(epi_in_int > release.getEpisodeCount()):
                            print("Deine Episodenzahl darf nicht größer als verfügbare Episoden sein")
                        else:
                            curEpisodes = epi_in_int
                except:
                    print("Fehlerhafte Eingabe, muss eine Zahl sein")

            print("\n")

            customPackage = ""

            if(compare(input("Möchtest du dem Anime einen spezifischen Paketnamen geben? Andernfalls wird der Name des Anime genutzt [J/N]: "), {"j", "ja", "yes", "y"}) == True):
                customPackage = input("Packagename: ")

            animedata = {
                "name": anime.getName(),
                "missing": [],
                "releaseID": relchoice,
                "episodes": curEpisodes,
                "url": anime.getURL(),
                "customPackage": customPackage
            }
        
            os.makedirs(os.path.dirname(botfolder), exist_ok=True)
            f = open(botfile, "r")
            data = json.load(f)
            f.close()

            haveAddedAnime = False

            try:
                anidata = data['anime']
            except:
                print("Erster Anime in Liste, füge hinzu")
                fullanimedata = []
                fullanimedata.append(animedata)
                data['anime'] = fullanimedata 
                haveAddedAnime = True
                os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                jfile = open(botfile, "w")
                jfile.write(json.dumps(data, indent=4, sort_keys=True))
                jfile.flush()
                jfile.close()
                print("Anime wurde hinzugefügt")

            if(haveAddedAnime == False):              #Füge zu liste hinzu
                isNewAnime = True
                for animeentry in anidata:
                    url = animeentry['url']
                    release = animeentry['releaseID']
                    if(url == anime.getURL() and release == relchoice):
                        print("Anime mit gleichem Release ist bereits in Liste, gehe zurück zur Suche")
                        isNewAnime = False
                if(isNewAnime):
                    print("Füge Anime zu liste hinzu")
                    fullanimedata = data['anime']
                    fullanimedata.append(animedata)
                    data['anime'] = fullanimedata 
#                animedata = {"anime": animedata}
#                data.append(animedata)


                    os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                    jfile = open(botfile, "w")
                    jfile.write(json.dumps(data, indent=4, sort_keys=True))
                    jfile.flush()
                    jfile.close()
                    print("Anime wurde hinzugefügt")

            print("\n\n\n")

        elif(aniquery != "suche"):
            results = al.search(aniquery)
        
            if(len(results) == 0):
                print("Keine Ergebnisse")
                search = True
                break

            print("Ergebnisse: ")
    
            for idx, result in enumerate(results):
                print("[" + str(idx + 1) + "] " + result.tostring())
    
            while(True):
                anichoice = input("Wähle einen Anime (Zahl links daneben eingeben): ")
                if(anichoice == "exit"):
                    exit = True
                    break
                elif(anichoice == "suche"):
                    search = True
                    break
                try:
                    anichoice = int(anichoice)
                    anime = results[anichoice - 1].getAnime()
                    break
                except:
                    print("Fehlerhafte eingabe, versuche erneut")
    
            if(search or exit):
                continue

            releases = anime.getReleases()
        
            print("\n\nReleases:\n")
        
            for rel in releases:
                print(rel.tostring())
    
            print("\n")
            relchoice = ""
            while(True):
                relchoice = input("Wähle eine Release ID: ")
                if(relchoice == "exit"):
                    exit = True
                    break
                elif(relchoice == "suche"):
                    search = True
                    break
                try:
                    relchoice = int(relchoice)
                    if(relchoice <= len(releases)):
                        break
                    else:
                        raise Exception()
                except:
                    print("Fehlerhafte Eingabe, versuche erneut")
    
            if(search or exit):
                continue

            release = releases[relchoice-1]
            print("Du hast folgendes Release gewählt: " + str(release.tostring()))
    
            print("\n")

            print("Das Release hat " + str(release.getEpisodeCount()) + " Episode(n)")
            curEpisodes = -1
            while(curEpisodes == -1):
                epi_in = input("Wieviel Episoden hast du bereits runtergeladen? Die restlichen verfügbaren werden dann automatisch heruntergeladen (Leerlassen, wenn nur neue Episoden runterladen willst): ")
                if(epi_in == "exit"):
                    exit = True
                    break
                elif(epi_in == "suche"):
                    search = True
                    break
                try:
                    if(epi_in == ""):
                        curEpisodes = release.getEpisodeCount()
                    else:
                        epi_in_int = int(epi_in)
                        if(epi_in_int > release.getEpisodeCount()):
                            print("Deine Episodenzahl darf nicht größer als verfügbare Episoden sein")
                        else:
                            curEpisodes = epi_in_int
                except:
                    print("Fehlerhafte Eingabe, muss eine Zahl sein")

            print("\n")

            customPackage = ""

            if(compare(input("Möchtest du dem Anime einen spezifischen Paketnamen geben? Andernfalls wird der Name des Anime genutzt [J/N]: "), {"j", "ja", "yes", "y"}) == True):
                customPackage = input("Packagename: ")

            animedata = {
                "name": anime.getName(),
                "missing": [],
                "releaseID": relchoice,
                "episodes": curEpisodes,
                "url": anime.getURL(),
                "customPackage": customPackage
            }
    

            os.makedirs(os.path.dirname(botfolder), exist_ok=True)
            f = open(botfile, "r")
            data = json.load(f)
            f.close()

            haveAddedAnime = False

            try:
                anidata = data['anime']
            except:
                print("Erster Anime in Liste, füge hinzu")
                fullanimedata = []
                fullanimedata.append(animedata)
                data['anime'] = fullanimedata 
                haveAddedAnime = True
                os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                jfile = open(botfile, "w")
                jfile.write(json.dumps(data, indent=4, sort_keys=True))
                jfile.flush()
                jfile.close()
                print("Anime wurde hinzugefügt")

            if(haveAddedAnime == False):              #Füge zu liste hinzu
                isNewAnime = True
                for animeentry in anidata:
                    url = animeentry['url']
                    release = animeentry['releaseID']
                    if(url == anime.getURL() and release == relchoice):
                        print("Anime mit gleichem Release ist bereits in Liste, gehe zurück zur Suche")
                        isNewAnime = False
                if(isNewAnime):
                    print("Füge Anime zu liste hinzu")
                    fullanimedata = data['anime']
                    fullanimedata.append(animedata)
                    data['anime'] = fullanimedata 
#                animedata = {"anime": animedata}
#                data.append(animedata)
                    os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                    jfile = open(botfile, "w")
                    jfile.write(json.dumps(data, indent=4, sort_keys=True))
                    jfile.flush()
                    jfile.close()
                    print("Anime wurde hinzugefügt")

            print("\n\n\n")


def startbot():

    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
 
    interactive = "--docker" not in sys.argv
    if "--not-interactive" in sys.argv:
        interactive = False
    if "--interactive" in sys.argv:
        interactive = True

    while(jdhost == False):
        if(interactive):
            print("Noch keine oder Fehlerhafte konfiguration, leite weiter zu Einstellungen")
            editconfig()
            jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
        else:
            print("Keine oder fehlerhafte Konfiguration und Script ist nicht interaktiv, beende...")
            interactive = False
            sys.exit(1)

    if(pushkey != ""):
        pb = Pushbullet(pushkey)
    else:
        pb = ""
    
    al = animeloads(browser=browser, browserloc=browserlocation)
    
    if(interactive):
        if(compare(input("Möchtest du dich anmelden? [J/N]: "), {"j", "ja", "yes", "y"})):
            user = input("Username: ")
            password = getpass("Passwort: ")
            try:
                al.login(user, password)
            except:
                print("Fehlerhafte Anmeldedaten, fahre mit anonymen Account fort")
        else:
            print("Überspringe Anmeldung")
    else:
        print("Script wurde nicht interaktiv gestartet, überspringe Anmeldung..")
        interactive = False

    if(jdhost == "" and myjd_pass == ""):
        if(interactive == False):
            print("Kein MyJdownloader Passwort gesetzt, beende..")
            sys.exit(1)
        print("Kein MyJdownloader Passwort gesetzt")
        logincorrect = False 
        jd=myjdapi.Myjdapi()
        jd.set_app_key("animeloads")
        while(logincorrect == False):
            myjd_pass = getpass("MyJdownloader Passwort: ")
          
            try:
              jd.connect(myjd_user, myjd_pass)
              logincorrect = True
            except:
                print("Fehlerhafte Logindaten")
    print("Erfolgreich eingeloggt")
    
    while(True):
        os.makedirs(os.path.dirname(botfolder), exist_ok=True)
        f = open(botfile, "r")
        data = json.load(f)
        f.close()
      
        anidata = ""
        try:
            anidata = data['anime']
        except:
            print("Du hast keine Anime in deiner Liste")
            addAnime()
            return

        if(anidata != ""):
            for idx, animeentry in enumerate(anidata):
                name = animeentry['name']
                url = animeentry['url']
                releaseID = animeentry['releaseID']
                try:
                    customPackage = animeentry['customPackage']
                except:
                    customPackage = ""
                try:
                    anime = al.getAnime(url)
                    release = anime.getReleases()[releaseID-1]
                except:
                    print("Failed to get Anime, skipping...")
                    continue
                missingEpisodes = animeentry['missing']
                episodes = animeentry['episodes']


                now = datetime.now()
                print("[" + now.strftime("%H:%M:%S") + "] Prüfe " + name + " auf updates")
                anime.updateInfo()
                curEpisodes = release.getEpisodeCount()               #Anzahl der Episoden aktuell online
                if(len(missingEpisodes) > 0):                                 #Fehlende Episoden, die noch runtergeladen werden müssen
                    print("[INFO] " + name + "hat fehlende Episode(n)")
                    for idx, missingEpisode in enumerate(missingEpisodes):
                        log("[DOWNLOAD] Lade fehlende Episode " + str(missingEpisode) + " von " + name, pb)
                        try:
                            if(myjd_user != ""):
                                dl_ret = anime.downloadEpisode(missingEpisode, release, hoster, browser, browserlocation, myjd_user=myjd_user, myjd_pw=myjd_pass, myjd_device=myjd_device, pkgName=customPackage)
                            else:
                                dl_ret = anime.downloadEpisode(missingEpisode, release, hoster, browser, browserlocation, jdhost, pkgName=customPackage)
                        except Exception as e:
                            printException(e)
                            dl_ret = False
                        if(dl_ret == True):
                            log("[DOWNLOAD] Fehlende Episode " + str(missingEpisode) + " von " + name + " wurde zu JDownloader hinzugefügt", pb)
                            missingEpisodes[idx] = -1
                            animeentry['missing'] = list(filter(lambda a: a != -1, missingEpisodes))
                            print("[INFO] Update ani.json")
                            os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                            jfile = open(botfile, "w")
                            jfile.write(json.dumps(data, indent=4, sort_keys=True))
                            jfile.flush()
                            jfile.close
                        else:
                            log("[ERROR] Fehler beim hinzufügen von Episode " + str(missingEpisode) + " von " + name + ", wird im nächsten Durchlauf erneut versucht. Ist JDownloader gestartet?", pb)
        
                if(int(episodes) < curEpisodes):
                    log("[INFO] " + name + " hat neue Episode, lade herunter...", pb)
                    for i in range(episodes + 1, curEpisodes + 1):
                        print("[DOWNLOAD] Lade episode " + str(i) + " von " + name)
                        try:
                            if(myjd_user != ""):
                                dl_ret = anime.downloadEpisode(i, release, hoster, browser, browserlocation, myjd_user=myjd_user, myjd_pw=myjd_pass, myjd_device=myjd_device, pkgName=customPackage)
                            else:
                                dl_ret = anime.downloadEpisode(i, release, hoster, browser, browserlocation, jdhost, pkgName=customPackage)
                        except Exception as e:
                            printException(e)
                            dl_ret = False
                        if(dl_ret == True):
                            log("[DOWNLOAD] Fehlende Episode " + str(i) + " von " + name + " wurde zu JDownloader hinzugefügt", pb)
                            animeentry['episodes'] += 1
                            print("[INFO] Update ani.json")
                            os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                            jfile = open(botfile, "w")
                            jfile.write(json.dumps(data, indent=4, sort_keys=True))
                            jfile.flush()
                            jfile.close
                        else:
                            log("[ERROR] Fehler beim runterladen von Episode " + str(i) + " von " + name + ", wird im nächsten Durchlauf erneut versucht. Ist JDownloader gestartet?", pb)
                            missingEpisodes.append(i)
                            animeentry['missing'] = missingEpisodes
                            animeentry['episodes'] += 1
                            os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                            jfile = open(botfile, "w")
                            jfile.write(json.dumps(data, indent=4, sort_keys=True))
                            jfile.flush()
                            jfile.close
                else:
                    print("[INFO]" + name + " hat keine neuen Folgen verfügbar")
            print("Schlafe " + str(timedelay) + " Sekunden")
            time.sleep(timedelay)

def removeAnime():
    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
 
    while(jdhost == False):
        print("Noch keine oder Fehlerhafte konfiguration, leite weiter zu Einstellungen")
        editconfig()
        jdhost, hoster, browser, browserlocation, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()

    os.makedirs(os.path.dirname(botfolder), exist_ok=True)
    f = open(botfile, "r")
    data = json.load(f)
    f.close()

    anidata = ""
    try:
        anidata = data['anime']
    except:
        print("Du hast keine Anime in deiner Liste")


    if(anidata != ""):
        print("Deine Liste: ")
        while(True):
            for idx, animeentry in enumerate(anidata):
                print("[ID: " + str(idx+1) + "] " + animeentry['name'] + " mit Release " + str(animeentry['releaseID']))
            selection = input("Welchen Anime möchtest du löschen? (ID eingeben, \"exit\" zum beenden): ")
            if(selection == "exit"):
                print("Exit, beende...")
                break
            else:
                try:
                    sel_int = int(selection) - 1
                    data['anime'].pop(sel_int)
                    os.makedirs(os.path.dirname(botfolder), exist_ok=True)
                    jfile = open(botfile, "w")
                    jfile.write(json.dumps(data, indent=4, sort_keys=True))
                    jfile.flush()
                    jfile.close()
                    print("Anime wurde gelöscht")
                except:
                    print("Fehler beim löschen des Eintrags")

def printhelp():
    print("anibot.py [edit | start | add | remove]")
    print("[edit]:    Ändere deine Einstellungen")
    print("[start]:   Starte Bot und lade Episoden runter")
    print("[add]:     Füge neue Anime zu deiner Liste hinzu")
    print("[remove]:  Lösche Anime aus deiner Liste")


commandSet = False
if(arglen >= 2):
    for idx, arg in enumerate(sys.argv):
        if(arg == "--configfile"):
            try:
                botfile = sys.argv[idx+1]
                botfolder_arr = botfile.split("/")[:-1]
                botfolder = ""
                for p in botfolder_arr:
                    botfolder += p
                    botfolder += "/"
                print("Config Datei: " + botfile)
            except Exception as e:
                botfile = "config/ani.json"
                botfolder = "config/"
                print("--configfile gegeben, aber kein Pfad (oder fehlerhafter) danach, setze Pfad auf ./config/ani.json")
        if(arg == "start"):
            commandSet = True
            startbot()
        elif(arg == "edit"):
            commandSet = True
            editconfig()
            print("Einstellungen gespeichert")
        elif(arg == "add"):
            commandSet = True
            addAnime()
        elif(arg == "remove"):
          commandSet = True
          removeAnime()
        elif("help" in arg):
            printhelp()

else:
    if(arglen == 1):
        startbot()
    printhelp()

if(commandSet == False):
    startbot()

#episodes = getEpisodes()