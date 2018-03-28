import requests, json
from bs4 import BeautifulSoup as soup

def request():
    url = "https://www.sofascore.com/football/livescore/json"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    req = requests.get(url, headers=headers)
    events = json.loads(req.content)['sportItem']

    print "Content"
    print events['tournaments'][0]
    print "Content"

request()