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

        if period != 'all':
            events = {}

            tricky_data = '|||'.join([str(x) for x in events_data.contents]).split('<br/>')
            for i,data in enumerate(tricky_data):
                data = data.replace('|||', '')
                if not data.startswith("<div") and data != '':
                    souped_data = soup(data, "html.parser")
                    try:
                        print souped_data.h4.text
                        print souped_data.span.text, souped_data.get_text().replace(souped_data.h4.text, '').replace(souped_data.span.text, '')
                    except:
                        print souped_data.span.text,souped_data.get_text().replace(souped_data.span.text, '')
        else:
            print len(events_data)
            print str(events_data[0]).split("<br/>")


    def start(self):
        self.scrape_football(self.period)

f = FlashScore('finished','football',20)
f.start()