import requests, json, re
from bs4 import BeautifulSoup as soup

def request():
    url = "http://www.flashscore.mobi/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    req = requests.get(url, headers=headers)
    html_content = soup(req.content, "html.parser")
    events_container = html_content.find("div", {"id":"score-data"})


    print "First league"
    print events_container.find_all('h4')
    events_container.h4.decompose()
    event_names = re.compile("\d:\d").split(events_container.get_text())
    print event_names
    print "First league"

request()