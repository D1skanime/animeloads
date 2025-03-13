import base64
import json
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils import decodeCNL, addToMYJD, doCaptcha, getDifference
import utils

class AnimeDownload:
    def __init__(self, animeloads_instance):
        self.al = animeloads_instance  # Referenz auf die Hauptklasse
    
    def prepare_download(self, episode, release, hoster):
        """ Wählt den richtigen Hoster und erstellt die Anfrage-Daten. """
        anime_identifier = self.al.url.split("/")[-1]  # Anime-Name für POST-Request
        unenc_request = f'["media","{anime_identifier}","downloads",{release.getID()},{int(episode)-1}]'
        b64 = base64.b64encode(unenc_request.encode("ascii"))
        return b64
    
    def fetch_download_links(self, b64, driver):
        """ Holt die verschlüsselten Download-Links über AJAX & JS. """
        js = "var xhr = new XMLHttpRequest(); \
xhr.open('POST', 'https://www.anime-loads.org/ajax/captcha', false); \
xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded'); \
xhr.send('enc=" + b64.decode('ascii') + "&response=nocaptcha'); \
return xhr.response"

        ajaxresponse = driver.execute_script(js)
        return json.loads(ajaxresponse)
    
    def decrypt_links(self, cnldata):
        """ Entschlüsselt die Download-Links. """
        try:
            k = cnldata['cnl']['jk']
            crypted = cnldata['cnl']['crypted']
            k_list = list(k)
            k_list[15], k_list[16] = k_list[16], k_list[15]  # Deobfuskation
            k = "".join(k_list)
            jk = f"function f(){{ return '{k}';}}"
            return decodeCNL(k, crypted)
        except KeyError:
            raise Exception("Fehler beim Entschlüsseln der Links")
    
    def send_to_jdownloader(self, links, myjd_user, myjd_pw, myjd_device, pkgName, release):
        """ Schickt die entschlüsselten Links an MyJDownloader. """
        for link in links:
            response = addToMYJD(myjd_user, myjd_pw, myjd_device, link.decode('utf-8'), pkgName, release.getPassword())
            if 'id' in response:
                return True
        return False
    
    def downloadEpisode(self, episode, release, hoster, browser, browserlocation="", jdhost="", myjd_user="", myjd_pw="", myjd_device="", pkgName=""):
        """ Startet den Download-Prozess. """
        if browser == "Firefox":
            browser = self.al.FIREFOX
        elif browser == "Chrome":
            browser = self.al.CHROME
        
        b64 = self.prepare_download(episode, release, hoster)
        
        options = FirefoxOptions() if browser == self.al.FIREFOX else Options()
        options.headless = True
        if browserlocation:
            options.binary_location = browserlocation
        
        driver = webdriver.Firefox(options=options) if browser == self.al.FIREFOX else webdriver.Chrome(options=options)
        driver.get("https://www.anime-loads.org/assets/pub/images/logo.png")
        for c in self.al.session.cookies:
            driver.add_cookie({'name': c.name, 'value': c.value})
        driver.get(self.al.url)
        
        response_json = self.fetch_download_links(b64, driver)
        driver.quit()
        
        cnldata = response_json.get("content", [])[0]  # Wählt den richtigen Hoster
        links_decoded = self.decrypt_links(cnldata)
        
        if jdhost == "" and myjd_user != "":
            return self.send_to_jdownloader(links_decoded, myjd_user, myjd_pw, myjd_device, pkgName, release)
        else:
            return [link.decode('ascii') for link in links_decoded]

if __name__ == "__main__":
    print("Teste Anime-Download...")
    from animeloads import Animeloads
    from config_manager import loadconfig
    al_instance = Animeloads()
    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
    al_instance = Animeloads(browser=browser, browserloc=browserlocation) 
    download_module = AnimeDownload(al_instance)
    test_episode = "1"
    test_release = None  # Dummy-Wert, ersetzen mit echtem Release-Objekt
    test_hoster = "uploaded"
    print(download_module.downloadEpisode(test_episode, test_release, test_hoster, "Chrome"))
