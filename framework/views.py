from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction
from django.contrib.auth.decorators import login_required
from forms import RegisterForm, SignInForm, UserForm, AppForm
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from models import CalendarUser, AppSettings, App
import jsonschema
import json
from appForms import convertJsonToForm, convertRequestToJson

# google OAuthStuff
import os
import httplib2
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError, TokenRevokeError
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from apiclient.errors import HttpError
from django.conf import settings

from .models import CredentialsModel, FlowModel
import datetime

# Needs to be Heroku Env vars TODO
CLIENT_SECRETS = os.path.join(
    os.path.dirname(__file__), 'client_secrets.json')


def home(request):
    return viewCalendar(request)


@login_required
def viewCalendar(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    context['user'] = request.user
    context['userApps'] = []

    user = request.user
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid is True or not user.userPointer.isOAuthed:
        return checkAuth(request)
    cUser = CalendarUser.objects.get(user=user)
    qSet = AppSettings.objects.filter(user=cUser)
    context['userApps'] = qSet.all()
    context['isDev'] = cUser.isDev
    return render(request, 'main.html', context)


@login_required
def removeApp(request):
    if request.method == 'GET' or not request.POST['appSettingID']:
        return redirect(reverse('editapp'))
    settingID = request.POST['appSettingID']
    user = request.user
    cUser = CalendarUser.objects.get(user=user)
    appSettingToDelete = AppSettings.objects.get(id=settingID, user=cUser)
    appSettingToDelete.delete()
    return redirect(reverse('editapp'))


@login_required
def getFormFromJson(request):
    context = {}
    if request.method == "GET":
        return Http404
    settingsId = request.POST.get('id', 0)
    context['settings_id'] = settingsId
    context['appSetting'] = get_object_or_404(AppSettings, id=settingsId)
    context['form_action'] = ""
    try:
        form = convertJsonToForm(
            request.POST['data'], context['appSetting'].settings_json)
    except Exception, e:
        print e
        return HttpResponse('')
    context['submit_string'] = "Update"
    context['form'] = form
    context['isDev'] = cUser.isDev
    return render(request, 'appForm.html', context)


@login_required
def viewAppForms(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    context['user'] = request.user
    context['userApps'] = []
    user = request.user
    cUser = CalendarUser.objects.get(user=user)
    qSet = AppSettings.objects.filter(user=cUser).order_by('-id')
    context['userApps'] = qSet.all()
    context['isDev'] = cUser.isDev
    return render(request, 'editSettings.html', context)


@login_required
def appStore(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    context['user'] = request.user
    context['availableApps'] = []
    user = request.user
    cUser = CalendarUser.objects.get(user=user)
    qSet = AppSettings.objects.filter(user=cUser)
    if request.method == "POST":
        idOfAppSelected = request.POST["app"]
        appObj = App.objects.get(id=idOfAppSelected)
        newAppSetting = AppSettings(
            user=cUser, app=appObj, version=appObj.version)
        newAppSetting.save()
        return redirect(reverse('editapp'))

    setOfAppsUsed = set()
    for appSetting in qSet:
        setOfAppsUsed.add(appSetting.app)
    qSet = App.objects.all()
    listOfUnusedApps = []
    for app in qSet:
        if app.allow_duplicates or (app not in setOfAppsUsed):
            listOfUnusedApps.append(app)
    context['availableApps'] = listOfUnusedApps
    context['isDev'] = cUser.isDev
    return render(request, 'appStore.html', context)


@login_required
def getEventsJSON(request):
    events = []
    if "start" in request.GET and "end" in request.GET:
        try:
            start = datetime.datetime.strptime(
                request.GET['start'], "%Y-%m-%d")
            end = datetime.datetime.strptime(request.GET['end'], "%Y-%m-%d")
        except ValueError, e:
            print e
            return JsonResponse(events, safe=False)
        end = end.isoformat() + "Z"
        start = start.isoformat() + "Z"
    else:
        start = datetime.datetime.utcnow()
        end = start.replace(year=start.year + 1)
        end = end.isoformat() + "Z"
        start = start.replace(day=1, hour=0, minute=0)
        start = start.isoformat() + "Z"

    user = request.user
    cUser = CalendarUser.objects.get(user=user)
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid is True or not cUser.isOAuthed:
        return checkAuth(request)
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build('calendar', 'v3', http=http)
    try:
        eventsResult = service.events().list(
            calendarId='primary', timeMin=start, timeMax=end, maxResults=1000, singleEvents=True,
            orderBy='startTime').execute()
    except HttpError:
        return JsonResponse(events, safe=False)
    gCalEvents = eventsResult.get('items', [])
    for event in gCalEvents:
        events.append(gCalToFullCalEventAdapter(event))
    return JsonResponse(events, safe=False)


def gCalToFullCalEventAdapter(gCalEvent):
    """
    Returns FullCalendar Event Json Representation of 
    some Google Calendar Event object
    Overtime, I imagine this will become increasingly sophisticated
    """
    fCalEvent = {}
    fCalEvent["title"] = gCalEvent["summary"]
    fCalEvent["url"] = gCalEvent["htmlLink"]
    try:
        fCalEvent["start"] = gCalEvent["start"]["dateTime"]
        fCalEvent["end"] = gCalEvent["end"]["dateTime"]
    except KeyError:
        fCalEvent['allDay'] = True
        fCalEvent["start"] = gCalEvent["start"]["date"]
        fCalEvent["end"] = gCalEvent["end"]["date"]
    return fCalEvent


@login_required
@transaction.atomic
def removeUserOAuth(request):
    user = request.user
    calUser = CalendarUser.objects.get(user=user)
    if not calUser.isOAuthed:
        return redirect(reverse('editprofile'))
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid is True:
        return redirect(reverse('editprofile'))
    http = httplib2.Http()
    try:
        credential.revoke(http)
    except TokenRevokeError, e:
        print e
    storage.delete()
    calUser.isOAuthed = False
    calUser.save()
    return redirect(reverse('editprofile'))


@login_required
def checkAuth(request):
    REDIRECT_URI = "http://%s%s" % (request.get_host(),
                                    reverse("oauth2return"))
    FLOW = flow_from_clientsecrets(
        CLIENT_SECRETS,
        scope='https://www.googleapis.com/auth/calendar.readonly',
        redirect_uri=REDIRECT_URI
    )
    user = request.user
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid is True or not user.userPointer.isOAuthed:
        FLOW.params['state'] = xsrfutil.generate_token(
            settings.SECRET_KEY, user)
        authorize_url = FLOW.step1_get_authorize_url()
        f = FlowModel(id=user, flow=FLOW)
        f.save()
        calUser = CalendarUser.objects.get(user=user)
        calUser.isOAuthed = True
        calUser.save()
        return HttpResponseRedirect(authorize_url)
    else:
        return HttpResponseRedirect(reverse('main'))


@login_required
def auth_return(request):
    user = request.user
    if not xsrfutil.validate_token(
            settings.SECRET_KEY, request.GET['state'], user):
        return HttpResponseBadRequest()
    try:
        FLOW = FlowModel.objects.get(id=user).flow
        credential = FLOW.step2_exchange(request.GET)
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        storage.put(credential)
        return HttpResponseRedirect(reverse('checkAuth'))
    except FlowExchangeError:
        return redirect(reverse('about'))


def about(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    context['user'] = request.user
    cUser = CalendarUser.objects.get(user=request.user)
    context['isDev'] = cUser.isDev
    return render(request, 'about.html', context)


def signIn(request):
    context = {}
    if (request.method == "GET"):
        context['form'] = SignInForm()
        return render(request, 'login.html', context)

    form = SignInForm(request.POST)
    if (not form.is_valid()):
        context['form'] = form
        return render(request, 'login.html', context)

    login(request, form.user)
    return redirect(reverse('main'))


@login_required
def profile(request, userArg):
    context = {}
    context['errors'] = []
    try:
        userMatch = User.objects.get(username__exact=userArg)
    except ObjectDoesNotExist:
        context['errors'].append("could not find object")
        return render(request, 'main.html', context)
    except MultipleObjectsReturned:
        context['errors'].append("multiple objects returned")
        return render(request, 'main.html', context)
    context['author'] = userArg
    context['firstname'] = userMatch.first_name
    context['lastname'] = userMatch.last_name
    try:
        profMatch = CalendarUser.objects.get(user=userMatch)
    except ObjectDoesNotExist:
        context['errors'].append("You dont have a profile yet!")
        return redirect(reverse("editprofile"))
    except MultipleObjectsReturned:
        context['errors'].append("multiple objects returned")
        return render(request, 'main.html', context)
    context['profile'] = profMatch
    cUser = CalendarUser.objects.get(user=request.user)
    context['isDev'] = cUser.isDev
    return render(request, 'profile.html', context)


@login_required
def editProfile(request):
    context = {}
    context['errors'] = []
    cUser = CalendarUser.objects.get(user=request.user)
    context['isDev'] = cUser.isDev
    if request.method == 'GET':
        context['userform'] = UserForm(instance=request.user,
                                       prefix="userform")
        return render(request, 'editprofile.html', context)
    userform = UserForm(
        data=request.POST, instance=request.user, prefix="userform")
    context['userform'] = userform
    if not userform.is_valid():
        context['errors'].append("form data invalid")
        return render(request, 'editprofile.html', context)
    userform.save()
    currentUser = request.user
    currentUser.firstname = userform.cleaned_data['first_name']
    currentUser.lastname = userform.cleaned_data['last_name']
    currentUser.save()
    return render(request, 'editprofile.html', context)


@transaction.atomic
def register(request):
    context = {}
    context['errors'] = []
    context['messages'] = []
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'registration.html', context)
    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'registration.html', context)

    registeredUser = User.objects.create_user(username=form.cleaned_data['username'],
                                              password=form.cleaned_data[
                                                  'password1'],
                                              first_name=form.cleaned_data[
                                                  'first_name'],
                                              last_name=form.cleaned_data[
                                                  'last_name'],
                                              email=form.cleaned_data['email'])

    registeredUser.backend = 'django.contrib.auth.backends.ModelBackend'
    registeredUser.is_active = True
    registeredUser.save()

    newCalUser = CalendarUser.objects.create(
        user=registeredUser, isOAuthed=False, isDev=form.cleaned_data['isDev'])
    newCalUser.save()

    return render(request, 'main.html', context)


@login_required
def registerApp(request):
    usr = request.user
    cUser = CalendarUser.objects.get(user=usr)
    if not cUser.isDev:
        return redirect(reverse('editprofile'))

    context = {}
    context['errors'] = []
    context['messages'] = []
    if request.method == 'GET':
        context['form'] = AppForm()
        return render(request, 'registerapp.html', context)
    form = AppForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'registerapp.html', context)

    app = App.objects.create(settings_url=form.cleaned_data['settings_url'])
    app.data_url = form.cleaned_data['data_url']
    app.description = form.cleaned_data['description']
    app.name = form.cleaned_data['name']
    app.icon_url = form.cleaned_data['icon_url']
    app.allow_duplicates = form.cleaned_data['allow_duplicates']
    app.save()

    context['isDev'] = cUser.isDev
    return render(request, 'registerapp.html', context)


def testAppForm(request):
    context = {}
    context['form_errors'] = []
    context['generated_form'] = ''

    if request.method == 'GET':
        context['json_string'] = '{\n\
  "fields": [\n\
                 {"type": "boolean", "name": "field1", "required": true, "default": true},\n\
                 {"type": "boolean", "name": "field2", "required": true, "default": false},\n\
                 {"type": "text", "name": "field3", "required": false, "default": "Hello"},\n\
                 {"type": "choice", "name": "field4", "required": true, "choices": ["1", "2", "3"], "default": "2"}, \n\
                 {"type": "date", "name": "field5", "required": true, "default": {"month":5, "day":27, "year":1994}},\n\
                 {"type": "time", "name": "field6", "required": true, "default": {"hour":5, "minute":27, "am":false}},\n\
                 {"type": "number", "name": "field7", "required": true, "default": 27} \n\
  ]\n\
}'
        return render(request, 'form-generator.html', context)

    json_string = request.POST.get('json_string', '')
    context['json_string'] = json_string
    import traceback
    try:
        context['generated_form'] = convertJsonToForm(json_string)
    except ValueError, e:
        traceback.print_exc()
        context['form_errors'].append("Invalid JSON!")
    except jsonschema.ValidationError, e:
        traceback.print_exc()
        context['form_errors'].append("JSON does not follow schema!")

    return render(request, 'form-generator.html', context)


@login_required
def getFormJson(request):
    try:
        appInstance = AppSettings.objects.get(id=request.POST['id'])
        jsonResp = convertRequestToJson(
            request.POST, ['id', 'display_color', 'csrfmiddlewaretoken'])
        if request.POST['display_color'] != "":
            appInstance.color.update(request.POST['display_color'])
        appInstance.save()
    except Exception, e:
        print e
        return HttpResponseBadRequest('')
    return JsonResponse(jsonResp)


@login_required
def saveSettings(request):
    try:
        data = json.loads(request.POST['settings'])
        errorDict = {}
        for field in data:
            if field == 'error' and data[field] != "":
                return JsonResponse({"error": data[field]})
            elif "error" in data[field] and data[field]['error'] != "":
                errorDict[field] = data[field]['error']
        if len(errorDict):
            return JsonResponse(errorDict)
        appInstance = AppSettings.objects.get(id=request.POST['id'])
        appInstance.settings_json = request.POST['settings']
        appInstance.save()
    except Exception, e:
        print e
        return HttpResponseBadRequest('')
    return JsonResponse({})
