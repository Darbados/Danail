__author__ = "Petar Netev"

import requests, json, os, sys, traceback, time, codecs
from datetime import datetime, timedelta
from collections import OrderedDict

path_app = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(path_app)


class Sofascore:
    LEAGUES_LINEUPS = {
        'LEAGUES': ('Serie A', 'LaLiga', 'Ligue 1', 'Premier League', 'Bundesliga'),
        'COUNTRIES': ('Italy', 'Spain', 'France', 'England', 'Germany')
    }

    def __init__(self, sleeptime, sport, period):
        self.host = "https://www.sofascore.com/"
        self.sleeptime = sleeptime
        self.sport = sport
        self.period = period
        self.session = requests.Session()
        self.session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

    def get_data(self, period):
        """
        The first link is used when live events are available, if there are no such, the second link will get the info
        for the football.
        """

        if period == 'live':
            sport_content = self.session.get("{}football/livescore/json".format(self.host))
            now = datetime.now().strftime("%Y-%m-%d")
            sport_content_live = {now: json.loads(sport_content.content)['sportItem']['tournaments']}

            return sport_content_live

        elif period == 'prematch':
            today = datetime.now()
            prematch_schedule = OrderedDict()

            sport_content = self.session.get(
                "{}football//{}/json".format(self.host, datetime.now().strftime("%Y-%m-%d")))
            prematch_schedule[today.strftime("%Y-%m-%d")] = json.loads(sport_content.content)['sportItem']['tournaments']

            for x in range(1, 8):
                try:
                    sport_content_scheduled = self.session.get(
                        "{}football//{}/json".format(self.host, (today + timedelta(days=x)).strftime("%Y-%m-%d")))
                    prematch_schedule[(today + timedelta(days=x)).strftime("%Y-%m-%d")] = \
                    json.loads(sport_content_scheduled.content)['sportItem']['tournaments']
                except:
                    continue

            return prematch_schedule

        else:
            today = datetime.now()
            finished_archive = OrderedDict()

            sport_content = self.session.get(
                "{}football//{}/json".format(self.host, datetime.now().strftime("%Y-%m-%d")))
            finished_archive[today.strftime("%Y-%m-%d")] = json.loads(sport_content.content)['sportItem']['tournaments']

            for x in range(1, 8):
                try:
                    sport_content_scheduled = self.session.get(
                        "{}football//{}/json".format(self.host, (today - timedelta(days=x)).strftime("%Y-%m-%d")))
                    finished_archive[(today - timedelta(days=x)).strftime("%Y-%m-%d")] = \
                    json.loads(sport_content_scheduled.content)['sportItem']['tournaments']
                except ConnectionError:
                    continue

            return finished_archive

    def scrape_soccer(self, period):

        sport_content = self.get_data(period)
        tournaments_events = {}

        for key,tournaments in sport_content.items():
            if key not in tournaments_events:
                tournaments_events[key] = {}
            if len(tournaments)> 0:
                for tournament in tournaments:
                    """
                    Here starts the tournaments loop and I set some variables for the tournaments_events structure.
                    """
                    league_name = tournament['tournament']['name']

                    country = tournament['category']['name']

                    if league_name not in tournaments_events[key]:
                        tournaments_events[key][league_name] = []

                    try:
                        league_events = tournament['events']
                    except KeyError:
                        print("There are no events for {}".format(league_name))
                        continue

                    for event in league_events:
                        name = event['name']
                        sport_title = event['sport']['name']
                        home_team = event['homeTeam']['name']
                        away_team = event['awayTeam']['name']
                        start_date = datetime.fromtimestamp(float(event['startTimestamp'])).strftime("%Y-%m-%d %H:%M:%S")
                        status = event['status']['type']

                        if period == 'live' and status != 'inprogress':
                            continue
                        if period == 'prematch' and status != 'notstarted':
                            continue
                        if period == 'finished' and status != 'finished':
                            continue

                        liveScore = {}

                        if period == 'live':
                            home_team_score = event['homeScore']['current']
                            away_team_score = event['awayScore']['current']

                            # Get the current minute for live events
                            live_minute = event['statusDescription']

                            liveScore = {
                                'home_team_score': home_team_score,
                                'away_team_score': away_team_score,
                                'live_minute': live_minute
                            }
                        elif period == 'prematch':
                            # For not started events, I'm harccding the home & away scores to 0.
                            liveScore = {
                                'home_team_score': 0,
                                'away_team_score': 0
                            }
                        else:
                            home_team_score = event['homeScore']['current']
                            away_team_score = event['awayScore']['current']

                            liveScore = {
                                'home_team_score': home_team_score,
                                'away_team_score': away_team_score,
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
                        if 'odds' in event and status != 'finished':
                            e['odds'] = {}
                            try:
                                if 'fullTimeOdds' in event['odds']:
                                    full_time_odds = event['odds']['fullTimeOdds']

                                    if 'regular' in full_time_odds:
                                        regular_odds = {}

                                        for odd_type, data in full_time_odds['regular'].items():
                                            regular_odds["odd_{}".format(odd_type)] = {
                                                "external": {
                                                    'event_name': name,
                                                    'home_team': home_team,
                                                    'away_team': away_team,
                                                },
                                                "value": data["decimalValue"],
                                            }

                                        if len(regular_odds.keys()):
                                            e['odds']['ft-ml'] = regular_odds

                                if 'doubleChanceOdds' in event['odds']:
                                    double_chance_odds = {}

                                    for odd_type, data in event['odds']['doubleChanceOdds']['regular'].items():
                                        double_chance_odds["odd_{}".format(odd_type)] = {
                                            "external": {
                                                'event_name': name,
                                                'home_team': home_team,
                                                'away_team': away_team,
                                            },
                                            "value": data["decimalValue"],
                                        }

                                    if len(double_chance_odds.keys()):
                                        e['odds']['ft-dch'] = double_chance_odds
                            except KeyError:
                                pass

                        if start_date.split(" ")[0] == key:
                            tournaments_events[key][league_name].append(e)
            else:
                print("There are no {} events.".format(period))

        return tournaments_events

    def scrape_soccer_prematch(self):
        return self.scrape_soccer(self.period)

    def scrape_soccer_live(self):
        return self.scrape_soccer(self.period)

    def scrape_soccer_finished(self):
        return self.scrape_soccer(self.period)

    def write_in_file(self, data):
        try:
            dir_name = os.path.abspath(os.path.join(path_app, 'sofascore_debug/results'))
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            filename = '{}/{}_{}.json'.format(dir_name, self.sport, self.period)
            with open(filename, 'w') as outfile:
                json.dump(data, outfile)
                print("FILENAME: {}".format(filename))
            return filename
        except:
            traceback.print_exc()
            print("CANNOT SAVE FILE")

    def start(self):
        while True:
            starttime = datetime.now()
            print(">>>>>>>>>>>>>>>>>> ITERATION STARTED AT {}".format(starttime.strftime("%Y-%m-%d %H:%M:%S")))
            method = "scrape_{}_{}".format(self.sport, self.period)
            data = getattr(self, method)()

            self.write_in_file(data)
            finish_time = datetime.now()
            iteration_time = (finish_time-starttime).seconds
            print(">>>>>>>>>>>>>>>>>> ITERATION FINISHED AT {}, for {} seconds".format(finish_time.strftime("%Y-%m-%d %H:%M:%S"), iteration_time))
            if self.sleeptime > iteration_time:
                print("Will sleep for {} seconds.".format(self.sleeptime-iteration_time))
                time.sleep(self.sleeptime-iteration_time)