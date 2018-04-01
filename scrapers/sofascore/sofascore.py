import requests, json, os, sys, traceback, time
from bs4 import BeautifulSoup as soup
from datetime import datetime

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

    def scrape_soccer(self, period):
        """
        The first link is used when live events are available, if there are no such, the second link will get the info
        for the football.
        """

        if period == 'live':
            sport_content = self.session.get("{}football/livescore/json".format(self.host))
        else:
            sport_content = self.session.get("{}football//{}/json".format(self.host, datetime.now().strftime("%Y-%m-%d")))

        tournaments_events = {}

        sportContent = json.loads(sport_content.content)['sportItem']

        """
        This check here is to get the info from the url that actually returned information, i.e. the 'sportItem' element
        has data within.
        """
        if len(sportContent) > 0:
            tournaments = sportContent['tournaments']
        else:
            print "There are no {} events.".format(self.period)
            return {}

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

                if period == 'live' and status != 'inprogress':
                    continue
                if period == 'prematch' and status != 'notstarted':
                    continue
                if period == 'finished' and status != 'finished':
                    continue

                liveScore = {}
                lineup_info = {}

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


                    if league_name in Sofascore.LEAGUES_LINEUPS['LEAGUES'] and country in Sofascore.LEAGUES_LINEUPS['COUNTRIES']:
                        event_id = event['id']
                        req = self.session.get("{}event/{}/lineups/json".format(self.host,event_id))
                        home_team_info = json.loads(req.content)['homeTeam']
                        away_team_info = json.loads(req.content)['awayTeam']

                        try:
                            formation_ht = home_team_info['formation']
                            formation_at = away_team_info['formation']

                            home_team_lineup = []
                            away_team_lineup = []
                            home_incidents = {}
                            away_incidents = {}

                            for player in home_team_info['lineupsSorted']:
                                player_info = {
                                    'name': player['player']['name'].encode('utf-8'),
                                    'position': player['positionName'],
                                    'shirt_number': player['shirtNumber']
                                }
                                home_team_lineup.append(player_info)

                            if home_team_info.has_key('incidents') and type(home_team_info['incidents']) == dict:
                                for inc_id,data in home_team_info['incidents'].items():
                                    for incident in data:
                                        if incident['incidentType'] == 'substitution':
                                            type_inc = 'substitution'
                                            playerIn = incident['playerIn']['name'].encode('utf-8')
                                            playerOut = incident['playerOut']['name'].encode('utf-8')
                                            subst_time = incident['time']
                                            substitution = {
                                                'time': subst_time,
                                                'playerOut': playerOut,
                                                'playerIn': playerIn
                                            }

                                            if type not in home_incidents:
                                                home_incidents[type_inc] = []
                                            home_incidents[type_inc].append(substitution)
                                        elif incident['incidentType'] == 'card':
                                            type_inc = 'card'
                                            card_type = incident['type']
                                            reason = incident['reason']
                                            time = incident['time']
                                            player = incident['player']['name'].encode('utf-8')
                                            player_team = incident['playerTeam']

                                            card = {
                                                'card_type': card_type,
                                                'reason': reason,
                                                'time': time,
                                                'player_name': player,
                                                'player_team': player_team
                                            }

                                            if type not in home_incidents:
                                                home_incidents[type_inc] = []
                                            home_incidents[type_inc].append(card)
                                        elif incident['incidentType'] == 'goal':
                                            type_inc =  'goal'
                                            goal_type =  incident['incidentClass']
                                            time = incident['time']
                                            player = incident['player']['name'].encode('utf-8')
                                            player_team = incident['playerTeam']

                                            goal = {
                                                'goal_type': goal_type,
                                                'time': time,
                                                'player_name': player,
                                                'player_team': player_team
                                            }

                                            if type not in home_incidents:
                                                home_incidents[type_inc] = []
                                            home_incidents[type_inc].append(goal)

                            for player in away_team_info['lineupsSorted']:
                                player_info = {
                                    'name': player['player']['name'].encode('utf-8'),
                                    'position': player['positionName'],
                                    'shirt_number': player['shirtNumber']
                                }
                                away_team_lineup.append(player_info)

                            if away_team_info.has_key('incidents') and type(away_team_info['incidents']) == dict:
                                for inc_id,data in away_team_info['incidents'].items():
                                    for incident in data:
                                        if incident['incidentType'] == 'substitution':
                                            type_inc = 'substitution'
                                            playerIn = incident['playerIn']['name'].encode('utf-8')
                                            playerOut = incident['playerOut']['name'].encode('utf-8')
                                            subst_time = incident['time']
                                            substitution = {
                                                'time': subst_time,
                                                'playerOut': playerOut,
                                                'playerIn': playerIn
                                            }

                                            if type not in away_incidents:
                                                away_incidents[type_inc] = []
                                            away_incidents[type_inc].append(substitution)
                                        elif incident['incidentType'] == 'card':
                                            type_inc = 'card'
                                            card_type = incident['type']
                                            reason = incident['reason']
                                            time = incident['time']
                                            player = incident['player']['name'].encode('utf-8')
                                            player_team = incident['playerTeam']

                                            card = {
                                                'card_type': card_type,
                                                'reason': reason,
                                                'time': time,
                                                'player_name': player,
                                                'player_team': player_team
                                            }

                                            if type not in home_incidents:
                                                away_incidents[type_inc] = []
                                            away_incidents[type_inc].append(card)
                                        elif incident['incidentType'] == 'goal':
                                            type_inc = 'goal'
                                            goal_type = incident['incidentClass']
                                            time = incident['time']
                                            player = incident['player']['name'].encode('utf-8')
                                            player_team = incident['playerTeam']

                                            goal = {
                                                'goal_type': goal_type,
                                                'time': time,
                                                'player_name': player,
                                                'player_team': player_team
                                            }

                                            if type not in home_incidents:
                                                away_incidents[type_inc] = []
                                            away_incidents[type_inc].append(goal)

                            lineup_info = {
                                'homeTeam': {
                                    'formation': formation_ht,
                                    'lineups': home_team_lineup,
                                    'incidents': home_incidents
                                } ,
                                'awayTeam': {
                                    'formation': formation_at,
                                    'lineups': away_team_lineup,
                                    'incidents': away_incidents
                                }
                            }
                        except:
                            print req.url
                            print type(home_team_info['incidents']),type(away_team_info['incidents'])
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

                if period == 'live' and len(lineup_info.keys()):
                    e['lineups'] = lineup_info


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
            method = "scrape_{}_{}".format(self.sport, self.period)
            data = getattr(self, method)()

            filename = self.write_in_file(data)
            finishTime = datetime.now()
            iteration_time = (finishTime-starttime).seconds
            print ">>>>>>>>>>>>>>>>>> ITERATION FINISHED AT {}, for {} seconds".format(finishTime.strftime("%Y-%m-%d %H:%M:%S"), iteration_time)
            if self.sleeptime > iteration_time:
                print "Will sleep for {} seconds.".format(self.sleeptime-iteration_time)
                time.sleep(self.sleeptime-iteration_time)


if __name__ == '__main__':
    f = Sofascore(30, 'soccer')
    f.start()