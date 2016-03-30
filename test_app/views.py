from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

@csrf_exempt
def getEvents(request):
    events = []
    s = datetime.datetime.now()
    e = s.replace(hour = s.hour + 1)
    format = '%Y-%m-%dT%H:%MZ'
    events.append({'title': 'test', 'start': s.strftime(format), 'e': e.strftime(format)})
    return JsonResponse(events, safe=False)

@csrf_exempt
def formHandling(request):
    return JsonResponse({})
