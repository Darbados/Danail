import requests, json
from bs4 import BeautifulSoup as soup
from datetime import datetime

class Sofascore:

    def __init__(self, sleeptime, period):
        self.host = "https://www.sofascore.com/"
        self.sleeptime = sleeptime
        self.period = period
        self.session = requests.Session()
        self.session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

    def scrape_soccer(self):
        base_info = self.session.get("{}football/livescore/json".format(self.host))

        tournaments_events = {}

        sportContent = json.loads(base_info.content)['sportItem']
        tournaments = sportContent['tournaments']

        for tournament in tournaments:
            league_name = tournament['tournament']['name'].encode('utf-8')
            league_events = tournament['events']

            if league_name not in tournaments_events:
                tournaments_events[league_name] = []

            for event in league_events:
                name = event['name'].encode('utf-8')
                home_team = event['homeTeam']['name'].encode('utf-8')
                away_team = event['awayTeam']['name'].encode('utf-8')
                start_date = datetime.fromtimestamp(float(event['startTimestamp'])).strftime("%Y-%m-%d %H:%M:%S")
                home_team_score = event['homeScore']['current']
                away_team_score = event['awayScore']['current']
                liveScore = {
                    'home_team_score': home_team_score,
                    'away_team_score': away_team_score
                }
                e = {
                    'event_name': name,
                    'home_team': home_team,
                    'away_team': away_team,
                    'start_date': start_date,
                    'liveScore': liveScore
                }

                tournaments_events[league_name].append(e)

        print tournaments_events


if __name__ == '__main__':
    f = Sofascore(20, 'live')
    f.scrape_soccer()