from anime_search import AnimeSearch
from fake_useragent import UserAgent
from captcha_solver import doCaptcha
import requests
from selenium import webdriver
from html_table_parser import HTMLTableParser
from Crypto.Cipher import AES
from binascii import unhexlify
import base64
import re
import numpy, random, time
from urllib.parse import unquote
import myjdapi
from lxml import etree
from lxml import html
import os, sys
#captcha
import time, json, hashlib, cv2, numpy, shutil
from captcha_solver import doCaptcha

class Animeloads:

    FIREFOX = 0
    CHROME = 1
    UPLOADED = 0
    DDOWNLOAD = 1
    RAPIDGATOR = 2

    def __init__(self, user="", pw="", browser="", browserloc=""):
        self.user = user
        self.pw = pw
        self.session = requests.session()
        self.username = "anonymous"
        self.isVIP = False
        ua = UserAgent()
        self.session.headers = {'User-Agent': ua.chrome}

        if user and pw:
            self.login(self.user, self.pw)
            
        if browser == Animeloads.CHROME:
            options = webdriver.ChromeOptions()
            options.headless = True  # Headless-Modus aktivieren

            if browserloc:
                options.binary_location = browserloc  # Falls ein bestimmter Browser-Pfad angegeben ist

            driver = webdriver.Chrome(options=options)  # Selenium Manager übernimmt den Rest

        elif browser == Animeloads.FIREFOX:
            options = webdriver.FirefoxOptions()
            options.headless = True  

            if browserloc:
                options.binary_location = browserloc  

            driver = webdriver.Firefox(options=options)  # Kein manuelles Service-Objekt mehr nötig

        else:
            raise ALInvalidBrowserException("Nicht unterstützter Browser")

    
        #Erster besuch auf der Seite, damit cookies hinzugefügt werden können
        driver.get("https://www.anime-loads.org/assets/pub/images/logo.png")
        
        cookies = driver.get_cookies()

        if not cookies:
            print("⚠ Warnung: Keine Cookies erhalten! Überprüfe die Seite oder Browser-Einstellungen.")
        else:
            print(f"✅ Cookies erfolgreich geladen: {len(cookies)} Cookies gefunden.")    
        
        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
        driver.quit()

        self.search_module = AnimeSearch(self)

    def search(self, query):
        """Delegiert die Suche an das ausgelagerte AnimeSearch-Modul"""
        return self.search_module.search(query)  

    def getAnime(self, url):
        return anime(url, self.session, self)


    def login(self, user, pw):
        data = {"identity": user, "password": pw, "remember": "1"}
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random
        }
        r = self.session.post("https://www.anime-loads.org/auth/signin", data=data, headers=headers)

        for c in self.session.cookies:
            if("username" in c.value):
                data = unquote(c.value)
                jdata = json.loads(data)
                for key in jdata:
                    if(key == "username"):
                        self.username = jdata[key]
                    elif(key == "is_vip"):
                        if(jdata[key] == True):
                            self.isVIP = True
                return True
        raise ALInvalidLoginException("Login data is invalid")



