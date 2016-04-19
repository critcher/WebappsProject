from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator
# Google Django Support Library
from oauth2client.django_orm import FlowField, CredentialsField
import datetime


class FlowModel(models.Model):
    """Wrapper for oauth2client's FlowField uniquely associated with User."""
    id = models.OneToOneField(User, primary_key=True)
    flow = FlowField()


class CredentialsModel(models.Model):
    """Wrapper for oauth2client's CredentialsField
    uniquely associated with User"""
    id = models.OneToOneField(User, primary_key=True)
    credential = CredentialsField()


class CalendarUser(models.Model):
    """Wraps django's User model with add'l attributes.

    Attributes:
        user (User): pointer to target user to associate with.
        isOAuthed (bool): tracks status of user if they have initiated OAuth,
        or have revoked OAuth.
        isDev (bool): determines if user can access Dev tools,
        or is a Developer User-class.
    """
    user = models.OneToOneField(User, related_name='userPointer')
    isOAuthed = models.BooleanField(default=False)
    isDev = models.BooleanField(default=False)


class Calendar(models.Model):
    """Container of Event objects"""
    owner = models.OneToOneField(CalendarUser, on_delete=models.CASCADE)


class Event(models.Model):
    """Representation of Events, associated with Calendar.

    Attributes:
        description (str): Description of event.
        name (str): Name of event.
        start_timestamp (str): ISO timestamp for event's start time.
        end_timestamp (str): ISO timestamp for event's end time.
        icon_url (str): string rep of event's icon url.
        calendar (Calendar): pointer to containing Calendar instance.
        source (AppSetting): pointer to AppSetting from which event
        was created.
    """
    description = models.CharField(blank=True, max_length=100)
    name = models.CharField(blank=True, max_length=60)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    icon_url = models.CharField(blank=True, max_length=256)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    # A handle to the AppSettings instance that created this event.
    # Blank if this event is a static calendar event.
    source = models.ForeignKey(
        'AppSettings', blank=True, on_delete=models.CASCADE)


class App(models.Model):
    """Contains necesary data to make requests to 3rd party app

    Attributes:
        owner (CalendarUser): pointer to dev-class user that created
        this instance.
        description (str): description of App.
        name (str): name of App.
        version (str): version of App.
        icon_url (str): App's icon location for display and visual
        representation.
        settings_url (str): Callback URL for JSON data to build an App Form.
        data_url (str): Callback URL to send submitted form data to,
        which returns Events as Json.
        allows_duplicates (bool): flag for whether or not App can be bought
        multiple times by one user.
    """
    owner = models.ForeignKey(CalendarUser, on_delete=models.CASCADE)
    description = models.CharField(blank=True, max_length=1000)
    name = models.CharField(max_length=60)
    # Can be used to detect that a user's AppSettings are out of
    # date and might need to be prompted again
    version = models.CharField(max_length=60)
    icon_url = models.CharField(max_length=256)
    # URL that we send a GET request to in order to find out what
    # settings the user can set. Also the URL we send a POST request
    # with the user chosen settings for verification. If blank,
    # no special settings are needed
    settings_url = models.CharField(max_length=256)
    # URL that we send the request to in order to get the actual
    # data from the app
    data_url = models.CharField(max_length=256)
    # True if the app should be allowed to be added to a calendar
    # multiple times (with different settings, maybe)
    allow_duplicates = models.BooleanField(default=True)


class Color(models.Model):
    """Adapter for web color representations."""
    red = models.PositiveIntegerField(
        validators=[MaxValueValidator(255)], default=0)
    green = models.PositiveIntegerField(
        validators=[MaxValueValidator(255)], default=0)
    blue = models.PositiveIntegerField(
        validators=[MaxValueValidator(255)], default=0)

    def update(self, value):
        value = value.lstrip('#')
        lv = len(value)
        comps = tuple(int(value[i:i + lv / 3], 16)
                      for i in range(0, lv, lv / 3))
        self.red = comps[0]
        self.green = comps[1]
        self.blue = comps[2]
        self.save()

    def __unicode__(self):
        s = "#"
        s += "%02x" % self.red
        s += "%02x" % self.green
        s += "%02x" % self.blue
        return s


class AppSettings(models.Model):
    """AppSettings store App and User-set specific data used on calendar view calls

    Attributes:
        user (CalendarUser): creator/editor/owner of instance.
        settings_json (str): JSON that represents form, and submitted form data
        version (str): used to match against App version
        app (App): pointer to App instance for these settings
        last_updated_timestamp (str): used to track changes for ajax calls
        color (Color): color rep for appsetting, customized by user,
        colors events in calendar
    """
    user = models.ForeignKey(CalendarUser, on_delete=models.CASCADE)
    settings_json = models.TextField()
    # Can be used to detect that a user's AppSettings are out of
    # date and might need to be prompted again
    version = models.CharField(max_length=60)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    # Used to let the app know when we last asked for information
    # for this user. Note that the app can still give us data
    # for dates before this timestamp (to update changed events,
    # for example)
    last_updated_timestamp = models.DateTimeField(blank=True)
    color = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.last_updated_timestamp = datetime.datetime.now()
        if self.color is None:
            c = Color(red=111, green=111, blue=111)
            c.save()
            self.color = c
        super(AppSettings, self).save(*args, **kwargs)
