import urllib
import time, re, request
from bs4 import BeautifulSoup

class Movie:
    def __init__(self, imdbLink = None):
        self.ImdbLink = imdbLink
        self.parse(imdbLink)

    def parse(self, url):
        response = urllib.urlopen(url)
        print url
        html = response.read()
        soup = BeautifulSoup(html,"lxml")

        self.Title = soup.title.string[:-14].strip()
        self.Rating = float(soup.find(itemprop="ratingValue").string.strip())

        dates = soup.find_all("span", "nobr")
        if len(dates) > 1:
            date = dates[1].string.split("(")[0][:-1].strip()
        else:
            date = dates[0].a.get_text()
        try:
            self.ReleaseDate = time.strptime(date, '%d %B %Y')
        except ValueError:
            try:
                self.ReleaseDate = time.strptime(date, '%B %Y')
            except ValueError:
                try:
                    self.ReleaseDate = time.strptime(date, '%Y')
                except ValueError:
                    self.ReleaseDate = time.gmtime(0)
                    pass

        synopsis = soup.find(itemprop="description")
        self.Synopsis = re.sub(' +', ' ', synopsis.get_text().strip())

        directors = soup.find_all(itemprop="director")
        self.Directors = []
        for director in directors:
            self.Directors.append(str(director.a.string))

        actors = soup.find('table', 'cast_list').find_all("span", "itemprop")
        characters = soup.find('table', 'cast_list').find_all("td", "character")

        genres = soup.find('div',{"id":"titleStoryLine"}).find("div", {"itemprop":"genre"}).findAll("a",attrs={'class': None})
        for gen in genres:
            print gen.string

        self.Actors = {}
        for i in range(len(actors)):
            if characters[i].a != None:
                characterName = characters[i].a.get_text()

                #if characterName == None:
                #    characterName = characters[i].div.a.string

                self.Actors[str(actors[i].string).strip()] = re.sub(' +', ' ', characterName)
            else:
                self.Actors[str(actors[i].string).strip()] = None

        #self.Characters = []
        #for character in characters:
        #    self.Characters.append(str(character.div.string).strip())

    def __repr__(self):
        return "<Movie('%s', '%s', '%s')>" % (self.ImdbLink, self.Title, self.ReleaseDate)
