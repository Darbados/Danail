__author__ = "Petar Netev"

import requests, json, re, sys, traceback
from bs4 import BeautifulSoup as soup


URL_SPORTS_MAP = {
    'football': '',
    'hockey': 'hockey',
    'tennis': 'tennis',
    'basketball': 'basketball',
    'handball': 'handball',
}

URL_PERIODS_MAP = {
    'all': [('today',''),('yesterday','?d=-1'),('tomorrow','?d=1')],
    'live': '?s=2',
    'finished': '?s=3'
}

class FlashScore:
    def __init__(self, period, sport, sleeptime):
        self.host = 'http://www.flashscore.mobi'
        self.period = period
        self.sport = sport
        self.sleeptime = sleeptime
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
        self.session = requests.Session()
        self.session.headers = self.headers

    def get_data(self, period, sport):
        try:
            if period != 'all':
                url = "{}/{}/{}".format(self.host, URL_SPORTS_MAP[sport],URL_PERIODS_MAP[period])
                req = self.session.get(url)
                events_container = soup(req.content, "html.parser").find("div",{"id":"score-data"})
                return events_container
            else:
                three_days_events = []
                for day in URL_PERIODS_MAP[period]:
                    url = "{}/{}/{}".format(self.host, URL_SPORTS_MAP[sport], day[1])
                    req = self.session.get(url)
                    three_days_events.append(soup(req.content, "html.parser").find("div",{"id":"score-data"}))
                return three_days_events
        except:
            print "There is some problem with the data container get"
            traceback.print_exc()

    def scrape_football(self, period):
        events_data = self.get_data(period, self.sport)

        events = {}
        events_section = [[] for x in events_data.contents if str(x) == "<br/>"]

        tournaments = events_data.find_all('h4')
        for tournament in tournaments:
            if tournament.text not in events:
                events[tournament.text] = []

        print events_section
        print events_data.contents


    def start(self):
        self.scrape_football(self.period)

f = FlashScore('live','tennis',20)
f.start()