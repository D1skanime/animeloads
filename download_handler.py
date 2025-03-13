import base64
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from utils import decodeCNL, addToMYJD
from error_handler import printException

def prepare_download_request(animeloads_instance, episode, release):
    """Erstellt die verschlüsselte Anfrage für den Download."""
    anime_identifier = animeloads_instance.url.split("/")[-1]
    unenc_request = f'["media","{anime_identifier}","downloads",{release.getID()},{int(episode)-1}]'
    return base64.b64encode(unenc_request.encode("ascii"))

def fetch_download_links(animeloads_instance, b64, driver):
    """Führt das notwendige JavaScript aus, um die verschlüsselten Download-Links zu erhalten."""
    js = f"""
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://www.anime-loads.org/ajax/captcha', false);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send('enc={b64.decode("ascii")}&response=nocaptcha');
    return xhr.response;
    """
    ajaxresponse = driver.execute_script(js)
    return json.loads(ajaxresponse)

def decrypt_links(cnldata):
    """Entschlüsselt die Download-Links."""
    try:
        k = cnldata['cnl']['jk']
        crypted = cnldata['cnl']['crypted']
        return decodeCNL(k, crypted)
    except KeyError:
        raise Exception("Fehler beim Entschlüsseln der Links")

def send_to_jdownloader(links, myjd_user, myjd_pw, myjd_device, pkgName, release):
    """Sendet die entschlüsselten Links an MyJDownloader."""
    for link in links:
        response = addToMYJD(myjd_user, myjd_pw, myjd_device, link.decode('utf-8'), pkgName, release.getPassword())
        if 'id' in response:
            return True
    return False

def download_episode(animeloads_instance, episode, release, hoster, browser, browserlocation="", jdhost="", myjd_user="", myjd_pw="", myjd_device="", pkgName=""):
    """Startet den Download-Prozess."""
    b64 = prepare_download_request(animeloads_instance, episode, release)

    options = FirefoxOptions() if browser == animeloads_instance.FIREFOX else Options()
    options.headless = True
    if browserlocation:
        options.binary_location = browserlocation

    driver = webdriver.Firefox(options=options) if browser == animeloads_instance.FIREFOX else webdriver.Chrome(options=options)
    driver.get("https://www.anime-loads.org/assets/pub/images/logo.png")
    
    for c in animeloads_instance.session.cookies:
        driver.add_cookie({'name': c.name, 'value': c.value})

    driver.get(animeloads_instance.url)
    response_json = fetch_download_links(animeloads_instance, b64, driver)
    driver.quit()

    cnldata = response_json.get("content", [])[0]
    links_decoded = decrypt_links(cnldata)

    if jdhost == "" and myjd_user != "":
        return send_to_jdownloader(links_decoded, myjd_user, myjd_pw, myjd_device, pkgName, release)
    else:
        return [link.decode('ascii') for link in links_decoded]

if __name__ == "__main__":
    print("Teste Download-Handler...")
    from animeloads import Animeloads
    from config_manager import loadconfig

    al_instance = Animeloads()
    jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
    
    al_instance = Animeloads(browser=browser, browserloc=browserlocation)
    test_episode = "1"
    test_release = None  # Hier müsste eine gültige Release-Instanz stehen
    test_hoster = "uploaded"

    print(download_episode(al_instance, test_episode, test_release, test_hoster, browser))
