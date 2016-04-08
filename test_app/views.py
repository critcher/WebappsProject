from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

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
    e = s.replace(hour = (s.hour + 1)%24)
    format = '%Y-%m-%dT%H:%MZ'
    events.append({'title': title, 'start': s.strftime(format), 'e': e.strftime(format), 'description':"This is a really cool event."})
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
                     {"type": "boolean", "name": "field1", "required": True, "default": True},
                     {"type": "boolean", "name": "field2", "required": True, "default": False},
                     {"type": "text", "name": "Event Name", "required": False, "default": "test"},
                     {"type": "choice", "name": "field4", "required": True, "choices": ["1", "2", "3"], "default": "2"}, 
                     {"type": "date", "name": "Field4", "required": True, "default": {"month":5, "day":27, "year":1994}},
                     {"type": "time", "name": "Field6", "required": True, "default": {"hour":5, "minute":27, "am":False}},
                     {"type": "number", "name": "field7", "required": True, "default": 27} 
      ]})