class utils:
    @staticmethod
    def decodeCNL(k, crypted):
        key = unhexlify(k)
        data = base64.standard_b64decode(crypted)
        obj = AES.new(key, AES.MODE_CBC, key)
        d = obj.decrypt(data)
        d = map(lambda x: x.strip(b'\r\x00'), d.split(b'\n'))
        d = list(d)
        return d
    
    @staticmethod
    def b(s):
        s = str(s)
        a = numpy.int32(0)
        if(len(s) == 0):
            return 0
        for curChar in range(0, len(s)):
            a = numpy.int32(a)
            a = ((a << 5) - a + ord(s[curChar]))
        return abs(a)
        
    @staticmethod
    def getAdString():
        rand1 = random.uniform(0, 1)
        first = ("" + str(utils.b(str(abs(rand1)))))
        
        
        date = str(round(time.time() * 1000))
        sec = ("" + str(utils.b(date)))
        
        rand3 = random.uniform(0, 1)
        third = ("" + str(utils.b(str(abs(rand3)))))
        
        return first + "" + sec + third

    @staticmethod
    def addToJD(host, passwords, source, crypted, jk):
        data = {
            "passwords": str(passwords),
            "source": str(source),
            "jk": str(jk),
            "crypted": str(crypted)
        }
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0 Waterfox/78.7.0"
        }
        try:
            req = requests.post("http://" + host + ":9666/flash/addcrypted2", data=data, headers=headers)
        except:
            return False
        retdata = req.text
        if(retdata == "failed"):
            return False
        else:
            return True

    @staticmethod
    def addToMYJD(myjd_user, myjd_pass, myjd_device, links, pkgName, pwd):
        jd=myjdapi.Myjdapi()
        jd.set_app_key("animeloads")
        jd.connect(myjd_user, myjd_pass)
        jd.update_devices()

        device=jd.get_device(myjd_device) 
        
        dl = device.linkgrabber
        
        return dl.add_links([{
                              "autostart": True,
                              "links": links,
                              "packageName": pkgName,
                              "extractPassword": pwd,
                              "priority": "DEFAULT",
                              "downloadPassword": None,
                              "destinationFolder": None,
                              "overwritePackagizerRules": False
                          }])

    @staticmethod
    def getDifference(img1, img2):
        res = cv2.absdiff(img1, img2)
        res = res.astype(numpy.uint8)
        percentage = (numpy.count_nonzero(res) * 100)/ res.size
        return percentage


class apihelper:
    @staticmethod
    def getSearchURL(query):
        return "https://www.anime-loads.org/search?q=" + query




class searchResult():
    def __init__(self, url, name, typ, relDate, epCountCurrent, epCountMax, dubLang, subLang, genre, session, animeloads):
        self.url = url
        self.animeloads = animeloads
        self.name = name
        self.typ = typ
        self.relDate = relDate
        self.epCountCurrent = epCountCurrent
        self.epCountMax = epCountMax
        self.dubLang = dubLang
        self.subLang = subLang
        self.genre = genre
        self.session = session

    def getUrl(self):
        return self.url

    def getName(self):
        return self.name
    
    def getTyp(self):
        return self.typ

    def getReleaseDate(self):
        return self.relDate

    def getCurrentEpisodeCount(self):
        return self.epCountCurrent

    def getMaxEpisodeCount(self):
        return self.epCountMax

    def getDubLang(self):
        return self.dubLang

    def getSubLang(self):
        return self.getSubLang

    def getGenre(self):
        return self.genre

    def tostring(self):
        return "Name: " + self.name + ", Typ: " + self.typ + ", Episoden: " + str(self.epCountCurrent) + "/" + str(self.epCountMax) + ", Dub: " + str(self.dubLang) + ", Subs: " + str(self.subLang)

    def getAnime(self):
        return anime(self.url, self.session, self.animeloads)   #todo session redundant

