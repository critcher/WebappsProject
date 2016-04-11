from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import urllib2


query = "https://api.seatgeek.com/2/events?datetime_utc.gte='%s'datetime_utc.lte='%s'&taxonomies.name=concert&per_page=5&sort=score.desc"

output_format = '%Y-%m-%dT%H:%MZ'
input_format = '%Y-%m-%d'


@csrf_exempt
def getEvents(request):

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
        response = urllib2.urlopen(query % (start, end))
        data = json.load(response)
        print data
        if "events" in data:
            for ev in data["events"]:
                if "date_tbd" in ev and ev["date_tbd"]:
                    #no announced start/end time
                    continue

                title = ev["short_title"]
                s = datetime.datetime.strptime(ev["datetime_utc"], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=4)
                e = s + datetime.timedelta(hours=3)
                description=ev["title"]
                events.append({'title': title, 'start': s.strftime(output_format), 'end': e.strftime(output_format), "description": description})

        
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
            if zipCode>0 and zipCode<99999:
                return JsonResponse(jsonDict)
            else:
                raise KeyError
        except Exception, e:
            print e
            return JsonResponse({"error": "Form error."})
    else:
        return JsonResponse({"fields": [
                    {"type": "number", "name": "Zip Code", "required": True, "default": 15217} 
      ]})
