import re
from lxml import etree, html
from config_manager import loadconfig  # Import der Hauptklasse


class AnimeSearch:
    def __init__(self, animeloads_instance):
        self.al = animeloads_instance  # Referenz auf die Hauptklasse
    
    def fetch_search_results(self, query):
        """ Holt die Rohdaten der Suche und verarbeitet Umleitungen. """
        from animeloads import apihelper, Animeloads, searchResult
        searchdata = self.al.session.get(apihelper.getSearchURL(query), allow_redirects=False)
        if searchdata.status_code == 302:
            redir_url = searchdata.headers['Location']
            return redir_url, None  # Umleitung zu einer Detailseite
        return None, searchdata.text  # Standard-Suchergebnisse
    
    def parse_search_results(self, search_html):
        """ Parst das HTML und extrahiert die relevanten Daten. """
        from animeloads import apihelper, Animeloads, searchResult
        searchresults = []
        search_dom = etree.HTML(search_html)
        searchboxes = search_dom.xpath("//div/div[@class='panel panel-default' and 1]/div[@class='panel-body' and 1]")
        
        for result in searchboxes:
            url, name, typ, relDate, epCountCurrent, epCountMax, dubLang, subLang, genre = "", "", "", "", 0, 0, [], [], ""
            boxtree = etree.HTML(html.tostring(result))
            result_links = boxtree.xpath("//a")
            isFirst = True
            
            for link in result_links:
                linktext = link.text
                href = link.get('href')
                if href and "genre" in href:
                    genre = linktext
                elif href and "https://www.anime-loads.org/media/" in href:
                    if isFirst:
                        isFirst = False
                        continue
                    url = href
                    name = linktext
                    isFirst = True
            
            result_span = boxtree.xpath("//span[@class='label label-gold']")
            for span in result_span:
                epsplit = str(html.tostring(span)).split("/")
                epCountCurrent = re.sub("[^0-9]", "", epsplit[1])
                epCountMax = re.sub("[^0-9]", "", epsplit[2])
            
            lang_class = boxtree.xpath("//div[@class='mt10 mb10' and 3]")[0]
            langsplit = str(html.tostring(lang_class)).split("\"")
            for substring in langsplit:
                if "Sprache: " in substring:
                    dubLang.append(substring.replace("Sprache: ", ""))
                elif "Untertitel: " in substring:
                    subLang.append(substring.replace("Untertitel: ", ""))
            
            result = searchResult(url, name, typ, relDate, epCountCurrent, epCountMax, dubLang, subLang, genre, self.al.session, self.al)
            searchresults.append(result)
        
        return searchresults
    
    def search(self, query):
        """ Sucht nach einem Anime und verarbeitet die Ergebnisse. """
        from animeloads import apihelper, Animeloads, searchResult
        redir_url, search_html = self.fetch_search_results(query)
        if redir_url:
            redir_anime = Animeloads(redir_url, self.al.session, self.al)
            return [searchResult(redir_url, redir_anime.getName(), redir_anime.getType(), redir_anime.getYear(), redir_anime.getCurrentEpisodes(), redir_anime.getMaxEpisodes(), ["UNKNOWN"], ["UNKNOWN"], redir_anime.getMainGenre(), self.al.session, self.al)]
        return self.parse_search_results(search_html)

if __name__ == "__main__":
    print("Teste Anime-Suche...")
    from animeloads import apihelper, Animeloads, searchResult
    try:
        jdhost, hoster, browser, browserlocation, pushkey, timedelay, myjd_user, myjd_pass, myjd_device = loadconfig()
        al_instance = Animeloads(browser=browser, browserloc=browserlocation)  # Sicherstellen, dass der Browser korrekt übergeben wird
        search_module = AnimeSearch(al_instance)
        result = search_module.search("One Piece")
        for res in result:
            print(res.tostring())  # Falls `tostring()` existiert
    except Exception as e:
        print(f"Fehler beim Testen: {e}")