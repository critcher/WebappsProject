from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import datetime
import urllib2


query = "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte=%s&primary_release_date.lte=%s&vote_average.gte=%f&vote_count.gte=10&api_key=" + settings.API_KEY
query2 = "https://api.themoviedb.org/3/movie/%d/release_dates?api_key=" + settings.API_KEY
descStr = "Venue: <a href='https://www.google.com/maps/@%f,%f,15z' target='_blank'>%s</a><br>%d tickets left on <a href='%s' target='_blank'>SeatGeek</a>"

inputFormat = "%Y-%m-%dT%H:%M:%S.000Z"

@csrf_exempt
def getEvents(request):
    min_rating = 5.0
    try:
        tmp = json.loads(request.GET['settings'])
        min_rating = float(tmp["Minimum Rating"]["value"])
    except Exception, e:
        pass
    events = []
    try:
        start = request.GET['start']
        end = request.GET['end']
        q = query % (start, end, min_rating)
        response = urllib2.urlopen(q)
        data = json.load(response)
        for movie in data["results"]:
            if movie['original_language'] != 'en':
                continue
            try:
                q2 = query2 % (movie['id'])
                response2 = urllib2.urlopen(q2)
                data2 = json.load(response2)
                title = movie["title"]
                date = movie['release_date']
                for release in data2['results']:
                    if release['iso_3166_1'] == "US":
                        tmpDate = datetime.datetime.strptime(release['release_dates'][0]['release_date'], inputFormat)
                        date = tmpDate.strftime("%Y-%m-%d")
                        break
                events.append({'title': title, 'start': date, 'allDay': True})
            except KeyError:
                pass

    except Exception, ex:
        print ex
        return JsonResponse(events, safe=False)

    return JsonResponse(events, safe=False)


@csrf_exempt
def formHandling(request):
    if request.POST:
        try:
            jsonDict = json.loads(request.body)

            rating = jsonDict["Minimum Rating"]["value"]
            rating = float(rating)
            if rating > 0 and rating < 10:
                return JsonResponse(jsonDict)
            else:
                raise KeyError
        except Exception, e:
            print e
            return JsonResponse({"error": "Minimmum rating must be between 0 and 10."})
    else:
        return JsonResponse({"fields": [
            {"type": "number", "name": "Minimum Rating",
                "required": True, "default": 5.0}
        ]})
