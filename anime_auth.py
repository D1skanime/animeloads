import requests
from config_manager import loadconfig

class AnimeAuth:
    def __init__(self, animeloads_instance):
        self.al = animeloads_instance  # Referenz auf die Hauptklasse
    
    def login(self, username, password):
        """ Loggt sich auf Anime-Loads ein und speichert die Session-Cookies. """
        login_url = "https://www.anime-loads.org/login"
        payload = {"username": username, "password": password}
        
        session = requests.Session()
        response = session.post(login_url, data=payload)
        
        if "logout" in response.text:
            print("Erfolgreich eingeloggt!")
            self.al.session = session  # Speichert die Session in der Hauptklasse
            return True
        else:
            print("Login fehlgeschlagen. Bitte überprüfe Benutzername und Passwort.")
            return False

if __name__ == "__main__":
    print("Teste Anime-Login...")
    from animeloads import Animeloads  # Import der Hauptklasse
    try:
        jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
        al_instance = Animeloads(browser=browser, browserloc=browserlocation)  # Nur einmal erstellen
        auth_module = AnimeAuth(al_instance)
        username = input("Benutzername: ")
        password = input("Passwort: ")
        auth_module.login(username, password)
    except Exception as e:
        print(f"Fehler beim Testen: {e}") 