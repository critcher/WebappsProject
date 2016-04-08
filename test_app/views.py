from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import urllib2

teamMapping = {"Arizona Diamondbacks": "arizona-diamondbacks",
               "Atlanta Braves": "atlanta-braves",
               "Baltimore Orioles": "baltimore-orioles",
               "Boston Red Sox": "boston-red-sox",
               "Chicago Cubs": "chicago-cubs",
               "Chicago White Sox": "chicago-white-sox",
               "Cincinnati Reds": "cincinnati-reds",
               "Cleveland Indians": "cleveland-indians",
               "Colorado Rockies": "colorado-rockies",
               "Detroit Tigers": "detroit-tigers",
               "Houston Astros": "houston-astros",
               "Kansas City Royals": "kansas-city-royals",
               "Los Angeles Angels": "los-angeles-angels",
               "Los Angeles Dodgers": "los-angeles-dodgers",
               "Miami Marlins": "miami-marlins",
               "Milwaukee Brewers": "milwaukee-brewers",
               "Minnesota Twins": "minnesota-twins",
               "New York Mets": "new-york-mets",
               "New York Yankees": "new-york-yankees",
               "Oakland Athletics": "oakland-athletics",
               "Philadelphia Phillies": "philadelphia-phillies",
               "Pittsburgh Pirates": "pittsburgh-pirates",
               "San Diego Padres": "san-diego-padres",
               "San Francisco Giants": "san-francisco-giants",
               "Seattle Mariners": "seattle-mariners",
               "St. Louis Cardinals": "st-louis-cardinals",
               "Tampa Bay Rays": "tampa-bay-rays",
               "Texas Rangers": "texas-rangers",
               "Toronto Blue Jays": "toronto-blue-jays",
               "Washington Nationals": "washington-nationals"
               }
query = "https://api.seatgeek.com/2/events?datetime_utc.gte=%s&datetime_utc.lte=%sT21:59:59&performers.slug=%s&page=%d"
output_format = '%Y-%m-%dT%H:%MZ'

@csrf_exempt
def getEvents(request):
    team = "Arizona Diamondbacks"
    try:
        tmp = json.loads(request.GET['settings'])
        team = tmp['Team']['value']
    except Exception, e:
        print e
    events = []

    moreEvents = True
    pageNum = 1
    try:
        while moreEvents:
            response = urllib2.urlopen(query % (request.GET['start'], request.GET['end'], teamMapping[team], pageNum))
            pageNum += 1
            data = json.load(response)
            moreEvents = (pageNum * data["meta"]["per_page"] < data["meta"]["total"])
            curEvents = data["events"]
            for ev in curEvents:
                s = datetime.datetime.strptime(ev["datetime_utc"], "%Y-%m-%dT%H:%M:%S")
                e = s + datetime.timedelta(hours = 3)
                events.append({'title': ev["title"], 'start': s.strftime(output_format), 'end': e.strftime(output_format)})
    except KeyError:
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
                     {"type": "choice", "name": "Team", "required": True, "choices": teamMapping.keys()}
      ]})