class anime():
    def __init__(self, url, session, animeloads):
        self.url = url
        self.animeloads = animeloads
        self.session = session
        self.gerName = ""
        self.engName = ""
        self.japName = ""
        self.synonymes = []     
        self.type = ""
        self.year = 0
        self.runtime = 0
        self.status = ""
        self.mainGenre = ""
        self.sideGenres = []
        self.tags = []
        self.releases = []
        self.curEpisodes = 1337
        self.maxEpisodes = 1337
        self.updateInfo()

    def updateInfo(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        
        #Ad Adstring, an attempt to bypass adblock detection
        #adstring = utils.getAdString()
        #self.session.cookies.set("adcashufpv3", adstring, domain="www.anime-loads.org")
        
        self.session.cookies.set("adsblocked", "0", domain="www.anime-loads.org")
        self.session.cookies.set("hideads", "1", domain="www.anime-loads.org")

        detailPage = self.session.get(self.url, headers=headers)
        cock = [
            {'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path}
            for c in self.session.cookies
        ]

        #Load all JS scripts in an attempt to bypass adblock detection
#        js = detailPage.text.split("<script type=\"text/javascript\" src=\"")
#        for j in js:
#            if(j[0:4] == "http"):
#                self.session.get(j.split("\"")[0])

        try:

            p = HTMLTableParser()
            p.feed(detailPage.text)
    
            detailtable = p.tables[0]
            for detail in detailtable:
                leftEntry = detail[0]
                rightEntry = detail[1]
                if("Titel" == leftEntry):
                    if(self.japName == ""):
                        self.japName = rightEntry
                    elif(self.gerName == ""):
                        self.gerName = rightEntry
                    else:
                        self.engName = rightEntry
                elif("Synonyme" == leftEntry):
                    self.synonymes = rightEntry.split(", ")
                elif("Typ" == leftEntry):
                    if(rightEntry == "Anime Series"):
                        self.type = "series"
                    elif(rightEntry == "Web"):
                        self.type = "web"
                    elif(rightEntry == "Special"):
                        self.type = "special"
                    elif(rightEntry == "OVA"):
                        self.type = "ova"
                    elif(rightEntry == "Anime Film"):
                        self.type = "movie"
                    elif(rightEntry == "Bonus"):
                        self.type = "bonus"
                elif("Episoden" == leftEntry):
                    epString = rightEntry.split("/")
                    try:
                        self.curEpisodes = int(epString[0])
                    except:
                        self.curEpisodes = 0
                    try:
                        self.maxEpisodes = int(epString[1])
                    except:
                        self.maxEpisodes = 999999
                elif("Jahr" == leftEntry):
                    self.year = int(rightEntry)
                elif("Laufzeit" == leftEntry):
                    runtimestring = re.sub("[^0-9]", "", rightEntry)
                    if(runtimestring == ""):
                        runtimestring = "0"
                    self.runtime = int(runtimestring)
                elif("Status" == leftEntry):
                    self.status = rightEntry
                elif("Hauptgenre" == leftEntry):
                    self.mainGenre = rightEntry
                elif("Nebengenre" == leftEntry):
                    self.sideGenres = rightEntry.split("  ")
                elif("Tags" == leftEntry):
                    self.tags = rightEntry.split("  ")
    
    
            rel_dom = etree.HTML(detailPage.text)
            releases_unparsed = rel_dom.xpath("//div[@id='downloads']/div[@class='row' and 1]/div[@class='col-sm-3' and 1]/ul[@class='nav nav-pills nav-stacked' and 1]")[0]    #Get left list of releases
            releases_dom = etree.HTML(html.tostring(releases_unparsed))
            releases = releases_dom.xpath("//li")   #Get single releases from list
    
            numReleases = len(releases) - 1         #Last release is "Add release", ignoring
    
            #rid, group, res, dubs, subs, format, size, password, anmerkung=""
            for relIndex in range(0, numReleases):
                relID = relIndex + 1
                group = ""      #done
                res = ""        
                dubs = []       #done
                subs = []       #done
                videoformat = ""    
                size = 0            
                password = ""       
                anmerkung = ""      
                episodes = 0
                table = p.tables[relID]    #First release, get name and anmerkung
    
                for idx in range(0, len(table)):
                    try:
                        tLeft = table[idx][0]
                        tRight = table[idx][1]
                    except:
                        continue
    
                    if(tLeft == "Release Gruppe"):
                        group = tRight
                    elif(tLeft == "Auflösung"):
                        res = tRight.split("x")[1] + "p"
                    elif(tLeft == "Typ"):
                        videoformat = tRight
                    elif(tLeft == "Größe"):
                        if("GB" in tRight):
                            try:
                                size = float(re.sub("[^0-9.]", "", tRight)) * 1000
                            except:
                                size = 0.0
                        else:
                            try:
                                size = float(re.sub("[^0-9.]", "", tRight))
                            except:
                                size = 0.0
                    elif(tLeft == "Passwort"):
                        password = tRight
                    elif(tLeft == "Release Anmerkungen"):
                        anmerkung = tRight
    
        
                detailhtmlstring = str(html.tostring(releases[relIndex]))        #Detail html from release for languages#
    
                ###################
                #WARNING: UGLY CODE
                ###################
    
                dublangsubstring = detailhtmlstring.split("title=\"Sprache: ")      #HTMLCode split for Languages
                for idx in range(1, len(dublangsubstring)):                         #Start with second result, first is always garbage
                    dublang = dublangsubstring[idx].split("\"")[0]                  #Cut string after ", language end there
                    dubs.append(dublang)                                            #Add to dublist
    
    
    
                sublangsubstring = detailhtmlstring.split("title=\"Untertitel: ")   #HTMLcode split for Subtitles
                for idx in range(1, len(sublangsubstring)):                         #Start with second result, first is always garbage
                    sublang = sublangsubstring[idx].split("\"")[0]                  #Cut string after ", subtitle end there
                    subs.append(sublang)                                            #Add to sublist
    
                ##############
                #UGLY CODE END
                ##############
                #TODO Search for faster method for episode traversal        SLOOOOOOOOOOW
                epnum = 0
                while(True):
                    singleEP = rel_dom.xpath("//a[@aria-controls='downloads_episodes_" + str(relID) + "_" + str(epnum) + "']")
    #                print("Episodenumber: " + str(epnum))
                    if(len(singleEP) == 0):
                        nextEP = rel_dom.xpath("//a[@aria-controls='downloads_episodes_" + str(relID) + "_" + str(epnum+1) + "']")
                        if(len(nextEP) == 0):
                            nextEP = rel_dom.xpath("//a[@aria-controls='downloads_episodes_" + str(relID) + "_" + str(epnum+2) + "']")
                            if(len(nextEP) == 0):
                                break
                    epnum += 1
    
                tmprel = release(self.url, relID, group, res, dubs, subs, epnum, videoformat, size, password, anmerkung, detailPage.text, self.session)
                self.releases.append(tmprel)
            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

            if("IndexError" in str(exc_type)):
                print("Fehler beim parsen. Dies liegt sehr wahrscheinlich daran, dass anime-loads gerade offline ist oder einen Fehler hat.\nWenn der Fehler länger besteht, bitte auf Github melden.")
            else:
                print("Fehler beim parsen, bitte auf Github melden")
                print(exc_type, fname, exc_tb.tb_lineno)
            return False

    
    #quality: prefer 1080p/DTS
    def getBestReleaseByQuality(self, releaseList=[]):
        if(len(releaseList) == 0):
            releaseList = self.releases

        if(len(releaseList) == 1): #Only 1 release available, has to be the best
            return releaseList[0]

        rel720p = []
        rel1080p = []
        relrest = []
        for rel in releaseList:
            if(rel.getResolution() == "1080p"):
                rel1080p.append(rel)
            elif(rel.getResolution() == "720p"):
                rel720p.append(rel)
            else:
                relrest.append(rel)
        if(len(rel1080p) == 0):         #Get best video quality
            if(len(rel720p) == 0):
                bestList = relrest
            else:
                bestList = rel720p
        else:
            bestList = rel1080p
        
        #PCM>FLAC=DTS>AC3>AAC>MP3           #Thx to Toastkiste21 & Tanukichan
        pointlist = []
        for rel in bestList:            #Get best audio quality
            points = 0
            audio = rel.getAudioCodec()
            audiotypes = ["MP3", "AAC", "AC3", "DTS", "FLAC&DTS", "PCM"]        #list, from worse to best
            for idx, typ in enumerate(audiotypes):
                audios = typ.split("&")
                for splitaudio in audios:
                    if(splitaudio == audio):
                        points += idx       #Audio found, add index to points(best has highest index)
                    else:
                        points += 1         #Other, unknown audio, only one point
            pointlist.append(points)


        bestrel = bestList[0]
        bestscore = 0
        for idx, rel in enumerate(bestList):
            score = pointlist[idx]
            codec = rel.getVideoCodec().lower()
            if(codec == "x265" or codec == "hevc"):
                score += 2
            #print("Release " + str(rel.getID()) + " with " + str(score) + " points")
            if(score > bestscore):
                bestscore = score
                bestrel = rel
        
        return rel


    #language: prefer GerDub/GerSub
    def getBestReleaseByLanguage(self, releaseList=[]):
        if(len(releaseList) == 0):
            releaseList = self.releases

        if(len(releaseList) == 1): #Only 1 release available, has to be the best
            return releaseList[0]

        dubreleases = []
        for rel in releaseList:
            for dub in rel.getDubs():
                if(dub == "Deutsch"):
                    dubreleases.append(rel)
        if(len(dubreleases) == 0):
            for rel in releaseList:
                for dub in rel.getDubs():
                    if(dub == "Englisch"):
                        dubreleases.append(rel)
        if(len(dubreleases) == 0):
            dubreleases = releaseList #No (Eng/Ger)dub releases, just going with subs
        maxsubs = 0
        relmaxsubs = []
        for rel in dubreleases:
            if(len(rel.getSubs()) >= maxsubs):
                maxsubs = len(rel.getSubs())
                relmaxsubs.append(rel)

        return self.getBestReleaseByQuality(relmaxsubs)


    #episodes: most episodes
    def getBestReleaseByEpisodes(self, releaseList=[]):
        if(len(releaseList) == 0):
            releaseList = self.releases

        if(len(releaseList) == 1): #Only 1 release available, has to be the best
            return releaseList[0]

        max = 0
        maxrel = []
        for rel in releaseList:
            if(rel.getEpisodeCount() >= max):
                max = rel.getEpisodeCount()
                maxrel.append(rel)
        return self.getBestReleaseByQuality(maxrel)


    def getName(self):
        if(self.gerName != ""):
            return self.gerName
        elif(self.engName != ""):
            return self.engName
        else:
            return self.japName

    def getNameGerman(self):
        return self.gerName

    def getNameJapanese(self):
        return self.japName

    def getNameEnglish(self):
        return self.japName

    def getURL(self):
        return self.url

    def getRuntime(self):
        return self.runtime

    def getType(self):
        return self.type

    def getSynonymes(self):
        return self.synonymes
    
    def getYear(self):
        return self.year

    def getCurrentEpisodes(self):
        return self.curEpisodes
    
    def getMaxEpisodes(self):
        return self.maxEpisodes

    def getStatus(self):
        return self.status

    def getMainGenre(self):
        return self.mainGenre

    def getSideGenres(self):
        return self.sideGenres
    
    def getTags(self):
        return self.tags

    def getReleases(self):
        return self.releases

    def tostring(self):
        return str("[Jap/Ger/EngName]: " + self.japName + "/" + self.gerName + "/" + self.engName + ", [Synonyms]: " + str(self.synonymes) + ", [Type]: " + \
            self.type + ", [Episodes]: " + str(self.curEpisodes) + "/" + str(self.maxEpisodes) + ", [Status]: " + self.status + ", [Year]: " + str(self.year) \
                + ", [Maingenre]: " + self.mainGenre + ", [Sidegenres]: " + str(self.sideGenres) + ", [Tags]: " + str(self.tags))


    def downloadEpisode(self, episode, release, hoster, browser, browserlocation="", jdhost="", myjd_user="", myjd_pw="", myjd_device="", pkgName=""):
        if(browser == "Firefox"):
            browser = Animeloads.FIREFOX
        elif(browser == "Chrome"):
            browser = Animeloads.CHROME
        try:
            if("uploaded" in hoster.lower()):
                hoster = Animeloads.UPLOADED
            elif("ddownload" in hoster.lower()):
                hoster = Animeloads.DDOWNLOAD
            elif("rapidgator" in hoster.lower()):
                hoster = Animeloads.RAPIDGATOR
        except:
            pass


        anime_identifier = self.url.split("/")[len(self.url.split("/"))-1] #Name of Anime, used for POST Request
        unenc_request = "[\"media\",\"" + anime_identifier + "\",\"downloads\"," + str(release.getID()) + "," + str(int(episode)-1) + "]"
        #print(unenc_request)
        b64 = base64.b64encode(unenc_request.encode("ascii"))
        data = {"enc": b64,
       "response": "nocaptcha"}

        #Create Headless browser to bypass adblock detection
        if browser == Animeloads.CHROME:
            options = webdriver.ChromeOptions()
            options.headless = True  # Headless-Modus aktivieren

            if browserlocation:
                options.binary_location = browserlocation

            driver = webdriver.Chrome(options=options)

        elif(browser == Animeloads.FIREFOX):
            options = webdriver.FirefoxOptions()
            options.headless = True

            if browserlocation:
                options.binary_location = browserlocation
            driver = webdriver.Firefox(options=options)
        else:
            raise ALInvalidBrowserException("Nicht unterstützter Browser")

        #Erster besuch auf der Seite, damit cookies hinzugefügt werden können
        driver.get("https://www.anime-loads.org/assets/pub/images/logo.png")

        #Login cookies auf Selenium übertragen
        for c in self.session.cookies:
            driver.add_cookie({'name': c.name, 'value': c.value})

        driver.get(self.url)


        #JS to make post request to get URLs
        js = "var xhr = new XMLHttpRequest(); \
xhr.open('POST', 'https://www.anime-loads.org/ajax/captcha', false); \
xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded'); \
xhr.send('enc=" + b64.decode('ascii') + "&response=nocaptcha'); \
return xhr.response"

        ajaxresponse = driver.execute_script(js)

        code = ""
        message = ""
        reflinks = ""
        content_uploaded = ""
        content_ddl = ""
        content_rapid = ""

        response_json = json.loads(ajaxresponse)

        print(response_json)

        for key in response_json:
            value = response_json[key]
            if(key == "code"):
                code = value
            elif(key == "message"):
                message = value
            elif(key == "reflink"):
                reflinks = value
            elif(key == "content"):
                try:
                    content_uploaded = value[0]
                except:
                    pass
                try:
                    content_ddl = value[1]
                except:
                    pass
                try:
                    content_rapid = value[2]
                except:
                    pass

        tries = 0
        while(code != "success" and "noadblock" in message and tries < 5):
            print("Need to solve a captcha")
            cID = ""
            response_json = utils.doCaptcha(cID, driver, self.session, b64)
            if response_json == False:
                return ALUnknownException("Ein unbekannter Fehler beim lesen der Hosterlinks aufgetreten, möglicherweise serverseitig.")
            for key in response_json:
                value = response_json[key]
                if(key == "code"):
                    code = value
                elif(key == "message"):
                    message = value
                elif(key == "reflink"):
                    reflinks = value
                elif(key == "content"):
                    try:
                        content_uploaded = value[0]
                    except:
                        pass
                    try:
                        content_ddl = value[1]
                    except:
                        pass
                    try:
                        content_rapid = value[2]
                    except:
                        pass
            tries += 1
            
#            raise ALCaptchaException("Captcha is needed to get download links")

        if(code != "success"):
            return ALUnknownException("Ein unbekannter Fehler beim lesen der Hosterlinks aufgetreten, möglicherweise serverseitig oder das Captcha konnte nach 5 Versuchen nicht gelöst werrden.")

        driver.quit()

        reflinks = ""
        k = ""
        jk = ""
        crypted = ""


        if(hoster == Animeloads.DDOWNLOAD):
            cnldata = content_ddl
        elif(hoster == Animeloads.RAPIDGATOR):
            cnldata = content_rapid
        else:
            cnldata = content_uploaded

        for key in cnldata:
            value = cnldata[key]
            if(key == "links"):
                reflinks = value
            elif(key == "cnl"):
                try:
                    k = value['jk']
                except:
                    raise ALLinkExtractionException("AES-Key konnte nicht gelesen werden")
                try:
                    crypted = value['crypted']
                except:
                    raise ALLinkExtractionException("Linkdaten konnten nicht gelesen werden")

        try:
            k_list = list(k)        
            tmp = k_list[15]
            k_list[15] = k_list[16]
            k_list[16] = tmp
            k = "".join(k_list)
        except:
            print("Failed to deobfuscate key")
            raise ALLinkExtractionException("Linkdaten konnten nicht gelesen werden")

#        print("Key wurde erfolgreich deobfuskiert")

        jk = "function f(){ return \'" + k + "\';}"

        if(pkgName == ""):
            pkgName = anime_identifier
        if(jdhost == "" and myjd_user != ""):
            try:
                links_decoded = utils.decodeCNL(k, crypted)
                print("Successfully decoded links")
            except:
                print("Failed to decode links")
                raise ALUnknownException("Failed to decode links")
          #  links = []
           # linkstring = ""
            try:
                for link in links_decoded:
                    decoded_link = link.decode('utf-8')
                    myjd_return = utils.addToMYJD(myjd_user, myjd_pw, myjd_device, decoded_link, pkgName, release.getPassword())
                   # myjd_return = utils.addToMYJD(myjd_user, myjd_pw, myjd_device, decoded_link, pkgName, release.getPassword())
            except:
                print("Failed to add Link to MyJD")
                raise ALUnknownException("Failed to add Link to MyJD")
            try:
                pkgID = myjd_return['id']
                return True
            except Exception as e:
                print(e)
                return False
        else:
            links_decoded = utils.decodeCNL(k, crypted)
            links = []
            for link in links_decoded:
                links.append(link.decode('ascii'))
            return links
        



class release:

    @staticmethod
    def parseAudioCodec(anmerkung):
        if(anmerkung == ""):
            return ""
        formats = ["PCM", "FLAC", "DTS", "AC3", "AAC", "MP3"]
        format = "UNKNOWN"
        for f in formats:
            if(f in anmerkung):
                format = f
        return format

    @staticmethod
    def parseVideoCodec(anmerkung):
        if(anmerkung == ""):
            return ""
        codecs = ["x264", "x265"]
        codec = "UNKNOWN"
        for c in codecs:
            if(c in anmerkung):
                codec = c
        return codec

    def __init__(self, url, rid, group, res, dubs, subs, episodeCount, videoformat, size, password, anmerkung="", sitesource="", session=""):   #TODO sortieren
        self.url = url
        self.rid = rid
        self.group = group
        self.res = res
        self.audiocodec = self.parseAudioCodec(anmerkung)
        self.dubs = dubs
        self.subs = subs
        self.videoformat = videoformat
        self.size = size
        self.episodeCount = episodeCount
        self.password = password
        self.videocodec = self.parseVideoCodec(anmerkung)
        self.anmerkung = anmerkung
        self.sitesource = sitesource
        self.session = session

    def getID(self):
        return self.rid

    def getGroup(self):
        return self.group

    def getResolution(self):
        return self.res
        
    def getAudioCodec(self):
        return self.audiocodec

    def getDubs(self):
        return self.dubs

    def getSubs(self):
        return self.subs

    def getVideoFormat(self):
        return self.videoformat
    
    def getSize(self):
        return self.size
    
    def getPassword(self):
        return self.password

    def getAnmerkung(self):
        return self.anmerkung

    def getVideoCodec(self):
        return self.videocodec

    def tostring(self):
        return "Release ID: " + str(self.rid) + ", Group: " + self.group + ", Resolution: " + self.res + ", Videocodec: " + self.videocodec + ", Audiocodec: " + self.audiocodec + ", Dubs: " + str(self.dubs) + \
            ", Subs: " + str(self.subs) + ", Format: " + self.videoformat + ", Size: " + str(self.size) + "MB, Password: " + self.password

    def getEpisodeCount(self):
        return self.episodeCount


#Exceptions
class ALCaptchaException(Exception):
    pass

class ALInvalidBrowserException(Exception):
    pass

class ALLinkExtractionException(Exception):
    pass

class ALInvalidLoginException(Exception):
    pass

class ALUnknownException(Exception):
    pass