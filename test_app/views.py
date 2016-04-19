from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import urllib2


query = "https://api.seatgeek.com/2/events?datetime_utc.gte=%s&datetime_utc.lte=%s&taxonomies.name=concert&per_page=100&range=%smi&sort=score.desc"
descStr = "Venue: <a href='https://www.google.com/maps/@%f,%f,15z' target='_blank'>%s</a><br>%d tickets left on <a href='%s' target='_blank'>SeatGeek</a>"

output_format = '%Y-%m-%dT%H:%MZ'
input_format = '%Y-%m-%d'


@csrf_exempt
def getEvents(request):
    loc = "15217"
    minPopularity = 0.6
    radius = "30"
    try:
        tmp = json.loads(request.GET['settings'])
        loc = tmp["Zip Code"]["value"]
        minPopularity = tmp["Popularity Threshold"]["value"]
        radius = tmp["Range"]["value"]
        radius = round(abs(float(radius)))
        minPopularity = float(minPopularity)
        if radius < 1:
            radius = 1
        radius = str(radius)
    except Exception, e:
        print e
    events = []
    try:
        start = request.GET['start']
        end = request.GET['end']
        q = query % (start, end, radius)
        if loc is not "":
            q += "&postal_code=%s" % (loc)
        response = urllib2.urlopen(q)
        data = json.load(response)
        if "events" in data:
            for ev in data["events"]:
                try:
                    if "date_tbd" in ev and ev["date_tbd"]:
                        # no announced start/end time
                        continue
                    if 'score' in ev and ev['score'] < minPopularity:
                        # low rated concert
                        continue
                    title = ev["short_title"]
                    print title
                    print ev["datetime_utc"]
                    s = datetime.datetime.strptime(
                        ev["datetime_utc"], "%Y-%m-%dT%H:%M:%S")
                    e = s + datetime.timedelta(hours=3)
                    ven = ev['venue']
                    description = descStr % (ven['location']['lat'], ven['location']['lon'], ven[
                                             'name'], ev['stats']['listing_count'], ev['url'])
                    events.append({'title': title, 'start': s.strftime(output_format), 'end': e.strftime(output_format), "description": description})
                except Exception:
                    continue

    except Exception, ex:
        return JsonResponse(events, safe=False)

    return JsonResponse(events, safe=False)


@csrf_exempt
def formHandling(request):
    if request.POST:
        try:
            jsonDict = json.loads(request.body)

            zipCode = jsonDict["Zip Code"]["value"]
            zipCode = int(zipCode)
            if zipCode > 0 and zipCode < 99999:
                return JsonResponse(jsonDict)
            else:
                raise KeyError
        except Exception, e:
            print e
            return JsonResponse({"error": "Form error."})
    else:
        return JsonResponse({"fields": [
            {"type": "number", "name": "Zip Code",
                "required": True, "default": 15217},
            {"type": "choice", "name": "Popularity Threshold",
             "required": True, "choices": ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"],
             "default": "2"},
            {"type": "number", "name": "Range",
                "required": True, "default": 30}
        ]})
