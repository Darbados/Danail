import requests, json, os, sys, traceback, time
from bs4 import BeautifulSoup as soup
from datetime import datetime

path_app = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(path_app)

class Sofascore:
    def __init__(self, sleeptime, sport):
        self.host = "https://www.sofascore.com/"
        self.sleeptime = sleeptime
        self.sport = sport
        self.session = requests.Session()
        self.session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

    def scrape_soccer(self):
        """
        The first link is used when live events are available, if there are no such, the second link will get the info
        for the football.
        """

        base_info = self.session.get("{}football/livescore/json".format(self.host))
        no_live_score_url = self.session.get("{}football//{}/json".format(self.host, datetime.now().strftime("%Y-%m-%d")))

        tournaments_events = {}

        sportContent = json.loads(base_info.content)['sportItem']

        """
        This check here is to get the info from the url that actually returned information, i.e. the 'sportItem' element
        has data within.
        """
        if len(sportContent) > 0:
            tournaments = sportContent['tournaments']
        else:
            today_events = json.loads(no_live_score_url.content)['sportItem']
            tournaments = today_events['tournaments']

        for tournament in tournaments:
            """
            Here starts the tournaments loop and I'm setting some variables for the tournaments_events structure.
            """
            league_name = tournament['tournament']['name'].encode('utf-8')

            country = tournament['category']['name']

            if league_name not in tournaments_events:
                tournaments_events[league_name] = []

            try:
                league_events = tournament['events']
            except:
                print "There are no events for {}".format(league_name)
                continue

            for event in league_events:
                name = event['name'].encode('utf-8')
                sport_title = event['sport']['name']
                home_team = event['homeTeam']['name'].encode('utf-8')
                away_team = event['awayTeam']['name'].encode('utf-8')
                start_date = datetime.fromtimestamp(float(event['startTimestamp'])).strftime("%Y-%m-%d %H:%M:%S")
                status = event['status']['type']

                liveScore = {}

                if len(event['homeScore'].keys()) and len(event['awayScore'].keys()):
                    home_team_score = event['homeScore']['current']
                    away_team_score = event['awayScore']['current']
                    liveScore = {
                        'home_team_score': home_team_score,
                        'away_team_score': away_team_score
                    }
                else:
                    # For not started events, I'm harccding the home & away scores to 0.
                    liveScore = {
                        'home_team_score': 0,
                        'away_team_score': 0
                    }


                e = {
                    'event_name': name,
                    'home_team': home_team,
                    'away_team': away_team,
                    'sport_title': sport_title,
                    'start_date': start_date,
                    'status': status,
                    'country': country,
                    'liveScore': liveScore
                }

                # If there are odds and the event is not finished, we'll get the fullTimeOdds & doubleChanceOdds, if
                # available.
                if event.has_key('odds') and status != 'finished':
                    e['odds'] = {}
                    try:
                        if event['odds'].has_key('fullTimeOdds'):
                            fullTimeOdds = event['odds']['fullTimeOdds']

                            if fullTimeOdds.has_key('regular'):
                                regular_odds = {}

                                for odd_type, data in fullTimeOdds['regular'].items():
                                    regular_odds["odd_{}".format(odd_type)] = {
                                        "external": {
                                            'event_name': name,
                                            'home_team': home_team,
                                            'away_team': away_team,
                                        },
                                        "value": data["decimalValue"],
                                        "bet_link": data["betSlipLink"]
                                    }

                                if len(regular_odds.keys()):
                                    e['odds']['ft-ml'] = regular_odds

                        if event['odds'].has_key('doubleChanceOdds'):
                            double_chance_odds = {}

                            for odd_type, data in event['odds']['doubleChanceOdds']['regular'].items():
                                double_chance_odds["odd_{}".format(odd_type)] = {
                                    "external": {
                                        'event_name': name,
                                        'home_team': home_team,
                                        'away_team': away_team,
                                    },
                                    "value": data["decimalValue"],
                                    "bet_link": data["betSlipLink"]
                                }

                            if len(double_chance_odds.keys()):
                                e['odds']['ft-dch'] = double_chance_odds
                    except:
                        pass

                tournaments_events[league_name].append(e)

        return tournaments_events

    def write_in_file(self, data):
        try:
            dir_name = os.path.abspath(os.path.join(path_app, 'sofascore_debug/results'))
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            filename = '{}/{}.json'.format(dir_name, self.sport)
            with open(filename, 'w') as outfile:
                json.dump(data, outfile, ensure_ascii=False)
                print "FILENAME: {}".format(filename)
            return filename
        except:
            traceback.print_exc()
            print "CANNOT SAVE FILE"

    def start(self):
        while True:
            starttime = datetime.now()
            print ">>>>>>>>>>>>>>>>>> ITERATION STARTED AT {}".format(starttime.strftime("%Y-%m-%d %H:%M:%S"))
            method = "scrape_{}".format(self.sport)
            data = getattr(self, method)()

            filename = self.write_in_file(data)
            finishTime = datetime.now()
            print ">>>>>>>>>>>>>>>>>> ITERATION FINISHED AT {}, for {} seconds".format(finishTime.strftime("%Y-%m-%d %H:%M:%S"), (finishTime-starttime).seconds)
            time.sleep(self.sleeptime)


if __name__ == '__main__':
    f = Sofascore(30, 'soccer')
    f.start()