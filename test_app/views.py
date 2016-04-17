from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import urllib2

teamMapping = {"Arizona Diamondbacks": 109,
               "Atlanta Braves": 144,
               "Baltimore Orioles": 110,
               "Boston Red Sox": 111,
               "Chicago Cubs": 112,
               "Chicago White Sox": 145,
               "Cincinnati Reds": 113,
               "Cleveland Indians": 114,
               "Colorado Rockies": 115,
               "Detroit Tigers": 116,
               "Houston Astros": 117,
               "Kansas City Royals": 118,
               "Los Angeles Angels": 108,
               "Los Angeles Dodgers": 119,
               "Miami Marlins": 146,
               "Milwaukee Brewers": 158,
               "Minnesota Twins": 142,
               "New York Mets": 121,
               "New York Yankees": 147,
               "Oakland Athletics": 133,
               "Philadelphia Phillies": 143,
               "Pittsburgh Pirates": 134,
               "San Diego Padres": 135,
               "San Francisco Giants": 137,
               "Seattle Mariners": 136,
               "St. Louis Cardinals": 138,
               "Tampa Bay Rays": 139,
               "Texas Rangers": 140,
               "Toronto Blue Jays": 141,
               "Washington Nationals": 120
               }
query = "http://mlb.com/lookup/json/named.schedule_team_sponsors.bam?start_date='%s'&end_date='%s'&team_id=%d&season=%d&game_type='R'&game_type='A'"
output_format = '%Y-%m-%dT%H:%MZ'
input_format = '%Y-%m-%d'
mlb_format = '%Y/%m/%d'

teamRecordStr = "%s (%s)"
pitcherStr = "%s (%s, %s)"

def buildTeamDesc(team, wl, prob, probWl, probEra):
    description = teamRecordStr % (team, wl)
    if prob != "":
        description += ": " + pitcherStr % (prob, probWl, probEra)
    return description

@csrf_exempt
def getEvents(request):
    team = "Arizona Diamondbacks"
    try:
        tmp = json.loads(request.GET['settings'])
        team = tmp['Team']['value']
    except Exception, e:
        pass
    events = []

    moreEvents = True
    pageNum = 1
    try:
        start = datetime.datetime.strptime(request.GET['start'], input_format)
        end = datetime.datetime.strptime(request.GET['end'], input_format)
        response = urllib2.urlopen(query % (start.strftime(mlb_format), end.strftime(mlb_format), teamMapping[team], start.year))
        data = json.load(response)
        curEvents = data["schedule_team_sponsors"]["schedule_team_complete"]["queryResults"]["row"]
        
        for ev in curEvents:
            s = datetime.datetime.strptime(ev["game_time_et"], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=4)
            e = s + datetime.timedelta(hours = 3)
            teamStr = ev["team_brief"]
            opponentStr = ev["opponent_brief"]
            atHome = ev["home_away_sw"] == 'H'
            if (atHome):
                title = teamStr + " vs " + opponentStr
            else:
                title = teamStr + " @ " + opponentStr
            gameStarted = ev["game_status_ind"] in ['F', 'I']
            if gameStarted:
                description = teamStr + ": " + ev['team_score'] + "<br>" + opponentStr + ": " + ev["opponent_score"]
            else:
                description = buildTeamDesc(teamStr, ev["team_wl"], ev["probable"], ev["probable_wl"], ev["probable_era"]) + "<br>"
                description += buildTeamDesc(opponentStr, ev["opponent_wl"], ev["opp_probable"], ev["opp_probable_wl"], ev["opp_probable_era"])
            events.append({'title': title, 'start': s.strftime(output_format), 'end': e.strftime(output_format), "description": description})
    except Exception, ex:
        return JsonResponse(events, safe=False)

    return JsonResponse(events, safe=False)

@csrf_exempt
def formHandling(request):
    if request.POST:
        try:
            jsonDict = json.loads(request.body)
            if jsonDict["Team"]["value"] not in teamMapping:
                raise KeyError
            return JsonResponse(jsonDict)
        except Exception, e:
            print e
            return JsonResponse({"error": "Form error."})
    else:
        return JsonResponse({"fields": [
                     {"type": "choice", "name": "Team", "required": True, "choices": teamMapping.keys(), "default": "Arizona Diamondbacks"}
      ]})
