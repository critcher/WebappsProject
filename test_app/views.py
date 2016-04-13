from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import datetime
from django.utils.dateparse import parse_datetime
import urllib2
import xml.etree.ElementTree as ET


query = "http://graphical.weather.gov/xml/SOAP_server/ndfdXMLclient.php?whichClient=NDFDgenMultiZipCode&zipCodeList=%d&product=time-series&Unit=e&maxt=maxt&mint=mint&pop12=pop12&sky=sky"
descStr = "High/Low (F): %s/%s<br>%s%s%% chance of precipitation."

def getCloudinessString(chance):
    if (chance < 20):
        return "Clear skies with "
    elif (chance < 50):
        return "Partly cloudy with "
    elif (chance < 70):
        return "Mostly cloudy with "
    else:
        return "Dreary with "

def fillWeatherInfo(dateWeather, dataGroup, key, timeLayouts):
    tInd = 0
    times = timeLayouts[dataGroup.get('time-layout')].findall('start-valid-time')
    for t in dataGroup.iter('value'):
        date = parse_datetime(times[tInd].text).date()
        tInd += 1
        if date in dateWeather:
            if key in dateWeather[date]:
                dateWeather[date][key] += [t.text]
            else:
                dateWeather[date][key] = [t.text]
        else:
            dateWeather[date] = {key: [t.text]}

@csrf_exempt
def getEvents(request):
    events = []
    try:
        tmp = json.loads(request.GET['settings'])
        zipCode = float(tmp["Zip Code"]["value"])
    except Exception, e:
        print e
        return JsonResponse(events, safe=False)
    try:
        q = query % (zipCode)
        response = urllib2.urlopen(q)
        root = ET.fromstring(response.read())
        data = root.find('data').find('parameters')
        timeLayouts = {}
        dateWeather = {}
        # Get time layout info
        for tLayout in root.find('data').iter('time-layout'):
            timeLayouts[tLayout.find('layout-key').text] = tLayout
        # Get temperature data
        for tempGroup in data.iter('temperature'):
            if tempGroup.get('type') == 'maximum':
                fillWeatherInfo(dateWeather, tempGroup, 'maxT', timeLayouts)
            else:
                fillWeatherInfo(dateWeather, tempGroup, 'minT', timeLayouts)

        rainGroup = data.find('probability-of-precipitation')
        fillWeatherInfo(dateWeather, rainGroup, 'rain', timeLayouts)
        cloudGroup = data.find('cloud-amount')
        fillWeatherInfo(dateWeather, cloudGroup, 'clouds', timeLayouts)
        for d in dateWeather:
            if 'maxT' in dateWeather[d]:
                maxT = dateWeather[d]['maxT'][0]
            else:
                maxT = "N/A"
            if 'minT' in dateWeather[d]:
                minT = dateWeather[d]['minT'][0]
            else:
                minT = "N/A"
            if 'rain' in dateWeather[d]:
                tmp = [int(v) for v in dateWeather[d]['rain']]
                rain = str(int(sum(tmp)/len(tmp)))
            else:
                rain = "N/A"
            if 'clouds' in dateWeather[d]:
                tmp = [int(v) for v in dateWeather[d]['clouds']]
                clouds = str(int(sum(tmp)/len(tmp)))
            else:
                clouds = "N/A"
            description = descStr % (maxT, minT, getCloudinessString(int(clouds)), rain)
            events.append({'title': "Weather", 'start': d.strftime("%Y-%m-%d"), 'allDay': True, 'description': description})

    except Exception, ex:
        print ex
        return JsonResponse(events, safe=False)

    return JsonResponse(events, safe=False)


@csrf_exempt
def formHandling(request):
    if request.POST:
        try:
            jsonDict = json.loads(request.body)

            zipCode = jsonDict["Zip Code"]["value"]
            try:
                q = query % (int(zipCode))
            except:
                return JsonResponse({"error": "Invalid Zip Code"})
            response = urllib2.urlopen(q)
            root = ET.fromstring(response.read())
            if root.tag == 'error':
                return JsonResponse({"error": "Invalid Zip Code"})
            else:
                return JsonResponse(jsonDict)
        except Exception, e:
            print e
            return JsonResponse({"error": "App Error"})
    else:
        return JsonResponse({"fields": [
            {"type": "number", "name": "Zip Code", "required": True}
        ]})
