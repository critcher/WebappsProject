from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

APIKEY = settings.WEATHER_API_KEY


@csrf_exempt
def getEvents(request):
    title = 'test'
    try:
        tmp = json.loads(request.GET['settings'])
        title = tmp['Event Name']['value']
    except Exception, e:
        print e
    events = []
    s = datetime.datetime.now()
    e = s.replace(hour=(s.hour + 1) % 24)
    format = '%Y-%m-%dT%H:%MZ'
    events.append(
        {'title': title, 'start': s.strftime(format), 'e': e.strftime(format)})
    return JsonResponse(events, safe=False)


@csrf_exempt
def formHandling(request):
    if request.POST:
        try:
            jsonDict = json.loads(request.body)
            return JsonResponse(jsonDict)
        except:
            return JsonResponse({"error": "Form error."})
    else:
        return JsonResponse({"fields": [
            {"type": "text", "name": "CITY",
             "required": True, "default": "Pittsburgh"}
        ]})
